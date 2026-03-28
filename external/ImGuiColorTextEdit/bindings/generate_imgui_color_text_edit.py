# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from srcmlcpp.scrml_warning_settings import WarningType


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

MAIN_DIR = THIS_DIR + "/../"


def main():
    print("autogenerate_imgui_color_text_edi")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_color_text_edit.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_color_text_edit.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])
    options.srcmlcpp_options.ignored_warnings = [
        WarningType.LitgenClassMemberSkipBitfield
    ]
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"

    # Exclude void* userData member from Decorator (not bindable in Python)
    options.member_exclude_by_name__regex = r"^userData$"

    # Some structs contain a private member named main, which confuses srcML.
    # Inline class-member declarations (`} cursors;` etc.) are not supported by srcML.
    # Iterator operators are not bindable in Python.
    options.srcmlcpp_options.ignored_warning_parts += [
        "main =", "operator*", "operator->", "operator++",
        "} cursors;", "} document;", "} transactions;",
        "} colorizer;", "} bracketeer;", "} autocomplete;",
    ]

    # Workaround for srcML bug: expressions with parentheses inside template arguments
    # (e.g. static_cast<size_t>(...)) break the parser. Use C-style cast instead.
    # See https://github.com/srcML/srcML/issues/2327
    def preprocess(code: str) -> str:
        return code.replace("static_cast<size_t>(Color::count)", "(size_t)(Color::count)")
    options.srcmlcpp_options.code_preprocess_function = preprocess

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(MAIN_DIR + "/ImGuiColorTextEdit/TextEditor.h")
    generator.process_cpp_file(MAIN_DIR + "/ImGuiColorTextEdit/TextDiff.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
