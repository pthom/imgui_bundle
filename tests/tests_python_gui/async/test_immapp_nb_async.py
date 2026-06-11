"""Comprehensive async tests for immapp.nb module.

These tests verify the non-blocking GUI functionality provided by immapp.nb.
"""

import pytest
import asyncio
from imgui_bundle import immapp, imgui, hello_imgui
from imgui_bundle.demos_python import demo_utils
demo_utils.set_hello_imgui_demo_assets_folder()


@pytest.mark.asyncio
async def test_nb_start_with_gui_function():
    """Test immapp.nb.start() with gui_function."""
    counter = {"value": 0}

    def my_gui():
        imgui.text(f"Counter: {counter['value']}")
        if counter["value"] >= 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    # Start the GUI
    immapp.nb.start(my_gui, window_title="Test", window_size_auto=True)

    # Verify it's running
    assert immapp.nb.is_running(), "GUI should be running"

    # Modify counter while GUI runs
    for i in range(5):
        counter["value"] = i
        await asyncio.sleep(0.05)

    # Wait for exit
    await asyncio.sleep(0.2)
    assert not immapp.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_start_with_simple_params():
    """Test immapp.nb.start() with SimpleRunnerParams."""
    exit_flag = {"value": False}

    def my_gui():
        imgui.text("Simple params test")
        if exit_flag["value"]:
            hello_imgui.get_runner_params().app_shall_exit = True

    simple_params = hello_imgui.SimpleRunnerParams()
    simple_params.gui_function = my_gui
    simple_params.window_title = "Simple Test"

    immapp.nb.start(simple_params)
    assert immapp.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)
    exit_flag["value"] = True
    await asyncio.sleep(0.2)

    assert not immapp.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_start_with_runner_params_and_addons():
    """Test immapp.nb.start() with RunnerParams and AddOnsParams."""
    exit_flag = {"value": False}

    def my_gui():
        imgui.text("Runner params + addons test")
        if exit_flag["value"]:
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = my_gui
    runner_params.app_window_params.window_title = "Runner Test"

    addons = immapp.AddOnsParams()
    addons.with_implot = True

    immapp.nb.start(runner_params, addons)
    assert immapp.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)
    exit_flag["value"] = True
    await asyncio.sleep(0.2)

    assert not immapp.nb.is_running(), "GUI should have exited"


@pytest.mark.asyncio
async def test_nb_stop():
    """Test immapp.nb.stop() functionality."""
    def my_gui():
        imgui.text("Test stop")

    immapp.nb.start(my_gui, window_title="Stop Test")
    assert immapp.nb.is_running(), "GUI should be running"

    await asyncio.sleep(0.1)

    # Stop the GUI
    immapp.nb.stop()
    await asyncio.sleep(0.2)

    assert not immapp.nb.is_running(), "GUI should have stopped"


@pytest.mark.asyncio
async def nb_auto_stop_existing():
    """Test that starting a new GUI auto-stops the existing one."""
    sleep_after_start = 0.25  # time needed for the app to start and display its first frames

    gui2_active = True
    where_am_i  = ""

    def gui1():
        nonlocal where_am_i
        where_am_i = "gui1"
        imgui.text("GUI 1")
        imgui.text(f"Counter: {imgui.get_frame_count()} fps:{imgui.get_io().framerate}")

    def gui2():
        nonlocal gui2_active
        nonlocal where_am_i
        where_am_i = "gui2"
        imgui.text("GUI 2")
        imgui.text(f"Counter: {imgui.get_frame_count()} fps:{imgui.get_io().framerate}")
        if not gui2_active:
            hello_imgui.get_runner_params().app_shall_exit = True

    # Start first GUI
    immapp.nb.start(gui1, window_title="GUI 1")
    assert immapp.nb.is_running(), "GUI 1 should be running"
    await asyncio.sleep(sleep_after_start)  # The app takes a while to start
    assert where_am_i == "gui1"
    await asyncio.sleep(0.1)

    # Start second GUI - should auto-stop first
    immapp.nb.start(gui2, window_title="GUI 2")
    await asyncio.sleep(sleep_after_start)
    assert where_am_i == "gui2"
    await asyncio.sleep(0.1)

    assert immapp.nb.is_running(), "GUI 2 should be running"

    # Clean up
    gui2_active = False
    await asyncio.sleep(0.1)
    assert not immapp.nb.is_running(), "GUI 2 should be stopped"


