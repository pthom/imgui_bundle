# Code output guidelines for Claude

When helping users with coding tasks, please follow these guidelines to ensure high-quality, maintainable code.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.


=================

Now, some notes about the ImGui Bundle project itself.


# ImGui Bundle: Conversation Starter for LLMs

ImGui Bundle provides a complete set of libraries on top of Dear ImGui, enabling users to create interactive applications in C++ and Python. 

This conversation starter is intended to be studied by a LLM, so that it can then help users.

Please read thoroughly the following sections to understand the structure of the project and how to use it. 

The following sections will contain lots of links: 
* those which are marked with "please do read" are important to understand the project, and you should read them right away.
* those which are marked with "if needed" are less important, and you can read them later if you need to help users with specific questions.

# Docs for ImGui Bundle and Hello ImGui

ImGui Bundle is based on Dear ImGui, and can also use Hello ImGui as a base, in order to ease the creation of interactive applications.

Please do read to the following documentation for a comprehensive understanding of the libraries:

**Dear ImGui Bundle, full doc (PDF):** 
https://pthom.github.io/imgui_bundle/assets/book.pdf

**Hello ImGui**
https://pthom.github.io/hello_imgui/book/intro.html
https://pthom.github.io/hello_imgui/book/doc_params.html
https://pthom.github.io/hello_imgui/book/doc_api.html

**Docs for Fiatlight**
Fiatlight is a library heavily based on Dear ImGui Bundle, by the same author.
Reading this is not mandatory, it only helps if working on Fiatlight itself.
https://pthom.github.io/fiatlight_doc/flgt.pdf

# Differences in the C++ versus Python APIs

ImGui Bundle's Python bindings follow Python's conventions while maintaining compatibility with the underlying C++ API. Here are the key differences:

## 1. Naming Conventions

* C++ uses `CamelCase` while Python uses `snake_case`:
  ```cpp
  // C++
  ImGui::BeginMainMenuBar();
  ImGui::SliderFloat("My Slider", &value, 0.0f, 1.0f);
  ```
  ```python
  # Python
  imgui.begin_main_menu_bar()
  imgui.slider_float("My Slider", value, 0.0, 1.0)
  ```

## 2. Return Values vs Output Parameters

* C++ modifies variables through pointers, while Python returns modified values:
  ```cpp
  // C++: Modified through pointer, returns if value changed
  bool changed = ImGui::SliderFloat("value", &f, 0.0f, 1.0f);
  ```
  ```python
  # Python: Returns both the change status and modified value
  changed, f = imgui.slider_float("value", f, 0.0, 1.0)
  ```

## 3. Enum Values

* C++ enums are converted to Python enum classes:
  ```cpp
  // C++ (buffer is a char[256])
  bool changed = ImGui::InputText("Input", buffer, 256, ImGuiInputTextFlags_CharsUppercase);
  ```
  ```python
  # Python (text is a str)
  changed, text = imgui.input_text("Input", text, imgui.InputTextFlags_.chars_uppercase.value)
  ```

## 4. Module Structure and Imports

* Python requires explicit imports from the imgui_bundle package:
  ```python
  from imgui_bundle import imgui, implot, immapp, hello_imgui

  # Or specific components:
  from imgui_bundle.immapp import fonts, icons_fontawesome_6
  ```
* C++ uses `#include` directives:
  ```cpp
  #include "imgui.h"
  #include "implot.h"
  #include "hello_imgui/hello_imgui.h"
  #include "immapp/immapp.h"
  ```


# Common ImGui Patterns and Gotchas

## Widget IDs

ImGui identifies widgets by their label string. You must not have two widgets with the same label in the same scope, or they will conflict.

**Solution 1: Use `##` to add a hidden ID suffix:**
```python
imgui.button("OK")           # ID is "OK"
imgui.button("OK##dialog2")  # ID is "OK##dialog2", but displays as "OK"
imgui.button("##hidden")     # No visible label, ID is "##hidden"
```

**Solution 2: Use `push_id()`/`pop_id()` for loops:**
```python
for i, item in enumerate(items):
    imgui.push_id(i)          # or push_id(str(i)) or push_id(item.name)
    if imgui.button("Delete"):
        delete_item(item)
    imgui.pop_id()
```

