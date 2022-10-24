from imgui_bundle import run, imgui, imgui_node_editor as ed, ImVec4, ImVec2


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
        ed.begin_pin(self.pin_loves, ed.PinKind.output), imgui.text("Loves")
        ed.end_pin()
        ed.begin_pin(self.pin_hates, ed.PinKind.output)
        imgui.text("Hates")
        ed.end_pin()
        ed.end_node()


class Tie:
    lover: Lover
    loved: Lover
    kind: str

    def __init__(self, lover: Lover, kind: str, loved: Lover) -> None:
        self.lover = lover
        self.loved = loved
        self.kind = kind
        self.id = ed.LinkId.create()

    def draw(self) -> None:
        red = ImVec4(0.3, 0.8, 0.2, 1.0)
        green = ImVec4(1.0, 0.0, 0.0, 1.0)
        if self.kind == "loves":
            ed.link(self.id, self.lover.pin_loves, self.loved.pin_in, green)
        else:
            ed.link(self.id, self.lover.pin_hates, self.loved.pin_in, red)


paul = Lover("Paul")
claire = Lover("Claire")
cesar = Lover("Cesar")
lovers = [paul, claire, cesar]
links = [
    Tie(paul, "loves", claire),
    Tie(claire, "loves", paul),
    Tie(cesar, "loves", claire),
    Tie(cesar, "hates", paul),
    Tie(claire, "hates", cesar),
]


def gui():
    ed.begin("Love ed.PinId.create")
    for lover in lovers:
        lover.draw()
    for link in links:
        link.draw()
    ed.end()


run(gui, with_node_editor=True, window_size=ImVec2(300, 300), window_title="It will not end well...")
