"""Screenshots of the playground examples, for the playground's examples menu.

Each example runs on the desktop, in its own process, for a few frames (with an optional action, e.g. "fly to the
Douady rabbit"), then the part of its window given by SHOTS is saved as a WebP picture, 640 pixels wide, in the
website resources: docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground/<file name>.webp
(served at https://imgui-bundle.pages.dev/resources/playground/).

Usage:
    python ci_scripts/playground_screenshots.py                 # all the examples of SHOTS
    python ci_scripts/playground_screenshots.py julia_map boids  # some of them
    python ci_scripts/playground_screenshots.py --raw DIR        # full windows as PNG, in DIR (to choose the crops)
    python ci_scripts/playground_screenshots.py --browser DIR    # the examples of BROWSER_SHOTS, from Chrome pictures

The examples that run only in the browser (BROWSER_SHOTS) are pictured in Chrome, in the local playground, with the
screenshot-web-demos skill (it opens a visible Chrome window: ask first). For each of them:
    uv run --no-project --with playwright python .claude/skills/screenshot-web-demos/drive_page.py \
        "http://localhost:6456/playground/?demo=<file name>" --out DIR/web wait:45 shot:<file stem>
which writes DIR/web_<file stem>.png (1400 x 900), then `--browser DIR` crops them.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

REPO = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO / "bindings/imgui_bundle/demos_python/playground/examples"
OUTPUT_DIR = REPO / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground"
WIDTH = 640  # the width of the pictures, in pixels

Box = tuple[float, float, float, float]  # a crop: left, top, right, bottom, as fractions of the window


@dataclass
class Shot:
    frames: int = 60  # frames before the picture
    crop: Box = (0.0, 0.0, 1.0, 1.0)
    action: Optional[Callable[[dict[str, Any], int], None]] = None  # called each frame with the example's globals
    test: Optional[Callable[[Any], None]] = None  # a test engine script (e.g. open a section), then `frames` frames


def _julia_rabbit(g: dict[str, Any], frame: int) -> None:
    if frame == 2:
        name = "Douady rabbit"
        g["state"].go_to(g["FAMOUS_C"][name][0], g["ARRIVAL_WIDTH"][name])


def _train(g: dict[str, Any], frame: int) -> None:
    g["state"].training = True


def _open(window: str, *labels: str) -> Callable[[Any], None]:
    """A test engine script: opens these headers or tree nodes of a full demo's window (in its child windows too)"""
    def test(ctx: Any) -> None:
        ctx.set_ref(window)
        for label in labels:
            ctx.item_open("**/" + label)
    return test


SHOTS: dict[str, Shot] = {
    "landing_page.py": Shot(crop=(0.0, 0.02, 0.49, 0.57)),
    "welcome_imm_mode.py": Shot(crop=(0.0, 0.52, 0.66, 0.86)),
    "imgui_demo.py": Shot(test=_open("ImGui Demo##aaa", "Widgets", "Basic"), crop=(0.0, 0.08, 0.98, 0.7)),
    "implot_demo.py": Shot(test=_open("ImGui Demo##aaa", "Line Plots"), crop=(0.0, 0.12, 1.0, 0.54)),
    "implot3d_demo.py": Shot(test=_open("ImPlot3d Demo##aaa", "Mesh Plots"), crop=(0.15, 0.42, 0.85, 0.9)),
    "implot3d_butterfly.py": Shot(frames=600, crop=(0.28, 0.5, 0.72, 1.0)),
    "immvision.py": Shot(frames=120, crop=(0.0, 0.3, 0.75, 0.72)),
    "fiatlight_image.py": Shot(frames=120, crop=(0.0, 0.0, 0.7, 0.57)),
    "themes.py": Shot(crop=(0.0, 0.33, 1.0, 1.0)),
    "layout_child.py": Shot(crop=(0.0, 0.43, 1.0, 1.0)),
    "layout_docking.py": Shot(crop=(0.0, 0.0, 1.0, 0.75)),
    "explorables/julia_map.py": Shot(frames=240, action=_julia_rabbit, crop=(0.0, 0.12, 0.51, 0.47)),
    "explorables/neural_spiral/neural_spiral.py": Shot(frames=320, action=_train, crop=(0.0, 0.11, 0.77, 0.49)),
    "explorables/lesson_harmonic_motion.py": Shot(frames=360, crop=(0.0, 0.5, 0.98, 0.94)),
    "explorables/double_pendulum.py": Shot(frames=900, crop=(0.3, 0.0, 0.85, 0.7)),
    "explorables/fourier_epicycles.py": Shot(frames=240, crop=(0.38, 0.12, 0.9, 0.8)),
    "explorables/boids.py": Shot(frames=240, crop=(0.28, 0.0, 1.0, 0.82)),
    "explorables/logistic_map.py": Shot(frames=120, crop=(0.3, 0.0, 0.99, 0.62)),
    "minimal_example.py": Shot(crop=(0.0, 0.0, 1.0, 0.62)),
    "webgl_background_shader.py": Shot(frames=120),
}


