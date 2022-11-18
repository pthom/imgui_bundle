def _set_glfw_pip_search_path():
    """Sets os.environ["PYGLFW_LIBRARY"] so that glfw provided by pip uses our glfw library.

    venv/lib/python3.9/site-packages/glfw/library.py

    if os.environ.get('PYGLFW_LIBRARY', ''):
        try:
            glfw = ctypes.CDLL(os.environ['PYGLFW_LIBRARY'])
        except OSError:
            glfw = None

    """
    import os
    import platform
    this_dir = os.path.dirname(__file__)
    if platform.system() == "Darwin":
        lib_file = "libglfw.3.dylib"
    elif platform.system() == "Windows":
        lib_file = "glfw3.dll"
    elif platform.system() == "Linux":
        lib_file = "libglfw.so.3"
    else:
        msg = f"Please implement set_pip_glfw_search_path() for your os: {platform.system()}\n"
        raise NotImplementedError(msg)
    os.environ["PYGLFW_LIBRARY"] = f"{this_dir}/{lib_file}"


_set_glfw_pip_search_path()


# do not move this import at the top, it should be done after the call to _set_glfw_pip_search_path()
import glfw 
from typing import cast


def glfw_window_hello_imgui() -> glfw._GLFWwindow:
    """Return the main glfw window used by HelloImGui (when the backend is GLFW)
    You can use this window to setup additional GLFW callbacks.
    """
    import ctypes
    from imgui_bundle import hello_imgui

    window_address = hello_imgui.get_glfw_window_address()
    window_pointer = ctypes.cast(window_address, ctypes.POINTER(glfw._GLFWwindow))
    return cast(glfw._GLFWwindow, window_pointer)
