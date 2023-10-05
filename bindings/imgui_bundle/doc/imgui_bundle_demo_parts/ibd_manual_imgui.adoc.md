# Dear ImGui - Immediate GUI

Dear ImGui is an implementation of the Immediate Gui paradigm.

## Dear ImGui demo (and manual)

Dear ImGui comes with a complete demo. It demonstrates all the widgets, together with an example code on how to use them.

::: tip
To run this demo in your browser, launch [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html).\
\
For each widget, you will see the corresponding demo code (in C++. Read the part \"C++ / Python porting advices\" to see how easy it is to translate Gui code from C++ to python.
:::

## Dear ImGui C++ API

Dear ImGui's C++ API is thoroughly documented in its header files:

-   [main API](https://github.com/ocornut/imgui/blob/master/imgui.h)

-   [internal API](https://github.com/ocornut/imgui/blob/master/imgui_internal.h)

## Dear ImGui Python API

The python API closely mirrors the C++ API, and its documentation is extremely easy to access from your IDE, via thoroughly documented stub (\*.pyi) files.

-   [main API](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi)

-   [internal API](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/internal.pyi)

## Example

An example is often worth a thousand words, the following code:

C++

``` cpp
// Display a text
ImGui::Text("Counter = %i", app_state.counter);
ImGui::SameLine(); // by default ImGui starts a new line at each widget

// The following line displays a button
if (ImGui::Button("increment counter"))
    // And returns true if it was clicked: you can *immediately* handle the click
    app_state.counter += 1;

// Input a text: in C++, InputText returns a bool and modifies the text directly
bool changed = ImGui::InputText("Your name?", &app_state.name);
ImGui::Text("Hello %s!", app_state.name.c_str());
```

Python

``` python
# Display a text
imgui.text(f"Counter = {app_state.counter}")
imgui.same_line()  # by default ImGui starts a new line at each widget

# The following line displays a button
if imgui.button("increment counter"):
    # And returns true if it was clicked: you can *immediately* handle the click
    app_state.counter += 1

# Input a text: in python, input_text returns a tuple(modified, new_value)
changed, app_state.name = imgui.input_text("Your name?", app_state.name)
imgui.text(f"Hello {app_state.name}!")
```

Displays this:
