# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen

from codemanip.code_utils import join_string_by_pipe_char

THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui-node-editor"


def main():
    print("autogenerate_imgui_node_editor")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_node_editor.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_node_editor.pyi"

    # Configure options
    # options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.ignored_warning_parts = [
        "explicit SafePointerType",
        "Colors[StyleColor_Count]",
        "template <typename T2, typename Tag2>",
        "template <typename Tag>",
        " inline SaveReasonFlags operator |",
        "SaveReasonFlags operator &",
    ]
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_NODE_EDITOR_API"
    options.original_location_flag_show = False
    options.original_signature_flag_show = True
    options.python_run_black_formatter = True
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.namespaces_root = ["ax", "NodeEditor", "ax::NodeEditor"]
    options.class_exclude_by_name__regex = "^NodeId$|^LinkId$|^PinId$"
    options.srcmlcpp_options.header_filter_acceptable__regex = "H__$"
    options.type_replacements.add_last_replacement(r"ImVector<(\w*)>", r"List[\1]")
    options.type_replacements.add_last_replacement(
        r"CanvasSizeModeAlias", "CanvasSizeMode"
    )
    options.member_exclude_by_type__regex = join_string_by_pipe_char(
        [
            # All those types are C style functions pointers
            "ConfigSaveSettings",
            "ConfigLoadSettings",
            "ConfigSaveNodeSettings",
            "ConfigLoadNodeSettings",
            "ConfigSession",
            r"^ImVector",
        ]
    )
    options.srcmlcpp_options.header_filter_acceptable__regex += (
        "|^IMGUI_BUNDLE_PYTHON_API$"
    )

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_node_editor.h")
    generator.process_cpp_file(
        THIS_DIR + "/../imgui_node_editor_immapp/node_editor_default_context.h"
    )

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
