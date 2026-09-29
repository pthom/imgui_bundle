"""Node editor: an image pipeline

An image flows through a graph of filters, and each node shows its result. Change a parameter, and the nodes
downstream follow at once. The patterns of [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) for a
real app: typed pins, links refused with a reason, a node created by dropping a link in empty space, menus, a group.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import cv2
import numpy as np
from numpy.typing import NDArray

from imgui_bundle import (
    imgui, immapp, implot, immvision, imgui_node_editor as ed, rich_md, hello_imgui, ImVec2, ImVec4, em_size,
    register_demos_assets_folder,
)

IMAGE_WIDTH_EM = 12.0  # the width of the images in the nodes: it also gives the nodes their width
HISTOGRAM_SIZE_EM = ImVec2(12.0, 6.0)  # the initial size of the histogram of a Levels node (the user can resize it)
PIN_RADIUS_EM = 0.45  # the radius of a pin's icon
LINK_THICKNESS = 3.0  # the thickness of the links (they follow the zoom)
IMAGES = ["images/house.jpg", "images/tennis.jpg"]  # the images an Image node can load, from the demos' assets

HELP = (
    "**Link** two pins: drag from one to the other; drop a link in empty space to add a node there  \n"
    "**Delete**: select, then <kbd>Delete</kbd>  ·  **Menus**: right-click  ·  **Pan**: right-drag  ·  "
    "**Zoom**: the wheel  ·  **See the whole graph**: <kbd>F</kbd>  ·  **Zoom in an image**: the wheel over it"
)

Image = NDArray[np.uint8]  # an OpenCV image: height x width (x 3 for a color image, in RGB order)

register_demos_assets_folder()


# =====================================================================================================================
# 1. The types of the pins
# =====================================================================================================================
# Each pin carries a type of image. A link is accepted when the input can take the output's type: a gray image can go
# where a color image is expected (it is converted), but not the reverse.
class PinType(Enum):
    COLOR = "a color image"
    GRAY = "a gray image"


PIN_COLORS = {PinType.COLOR: ImVec4(0.95, 0.6, 0.25, 1.0), PinType.GRAY: ImVec4(0.7, 0.78, 0.85, 1.0)}


def accepts(input_type: PinType, output_type: PinType) -> bool:
    return input_type == PinType.COLOR or output_type == PinType.GRAY


# =====================================================================================================================
# 2. The nodes: one class per filter
# =====================================================================================================================
# The editor draws the graph, but the app owns it: its nodes, pins and links, each with an id that stays the same from
# one frame to the next (ed.NodeId.create() gives a new unique one).
@dataclass(eq=False)
class Pin:
    name: str
    type: PinType
    kind: ed.PinKind  # an input (on the left of its node) or an output (on the right)
    node: Node
    id: ed.PinId = field(default_factory=ed.PinId.create)


class Node:
    """A filter: its pins, its parameters, and what it computes. The subclasses below fill the class attributes."""
    title = ""
    doc = ""  # what it does, under its title (markdown, with math between $ signs)
    input_types: list[tuple[str, PinType]] = []
    output_type = PinType.COLOR

    def __init__(self) -> None:
        self.id = ed.NodeId.create()
        self.inputs = [Pin(name, pin_type, ed.PinKind.input, self) for name, pin_type in self.input_types]
        self.output = Pin("out", self.output_type, ed.PinKind.output, self)
        # The state of the evaluation (see section 3)
        self.image: Image | None = None  # the last result
        self.error = ""  # why there is no result
        self.version = 0  # increases with each new result
        self.inputs_versions: tuple[int, ...] = ()  # the versions of the inputs that gave the last result
        self.params_changed = True  # set by the widgets of the parameters
        self.computed_frame = -1  # the frame of the last result (its output links then show the data flowing)
        self.image_params = immvision.ImageParams()  # how the node shows its image
        self.image_params.image_display_size = (int(em_size(IMAGE_WIDTH_EM)), 0)
        for tool in ("show_options_button", "show_zoom_buttons", "show_image_info", "show_pixel_info"):
            setattr(self.image_params, tool, False)  # the image alone: zoom and pan stay, with the mouse

    def draw_params(self) -> bool:
        """Draws the widgets of the parameters, and returns True when one of them changed"""
        return False

    def compute(self, inputs: list[Image]) -> Image:
        raise NotImplementedError


class ImageFile(Node):
    title = "Image"
    doc = "An image of the demos' assets"

    def __init__(self, index: int = 0) -> None:
        super().__init__()
        self.index = index

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed, self.index = imgui.combo("##file", self.index, IMAGES)  # its popup opens from inside the node
        return changed

    def compute(self, inputs: list[Image]) -> Image:
        path = hello_imgui.asset_file_full_path(IMAGES[self.index])
        return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)  # type: ignore  # OpenCV reads in BGR order


class Grayscale(Node):
    title = "Grayscale"
    doc = r"The luminance: $0.3\,r + 0.59\,g + 0.11\,b$"
    input_types = [("in", PinType.COLOR)]
    output_type = PinType.GRAY

    def compute(self, inputs: list[Image]) -> Image:
        return cv2.cvtColor(inputs[0], cv2.COLOR_RGB2GRAY)  # type: ignore


class Blur(Node):
    title = "Blur"
    doc = "A [Gaussian blur](https://en.wikipedia.org/wiki/Gaussian_blur): fewer, smoother edges downstream"
    input_types = [("in", PinType.GRAY)]
    output_type = PinType.GRAY

    def __init__(self) -> None:
        super().__init__()
        self.sigma = 1.5

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed, self.sigma = imgui.slider_float("##sigma", self.sigma, 0.1, 10.0, "sigma = %.1f")
        imgui.set_item_tooltip("The standard deviation of the Gaussian, in pixels: the larger, the blurrier")
        return changed

    def compute(self, inputs: list[Image]) -> Image:
        return cv2.GaussianBlur(inputs[0], (0, 0), sigmaX=self.sigma)  # type: ignore


class Edges(Node):
    title = "Edges"
    doc = "The [Canny edge detector](https://en.wikipedia.org/wiki/Canny_edge_detector)"
    input_types = [("in", PinType.GRAY)]
    output_type = PinType.GRAY

    def __init__(self) -> None:
        super().__init__()
        self.low, self.high = 40.0, 100.0

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed_low, self.low = imgui.slider_float("##low", self.low, 0.0, 300.0, "low = %.0f")
        imgui.set_item_tooltip("A pixel whose gradient is below this threshold is never an edge")
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed_high, self.high = imgui.slider_float("##high", self.high, 0.0, 300.0, "high = %.0f")
        imgui.set_item_tooltip("A pixel whose gradient is above this threshold is always an edge; between the two, "
                               "only when it touches an edge")
        return changed_low or changed_high

    def compute(self, inputs: list[Image]) -> Image:
        return cv2.Canny(inputs[0], self.low, self.high)  # type: ignore


class Threshold(Node):
    title = "Threshold"
    doc = "White where the image is brighter than the level, black elsewhere"
    input_types = [("in", PinType.GRAY)]
    output_type = PinType.GRAY

    def __init__(self) -> None:
        super().__init__()
        self.level = 128

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed, self.level = imgui.slider_int("##level", self.level, 0, 255, "level = %d")
        return changed

    def compute(self, inputs: list[Image]) -> Image:
        return cv2.threshold(inputs[0], self.level, 255, cv2.THRESH_BINARY)[1]  # type: ignore


class Dilate(Node):
    title = "Dilate"
    doc = "[Dilation](https://en.wikipedia.org/wiki/Dilation_(morphology)): the white areas grow"
    input_types = [("in", PinType.GRAY)]
    output_type = PinType.GRAY

    def __init__(self) -> None:
        super().__init__()
        self.size = 3

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed, self.size = imgui.slider_int("##size", self.size, 1, 9, "size = %d")
        imgui.set_item_tooltip("The size of the disk that dilates the image, in pixels (1: no change)")
        return changed

    def compute(self, inputs: list[Image]) -> Image:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.size, self.size))
        return cv2.dilate(inputs[0], kernel)  # type: ignore


class Colorize(Node):
    title = "Colorize"
    doc = r"Paints the gray image: $g \cdot c$"
    input_types = [("in", PinType.GRAY)]
    output_type = PinType.COLOR

    def __init__(self) -> None:
        super().__init__()
        self.color = ImVec4(0.3, 0.85, 1.0, 1.0)

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        # A color picker: its popup opens from inside the node
        changed, self.color = imgui.color_edit4("##color", self.color, imgui.ColorEditFlags_.no_alpha.value)
        return changed

    def compute(self, inputs: list[Image]) -> Image:
        rgb = np.array([self.color.x, self.color.y, self.color.z])
        return (inputs[0][:, :, np.newaxis] * rgb).astype(np.uint8)  # type: ignore


class Levels(Node):
    title = "Levels"
    doc = "Drag the black and white points on the histogram"
    input_types = [("in", PinType.COLOR)]

    def __init__(self) -> None:
        super().__init__()
        self.black, self.white, self.gamma = 20.0, 235.0, 1.0
        self.histogram_size_em = HISTOGRAM_SIZE_EM
        self.histograms: list[NDArray[np.float64]] = []  # of the input image, one per channel

    def draw_params(self) -> bool:
        changed = False

        def plot_histogram() -> None:
            nonlocal changed
            implot.setup_axes("", "", implot.AxisFlags_.no_tick_labels.value, implot.AxisFlags_.no_decorations.value)
            # The square root of the counts: a few very frequent values (a white sky) would flatten the others
            heights = [np.sqrt(histogram) for histogram in self.histograms]
            implot.setup_axes_limits(0, 255, 0, max((h.max() for h in heights), default=1) * 1.05,
                                     implot.Cond_.always.value)
            x = np.arange(256, dtype=np.float64)
            for height, name, color in zip(heights, "RGB", CHANNEL_COLORS, strict=True):
                implot.plot_shaded(name, x, height, 0, implot.Spec(fill_color=color, fill_alpha=0.3))
                implot.plot_line(name, x, height, implot.Spec(line_color=color))
            # Two vertical lines that the user drags. The plot keeps the mouse: dragging does not move the node.
            changed_black, self.black, *_ = implot.drag_line_x(0, self.black, ImVec4(0.2, 0.2, 0.2, 1.0), 3)
            changed_white, self.white, *_ = implot.drag_line_x(1, self.white, ImVec4(1.0, 1.0, 1.0, 1.0), 3)
            self.black = float(np.clip(self.black, 0, self.white - 1))
            self.white = float(np.clip(self.white, self.black + 1, 255))
            changed = changed or changed_black or changed_white

        # A plot inside a node, with a handle at its bottom right corner to resize it
        flags = implot.Flags_.no_legend.value | implot.Flags_.no_menus.value | implot.Flags_.no_box_select.value
        self.histogram_size_em = immapp.show_resizable_plot_in_node_editor_em(
            "##histogram", self.histogram_size_em, plot_histogram, flags)
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed_gamma, self.gamma = imgui.slider_float("##gamma", self.gamma, 0.2, 3.0, "gamma = %.2f")
        imgui.set_item_tooltip("Above 1, the midtones get brighter")
        return changed or changed_gamma

    def compute(self, inputs: list[Image]) -> Image:
        self.histograms = [np.bincount(inputs[0][:, :, c].ravel(), minlength=256).astype(np.float64) for c in range(3)]
        x = np.clip((np.arange(256) - self.black) / (self.white - self.black), 0.0, 1.0)
        lut = (x ** (1.0 / self.gamma) * 255.0).astype(np.uint8)
        return cv2.LUT(inputs[0], lut)  # type: ignore


CHANNEL_COLORS = [ImVec4(1.0, 0.3, 0.3, 1.0), ImVec4(0.3, 1.0, 0.3, 1.0), ImVec4(0.35, 0.5, 1.0, 1.0)]


class Blend(Node):
    title = "Blend"
    doc = r"Mix: $(1-t)\,a + t\,b$  " "\n" r"Add: $a + t\,b$"
    input_types = [("a", PinType.COLOR), ("b", PinType.COLOR)]
    MODES = ["Mix", "Add"]

    def __init__(self) -> None:
        super().__init__()
        self.mode, self.t = 1, 1.0

    def draw_params(self) -> bool:
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed_mode, self.mode = imgui.combo("##mode", self.mode, self.MODES)
        imgui.set_next_item_width(em_size(IMAGE_WIDTH_EM))
        changed_t, self.t = imgui.slider_float("##t", self.t, 0.0, 1.0, "t = %.2f")
        return changed_mode or changed_t

    def compute(self, inputs: list[Image]) -> Image:
        a, b = inputs
        b = cv2.resize(b, (a.shape[1], a.shape[0]))  # type: ignore  # b takes the size of a
        if self.MODES[self.mode] == "Mix":
            return cv2.addWeighted(a, 1.0 - self.t, b, self.t, 0.0)  # type: ignore
        return cv2.addWeighted(a, 1.0, b, self.t, 0.0)  # type: ignore  # saturates at 255


NODE_CLASSES: list[type[Node]] = [ImageFile, Grayscale, Blur, Edges, Threshold, Dilate, Colorize, Levels, Blend]


# =====================================================================================================================
# 3. The graph, and its evaluation
# =====================================================================================================================
@dataclass(eq=False)
class Link:
    start: Pin  # an output
    end: Pin  # an input
    id: ed.LinkId = field(default_factory=ed.LinkId.create)


@dataclass(eq=False)
class Group:
    """A frame behind some nodes, with a title: dragging it moves the nodes inside"""
    title: str
    size_em: ImVec2
    id: ed.NodeId = field(default_factory=ed.NodeId.create)


class Graph:
    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.links: list[Link] = []
        self.groups: list[Group] = []

    def add_node(self, node: Node, position: ImVec2) -> Node:
        """Adds a node at a position in the editor's coordinates (pixels at zoom 1)"""
        self.nodes.append(node)
        ed.set_node_position(node.id, position)  # the editor keeps the positions: we only give the first one
        return node

    def add_group(self, group: Group, position: ImVec2) -> None:
        self.groups.append(group)
        ed.set_node_position(group.id, position)

    def connect(self, output: Pin, input: Pin) -> None:
        self.links = [link for link in self.links if link.end is not input]  # an input receives one link at most
        self.links.append(Link(output, input))

    def link_to(self, input: Pin) -> Link | None:
        return next((link for link in self.links if link.end is input), None)

    def remove(self, node_id: ed.NodeId) -> None:
        """Removes a node and its links, or a group"""
        self.groups = [group for group in self.groups if group.id != node_id]
        self.nodes = [node for node in self.nodes if node.id != node_id]
        self.links = [link for link in self.links if link.start.node in self.nodes and link.end.node in self.nodes]

    def find_pin(self, pin_id: ed.PinId) -> Pin | None:
        for node in self.nodes:
            for pin in node.inputs + [node.output]:
                if pin.id == pin_id:
                    return pin
        return None

    def feeds(self, node: Node, other: Node) -> bool:
        """True if `node` is `other`, or feeds it through links"""
        return node is other or any(self.feeds(node, link.start.node) for link in self.links if link.end.node is other)


