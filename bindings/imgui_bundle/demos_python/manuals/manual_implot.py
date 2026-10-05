"""ImPlot: the interactive manual

Every kind of plot of [ImPlot](https://github.com/epezent/implot), section by section, with the code of each beside
it. Lines, scatter, bars, heatmaps, histograms, real-time plots and more, in Python and C++. From
[Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/), the interactive manual for Dear ImGui and its libraries.
"""
from imgui_bundle import immapp, implot

try:
    from imgui_bundle.demos_python.manuals.manual_common import show_manual
except ImportError:  # a script: the module is beside this file
    from manual_common import show_manual  # type: ignore[import-not-found, no-redef]


def gui() -> None:
    show_manual("implot", fallback=lambda: implot.show_demo_window())


if __name__ == "__main__":
    immapp.run(gui, window_size=(1100, 800), with_markdown=True, with_implot=True)
