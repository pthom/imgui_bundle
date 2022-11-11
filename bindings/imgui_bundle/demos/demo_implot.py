from typing import Any, Callable
import math
from munch import Munch

import numpy as np
from imgui_bundle import imgui, implot, static, imgui_md


ImVec2 = imgui.ImVec2
ImVec4 = imgui.ImVec4


def _demo_drag_rects_statics() -> Munch:
    nb_data = 512
    sampling_freq = 44100
    freq = 500.0
    r = Munch()
    i = np.arange(-nb_data, 2 * nb_data, 1)
    t = i / sampling_freq
    r.x_data = t
    arg = 2 * math.pi * freq * t
    r.y_data1 = np.sin(arg)
    r.y_data2 = r.y_data1 - 0.6 + np.sin(arg * 2) * 0.4
    r.y_data3 = r.y_data2 - 0.6 + np.sin(arg * 3) * 0.4
    r.rect = implot.ImPlotRect(0.0025, 0.0045, 0, 0.5)
    r.flags = implot.ImPlotDragToolFlags_.none
    return r


@static(statics=_demo_drag_rects_statics())
def demo_drag_rects():
    statics = demo_drag_rects.statics

    imgui.bullet_text("Click and drag the edges, corners, and center of the rect.")
    _, statics.flags = imgui.checkbox_flags("NoCursors", statics.flags, implot.ImPlotDragToolFlags_.no_cursors)
    imgui.same_line()
    _, statics.flags = imgui.checkbox_flags("NoFit", statics.flags, implot.ImPlotDragToolFlags_.no_fit)
    imgui.same_line()
    _, statics.flags = imgui.checkbox_flags("NoInput", statics.flags, implot.ImPlotDragToolFlags_.no_inputs)

    if implot.begin_plot("##Main", ImVec2(-1, 200)):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_tick_labels, implot.ImPlotAxisFlags_.no_tick_labels)
        implot.setup_axes_limits(0, 0.01, -1, 1)
        implot.plot_line("Signal 1", statics.x_data, statics.y_data1)
        implot.plot_line("Signal 2", statics.x_data, statics.y_data2)
        implot.plot_line("Signal 3", statics.x_data, statics.y_data3)
        _, statics.rect.x.min, statics.rect.y.min, statics.rect.x.max, statics.rect.y.max = implot.drag_rect(
            0,
            statics.rect.x.min,
            statics.rect.y.min,
            statics.rect.x.max,
            statics.rect.y.max,
            ImVec4(1, 0, 1, 1),
            statics.flags,
        )
        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1, 200), implot.ImPlotFlags_.canvas_only):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(
            statics.rect.x.min, statics.rect.x.max, statics.rect.y.min, statics.rect.y.max, imgui.ImGuiCond_.always
        )
        implot.plot_line("Signal 1", statics.x_data, statics.y_data1)
        implot.plot_line("Signal 2", statics.x_data, statics.y_data2)
        implot.plot_line("Signal 3", statics.x_data, statics.y_data3)
        implot.end_plot()


def demo_mixed_plot():
    implot.push_colormap(implot.ImPlotColormap_.deep)
    if implot.begin_plot("Mixed plot"):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(-0.5, 9.5, 0, 10)
        lin = np.array([8, 8, 9, 7, 8, 8, 8, 9, 7, 8])
        bar = np.array([1, 2, 5, 3, 4, 1, 2, 5, 3, 4])
        dot = np.array([7, 6, 6, 7, 8, 5, 6, 5, 8, 7])
        implot.plot_bars("Bars", bar, 0.5)
        implot.plot_line("Line", lin)
        implot.next_colormap_color()  # skip green
        implot.plot_scatter("Scatter", dot)
        implot.end_plot()


def demo_implot():
    imgui_md.render(
        """
# ImPlot
[Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
You can see lots of demos together with their code [online](https://traineq.org/implot_demo/src/implot_demo.html)"""
    )
    if imgui.button("View the full demo"):
        import webbrowser

        webbrowser.open("https://traineq.org/implot_demo/src/implot_demo.html")
    imgui.new_line()

    if imgui.collapsing_header("Drag Rects"):
        demo_drag_rects()
    if imgui.collapsing_header("Mixed plot"):
        demo_mixed_plot()


def main():
    from imgui_bundle import run

    run(demo_implot, with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
