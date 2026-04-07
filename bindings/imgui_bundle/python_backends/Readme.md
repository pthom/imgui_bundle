# ImGui Bundle - Python backends

In this folder, you can find examples where the backend is programmed via python.
You can use them if you want to control the full app cycle (i.e. not using ImmApp or HelloImGui).

## Contents
```
python_backends/             # Backends implemented in pure python
    +-- base_backend.py
    +-- glfw_backend.py      # Those files are inspired from pyimgui bindings
    +-- opengl_backend.py    # (see https://github.com/pyimgui/pyimgui)
    +-- pyglet_backend.py
    +-- sdl2_backend.py
    +-- sdl3_backend.py
    +-- __init__.py
    +-- Readme.md
    +-- LICENSE_pyimgui.txt
    +-- examples/
        +-- example_python_backend_glfw3.py   # An example app with glfw
        +-- example_python_backend_pyglet.py  # An example app with pyglet
        +-- example_python_backend_sdl2.py    # An example app with sdl2
        +-- example_python_backend_sdl3.py    # An example app with sdl3
```

## Notes

* Those files are inspired from [pyimgui](https://github.com/pyimgui/pyimgui) bindings:
  for example, the [python glfw backend](glfw_backend.py) is adapted from [pyimgui's glfw integration](https://github.com/pyimgui/pyimgui/blob/master/imgui/integrations/glfw.py)
* This is largely a work in progress, and thus incomplete. At the moment, only glfw, sdl2, sdl3 and pyglet are implemented.
* Key binding needs to be improved (support for modifiers like Ctrl-Shift, etc.)

## Using `imgui_md` (Markdown) without HelloImGui

`imgui_md` can be hosted inside a pure-python backend with no `HelloImGui::Run()`
loop. Standard markdown features (text, headings, code blocks, tables, links)
work everywhere; image and LaTeX-math rendering additionally need GPU texture
uploads, which are supported only on **OpenGL3** in the standalone path.

`imgui_md.initialize_markdown()` automatically initializes HelloImGui's GLAD
function loader if you are not inside `HelloImGui::Run()`, so user code does
not need to call `hello_imgui.init_gl_loader()` itself.
`imgui_md.de_initialize_markdown()` similarly clears the asset image cache.

A complete working example lives at
[`../demos_python/sandbox/sandbox_md_without_hello_imgui.py`](../demos_python/sandbox/sandbox_md_without_hello_imgui.py)
(GLFW + PyOpenGL). The C++ counterpart is at
`bindings/imgui_bundle/demos_cpp/sandbox/sandbox_md_without_hello_imgui.cpp`.

### Limitations
* Standalone use is **OpenGL3 only**. Metal, Vulkan, DirectX11/12 require
  device handles that HelloImGui's runner would normally create — they are
  not exposed for standalone injection.
* Pyodide is not supported in the pure-backend mode (no PyOpenGL, no native glfw).