## Begin/End Pairs

Many ImGui functions come in begin/end pairs. **Important rules:**

1. **`imgui.begin()` is special**: Always call `imgui.end()`, even if `begin()` returns False:
   ```python
   # CORRECT
   if imgui.begin("Window"):
       imgui.text("Content")
   imgui.end()  # Always called!

   # WRONG - will cause errors
   if imgui.begin("Window"):
       imgui.text("Content")
       imgui.end()  # Only called when window is visible - BUG!
   ```

2. **Other begin/end pairs**: Only call `end_*()` if `begin_*()` returned True:
   ```python
   if imgui.begin_menu("File"):
       if imgui.menu_item("Open"):
           open_file()
       imgui.end_menu()  # Only when begin_menu returned True

   if imgui.begin_popup("popup"):
       imgui.text("Popup content")
       imgui.end_popup()  # Only when begin_popup returned True
   ```

## Context Managers (Python)

Python users can use `imgui_ctx` for automatic end calls, which is cleaner and less error-prone:

```python
from imgui_bundle import imgui, imgui_ctx

# Automatic imgui.end() when exiting the with block
with imgui_ctx.begin("My Window") as window_visible:
    if window_visible:
        imgui.text("Hello")

# Works for other pairs too
with imgui_ctx.begin_menu("File") as menu_open:
    if menu_open:
        if imgui.menu_item("Open"):
            open_file()

# Useful for tree nodes, popups, etc.
with imgui_ctx.tree_node("Settings") as node_open:
    if node_open:
        imgui.text("Settings content")
```

See: https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_ctx.py

## DPI-Aware Sizing

**Never use hardcoded pixel sizes** - they will look wrong on high-DPI screens and different platforms.

```python
# BAD - hardcoded pixels
imgui.button("Click", imgui.ImVec2(100, 30))

# GOOD - use em units (1 em = font height, typically ~16px at 100% DPI)
imgui.button("Click", hello_imgui.em_to_vec2(8, 2))

# Also available:
width = hello_imgui.em_size(10)  # Single dimension
em = hello_imgui.em_size()       # Get 1 em in pixels
```

The `em_to_vec2()` and `em_size()` functions are available in both `hello_imgui` and `immapp` modules.


# References for Python APIs

## Hello ImGui and ImApp API

Hello ImGui and ImmApp are frameworks that simplify creating interactive applications with ImGui. They handle window creation, rendering, UI loops, and events, allowing developers to focus on GUI elements.

### Hello ImGui Core Features

1. **Simple Application Structure**:
   - Define a single GUI function that will be called each frame
   - Call `HelloImGui::Run()` (C++) or `hello_imgui.run()` (Python) to start the application

2. **DPI-Aware Interface**:
   - Automatically handles high-DPI screens across platforms
   - Provides utilities like `em_size()` and `em_to_vec2()` for resolution-independent sizing

3. **Asset Management**:
   - Embedded asset system for fonts, images, and other resources
   - Functions like `image_from_asset()` and `load_font()` for easy asset loading
   - Works across all platforms (including mobile and web)

4. **Theming Support**:
   - Multiple built-in themes (Darcula, SoDark, PhotoshopStyle, etc.)
   - Theme customization with `ImGuiTweakedTheme`
   - Theme editor GUI with `show_theme_tweak_gui()`

5. **Window Management**:
   - Optional docking support
   - Window geometry restoration
   - Multi-viewport support

### ImmApp Features

ImmApp extends Hello ImGui with additional capabilities:

1. **AddOns Support**:
   - Enables integration with ImPlot, ImPlot3D, Markdown, Node Editor, etc.
   - Simple boolean flags to activate add-ons

2. **Extended API**:
   - Simplified interface for common tasks
   - Additional utilities for GUI layouts

### Basic Usage

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

Note: When using Hello ImGui or ImmApp, you don't need to call `imgui.begin()` and `imgui.end()` for the main window, as they automatically create a full-window ImGui context.

### Async and Pyodide Support

ImGui Bundle supports asynchronous execution for Jupyter notebooks and web deployment via Pyodide.

**Desktop Async** - For applications that need async integration:

```python
import asyncio
from imgui_bundle import immapp

async def main():
    await immapp.run_async(gui, window_title="My App")
    print("GUI closed")

asyncio.run(main())
```

**Jupyter Notebooks** - Use the `.nb` module for non-blocking execution:

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

**Pyodide (Web Browser)** - In Pyodide, `run()` starts the GUI and returns immediately (browsers cannot block):

```python
# Same code works on desktop (blocking) and Pyodide (fire-and-forget)
immapp.run(gui, window_title="My App")
```

For async control in Pyodide (waiting for GUI to exit), use `run_async()`:

```python
import asyncio
async def main():
    await immapp.run_async(gui, window_title="My App")
    print("GUI closed")
asyncio.create_task(main())
```

| Platform | `run()` | `run_async()` |
|----------|---------|---------------|
| Desktop | Blocking | Awaitable |
| Pyodide | Fire-and-forget | Awaitable |
| Notebook | Use `nb.start()` | Use `nb.start()` |

### Advanced Configuration with RunnerParams

For more sophisticated applications, Hello ImGui provides a comprehensive `RunnerParams` structure that controls all aspects of application behavior. Instead of using simple parameters, you can create and configure a `RunnerParams` object:

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

#### Key RunnerParams Components

1. **App Window Parameters** (`app_window_params`):
   - Controls the application window appearance and behavior
   - Window geometry (size, position, full-screen mode)
   - Borderless mode with customizable controls

2. **ImGui Window Parameters** (`imgui_window_params`):
   - Configures the ImGui windows inside the application
   - Menu bar options (app menu, view menu, themes)
   - Status bar settings
   - Default window types (full screen, dockspace, none)

3. **Callbacks** (`callbacks`):
   - GUI callbacks (called every frame):
     - `show_gui`: Main GUI content
     - `show_menus`: Custom menu bar content
     - `show_app_menu_items`: Items in the "App" menu
     - `show_status`: Status bar content
   - Lifecycle callbacks:
     - `post_init`: Called once after OpenGL/backend initialization
     - `before_exit`: Called once before shutdown
     - `pre_new_frame`: Called before each frame starts
   - Font loading:
     - `load_additional_fonts`: Load custom fonts at startup
   - Custom rendering:
     - `custom_background`: For custom OpenGL/3D backgrounds
   - Mobile-specific:
     - `mobile_on_pause`, `mobile_on_resume`: App backgrounded/foregrounded

4. **Docking Parameters** (`docking_params`):
   - Define dockable window layouts
   - Create complex UI arrangements with splits
   - Manage multiple alternative layouts

5. **Performance Settings**:
   - Control frame rate limiting with `fps_idling`
   - Mobile device optimizations
   - Background rendering options

This comprehensive parameter system allows for highly customized applications while maintaining the simplicity of the basic API for common use cases.

### Asset Management

Hello ImGui provides a cross-platform asset system for fonts, images, and other resources.

**Asset Directories** - By default, assets are loaded from a folder named `assets` next to your executable or script:

```python
# Set custom assets folder (call before run)
hello_imgui.set_assets_folder("my_assets")
```

**Loading Fonts**:

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

**Loading Images**:

```python
from imgui_bundle import hello_imgui, imgui

def gui():
    # Load and display an image from assets
    texture = hello_imgui.im_texture_id_from_asset("images/logo.png")
    imgui.image(texture, imgui.ImVec2(100, 100))
```

**DPI-Aware Sizing** - Use `em_size()` for resolution-independent sizing (see also "Common ImGui Patterns and Gotchas" section above):

```python
from imgui_bundle import hello_imgui, imgui

def gui():
    em = hello_imgui.em_size()  # Current font size (adapts to DPI)
    imgui.button("Click", imgui.ImVec2(10 * em, 2 * em))

    # Convenience function (preferred)
    imgui.button("Click", hello_imgui.em_to_vec2(10, 2))
```

### API References

Hello ImGui:
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi

ImmApp:
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/immapp/__init__.pyi
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/immapp/immapp_cpp.pyi

