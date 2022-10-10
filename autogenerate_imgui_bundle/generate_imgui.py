import os

import litgen
from litgen.options_customized.litgen_options_imgui import litgen_options_imgui


THIS_DIR = os.path.dirname(__file__)
REPO_DIR = os.path.abspath(THIS_DIR + "/..")
print(f"{THIS_DIR=}")
CPP_HEADERS_DIR = REPO_DIR + "/external/imgui"
CPP_GENERATED_PYBIND_DIR = REPO_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui() -> None:
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_imgui_bundle/imgui.pyi"
    output_glue_code_file = CPP_GENERATED_PYBIND_DIR + "/litgen_glue_code.h"

    # Configure options
    options_imgui = litgen_options_imgui()
    options_imgui.fn_exclude_by_name__regex += "|^InputText"
    options_imgui_stdlib = litgen_options_imgui()

    # Generate code for imgui.h and imgui_stdlib.h
    input_cpp_header = CPP_HEADERS_DIR + "/imgui.h"
    input_cpp_header_stdlib = CPP_HEADERS_DIR + "/misc/cpp/imgui_stdlib.h"

    generator = litgen.LitgenGenerator(options_imgui)
    generator.process_cpp_file(input_cpp_header)
    generator.lg_context.options = options_imgui_stdlib
    generator.process_cpp_file(input_cpp_header_stdlib)

    generator.write_generated_code(output_cpp_pydef_file, output_stub_pyi_file, output_glue_code_file)


if __name__ == "__main__":
    print("autogenerate_imgui")
    autogenerate_imgui()