@pytest.mark.asyncio
async def test_nb_is_running():
    """Test immapp.nb.is_running() state tracking."""
    # Initially not running
    assert not immapp.nb.is_running(), "Should not be running initially"

    def my_gui():
        imgui.text("Test")

    # Start GUI
    immapp.nb.start(my_gui, window_title="Running Test")
    assert immapp.nb.is_running(), "Should be running after start"

    await asyncio.sleep(0.1)

    # Stop GUI
    immapp.nb.stop()
    await asyncio.sleep(0.2)

    assert not immapp.nb.is_running(), "Should not be running after stop"


@pytest.mark.asyncio
async def test_nb_variable_updates():
    """Test that variables can be updated while GUI is running."""
    data = {"counter": 0, "text": "Initial"}

    def my_gui():
        imgui.text(f"Counter: {data['counter']}")
        imgui.text(f"Text: {data['text']}")
        if data["counter"] >= 5:  # type: ignore
            hello_imgui.get_runner_params().app_shall_exit = True

    immapp.nb.start(my_gui, window_title="Variable Test")

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
    """Regression test: a second concurrent run_async() must NOT corrupt the
    first runner.

    Bypasses nb.start() (which has its own auto-drain) to exercise the raw
    run_async() path. A second run_async() launched while the first is alive
    will hit `IM_ASSERT(...SetupFromXXX cannot be called while already
    initialized...)` inside `setup_from_gui_function`, which throws a
    RuntimeError. The bug: run_async()'s `finally: manual_render.tear_down()`
    then runs and tears down the GLOBAL renderer — which still belongs to the
    first task — causing a SIGSEGV on the first task's next render().

    The fix: setup must live OUTSIDE the try/finally that owns tear_down,
    so a setup that never took ownership cannot tear down state it doesn't
    own.
    """
    gui1_frames = 0

    def gui1():
        nonlocal gui1_frames
        gui1_frames += 1

    def gui2():
        pass  # never reached — setup will throw

    # Start GUI 1 directly via run_async (bypass nb.start auto-stop)
    task1 = asyncio.create_task(immapp.run_async(gui1, window_title="GUI1"))
    await asyncio.sleep(0.5)  # let it set up and render a few frames
    assert gui1_frames > 0, "GUI 1 should have rendered at least one frame"
    frames_at_collision = gui1_frames

    # Launch a second run_async while the first is still alive.
    # It MUST raise RuntimeError on setup, and MUST NOT tear down GUI 1.
    task2 = asyncio.create_task(immapp.run_async(gui2, window_title="GUI2"))
    await asyncio.sleep(0.3)
    assert task2.done(), "Task 2 should have failed quickly during setup"
    exc = task2.exception()
    assert isinstance(exc, RuntimeError), f"Expected RuntimeError, got {exc!r}"
    assert "already initialized" in str(exc)

    # GUI 1 must still be alive AND still rendering. Pre-fix this is where
    # the process either segfaults or task1 silently dies because its renderer
    # was torn down underneath it.
    await asyncio.sleep(0.3)
    assert not task1.done(), f"GUI 1 should still be running, got: {task1.exception() if task1.done() else 'done'}"
    assert gui1_frames > frames_at_collision, "GUI 1 should keep rendering after the failed task 2"

    # Clean shutdown of GUI 1
    hello_imgui.get_runner_params().app_shall_exit = True
    await task1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
