"""Demonstrate how immapp.run_async enables parallel Python execution with GUI rendering.

This demo runs a computation loop in Python while the GUI remains responsive.
By calling `immapp.run_async`, the GUI runs in an asyncio Task, allowing Python code to execute concurrently.

`immapp.run_async` automatically adjusts FPS idling parameters to optimize performance, so that the Python loop
can run at maximum speed.

The settings below are applied automatically by `immapp.run_async` to ensure that the GUI rendering
returns early to Python instead of sleeping, allowing maximum parallelism between GUI rendering and Python code execution:
```python
    runner_params.fps_idling.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return
    runner_params.fps_idling.vsync_to_monitor = False
    runner_params.fps_idling.fps_max = 60.0
```
"""

import asyncio
import time
from imgui_bundle import immapp, imgui, hello_imgui


GUI_FINISHED = False
COMPUTATION_COUNT = 0
START_TIME = time.time()

def gui():
    params = hello_imgui.get_runner_params()
    idling_params = params.fps_idling
    idling_params.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return
    idling_params.vsync_to_monitor = False
    idling_params.fps_max = 60.0

    imgui.text(f"GUI FPS: {hello_imgui.frame_rate():.1f}")
    imgui.text(f"Computations per second: {COMPUTATION_COUNT / (time.time() - START_TIME):.1f}")
    global GUI_FINISHED
    GUI_FINISHED = hello_imgui.get_runner_params().app_shall_exit


async def python_computation_loop():
    """Run computations while GUI is active."""
    """Python code which runs in parallel with the GUI!"""
    global COMPUTATION_COUNT
    while not GUI_FINISHED:
        _ = sum(range(1000)) # Do some work
        COMPUTATION_COUNT += 1
        await asyncio.sleep(0) # Yield to event loop (required for async cooperation)


async def main():
    # Start GUI as an asyncio task (non-blocking)
    _gui_task = asyncio.create_task(immapp.run_async(gui, window_size_auto=True))
    # Run computations in parallel
    await python_computation_loop()


if __name__ == "__main__":
    asyncio.run(main())
