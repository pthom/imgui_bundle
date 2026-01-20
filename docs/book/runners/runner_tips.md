# Tips

## Correctly size and position the widgets

It is almost always a bad idea to use fixed sizes. This will lead to portability issues, especially on high-DPI screens.

Instead of using fixed pixel sizes, it is recommended to use sizes relative to the font size, aka "em" units.

:::{tip}
See the definition of the [em CSS Unit](https://en.wikipedia.org/wiki/Em_(typography)).
:::

To achieve this, you should multiply your positions and sizes by `ImGui::GetFontSize()` (C++), or `imgui.get_font_size()` (Python).

In order to make this simpler, the `HelloImGui::EmToVec2` (C++) or `hello_imgui::em_to_vec2` (Python) function below can greatly reduce the friction: it transforms a size in "em" units to a size in pixels.


Example with Python:

```python
from imgui_bundle import imgui, hello_imgui

def gui():
    imgui.button("A button", hello_imgui.em_to_vec2(10, 2))  # 10em x 2em button
```

Example with C++:

```cpp
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"

void gui() {
    ImGui::Button("A button", HelloImGui::EmToVec2(10, 2)); // 10em x 2em button
}
```

:::{note}
* `EmSize(x)` functions are also available to get only one dimension in pixels. (e.g., `hello_imgui.em_size(2)` or `HelloImGui::EmSize(2)`).

* `EmToVec2` and `EmSize` are also available in the `immapp` module in Python, and in the `ImmApp` namespace in C++.
  :::
