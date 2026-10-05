"""ImPlot3D: the interactive manual

The 3D plots of [ImPlot3D](https://github.com/brenocq/implot3d), section by section, with the code of each beside it.
Lines, scatter, surfaces, meshes and more, in Python and C++. From
[Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive manual for Dear ImGui and its libraries.
"""
from imgui_bundle import immapp, implot3d

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]


def gui() -> None:
    show_manual("implot3_d", fallback=lambda: implot3d.show_demo_window())


if __name__ == "__main__":
    immapp.run(gui, window_size=(1100, 800), with_markdown=True, with_implot3d=True)