def evaluate(graph: Graph, node: Node) -> None:
    """Computes the node's image again if its parameters, or the images it receives, changed.

    Its sources are evaluated first (a pull). A version number tells whether an image changed: this is cheaper than
    comparing the images, and it follows the new links too."""
    sources = []
    for pin in node.inputs:
        link = graph.link_to(pin)
        if link is not None:
            evaluate(graph, link.start.node)
        sources.append(link.start.node if link is not None else None)
    versions = tuple(source.version if source is not None else -1 for source in sources)
    if not node.params_changed and versions == node.inputs_versions:
        return

    node.params_changed, node.inputs_versions = False, versions
    node.version += 1
    node.computed_frame = imgui.get_frame_count()
    node.image_params.refresh_image = True  # ImmVision keeps a texture of each image: it must know of a new one
    missing = [pin.name for pin, source in zip(node.inputs, sources, strict=True)
               if source is None or source.image is None]
    if missing:
        node.image, node.error = None, "Waiting for an image on: " + ", ".join(missing)
        return
    inputs = []
    for pin, source in zip(node.inputs, sources, strict=True):
        assert source is not None and source.image is not None
        image = source.image
        if pin.type == PinType.COLOR and image.ndim == 2:  # a gray image where a color image is expected
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # type: ignore
        inputs.append(image)
    node.image, node.error = node.compute(inputs), ""


