# Quick Start

Get up and running with ImGui Bundle in just a few minutes.

## 1. Installation

::::{tab-set}

:::{tab-item} Python
The easiest way to install ImGui Bundle for Python is via pip:

```bash
# Minimal install
pip install imgui-bundle

# Or to get all optional features (recommended for full cookbook support)
pip install "imgui-bundle[full]"
```

*Binary wheels are available for Windows, macOS, and Linux.*
:::

:::{tab-item} C++
For C++, we recommend using the [starter template](https://github.com/pthom/imgui_bundle_template) or `FetchContent` in your `CMakeLists.txt`.

**Using FetchContent:**

```cmake
include(FetchContent)
FetchContent_Declare(
    imgui_bundle
    GIT_REPOSITORY https://github.com/pthom/imgui_bundle.git
    GIT_TAG main
)
FetchContent_MakeAvailable(imgui_bundle)

# Create your app
imgui_bundle_add_app(my_app main.cpp)
```
:::

::::

## 2. Hello, World!

Here is the simplest possible application using the `ImmApp` runner.

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Hello, world!")

immapp.run(
    gui_function=gui,
    window_title="Hello!",
    window_size_auto=True
)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui.h"

void Gui() {
    ImGui::Text("Hello, world!");
}

int main(int, char **) {
    ImmApp::Run(Gui, "Hello!", true);
    return 0;
}
```
:::

::::

## 3. Interactive Demos

ImGui Bundle comes with an extensive interactive manual. You can run it locally after installation:

**Python:**
```bash
demo_imgui_bundle
```

**Online:**
You can also [run the interactive manual in your browser](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html).
