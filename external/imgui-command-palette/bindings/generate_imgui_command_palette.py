# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_imgui_command_palette")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_command_palette.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_command_palette.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["ImCmd"]
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    options.python_run_black_formatter = False
    options.struct_create_default_named_ctor__regex = ""

    # pybind11 stubbornly fails on perfect encapsulation. See https://github.com/pybind/pybind11/issues/2770
    options.fn_exclude_by_name__regex = "Context$"

    options.postprocess_stub_function = lambda s: s.replace("Callable[[int selected_option], None]", "Callable[[int], None]")

    generator = litgen.LitgenGenerator(options)

    generator.process_cpp_file(
        THIS_DIR + "/../imgui-command-palette/imcmd_command_palette.h"
    )
    generator.process_cpp_file(
        THIS_DIR
        + "/../imgui-command-palette-py-wrapper/imgui-command-palette-py-wrapper.h"
    )

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