def initial_graph() -> Graph:
    em = em_size()
    graph = Graph()
    graph.add_group(Group("Draw the edges", ImVec2(62, 24)), ImVec2(15, 27) * em)
    image = graph.add_node(ImageFile(), ImVec2(0, 0) * em)
    levels = graph.add_node(Levels(), ImVec2(17, 0) * em)
    gray = graph.add_node(Grayscale(), ImVec2(16, 30) * em)
    blur = graph.add_node(Blur(), ImVec2(31, 30) * em)
    edges = graph.add_node(Edges(), ImVec2(46, 30) * em)
    dilate = graph.add_node(Dilate(), ImVec2(61, 30) * em)
    colorize = graph.add_node(Colorize(), ImVec2(79, 16) * em)
    blend = graph.add_node(Blend(), ImVec2(96, 4) * em)
    chain = [(image, levels, 0), (image, gray, 0), (gray, blur, 0), (blur, edges, 0), (edges, dilate, 0),
             (dilate, colorize, 0), (levels, blend, 0), (colorize, blend, 1)]
    for source, target, input_index in chain:
        graph.connect(source.output, target.inputs[input_index])
    return graph


# =====================================================================================================================
# 4. Drawing the graph
# =====================================================================================================================
def draw_pin(pin: Pin, linked: bool) -> None:
    """A pin's icon: a circle for a color image, a square for a gray one; filled when linked"""
    ed.begin_pin(pin.id, pin.kind)
    ed.pin_pivot_alignment(ImVec2(0.5, 0.5))  # the links reach the center of the icon...
    ed.pin_pivot_size(ImVec2(0, 0))  # ...and not the edge of the pin's rectangle
    radius = em_size(PIN_RADIUS_EM)
    top_left = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(2 * radius, 2 * radius))  # the space of the pin; the draw list paints it
    center = top_left + ImVec2(radius, radius)
    color = imgui.get_color_u32(PIN_COLORS[pin.type])
    draw_list = imgui.get_window_draw_list()
    if pin.type == PinType.COLOR:
        draw_list.add_circle(center, radius, color, thickness=2.0)
        if linked:
            draw_list.add_circle_filled(center, radius * 0.6, color)
    else:
        half = ImVec2(radius * 0.85, radius * 0.85)
        draw_list.add_rect(center - half, center + half, color, thickness=2.0)
        if linked:
            draw_list.add_rect_filled(center - half * 0.6, center + half * 0.6, color)
    ed.end_pin()
    imgui.set_item_tooltip(f"{pin.name}: {pin.type.value}")


