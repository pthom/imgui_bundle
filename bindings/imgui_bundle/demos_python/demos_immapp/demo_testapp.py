# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""demo_testapp: use `immapp.testing` to drive an app and capture screenshots, then exit

Customization: edit EXIT_AFTER_TESTS & SCREENSHOTS_FOLDER
"""
from __future__ import annotations

from imgui_bundle import imgui
from imgui_bundle.immapp import testing
import os

SCREENSHOTS_FOLDER = "."  # folder where screenshots are saved
EXIT_AFTER_TESTS = True


class State:
    counter: int = 0
    slider_value: int = 0
    checkbox: bool = False


state = State()


def gui() -> None:
    imgui.text("demo_testapp — exercise these widgets under the test engine")
    imgui.separator()

    if imgui.button("Click me"):
        state.counter += 1
    imgui.same_line()
    imgui.text(f"clicks: {state.counter}")

    _, state.slider_value = imgui.slider_int("A slider", state.slider_value, 0, 100)
    _, state.checkbox = imgui.checkbox("A checkbox", state.checkbox)

    if imgui.collapsing_header("Details"):
        imgui.text("These details are hidden until the header is expanded.")
        imgui.bullet_text("Line 1")
        imgui.bullet_text("Line 2")


def screenshot_test(ctx: imgui.test_engine.TestContext) -> None:
    """Test function: drive the GUI and capture a screenshot at each stage."""

    # 0) Initial state (header closed, counter=0).
    testing.capture(ctx, os.path.join(SCREENSHOTS_FOLDER, "00_initial.png"))

    # 1) Click the button twice.
    ctx.item_click("//**/Click me")
    ctx.item_click("//**/Click me")
    testing.capture(ctx, os.path.join(SCREENSHOTS_FOLDER, "01_after_clicks.png"))

    # 2) Move the slider.
    ctx.item_input_value("//**/A slider", 77)
    testing.capture(ctx, os.path.join(SCREENSHOTS_FOLDER, "02_slider.png"))

    # 3) Toggle the checkbox.
    ctx.item_click("//**/A checkbox")
    testing.capture(ctx, os.path.join(SCREENSHOTS_FOLDER, "03_checkbox.png"))

    # 4) Expand the collapsing header.
    ctx.item_open("//**/Details")
    testing.capture(ctx, os.path.join(SCREENSHOTS_FOLDER, "04_details.png"))


def main() -> None:

    # Reset state so the captures are deterministic, regardless of repeated runs.
    state.counter = 0
    state.slider_value = 0
    state.checkbox = False

    testing.run(
        gui_function=gui,
        test_function=screenshot_test,
        window_title="demo_testapp",
        window_size=(600, 400),
        run_speed=testing.TestRunSpeed.normal,
        exit_after_test=EXIT_AFTER_TESTS
    )
    print(f"Wrote 5 PNGs to {SCREENSHOTS_FOLDER}")


if __name__ == "__main__":
    main()
