# Examples and Gallery

## Examples in the interactive manual

Below are simple example applications available in the [Dear ImGui Bundle interactive manual](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html), in the "Demo Apps" tab.

````{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html
```{figure} ../images/bundle_apps.jpg
:alt: A screenshot of ImGui Bundle interactive manual, showing how to open example apps and show their source code
:width: 500px
:align: left
Inside the manual, click the "Demo Apps" tab, select a demo, run it and look at its source code.
```
````

### Complex layouts with docking windows

```{figure} ../images/demo_docking.jpg
:alt: Complex docking layout
:width: 300px
:align: left
A complex GUI app with a docking layout, and several possible arrangements
```

[Run this demo in your browser](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html)


This demonstration showcases how to:

- set up a complex docking layouts (with several possible layouts)
- use the status bar
- use default menus (App and view menu), and how to customize them
- display a log window
- load additional fonts
- use a specific application state (instead of using static variables)
- save some additional user settings within imgui ini file

Its source code is heavily documented and should be self-explanatory.
* [C++ source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp)
* [Python source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py)

---

### Custom 3D Background

```{figure} ../images/demo_custom_background.jpg
:alt: Custom 3D Background
:width: 300px
:align: left
A custom 3D scene rendered in the background of an ImGui application
```

[Run this demo in your browser](https://traineq.org/ImGuiBundle/emscripten/bin/demo_custom_background.html)


This demonstration showcases how to:

- Display a 3D scene in the background via the callback `runnerParams.callbacks.CustomBackground`
- Load and compile a shader
- Adjust uniforms in the GUI

Its source code is heavily documented and should be self-explanatory.

* [C++ source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_custom_background.cpp)
* [Python source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py)

---

### Display & analyze images with ImmVision

```{figure} ../images/demo_immvision_process_1.jpg
:alt: Immvision in action
:width: 300px
:align: left
ImmVision in action
```

```{figure} ../images/demo_immvision_process_2.jpg
:alt: Immvision in action
:width: 300px
:align: left
Zooming on the images (with the mouse wheel) to display pixel values
```

[Run this demo in your browser](https://traineq.org/ImGuiBundle/emscripten/bin/demo_immvision_process.html)

[ImmVision](https://github.com/pthom/immvision) is an immediate image debugger which can display multiple kinds of images (RGB, RGBA, float, etc.), zoom to examine precise pixel values, display float images with a versatile colormap, etc.

This demonstration showcases how to:

- display two versions of an image, before after an image processing pipeline
- zoom on specific ROI of those images to see pixel values
- play with the parameter of the image processing pipeline

Its source code is heavily documented and should be self-explanatory.

* [C++ source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immvision/demo_immvision_process.cpp)
* [Python source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immvision/demo_immvision_process.py)


---

### Test & Automation with ImGui Test Engine

```{figure} ../images/demo_testengine.jpg
:alt: ImmGui Test Engine in action
:width: 300px
:align: left
```


[Run this demo in your browser](https://traineq.org/ImGuiBundle/emscripten/bin/demo_testengine.html)

[ImGui Test Engine](https://github.com/ocornut/imgui_test_engine) is a Tests & Automation Engine for Dear ImGui.

This demo source code is heavily documented and should be self-explanatory. It shows how to:

* enable ImGui Test Engine via RunnerParams.use_imgui_test_engine
* define a callback where the tests are registered (runner_params.callbacks.register_tests)
* create tests, and:
    * automate actions using "named references" (see [Named References](https://github.com/ocornut/imgui_test_engine/wiki/Named-References))
    * display an optional custom GUI for a test
* manipulate custom variables
* check that simulated actions do modify those variables

```{note}
See [Dear ImGui Test Engine License](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt). (TL;DR: free for individuals, educational, open-source and small businesses uses. Paid for larger businesses)
```

* [C++ source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_testengine.cpp)
* [Python source code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_testengine.py)


## Example Applications Gallery

More examples in the [Gallery](https://github.com/pthom/imgui_bundle/discussions/107). Add yours!

### 4K4D

A research project aimed for CVPR 2024, using python bindings (ImGui Bundle).
```
@inproceedings{xu20244k4d,
  title={4K4D: Real-Time 4D View Synthesis at 4K Resolution},
  author={Xu, Zhen and Peng, Sida and Lin, Haotong and He, Guangzhao and Sun, Jiaming and Shen, Yujun and Bao, Hujun and Zhou, Xiaowei},
  booktitle={CVPR},
  year={2024}
}
```

[ 4K4D: Real-Time 4D View Synthesis at 4K Resolution](https://zju3dv.github.io/4k4d/)

```{figure} ../images/4k4d.jpg
:alt: 4K4D screenshot
:width: 600px
:align: left
A volumetric video, showing an ImGui interface to control the rendering parameters.
```


### HDRview

[HDRview](https://github.com/wkjarosz/hdrview) is a research-oriented image viewer with an emphasis on examining and comparing high-dynamic range (HDR) images.

It is developed by Wojciech Jarosz and is built using Hello ImGui (which is included in Dear ImGui Bundle), in C++.
It runs on Windows, Linux, macOS, iOS, and on the web via emscripten!

```{figure} https://github.com/wkjarosz/hdrview/raw/master/resources/screenshot-ipad.jpg
:alt: HDRview screenshot
:width: 600px
:align: left
HDRview running on an iPad as a webapp, viewing a luminance-chroma EXR image stored using XYZ primaries with chroma subsampling.
```

Access HDRview online: [https://wkjarosz.github.io/hdrview/](
https://wkjarosz.github.io/hdrview/)

