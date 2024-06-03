# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import cast

try:
    import glfw  # type: ignore

    def glfw_window_hello_imgui() -> glfw._GLFWwindow:
        """Return the main glfw window used by HelloImGui (when the backend is GLFW)
        You can use this window to set up additional GLFW callbacks.
        """
        import ctypes
        from imgui_bundle import hello_imgui

        window_address = hello_imgui.get_glfw_window_address()  # type: ignore
        window_pointer = ctypes.cast(window_address, ctypes.POINTER(glfw._GLFWwindow))
        return cast(glfw._GLFWwindow, window_pointer)

except ImportError:
    pass
    # print("Warning: could not import glfw")
