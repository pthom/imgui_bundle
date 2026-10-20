# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_explorer"


def main() -> None:
    print("autogenerate_imgui_explorer")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_explorer.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_explorer.pyi"

    options = litgen.LitgenOptions()
    options.use_nanobind()
    # In the comments' backticks, C++ names become Python names: `ImGui::Text()` -> `imgui.text()`
    options.comments_python_names_in_backticks = True
    options.comments_python_modules = {"ImGui": "imgui"}
    options.comments_python_names_of_other_modules = {
        "imgui": litgen.python_names_in_stub(STUB_DIR + "/imgui/__init__.pyi")
    }
    options.python_run_black_formatter = True
    options.original_signature_flag_show = True

    options.var_names_replacements.add_first_replacement("ImGui", "Imgui")
    options.var_names_replacements.add_first_replacement("ImPlot", "Implot")
    options.function_names_replacements.add_first_replacement("ImGui", "Imgui")

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_explorer.h")
    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
