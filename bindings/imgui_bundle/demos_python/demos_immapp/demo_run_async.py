"""
Run Python code alongside the GUI with immapp.run_async.

The GUI runs as an [asyncio](https://docs.python.org/3/library/asyncio.html) task, while a Python loop keeps
computing. The window shows both rates: the GUI's frames per second, and the loop's computations per second. The loop
yields with `await asyncio.sleep(0)` to share the event loop. See [async
support](https://imgui-bundle.pages.dev/doc/python/python-async/).

## Idling

`immapp.run_async` adjusts the FPS idling parameters, so that the GUI returns early to Python instead of sleeping,
and the Python loop runs at full speed:
```python
    runner_params.fps_idling.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return
    runner_params.fps_idling.vsync_to_monitor = False
    runner_params.fps_idling.fps_max = 60.0
```
"""

import asyncio
import time
from imgui_bundle import immapp, imgui, hello_imgui


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


async def python_computation_loop(gui_task: asyncio.Task[None]):
    """Run computations while GUI is active."""
    """Python code which runs in parallel with the GUI!"""
    global COMPUTATION_COUNT
    while not gui_task.done():  # the GUI task ends when the app exits
        _ = sum(range(1000)) # Do some work
        COMPUTATION_COUNT += 1
        await asyncio.sleep(0) # Yield to event loop (required for async cooperation)


async def main():
    # Start GUI as an asyncio task (non-blocking)
    gui_task = asyncio.create_task(immapp.run_async(gui, window_size_auto=True))
    # Run computations in parallel
    await python_computation_loop(gui_task)


if __name__ == "__main__":
    asyncio.run(main())
