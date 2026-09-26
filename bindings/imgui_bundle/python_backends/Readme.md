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

## Markdown with a pure Python backend

`rich_md` works with these backends, with all its features: text, tables, code blocks,
links, local and URL images, LaTeX math.

`rich_md.create_context()` is the only setup needed (the fonts load at the first
render), and `rich_md.destroy_context()` frees what markdown created: its textures,
the pending downloads and the LaTeX engine.
Each example of [examples/](examples/) shows an image, a formula and a code block, including
the one that uses wgpu-py's backend (WebGPU).

### Limitations
* Images and formulas are Dear ImGui textures that the backend creates itself: they need a
  backend that supports Dear ImGui's texture protocol (`ImGuiBackendFlags_RendererHasTextures`,
  Dear ImGui 1.92+). All the backends of this folder do.
* Pyodide is not supported in the pure-backend mode (no PyOpenGL, no native glfw).
