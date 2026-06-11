# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""GUI smoke test for the implot_ctx context managers which require a running
frame: begin_plot, begin_subplots and push_plot_clip_rect.
"""
import numpy as np
from imgui_bundle import hello_imgui, imgui, implot, implot_ctx


def test_implot_ctx_gui() -> None:
    results = {}

    def gui() -> None:
        x = np.arange(0, 10, 0.1)
        y = np.sin(x)

        with implot_ctx.begin_plot("Plot") as plot:
            results["plot_visible"] = bool(plot)
            if plot:
                implot.plot_line("sin", x, y)
                with implot_ctx.push_plot_clip_rect():
                    pass

        with implot_ctx.begin_subplots("Subplots", 1, 2, hello_imgui.em_to_vec2(30, 10)) as subplots:
            results["subplots_visible"] = bool(subplots)
            if subplots:
                for _ in range(2):
                    with implot_ctx.begin_plot("##sub") as plot:
                        if plot:
                            implot.plot_line("sin", x, y)

        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    # implot_ctx.create_context() is also exercised in real conditions
    # (hello_imgui.run does not create an implot context by itself)
    with implot_ctx.create_context():
        hello_imgui.run(gui)

    assert results["plot_visible"], "begin_plot should be visible in a fresh window"
    assert results["subplots_visible"], "begin_subplots should be visible in a fresh window"
    print("OK test_implot_ctx_gui")


if __name__ == "__main__":
    test_implot_ctx_gui()
