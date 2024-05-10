# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imspinner"


def main():
    print("autogenerate_imspinner")
    input_cpp_header = CPP_HEADERS_DIR + "/imspinner.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imspinner.cpp"
    output_stub_pyi_file = STUB_DIR + "/imspinner.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImSpinner"]
    options.srcmlcpp_options.header_filter_acceptable__regex = "_H_$"
    options.fn_exclude_by_name__regex = "min_patched"
    options.srcmlcpp_options.ignored_warning_parts = [
        "Ignoring template function",
        "unhandled tag template",
    ]
    # options.python_run_black_formatter = True
    options.postprocess_stub_function = lambda s: s.replace("IM_PI  0.7", "math.pi * 0.7")

    options.globals_vars_include_by_name__regex = r"^PI_|white|red"


    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
