"""Screenshots of the playground examples, for the playground's examples menu.

Each example runs on the desktop, in its own process, for a few frames (with an optional action, e.g. "fly to the
Douady rabbit"), then the part of its window given by SHOTS is saved as a JPEG picture, 640 pixels wide, in the
website resources: docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground/<file stem>.jpg
(served at https://imgui-bundle.pages.dev/resources/playground/). JPEG, not WebP: the launchers decode the pictures with
stb_image, which has no WebP. An example's file is in the folder of its "source" (see examples.json).

Usage:
    python ci_scripts/playground_screenshots.py                 # all the examples of SHOTS
    python ci_scripts/playground_screenshots.py julia_map boids  # some of them
    python ci_scripts/playground_screenshots.py --raw DIR        # full windows as PNG, in DIR (to choose the crops)
    python ci_scripts/playground_screenshots.py --browser DIR    # the examples of BROWSER_SHOTS, from Chrome pictures
    python ci_scripts/playground_screenshots.py --stale          # the examples whose file changed since their picture
    python ci_scripts/playground_screenshots.py --mark-fresh julia_map  # its picture is still right (all if no name)

When a picture is saved, the hash of its example's file goes to picture_hashes.json, next to the pictures: `--stale`
compares it with the file as it is now. A change that does not show (e.g. a docstring) calls for `--mark-fresh`.

The examples that run only in the browser (BROWSER_SHOTS) are pictured in Chrome, in the local playground, with the
screenshot-web-demos skill (it opens a visible Chrome window: ask first). For each of them:
    uv run --no-project --with playwright python .claude/skills/screenshot-web-demos/drive_page.py \
        "http://localhost:6456/playground/?demo=<file name>" --out DIR/web wait:45 shot:<file stem>
which writes DIR/web_<file stem>.png (1400 x 900), then `--browser DIR` crops those it finds in DIR.

Pitfalls:
- The GLFW backend overwrites an injected mouse position at the next frame: drive an example with a test engine
  script (`test`) or with key events.
- The Fiatlight examples take their values and layout from their `fiat_settings` (a saved state, see the examples'
  README): `setup` only fixes what is random.
- On macOS, the examples crash at setup when the display is asleep: run `caffeinate -u -d -t 240 &` first.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

REPO = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO / "bindings/imgui_bundle/demos_python/playground/examples"
OUTPUT_DIR = REPO / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground"
HASHES = OUTPUT_DIR / "picture_hashes.json"  # for each picture: the hash of the example's file it was taken from
WIDTH = 640  # the width of the pictures, in pixels
TIMEOUT = 45  # seconds: an example still running by then is killed (its window closes), and reported

Box = tuple[float, float, float, float]  # a crop: left, top, right, bottom, as fractions of the window


@dataclass
class Shot:
    frames: int = 60  # frames before the picture (0: the example exits by itself, e.g. after its own test)
    crop: Box = (0.0, 0.0, 1.0, 1.0)
    action: Optional[Callable[[dict[str, Any], int], None]] = None  # called each frame with the example's globals
    test: Optional[Callable[[Any], None]] = None  # a test engine script (e.g. open a section), then `frames` frames
    setup: Optional[Callable[[], None]] = None  # called before the example starts


def _julia_rabbit(g: dict[str, Any], frame: int) -> None:
    if frame == 2:
        name = "Douady rabbit"
        g["state"].go_to(g["FAMOUS_C"][name][0], g["ARRIVAL_WIDTH"][name])


def _train(g: dict[str, Any], frame: int) -> None:
    g["state"].training = True


def _fixed_picture() -> None:
    """Fiatlight: the example downloads a random picture; this one gives clean edges (a vulture)"""
    from imgui_bundle import immapp
    download = immapp.download_url_bytes

    def fixed(url: str, *args: Any, **kwargs: Any) -> bytes:
        return download("https://picsum.photos/id/1024/640/480" if url == "https://picsum.photos/640/480" else url,
                        *args, **kwargs)
    immapp.download_url_bytes = fixed  # type: ignore[assignment]


def _open(window: str, *labels: str) -> Callable[[Any], None]:
    """A test engine script: opens these headers or tree nodes of a full demo's window (in its child windows too)"""
    def test(ctx: Any) -> None:
        ctx.set_ref(window)
        for label in labels:
            ctx.item_open("**/" + label)
    return test


