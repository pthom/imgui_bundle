# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from codemanip.code_utils import join_string_by_pipe_char

from litgen.options import LitgenOptions

import sys
import os

THIS_DIR = os.path.dirname(__file__)
sys.path.append(THIS_DIR + "/../../imgui/bindings")
from litgen_options_imgui import litgen_options_imgui, ImguiOptionsType  # noqa: E402


def litgen_options_implot3d() -> LitgenOptions:
    options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    options.namespaces_root = ["ImPlot3D"]
    options.srcmlcpp_options.functions_api_prefixes = "IMPLOT3D_API|IMPLOT3D_TMP"
    options.srcmlcpp_options.header_filter_acceptable__regex += "|IMGUI_BUNDLE_PYTHON_API"

    options.function_names_replacements.add_first_replacement("ImGui", "Imgui")
    options.function_names_replacements.add_first_replacement("NaN", "Nan")
    options.var_names_replacements.add_first_replacement("NaN", "Nan")
    options.type_replacements.add_last_replacement(r"ImPlot3D([A-Z][a-zA-Z0-9]*)", r"\1")

    options.fn_exclude_by_name__regex = "Formatter_Default|SetupAxisTicks"
    options.fn_exclude_by_param_type__regex = "ImPlot3DFormatter"
    options.fn_force_lambda__regex = "PlotMesh"
    options.class_exclude_by_name__regex = "ImDrawList3D"
    options.member_exclude_by_type__regex = r"^ImVector|TextBuffer|Storage|ImPool|ImPlot3DFormatter|ImPlot3DLocator|ImDrawList3D"

    options.class_copy__regex = "ImPlot3DStyle|Style"
    options.class_copy_add_info_in_stub = True

    options.fn_params_buffer_types = join_string_by_pipe_char(
        [
            # // Scalar data types defined by imgui.h
            # // typedef unsigned int        ImGuiID;// A unique ID used by widgets (typically the result of hashing a stack of string)
            # // typedef signed char         ImS8;   // 8-bit signed integer
            # // typedef unsigned char       ImU8;   // 8-bit unsigned integer
            # // typedef signed short        ImS16;  // 16-bit signed integer
            # // typedef unsigned short      ImU16;  // 16-bit unsigned integer
            # // typedef signed int          ImS32;  // 32-bit signed integer == int
            # // typedef unsigned int        ImU32;  // 32-bit unsigned integer (often used to store packed colors)
            # // typedef signed   long long  ImS64;  // 64-bit signed integer
            # // typedef unsigned long long  ImU64;  // 64-bit unsigned integer
            "uint8_t",
            "int8_t",
            "uint16_t",
            "int16_t",
            "uint32_t",
            "int32_t",
            "np_uint_l",  # Platform dependent: "uint64_t" on *nixes, "uint32_t" on windows
            "np_int_l",  # Platform dependent: "int64_t" on *nixes, "int32_t" on windows
            "float",
            "double",
            "long double",  # Note: long double not supported in implot (yet?)
            "long long",
        ]
    )


    return options
