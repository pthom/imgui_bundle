"""The pure-Python backends without PyOpenGL: their import fails with a message that names PyOpenGL and how to
install it"""

import importlib
import importlib.machinery
import sys
from typing import Any, Optional, Sequence

import pytest


class HidePyOpenGL:
    """Delegates to Python's path finder, except for PyOpenGL: Python then fails as when it is not installed"""

    @staticmethod
    def find_spec(fullname: str, path: Optional[Sequence[str]] = None, target: Any = None) -> Any:
        if fullname.split(".")[0] == "OpenGL":
            return None
        return importlib.machinery.PathFinder.find_spec(fullname, path, target)


def test_missing_pyopengl_is_named(monkeypatch: pytest.MonkeyPatch) -> None:
    finders = [HidePyOpenGL if f is importlib.machinery.PathFinder else f for f in sys.meta_path]
    monkeypatch.setattr(sys, "meta_path", finders)
    for name in [m for m in sys.modules if m.split(".")[0] == "OpenGL" or m.startswith("imgui_bundle.python_backends.")]:
        monkeypatch.delitem(sys.modules, name)

    with pytest.raises(ModuleNotFoundError, match="pip install PyOpenGL"):
        importlib.import_module("imgui_bundle.python_backends.opengl_backend_programmable")
