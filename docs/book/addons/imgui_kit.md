# ImGuiKit

[ImGuiKit](https://github.com/pthom/imgui_kit) brings small, standalone additions to Dear ImGui: rows that fill, groups that align, a few widgets, touch screens, and a mouse wheel that stays with what it scrolls.

It is a library of its own (MIT): one header, a few sources, and Dear ImGui as its only dependency. Dear ImGui Bundle includes it, with Python bindings.

## Its parts

- **Em units**: sizes in multiples of the font size (`EmSize()`, `EmToVec2()`). They follow the font, so they stay right on high-DPI screens and when the user zooms the text.
- **Layout**: helpers that measure their parts on the previous frame.
  - A *fill row*: a slider or an input fills the line, and the items after it stay on the right.
  - An *aligned group*: a group placed at the right of the line, or centered.
  - A *column*: a group that knows its width, so that what is inside can be centered under a knob or a slider.
  - A *label column*: labels on the left, and the widgets after them aligned at the widest label.
  - A *flow*: items on a line while they fit, then on the next one, as words in a paragraph.
- **Widgets**:
  - A *help marker*: an (i) that shows its text on hover, and on a tap (a touch screen has no hover). Its text can be rendered as Markdown.
  - *Icon buttons*: plus, minus, zoom in, zoom out, 1:1, fit, drawn with the draw list (no icon font needed).
  - A *segmented switch*: exclusive choices in one frame, such as "Demo | Code".
- **Touch screens** (`imgui_kit.touch`): an app made for the mouse works with a finger. A swipe scrolls, a long press is a right click, a pinch scales the font or zooms a plot or an image, and a browser opens the phone's keyboard. See [Touch screens](#touch-screens).
- **Wheel session**: the mouse wheel keeps scrolling the window it started on, as in a browser. A page scrolled over a plot keeps scrolling, and the plot zooms only with a wheel that starts on it.

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

In Python, each `begin_x()` / `end_x()` pair is also a context manager, named `x`: `fill_row`, `aligned_group`, `column`, `label_column`, `flow`. The help marker's is `help_marker_ctx`, since `help_marker(text)` is already a plain function.

## Touch screens

An app run by Hello ImGui or ImmApp gets the touch layer and the wheel session with nothing to write: the runner sets them up, and their settings are `RunnerParams.touch_config` and `RunnerParams.wheel_session`. An app with its own backend and loop sets them up once, after creating the context: `imgui_kit.touch.setup()` and `imgui_kit.setup_wheel_session()`.

On a touch screen:
- *A swipe* scrolls any window, with inertia, even when it starts on a button. A tap still clicks it.
- *A hold, then a drag*, goes to the widget under the finger (a text selection).
- *A slider or a drag*: a drag along its axis moves it at once, a drag across scrolls the window (Dear ImGui Bundle's Dear ImGui tells the kit about its draggable widgets). A widget of your own does the same with `imgui_kit.touch.set_item_takes_drags(imgui_kit.TouchAxis_.x)` right after it.
- *A long press* is a right click: the context menus.
- *A pinch* scales the app's font. On a plot (ImPlot, ImPlot3D) or an image (ImmVision), it zooms it, around the fingers.
- *Two fingers that move together* are a right drag (the box selection of a plot, the pan of a node editor).

A widget of your own takes two fingers with one call, right after it: `item_pinch()` returns their gesture at each frame (its center, its spread and its move since the last frame). The widget then zooms and pans at once, as a map does on a phone.

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, imgui_kit, ImVec2

zoom, origin = 1.0, ImVec2(0, 0)  # in your app's state: the content's scale, and its origin on the screen
imgui.invisible_button("##canvas", ImVec2(300, 200))
pinch = imgui_kit.touch.item_pinch()  # two fingers on the canvas
if pinch.active:
    c, k = pinch.center, pinch.scale_delta
    origin = ImVec2(c.x - (c.x - origin.x) * k + pinch.center_delta.x,  # zoom around the fingers,
                    c.y - (c.y - origin.y) * k + pinch.center_delta.y)  # and follow their move
    zoom *= k
```
:::

:::{tab-item} C++
```cpp
#include "imgui_kit/imgui_kit.h"

ImGui::InvisibleButton("##canvas", ImVec2(300.f, 200.f));
ImGuiTouchPinch pinch = ImGuiTouch::ItemPinch();  // two fingers on the canvas
if (pinch.Active)
{
    // Zoom around the fingers, and follow their move
    origin = pinch.Center - (pinch.Center - origin) * pinch.ScaleDelta + pinch.CenterDelta;
    zoom *= pinch.ScaleDelta;
}
```
:::

::::

A widget that already zooms with the wheel and pans with a mouse button (an image viewer, a plot) needs no new code: `set_item_pinch_as_wheel(wheel_zoom_factor)` turns the pinch into wheel events (1.1 for +10% per wheel unit; `TouchPinchDelivery_.wheel_notches` for a widget that reads only the wheel's sign, as ImPlot), and `set_item_two_finger_pan_as_mouse_drag(button)` turns two fingers moved together into a drag. For a widget that is not one item, the `set_rect_...` and `rect_pinch()` variants take its rectangle. The demo "Touch screens (phones, tablets)" shows every gesture; on a desktop, its "Simulate a touch source" checkbox plays the finger with the mouse.

Where the gestures work:
- *In a browser* (the web explorer, Pyodide, an Emscripten build): all of them, the pinch and the phone's keyboard included.
- *A native app* (desktop, iOS, Android through SDL): a swipe and a long press work where the backend tells a finger from the mouse (SDL, and Windows). The pinch does not yet: Hello ImGui's native runners forward no fingers. On Linux and macOS with GLFW, a finger is seen as a mouse.
- The details, backend by backend, and what an app with its own backend adds: [ImGuiKit's README](https://github.com/pthom/imgui_kit#what-each-backend-reports).

## Learn more

- [Try online](https://pthom.github.io/imgui_explorer/?lib=imguikit): the kit's demo, with its code in C++ or Python.
- API: [Python](../api/imgui_kit/imgui_kit.md), [C++](../api/imgui_kit/imgui_kit_cpp.md).
- Demo code: [imgui_kit_demo.cpp](https://github.com/pthom/imgui_kit/blob/main/imgui_kit_demo.cpp), [imgui_kit_demo.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_explorer/imgui_kit_demo.py).
- The repository: [pthom/imgui_kit](https://github.com/pthom/imgui_kit).