def draw_node(graph: Graph, node: Node) -> None:
    width = em_size(IMAGE_WIDTH_EM)
    ed.begin_node(node.id)
    imgui.push_id(node.id.id())  # the widgets of two nodes of the same kind need different ids
    # The editor wraps the text at the width of the node (see main()). So the node needs an item with a fixed width,
    # first: text alone would give it no width, and it would collapse to one character per line.
    imgui.dummy(ImVec2(width, 0))
    rich_md.render(f"**{node.title}**  \n{node.doc}")

    for pin in node.inputs:  # the inputs, on the left
        draw_pin(pin, graph.link_to(pin) is not None)
        imgui.same_line()
        imgui.text(pin.name)

    node.params_changed |= node.draw_params()

    if node.error:
        imgui.text_colored(ImVec4(1.0, 0.55, 0.3, 1.0), node.error)
    elif node.image is not None:
        immvision.image("##image", node.image, node.image_params)  # zoom with the wheel, pan with a drag
        node.image_params.refresh_image = False
        if imgui.is_item_hovered():
            ed.disable_user_input_this_frame()  # the wheel zooms the image, not the graph

    imgui.begin_horizontal("output", ImVec2(width, 0))  # the output, on the right
    imgui.spring()
    imgui.text(node.output.name)
    draw_pin(node.output, any(link.start is node.output for link in graph.links))
    imgui.end_horizontal()

    imgui.pop_id()
    ed.end_node()


