# Hello ImGui - Starter pack

ImGui Bundle includes [Hello ImGui](https://github.com/pthom/hello_imgui), which is itself based on ImGui. \"Hello ImGui\" can be compared to a starter pack that enables to easily write cross-platform Gui apps for Windows, macOS, Linux, iOS, and [emscripten](https://en.wikipedia.org/wiki/Emscripten).

## API

See the \"Hello ImGui\" [API doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md). Also consult the doc on how to build [DPI aware](https://github.com/pthom/hello_imgui/tree/master/src/hello_imgui/dpi_aware.h) applications.

## Features

-   Full multiplatform support: Windows, Linux, OSX, iOS, Emscripten, Android (poorly supported). See demo [video](https://traineq.org/HelloImGui_6_Platforms.mp4)

-   Power Save mode: reduce FPS when application is idle (see [RunnerParams.fpsIdle](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/runner_params.h))

-   [DPI aware](https://github.com/pthom/hello_imgui/tree/master/src/hello_imgui/dpi_aware.h) applications (widget placement, window size, font loading and scaling)

-   Theme tweaking (see [demo video](https://www.youtube.com/watch?v=4f_-3DDcAZk), and [API](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/imgui_theme.h) )

-   Window geometry utilities: autosize, restore window position, full screen, etc. (see [WindowGeometry](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/app_window_params.h))

-   Multiplatform [assets embedding](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_assets.h)

-   Switch between Glfw or Sdl backend (see [RunnerParams.backendType](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/runner_params.h))

::: note
The usage of `Hello ImGui` is optional. You can also build an imgui application from scratch, in C++ or in python (see [python example](https://github.com/pthom/imgui_bundle/tree/doc/bindings/imgui_bundle/demos_python/demos_immapp/imgui_example_glfw_opengl3.py))
:::

::: tip
HelloImGui is fully configurable by POD (plain old data) structures. See [their description](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md)
:::
