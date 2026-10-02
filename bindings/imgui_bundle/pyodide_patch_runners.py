"""This module provides a way to render hello imgui and immapp applications in the browser using pyodide.
It works by monkey patching the `hello_imgui.run` and `immapp.run` functions to use a custom implementation
that integrates with the browser's requestAnimationFrame API.
"""
from dataclasses import dataclass
from typing import Any, Callable
from imgui_bundle import hello_imgui, immapp
from enum import Enum
from pyodide.code import run_js  # type: ignore
import asyncio
import js  # type: ignore
import gc
import logging
import traceback

logger = logging.getLogger("pyodide_imgui_render")
logger.setLevel(logging.WARNING)  # Avoid noise in Fiatlight's log window

def _log(msg: str) -> None:
    logger.info(msg)


# Returns a JS promise, resolved at the next animation frame
_next_animation_frame = run_js("() => new Promise(resolve => requestAnimationFrame(resolve))")


class _JsAnimationRenderer:
    """Make it possible to call a python function to do rendering at each javascript frame.

    The frames are rendered from one asyncio task, which awaits each animation frame: inside a task,
    a frame can block with pyodide.ffi.run_sync (the test engine's coroutine does).
    """
    render_fn: Callable[[], None]  # A python function that performs rendering
    stop_requested: bool  # A flag to request the animation loop to stop
    stop_callback: Callable[[], None] | None  # Callback to call when stopping (to trigger teardown)
    frame_in_flight: Any  # A JS promise while a frame renders (a frame may be suspended in run_sync), else None

    def __init__(self, render_fn: Callable[[], None], stop_callback: Callable[[], None] | None = None):
        self.render_fn = render_fn
        self.stop_requested = False
        self.stop_callback = stop_callback
        self.frame_in_flight = None

    async def main_loop(self) -> None:
        while not self.stop_requested:
            await _next_animation_frame()
            if self.stop_requested:
                break
            self.frame_in_flight = js.Promise.withResolvers()
            try:
                self.render_fn()
            except Exception:
                self.request_stop()
                traceback.print_exc()
                return
            finally:
                self.frame_in_flight.resolve()
                self.frame_in_flight = None

            # Check if the application requested exit (like AbstractRunner::Run does)
            # This happens when user clicks close button or calls app_shall_exit = True
            if hello_imgui.get_runner_params().app_shall_exit:
                _log("_JsAnimationRenderer: app_shall_exit detected, calling stop_callback")
                self.request_stop()
                # Trigger teardown via callback
                if self.stop_callback:
                    self.stop_callback()
                return
        _log("_JsAnimationRenderer: received stop_requested => leaving main_loop")

    def start(self) -> None:
        _log("_JsAnimationRenderer.start()")
        self.stop_requested = False
        asyncio.ensure_future(self.main_loop())

    def request_stop(self) -> None:
        _log("_JsAnimationRenderer:stop() => set stop_requested=True")
        self.stop_requested = True


class _GcWithoutIncrements:
    """Disables Python's automatic GC, and collects at each frame with the kinds of collection that are safe.

    Pyodide 314.0.x crashes when an increment of Python's GC walks the frames of a suspended task (pyodide#6464,
    fixed by pyodide#6466, not in a release yet), and the test engine's coroutine is such a task. Automatic
    collections are increments: while the engine runs, the frame loop runs instead the two kinds that do not walk
    the frames: a young collection at each frame, and a full one from time to time.
    """
    FULL_COLLECTION_EVERY_N_FRAMES = 600

    def __init__(self) -> None:
        self.was_enabled = gc.isenabled()
        self.nb_frames = 0
        gc.disable()

    def collect(self) -> None:
        self.nb_frames += 1
        if self.nb_frames % self.FULL_COLLECTION_EVERY_N_FRAMES == 0:
            gc.collect()
        else:
            gc.collect(0)

    def restore(self) -> None:
        if self.was_enabled:
            gc.enable()


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


def _runner_params_in_args(args: Any, kwargs: Any) -> hello_imgui.RunnerParams | None:
    """The RunnerParams of a run() call, if it has one (the only form that can turn the test engine on)."""
    if len(args) >= 1 and isinstance(args[0], hello_imgui.RunnerParams):
        return args[0]
    runner_params = kwargs.get("runner_params")
    return runner_params if isinstance(runner_params, hello_imgui.RunnerParams) else None


