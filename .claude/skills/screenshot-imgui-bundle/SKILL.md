---
name: screenshot-imgui-bundle
description: Capture a screenshot of an imgui_bundle GUI for visual self-validation. Use after editing any C++ or Python code that affects UI rendering (markdown, plots, themes, layout, fonts, math) so you can verify the result before asking the user to look. Avoids running apps blindly.
---

# Screenshot ImGui Bundle GUIs for visual validation

When you've changed UI code and want to verify the result, do not run the app
"for 3 seconds and hope for the best". Take a screenshot, look at it, and
confirm visually before claiming the change works.

The helpers live in `immapp.testing` (Python) and `immapp/testing.h` (C++).
Both run the GUI for a few frames, grab the final framebuffer, and save it
as a PNG.

- Python: `immapp.testing.capture_final_frame(gui_fn, output_path, ...)`
- C++:    `ImmApp::Testing::CaptureFinalFrame(guiFn, path, opts)`

For **interactive** captures (click a button, set a slider, expand a
collapsing header *then* screenshot), use the companion skill
`interact-and-screenshot`, which drives the GUI via the ImGui Test Engine.

## Entry points

- No recipe: the helpers are `immapp.testing` (Python) and `immapp/testing.h` (C++), described below.
- The pictures of the playground's examples have their own tool: `just playground_screenshots [names]` (its options, e.g. `--stale`, are in the docstring of `ci_scripts/playground_screenshots.py`).

## Decision: Python or C++?

- **Default to Python.** Use Python whenever the rendering you want to
  validate is reachable through `rich_md.render()`, an existing
  `demo_*.py`, or any other Python-side gui callback. This covers ~all UI
  changes that affect the markdown / LaTeX / themes / widgets path.
- **Use C++ only when** the change is specific to a C++ code path with no
  equivalent Python entry point.

Python is faster (no rebuild) and the failure mode is the same in both
languages.

## Python workflow

Write a tiny temp script (in `/tmp/` to keep the repo clean), import the
gui function you want to capture, call `capture_final_frame`, then `Read`
the PNG file.

```python
# /tmp/shoot.py
from imgui_bundle.immapp import testing
from imgui_bundle.demos_python import demo_imgui_md

testing.capture_final_frame(
    demo_imgui_md.demo_gui,
    "/tmp/out.png",
    window_size=(900, 950),     # logical pixels; framebuffer is 2x on retina
    with_latex=True,            # any immapp.run addon works
)
# An addon without a shortcut (e.g. with_node_editor_config): pass add_ons_params=immapp.AddOnsParams(...)
```

Run it and read the PNG:

```bash
python /tmp/shoot.py   # the Python where imgui_bundle is installed
```

```
Read /tmp/out.png
```

The PNG appears as `<output_image>` in the tool result.

### Common parameters

- `window_size=(W, H)` — logical pixels. The captured framebuffer is
  `W*scale` by `H*scale` (typically 2.0 on macOS retina, 1.0 otherwise).
- `exit_after_frames=8` — bump higher (15-30) if the layout needs more
  time to settle (async assets, animations, font baking).
- `with_markdown=True` / `with_latex=True` / `with_implot=True` etc. — as
  in `immapp.run`.
- `ini_disable=True` (default) — avoids leaving `.ini` files on disk and
  prevents window-state drift across repeated screenshot runs.

### Validating only a SECTION of a long demo

If the relevant content is at the bottom of a long markdown demo, your
screen won't fit the whole window. Don't try to make the window taller
than the display — HelloImGui will silently clamp it. Instead, render
only the section you care about:

```python
from imgui_bundle import rich_md

full = demo_imgui_md.example_markdown_string()
section = full[full.index("## Math formulas"):]

def gui():
    rich_md.render_unindented(section)

testing.capture_final_frame(gui, "/tmp/section.png", with_latex=True)
```

## C++ workflow

Drop a temporary `.cpp` file into `bindings/imgui_bundle/demos_cpp/sandbox/`.
That folder's CMakeLists globs `*.cpp`, so on the next `cmake .` reconfigure
your file becomes a target named after the filename (without `.cpp`).

```cpp
// bindings/imgui_bundle/demos_cpp/sandbox/sandbox_shoot_xxx.cpp
// TEMPORARY: delete after validating the screenshot.
#include "immapp/testing.h"
#include "imgui_rich_md/rich_md.h"

int main()
{
    ImmApp::Testing::CaptureFinalFrameOptions opts;
    opts.windowSize = ImVec2(900, 600);
    opts.withLatex  = true;

    bool ok = ImmApp::Testing::CaptureFinalFrame(
        [](){ RichMd::Render("Inline: $E = mc^2$"); },
        "/tmp/out.png",
        opts);
    return ok ? 0 : 1;
}
```

Build and run:

```bash
cd builds/claude_python_bindings           # a build folder of yours, with the C++ demos (AGENTS.md, "Build folders")
cmake .                                    # rediscover the new sandbox file
cmake --build . --target sandbox_shoot_xxx -j4
./bin/sandbox_shoot_xxx.app/Contents/MacOS/sandbox_shoot_xxx   # macOS
# (on Linux/Windows the binary is at ./bin/sandbox_shoot_xxx[.exe])
```

```
Read /tmp/out.png
```

After validation, **delete the temp `sandbox_shoot_xxx.cpp`**:

```bash
rm bindings/imgui_bundle/demos_cpp/sandbox/sandbox_shoot_xxx.cpp
```

## Caveats

- **Real GL context required.** Both helpers open a real window for a few
  frames; they're not headless. On macOS / Windows / Linux desktop they
  just work; on a headless Linux CI runner you'd need Xvfb.
- **Window briefly flashes.** ~100-200 ms. By design: real frames render
  to capture real output.
- **`window_size` is logical pixels**, framebuffer is `size * scale`. On
  retina the PNG is 2× the logical size.
- **Display-height clamp.** If you ask for a window taller than the
  display, HelloImGui silently clamps it. Render the section you care
  about rather than fighting this.
- **Always clean up temp files.** Python: delete `/tmp/shoot_*.py`. C++:
  delete the sandbox `.cpp`. Leaving these around clutters the repo and
  can confuse future builds.

## Reference

- Python: `immapp.testing.capture_final_frame`
- C++: `ImmApp::Testing::CaptureFinalFrame` (in `immapp/testing.h`)
- Interactive captures: see the `interact-and-screenshot` skill.
- Web builds (Emscripten, Pyodide) in a browser: see the `screenshot-web-demos` skill.
- Underlying API: `hello_imgui::FinalAppWindowScreenshotRgbBuffer()` /
  `hello_imgui.final_app_window_screenshot()`.
