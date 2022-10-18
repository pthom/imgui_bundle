import math
from munch import Munch

import numpy as np
from imgui_bundle import imgui, implot, implot_create_global_context


ImVec2 = imgui.ImVec2
ImVec4 = imgui.ImVec4


def _demo_drag_rects_statics() -> Munch:
    nb_data = 512; sampling_freq = 44100; freq = 500.
    r = Munch()
    i = np.arange(-nb_data, 2 * nb_data, 1)
    t = i / sampling_freq
    r.x_data = t
    arg = 2 * math.pi * freq * t
    r.y_data1 = np.sin(arg)
    r.y_data2 = r.y_data1 - 0.6 + np.sin(arg * 2) * 0.4
    r.y_data3 = r.y_data2 - 0.6 + np.sin(arg * 3) * 0.4
    r.rect = implot.ImPlotRect(0.0025,0.0045,0,0.5)
    r.flags = implot.ImPlotDragToolFlags_.none
    return r


def demo_drag_rects():
    if not hasattr(demo_drag_rects, "statics"):
        demo_drag_rects.statics = _demo_drag_rects_statics()
    statics = demo_drag_rects.statics

    imgui.bullet_text("Click and drag the edges, corners, and center of the rect.")
    _, statics.flags = imgui.checkbox_flags("NoCursors", statics.flags, implot.ImPlotDragToolFlags_.no_cursors); imgui.same_line()
    _, statics.flags = imgui.checkbox_flags("NoFit", statics.flags, implot.ImPlotDragToolFlags_.no_fit); imgui.same_line()
    _, statics.flags = imgui.checkbox_flags("NoInput", statics.flags, implot.ImPlotDragToolFlags_.no_inputs)

    if implot.begin_plot("##Main", ImVec2(-1,200)):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_tick_labels, implot.ImPlotAxisFlags_.no_tick_labels)
        implot.setup_axes_limits(0, 0.01, -1, 1)
        implot.plot_line("Signal 1", statics.x_data, statics.y_data1)
        implot.plot_line("Signal 2", statics.x_data, statics.y_data2)
        implot.plot_line("Signal 3", statics.x_data, statics.y_data3)
        _, statics.rect.x.min, statics.rect.y.min, statics.rect.x.max, statics.rect.y.max = \
            implot.drag_rect(0, statics.rect.x.min, statics.rect.y.min, statics.rect.x.max, statics.rect.y.max, ImVec4(1,0,1,1), statics.flags)
        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1,200), implot.ImPlotFlags_.canvas_only):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(statics.rect.x.min, statics.rect.x.max, statics.rect.y.min, statics.rect.y.max, imgui.ImGuiCond_.always)
        implot.plot_line("Signal 1", statics.x_data, statics.y_data1)
        implot.plot_line("Signal 2", statics.x_data, statics.y_data2)
        implot.plot_line("Signal 3", statics.x_data, statics.y_data3)
        implot.end_plot()


def main():
    implot_create_global_context()
    from imgui_bundle import hello_imgui
    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = demo_drag_rects

    hello_imgui.run(params)


if __name__ == "__main__":
    main()


