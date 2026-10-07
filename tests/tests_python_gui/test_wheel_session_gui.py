"""The mouse wheel in a page that scrolls (a child window inside another one), with a widget that zooms with the wheel,
driven by the ImGui Test Engine. Three scenarios:
- a wheel that starts on the widget zooms it, and does not scroll the page;
- a notch on the text, then at once onto the widget: the move ends the page's hold on the wheel, the widget zooms;
- the mouse still above the widget: the page scrolls past it, and it does not zoom.
Three widgets: an ImPlot plot, an ImmVision image, and a widget of the app that claims the wheel as the docs say
(set_item_key_owner). With hello_imgui's wheel session (RunnerParams.wheel_session), all of them; without it, Dear
ImGui's own lock of the scrolled window, which the plot respects."""

from typing import Callable

import numpy as np
import pytest
from imgui_bundle import has_submodule, hello_imgui, imgui, implot
from imgui_bundle.immapp import testing

XS = np.linspace(0.0, 10.0, 200)
YS = np.sin(XS)
IMAGE = np.full((150, 300, 3), 128, dtype=np.uint8)

Draw = Callable[[dict[str, float]], None]


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


_image_params = None


def _draw_image(state: dict[str, float]) -> None:
    from imgui_bundle import immvision

    global _image_params
    if _image_params is None:
        _image_params = immvision.ImageParams()
        _image_params.image_display_size = (300, 150)
        _image_params.show_image_info = False
        _image_params.show_pixel_info = False
        _image_params.show_zoom_buttons = False
        _image_params.show_options_button = False
    immvision.image("##image", IMAGE, _image_params)
    state["zoom"] = float(_image_params.zoom_pan_matrix[0][0])


def _run_bench(draw_zoomable: Draw, wheel_session: bool = True) -> dict[str, list[float]]:
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

    results: dict[str, list[float]] = {}

    def record(key: str) -> None:
        results.setdefault(f"scroll_{key}", []).append(state["scroll_y"])
        results.setdefault(f"zoom_{key}", []).append(state["zoom"])

    def center() -> imgui.ImVec2:
        top_left, bottom_right = rects["zoomable"]
        return imgui.ImVec2((top_left.x + bottom_right.x) / 2, (top_left.y + bottom_right.y) / 2)

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.yield_(3)
        # A wheel that starts on the widget
        ctx.mouse_move_to_pos(center())
        ctx.yield_(3)
        record("before_zoom")
        ctx.mouse_wheel_y(-1.0)
        ctx.yield_(3)
        record("after_zoom")
        ctx.sleep_no_skip(1.0, 1.0 / 60.0)  # the page's hold ends after a pause (by time: the engine's frames are fast)
        # A notch on the text (the widget stays below the mouse), then at once onto the widget
        ctx.mouse_move_to_pos(imgui.ImVec2(250, 50))
        ctx.yield_(2)
        ctx.mouse_wheel_y(-1.0)
        ctx.yield_()
        ctx.mouse_move_to_pos(center())
        ctx.yield_(2)
        record("before_move_zoom")
        ctx.mouse_wheel_y(-1.0)
        ctx.yield_(3)
        record("after_move_zoom")
        ctx.sleep_no_skip(1.0, 1.0 / 60.0)
        # The mouse still, just above the widget: the first notch brings it under the mouse
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
    # A wheel that starts on the widget zooms it, and the page does not scroll
    assert results["scroll_after_zoom"] == results["scroll_before_zoom"], results
    assert results["zoom_after_zoom"] != results["zoom_before_zoom"], results
    # After a notch on the text, a move onto the widget: it zooms, and the page does not scroll
    assert results["scroll_after_move_zoom"] == results["scroll_before_move_zoom"], results
    assert results["zoom_after_move_zoom"] != results["zoom_before_move_zoom"], results
    # The mouse still: each notch scrolls the page, and the widget does not zoom
    scrolls = results["scroll_still"]
    assert all(b > a for a, b in zip(scrolls, scrolls[1:])), results
    assert len(set(results["zoom_still"])) == 1, results


def test_wheel_session_plot() -> None:
    _check(_run_bench(_draw_plot))


def test_wheel_session_widget_that_claims_the_wheel() -> None:
    _check(_run_bench(_draw_custom_zoom))


@pytest.mark.skipif(not has_submodule("immvision"), reason="imgui_bundle built without immvision")
def test_wheel_session_image() -> None:
    _check(_run_bench(_draw_image))


def test_without_wheel_session_the_plot_respects_imgui_lock() -> None:
    _check(_run_bench(_draw_plot, wheel_session=False))


if __name__ == "__main__":
    test_wheel_session_plot()
    test_wheel_session_widget_that_claims_the_wheel()
    test_wheel_session_image()
    test_without_wheel_session_the_plot_respects_imgui_lock()
    print("OK test_wheel_session")
