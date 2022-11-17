import os

import litgen


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/glfw/include/GLFW"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_glfw():
    input_cpp_header = CPP_HEADERS_DIR + "/glfw3.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_glfw.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/glfw.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    # options.srcmlcpp_options.header_filter_preprocessor_regions = False
    options.srcmlcpp_options.functions_api_prefixes = "GLFWAPI"
    options.macro_define_include_by_name__regex = r"^GLFW_"
    options.macro_name_replacements.add_first_replacement(r"GLFW_", "")
    options.code_replacements.add_last_replacement("unsigned char", "int")
    options.names_replacements.add_last_replacement(r"^glfw_", "")
    options.fn_exclude_by_name__regex = r"Callback$|glfwGetProcAddress"
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = r".*"
    # options.python_run_black_formatter = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        output_cpp_glue_code_file=output_cpp_pydef_file,
        omit_boxed_types=False,
    )


if __name__ == "__main__":
    print("autogenerate_glfw")
    autogenerate_glfw()