def draw_group(group: Group) -> None:
    ed.push_style_color(ed.StyleColor.node_bg, ImVec4(1.0, 1.0, 1.0, 0.05))
    ed.push_style_color(ed.StyleColor.node_border, ImVec4(1.0, 1.0, 1.0, 0.25))
    ed.begin_node(group.id)
    rich_md.render(f"**{group.title}**")
    ed.group(group.size_em * em_size())  # its size at creation; then the user resizes it
    ed.end_node()
    ed.pop_style_color(2)


def draw_links(graph: Graph) -> None:
    for link in graph.links:
        ed.link(link.id, link.start.id, link.end.id, PIN_COLORS[link.start.type], LINK_THICKNESS)
        if link.start.node.computed_frame == imgui.get_frame_count():
            ed.flow(link.id)  # a new image runs along the link


# =====================================================================================================================
# 5. Letting the user edit the graph
# =====================================================================================================================
# The editor tells what the user wants (a new link, a new node, a deletion); the app decides, and changes its graph.
def why_not(output: Pin, input: Pin, graph: Graph) -> str:
    """Why a link from `output` to `input` is refused ("" if it is accepted)"""
    if output.kind != ed.PinKind.output or input.kind != ed.PinKind.input:
        return "A link goes from an output (right) to an input (left)"
    if graph.feeds(input.node, output.node):
        return "This link would make a loop"
    if not accepts(input.type, output.type):
        return f"{input.node.title} needs {input.type.value}: add a Grayscale node before it"
    return ""


