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

Bundle
https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/doc/Readme.adoc

Hello ImGui:
https://pthom.github.io/hello_imgui/book/intro.html
https://pthom.github.io/hello_imgui/book/doc_params.html
https://pthom.github.io/hello_imgui/book/doc_api.html



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
   - Function hooks for various application lifecycle events
   - GUI rendering (`show_gui`)
   - Menu generation (`show_menus`, `show_app_menu_items`)
   - Status bar content (`show_status`)
   - Application events (init, exit, frame updates)

4. **Docking Parameters** (`docking_params`):
   - Define dockable window layouts
   - Create complex UI arrangements with splits
   - Manage multiple alternative layouts

5. **Performance Settings**:
   - Control frame rate limiting with `fps_idling`
   - Mobile device optimizations
   - Background rendering options

This comprehensive parameter system allows for highly customized applications while maintaining the simplicity of the basic API for common use cases.

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


## List of all included libraries APIs

Below are links to the Python bindings for all the libraries included in ImGui Bundle. Read them if needed.

* Hello ImGui and ImmApp:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/immapp/__init__.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/hello_imgui.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/immapp/immapp_cpp.pyi

* ImGui:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui/__init__.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui/backends.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui/test_engine.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui/internal.pyi

* ImPlot:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/implot/__init__.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/implot/internal.pyi

* ImPlot3D:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/implot3d/__init__.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/implot3d/internal.pyi

* ImmVision
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/immvision.pyi

* Other libraries:
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_md.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_color_text_edit.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/portable_file_dialogs.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_tex_inspect.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imspinner.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/im_file_dialog.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_knobs.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_node_editor.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imguizmo.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_command_palette.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/nanovg.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/imgui_toggle.pyi
https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/im_cool_bar.pyi


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


# ImmVision API and Usage

ImmVision is an immediate mode image debugger and visualization library included in ImGui Bundle. It allows for interactive inspection, analysis, and visualization of images within ImGui interfaces.

## Key Features

1. **Image Display Functions**:
   - `image()`: Full-featured display with zoom, pan, pixel inspection, colormap options
   - `image_display()`: Simpler display with minimal interactive features
   - `image_display_resizable()`: Simple display with resizable widget

2. **Color Order Configuration**:
   - Must initialize with `immvision.use_rgb_color_order()` or `immvision.use_bgr_color_order()`
   - Temporary color order changes with `push_color_order_rgb()`, `push_color_order_bgr()` and `pop_color_order()`

3. **Image Parameters**:
   - `ImageParams` class controls display options including:
     - Zoom/pan settings with `zoom_pan_matrix` and `zoom_key` for syncing views
     - Colormap settings for visualizing single-channel images
     - Interactive options (mouse controls, grid display, pixel info)
     - Watched pixels functionality

4. **Inspector Functionality**:
   - `inspector_add_image()`: Add images to a collection
   - `inspector_show()`: Display all collected images in a single view

5. **Colormap Support**:
   - Apply color mappings to single-channel images
   - `available_colormaps()` returns list of supported colormaps
   - Configure mapping with `ColormapSettingsData`

## Basic Example

```python
from imgui_bundle import immvision, immapp, imgui

# Initialize color order at application start
immvision.use_rgb_color_order()

# Create an ImageParams object to maintain state
params = immvision.ImageParams()
params.zoom_key = "my_key"  # For synchronized views
params.show_options_panel = True  # Show options panel by default

# Inside your GUI function:
def gui_function():
    # Display image with full features
    immvision.image("Image Label", image_data, params)
    
    # Or simple display
    immvision.image_display("Simple Image", image_data)
```

## Demo Examples

ImmVision comes with several demo examples that showcase its capabilities:

1. Basic display: `demos_python/demos_immvision/demo_immvision_display.py`
2. Inspector usage: `demos_python/demos_immvision/demo_immvision_inspector.py`
3. Image processing: `demos_python/demos_immvision/demo_immvision_process.py` 
4. Linked views: `demos_python/demos_immvision/demo_immvision_link.py`

These demos show how to effectively use ImmVision for various image visualization and analysis tasks.

# Follow up

Please study the documentation you were provided (especially the links marked with "please do read").

Then, provide a quick summary of what you understood. 

You then should be ready to help users with their questions.

**Do not forget to consult the links that were marked with "if needed" if you need to help users with specific questions on the APIs**

