# ImGuiKit

[ImGuiKit](https://github.com/pthom/imgui_kit) brings small, standalone additions to Dear ImGui: rows that fill, groups that align, a few widgets.

It is a library of its own (MIT): one header, a few sources, and Dear ImGui as its only dependency. Dear ImGui Bundle includes it, with Python bindings.

## Its three parts

- **Em units**: sizes in multiples of the font size (`EmSize()`, `EmToVec2()`). They follow the font, so they stay right on high-DPI screens and when the user zooms the text.
- **Layout**: helpers that measure their parts on the previous frame.
  - A *fill row*: a slider or an input fills the line, and the items after it stay on the right.
  - An *aligned group*: a group placed at the right of the line, or centered.
  - A *column*: a group that knows its width, so that what is inside can be centered under a knob or a slider.
  - A *flow*: items on a line while they fit, then on the next one, as words in a paragraph.
- **Widgets**:
  - A *help marker*: an (i) that shows its text on hover, and on a tap (a touch screen has no hover). Its text can be rendered as Markdown.
  - *Icon buttons*: plus, minus, zoom in, zoom out, 1:1, fit, drawn with the draw list (no icon font needed).
  - A *segmented switch*: exclusive choices in one frame, such as "Demo | Code".

## Quick example

A slider that fills the line, with two arrows and a help marker on its right:

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, imgui_kit

slice_ = 37  # in your app's state
with imgui_kit.fill_row("slice") as row:
    _, slice_ = imgui.slider_int("##slice", slice_, 0, 59)  # fills the line
    row.tail()  # the items after this call stay on the right
    imgui.arrow_button("##prev", imgui.Dir.left)
    imgui.same_line()
    imgui.arrow_button("##next", imgui.Dir.right)
    imgui.same_line()
    imgui_kit.help_marker("Drag the slider, or click the arrows.")
```
:::

:::{tab-item} C++
```cpp
#include "imgui_kit/imgui_kit.h"

ImGuiKit::BeginFillRow("slice");
ImGui::SliderInt("##slice", &slice, 0, 59);    // fills the line
ImGuiKit::FillRowTail();                        // the items after this call stay on the right
ImGui::ArrowButton("##prev", ImGuiDir_Left);
ImGui::SameLine();
ImGui::ArrowButton("##next", ImGuiDir_Right);
ImGui::SameLine();
ImGuiKit::HelpMarker("Drag the slider, or click the arrows.");
ImGuiKit::EndFillRow();
```
:::

::::

In Python, each `begin_x()` / `end_x()` pair is also a context manager, named `x`: `fill_row`, `aligned_group`, `column`, `flow`. The help marker's is `help_marker_ctx`, since `help_marker(text)` is already a plain function.

## Learn more

- [Try online](https://pthom.github.io/imgui_explorer/?lib=imguikit): the kit's demo, with its code in C++ or Python.
- API: [Python](../api/imgui_kit/imgui_kit.md), [C++](../api/imgui_kit/imgui_kit_cpp.md).
- Demo code: [imgui_kit_demo.cpp](https://github.com/pthom/imgui_kit/blob/main/imgui_kit_demo.cpp), [imgui_kit_demo.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_explorer/imgui_kit_demo.py).
- The repository: [pthom/imgui_kit](https://github.com/pthom/imgui_kit).
