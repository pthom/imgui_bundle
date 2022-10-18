import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/ImGuiColorTextEdit"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_color_text_edit():
    input_cpp_header = CPP_HEADERS_DIR + "/TextEditor.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_color_text_edit.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_color_text_edit.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.member_exclude_by_type__regex = "Callback$|^char$"

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_hello_implot")
    autogenerate_imgui_color_text_edit()
