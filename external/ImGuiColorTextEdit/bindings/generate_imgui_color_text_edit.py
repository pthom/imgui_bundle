# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from srcmlcpp.scrml_warning_settings import WarningType


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

MAIN_DIR = THIS_DIR + "/../"


def main():
    print("autogenerate_imgui_color_text_edit")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_color_text_edit.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_color_text_edit.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.ignored_warnings = [
        WarningType.LitgenClassMemberSkipBitfield
    ]
    options.member_exclude_by_type__regex = "Callback$|^char$"
    options.fn_return_force_policy_reference_for_references__regex = ".*"
    options.postprocess_stub_function = lambda s: s.replace("Optional[std.unordered_set<int>]", "Optional[Set[int]]")

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(MAIN_DIR + "/ImGuiColorTextEdit/TextEditor.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
