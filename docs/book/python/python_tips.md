# Tips

# Context Managers

In Python, the module imgui_ctx provides a lot of context managers that automatically call imgui.end(), imgui.end_child(), etc., when the context is exited, so that you can write:

```python
from imgui_bundle import imgui, imgui_ctx

with imgui_ctx.begin("My Window"): # imgui.end() called automatically
imgui.text("Hello World")
```

Of course, you can choose to use the standard API by using the module imgui:

```
imgui.begin("My Window")
imgui.text("Hello World")
imgui.end()
```

* See [imgui_ctx](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_ctx.py)
* See [demo_python_context_manager.py](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_python_context_manager.py)


# Advanced glfw callbacks

When using the glfw backend, you can set advanced callbacks on all glfw events.

Below is an example that triggers a callback whenever the window size is changed:

```python
from imgui_bundle import glfw_utils, hello_imgui, imgui
# import glfw   # if you import glfw, do it _after_ imgui_bundle

# define a callback
def my_window_size_callback(window: glfw._GLFWwindow, w: int, h: int):
    print(f"Window size changed to {w}x{h}")


def install_glfw_callbacks():
    # Get the glfw window used by hello imgui
    glfw_win = glfw_utils.glfw_window_hello_imgui()
    glfw_utils.glfw.set_window_size_callback(glfw_win, my_window_size_callback)


# Install the callback once everything is initialized, for example:
runner_params = hello_imgui.RunnerParams()
# ...
runner_params.callbacks.post_init = install_glfw_callbacks
```

:::{important} Caution
It is important to import glfw after imgui_bundle, since - upon import - imgui_bundle informs glfw that it shall use its own version of the glfw dynamic library.
:::

# Display Matplotlib plots in ImGui

[imgui_fig.py](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_fig.py) is a small utility to display Matplotlib plots in ImGui.

See [demo_matplotlib.py](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_matplotlib.py) for an example.

