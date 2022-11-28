import os
import patch
import logging

import litgen

from codemanip.code_utils import join_string_by_pipe_char


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imgui-node-editor"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def apply_patch():
    """
    Applies a simple patch to imgui-node-editor that will
    change the type of Config::SettingsFile from char* to std::string

    This is not needed anymore, since we use a fork where the patch is already applied
    """

    this_dir = os.path.realpath(os.path.dirname(__file__))
    target_dir = f"{this_dir}/../external/imgui-node-editor"

    patch_file = f"{target_dir}/../imgui-node-editor_patch_settings_file.patch"
    patch_content = patch.fromfile(patch_file)

    patch_success = patch_content.apply(root=target_dir)
    if not patch_success:
        logging.warning("apply_imgui_string_patch failed")


def autogenerate_imgui_node_editor():
    print("autogenerate_imgui_node_editor")
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_node_editor.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_node_editor.pyi"

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
    options.original_location_flag_show = True
    options.original_signature_flag_show = True
    options.python_run_black_formatter = True
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.namespace_root__regex = "^ax$|^NodeEditor$"
    options.class_exclude_by_name__regex = "^NodeId$|^LinkId$|^PinId$"
    options.srcmlcpp_options.header_filter_acceptable__regex = "H__$"
    options.type_replacements.add_last_replacement(r"ImVector<(\w*)>", r"List[\1]")
    options.type_replacements.add_last_replacement(r"CanvasSizeModeAlias", "CanvasSizeMode")
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

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_node_editor.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    autogenerate_imgui_node_editor()
