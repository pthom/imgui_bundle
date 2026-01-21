# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""
Notebook-specific API for immapp - simplified async GUI execution in Jupyter notebooks.

This module provides convenient functions for running ImGui apps in Jupyter notebooks:
- run(): Blocking execution with screenshot output (delegates to patched immapp.run)
- start(): Non-blocking execution, returns auto-started asyncio.Task
- stop(): Stop the currently running async GUI
- is_running(): Check if an async GUI is currently running
"""
import asyncio
from typing import Optional

# from imgui_bundle._imgui_bundle.immapp_cpp import AddOnsParams  # type: ignore
from imgui_bundle._imgui_bundle.hello_imgui import (  # type: ignore
    RunnerParams,
    SimpleRunnerParams,
)


# Global state for tracking the current async GUI task
_current_task: Optional[asyncio.Task] = None


def is_running() -> bool:
    """Check if an async GUI is currently running.

    Returns:
        True if a GUI started with start() is currently running, False otherwise

    Example:
        if immapp.nb.is_running():
            print("GUI is running")
        else:
            print("No GUI running")
    """
    global _current_task
    return _current_task is not None and not _current_task.done()


def stop() -> None:
    """Stop the currently running async GUI.

    This sets the app_shall_exit flag, causing the GUI to close gracefully.
    The GUI will clean up and the task will complete.

    Example:
        task = immapp.nb.start(my_gui)
        # ... work in other cells ...
        immapp.nb.stop()  # Close the GUI
    """
    if not is_running():
        print("Warning: No GUI is currently running")
        return

    from imgui_bundle import hello_imgui
    hello_imgui.get_runner_params().app_shall_exit = True


def run(*args, **kwargs):
    """Run an ImGui application in blocking mode with screenshot output.

    This is a convenience wrapper that delegates to the patched immapp.run(),
    which runs the GUI, waits for it to close, and displays a screenshot in
    the notebook cell output.

    Signatures:
        run(runner_params: RunnerParams, addons_params: Optional[AddOnsParams] = None)
        run(simple_params: SimpleRunnerParams, addons_params: Optional[AddOnsParams] = None)
        run(gui_function, window_title="", ..., with_implot=False, ...)

    Example:
        def my_gui():
            imgui.text("Hello from notebook!")

        immapp.nb.run(my_gui, window_title="My App", window_size_auto=True)
        # Screenshot appears in cell output after closing

    Additional parameters to controls the thumbnail screenshot:
    * thumbnail_ratio: (default=1.0)
      You can use it to change the size of the thumbnail.
      Passing 0.5 will create a thumbnail half the width of the window.
    * thumbnail_height: (default=0)
      You can use it to set a fixed height for the thumbnail (in pixels).
      If 0, the height is computed from the app window size.
    (choose only one of the two parameters to control size)
    """
    from imgui_bundle import immapp
    return immapp.run(*args, **kwargs)


def start(*args, **kwargs) -> asyncio.Task:
    """Start an ImGui application in non-blocking mode for interactive notebook use.

    This function starts a GUI that runs asynchronously, allowing you to:
    - Continue executing other notebook cells while the GUI is open
    - Modify variables from other cells and see updates in real-time
    - Run multiple sequential GUIs (close one before starting another)

    The function automatically applies notebook-friendly defaults:
    - Light theme for better visibility
    - window_size_auto=True (if not specified)
    - top_most=True (if not specified)

    If a GUI is already running, it will be automatically stopped with a warning.

    Signatures:
        start(runner_params: RunnerParams, addons_params: Optional[AddOnsParams] = None)
        start(simple_params: SimpleRunnerParams, addons_params: Optional[AddOnsParams] = None)
        start(gui_function, window_title="", ..., with_implot=False, ...)

    Returns:
        asyncio.Task: The task running the GUI (can be awaited if needed)

    Example:
        def my_gui():
            global freq
            changed, freq = imgui.slider_float("Frequency", freq, 0.1, 10.0)

        # Start the GUI
        task = immapp.nb.start(my_gui, with_implot=True, window_size_auto=True)
        print("GUI started")

        # In another cell: modify variables
        freq = 5.0  # GUI updates immediately!

        # In another cell: close the GUI
        immapp.nb.stop()
    """
    global _current_task

    # Check if a GUI is already running and stop it
    if is_running():
        print("Warning: A GUI is already running. Stopping it first...")
        stop()
        # Give it a moment to clean up
        import time
        time.sleep(0.2)

    # Import here to avoid circular imports
    from imgui_bundle import immapp
    from imgui_bundle.immapp.immapp_notebook import _make_gui_with_light_theme

    # Determine which signature is being used and apply defaults
    if len(args) >= 1:
        first_arg = args[0]

        # Case 1: RunnerParams
        if isinstance(first_arg, RunnerParams):
            runner_params = first_arg
            addons_params = args[1] if len(args) > 1 else kwargs.get("addons_params", None)

            # Apply notebook-friendly defaults
            # if runner_params.app_window_params.window_geometry.size_auto is None:
            #     runner_params.app_window_params.window_geometry.size_auto = True
            # if not runner_params.app_window_params.top_most:
            #     runner_params.app_window_params.top_most = True

            # Wrap GUI function with light theme
            if runner_params.callbacks.show_gui is not None:
                original_gui = runner_params.callbacks.show_gui
                runner_params.callbacks.show_gui = _make_gui_with_light_theme(original_gui)

            # Create the task
            _current_task = asyncio.create_task(
                immapp.run_async(runner_params, addons_params)
            )

        # Case 2: SimpleRunnerParams
        elif isinstance(first_arg, SimpleRunnerParams):
            simple_params = first_arg
            addons_params = args[1] if len(args) > 1 else kwargs.get("addons_params", None)

            # Apply notebook-friendly defaults
            # if not simple_params.window_size_auto:
            #     simple_params.window_size_auto = True
            # if not simple_params.top_most:
            #     simple_params.top_most = True

            # Wrap GUI function with light theme
            if simple_params.gui_function is not None:
                original_gui = simple_params.gui_function
                simple_params.gui_function = _make_gui_with_light_theme(original_gui)

            # Create the task
            _current_task = asyncio.create_task(
                immapp.run_async(simple_params, addons_params)
            )

        # Case 3: GUI function with keyword arguments
        elif callable(first_arg):
            gui_function = first_arg

            # Wrap GUI function with light theme
            gui_with_theme = _make_gui_with_light_theme(gui_function)

            # Apply notebook-friendly defaults to kwargs
            if "window_size_auto" not in kwargs and "window_size" not in kwargs:
                kwargs["window_size_auto"] = True

            # Create the task
            _current_task = asyncio.create_task(
                immapp.run_async(gui_with_theme, *args[1:], **kwargs)
            )
        else:
            raise TypeError(f"First argument must be RunnerParams, SimpleRunnerParams, or a callable GUI function, got {type(first_arg)}")
    else:
        raise TypeError("start() requires at least one argument")

    return _current_task
