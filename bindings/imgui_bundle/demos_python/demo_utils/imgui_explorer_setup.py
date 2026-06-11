# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Setup imgui_explorer for Python demos.

Provides get_imgui_explorer() which imports the module and determines
the package path for ShowImGuiExplorerGui_Python.
"""
import os
from types import ModuleType
from typing import Optional, Tuple

_package_path: Optional[str] = None


def get_package_path() -> str:
    """Return the root directory of the installed imgui_bundle package."""
    global _package_path
    if _package_path is None:
        import imgui_bundle
        _package_path = os.path.dirname(os.path.abspath(imgui_bundle.__file__))
    return _package_path


def get_imgui_explorer() -> Tuple[Optional[ModuleType], bool]:
    """Import imgui_explorer if available.

    Returns (module, True) if available, (None, False) otherwise.
    """
    try:
        from imgui_bundle import imgui_explorer
        return imgui_explorer, True
    except ImportError:
        return None, False