# The examples that run only in the browser: the crop of their Chrome picture (the playground's canvas is on the right)
BROWSER_SHOTS: dict[str, Box] = {
    "webgl_minimal_mandelbrot.py": (0.254, 0.063, 1.0, 1.0),
    "webgl_texture_in_image.py": (0.254, 0.063, 0.714, 0.733),
    "webaudio_minimal_beep.py": (0.254, 0.063, 0.814, 0.206),
}


def _save(image: Any, crop: Box, output: Path) -> None:
    """Crops the picture, and saves it WIDTH pixels wide, as WebP"""
    from PIL import Image
    width, height = image.size
    left, top, right, bottom = crop
    image = image.crop((int(left * width), int(top * height), int(right * width), int(bottom * height)))
    image = image.resize((WIDTH, round(image.size[1] * WIDTH / image.size[0])), Image.Resampling.LANCZOS)
    image.convert("RGB").save(output, "WEBP", quality=80, method=6)


def _run_one(filename: str, output: str, raw: bool) -> None:
    """In a child process: runs the example, then saves its picture"""
    from PIL import Image
    from imgui_bundle import hello_imgui, immapp

    shot = SHOTS[filename]
    path = EXAMPLES_DIR / filename
    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": str(path)}
    frame = [0]

    def on_frame() -> None:
        frame[0] += 1
        if shot.action is not None:
            shot.action(namespace, frame[0])
        if frame[0] >= shot.frames:
            hello_imgui.get_runner_params().app_shall_exit = True

    def drive(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """The same arguments, with on_frame() called each frame"""
        if args and isinstance(args[0], hello_imgui.RunnerParams):
            params = args[0]
            previous = params.callbacks.after_swap

            def after_swap() -> None:
                if previous is not None:
                    previous()
                on_frame()
            params.callbacks.after_swap = after_swap
            return args, kwargs
        gui = args[0] if args else kwargs.pop("gui_function")

        def driven_gui() -> None:
            gui()
            on_frame()
        return (driven_gui, *args[1:]), kwargs

    run, run_async = immapp.run, immapp.run_async

    def run_driven(*args: Any, **kwargs: Any) -> None:
        if shot.test is not None:  # the test engine drives the app, then exits
            from imgui_bundle.immapp import testing
            gui = args[0] if args else kwargs.pop("gui_function")

            def test_fn(ctx: Any) -> None:
                shot.test(ctx)  # type: ignore[misc]
                ctx.yield_(shot.frames)
            immapp.run = run  # testing.run calls immapp.run itself
            testing.run(gui, test_fn, **kwargs)
            return
        args, kwargs = drive(args, kwargs)
        run(*args, **kwargs)

    async def run_async_driven(*args: Any, **kwargs: Any) -> None:
        args, kwargs = drive(args, kwargs)
        await run_async(*args, **kwargs)

    immapp.run, immapp.run_async = run_driven, run_async_driven  # type: ignore[assignment]
    sys.path.insert(0, str(path.parent))
    exec(compile(path.read_text(), str(path), "exec"), namespace)

    image = Image.fromarray(hello_imgui.final_app_window_screenshot())
    if raw:
        image.save(output)
    else:
        _save(image, shot.crop, Path(output))


def _bundle_folders() -> dict[str, list[str]]:
    examples = json.loads((EXAMPLES_DIR / "examples.json").read_text())["examples"]
    return {e["filename"]: e.get("bundle_folders", []) for e in examples}


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--one"]:
        _run_one(args[1], args[2], raw=args[3] == "raw")
        return
    if args[:1] == ["--browser"]:
        from PIL import Image
        for filename, crop in BROWSER_SHOTS.items():
            stem = Path(filename).stem
            output = OUTPUT_DIR / f"{stem}.webp"
            _save(Image.open(Path(args[1]) / f"web_{stem}.png"), crop, output)
            print(f"ok           {filename} -> {output}")
        return
    raw_dir = None
    if args[:1] == ["--raw"]:
        raw_dir, args = Path(args[1]), args[2:]
        raw_dir.mkdir(parents=True, exist_ok=True)
    names = [f for f in SHOTS if not args or Path(f).stem in args]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle_folders = _bundle_folders()
    for filename in names:
        stem = Path(filename).stem
        output = raw_dir / f"{stem}.png" if raw_dir else OUTPUT_DIR / f"{stem}.webp"
        # Run in a scratch folder, as the playground does (its home folder, with the example's bundle folders)
        with tempfile.TemporaryDirectory() as cwd:
            for folder in bundle_folders.get(filename, []):
                shutil.copytree(EXAMPLES_DIR / folder, Path(cwd) / folder)
            result = subprocess.run([sys.executable, __file__, "--one", filename, str(output),
                                     "raw" if raw_dir else "webp"], cwd=cwd, timeout=180,
                                    capture_output=True, text=True, env={**os.environ, "PYTHONUNBUFFERED": "1"})
        status = "ok" if result.returncode == 0 and output.exists() else f"FAILED ({result.returncode})"
        print(f"{status:12s} {filename} -> {output}")
        if status != "ok":
            print(result.stderr[-1500:])


if __name__ == "__main__":
    main()
