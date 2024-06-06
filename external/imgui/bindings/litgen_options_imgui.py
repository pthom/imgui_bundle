# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from enum import Enum
import copy

import litgen
from codemanip.code_replacements import RegexReplacementList
from codemanip.code_utils import join_string_by_pipe_char
from srcmlcpp.srcmlcpp_options import WarningType

from litgen.options import LitgenOptions


class ImguiOptionsType(Enum):
    imgui_h = 1
    imgui_stdlib_h = 2
    imgui_internal_h = 3
    imgui_test_engine = 4


def _preprocess_imgui_code(code: str) -> str:
    # The imgui code uses two macros (IM_FMTARGS and IM_FMTLIST) which help the compiler
    #     #define IM_FMTARGS(FMT)             __attribute__((format(printf, FMT, FMT+1)))
    #     #define IM_FMTLIST(FMT)             __attribute__((format(printf, FMT, 0)))
    #
    # They are used like this:
    #     IMGUI_API bool          TreeNode(const char* str_id, const char* fmt, ...) IM_FMTARGS(2);
    #
    # They are removed before processing the header, because they would not be correctly interpreted by srcml.
    import re

    new_code = code
    new_code, _n = re.subn(r"IM_FMTARGS\(\d\)", "", new_code)
    new_code, _n = re.subn(r"IM_FMTLIST\(\d\)", "", new_code)
    # Also, imgui_internal.h contains lines like this (with no final ";"):
    #       IM_MSVC_RUNTIME_CHECKS_OFF
    # This confuses srcML, so we add a ";" at the end of those lines
    new_code, _n = re.subn(
        r"\nIM_MSVC_RUNTIME_CHECKS_OFF\n", "\nIM_MSVC_RUNTIME_CHECKS_OFF;\n", new_code
    )
    new_code, _n = re.subn(
        r"\nIM_MSVC_RUNTIME_CHECKS_RESTORE\n",
        "\nIM_MSVC_RUNTIME_CHECKS_RESTORE;\n",
        new_code,
    )

    # force publish GetCurrentWindow
    new_code = new_code.replace(
        "inline    ImGuiWindow*  GetCurrentWindow()",
        "IMGUI_API ImGuiWindow*  GetCurrentWindow()",
    )

    new_code = new_code.replace("unsigned char", "uchar")

    return new_code


def _add_imvector_template_options(options: litgen.LitgenOptions):
    instantiated_types = [
        "int",
        "uint",
        "float",
        "char",
        "uchar",
        "ImDrawCmd",
        "ImDrawChannel",
        "ImDrawVert",
        "ImVec4",
        "ImVec2",
        "ImDrawList*",
        "ImFont*",
        "ImFontGlyph",
        "ImGuiPlatformMonitor",
        "ImGuiViewport*",
        "ImGuiWindow*",
        "ImFontAtlasCustomRect",
        "ImFontConfig",
        "ImGuiFocusScopeData",
        # from imgui_internal.h
        "ImRect",
        "ImGuiColorMod",
        "ImGuiGroupData",
        "ImGuiPopupData",
        "ImGuiViewportP*",
        "ImGuiInputEvent",
        "ImGuiWindowStackData",
        "ImGuiTableColumnSortSpecs",
        "ImGuiTableInstanceData",
        "ImGuiTableTempData",
        "ImGuiNavTreeNodeData",
        "ImGuiPtrOrIndex",
        "ImGuiSettingsHandler",
        "ImGuiShrinkWidthItem",
        "ImGuiStackLevelInfo",
        "ImGuiTabItem",
        "ImGuiKeyRoutingData",
        "ImGuiListClipperData",
        "ImGuiListClipperRange",
        "ImGuiOldColumnData",
        "ImGuiOldColumns",
        "ImGuiStyleMod",  # uses union
        "ImGuiTableHeaderData",  # new in v1.90.7
    ]
    cpp_synonyms_list_str = [
        "ImTextureID=int",
        "ImDrawIdx=uint",
        "ImGuiID=uint",
        "ImU32=uint",
        "ImWchar32=uint",
        "ImWchar=ImWchar32",
        "ImGuiItemFlags=int",
    ]
    ignored_types = [
        "const char*",
        "ImBitArray",  # double template
        "ImGuiTextRange",  # char * pointers
        "ImGuiStoragePair",  # internal subclass
        "ImGuiContextHook",  # callbacks with C function pointers
        "ImGuiDockNodeSettings",  # opaque
        "ImGuiDockRequest",  # opaque
        "ImGuiTest*",  # ImGui Test Engine only
        "ImGuiTestInfoTask*",
        "ImGuiTestInput",
        "ImGuiTestLogLineInfo",
        "ImGuiTestRunTask",
        "ImGuiTestRunTask",
    ]

    options.class_template_options.add_specialization(
        name_regex="^ImVector$",
        cpp_types_list_str=instantiated_types,
        cpp_synonyms_list_str=cpp_synonyms_list_str,
    )
    for ignored_spec in ignored_types:
        options.srcmlcpp_options.ignored_warning_parts.append(
            "Excluding template type ImVector<" + ignored_spec + ">"
        )
    options.srcmlcpp_options.ignored_warning_parts += [
        "Excluding template type const ImVector<T>",
        "Excluding template type ImVector<T>",
    ]

    for instantiated_type in instantiated_types:
        python_iterable_type = instantiated_type.replace("ImGui", "").replace(
            "*", "_ptr"
        )
        python_class_name__regex = "^ImVector_" + python_iterable_type + "$"
        if python_iterable_type.endswith("_ptr"):
            python_iterable_type = python_iterable_type[: -len("_ptr")]
        options.class_iterables_infos.add_iterable_class(
            python_class_name__regex=python_class_name__regex,
            python_iterable_type=python_iterable_type,
        )


