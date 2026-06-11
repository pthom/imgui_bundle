# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from litgen_options_implot3d import litgen_options_implot3d


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot3d"


def _add_implot3d_spec_array_bindings(options: litgen.LitgenOptions) -> None:
    """Add custom bindings for ImPlot3DSpec pointer-array fields so they accept numpy arrays.
    This function is a copy of _add_implot_spec_array_bindings from ImPlot / generate_implot.py
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
        [](ImPlot3DSpec& self) -> uintptr_t {{ return reinterpret_cast<uintptr_t>(self.{cpp_name}); }},
        [](ImPlot3DSpec& self, nb::ndarray<nb::ro>& arr) {{
            if (arr.dtype() != nb::dtype<uint32_t>())
                throw nb::type_error("{py_name} requires a np.uint32 array");
            self.{cpp_name} = (ImU32*)arr.data();
        }},
        "{doc}");""")

    for py_name, cpp_name, doc in float_fields:
        stub_lines.append(f'    {py_name}: Optional[np.ndarray] = None  # {doc}')
        pydef_lines.append(f"""
    LG_CLASS.def_prop_rw("{py_name}",
        [](ImPlot3DSpec& self) -> uintptr_t {{ return reinterpret_cast<uintptr_t>(self.{cpp_name}); }},
        [](ImPlot3DSpec& self, nb::ndarray<nb::ro>& arr) {{
            if (arr.dtype() != nb::dtype<float>())
                throw nb::type_error("{py_name} requires a np.float32 array");
            self.{cpp_name} = (float*)arr.data();
        }},
        "{doc}");""")

    options.custom_bindings.add_custom_bindings_to_class(
        "ImPlot3DSpec",
        stub_code="\n".join(stub_lines) + "\n",
        pydef_code="\n".join(pydef_lines) + "\n",
    )


def autogenerate_implot3d():
    print("autogenerate_implot3d")
    input_cpp_header = CPP_HEADERS_DIR + "/implot3d.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_implot3d.cpp"
    output_stub_pyi_file = STUB_DIR + "/implot3d/__init__.pyi"

    # Configure options
    options = litgen_options_implot3d()
    options.srcmlcpp_options.flag_show_progress = True
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"

    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    # Custom bindings for ImPlot3DSpec array fields: accept typed numpy arrays
    _add_implot3d_spec_array_bindings(options)

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


def autogenerate_implot3d_internal() -> None:
    print("autogenerate_implot3d_internal")
    options = litgen_options_implot3d()
    options.srcmlcpp_options.flag_show_progress = True
    options.python_run_black_formatter = False

    options.srcmlcpp_options.ignored_warning_parts.append("Excluding template type ImVector")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=CPP_HEADERS_DIR + "/implot3d_internal.h",
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_implot3d_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/implot3d/internal.pyi",
    )


def sandbox():
    code = """
enum ImPlot3DFlags_ {
    ImPlot3DFlags_None = 0,             // Default
    ImPlot3DFlags_NoTitle = 1 << 0,     // Hide plot title
    ImPlot3DFlags_NoLegend = 1 << 1,    // Hide plot legend
    ImPlot3DFlags_NoMouseText = 1 << 2, // Hide mouse position in plot coordinates
    ImPlot3DFlags_NoClip = 1 << 3,      // Disable 3D box clipping
    ImPlot3DFlags_NoMenus = 1 << 4,     // The user will not be able to open context menus
    ImPlot3DFlags_CanvasOnly = ImPlot3DFlags_NoTitle | ImPlot3DFlags_NoLegend | ImPlot3DFlags_NoMouseText,
};
    """
    options = litgen_options_implot3d()
    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_code(code, "file")
    print(generator.stub_code())


def main():
    autogenerate_implot3d()
    autogenerate_implot3d_internal()
    # sandbox()


if __name__ == "__main__":
    main()
