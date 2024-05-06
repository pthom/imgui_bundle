# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
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
