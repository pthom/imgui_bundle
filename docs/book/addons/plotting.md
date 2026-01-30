# Plotting Libraries

Dear ImGui Bundle includes two powerful plotting libraries for 2D and 3D visualization.

## ImPlot - 2D Plotting

### Introduction
[ImPlot](https://github.com/epezent/implot) adds interactive 2D plots to your GUI: line charts, bar charts, scatter plots, heatmaps, and more. Plots support zooming, panning, and hover inspection.

::::{card}
:link: https://github.com/epezent/implot
```{figure} ../images/battery_implot.jpg
:width: 350
Some of the many plot types supported by ImPlot.
```
::::

**Quick example:**

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import implot, immapp
import numpy as np

x = np.arange(0, 10, 0.1)
y = np.sin(x)

def gui():
    if implot.begin_plot("My Plot"):
        implot.plot_line("sin(x)", x, y)
        implot.end_plot()

immapp.run(gui, with_implot=True)
```

```{tip}
Enable ImPlot by passing `with_implot=True` to `immapp.run()`.
```

:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "implot/implot.h"
#include <cmath>
#include <vector>

std::vector<double> x, y;

void gui() {
    if (ImPlot::BeginPlot("My Plot")) {
        ImPlot::PlotLine("sin(x)", x.data(), y.data(), x.size());
        ImPlot::EndPlot();
    }
}

int main() {
    for (double i = 0; i < 10; i += 0.1) {
        x.push_back(i);
        y.push_back(std::sin(i));
    }
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = gui;
    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    ImmApp::Run(runner_params, addons);
    return 0;
}
```

```{tip}
In C++, enable ImPlot by setting `withImplot = true` in `ImmApp::AddOnsParams`.
```
:::

::::

### Full Demo

::::{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_implot.html
```{figure} ../images/implot_demo.webp
:width: 350
ImPlot demo showcasing various plot types and features.
```
::::

- [Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_implot.html)

- Python demo code: [implot_demo.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot/implot_demo.py)
- C++ demo code: [implot_demo.cpp](https://github.com/epezent/implot/blob/master/implot_demo.cpp)

### Documented APIs
- Python API reference: [implot/\_\_init\_\_.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot/__init__.pyi)
- C++ API reference: [implot.h](https://github.com/epezent/implot/blob/master/implot.h)


## ImPlot3D - 3D Plotting

### Introduction

[ImPlot3D](https://github.com/brenocq/implot3d) extends ImPlot with 3D visualization capabilities. Create interactive 3D line plots, scatter plots, surface plots, and more with rotation, zoom, and pan controls.

::::{card}
:link: https://github.com/brenocq/implot3d
```{figure} ../images/battery_implot3d.jpg
:width: 350
Some of the plot types supported by ImPlot3D.
```
::::


**Quick example:**

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import implot3d, immapp, hello_imgui
import numpy as np

t = np.linspace(0, 10, 100)
x, y, z = np.cos(t), np.sin(t), t

def gui():
    if implot3d.begin_plot("3D Helix", hello_imgui.em_to_vec2(30, 30)):
        implot3d.setup_axes("X", "Y", "Z")
        implot3d.plot_line("helix", x, y, z)
        implot3d.end_plot()

immapp.run(gui, with_implot3d=True)
```

```{tip}
Enable ImPlot3D by passing `with_implot3d=True` to `immapp.run()`.
```

:::



:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "implot3d/implot3d.h"
#include <vector>
#include <cmath>

std::vector<double> x, y, z;

void gui() {
    if (ImPlot3D::BeginPlot("3D Helix")) {
        ImPlot3D::SetupAxes("X", "Y", "Z");
        ImPlot3D::PlotLine("helix", x.data(), y.data(), z.data(), x.size());
        ImPlot3D::EndPlot();
    }
}

int main() {
    for (double t = 0; t < 10; t += 0.1) {
        x.push_back(std::cos(t));
        y.push_back(std::sin(t));
        z.push_back(t);
    }

    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = gui;
    ImmApp::AddOnsParams addons;
    addons.withImplot3d = true;
    ImmApp::Run(runner_params, addons);
    return 0;
}
```

```{tip}
In C++, enable ImPlot3D by setting `withImplot3d = true` in `ImmApp::AddOnsParams`.
```

:::


::::


### Full Demo

The full demo for ImPlot3D is available online together with ImPlot's full demo.

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_implot.html)

- Python demo code: [implot3d_demo.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot3d/implot3d_demo.py)
- C++ demo code: [implot3d_demo.cpp](https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp)

### Documented APIs

- Python API reference: [implot3d/\_\_init\_\_.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot3d/__init__.pyi)
- C++ API reference: [implot3d.h](https://github.com/brenocq/implot3d/blob/main/implot3d.h)
