# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""GUI test: ImPlot's plotting functions accept read-only numpy arrays (they need a plot, hence a frame).

plot_line is generated (nb::ndarray<nb::ro>), plot_heatmap is hand-written: both read the arrays only.
"""
import numpy as np
from imgui_bundle import hello_imgui, imgui, implot, implot_ctx


def read_only(a: np.ndarray) -> np.ndarray:
    a = a.copy()
    a.setflags(write=False)
    return a


def test_implot_read_only_gui() -> None:
    x = read_only(np.linspace(0.0, 1.0, 10))
    y = read_only(x**2)
    heat = read_only(np.arange(12, dtype=np.float64).reshape(3, 4))
    results = {}

    def gui() -> None:
        with implot_ctx.begin_plot("Read only") as plot:
            if plot:
                implot.plot_line("line", x, y)
                implot.plot_heatmap("heatmap", heat)
                results["plotted"] = True
        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    with implot_ctx.create_context():
        hello_imgui.run(gui)

    assert results.get("plotted"), "the plot should be drawn, with its read-only arrays"
    print("OK test_implot_read_only_gui")


if __name__ == "__main__":
    test_implot_read_only_gui()
