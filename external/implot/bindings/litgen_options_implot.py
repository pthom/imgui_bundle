# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from codemanip.code_utils import join_string_by_pipe_char

from litgen.options import LitgenOptions

import sys
import os

THIS_DIR = os.path.dirname(__file__)
sys.path.append(THIS_DIR + "/../../imgui/bindings")
from litgen_options_imgui import litgen_options_imgui, ImguiOptionsType  # noqa: E402


def litgen_options_implot() -> LitgenOptions:
    options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    options.namespaces_root = ["ImPlot"]
    options.srcmlcpp_options.functions_api_prefixes = "IMPLOT_API|IMPLOT_TMP"
    options.srcmlcpp_options.header_filter_acceptable__regex += "|IMGUI_BUNDLE_PYTHON_API"

    options.fn_force_overload__regex = "BeginPlot"
    options.fn_force_lambda__regex = join_string_by_pipe_char(["^Contains$"])

    options.fn_params_exclude_names__regex += "|^stride$"
    options.fn_exclude_by_param_type__regex = "ImPlotFormatter|ImPlotTransform"

    # Patches for wrapping of BeginSubplots (cf https://github.com/pthom/imgui_bundle/issues/207)
    options.fn_params_exclude_types__regex += r"|^float\s*\*$"
    options.fn_exclude_by_name__regex += "|^BeginSubplots$|"
    options.function_names_replacements.add_first_replacement("begin_subplots_with_ratios", "begin_subplots")

    options.function_names_replacements.add_first_replacement("ImGui", "Imgui")
    options.function_names_replacements.add_first_replacement("plot_histogram2_d", "plot_histogram_2d")
    options.type_replacements.add_first_replacement("ImGuiContext", "ImGui_Context")

    options.type_replacements.add_last_replacement(r"ImPlot([A-Z][a-zA-Z0-9]*)", r"\1")

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

    options.fn_exclude_by_name__regex += join_string_by_pipe_char(
        [
            #  Legitimate Excludes
            # Exclude functions whose name end with G, like for example
            #       IMPLOT_API void PlotLineG(const char* label_id, ImPlotGetter getter, void* data, int count);
            # which are made for specialized C/C++ getters
            r"\w*G\Z",
            # Exclude function whose name ends with V, like for example
            #       IMPLOT_API void TagXV(double x, const ImVec4& color, const char* fmt, va_list args) IM_FMTLIST(3);
            # which are utilities for variadic print format
            r"\w*V\Z",
            #  Excludes due to two-dimensional buffer
            #  PlotHeatmap(.., const T* values, int rows, int cols, !!!
            #                            ^          ^          ^
            "PlotHeatmap",
            #  Excludes due to antique style string vectors
            #  for which there is no generalizable parse
            # void SetupAxisTicks(ImAxis idx, const double* values, int n_ticks, const char* const labels[], bool show_default)
            #                                                            ^                           ^
            "SetupAxisTicks",
            # IMPLOT_API ImPlotColormap AddColormap(const char* name, const ImU32*  cols, int size, bool qual=true);
            # (This API is a bit exotic, and cannot be bound automatically)
            "^AddColormap$",
        ]
    )

    return options
