import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imgui_md"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_md():
    input_cpp_header = CPP_HEADERS_DIR + "/imgui_md_wrapper.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_md.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_md.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "ImGuiMd"
    options.python_run_black_formatter = True
    options.code_replacements.add_last_replacement("OnOpenLink_Default", "on_open_link_default")
    options.code_replacements.add_last_replacement("OnImage_Default", "on_image_default")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_imgui_md")
    autogenerate_imgui_md()