def _cjk_font() -> None:
    """The Chinese font demo: a CJK font, downloaded once to a folder the demo finds as an asset (the font is not
    shipped: 16 MB). The picture shows the sample text instead of the "font not found" fallback."""
    import urllib.request
    from imgui_bundle import hello_imgui
    folder = Path(tempfile.gettempdir()) / "imgui_bundle_screenshots_assets"
    font = folder / "fonts/NotoSansSC-Regular.otf"
    if not font.exists():
        font.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf", font)
    hello_imgui.add_assets_search_path(str(folder))


def _neutral_shell() -> None:
    """The terminal: /bin/sh with a plain prompt (the user's shell prompt may show their name and their machine's)"""
    os.environ["SHELL"] = "/bin/sh"
    os.environ["PS1"] = "$ "
    os.environ.pop("ENV", None)  # sh's startup file


def _shell_commands(ctx: Any) -> None:
    """Focuses the terminal (a click in it), and types a few commands"""
    from imgui_bundle import imgui, ImVec2
    ctx.mouse_move_to_pos(ImVec2(400, 200))
    ctx.mouse_click(0)
    ctx.yield_(30)  # the shell starts
    for command in ['echo "A real shell, inside an ImGui window"',
                    r"printf '\033[1;32mgreen \033[1;33myellow \033[1;34mblue\033[0m\n'", "seq 1 3"]:
        ctx.key_chars(command)
        ctx.key_press(imgui.Key.enter)
        ctx.yield_(10)


def _command_palette(ctx: Any) -> None:
    """Opens the command palette (Ctrl+Shift+P), and filters its commands"""
    from imgui_bundle import imgui
    ctx.key_press(imgui.Key.mod_ctrl | imgui.Key.mod_shift | imgui.Key.p)
    ctx.yield_(5)
    ctx.key_chars("the")


MAIN_WINDOW = "Main window (title bar invisible)"  # Hello ImGui's full window, when there is no docking


