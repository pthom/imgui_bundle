# Dear ImGui Bundle

> Dear ImGui Bundle: an extensive set of ready-to-use widgets and libraries, based on ImGui. Start your first app in 5 lines of code, or less.
>
> Whether you prefer Python or C++, this pack has you covered, with the same ease in both languages.

<a href="https://github.com/pthom/imgui_bundle/"><img src="https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_view_sources.png" alt="sources" width="100"></a>
<a href="https://pthom.github.io/imgui_bundle"><img src="https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_view_docs.png" alt="doc" width="81"></a>
<a href="https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html"><img src="https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_interactive_manual.png" alt="manual" width="137"></a>


## Key Features

* **Python Bindings:** Using Dear ImGui Bundle in Python is extremely easy. Here is a beginner-friendly introduction: https://github.com/pthom/imgui_bundle/blob/main/docs/docs_md/imgui_python_intro.md[Immediate Mode GUI with Python and Dear ImGui Bundle]

* **Cross-platform in C++ and Python:** Works on Windows, Linux, macOS, iOS, Android, and WebAssembly!

* **Easy to use, yet very powerful:** Start your first app in 3 lines. The Immediate Mode GUI (IMGUI) paradigm is simple and powerful, letting you focus on the creative aspects of your projects.

* **A lot of widgets and libraries:** All of Dear ImGui along with a suite of additional libraries for plotting, node editing, markdown rendering, and much more.

* **Web ready**: Develop full web applications, in C++ via Emscripten; or in Python thanks to ImGui Bundle's integration within _Pyodide_

* **Always up-to-date:** The libraries are always very close to the latest version of Dear ImGui. This is also true for Python developers, since the bindings are automatically generated.

* **Interactive Demos and Documentation:** Quickly get started with our interactive manual and demos that showcase the capabilities of the pack. Read or copy-paste the source code (Python and C++) directly from the interactive manual!

* **Fast:** Rendering is done via OpenGL (or any other renderer you choose), through native code.

* **Beautifully documented Python bindings and stubs:** The Python bindings stubs reflect the C++ API and documentation, serving as a reference and aiding autocompletion in your IDE. See for example the https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/$$__init__$$.pyi[stubs for imgui], and https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi[for hello_imgui] (which complete the https://pthom.github.io/hello_imgui/book/intro.html[hello_imgui manual]).


For a detailed look at each feature and more information, explore the sections listed in the Table of Contents.

## Batteries Included

Dear ImGui Bundle includes the following libraries, which are available in C++ _and_ in Python:

| Library | Screenshot |
|---|---|
| [Dear ImGui](https://github.com/ocornut/imgui) : Bloat-free Graphical User interface with minimal dependencies | ![demo widgets imgui](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_imgui.jpg) |
| [ImGui Test Engine](https://github.com/ocornut/imgui_test_engine) : Dear ImGui Tests & Automation Engine | ![demo testengine](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_testengine.jpg) |
| [Hello ImGui](https://github.com/pthom/hello_imgui) : cross-platform Gui apps with the simplicity of a "Hello World" app | ![docking](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_docking.jpg) <br/> ![custom background](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_custom_background.jpg) |
| [ImPlot](https://github.com/epezent/implot) : Immediate Mode Plotting | ![implot](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/battery_implot.jpg) |
| [ImPlot3D](https://github.com/brenocq/implot3d) : Immediate Mode 3D Plotting | ![implot3d](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/battery_implot3d.jpg) |
| [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) : Immediate mode 3D gizmo for scene editing | ![gizmo](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_gizmo.jpg) |
| [ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit) : Colorizing text editor for ImGui | ![editor](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_editor.jpg) |
| [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) : Node Editor built using Dear ImGui | ![node editor](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_node_editor.jpg) |
| [imgui_md](https://github.com/mekhontsev/imgui_md) : Markdown renderer for Dear ImGui using MD4C parser | ![markdown renderer](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_md.jpg) |
| [ImmVision](https://github.com/pthom/immvision) : Immediate image debugger and insights | ![immvision 1](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_immvision_process_1.jpg) <br/> ![immvision 2](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_immvision_process_2.jpg) |
| [NanoVG](https://github.com/memononen/nanovg) : Antialiased 2D vector drawing library on top of OpenGL | ![nanovg demo](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/nanovg_full_demo.jpg) |
| [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect) : A texture inspector tool for Dear ImGui | ![texture inspector](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_imgui_tex_inspector.jpg) |
| [ImFileDialog](https://github.com/pthom/ImFileDialog) : A file dialog library for Dear ImGui | ![imfiledialog](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_imfiledialog.jpg) |
| [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) : _OS native_ file dialogs library (C++11, single-header) | ![portable file dialogs](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_portablefiledialogs.jpg) |
| [imgui-knobs](https://github.com/altschuler/imgui-knobs) : Knobs widgets for ImGui | ![knobs](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_knobs.jpg) |
| [imspinner](https://github.com/dalerank/imspinner) : Set of nice spinners for imgui | ![spinners](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_spinners.jpg) |
| [imgui_toggle](https://github.com/cmdwtf/imgui_toggle) : A toggle switch widget for Dear ImGui | ![toggle](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_toggle.jpg) |
| [ImCoolBar](https://github.com/aiekick/ImCoolBar) : A Cool bar for Dear ImGui | ![coolbar](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_coolbar.jpg) |
| [imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette) : A Sublime Text or VSCode style command palette in ImGui | ![command palette](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_command_palette.jpg) |



A big thank you to their authors for their awesome work!


## Manuals and Examples

**Interactive Manual**

Click on the animated demonstration below to launch the fully interactive manual.

.Dear ImGui Bundle interactive manual (in C++, via Emscripten)
[#truc,link={url-demo-imgui-bundle}]
image::https://traineq.org/imgui_bundle_doc/demo_bundle8.gif[Demo, 700]


**Online playground in Pure Python (via Pyodide)**

Since ImGui Bundle is available in Python and Pyodide, an https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/[online playground] will enable you to run and edit various ImGui applications in the browser without any setup.

.ImGui Bundle online playground (in Python, via Pyodide)
[#playground,link=https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/]
image::https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/playground.jpg[Playground, 500]

See https://code-ballads.net/dear-imgui-bundle-build-real-time-python-web-applications-with-zero-fuss/[this page] for more information about availability of ImGui Bundle in Pyodide.


**Full manual (PDF)**

View or download the https://raw.githubusercontent.com/pthom/imgui_related_docs/refs/heads/main/manuals/imgui_bundle_manual.pdf[full pdf]  for this manual.

You may feed it into a LLM such as ChatGPT, so that it can help you when using ImGui bundle.


## Hello World

_A hello world example with Dear ImGui Bundle_

image:https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_hello.jpg[]

```python
from imgui_bundle import imgui, immapp
immapp.run(gui_function=lambda: imgui.text("Hello, world!"))
```

_For {cpp} developers_
```cpp
#include "immapp/immapp.h"
#include "imgui.h"
int main() {   ImmApp::Run([] {   ImGui::Text("Hello, world!");   });  }
```



