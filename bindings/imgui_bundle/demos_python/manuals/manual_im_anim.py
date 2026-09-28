"""ImAnim: the interactive manual

The animations of [ImAnim](https://github.com/SoufianeKHIAT/ImAnim), section by section, with the code of each beside
it. Tweens, easings, oscillators, delays, callbacks, stagger, loops and chains, in Python and C++. From
[Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive manual for Dear ImGui and its libraries.
"""
from imgui_bundle import imgui, immapp

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]


def fallback() -> None:
    imgui.text("The ImAnim manual needs the imgui_explorer library, absent from this build.")


def demo_gui() -> None:
    show_manual("im_anim", fallback=fallback)


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1100, 800), with_markdown=True, with_im_anim=True)
