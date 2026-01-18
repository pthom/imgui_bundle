# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle


def _glfw_set_search_path() -> None:
    """Sets os.environ["PYGLFW_LIBRARY"] so that glfw provided by pip uses our dynamic glfw library
    (provided in imgui_bundle package).
    This is necessary if a user want to "import glfw" after having started an imgui_bundle application:
    1. imgui_bundle ships its own glfw dynamic library (libglfw.so / glfw3.dll / libglfw.dylib)
    2. in that case the glfw python package (pyglfw) must be told to use that library

    This function searches for the GLFW dynamic library in multiple locations to support
    different packaging tools (pip, PyInstaller, Nuitka, etc.).

    Search priority:
    1. PYGLFW_LIBRARY preexisting environment variable (user override)
    2. imgui_bundle package directory (standard pip install)
    3. Directory containing sys.executable (for Nuitka and frozen apps)
    4. Current working directory (fallback)

    If GLFW library is not found in any location, a warning is issued and the function
    returns without setting PYGLFW_LIBRARY, allowing the system to attempt loading GLFW
    through default mechanisms.

    Background:
        venv/lib/python3.9/site-packages/glfw/library.py checks:
        if os.environ.get('PYGLFW_LIBRARY', ''):
            try:
                glfw = ctypes.CDLL(os.environ['PYGLFW_LIBRARY'])
            except OSError:
                glfw = None
    """
    import os
    import sys
    import platform
    import warnings

    # Determine the expected library filename for the current platform
    if platform.system() == "Darwin":
        lib_filenames = ["libglfw.3.dylib"]
    elif platform.system() == "Windows":
        lib_filenames = ["glfw3.dll"]
    elif platform.system() == "Linux":
        # Try multiple common naming conventions
        lib_filenames = ["libglfw.so.3", "libglfw.3.so", "libglfw. so.3.4", "libglfw.so.3.3"]
    else:
        warnings.warn(
            f"GLFW library search not implemented for platform: {platform.system()}. "
            f"GLFW functionality may not work correctly.",
            RuntimeWarning,
            stacklevel=2
        )
        return

    # Priority 1: Check if user has explicitly set PYGLFW_LIBRARY
    if os.environ.get("PYGLFW_LIBRARY"):
        glfw_path = os.environ["PYGLFW_LIBRARY"]
        if os.path.exists(glfw_path):
            return
        else:
            warnings.warn(
                f"env var PYGLFW_LIBRARY is set to '{glfw_path}' but file does not exist. ",
                RuntimeWarning,
                stacklevel=2
            )
            return

    # Define search directories in priority order
    search_dirs = [
        os.path.dirname(__file__),                    # imgui_bundle package directory (pip install)
        os.path.dirname(os.path.abspath(sys. executable)),  # Nuitka/PyInstaller executable directory
        os.getcwd(),                                   # Current working directory (fallback)
    ]

    # Search for the library in all directories
    for search_dir in search_dirs:
        for lib_filename in lib_filenames:
            lib_path = os.path.join(search_dir, lib_filename)
            if os.path. exists(lib_path):
                # Found it! Set the environment variable and return
                os. environ["PYGLFW_LIBRARY"] = lib_path
                return

    # If we get here, we couldn't find the GLFW library anywhere
    search_locations = "\n  - ".join(search_dirs)
    warnings.warn(
        f"Could not find GLFW library ({', '.join(lib_filenames)}) in any of the following locations:\n"
        f"  - {search_locations}\n\n"
        f"GLFW functionality may not work correctly."
        f"You may set the PYGLFW_LIBRARY environment variable to the full path of your GLFW library.\n\n"
        f"Falling back to system GLFW library loading (if available).",
        RuntimeWarning,
        stacklevel=2
    )
