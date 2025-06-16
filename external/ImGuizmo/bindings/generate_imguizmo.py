# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from codemanip import amalgamated_header


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


HEADER_PARENT_DIR = THIS_DIR + "/../"
STL_SUBDIR = "ImGuizmoPure"
OFFICIAL_SUBDIR = "ImGuizmo"


def make_amalgamated_header(header_file: str) -> str:
    options = amalgamated_header.AmalgamationOptions()

    options.base_dir = HEADER_PARENT_DIR
    options.local_includes_startwith = OFFICIAL_SUBDIR
    options.include_subdirs = [OFFICIAL_SUBDIR]
    options.main_header_file = STL_SUBDIR + "/" + header_file

    amalgamation = amalgamated_header.amalgamation_content(options)
    return amalgamation


def main():
    print("autogenerate_imguizmo")

    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imguizmo.cpp"
    output_stub_pyi_file = STUB_DIR + "/imguizmo.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    options.class_override_virtual_methods_in_python__regex = r".*"
    options.struct_create_default_named_ctor__regex = ""
    options.python_run_black_formatter = False

    generator = litgen.LitgenGenerator(options)

    def preprocess_code(code: str) -> str:
        code = code.replace("IMGUIZMO_NAMESPACE", "ImGuizmo")
        # code = code.replace("COLOR::COUNT", "15")
        return code

    options.srcmlcpp_options.code_preprocess_function = preprocess_code
    options.srcmlcpp_options.ignored_warning_parts += [
        "ImVec4 Colors[COLOR::COUNT]",
        "Ignoring template class",
        "float values[N]",
    ]
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options.fn_exclude_by_param_type__regex = r"float[ ]*\*"
    options.fn_exclude_by_name__regex = r"^SetID$"  # deprecated function
    options.fn_force_overload__regex = "DecomposeMatrixToComponents|RecomposeMatrixFromComponents|DrawCubes|DrawGrid|Manipulate"
    amalgamation = make_amalgamated_header("ImGuizmoPure.h")
    generator.process_cpp_code(code=amalgamation, filename="ImGuizmoPure.h")
    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
