# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
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
from imgui_bundle._imgui_bundle import imguizmo as imguizmo
from imgui_bundle._imgui_bundle import imgui_tex_inspect as imgui_tex_inspect
from imgui_bundle._imgui_bundle import imgui_toggle as imgui_toggle
from imgui_bundle._imgui_bundle import portable_file_dialogs as portable_file_dialogs
from imgui_bundle._imgui_bundle import imgui_command_palette as imgui_command_palette
from imgui_bundle import immapp as immapp
from imgui_bundle.immapp import icons_fontawesome as icons_fontawesome

from imgui_bundle._imgui_bundle import __version__, compilation_time

from imgui_bundle._imgui_bundle.imgui import ImVec2, ImVec4, ImColor, FLT_MIN, FLT_MAX
from imgui_bundle.im_col32 import IM_COL32


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
    "immapp",
    "hello_imgui",
    "implot",
    "immvision",
    "imgui_bundle",
    "imspinner",
    "imgui_md",
    "imgui_knobs",
    "imgui_color_text_edit",
    "imgui_node_editor",
    "imgui_toggle",
    # Utilities related to ImGui
    "glfw_window_hello_imgui",
    "icons_fontawesome",
    # Base ImGui types
    "IM_COL32",
    "ImVec2",
    "ImVec4",
    "ImColor",
    "FLT_MIN",
    "FLT_MAX",
    # Base utilities
    "__version__",
]
