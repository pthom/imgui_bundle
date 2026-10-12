"""Test imgui.internal.separator_text_ex: the label is shown up to its "##", and same_line() places an item after it
(discussion #498: the C++ label_end could not be given from Python)"""

from imgui_bundle import hello_imgui, imgui


def test_separator_text_ex_label_and_extra_width() -> None:
    results = {}

    def gui() -> None:
        style = imgui.get_style()
        icon = "[i]"
        start_x = imgui.get_cursor_screen_pos().x
        imgui.internal.separator_text_ex(imgui.get_id("sep"), "Hello world##some_id", imgui.calc_text_size(icon).x)
        imgui.same_line()
        # SeparatorTextEx sets the previous line's end at the end of the label: same_line() starts there
        label_width = imgui.get_cursor_screen_pos().x - style.item_spacing.x - (start_x + style.separator_text_padding.x)
        imgui.text(icon)
        results["label_width"] = label_width
        results["expected_width"] = imgui.calc_text_size("Hello world").x

        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    hello_imgui.run(gui, window_title="Test separator_text_ex", window_size=(400, 200))

    assert abs(results["label_width"] - results["expected_width"]) < 1.0, results
    print("OK test_separator_text_ex_label_and_extra_width")
