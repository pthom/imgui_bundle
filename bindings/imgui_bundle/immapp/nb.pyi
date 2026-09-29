"""Run an ImmApp app from a Jupyter notebook, with its add-ons (ImPlot, markdown...). Use it as `immapp.nb`.

- `run()`: runs the app and waits until its window closes, then shows a screenshot of it in the notebook.
- `start()`: runs the app without blocking the notebook, which stays usable while the app runs. It returns an
  `asyncio.Task`.
- `stop()`, `is_running()`: stop the app started by `start()`, or query it.

`hello_imgui.nb` does the same without the add-ons.
"""

from typing import Callable, Optional, overload
import asyncio
from imgui_bundle.hello_imgui import RunnerParams, SimpleRunnerParams
from imgui_bundle.immapp import AddOnsParams

# run() - Blocking mode with screenshot
@overload
def run(
    runner_params: RunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> None: ...

@overload
def run(
    simple_params: SimpleRunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> None: ...

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
    ini_disable: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
    with_latex: bool = False,
) -> None: ...

# start() - Non-blocking async mode
@overload
def start(
    runner_params: RunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> asyncio.Task[None]: ...

@overload
def start(
    simple_params: SimpleRunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> asyncio.Task[None]: ...

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
    ini_disable: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
    with_latex: bool = False,
) -> asyncio.Task[None]: ...

# stop() and is_running()
def stop() -> None: ...
def is_running() -> bool: ...
