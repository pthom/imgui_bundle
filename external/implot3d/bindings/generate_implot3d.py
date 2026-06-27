# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from string import Template

import litgen
from litgen_options_implot3d import litgen_options_implot3d


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../implot3d"


# NOTE: _SPEC_ARRAY_PYDEF_TEMPLATE, _SPEC_ARRAY_FIELDS and _add_spec_array_bindings
# below are a copy of the same code in ImPlot / generate_implot.py (both libs share
# the same Spec array API). Keep the two copies in sync.

# C++ template for one Spec array field (issue #484).
# The setter keeps a reference to the numpy array on the Spec instance (via a
# dynamic attribute "$ref"), so it is not garbage collected while ImPlot3D holds
# the raw data pointer. The getter returns that stored array (a real
# np.ndarray, identity preserved), not the raw pointer address.
# Uses string.Template ($ placeholders) to avoid escaping the C++ braces.
_SPEC_ARRAY_PYDEF_TEMPLATE = Template('''
    LG_CLASS.def_prop_rw("$py_name",
        [](nb::handle self) -> nb::object {
            if (nb::hasattr(self, "$ref"))
                return self.attr("$ref");
            return nb::none();
        },
        [](nb::handle self, nb::object value) {
            $spec& spec = nb::cast<$spec&>(self);
            if (value.is_none()) {
                spec.$cpp_name = nullptr;
                if (nb::hasattr(self, "$ref"))
                    nb::delattr(self, "$ref");
                return;
            }
            if (!nb::isinstance<nb::ndarray<nb::ro>>(value))
                throw nb::type_error("$py_name requires a np.$np_name array");
            auto arr = nb::cast<nb::ndarray<nb::ro>>(value);
            if (arr.dtype() != nb::dtype<$cpp_dtype>())
                throw nb::type_error("$py_name requires a np.$np_name array");
            // Reject non-contiguous input (e.g. a slice): we keep the raw data
            // pointer, so a contiguous copy would dangle. Strides are in elements.
            if (arr.ndim() != 1 || arr.stride(0) != 1)
                throw nb::value_error("$py_name requires a 1-D contiguous array (use np.ascontiguousarray)");
            spec.$cpp_name = ($cpp_elem*)arr.data();
            // Keep the array alive for the Spec's lifetime, and let the getter
            // return the very object the caller passed (identity preserved):
            self.attr("$ref") = value;
        },
        nb::arg("value").none(),
        "$doc");''')

# (py_name, cpp_name, np_name, cpp_dtype, cpp_elem, doc) for each Spec array field.
_SPEC_ARRAY_FIELDS = [
    ("line_colors", "LineColors", "uint32", "uint32_t", "ImU32", "array of colors (np.uint32) for each line. Must have the same length as the data arrays. If None, use LineColor for all lines."),
    ("fill_colors", "FillColors", "uint32", "uint32_t", "ImU32", "array of colors (np.uint32) for each fill. Must have the same length as the data arrays. If None, use FillColor for all fills."),
    ("marker_line_colors", "MarkerLineColors", "uint32", "uint32_t", "ImU32", "array of colors (np.uint32) for each marker edge. Must have the same length as the data arrays. If None, use MarkerLineColor for all markers."),
    ("marker_fill_colors", "MarkerFillColors", "uint32", "uint32_t", "ImU32", "array of colors (np.uint32) for each marker face. Must have the same length as the data arrays. If None, use MarkerFillColor for all markers."),
    ("marker_sizes", "MarkerSizes", "float32", "float", "float", "array of sizes (np.float32) for each marker. Must have the same length as the data arrays. If None, use MarkerSize for all markers."),
]


def _add_spec_array_bindings(options: litgen.LitgenOptions, spec_cpp_name: str) -> None:
    """Add custom bindings for the Spec pointer-array fields so they accept numpy arrays
    and keep them alive (issue #484). `spec_cpp_name` is "ImPlotSpec" or "ImPlot3DSpec"."""

    options.member_exclude_by_name__regex += "|^LineColors$|^FillColors$|^MarkerLineColors$|^MarkerFillColors$|^MarkerSizes$"

    # Make the Spec class accept dynamic attributes so each setter can stash the
    # numpy array on the instance (keeps it alive + retrievable by the getter).
    options.class_dynamic_attributes__regex += f"|^{spec_cpp_name}$"

    stub_lines = []
    pydef_lines = []
    for py_name, cpp_name, np_name, cpp_dtype, cpp_elem, doc in _SPEC_ARRAY_FIELDS:
        stub_lines.append(f'    {py_name}: Optional[np.ndarray] = None  # {doc}')
        pydef_lines.append(_SPEC_ARRAY_PYDEF_TEMPLATE.substitute(
            py_name=py_name, cpp_name=cpp_name, np_name=np_name,
            cpp_dtype=cpp_dtype, cpp_elem=cpp_elem, doc=doc,
            ref=f"_{py_name}_ref", spec=spec_cpp_name,
        ))

    options.custom_bindings.add_custom_bindings_to_class(
        spec_cpp_name,
        stub_code="\n".join(stub_lines) + "\n",
        pydef_code="\n".join(pydef_lines) + "\n",
    )


def _add_implot3d_spec_array_bindings(options: litgen.LitgenOptions) -> None:
    _add_spec_array_bindings(options, "ImPlot3DSpec")


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
