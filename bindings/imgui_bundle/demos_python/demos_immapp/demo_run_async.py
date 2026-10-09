"""
Run Python code alongside the GUI with immapp.run_async.

The GUI runs as an [asyncio](https://docs.python.org/3/library/asyncio.html) task, while a Python loop keeps
computing. The window shows both rates: the GUI's frames per second, and the loop's computations per second. The loop
works in short slices, and yields between them with `await asyncio.sleep(...)` to share the event loop. See [async
support](https://imgui-bundle.pages.dev/doc/python/python-async/).

## In the browser

It runs in the browser too, with [Pyodide](https://pyodide.org), whose event loop is the browser's: there, the loop
sleeps a little longer between its slices (20 ms), so that the browser can draw the page.

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
import sys
import time
from imgui_bundle import immapp, imgui, hello_imgui

IS_BROWSER = sys.platform == "emscripten"  # Pyodide
WORK_SLICE = 0.01  # s: how long the loop computes before it yields
YIELD_SECONDS = 0.02 if IS_BROWSER else 0.0  # the browser draws the page only while the loop sleeps

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
        slice_start = time.perf_counter()
        while time.perf_counter() - slice_start < WORK_SLICE:
            _ = sum(range(1000)) # Do some work
            COMPUTATION_COUNT += 1
        await asyncio.sleep(YIELD_SECONDS) # Yield to event loop (required for async cooperation)


async def main():
    # Start GUI as an asyncio task (non-blocking)
    gui_task = asyncio.create_task(immapp.run_async(gui, window_size_auto=True))
    # Run computations in parallel
    await python_computation_loop(gui_task)


if __name__ == "__main__":
    if IS_BROWSER:  # Pyodide runs an event loop already
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())