SHOTS: dict[str, Shot] = {
    "landing_page.py": Shot(crop=(0.0, 0.02, 0.49, 0.57)),
    "welcome_imm_mode.py": Shot(crop=(0.0, 0.52, 0.66, 0.86)),
    "immvision.py": Shot(frames=120, crop=(0.0, 0.3, 0.75, 0.72)),
    "fiatlight_image.py": Shot(frames=200, setup=_fixed_picture, crop=(0.02, 0.08, 0.95, 0.82)),  # layout: fiat_settings
    "fiatlight_dataframe.py": Shot(frames=200, crop=(0.0, 0.04, 0.86, 0.88)),
    "themes.py": Shot(crop=(0.0, 0.33, 1.0, 1.0)),
    # The explorer's demos (source: demos_python)
    "demo_widgets.py": Shot(crop=(0.0, 0.0, 0.82, 0.512)),  # 16:10, as the launcher's cards
    "demo_imgui_md.py": Shot(crop=(0.0, 0.0, 1.0, 0.625)),
    "demo_text_edit.py": Shot(crop=(0.0, 0.0, 0.85, 0.664)),
    "demo_logger.py": Shot(crop=(0.0, 0.0, 0.8, 0.667)),
    "demo_terminal.py": Shot(setup=_neutral_shell, test=_shell_commands, crop=(0.0, 0.0, 0.6, 0.5625)),
    # The explorer's sub-demos (sources: demos_immvision, demos_node_editor)
    "demo_immvision_display.py": Shot(crop=(0.0, 0.0, 0.75, 0.586)),
    "demo_immvision_inspector.py": Shot(crop=(0.0, 0.06, 1.0, 0.84)),
    "demo_immvision_link.py": Shot(crop=(0.0, 0.03, 1.0, 0.81)),
    "demo_immvision_process.py": Shot(crop=(0.0, 0.08, 0.75, 0.549)),
    # the node editor's demos: 200 frames, so that the flow animation along the links has ended (about 2 seconds)
    "demo_node_editor_color_mixer.py": Shot(frames=200, crop=(0.04, 0.1, 0.77, 0.94)),
    "demo_node_editor_image_pipeline.py": Shot(frames=200, crop=(0.05, 0.075, 0.955, 1.0)),
    "demo_node_editor_basic.py": Shot(crop=(0.0, 0.0, 0.65, 0.542)),
    "demo_romeo_and_juliet.py": Shot(crop=(0.0, 0.0, 0.6, 0.469)),
    "demo_gizmo.py": Shot(crop=(0.0, 0.0, 1.0, 0.938)),
    "demo_nanovg_full.py": Shot(crop=(0.0, 0.05, 1.0, 0.883)),
    "demo_nanovg_heart.py": Shot(crop=(0.0, 0.02, 1.0, 0.853)),
    "demo_terminal_pyte.py": Shot(setup=_neutral_shell, test=_shell_commands, crop=(0.0, 0.0, 0.6, 0.603)),
    # The interactive manuals (source: manuals)
    "manual_imgui.py": Shot(crop=(0.0, 0.0, 1.0, 0.625)),
    "manual_implot.py": Shot(crop=(0.0, 0.0, 1.0, 0.625)),
    "manual_implot3d.py": Shot(crop=(0.0, 0.0, 1.0, 0.625)),
    "manual_im_anim.py": Shot(crop=(0.0, 0.0, 1.0, 0.625)),
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
    # The immapp demos (source: demos_immapp)
    "demo_hello_world.py": Shot(crop=(0.0, 0.0, 0.22, 0.18)),
    "demo_parametric_curve.py": Shot(crop=(0.0, 0.0, 1.0, 0.75)),
    "demo_implot_markdown.py": Shot(frames=90, crop=(0.0, 0.0, 0.9, 0.84)),
    "demo_assets_addons.py": Shot(crop=(0.0, 0.0, 0.8, 0.5)),
    "demo_docking.py": Shot(frames=90, crop=(0.0, 0.0, 1.0, 0.64)),
    "demo_custom_background.py": Shot(frames=120),
    "demo_powersave.py": Shot(crop=(0.0, 0.0, 1.0, 0.72)),
    "demo_chinese_font.py": Shot(setup=_cjk_font, crop=(0.0, 0.3, 0.8, 0.9)),  # the sample lines
    "demo_drag_and_drop.py": Shot(crop=(0.0, 0.0, 0.36, 0.44)),
    "demo_command_palette.py": Shot(test=_command_palette, frames=30, crop=(0.0, 0.0, 0.8, 0.3)),
    "demo_testengine.py": Shot(frames=90, crop=(0.0, 0.0, 1.0, 0.8)),
    "demo_testapp.py": Shot(frames=0, crop=(0.0, 0.0, 1.0, 0.36)),  # its test drives it, then it exits
    "demo_python_context_manager.py": Shot(test=_open(MAIN_WINDOW, "ImPlot: Begin\\/End Plot"),  # \/: a "/" in a label
                                           frames=30, crop=(0.0, 0.0, 1.0, 0.8)),
    "demo_run_async.py": Shot(frames=120),
    "demo_glfw_window_manip.py": Shot(crop=(0.0, 0.0, 0.6, 0.22)),
    "demo_matplotlib.py": Shot(frames=60, crop=(0.0, 0.0, 0.92, 0.9)),
    "demo_pydantic.py": Shot(crop=(0.0, 0.0, 1.0, 0.62)),
    "haiku_implot_heart.py": Shot(frames=90, crop=(0.0, 0.0, 0.93, 0.96)),
    "haiku_butterfly.py": Shot(frames=300, crop=(0.08, 0.43, 0.92, 0.706)),  # 16:10, as the launcher's cards
}


# The examples that run only in the browser: the crop of their Chrome picture (the playground's canvas is on the right)
BROWSER_SHOTS: dict[str, Box] = {
    "webgl_minimal_mandelbrot.py": (0.254, 0.063, 1.0, 1.0),
    "webgl_texture_in_image.py": (0.254, 0.063, 0.714, 0.733),
    "webaudio_synth.py": (0.254, 0.063, 1.0, 1.0),
}


def _save(image: Any, crop: Box, output: Path) -> None:
    """Crops the picture, and saves it WIDTH pixels wide, as JPEG"""
    from PIL import Image
    width, height = image.size
    left, top, right, bottom = crop
    image = image.crop((int(left * width), int(top * height), int(right * width), int(bottom * height)))
    image = image.resize((WIDTH, round(image.size[1] * WIDTH / image.size[0])), Image.Resampling.LANCZOS)
    image.convert("RGB").save(output, "JPEG", quality=85, optimize=True, progressive=True)


