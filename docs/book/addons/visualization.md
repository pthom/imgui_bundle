# Image Visualization

Dear ImGui Bundle includes specialized tools for image inspection and debugging.

## ImmVision - Image Viewer Widget

### Introduction

[ImmVision](https://github.com/pthom/immvision) provides an interactive image viewer widget for ImGui applications, with zoom, pan, pixel inspection, and colormap support. Useful for building image processing tools and debugging computer vision pipelines from within your application.

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

:::{note}
This example uses `cv::Mat` from OpenCV, but **OpenCV is optional**. ImmVision works standalone with its own `ImmVision::ImageBuffer` type. If you don't need OpenCV, replace `cv::Mat` with `ImageBuffer` and use `UseRgbColorOrder()` instead.
:::

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
:link: https://traineq.org/imgui_bundle_explorer/demo_immvision_launcher.html
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

## ImmDebug — Standalone Image Debugger

[Video tutorial on Youtube](https://www.youtube.com/watch?v=ztVBk2FN6_8)

ImmDebug a tool from [ImmVision](https://github.com/pthom/immvision) lets you visually inspect images from any running program — during execution or even after it finishes (post-mortem). Add one-line calls to send images to a standalone viewer with zoom, pan, pixel inspection, and colormaps.

```{figure} ../images/immdebug.jpg
:width: 500
The immdebug viewer displaying images sent from a running program.
```

### Python

Install from PyPI:

```bash
pip install immdebug
```

Start the viewer in a terminal, then send images from your code:

```python
# In a terminal: immdebug-viewer

import numpy as np
import cv2
from immdebug import immdebug

image = cv2.imread("photo.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 100, 200)

immdebug(image, "image")  # inspect the original image
immdebug(gray, "gray")    # inspect different steps of your processing pipeline
immdebug(edges, "edges")  
```

Works with OpenCV, PIL, matplotlib, or any numpy array. See the [immdebug PyPI package](https://pypi.org/project/immdebug/) for full API documentation.

### C++

Drop 4 files from [src/immdebug](https://github.com/pthom/immvision/tree/master/src/immdebug) into your project (only OpenCV required):

```cpp
#include "immdebug/immdebug.h"

cv::Mat image = cv::imread("photo.jpg");
ImmVision::ImmDebug(image, "original");
```

Build and run the C++ viewer separately — see the [immvision README](https://github.com/pthom/immvision) for instructions.

### Features

- **Non-blocking** — just writes a file and returns immediately
- **Cross-language** — C++ and Python clients use the same protocol, both work with either viewer
- **Post-mortem** — images persist in the temp directory for 1 hour; start the viewer after your script finishes
- **Single instance** — re-launching the viewer brings the existing instance to the top




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

- [Demo Window](https://traineq.org/imgui_bundle_explorer/demo_tex_inspect_demo_window.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_tex_inspect/demo_tex_inspect_demo_window.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_tex_inspect/demo_tex_inspect_demo_window.cpp)
- [Simple Example](https://traineq.org/imgui_bundle_explorer/demo_tex_inspect_simple.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_tex_inspect/demo_tex_inspect_simple.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_tex_inspect/demo_tex_inspect_simple.cpp)

### Documented APIs

- **Python:** [imgui_tex_inspect.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_tex_inspect.pyi)
- **C++:** [imgui_tex_inspect.h](https://github.com/pthom/imgui_tex_inspect/blob/main/imgui_tex_inspect.h)
