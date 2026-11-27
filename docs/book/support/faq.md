# FAQ

Answers to questions that users asked in the GitHub issues. Each answer was checked on the current version, and links its issue for the full discussion.

## Fonts and text

### Chinese, Japanese or Korean text shows up as `???`

The bundled fonts (DroidSans, Roboto) cover Latin, Greek and Cyrillic only. Load a font that contains the glyphs you need, for example [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) or [Source Han Sans](https://github.com/adobe-fonts/source-han-sans).

Since Dear ImGui 1.92, there are no glyph ranges to configure: glyphs are rasterized on demand. Put the font in your `assets/fonts/` folder, and load it first, so that it becomes the default font:

```python
from imgui_bundle import hello_imgui, imgui, immapp

def gui():
    imgui.text("你好，世界")

def load_fonts():
    # Loaded first: it becomes the default font
    hello_imgui.load_font("fonts/NotoSansSC-Regular.otf", 16.0)
    # Optional: keep the FontAwesome icons
    icons = hello_imgui.FontLoadingParams()
    icons.merge_to_last_font = True
    hello_imgui.load_font("fonts/fontawesome-webfont.ttf", 16.0, icons)

params = hello_imgui.RunnerParams()
params.callbacks.show_gui = gui
params.callbacks.load_additional_fonts = load_fonts
immapp.run(params)
```

The demo [demo_chinese_font.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_chinese_font.py) also loads a font after startup, and works in the browser.

Issues: [#477](https://github.com/pthom/imgui_bundle/issues/477), [#196](https://github.com/pthom/imgui_bundle/issues/196) (glyph ranges, no longer needed).

## Platforms

### Raspberry Pi: "Failed to create context: GLXBadFBConfig"

The Raspberry Pi supports OpenGL 3.1, while Hello ImGui asks for OpenGL 3.3 by default. Ask for 3.1, in your code:

```python
gl = runner_params.renderer_backend_options.open_gl_options
gl.major_version = 3
gl.minor_version = 1
gl.use_core_profile = False
```

Or, without changing the code, in a `hello_imgui.ini` file placed in the app's working folder (or one of its parents):

```ini
[OpenGlOptions]
MajorVersion = 3
MinorVersion = 1
UseCoreProfile = false
```

The file [hello_imgui_example.ini](https://github.com/pthom/hello_imgui/blob/master/hello_imgui_example.ini) lists all the options. In C++, the same fields are in `runnerParams.rendererBackendOptions.openGlOptions`.

Issue: [#355](https://github.com/pthom/imgui_bundle/issues/355).

### Android: the on-screen keyboard does not open

It opens by itself since Dear ImGui Bundle v1.93: Dear ImGui's SDL2 backend now starts SDL's text input on Android when a widget wants text. On iOS, Hello ImGui does the same since the version after v1.93.

With an older version, the issue holds a workaround (a Java method that toggles the keyboard, called through JNI).

Issue: [#408](https://github.com/pthom/imgui_bundle/issues/408).

### Linux on Wayland: "Attempt to retrieve context when no valid context" (PyOpenGL)

PyOpenGL picks its platform (X11 or Wayland) at its first import. On a Wayland session it picks Wayland, while GLFW (used by Hello ImGui and ImmApp) draws through X11 (XWayland). The mismatch gives this error.

When your code uses PyOpenGL with GLFW, add this at the top of your script, before any import of OpenGL:

```python
import os
if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
    os.environ["PYOPENGL_PLATFORM"] = "x11"
```

The SDL2 and SDL3 backends create a Wayland window: they need nothing. If one still fails, run it with `PYOPENGL_PLATFORM=egl`.

Issue: [#321](https://github.com/pthom/imgui_bundle/issues/321).

### Windows: a build from source fails in a venv, with MinGW in the compiler's path

The Python bindings are built with MSVC (Visual Studio). When the `PATH` holds a MinGW or MSYS2 folder (Perl's `c\bin` folder is one), CMake may pick its compiler and fail. Remove these folders from the `PATH`, then run `pip install -v .` again.

Issue: [#332](https://github.com/pthom/imgui_bundle/issues/332).

## Windows and backends

### Change the background color, or make the window transparent

Hello ImGui fills the application window with a full screen ImGui window by default. Remove it, then set the background color:

```python
window_params = runner_params.imgui_window_params
window_params.default_imgui_window_type = (
    hello_imgui.DefaultImGuiWindowType.no_default_window)
window_params.background_color = ImVec4(0.0, 0.5, 0.5, 1.0)
```

For a transparent application window, ask GLFW for a transparent framebuffer before the run, and give the background color an alpha below 1:

```python
import glfw  # import glfw after imgui_bundle

glfw.init()
glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
```

Do not call OpenGL in the GUI function to clear the screen. To draw your own background with OpenGL, use the `custom_background` callback (see [demo_custom_background.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py)).

Issue: [#173](https://github.com/pthom/imgui_bundle/issues/173).

### Maximize or minimize the window from Python

`glfw_utils.glfw_window_hello_imgui()` returns the GLFW window that Hello ImGui created. Any GLFW function then works on it:

```python
from imgui_bundle import hello_imgui, imgui, glfw_utils
import glfw

def gui():
    if imgui.button("Maximize"):
        glfw.maximize_window(glfw_utils.glfw_window_hello_imgui())

glfw.init()  # needed by glfw_utils.glfw_window_hello_imgui
hello_imgui.run(gui)
```

Issues: [#322](https://github.com/pthom/imgui_bundle/issues/322), [#355](https://github.com/pthom/imgui_bundle/issues/355).

### Several app windows at once, or a GUI in a thread

One process runs one Hello ImGui app, on its main thread. Dear ImGui keeps global state, and on macOS, windows can only be created on the main thread.

- *Several independent GUIs*: run each one in its own process, with `multiprocessing`.
- *Several windows in one app*: use ImGui windows, docking, or viewports (windows that leave the main window).
- *Long work beside the GUI*: run the work in a thread, and keep the GUI on the main thread. See [Async and threads](../python/python_async.md).

Issue: [#223](https://github.com/pthom/imgui_bundle/issues/223).

### Docking: a minimal layout, and windows created at runtime

The docking demo is the template: [demo_docking.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py).

- A layout rearranged by the user is restored at the next start. To always start with the default layout: `runner_params.docking_params.layout_condition = hello_imgui.DockingLayoutCondition.application_start`.
- To add a window while the app runs, call `hello_imgui.add_dockable_window()`, and `hello_imgui.remove_dockable_window(name)` to remove it. Do not change `docking_params.dockable_windows` yourself while the app runs.

```python
if imgui.button("Show a new window"):
    window = hello_imgui.DockableWindow()
    window.label = "New window"
    window.dock_space_name = "MainDockSpace"
    window.gui_function = lambda: imgui.text("Created at runtime")
    hello_imgui.add_dockable_window(window, force_dockspace=False)
```

Issue: [#268](https://github.com/pthom/imgui_bundle/issues/268).

### All of Dear ImGui's style parameters, beyond the themes

Hello ImGui's themes set a full style. After them, `imgui.get_style()` gives every parameter of Dear ImGui. Change them in the `setup_imgui_style` callback:

```python
def setup_my_theme():
    # A theme first (or hello_imgui.apply_tweaked_theme)
    hello_imgui.imgui_default_settings.setup_default_imgui_style()
    style = imgui.get_style()
    style.window_rounding = 8.0
    style.item_spacing = ImVec2(6, 4)
    style.set_color_(imgui.Col_.text, ImVec4(0.8, 0.8, 0.85, 1.0))

runner_params.callbacks.setup_imgui_style = setup_my_theme
```

The function `setup_my_theme` of [demo_docking.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_docking.py) and [demo_docking.cpp](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_docking.cpp) does this with a theme.

Issue: [#258](https://github.com/pthom/imgui_bundle/issues/258).

### A 3D engine with Dear ImGui Bundle (Panda3D, ModernGL)

First choose who owns the window and its events.

- *Dear ImGui Bundle owns the window*: draw the 3D scene in the `custom_background` callback, or into a texture that `imgui.image()` shows.
- *The engine owns the window*: use one of the [pure Python backends](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends) as a model, and feed Dear ImGui with the engine's events. [moderngl-window](https://github.com/moderngl/moderngl-window) supports Dear ImGui Bundle this way.

Issue: [#253](https://github.com/pthom/imgui_bundle/issues/253).

### imgui_internal, and using your own backend

Dear ImGui's internal API is in `imgui.internal`. To run Dear ImGui without Hello ImGui, the [pure Python backends](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends) (GLFW, SDL2, SDL3, pygame, pyglet) are ready to use, with examples.

Issue: [#7](https://github.com/pthom/imgui_bundle/issues/7).

### Choose where Dear ImGui saves its settings (`ini_filename`)

`imgui.get_io().ini_filename` cannot be assigned from Python. Use `imgui.get_io().set_ini_filename("my_settings.ini")`, and `get_ini_filename()` to read it.

With Hello ImGui, set `runner_params.ini_filename` and `runner_params.ini_folder_type` instead (for example `hello_imgui.IniFolderType.app_user_config_folder`).

Issue: [#17](https://github.com/pthom/imgui_bundle/issues/17).

## Using the libraries

### File dialogs: ImFileDialog fails with a "bad_function_call"

ImFileDialog needs a function that uploads its icons to the GPU. `immapp.run()` provides it; `hello_imgui.run()` and the pure Python backends do not.

Use [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) (`imgui_bundle.portable_file_dialogs`) instead. Its dialogs are the system's own: they look native, handle high DPI screens, and also offer notifications. See [demo_widgets.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_widgets.py).

Issue: [#294](https://github.com/pthom/imgui_bundle/issues/294).

### Markdown inside a node of the node editor

A node cannot hold a child window, so a code block cannot use its usual editor there: inside a node, code blocks are drawn as plain monospace text. To make the markdown use the node's width, set this before the run:

```python
add_ons_params.with_node_editor = True
add_ons_params.with_node_editor_config = ed.Config()
add_ons_params.with_node_editor_config.force_window_content_width_to_node_width = True
```

Then give the node its width with a first item, or `imgui.dummy()`. Example: [sandbox_node_md_code.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/sandbox/sandbox_node_md_code.py).

Issue: [#281](https://github.com/pthom/imgui_bundle/issues/281).

### Test engine: simulate key presses

`ctx.key_down()`, `ctx.key_up()` and `ctx.key_press()` send key events. To type text in a field, use `ctx.key_chars()`.

```python
def test_alt_a(ctx: imgui.test_engine.TestContext) -> None:
    ctx.key_down(imgui.Key.left_alt)
    ctx.key_press(imgui.Key.a)
    ctx.key_up(imgui.Key.left_alt)
```

In the GUI, read the keys with `imgui.is_key_down()`, `imgui.is_key_pressed()` or `imgui.shortcut()`. See [demo_testengine.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_testengine.py).

Issue: [#200](https://github.com/pthom/imgui_bundle/issues/200).

### Test engine with a pure Python backend

It is not supported. The test engine runs its tests in a second thread, and Hello ImGui hands Python's GIL between the two threads from C++. Use `hello_imgui.run()` or `immapp.run()`, with `runner_params.use_imgui_test_engine = True`.

Issue: [#149](https://github.com/pthom/imgui_bundle/issues/149).

### NanoVG with a pure Python backend

It is not possible. NanoVG calls OpenGL from C++, and with a pure Python backend, OpenGL is only set up on the Python side. With Hello ImGui or ImmApp, `nanovg.create_nvg_context_hello_imgui()` gives a NanoVG context. See [demo_nanovg_full.py](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_nanovg/demo_nanovg_full.py).

Issue: [#259](https://github.com/pthom/imgui_bundle/issues/259).

### A function disappeared after an update

Dear ImGui Bundle follows the latest Dear ImGui, which sometimes renames or removes a function. Search the function's C++ name in [Dear ImGui's release notes](https://github.com/ocornut/imgui/releases): they say what replaces it. For example, `get_window_content_region_max()` (`GetWindowContentRegionMax`) was removed in Dear ImGui 1.91: use `get_cursor_screen_pos()` and `get_content_region_avail()` instead.

Each release of Dear ImGui Bundle names the Dear ImGui version it uses.

Issue: [#285](https://github.com/pthom/imgui_bundle/issues/285).

### Add another library to the bundle, or bind your own

The bindings are generated by [litgen](https://pthom.github.io/litgen/). [Adding a new library](../devel_docs/bindings_newlib.md) describes the steps.

Issue: [#182](https://github.com/pthom/imgui_bundle/issues/182).

## Packaging

### Set the app's icon, and package a Python app

There are two icons:

- *The window icon* (title bar, taskbar): put a square PNG of 256 pixels or more at `assets/app_settings/icon.png`, and call `hello_imgui.set_assets_folder()` with your assets folder. Windows and Linux only.
- *The app icon* (the executable): in Python, it comes from a packaging tool such as PyInstaller. On macOS, it is also the window icon.

[Desktop deployment](../python/desktop_deploy.md) describes both, with PyInstaller examples.

Issue: [#427](https://github.com/pthom/imgui_bundle/issues/427).
