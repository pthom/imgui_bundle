# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from litgen_options_implot3d import litgen_options_implot3d


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot3d"


def autogenerate_implot3d():
    print("autogenerate_implot3d")
    input_cpp_header = CPP_HEADERS_DIR + "/implot3d.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_implot3d.cpp"
    output_stub_pyi_file = STUB_DIR + "/implot3d/__init__.pyi"

    # Configure options
    options = litgen_options_implot3d()
    options.srcmlcpp_options.flag_show_progress = True
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"

    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])


    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


def autogenerate_implot3d_internal() -> None:
    print("autogenerate_implot3d_internal")
    options = litgen_options_implot3d()
    options.srcmlcpp_options.flag_show_progress = True
    options.python_run_black_formatter = False

    options.srcmlcpp_options.ignored_warning_parts.append("Excluding template type ImVector")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=CPP_HEADERS_DIR + "/implot3d_internal.h",
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_implot3d_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/implot3d/internal.pyi",
    )


def sandbox():
    code = """
enum ImPlot3DFlags_ {
    ImPlot3DFlags_None = 0,             // Default
    ImPlot3DFlags_NoTitle = 1 << 0,     // Hide plot title
    ImPlot3DFlags_NoLegend = 1 << 1,    // Hide plot legend
    ImPlot3DFlags_NoMouseText = 1 << 2, // Hide mouse position in plot coordinates
    ImPlot3DFlags_NoClip = 1 << 3,      // Disable 3D box clipping
    ImPlot3DFlags_NoMenus = 1 << 4,     // The user will not be able to open context menus
    ImPlot3DFlags_CanvasOnly = ImPlot3DFlags_NoTitle | ImPlot3DFlags_NoLegend | ImPlot3DFlags_NoMouseText,
};
    """
    options = litgen_options_implot3d()
    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_code(code, "file")
    print(generator.stub_code())


def main():
    autogenerate_implot3d()
    autogenerate_implot3d_internal()
    # sandbox()


if __name__ == "__main__":
    main()
