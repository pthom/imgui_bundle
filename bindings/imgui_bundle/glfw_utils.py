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


def _set_glfw_pip_search_path():
    this_dir = os.path.dirname(__file__)
    if platform.system() == "Darwin":
        lib_file = "libglfw.3.dylib"
    elif platform.system() == "Window":
        lib_file = "glfw3.dll"
    elif platform.system() == "Linux":
        lib_file = "libglfw.so.3"
    else:
        raise NotImplemented(f"Please implement set_pip_glfw_search_path() for your os {platform.system()}")
    os.environ["PYGLFW_LIBRARY"] = f"{this_dir}/{lib_file}"