def can_link(pin: Pin, node_class: type[Node]) -> bool:
    """Whether a new node of this class could be linked to a pin"""
    if pin.kind == ed.PinKind.output:
        return any(accepts(input_type, pin.type) for _, input_type in node_class.input_types)
    return accepts(pin.type, node_class.output_type)


class MenuState:
    def __init__(self) -> None:
        self.dropped_pin: Pin | None = None  # the pin of a link dropped in empty space: the new node is linked to it
        self.position = ImVec2(0, 0)  # where the add menu opened, in the editor's coordinates
        self.node_id = ed.NodeId()  # the node whose menu is open
        self.link_id = ed.LinkId()  # the link whose menu is open


def handle_creations(graph: Graph, menu: MenuState) -> None:
    # ed.end_create() only when ed.begin_create() returned True
    if ed.begin_create(ImVec4(1.0, 1.0, 1.0, 1.0), 2.0):
        start_id, end_id = ed.PinId(), ed.PinId()
        # True while the user drags a link between two pins (the drag may start from an input or from an output)
        if ed.query_new_link(start_id, end_id):
            start, end = graph.find_pin(start_id), graph.find_pin(end_id)
            if start is not None and end is not None:
                output, input = (end, start) if start.kind == ed.PinKind.input else (start, end)
                reason = why_not(output, input, graph)
                if reason:
                    ed.reject_new_item(ImVec4(1.0, 0.3, 0.3, 1.0), 2.0)  # the link turns red
                    imgui.set_tooltip(reason)
                else:
                    imgui.set_tooltip("Release to link")
                    if ed.accept_new_item():  # True when the user releases the mouse
                        graph.connect(output, input)
        pin_id = ed.PinId()
        # True while the user drags a link from a pin to empty space
        if ed.query_new_node(pin_id):
            imgui.set_tooltip("Release to add a node linked to this pin")
            if ed.accept_new_item():
                open_add_menu(menu, graph.find_pin(pin_id))
        ed.end_create()


