# Basic Runner (Hello ImGui & ImmApp)

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
