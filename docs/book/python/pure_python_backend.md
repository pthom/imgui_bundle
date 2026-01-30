# Pure Python Backends

Pure Python backends in ImGui Bundle let you use ImGui with Python-only windowing and rendering libraries instead of the default C++ GLFW+OpenGL backend. This gives you full control over the application loop but requires manual setup of windowing, input handling, and rendering.

**Key Differences**

* No Hello ImGui features: Pure Python backends don't provide DPI handling, themes, asset management, or other Hello ImGui conveniences
* Manual setup required: You must handle window creation, input events, and the render loop yourself 
* Texture handling: Backends must implement support for dynamic fonts (ImGui 1.92+)

[python_backends](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends) contains pure python backends for glfw, pyglet, sdl2 and sdl3. They do not offer the same DPI handling as HelloImGui, but they are a good starting point if you want to use alternative backends.

See [examples](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends/examples) where you will find:
* example_python_backend_glfw3.py
* example_python_backend_pygame.py
* example_python_backend_pyglet.py
* example_python_backend_sdl2.py
* example_python_backend_sdl3.py
* example_python_backend_wgpu.py

:::{note}
Some other python libraries also provide ImGui integration, using Dear ImGui Bundle.

See for example:
* [wgpu-py](https://github.com/pygfx/wgpu-py/blob/main/examples/imgui_basic_example.py)
* [moderngl-window](https://github.com/moderngl/moderngl-window/blob/master/examples/integration_imgui.py)
:::
