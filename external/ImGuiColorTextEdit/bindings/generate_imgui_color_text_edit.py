import os

import litgen
from srcmlcpp.scrml_warning_settings import WarningType


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../ImGuiColorTextEdit"


def main():
    print("autogenerate_imgui_color_text_edit")
    input_cpp_header = CPP_HEADERS_DIR + "/TextEditor.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_color_text_edit.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_color_text_edit.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.ignored_warnings = [WarningType.LitgenClassMemberSkipBitfield]
    options.member_exclude_by_type__regex = "Callback$|^char$"

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
