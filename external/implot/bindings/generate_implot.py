# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from litgen_options_implot import litgen_options_implot


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot"


def main():
    print("autogenerate_hello_implot")
    input_cpp_header = CPP_HEADERS_DIR + "/implot.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_implot.cpp"
    output_stub_pyi_file = STUB_DIR + "/implot.pyi"

    # Configure options
    options = litgen_options_implot()
    options.srcmlcpp_options.flag_show_progress = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
