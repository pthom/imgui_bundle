# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from __future__ import annotations
from enum import Enum
import copy

import litgen
from codemanip import code_utils
from codemanip.code_replacements import RegexReplacementList
from codemanip.code_utils import join_string_by_pipe_char
from srcmlcpp.srcmlcpp_options import WarningType

from litgen.options import LitgenOptions


class ImguiOptionsType(Enum):
    imgui_h = 1
    imgui_stdlib_h = 2
    imgui_internal_h = 3
    imgui_test_engine = 4


# ================================================================================================
# Code preprocessing (applied to the C++ headers before parsing)
# ================================================================================================

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

    # imgui.h contains lines like this (with no final ";"), which confuse srcML
    # and make it swallow the following declarations:
    #       IM_VEC2_CLASS_EXTRA     // Define additional constructors ...
    new_code, _n = re.subn(r"^(\s+IM_VEC[24]_CLASS_EXTRA)(\s)", r"\1;\2", new_code, flags=re.MULTILINE)

    new_code = new_code.replace("unsigned char", "uchar")

    return new_code


# ================================================================================================
# General options: backend, formatting, header filters, warnings
# ================================================================================================

def _options_general(options: LitgenOptions, docking_branch: bool) -> None:
    """Generator backend, indentation, stub formatting, preprocessor regions accepted by litgen, silenced warnings"""
    options.cpp_indent_size = 4

    options.namespaces_root = ["ImGui"]

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

    options.srcmlcpp_options.header_filter_acceptable__regex = code_utils.append_regex(options.srcmlcpp_options.header_filter_acceptable__regex, "^IMGUI_DISABLE$")
    options.srcmlcpp_options.header_filter_acceptable__regex = code_utils.append_regex(options.srcmlcpp_options.header_filter_acceptable__regex, "IMGUI_OVERRIDE_DRAWVERT_STRUCT_LAYOUT")
    options.srcmlcpp_options.header_filter_acceptable__regex = code_utils.append_regex(options.srcmlcpp_options.header_filter_acceptable__regex, "^IMGUI_BUNDLE_PYTHON_API$|^IMGUI_HAS_TEXTURES$")
    if docking_branch:
        options.srcmlcpp_options.header_filter_acceptable__regex = code_utils.append_regex(options.srcmlcpp_options.header_filter_acceptable__regex, "^IMGUI_HAS_DOCK$")

    options.srcmlcpp_options.code_preprocess_function = _preprocess_imgui_code

    options.srcmlcpp_options.flag_show_progress = True

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



# ================================================================================================
# Naming: type / function / variable name replacements, enums
# ================================================================================================

