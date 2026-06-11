# ImGui Test Engine

[ImGui Test Engine](https://github.com/ocornut/imgui_test_engine) is the official testing and automation framework for Dear ImGui. It enables automated UI testing, screenshot capture, and regression testing.

:::{note}
**License:** Free for individuals, educational, open-source, and small business uses. Larger businesses require a paid license. See the [full license](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt).
:::

:::{important}
**Python:** Requires Hello ImGui or ImmApp – standalone usage isn't supported due to internal threading requirements.
:::

## Quick Start

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, hello_imgui

my_test: imgui.test_engine.Test

def my_register_tests():
    global my_test
    engine = hello_imgui.get_imgui_test_engine()
    my_test = imgui.test_engine.register_test(engine, "My Tests", "Click Button")

    def test_func(ctx: imgui.test_engine.TestContext):
        ctx.item_click("**/My Button")

    my_test.test_func = test_func

def gui():
    test_engine = hello_imgui.get_imgui_test_engine()
    if imgui.button("My Button"):
        print("Clicked!")
    if imgui.button("Run Tests"):
        imgui.test_engine.queue_test(test_engine, my_test)

params = hello_imgui.RunnerParams()
params.use_imgui_test_engine = True
params.callbacks.register_tests = my_register_tests
params.callbacks.show_gui = gui
hello_imgui.run(params)
```
:::

:::{tab-item} C++
```cpp
#include "hello_imgui/hello_imgui.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"

ImGuiTest * myTest = nullptr;

void RegisterTests() {
    ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
    myTest = ImGuiTestEngine_RegisterTest(engine, "My Tests", "Click Button");

    myTest->TestFunc = [](ImGuiTestContext* ctx) {
        ctx->ItemClick("**/My Button");
    };
}

void Gui() {
    auto testEngine = HelloImGui::GetImGuiTestEngine();
    if (ImGui::Button("My Button"))
        printf("Clicked!\n");
    if (ImGui::Button("Run Tests"))
        ImGuiTestEngine_QueueTest(testEngine, myTest);
}

int main() {
    HelloImGui::RunnerParams params;
    params.useImGuiTestEngine = true;
    params.callbacks.RegisterTests = RegisterTests;
    params.callbacks.ShowGui = Gui;
    HelloImGui::Run(params);
    return 0;
}
```
:::
::::

## Full demo

For more complete examples, see the test engine demo from the interactive explorer:
* [Try online](https://imgui-bundle.pages.dev/explorer/demo_testengine.html)
* [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_testengine.py)
* [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_testengine.cpp)


## Named References

Test Engine uses "named references" to find widgets. The syntax uses path separators:

| Pattern | Meaning |
|---------|---------|
| `"Button"` | Widget named "Button" in current reference |
| `"**/Button"` | Search for "Button" anywhere in children |
| `"//Window/Button"` | Absolute path from root |
| `"$FOCUSED"` | Currently focused window |

```python
ctx.set_ref("My Window")           # Set current reference
ctx.item_click("**/Save")          # Find "Save" anywhere in window
ctx.item_click("//Dialog/OK")      # Absolute path to OK button
```

## Common Actions

```python
# Click items
ctx.item_click("**/Button")
ctx.item_double_click("**/Item")

# Input text
ctx.item_input("**/Name", "John Doe")

# Check/uncheck
ctx.item_check("**/Enable")
ctx.item_uncheck("**/Disable")

# Open/close tree nodes
ctx.item_open("**/Settings")
ctx.item_close("**/Settings")
ctx.item_open_all("**/Tree")

# Screenshots
ctx.capture_screenshot_window("Window Name")

# Keyboard input
ctx.key_press(imgui.Key.enter)
ctx.key_chars("Hello")
```

## Assertions

Use the `CHECK` function to verify conditions:

```python
from imgui_bundle.imgui.test_engine_checks import CHECK

def test_func(ctx: imgui.test_engine.TestContext):
    ctx.item_click("**/Increment")
    CHECK(counter == 1)  # Verify counter was incremented
```

## Custom Test GUI

Tests can display their own GUI:

```python
my_test = imgui.test_engine.register_test(engine, "Category", "Test Name")


def test_gui_func(ctx: imgui.test_engine.TestContext):
    imgui.text("Custom test controls here")
    if imgui.button("Do Something"):
        # Custom action
        pass


my_test.gui_func = test_gui_func
```

## Driving a GUI and capturing screenshots — `immapp.testing`

ImGui Bundle ships a small testing module that combines the test engine
with screenshot capture. Use it when you want to script an interaction
(click, type, expand a header) and grab a PNG at chosen moments.

- `immapp.testing.run(gui, test_fn, ...)` — Python: runs the GUI and drives
  it with `test_fn(ctx)`; exits once the test finishes (override with
  `exit_after_test=False`).
- `immapp.testing.capture(ctx, path, window=None, flags=0)` — Python: write
  a PNG from inside a test. Captures the full framebuffer, or a single
  window if `window="My Window"`.
- `immapp.testing.capture_final_frame(gui, path, ...)` — Python one-shot:
  run the GUI for a few frames, save the final frame. No test engine.
- `ImmApp::Testing::Capture(ctx, path, {window, flags})` — C++ equivalent
  of `capture`, from `immapp/testing.h`.
- `ImmApp::Testing::CaptureFinalFrame(guiFn, path, opts)` — C++ one-shot.

Example:

```python
from imgui_bundle import imgui
from imgui_bundle.immapp import testing

def gui():
    imgui.button("Click me")

def my_test(ctx: imgui.test_engine.TestContext):
    testing.capture(ctx, "/tmp/00_initial.png")
    ctx.item_click("//**/Click me")
    testing.capture(ctx, "/tmp/01_after_click.png")

testing.run(gui, my_test, window_size=(600, 400))
```

See the full demo in
[`demo_testapp.py`](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_testapp.py)
and
[`demo_testapp.cpp`](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_testapp.cpp).

## Running Tests

When test engine is enabled:
1. A "Test Engine" window appears
2. Click tests to run them
3. Watch as actions are automated
4. Check results (green = pass, red = fail)

## Documentation & Resources

- **[Test Engine Wiki](https://github.com/ocornut/imgui_test_engine/wiki)** - Official documentation
- **[Named References](https://github.com/ocornut/imgui_test_engine/wiki/Named-References)** - Path syntax reference
