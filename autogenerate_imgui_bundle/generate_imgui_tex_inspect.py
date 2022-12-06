import os

import litgen
from codemanip.code_utils import join_string_by_pipe_char

_THIS_DIR = os.path.dirname(__file__)
LG_HELLO_IMGUI_DIR = os.path.realpath(_THIS_DIR + "/..")
CPP_HEADERS_DIR = LG_HELLO_IMGUI_DIR + "/external/imgui_tex_inspect"
CPP_GENERATED_PYBIND_DIR = LG_HELLO_IMGUI_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate_imgui_tex_inspect():
    print("autogenerate_imgui_tex_inspect")
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui_tex_inspect.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/imgui_bundle/imgui_tex_inspect.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespace_root__regex = "ImGuiTexInspect"
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
    options.srcmlcpp_options.flag_show_progress = True

    generator = litgen.LitgenGenerator(options)

    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_tex_inspect.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_tex_inspect_demo.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    autogenerate_imgui_tex_inspect()