def handle_deletions(graph: Graph) -> None:
    if ed.begin_delete():
        # The Delete key, and the menus below, send the items to delete here, one by one
        link_id = ed.LinkId()
        while ed.query_deleted_link(link_id):
            if ed.accept_deleted_item():
                graph.links = [link for link in graph.links if link.id != link_id]
        node_id = ed.NodeId()
        while ed.query_deleted_node(node_id):
            if ed.accept_deleted_item():
                graph.remove(node_id)
        ed.end_delete()


def open_add_menu(menu: MenuState, dropped_pin: Pin | None) -> None:
    imgui.open_popup("Add a node")
    menu.dropped_pin = dropped_pin
    # The mouse in the editor's coordinates, those of the node positions. imgui.get_mouse_pos() gives them too, but not
    # in handle_creations(): once a query returned True, the editor is suspended, and it gives screen coordinates.
    menu.position = ed.get_mouse_pos_on_canvas()


def handle_menus(graph: Graph, menu: MenuState) -> None:
    if ed.show_background_context_menu():
        open_add_menu(menu, None)
    if imgui.begin_popup("Add a node"):
        pin = menu.dropped_pin
        for node_class in NODE_CLASSES:
            if pin is not None and not can_link(pin, node_class):
                continue
            if imgui.menu_item_simple(node_class.title):
                node = graph.add_node(node_class(), menu.position)
                if pin is not None and pin.kind == ed.PinKind.output:
                    graph.connect(pin, next(i for i in node.inputs if accepts(i.type, pin.type)))
                elif pin is not None:
                    graph.connect(node.output, pin)
        imgui.end_popup()

    if ed.show_node_context_menu(menu.node_id):
        imgui.open_popup("Node")
    if imgui.begin_popup("Node"):
        if imgui.menu_item_simple("Delete"):
            ed.delete_node(menu.node_id)  # the node then goes through handle_deletions()
        imgui.end_popup()
    if ed.show_link_context_menu(menu.link_id):
        imgui.open_popup("Link")
    if imgui.begin_popup("Link"):
        if imgui.menu_item_simple("Delete"):
            ed.delete_link(menu.link_id)
        imgui.end_popup()


# =====================================================================================================================
# 6. The GUI function
# =====================================================================================================================
class AppState:
    def __init__(self) -> None:
        self.graph: Graph | None = None  # created at the first frame: the node positions need the editor
        self.menu = MenuState()
        self.frame = 0  # since the graph was created


state = AppState()


def demo_gui() -> None:
    rich_md.render(HELP)
    if imgui.button("Reset the graph"):
        state.graph, state.frame = None, 0
    ed.begin("Image pipeline")
    if state.graph is None:
        state.graph = initial_graph()
    for node in state.graph.nodes:
        evaluate(state.graph, node)
    for group in state.graph.groups:  # the groups first: they are behind the nodes
        draw_group(group)
    for node in state.graph.nodes:
        draw_node(state.graph, node)
    draw_links(state.graph)
    handle_creations(state.graph, state.menu)
    handle_deletions(state.graph)
    handle_menus(state.graph, state.menu)
    ed.end()

    # Fit the graph in the view, once the editor knows the size of the nodes: at the third frame (at the second, the
    # fit has no effect). The navigation functions work after ed.end().
    if state.frame == 2:
        ed.navigate_to_content(0.0)
    state.frame += 1


def main() -> None:
    config = ed.Config()
    # Inside a node, text wraps at the width of the node, and separators span it (instead of the width of the window).
    # A node then needs an item with a fixed width: see draw_node().
    config.force_window_content_width_to_node_width = True
    immapp.run(demo_gui, window_title="Node editor: an image pipeline", window_size=(1400, 850),
               with_node_editor_config=config, with_markdown=True, with_latex=True, with_implot=True)


if __name__ == "__main__":
    main()
