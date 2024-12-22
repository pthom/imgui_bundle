# Intro

```{codes_include} discover/widget_edit
```

## What is an Immediate Mode GUI

Graphical User Interfaces (GUIs) handle how your application is presented to the user.

Most GUI frameworks rely on complex patterns like **MVC**, which separate application logic into layers: Model (the data), View (the presentation), and Controller (the logic). Thus, the code which handles the state of the application is split in different places, which can make it hard to follow, and to synchronize, once the application grows.

**Immediate Mode GUI (IMGUI)** frameworks, like **Dear ImGui**, take a radically different approach: *the code which renders the widgets and the code which handles the user interactions are in the same place*, i.e. in the rendering loop. Handling the state of the application, and adding features, becomes extremely simple.

The example below illustrates this concept, where an application could display a counter, together with a button to increase it:

![example](discover/button.jpg)

**Python**:
```python
# on_frame is called at each frame
def on_frame():
    imgui.text(f"Counter: {counter}") # Display a text widget
    if imgui.button("Increment"):     # Display a button, and return true if clicked
        counter += 1                  # Perform an action immediately on interaction
```

**C++**:
```cpp
void on_frame() {
    ImGui::Text("Counter: %d", counter);
    if (ImGui::Button("Increment"))
        counter++;
}
```

## Why Use Immediate Mode GUIs?

Here are some key benefits:

1. **Simplicity**: UI code is clean and readable. You describe what to display and interact with, frame by frame.
2. **Minimal State Management**: No complex state updates; you control state directly in your code.
3. **Performance**: Optimized for real-time rendering and interaction.

Widgets are defined and user interactions are managed in the same code section. This immediate approach is particularly useful for:

**Notes:**
- **Separation of concerns**: The immediate mode paradigm is compatible with best practices, such as having a separate Model (or Application State).
  See the next example for an illustration.
- **Limitations:** The Dear ImGui library is not designed for fully "skinnable" UIs (although custom "themes" or "styles" are available), and will not support complex font rendering (left to right, etc).


## Contents of this tutorial
In this tutorial, you will:

1. Learn the basics of Immediate Mode GUIs.
2. Explore the fundamental widgets provided by **Dear ImGui**.
3. Use **Hello ImGui** to quickly set up applications with minimal boilerplate code.
4. Build a small, interactive project to solidify your understanding.

Let’s dive in and explore the straightforward yet powerful world of Immediate Mode GUI programming!


## Introducing *Dear ImGui*, *Hello ImGui*, and *Dear ImGui Bundle*

- **[Dear ImGui](https://github.com/ocornut/imgui)**: A lightweight and fast C++ library for Immediate Mode GUI programming, with over 60k stars on GitHub. It enables rapid creation of UI components such as buttons, sliders, and text fields with minimal code, leveraging GPU rendering for exceptional performance.
- **[Hello ImGui](https://pthom.github.io/hello_imgui)**: A powerful C++ wrapper around Dear ImGui designed to streamline apps creation with Dear ImGui, and to simplify complex tasks such as layout handling, FPS idling, and creating mobile and desktop applications. It reduces boilerplate and adds enhanced utilities, making it ideal for both simple prototypes and advanced production-grade GUIs.
- **[Dear ImGui Bundle](https://pthom.github.io/imgui_bundle)**: an extensive set of ready-to-use widgets and libraries, based on ImGui and Hello ImGui. It also provides bindings for Python, enabling you to create GUI applications in **Python**, which we will explore in this tutorial.


## Deploy web applications in Python with Dear ImGui Bundle

TODO: Add content