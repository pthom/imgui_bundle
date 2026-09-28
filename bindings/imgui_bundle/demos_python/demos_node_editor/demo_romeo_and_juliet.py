"""Node editor: Romeo, Juliet and Count Paris

Three characters as nodes, their feelings as links: green for love, red for hate. Drag the nodes around, and follow
the links. A small graph with [imgui-node-editor](https://github.com/thedmd/imgui-node-editor).
"""
from imgui_bundle import immapp, imgui, imgui_node_editor as ed, ImVec4, ImVec2

first_frame = True


class Lover:
    name: str
    node_id: ed.NodeId
    pin_loves: ed.PinId
    pin_hates: ed.PinId
    pin_in: ed.PinId

    def __init__(self, name: str) -> None:
        self.name = name
        self.node_id = ed.NodeId.create()
        self.pin_loves = ed.PinId.create()
        self.pin_hates = ed.PinId.create()
        self.pin_in = ed.PinId.create()

    def draw(self) -> None:
        ed.begin_node(self.node_id)
        ed.begin_pin(self.pin_in, ed.PinKind.input)
        imgui.text(self.name)
        ed.end_pin()
        ed.begin_pin(self.pin_loves, ed.PinKind.output)
        imgui.text("Loves")
        ed.end_pin()
        ed.begin_pin(self.pin_hates, ed.PinKind.output)
        imgui.text("Hates")
        ed.end_pin()
        ed.end_node()


class Tie:
    lover: Lover
    loved: Lover
    kind: str
    id: ed.LinkId

    def __init__(self, lover: Lover, kind: str, loved: Lover) -> None:
        self.id = ed.LinkId.create()
        self.lover = lover
        self.loved = loved
        self.kind = kind

    def draw(self) -> None:
        red = ImVec4(1.0, 0.3, 0.2, 1.0)
        green = ImVec4(0.3, 0.9, 0.0, 1.0)
        if self.kind == "loves":
            ed.link(self.id, self.lover.pin_loves, self.loved.pin_in, green)
        else:
            ed.link(self.id, self.lover.pin_hates, self.loved.pin_in, red)


Romeo = Lover("Romeo")
Juliet = Lover("Juliet")
CountParis = Lover("Count Paris")
lovers = [Romeo, Juliet, CountParis]
links = [
    Tie(Romeo, "loves", Juliet),
    Tie(Juliet, "loves", Romeo),
    Tie(CountParis, "loves", Juliet),
    Tie(CountParis, "hates", Romeo),
    Tie(Romeo, "hates", CountParis),
]


def demo_gui():
    global first_frame
    ed.begin("Romeo and Juliet")

    # Position nodes as a triangle on first frame, near the origin: the default view shows them whole
    if first_frame:
        ed.set_node_position(lovers[0].node_id, ImVec2(200, 40))   # Romeo - top
        ed.set_node_position(lovers[1].node_id, ImVec2(350, 240))  # Juliet - bottom right
        ed.set_node_position(lovers[2].node_id, ImVec2(50, 240))   # Count Paris - bottom left
        first_frame = False

    for lover in lovers:
        lover.draw()
    for link in links:
        link.draw()
    ed.end()


if __name__ == "__main__":
    immapp.run(demo_gui, with_node_editor=True, window_size=(1000, 800), window_title="It will not end well...")
