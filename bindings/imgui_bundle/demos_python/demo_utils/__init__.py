import os as _os
from imgui_bundle import hello_imgui as _hello_imgui

# Register demos_assets as an asset search path when demos are imported
_demos_assets = _os.path.dirname(_os.path.dirname(__file__)) + "/../demos_assets"
_demos_assets = _os.path.normpath(_demos_assets)
if _os.path.isdir(_demos_assets):
    _hello_imgui.add_assets_search_path(_demos_assets)

from imgui_bundle.demos_python.demo_utils.api_demos import (
    GuiFunction,
    demos_assets_folder,
    show_python_vs_cpp_and_run,
    show_python_vs_cpp_file,
    show_python_vs_cpp_code,
    set_hello_imgui_demo_assets_folder,
    spawn_demo_file,
    can_run_subprocess
)
from imgui_bundle.demos_python.demo_utils.animate_logo import animate_logo
from imgui_bundle.demos_python.demo_utils.imread_demo import imread_demo

__all__ = [
    "GuiFunction",
    "demos_assets_folder",
    "show_python_vs_cpp_and_run",
    "show_python_vs_cpp_file",
    "set_hello_imgui_demo_assets_folder",
    "animate_logo",
    "imread_demo",
    "spawn_demo_file",
    "can_run_subprocess"
]
