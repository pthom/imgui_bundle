# Async Support

_(Since v1.92.6)_

ImGui Bundle provides async/await support that enables **true parallel execution** of Python code alongside GUI rendering. This allows your Python computations to run at full speed while the GUI remains responsive.

_Note: an async execution mode is also available for Jupyter notebooks; see [Notebook Usage](notebook_runners.md) for details._

## Overview

`immapp.run_async()` and `hello_imgui.run_async()` function allows you to run ImGui applications asynchronously using Python's `asyncio` framework. This is particularly useful when:

- You need to perform computations while the GUI is running
- You're building data visualization dashboards with live updates
- You want to integrate ImGui into async Python applications
- You're working in Jupyter notebooks (see [Notebook Usage](notebook_runners.md))


## Quick Example

Here's a simple example showing parallel execution:

```python
import asyncio
import time
from imgui_bundle import immapp, imgui, hello_imgui, imgui_md


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
```

Also see
[`demos_immapp/demo_run_async.py`](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_run_async.py)


## Automatic FPS Optimization

`immapp.run_async` automatically adjusts FPS idling parameters to optimize performance, so that the Python loop
can run at maximum speed.

The settings below are applied automatically by `immapp.run_async` to ensure that the GUI rendering
returns early to Python instead of sleeping, allowing maximum parallelism between GUI rendering and Python code execution:

```python
    runner_params.fps_idling.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return
    runner_params.fps_idling.vsync_to_monitor = False
    runner_params.fps_idling.fps_max = 60.0
```


## Signature Patterns

`run_async()` supports two different ways to configure your application:

### 1. Simple GUI Function

```python
async def gui():
    imgui.text("Hello, World!")
    if imgui.button("Click me"):
        print("Button clicked!")

await immapp.run_async(
    gui,
    window_title="My App",
    window_size_auto=True,
    top_most=True,
    # Optional addons (immapp only)
    with_implot=True,
    with_markdown=True
)
```

### 2. Full RunnerParams (Maximum Control)

```python
from imgui_bundle import hello_imgui, immapp

runner_params = hello_imgui.RunnerParams()
runner_params.callbacks.show_gui = gui
runner_params.app_window_params.window_title = "My App"
runner_params.imgui_window_params.show_menu_bar = True

# With immapp, you can use AddOnsParams
addons = immapp.AddOnsParams()
addons.with_implot = True
addons.with_node_editor = True


asyncio.run(immapp.run_async(runner_params, addons))
```


## Yielding to the Event Loop

In your async code, you **must** regularly yield control to the event loop to allow the GUI to render:

```python
async def my_computation():
    while condition:
        # Do some work
        result = expensive_computation()

        # Yield to allow GUI rendering (critical!)
        await asyncio.sleep(0)
```

Without `await asyncio.sleep(0)`, the GUI will freeze because asyncio can't switch between tasks.


## Troubleshooting

### GUI Freezes

**Problem**: The GUI becomes unresponsive during computations.
**Solution**: Make sure to `await asyncio.sleep(0)` regularly in your computation loops.


### Exceptions in the async GUI

If your GUI raises an exception, it might be difficult to trace with the GUI is running in an async way.

In that case, it is recommended to first test your GUI in blocking mode using `immapp.run`, which will propagate exceptions normally.
Once your GUI works in blocking mode, you can then switch to non-blocking mode (`immapp.run_async`).

