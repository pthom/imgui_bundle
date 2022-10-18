import os

import litgen
from litgen.options_customized.litgen_options_implot import litgen_options_implot


_THIS_DIR = os.path.dirname(__file__)
LG_HELLO_IMGUI_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = LG_HELLO_IMGUI_DIR + "/external/implot"
CPP_GENERATED_PYBIND_DIR = LG_HELLO_IMGUI_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_implot():
    input_cpp_header = CPP_HEADERS_DIR + "/implot.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_implot.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/implot.pyi"

    # Configure options
    options = litgen_options_implot()

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_hello_implot")
    autogenerate_implot()
