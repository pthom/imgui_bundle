import os

import litgen
from litgen.options_customized.litgen_options_imgui import (
    litgen_options_imgui,
    ImguiOptionsType,
)

FLAG_DOCKING_BRANCH = True
THIS_DIR = os.path.dirname(__file__)
REPO_DIR = os.path.abspath(THIS_DIR + "/..")
print(f"{THIS_DIR=}")
CPP_HEADERS_DIR = REPO_DIR + "/external/imgui"
CPP_GENERATED_PYBIND_DIR = REPO_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui() -> None:
    # Generate for imgui.h
    options_imgui = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=FLAG_DOCKING_BRANCH)

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator = litgen.LitgenGenerator(options_imgui)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui.h")

    generator.process_cpp_file(REPO_DIR + "/external/imgui_toggle/imgui_toggle.h")

    # Generate for imgui_stdlib.h
    options_imgui_stdlib = litgen_options_imgui(ImguiOptionsType.imgui_stdlib_h, docking_branch=FLAG_DOCKING_BRANCH)

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui_stdlib.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator.lg_context.options = options_imgui_stdlib
    generator.process_cpp_file(CPP_HEADERS_DIR + "/misc/cpp/imgui_stdlib.h")

    generator.write_generated_code(
        output_cpp_pydef_file=CPP_GENERATED_PYBIND_DIR + "/pybind_imgui.cpp",
        output_stub_pyi_file=CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui/__init__.pyi",
        output_cpp_glue_code_file=CPP_GENERATED_PYBIND_DIR + "/litgen_glue_code.h",
    )


def autogenerate_imgui_internal() -> None:
    options_imgui_internal = litgen_options_imgui(ImguiOptionsType.imgui_internal_h, docking_branch=FLAG_DOCKING_BRANCH)
    litgen.write_generated_code_for_file(
        options_imgui_internal,
        input_cpp_header_file=CPP_HEADERS_DIR + "/imgui_internal.h",
        output_cpp_pydef_file=CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_internal.cpp",
        output_stub_pyi_file=CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui/internal.pyi",
    )


if __name__ == "__main__":
    print("autogenerate_imgui")
    autogenerate_imgui()
    autogenerate_imgui_internal()
