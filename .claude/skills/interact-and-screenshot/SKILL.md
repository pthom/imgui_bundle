---
name: interact-and-screenshot
description: Drive an imgui_bundle GUI via the ImGui Test Engine (click, type, expand headers) and capture screenshots at chosen moments. Use whenever validating a UI change requires interaction first — e.g. clicking a button to open a panel, expanding a collapsing header, filling a text field — before the interesting state is visible.
---

# Interact and screenshot an ImGui Bundle GUI

When a UI change only shows its effect **after interaction** (click a
button, set a slider, expand a collapsing header, type in a field), a
single post-launch screenshot isn't enough. Use the `immapp.testing`
module to drive the GUI with the ImGui Test Engine and save a PNG at
each interesting state.

For **one-shot** captures with no interaction, use the simpler
`screenshot-imgui-bundle` skill instead.

## Entry points

- No recipe: `immapp.testing.run` and `capture`, described below. The test engine's doc: `docs/book/core_libs/test_engine.md`.
- The pictures of the playground's examples have their own tool: `just playground_screenshots [names]` (see the docstring of `ci_scripts/playground_screenshots.py`).

## Python

```python
# /tmp/shoot.py
from imgui_bundle import imgui
from imgui_bundle.immapp import testing

def gui():
    # ... the GUI you want to drive (your own, or imported from a demo).
    if imgui.button("Click me"):
        pass

def my_test(ctx: imgui.test_engine.TestContext):
    testing.capture(ctx, "/tmp/00_initial.png")
    ctx.item_click("//**/Click me")
    testing.capture(ctx, "/tmp/01_after_click.png")

testing.run(gui, my_test, window_size=(600, 400))
```

Run it and read the PNGs:

```bash
python /tmp/shoot.py   # the Python where imgui_bundle is installed
```

```
Read /tmp/00_initial.png
Read /tmp/01_after_click.png
```

### API cheat sheet

- `testing.run(gui, test_fn, *, exit_after_test=True, run_speed=fast, ...)`
  — runs the GUI, drives it with `test_fn(ctx)`, exits when `test_fn`
  returns. Accepts the same `with_markdown` / `with_latex` / `with_implot`
  / etc. addon flags as `immapp.run`. Set `exit_after_test=False` to keep
  the window open after the test (useful for manual inspection). An app
  with its own params (e.g. the explorer's `make_params()`):
  `testing.run(test_function=test_fn, runner_params=rp, add_ons_params=addons)`.
- `testing.capture(ctx, path, *, window=None, flags=0)` — write a PNG.
  Default captures the full framebuffer; pass `window="My Window"` for a
  single window (bare labels are auto-prefixed with `//`).
- `testing.TestRunSpeed.fast | normal | cinematic` — speed enum.
- Full demo: `bindings/imgui_bundle/demos_python/demos_immapp/demo_testapp.py`.

### Common interactions inside `test_fn`

```python
ctx.item_click("//**/Button label")           # click a button
ctx.item_input_value("//**/Slider", 42)       # set slider/input
ctx.item_click("//**/Checkbox label")         # toggle
ctx.item_open("//**/Header label")            # expand collapsing header
ctx.key_chars("Hello from test engine!")      # type text (item must be focused)
ctx.set_ref("My Window")                      # scope further refs
ctx.sleep_short()                             # let async state settle
```

Path syntax:
- `"//..."` — absolute (ignore any prior `set_ref`).
- `"**/Name"` — wildcard search inside current scope.
- `"//**/Name"` — absolute wildcard (most common for self-contained demos).
- `\/` escapes a `/` inside a label, in full paths and in wildcards: write a raw string, `r"//**/Begin\/End Group"`.
  To discover paths interactively, add `imgui.show_id_stack_tool_window()` to the gui.

## C++

The C++ side ships only the `Capture` primitive — no `Run` wrapper (the
RunnerParams boilerplate is already small). Reproduce the Python flow
by hand:

```cpp
#include "hello_imgui/hello_imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "immapp/testing.h"

static bool gDone = false;

int main() {
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowTitle         = "probe";
    params.appWindowParams.windowGeometry.size = {600, 400};
    params.iniDisable         = true;
    params.useImGuiTestEngine = true;
    params.callbacks.ShowGui  = [](){ /* your GUI */ };

    params.callbacks.RegisterTests = []() {
        auto* engine = HelloImGui::GetImGuiTestEngine();
        ImGuiTest* t = IM_REGISTER_TEST(engine, "probe", "shots");
        t->TestFunc = [](ImGuiTestContext* ctx) {
            ImmApp::Testing::Capture(ctx, "/tmp/00_initial.png");
            ctx->ItemClick("//**/Click me");
            ImmApp::Testing::Capture(ctx, "/tmp/01_after_click.png");
            gDone = true;
        };
        ImGuiTestEngine_QueueTest(engine, t);
    };

    params.callbacks.BeforeImGuiRender = []() {
        if (!gDone) return;
        auto* engine = HelloImGui::GetImGuiTestEngine();
        if (ImGuiTestEngine_IsTestQueueEmpty(engine))
            HelloImGui::GetRunnerParams()->appShallExit = true;
    };

    HelloImGui::Run(params);
    return 0;
}
```

Full demo: `bindings/imgui_bundle/demos_cpp/demos_immapp/demo_testapp.cpp`.

## Caveats

- **Engine failures raise.** `testing.run` raises `RuntimeError` (with the
  test engine log attached) when an interaction failed, and `capture` raises
  instead of silently writing nothing. Engine errors are also printed live
  to the terminal. After a first failed interaction, the engine ignores all
  subsequent operations, so fix the first error reported.
- **Real GL context required.** Same as `screenshot-imgui-bundle`: not
  headless; needs Xvfb on headless CI.
- **`<details>` (markdown collapsibles) are not ImGui widgets** and
  cannot be driven by `item_click` / `item_open`. For markdown-only
  captures, fall back to the one-shot flow.
- **`capture(..., window=...)` uses named references** — a bare label is
  auto-prefixed with `//` (absolute). Pass a full path explicitly for
  nested windows.
- **Capture yields one frame** before grabbing the framebuffer to settle
  animation state. If a wider settling is needed (font baking, async
  assets), add `ctx.sleep_short()` before `capture`.
- **In the default `fast` run speed, `ctx.sleep(...)` only yields a frame**:
  no real time passes. What needs real time (a tooltip's delay, an
  animation, a download) needs `run_speed=testing.TestRunSpeed.normal`.
  To hover a point rather than an item: `ctx.mouse_move_to_pos(ImVec2(x, y))`,
  with coordinates read on a first capture.
- **Clean up temp files** (`/tmp/shoot_*.py`, temp sandbox `.cpp`) after
  validating — same hygiene as `screenshot-imgui-bundle`.

## Reference

- Python: `immapp.testing.run`, `immapp.testing.capture`,
  `imgui.test_engine.TestContext` methods
  (`bindings/imgui_bundle/imgui/test_engine.pyi`).
- C++: `immapp/testing.h` (`Capture`, `CaptureFinalFrame`);
  `imgui_test_engine/imgui_te_context.h` for `ItemClick` /
  `ItemInputValue` / `ItemOpen` / `KeyChars` / etc.
- Web builds (Emscripten, Pyodide) in a browser: see the `screenshot-web-demos` skill.
- Docs: [`docs/book/core_libs/test_engine.md`](https://github.com/pthom/imgui_bundle/blob/main/docs/book/core_libs/test_engine.md).
