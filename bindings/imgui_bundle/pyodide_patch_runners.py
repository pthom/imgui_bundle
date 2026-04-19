"""This module provides a way to render hello imgui and immapp applications in the browser using pyodide.
It works by monkey patching the `hello_imgui.run` and `immapp.run` functions to use a custom implementation
that integrates with the browser's requestAnimationFrame API.
"""
from dataclasses import dataclass
from typing import Any, Callable
from imgui_bundle import hello_imgui, immapp
from enum import Enum
from pyodide.ffi import create_proxy  # type: ignore
import js  # type: ignore
import gc
import logging

logger = logging.getLogger("pyodide_imgui_render")
logger.setLevel(logging.WARNING)  # Avoid noise in Fiatlight's log window

def _log(msg: str) -> None:
    logger.info(msg)


class _JsAnimationRenderer:
    """Make it possible to call a python function to do rendering at each javascript frame."""
    render_fn: Callable[[], None]  # A python function that performs rendering
    stop_requested: bool  # A flag to request the animation loop to stop
    main_loop_proxy: js.Proxy  # A JavaScript proxy to the main_loop method that is called at each frame
    stop_callback: Callable[[], None] | None  # Callback to call when stopping (to trigger teardown)

    def __init__(self, render_fn: Callable[[], None], stop_callback: Callable[[], None] | None = None):
        self.render_fn = render_fn
        self.stop_requested = False
        self.stop_callback = stop_callback
        self.main_loop_proxy = create_proxy(self.main_loop)

    def main_loop(self, _timestamp: Any) -> None:
        if self.stop_requested:
            if self.main_loop_proxy:
                _log("_JsAnimationRenderer: received stop_requested => destroying main_loop_proxy")
                self.main_loop_proxy.destroy()
                self.main_loop_proxy = None
            return

        try:
            if not self.stop_requested:
                self.render_fn()

                # Check if the application requested exit (like AbstractRunner::Run does)
                # This happens when user clicks close button or calls app_shall_exit = True
                if hello_imgui.get_runner_params().app_shall_exit:
                    _log("_JsAnimationRenderer: app_shall_exit detected, calling stop_callback")
                    self.request_stop()
                    # Trigger teardown via callback
                    if self.stop_callback:
                        self.stop_callback()
                    return
        except Exception as e:
            self.request_stop()
            raise e

        # Only schedule the next frame if not stopping/tearing down
        if not self.stop_requested:
            js.requestAnimationFrame(self.main_loop_proxy)

    def start(self) -> None:
        _log("_JsAnimationRenderer.start()")
        self.stop_requested = False
        js.requestAnimationFrame(self.main_loop_proxy)

    def request_stop(self) -> None:
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


def _wants_latex(args: Any, kwargs: Any) -> bool:
    """Detect whether the caller asked for LaTeX rendering across the
    three immapp.run() calling conventions.

    - gui-function form: kwargs["with_latex"]
    - RunnerParams / SimpleRunnerParams form: addons_params.with_latex,
      passed as args[1] or kwargs["addons_params"]
    """
    if kwargs.get("with_latex"):
        return True
    addons = None
    if len(args) >= 2:
        addons = args[1]
    elif "addons_params" in kwargs:
        addons = kwargs["addons_params"]
    if addons is not None and getattr(addons, "with_latex", False):
        return True
    return False


