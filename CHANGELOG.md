Version numbers are synced between hello_imgui and imgui_bundle.

# v1.5.0

### ImGui:
* Updated ImGui to v1.90.5-docking
* Added [support for StackLayout](https://github.com/pthom/imgui/blob/a178a6c98fc877f0d9d4dfd6063bae15d41c14d0/imgui_stacklayout.h) (by @thedmd)
* Warn if users reuse an ID (cf https://github.com/ocornut/imgui/issues/7669)

### Hello ImGui
See changes in [Hello ImGui v1.5.0-rc1](https://github.com/pthom/hello_imgui/releases/tag/v1.5.0-rc1)
* add FontDpiResponsive
* add OpenGlOptions
* add null backends
* Improved text rendering on windows (via improved antialiasing)
* Can set OpenGL options in hello_imgui.ini in any parent folder
* add InputTextResizable & WidgetWithResizeHandle
* Logger: use less vertical space
* add Push/PopTweakedTheme (different windows can have different themes)
* add callback PostRenderDockableWindows
* Polish Themes

### Libraries

#### immvision
  * fixup Custom version of cv::warpAffine for small sizes
  * ImmVision::Image is now resizable / added ImmVision::ImageDisplayResizable
  * fix icon buttons size
  * Add option ResizeKeepAspectRatio: when resizing an image, the widget will keep the aspect ratio of the image

#### imgui-knobs
  * can drag knob horizontally or vertically

#### ImPlot
  * Add Python binding for colors (cf https://github.com/pthom/imgui_bundle/issues/221)

### imgui-node-editor
  * Add ForceWindowContentWidthToNodeWidth: ImGui::TextWrapped(), ImGui::Separator(), and ImGui::SliderXXX can now fit inside a Node. See proposed fix to @thedmd here: https://github.com/thedmd/imgui-node-editor/issues/298
  * The theme of the node editor can be derived and adapted automatically from ImGui Theme (see UpdateNodeEditorColorsFromImguiColors)

### Python
* imgui_fig is now resizable
* Added binding for ColorPicker4
* Added mathematical operators for ImVec2, ImVec4, ImColor
* add pickle support for ImVec2, ImVec4, ImColor
* Add eq operator to ImVec2/4/ImColor bindings
* add pydantic support for ImVec2, ImVec4, ImColor

### Build
* Add [CMake options](https://github.com/pthom/imgui_bundle/blob/6b0132a4bf6bfb82b7eb90e15ba3db52b0daa778/CMakeLists.txt#L119-L128) to disable some libraries


# v1.3.0

### New libraries
* Added [NanoVG](https://github.com/memononen/nanovg): see [python bindings](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/nanovg.pyi), code of [python demos](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/demos_nanovg), code of [C++ demos](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_cpp/demos_nanovg), online [full demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_nanovg_full.html), online [simple demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_nanovg_heart.html), and [API for integration with ImGui](https://github.com/pthom/imgui_bundle/blob/main/external/nanovg/nvg_imgui/nvg_imgui.h). Works on Linux, Windows, macOS, emscripten, iOS and Android (OpenGL only).

### Bundle
* Update imgui to v1.90.1-docking
* Update implot, imgui_test_engine, imgui-node-editor

### Python
* Release the Python GIL when rendering: improve multithreading performance (see [#171](https://github.com/pthom/imgui_bundle/issues/171))
* Fix an issue under Ubuntu where cibuildwheel binary wheels did not work (see [#170](https://github.com/pthom/imgui_bundle/issues/170))

### Hello ImGui
* Added EdgeToolbars: see [definition](https://github.com/pthom/hello_imgui/blob/3a279ce7459b04a4c2e7460b844cbf354833964e/src/hello_imgui/runner_callbacks.h#L72-L102), [callbacks](https://github.com/pthom/hello_imgui/blob/3a279ce7459b04a4c2e7460b844cbf354833964e/src/hello_imgui/runner_callbacks.h#L140-L147), [example usage](https://github.com/pthom/hello_imgui/blob/3a279ce7459b04a4c2e7460b844cbf354833964e/src/hello_imgui_demos/hello_imgui_demodocking/hello_imgui_demodocking.main.cpp#L694-L714), and [demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html)
* Callbacks: add [EnqueuePostInit, EnqueueBeforeExit, PostInit_AddPlatformBackendCallbacks](https://pthom.github.io/hello_imgui/book/doc_params.html#runnercallbacks)
* Add [renderer_backend_options](https://pthom.github.io/hello_imgui/book/doc_params.html#renderer-backend-options)
* Add support for Extended Dynamic Range (EDR) on macOS : see [PR](https://github.com/pthom/hello_imgui/pull/89). Added [demo / EDR](https://github.com/pthom/hello_imgui/tree/master/src/hello_imgui_demos/hello_edr) - Only works with Metal
* Test Engine: can re-call params.callbacks.RegisterTests
* rememberEnableIdling default=false (true is too surprising)
* emscripten: Use webgl2 / GLES3

### Fixes
* Fix usage of `ShowIdStackTool` without ImGui Test Engine (see [#166](https://github.com/pthom/imgui_bundle/issues/166))
* ImGuiColorTextEdit: added bindings for GetSelection / Fixed keyboard selection (see [#169](https://github.com/pthom/imgui_bundle/issues/169))


# v1.2.1

### Hello ImGui
* Added nice [documentation pages](https://pthom.github.io/hello_imgui)
* Uses [Freetype for font rendering](https://github.com/pthom/hello_imgui/blob/549c205dd3ca98f18fcf541a2ebbfc5abdd10410/CMakeLists.txt#L96-L106)
* Improved [Font Loading utility](https://github.com/pthom/hello_imgui/blob/549c205dd3ca98f18fcf541a2ebbfc5abdd10410/src/hello_imgui/hello_imgui_font.h#L13-L62)
* Added support for Colored font and Emoji fonts ([Demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html))
* Can [fully customize the menu bar](https://pthom.github.io/hello_imgui/book/doc_api.html#customize-hello-imgui-menus)

### Backends
* Review [CMake options](https://github.com/pthom/hello_imgui/blob/549c205dd3ca98f18fcf541a2ebbfc5abdd10410/CMakeLists.txt#L56-L91) for backend selection
* Add support for [Metal rendering backend](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/internal/backend_impls/rendering_metal.mm) (C++ only, macOS only)
* Add support for [Vulkan rendering backend](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/internal/backend_impls/rendering_vulkan.cpp) (C++ only, Linux, Windows, macOS)
* Add support for [DirectX11 rendering backend](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/internal/backend_impls/rendering_dx11.cpp) (C++ only, Windows)
* Add support for [DirectX12 rendering backend](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/internal/backend_impls/rendering_dx12.cpp) (C++ only, Windows). Experimental
* Deprecated CMake options IMGUI_BUNDLE_WITH_GLFW and IMGUI_BUNDLE_WITH_SDL
  (use HELLOIMGUI_USE_GLFW_OPENGL3 and HELLOIMGUI_USE_SDL_OPENGL3 instead)
* updated imgui to v1.90-docking

### iOS
* Add [LaunchScreen.storyboard](https://github.com/pthom/hello_imgui_template/tree/0e2b53d96b5de5cfa3ccbf4d3c823a07afcb947b/assets/app_settings/apple/Resources/ios) for iOS: apps are now full screen
* Add support for EdgeInsets (handle safe area on iOS, i.e. the notch): see [here](https://github.com/pthom/hello_imgui/blob/549c205dd3ca98f18fcf541a2ebbfc5abdd10410/src/hello_imgui/app_window_params.h#L205-L214) and [here](https://github.com/pthom/hello_imgui/blob/549c205dd3ca98f18fcf541a2ebbfc5abdd10410/src/hello_imgui/app_window_params.h#L138-L145)

### Android
* Hello ImGui now compatible with Android (including assets, app icon, etc.): see instruction [here in the Starter template](https://github.com/pthom/hello_imgui_template#build-for-android) and [here](https://github.com/pthom/hello_imgui_template#assets-folder-structure)

### Python
* Can plot Matplotlib figures in Python: see [demo](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_matplotlib.py) and [imgui_fig](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_fig.py)
* Added [imgui_ctx](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_ctx.py): python context manager for imgui.begin / imgui.end, etc (lots)
* Show python & C++ code in the ImGui Demo window (see "Dear ImGui" tab in the [interactive manual](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html))
* Added bindings for imgui [AddPolyline / AddConvexPolyFilled](https://github.com/pthom/imgui_bundle/blob/7c7f31944edd3cf92e040226a73eda7b6e4e5c5f/bindings/imgui_bundle/imgui/__init__.pyi#L9283C23-L9290)
* Added bindings for imgui [IniFileName and LogFilename](https://github.com/pthom/imgui_bundle/blob/7c7f31944edd3cf92e040226a73eda7b6e4e5c5f/bindings/imgui_bundle/imgui/__init__.pyi#L7943-L7946), WindowName
* Added bindings for [ImGuiInputTextCallback](https://github.com/pthom/imgui_bundle/blob/7c7f31944edd3cf92e040226a73eda7b6e4e5c5f/bindings/imgui_bundle/imgui/__init__.pyi#L10453-L10463) and ImGuiSizeCallback (also see [this](https://github.com/pthom/imgui_bundle/blob/7c7f31944edd3cf92e040226a73eda7b6e4e5c5f/bindings/imgui_bundle/imgui/__init__.pyi#L255C1-L256))
* [Python backends](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends): use new ImGui mouse API. Corrected pygame backend keymap

### Bundle
* Added [starter template repo](https://github.com/pthom/imgui_bundle_template) as quickstart for C++ apps


# v1.1.0

### 3D
* Added callback `runnerParams.callbacks.CustomBackground`: display any 3D scene in the background of the app: see [doc](https://pthom.github.io/imgui_bundle/quickstart.html#_custom_3d_background)
  ![Custom background](bindings/imgui_bundle/doc/doc_images/demo_custom_background.jpg)

### App deployment
* Added support for macOS application bundles
* Added option to specify where settings are saved: `RunnerParams.iniFolderType` can be set to: `CurrentFolder`, `AppUserConfigFolder`, `DocumentsFolder`, `HomeFolder`, `TempFolder`, `AppExecutableFolder`.
* Support for Application Icon: the file `assets/app_settings/icon.png` will be used to generate the window icon (C++, Python), and app icon (C++ only) for any platform. See assets structure below:
```
assets/
├── world.png                         # A custom asset
├── app_settings/                     # Application settings
│         ├── icon.png                # This will be the app icon, it should be square
│         │                           # and at least 512x512. It will  be converted
│         │                           # to the right format, for each platform.
│         ├── apple/
│         │         └── Info.plist    # macOS and iOS app settings
│         │                          # (or Info.ios.plist + Info.macos.plist)
├── fonts/
│         ├── DroidSans.ttf               # Default fonts
│         └── fontawesome-webfont.ttf     #     used by HelloImGui
│         ├── Roboto
│         │    ├── Roboto-Bold.ttf        # Font used by Markdown
│         │    ├── Roboto-BoldItalic.ttf
│         │    ├── Roboto-Regular.ttf
│         │    └── Roboto-RegularItalic.ttf
│         ├── SourceCodePro-Regular.ttf
├── images
│         └── markdown_broken_image.png
```


### Python bindings
* Added initial support for full python backends:
  * see [bindings/imgui_bundle/python_backends](bindings/imgui_bundle/python_backends)
  * see https://github.com/pthom/imgui_bundle/issues/142
  * see full example with glfw3 + OpenGL3: [bindings/imgui_bundle/python_backends/examples/example_python_backend_glfw3.py](bindings/imgui_bundle/python_backends/examples/example_python_backend_glfw3.py)
  * _Note: ImmApp and Hello ImGui provide advanced support for anti-aliased fonts and HighDPI. This is not provided by python backends: you will have to implement it yourself_
* Improved ImGui bindings: added bindings for `ImDrawData` and `ImDrawList` arrays
  (see https://github.com/pthom/imgui_bundle/issues/142)

### CMake
* hello_imgui_add_app and imgui_bundle.add_app can now accept ASSETS_LOCATION as a parameter e.g. `hello_imgui_add_app(my_app file1.cpp file2.cpp ASSETS_LOCATION my_assets)`


# v1.0.0-beta1
### Added support for ImGui Test Engine
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_testengine.jpg" width=200 />

ImGui Test Engine is a Tests & Automation Engine for Dear ImGui.

* Can be used with python, and C++ (all platforms, incl emscripten). See [python bindings](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/test_engine.pyi) declarations (stubs).
* Enabled by default inside ImGui Bundle. Needs to be enabled manually when using Hello ImGui.
* Lots of work on making ImGui Test Engine's coroutines (thread based) compatible with Python and emscripten
* ImGui Test Engine is now used to run interactive automations in the [interactive manual](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html) (click on the "Show me" buttons)
* Added specific demo and doc

_Note: See [Dear ImGui Test Engine License](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt). (TL;DR: free for individuals, educational, open-source and small businesses uses. Paid for larger businesses)_

### New library
* Added new library: ImCoolBar
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_coolbar.jpg" width=200>

### Doc
* Completely reviewed the [doc site](https://pthom.github.io/imgui_bundle/).
* Added ["quickstart & example"](https://pthom.github.io/imgui_bundle/quickstart.html) section, with lots of examples
* Added & reviewed [development doc](https://pthom.github.io/imgui_bundle/devel_docs/index.html)
* Added specific [doc / bindings maintenance](https://pthom.github.io/imgui_bundle/devel_docs/bindings.html) (and how to add bindings for new libraries)

### Misc
* Python bindings stubs: add @overload everywhere when required
* cmake: add options to run sanitizers (no warning given by any of them at this moment)
* demo_logger: add logs at startup
* implot python bindings: add plot_bar_groups & plot_pie_chart
* update imgui_toggle (after merged PRs from imgui_bundle)
* update HelloImGui: add callback BeforeImGuiRender
* update ImmVision: can call gladLoadGl if needed (fix #134)
* add demo imgui_example_glfw_opengl3.cpp


# v0.9.0
* Added wheels for python3.12
Submodule updates:
* imgui-node-editor: fix suspend/resume issue
* HelloImGui::DockingParams::focusDockableWindow() can show a window tab


# v0.8.8
* update imgui to v1.89.6 and implot to v0.17
* Enable 32 bits ImDrawIdx for ImPlot
Submodules changes:
* ImmVision: fix exit sequence, can save colormap image
* imgui-node-editor: fixes
* HelloImGui: basic apps can run without font assets / can set docking options for main dock space


# v0.8.7
### Updates and new features
* ImGui: updated imgui to v1.89.6 (May 2023)
* ImGui: python bindings now can use [SDL2](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/imgui_example_sdl2_opengl3.py) (glfw is of course still supported, and remains the default with Hello ImGui)
* ImGui: Add python bindings for drag&drop
* HelloImGui: can now handle several layouts and save settings per layout (see details below)
* HelloImGui: can now store user defined settings in the ini file
* HelloImGui: now remembers user choices for the theme, status bar, and fps throttling
* HelloImGui: handle utf8 filenames for assets loading
* ImGuiColorTextEdit is now based on @santaclose [fork](https://github.com/santaclose/ImGuiColorTextEdit)
* immvision bindings: use shared memory (between python and C++) for images
* ImPlot bindings: Add support for colormap in implot python bindings
* ImPlot bindings: Add support for heatmaps

As always, an online interactive manual is available
[<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/doc/bindings/imgui_bundle/doc/doc_images/badge_interactive_manual.png" height=20>](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)&nbsp;&nbsp;&nbsp;[<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/doc/bindings/imgui_bundle/doc/doc_images/badge_view_docs.png" height=20>](https://pthom.github.io/imgui_bundle)

### More details about layouts handling with Hello ImGui:

![Layout demo](https://traineq.org/ImGuiBundle/HelloImGuiLayout.gif)

Each layout has a different spatial layout and can contain a different list of windows. Each layout also remembers the user modifications to this given layout, as well as the  list of opened windows.

See [this online emscripten demo](https://traineq.org/ImGuiBundle/emscripten/bin/demo_docking.html)  of the docking and layout, the  [C++ demo code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp), and [python demo code](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py)

For more explanations on how to handle complex layouts, see this [video explanation on YouTube](https://www.youtube.com/watch?v=XKxmz__F4ow) (5 minutes)


# v0.8.6
Please use v0.8.7 instead


# v0.8.5
Hello ImGui and ImmApp usability improvements:
* customize menu App
* Docking Layout: keep user preferences
* improve windows initial layout


# v0.8.3
Added python bindings for implot_internal

Minor improvements:
- Improve font rendering
- Improve emscripten idling mode
- Review main theme (DarculaDarker) to make it easier on the eyes


# v0.8.2
* Autoresize window post startup
* Corrected notebook rendering


# v0.8.1
* correct launch demo_node_editor_basic


# v0.8.0
* markdown: render code blocks with text editor, and make them easily copyable
* add lots of demos
* add doc / ascii_doc
* add emscripten interactive manual
* add immapp::snippets
* add portable_file_dialogs


# v0.7.2
* Improved doc and notebook support


# v0.7.1
*   Improved support for High DPI in third parties
*   Improved demos
*   Markdown now support code blocks


# v0.7.0 (work in progress)
* Added support for [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo)
  * all components available in C++ (gizmo, curve, graph, sequencer, etc.)
  * added [ImGuizmoPure](external/ImGuizmo/ImGuizmoPure): C++ wrappers around existing api with clearly marked inputs and outputs
  * for python: ported pure API
  * added set of twin demos showing usage [with C++](bindings/imgui_bundle/demos_cpp/demos_imguizmo) and [with python](bindings/imgui_bundle/demos/demos_imguizmo). A good example showing how to port features between C++ and python.
  * the following items could not be ported to python (making a pure wrapper failed): ImGradient, GraphEditor, Sequencer
* Added support for [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect), a texture inspector.
  * Added support for codeless init of imgui_tex_inspect when using ImGuiBundle runner (future ImmApp), thanks to AddOnParams::withTexInspect
* 6ef5df64: added imgui.set_io_ini_filename() & imgui.set_io_log_filename()
  Manual binding for ImGuiIO::IniFilename (naked const char* pointer)
* 778aabf3: Added imgui_bundle.em_size and visible_font_size():
In order to scale your widgets properly on all platforms, use multiples of this size.
(on MacOS with retina FontGlobalScale can be equal to 2)
(EmSize is an alias for VisibleFontSize)
* f6ae2072: generate named constructors if there is *no* user defined constructors
* 19ca013a: remove ImGui prefix from classes and enums => lots of API changes
* f9210578: ImPlot bindings: remove prefix ImPlot from classes and enums
* hardened stub typings with mypy
* imgui.backends: replace open_gl3 by opengl3
* immvision module now stable
* Lots of work on the CI and wheel generation


# v0.6.6
#### Added Immvision (image debugger and analyzer utility)
immvision will be compiled if OpenCV is available.
immvision is not available by default on the pip bindings.

To add them, compile from source [after having installed conan](https://github.com/pthom/imgui_bundle/blob/v0.6.6/external/immvision/find_opencv.cmake#L5)

#### Added theming
* [Demo](https://www.youtube.com/watch?v=Hhartw0cUjg)
* [API](https://github.com/pthom/imgui_bundle/blob/v0.6.6/bindings/imgui_bundle/hello_imgui.pyi#L375)
* Default theme is now a variation on Darcula

#### Improve ImGui & Glfw,  low level integration
* glfw is now linked as a dynamic library
* support [any glfw callback](https://github.com/pthom/imgui_bundle/blob/v0.6.6/bindings/imgui_bundle/demos/demo_imgui_bundle.py#L119)
* added low level binding for [imgui backends](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_backends.pyi) glfw and OpenGl3
* imgui apps can now be written from scratch : as an example, ported [imgui/examples/example_glfw_opengl3/main.cpp](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_opengl3/main.cpp) to python [imgui_example_glfw_opengl3.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos/imgui_example_glfw_opengl3.py)

**Full Changelog**: https://github.com/pthom/imgui_bundle/compare/v0.6.5...v0.6.6


# v0.6.5
Lots of additions
* Fine tune window geometry:
  * save & restore window position & size
  * support for full screen
  * auto size window from its inner widgets
  * handle high dpi (especially on windows)
* Crisp fonts on MacOS
* Backend support: can switch between sdl and glfw
* Added python support to ImGuiColorTextEdit
* Powersave: reduce app fps when idle
* Add toggle switches from https://github.com/cmdwtf/imgui_toggle.git
* Support for jupyter notebook (with inline screenshots), via `imgui_bundle.run_nb`
  (see https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos/notebooks/demo_notebook.ipynb)

**Full Changelog**: https://github.com/pthom/imgui_bundle/compare/v0.6.4...v0.6.5
