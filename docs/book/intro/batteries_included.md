# Bundled Libraries

# Full list of included libraries

Dear ImGui Bundle includes the following libraries, which are available in C++ _and_ in Python:

* <a href="https://github.com/ocornut/imgui">Dear ImGui</a> : Bloat-free Graphical User interface with minimal dependencies
* <a href="https://github.com/ocornut/imgui_test_engine">ImGui Test Engine</a> : Dear ImGui Tests & Automation Engine
* <a href="https://github.com/pthom/hello_imgui">Hello ImGui</a> : cross-platform Gui apps with the simplicity of a "Hello World" app
* <a href="https://github.com/epezent/implot">ImPlot</a> : Immediate Mode Plotting
* <a href="https://github.com/brenocq/implot3d">ImPlot3D</a> : Immediate Mode 3D Plotting
* <a href="https://github.com/CedricGuillemet/ImGuizmo">ImGuizmo</a> : Immediate mode 3D gizmo for scene editing
* <a href="https://github.com/BalazsJako/ImGuiColorTextEdit">ImGuiColorTextEdit</a> : Colorizing text editor for ImGui
* <a href="https://github.com/thedmd/imgui-node-editor">imgui-node-editor</a> : Node Editor built using Dear ImGui
* <a href="https://github.com/mekhontsev/imgui_md">imgui_md</a> : Markdown renderer for Dear ImGui using MD4C parser
* <a href="https://github.com/pthom/immvision">ImmVision</a> : Immediate image debugger and insights
* <a href="https://github.com/memononen/nanovg">NanoVG</a> : Antialiased 2D vector drawing library on top of OpenGL
* <a href="https://github.com/andyborrell/imgui_tex_inspect">imgui_tex_inspect</a> : A texture inspector tool for Dear ImGui
* <a href="https://github.com/pthom/ImFileDialog">ImFileDialog</a> : A file dialog library for Dear ImGui
* <a href="https://github.com/samhocevar/portable-file-dialogs">portable-file-dialogs</a> : _OS native_ file dialogs library (C++11, single-header)
* <a href="https://github.com/altschuler/imgui-knobs">imgui-knobs</a> : Knobs widgets for ImGui
* <a href="https://github.com/dalerank/imspinner">imspinner</a> : Set of nice spinners for imgui
* <a href="https://github.com/cmdwtf/imgui_toggle">imgui_toggle</a> : A toggle switch widget for Dear ImGui
* <a href="https://github.com/aiekick/ImCoolBar">ImCoolBar</a> : A Cool bar for Dear ImGui
* <a href="https://github.com/hnOsmium0001/imgui-command-palette">imgui-command-palette</a> : A Sublime Text or VSCode style command palette in ImGui

A big thank you to their authors for their awesome work!

# Key Features

## Works everywhere

* **Cross-platform in C++ and Python:** Works on Windows, Linux, macOS, iOS, Android, and WebAssembly!

* **Web ready**: Develop full web applications, in C++ via Emscripten; or in Python thanks to ImGui Bundle's integration within _Pyodide_

## First class support for Python

* **Python Bindings:** Using Dear ImGui Bundle in Python is extremely easy and productive.

* **Beautifully documented Python bindings and stubs:** The Python bindings stubs reflect the C++ API and documentation, serving as a reference and aiding autocompletion in your IDE. See for example the [stubs for imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi), and [for hello_imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi).

* Use it to create **standalone apps** (on Windows, macOS, and Linux), or to add **interactive UIs to your notebooks**. Deploy your apps **on the web** with ease, using [Pyodide](https://pyodide.org/en/stable/).

## Easy to use & well documented

* The Immediate Mode GUI (IMGUI) paradigm is simple and powerful, letting you focus on the creative aspects of your projects.

* **Easy to use, yet very powerful:** Start your first app in 3 lines.

* **Interactive Demos and Documentation:** Quickly get started with our interactive manual and demos that showcase the capabilities of the pack. Read or copy-paste the source code (Python and C++) directly from the interactive manual!


## Always up-to-date

* **Always up-to-date:** The libraries are always very close to the latest version of Dear ImGui. This is also true for Python developers, since the bindings are automatically generated.

* **Fast:** Rendering is done via OpenGL (or any other renderer you choose), through native code.

