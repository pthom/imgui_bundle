# Intro to Runners

ImGui Bundle uses two main libraries to manage the application lifecycle: **Hello ImGui** and **ImmApp**.

## Hello ImGui vs ImmApp

*   **[Hello ImGui](https://github.com/pthom/hello_imgui)**: A "starter pack" for Dear ImGui. It handles window creation, backend initialization (SDL, GLFW, etc.), cross-platform assets, docking, and more.
*   **ImmApp (Immediate App)**: A thin wrapper around Hello ImGui specifically designed for ImGui Bundle. Its main purpose is to simplify the initialization of **add-ons** (like ImPlot or Markdown) that require specific setup.

## Starting an Application

The simplest way to start an application is to use `immapp.run()` (Python) or `ImmApp::Run()` (C++).


::::{tab-set}

:::{tab-item} Python
In Python, `immapp.run` accepts a `gui_function` and several optional parameters to quickly configure the window and add-ons.

```python
from imgui_bundle import immapp, imgui

def gui():
    imgui.text("My App")

immapp.run(
    gui,
    window_title="Hello",
    window_size=(800, 600)
)
```
:::

:::{tab-item} C++
In C++, you typically use a lambda or a function pointer for the GUI, and pass configuration via `SimpleRunnerParams`.

```cpp
#include "immapp/immapp.h"
#include "imgui.h"

int main() {
    auto gui = []() { ImGui::Text("My App"); };
    ImmApp::Run(gui, "Hello", {800, 600});
    return 0;
}
```
:::

::::

:::{note}
You may also call `hello_imgui.run()` (Python) or `HelloImGui::Run()` (C++), but in that case you cannot use addons, such as ImPlot; unless you initialize them manually.
:::


## Activating Add-ons

Many libraries in the bundle (like **ImPlot** or **imgui_md**) require initialization at startup (e.g., creating contexts or loading specific fonts). `ImmApp` manages this via `AddOnsParams`.

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import immapp, implot, imgui_md

def gui():
    imgui_md.render("# Title")
    if implot.begin_plot("My Plot"):
        # ...
        implot.end_plot()

immapp.run(
    gui,
    with_implot=True,   # Activates ImPlot context
    with_markdown=True  # Loads Markdown fonts
)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"

int main() {
    auto gui = []() { /* ... */ };

    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui;

    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    addons.withMarkdown = true;

    ImmApp::Run(runnerParams, addons);
    return 0;
}
```
:::

::::


## Correctly size and position the widgets

It is almost always a bad idea to use fixed sizes. This will lead to portability issues, especially on high-DPI screens.

Instead of using fixed pixel sizes, it is recommended to use sizes relative to the font size, aka "em" units.

:::{tip}
See the definition of the [em CSS Unit](https://en.wikipedia.org/wiki/Em_(typography)).
:::

To achieve this, you should multiply your positions and sizes by `ImGui::GetFontSize()` (C++), or `imgui.get_font_size()` (Python).

In order to make this simpler, the `HelloImGui::EmToVec2` (C++) or `hello_imgui::em_to_vec2` (Python) function below can greatly reduce the friction: it transforms a size in "em" units to a size in pixels.


Example with Python:

```python
from imgui_bundle import imgui, hello_imgui

def gui():
    imgui.button("A button", hello_imgui.em_to_vec2(10, 2))  # 10em x 2em button
```

Example with C++:

```cpp
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"

void gui() {
    ImGui::Button("A button", HelloImGui::EmToVec2(10, 2)); // 10em x 2em button
}
```

:::{note}
* `EmSize(x)` functions are also available to get only one dimension in pixels. (e.g., `hello_imgui.em_size(2)` or `HelloImGui::EmSize(2)`).

* `EmToVec2` and `EmSize` are also available in the `immapp` module in Python, and in the `ImmApp` namespace in C++.
:::
