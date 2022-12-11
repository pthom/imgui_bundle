import os

import litgen
from litgen_options_imgui import *


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imgui_toggle"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_toggle():
    print("autogenerate_imgui_toggle")
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_toggle.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_toggle.pyi"

    # Configure options
    options = litgen_options_imgui(ImguiOptionsType.imgui_h, True)
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options.fn_exclude_non_api = False
    options.namespace_root__regex = "ImGui"
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    options.python_run_black_formatter = True
    options.struct_create_default_named_ctor__regex = ""
    options.function_names_replacements.add_last_replacement("iOS", "ios")
    options.srcmlcpp_options.ignored_warning_parts = [
        "operators are supported only when implemented as a member functions",
        "decl_stmt are not supported in python conversion",
    ]

    generator = litgen.LitgenGenerator(options)

    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_toggle.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_toggle_presets.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_toggle_palette.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_offset_rect.h")
    # generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_toggle_renderer.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    autogenerate_imgui_toggle()
