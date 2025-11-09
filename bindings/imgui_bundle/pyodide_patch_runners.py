"""This module provides a way to render hello imgui and immapp applications in the browser using pyodide.
It works by monkey patching the `hello_imgui.run` and `immapp.run` functions to use a custom implementation
that integrates with the browser's requestAnimationFrame API.
"""
from dataclasses import dataclass
from typing import Callable
from imgui_bundle import hello_imgui, immapp
from enum import Enum
from pyodide.ffi import create_proxy  # type: ignore
import js  # type: ignore
import gc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pyodide_imgui_render")
logger.setLevel(logging.INFO)

def _log(msg: str):
    # logger.info(msg)
    # js.console.log("pyodide_imgui_render: " + msg)
    pass


class _JsAnimationRenderer:
    """Make it possible to call a python function to do rendering at each javascript frame."""
    render_fn: Callable[[], None]  # A python function that performs rendering
    stop_requested: bool  # A flag to request the animation loop to stop
    main_loop_proxy: js.Proxy  # A javascript proxy to the main_loop method that is called at each frame

    def __init__(self, render_fn: Callable[[], None]):
        self.render_fn = render_fn
        self.stop_requested = False
        self.main_loop_proxy = create_proxy(self.main_loop)

    def main_loop(self, _timestamp):
        if self.stop_requested:
            if self.main_loop_proxy:
                _log("_JsAnimationRenderer: received stop_requested => destroying main_loop_proxy")
                self.main_loop_proxy.destroy()
                self.main_loop_proxy = None
            return
        try:
            self.render_fn()
        except Exception as e:
            self.request_stop()
            raise e

        # Schedule the next frame
        js.requestAnimationFrame(self.main_loop_proxy)

    def start(self):
        _log("_JsAnimationRenderer.start()")
        self.stop_requested = False
        js.requestAnimationFrame(self.main_loop_proxy)

    def request_stop(self):
        _log("_JsAnimationRenderer:stop() => set stop_requested=True")
        self.stop_requested = True


@dataclass
class _RenderLifeCycleFunctions:
    setup: Callable[[], None]
    render: Callable[[], None]
    tear_down: Callable[[], None]


class _HelloImGuiOrImmApp(Enum):
    HELLO_IMGUI = 1
    IMMAPP = 2


def _arg_to_render_lifecycle_functions(himgui_or_immapp: _HelloImGuiOrImmApp, *args, **kwargs) -> _RenderLifeCycleFunctions:
    """Converts the arguments to the correct render lifecycle functions,
    depending on the type of arguments passed and whether it is a hello_imgui or immapp application."""
    if himgui_or_immapp == _HelloImGuiOrImmApp.HELLO_IMGUI:
        render_module = hello_imgui.manual_render
    elif himgui_or_immapp == _HelloImGuiOrImmApp.IMMAPP:
        render_module = immapp.manual_render  # type: ignore
    else:
        raise ValueError("Invalid value for himgui_or_immapp")

    _log(f"{len(args)=}  args: {args} kwargs: {kwargs}")
    use_runner_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.RunnerParams)) or "runner_params" in kwargs
    use_simple_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.SimpleRunnerParams)) or "simple_params" in kwargs
    use_gui_function = (len(args) >= 1 and callable(args[0])) or "gui_function" in kwargs

    if use_runner_params:
        _log("overload with RunnerParams")
        fn_setup = lambda: render_module.setup_from_runner_params(*args, **kwargs)   # noqa: E731
    elif use_simple_params:
        _log("overload with SimpleRunnerParams")
        fn_setup = lambda: render_module.setup_from_simple_runner_params(*args, **kwargs)   # noqa: E731
    elif use_gui_function:
        _log("overload with callable")
        fn_setup = lambda:render_module.setup_from_gui_function(*args, **kwargs)   # noqa: E731
    else:
        raise ValueError("Invalid arguments")

    fn_render = render_module.render
    fn_tear_down = render_module.tear_down

    functions = _RenderLifeCycleFunctions(fn_setup, fn_render, fn_tear_down)
    return functions


class _ManualRenderJs:
    """Manages the ManualRender lifecycle (from HelloImGui or ImmApp) and integrates with _JsAnimationRenderer."""
    js_animation_renderer: _JsAnimationRenderer | None = None
    is_running: bool = False
    render_lifecycle_functions: _RenderLifeCycleFunctions | None = None

    def _stop(self):
        """Stops the current rendering loop and tears down the renderer."""
        if not  self.is_running:
            return
        if self.js_animation_renderer is not None:
            _log("_ManualRenderJs: Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            self.js_animation_renderer = None

        try:
            assert(self.js_animation_renderer is not None)
            self.render_lifecycle_functions.tear_down()
            self.render_lifecycle_functions = None
            _log("_ManualRenderJs: HelloImGuiRunnerJs: Renderer torn down successfully.")
        except Exception as e:
            import traceback
            js.console.error(f"_ManualRenderJs: Error during Renderer teardown: {e}\n{traceback.format_exc()}")
        finally:
            # Force garbage collection to free resources
            gc.collect()

    def _run(self, himgui_or_immapp: _HelloImGuiOrImmApp, *args, **kwargs):
        if self.is_running:
            self._stop()
        self.is_running = True

        self.render_lifecycle_functions = _arg_to_render_lifecycle_functions(himgui_or_immapp, *args, **kwargs)
        self.render_lifecycle_functions.setup()
        self.js_animation_renderer = _JsAnimationRenderer(self.render_lifecycle_functions.render)
        self.js_animation_renderer.start()

    def run_immapp(self, *args, **kwargs):
        self._run(_HelloImGuiOrImmApp.IMMAPP, *args, **kwargs)

    def run_hello_imgui(self, *args, **kwargs):
        self._run(_HelloImGuiOrImmApp.HELLO_IMGUI, *args, **kwargs)


_MANUAL_RENDER_JS: _ManualRenderJs | None = None


def pyodide_do_patch_runners():
    # Instantiate global runners
    global _MANUAL_RENDER_JS
    print("pyodide_do_patch_runners()")
    _log("_MANUAL_RENDER_JS: Version 1")
    _MANUAL_RENDER_JS = _ManualRenderJs()
    # Monkey patch the hello_imgui.run and immapp.run function to use the js version
    hello_imgui.run = _MANUAL_RENDER_JS.run_hello_imgui
    immapp.run = _MANUAL_RENDER_JS.run_immapp