def add_imgui_test_engine_options(options: LitgenOptions):
    # patch preprocess: add replace("ImFuncPtr(ImGuiTestTestFunc)", "VoidFunction")
    old_preprocess = copy.copy(options.srcmlcpp_options.code_preprocess_function)

    def preprocess_ImGuiTestGuiFunc(code: str) -> str:
        r = code
        r = r.replace("ImFuncPtr(ImGuiTestTestFunc)", "Function_TestRunner")
        r = r.replace("ImFuncPtr(ImGuiTestGuiFunc)", "Function_TestGui")
        r = old_preprocess(r)
        return r

    options.srcmlcpp_options.code_preprocess_function = preprocess_ImGuiTestGuiFunc

    options.function_names_replacements.add_last_replacement("^ImGuiTestEngine_", "")
    options.function_names_replacements.add_last_replacement(
        "^ImGuiTestEngineHook_", "hook_"
    )
    options.fn_exclude_by_name__regex += "|^ImGuiTestEngineUtil_AppendStrValue|^ImGuiTestEngine_GetPerfTool$|^ItemOpenFullPath$"
    options.member_exclude_by_name__regex += "|Coroutine|^UiFilterByStatusMask$|^VarsConstructor$|^VarsPostConstructor$|^VarsDestructor$|^UiFilter"
    options.member_exclude_by_type__regex += "|^ImMovingAverage|^Str$|^ImGuiPerfTool|^ImGuiCaptureToolUI|^ImGuiCaptureContext|^ImGuiCaptureArgs"
    options.fn_exclude_by_param_type__regex += "|^ImGuiCaptureArgs"

    def postprocess_stub(code: str):
        # any function that accepts a TestRef param should also accept str (which is convertible to TestRef)
        r = code.replace(": TestRef", ": Union[TestRef, str]")
        r = r.replace("(TestEngineExportFormat)0", "TestEngineExportFormat.j_unit_xml")
        return r

    options.postprocess_stub_function = postprocess_stub


