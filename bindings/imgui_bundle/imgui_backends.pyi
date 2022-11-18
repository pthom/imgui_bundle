# type: ignore

# Note: all this code is generated *manually*

# dear imgui: Renderer Backend for modern OpenGL with shaders / programmatic pipeline
# - Desktop GL: 2.x 3.x 4.x
# - Embedded GL: ES 2.0 (WebGL 1.0), ES 3.0 (WebGL 2.0)
# This needs to be used along with a Platform Backend (e.g. GLFW, SDL, Win32, custom..)

# Implemented features:
#  [X] Renderer: User texture binding. Use 'GLuint' OpenGL texture identifier as None*/ImTextureID. Read the FAQ about ImTextureID!
#  [X] Renderer: Multi-viewport support (multiple windows). Enable with 'io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable'.
#  [x] Renderer: Large meshes support (64k+ vertices) with 16-bit indices (Desktop OpenGL only).

# You can use unmodified imgui_impl_* files in your project. See examples/ folder for examples of using this.
# Prefer including the entire imgui/ repository into your project (either as a copy or as a submodule), and only build the backends you need.
# If you are new to Dear ImGui, read documentation from the docs/ folder + read the top of imgui.cpp.
# Read online: https://github.com/ocornut/imgui/tree/master/docs

# About GLSL version:
#  The 'glsl_version' initialization parameter should be None (default) or a "#version XXX" string.
#  On computer platform the GLSL version default to "#version 130". On OpenGL ES 3 platform it defaults to "#version 300 es"
#  Only override if your GL version doesn't handle this GLSL version. See GLSL version table at the top of imgui_impl_opengl3.cpp.

# Backend API
def open_gl3_init(glsl_version: str = None) -> bool:
    pass

def open_gl3_shutdown() -> None:
    pass

def open_gl3_new_frame() -> None:
    pass

def open_gl3_render_draw_data(draw_data: ImDrawData) -> None:
    pass

# (Optional) Called by Init/NewFrame/Shutdown
def open_gl3_create_fonts_texture() -> bool:
    pass

def open_gl3_destroy_fonts_texture() -> None:
    pass

def open_gl3_create_device_objects() -> bool:
    pass

def open_gl3_destroy_device_objects() -> None:
    pass

# Specific OpenGL ES versions
##define IMGUI_IMPL_OPENGL_ES2     // Auto-detected on Emscripten
##define IMGUI_IMPL_OPENGL_ES3     // Auto-detected on iOS/Android

# You can explicitly select GLES2 or GLES3 API by using one of the '#define IMGUI_IMPL_OPENGL_LOADER_XXX' in imconfig.h or compiler command-line.
####################    </generated_from:imgui_impl_opengl3.h>    ####################


####################    <generated_from:imgui_impl_glfw.h>    ####################
# dear imgui: Platform Backend for GLFW
# This needs to be used along with a Renderer (e.g. OpenGL3, Vulkan, WebGPU..)
# (Info: GLFW is a cross-platform general purpose library for handling windows, inputs, OpenGL/Vulkan graphics context creation, etc.)
# (Requires: GLFW 3.1+. Prefer GLFW 3.3+ for full feature support.)

# Implemented features:
#  [X] Platform: Clipboard support.
#  [X] Platform: Keyboard support. Since 1.87 we are using the io.AddKeyEvent() function. Pass ImGuiKey values to all key functions e.g. ImGui::IsKeyPressed(ImGuiKey_Space). [Legacy GLFW_KEY_* values will also be supported unless IMGUI_DISABLE_OBSOLETE_KEYIO is set]
#  [X] Platform: Gamepad support. Enable with 'io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad'.
#  [x] Platform: Mouse cursor shape and visibility. Disable with 'io.ConfigFlags |= ImGuiConfigFlags_NoMouseCursorChange' (note: the resizing cursors requires GLFW 3.4+).
#  [X] Platform: Multi-viewport support (multiple windows). Enable with 'io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable'.

# Issues:
#  [ ] Platform: Multi-viewport support: ParentViewportID not honored, and so io.ConfigViewportsNoDefaultParent has no effect (minor).

# You can use unmodified imgui_impl_* files in your project. See examples/ folder for examples of using this.
# Prefer including the entire imgui/ repository into your project (either as a copy or as a submodule), and only build the backends you need.
# If you are new to Dear ImGui, read documentation from the docs/ folder + read the top of imgui.cpp.
# Read online: https://github.com/ocornut/imgui/tree/master/docs

# About GLSL version:
# The 'glsl_version' initialization parameter defaults to "#version 150" if None.
# Only override if your GL version doesn't handle this GLSL version. Keep None if unsure!

def glfw_init_for_open_gl(window_address: int, install_callbacks: bool) -> bool:
    pass

def glfw_init_for_vulkan(window_address: int, install_callbacks: bool) -> bool:
    pass

def glfw_init_for_other(window_address: int, install_callbacks: bool) -> bool:
    pass

def glfw_shutdown() -> None:
    pass

def glfw_new_frame() -> None:
    pass

# GLFW callbacks (installer)
# - When calling Init with 'install_callbacks=True': ImGui_ImplGlfw_InstallCallbacks() is called. GLFW callbacks will be installed for you. They will chain-call user's previously installed callbacks, if any.
# - When calling Init with 'install_callbacks=False': GLFW callbacks won't be installed. You will need to call individual function yourself from your own GLFW callbacks.
def glfw_install_callbacks(window_address: int) -> None:
    pass

def glfw_restore_callbacks(window_address: int) -> None:
    pass

# GLFW callbacks (individual callbacks to call if you didn't install callbacks)
def glfw_window_focus_callback(window_address: int, focused: int) -> None:
    """Since 1.84"""
    pass

def glfw_cursor_enter_callback(window_address: int, entered: int) -> None:
    """Since 1.84"""
    pass

def glfw_cursor_pos_callback(window_address: int, x: float, y: float) -> None:
    """Since 1.87"""
    pass

def glfw_mouse_button_callback(
    window_address: int, button: int, action: int, mods: int
) -> None:
    pass

def glfw_scroll_callback(window_address: int, xoffset: float, yoffset: float) -> None:
    pass

def glfw_key_callback(
    window_address: int, key: int, scancode: int, action: int, mods: int
) -> None:
    pass

def glfw_char_callback(window_address: int, c: int) -> None:
    pass

def glfw_monitor_callback(monitor: GLFWmonitor, event: int) -> None:
    pass
####################    </generated_from:imgui_impl_glfw.h>    ####################
