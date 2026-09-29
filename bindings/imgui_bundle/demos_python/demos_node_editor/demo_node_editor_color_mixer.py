"""Node editor: a color mixer

Colors flow through a small graph: pick two colors, mix them, and see the result in the swatches. Each link is drawn
in the color it carries. A first graph with [imgui-node-editor](https://github.com/thedmd/imgui-node-editor): the
nodes, pins and links that the app owns, and how the user edits them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple

from imgui_bundle import imgui, immapp, imgui_node_editor as ed, rich_md, ImVec2, ImVec4, em_size

NODE_WIDTH_EM = 9.0  # the width of a node's content
SWATCH_SIZE_EM = 5.0  # the side of a swatch's square
PIN_RADIUS_EM = 0.4  # the radius of a pin's circle
LINK_THICKNESS = 3.0  # the thickness of the links (they follow the zoom)
UNLINKED = ImVec4(0.3, 0.3, 0.3, 1.0)  # the color an input receives when no link reaches it
WHITE = ImVec4(1.0, 1.0, 1.0, 1.0)

# The gestures, in markdown ("  \n" ends a line)
HELP = (
    "**Link** two pins: drag from one to the other  ·  "
    "**Delete** a node or a link: select it, then <kbd>Delete</kbd>  \n"
    "**Add a node**: right-click the background  ·  **Pan**: right-drag  ·  **Zoom**: the wheel  ·  "
    "**See the whole graph**: <kbd>F</kbd>"
)


class NodeKind(NamedTuple):
    inputs: list[str]  # the names of its input pins
    doc: str  # what it does, shown under its title (markdown, with math between $ signs)


# Every kind of node has one output, except the swatch, which shows its input
NODE_KINDS = {
    "Color": NodeKind([], "Pick a color"),
    "Mix": NodeKind(["a", "b"], r"$(1-t)\,a + t\,b$"),
    "Invert": NodeKind(["in"], r"$1 - c$, per channel"),
    "Grayscale": NodeKind(["in"], r"$0.3\,r + 0.59\,g + 0.11\,b$"),
    "Swatch": NodeKind(["in"], "Show the color"),
}


# =====================================================================================================================
# 1. The graph: nodes, pins and links
# =====================================================================================================================
# The editor draws the graph and lets the user edit it, but it does not store it: the app owns its nodes, pins and
# links, and submits them at each frame. Each of them has an id (ed.NodeId, ed.PinId, ed.LinkId), which must stay
# the same from one frame to the next: ed.NodeId.create() gives a new unique one.
@dataclass(eq=False)
class Pin:
    name: str
    kind: ed.PinKind  # an input (on the left of its node) or an output (on the right)
    node: Node
    id: ed.PinId = field(default_factory=ed.PinId.create)


class Node:
    def __init__(self, kind: str, color: ImVec4 = WHITE) -> None:
        self.kind = kind
        self.id = ed.NodeId.create()
        self.inputs = [Pin(name, ed.PinKind.input, self) for name in NODE_KINDS[kind].inputs]
        self.output = Pin("out", ed.PinKind.output, self) if kind != "Swatch" else None
        self.color = color  # what a Color node gives
        self.mix = 0.5  # t: a Mix node's share of b


@dataclass(eq=False)
class Link:
    start: Pin  # an output
    end: Pin  # an input
    id: ed.LinkId = field(default_factory=ed.LinkId.create)


class Graph:
    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.links: list[Link] = []

    def add_node(self, kind: str, position_em: ImVec2, color: ImVec4 = WHITE) -> Node:
        node = Node(kind, color)
        self.nodes.append(node)
        # The editor keeps the positions: we only give the first one. They are in the editor's coordinates (pixels
        # at zoom 1), which is why we convert from em.
        ed.set_node_position(node.id, position_em * em_size())
        return node

    def connect(self, output: Pin, input: Pin) -> None:
        self.links = [link for link in self.links if link.end is not input]  # an input receives one link at most
        self.links.append(Link(output, input))

    def remove_node(self, node: Node) -> None:
        self.nodes.remove(node)
        self.links = [link for link in self.links if node not in (link.start.node, link.end.node)]

    def find_pin(self, pin_id: ed.PinId) -> Pin | None:
        for node in self.nodes:
            for pin in node.inputs + ([node.output] if node.output else []):
                if pin.id == pin_id:
                    return pin
        return None

    def feeds(self, node: Node, other: Node) -> bool:
        """True if `node` is `other`, or feeds it through links"""
        return node is other or any(self.feeds(node, link.start.node) for link in self.links if link.end.node is other)


def initial_graph() -> Graph:
    graph = Graph()
    red = graph.add_node("Color", ImVec2(0, 0), ImVec4(0.95, 0.2, 0.2, 1.0))
    blue = graph.add_node("Color", ImVec2(0, 9), ImVec4(0.2, 0.35, 0.95, 1.0))
    mix = graph.add_node("Mix", ImVec2(13, 4))
    swatch = graph.add_node("Swatch", ImVec2(26, 0))
    invert = graph.add_node("Invert", ImVec2(26, 10))
    swatch2 = graph.add_node("Swatch", ImVec2(39, 8))
    assert red.output and blue.output and mix.output and invert.output
    graph.connect(red.output, mix.inputs[0])
    graph.connect(blue.output, mix.inputs[1])
    graph.connect(mix.output, swatch.inputs[0])
    graph.connect(mix.output, invert.inputs[0])
    graph.connect(invert.output, swatch2.inputs[0])
    return graph


# =====================================================================================================================
# 2. What the nodes compute
# =====================================================================================================================
# Colors are cheap: the whole graph is computed again at each frame, from each node back to its sources.
def input_color(graph: Graph, pin: Pin) -> ImVec4:
    for link in graph.links:
        if link.end is pin:
            return node_color(graph, link.start.node)
    return UNLINKED


def node_color(graph: Graph, node: Node) -> ImVec4:
    """The color that a node gives (for a swatch: the color it shows)"""
    inputs = [input_color(graph, pin) for pin in node.inputs]
    if node.kind == "Color":
        return node.color
    if node.kind == "Mix":
        a, b, t = inputs[0], inputs[1], node.mix
        return a * (1.0 - t) + b * t
    c = inputs[0]
    if node.kind == "Invert":
        return ImVec4(1.0 - c.x, 1.0 - c.y, 1.0 - c.z, c.w)
    if node.kind == "Grayscale":
        luminance = 0.299 * c.x + 0.587 * c.y + 0.114 * c.z
        return ImVec4(luminance, luminance, luminance, c.w)
    return c  # a swatch


# =====================================================================================================================
# 3. Drawing the graph
# =====================================================================================================================
# Between ed.begin() and ed.end(), a node is drawn with ordinary widgets, between ed.begin_node() and ed.end_node().
# The widgets drawn between ed.begin_pin() and ed.end_pin() become the pin: the user drags a link from them.
def draw_pin(pin: Pin, color: ImVec4) -> None:
    ed.begin_pin(pin.id, pin.kind)
    ed.pin_pivot_alignment(ImVec2(0.5, 0.5))  # the links reach the center of the circle...
    ed.pin_pivot_size(ImVec2(0, 0))  # ...and not the edge of the pin's rectangle
    radius = em_size(PIN_RADIUS_EM)
    top_left = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(2 * radius, 2 * radius))  # the space of the pin; the draw list paints it
    center = top_left + ImVec2(radius, radius)
    draw_list = imgui.get_window_draw_list()
    draw_list.add_circle_filled(center, radius, imgui.get_color_u32(color))
    draw_list.add_circle(center, radius, imgui.get_color_u32(imgui.Col_.text), thickness=1.5)
    ed.end_pin()


def draw_node(graph: Graph, node: Node) -> None:
    width = em_size(NODE_WIDTH_EM)
    ed.begin_node(node.id)
    imgui.push_id(node.id.id())  # the widgets of two nodes of the same kind need different ids
    rich_md.render(f"**{node.kind}**  \n{NODE_KINDS[node.kind].doc}")  # the title, and on the next line the doc

    for pin in node.inputs:  # the inputs, on the left
        draw_pin(pin, input_color(graph, pin))
        imgui.same_line()
        imgui.text(pin.name)

    # The widgets of the node. A color picker opens its popup from inside the node, as it would anywhere else.
    if node.kind == "Color":
        imgui.set_next_item_width(width)
        _, node.color = imgui.color_edit4("##color", node.color, imgui.ColorEditFlags_.no_alpha.value)
    elif node.kind == "Mix":
        imgui.set_next_item_width(width)
        _, node.mix = imgui.slider_float("##mix", node.mix, 0.0, 1.0, "t = %.2f")
    elif node.kind == "Swatch":
        swatch_size = em_size(SWATCH_SIZE_EM)
        imgui.color_button("##swatch", node_color(graph, node), 0, ImVec2(swatch_size, swatch_size))

    if node.output is not None:  # the output, on the right
        imgui.begin_horizontal("output", ImVec2(width, 0))
        imgui.spring()
        imgui.text(node.output.name)
        draw_pin(node.output, node_color(graph, node))
        imgui.end_horizontal()

    imgui.pop_id()
    ed.end_node()


def draw_links(graph: Graph) -> None:
    for link in graph.links:
        ed.link(link.id, link.start.id, link.end.id, node_color(graph, link.start.node), LINK_THICKNESS)


# =====================================================================================================================
# 4. Letting the user edit the graph
# =====================================================================================================================
# The editor tells what the user wants (a new link, a deletion); the app decides, and changes its graph.
def why_not(output: Pin, input: Pin, graph: Graph) -> str:
    """Why a link from `output` to `input` is refused ("" if it is accepted)"""
    if output.kind != ed.PinKind.output or input.kind != ed.PinKind.input:
        return "A link goes from an output (right) to an input (left)"
    if graph.feeds(input.node, output.node):
        return "This link would make a loop"
    return ""


def handle_new_links(graph: Graph) -> None:
    # ed.end_create() only when ed.begin_create() returned True
    if ed.begin_create(WHITE, 2.0):
        start_id, end_id = ed.PinId(), ed.PinId()
        # True while the user drags a link; the ids are filled with the pins at its two ends (0 when there is none
        # yet). The drag may start from an input or from an output.
        if ed.query_new_link(start_id, end_id):
            start, end = graph.find_pin(start_id), graph.find_pin(end_id)
            if start is not None and end is not None:  # the mouse is over a second pin
                output, input = (end, start) if start.kind == ed.PinKind.input else (start, end)
                reason = why_not(output, input, graph)
                if reason:
                    ed.reject_new_item(ImVec4(1.0, 0.3, 0.3, 1.0), 2.0)  # the link turns red
                    imgui.set_tooltip(reason)
                else:
                    imgui.set_tooltip("Release to link")
                    if ed.accept_new_item():  # True when the user releases the mouse
                        graph.connect(output, input)
        ed.end_create()


def handle_deletions(graph: Graph) -> None:
    if ed.begin_delete():
        # The Delete key, or ed.delete_node() below, sends the selected items here, one by one
        link_id = ed.LinkId()
        while ed.query_deleted_link(link_id):
            if ed.accept_deleted_item():
                graph.links = [link for link in graph.links if link.id != link_id]
        node_id = ed.NodeId()
        while ed.query_deleted_node(node_id):
            if ed.accept_deleted_item():
                graph.remove_node(next(node for node in graph.nodes if node.id == node_id))
        ed.end_delete()


@dataclass
class MenuState:
    new_node_position: ImVec2 = field(default_factory=ImVec2)  # where the background menu was opened
    node_id: ed.NodeId = field(default_factory=ed.NodeId)  # the node whose menu is open


def handle_menus(graph: Graph, menu: MenuState) -> None:
    if ed.show_background_context_menu():
        imgui.open_popup("Add a node")
        menu.new_node_position = ed.get_mouse_pos_on_canvas()  # in the editor's coordinates, as the node positions
    if imgui.begin_popup("Add a node"):
        for kind in NODE_KINDS:
            if imgui.menu_item_simple(kind):
                graph.add_node(kind, menu.new_node_position / em_size())
        imgui.end_popup()

    if ed.show_node_context_menu(menu.node_id):
        imgui.open_popup("Node")
    if imgui.begin_popup("Node"):
        if imgui.menu_item_simple("Delete"):
            ed.delete_node(menu.node_id)  # the node then goes through handle_deletions()
        imgui.end_popup()


# =====================================================================================================================
# 5. The app
# =====================================================================================================================
class AppState:
    def __init__(self) -> None:
        self.editor: ed.EditorContext | None = None  # the demo's own editor (see editor())
        self.graph: Graph | None = None  # created at the first frame: the node positions need the editor
        self.menu = MenuState()
        self.frame = 0


state = AppState()


def editor() -> ed.EditorContext:
    """The demo's own editor, with its own config, whatever the app that shows it: an app such as the bundle's explorer
    shows several node editor demos, which need different configs (the image pipeline wraps the text in its nodes)."""
    if state.editor is None:
        config = ed.Config()
        config.settings_file = None  # the demo places its nodes at start: nothing to save
        state.editor = ed.create_editor(config)
    return state.editor


def demo_gui() -> None:
    rich_md.render(HELP)
    previous_editor = ed.get_current_editor()
    ed.set_current_editor(editor())
    ed.begin("Color mixer")
    if state.graph is None:
        state.graph = initial_graph()
    for node in state.graph.nodes:
        draw_node(state.graph, node)
    draw_links(state.graph)
    handle_new_links(state.graph)
    handle_deletions(state.graph)
    handle_menus(state.graph, state.menu)
    ed.end()

    # Fit the graph in the view, once the editor knows the size of the nodes: at the third frame (at the second, the
    # fit has no effect). The navigation functions work after ed.end().
    if state.frame == 2:
        ed.navigate_to_content(0.0)
    state.frame += 1
    if previous_editor is not None:  # the app's own editor, if it has one
        ed.set_current_editor(previous_editor)


def main() -> None:
    # The demo creates its own node editor: no need for immapp's (with_node_editor)
    immapp.run(demo_gui, window_title="Node editor: a color mixer", window_size=(1100, 600), with_markdown=True,
               with_latex=True)


if __name__ == "__main__":
    main()
