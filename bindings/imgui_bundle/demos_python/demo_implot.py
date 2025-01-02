# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List
import math
import numpy as np
from numpy.typing import NDArray
from imgui_bundle import imgui, implot, implot3d, imgui_md, immapp, ImVec2, ImVec4


# ========================
# Demos for ImPlot (2D)
# ========================

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
        self.flags = implot.DragToolFlags_.none.value


@immapp.static(state=DemoDragRectState())
def demo_drag_rects():
    state = demo_drag_rects.state

    imgui.bullet_text("Click and drag the edges, corners, and center of the rect.")
    _, state.flags = imgui.checkbox_flags(
        "NoCursors", state.flags, implot.DragToolFlags_.no_cursors.value
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoFit", state.flags, implot.DragToolFlags_.no_fit.value
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoInput", state.flags, implot.DragToolFlags_.no_inputs.value
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
        implot.internal.fit_point(implot.Point(0, -3.5))
        implot.internal.fit_point(implot.Point(0, 1.5))

        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1, plot_height), implot.Flags_.canvas_only.value):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(
            state.rect.x.min,
            state.rect.x.max,
            state.rect.y.min,
            state.rect.y.max,
            imgui.Cond_.always.value,
        )
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        implot.end_plot()


def demo_mixed_plot():
    implot.push_colormap(implot.Colormap_.deep.value)
    plot_height = immapp.em_size() * 30
    if implot.begin_plot("Mixed plot", ImVec2(-1, plot_height)):
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


class MyHeatmapData:
    values: NDArray[np.float64]
    x_ticks: List[str]
    y_ticks: List[str]
    n_ticks: int

    def __init__(self):
        x = np.linspace(-4, 4, 401)
        xx = np.outer(x, x)
        self.values = np.sinc(xx)
        self.n_ticks = 5
        self.x_ticks = [str(x) for x in np.linspace(-4, 4, self.n_ticks)]
        self.y_ticks = self.x_ticks


@immapp.static(data=MyHeatmapData())
def demo_heatmap():
    data = demo_heatmap.data

    axis_flags = (
        implot.AxisFlags_.lock.value
        | implot.AxisFlags_.no_grid_lines.value
        | implot.AxisFlags_.no_tick_marks.value
    )
    cmap = implot.Colormap_.viridis.value
    implot.push_colormap(cmap)
    imgui.begin_group()
    plot_size = (imgui.get_content_region_avail().x - immapp.em_size() * 5, -1)
    plot_flags = implot.Flags_.no_legend.value | implot.Flags_.no_mouse_text.value
    if implot.begin_plot("Sinc Function", plot_size, plot_flags):  # type: ignore
        implot.setup_axes("", "", axis_flags, axis_flags)
        implot.setup_axis_ticks(
            implot.ImAxis_.x1.value, 0, 1, data.n_ticks, data.x_ticks, False
        )
        implot.setup_axis_ticks(
            implot.ImAxis_.y1.value, 0, 1, data.n_ticks, data.y_ticks, False
        )
        implot.plot_heatmap(
            "##heatmap",
            data.values,
            data.values.min(),
            data.values.max(),
            "",  # no label
            [0, 1],   # type: ignore
            [1, 0],  # type: ignore
            0,
        )
        implot.end_plot()
    imgui.end_group()
    imgui.same_line()
    implot.colormap_scale(
        "##heatmap_scale",
        data.values.min(),
        data.values.max(),
        imgui.ImVec2(60, -1),
        "%g",
        0,
        cmap,
    )
    implot.pop_colormap()


# ========================
# Demos for ImPlot3D
# ========================
def demo3d_lineplots():
    xs1 = np.linspace(0, 1, 1001)
    ys1 = 0.5 + 0.5 * np.cos(50 * (xs1 + imgui.get_time() / 10))
    zs1 = 0.5 + 0.5 * np.sin(50 * (xs1 + imgui.get_time() / 10))

    xs2 = np.linspace(0, 1, 20)
    ys2 = xs2 * xs2
    zs2 = xs2 * ys2

    if implot3d.begin_plot("Line Plots"):
        implot3d.setup_axes("x", "y", "z")
        implot3d.plot_line("f(x)", xs1, ys1, zs1)
        implot3d.set_next_marker_style(implot3d.Marker_.circle.value)
        implot3d.plot_line("g(x)", xs2, ys2, zs2, implot3d.LineFlags_.segments.value)
        implot3d.end_plot()


