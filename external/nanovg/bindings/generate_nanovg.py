# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../nanovg/src"


def main():
    print("autogenerate_nanovg")
    input_cpp_header = CPP_HEADERS_DIR + "/nanovg.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_nanovg.cpp"
    output_stub_pyi_file = STUB_DIR + "/nanovg.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.original_signature_flag_show = True
    options.type_replacements.add_last_replacement("unsigned char", "UChar")
    options.var_names_replacements.add_last_replacement("^NVG_", "")
    options.function_names_replacements.add_last_replacement("^nvg", "")
    options.class_exclude_by_name__regex = "^NVGcolor$"  # contains a union...

    for letter in "abcdefghijklmnopqrstuvwxyz":
        options.type_replacements.add_last_replacement(
            "NVG" + letter, letter.upper()
        )

    # options.namespace_root__regex = "LIBNAME"
    # options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    # options.python_run_black_formatter = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
