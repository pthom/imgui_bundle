# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen
from codemanip.code_utils import join_string_by_pipe_char

THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_tex_inspect"


def main():
    print("autogenerate_imgui_tex_inspect")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_tex_inspect.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_tex_inspect.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImGuiTexInspect"]
    options.namespace_names_replacements.add_last_replacement("ImGui", "Imgui")
    options.srcmlcpp_options.ignored_warning_parts = ["CurrentInspector_SetColorMatrix"]
    options.fn_exclude_by_name__regex = join_string_by_pipe_char(
        [
            "^LoadTexture$",  # published elsewhere by hello_imgui
            "CurrentInspector_SetColorMatrix",  # Bad signature
            "CurrentInspector_ResetColorMatrix",
            "GetTexel",  # internal function
            "DrawAnnotations",  # internal function
            "GetAnnotationDesc",  # internal function
            "CreateContext",
            "DestroyContext",
            "SetCurrentContext",  # Context is perfectly encapsulated, and pybind does not like this...
        ]
    )
    options.class_exclude_by_name__regex = "^BufferDesc$|^AnnotationsDesc$"

    generator = litgen.LitgenGenerator(options)

    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_tex_inspect.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_tex_inspect_demo.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
