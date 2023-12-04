# Backend API
# Note: all this code is generated *manually*

from imgui_bundle.imgui import ImDrawData

###############################################################################
# <bindings for imgui_impl_opengl3.h
###############################################################################
def opengl3_init(glsl_version: str) -> bool:
    pass

def opengl3_shutdown() -> None:
    pass

def opengl3_new_frame() -> None:
    pass

def opengl3_render_draw_data(draw_data: ImDrawData) -> None:
    pass

# (Optional) Called by Init/NewFrame/Shutdown
def opengl3_create_fonts_texture() -> bool:
    pass

def opengl3_destroy_fonts_texture() -> None:
    pass

def opengl3_create_device_objects() -> bool:
    pass

def opengl3_destroy_device_objects() -> None:
    pass

###############################################################################
# <bindings for imgui_impl_opengl2.h
###############################################################################

def opengl2_init() -> bool:
    pass

def opengl2_shutdown() -> None:
    pass

def opengl2_new_frame() -> None:
    pass

def opengl2_render_draw_data(draw_data: ImDrawData) -> None:
    pass

#
# Called by Init/NewFrame/Shutdown
#
def opengl2_create_fonts_texture() -> bool:
    pass

def opengl2_destroy_fonts_texture() -> None:
    pass

def opengl2_create_device_objects() -> bool:
    pass

def opengl2_destroy_device_objects() -> None:
    pass

###############################################################################
# <bindings for imgui_impl_glfw.h
###############################################################################

def glfw_init_for_opengl(window_address: int, install_callbacks: bool) -> bool:
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

# def glfw_monitor_callback(monitor: GLFWmonitor, event: int) -> None:
#     pass
