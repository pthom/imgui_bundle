"""Type stubs for hello_imgui.nb notebook convenience API.

This module provides notebook-friendly wrappers for hello_imgui (without AddOnsParams).
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
def start(runner_params: RunnerParams) -> asyncio.Task: ...

@overload
def start(simple_params: SimpleRunnerParams) -> asyncio.Task: ...

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
) -> asyncio.Task: ...

# stop() and is_running()
def stop() -> None: ...
def is_running() -> bool: ...