def _options_naming(options: LitgenOptions) -> None:
    """How C++ names and types are rendered in Python (ImGuiXxx -> Xxx, snake_case, ImVec2Like params, enum values)"""
    from litgen.internal import cpp_to_python

    options.type_replacements = cpp_to_python.standard_type_replacements()
    options.type_replacements.merge_replacements(
        RegexReplacementList.from_string(
            r"""
            ^signed char$ -> int
            ^char$ -> int
            \bImVector\s*<\s*(.*?)\s*> -> ImVector_\1
            """
        )
    )

    options.function_names_replacements.merge_replacements(
        RegexReplacementList.from_string(
            r"""
            RGBtoHSV -> RgbToHsv
            HSVtoRGB -> HsvToRgb
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
    options.var_names_replacements.add_last_replacement(r"im_gui_", "")

    # options.names_replacements.add_last_replacement(r"(^ImGui)([A-Z])", r"\2")

    # Remove prefixes from enum values, with a specific case for ImGui,
    # which defines private enums which may extend the public ones:
    #     enum ImGuiMyFlags_ { ImGuiMyFlags_None = 0,...};  enum ImGuiMyFlagsPrivate_ { ImGuiMyFlags_PrivValue = ...};
    options.enum_flag_remove_values_prefix = True
    options.enum_flag_remove_values_prefix_group_private = True
    options.enum_make_arithmetic__regex = r".*"
    options.enum_make_flag__regex = r".*"

    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])



# ================================================================================================
# Exclusions: functions, overloads, members and classes hidden from Python
# ================================================================================================

def _options_exclusions(options: LitgenOptions) -> None:
    """What is not published, and why. Overload sets replaced by custom bindings are listed here too."""
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
            # ColorConvertRGBtoHSV / ColorConvertHSVtoRGB: the out_ params should not be
            # required as inputs. The custom bindings (_custom_bindings_imgui_h) take only the 3 inputs.
            r"^ColorConvertRGBtoHSV$",
            r"^ColorConvertHSVtoRGB$",
            # Functions whose overload sets are entirely provided by custom bindings (_custom_bindings_imgui_h):
            # Python overloads must be consecutive in the stub, so the whole set is written there.
            r"^PushFont$",
            r"^SetWindowFocus$",
            r"^SliderFloat2$", r"^SliderFloat4$", r"^InputFloat2$", r"^InputFloat4$",
            r"^ColorEdit3$", r"^ColorEdit4$", r"^ColorPicker3$", r"^ColorPicker4$",
        ]
    )

    # Exclude some overloads by their exact signature (they are replaced by more pythonic versions)
    options.fn_exclude_by_name_and_signature = {
        # Only the `bool* p_selected` overload is published (returns Tuple[bool, bool])
        "Selectable": "const char *, bool, ImGuiSelectableFlags, const ImVec2 &",
        # Only the `bool* p_selected` overload is published; see also menu_item_simple
        "MenuItem": "const char *, const char *, bool, bool",
        # Pointer-based versions of the polygon functions: replaced by versions accepting a list of points
        "AddPolyline": "const ImVec2 *, int, ImU32, float, ImDrawFlags",
        "AddConvexPolyFilled": "const ImVec2 *, int, ImU32",
        "AddConcavePolyFilled": "const ImVec2 *, int, ImU32",
        # Output params (imgui_internal.h): replaced by a version returning DockBuilderSplitNodeResult
        "DockBuilderSplitNode": "ImGuiID, ImGuiDir, float, ImGuiID *, ImGuiID *",
        # char* buffers (imgui_internal.h): replaced by versions using std::string
        "InputTextEx": "const char *, const char *, char *, int, const ImVec2 &, ImGuiInputTextFlags, ImGuiInputTextCallback, void *",
        "TempInputText": "const ImRect &, ImGuiID, const char *, char *, size_t, ImGuiInputTextFlags, ImGuiInputTextCallback, void *",
    }

    # Exclude some members and methods, per class
    options.member_exclude_by_name_and_class__regex = {
        "ImVec2": r"^operator\[\]$",  # __getitem__ / __setitem__ are custom bindings (_custom_bindings_common)
        "ImGuiIO": r"^IniFilename$|^LogFilename$",  # bare const char* with no storage: see set_ini_filename & co
        "ImDrawList": r"^AddCallback$",  # C function pointer, incompatible with nanobind
        "ImTextureData": r"^GetPixels$|^GetPixelsAt$",  # void* : see get_pixels_array
        "ImFont": r"^CalcWordWrapPosition$",  # returns a pointer inside the text
        "ImGuiWindowSettings": r"^GetName$",  # char*: see get_name_str
        # ImVector: only a minimal API is published (iterable, indexable, push_back...); raw members,
        # iterators and pointer-based methods are not. See also data_address (_custom_bindings_imgui_h).
        "ImVector": join_string_by_pipe_char([
            r"^Size$", r"^Capacity$", r"^Data$",
            r"^clear_delete$", r"^size_in_bytes$", r"^max_size$", r"^capacity$",
            r"^begin$", r"^end$", r"^front$", r"^back$", r"^swap$", r"^_grow_capacity$",
            r"^resize$", r"^shrink$", r"^reserve$", r"^reserve_discard$",
            r"^erase$", r"^erase_unsorted$", r"^insert$", r"^contains$", r"^find$", r"^find_index$",
            r"^find_erase$", r"^find_erase_unsorted$", r"^index_from_ptr$",
        ]),
    }

    options.member_exclude_by_name__regex = join_string_by_pipe_char(
        [
            #     typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
            #     ImDrawCallback  UserCallback;       // 4-8  // If != NULL, call the function instead of rendering the vertices. clip_rect and texture_id will be set normally.
            r"^TexPixelsAlpha8$",
            r"^Stb$",
            r"^ErrorCallback$",  # callback with C function pointers
            r"^BakedPool$",
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
            r"^ImFileHandle$",
            r"ImFontLoader",
            r"^ImFontAtlasBuilder",
            r"^ImGuiDemoMarkerCallback",
        ]
    )

    options.member_readonly_by_type__regex = join_string_by_pipe_char([
        r"^char\s*\*",
    ])

    options.class_exclude_by_name__regex = join_string_by_pipe_char([
        "ImStableVector",
    ])



# ================================================================================================
# Function and member adaptations: parameters, return policies, overloads, copyable classes
# ================================================================================================

def _options_adaptations(options: LitgenOptions) -> None:
    """How published functions are adapted (output params returned as tuples, reference policies, forced overloads / lambdas...)"""
    def is_immutable_cpp_type(cpp_type: str) -> bool:
        if cpp_type in [
            "ImGuiDataType_", "ImGuiKey",  # enums
            "ImGuiID", "ImS8", "ImU8", "ImS16", "ImU16", "ImS32", "ImU32", "ImS64", "ImU64",  # Scalar types
            "IM_COL32"  # a function that returns a color (ImU32)
        ]:
            return True
        if cpp_type.endswith("Flags"):
            return True
        return False

    options.fn_params_adapt_mutable_param_with_default_value__fn_is_known_immutable_type = is_immutable_cpp_type
    options.class_copy__regex = r"^ImVec2$|^ImVec4$|^ImRect$|^ImColor$"

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
            r"^ColorPicker",
            r"^ColorEdit",
            r"^Shortcut",
            r"^SetItemKeyOwner",
            r"^GetIO",
            r"^GetPlatformIO",
            r"^PushFont",
        ]
    )
    options.fn_force_lambda__regex = join_string_by_pipe_char(
        ["^ImMin$", "^ImMax$", "^ImClamp$", "^ImLerp$", "^Contains$", "^DockBuilderSplitNode",
         "^AddRect$", "^PathStroke$"]
    )

    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.fn_return_force_policy_reference_for_references__regex = r".*"

    options.fn_params_replace_buffer_by_array__regex = r"^Plot"

    # Exclude callbacks from the params when they have a default value
    # (since imgui use bare C function pointers, not easily portable)
    options.fn_params_exclude_types__regex = r"size_t[ ]*\*"
    # Exclude functions with those param types:
    # - any function using a double pointer (like char **): see \* \* below
    # - char, const ImWchar *, ImGuiErrorLogCallback
    options.fn_exclude_by_param_type__regex = (
        r"^char$|^const ImWchar \*$|^ImGuiErrorLogCallback$|\* \*"
    )

    # Version where we use Boxed types everywhere:
    #     options.fn_params_replace_modifiable_immutable_by_boxed__regex = r".*"
    # Version where we return tuples:
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"

    options.fn_params_replace_c_array_modifiable_by_boxed__regex = ""



# ================================================================================================
# ImVector<T>: template specializations published as ImVector_int, ImVector_ImVec2...
# ================================================================================================

def _add_imvector_template_options(options: litgen.LitgenOptions) -> None:
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
        "ImFontAtlas*",  # ImGuiContext::FontAtlases (multi-atlas support, new in v1.92)
        "ImFontGlyph",
        "ImGuiPlatformMonitor",
        "ImGuiViewport*",
        "ImGuiWindow*",
        "ImFontConfig",
        "ImFontConfig*",
        "ImGuiFocusScopeData",
        "ImGuiSelectionRequest",
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
        "ImGuiTreeNodeStackData",
        "ImGuiMultiSelectTempData",
        "ImTextureData*",
        "ImTextureRef",
        "ImTextureRect",
    ]
    cpp_synonyms_list_str = [
        "ImTextureID=int",
        "ImDrawIdx=uint",
        "ImGuiID=uint",
        "ImU32=uint",
        "ImU16=uint",
        "ImWchar32=uint",
        "ImWchar=ImWchar32",
        "ImGuiItemFlags=int",
        "ImU8=uchar",
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
        "ImFontAtlasRectEntry",
        "stbrp_node",
        "stbrp_node_im",  # typedef for the opaque stb rect-packer node (ImGuiContext::PackNodes)
        "ImDrawListSharedData*",
        "ImFontStackData",
        "ImGuiTableReconcileColumnData",  # internal, used when validating ini settings column count
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
        "Ignoring template class ImStableVector",
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


# ================================================================================================
# Custom bindings shared by all generators (imgui.h, imgui_internal.h, test engine)
# ================================================================================================

def _custom_bindings_common(options: LitgenOptions) -> None:
    """Indexing of ImVec2 / ImVec4, ImGuiTextFilter.input_buf"""
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImVec2",
        stub_code='''
        def __getitem__(self, idx: int) -> float:
            """Get the value at the given index (0 for x, 1 for y)"""
            ...
        def __setitem__(self, idx: int, value: float) -> None:
            """Set the value at the given index (0 for x, 1 for y)"""
            ...
    ''',
        pydef_code="""
        LG_CLASS.def("__getitem__", [](const ImVec2& self, int idx) {
            if (idx == 0) return self.x;
            else if (idx == 1) return self.y;
            else throw std::out_of_range("Index out of range for ImVec2");
        });
        LG_CLASS.def("__setitem__", [](ImVec2& self, int idx, float value) {
            if (idx == 0) self.x = value;
            else if (idx == 1) self.y = value;
            else throw std::out_of_range("Index out of range for ImVec2");
        });
    """,
    )
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImVec4",
        stub_code='''
        def __getitem__(self, idx: int) -> float:
            """Get the value at the given index (0 for x, 1 for y, 2 for z, 3 for w)"""
            ...
        def __setitem__(self, idx: int, value: float) -> None:
            """Set the value at the given index (0 for x, 1 for y, 2 for z, 3 for w)"""
            ...
    ''',
        pydef_code="""
        LG_CLASS.def("__getitem__", [](const ImVec4& self, int idx) {
            if (idx == 0) return self.x;
            else if (idx == 1) return self.y;
            else if (idx == 2) return self.z;
            else if (idx == 3) return self.w;
            else throw std::out_of_range("Index out of range for ImVec4");
        });
        LG_CLASS.def("__setitem__", [](ImVec4& self, int idx, float value) {
            if (idx == 0) self.x = value;
            else if (idx == 1) self.y = value;
            else if (idx == 2) self.z = value;
            else if (idx == 3) self.w = value;
            else throw std::out_of_range("Index out of range for ImVec4");
        });
    """,
    )


    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiTextFilter",
        stub_code='''
        @property
        def input_buf(self) -> str:
            """The current filter text. Setting it also calls build()."""
            ...
        @input_buf.setter
        def input_buf(self, value: str) -> None: ...
    ''',
        pydef_code="""
        LG_CLASS.def_prop_rw("input_buf",
            [](const ImGuiTextFilter& self) { return std::string(self.InputBuf); },
            [](ImGuiTextFilter& self, const std::string& s) {
                strncpy(self.InputBuf, s.c_str(), sizeof(self.InputBuf) - 1);
                self.InputBuf[sizeof(self.InputBuf) - 1] = '\\0';
                self.Build();
            });
    """,
    )



# ================================================================================================
# Custom bindings for imgui.h (main module and classes)
# ================================================================================================

def _custom_bindings_imgui_h(options: LitgenOptions) -> None:
    """Python-specific API of the imgui module. Most of these replace former Python-only regions of the imgui fork
    (see docs/book/devel_docs/bindings_forks.md)."""
    # GetStyleColorVec4 returns const ImVec4& (reference into the style array).
    # With rv_policy::reference, Python can mutate the style directly without PushStyleColor.
    # Exclude only for imgui (not shared options, since ImPlot's version returns by value).
    options.fn_exclude_by_name__regex = code_utils.append_regex(options.fn_exclude_by_name__regex, r"^GetStyleColorVec4$")
    # Custom binding returns a copy instead.
    options.custom_bindings.add_custom_bindings_to_main_module(
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
    options.custom_bindings.add_custom_bindings_to_main_module(
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
    options.custom_bindings.add_custom_bindings_to_class(
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
    options.custom_bindings.add_custom_bindings_to_main_module(
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
    options.custom_bindings.add_custom_bindings_to_main_module(
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
    # The ImVec versions are registered first: an ImVec2/ImVec4 argument then returns an ImVec2/ImVec4 (as the stubs say),
    # while lists and tuples still reach the list version (implicit conversions to ImVec only happen in nanobind's second pass).
    # The list versions take doubles: nanobind's first pass accepts a Python float for a C++ float only when it is exactly
    # representable in single precision (0.5 is, 0.3 is not), which would otherwise send [0.3, ...] to the ImVec version.
    options.custom_bindings.add_custom_bindings_to_main_module(
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
            [](const char* label, ImVec2 v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, ImVec2> {
                bool changed = ImGui::SliderFloat2(label, &v.x, v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float2",
            [](const char* label, std::array<double, 2> v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, std::array<double, 2>> {
                float vf[2]; for (int i = 0; i < 2; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::SliderFloat2(label, vf, v_min, v_max, format, flags);
                for (int i = 0; i < 2; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float4",
            [](const char* label, ImVec4 v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::SliderFloat4(label, &v.x, v_min, v_max, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("slider_float4",
            [](const char* label, std::array<double, 4> v, float v_min, float v_max, const char* format, ImGuiSliderFlags flags) -> std::tuple<bool, std::array<double, 4>> {
                float vf[4]; for (int i = 0; i < 4; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::SliderFloat4(label, vf, v_min, v_max, format, flags);
                for (int i = 0; i < 4; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("v_min"), nb::arg("v_max"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float2",
            [](const char* label, ImVec2 v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, ImVec2> {
                bool changed = ImGui::InputFloat2(label, &v.x, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float2",
            [](const char* label, std::array<double, 2> v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, std::array<double, 2>> {
                float vf[2]; for (int i = 0; i < 2; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::InputFloat2(label, vf, format, flags);
                for (int i = 0; i < 2; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float4",
            [](const char* label, ImVec4 v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::InputFloat4(label, &v.x, format, flags); return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("input_float4",
            [](const char* label, std::array<double, 4> v, const char* format, ImGuiInputTextFlags flags) -> std::tuple<bool, std::array<double, 4>> {
                float vf[4]; for (int i = 0; i < 4; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::InputFloat4(label, vf, format, flags);
                for (int i = 0; i < 4; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("v"), nb::arg("format") = "%.3f", nb::arg("flags") = 0);
        LG_MODULE.def("color_edit3",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorEdit3(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit3",
            [](const char* label, std::array<double, 3> v, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<double, 3>> {
                float vf[3]; for (int i = 0; i < 3; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::ColorEdit3(label, vf, flags);
                for (int i = 0; i < 3; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit4",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorEdit4(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_edit4",
            [](const char* label, std::array<double, 4> v, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<double, 4>> {
                float vf[4]; for (int i = 0; i < 4; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::ColorEdit4(label, vf, flags);
                for (int i = 0; i < 4; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker3",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorPicker3(label, &col.x, flags); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker3",
            [](const char* label, std::array<double, 3> v, ImGuiColorEditFlags flags) -> std::tuple<bool, std::array<double, 3>> {
                float vf[3]; for (int i = 0; i < 3; ++i) vf[i] = (float)v[i];
                bool changed = ImGui::ColorPicker3(label, vf, flags);
                for (int i = 0; i < 3; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0);
        LG_MODULE.def("color_picker4",
            [](const char* label, ImVec4 col, ImGuiColorEditFlags flags, std::optional<ImVec4> ref_col) -> std::tuple<bool, ImVec4> {
                bool changed = ImGui::ColorPicker4(label, &col.x, flags, ref_col.has_value() ? &ref_col->x : nullptr); return {changed, col}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0, nb::arg("ref_col").none() = nb::none());
        LG_MODULE.def("color_picker4",
            [](const char* label, std::array<double, 4> v, ImGuiColorEditFlags flags, std::optional<double> ref_col) -> std::tuple<bool, std::array<double, 4>> {
                float vf[4]; for (int i = 0; i < 4; ++i) vf[i] = (float)v[i];
                float ref_col_f = ref_col.has_value() ? (float)*ref_col : 0.f;
                bool changed = ImGui::ColorPicker4(label, vf, flags, ref_col.has_value() ? &ref_col_f : nullptr);
                for (int i = 0; i < 4; ++i) v[i] = vf[i];
                return {changed, v}; },
            nb::arg("label"), nb::arg("col"), nb::arg("flags") = 0, nb::arg("ref_col").none() = nb::none());
    """,
    )

    # ------------------------------------------------------------------------------------------
    # Class custom bindings (replace former Python-only members of the imgui fork)
    # ------------------------------------------------------------------------------------------

    # ImVec2 / ImVec4 / ImColor: to_dict / from_dict (used for serialization, e.g. in fiatlight)
    for vec_class, keys in [("ImVec2", "xy"), ("ImVec4", "xyzw")]:
        keys_list = ", ".join(f'"{k}"' for k in keys)
        to_dict_cpp = ", ".join(f'{{"{k}", self.{k}}}' for k in keys)
        from_dict_cpp = ", ".join(f'd.at("{k}")' for k in keys)
        options.custom_bindings.add_custom_bindings_to_class(
            qualified_class=vec_class,
            stub_code=f'''
            def to_dict(self) -> Dict[str, float]:
                """Convert to a dict with keys {", ".join(keys)}"""
                pass
            @staticmethod
            def from_dict(d: Dict[str, float]) -> {vec_class}:
                """Create from a dict with keys {", ".join(keys)}"""
                pass
        ''',
            pydef_code=f'''
            LG_CLASS.def("to_dict",
                [](const {vec_class}& self) -> std::map<std::string, float> {{ return {{{to_dict_cpp}}}; }},
                "Convert to a dict with keys {", ".join(keys)}");
            LG_CLASS.def_static("from_dict",
                [](const std::map<std::string, float>& d) -> {vec_class} {{
                    for (const char* k : {{{keys_list}}})
                        if (d.find(k) == d.end())
                            throw std::invalid_argument(std::string("{vec_class}.from_dict: missing key ") + k);
                    return {vec_class}({from_dict_cpp});
                }},
                nb::arg("d"), "Create from a dict with keys {", ".join(keys)}");
        ''',
        )
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImColor",
        stub_code='''
        def to_dict(self) -> Dict[str, float]:
            """Convert to a dict with keys x, y, z, w"""
            pass
        @staticmethod
        def from_dict(d: Dict[str, float]) -> ImColor:
            """Create from a dict with keys x, y, z, w"""
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("to_dict",
            [](const ImColor& self) -> std::map<std::string, float> {
                return {{"x", self.Value.x}, {"y", self.Value.y}, {"z", self.Value.z}, {"w", self.Value.w}}; },
            "Convert to a dict with keys x, y, z, w");
        LG_CLASS.def_static("from_dict",
            [](const std::map<std::string, float>& d) -> ImColor {
                for (const char* k : {"x", "y", "z", "w"})
                    if (d.find(k) == d.end())
                        throw std::invalid_argument(std::string("ImColor.from_dict: missing key ") + k);
                return ImColor(d.at("x"), d.at("y"), d.at("z"), d.at("w"));
            },
            nb::arg("d"), "Create from a dict with keys x, y, z, w");
    """,
    )

    # ImVector<T>: address of the data (e.g. to build a numpy view); emitted for each specialization
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImVector",
        stub_code='''
        def data_address(self) -> int:
            """Address of the underlying array (e.g. to create a numpy view of it)"""
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("data_address", [](const LG_CPP_CLASS_NAME& self) -> size_t { return (size_t)self.Data; },
            "Address of the underlying array (e.g. to create a numpy view of it)");
    """,
    )

    # Tables: indexed access to the sort specs, and accessors for the SortDirection bitfield
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiTableSortSpecs",
        stub_code='''
        def get_specs(self, idx: int) -> TableColumnSortSpecs:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("get_specs",
            [](const ImGuiTableSortSpecs& self, size_t idx) -> const ImGuiTableColumnSortSpecs& {
                if (idx >= (size_t)self.SpecsCount)
                    throw std::out_of_range("TableSortSpecs.get_specs: index out of range");
                return self.Specs[idx];
            },
            nb::arg("idx"), nb::rv_policy::reference);
    """,
    )
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiTableColumnSortSpecs",
        stub_code='''
        def get_sort_direction(self) -> SortDirection:
            pass
        def set_sort_direction(self, direction: SortDirection) -> None:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("get_sort_direction",
            [](const ImGuiTableColumnSortSpecs& self) -> ImGuiSortDirection { return self.SortDirection; });
        LG_CLASS.def("set_sort_direction",
            [](ImGuiTableColumnSortSpecs& self, ImGuiSortDirection direction) { self.SortDirection = direction; },
            nb::arg("direction"));
    """,
    )

    # ImGuiStyle::Colors[ImGuiCol_COUNT]: indexed access
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiStyle",
        stub_code='''
        def color_(self, idx_color: int) -> ImVec4:
            pass
        def set_color_(self, idx_color: int, color: ImVec4Like) -> None:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("color_",
            [](ImGuiStyle& self, size_t idx_color) -> ImVec4& {
                if (idx_color >= (size_t)ImGuiCol_COUNT)
                    throw std::out_of_range("Style.color_: index out of range");
                return self.Colors[idx_color];
            },
            nb::arg("idx_color"), nb::rv_policy::reference);
        LG_CLASS.def("set_color_",
            [](ImGuiStyle& self, size_t idx_color, ImVec4 color) {
                if (idx_color >= (size_t)ImGuiCol_COUNT)
                    throw std::out_of_range("Style.set_color_: index out of range");
                self.Colors[idx_color] = color;
            },
            nb::arg("idx_color"), nb::arg("color"));
    """,
    )

    # ImGuiIO::IniFilename / LogFilename are bare const char* with no storage: provide setters with storage
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiIO",
        stub_code='''
        def set_ini_filename(self, filename: Optional[str]) -> None:
            """- The disk functions are automatically called if IniFilename != None
            - Set IniFilename to None to load/save manually. Read io.WantSaveIniSettings description about handling .ini saving manually.
            - Important: default value "imgui.ini" is relative to current working dir! Most apps will want to lock this to an absolute path (e.g. same path as executables).
            """
            pass
        def get_ini_filename(self) -> str:
            pass
        def set_log_filename(self, filename: str) -> None:
            pass
        def get_log_filename(self) -> str:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("set_ini_filename",
            [](ImGuiIO& self, std::optional<std::string> filename) {
                static std::string storage;  // ImGuiIO::IniFilename is a bare pointer with no storage
                if (filename.has_value()) { storage = *filename; self.IniFilename = storage.c_str(); }
                else self.IniFilename = NULL;
            },
            nb::arg("filename").none(),
            " - The disk functions are automatically called if IniFilename != None\\n - Set IniFilename to None to load/save manually. Read io.WantSaveIniSettings description about handling .ini saving manually.\\n - Important: default value \\"imgui.ini\\" is relative to current working dir! Most apps will want to lock this to an absolute path (e.g. same path as executables).");
        LG_CLASS.def("get_ini_filename",
            [](const ImGuiIO& self) -> std::string { return self.IniFilename ? self.IniFilename : ""; });
        LG_CLASS.def("set_log_filename",
            [](ImGuiIO& self, std::string filename) {
                static std::string storage;  // ImGuiIO::LogFilename is a bare pointer with no storage
                storage = filename; self.LogFilename = storage.c_str();
            },
            nb::arg("filename"));
        LG_CLASS.def("get_log_filename",
            [](const ImGuiIO& self) -> std::string { return self.LogFilename ? self.LogFilename : ""; });
    """,
    )

    # ImFontGlyph bitfields
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImFontGlyph",
        stub_code='''
        def is_colored(self) -> bool:
            """Flag to indicate glyph is colored and should generally ignore tinting (make it usable with no shift on little-endian as this is used in loops) (bitfield accessor)"""
            pass
        def is_visible(self) -> bool:
            """Flag to indicate glyph has no visible pixels (e.g. space). Allow early out when rendering. (bitfield accessor)"""
            pass
        def get_codepoint(self) -> int:
            """0x0000..0x10FFFF (bitfield accessor)"""
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("is_colored", [](const ImFontGlyph& self) -> bool { return self.Colored != 0; },
            "Flag to indicate glyph is colored and should generally ignore tinting (make it usable with no shift on little-endian as this is used in loops) (bitfield accessor)");
        LG_CLASS.def("is_visible", [](const ImFontGlyph& self) -> bool { return self.Visible != 0; },
            "Flag to indicate glyph has no visible pixels (e.g. space). Allow early out when rendering. (bitfield accessor)");
        LG_CLASS.def("get_codepoint", [](const ImFontGlyph& self) -> unsigned int { return self.Codepoint; },
            "0x0000..0x10FFFF (bitfield accessor)");
    """,
    )

    # ImTextureData::GetPixels() as a numpy array (a view on the texture memory, owned by C++)
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImTextureData",
        stub_code='''
        def get_pixels_array(self) -> NpBuffer:
            """GetPixelsArray(): returns the pixel data as a NumPy array.

             Note: GetPixelsAt(x, y) is not implemented for Python, but you can use the offset below:
                offset = (y * tex.width + x) * tex.bytes_per_pixel
            """
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("get_pixels_array",
            [](ImTextureData& self) {
                if (self.Pixels == NULL)
                    throw std::runtime_error("ImTextureData.get_pixels_array: no pixels");
                size_t shape[1] = {(size_t)self.GetSizeInBytes()};
                return nb::ndarray<uint8_t, nb::numpy>(self.Pixels, 1, shape, nb::handle());  // no owner: memory is owned by C++
            },
            nb::rv_policy::reference,
            " GetPixelsArray(): returns the pixel data as a NumPy array.\\n\\n Note: GetPixelsAt(x, y) is not implemented for Python, but you can use the offset below:\\n    offset = (y * tex.width + x) * tex.bytes_per_pixel");
    """,
    )

    # ImFontAtlas: texture id accessors for older backends, and AddFontFromFileTTF without glyph ranges
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImFontAtlas",
        stub_code='''
        def add_font_from_file_ttf(
            self, filename: str, size_pixels: float, font_cfg: Optional[ImFontConfig] = None
        ) -> ImFont:
            pass
        def python_set_texture_id(self, id_: ImTextureID) -> None:
            """Set the font texture id (for older backends which do not implement ImGuiBackendFlags_RendererHasTextures)"""
            pass
        def python_get_texture_id(self) -> ImTextureID:
            """Get the font texture id (for older backends which do not implement ImGuiBackendFlags_RendererHasTextures)"""
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("add_font_from_file_ttf",
            [](ImFontAtlas& self, const char* filename, float size_pixels, const ImFontConfig* font_cfg) -> ImFont* {
                return self.AddFontFromFileTTF(filename, size_pixels, font_cfg); },
            nb::arg("filename"), nb::arg("size_pixels"), nb::arg("font_cfg") = nb::none(),
            nb::rv_policy::reference);
        LG_CLASS.def("python_set_texture_id",
            [](ImFontAtlas& self, ImTextureID id) { self.TexRef = ImTextureRef(id); },
            nb::arg("id_"),
            "Set the font texture id (for older backends which do not implement ImGuiBackendFlags_RendererHasTextures)");
        LG_CLASS.def("python_get_texture_id",
            [](ImFontAtlas& self) -> ImTextureID { return self.TexRef.GetTexID(); },
            "Get the font texture id (for older backends which do not implement ImGuiBackendFlags_RendererHasTextures)");
    """,
    )

    # ImGuiPlatformIO clipboard / open-in-shell callbacks: Python callables through static trampolines
    # (g_py_get_clipboard & co, defined in the hand-written part of pybind_imgui.cpp). Reading an attribute set from C++ returns None.
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiPlatformIO",
        stub_code='''
        platform_get_clipboard_text_fn: Callable[[Context], str]
        platform_set_clipboard_text_fn: Callable[[Context, str], None]
        platform_open_in_shell_fn: Callable[[Context, str], bool]
    ''',
        pydef_code="""
        LG_CLASS.def_prop_rw("platform_get_clipboard_text_fn",
            [](ImGuiPlatformIO&) { return g_py_get_clipboard.is_valid() ? g_py_get_clipboard : nb::none(); },
            [](ImGuiPlatformIO& self, nb::object f) {
                g_py_get_clipboard = f;
                self.Platform_GetClipboardTextFn = f.is_none() ? NULL : PyGetClipboardTextTrampoline;
            },
            nb::arg("f").none(),
            "Optional: Access OS clipboard. Callable[[Context], str], should return an empty string on failure.");
        LG_CLASS.def_prop_rw("platform_set_clipboard_text_fn",
            [](ImGuiPlatformIO&) { return g_py_set_clipboard.is_valid() ? g_py_set_clipboard : nb::none(); },
            [](ImGuiPlatformIO& self, nb::object f) {
                g_py_set_clipboard = f;
                self.Platform_SetClipboardTextFn = f.is_none() ? NULL : PySetClipboardTextTrampoline;
            },
            nb::arg("f").none(),
            "Optional: Access OS clipboard. Callable[[Context, str], None]");
        LG_CLASS.def_prop_rw("platform_open_in_shell_fn",
            [](ImGuiPlatformIO&) { return g_py_open_in_shell.is_valid() ? g_py_open_in_shell : nb::none(); },
            [](ImGuiPlatformIO& self, nb::object f) {
                g_py_open_in_shell = f;
                self.Platform_OpenInShellFn = f.is_none() ? NULL : PyOpenInShellTrampoline;
            },
            nb::arg("f").none(),
            "Optional: Open link/folder/file in OS Shell. Callable[[Context, str], bool], expected to return False on failure.");
    """,
    )

    # ImDrawList polygons: accept a list of points (the C++ versions take a pointer + count)
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImDrawList",
        stub_code='''
        def add_polyline(self, points: List[ImVec2Like], col: ImU32, thickness: float, flags: ImDrawFlags) -> None:
            pass
        def add_convex_poly_filled(self, points: List[ImVec2Like], col: ImU32) -> None:
            pass
        def add_concave_poly_filled(self, points: List[ImVec2Like], col: ImU32) -> None:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("add_polyline",
            [](ImDrawList& self, const std::vector<ImVec2>& points, ImU32 col, float thickness, ImDrawFlags flags) {
                self.AddPolyline(points.data(), (int)points.size(), col, thickness, flags); },
            nb::arg("points"), nb::arg("col"), nb::arg("thickness"), nb::arg("flags"));
        LG_CLASS.def("add_convex_poly_filled",
            [](ImDrawList& self, const std::vector<ImVec2>& points, ImU32 col) {
                self.AddConvexPolyFilled(points.data(), (int)points.size(), col); },
            nb::arg("points"), nb::arg("col"));
        LG_CLASS.def("add_concave_poly_filled",
            [](ImDrawList& self, const std::vector<ImVec2>& points, ImU32 col) {
                self.AddConcavePolyFilled(points.data(), (int)points.size(), col); },
            nb::arg("points"), nb::arg("col"));
    """,
    )



# ================================================================================================
# Custom bindings for imgui_internal.h
# ================================================================================================

def _custom_bindings_imgui_internal_h(options: LitgenOptions) -> None:
    """Python-specific API of the imgui.internal module"""
    # GetCurrentWindow: check the context and the current window before dereferencing them,
    # since a null pointer here leads to an un-debuggable segfault for Python users.
    options.fn_exclude_by_name__regex = code_utils.append_regex(options.fn_exclude_by_name__regex, r"^GetCurrentWindow$")
    options.custom_bindings.add_custom_bindings_to_main_module(
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

    # ImGuiWindowSettings::GetName() returns a char* into the settings buffer: return a copy as str
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiWindowSettings",
        stub_code='''
        def get_name_str(self) -> str:
            pass
    ''',
        pydef_code="""
        LG_CLASS.def("get_name_str", [](ImGuiWindowSettings& self) -> std::string { return self.GetName(); });
    """,
    )



# ================================================================================================
# ImGui Test Engine specifics
# ================================================================================================

def add_imgui_test_engine_options(options: LitgenOptions) -> None:
    # patch preprocess: add replace("ImFuncPtr(ImGuiTestTestFunc)", "VoidFunction")
    old_preprocess = copy.copy(options.srcmlcpp_options.code_preprocess_function)
    assert old_preprocess is not None  # set by _options_general

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
    options.fn_exclude_by_name__regex = code_utils.append_regex(options.fn_exclude_by_name__regex, "^ImGuiTestEngineUtil_AppendStrValue|^ImGuiTestEngine_GetPerfTool$|^ItemOpenFullPath$|^ItemReadAsString$")
    options.member_exclude_by_name__regex = code_utils.append_regex(options.member_exclude_by_name__regex, "Coroutine|^UiFilterByStatusMask$|^VarsConstructor$|^VarsPostConstructor$|^VarsDestructor$|^UiFilter")
    options.member_exclude_by_type__regex = code_utils.append_regex(options.member_exclude_by_type__regex, "^ImMovingAverage|^Str$|^ImGuiPerfTool|^ImGuiCaptureToolUI|^ImGuiCaptureContext|^ImGuiCaptureArgs|^ImGuiCaptureImageBuf")
    options.fn_exclude_by_param_type__regex = code_utils.append_regex(options.fn_exclude_by_param_type__regex, "^ImGuiCaptureArgs")
    options.class_exclude_by_name__regex = code_utils.append_regex(options.class_exclude_by_name__regex, "^ImGuiCaptureImageBuf$|^ImGuiCaptureContext$|^ImGuiCaptureToolUI$")
    options.fn_exclude_by_name__regex = code_utils.append_regex(options.fn_exclude_by_name__regex, "^ImGuiTestEngineUtil_appendf_auto")


# ================================================================================================
# Stub post-processing
# ================================================================================================

def _postprocess_stub_imgui(stub_code: str) -> str:
    stub_code = stub_code.replace(
        "class ImVec2:", "class ImVec2(Vec2Protocol):"
    )
    stub_code = stub_code.replace(
        "class ImVec4:", "class ImVec4(Vec4Protocol):"
    )
    stub_code = stub_code.replace(
        "SelectionRequestType = SelectionRequestType()",
        "SelectionRequestType = SelectionRequestType.none"
    )

    # Replace ImVector[int] by ImVector_int, etc.
    import re
    pattern = r'\bImVector\s*\[\s*(.*?)\s*\]'
    replacement = r'ImVector_\1'
    stub_code = re.sub(pattern, replacement, stub_code)

    return stub_code


def _postprocess_stub_test_engine(code: str) -> str:
    # any function that accepts a TestRef param should also accept str (which is convertible to TestRef)
    r = code.replace(": TestRef", ": Union[TestRef, str]")
    r = r.replace("(TestEngineExportFormat)0", "TestEngineExportFormat.j_unit_xml")
    r = r.replace(
        ": TestVerboseLevel = TestVerboseLevel()",
        ": TestVerboseLevel = TestVerboseLevel.warning"
    )
    return r


# ================================================================================================
# Entry point
# ================================================================================================

def litgen_options_imgui(options_type: ImguiOptionsType, docking_branch: bool) -> LitgenOptions:
    """Base litgen options for the imgui headers (see ImguiOptionsType).
    Also used as a starting point by libraries built on top of imgui (implot, implot3d, imgui_toggle):
    it must not register custom bindings, since those of the main module would be emitted in their modules too.
    For imgui's own bindings, use litgen_options_imgui_with_custom_bindings()."""
    options = LitgenOptions()
    options.use_nanobind()

    _options_general(options, docking_branch)
    _options_naming(options)
    _options_exclusions(options)
    _options_adaptations(options)
    _add_imvector_template_options(options)

    if options_type == ImguiOptionsType.imgui_h:
        options.fn_exclude_by_name__regex = code_utils.append_regex(options.fn_exclude_by_name__regex, "^InputText")  # InputText comes from imgui_stdlib.h (std::string version)
    elif options_type == ImguiOptionsType.imgui_test_engine:
        add_imgui_test_engine_options(options)

    if options_type == ImguiOptionsType.imgui_test_engine:
        options.postprocess_stub_function = _postprocess_stub_test_engine
    else:
        options.postprocess_stub_function = _postprocess_stub_imgui

    return options


def litgen_options_imgui_with_custom_bindings(options_type: ImguiOptionsType, docking_branch: bool) -> LitgenOptions:
    """Options for the generation of imgui's own bindings: the base options, plus imgui's custom bindings"""
    options = litgen_options_imgui(options_type, docking_branch)
    _custom_bindings_common(options)
    if options_type == ImguiOptionsType.imgui_h:
        _custom_bindings_imgui_h(options)
    elif options_type == ImguiOptionsType.imgui_internal_h:
        _custom_bindings_imgui_internal_h(options)
    return options


def sandbox() -> None:
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