def _disable_test_engine_without_jspi(runner_params: hello_imgui.RunnerParams | None) -> None:
    """In Pyodide, the test engine's coroutine needs JSPI stack switching. Without it (Pyodide's own test:
    WebAssembly.Suspending), the app runs without the engine, and says so in the console."""
    if runner_params is None or not runner_params.use_imgui_test_engine:
        return
    if hasattr(js.WebAssembly, "Suspending"):
        return
    js.console.warn(
        "imgui_bundle: this browser has no JSPI (WebAssembly.Suspending), which the test engine needs in Pyodide. "
        "The app runs without the engine: get_runner_params().use_imgui_test_engine is False, "
        "get_imgui_test_engine() is None.")
    runner_params.use_imgui_test_engine = False


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
    gc_without_increments: _GcWithoutIncrements | None = None  # while the test engine runs

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
            if self.gc_without_increments is not None:
                self.gc_without_increments.restore()
                self.gc_without_increments = None
            # Force garbage collection to free resources
            gc.collect()

    def _run(self, himgui_or_immapp: _HelloImGuiOrImmApp, *args: Any, **kwargs: Any) -> None:
        _log(f"_ManualRenderJs._run() called with {himgui_or_immapp}, args: {args}, kwargs: {kwargs}")
        if self.is_running:
            _log("_ManualRenderJs._run() -> Stopping existing renderer before starting a new one.")
            self._stop()
        self.is_running = True

        _disable_test_engine_without_jspi(_runner_params_in_args(args, kwargs))
        self.render_lifecycle_functions = _arg_to_render_lifecycle_functions(himgui_or_immapp, *args, **kwargs)
        try:
            self.render_lifecycle_functions.setup()
        except Exception:
            # A failed setup tears itself down (AbstractRunner::Setup): there is nothing left to stop
            self.is_running = False
            self.render_lifecycle_functions = None
            raise
        render_frame = self.render_lifecycle_functions.render
        render = render_frame
        if hello_imgui.get_runner_params().use_imgui_test_engine:
            gc_without_increments = self.gc_without_increments = _GcWithoutIncrements()

            def render_and_collect() -> None:
                render_frame()
                gc_without_increments.collect()
            render = render_and_collect
        # Pass _stop as callback so animation renderer can trigger teardown when app_shall_exit
        self.js_animation_renderer = _JsAnimationRenderer(render, stop_callback=self._stop)
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

            # Tear down any previous renderer synchronously, so its animation
            # frames stop firing while we await the LaTeX font download.
            # Otherwise the old lambda keeps ticking against freshly-rebound
            # globals from the new exec (playground reuses one namespace),
            # producing spurious AttributeErrors.
            # Note: when not using latex, self._run() will also call self._stop() if needed
            if self.is_running:
                self._stop()

            async def _delayed_start() -> None:
                try:
                    from imgui_bundle._pyodide_latex_fonts import ensure_fonts_async
                    await ensure_fonts_async()
                except Exception as e:  # noqa: BLE001
                    # Log here for visibility; the C++ wrapper has its own
                    # missing-fonts safety net (rich_md.cpp:
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
            # Stop the previous renderer up front (see run_immapp).
            if self.is_running:
                self._stop()
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


def stop_active_renderer() -> None:
    """Stop the currently running renderer, if any. No-op if nothing is running.

    Intended for the playground's demo-switching JS to call *before* exec'ing
    a new demo's code. Without this call, the old animation lambda keeps
    ticking against module globals (e.g. `gui`, `AppState`) that the new
    exec freshly rebinds — producing surprising AttributeErrors and a
    cascading teardown failure (see the inline comment around `_run_async`'s
    latex path for the same race in another shape).

    Safe to call repeatedly: subsequent calls when nothing is running do
    nothing. Safe to call before this module's runner has ever started.
    """
    global _MANUAL_RENDER_JS
    if _MANUAL_RENDER_JS is None:
        return
    if not _MANUAL_RENDER_JS.is_running:
        return
    renderer = _MANUAL_RENDER_JS.js_animation_renderer
    if renderer is not None and renderer.frame_in_flight is not None:
        # A frame is suspended (the test engine's coroutine, or a test function that blocks in run_sync): tear down
        # after it, not in the middle of it. The stop is requested first: a run_sync resumes through the event loop,
        # and the loop would otherwise start another frame before we wake up. Needs a promising call stack, as the
        # teardown does anyway (the playground calls through runPythonAsync).
        from pyodide.ffi import run_sync  # type: ignore
        renderer.request_stop()
        run_sync(renderer.frame_in_flight.promise)
    _MANUAL_RENDER_JS._stop()


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
