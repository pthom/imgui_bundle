*Version numbers are synced between "Dear ImGui", "Hello ImGui" and "Dear ImGui Bundle"*

# v1.92.XXX (ongoing)

# v1.92.4

This version is based on ImGui v1.92.3, and brings some small fixes.

* InputTextMultiline: when inside imgui-node-editor, improve handling of single preview
* imgui-node-editor: solve clipping issue which occur when a popup is open inside a node

# v1.92.3

## Updates to libraries
### ImGui:
- Updates imgui and imgui_test_engine to v1.92.3
### hello_imgui:
- update to v1.92.3
- add SetLoadAssetFileDataFunction (and python binding): a way to customize asset loading
### imgui_md:
- fix line wrapping (thanks to @bgribble). cf #366
### imgui-knobs, ImGuizmo, imgui_toggle:
- update to latest version
### ImGuiColorTextEdit:
- update to latest version (from santaclose fork)

## Python bindings:
### ImGui bindings:
* ImGui Enums now use 'enum.IntFlag'
  (This impacts only the typing checks, not the runtime behavior)
  This means that you may replace code like:
```python
imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_decoration.value
```
with:
```python
imgui.WindowFlags_.no_collapse | imgui.WindowFlags_.no_decoration
```
* imgui.push_font (accepts optional font)
* Improve typing for ImVec2 and ImVec4 (use different protocols. Thanks to @joegnis)
### Pure Python Backends
## Pure Python Backends
* Fix pygame backend (thanks Dom Ormsby)
* Fix issue when pasting with glfw backend (thanks to @sunsigil)
### Other
* ImGuizmo:handle deltaMatrix / document Manipulate API


# v1.92.0

*Starting with v1.92.0, version numbers are now synced between "Dear ImGui", "Hello ImGui" and "Dear ImGui Bundle"*


## ImGui

