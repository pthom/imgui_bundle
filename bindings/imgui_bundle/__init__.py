# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle._imgui_bundle import imgui as imgui  # type: ignore
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
from imgui_bundle._imgui_bundle import im_cool_bar as im_cool_bar
from imgui_bundle._imgui_bundle import nanovg as nanovg
from imgui_bundle import immapp as immapp

# Note: to enable font awesome 6:
#     runner_params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome_4
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome  # v4
from imgui_bundle.immapp import icons_fontawesome_6 as icons_fontawesome_6

# if matplotlib is not installed, we can't import imgui_fig
try:
    from imgui_bundle import imgui_fig as imgui_fig
except ImportError:
    pass

from imgui_bundle._imgui_bundle import __version__, compilation_time

from imgui_bundle._imgui_bundle.imgui import ImVec2, ImVec4, ImColor, FLT_MIN, FLT_MAX  # type: ignore
from imgui_bundle.im_col32 import IM_COL32

from imgui_bundle import imgui_ctx as imgui_ctx
from imgui_bundle import imgui_node_editor_ctx as imgui_node_editor_ctx

from imgui_bundle import imgui_pydantic as imgui_pydantic
from imgui_bundle.imgui_pydantic import (
    ImVec4_Pydantic as ImVec4_Pydantic,
    ImVec2_Pydantic as ImVec2_Pydantic,
    ImColor_Pydantic as ImColor_Pydantic,
)

# Glfw setup:
# By importing imgui_bundle.glfw_utils, we make sure that glfw provided by pip will use our glfw dynamic library.
# (imgui_bundle.glfw_utils will call _set_glfw_pip_search_path automatically)
from imgui_bundle._glfw_set_search_path import _glfw_set_search_path

_glfw_set_search_path()
from imgui_bundle import glfw_utils as glfw_utils  # noqa: E402

# Flag types for ImPlot
implot.LineFlags = int  # see implot.LineFlags_
implot.ScatterFlags = int  # see implot.ScatterFlags_
implot.StairsFlags = int  # see implot.StairsFlags_
implot.ShadedFlags = int  # see implot.ShadedFlags_
implot.BarsFlags = int  # see implot.BarsFlags_
implot.PieChartFlags = int  # see implot.PieChartFlags_
implot.HistogramFlags = int  # see implot.HistogramFlags_


import os  # noqa: E402

THIS_DIR = os.path.dirname(__file__)
hello_imgui.override_assets_folder(THIS_DIR + "/assets")

# Patch after imgui v1.90.9, where
# the enum ImGuiDir_ was renamed to ImGuiDir and ImGuiSortDirection_ was renamed to ImGuiSortDirection
# this enables old python to continue to work
imgui.Dir_ = imgui.Dir
imgui.SortDirection_ = imgui.SortDirection


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
    "imgui_ctx",
    "imgui_pydantic",
    # Utilities related to ImGui
    "icons_fontawesome",
    "icons_fontawesome_6",
    "icons_fontawesome_4",
    # Base ImGui types
    "IM_COL32",
    "ImVec2",
    "ImVec4",
    "ImColor",
    "FLT_MIN",
    "FLT_MAX",
    # Pydantic types
    "ImVec4_Pydantic",
    "ImVec2_Pydantic",
    "ImColor_Pydantic",
    # Base utilities
    "__version__",
    "compilation_time",
]
