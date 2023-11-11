# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import Optional
import copy
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
    options.class_override_virtual_methods_in_python__regex = r".*"
    options.struct_create_default_named_ctor__regex = ""
    options.python_run_black_formatter = False

    generator = litgen.LitgenGenerator(options)

    def process_one_file_backup_options(
        code: Optional[str], filename: str, options: litgen.LitgenOptions
    ):
        options_backup = generator.lg_context.options
        generator.lg_context.options = options
        generator.process_cpp_code(code=code, filename=filename)
        generator.lg_context.options = options_backup

    def process_one_amalgamated_file(header_file: str, options: litgen.LitgenOptions):
        amalgamation = make_amalgamated_header(header_file)
        process_one_file_backup_options(
            code=amalgamation, filename=header_file, options=options
        )

    # Process Editable
    options_pure = copy.deepcopy(options)
    options_pure.class_template_options.add_specialization(
        "Editable", ["SelectedPoints", "int", "Matrix16", "Range"], cpp_synonyms_list_str=[]
    )
    header_file = f"{HEADER_PARENT_DIR}/ImGuizmoPure/Editable.h"
    process_one_file_backup_options(None, header_file, options_pure)
    options.srcmlcpp_options.ignored_warning_parts.append("struct Editable")
    options.type_replacements.add_last_replacement(
        "Editable<SelectedPoints>", "EditableSelectedPoints"
    )
    options.type_replacements.add_last_replacement("Editable<int>", "EditableInt")
    options.type_replacements.add_last_replacement(
        "Editable<Matrix16>", "EditableMatrix16"
    )
    options.type_replacements.add_last_replacement("Editable<Range>", "EditableRange")

    # Process ImCurveEditStl
    options_curve = copy.deepcopy(options)
    options_curve.fn_exclude_by_name__regex = "^Edit$|GetPointCount$|^GetPoints$"
    options_curve.fn_exclude_by_param_type__regex = "^Delegate[ ]*&$"
    process_one_amalgamated_file("ImCurveEditPure.h", options_curve)

    # Process ImGradientStl
    options_gradient = copy.deepcopy(options)
    options_gradient.fn_exclude_by_name__regex = "^Edit$|^GetPointCount$|^GetPoints$"
    process_one_amalgamated_file("ImGradientPure.h", options_gradient)

    # Process ImZoomSlider
    options_slider = copy.deepcopy(options)
    options_slider.srcmlcpp_options.ignored_warning_parts.append(
        "Ignoring template function"
    )
    options_slider.var_names_replacements.add_last_replacement(
        "im_gui_zoom_slider_flags_", ""
    )
    options_slider.type_replacements.add_last_replacement(
        "ImGuiPopupFlags_", "ImGuiZoomSliderFlags_"
    )
    process_one_amalgamated_file("ImZoomSliderPure.h", options_slider)

    # Process ImSequencer:
    # abandoned due to double pointer in the public API
    # --------------
    # options_sequencer = copy.deepcopy(options)
    # options_sequencer.fn_exclude_by_name__regex = r"^Get$"
    # process_one_amalgamated_file("ImSequencerPure.h", options_sequencer)

    # Process GraphEditor:
    # cowardly avoided because of double pointers in structs + pointer to enum in params
    # --------------
    # options_graph = copy.deepcopy(options)
    # header_file = f"{HEADER_PARENT_DIR}/{OFFICIAL_SUBDIR}/GraphEditor.h"
    # process_one_file_backup_options(code=None, filename=header_file, options=options_graph)

    # Process ImGuizmo:
    options_guizmo = copy.deepcopy(options)

    def preprocess_code(code: str) -> str:
        code = code.replace("IMGUIZMO_NAMESPACE", "ImGuizmo")
        # code = code.replace("COLOR::COUNT", "15")
        return code

    options_guizmo.srcmlcpp_options.code_preprocess_function = preprocess_code
    options_guizmo.srcmlcpp_options.ignored_warning_parts += [
        "ImVec4 Colors[COLOR::COUNT]",
        "Ignoring template class",
        "float values[N]",
    ]
    options_guizmo.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options_guizmo.fn_exclude_by_param_type__regex = r"float[ ]*\*"
    options_guizmo.class_exclude_by_name__regex = r"^Matrix16$|^Matrix6$|^Matrix3$"
    options_guizmo.fn_force_overload__regex = "DecomposeMatrixToComponents|RecomposeMatrixFromComponents|DrawCubes|DrawGrid|Manipulate"
    process_one_amalgamated_file("ImGuizmoPure.h", options_guizmo)

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
