"""Run a Hello ImGui app from a Jupyter notebook. Import it as `hello_imgui.nb`.

- `run()`: runs the app and waits until its window closes, as `hello_imgui.run` does.
- `start()`: runs the app without blocking the notebook, which stays usable while the app runs. It returns an
  `asyncio.Task`.
- `stop()`, `is_running()`: stop the app started by `start()`, or query it.

`immapp.nb` does the same with the add-ons (ImPlot, markdown...), and its `run()` shows a screenshot of the app in
the notebook.
"""

from typing import Callable, Optional, overload
import asyncio
from imgui_bundle.hello_imgui import RunnerParams, SimpleRunnerParams

# run() - Blocking mode
@overload
def run(runner_params: RunnerParams) -> None: ...

@overload
def run(simple_params: SimpleRunnerParams) -> None: ...

@overload
def run(
    gui_function: Callable[[], None],
    *,
    window_title: str = "",
    window_size_auto: bool = False,
    window_restore_previous_geometry: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    fps_idle: float = 10.0,
    top_most: bool = False,
) -> None: ...

# start() - Non-blocking async mode
@overload
def start(runner_params: RunnerParams) -> asyncio.Task[None]: ...

@overload
def start(simple_params: SimpleRunnerParams) -> asyncio.Task[None]: ...

@overload
def start(
    gui_function: Callable[[], None],
    *,
    window_title: str = "",
    window_size_auto: bool = True,
    window_restore_previous_geometry: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    fps_idle: float = 10.0,
    top_most: bool = True,
) -> asyncio.Task[None]: ...

# stop() and is_running()
def stop() -> None: ...
def is_running() -> bool: ...
