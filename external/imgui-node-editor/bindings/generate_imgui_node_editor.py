# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen

from codemanip.code_utils import join_string_by_pipe_char

THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

CPP_HEADERS_DIR = THIS_DIR + "/../imgui-node-editor"


def main() -> None:
    print("autogenerate_imgui_node_editor")
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_node_editor.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_node_editor.pyi"

    # Configure options
    # options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    options.srcmlcpp_options.ignored_warning_parts = [
        "explicit SafePointerType",
        "Colors[StyleColor_Count]",
        "template <typename T2, typename Tag2>",
        "template <typename Tag>",
        " inline SaveReasonFlags operator |",
        "SaveReasonFlags operator &",
    ]
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_NODE_EDITOR_API"
    options.original_location_flag_show = False
    options.original_signature_flag_show = True
    options.python_run_black_formatter = True
    options.fn_return_force_policy_reference_for_references__regex = r".*"
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.namespaces_root = ["ax", "NodeEditor", "ax::NodeEditor"]
    options.class_exclude_by_name__regex = "^NodeId$|^LinkId$|^PinId$"
    options.srcmlcpp_options.header_filter_acceptable__regex = "H__$"
    options.type_replacements.add_last_replacement(r"ImVector<(\w*)>", r"List[\1]")
    options.type_replacements.add_last_replacement(
        r"CanvasSizeModeAlias", "CanvasSizeMode"
    )
    options.member_exclude_by_type__regex = join_string_by_pipe_char(
        [
            # All those types are C style functions pointers
            "ConfigSaveSettings",
            "ConfigLoadSettings",
            "ConfigSaveNodeSettings",
            "ConfigLoadNodeSettings",
            "ConfigSession",
            r"^ImVector",
        ]
    )
    # ed::InputTextMultiline() edits a char buffer. It is not needed in Python: inside a node,
    # imgui.input_text_multiline() is redirected to it (see ImGuiContext::InputTextMultilineOverride)
    options.fn_exclude_by_name__regex = "^InputTextMultiline$"

    # Functions that fill an array provided by the caller: replaced by versions returning a list
    # (see imgui_node_editor_pywrappers.h)
    options.fn_exclude_by_name_and_signature = {
        "GetSelectedNodes": "NodeId *, int",
        "GetSelectedLinks": "LinkId *, int",
        "GetActionContextNodes": "NodeId *, int",
        "GetActionContextLinks": "LinkId *, int",
        "GetOrderedNodeIds": "NodeId *, int",
    }
    # (their names are overloaded in C++: the bindings must call them through a lambda)
    options.fn_force_lambda__regex = r"GetSelectedNodes|GetSelectedLinks|GetActionContextNodes|GetActionContextLinks|GetOrderedNodeIds"

    # Config::SettingsFile is a `const char*`, and the editor keeps the pointer (it reads it at each load / save):
    # a Python str cannot be stored there. It is published as a property whose setter interns the string.
    options.member_exclude_by_name__regex = "^SettingsFile$"
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ax::NodeEditor::Config",
        stub_code='''
        # File where the state of the editor is saved (positions of the nodes, view, selection). None: no settings file
        settings_file: Optional[str]
    ''',
        pydef_code="""
        LG_CLASS.def_prop_rw("settings_file",
            [](const ax::NodeEditor::Config& self) -> std::optional<std::string> {
                if (self.SettingsFile == nullptr)
                    return std::nullopt;
                return std::string(self.SettingsFile);
            },
            [](ax::NodeEditor::Config& self, const std::optional<std::string>& value) {
                // The strings are interned in a node-based container: its elements never move and are never freed,
                // so the pointer stays valid for the whole life of the editor (and of the copies of the Config).
                // Memory use is bounded by the number of distinct file names.
                static std::set<std::string> interned_strings;
                self.SettingsFile = value.has_value() ? interned_strings.insert(*value).first->c_str() : nullptr;
            },
            nb::arg("value").none(),
            "File where the state of the editor is saved (positions of the nodes, view, selection). None: no settings file");
    """,
    )

    # Style::Colors is a C array: it is published through color_() and set_color_()
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ax::NodeEditor::Style",
        stub_code='''
        def color_(self, idx_color: StyleColor) -> ImVec4:
            """Python API for Style::Colors[]: returns a reference to the color (0 <= idx_color < StyleColor.count)"""
            ...
        def set_color_(self, idx_color: StyleColor, color: ImVec4Like) -> None:
            """Python API for Style::Colors[]: sets the color (0 <= idx_color < StyleColor.count)"""
            ...
    ''',
        pydef_code="""
        LG_CLASS.def("color_",
            [](ax::NodeEditor::Style& self, ax::NodeEditor::StyleColor idx_color) -> ImVec4& {
                IM_ASSERT((idx_color >= 0) && (idx_color < ax::NodeEditor::StyleColor_Count));
                return self.Colors[idx_color];
            },
            nb::arg("idx_color"),
            "Python API for Style::Colors[]: returns a reference to the color (0 <= idx_color < StyleColor.count)",
            nb::rv_policy::reference);
        LG_CLASS.def("set_color_",
            [](ax::NodeEditor::Style& self, ax::NodeEditor::StyleColor idx_color, ImVec4 color) {
                IM_ASSERT((idx_color >= 0) && (idx_color < ax::NodeEditor::StyleColor_Count));
                self.Colors[idx_color] = color;
            },
            nb::arg("idx_color"), nb::arg("color"),
            "Python API for Style::Colors[]: sets the color (0 <= idx_color < StyleColor.count)");
    """,
    )

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_node_editor.h")
    generator.process_cpp_file(THIS_DIR + "/../imgui_node_editor_pywrappers/imgui_node_editor_pywrappers.h")
    generator.process_cpp_file(
        THIS_DIR + "/../imgui_node_editor_immapp/node_editor_default_context.h"
    )

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
