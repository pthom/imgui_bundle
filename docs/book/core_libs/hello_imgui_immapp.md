# App Runners

**Hello ImGui** and **ImmApp** are the two main ways to create applications with ImGui Bundle.

- **[Hello ImGui](https://github.com/pthom/hello_imgui)** is a cross-platform framework that handles window creation, backend initialization, assets, theming, and more.
- **ImmApp** (Immediate App) is a thin wrapper around Hello ImGui that simplifies the initialization of add-ons (ImPlot, Markdown, Node Editor, etc.).

These runners enable you to create powerful ImGui applications with minimal boilerplate code.

:::{tip}
* Use `hello_imgui.run()` for simple apps without add-ons. Use `immapp.run()` when you need add-ons like ImPlot or Markdown.
* In Python, you may also choose to use [pure Python backends](../python/pure_python_backend.md) for full control over windowing and rendering.
:::

---

## Interactive Manual

The best way to learn is through the **[Interactive Manual](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)**. The "Demo Apps" tab lets you explore demos with their source code in Python and C++.

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html
```{figure} ../images/demo_immapp_apps.webp
:width: 500
ImGui Bundle Interactive Manual - Explore the "Demo Apps" tab
```
````

:::{tip}
The source code for all demos is extensively documented and can serve as practical documentation.
:::


## Hello ImGui

### Quick Start

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import hello_imgui, imgui

def gui():
    imgui.text("Hello, world!")

hello_imgui.run(gui, window_title="My App", window_size=(800, 600))
```
:::

:::{tab-item} C++
```cpp
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

void gui() {
    ImGui::Text("Hello, world!");
}

int main() {
    HelloImGui::Run(gui, "My App", {800, 600});
    return 0;
}
```
:::

::::

### Documentation

- **[Hello ImGui Documentation](https://pthom.github.io/hello_imgui)** - Full documentation
- **[RunnerParams Reference](https://pthom.github.io/hello_imgui/book/doc_params.html)** - All configuration options
- **[API Reference](https://pthom.github.io/hello_imgui/book/doc_api.html)** - Full API documentation
- **Python API Stubs:** [hello_imgui.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi) | [immapp/\_\_init\_\_.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/immapp/__init__.pyi)


### Features

**Application Features:**
- Power Save mode: reduce FPS when idling
- High DPI support across all platforms
- Dockable windows and multiple layouts
- Window geometry persistence
- Extensive theming options
- Borderless, movable/resizable windows
- Icon fonts and emoji support
- ImGui Test Engine integration

**Multiplatform:**
- Windows, Linux, macOS, iOS, Android, WebAssembly
- Available backends: SDL2, GLFW3 (only Glfw3 with Python)
- Available renderers: OpenGL3, Metal, Vulkan, DirectX (only OpenGL3 with Python)

### Configuration with RunnerParams

For full control, configure your application via `RunnerParams`:

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import hello_imgui, imgui

def gui():
    imgui.text("Hello!")

# Create and configure runner params
params = hello_imgui.RunnerParams()
params.app_window_params.window_title = "My Application"
params.app_window_params.window_geometry.size = (1200, 800)
params.app_window_params.restore_previous_geometry = True

# ImGui window settings
params.imgui_window_params.show_menu_bar = True
params.imgui_window_params.show_status_bar = True

# Set the GUI callback
params.callbacks.show_gui = gui

# Run
hello_imgui.run(params)
```
:::

:::{tab-item} C++
```cpp
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

void gui() {
    ImGui::Text("Hello!");
}

int main() {
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowTitle = "My Application";
    params.appWindowParams.windowGeometry.size = {1200, 800};
    params.appWindowParams.restorePreviousGeometry = true;

    params.imGuiWindowParams.showMenuBar = true;
    params.imGuiWindowParams.showStatusBar = true;

    params.callbacks.ShowGui = gui;

    HelloImGui::Run(params);
    return 0;
}
```
:::

::::

See [RunnerParams Reference](https://pthom.github.io/hello_imgui/book/doc_params.html) for all configuration options. For Python, see [RunnerParams Type Hints](https://github.com/pthom/imgui_bundle/blob/33f407b1d8083f88514d61e0b43683860b39fc96/bindings/imgui_bundle/hello_imgui.pyi#L2936)

### Callbacks

Hello ImGui provides several callback hooks:

| Callback | When Called |
|----------|-------------|
| `show_gui` | Every frame (main GUI) |
| `show_menus` | Every frame (menu bar content) |
| `show_status` | Every frame (status bar) |
| `post_init` | Once, after OpenGL initialization |
| `before_exit` | Once, before shutdown |

See [Full Callback Reference](https://pthom.github.io/hello_imgui/book/doc_params.html#runner-callbacks) for details. For Python, see [Callbacks Type Hints](https://github.com/pthom/imgui_bundle/blob/33f407b1d8083f88514d61e0b43683860b39fc96/bindings/imgui_bundle/hello_imgui.pyi#L1713).

### Application Settings

ImGui applications store settings (window positions, etc.) in an INI file. By default, it's named after your window title. For production apps, use a proper config location:

```python
params.ini_folder_type = hello_imgui.IniFolderType.app_user_config_folder  # ~/.config or AppData
params.ini_filename = "my_app/settings.ini"
```

You can also store custom settings: `hello_imgui.save_user_pref("key", "value")` / `load_user_pref("key")`

### DPI-Aware Sizing

**Never use fixed pixel sizes.** This leads to portability issues on high-DPI screens.

Instead, use sizes relative to the font size using "em" units. Hello ImGui provides helper functions:

:::{tip}
1 em = the height of the current font. See [em (typography)](https://en.wikipedia.org/wiki/Em_(typography)).
:::

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, em_to_vec2, em_size

def gui():
    # Button sized as 10em x 2em (scales with DPI)
    imgui.button("A button", em_to_vec2(10, 2))

    # For single values, use em_size
    width = em_size(10)
```
:::

:::{tab-item} C++
```cpp
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"

void gui() {
    // Button sized as 10em x 2em (scales with DPI)
    ImGui::Button("A button", HelloImGui::EmToVec2(10, 2));

    // For single values, use EmSize
    float width = HelloImGui::EmSize(10);
}
```
:::

::::

:::{note}
`em_to_vec2` and `em_size` are available:

- Directly from `imgui_bundle` (Python, since v1.92.6: `from imgui_bundle import em_to_vec2`)
- In the `hello_imgui` and `immapp` modules (Python)
- In the `HelloImGui` and `ImmApp` namespaces (C++, as `EmToVec2` and `EmSize`)
:::

---

## ImmApp

ImmApp handles add-on initialization automatically via simple boolean flags.

### Quick Start

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import immapp, imgui, implot, imgui_md

def gui():
    imgui_md.render("# Hello with Markdown!")

    if implot.begin_plot("My Plot"):
        implot.plot_line("data", [1, 2, 3, 4], [1, 4, 2, 3])
        implot.end_plot()

# Enable add-ons with simple flags
immapp.run(
    gui,
    window_title="My App",
    window_size=(800, 600),
    with_implot=True,
    with_markdown=True
)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"

void gui() {
    ImGuiMd::Render("# Hello with Markdown!");

    if (ImPlot::BeginPlot("My Plot")) {
        double x[] = {1, 2, 3, 4};
        double y[] = {1, 4, 2, 3};
        ImPlot::PlotLine("data", x, y, 4);
        ImPlot::EndPlot();
    }
}

int main() {
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui;
    runnerParams.windowSize = {800, 600};

    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    addons.withMarkdown = true;

    ImmApp::Run(runnerParams, addons);
    return 0;
}
```
:::

::::

### Available Add-ons

| Flag | Add-on | Description |
|------|--------|-------------|
| `with_implot` | ImPlot | 2D plotting |
| `with_implot3d` | ImPlot3D | 3D plotting |
| `with_markdown` | imgui_md | Markdown rendering |
| `with_node_editor` | imgui-node-editor | Node graphs |
| `with_tex_inspect` | imgui_tex_inspect | Texture inspector |

### Full Configuration

For advanced configuration, use `RunnerParams` (same as Hello ImGui) combined with `AddOnsParams`:

```python
immapp.run(runner_params, addons)  # Python
ImmApp::Run(runnerParams, addons);  // C++
```

---


## Demonstrations

Below are demonstrations from the ImGui Bundle Interactive Manual, showcasing various features of Hello ImGui and ImmApp.

### Docking Demo

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html
```{figure} ../images/demo_docking.webp
:width: 400
Docking Demo - Full-featured ImGui application with Hello ImGui
```
````


[Docking Demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html) shows how to create a full-featured application:

- Complex app layout (with several possible layouts)
- Load additional fonts, possibly colored, and with emojis
- Display a status bar and log window
- Customize the theme
- User settings persistence

The source code is heavily documented and can be used as a template for your own applications.

Source code: [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp)

### ImmApp - Launch an app with addons

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_assets_addons.html
```{figure} ../images/demo_assets_addons.jpg
:width: 400
ImmApp with add-ons: assets, markdown, and ImPlot
```
````

Demonstrates how to use ImmApp with multiple add-ons:
- Load and display assets (images, icons)
- Render markdown content with imgui_md
- Display interactive plots with ImPlot

Source code: [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_assets_addons.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_assets_addons.cpp)

### Custom 3D Background

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_custom_background.html
```{figure} ../images/demo_custom_background.jpg
:width: 400
Custom 3D background with OpenGL shaders
```
````

Demonstrates how to render a custom 3D background using OpenGL:
- Use `runner_params.callbacks.custom_background` callback
- Load and compile shaders
- Adjust uniforms via the GUI

Source code: [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_custom_background.cpp)

### Power Save Mode

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_powersave.html
Demonstrates FPS idling to reduce CPU usage when the app is idle.
````

Hello ImGui automatically reduces FPS when no user interaction is detected. Configure this with:

```python
immapp.run(gui, fps_idle=10.0)  # 10 FPS when idle

# Or dynamically:
runner_params = hello_imgui.get_runner_params()
runner_params.fps_idling.fps_idle = 10.0
runner_params.fps_idling.enable_idling = True
```

* Demo: [Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_powersave.html) |
* Source code: [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_powersave.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_powersave.cpp)



## Advanced - Manual Rendering

For complete control over the render loop (useful for game engines or custom frameworks), use manual rendering instead of `run()`.

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, hello_imgui, immapp

def gui():
    imgui.text("Hello, ImGui Bundle!")

# Setup
runner_params = hello_imgui.RunnerParams()
runner_params.callbacks.show_gui = gui
addons = immapp.AddOnsParams()
addons.with_implot = True
immapp.manual_render.setup_from_runner_params(runner_params, addons)

# Custom render loop
while not hello_imgui.get_runner_params().app_shall_exit:
    immapp.manual_render.render()
    # Do other work here (physics, networking, etc.)

# Cleanup
immapp.manual_render.tear_down()
```
:::

:::{tab-item} C++
```cpp
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"

int main()
{
    // Setup
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = []() {
        ImGui::Text("Hello, ImGui Bundle!");
    };
    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    ImmApp::ManualRender::SetupFromRunnerParams(runnerParams, addons);

    // Custom render loop
    while (!HelloImGui::GetRunnerParams()->appShallExit) {
        ImmApp::ManualRender::Render();
        // Do other work here (physics, networking, etc.)
    }

    // Cleanup
    ImmApp::ManualRender::TearDown();
    return 0;
}
```
:::

::::

**Use cases:** game engine integration, heavy computation between frames, synchronizing with external systems, precise frame timing control.

**Demo:** [Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_custom_background.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_custom_background.cpp)

---

## See Also

- **[Dear ImGui Basics](imgui.md)** – Widget concepts, IDs, common patterns
- **[ImGui Test Engine](test_engine.md)** – Automated testing for ImGui apps
- **[Add-on Libraries](../addons/plotting.md)** – ImPlot, ImmVision, markdown, node editors
