# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui_kit"


def main() -> None:
    print("autogenerate_imgui_kit")
    input_cpp_header = CPP_HEADERS_DIR + "/imgui_kit.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_kit.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_kit.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"

    options.namespaces_root = ["ImGuiKit"]
    # ImGuiKitIcon_ -> Icon_, as ImPlot drops its own prefix
    options.type_replacements.add_last_replacement(r"ImGuiKit([A-Z][a-zA-Z0-9]*)", r"\1")
    # The touch layer: ImGuiTouchConfig -> TouchConfig, and the namespace ImGuiTouch -> the submodule imgui_kit.touch
    options.type_replacements.add_last_replacement(r"ImGuiTouch([A-Z][a-zA-Z0-9]*_?)(?![A-Za-z0-9_])", r"Touch\1")
    options.namespace_names_replacements.add_last_replacement(r"^ImGuiTouch$", "touch")
    # A C function pointer, set from C++ by the bundle (which installs a Markdown renderer)
    # ResizeHandle is bound by hand (pybind_imgui_kit.cpp): it returns (changed, size), size being an ImVec2
    options.fn_exclude_by_name__regex = "^(SetHelpMarkerTextRenderer|ResizeHandle)$"
    # In the comments' backticks, C++ names become Python names: `ImGui::Text()` -> `imgui.text()`
    options.comments_python_names_in_backticks = True
    options.comments_python_modules = {"ImGuiKit": "imgui_kit", "ImGui": "imgui"}
    options.comments_python_names_of_other_modules = {
        "imgui": litgen.python_names_in_stub(STUB_DIR + "/imgui/__init__.pyi")
    }
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    # The touch layer's config, changed in place from Python
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
