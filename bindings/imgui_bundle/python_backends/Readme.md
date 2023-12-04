In this folder, you can find examples where the backend is programmed via python.

Those files are inspired from [pyimgui](https://github.com/pyimgui/pyimgui) bindings.

This is largely work in progress, and thus it may not work.
At the moment,  only glfw + OpenGL is implemented.


* Key binding needs to be improved (support for modifiers like Ctrl-Shift, etc.).See [glfw backend](glfw_backend.py) (adapted from [pyimgui's glfw integration](https://github.com/pyimgui/pyimgui/blob/master/imgui/integrations/glfw.py))
* The rendering works, and is implemented in [opengl_backend](opengl_backend.py) (adapted from [pyimgui's opengl integration](https://github.com/pyimgui/pyimgui/blob/master/imgui/integrations/opengl.py))

See [working example app with glfw](examples/example_python_backend_glfw3.py) (adapted from [pyimgui's glfw example](https://github.com/pyimgui/pyimgui/blob/master/doc/examples/integrations_glfw3.py))
