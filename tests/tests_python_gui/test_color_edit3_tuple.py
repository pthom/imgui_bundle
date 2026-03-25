"""Test that color_edit3 and color_picker3 accept 3-element ImVec4 and tuples/lists (issue #444)"""

from imgui_bundle import hello_imgui, imgui, ImVec4


def test_color_edit3_accepts_tuples():
    results = {}

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test color_edit3 tuples"
    runner_params.app_window_params.window_geometry.size = (400, 300)

    def gui():
        # 3-tuple
        changed, col = imgui.color_edit3("t3", (0.5, 0.3, 0.1))
        results["tuple3_type"] = type(col).__name__
        results["tuple3_len"] = len(col)

        # 3-list
        changed, col = imgui.color_edit3("l3", [0.5, 0.3, 0.1])
        results["list3_type"] = type(col).__name__
        results["list3_len"] = len(col)

        # ImVec4
        changed, col = imgui.color_edit3("v4", ImVec4(0.5, 0.3, 0.1, 0.8))
        results["imvec4_type"] = type(col).__name__

        # 4-tuple (should still work, passthrough to C++ binding)
        changed, col = imgui.color_edit3("t4", (0.5, 0.3, 0.1, 1.0))
        results["tuple4_type"] = type(col).__name__

        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    hello_imgui.run(gui)

    assert results["tuple3_type"] == "list", f"3-tuple should return list, got {results['tuple3_type']}"
    assert results["tuple3_len"] == 3, f"3-tuple should return 3 elements, got {results['tuple3_len']}"
    assert results["list3_type"] == "list", f"3-list should return list, got {results['list3_type']}"
    assert results["list3_len"] == 3, f"3-list should return 3 elements, got {results['list3_len']}"
    assert results["imvec4_type"] == "ImVec4", f"ImVec4 should return ImVec4, got {results['imvec4_type']}"
    assert results["tuple4_type"] == "ImVec4", f"4-tuple should return ImVec4, got {results['tuple4_type']}"
    print("OK test_color_edit3_accepts_tuples")


def test_color_picker3_accepts_tuples():
    results = {}

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test color_picker3 tuples"
    runner_params.app_window_params.window_geometry.size = (400, 400)

    def gui():
        changed, col = imgui.color_picker3("p3", (0.5, 0.3, 0.1))
        results["tuple3_type"] = type(col).__name__
        results["tuple3_len"] = len(col)

        changed, col = imgui.color_picker3("pv4", ImVec4(0.5, 0.3, 0.1, 0.8))
        results["imvec4_type"] = type(col).__name__

        if imgui.get_frame_count() == 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    hello_imgui.run(gui)

    assert results["tuple3_type"] == "list", f"3-tuple should return list, got {results['tuple3_type']}"
    assert results["tuple3_len"] == 3
    assert results["imvec4_type"] == "ImVec4", f"ImVec4 should return ImVec4, got {results['imvec4_type']}"
    print("OK test_color_picker3_accepts_tuples")


if __name__ == "__main__":
    print("Testing color_edit3/color_picker3 tuple support (issue #444)...")
    print()
    test_color_edit3_accepts_tuples()
    test_color_picker3_accepts_tuples()
    print()
    print("All tests passed!")
