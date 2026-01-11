"""Type stubs for immapp.nb notebook convenience API.

Full documentation is in the implementation file (nb.py).
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
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
) -> None: ...

# start() - Non-blocking async mode
@overload
def start(
    runner_params: RunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> asyncio.Task: ...

@overload
def start(
    simple_params: SimpleRunnerParams,
    addons_params: Optional[AddOnsParams] = None
) -> asyncio.Task: ...

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
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
) -> asyncio.Task: ...

# stop() and is_running()
def stop() -> None: ...
def is_running() -> bool: ...
