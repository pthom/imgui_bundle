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
    +-- sdl_backend.py
    +-- __init__.py
    +-- Readme.md
    +-- LICENSE_pyimgui.txt
    +-- examples/
        +-- example_python_backend_glfw3.py   # An example app with glfw
        +-- example_python_backend_pyglet.py  # An example app with pyglet
        +-- example_python_backend_sdl2.py    # An example app with sdl2
```

## Notes

* Those files are inspired from [pyimgui](https://github.com/pyimgui/pyimgui) bindings:
  for example, the [python glfw backend](glfw_backend.py) is adapted from [pyimgui's glfw integration](https://github.com/pyimgui/pyimgui/blob/master/imgui/integrations/glfw.py)
* This is largely a work in progress, and thus incomplete. At the moment, only glfw, sdl2 and pyglet are implemented.
* Key binding needs to be improved (support for modifiers like Ctrl-Shift, etc.)