Main ImmApp run function:
```python
@overload
def run(
    gui_function: VoidFunction,
    window_title: str = "",
    window_size_auto: bool = False,
    window_restore_previous_geometry: bool = False,
    window_size: Optional[ScreenSize] = None,
    fps_idle: float = 10.0,
    with_implot: bool = False,
    with_implot3d: bool = False,
    with_markdown: bool = False,
    with_node_editor: bool = False,
    with_tex_inspect: bool = False,
    with_node_editor_config: Optional[NodeEditorConfig] = None,
    with_markdown_options: Optional[ImGuiMd.MarkdownOptions] = None,
) -> None:
    ...
```

## ImGui API

If needed, the Python bindings for ImGui are available in the following files:

Python:
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/internal.pyi

(those are bindings for imgui.h and imgui_internal.h)

## ImPlot and ImPlot3D API

Below are the Python bindings for ImPlot and ImPlot3D, read them if needed:

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot/__init__.pyi

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot3d/__init__.pyi


## All Library APIs

All library stubs (Python type hints and API documentation) are in `bindings/imgui_bundle/*.pyi`:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle

Key files: `hello_imgui.pyi`, `imgui/__init__.pyi`, `implot/__init__.pyi`, `immvision.pyi`, `immapp/__init__.pyi`


# Example programs and demos


## Hello World

Please do read these minimal hello world programs:

Hello World in Python and C++:
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_hello_world.py
and
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_hello_world.cpp


## A small program using ImGui, ImPlot and ImmApp
The program below shows a beating heart whose pulse is controlled by a knob.
It is a good example of how to use ImGui, ImPlot and ImmApp together.

Please do read it:

in python
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/haiku_implot_heart.py
and in C++
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/haiku_implot_heart.cpp


## Demos for ImPlot and ImPlot3D

If needed, a full set of Python demos for ImPlot and ImPlot3D are available:

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot/implot_demo.py

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot3d/implot3d_demo.py

They are almost direct translation of the C++ demos available in the ImPlot and ImPlot3D repositories:
https://github.com/epezent/implot/blob/master/implot_demo.cpp
https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp



## How to create complex applications layouts using Hello ImGui

The demo below demonstrates how to use Hello ImGui to create complex applications layouts, using the following features:
- set up a complex docking layouts (with several possible layouts):
- use the status bar
- use default menus (App and view menu), and how to customize them
- display a log window
- load additional fonts, possibly colored, and with emojis
- use a specific application state (instead of using static variables)
- save some additional user settings within imgui ini file
- use borderless windows, that are movable and resizable

Read it if needed.

See
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py

and its C++ equivalent:
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp

## Custom background: 

If a user wants to create a custom 3D background (using OpenGL and shaders), an example is available in the following files, which you can read if needed:

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_custom_background.cpp

## Pure python backends
If a users wants to control the full app cycle (i.e. not using ImmApp or HelloImGui), they may want to use a pure python backend.

If needed, read the following links to understand how to use the pure python backends:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/python_backends/examples/example_python_backend_glfw3.py

https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/python_backends/examples/example_python_backend_sdl2.py


# ImmVision

ImmVision is an image debugger with zoom, pan, pixel inspection, and colormaps. Key points:

- Initialize color order: `immvision.use_rgb_color_order()` or `use_bgr_color_order()`
- `image()`: Full-featured display with `ImageParams` for options
- `image_display()`: Simple display
- `inspector_add_image()` / `inspector_show()`: Multi-image inspection

Demos: `demos_python/demos_immvision/` (display, inspector, processing, linked views)

# For Developers

Developer documentation (building, bindings, repo structure) is available in:
`docs/book/devel_docs/`

Key files:
- `structure.md` - Repository folder structure
- `bindings_intro.md` - How bindings are generated (uses litgen)
- `bindings_update.md` - Updating library bindings
- `bindings_newlib.md` - Adding a new library
- `pypi_deploy.md` - PyPI deployment process

The bindings are generated automatically using [litgen](https://pthom.github.io/litgen/litgen_book/00_00_intro.html), a Python bindings generator for C++ libraries.

External libraries and their bindings are in `external/`:
- Each library has a submodule and a `bindings/` folder
- `external/bindings_generation/autogenerate_all.py` regenerates all bindings

# Follow up

**Consult the links that were marked with "if needed" if you need to help users with specific questions on the APIs**

