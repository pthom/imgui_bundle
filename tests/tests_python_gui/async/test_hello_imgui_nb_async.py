"""Comprehensive async tests for hello_imgui.nb module.

These tests verify the non-blocking GUI functionality provided by hello_imgui.nb.
"""

import pytest
import asyncio
from imgui_bundle import hello_imgui, imgui
from imgui_bundle.demos_python import demo_utils

# Setup assets folder for tests
demo_utils.set_hello_imgui_demo_assets_folder()


@pytest.mark.asyncio
async def test_nb_start_with_gui_function():
    """Test hello_imgui.nb.start() with gui_function."""
    counter = {"value": 0}

    def my_gui():
        imgui.text(f"Counter: {counter['value']}")
        if counter["value"] >= 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    # Start the GUI
    hello_imgui.nb.start(my_gui, window_title="Test", window_size_auto=True)

    # Verify it's running
    assert hello_imgui.nb.is_running(), "GUI should be running"

    # Modify counter while GUI runs
    for i in range(5):
        counter["value"] = i
        await asyncio.sleep(0.05)

    # Wait for exit
    await asyncio.sleep(0.2)
    assert not hello_imgui.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_start_with_simple_params():
    """Test hello_imgui.nb.start() with SimpleRunnerParams."""
    exit_flag = {"value": False}

    def my_gui():
        imgui.text("Simple params test")
        if exit_flag["value"]:
            hello_imgui.get_runner_params().app_shall_exit = True

    simple_params = hello_imgui.SimpleRunnerParams()
    simple_params.gui_function = my_gui
    simple_params.window_title = "Simple Test"

    hello_imgui.nb.start(simple_params)
    assert hello_imgui.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)
    exit_flag["value"] = True
    await asyncio.sleep(0.2)

    assert not hello_imgui.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_start_with_runner_params():
    """Test hello_imgui.nb.start() with RunnerParams."""
    exit_flag = {"value": False}

    def my_gui():
        imgui.text("Runner params test")
        if exit_flag["value"]:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = my_gui
    runner_params.app_window_params.window_title = "Runner Test"

    hello_imgui.nb.start(runner_params)
    assert hello_imgui.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)
    exit_flag["value"] = True
    await asyncio.sleep(0.2)

    assert not hello_imgui.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_stop():
    """Test hello_imgui.nb.stop() functionality."""
    def my_gui():
        imgui.text("Test stop")

    hello_imgui.nb.start(my_gui, window_title="Stop Test")
    assert hello_imgui.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)

    # Stop the GUI
    hello_imgui.nb.stop()
    await asyncio.sleep(0.2)

    assert not hello_imgui.nb.is_running(), "GUI should have stopped"


@pytest.mark.asyncio
async def test_nb_is_running():
    """Test hello_imgui.nb.is_running() state tracking."""
    # Initially not running
    assert not hello_imgui.nb.is_running(), "Should not be running initially"

    def my_gui():
        imgui.text("Test")

    # Start GUI
    hello_imgui.nb.start(my_gui, window_title="Running Test")
    assert hello_imgui.nb.is_running(), "Should be running after start"

    await asyncio.sleep(0.1)

    # Stop GUI
    hello_imgui.nb.stop()
    await asyncio.sleep(0.2)

    assert not hello_imgui.nb.is_running(), "Should not be running after stop"


@pytest.mark.asyncio
async def test_nb_variable_updates():
    """Test that variables can be updated while GUI is running."""
    data = {"counter": 0, "text": "Initial"}

    def my_gui():
        imgui.text(f"Counter: {data['counter']}")
        imgui.text(f"Text: {data['text']}")
        if data["counter"] >= 5:  # type: ignore
            hello_imgui.get_runner_params().app_shall_exit = True

    hello_imgui.nb.start(my_gui, window_title="Variable Test")

    # Update variables while running
    for i in range(6):
        data["counter"] = i
        data["text"] = f"Iteration {i}"
        await asyncio.sleep(0.05)

    await asyncio.sleep(0.2)

    # Verify final state
    assert data["counter"] == 5, "Counter should be 5"
    assert data["text"] == "Iteration 5", "Text should be 'Iteration 5'"


@pytest.mark.asyncio
async def test_run_async_double_setup_does_not_tear_down_first():
    """Regression test mirroring the immapp version, but exercising the
    HelloImGui::ManualRender state machine instead of immapp's.

    Two concurrent hello_imgui.run_async() tasks: the second's setup must
    raise RuntimeError ("...already initialized...") AND must leave the
    first task's renderer untouched. Pre-fix, if any state mutation in
    HelloImGui::ManualRender::SetupFrom* runs before the not-initialized
    check, the first task's renderer is corrupted (segfault on Linux,
    silent freeze elsewhere).
    """
    gui1_frames = 0

    def gui1():
        nonlocal gui1_frames
        gui1_frames += 1

    def gui2():
        pass  # never reached — setup will throw

    task1 = asyncio.create_task(hello_imgui.run_async(gui1, window_title="HI_GUI1"))
    await asyncio.sleep(0.5)
    assert gui1_frames > 0, "GUI 1 should have rendered at least one frame"
    frames_at_collision = gui1_frames

    task2 = asyncio.create_task(hello_imgui.run_async(gui2, window_title="HI_GUI2"))
    await asyncio.sleep(0.3)
    assert task2.done(), "Task 2 should have failed quickly during setup"
    exc = task2.exception()
    assert isinstance(exc, RuntimeError), f"Expected RuntimeError, got {exc!r}"
    assert "already initialized" in str(exc)

    await asyncio.sleep(0.3)
    assert not task1.done(), f"GUI 1 should still be running, got: {task1.exception() if task1.done() else 'done'}"
    assert gui1_frames > frames_at_collision, "GUI 1 should keep rendering after the failed task 2"

    hello_imgui.get_runner_params().app_shall_exit = True
    await task1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
