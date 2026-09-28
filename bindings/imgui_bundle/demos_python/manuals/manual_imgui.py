"""Dear ImGui: the interactive manual

Every widget and feature of [Dear ImGui](https://github.com/ocornut/imgui), section by section, with the Python and
C++ code of each beside it. From [Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive
manual for Dear ImGui and its libraries.
"""
from imgui_bundle import imgui, immapp

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]


def demo_gui() -> None:
    show_manual("imgui", fallback=lambda: imgui.show_demo_window())


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1100, 800), with_markdown=True)
