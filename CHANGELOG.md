# v0.7.0 (work in progress)
* Added support for [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo)
  * all components available in C++ (gizmo, curve, graph, sequencer, etc.)
  * added [ImGuizmoPure](external/ImGuizmo/ImGuizmoPure): C++ wrappers around existing api with clearly marked inputs and outputs
  * for python: ported pure API
  * added set of twin demos showing usage [with C++](bindings/imgui_bundle/demos_cpp/demos_imguizmo) and [with python](bindings/imgui_bundle/demos/demos_imguizmo). A good example showing how to port features between C++ and python.
  * the following items could not be ported to python (making a pure wrapper failed): ImGradient, GraphEditor, Sequencer
* Added support for [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect), a texture inspector.
  * Added support for codeless init of imgui_tex_inspect when using ImGuiBundle runner (future ImmApp), thanks to AddOnParams::withTexInspect
* 6ef5df64: added imgui.set_io_ini_filename() & imgui.set_io_log_filename()
  Manual binding for ImGuiIO::IniFilename (naked const char* pointer)
* 778aabf3: Added imgui_bundle.em_size and visible_font_size():
In order to scale your widgets properly on all platforms, use multiples of this size.
(on MacOS with retina FontGlobalScale can be equal to 2)
(EmSize is an alias for VisibleFontSize)
* f6ae2072: generate named constructors if there is *no* user defined constructors
* 19ca013a: remove ImGui prefix from classes and enums => lots of API changes
* f9210578: ImPlot bindings: remove prefix ImPlot from classes and enums
* hardened stub typings with mypy
* imgui.backends: replace open_gl3 by opengl3
* immvision module now stable
* Lots of work on the CI and wheel generation


# v0.6.6
#### Added Immvision (image debugger and analyzer utility)
immvision will be compiled if OpenCV is available.
immvision is not available by default on the pip bindings.

To add them, compile from source [after having installed conan](https://github.com/pthom/imgui_bundle/blob/v0.6.6/external/immvision/find_opencv.cmake#L5)

#### Added theming
* [Demo](https://www.youtube.com/watch?v=Hhartw0cUjg)
* [API](https://github.com/pthom/imgui_bundle/blob/v0.6.6/bindings/imgui_bundle/hello_imgui.pyi#L375)
* Default theme is now a variation on Darcula

#### Improve ImGui & Glfw,  low level integration
* glfw is now linked as a dynamic library
* support [any glfw callback](https://github.com/pthom/imgui_bundle/blob/v0.6.6/bindings/imgui_bundle/demos/demo_imgui_bundle.py#L119)
* added low level binding for [imgui backends](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_backends.pyi) glfw and OpenGl3
* imgui apps can now be written from scratch : as an example, ported [imgui/examples/example_glfw_opengl3/main.cpp](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) to python [imgui_example_glfw_opengl3.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos/imgui_example_glfw_opengl3.py)

**Full Changelog**: https://github.com/pthom/imgui_bundle/compare/v0.6.5...v0.6.6

# v0.6.5
Lots of additions
* Fine tune window geometry:
  * save & restore window position & size
  * support for full screen
  * auto size window from its inner widgets
  * handle high dpi (especially on windows)
* Crisp fonts on MacOS
* Backend support: can switch between sdl and glfw
* Added python support to ImGuiColorTextEdit
* Powersave: reduce app fps when idle
* Add toggle switches from https://github.com/cmdwtf/imgui_toggle.git
* Support for jupyter notebook (with inline screenshots), via `imgui_bundle.run_nb`
  (see https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos/notebooks/demo_notebook.ipynb)

**Full Changelog**: https://github.com/pthom/imgui_bundle/compare/v0.6.4...v0.6.5

