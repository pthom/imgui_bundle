from imgui_bundle._imgui_bundle import imgui as imgui
from imgui_bundle._imgui_bundle import hello_imgui as hello_imgui
from imgui_bundle._imgui_bundle import implot as implot
from imgui_bundle._imgui_bundle import imgui_color_text_edit as imgui_color_text_edit
from imgui_bundle._imgui_bundle import imgui_node_editor as imgui_node_editor
from imgui_bundle._imgui_bundle import imgui_knobs as imgui_knobs
from imgui_bundle._imgui_bundle import im_file_dialog as im_file_dialog
from imgui_bundle._imgui_bundle import imspinner as imspinner
from imgui_bundle._imgui_bundle import imgui_md as imgui_md
from imgui_bundle._imgui_bundle import immvision as immvision
from imgui_bundle._imgui_bundle import imgui_backends as imgui_backends
from imgui_bundle._imgui_bundle import imguizmo as imguizmo
from imgui_bundle._imgui_bundle import imgui_tex_inspect as imgui_tex_inspect

from imgui_bundle._imgui_bundle import (
    run as run,
    current_node_editor_context as current_node_editor_context,
    clock_seconds as clock_seconds,
    AddOnsParams as AddOnsParams,
    visible_font_size as visible_font_size,
    em_size as em_size,
)

from imgui_bundle import icons_fontawesome
from imgui_bundle.imgui_bundle_utils import static as static, run_anon_block as run_anon_block, run_nb as run_nb

from imgui_bundle._imgui_bundle import __version__

from imgui_bundle._imgui_bundle.imgui import ImVec2, ImVec4, ImColor, FLT_MIN, FLT_MAX
from imgui_bundle.im_col32 import IM_COL32

from imgui_bundle._imgui_bundle.hello_imgui import (
    RunnerParams as RunnerParams,
    SimpleRunnerParams as SimpleRunnerParams,
)

# By importing imgui_bundle.glfw_utils below,
# _set_glfw_pip_search_path() will set os.environ["PYGLFW_LIBRARY"] so that glfw provided by pip
# uses our glfw library.
from imgui_bundle.glfw_utils import glfw_window_hello_imgui as glfw_window_hello_imgui


import os

THIS_DIR = os.path.dirname(__file__)
hello_imgui.override_assets_folder(THIS_DIR + "/assets")


__all__ = [
    # submodules
    "imgui",
    "hello_imgui",
    "implot",
    "immvision",
    "imgui_bundle",
    "imspinner",
    "imgui_backends",
    "imgui_md",
    "imgui_knobs",
    "imgui_color_text_edit",
    "imgui_node_editor",
    # Utilities related to ImGui
    "glfw_window_hello_imgui",
    "icons_fontawesome",
    "current_node_editor_context",
    # Base ImGui types
    "IM_COL32",
    "ImVec2",
    "ImVec4",
    "ImColor",
    "FLT_MIN",
    "FLT_MAX",
    # HelloImGui and ImGuiBundle runners
    "RunnerParams",
    "SimpleRunnerParams",
    "AddOnsParams",
    "run_nb",
    "run",
    # Base utilities
    "static",
    "run_anon_block",
    "clock_seconds",
    "__version__",
]
