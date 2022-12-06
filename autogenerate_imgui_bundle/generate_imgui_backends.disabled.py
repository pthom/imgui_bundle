"""
Disabled!
backend code is manual!!!
"""
import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imgui/backends"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_backends():
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_backends.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui/backends.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.python_run_black_formatter = True
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_IMPL_API"

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_impl_opengl3.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_impl_glfw.h")

    generator.write_generated_code(
        output_cpp_pydef_file=CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_backends.cpp",
        output_stub_pyi_file=CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/backends.pyi",
    )


if __name__ == "__main__":
    # imgui_backend is now generated manually
    pass
    # print("autogenerate_imgui_backends")
    # autogenerate_imgui_backends()
