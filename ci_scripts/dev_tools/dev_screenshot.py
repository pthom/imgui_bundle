"""Take a screenshot of an ImGui Bundle GUI programmatically.

Used for visual validation of UI changes without launching a window
manually. The function wraps the user's gui callback in a frame counter
that flips ``app_shall_exit`` after N frames, runs ``immapp.run``, then
fetches the captured final framebuffer and saves it as PNG.

See ``ci_scripts/dev_tools/README.md`` for the full story and the C++
equivalent.

Example:

    from dev_screenshot import take_screenshot

    def my_gui():
        imgui.text("Hello")

    png = take_screenshot(my_gui, "/tmp/out.png", with_latex=True)
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Tuple, Union

PathLike = Union[str, Path]
GuiFn = Callable[[], None]


def take_screenshot(
    gui_fn: GuiFn,
    output_path: PathLike,
    *,
    exit_after_frames: int = 8,
    window_size: Tuple[int, int] = (900, 950),
    window_title: str = "DevScreenshot probe",
    ini_disable: bool = True,
    with_markdown: bool = False,
    with_latex: bool = False,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_node_editor: bool = False,
    fps_idle: float = 0.0,
) -> Path:
    """Run ``gui_fn`` for ``exit_after_frames`` frames, exit, save the
    final framebuffer to ``output_path`` as PNG. Returns the resolved
    output path so the caller can immediately read the file.

    Parameters
    ----------
    gui_fn : Callable[[], None]
        The user's per-frame draw callback. Will be invoked from inside
        a frame counter wrapper that exits the app after N frames.
    output_path : str | Path
        Where to write the PNG. Parent directories must already exist.
    exit_after_frames : int
        Number of frames to render before exiting (default 8). Increase
        if your layout takes longer to settle (e.g. async asset loads).
    window_size : (int, int)
        Logical pixel size of the app window (default 900x950). On HiDPI
        displays the captured framebuffer is larger by the framebuffer
        scale factor.
    window_title : str
        Window title (mostly cosmetic for the brief moment the window
        is visible during capture).
    ini_disable : bool
        Disables the auto-saved imgui .ini file (default True). This
        avoids leaving artifacts on disk and prevents window-state
        drift across repeated screenshot runs of the same demo.
    with_markdown, with_latex, with_implot, with_implot3d, with_node_editor : bool
        Standard ``immapp.run`` addons. Enable as needed by the demo
        being captured. ``with_latex`` implies ``with_markdown``.
    fps_idle : float
        FPS when the app is idle. Default 0 (no throttling) since we
        want the few frames to render as fast as possible.

    Returns
    -------
    Path
        Resolved absolute path to the saved PNG.
    """
    output_path = Path(output_path).expanduser().resolve()

    # Lazy imports so the module can be inspected without an imgui_bundle build
    from imgui_bundle import hello_imgui, immapp

    state = {"frames": 0}

    def _wrapped_gui() -> None:
        gui_fn()
        state["frames"] += 1
        if state["frames"] >= exit_after_frames:
            hello_imgui.get_runner_params().app_shall_exit = True

    immapp.run(
        gui_function=_wrapped_gui,
        window_title=window_title,
        window_size=window_size,
        ini_disable=ini_disable,
        with_markdown=with_markdown,
        with_latex=with_latex,
        with_implot=with_implot,
        with_implot3d=with_implot3d,
        with_node_editor=with_node_editor,
        fps_idle=fps_idle,
    )

    img = hello_imgui.final_app_window_screenshot()
    if img is None or img.size == 0:
        raise RuntimeError(
            f"final_app_window_screenshot() returned an empty buffer. "
            f"Did the app exit before any frame was rendered? "
            f"(exit_after_frames={exit_after_frames})"
        )

    # PIL is the most universally available image lib in Python envs.
    from PIL import Image
    Image.fromarray(img).save(output_path)

    return output_path
