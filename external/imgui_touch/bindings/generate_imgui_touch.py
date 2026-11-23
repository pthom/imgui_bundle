# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_touch"


def main() -> None:
    print("autogenerate_imgui_touch")
    input_cpp_header = CPP_HEADERS_DIR + "/imgui_touch.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_touch.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_touch.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"

    options.namespaces_root = ["ImGuiTouch"]
    # ImGuiTouchConfig -> Config, ImGuiTouchScrollMode_ -> ScrollMode_, as ImPlot drops its own prefix
    options.type_replacements.add_last_replacement(r"ImGuiTouch([A-Z][a-zA-Z0-9]*_?)(?![A-Za-z0-9_])", r"\1")
    # In the comments' backticks, C++ names become Python names: `ImGui::Text()` -> `imgui.text()`
    options.comments_python_names_in_backticks = True
    options.comments_python_modules = {"ImGuiTouch": "imgui_touch", "ImGui": "imgui"}
    options.comments_python_names_of_other_modules = {
        "imgui": litgen.python_names_in_stub(STUB_DIR + "/imgui/__init__.pyi")
    }
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    # The config, changed in place from Python
    options.fn_return_force_policy_reference_for_references__regex = r"^GetConfig$"
    options.original_signature_flag_show = True
    options.python_run_black_formatter = True

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
