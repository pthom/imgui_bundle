# Advices to layout your GUI

* Widget labels need to be unique, so you can use a suffix to create a unique identifier for a widget by adding a suffix "##some_suffix", which will not be displayed : see [FAQ](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md#q-about-the-id-stack-system)
* You can use horizontal and vertical layouts to create columns and rows.
* You can use the `imgui.set_next_item_with` function to set the width of the next widget.

**Using em units**

It is important to use em units (see https://en.wikipedia.org/wiki/Em_(typography) ), in order to create application whose layout adapts to the font size,  and does not depend on the screen resolution and scaling.

Hello ImGui provides several helper functions to convert between pixels and em units:

*In Python*
```python
hello_imgui.em_to_vec2(em_width: float, em_height: float) -> ImVec2
hello_imgui.em_size(em: float = 1.0) -> float
hello_imgui.pixels_to_em(px_width: float, px_height: float) -> ImVec2
```

*In C++*
```cpp
ImVec2 HelloImGui::EmToVec2(float em_width, float em_height);
float HelloImGui::EmSize(float em = 1.0f);
ImVec2 HelloImGui::PixelsToEm(float px_width, float px_height);
```


The code below demonstrates these advices and create this application:

![](layout_advices.jpg)


```{codes_include} discover/layout_advices
```
