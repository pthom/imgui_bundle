import os

import litgen


THIS_DIR = os.path.dirname(__file__)
print(f"{THIS_DIR=}")
CPP_HEADERS_DIR = THIS_DIR + "/external/hello_imgui/src/hello_imgui"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def make_hello_imgui_amalgamated_header():
    from make_amalgamation import AmalgamationOptions, write_amalgamate_header_file

    hello_imgui_src_dir = THIS_DIR + "/external/hello_imgui/src/"
    options = AmalgamationOptions()

    options.base_dir = hello_imgui_src_dir
    options.local_includes_startwith = "hello_imgui/"
    options.include_subdirs = ["hello_imgui"]
    options.main_header_file = "hello_imgui.h"
    options.dst_amalgamated_header_file = THIS_DIR + "/hello_imgui_amalgamation.h"

    write_amalgamate_header_file(options)


def autogenerate():
    input_cpp_header = THIS_DIR + "/hello_imgui_amalgamation.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_hello_imgui.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/hello_imgui/hello_imgui.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, filename=input_cpp_header)

    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    print("autogenerate_hello_imgui")
    make_hello_imgui_amalgamated_header()
    autogenerate()
