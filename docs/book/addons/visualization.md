# Image Visualization

Dear ImGui Bundle includes specialized tools for image inspection and debugging.

## ImmVision - Image Debugger

### Introduction

[ImmVision](https://github.com/pthom/immvision) provides interactive image display with zoom, pan, pixel inspection, and colormap support. Particularly useful for debugging computer vision pipelines.

::::{card}
:link: https://github.com/pthom/immvision
```{figure} ../images/demo_immvision.webp
:width: 350
ImmVision: interactive image display with zoom, pan, and pixel inspection.
```
::::

**Quick example:**

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import immvision, immapp
import numpy as np

immvision.use_rgb_color_order()

image = np.zeros((100, 100, 3), dtype=np.uint8)
params = immvision.ImageParams()

def gui():
    # Simple display
    immvision.image_display("Simple", image)

    # Full interactivity (zoom, pan, pixel inspection)
    immvision.image("Interactive", image, params)

immapp.run(gui)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include <opencv2/core.hpp>

cv::Mat image;
ImmVision::ImageParams params;

void gui() {
    // Simple display
    ImmVision::ImageDisplay("Simple", image);

    // Full interactivity
    ImmVision::Image("Interactive", image, &params);
}

int main() {
    ImmVision::UseBgrColorOrder();
    image = cv::Mat::zeros(100, 100, CV_8UC3);
    ImmApp::Run(gui);
    return 0;
}
```
:::

::::

**Features:**
- Zoom in/out using the mouse wheel
- Pixel values displayed at high zoom levels
- Pan by dragging with left mouse button
- Settings panel for colormap, channels, etc.

:::{tip} 
Call `immvision.use_rgb_color_order()` once at startup for RGB images. Call `use_bgr_color_order()` for OpenCV BGR images.
:::

### Full Demo

::::{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_immvision_launcher.html
```{figure} ../images/demo_immvision_process_1.jpg
:width: 350
Click the image to run a launcher that includes several examples.
```
::::


| Demo | Python | C++ |
|------|--------|-----|
| Display Image | [demo_immvision_display.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immvision/demo_immvision_display.py) | [demo_immvision_display.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immvision/demo_immvision_display.cpp) |
| Link Images Zoom/Pan | [demo_immvision_link.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immvision/demo_immvision_link.py) | [demo_immvision_link.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immvision/demo_immvision_link.cpp) |
| Image Inspector | [demo_immvision_inspector.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immvision/demo_immvision_inspector.py) | [demo_immvision_inspector.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immvision/demo_immvision_inspector.cpp) |
| Image Processing | [demo_immvision_process.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immvision/demo_immvision_process.py) | [demo_immvision_process.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immvision/demo_immvision_process.cpp) |

### Documented APIs

- **Python:** [immvision.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/immvision.pyi)
- **C++:** [image.h](https://github.com/pthom/immvision/blob/master/src/immvision/image.h) | [inspector.h](https://github.com/pthom/immvision/blob/master/src/immvision/inspector.h)


## imgui_tex_inspect - Texture Inspector

### Introduction

[imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect) is a texture inspector tool for debugging GPU textures. It displays textures with zoom, pan, and detailed pixel information.

::::{card}
:link: https://github.com/andyborrell/imgui_tex_inspect
```{figure} ../images/demo_imgui_tex_inspector.jpg
:width: 350
imgui_tex_inspect: GPU texture inspection with zoom and pixel details.
```
::::

:::{tip}
Enable imgui_tex_inspect by passing `with_tex_inspect=True` (Python) or `addons.withTexInspect = true` (C++).
:::

### Full Demo

- [Demo Window](https://traineq.org/ImGuiBundle/emscripten/bin/demo_tex_inspect_demo_window.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_tex_inspect/demo_tex_inspect_demo_window.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_tex_inspect/demo_tex_inspect_demo_window.cpp)
- [Simple Example](https://traineq.org/ImGuiBundle/emscripten/bin/demo_tex_inspect_simple.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_tex_inspect/demo_tex_inspect_simple.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_tex_inspect/demo_tex_inspect_simple.cpp)

### Documented APIs

- **Python:** [imgui_tex_inspect.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_tex_inspect.pyi)
- **C++:** [imgui_tex_inspect.h](https://github.com/pthom/imgui_tex_inspect/blob/main/imgui_tex_inspect.h)
