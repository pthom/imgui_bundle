# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
import time
from functools import wraps

import litgen
from litgen_options_imgui import (
    litgen_options_imgui,
    ImguiOptionsType,
)


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

FLAG_DOCKING_BRANCH = True
CPP_HEADERS_DIR = THIS_DIR + "/../imgui"


def my_time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.6f} seconds to run.")
        return result

    return wrapper


def autogenerate_imgui() -> None:
    print("Processing imgui.h")
    # Generate for imgui.h
    options_imgui = litgen_options_imgui(
        ImguiOptionsType.imgui_h, docking_branch=FLAG_DOCKING_BRANCH
    )

    # GetStyleColorVec4 returns const ImVec4& (reference into the style array).
    # With rv_policy::reference, Python can mutate the style directly without PushStyleColor.
    # Exclude only for imgui (not shared options, since ImPlot's version returns by value).
    options_imgui.fn_exclude_by_name__regex += r"|^GetStyleColorVec4$"
    # Custom binding returns a copy instead.
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def get_style_color_vec4(idx: Col) -> ImVec4:
            """retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in.
            (Note: returns a copy, not a reference to the internal style color.)"""
            ...
    ''',
        pydef_code="""
        LG_MODULE.def("get_style_color_vec4",
            [](ImGuiCol idx) -> ImVec4 { return ImGui::GetStyleColorVec4(idx); },
            nb::arg("idx"),
            "retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in.");
    """,
    )

    # ColorConvertRGBtoHSV / ColorConvertHSVtoRGB: output params should not be
    # required as inputs. Custom bindings take only the 3 input values.
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def color_convert_rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
            """Convert rgb floats ([0-1],[0-1],[0-1]) to hsv floats ([0-1],[0-1],[0-1])"""
            ...
        def color_convert_hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
            """Convert hsv floats ([0-1],[0-1],[0-1]) to rgb floats ([0-1],[0-1],[0-1])"""
            ...
    ''',
        pydef_code="""
        LG_MODULE.def("color_convert_rgb_to_hsv",
            [](float r, float g, float b) -> std::tuple<float, float, float> {
                float h, s, v;
                ImGui::ColorConvertRGBtoHSV(r, g, b, h, s, v);
                return std::make_tuple(h, s, v);
            }, nb::arg("r"), nb::arg("g"), nb::arg("b"),
            "Convert rgb floats ([0-1],[0-1],[0-1]) to hsv floats ([0-1],[0-1],[0-1])");
        LG_MODULE.def("color_convert_hsv_to_rgb",
            [](float h, float s, float v) -> std::tuple<float, float, float> {
                float r, g, b;
                ImGui::ColorConvertHSVtoRGB(h, s, v, r, g, b);
                return std::make_tuple(r, g, b);
            }, nb::arg("h"), nb::arg("s"), nb::arg("v"),
            "Convert hsv floats ([0-1],[0-1],[0-1]) to rgb floats ([0-1],[0-1],[0-1])");
    """,
    )

    # ImFont::CalcWordWrapPosition returns a pointer inside the text (excluded in the shared options):
    # the Python version returns an index instead.
    options_imgui.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImFont",
        stub_code='''
        def calc_word_wrap_position_python(self, size: float, text: str, wrap_width: float) -> int:
            """Python API for CalcWordWrapPosition (will return an index in the text, not a pointer)"""
            ...
    ''',
        pydef_code="""
        LG_CLASS.def("calc_word_wrap_position_python",
            [](ImFont& self, float size, const char* text, float wrap_width) -> int {
                const char* text_end = text + strlen(text);
                const char* word_wrap_eol = self.CalcWordWrapPosition(size, text, text_end, wrap_width);
                return (int)(word_wrap_eol - text);
            },
            nb::arg("size"), nb::arg("text"), nb::arg("wrap_width"),
            "Python API for CalcWordWrapPosition (will return an index in the text, not a pointer)");
    """,
    )

    # Simplified versions of MenuItem and BeginTabItem (the C++ overloads with an output param are also bound)
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def menu_item_simple(label: str, shortcut: Optional[str] = None, selected: bool = False, enabled: bool = True) -> bool:
            """return True when activated. (simplified version of menu_item, where selected is read-only)"""
            pass
        def begin_tab_item_simple(label: str, flags: TabItemFlags = 0) -> bool:
            """create a Tab (non-closable). Returns True if the Tab is selected."""
            pass
    ''',
        pydef_code="""
        LG_MODULE.def("menu_item_simple",
            [](const char* label, std::optional<std::string> shortcut, bool selected, bool enabled) -> bool {
                return ImGui::MenuItem(label, shortcut.has_value() ? shortcut->c_str() : nullptr, selected, enabled);
            },
            nb::arg("label"), nb::arg("shortcut").none() = nb::none(), nb::arg("selected") = false, nb::arg("enabled") = true,
            "return True when activated. (simplified version of menu_item, where selected is read-only)");
        LG_MODULE.def("begin_tab_item_simple",
            [](const char* label, ImGuiTabItemFlags flags) -> bool { return ImGui::BeginTabItem(label, NULL, flags); },
            nb::arg("label"), nb::arg("flags") = 0,
            "create a Tab (non-closable). Returns True if the Tab is selected.");
    """,
    )

    # SetWindowFocus() / SetWindowFocus(name) accept None, PushFont(ImFont* font, ...) accepts None
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        @overload
        def set_window_focus() -> None:
            """(not recommended) set current window to be focused / top-most. prefer using SetNextWindowFocus()."""
            pass
        @overload
        def set_window_focus(name: Optional[str]) -> None:
            """set named window to be focused / top-most. use None to remove focus."""
            pass
        def push_font(font: Optional[ImFont], font_size_base_unscaled: float) -> None:
            """Use None as a shortcut to keep current font. Use 0.0 to keep current size."""
            pass
    ''',
        pydef_code="""
        LG_MODULE.def("set_window_focus",
            []() { ImGui::SetWindowFocus(); },
            "(not recommended) set current window to be focused / top-most. prefer using SetNextWindowFocus().");
        LG_MODULE.def("set_window_focus",
            [](std::optional<std::string> name) { ImGui::SetWindowFocus(name.has_value() ? name->c_str() : nullptr); },
            nb::arg("name").none(),
            "set named window to be focused / top-most. use None to remove focus.");
        LG_MODULE.def("push_font",
            [](ImFont* font, float font_size_base_unscaled) { ImGui::PushFont(font, font_size_base_unscaled); },
            nb::arg("font").none(), nb::arg("font_size_base_unscaled"),
            "Use None as a shortcut to keep current font. Use 0.0 to keep current size.");
    """,
    )

    # SliderFloat2/4, InputFloat2/4, ColorEdit3/4, ColorPicker3/4: two overloads each, accepting
    # a list of floats (returned as a list) or an ImVec2 / ImVec4 (returned as such).
    # Both overloads are written here, since Python overloads must be consecutive in the stub.
    # The list versions are registered first, so that nanobind tries them first.
    options_imgui.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        @overload
        def slider_float2(
            label: str, v: List[float], v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
        ) -> Tuple[bool, List[float]]:
            pass
        @overload
        def slider_float2(
            label: str, v: ImVec2Like, v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
        ) -> Tuple[bool, ImVec2]:
            pass
        @overload
        def slider_float4(
            label: str, v: List[float], v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
        ) -> Tuple[bool, List[float]]:
            pass
        @overload
        def slider_float4(
            label: str, v: ImVec4Like, v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
        ) -> Tuple[bool, ImVec4]:
            pass
        @overload
        def input_float2(
            label: str, v: List[float], format: str = "%.3", flags: InputTextFlags = 0
        ) -> Tuple[bool, List[float]]:
            pass
        @overload
        def input_float2(label: str, v: ImVec2Like, format: str = "%.3", flags: InputTextFlags = 0) -> Tuple[bool, ImVec2]:
            pass
        @overload
        def input_float4(
            label: str, v: List[float], format: str = "%.3", flags: InputTextFlags = 0
        ) -> Tuple[bool, List[float]]:
            pass
        @overload
        def input_float4(label: str, v: ImVec4Like, format: str = "%.3", flags: InputTextFlags = 0) -> Tuple[bool, ImVec4]:
            pass
        @overload
        def color_edit3(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
            pass
        @overload
        def color_edit3(label: str, col: ImVec4Like, flags: ColorEditFlags = 0) -> Tuple[bool, ImVec4]:
            pass
        @overload
        def color_edit4(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
            pass
        @overload
        def color_edit4(label: str, col: ImVec4Like, flags: ColorEditFlags = 0) -> Tuple[bool, ImVec4]:
            pass
        @overload
        def color_picker3(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
            pass
        @overload
        def color_picker3(label: str, col: ImVec4Like, flags: ColorEditFlags = 0) -> Tuple[bool, ImVec4]:
            pass
        @overload
        def color_picker4(
            label: str, col: List[float], flags: ColorEditFlags = 0, ref_col: Optional[float] = None
        ) -> Tuple[bool, List[float]]:
            pass
        @overload
        def color_picker4(
            label: str, col: ImVec4Like, flags: ColorEditFlags = 0, ref_col: Optional[ImVec4Like] = None
        ) -> Tuple[bool, ImVec4]:
            pass
    ''',
        pydef_code="""
        LG_MODULE.def("slider_float2",
            [](const char* label, std::array<float, 2> v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, std::array<float, 2>> {
                bool changed = ImGui::SliderFloat2(label, v.data(), v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float2",
            [](const char* label, ImVec2 v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, ImVec2> {
                bool changed = ImGui::SliderFloat2(label, &v.x, v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float4",
            [](const char* label, std::array<float, 4> v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, std::array<float, 4>> {
                bool changed = ImGui::SliderFloat4(label, v.data(), v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float4",
            [](const char* label, ImVec4 v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::SliderFloat4(label, &v.x, v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float2",
            [](const char* label, std::array<float, 2> v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, std::array<float, 2>> {
                bool changed = ImGui::InputFloat2(label, v.data(), format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float2",
            [](const char* label, ImVec2 v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, ImVec2> {
                bool changed = ImGui::InputFloat2(label, &v.x, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float4",
            [](const char* label, std::array<float, 4> v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, std::array<float, 4>> {
                bool changed = ImGui::InputFloat4(label, v.data(), format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float4",
            [](const char* label, ImVec4 v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::InputFloat4(label, &v.x, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("color_edit3",
            [](const char* label, std::array<float, 3> col, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<float, 3>> {
                bool changed = ImGui::ColorEdit3(label, col.data(), flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit3",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorEdit3(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit4",
            [](const char* label, std::array<float, 4> col, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<float, 4>> {
                bool changed = ImGui::ColorEdit4(label, col.data(), flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit4",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorEdit4(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker3",
            [](const char* label, std::array<float, 3> col, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<float, 3>> {
                bool changed = ImGui::ColorPicker3(label, col.data(), flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker3",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorPicker3(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker4",
            [](const char* label, std::array<float, 4> col, ImGuiColorEditFlags flags, std::optional<float> ref_col) -> std::tuple<bool, std::array<float, 4>> {
                bool changed = ImGui::ColorPicker4(label, col.data(), flags, ref_col.has_value() ? &ref_col.value() : nullptr); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0, nb::arg("ref_col").none() = nb::none());
        LG_MODULE.def("color_picker4",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags, std::optional<ImVec4> ref_col) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorPicker4(label, &col.x, flags, ref_col.has_value() ? &ref_col->x : nullptr); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0, nb::arg("ref_col").none() = nb::none());
    """,
    )

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator = litgen.LitgenGenerator(options_imgui)

    print("Processing imgui.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui.h")

    print("Processing imgui_stacklayout.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_stacklayout.h")
    print("Processing imgui_stacklayout_internal.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_stacklayout_internal.h")

    # Generate for imgui_stdlib.h
    options_imgui_stdlib = litgen_options_imgui(
        ImguiOptionsType.imgui_stdlib_h, docking_branch=FLAG_DOCKING_BRANCH
    )
    options_imgui.srcmlcpp_options.flag_quiet = True

    # Workaround internal compiler error on MSVC:
    # See failure logs: https://github.com/pthom/imgui_bundle/actions/runs/3267470437/jobs/5372682867
    # Commit 55d4d342efebb306bafd63b4fb72085f27f59e7d
    # options_imgui_stdlib.fn_exclude_by_name__regex += "|^Selectable$|^PlotLines$|^PlotHistogram$|^InputTextMultiline$"

    generator.lg_context.options = options_imgui_stdlib
    print("Processing imgui_stdlib.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/misc/cpp/imgui_stdlib.h")

    print("Processing imgui_pywrappers.h")
    generator.process_cpp_file(THIS_DIR + "/../imgui_pywrappers/imgui_pywrappers.h")

    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/__init__.pyi",
    )


def autogenerate_imgui_internal() -> None:
    options_imgui_internal = litgen_options_imgui(
        ImguiOptionsType.imgui_internal_h, docking_branch=FLAG_DOCKING_BRANCH
    )

    # GetCurrentWindow: check the context and the current window before dereferencing them,
    # since a null pointer here leads to an un-debuggable segfault for Python users.
    options_imgui_internal.fn_exclude_by_name__regex += r"|^GetCurrentWindow$"
    options_imgui_internal.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def get_current_window() -> Window:
            pass
    ''',
        pydef_code="""
        LG_MODULE.def("get_current_window",
            []() -> ImGuiWindow* {
                if (GImGui == NULL)
                    throw std::runtime_error("ImGui::GetCurrentWindow() -> ImGuiContext is NULL. This is likely because you are calling ImGui functions even before ImGui::CreateContext().");
                if (GImGui->CurrentWindow == NULL)
                    throw std::runtime_error("ImGui::GetCurrentWindow() -> CurrentWindow is NULL. This is likely because you are calling ImGui functions after ImGui::EndFrame()/ImGui::Render() and before the next ImGui::NewFrame().");
                return ImGui::GetCurrentWindow();
            },
            nb::rv_policy::reference);
    """,
    )

    generator = litgen.LitgenGenerator(options_imgui_internal)

    print("Processing imgui_internal.h")
    generator.process_cpp_file(CPP_HEADERS_DIR + "/imgui_internal.h")
    print("Processing imgui_internal_pywrappers.h")
    generator.process_cpp_file(
        THIS_DIR + "/../imgui_pywrappers/imgui_internal_pywrappers.h"
    )

    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui_internal.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/internal.pyi",
    )


def autogenerate_imgui_test_engine() -> None:
    options = litgen_options_imgui(
        ImguiOptionsType.imgui_test_engine, docking_branch=FLAG_DOCKING_BRANCH
    )
    options.fn_exclude_by_name__regex += "|^ImGuiTestEngineUtil_appendf_auto"

    generator = litgen.LitgenGenerator(options)
    imgui_test_engine_dir = (
        THIS_DIR + "/../../imgui_test_engine/imgui_test_engine/imgui_test_engine"
    )
    print("Processing imgui_test_engine")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_exporters.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_engine.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_context.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_internal.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_te_ui.h")
    generator.process_cpp_file(imgui_test_engine_dir + "/imgui_capture_tool.h")
    generator.write_generated_code(
        output_cpp_pydef_file=PYDEF_DIR + "/pybind_imgui_test_engine.cpp",
        output_stub_pyi_file=STUB_DIR + "/imgui/test_engine.pyi",
    )


@my_time_it
def main():
    autogenerate_imgui()
    autogenerate_imgui_internal()
    autogenerate_imgui_test_engine()


def sandbox():
    code = """
    IMGUI_API bool          InputTextEx(const char* label, const char* hint, char* buf, int buf_size, const ImVec2& size_arg, ImGuiInputTextFlags flags, ImGuiInputTextCallback callback = NULL, void* user_data = NULL);
    // IMGUI_API void          InputTextDeactivateHook(ImGuiID id);
    // IMGUI_API bool          TempInputText(const ImRect& bb, ImGuiID id, const char* label, char* buf, int buf_size, ImGuiInputTextFlags flags);
    """
    options_imgui = litgen_options_imgui(
        ImguiOptionsType.imgui_internal_h, docking_branch=FLAG_DOCKING_BRANCH
    )
    generated_code = litgen.generate_code(options_imgui, code)
    print(generated_code.pydef_code)


if __name__ == "__main__":
    main()
    # sandbox()
