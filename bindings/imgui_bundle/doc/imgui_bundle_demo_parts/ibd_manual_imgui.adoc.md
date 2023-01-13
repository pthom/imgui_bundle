# Dear ImGui - Immediate GUI

Dear ImGui is an implementation of the Immediate Gui paradigm.

## Consult the ImGui Manual

Dear ImGui comes with a complete demo. It demonstrates all the widgets, together with an example code on how to use them.

[ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html) is an easy way to consult this demo, and to see the corresponding code. The demo code is in C++, but read on for \"Code advices\" on how to translate from C++ to python.

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
