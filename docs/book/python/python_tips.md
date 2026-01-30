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


# Read the libraries doc as a Python developer

## General advices

ImGui is a C++ library that was ported to Python. In order to work with it, you will often refer to its manual, which shows example code in C++.

In order to translate from C++ to Python:

1. Change the function names and parameters' names from CamelCase to snake_case

2. Change the way the output are handled.

   a. in C++ ImGui::RadioButton modifies its second parameter (which is passed by address) and
   returns true if the user clicked the radio button.

   b. In python, the (possibly modified) value is transmitted via the return: imgui.radio_button returns a Tuple[bool, str] which contains (user_clicked, new_value).

3. if porting some code that uses static variables, use the `@immapp.static` decorator. In this case, this decorator simply adds a variable value at the function scope. It is preserved between calls. Normally, this variable should be accessed via demo_radio_button.value, however the first line of the function adds a synonym named static for more clarity. Do not overuse them! Static variable suffer from almost the same shortcomings as global variables, so you should prefer to modify an application state.



**Example**

C++

```cpp
void DemoRadioButton()
{
   static int value = 0;
   ImGui::RadioButton("radio a", &value, 0); ImGui::SameLine();
   ImGui::RadioButton("radio b", &value, 1); ImGui::SameLine();
   ImGui::RadioButton("radio c", &value, 2);
}
```

Python
```python
@immapp.static(value=0)
def demo_radio_button():
   static = demo_radio_button
   clicked, static.value = imgui.radio_button("radio a", static.value, 0)
   imgui.same_line()
   clicked, static.value = imgui.radio_button("radio b", static.value, 1)
   imgui.same_line()
   clicked, static.value = imgui.radio_button("radio c", static.value, 2)
```


## Enums and TextInput

In the example below, two differences are important:

**InputText functions:**

`imgui.input_text` (Python) is equivalent to `ImGui::InputText` (C++)

* In C++, it uses two parameters for the text: the text pointer, and its length.
* In Python, you can simply pass a string, and get back its modified value in the returned tuple.

**Enums handling:**

* `ImGuiInputTextFlags_` (C++) corresponds to `imgui.InputTextFlags_` (python) and it is an enum (note the trailing underscore).

* `ImGuiInputTextFlags` (C++) corresponds to `imgui.InputTextFlags` (python) and it is an int (note: no trailing underscore)

You will find many similar enums.

The dichotomy between int and enums, enables you to write flags that are a combinations of values from the enum (see example below).

**Example**

C++

```cpp
void DemoInputTextUpperCase()
{
   static char text[64] = "";
   ImGuiInputTextFlags flags = (
   ImGuiInputTextFlags_CharsUppercase
   | ImGuiInputTextFlags_CharsNoBlank
   );
   /*bool changed = */ ImGui::InputText("Upper case, no spaces", text, 64, flags);
}
```

Python
```python
@immapp.static(text="")
def demo_input_text_decimal() -> None:
   static = demo_input_text_decimal
   flags:imgui.InputTextFlags = (
   imgui.InputTextFlags_.chars_uppercase.value
   | imgui.InputTextFlags_.chars_no_blank.value
   )
   changed, static.text = imgui.input_text("Upper case, no spaces", static.text, flags)
```


## Dear ImGui C++ vs Python API

Dear ImGui’s C++ API is thoroughly documented in its header files:

* [main API](https://github.com/ocornut/imgui/blob/master/imgui.h)
* [internal API](https://github.com/ocornut/imgui/blob/master/imgui_internal.h)

The Dear ImGui Python API The python API closely mirrors the C++ API, and its documentation is extremely easy to access from your IDE, via thoroughly documented stub (*.pyi) files.

* [main API](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi)
* [internal API](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/internal.pyi)

# See Also

- **[Dear ImGui Basics](../core_libs/imgui.md)** – Widget concepts, IDs, common patterns
- **[Hello ImGui & ImmApp](../core_libs/hello_imgui_immapp.md)** – App runners, DPI handling, configuration
- **[Async Support](python_async.md)** – Running GUI alongside async Python code
- **[Jupyter Notebooks](notebook_runners.ipynb)** – Using ImGui Bundle in notebooks
