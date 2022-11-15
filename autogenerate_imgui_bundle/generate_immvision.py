import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/immvision"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_immvision():
    input_cpp_header = CPP_HEADERS_DIR + "/immvision.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_immvision.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/immvision.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "ImmVision"
    options.srcmlcpp_options.functions_api_prefixes = "IMMVISION_API"
    options.python_run_black_formatter = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_immvision")
    autogenerate_immvision()
