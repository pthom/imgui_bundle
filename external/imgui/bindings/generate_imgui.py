# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
import time
from functools import wraps

import litgen
from litgen_options_imgui import (
    litgen_options_imgui,
    ImguiOptionsType,
)


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

FLAG_DOCKING_BRANCH = True
CPP_HEADERS_DIR = THIS_DIR + "/../imgui"


def my_time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.6f} seconds to run.")
        return result

    return wrapper


def autogenerate_imgui() -> None:
    print("Processing imgui.h")
    # Generate for imgui.h
    options_imgui = litgen_options_imgui(
        ImguiOptionsType.imgui_h, docking_branch=FLAG_DOCKING_BRANCH
    )

    # GetStyleColorVec4 returns const ImVec4& (reference into the style array).
    # With rv_policy::reference, Python can mutate the style directly without PushStyleColor.
    # Exclude only for imgui (not shared options, since ImPlot's version returns by value).
    options_imgui.fn_exclude_by_name__regex += r"|^GetStyleColorVec4$"
    # Custom binding returns a copy instead.
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def get_style_color_vec4(idx: Col) -> ImVec4:
            """retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in.
            (Note: returns a copy, not a reference to the internal style color.)"""
            ...
    ''',
        pydef_code="""
        LG_MODULE.def("get_style_color_vec4",
            [](ImGuiCol idx) -> ImVec4 { return ImGui::GetStyleColorVec4(idx); },
            nb::arg("idx"),
            "retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in.");
    """,
    )

    # ColorConvertRGBtoHSV / ColorConvertHSVtoRGB: output params should not be
    # required as inputs. Custom bindings take only the 3 input values.
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def color_convert_rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
            """Convert rgb floats ([0-1],[0-1],[0-1]) to hsv floats ([0-1],[0-1],[0-1])"""
            ...
        def color_convert_hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
            """Convert hsv floats ([0-1],[0-1],[0-1]) to rgb floats ([0-1],[0-1],[0-1])"""
            ...
    ''',
        pydef_code="""
        LG_MODULE.def("color_convert_rgb_to_hsv",
            [](float r, float g, float b) -> std::tuple<float, float, float> {
                float h, s, v;
                ImGui::ColorConvertRGBtoHSV(r, g, b, h, s, v);
                return std::make_tuple(h, s, v);
            }, nb::arg("r"), nb::arg("g"), nb::arg("b"),
            "Convert rgb floats ([0-1],[0-1],[0-1]) to hsv floats ([0-1],[0-1],[0-1])");
        LG_MODULE.def("color_convert_hsv_to_rgb",
            [](float h, float s, float v) -> std::tuple<float, float, float> {
                float r, g, b;
                ImGui::ColorConvertHSVtoRGB(h, s, v, r, g, b);
                return std::make_tuple(r, g, b);
            }, nb::arg("h"), nb::arg("s"), nb::arg("v"),
            "Convert hsv floats ([0-1],[0-1],[0-1]) to rgb floats ([0-1],[0-1],[0-1])");
    """,
    )

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator = litgen.LitgenGenerator(options_imgui)

    print("Processing imgui.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui.h")

    print("Processing imgui_stacklayout.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_stacklayout.h")
    print("Processing imgui_stacklayout_internal.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_stacklayout_internal.h")

    # Generate for imgui_stdlib.h
    options_imgui_stdlib = litgen_options_imgui(
        ImguiOptionsType.imgui_stdlib_h, docking_branch=FLAG_DOCKING_BRANCH
    )
    options_imgui.srcmlcpp_options.flag_quiet = True

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui_stdlib.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator.lg_context.options = options_imgui_stdlib
    print("Processing imgui_stdlib.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/misc/cpp/imgui_stdlib.h")

    print("Processing imgui_pywrappers.h")
    generator.process_cpp_file(THIS_DIR + "/../imgui_pywrappers/imgui_pywrappers.h")

    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/__init__.pyi",
    )


def autogenerate_imgui_internal() -> None:
    options_imgui_internal = litgen_options_imgui(
        ImguiOptionsType.imgui_internal_h, docking_branch=FLAG_DOCKING_BRANCH
    )
    generator = litgen.LitgenGenerator(options_imgui_internal)

    print("Processing imgui_internal.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_internal.h")
    print("Processing imgui_internal_pywrappers.h")
    generator.process_cpp_file(
        THIS_DIR + "/../imgui_pywrappers/imgui_internal_pywrappers.h"
    )

    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/internal.pyi",
    )


def autogenerate_imgui_test_engine() -> None:
    options = litgen_options_imgui(
        ImguiOptionsType.imgui_test_engine, docking_branch=FLAG_DOCKING_BRANCH
    )
    options.fn_exclude_by_name__regex += "|^ImGuiTestEngineUtil_appendf_auto"

    generator = litgen.LitgenGenerator(options)
    imgui_test_engine_dir = (
        THIS_DIR + "/../../imgui_test_engine/imgui_test_engine/imgui_test_engine"
    )
    print("Processing imgui_test_engine")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_exporters.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_engine.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_context.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_internal.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_ui.h")
    # generator.process_cpp_file(imgui_test_engine_dir + "/imgui_capture_tool.h")
    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui_test_engine.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/test_engine.pyi",
    )


@my_time_it
def main():
    autogenerate_imgui()
    autogenerate_imgui_internal()
    autogenerate_imgui_test_engine()


def sandbox():
    code = """
    IMGUI_API bool          InputTextEx(const char* label, const char* hint, char* buf, int buf_size, const ImVec2& size_arg, ImGuiInputTextFlags flags, ImGuiInputTextCallback callback = NULL, void* user_data = NULL);
    // IMGUI_API void          InputTextDeactivateHook(ImGuiID id);
    // IMGUI_API bool          TempInputText(const ImRect& bb, ImGuiID id, const char* label, char* buf, int buf_size, ImGuiInputTextFlags flags);
    """
    options_imgui = litgen_options_imgui(
        ImguiOptionsType.imgui_internal_h, docking_branch=FLAG_DOCKING_BRANCH
    )
    generated_code = litgen.generate_code(options_imgui, code)
    print(generated_code.pydef_code)


if __name__ == "__main__":
    main()
    # sandbox()
