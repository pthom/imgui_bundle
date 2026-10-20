"""Test imgui.begin_simple: a bool (False when the window is collapsed), and the flags reach the window"""

from imgui_bundle import hello_imgui, imgui


def test_begin_simple() -> None:
    results: dict[str, int] = {}  # two bools and the window's flags

    def gui() -> None:
        results["expanded"] = imgui.begin_simple("Expanded", imgui.WindowFlags_.no_title_bar)
        results["flags"] = imgui.internal.get_current_window().flags
        imgui.end()

        imgui.set_next_window_collapsed(True)
        results["collapsed"] = imgui.begin_simple("Collapsed")
        imgui.end()

        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    hello_imgui.run(gui, window_title="Test begin_simple", window_size=(400, 200))

    assert results["expanded"] is True, results
    assert results["collapsed"] is False, results
    assert results["flags"] & imgui.WindowFlags_.no_title_bar, results
    print("OK test_begin_simple")