def demo3d_surfaceplots():
    statics = demo3d_surfaceplots
    N = 20
    if not hasattr(statics, "xs"):
        statics.xs = np.zeros(N * N)
        statics.ys = np.zeros(N * N)
        statics.zs = np.zeros(N * N)
        statics.t = 0.0

    statics.t += imgui.get_io().delta_time

    # Define the range for X and Y
    min_val = -1.0
    max_val = 1.0
    step = (max_val - min_val) / (N - 1)

    # Populate the xs, ys, and zs arrays
    for i in range(N):
        for j in range(N):
            idx = i * N + j
            statics.xs[idx] = min_val + j * step  # X values are constant along rows
            statics.ys[idx] = min_val + i * step  # Y values are constant along columns
            # z = sin(2t + sqrt(x^2 + y^2))
            statics.zs[idx] = math.sin(2 * statics.t + math.sqrt(statics.xs[idx] * statics.xs[idx] + statics.ys[idx] * statics.ys[idx]))

    # Choose fill color
    imgui.text("Fill color")
    if not hasattr(statics, "selected_fill"):
        statics.selected_fill = 1  # Colormap by default
    if not hasattr(statics, "solid_color"):
        statics.solid_color = [0.8, 0.8, 0.2, 0.6]
    colormaps = [
        "Viridis", "Plasma", "Hot", "Cool", "Pink", "Jet",
        "Twilight", "RdBu", "BrBG", "PiYG", "Spectral", "Greys"
    ]
    if not hasattr(statics, "sel_colormap"):
        statics.sel_colormap = 5 # Jet by default

    imgui.indent()

    # Choose solid color
    if imgui.radio_button("Solid", statics.selected_fill == 0):
        statics.selected_fill = 0
    if statics.selected_fill == 0:
        imgui.same_line()
        _, statics.solid_color = imgui.color_edit4("##SurfaceSolidColor", statics.solid_color)

    # Choose colormap
    if imgui.radio_button("Colormap", statics.selected_fill == 1):
        statics.selected_fill = 1
    if statics.selected_fill == 1:
        imgui.same_line()
        _, statics.sel_colormap = imgui.combo("##SurfaceColormap", statics.sel_colormap, colormaps)

    imgui.unindent()

    # Choose range
    if not hasattr(statics, "custom_range"):
        statics.custom_range = False
    if not hasattr(statics, "range_min"):
        statics.range_min = -1.0
    if not hasattr(statics, "range_max"):
        statics.range_max = 1.0
    _, statics.custom_range = imgui.checkbox("Custom range", statics.custom_range)
    imgui.indent()
    if not statics.custom_range:
        imgui.begin_disabled()
    _, statics.range_min = imgui.slider_float("Range min", statics.range_min, -1.0, statics.range_max - 0.01)
    _, statics.range_max = imgui.slider_float("Range max", statics.range_max, statics.range_min + 0.01, 1.0)
    if not statics.custom_range:
        imgui.end_disabled()
    imgui.unindent()

    # Begin the plot
    if statics.selected_fill == 1:
        implot3d.push_colormap(colormaps[statics.sel_colormap])
    if implot3d.begin_plot("Surface Plots", ImVec2(-1, 400), implot3d.Flags_.no_clip.value):
        # Set styles
        implot3d.setup_axes_limits(-1, 1, -1, 1, -1.5, 1.5)
        implot3d.push_style_var(implot3d.StyleVar_.fill_alpha.value, 0.8)
        if statics.selected_fill == 0:
            implot3d.set_next_fill_style(statics.solid_color)
        implot3d.set_next_line_style(implot3d.get_colormap_color(1))

        # Plot the surface
        if statics.custom_range:
            implot3d.plot_surface("Wave Surface", statics.xs, statics.ys, statics.zs, N, N, statics.range_min, statics.range_max)
        else:
            implot3d.plot_surface("Wave Surface", statics.xs, statics.ys, statics.zs, N, N)

        # End the plot
        implot3d.pop_style_var()
        implot3d.end_plot()

    if statics.selected_fill == 1:
        implot3d.pop_colormap()


# =======================
# Main demo function
# =======================
def demo_gui():
    imgui_md.render_unindented(
        """
        # ImPlot & ImPlot3D
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.

        You can see lots of demos together with their code [online](https://traineq.org/implot_demo/src/implot_demo.html)
        """
    )
    if imgui.button("View the full demo"):
        import webbrowser

        webbrowser.open("https://traineq.org/implot_demo/src/implot_demo.html")
    imgui.new_line()

    if imgui.collapsing_header("ImPlot: Drag Rects"):
        demo_drag_rects()
    if imgui.collapsing_header("ImPlot: Mixed plot##2"):
        demo_mixed_plot()
    if imgui.collapsing_header("ImPlot: Heatmap"):
        demo_heatmap()

    if imgui.collapsing_header("ImPlot3D: Line plots ##2"):
        demo3d_lineplots()
    if imgui.collapsing_header("ImPlot3D: Surface Plots##2"):
        demo3d_surfaceplots()



def main():
    immapp.run(demo_gui, with_implot=True, with_implot3d=True, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
