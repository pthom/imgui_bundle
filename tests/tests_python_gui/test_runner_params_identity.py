"""Test that runner_params identity is preserved between user code and HelloImGui internals.

This test verifies the fix for the issue where ManualRender::SetupFromRunnerParams
used to make a copy of RunnerParams, causing inconsistencies between the user's
RunnerParams and the internal state accessed via hello_imgui.get_runner_params().

After the fix, both Run() and ManualRender::SetupFromRunnerParams() keep a reference
to the user's RunnerParams, so modifications to runner_params are reflected in
hello_imgui.get_runner_params() and vice versa.
"""

def test_runner_params_identity_with_manual_render():
    """Test that runner_params identity is preserved when using manual_render."""
    from imgui_bundle import hello_imgui, imgui

    # Track if the GUI function was called
    gui_called = [False]

    # Create RunnerParams
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test Runner Params Identity"
    runner_params.app_window_params.window_geometry.size = (800, 600)

    def gui():
        gui_called[0] = True
        imgui.text("Testing runner_params identity")

        # Get the runner params from HelloImGui
        internal_runner_params = hello_imgui.get_runner_params()

        # Check that they are the SAME object (not just equal values)
        assert id(runner_params) == id(internal_runner_params), \
            f"runner_params identity mismatch: user={id(runner_params)}, internal={id(internal_runner_params)}"

        # Verify that modifications to runner_params are reflected
        runner_params.app_window_params.window_title = "Modified Title"
        assert internal_runner_params.app_window_params.window_title == "Modified Title", \
            "Modifications to runner_params should be reflected in internal runner_params"

        # Signal to exit
        hello_imgui.get_runner_params().app_shall_exit = True

    runner_params.callbacks.show_gui = gui

    # Setup and run using manual_render
    hello_imgui.manual_render.setup_from_runner_params(runner_params)

    # Run a few frames
    for _ in range(5):
        hello_imgui.manual_render.render()
        if runner_params.app_shall_exit:
            break

    hello_imgui.manual_render.tear_down()

    assert gui_called[0], "GUI function should have been called"
    print("✓ runner_params identity preserved with manual_render")


def test_runner_params_identity_with_immapp_manual_render():
    """Test that runner_params identity is preserved when using immapp.manual_render."""
    from imgui_bundle import hello_imgui, imgui, immapp

    # Track if the GUI function was called
    gui_called = [False]

    # Create RunnerParams
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test ImmApp Runner Params Identity"
    runner_params.app_window_params.window_geometry.size = (800, 600)

    def gui():
        gui_called[0] = True
        imgui.text("Testing immapp runner_params identity")

        # Get the runner params from HelloImGui
        internal_runner_params = hello_imgui.get_runner_params()

        # Check that they are the SAME object (not just equal values)
        assert id(runner_params) == id(internal_runner_params), \
            f"runner_params identity mismatch: user={id(runner_params)}, internal={id(internal_runner_params)}"

        # Verify that modifications to runner_params are reflected
        runner_params.app_window_params.window_title = "Modified ImmApp Title"
        assert internal_runner_params.app_window_params.window_title == "Modified ImmApp Title", \
            "Modifications to runner_params should be reflected in internal runner_params"

        # Signal to exit
        hello_imgui.get_runner_params().app_shall_exit = True

    runner_params.callbacks.show_gui = gui

    # Setup and run using immapp.manual_render
    immapp.manual_render.setup_from_runner_params(runner_params)

    # Run a few frames
    for _ in range(5):
        immapp.manual_render.render()
        if runner_params.app_shall_exit:
            break

    immapp.manual_render.tear_down()

    assert gui_called[0], "GUI function should have been called"
    print("✓ runner_params identity preserved with immapp.manual_render")


if __name__ == "__main__":
    print("Testing runner_params identity preservation...")
    print()

    print("Test 1: manual_render")
    test_runner_params_identity_with_manual_render()
    print()

    print("Test 2: immapp.manual_render")
    test_runner_params_identity_with_immapp_manual_render()
    print()

    print("All tests passed! ✓")

