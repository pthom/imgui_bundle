# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""immapp.testing — drive an imgui_bundle GUI via ImGui Test Engine.

Run a GUI together with a single test function; the test can click, type,
capture screenshots, etc. The window exits automatically once the test
finishes (unless exit_after_test=False).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Tuple, Union

from imgui_bundle import imgui, hello_imgui, immapp

PathLike = Union[str, Path]


TestFunction = Callable[["imgui.test_engine.TestContext"], None]
TestRunSpeed = imgui.test_engine.TestRunSpeed


def capture(
    ctx: "imgui.test_engine.TestContext",
    path: str,
    *,
    window: Optional[str] = None,
    flags: int = 0,
) -> None:
    """Write a PNG screenshot from inside a test function.

    Yields one frame first so pending animation/layout state has a chance to
    settle before the capture.

    Args:
        ctx: the TestContext passed to your test function.
        path: absolute output path. The file extension (usually `.png`) is
            honored by the test engine.
        window: if set, capture only that window. A bare label (e.g.
            "Dear ImGui Demo") is interpreted as an absolute root reference
            (prefixed with "//" automatically). Pass None to capture the
            full application framebuffer.
        flags: imgui.test_engine.CaptureFlags_ bitfield.
    """
    ctx.yield_()
    ctx.capture_reset()
    if window is not None:
        ref = window if window.startswith("//") else "//" + window
        ctx.capture_add_window(ref)
    ctx.capture_set_filename(path)
    ctx.capture_screenshot(flags)


def run(
    gui_function: Callable[[], None],
    test_function: TestFunction,
    *,
    exit_after_test: bool = True,
    run_speed: TestRunSpeed = TestRunSpeed.fast,
    # Common RunnerParams / AddOns shortcuts (ignored if runner_params is provided)
    window_title: str = "",
    window_size: Optional[Tuple[int, int]] = None,
    window_size_auto: bool = False,
    fps_idle: float = 10.0,
    ini_disable: bool = True,
    with_markdown: bool = False,
    with_latex: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
    # Escape hatch: pass a fully configured RunnerParams instead of the shortcuts above.
    runner_params: Optional[hello_imgui.RunnerParams] = None,
    add_ons_params: Optional[immapp.AddOnsParams] = None,
) -> None:
    """Run `gui_function` and automatically drive it with `test_function`.

    `test_function(ctx)` receives an imgui.test_engine.TestContext and can use
    the full test engine API (item_click, item_open, key_chars,
    capture_screenshot_window, ...). It also works with `immapp.testing.capture`
    to grab screenshots at chosen moments.

    Args:
        gui_function: the GUI to drive (called each frame).
        test_function: the test body, called once by the engine. When it
            returns, the app exits (unless exit_after_test=False).
        exit_after_test: if True (default), set app_shall_exit once the test
            finishes. Set to False to keep the window open for inspection.
        run_speed: fast / normal / cinematic. Defaults to fast.
        runner_params: if given, the shortcut kwargs above are ignored and
            this RunnerParams is used as-is (we only wire the test engine
            on top of it).
        add_ons_params: immapp addons. If None, built from the with_* flags.
    """
    if runner_params is None:
        simple = hello_imgui.SimpleRunnerParams()
        simple.gui_function = gui_function
        simple.window_title = window_title
        simple.window_size_auto = window_size_auto
        if window_size is not None:
            simple.window_size = window_size
        simple.fps_idle = fps_idle
        runner_params = simple.to_runner_params()
        runner_params.ini_disable = ini_disable

    runner_params.use_imgui_test_engine = True

    if add_ons_params is None:
        add_ons_params = immapp.AddOnsParams(
            with_implot=with_implot,
            with_implot3d=with_implot3d,
            with_markdown=with_markdown or with_latex,
            with_latex=with_latex,
            with_node_editor=with_node_editor,
            with_tex_inspect=with_tex_inspect,
        )

    test_done = False
    test_error: Optional[BaseException] = None

    def _wrapped_test(ctx: "imgui.test_engine.TestContext") -> None:
        nonlocal test_done, test_error
        try:
            test_function(ctx)
        except BaseException as e:
            test_error = e
        finally:
            test_done = True

    prior_register_tests = runner_params.callbacks.register_tests

    def _register_tests() -> None:
        if callable(prior_register_tests):
            prior_register_tests()
        engine = hello_imgui.get_imgui_test_engine()
        io = imgui.test_engine.get_io(engine)
        io.config_run_speed = run_speed
        test = imgui.test_engine.register_test(engine, "immapp.testing", "auto")
        test.test_func = _wrapped_test
        imgui.test_engine.queue_test(engine, test)

    runner_params.callbacks.register_tests = _register_tests

    if exit_after_test:
        prior_before_render = runner_params.callbacks.before_imgui_render

        def _exit_when_done() -> None:
            if callable(prior_before_render):
                prior_before_render()
            if test_done:
                engine = hello_imgui.get_imgui_test_engine()
                if imgui.test_engine.is_test_queue_empty(engine):
                    runner_params.app_shall_exit = True

        runner_params.callbacks.before_imgui_render = _exit_when_done

    immapp.run(runner_params, add_ons_params)

    if test_error is not None:
        raise test_error


def capture_final_frame(
    gui_function: Callable[[], None],
    output_path: PathLike,
    *,
    exit_after_frames: int = 8,
    window_size: Tuple[int, int] = (900, 950),
    window_title: str = "capture_final_frame",
    ini_disable: bool = True,
    fps_idle: float = 0.0,
    with_markdown: bool = False,
    with_latex: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_node_editor: bool = False,
) -> Path:
    """One-shot: run `gui_function` for a few frames, save the last
    framebuffer as PNG, return the absolute output path.

    Simple alternative to `run`/`capture` for the common case where you
    just want a snapshot of a GUI (no interaction, no test engine). Kept
    as the workhorse of the `screenshot-imgui-bundle` skill.

    Args:
        gui_function: per-frame draw callback.
        output_path: where to write the PNG (parent dir must exist).
        exit_after_frames: render N frames before exit (default 8). Bump
            higher (15-30) if the layout takes longer to settle.
        window_size: logical pixels. On HiDPI displays the PNG is scaled.
        window_title: cosmetic — window is only briefly visible.
        ini_disable: disable imgui .ini to avoid side effects.
        fps_idle: 0 (no throttle) — we want the few frames to render fast.
        with_*: standard immapp.run addons.
    """
    output_path = Path(output_path).expanduser().resolve()

    state = {"frames": 0}

    def _wrapped() -> None:
        gui_function()
        state["frames"] += 1
        if state["frames"] >= exit_after_frames:
            hello_imgui.get_runner_params().app_shall_exit = True

    immapp.run(
        gui_function=_wrapped,
        window_title=window_title,
        window_size=window_size,
        ini_disable=ini_disable,
        fps_idle=fps_idle,
        with_markdown=with_markdown,
        with_latex=with_latex,
        with_implot=with_implot,
        with_implot3d=with_implot3d,
        with_node_editor=with_node_editor,
    )

    img = hello_imgui.final_app_window_screenshot()
    if img is None or img.size == 0:
        raise RuntimeError(
            "final_app_window_screenshot() returned an empty buffer. "
            f"Did the app exit before any frame was rendered? "
            f"(exit_after_frames={exit_after_frames})"
        )

    from PIL import Image
    Image.fromarray(img).save(output_path)
    return output_path