def litgen_options_imgui(
    options_type: ImguiOptionsType, docking_branch: bool
) -> LitgenOptions:
    from litgen.internal import cpp_to_python

    options = LitgenOptions()

    options.srcmlcpp_options.ignored_warnings = [
        WarningType.LitgenClassMemberSkipBitfield,
        WarningType.LitgenClassMemberUnparsableSize,
        WarningType.LitgenClassMemberNonNumericCStyleArray,
    ]

    options.srcmlcpp_options.ignored_warning_parts = [
        "C style function pointers",
        "function_decl as a param",
        'Unsupported zero param "operator bool"',
        "ImGuiDataType_Pointer",
        "ImGuiDataType_ID",
        "operators are supported only when implemented as a member functions",
        'Unsupported zero param "operator',
        "Ignoring template function",
        "inline ImVector<T>& operator=(const ImVector<T>& src)",
        "Ignoring template class ImChunkStream",
        "Ignoring template class ImPool",
        "Ignoring template class ImBitArray",
        "Ignoring template class ImSpan",
        "Ignoring template class ImSpanAllocator",
    ]
    # Warning: (Undefined) Excluding template type std::unique_ptr<ImSpan> because its specialization for `ImSpan` is not handled
    # Excluding template type ImSpan<T> * because its specialization for `T`
    # Excluding template type ImVector<ImDrawList*> because its specialization for `ImDrawList *` is not handled

    options.cpp_indent_size = 4

    options.namespaces_root = ["ImGui"]

    options.type_replacements = cpp_to_python.standard_type_replacements()
    options.type_replacements.merge_replacements(
        RegexReplacementList.from_string(
            r"""
            ^signed char$ -> int
            ^char$ -> int
            """
        )
    )

    options.function_names_replacements.merge_replacements(
        RegexReplacementList.from_string(
            r"""
            RGBtoHSV -> RgbToHsv
            HSVtoRGB -> HsvToRgb
            _AddFontFromFileTTF -> AddFontFromFileTTF
            _GetGlyphRanges -> GetGlyphRanges
            """
        )
    )

    options.type_replacements.add_last_replacement(r"ImGui([A-Z][a-zA-Z0-9]*)", r"\1")
    options.var_names_replacements.add_last_replacement(
        r"^id$", "id_"
    )  # id() is a built-in function in python

    # fix https://github.com/pthom/imgui_bundle/issues/40
    options.var_names_replacements.add_last_replacement(r"im_gui_selectable_flags_", "")
    options.var_names_replacements.add_last_replacement(r"im_gui_dock_node_flags_", "")

    # options.names_replacements.add_last_replacement(r"(^ImGui)([A-Z])", r"\2")

    options.python_max_line_length = (
        -1
    )  # in ImGui, the function decls are on *one* line
    options.python_convert_to_snake_case = True
    options.original_location_flag_show = False
    options.original_signature_flag_show = True

    options.python_run_black_formatter = True
    options.python_black_formatter_line_length = 120

    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options.fn_exclude_non_api = False

    options.srcmlcpp_options.header_filter_acceptable__regex += "|^IMGUI_DISABLE$"
    options.srcmlcpp_options.header_filter_acceptable__regex += (
        "|IMGUI_OVERRIDE_DRAWVERT_STRUCT_LAYOUT"
    )
    options.srcmlcpp_options.header_filter_acceptable__regex += (
        "|^IMGUI_BUNDLE_PYTHON_API$"
    )
    if docking_branch:
        options.srcmlcpp_options.header_filter_acceptable__regex += "|^IMGUI_HAS_DOCK$"

    options.srcmlcpp_options.code_preprocess_function = _preprocess_imgui_code

    options.class_copy__regex = r"^ImVec2$|^ImVec4$|^ImRect$|^ImColor$"

    options.fn_exclude_by_name__regex = join_string_by_pipe_char(
        [
            # IMGUI_API void          SetAllocatorFunctions(ImGuiMemAllocFunc alloc_func, ImGuiMemFreeFunc free_func, void* user_data = NULL);
            # IMGUI_API void          GetAllocatorFunctions(ImGuiMemAllocFunc* p_alloc_func, ImGuiMemFreeFunc* p_free_func, void** p_user_data);
            # IMGUI_API void*         MemAlloc(size_t size);
            # IMGUI_API void          MemFree(void* ptr);
            r"\bGetAllocatorFunctions\b",
            r"\bSetAllocatorFunctions\b",
            r"\bMemAlloc\b",
            r"\bMemFree\b",
            # IMGUI_API void              GetTexDataAsAlpha8(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 1 byte per-pixel
            # IMGUI_API void              GetTexDataAsRGBA32(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 4 bytes-per-pixel
            r"\bGetTexDataAsAlpha8\b",
            r"\bGetTexDataAsRGBA32\b",
            # IMGUI_API ImVec2            CalcTextSizeA(float size, float max_width, float wrap_width, const char* text_begin, const char* text_end = NULL, const char** remaining = NULL) const; // utf8
            r"\bCalcTextSizeA\b",
            r"ImFormatStringToTempBuffer",
            r"ImTextStrFromUtf8",
            "appendfv",
            # Exclude function whose name ends with V, like for example
            #       IMGUI_API void          TextV(const char* fmt, va_list args)                            IM_FMTLIST(1);
            # which are utilities for variadic print format
            r"[a-z0-9]V$",
            # Low level utility functions from imgui_internal.h
            r"^ImStr",
            r"^ImFormat",
            r"^ImParseFormat",
            r"^ImFontAtlasBuild",
            r"^ImText\w*To",
            r"^ImText\w*From",
            r"^DataType",
            # r"^InputTextEx$",
            r"^TempInputScalar",
            r"ImFileLoadToMemory",
            r"^GetGlyphRange",
            r"SetDragDropPayload^$",
            r"^AcceptDragDropPayload$",
            r"^GetDragDropPayload$",
            r"^GetKeyChordName$",
        ]
    )

    options.member_exclude_by_name__regex = join_string_by_pipe_char(
        [
            #     typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
            #     ImDrawCallback  UserCallback;       // 4-8  // If != NULL, call the function instead of rendering the vertices. clip_rect and texture_id will be set normally.
            r"^TexPixelsAlpha8$",
        ]
    )

    options.member_exclude_by_type__regex = join_string_by_pipe_char(
        [
            r"^ImDrawCallback$",
            r"^ContextHookCallback$",
            r"^ImGuiContextHookCallback$",
            r"const ImWchar\s*\*",
            r"unsigned char\s*\*",
            r"unsigned int\s*\*",
            r"^ImPool",
            r"^ImChunkStream",
            r"^ImSpan",
            r"^ImBitArray",
            r"::STB_",
            r"ImGuiStoragePair",
        ]
    )

    options.member_readonly_by_type__regex = join_string_by_pipe_char([
        r"^char\s*\*",
    ])

    options.class_exclude_by_name__regex = join_string_by_pipe_char([])

    options.member_numeric_c_array_types += "|" + join_string_by_pipe_char(
        [
            "ImGuiID",
            "ImS8",
            "ImU8",
            "ImS16",
            "ImU16",
            "ImS32",
            "ImU32",
            "ImS64",
            "ImU64",
        ]
    )

    # options.fn_force_overload__regex = r".*"
    options.fn_force_overload__regex = join_string_by_pipe_char(
        [
            r"^SetScroll",
            r"^Drag",
            r"^Slider",
            r"^InputText",
            r"Popup",
            r"DrawList",
            r"^Table",
            r"^SetWindowPos",
            r"^SetWindowSize",
            r"^SetWindowCollapsed",
            r"^ImageButton$",
            r"^IsKey",
            r"^IsMouse",
            r"^AddPolyline",
            r"^AddConvexPolyFilled",
            r"^AddConcavePolyFilled",
            r"^ColorPicker4",
            r"^Shortcut",
        ]
    )
    options.fn_force_lambda__regex = join_string_by_pipe_char(
        ["^ImMin$", "^ImMax$", "^ImClamp$", "^ImLerp$", "^Contains$", "^DockBuilderSplitNode"]
    )

    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.fn_return_force_policy_reference_for_references__regex = r".*"

    options.fn_params_replace_buffer_by_array__regex = r"^Plot"

    # Exclude callbacks from the params when they have a default value
    # (since imgui use bare C function pointers, not easily portable)
    options.fn_params_exclude_types__regex = r"size_t[ ]*\*"
    # Exclude functions that take char or const ImWchar * params
    options.fn_exclude_by_param_type__regex = (
        "^char$|^const ImWchar \\*$|^ImGuiErrorLogCallback$"
    )

    # Version where we use Boxed types everywhere:
    #     options.fn_params_replace_modifiable_immutable_by_boxed__regex = r".*"
    # Version where we return tuples:
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"

    options.fn_params_replace_c_array_modifiable_by_boxed__regex = ""

    options.srcmlcpp_options.flag_show_progress = True

    _add_imvector_template_options(options)

    if options_type == ImguiOptionsType.imgui_h:
        options.fn_exclude_by_name__regex += "|^InputText"
    elif options_type == ImguiOptionsType.imgui_internal_h:
        pass
    elif options_type == ImguiOptionsType.imgui_stdlib_h:
        pass
    elif options_type == ImguiOptionsType.imgui_test_engine:
        add_imgui_test_engine_options(options)

    return options


def sandbox():
    code = """
    struct Foo {
    std::function<std::string(void*)> GetClipboardTextFn_;
    std::function<void(std::string)> SetClipboardTextFn_;

    std::function<void(ImGuiViewport*, ImGuiPlatformImeData*)> SetPlatformImeDataFn;
    };
    """

    options = litgen_options_imgui(ImguiOptionsType.imgui_h, True)
    # options.python_run_black_formatter = False

    generated_code = litgen.generate_code(options, code)
    print(generated_code.stub_code)


if __name__ == "__main__":
    sandbox()
