"""
            ======= Glossary ====
"""
from dataclasses import dataclass
from imgui_bundle import run, imgui, imgui_node_editor as ed, ImVec4
from typing import Any as _
conundrum = ed.PinId.create
soul = ed.NodeId.create
lament = ed.begin_node
sober = ed.end_node
Title = ed.begin
the_end = ed.end
tenderly = ImVec4(0.3, 0.8, 0.2, 1.)
ferociously = ImVec4(1., 0., 0., 1.)


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
    run(gui, with_node_editor=True)


"""
            ======= Character and Intrigues Mechanics ======
"""


class Character:
    def __init__(my, name):
        my.name = name
        my.soul = soul(); my.loves = conundrum(); my.enemies = conundrum(); my.social_being = conundrum()

    def fate_in_action(my):
        lament(my.soul)
        I(my.name, my.social_being)
        I("love", my.loves); I("hate", my.enemies)
        sober()


@dataclass
class Intrigue:
    hero: _;  deeply: _;  feels: _; for_character: _

    def fate_in_action(_):
        start_intrigue(_)
        if _.feels == "loves":
            love_intrigue(_)
        else:
            feud(_)


"""
            ======= Romeo and Juliet ====
"""

Romeo = Character("Romeo"); Juliet = Character("Juliet"); Count_Paris = Character("Count Paris")
Characters = [Romeo, Juliet, Count_Paris]
Love_Intrigues = [
    Intrigue(Romeo, tenderly, "loves", Juliet),
    Intrigue(Juliet, tenderly, "loves", Romeo),
    Intrigue(Count_Paris, tenderly, "loves", Juliet),
    Intrigue(Count_Paris, ferociously, "hates", Romeo),
    Intrigue(Juliet, ferociously, "hates", Count_Paris),
]


def tragedy():
    Title("Romeo and Juliet")
    for _ in Characters + Love_Intrigues:
        _.fate_in_action()
    the_end()


begin_the(tragedy)
