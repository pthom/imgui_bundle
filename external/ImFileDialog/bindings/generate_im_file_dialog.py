# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_im_file_dialog")
    input_cpp_header = THIS_DIR + "/../ImFileDialog/ImFileDialog.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_im_file_dialog.cpp"
    output_stub_pyi_file = STUB_DIR + "/im_file_dialog.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.python_run_black_formatter = True
    options.namespace_root__regex = "^ifd$"
    options.fn_return_force_policy_reference_for_references__regex = "^Instance$"
    options.type_replacements.add_first_replacement("std::filesystem::path", "Path")
    options.member_exclude_by_name__regex = "CreateTexture|DeleteTexture"
    options.type_replacements.add_last_replacement(r"std.vector<(\w*)>", r"List[\1]")
    options.type_replacements.add_last_replacement(r"time_t", r"int")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    autogenerate_im_file_dialog()