> [v1.92.0: Scaling fonts & many more (big release)](https://github.com/ocornut/imgui/releases/tag/v1.92.0)

- Many Font related changes: this release brings many changes on the ImGui side (v1.92.0): do read the [release notes for ImGui v1.92.0](https://github.com/ocornut/imgui/releases/tag/v1.92.0)
  TLDR: Fonts may be rendered at any size. Glyphs are loaded and rasterized dynamically. No need to specify ranges, prebake etc. GetTexDataAsRGBA32() is now obsolete.

## Python bindings

* Potentially breaking change for extern pure Python backends: `font_atlas_get_tex_data_as_rgba32` was removed (read the advice below)
* Font-related changes, following ImGui [v1.92.0](https://github.com/ocornut/imgui/releases/tag/v1.92.0)
- Fix ImPlot stubs (thanks @tlambert03)
- Fix imgui_ctx and imgui_node_ctx
- pure python backends: split opengl implems,  implement texture update in python pure opengl backends
- imgui bindings => publish texture related infos

### Advice for extern pure Python Backends (wgpu, etc.)
Since v1.92, `font_atlas_get_tex_data_as_rgba32` was removed. Backends will need to be adapted by implementing support for dynamic fonts (preferred)

> Extract from ImGui doc: ImGui Version 1.92.0 (June 2025), added texture support in Rendering Backends, which is the backbone for supporting dynamic font scaling among other things. In order to move forward and take advantage of all new features, support for ImGuiBackendFlags_RendererHasTextures will likely be REQUIRED for all backends before June 2026.

Read ImGui backend doc: [flag `ImGuiBackendFlags_RendererHasTextures` (1.92+)](https://github.com/ocornut/imgui/blob/master/docs/BACKENDS.md) (read the part "Rendering: Adding support for ImGuiBackendFlags_RendererHasTextures (1.92+)").
For inspiration, look at
```
    def _update_texture(self, tex: imgui.ImTextureData):
```
inside ImGui Bundle (bindings/imgui_bundle/python_backends/opengl_base_backend.py)


## Pyodide
- Added support for Pyodide


# v1.6.3

## ImGui
- update imgui to v1.91.9b
- Python: adapt API for ImFont:: CalcWordWrapPositionA  (cf #308)

## Fixes
- update imgui_md (fix soft break handling). Cf #306
- ImGui / Python: adapt API for ImFont:: CalcWordWrapPositionA  (cf #308)
- Fix documentation rendering (cf #316)
- Fixes for compat with CMake 4

## ImPlot
- update implot
- Add implot_demo.py (full python transcription of implot_demo.cpp)
- add demo_implot_stock.py
- python Bindings: improve  setup_axis_ticks

## ImPlot3d
- Update implot3d: added PlotImage & bindings
- implot3d_demo.py: provide nice demo textures
- add implot3d_demo.py: full transcription of implot3d_demo.cpp
- improve python bindings
- adapt bindings for PlotMesh (cf #320)
- manual bindings for  setup_axis_ticks

## Pure Python Backends
- Review keyboard handling
- Sdl: handle SDL_GL_MakeCurrent errors
- Add SDL3 python backend
- Add an example using wgpu (WebGPU for Python)

## ImmVision
- update immvision (fix for compat with OpenCV 4.11)

## ImGuizmo
- update ImGuizmo to v1.91.3
- Fix customization of styles (cf #329)

## ImGuiColorTextEdit
- Update ImGuiColorTextEdit (from santaclose fork)

## ImGuiMd
- fix soft break handling. Cf https://github.com/pthom/imgui_bundle/issues/306


# v1.6.2

## New library: ImPlot3D
- The excellent [ImPlot3D](https://github.com/brenocq/implot3d) library is now included!

## Fixes
- Fix [#293](https://github.com/pthom/imgui_bundle/issues/293): IM_ASSERT( g.CurrentDpiScale > 0.0f && g.CurrentDpiScale < 99.0f )
- Fix initial window positioning / HighDPI on windows (demo window origin was offscreen)

## Build
- Some fixes for conda-forge package

## Python
- make it possible to recover from exceptions in notebooks
- preliminary work on pyodide support

# v1.6.1

### ImGuizmo

* **Breaking change on ImGuizmo Python API**: Added classes Matrix3/6/16, modifiable by manipulate and view_manipulate
See [changes in demo_gizmo.py](https://github.com/pthom/imgui_bundle/commit/a455607381eeaa65e05cfa7eac39f68e516b1ec4) to see how to adapt to the new API
Basically:
- use `gizmo.Matrix3` / `Matrix6` / `Matrix16` instead of `np.array`
- `gizmo.manipulate` and `view_manipulate` will modify the matrices they receive
- if using glm, you will to need to convert to Matrix16, see `glm_mat4x4_to_float_list` in demo_gizmo.py

### Python
- fix bindings for implot.plot_bar_groups
- sdl pure backend: fix get_clipboard_text
- patches for [conda-forge package](https://github.com/conda-forge/imgui-bundle-feedstock) (in preparation)

### iOs
- Improved font rendering on iOS (use static freetype, use retina resolution)

# v1.6.0

### ImGui
* Updated ImGui to v1.91.5

### Hello ImGui: updated to v1.6.0b
* SVG Font rendering: plutosvg replaces lunasvg (option HELLOIMGUI_USE_FREETYPE_PLUTOSVG on by default)
* Added AddDockableWindow / RemoveDockableWindow
* demo_docking: better demonstration / theme customization
* Add `HelloImGui::ManualRender: a namespace that groups functions, allowing fine-grained control over the rendering process
* Work on pyodide integration (for ImGui Bundle)
* Improve font rendering on iOS

### Node editor
* better handle popup placement and child windows: see https://github.com/thedmd/imgui-node-editor/issues/310
* InputTextMultiline compatible with imgui-node-editor
* Node theme colors will try to be coherent with the main theme

### ImGuiMd
* Add ImGuiMd::GetFont(const MarkdownFontSpec& fontSpec)

### ImmApp
* Add namespace Immapp::ManualRender: functions allowing fine-grained control over the rendering process

### ImmVision
- **Breaking Change - October 2024**: Color Order Must Be Set
  ImmVision now requires you to explicitly set the color order (RGB or BGR) at the start of your program.
  To configure the color order, you must call one of the following **once** before displaying images:
  - In C++: `ImmVision::UseRgbColorOrder()` or `ImmVision::UseBgrColorOrder()`
  - In Python: `immvision.use_rgb_color_order()` or `immvision.use_bgr_color_order()`
  - To enforce a temporary color order, use `ImmVision::PushColorOrderBgr/Rgb()` and `ImmVision::PopColorOrder()`.
  This change ensures that you are explicitly aware of the color order used throughout your program.
  If the color order is not configured, an error will be thrown when attempting to display images.
  Note: The `IsColorOrderBGR` member in `ImageParams` and the corresponding `isBgrOrBgra` parameter in `ImageDisplay` have been **removed**.
* Publish GlTexture in the API
* Refuse zoom if too extreme

### Python bindings
#### **Switched binding library from pybind11 to nanobind - Nov 2024**:
This change should be almost transparent to users. However, if you encounter any issues, please report them.
#### Support Python 3.13
* Binary wheels are provided for Python 3.11, 3.12, and 3.13 (3.10 is still supported, building from source)
#### Other
* python glfw_backend: updated clipboard handling to new api
* enum Key bindings:  remove prefix im_gui_ in values
* Flags enums (InputTextFlagsPrivate_, TreeNodeFlagsPrivate_, etc.): remove unwanted prefixes
* ImFontGlyph: publish get_codepoint(), is_visible(), is_colored()
* imgui_fig: let the user change matplotlib renderer
* add stubs for ImVec2/4 math operators (fix #267)
* pyglet backend: fix version checking (thks @DragonMoffon)
* implot: fix binding for setup_axis_links()
* delay loading PIL and matplotlib to make startup faster
* Initial efforts to support pyodide

### Demos
* demo docking: improve demo / setup customized theme
* demos python: do not require opencv (use pillow to load images)
* suppressed demos / ImGuizmo curve edit (we only maintain the 3D gizmo compatibility)


# v1.5.0

### ImGui:
* Updated ImGui to v1.90.9-docking
* Added support for [StackLayout](https://github.com/ocornut/imgui/pull/846): ImGui::BeginHorizontal & ImGui::BeginVertical (by @thedmd)
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
