from typing import Any as _
from dataclasses import dataclass
from imgui_bundle.demos.haikus.romeo_and_juliet.characters_and_intrigues_glossary import *


"""
            ======= Character and Intrigues Mechanics ======
"""


class Character:
    def __init__(my, name):
        my.name = name
        my.soul = soul()
        my.loves = conundrum()
        my.enemies = conundrum()
        my.social_being = conundrum()

    def fate_in_action(my):
        lament(my.soul)
        I(my.name, my.social_being)
        I("love", my.loves)
        I("hate", my.enemies)
        sober()


@dataclass
class Intrigue:
    hero: _
    deeply: _
    feels: _
    for_character: _

    def fate_in_action(_):
        start_intrigue(_)
        if _.feels.startswith("love"):
            love_intrigue(_)
        else:
            feud(_)


"""
            ======= Romeo and Juliet ====
"""

Romeo = Character("Romeo")
Juliet = Character("Juliet")
Count_Paris = Character("Count Paris")
Mercutio = Character("Mercutio")
Characters = [Romeo, Juliet, Count_Paris, Mercutio]
Love_Intrigues = [
    Intrigue(Romeo, tenderly, "loves", Juliet),
    Intrigue(Juliet, tenderly, "loves", Romeo),
    Intrigue(Mercutio, tenderly, "loves", Romeo),
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
