"""
            ======= Glossary ====
"""
from imgui_bundle import run, imgui, imgui_node_editor as ed, ImVec4, ImVec2

conundrum = ed.PinId.create
soul = ed.NodeId.create
lament = ed.begin_node
sober = ed.end_node
Title = ed.begin
the_end = ed.end
tenderly = ImVec4(0.3, 0.9, 0.4, 1.0)
ferociously = ImVec4(0.9, 0.3, 0.2, 1.0)


def love_intrigue(intrigue):
    ed.link(intrigue.id, intrigue.hero.loves, intrigue.for_character.social_being, intrigue.deeply)


def feud(intrigue):
    ed.link(intrigue.id, intrigue.hero.enemies, intrigue.for_character.social_being, intrigue.deeply)


def I(what: str, soul):
    if what in ["love", "hate"]:
        what += "s"
        pin_kind = ed.PinKind.output
    else:
        pin_kind = ed.PinKind.input
    ed.begin_pin(soul, pin_kind)
    imgui.text(what)
    ed.end_pin()


def start_intrigue(_):
    if not hasattr(_, "id"):
        _.id = ed.LinkId.create()


def begin_the(gui):
    run(gui, with_node_editor=True, window_size=(600, 600))
