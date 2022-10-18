import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imspinner"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imspinner():
    input_cpp_header = CPP_HEADERS_DIR + "/imspinner.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imspinner.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imspinner.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "ImSpinner"
    options.srcmlcpp_options.header_filter_acceptable__regex = "_H_$"
    options.fn_exclude_by_name__regex = "min_patched"
    # options.python_run_black_formatter = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_imspinner")
    autogenerate_imspinner()
