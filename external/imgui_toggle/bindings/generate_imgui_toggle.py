# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
import sys
import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_toggle"

sys.path.append(THIS_DIR + "/../../imgui/bindings")
import litgen_options_imgui  # noqa: E402


def main():
    print("autogenerate_imgui_toggle")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_toggle.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_toggle.pyi"

    # Configure options
    options = litgen_options_imgui.litgen_options_imgui(
        litgen_options_imgui.ImguiOptionsType.imgui_h, True
    )
    options.srcmlcpp_options.flag_show_progress = False
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options.fn_exclude_non_api = False
    options.namespaces_root = ["ImGui", "ImGuiToggleConstants", "ImGuiTogglePresets"]
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
    main()
