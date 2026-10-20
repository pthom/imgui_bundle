# For AI assistants

This page is written for AI assistants. Give it to yours: it will know how to help you write applications with Dear ImGui Bundle, in Python or C++. It is also at https://imgui-bundle.pages.dev/llms.txt.

## About this page

Dear ImGui Bundle is a set of libraries on top of [Dear ImGui](https://github.com/ocornut/imgui), to write interactive applications in Python and C++: on the desktop, on mobile, and in the browser.

Read this page first. It links to more:
- a link marked "please do read": read it right away;
- a link marked "if needed": read it when a question needs it.

## Install

**Python** (3.10 or later; binary wheels for Windows, macOS and Linux):

```bash
pip install imgui-bundle
```

- The package is `imgui-bundle`, the module is `imgui_bundle`.
- The minimal install has no dependency. ImPlot and ImmVision take numpy arrays: install `numpy` too.
- `pip install "imgui-bundle[full]"` also installs the optional dependencies (numpy, OpenCV, Pillow, matplotlib...).

**C++**: start from the template, https://github.com/pthom/imgui_bundle_template. In CMake, `imgui_bundle_add_app(my_app my_app.cpp)` creates an app, with its assets.

**In the browser, with no install**: the Python playground, https://imgui-bundle.pages.dev/playground/, runs Dear ImGui Bundle in Python (Pyodide), with ready-to-run demos.

The install pages, with the platform notes: https://imgui-bundle.pages.dev/doc/python/python-install/ and https://imgui-bundle.pages.dev/doc/cpp/cpp-install/

## Not pyimgui

`pyimgui` (`pip install imgui`, then `import imgui`) is another Python binding of Dear ImGui, with another API. Its code does not run with Dear ImGui Bundle. Assistants often mix the two up: check each name in the API files below.

| pyimgui | Dear ImGui Bundle |
|---|---|
| `import imgui` | `from imgui_bundle import imgui` |
| `imgui.WINDOW_NO_TITLE_BAR` | `imgui.WindowFlags_.no_title_bar` |
| `imgui.create_context()`, a renderer from `imgui.integrations`, and a loop written by hand | `immapp.run(gui)` or `hello_imgui.run(gui)`: the runner creates the window and runs the loop |

## Where to find more

**The book, in plain text (if needed):**
https://imgui-bundle.pages.dev/llms-full.txt holds the book's pages for users, one after the other (about 18,000 words): how to install, the core libraries, the add-ons, the notes for Python and for C++. Read it for a question that this page does not answer.

**The API, in plain text (if needed):**
https://imgui-bundle.pages.dev/llms/api/index.txt lists one file per module (a large module, such as imgui or implot, is cut into a few files), for example https://imgui-bundle.pages.dev/llms/api/hello_imgui.txt (Hello ImGui).
- Each file lists every function, class and enum of the module, with its Python signature, its C++ declaration, and the first paragraph of its doc.
- In Dear ImGui, ImPlot and ImPlot3D, an entry that a demo shows also has the link to that demo, live in the ImGui Explorer, and the demo's code that uses it, in Python and in C++.
- Read the file that a question needs, to check that a name exists and how to call it.

**The demos, in plain text (if needed):**
https://imgui-bundle.pages.dev/llms/demos.txt lists the demos of the catalog by category: what each one shows, the libraries it uses, and the links to its Python and C++ code. Read it to find a demo close to what the user wants, then read that demo's code.

**The explorers, where the demos run live (if needed):**
Two web apps show the demos in the browser, each beside its code:
- the Dear ImGui Explorer (https://pthom.github.io/imgui_explorer/): Dear ImGui, ImPlot, ImPlot3D and ImAnim, section by section;
- the Dear ImGui Bundle Explorer (https://imgui-bundle.pages.dev/explorer/): all the libraries.

Their pages draw in a canvas, with no text to read. https://imgui-bundle.pages.dev/llms/explorers.txt says what they show, and how to link to a demo section (e.g. https://pthom.github.io/imgui_explorer/?lib=implot&demo=Plots%2FLine%20Plots). Give such a link to a user who wants to see a feature in action.

**Hello ImGui's docs (if needed):** the app runner of the bundle, and its parameters.
- https://pthom.github.io/hello_imgui/book/
- https://pthom.github.io/hello_imgui/book/doc-params/
- https://pthom.github.io/hello_imgui/book/doc-api/

**Fiatlight (only for work on Fiatlight itself):** a library built on Dear ImGui Bundle, by the same author. https://pthom.github.io/fiatlight/flgt.pdf

## Python and C++: the differences

The Python bindings follow Python's conventions, and keep the C++ API's structure.

### 1. Naming

C++ uses `CamelCase`, Python uses `snake_case`:

```cpp
// C++
ImGui::BeginMainMenuBar();
ImGui::SliderFloat("My Slider", &value, 0.0f, 1.0f);
```
```python
# Python
imgui.begin_main_menu_bar()
changed, value = imgui.slider_float("My Slider", value, 0.0, 1.0)
```

### 2. Return values instead of output parameters

C++ modifies a variable through a pointer. Python returns the new value:

```cpp
// C++: modified through a pointer, returns whether the value changed
bool changed = ImGui::SliderFloat("value", &f, 0.0f, 1.0f);
```
```python
# Python: returns whether the value changed, and the new value
changed, f = imgui.slider_float("value", f, 0.0, 1.0)
```

### 3. Enums

C++ enums become Python enum classes:

```cpp
// C++ (buffer is a char[256])
bool changed = ImGui::InputText("Input", buffer, 256, ImGuiInputTextFlags_CharsUppercase);
```
```python
# Python (text is a str)
changed, text = imgui.input_text("Input", text, imgui.InputTextFlags_.chars_uppercase)
```

### 4. Imports

Python imports the modules from the `imgui_bundle` package:

```python
from imgui_bundle import imgui, implot, immapp, hello_imgui

# Or specific components:
from imgui_bundle import icons_fontawesome_6
```

C++ includes their headers:

```cpp
#include "imgui.h"
#include "implot.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
```

## Common patterns and gotchas

### Widget IDs

Dear ImGui identifies a widget by its label. Two widgets with the same label in the same scope conflict.

**Solution 1: `##` adds a hidden ID suffix:**
```python
imgui.button("OK")           # ID is "OK"
imgui.button("OK##dialog2")  # ID is "OK##dialog2", but displays as "OK"
imgui.button("##hidden")     # No visible label, ID is "##hidden"
```

**Solution 2: `push_id()` / `pop_id()` in loops:**
```python
for i, item in enumerate(items):
    imgui.push_id(i)          # or push_id(str(i)) or push_id(item.name)
    if imgui.button("Delete"):
        delete_item(item)
    imgui.pop_id()
```

### Begin/End pairs

Many functions come in begin/end pairs. Two rules:

1. **`imgui.begin()` is special**: always call `imgui.end()`, even if `begin()` returns False. In Python, `begin()` returns two values, `(expanded, opened)`: test the first one (a tuple is always true):
   ```python
   # CORRECT
   expanded, _ = imgui.begin("Window")
   if expanded:
       imgui.text("Content")
   imgui.end()  # Always called!

   # WRONG - will cause errors
   expanded, _ = imgui.begin("Window")
   if expanded:
       imgui.text("Content")
       imgui.end()  # Only called when window is visible - BUG!
   ```
   For a window without a close button, `imgui.begin_simple("Window")` returns `expanded` alone, a bool: `if imgui.begin_simple("Window"):`, then `imgui.end()` after the `if`.

2. **Other begin/end pairs**: call `end_*()` only if `begin_*()` returned True:
   ```python
   if imgui.begin_menu("File"):
       if imgui.menu_item_simple("Open"):  # menu_item() takes a shortcut and a "selected" flag, and returns two values
           open_file()
       imgui.end_menu()  # Only when begin_menu returned True

   if imgui.begin_popup("popup"):
       imgui.text("Popup content")
       imgui.end_popup()  # Only when begin_popup returned True
   ```

### Context managers (Python)

`imgui_ctx` calls the `end_*()` functions for you:

```python
from imgui_bundle import imgui, imgui_ctx

# Automatic imgui.end() when exiting the with block
with imgui_ctx.begin("My Window") as window_visible:
    if window_visible:
        imgui.text("Hello")

# Works for other pairs too
with imgui_ctx.begin_menu("File") as menu_open:
    if menu_open:
        if imgui.menu_item_simple("Open"):
            open_file()

# Useful for tree nodes, popups, etc.
with imgui_ctx.tree_node("Settings") as node_open:
    if node_open:
        imgui.text("Settings content")
```

All of them: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_ctx.py

### Sizes in em units (DPI-aware)

**Never use sizes in pixels**: they look wrong on high-DPI screens. Use em units: 1 em is the font's height.

```python
from imgui_bundle import imgui, em_to_vec2, em_size

# BAD - hardcoded pixels
imgui.button("Click", imgui.ImVec2(100, 30))

# GOOD - use em units (1 em = font height, typically ~16px at 100% DPI)
imgui.button("Click", em_to_vec2(8, 2))  # or hello_imgui.em_to_vec2(8, 2)

# Also available:
width = em_size(10)  # Single dimension
em = em_size()       # Get 1 em in pixels
```

`em_to_vec2()` and `em_size()` are in `imgui_bundle` (recommended), and also in `hello_imgui` and `immapp`.

### Horizontal and vertical layouts (StackLayout)

The bundle's Dear ImGui has StackLayout (by thedmd): `begin_horizontal()` / `end_horizontal()`, `begin_vertical()` / `end_vertical()`, and `spring()`. Prefer it to many `same_line()` calls, and for right-aligned or centered content:

```python
imgui.begin_horizontal("toolbar", imgui.ImVec2(imgui.get_content_region_avail().x, 0.0))
imgui.button("Left")
imgui.button("Also Left")
imgui.spring()  # pushes the next items to the right
imgui.text("Right-aligned")
imgui.end_horizontal()
```

The same in C++, and when to use it: https://imgui-bundle.pages.dev/doc/core-libs/imgui/#horizontal-and-vertical-layouts-stacklayout

### A widget that reads the mouse wheel

Hello ImGui keeps the wheel on the window it scrolls: a page scrolled with the wheel keeps scrolling over a plot. A widget that reads `io.mouse_wheel` itself (a value changed by the wheel, a zoom) must claim the wheel while hovered. Otherwise the page takes it, and the widget never sees it.

```python
imgui.invisible_button("zoom", em_to_vec2(10, 10))
if imgui.set_item_key_owner(imgui.Key.mouse_wheel_y):  # hovered: the wheel is this widget's
    zoom *= 1.1 ** imgui.get_io().mouse_wheel
```

```cpp
ImGui::InvisibleButton("zoom", HelloImGui::EmToVec2(10, 10));
if (ImGui::SetItemKeyOwner(ImGuiKey_MouseWheelY))  // hovered: the wheel is this widget's
    zoom *= powf(1.1f, ImGui::GetIO().MouseWheel);
```

### Animations and live data: idling

Hello ImGui lowers the frame rate 3 seconds after the last user input, to save the CPU. An animation, a live image or a plot of varying data then becomes choppy. Keep it smooth:
- `set_item_is_live()` right after its widget: the app keeps its full speed while the widget is visible.
- `request_refresh()` from any thread, when new data arrives (a camera, a socket).

```python
if implot.begin_plot("Live data"):
    implot.plot_line("signal", xs, ys)
    implot.end_plot()
    hello_imgui.set_item_is_live()  # no idling while the plot is visible
```

```cpp
if (ImPlot::BeginPlot("Live data"))
{
    ImPlot::PlotLine("signal", xs.data(), ys.data(), (int)xs.size());
    ImPlot::EndPlot();
    HelloImGui::SetItemIsLive();  // no idling while the plot is visible
}
```

Do not turn idling off (`fps_idling.enable_idling = False`, or `fps_idle=0`) to animate one widget. These settings are global, and the app would never idle. Keep them for an app whose whole window always moves.

## Let the AI see and drive the app

You can check your own work. After a change that the user sees, run the app for a few frames and look at a screenshot. Or drive the GUI (click, type, open a header) with the ImGui Test Engine, with screenshots along the way. Do it before saying that the change works.

**A screenshot of the final frame** (no test engine needed):

```python
from imgui_bundle import imgui
from imgui_bundle.immapp import testing

def gui():
    imgui.text("Hello")

testing.capture_final_frame(gui, "/tmp/out.png", window_size=(600, 400))
# then look at /tmp/out.png
```

**Driving the GUI, with screenshots at chosen moments:**

```python
def gui():
    imgui.button("Click me")

def my_test(ctx: imgui.test_engine.TestContext):
    testing.capture(ctx, "/tmp/00_initial.png")
    ctx.item_click("//**/Click me")  # a widget, found by its label
    testing.capture(ctx, "/tmp/01_after_click.png")

testing.run(gui, my_test, window_size=(600, 400))
```

In C++: `ImmApp::Testing::CaptureFinalFrame(guiFn, path, opts)` and `ImmApp::Testing::Capture(ctx, path)`, in `immapp/testing.h`.

Good to know:
- Both open a real window for a few frames: they need a display (on a headless Linux machine, use Xvfb).
- They accept the add-on flags of `immapp.run` (`with_markdown`, `with_implot`...).
- `window_size` is in logical pixels: on a Retina screen, the PNG is twice as large.
- In the default run speed, `ctx.sleep()` lets no real time pass: for a tooltip's delay or an animation, use `run_speed=testing.TestRunSpeed.normal`.
- The test engine is in the desktop packages, not in the Pyodide build (in the browser).
- The test engine's page gives more: https://imgui-bundle.pages.dev/doc/core-libs/test-engine/. Coding agents working in the bundle's repository also find skills about this in `.claude/skills/` (`screenshot-imgui-bundle`, `interact-and-screenshot`).

## Writing an app

### The runners: Hello ImGui and ImmApp

The runners create the window, run the loop, and handle the DPI, the assets and the themes. The app gives a function that draws the GUI, called at each frame:
- `hello_imgui.run()` (C++: `HelloImGui::Run()`) for an app without add-ons;
- `immapp.run()` (C++: `ImmApp::Run()`) for an app with add-ons (ImPlot, Markdown, the node editor...), enabled by flags.

```python
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Hello, world!")

immapp.run(
    gui_function=gui,           # Function called each frame
    window_title="Hello!",      # Window title
    window_size_auto=True,      # Auto-size window based on content
    with_implot=True,           # Enable ImPlot addon (optional)
    with_markdown=False,        # Enable Markdown addon (optional)
)
```

- The runner provides a full-window ImGui context: the main window needs no `imgui.begin()` / `imgui.end()`.
- `immapp.run()` and all its parameters (`with_implot3d`, `with_latex`, `with_node_editor`...): https://imgui-bundle.pages.dev/llms/api/immapp.txt
- Their page in the book: https://imgui-bundle.pages.dev/doc/core-libs/hello-imgui-immapp/

### More settings: RunnerParams

`hello_imgui.RunnerParams` controls the whole app: its window, its menus, its status bar, its docking layout, its callbacks.

```python
from imgui_bundle import hello_imgui, immapp

# Create and configure runner parameters
params = hello_imgui.RunnerParams()

# 1. Window settings
params.app_window_params.window_title = "Advanced Application"
params.app_window_params.window_geometry.size = (1200, 800)
params.app_window_params.restore_previous_geometry = True

# 2. ImGui window settings
params.imgui_window_params.show_menu_bar = True
params.imgui_window_params.show_status_bar = True
params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space

# 3. Callbacks
params.callbacks.show_gui = my_gui_function
params.callbacks.show_menus = my_menus_function
params.callbacks.show_status = my_status_function

# 4. Run the application with full parameters
immapp.run(params)
```

Its parts:
- `app_window_params`: the window (size, position, full screen, borderless).
- `imgui_window_params`: the menu bar (with its App and View menus), the status bar, the default window type (full screen, dock space, none).
- `callbacks`:
  - each frame: `show_gui`, `show_menus`, `show_app_menu_items`, `show_status`;
  - once: `post_init` (after the backend's init), `before_exit`;
  - `load_additional_fonts`, `custom_background` (OpenGL or 3D under the GUI), `mobile_on_pause` / `mobile_on_resume`.
- `docking_params`: the dockable windows and their layouts (several, to switch between).
- `fps_idling`: the frame rate when idle (global; for one animated widget, see "Animations and live data: idling" above).

All the parameters: https://pthom.github.io/hello_imgui/book/doc-params/ and https://imgui-bundle.pages.dev/llms/api/hello_imgui.txt

### Async, notebooks and the browser (Pyodide)

| Platform | `run()` | `run_async()` |
|----------|---------|---------------|
| Desktop | Blocking | Awaitable |
| Pyodide | Fire-and-forget | Awaitable |
| Notebook | Use `nb.start()` | Use `nb.start()` |

**Desktop, async:**

```python
import asyncio
from imgui_bundle import immapp

async def main():
    await immapp.run_async(gui, window_title="My App")
    print("GUI closed")

asyncio.run(main())
```

**Jupyter notebooks**: the `nb` module runs the GUI without blocking the next cells:

```python
from imgui_bundle import immapp

# Start GUI (non-blocking, continues to next cell)
immapp.nb.start(gui, window_title="My App")

# Later, to stop:
immapp.nb.stop()

# Check if running:
if immapp.nb.is_running():
    print("GUI is active")
```

**Pyodide (in the browser)**: `run()` starts the GUI and returns at once, since a browser cannot block. The same code works on the desktop (blocking) and in Pyodide:

```python
immapp.run(gui, window_title="My App")
```

To wait for the GUI's exit in Pyodide, use `run_async()`:

```python
import asyncio
async def main():
    await immapp.run_async(gui, window_title="My App")
    print("GUI closed")
asyncio.create_task(main())
```

More: https://imgui-bundle.pages.dev/doc/python/python-async/ and https://imgui-bundle.pages.dev/doc/python/python-pyodide/

### Assets: fonts and images

The runners load the assets from a folder named `assets`, next to the script or the executable:

```python
# Set custom assets folder (call before run)
hello_imgui.set_assets_folder("my_assets")
```

**Fonts**, loaded in the `load_additional_fonts` callback:

```python
from imgui_bundle import hello_imgui

def load_fonts():
    # Load a font at 18px size
    hello_imgui.load_font("fonts/Roboto-Regular.ttf", 18.0)

    # Load with options (e.g., merge icons into previous font)
    font_params = hello_imgui.FontLoadingParams()
    font_params.merge_to_last_font = True
    hello_imgui.load_font("fonts/icons.ttf", 16.0, font_params)

params = hello_imgui.RunnerParams()
params.callbacks.load_additional_fonts = load_fonts
```

**Images:**

```python
from imgui_bundle import hello_imgui, imgui

def gui():
    # Load and display an image from assets
    hello_imgui.image_from_asset("images/logo.png", imgui.ImVec2(100, 100))

    # Or with its texture, e.g. for imgui.image() (which takes an ImTextureRef)
    texture = hello_imgui.im_texture_id_from_asset("images/logo.png")
    imgui.image(imgui.ImTextureRef(texture), imgui.ImVec2(100, 100))
```

The assets folder, and what it holds: https://imgui-bundle.pages.dev/doc/python/python-assets/ (C++: https://imgui-bundle.pages.dev/doc/cpp/cpp-assets/)

## Example programs and demos

Read these first. The whole catalog, with a line per demo and the links to its code: https://imgui-bundle.pages.dev/llms/demos.txt

### Hello World

Please do read these minimal programs, in Python and C++:
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_hello_world.py
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_hello_world.cpp

### A small program with ImGui, ImPlot and ImmApp

A beating heart whose pulse is controlled by a knob: a good example of the three libraries together. Please do read it:
- in Python: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/haiku_implot_heart.py
- in C++: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/haiku_implot_heart.cpp

### ImPlot and ImPlot3D demos (if needed)

The full Python demos of ImPlot and ImPlot3D:
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_explorer/implot_demo.py
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_imgui_explorer/implot3d_demo.py

They are close translations of the C++ demos of the ImPlot and ImPlot3D repositories:
- https://github.com/epezent/implot/blob/master/implot_demo.cpp
- https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp

### Complex layouts with Hello ImGui (if needed)

This demo shows:
- docking layouts (several, to switch between);
- the status bar;
- the default menus (App and View), and how to customize them;
- a log window;
- additional fonts, possibly colored, and emojis;
- an app state (instead of static variables);
- user settings saved in the ImGui ini file;
- borderless windows, movable and resizable.

In Python: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py
In C++: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp

### A custom background (if needed)

A 3D background under the GUI, with OpenGL shaders:
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_custom_background.cpp

### Pure Python backends (if needed)

For an app that runs its own loop (without Hello ImGui or ImmApp):
- https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/python_backends/examples/example_python_backend_glfw3.py
- https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/python_backends/examples/example_python_backend_sdl2.py

## ImmVision

ImmVision is an image debugger: zoom, pan, pixel inspection, colormaps.
- Color order: RGB by default. Call `immvision.use_bgr_color_order()` once at startup for OpenCV (BGR) images.
- `image()`: the full display, with `ImageParams` for its options.
- `image_display()`: a simple display.
- `inspector_add_image()` / `inspector_show()`: the inspection of several images.

Demos: `demos_python/demos_immvision/` (display, inspector, processing, linked views).
