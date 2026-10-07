"""The wheel session of hello_imgui, driven by the ImGui Test Engine, in a page that scrolls (a child window inside
another one) with a widget that zooms with the wheel: a wheel that starts on the widget zooms it, and does not scroll
the page; the mouse still, the wheel scrolls the page past the widget, which does not zoom. Two widgets: a real ImPlot
plot, and a widget of the app that claims the wheel as the docs say (set_item_key_owner). With the option
wheel_session off, Dear ImGui's own behavior: the plot that arrives under the still mouse takes the wheel."""

from typing import Callable

import numpy as np
from imgui_bundle import hello_imgui, imgui, implot
from imgui_bundle.immapp import testing

XS = np.linspace(0.0, 10.0, 200)
YS = np.sin(XS)


def _draw_plot(state: dict[str, float]) -> None:
    if implot.begin_plot("##plot", (-1, 150)):
        implot.plot_line("sin", XS, YS)
        limits = implot.get_plot_limits()
        state["zoom"] = limits.x.max - limits.x.min
        implot.end_plot()


def _draw_custom_zoom(state: dict[str, float]) -> None:
    imgui.invisible_button("zoom", (-1, 150))
    if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y):  # hovered: the wheel is this widget's
        state["zoom"] *= 1.1 ** imgui.get_io().mouse_wheel


def _run_bench(draw_zoomable: Callable[[dict[str, float]], None], wheel_session: bool = True) -> dict[str, list[float]]:
    state = {"scroll_y": 0.0, "zoom": 1.0}
    rects: dict[str, tuple[imgui.ImVec2, imgui.ImVec2]] = {}

    def gui() -> None:
        imgui.set_next_window_pos((0, 0), imgui.Cond_.always)
        imgui.set_next_window_size((500, 400), imgui.Cond_.always)
        imgui.begin("Bench", None, imgui.WindowFlags_.no_title_bar)
        imgui.begin_child("outer")
        imgui.begin_child("page")
        state["scroll_y"] = imgui.get_scroll_y()
        for i in range(12):
            imgui.text(f"Line {i}")
        draw_zoomable(state)
        rects["zoomable"] = (imgui.get_item_rect_min(), imgui.get_item_rect_max())
        for i in range(12, 100):
            imgui.text(f"Line {i}")
        imgui.end_child()
        imgui.end_child()
        imgui.end()

    results: dict[str, list[float]] = {"scrolls": [], "zooms": []}

    def record(key: str) -> None:
        results.setdefault(f"scroll_{key}", []).append(state["scroll_y"])
        results.setdefault(f"zoom_{key}", []).append(state["zoom"])

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.yield_(3)
        # A wheel that starts on the widget is the widget's: it zooms, and the page does not scroll
        top_left, bottom_right = rects["zoomable"]
        ctx.mouse_move_to_pos(imgui.ImVec2((top_left.x + bottom_right.x) / 2, (top_left.y + bottom_right.y) / 2))
        ctx.yield_(3)
        record("before_zoom")
        ctx.mouse_wheel_y(-1.0)
        ctx.yield_(3)
        record("after_zoom")
        # The session ends after a pause (0.7 s, by time: the engine's frames are fast)
        ctx.sleep_no_skip(1.0, 1.0 / 60.0)
        # The mouse still, just above the widget: the first notch brings it under the mouse, and the page keeps
        # scrolling
        top_left, bottom_right = rects["zoomable"]
        ctx.mouse_move_to_pos(imgui.ImVec2((top_left.x + bottom_right.x) / 2, top_left.y - 10))
        ctx.yield_(2)
        record("still")
        for _ in range(6):
            ctx.mouse_wheel_y(-1.0)
            ctx.yield_()
            record("still")

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params.app_window_params.window_geometry.size = (500, 400)
    params.wheel_session = wheel_session
    testing.run(test_function=test_fn, runner_params=params, with_implot=True)
    return results


def _check(results: dict[str, list[float]]) -> None:
    assert results["scroll_after_zoom"] == results["scroll_before_zoom"], results
    assert results["zoom_after_zoom"] != results["zoom_before_zoom"], results
    scrolls = results["scroll_still"]
    assert all(b > a for a, b in zip(scrolls, scrolls[1:])), results  # each notch scrolled the page
    assert len(set(results["zoom_still"])) == 1, results  # the widget did not zoom


def test_wheel_session_plot() -> None:
    _check(_run_bench(_draw_plot))


def test_wheel_session_widget_that_claims_the_wheel() -> None:
    _check(_run_bench(_draw_custom_zoom))


def test_wheel_session_off() -> None:
    results = _run_bench(_draw_plot, wheel_session=False)
    assert len(set(results["zoom_still"])) > 1, results  # the plot under the still mouse zoomed


if __name__ == "__main__":
    test_wheel_session_plot()
    test_wheel_session_widget_that_claims_the_wheel()
    test_wheel_session_off()
    print("OK test_wheel_session")
