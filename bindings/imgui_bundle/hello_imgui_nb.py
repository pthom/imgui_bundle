"""Notebook convenience API for hello_imgui.

This module provides non-blocking GUI execution for Jupyter notebooks using hello_imgui.
It's similar to immapp.nb but without AddOnsParams support.

Functions:
    run() - Blocking mode (delegates to hello_imgui.run)
    start() - Non-blocking async mode with notebook-friendly defaults
    stop() - Stop the running GUI
    is_running() - Check if GUI is running
"""

import asyncio
from typing import Optional


# Track the current running task
_current_task: Optional[asyncio.Task] = None


def is_running() -> bool:
    """Check if a GUI is currently running.

    Returns:
        bool: True if a GUI task is active and not done, False otherwise.

    Example:
        if hello_imgui.nb.is_running():
            print("GUI is active")
    """
    global _current_task
    return _current_task is not None and not _current_task.done()


def stop() -> None:
    """Stop the currently running GUI by setting app_shall_exit flag.

    This is a convenience function that sets the exit flag for the running GUI.
    The GUI will close on its next render cycle.

    Example:
        hello_imgui.nb.stop()  # Close the current GUI
    """
    if is_running():
        try:
            from imgui_bundle import hello_imgui
            hello_imgui.get_runner_params().app_shall_exit = True
        except Exception:
            pass  # Ignore if runner params not available
    else:
        print("Warning: No GUI is currently running")


def run(*args, **kwargs):
    """Run a hello_imgui application in blocking mode.

    This is a convenience wrapper that delegates to hello_imgui.run(),
    which runs the GUI and waits for it to close.

    Note: Unlike immapp.run, this does NOT automatically add light theme
    or screenshot functionality (hello_imgui doesn't have those features).

    Signatures:
        run(runner_params: RunnerParams)
        run(simple_params: SimpleRunnerParams)
        run(gui_function, window_title="", ...)

    Example:
        def my_gui():
            imgui.text("Hello from notebook!")

        hello_imgui.nb.run(my_gui, window_title="My App")
        # Blocks until window closed
    """
    from imgui_bundle import hello_imgui
    return hello_imgui.run(*args, **kwargs)


def start(*args, **kwargs) -> asyncio.Task:
    """Start a hello_imgui application in non-blocking mode for interactive notebook use.

    This function starts a GUI that runs asynchronously, allowing you to:
    - Continue executing other notebook cells while the GUI is open
    - Modify variables from other cells and see updates in real-time
    - Run multiple sequential GUIs (close one before starting another)

    The function automatically applies notebook-friendly defaults:
    - window_size_auto=True (if not specified)
    - top_most=True (if not specified)

    If a GUI is already running, it will be automatically stopped with a warning.

    Signatures:
        start(runner_params: RunnerParams) -> asyncio.Task
        start(simple_params: SimpleRunnerParams) -> asyncio.Task
        start(gui_function, window_title="", window_size_auto=True, ...) -> asyncio.Task

    Args:
        *args: RunnerParams, SimpleRunnerParams, or gui_function
        **kwargs: Additional parameters when using gui_function signature

    Returns:
        asyncio.Task: The task running the GUI

    Example:
        counter = {"value": 0}

        def my_gui():
            imgui.text(f"Counter: {counter['value']}")
            if imgui.button("Increment"):
                counter["value"] += 1

        hello_imgui.nb.start(my_gui, window_title="Counter")

        # In another cell:
        counter["value"] = 100  # Updates in real-time!

        # To stop:
        hello_imgui.nb.stop()
    """
    global _current_task

    # Check if a GUI is already running
    if is_running():
        print("Warning: A GUI is already running. Stopping it first...")
        stop()
        # Give it time to stop
        import time
        time.sleep(0.2)

    # Import here to avoid circular imports
    from imgui_bundle import hello_imgui
    RunnerParams = hello_imgui.RunnerParams  # type: ignore
    SimpleRunnerParams = hello_imgui.SimpleRunnerParams  # type: ignore

    # Determine which signature is being used and apply defaults
    if len(args) >= 1:
        first_arg = args[0]

        # Case 1: RunnerParams
        if isinstance(first_arg, RunnerParams):
            runner_params = first_arg

            # Apply notebook-friendly defaults
            # Note: RunnerParams doesn't have simple properties, need to access nested structures
            # if not runner_params.app_window_params.window_geometry.size_auto:
            #     runner_params.app_window_params.window_geometry.size_auto = True

            # Create the task
            _current_task = asyncio.create_task(
                hello_imgui.run_async(runner_params)
            )

        # Case 2: SimpleRunnerParams
        elif isinstance(first_arg, SimpleRunnerParams):
            simple_params = first_arg

            # Apply notebook-friendly defaults
            # if not simple_params.window_size_auto:
            #     simple_params.window_size_auto = True

            # Create the task
            _current_task = asyncio.create_task(
                hello_imgui.run_async(simple_params)
            )

        # Case 3: GUI function with keyword arguments
        elif callable(first_arg):
            gui_function = first_arg

            # Apply notebook-friendly defaults to kwargs
            if "window_size_auto" not in kwargs and "window_size" not in kwargs:
                kwargs["window_size_auto"] = True

            # Create the task
            _current_task = asyncio.create_task(
                hello_imgui.run_async(gui_function, *args[1:], **kwargs)
            )
        else:
            raise TypeError(f"First argument must be RunnerParams, SimpleRunnerParams, or a callable GUI function, got {type(first_arg)}")
    else:
        raise TypeError("start() requires at least one argument")

    return _current_task