def _arg_to_render_lifecycle_functions(himgui_or_immapp: _HelloImGuiOrImmApp, *args: Any, **kwargs: Any) -> _RenderLifeCycleFunctions:
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

    def _stop(self) -> None:
        """Stops the current rendering loop and tears down the renderer."""
        _log("_ManualRenderJs._stop() called")
        if not self.is_running:
            _log("_ManualRenderJs.stop -> Not running, nothing to stop.")
            return
        if self.js_animation_renderer is not None:
            _log("_ManualRenderJs.stop -> Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            self.js_animation_renderer = None

        try:
            assert(self.render_lifecycle_functions is not None)
            self.render_lifecycle_functions.tear_down()
            self.render_lifecycle_functions = None
            _log("_ManualRenderJs._stop() -> HelloImGuiRunnerJs: Renderer torn down successfully.")
        except Exception as e:
            import traceback
            js.console.error(f"_ManualRenderJs._stop() -> _ManualRenderJs: Error during Renderer teardown: {e}\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            # Force garbage collection to free resources
            gc.collect()

    def _run(self, himgui_or_immapp: _HelloImGuiOrImmApp, *args: Any, **kwargs: Any) -> None:
        _log(f"_ManualRenderJs._run() called with {himgui_or_immapp}, args: {args}, kwargs: {kwargs}")
        if self.is_running:
            _log("_ManualRenderJs._run() -> Stopping existing renderer before starting a new one.")
            self._stop()
        self.is_running = True

        self.render_lifecycle_functions = _arg_to_render_lifecycle_functions(himgui_or_immapp, *args, **kwargs)
        self.render_lifecycle_functions.setup()
        # Pass _stop as callback so animation renderer can trigger teardown when app_shall_exit
        self.js_animation_renderer = _JsAnimationRenderer(
            self.render_lifecycle_functions.render,
            stop_callback=self._stop
        )
        self.js_animation_renderer.start()
        _log("_ManualRenderJs._run() -> Animation started (non-blocking)")

    async def _run_async(self, himgui_or_immapp: _HelloImGuiOrImmApp, *args: Any, **kwargs: Any) -> None:
        """Async version that can be awaited to wait until GUI exits."""
        import asyncio

        _log(f"_ManualRenderJs._run_async() called with {himgui_or_immapp}, args: {args}, kwargs: {kwargs}")

        # Start the GUI (non-blocking)
        self._run(himgui_or_immapp, *args, **kwargs)

        # Wait until stopped (either by stop_requested or app_shall_exit)
        # Teardown is automatic via stop_callback
        _log("_ManualRenderJs._run_async() -> Waiting for GUI to exit")
        while self.is_running:
            await asyncio.sleep(0.016)  # ~60 FPS check rate

        _log("_ManualRenderJs._run_async() -> GUI exited (teardown already done via callback)")

    def run_immapp(self, *args: Any, **kwargs: Any) -> None:
        """Run an immapp GUI in Pyodide (fire-and-forget).

        In Pyodide, run() starts the GUI and returns immediately since browsers
        cannot block. The GUI runs until the user closes it or sets app_shall_exit = True.

        For async control (waiting for GUI to exit), use run_async() instead.

        If ``with_latex=True`` is requested, the LaTeX math fonts are
        downloaded from a CDN before the renderer starts (one-time per
        session, ~876 KB). Desktop builds bundle the fonts in the wheel
        and never enter this path; Pyodide builds exclude the fonts to
        keep the wheel small (see ``IMGUI_BUNDLE_SLIM_PYODIDE_WHEEL=1``
        in the Pyodide build script + ``pyproject.toml`` override).
        """
        if _wants_latex(args, kwargs):
            import asyncio

            async def _delayed_start() -> None:
                try:
                    from imgui_bundle._pyodide_latex_fonts import ensure_fonts_async
                    await ensure_fonts_async()
                except Exception as e:  # noqa: BLE001
                    # Log here for visibility; the C++ wrapper has its own
                    # missing-fonts safety net (imgui_md_wrapper.cpp:
                    # EnsureMicroTeXInitialized) that falls back to rendering
                    # the LaTeX source as plain text.
                    js.console.error(
                        f"imgui_bundle: failed to fetch LaTeX fonts ({e}). "
                        f"Formulas will be shown as plain text."
                    )
                self._run(_HelloImGuiOrImmApp.IMMAPP, *args, **kwargs)

            asyncio.ensure_future(_delayed_start())
        else:
            self._run(_HelloImGuiOrImmApp.IMMAPP, *args, **kwargs)

    def run_hello_imgui(self, *args: Any, **kwargs: Any) -> None:
        """Run a hello_imgui GUI in Pyodide (fire-and-forget).

        In Pyodide, run() starts the GUI and returns immediately since browsers
        cannot block. The GUI runs until the user closes it or sets app_shall_exit = True.

        For async control (waiting for GUI to exit), use run_async() instead.
        """
        self._run(_HelloImGuiOrImmApp.HELLO_IMGUI, *args, **kwargs)

    async def run_immapp_async(self, *args: Any, **kwargs: Any) -> None:
        """Async version of run_immapp that waits until GUI exits.

        If ``with_latex=True``, awaits the LaTeX font download (one-time
        per session) before starting the renderer.
        """
        if _wants_latex(args, kwargs):
            try:
                from imgui_bundle._pyodide_latex_fonts import ensure_fonts_async
                await ensure_fonts_async()
            except Exception as e:  # noqa: BLE001
                # See run_immapp() above for the rationale: log + fall through.
                # The C++ wrapper handles missing fonts via its own fallback.
                js.console.error(
                    f"imgui_bundle: failed to fetch LaTeX fonts ({e}). "
                    f"Formulas will be shown as plain text."
                )
        await self._run_async(_HelloImGuiOrImmApp.IMMAPP, *args, **kwargs)

    async def run_hello_imgui_async(self, *args: Any, **kwargs: Any) -> None:
        """Async version of run_hello_imgui that waits until GUI exits."""
        await self._run_async(_HelloImGuiOrImmApp.HELLO_IMGUI, *args, **kwargs)


_MANUAL_RENDER_JS: _ManualRenderJs | None = None


def pyodide_do_patch_runners() -> None:
    # Instantiate global runners
    global _MANUAL_RENDER_JS
    # print("pyodide_do_patch_runners()")
    _log("pyodide_do_patch_runners: Version 12")
    _MANUAL_RENDER_JS = _ManualRenderJs()

    # Monkey patch the hello_imgui.run and immapp.run functions
    # In Pyodide, run() is fire-and-forget (returns immediately) since browsers cannot block
    hello_imgui.run = _MANUAL_RENDER_JS.run_hello_imgui
    immapp.run = _MANUAL_RENDER_JS.run_immapp

    # run_with_markdown is just run() with with_markdown=True baked in.
    # It must also be patched, otherwise it calls the blocking C++ Run() which crashes Pyodide.
    def _run_with_markdown_pyodide(gui_function: Any, *, with_markdown_options: Any = None, **kwargs: Any) -> None:
        kwargs["with_markdown"] = True
        if with_markdown_options is not None:
            kwargs["with_markdown_options"] = with_markdown_options
        _MANUAL_RENDER_JS.run_immapp(gui_function, **kwargs)
    immapp.run_with_markdown = _run_with_markdown_pyodide  # type: ignore[assignment]

    # Add async versions for waiting until GUI exits
    immapp.run_async = _MANUAL_RENDER_JS.run_immapp_async
    hello_imgui.run_async = _MANUAL_RENDER_JS.run_hello_imgui_async
