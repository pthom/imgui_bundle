# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_microtex"


def main():
    print("autogenerate_imgui_microtex")
    input_cpp_header = CPP_HEADERS_DIR + "/imgui_microtex.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_microtex.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_microtex.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.namespaces_root = ["ImGuiMicroTeX"]

    # Exclude the Pixels member (we provide a custom pixels_as_array() method instead)
    options.member_exclude_by_name__regex = r"^Pixels$"

    # Custom binding: expose Pixels as numpy array via pixels_as_array()
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiMicroTeX::RenderedFormula",
        stub_code='''
    def pixels_as_array(self) -> np.ndarray:
        """Return pixels as a numpy array with shape (height, width, 4) in RGBA format.
        The returned array is a view into the internal buffer (no copy).
        """
        ...
''',
        pydef_code="""
    LG_CLASS.def("pixels_as_array", [](nb::handle self_handle) {
        auto& self = nb::cast<ImGuiMicroTeX::RenderedFormula&>(self_handle);
        size_t shape[3] = {(size_t)self.Height, (size_t)self.Width, 4};
        return nb::ndarray<nb::numpy, uint8_t>(
            self.Pixels.data(),
            3, shape,
            self_handle  // owner: the RenderedFormula stays alive while the array exists
        );
    },
    "Return pixels as a numpy array with shape (height, width, 4) in RGBA format.");
""",
    )

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
