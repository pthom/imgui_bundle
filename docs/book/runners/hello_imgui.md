# Hello ImGui

Dear ImGui Bundle includes [Hello ImGui](https://github.com/pthom/hello_imgui), which is itself based on ImGui. "Hello ImGui" can be compared to a starter pack that enables to easily write cross-platform Gui apps for Windows, macOS, Linux, iOS, and emscripten.

## API & Usage

**RunnerParams**

Applications can be fully configured via `RunnerParams` (this incudes window size, app icon, fps settings, etc.).
`hello_imgui.get_runner_params()` will return the runnerParams of the current application.

See the [Application parameters doc](https://pthom.github.io/hello_imgui/book/doc_params.html).

**API**

See the "Hello ImGui" [API doc](https://pthom.github.io/hello_imgui/book/doc_api.html).

## Features

**Multiplatform utilities**

* Truly multiplatform: Linux, Windows, macOS, iOS, Android, emscripten (with 4 lines of CMake code)
* Easily embed assets on all platforms (no code required)
* Customize app settings (icon and app name for mobile platforms, etc.- no code required)
* Customize application icon on all platforms (including mobile and macOS - no code required)

**Dear ImGui Tweaks**

* Power Save mode: reduce FPS when idling
* High DPI support: scale UI according to DPI, whatever the platform
* Advanced layout handling: dockable windows, multiple layouts
* Window geometry utilities: autosize application window, restore app window position
* Theme tweaking: extensive list of additional themes
* Support for movable and resizable borderless windows
* Advanced font support: icons, emojis and colored fonts
* Integration with ImGui Test Engine: automate and test your apps
* Save user settings: window position, layout, opened windows, theme, user defined custom settings
* Easily add a custom 3D background to your app

**Backends**

* Available platform backends: SDL2, Glfw3
* Available rendering backends: OpenGL3, Metal, Vulkan, DirectX

:::{note}
The usage of Hello ImGui is optional. You can also build an imgui application from scratch, in C++ or in python (see [python example](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/demos_immapp/imgui_example_glfw_opengl3.py))
:::

:::{tip}
HelloImGui is fully configurable by POD (plain old data) structures. See their [description](https://pthom.github.io/hello_imgui/book/doc_params.html)
:::

## Advanced layout and theming with Hello ImGui:

See the demo named "demo_docking", which demonstrates:

* How to handle complex layouts: you can define several layouts and switch between them: each layout which will remember the user modifications and the list of opened windows
* How to use theming
* How to store you own user settings in the app ini file
* How to add a status bar and a log window
* How to reduce the FPS when idling (to reduce CPU usage)

Links:

* See [demo_docking.py](https://github.com/pthom/imgui_bundle//blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py)
* See [demo_docking.cpp](https://github.com/pthom/imgui_bundle//blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp)
* [Run this demo online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html)
* See a [short video explanation](https://www.youtube.com/watch?v=XKxmz__F4ow) about layouts on YouTube

