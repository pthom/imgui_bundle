# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Async support for ImGui Bundle - enables non-blocking GUI execution."""
import asyncio
from typing import Optional, Callable, Tuple, overload

from imgui_bundle._imgui_bundle.immapp_cpp import AddOnsParams  # type: ignore
from imgui_bundle._imgui_bundle.hello_imgui import (  # type: ignore
    RunnerParams,
    SimpleRunnerParams,
)


@overload
async def run_async(
    runner_params: RunnerParams,
    addons_params: Optional[AddOnsParams] = None,
) -> None:
    """Run an application asynchronously using RunnerParams and AddOnsParams.

    This function will run until the application exits (user closes window or app_shall_exit is set).
    Use this when you need full control over the async lifecycle.

    Example:
        async def my_app():
            runner = hello_imgui.RunnerParams()
            runner.callbacks.show_gui = my_gui_function
            await immapp.run_async(runner)
            print("GUI closed")

        asyncio.run(my_app())
    """
    ...


@overload
async def run_async(
    simple_params: SimpleRunnerParams,
    addons_params: Optional[AddOnsParams] = None,
) -> None:
    """Run an application asynchronously using SimpleRunnerParams and AddOnsParams."""
    ...


@overload
async def run_async(
    gui_function: Callable[[], None],
    window_title: str = "",
    window_size_auto: bool = False,
    window_restore_previous_geometry: bool = False,
    window_size: Optional[Tuple[int, int]] = None,
    fps_idle: float = 10.0,
    top_most: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
) -> None:
    """Run an application asynchronously using a simple GUI function and parameters."""
    ...


async def run_async(*args, **kwargs) -> None:
    """Run an ImGui application asynchronously in a non-blocking way.

    This function provides async/await support for ImGui Bundle applications.
    It will run until the application exits (user closes window or app_shall_exit is set).

    Three signatures are supported:
    1. run_async(runner_params: RunnerParams, addons_params: Optional[AddOnsParams] = None)
    2. run_async(simple_params: SimpleRunnerParams, addons_params: Optional[AddOnsParams] = None)
    3. run_async(gui_function, window_title="", ..., with_implot=False, ...)

    For Jupyter notebook usage, see immapp.nb.start() for a more convenient API.
    """
    # Import here to avoid issues at module load time
    from imgui_bundle import _imgui_bundle
    from imgui_bundle import hello_imgui

    manual_render = _imgui_bundle.immapp_cpp.manual_render

    # Determine which setup method to use based on arguments
    if len(args) >= 1:
        first_arg = args[0]

        # Case 1: RunnerParams
        if isinstance(first_arg, RunnerParams):
            runner_params = first_arg
            addons_params = args[1] if len(args) > 1 else kwargs.get("addons_params", None)
            if addons_params is None:
                addons_params = AddOnsParams()
            manual_render.setup_from_runner_params(runner_params, addons_params)

        # Case 2: SimpleRunnerParams
        elif isinstance(first_arg, SimpleRunnerParams):
            simple_params = first_arg
            addons_params = args[1] if len(args) > 1 else kwargs.get("addons_params", None)
            if addons_params is None:
                addons_params = AddOnsParams()
            manual_render.setup_from_simple_runner_params(simple_params, addons_params)

        # Case 3: GUI function with keyword arguments
        elif callable(first_arg):
            gui_function = first_arg
            # Extract parameters, using defaults from immapp.run signature
            window_title = kwargs.get("window_title", "")
            window_size_auto = kwargs.get("window_size_auto", False)
            window_restore_previous_geometry = kwargs.get("window_restore_previous_geometry", False)
            window_size = kwargs.get("window_size", None)
            fps_idle = kwargs.get("fps_idle", 10.0)
            top_most = kwargs.get("top_most", False)
            with_implot = kwargs.get("with_implot", False)
            with_implot3d = kwargs.get("with_implot3d", False)
            with_markdown = kwargs.get("with_markdown", False)
            with_node_editor = kwargs.get("with_node_editor", False)
            with_tex_inspect = kwargs.get("with_tex_inspect", False)

            manual_render.setup_from_gui_function(
                gui_function,
                window_title=window_title,
                window_size_auto=window_size_auto,
                window_restore_previous_geometry=window_restore_previous_geometry,
                window_size=window_size,
                fps_idle=fps_idle,
                top_most=top_most,
                with_implot=with_implot,
                with_implot3d=with_implot3d,
                with_markdown=with_markdown,
                with_node_editor=with_node_editor,
                with_tex_inspect=with_tex_inspect,
            )
        else:
            raise TypeError(f"First argument must be RunnerParams, SimpleRunnerParams, or a callable GUI function, got {type(first_arg)}")
    else:
        raise TypeError("run_async() requires at least one argument")

    # Configure FPS settings for optimal async performance
    # This ensures C++ code returns early to Python instead of sleeping,
    # allowing maximum parallelism between GUI rendering and Python code execution
    params = hello_imgui.get_runner_params()
    params.fps_idling.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return  # Use early return mode
    params.fps_idling.vsync_to_monitor = False  # Disable vsync which is implemented via sleep
    params.fps_idling.fps_max = 60.0  # Limit to 60 FPS (otherwise we may run at 500+ FPS on fast machines)

    # Async render loop
    try:
        while not hello_imgui.get_runner_params().app_shall_exit:
            manual_render.render()
            await asyncio.sleep(0)  # Yield control to the event loop
    finally:
        # Ensure cleanup happens even if an exception occurs
        manual_render.tear_down()