def _run_one(filename: str, output: str, raw: bool, path: Path) -> None:
    """In a child process: runs the example (a copy of it, at path), then saves its picture"""
    from PIL import Image
    from imgui_bundle import hello_imgui, immapp

    shot = SHOTS[filename]
    # The example runs as the __main__ module, at its path: inspect.getsource() then finds its code (demo_pydantic.py)
    main_module = types.ModuleType("__main__")
    main_module.__file__ = str(path)
    sys.modules["__main__"] = main_module
    namespace: dict[str, Any] = main_module.__dict__
    frame = [0]
    manual_params: list[Any] = []  # the RunnerParams of a manual render loop, which checks their app_shall_exit

    def on_frame() -> None:
        frame[0] += 1
        if shot.action is not None:
            shot.action(namespace, frame[0])
        if shot.frames and frame[0] >= shot.frames:
            hello_imgui.get_runner_params().app_shall_exit = True
            for params in manual_params:
                params.app_shall_exit = True

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
        if args and isinstance(args[0], hello_imgui.SimpleRunnerParams):
            simple_params = args[0]
            simple_gui = simple_params.gui_function

            def driven_simple_gui() -> None:
                simple_gui()
                on_frame()
            simple_params.gui_function = driven_simple_gui
            return args, kwargs
        gui = args[0] if args else kwargs.pop("gui_function")

        def driven_gui() -> None:
            gui()
            on_frame()
        return (driven_gui, *args[1:]), kwargs

    immapp_run = immapp.run

    def driven(run: Callable[..., None]) -> Callable[..., None]:
        """A runner (immapp.run, hello_imgui.run, immapp.run_with_markdown) that calls on_frame() each frame"""
        def run_driven(*args: Any, **kwargs: Any) -> None:
            if shot.test is not None:  # the test engine drives the app, then exits
                from imgui_bundle.immapp import testing

                def test_fn(ctx: Any) -> None:
                    shot.test(ctx)  # type: ignore[misc]
                    ctx.yield_(shot.frames)
                immapp.run = immapp_run  # testing.run calls immapp.run itself
                if args and isinstance(args[0], hello_imgui.RunnerParams):
                    # with runner_params, testing.run ignores its gui_function (the params have their own)
                    add_ons = args[1] if len(args) > 1 else kwargs.get("add_ons_params")
                    testing.run(args[0].callbacks.show_gui, test_fn, runner_params=args[0], add_ons_params=add_ons)
                else:
                    gui = args[0] if args else kwargs.pop("gui_function")
                    testing.run(gui, test_fn, **kwargs)
                return
            args, kwargs = drive(args, kwargs)
            run(*args, **kwargs)
        return run_driven

    def driven_async(run_async: Callable[..., Any]) -> Callable[..., Any]:
        """immapp.run_async or hello_imgui.run_async, calling on_frame() each frame"""
        async def run_async_driven(*args: Any, **kwargs: Any) -> None:
            args, kwargs = drive(args, kwargs)
            await run_async(*args, **kwargs)
        return run_async_driven

    # All the ways to run an app (the same list as pyodide_patch_runners.py), and the manual render loop below
    immapp.run = driven(immapp.run)  # type: ignore[assignment]
    immapp.run_with_markdown = driven(immapp.run_with_markdown)  # type: ignore[assignment]
    hello_imgui.run = driven(hello_imgui.run)  # type: ignore[assignment]
    immapp.run_async = driven_async(immapp.run_async)  # type: ignore[assignment]
    hello_imgui.run_async = driven_async(hello_imgui.run_async)  # type: ignore[assignment]

    setup_manual_render = hello_imgui.manual_render.setup_from_runner_params

    def setup_manual_render_driven(params: Any, *args: Any, **kwargs: Any) -> None:
        """A manual render loop (e.g. demo_docking.py): on_frame() after each frame, and it ends the loop"""
        drive((params,), {})
        manual_params.append(params)
        setup_manual_render(params, *args, **kwargs)
    hello_imgui.manual_render.setup_from_runner_params = setup_manual_render_driven  # type: ignore[assignment]
    sys.path.insert(0, str(path.parent))
    if shot.setup is not None:
        shot.setup()
    try:
        exec(compile(path.read_text(), str(path), "exec"), namespace)
    except SystemExit:  # e.g. `sys.exit(main())`, after the app ran: its picture can be saved
        pass

    image = Image.fromarray(hello_imgui.final_app_window_screenshot())
    if raw:
        image.save(output)
    else:
        _save(image, shot.crop, Path(output))


