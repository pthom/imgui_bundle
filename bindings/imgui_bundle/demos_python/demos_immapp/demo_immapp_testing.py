# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""
immapp.testing: a script drives the app, captures screenshots, then exits.

Easy automated tests with `immapp.testing`, a thin layer on the test engine: a script drives the app, then exits.
The test engine demo shows the engine itself. Here, a test function drives the GUI (it clicks, moves a slider, opens
a header) and captures a picture at each step; `immapp.testing.run()` starts the app, runs the test, then exits.
The same recipe gives documentation pictures, and lets an AI agent see and drive the app it writes, with nobody at
the mouse (the bundle's screenshot skills are built on it).
See the [test engine doc](https://imgui-bundle.pages.dev/doc/core-libs/test-engine/).

Customization: edit `EXIT_AFTER_TESTS`. The five screenshots go to a temporary folder, printed at the end of the test.
"""

from __future__ import annotations

from imgui_bundle import imgui
from imgui_bundle.immapp import testing
import os
import tempfile

SCREENSHOTS_FOLDER = tempfile.mkdtemp(prefix="demo_immapp_testing_")  # where the screenshots go
EXIT_AFTER_TESTS = True


class State:
    counter: int = 0
    slider_value: int = 0
    checkbox: bool = False


state = State()


def gui() -> None:
    imgui.text("demo_immapp_testing: exercise these widgets under the test engine")
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

    print(f"Wrote 5 PNGs to {SCREENSHOTS_FOLDER}")


def main() -> None:

    # Reset state so the captures are deterministic, regardless of repeated runs.
    state.counter = 0
    state.slider_value = 0
    state.checkbox = False

    testing.run(
        gui_function=gui,
        test_function=screenshot_test,
        window_title="demo_immapp_testing",
        window_size=(600, 400),
        run_speed=testing.TestRunSpeed.normal,
        exit_after_test=EXIT_AFTER_TESTS
    )


if __name__ == "__main__":
    main()
