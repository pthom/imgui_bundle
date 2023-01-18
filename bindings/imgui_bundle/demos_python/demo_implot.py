# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import math
import numpy as np
from imgui_bundle import imgui, implot, imgui_md, immapp, ImVec2, ImVec4


class DemoDragRectState:
    x_data: np.ndarray
    y_data1: np.ndarray
    y_data2: np.ndarray
    y_data3: np.ndarray
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
        self.rect = implot.Rect(0.0025, 0.0045, 0, 0.5)  # type: ignore
        self.flags = implot.DragToolFlags_.none


@immapp.static(state=DemoDragRectState())
def demo_drag_rects():
    state = demo_drag_rects.state

    imgui.bullet_text("Click and drag the edges, corners, and center of the rect.")
    _, state.flags = imgui.checkbox_flags("NoCursors", state.flags, implot.DragToolFlags_.no_cursors)
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags("NoFit", state.flags, implot.DragToolFlags_.no_fit)
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags("NoInput", state.flags, implot.DragToolFlags_.no_inputs)

    plot_height = immapp.em_size() * 15
    if implot.begin_plot("##Main", ImVec2(-1, plot_height)):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_tick_labels, implot.ImPlotAxisFlags_.no_tick_labels)
        implot.setup_axes_limits(0, 0.01, -1, 1)
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        _, state.rect.x.min, state.rect.y.min, state.rect.x.max, state.rect.y.max = implot.drag_rect(
            0,
            state.rect.x.min,
            state.rect.y.min,
            state.rect.x.max,
            state.rect.y.max,
            ImVec4(1, 0, 1, 1),
            state.flags,
        )
        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1, plot_height), implot.Flags_.canvas_only):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(
            state.rect.x.min, state.rect.x.max, state.rect.y.min, state.rect.y.max, imgui.Cond_.always
        )
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        implot.end_plot()


def demo_mixed_plot():
    implot.push_colormap(implot.Colormap_.deep)
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


def demo_gui():
    imgui_md.render_unindented(
        """
        # ImPlot
        [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        You can see lots of demos together with their code [online](https://traineq.org/implot_demo/src/implot_demo.html)
        """)
    if imgui.button("View the full demo"):
        import webbrowser

        webbrowser.open("https://traineq.org/implot_demo/src/implot_demo.html")
    imgui.new_line()

    if imgui.collapsing_header("Drag Rects"):
        demo_drag_rects()
    if imgui.collapsing_header("Mixed plot", imgui.TreeNodeFlags_.default_open):
        demo_mixed_plot()


def main():
    immapp.run(demo_gui, with_implot=True, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
