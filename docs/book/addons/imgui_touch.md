# ImGuiTouch

[ImGuiTouch](https://github.com/pthom/imgui_touch) makes Dear ImGui work on a touch screen, as on a phone: an app made for the mouse works with a finger, with no change to its widgets.

It is a library of its own (MIT): one header, a few sources, and Dear ImGui as its only dependency. It comes from [ImGuiKit](imgui_kit.md), which keeps the layout helpers and the widgets. Dear ImGui Bundle includes it, with Python bindings (`imgui_bundle.imgui_touch`).


An app run by Hello ImGui or ImmApp gets the touch layer with nothing to write: the runner sets it up, and its settings are `RunnerParams.touch_config`. An app with its own backend and loop sets it up once, after creating the context: `imgui_touch.setup()`.

On a touch screen:
- *A swipe* scrolls any window, with inertia, even when it starts on a button. A tap still clicks it.
- *A hold, then a drag*, goes to the widget under the finger (a text selection).
- *A slider or a drag*: a drag along its axis moves it at once, a drag across scrolls the window (Dear ImGui Bundle's Dear ImGui tells the layer about its draggable widgets). A widget of your own does the same with `imgui_touch.set_item_takes_drags(imgui_touch.Axis_.x)` right after it.
- *A long press* is a right click: the context menus.
- *A pinch* scales the app's font. On a plot (ImPlot, ImPlot3D), an image (ImmVision) or a node editor, it zooms it, around the fingers.
- *Two fingers that move together* are a right drag (the box selection of a plot, the pan of a node editor).

A widget of your own takes two fingers with one call, right after it: `item_pinch()` returns their gesture at each frame (its center, its spread and its move since the last frame). The widget then zooms and pans at once, as a map does on a phone.

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui, imgui_touch, ImVec2

zoom, origin = 1.0, ImVec2(0, 0)  # in your app's state: the content's scale, and its origin on the screen
imgui.invisible_button("##canvas", ImVec2(300, 200))
pinch = imgui_touch.item_pinch()  # two fingers on the canvas
if pinch.active:
    c, k = pinch.center, pinch.scale_delta
    origin = ImVec2(c.x - (c.x - origin.x) * k + pinch.center_delta.x,  # zoom around the fingers,
                    c.y - (c.y - origin.y) * k + pinch.center_delta.y)  # and follow their move
    zoom *= k
```
:::

:::{tab-item} C++
```cpp
#include "imgui_touch/imgui_touch.h"

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

A widget that already zooms with the wheel and pans with a mouse button (an image viewer, a plot) needs no new code: `set_item_pinch_as_wheel(wheel_zoom_factor)` turns the pinch into wheel events (1.1 for +10% per wheel unit; `PinchDelivery_.wheel_notches` for a widget that reads only the wheel's sign, as ImPlot), and `set_item_two_finger_pan_as_mouse_drag(button)` turns two fingers moved together into a drag. For a widget that is not one item, the `set_rect_...` and `rect_pinch()` variants take its rectangle. The demo "Touch screens (phones, tablets)" shows every gesture; on a desktop, its "Simulate a touch source" checkbox plays the finger with the mouse. The library's own demo, `imgui_touch.show_demo_window()`, has the same gestures, with its settings.

Where the gestures work:
- *In a browser* (the web explorer, Pyodide, an Emscripten build): all of them, the pinch and the phone's keyboard included.
- *A native app* (desktop, iOS, Android through SDL): a swipe and a long press work where the backend tells a finger from the mouse (SDL, and Windows). The pinch needs the fingers, which Dear ImGui's backends do not pass on: Hello ImGui's SDL2 runner forwards them to the layer (so an app run by Hello ImGui or ImmApp on SDL has the pinch, on a Windows touch screen, on iOS and on Android), its GLFW runner cannot (GLFW reports no fingers). An app with its own SDL loop forwards them with a dozen lines, `imgui_touch.add_finger_event()` for each finger: the README shows them ([The fingers from SDL](https://github.com/pthom/imgui_touch#the-fingers-from-sdl)), its `examples/sdl3_touch_demo` is a whole app (stock Dear ImGui on SDL3, desktop and iOS), and the pure Python example `example_python_backend_sdl2_imgui_kit.py` does the same in Python. On Linux and macOS with GLFW, a finger is seen as a mouse.
- The details, backend by backend, and what an app with its own backend adds: [ImGuiTouch's README](https://github.com/pthom/imgui_touch#what-each-backend-reports).

## Learn more

- [Try it on a phone](https://pthom.github.io/imgui_touch/): its demo, in a browser.
- The repository: [pthom/imgui_touch](https://github.com/pthom/imgui_touch).
