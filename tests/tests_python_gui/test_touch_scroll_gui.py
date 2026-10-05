"""The swipe of a touch screen (hello_imgui.RunnerParams.touch_scroll_mode), driven by the ImGui Test Engine with a
touch source injected each frame: a swipe on the text and from a button scrolls, a tap clicks when the finger lifts,
a hold then a drag goes to a slider, a swipe on a RichMd zone scrolls instead of selecting."""

from imgui_bundle import hello_imgui, imgui, rich_md
from imgui_bundle.immapp import testing

MARKDOWN = """
# A page

Some *markdown* text, selectable with the mouse: a swipe on it must scroll, not select.
""" + "\n".join(f"Paragraph {i}: lorem ipsum dolor sit amet, consectetur adipiscing elit." for i in range(10))


def test_touch_scroll() -> None:
    state = {"clicks": 0, "slider": 0.5, "scroll_y": 0.0, "touch": True}
    rects: dict[str, tuple[imgui.ImVec2, imgui.ImVec2]] = {}

    def gui() -> None:
        if state["touch"]:
            imgui.get_io().add_mouse_source_event(imgui.MouseSource.touch_screen)
        imgui.set_next_window_pos((0, 0), imgui.Cond_.always)
        imgui.set_next_window_size((400, 300), imgui.Cond_.always)
        imgui.begin("Bench", None, imgui.WindowFlags_.no_title_bar)
        state["scroll_y"] = imgui.get_scroll_y()
        if imgui.button("Button"):
            state["clicks"] += 1
        rects["button"] = (imgui.get_item_rect_min(), imgui.get_item_rect_max())
        _, state["slider"] = imgui.slider_float("Slider", state["slider"], 0.0, 1.0)
        rects["slider"] = (imgui.get_item_rect_min(), imgui.get_item_rect_max())
        rich_md.render(MARKDOWN)  # from about y=60 to past the bottom of the window
        for i in range(60):
            imgui.text(f"Line {i}")
        imgui.end()

    def center(name: str) -> imgui.ImVec2:
        a, b = rects[name]
        return imgui.ImVec2((a.x + b.x) / 2, (a.y + b.y) / 2)

    def swipe(ctx: imgui.test_engine.TestContext, pos: imgui.ImVec2, dy: float, steps: int = 5) -> None:
        ctx.mouse_move_to_pos(pos)
        ctx.yield_()
        ctx.mouse_down(0)
        ctx.yield_()
        for i in range(1, steps + 1):
            ctx.mouse_move_to_pos(imgui.ImVec2(pos.x, pos.y + dy * i / steps))
            ctx.yield_()
        ctx.yield_(15)  # the finger pauses: no inertia
        ctx.mouse_up(0)
        ctx.yield_(4)

    results: dict[str, float] = {}

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.yield_(3)
        # A swipe from the button scrolls, and does not click it
        swipe(ctx, center("button"), -50)
        results["scroll_after_button_swipe"] = state["scroll_y"]
        results["clicks_after_button_swipe"] = state["clicks"]
        # Back to the top with a swipe down on the markdown: it scrolls, it does not select (the scroll is the proof
        # that the press was not taken by the text)
        swipe(ctx, imgui.ImVec2(200, 200), 120)
        results["scroll_after_markdown_swipe"] = state["scroll_y"]
        # A tap on the button clicks it when the finger lifts
        ctx.mouse_move_to_pos(center("button"))
        ctx.yield_()
        ctx.mouse_down(0)
        ctx.yield_(2)
        results["clicks_while_down"] = state["clicks"]
        ctx.mouse_up(0)
        ctx.yield_(4)
        results["clicks_after_tap"] = state["clicks"]
        # A hold then a drag on the slider moves it
        ctx.mouse_move_to_pos(center("slider"))
        ctx.yield_()
        ctx.mouse_down(0)
        ctx.sleep_no_skip(0.4, 1.0 / 60.0)  # past the hold delay (the engine's frames are fast: wait by time)
        for i in range(1, 6):
            ctx.mouse_move_to_pos(imgui.ImVec2(center("slider").x + 12 * i, center("slider").y))
            ctx.yield_()
        ctx.yield_(15)
        ctx.mouse_up(0)
        ctx.yield_(4)
        results["slider_after_hold_drag"] = state["slider"]
        results["scroll_after_hold_drag"] = state["scroll_y"]

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params.app_window_params.window_geometry.size = (500, 400)
    params.touch_scroll_mode = hello_imgui.TouchScrollMode.auto
    testing.run(test_function=test_fn, runner_params=params, with_markdown=True)

    assert results["scroll_after_button_swipe"] > 30, results
    assert results["scroll_after_markdown_swipe"] == 0, results
    assert results["clicks_after_button_swipe"] == 0, results
    assert results["clicks_while_down"] == 0, results
    assert results["clicks_after_tap"] == 1, results
    assert results["slider_after_hold_drag"] > 0.6, results
    assert results["scroll_after_hold_drag"] == 0, results
    print("OK test_touch_scroll")


if __name__ == "__main__":
    test_touch_scroll()
