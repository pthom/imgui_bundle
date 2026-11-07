"""ImGuiKit: the interactive manual

The additions of [ImGuiKit](https://github.com/pthom/imgui_kit) to Dear ImGui, section by section, with the code of
each beside it. Em units, rows that fill, aligned groups, label columns, a help marker for mouse and touch, a segmented
switch, in Python and C++. From [Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive manual
for Dear ImGui and its libraries.
"""
from imgui_bundle import imgui, immapp

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]


def fallback() -> None:
    imgui.text("The ImGuiKit manual needs the imgui_explorer library, absent from this build.")


def gui() -> None:
    show_manual("imgui_kit", fallback=fallback)


if __name__ == "__main__":
    immapp.run(gui, window_size=(1100, 800), with_markdown=True)
