# Tools

Dear ImGui Bundle includes specialized tools for 3D editing and visual programming.

## ImGuizmo - 3D Gizmos

### Introduction

[ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) provides immediate mode 3D gizmos for scene editing: translate, rotate, and scale manipulators similar to those found in 3D modeling software.

::::{card}
:link: https://github.com/CedricGuillemet/ImGuizmo
```{figure} ../images/demo_gizmo.jpg
:width: 350
ImGuizmo: 3D gizmos for translation, rotation, and scale.
```
::::

**Features:**
- Translation, rotation, scale gizmos
- Local and world coordinate modes
- View cube for camera orientation
- Snap to grid support

:::{note}
**Python:** ImGuizmo requires PyGLM for matrix operations: `pip install PyGLM`
:::

### Full Demo

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_gizmo.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imguizmo/demo_gizmo.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_imguizmo/demo_gizmo.cpp)

### Documented APIs

- **Python:** [imguizmo.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imguizmo.pyi)
- **C++:** [ImGuizmo.h](https://github.com/CedricGuillemet/ImGuizmo/blob/master/ImGuizmo.h)


## imgui-node-editor - Visual Node Graphs

### Introduction

[imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a node editor built using Dear ImGui. Create visual programming interfaces, data flow graphs, etc.

::::{card}
:link: https://github.com/thedmd/imgui-node-editor
```{figure} ../images/demo_node_editor.jpg
:width: 350
imgui-node-editor: visual node graphs for data flow and shader editing.
```
::::


::::{card}
:link: https://pthom.github.io/fiatlight_doc
```{figure} https://pthom.github.io/fiatlight_doc/flgt/_static/images/meme.jpg
:width: 350
Note: [Fiatlight](https://pthom.github.io/fiatlight_doc), a library built on top of Dear ImGui Bundle uses imgui-node-editor intensively. It provides an automatic UI generation for functions and structured data.
```
::::


:::{tip}
Enable the node editor by passing `with_node_editor=True` (Python) or `addons.withNodeEditor = true` (C++).
:::


### Full Demo

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_node_editor_launcher.html) - A launcher with several demos:

| Demo | Python | C++ |
|------|--------|-----|
| Basic Demo | [demo_node_editor_basic.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_node_editor/demo_node_editor_basic.py) | [demo_node_editor_basic.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_node_editor/demo_node_editor_basic.cpp) |
| Romeo and Juliet | [demo_romeo_and_juliet.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_node_editor/demo_romeo_and_juliet.py) | [demo_romeo_and_juliet.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_node_editor/demo_romeo_and_juliet.cpp) |

### Documented APIs

- **Python:** [imgui_node_editor.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_node_editor.pyi)
- **C++:** [imgui_node_editor.h](https://github.com/pthom/imgui-node-editor/blob/imgui_bundle/imgui_node_editor.h)





## NanoVG - 2D Vector Graphics

### Introduction

[NanoVG](https://github.com/memononen/nanovg) is an antialiased 2D vector drawing library on top of OpenGL. Use it for custom drawing, charts, diagrams, or any vector graphics needs.

::::{card}
:link: https://github.com/memononen/nanovg
```{figure} ../images/nanovg_full_demo.jpg
:width: 350
NanoVG: antialiased 2D vector graphics with paths, shapes, and text.
```
::::

**Features:**
- Antialiased rendering
- Paths, shapes, gradients
- Text rendering with font support
- Scissoring and clipping

### Full Demo

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_nanovg_launcher.html) - A launcher with two demos:

| Demo        | Python | C++ |
|-------------|--------|-----|
| Full Demo   | [demo_nanovg_full.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_nanovg/demo_nanovg_full.py) | [demo_nanovg_full.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_full.cpp) |
| Simple Demo | [demo_nanovg_heart.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_nanovg/demo_nanovg_heart.py) | [demo_nanovg_heart.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_heart.cpp) |

### Documented APIs

- **Python:** [nanovg.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/nanovg.pyi)
- **C++:** [nanovg.h](https://github.com/memononen/nanovg/blob/master/src/nanovg.h)
