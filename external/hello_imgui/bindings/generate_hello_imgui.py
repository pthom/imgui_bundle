# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from srcmlcpp.scrml_warning_settings import WarningType
from codemanip import amalgamated_header
from codemanip.code_utils import join_string_by_pipe_char

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

HELLO_IMGUI_DIR = os.path.realpath(THIS_DIR + "/../hello_imgui")
CPP_HEADERS_DIR = HELLO_IMGUI_DIR + "/src/hello_imgui"


def make_hello_imgui_amalgamated_header():
    hello_imgui_src_dir = HELLO_IMGUI_DIR + "/src/"

    options = amalgamated_header.AmalgamationOptions()

    options.base_dir = hello_imgui_src_dir
    options.local_includes_startwith = "hello_imgui/"
    options.include_subdirs = ["hello_imgui"]
    options.main_header_file = "hello_imgui.h"
    options.dst_amalgamated_header_file = PYDEF_DIR + "/hello_imgui_amalgamation.h"

    amalgamated_header.write_amalgamate_header_file(options)


def main():
    print("autogenerate_hello_imgui")
    make_hello_imgui_amalgamated_header()

    input_cpp_header = THIS_DIR + "/hello_imgui_amalgamation.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_hello_imgui.cpp"
    output_stub_pyi_file = STUB_DIR + "/hello_imgui.pyi"

    # Configure options
    from codemanip.code_replacements import RegexReplacement

    options = litgen.LitgenOptions()
    # options.original_location_flag_show = True
    options.original_signature_flag_show = True
    options.srcmlcpp_options.ignored_warnings = [WarningType.LitgenIgnoreElement]
    options.srcmlcpp_options.ignored_warning_parts = ["gAssetsSubfolderFolderName"]
    options.namespace_names_replacements.add_last_replacement("ImGui", "Imgui")
    options.namespaces_root = ["HelloImGui","ImGuiTheme"]
    options.fn_return_force_policy_reference_for_pointers__regex = (
        join_string_by_pipe_char([r"\bLoadFontTTF\w*", r"MergeFontAwesomeToLastFont"])
    )
    options.var_names_replacements.replacements = [
        RegexReplacement("imGui", "imgui"),
        RegexReplacement("ImGui", "Imgui"),
    ]
    options.function_names_replacements.replacements = [
        # RegexReplacement("imGui", "imgui"),
        RegexReplacement("ImGui", "Imgui"),
    ]
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    # setAssetsFolder & SetAssetsFolder offer the same function
    options.fn_exclude_by_name__regex = r"^setAssetsFolder$|^TranslateCommonGlyphRanges$"

    options.python_run_black_formatter = True

    options.postprocess_stub_function = lambda code: code.replace("(VoidFunction)", "")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
