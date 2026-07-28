# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import ctypes

try:
    import glfw  # pip install glfw


    # The return type is a string annotation because ctypes._Pointer is only
    # subscriptable in type stubs, not at runtime.
    def glfw_window_hello_imgui() -> "ctypes._Pointer[glfw._GLFWwindow]":
        """Return the main glfw window used by HelloImGui (when the backend is GLFW)
        You can use this window to set up additional GLFW callbacks.
        """
        from imgui_bundle import hello_imgui

        window_address = hello_imgui.get_glfw_window_address()
        window_pointer = ctypes.cast(window_address, ctypes.POINTER(glfw._GLFWwindow))
        return window_pointer


except (ImportError, ModuleNotFoundError):


    def glfw_window_hello_imgui() -> None:  # type: ignore
        import sys
        print("""Please install glfw, so that glfw_window_hello_imgui works:
        pip install glfw""")
        sys.exit(1)


    pass
    # print("Warning: could not import glfw")