def _examples() -> dict[str, tuple[Path, list[tuple[Path, str]]]]:
    """For each example: the path of its file, and its bundle folders (their path, and where they go next to it, as in
    the playground: a folder outside the example's folder, e.g. ../demos_assets, goes under its own name)"""
    from playground_examples_docs import disk_path
    manifest = json.loads((EXAMPLES_DIR / "examples.json").read_text())
    sources = manifest["sources"]
    examples = {}
    for e in manifest["examples"]:
        source = e.get("source", "examples")
        folders = [(disk_path(sources, f"{source}/{f}"), re.sub(r"^(\.\./)+", "", f))
                   for f in e.get("bundle_folders", [])]
        examples[e["filename"]] = (disk_path(sources, f"{source}/{e['filename']}"), folders)
    return examples


def _hashes() -> dict[str, str]:
    return json.loads(HASHES.read_text()) if HASHES.exists() else {}


def _file_hash(filename: str, examples: dict[str, tuple[Path, list[tuple[Path, str]]]]) -> str:
    return hashlib.sha256(examples[filename][0].read_bytes()).hexdigest()[:12]


def _record(filenames: list[str]) -> None:
    """Remembers, for each example, the hash of its file as it is now (its picture was taken from it)"""
    examples, hashes = _examples(), _hashes()
    hashes.update({Path(f).stem: _file_hash(f, examples) for f in filenames})
    HASHES.write_text(json.dumps(dict(sorted(hashes.items())), indent=2) + "\n")


def _list_stale() -> None:
    """Lists the examples whose file changed since their picture was taken"""
    examples, hashes = _examples(), _hashes()
    stale = 0
    for filename in [*SHOTS, *BROWSER_SHOTS]:
        recorded = hashes.get(Path(filename).stem)
        if recorded != _file_hash(filename, examples):
            stale += 1
            where = "browser: see --browser" if filename in BROWSER_SHOTS else "desktop"
            print(f"{'changed' if recorded else 'no hash':12s} {filename} ({where})")
    print(f"{stale} of {len(SHOTS) + len(BROWSER_SHOTS)} pictures may be stale")


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--one"]:
        _run_one(args[1], args[2], raw=args[3] == "raw", path=Path(args[4]))
        return
    if args[:1] == ["--stale"]:
        _list_stale()
        return
    if args[:1] == ["--mark-fresh"]:
        _record([f for f in [*SHOTS, *BROWSER_SHOTS] if len(args) == 1 or Path(f).stem in args[1:]])
        return
    if args[:1] == ["--browser"]:
        from PIL import Image
        cropped = []
        for filename, crop in BROWSER_SHOTS.items():  # those whose Chrome picture is in DIR
            stem = Path(filename).stem
            capture = Path(args[1]) / f"web_{stem}.png"
            if capture.exists():
                output = OUTPUT_DIR / f"{stem}.jpg"
                _save(Image.open(capture), crop, output)
                cropped.append(filename)
                print(f"ok           {filename} -> {output}")
        _record(cropped)
        return
    raw_dir = None
    if args[:1] == ["--raw"]:
        raw_dir, args = Path(args[1]), args[2:]
        raw_dir.mkdir(parents=True, exist_ok=True)
    names = [f for f in SHOTS if not args or Path(f).stem in args]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    examples = _examples()
    for filename in names:
        stem = Path(filename).stem
        output = raw_dir / f"{stem}.png" if raw_dir else OUTPUT_DIR / f"{stem}.jpg"
        # Run a copy of the example in a scratch folder, as the playground does (its home folder, with the example's
        # bundle folders): what an example writes next to itself (e.g. Fiatlight's settings) stays out of the repository
        output.unlink(missing_ok=True)  # a picture from a previous run must not pass for this one's
        with tempfile.TemporaryDirectory() as cwd:
            source, bundle_folders = examples[filename]
            for folder, target in bundle_folders:
                shutil.copytree(folder, Path(cwd) / target, dirs_exist_ok=True)
            copy = Path(cwd) / filename
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, copy)
            try:
                result = subprocess.run([sys.executable, __file__, "--one", filename, str(output),
                                         "raw" if raw_dir else "jpg", str(copy)], cwd=cwd, timeout=TIMEOUT,
                                        capture_output=True, text=True, env={**os.environ, "PYTHONUNBUFFERED": "1"})
            except subprocess.TimeoutExpired:
                print(f"{'TIMEOUT':12s} {filename}: still running after {TIMEOUT} s, killed")
                continue
        status = "ok" if result.returncode == 0 and output.exists() else f"FAILED ({result.returncode})"
        print(f"{status:12s} {filename} -> {output}")
        if status != "ok":
            print(result.stderr[-1500:])
        elif not raw_dir:
            _record([filename])


if __name__ == "__main__":
    main()
