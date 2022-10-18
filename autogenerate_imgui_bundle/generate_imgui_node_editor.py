import os

import litgen

from codemanip.code_utils import join_string_by_pipe_char

from litgen.options_customized.litgen_options_imgui import litgen_options_imgui, ImguiOptionsType


_THIS_DIR = os.path.dirname(__file__)
BUNDLE_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = BUNDLE_DIR + "/external/imgui-node-editor"
CPP_GENERATED_PYBIND_DIR = BUNDLE_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_node_editor():
    input_cpp_headers = [CPP_HEADERS_DIR + "/imgui_node_editor.h"]
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_node_editor.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_node_editor.pyi"

    # Configure options
    # options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "^ax$|^NodeEditor$"
    options.class_exclude_by_name__regex = "^NodeId$|^LinkId$|^PinId$"
    options.srcmlcpp_options.header_filter_acceptable__regex = "H__$"
    options.member_exclude_by_type__regex = join_string_by_pipe_char(
        [
            # All those types are C style functions pointers
            "ConfigSaveSettings",
            "ConfigLoadSettings",
            "ConfigSaveNodeSettings",
            "ConfigLoadNodeSettings",
            "ConfigSession",
        ]
    )

    # options.class_template_options.add_specialization(
    #
    # )

    litgen.write_generated_code_for_files(
        options,
        input_cpp_header_files=input_cpp_headers,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    print("autogenerate_imgui_node_editor")
    autogenerate_imgui_node_editor()
