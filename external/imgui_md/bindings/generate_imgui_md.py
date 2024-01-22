# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_imgui_md")
    input_cpp_header = THIS_DIR + "/../imgui_md_wrapper/imgui_md_wrapper.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_md.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_md.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImGuiMd"]
    options.python_run_black_formatter = True
    options.value_replacements.add_last_replacement(
        "OnOpenLink_Default", "on_open_link_default"
    )
    options.value_replacements.add_last_replacement(
        "OnImage_Default", "on_image_default"
    )
    options.struct_create_default_named_ctor__regex = ""
    options.fn_return_force_policy_reference_for_pointers__regex = "GetCodeFont"

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
