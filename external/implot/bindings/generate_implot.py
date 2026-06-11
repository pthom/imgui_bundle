# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from litgen_options_implot import litgen_options_implot


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot"


def _add_implot_spec_array_bindings(options: litgen.LitgenOptions) -> None:
    """Add custom bindings for ImPlotSpec pointer-array fields so they accept numpy arrays.
    This function is copied into _add_implot3d_spec_array_bindings for ImPlot3D / generate_implot3d.py
    (both libs use the same Spec API)
    """

    # Exclude pointer-array fields from auto-generation;
    # custom bindings below accept numpy arrays instead of raw pointers.
    options.member_exclude_by_name__regex += "|^LineColors$|^FillColors$|^MarkerLineColors$|^MarkerFillColors$|^MarkerSizes$"

    # Build pydef and stub code for all 5 array fields
    color_fields = [
        ("line_colors", "LineColors", "array of colors (np.uint32) for each line. Must have the same length as the data arrays. If None, use LineColor for all lines."),
        ("fill_colors", "FillColors", "array of colors (np.uint32) for each fill. Must have the same length as the data arrays. If None, use FillColor for all fills."),
        ("marker_line_colors", "MarkerLineColors", "array of colors (np.uint32) for each marker edge. Must have the same length as the data arrays. If None, use MarkerLineColor for all markers."),
        ("marker_fill_colors", "MarkerFillColors", "array of colors (np.uint32) for each marker face. Must have the same length as the data arrays. If None, use MarkerFillColor for all markers."),
    ]
    float_fields = [
        ("marker_sizes", "MarkerSizes", "array of sizes (np.float32) for each marker. Must have the same length as the data arrays. If None, use MarkerSize for all markers."),
    ]

    stub_lines = []
    pydef_lines = []

    for py_name, cpp_name, doc in color_fields:
        stub_lines.append(f'    {py_name}: Optional[np.ndarray] = None  # {doc}')
        pydef_lines.append(f"""
    LG_CLASS.def_prop_rw("{py_name}",
        [](ImPlotSpec& self) -> uintptr_t {{ return reinterpret_cast<uintptr_t>(self.{cpp_name}); }},
        [](ImPlotSpec& self, nb::ndarray<nb::ro>& arr) {{
            if (arr.dtype() != nb::dtype<uint32_t>())
                throw nb::type_error("{py_name} requires a np.uint32 array");
            self.{cpp_name} = (ImU32*)arr.data();
        }},
        "{doc}");""")

    for py_name, cpp_name, doc in float_fields:
        stub_lines.append(f'    {py_name}: Optional[np.ndarray] = None  # {doc}')
        pydef_lines.append(f"""
    LG_CLASS.def_prop_rw("{py_name}",
        [](ImPlotSpec& self) -> uintptr_t {{ return reinterpret_cast<uintptr_t>(self.{cpp_name}); }},
        [](ImPlotSpec& self, nb::ndarray<nb::ro>& arr) {{
            if (arr.dtype() != nb::dtype<float>())
                throw nb::type_error("{py_name} requires a np.float32 array");
            self.{cpp_name} = (float*)arr.data();
        }},
        "{doc}");""")

    options.custom_bindings.add_custom_bindings_to_class(
        "ImPlotSpec",
        stub_code="\n".join(stub_lines) + "\n",
        pydef_code="\n".join(pydef_lines) + "\n",
    )


def autogenerate_implot():
    print("autogenerate_implot")
    input_cpp_header = CPP_HEADERS_DIR + "/implot.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_implot.cpp"
    output_stub_pyi_file = STUB_DIR + "/implot/__init__.pyi"

    # Configure options
    options = litgen_options_implot()
    options.srcmlcpp_options.flag_show_progress = True

    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    # Custom bindings for ImPlotSpec array fields: accept typed numpy arrays
    _add_implot_spec_array_bindings(options)

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


def autogenerate_implot_internal() -> None:
    print("autogenerate_implot_internal")
    options = litgen_options_implot()
    options.srcmlcpp_options.flag_show_progress = True
    options.python_run_black_formatter = False

    options.fn_exclude_by_name__regex += "|" + "|".join(
        [
            "^ImMinMaxArray$",
            "^ImMinArray$",
            "^ImMaxArray$",
            "^ImSum$",
            "^FormatDate$",
            "^FormatDateTime$",
            "^FormatTime$",
            "^LabelAxisValue$",
            "^MkTime$",
            "^MkGmtTime$",
            "^GetGmtTime$",
            "^MkLocTime$",
            "^GetLocTime$",
            "^GetTime$",
            "^Formatter_Default$",
            "^Formatter_Logit$",
            "^Formatter_Time$",
        ]
    )
    options.member_exclude_by_name__regex += "|^Formatter$|^Locator$"
    options.member_exclude_by_type__regex += "|^ImPlotTransform$|^ImPlotFormatter$|^tm$"
    options.fn_force_lambda__regex += "|^GetText$"

    options.srcmlcpp_options.ignored_warning_parts.append("Excluding template type ImVector")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=CPP_HEADERS_DIR + "/implot_internal.h",
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_implot_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/implot/internal.pyi",
    )


def sandbox():
    code = """
    """
    options = litgen_options_implot()
    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_code(code, "file")
    print(generator.stub_code())


def main():
    autogenerate_implot()
    autogenerate_implot_internal()
    # sandbox()


if __name__ == "__main__":
    main()
