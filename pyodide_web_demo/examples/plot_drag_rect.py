# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
doc = """
Plot using ImPlot with a draggable rectangle
============================================

This example shows how to use the `implot.drag_rect` function to create a draggable rectangle on a plot.

[ImPlot](https://github.com/epezent/implot) is a plotting extension for [Dear ImGui](https://github.com/ocornut/imgui),
which is included in the ImGui Bundle.

It focuses on **fast** rendering and ease of use.

*Note: this markdown text is rendered using the `imgui_md` module, which is part of [Dear ImGui Bundle](https://githb.com/pthom/imgui_bundle).*

"""
import math
import numpy as np
from numpy.typing import NDArray
from imgui_bundle import imgui, implot, imgui_md, immapp, ImVec2, ImVec4


class DemoDragRectState:
    x_data: NDArray[np.float64]
    y_data1: NDArray[np.float64]
    y_data2: NDArray[np.float64]
    y_data3: NDArray[np.float64]
    rect: implot.Rect
    flags: int

    def __init__(self):
        nb_data = 512
        sampling_freq = 44100
        freq = 500.0
        i = np.arange(-nb_data, 2 * nb_data, 1)
        t = i / sampling_freq
        self.x_data = t
        arg = 2 * math.pi * freq * t
        self.y_data1 = np.sin(arg)
        self.y_data2 = self.y_data1 - 0.6 + np.sin(arg * 2) * 0.4
        self.y_data3 = self.y_data2 - 0.6 + np.sin(arg * 3) * 0.4
        self.rect = implot.Rect(0.0025, 0.0075, -2.7, 1.1)  # type: ignore
        self.flags = implot.DragToolFlags_.none


@immapp.static(state=DemoDragRectState())
def demo_drag_rects():
    imgui_md.render_unindented(doc)
    imgui.separator_text("Plot with a draggable rectangle")

    state = demo_drag_rects.state

    _, state.flags = imgui.checkbox_flags(
        "NoCursors", state.flags, implot.DragToolFlags_.no_cursors
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoFit", state.flags, implot.DragToolFlags_.no_fit
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoInput", state.flags, implot.DragToolFlags_.no_inputs
    )

    plot_height = immapp.em_size() * 15
    if implot.begin_plot("##Main", ImVec2(-1, plot_height)):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_tick_labels, implot.ImPlotAxisFlags_.no_tick_labels)
        # implot.setup_axes_limits(0, 0.01, -1, 1)
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        (
            _,
            state.rect.x.min,
            state.rect.y.min,
            state.rect.x.max,
            state.rect.y.max,
            clicked,
            hovered,
            held,
        ) = implot.drag_rect(
            0,
            state.rect.x.min,
            state.rect.y.min,
            state.rect.x.max,
            state.rect.y.max,
            ImVec4(1, 0, 1, 1),
            state.flags,
        )

        # Example showing how to use implot_internal
        implot.internal.fit_point((0, -3.5))
        implot.internal.fit_point((0, 1.5))

        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1, plot_height), implot.Flags_.canvas_only):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(
            state.rect.x.min,
            state.rect.x.max,
            state.rect.y.min,
            state.rect.y.max,
            imgui.Cond_.always,
        )
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        implot.end_plot()


immapp.run(demo_drag_rects, with_implot=True, with_markdown=True)
