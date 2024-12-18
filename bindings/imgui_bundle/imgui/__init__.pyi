# ruff: noqa: B008, E741
from __future__ import annotations
import sys
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Tuple,
    overload,
    Iterator,
    Callable,
    Union,
    Protocol,
    TypeVar,
)
import numpy as np
import enum
from . import internal as internal
from . import backends as backends
from . import test_engine as test_engine
from .internal import TableHeaderData

##################################################
#    Manually inserted code (typedefs, etc.)
##################################################

from .internal import (
    Context,
    ImDrawListSharedData,
    ImFontBuilderIO,
    ImRect,
    ColorMod,
    GroupData,
    PopupData,
    ViewportP,
    InputEvent,
    TableInstanceData,
    TableTempData,
    PtrOrIndex,
    SettingsHandler,
    ShrinkWidthItem,
    StackLevelInfo,
    TabItem,
    KeyRoutingData,
    ListClipperData,
    ListClipperRange,
    OldColumnData,
    OldColumns,
    StyleMod,
    WindowStackData,
    FocusScopeData,
    MultiSelectFlags,
    SelectionUserData,
    TreeNodeStackData,
    MultiSelectTempData,
    ItemFlags,
)

VoidPtr = Any

FLT_MIN: float  # value defined by this module as the minimum acceptable C(++) float
FLT_MAX: float  # value defined by this module as the maximum acceptable C(++) float

Window = internal.Window
uint = int
uchar = int
char = int

def font_atlas_get_tex_data_as_rgba32(
    font_atlas: ImFontAtlas,
) -> np.ndarray:
    """Manual binding for ImFontAtlas::GetTexDataAsRGBA32
    This is also available as a method of ImFont: ImFontAtlas.get_tex_data_as_rgba32()
    """
    pass

# -----------------------------------------------------------------------------
# [SECTION] Forward declarations and basic types
# -----------------------------------------------------------------------------
"""
// Forward declarations
struct ImDrawChannel;               // Temporary storage to output draw commands out of order, used by ImDrawListSplitter and ImDrawList::ChannelsSplit()
struct ImDrawCmd;                   // A single draw command within a parent ImDrawList (generally maps to 1 GPU draw call, unless it is a callback)
struct ImDrawData;                  // All draw command lists required to render the frame + pos/size coordinates to use for the projection matrix.
struct ImDrawList;                  // A single draw command list (generally one per window, conceptually you may see this as a dynamic "mesh" builder)
struct ImDrawListSharedData;        // Data shared among multiple draw lists (typically owned by parent ImGui context, but you may create one yourself)
struct ImDrawListSplitter;          // Helper to split a draw list into different layers which can be drawn into out of order, then flattened back.
struct ImDrawVert;                  // A single vertex (pos + uv + col = 20 bytes by default. Override layout with IMGUI_OVERRIDE_DRAWVERT_STRUCT_LAYOUT)
struct ImFont;                      // Runtime data for a single font within a parent ImFontAtlas
struct ImFontAtlas;                 // Runtime data for multiple fonts, bake multiple fonts into a single texture, TTF/OTF font loader
struct ImFontBuilderIO;             // Opaque interface to a font builder (stb_truetype or FreeType).
struct ImFontConfig;                // Configuration data when adding a font or merging fonts
struct ImFontGlyph;                 // A single font glyph (code point + coordinates within in ImFontAtlas + offset)
struct ImFontGlyphRangesBuilder;    // Helper to build glyph ranges from text/string data
struct ImColor;                     // Helper functions to create a color that can be converted to either u32 or float4 (*OBSOLETE* please avoid using)
struct ImGuiContext;                // Dear ImGui context (opaque structure, unless including imgui_internal.h)
struct ImGuiIO;                     // Main configuration and I/O between your application and ImGui
struct ImGuiInputTextCallbackData;  // Shared state of InputText() when using custom ImGuiInputTextCallback (rare/advanced use)
struct ImGuiKeyData;                // Storage for ImGuiIO and IsKeyDown(), IsKeyPressed() etc functions.
struct ImGuiListClipper;            // Helper to manually clip large list of items
struct ImGuiOnceUponAFrame;         // Helper for running a block of code not more than once a frame
struct ImGuiPayload;                // User data payload for drag and drop operations
struct ImGuiPlatformImeData;        // Platform IME data for io.SetPlatformImeDataFn() function.
struct ImGuiSizeCallbackData;       // Callback data when using SetNextWindowSizeConstraints() (rare/advanced use)
struct ImGuiStorage;                // Helper for key->value storage
struct ImGuiStyle;                  // Runtime data for styling/colors
struct ImGuiTableSortSpecs;         // Sorting specifications for a table (often handling sort specs for a single column, occasionally more)
struct ImGuiTableColumnSortSpecs;   // Sorting specification for one column of a table
struct ImGuiTextBuffer;             // Helper to hold and append into a text buffer (~string builder)
struct ImGuiTextFilter;             // Helper to parse and apply text filters (e.g. "aaaaa[,bbbbb][,ccccc]")
struct ImGuiViewport;               // A Platform Window (always only one in 'master' branch), in the future may represent Platform Monitor
"""
# We forward declare only the opaque structures
# ImDrawVert = Any

"""
// Enums/Flags (declared as int for compatibility with old C++, to allow using as flags without overhead, and to not pollute the top of this file)
// - Tip: Use your programming IDE navigation facilities on the names in the _central column_ below to find the actual flags/enum lists!
//   In Visual Studio IDE: CTRL+comma ("Edit.GoToAll") can follow symbols in comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
//   With Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols in comments.
typedef int ImGuiCol;               // -> enum ImGuiCol_             // Enum: A color identifier for styling
typedef int ImGuiCond;              // -> enum ImGuiCond_            // Enum: A condition for many Set*() functions
typedef int ImGuiDataType;          // -> enum ImGuiDataType_        // Enum: A primary data type
typedef int ImGuiDir;               // -> enum ImGuiDir_             // Enum: A cardinal direction
typedef int ImGuiKey;               // -> enum ImGuiKey_             // Enum: A key identifier
typedef int ImGuiNavInput;          // -> enum ImGuiNavInput_        // Enum: An input identifier for navigation
typedef int ImGuiMouseButton;       // -> enum ImGuiMouseButton_     // Enum: A mouse button identifier (0=left, 1=right, 2=middle)
typedef int ImGuiMouseCursor;       // -> enum ImGuiMouseCursor_     // Enum: A mouse cursor identifier
typedef int ImGuiSortDirection;     // -> enum ImGuiSortDirection_   // Enum: A sorting direction (ascending or descending)
typedef int ImGuiStyleVar;          // -> enum ImGuiStyleVar_        // Enum: A variable identifier for styling
typedef int ImGuiTableBgTarget;     // -> enum ImGuiTableBgTarget_   // Enum: A color target for TableSetBgColor()
typedef int ImDrawFlags;            // -> enum ImDrawFlags_          // Flags: for ImDrawList functions
typedef int ImDrawListFlags;        // -> enum ImDrawListFlags_      // Flags: for ImDrawList instance
typedef int ImFontAtlasFlags;       // -> enum ImFontAtlasFlags_     // Flags: for ImFontAtlas build
typedef int ImGuiBackendFlags;      // -> enum ImGuiBackendFlags_    // Flags: for io.BackendFlags
typedef int ImGuiButtonFlags;       // -> enum ImGuiButtonFlags_     // Flags: for InvisibleButton()
typedef int ImGuiColorEditFlags;    // -> enum ImGuiColorEditFlags_  // Flags: for ColorEdit4(), ColorPicker4() etc.
typedef int ImGuiConfigFlags;       // -> enum ImGuiConfigFlags_     // Flags: for io.ConfigFlags
typedef int ImGuiComboFlags;        // -> enum ImGuiComboFlags_      // Flags: for BeginCombo()
typedef int ImGuiDockNodeFlags;     // -> enum ImGuiDockNodeFlags_   // Flags: for DockSpace()
typedef int ImGuiDragDropFlags;     // -> enum ImGuiDragDropFlags_   // Flags: for BeginDragDropSource(), AcceptDragDropPayload()
typedef int ImGuiFocusedFlags;      // -> enum ImGuiFocusedFlags_    // Flags: for IsWindowFocused()
typedef int ImGuiHoveredFlags;      // -> enum ImGuiHoveredFlags_    // Flags: for IsItemHovered(), IsWindowHovered() etc.
typedef int ImGuiInputTextFlags;    // -> enum ImGuiInputTextFlags_  // Flags: for InputText(), InputTextMultiline()
typedef int ImGuiModFlags;          // -> enum ImGuiModFlags_        // Flags: for io.KeyMods (Ctrl/Shift/Alt/Super)
typedef int ImGuiPopupFlags;        // -> enum ImGuiPopupFlags_      // Flags: for OpenPopup*(), BeginPopupContext*(), IsPopupOpen()
typedef int ImGuiSelectableFlags;   // -> enum ImGuiSelectableFlags_ // Flags: for Selectable()
typedef int ImGuiSliderFlags;       // -> enum ImGuiSliderFlags_     // Flags: for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
typedef int ImGuiTabBarFlags;       // -> enum ImGuiTabBarFlags_     // Flags: for BeginTabBar()
typedef int ImGuiTabItemFlags;      // -> enum ImGuiTabItemFlags_    // Flags: for BeginTabItem()
typedef int ImGuiTableFlags;        // -> enum ImGuiTableFlags_      // Flags: For BeginTable()
typedef int ImGuiTableColumnFlags;  // -> enum ImGuiTableColumnFlags_// Flags: For TableSetupColumn()
typedef int ImGuiTableRowFlags;     // -> enum ImGuiTableRowFlags_   // Flags: For TableNextRow()
typedef int ImGuiTreeNodeFlags;     // -> enum ImGuiTreeNodeFlags_   // Flags: for TreeNode(), TreeNodeEx(), CollapsingHeader()
typedef int ImGuiViewportFlags;     // -> enum ImGuiViewportFlags_   // Flags: for ImGuiViewport
typedef int ImGuiWindowFlags;       // -> enum ImGuiWindowFlags_     // Flags: for Begin(), BeginChild()
"""
Col = int  # -> enum Col_             # Enum: A color identifier for styling
Cond = int  # -> enum Cond_            # Enum: A condition for many Set*() functions
DataType = int  # -> enum DataType_        # Enum: A primary data type
NavInput = int  # -> enum NavInput_        # Enum: An input identifier for navigation
MouseButton = int  # -> enum MouseButton_     # Enum: A mouse button identifier (0=left, 1=right, 2=middle)
MouseCursor = int  # -> enum MouseCursor_     # Enum: A mouse cursor identifier
StyleVar = int  # -> enum StyleVar_        # Enum: A variable identifier for styling
TableBgTarget = int  # -> enum TableBgTarget_   # Enum: A color target for TableSetBgColor()
ImDrawFlags = int  # -> enum ImDrawFlags_          # Flags: for ImDrawList functions
ImDrawListFlags = int  # -> enum ImDrawListFlags_      # Flags: for ImDrawList instance
ImFontAtlasFlags = int  # -> enum ImFontAtlasFlags_     # Flags: for ImFontAtlas build
BackendFlags = int  # -> enum BackendFlags_    # Flags: for io.BackendFlags
ButtonFlags = int  # -> enum ButtonFlags_     # Flags: for InvisibleButton()
ColorEditFlags = int  # -> enum ColorEditFlags_  # Flags: for ColorEdit4(), ColorPicker4() etc.
ConfigFlags = int  # -> enum ConfigFlags_     # Flags: for io.ConfigFlags
ComboFlags = int  # -> enum ComboFlags_      # Flags: for BeginCombo()
DockNodeFlags = int  # -> enum DockNodeFlags_   // Flags: for DockSpace()
DragDropFlags = int  # -> enum DragDropFlags_   # Flags: for BeginDragDropSource(), AcceptDragDropPayload()
FocusedFlags = int  # -> enum FocusedFlags_    # Flags: for IsWindowFocused()
HoveredFlags = int  # -> enum HoveredFlags_    # Flags: for IsItemHovered(), IsWindowHovered() etc.
InputTextFlags = int  # -> enum InputTextFlags_  # Flags: for InputText(), InputTextMultiline()
ModFlags = int  # -> enum ModFlags_        # Flags: for io.KeyMods (Ctrl/Shift/Alt/Super)
PopupFlags = int  # -> enum PopupFlags_      # Flags: for OpenPopup*(), BeginPopupContext*(), IsPopupOpen()
SelectableFlags = int  # -> enum SelectableFlags_ # Flags: for Selectable()
SliderFlags = int  # -> enum SliderFlags_     # Flags: for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
TabBarFlags = int  # -> enum TabBarFlags_     # Flags: for BeginTabBar()
TabItemFlags = int  # -> enum TabItemFlags_    # Flags: for BeginTabItem()
TableFlags = int  # -> enum TableFlags_      # Flags: For BeginTable()
TableColumnFlags = int  # -> enum TableColumnFlags_# Flags: For TableSetupColumn()
TableRowFlags = int  # -> enum TableRowFlags_   # Flags: For TableNextRow()
TreeNodeFlags = int  # -> enum TreeNodeFlags_   # Flags: for TreeNode(), TreeNodeEx(), CollapsingHeader()
ViewportFlags = int  # -> enum ViewportFlags_   # Flags: for ImGuiViewport
WindowFlags = int  # -> enum WindowFlags_     # Flags: for Begin(), BeginChild()
ToggleFlags = int  # -> enum ToggleFlags_
ChildFlags = int  # -> enum ChildFlags_
InputFlags = int  # -> enum ImGuiInputFlags_      // Flags: for Shortcut(), SetNextItemShortcut()
KeyChord = ModFlags  # == int. We generally use ImGuiKeyChord to mean "a ImGuiKey or-ed with any number of ImGuiMod_XXX value", but you may store only mods in there.

"""
// ImTexture: user data for renderer backend to identify a texture [Compile-time configurable type]
// - To use something else than an opaque void* pointer: override with e.g. '#define ImTextureID MyTextureType*' in your imconfig.h file.
// - This can be whatever to you want it to be! read the FAQ about ImTextureID for details.
#ifndef ImTextureID
typedef void* ImTextureID;          // Default: store a pointer or an integer fitting in a pointer (most renderer backends are ok with that)
#endif
"""
ImTextureID = int

"""
// ImDrawIdx: vertex index. [Compile-time configurable type]
// - To use 16-bit indices + allow large meshes: backend need to set 'io.BackendFlags |= ImGuiBackendFlags_RendererHasVtxOffset' and handle ImDrawCmd::VtxOffset (recommended).
// - To use 32-bit indices: override with '#define ImDrawIdx unsigned int' in your imconfig.h file.
#ifndef ImDrawIdx
typedef unsigned short ImDrawIdx;   // Default: 16-bit (for maximum compatibility with renderer backends)
#endif
"""
ImDrawIdx = int

"""
// Scalar data types
typedef unsigned int        ImGuiID;// A unique ID used by widgets (typically the result of hashing a stack of string)
typedef signed char         ImS8;   // 8-bit signed integer
typedef unsigned char       ImU8;   // 8-bit unsigned integer
typedef signed short        ImS16;  // 16-bit signed integer
typedef unsigned short      ImU16;  // 16-bit unsigned integer
typedef signed int          ImS32;  // 32-bit signed integer == int
typedef unsigned int        ImU32;  // 32-bit unsigned integer (often used to store packed colors)
typedef signed   long long  ImS64;  // 64-bit signed integer
typedef unsigned long long  ImU64;  // 64-bit unsigned integer
"""
# Scalar data types
ID = int  # A unique ID used by widgets (typically the result of hashing a stack of string)
ImS8 = int  # 8-bit integer
ImU8 = int  # 8-bit integer
ImS16 = int  # 16-bit integer
ImU16 = int  # 16-bit integer
ImS32 = int  # 32-bit integer == int
ImU32 = int  # 32-bit integer (often used to store packed colors)
ImS64 = int  # 64-bit integer
ImU64 = int  # 64-bit integer

"""
// Character types
// (we generally use UTF-8 encoded string in the API. This is storage specifically for a decoded character used for keyboard input and display)
typedef unsigned short ImWchar16;   // A single decoded U16 character/code point. We encode them as multi bytes UTF-8 when used in strings.
typedef unsigned int ImWchar32;     // A single decoded U32 character/code point. We encode them as multi bytes UTF-8 when used in strings.
#ifdef IMGUI_USE_WCHAR32            // ImWchar [configurable type: override in imconfig.h with '#define IMGUI_USE_WCHAR32' to support Unicode planes 1-16]
typedef ImWchar32 ImWchar;
#else
typedef ImWchar16 ImWchar;
#endif
"""
ImWchar = int
ImWchar16 = int
ImWchar32 = int

"""
// Callback and functions types
typedef int     (*ImGuiInputTextCallback)(ImGuiInputTextCallbackData* data);    // Callback function for ImGui::InputText()
typedef void    (*ImGuiSizeCallback)(ImGuiSizeCallbackData* data);              // Callback function for ImGui::SetNextWindowSizeConstraints()
typedef void*   (*ImGuiMemAllocFunc)(size_t sz, void* user_data);               // Function signature for ImGui::SetAllocatorFunctions()
typedef void    (*ImGuiMemFreeFunc)(void* ptr, void* user_data);                // Function signature for ImGui::SetAllocatorFunctions()
"""
"""
#ifndef ImDrawCallback
    typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
#endif
"""
MemAllocFunc = Any
MemFreeFunc = Any
ImDrawCallback = Any

# using ImGuiInputTextCallback = std::function<int(ImGuiInputTextCallbackData*)>;  // Callback function for ImGui::InputText()
# using ImGuiSizeCallback = std::function<void(ImGuiSizeCallbackData*)>;           // Callback function for ImGui::SetNextWindowSizeConstraints()
InputTextCallback = Callable[[InputTextCallbackData], int]
SizeCallback = Callable[[SizeCallbackData], None]

"""
// Helpers macros to generate 32-bit encoded colors
// User can declare their own format by #defining the 5 _SHIFT/_MASK macros in their imconfig file.
#ifndef IM_COL32_R_SHIFT
#ifdef IMGUI_USE_BGRA_PACKED_COLOR
#define IM_COL32_R_SHIFT    16
#define IM_COL32_G_SHIFT    8
#define IM_COL32_B_SHIFT    0
#define IM_COL32_A_SHIFT    24
#define IM_COL32_A_MASK     0xFF000000
#else
#define IM_COL32_R_SHIFT    0
#define IM_COL32_G_SHIFT    8
#define IM_COL32_B_SHIFT    16
#define IM_COL32_A_SHIFT    24
#define IM_COL32_A_MASK     0xFF000000
#endif
#endif
#define IM_COL32(R,G,B,A)    (((ImU32)(A)<<IM_COL32_A_SHIFT) | ((ImU32)(B)<<IM_COL32_B_SHIFT) | ((ImU32)(G)<<IM_COL32_G_SHIFT) | ((ImU32)(R)<<IM_COL32_R_SHIFT))
#define IM_COL32_WHITE       IM_COL32(255,255,255,255)  // Opaque white = 0xFFFFFFFF
#define IM_COL32_BLACK       IM_COL32(0,0,0,255)        // Opaque black
#define IM_COL32_BLACK_TRANS IM_COL32(0,0,0,0)          // Transparent black = 0x00000000
"""
IM_COL32_R_SHIFT = 0
IM_COL32_G_SHIFT = 8
IM_COL32_B_SHIFT = 16
IM_COL32_A_SHIFT = 24

def IM_COL32(r: ImU32, g: ImU32, b: ImU32, a: ImU32) -> ImU32:
    r = (a << IM_COL32_A_SHIFT) | (b << IM_COL32_B_SHIFT) | (g << IM_COL32_G_SHIFT) | (r << IM_COL32_R_SHIFT)
    return r

IM_COL32_WHITE: int  #  = IM_COL32(255, 255, 255, 255)
IM_COL32_BLACK: int  #  = IM_COL32(0, 0, 0, 255)

"""
Additional customizations
"""
TextRange = Any  # internal structure of ImGuiTextFilter, composed of string pointers (cannot be easily adapted)
StoragePair = Any

PayloadId = int

# VERTEX_SIZE, VERTEX_BUFFER_POS_OFFSET, VERTEX_BUFFER_UV_OFFSET, etc.
# Utilities to facilitate rendering in python backends: they provide buffer offsets info
VERTEX_SIZE: int
VERTEX_BUFFER_POS_OFFSET: int
VERTEX_BUFFER_UV_OFFSET: int
VERTEX_BUFFER_COL_OFFSET: int
INDEX_SIZE: int

# VecProtocol: add __add__, __sub__, __mul__, __truediv__, __neg__ to ImVec2 and ImVec4
TVec = TypeVar("TVec", bound="VecProtocol")

class VecProtocol(Protocol[TVec]):
    def __add__(self: TVec, other: TVec) -> TVec: ...
    def __sub__(self: TVec, other: TVec) -> TVec: ...
    def __mul__(self: TVec, other: Union[TVec, float]) -> TVec: ...
    def __truediv__(self: TVec, other: Union[TVec, float]) -> TVec: ...
    def __neg__(self: TVec) -> TVec: ...

ImVec2Like = Union[ImVec2, Tuple[int | float, int | float], List[int | float]]
ImVec4Like = Union[ImVec4, Tuple[int | float, int | float, int | float, int | float], List[int | float]]

##################################################
#    AUTO GENERATED CODE BELOW
##################################################
# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:imgui.h>    ####################
# dear imgui, v1.91.7 WIP
# (headers)

# Help:
# - See links below.
# - Call and read ImGui::ShowDemoWindow() in imgui_demo.cpp. All applications in examples/ are doing that.
# - Read top of imgui.cpp for more details, links and comments.
# - Add '#define IMGUI_DEFINE_MATH_OPERATORS' before including this file (or in imconfig.h) to access courtesy maths operators for ImVec2 and ImVec4.

# Resources:
# - FAQ ........................ https://dearimgui.com/faq (in repository as docs/FAQ.md)
# - Homepage ................... https://github.com/ocornut/imgui
# - Releases & changelog ....... https://github.com/ocornut/imgui/releases
# - Gallery .................... https://github.com/ocornut/imgui/issues?q=label%3Agallery (please post your screenshots/video there!)
# - Wiki ....................... https://github.com/ocornut/imgui/wiki (lots of good stuff there)
#   - Getting Started            https://github.com/ocornut/imgui/wiki/Getting-Started (how to integrate in an existing app by adding ~25 lines of code)
#   - Third-party Extensions     https://github.com/ocornut/imgui/wiki/Useful-Extensions (ImPlot & many more)
#   - Bindings/Backends          https://github.com/ocornut/imgui/wiki/Bindings (language bindings, backends for various tech/engines)
#   - Glossary                   https://github.com/ocornut/imgui/wiki/Glossary
#   - Debug Tools                https://github.com/ocornut/imgui/wiki/Debug-Tools
#   - Software using Dear ImGui  https://github.com/ocornut/imgui/wiki/Software-using-dear-imgui
# - Issues & support ........... https://github.com/ocornut/imgui/issues
# - Test Engine & Automation ... https://github.com/ocornut/imgui_test_engine (test suite, test engine to automate your apps)

# For first-time users having issues compiling/linking/running/loading fonts:
# please post in https://github.com/ocornut/imgui/discussions if you cannot find a solution in resources above.
# Everything else should be asked in 'Issues'! We are building a database of cross-linked knowledge there.

# Library Version
# (Integer encoded as XYYZZ for use in #if preprocessor conditionals, e.g. '#if IMGUI_VERSION_NUM >= 12345')

#
# Adaptations for ImGui Bundle are noted with [ADAPT_IMGUI_BUNDLE]
#
# [ADAPT_IMGUI_BUNDLE]
# #ifdef IMGUI_BUNDLE_PYTHON_API
#
# #endif
#

# #ifdef IMGUI_BUNDLE_PYTHON_API
#
##define IMGUI_BUNDLE_IMGUI_USE_STRING
# #endif
#
# [/ADAPT_IMGUI_BUNDLE]

# [ADAPT_IMGUI_BUNDLE] utilities
# - std::function: switches between function pointer and std::function
# - std::string: switches between const char* and std::string
# - BundleHybridToChar: converts std::string to const char*
# [/ADAPT_IMGUI_BUNDLE] utilities

#
# Index of this file:
# // [SECTION] Header mess
# // [SECTION] Forward declarations and basic types
# // [SECTION] Dear ImGui end-user API functions
# // [SECTION] Flags & Enumerations
# // [SECTION] Tables API flags and structures (ImGuiTableFlags, ImGuiTableColumnFlags, ImGuiTableRowFlags, ImGuiTableBgTarget, ImGuiTableSortSpecs, ImGuiTableColumnSortSpecs)
# // [SECTION] Helpers: Debug log, Memory allocations macros, ImVector<>
# // [SECTION] ImGuiStyle
# // [SECTION] ImGuiIO
# // [SECTION] Misc data structures (ImGuiInputTextCallbackData, ImGuiSizeCallbackData, ImGuiWindowClass, ImGuiPayload)
# // [SECTION] Helpers (ImGuiOnceUponAFrame, ImGuiTextFilter, ImGuiTextBuffer, ImGuiStorage, ImGuiListClipper, Math Operators, ImColor)
# // [SECTION] Multi-Select API flags and structures (ImGuiMultiSelectFlags, ImGuiMultiSelectIO, ImGuiSelectionRequest, ImGuiSelectionBasicStorage, ImGuiSelectionExternalStorage)
# // [SECTION] Drawing API (ImDrawCallback, ImDrawCmd, ImDrawIdx, ImDrawVert, ImDrawChannel, ImDrawListSplitter, ImDrawFlags, ImDrawListFlags, ImDrawList, ImDrawData)
# // [SECTION] Font API (ImFontConfig, ImFontGlyph, ImFontGlyphRangesBuilder, ImFontAtlasFlags, ImFontAtlas, ImFont)
# // [SECTION] Viewports (ImGuiViewportFlags, ImGuiViewport)
# // [SECTION] ImGuiPlatformIO + other Platform Dependent Interfaces (ImGuiPlatformMonitor, ImGuiPlatformImeData)
# // [SECTION] Obsolete functions and types
#
#

# Configuration file with compile-time options
# (edit imconfig.h or '#define IMGUI_USER_CONFIG "myfilename.h" from your build system)

# #ifndef IMGUI_DISABLE
#

# -----------------------------------------------------------------------------
# [SECTION] Header mess
# -----------------------------------------------------------------------------

# Includes

# Define attributes of all API symbols declarations (e.g. for DLL under Windows)
# IMGUI_API is used for core imgui functions, IMGUI_IMPL_API is used for the default backends files (imgui_impl_xxx.h)
# Using dear imgui via a shared library is not recommended: we don't guarantee backward nor forward ABI compatibility + this is a call-heavy library and function call overhead adds up.

# Helper Macros

# Helper Macros - IM_FMTARGS, IM_FMTLIST: Apply printf-style warnings to our formatting functions.
# (MSVC provides an equivalent mechanism via SAL Annotations but it would require the macros in a different
#  location. e.g. #include <sal.h> + None myprintf(_Printf_format_string_ const char* format, ...))

# Disable some of MSVC most aggressive Debug runtime checks in function header/footer (used in some simple/low-level functions)

# Warnings

# -----------------------------------------------------------------------------
# [SECTION] Forward declarations and basic types
# -----------------------------------------------------------------------------

# Scalar data types

# Forward declarations

# Enumerations
# - We don't use strongly typed enums much because they add constraints (can't extend in private code, can't store typed in bit fields, extra casting on iteration)
# - Tip: Use your programming IDE navigation facilities on the names in the _central column_ below to find the actual flags/enum lists!
#   - In Visual Studio: CTRL+comma ("Edit.GoToAll") can follow symbols inside comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
#   - In Visual Studio w/ Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols inside comments.
#   - In VS Code, CLion, etc.: CTRL+click can follow symbols inside comments.

# Flags (declared as int to allow using as flags without overhead, and to not pollute the top of this file)
# - Tip: Use your programming IDE navigation facilities on the names in the _central column_ below to find the actual flags/enum lists!
#   - In Visual Studio: CTRL+comma ("Edit.GoToAll") can follow symbols inside comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
#   - In Visual Studio w/ Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols inside comments.
#   - In VS Code, CLion, etc.: CTRL+click can follow symbols inside comments.
# -> enum ImGuiWindowFlags_     // Flags: for Begin(), BeginChild()

# ImTexture: user data for renderer backend to identify a texture [Compile-time configurable type]
# - To use something else than an opaque None* pointer: override with e.g. '#define ImTextureID MyTextureType*' in your imconfig.h file.
# - This can be whatever to you want it to be! read the FAQ about ImTextureID for details.
# - You can make this a structure with various constructors if you need. You will have to implement ==/!= operators.
# - (note: before v1.91.4 (2024/10/08) the default type for ImTextureID was None*. Use intermediary intptr_t cast and read FAQ if you have casting warnings)

# ImDrawIdx: vertex index. [Compile-time configurable type]
# - To use 16-bit indices + allow large meshes: backend need to set 'io.BackendFlags |= ImGuiBackendFlags_RendererHasVtxOffset' and handle ImDrawCmd::VtxOffset (recommended).
# - To use 32-bit indices: override with '#define ImDrawIdx unsigned int' in your imconfig.h file.

# Character types
# (we generally use UTF-8 encoded string in the API. This is storage specifically for a decoded character used for keyboard input and display)
# A single decoded U16 character/code point. We encode them as multi bytes UTF-8 when used in strings.

# Callback and functions types
# #ifdef IMGUI_BUNDLE_PYTHON_API
#
# Callback function for ImGui::SetNextWindowSizeConstraints()
# #else
#
# #endif
#

class ImVec2(VecProtocol["ImVec2"]):
    # float                                   x,     /* original C++ signature */
    x: float
    # y;    /* original C++ signature */
    y: float
    # constexpr ImVec2()                      : x(0.0f), y(0.0f) { }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # constexpr ImVec2(float _x, float _y)    : x(_x), y(_y) { }    /* original C++ signature */
    @overload
    def __init__(self, _x: float, _y: float) -> None:
        pass
    # float& operator[] (size_t idx)          { IM_ASSERT(idx == 0 || idx == 1); return ((float*)(void*)(char*)this)[idx]; }     /* original C++ signature */
    @overload
    def __getitem__(self, idx: int) -> float:
        """(private API)

        We very rarely use this [] operator, so the assert overhead is fine.
        """
        pass
    # float  operator[] (size_t idx) const    { IM_ASSERT(idx == 0 || idx == 1); return ((const float*)(const void*)(const char*)this)[idx]; }    /* original C++ signature */
    @overload
    def __getitem__(self, idx: int) -> float:
        """(private API)"""
        pass
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # std::map<std::string, float> to_dict() const { return {{"x", x}, {"y", y}}; }    /* original C++ signature */
    def to_dict(self) -> Dict[str, float]:
        """(private API)"""
        pass
    # static ImVec2 from_dict(const std::map<std::string, float>& d) { IM_ASSERT((d.find("x") != d.end()) && (d.find("y") != d.end()) && "ImVec2::from_dict dict should contain x and y keys"); return ImVec2(d.at("x"), d.at("y")); }    /* original C++ signature */
    @staticmethod
    def from_dict(d: Dict[str, float]) -> ImVec2:
        """(private API)"""
        pass
    # #endif
    #

class ImVec4(VecProtocol["ImVec4"]):
    """ImVec4: 4D vector used to store clipping rectangles, colors etc. [Compile-time configurable type]"""

    # float                                                     x,     /* original C++ signature */
    x: float
    # y,     /* original C++ signature */
    y: float
    # z,     /* original C++ signature */
    z: float
    # w;    /* original C++ signature */
    w: float
    # constexpr ImVec4()                                        : x(0.0f), y(0.0f), z(0.0f), w(0.0f) { }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # constexpr ImVec4(float _x, float _y, float _z, float _w)  : x(_x), y(_y), z(_z), w(_w) { }    /* original C++ signature */
    @overload
    def __init__(self, _x: float, _y: float, _z: float, _w: float) -> None:
        pass
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # std::map<std::string, float> to_dict() const { return {{"x", x}, {"y", y}, {"z", z}, {"w", w}}; }    /* original C++ signature */
    def to_dict(self) -> Dict[str, float]:
        """(private API)"""
        pass
    # static ImVec4 from_dict(const std::map<std::string, float>& d) { IM_ASSERT((d.find("x") != d.end()) && (d.find("y") != d.end()) && (d.find("z") != d.end()) && (d.find("w") != d.end()) && "ImVec4::from_dict dict should contain x, y, z and w keys"); return ImVec4(d.at("x"), d.at("y"), d.at("z"), d.at("w")); }    /* original C++ signature */
    @staticmethod
    def from_dict(d: Dict[str, float]) -> ImVec4:
        """(private API)"""
        pass
    # #endif
    #

# -----------------------------------------------------------------------------
# [SECTION] Dear ImGui end-user API functions
# (Note that ImGui:: being a namespace, you can add extra ImGui:: functions in your own separate file. Please don't modify imgui source files!)
# -----------------------------------------------------------------------------

# Context creation and access
# - Each context create its own ImFontAtlas by default. You may instance one yourself and pass it to CreateContext() to share a font atlas between contexts.
# - DLL users: heaps and globals are not shared across DLL boundaries! You will need to call SetCurrentContext() + SetAllocatorFunctions()
#   for each static/DLL boundary you are calling from. Read "Context and Memory Allocators" section of imgui.cpp for details.
# IMGUI_API ImGuiContext* CreateContext(ImFontAtlas* shared_font_atlas = NULL);    /* original C++ signature */
def create_context(shared_font_atlas: Optional[ImFontAtlas] = None) -> Context:
    pass

# IMGUI_API void          DestroyContext(ImGuiContext* ctx = NULL);       /* original C++ signature */
def destroy_context(ctx: Optional[Context] = None) -> None:
    """None = destroy current context"""
    pass

# IMGUI_API ImGuiContext* GetCurrentContext();    /* original C++ signature */
def get_current_context() -> Context:
    pass

# IMGUI_API void          SetCurrentContext(ImGuiContext* ctx);    /* original C++ signature */
def set_current_context(ctx: Context) -> None:
    pass

# Main
# IMGUI_API ImGuiIO&      GetIO();                                        /* original C++ signature */
def get_io() -> IO:
    """access the ImGuiIO structure (mouse/keyboard/gamepad inputs, time, various configuration options/flags)"""
    pass

# IMGUI_API ImGuiPlatformIO& GetPlatformIO();                             /* original C++ signature */
def get_platform_io() -> PlatformIO:
    """access the ImGuiPlatformIO structure (mostly hooks/functions to connect to platform/renderer and OS Clipboard, IME etc.)"""
    pass

# IMGUI_API ImGuiStyle&   GetStyle();                                     /* original C++ signature */
def get_style() -> Style:
    """access the Style structure (colors, sizes). Always use PushStyleColor(), PushStyleVar() to modify style mid-frame!"""
    pass

# IMGUI_API void          NewFrame();                                     /* original C++ signature */
def new_frame() -> None:
    """start a new Dear ImGui frame, you can submit any command from this point until Render()/EndFrame()."""
    pass

# IMGUI_API void          EndFrame();                                     /* original C++ signature */
def end_frame() -> None:
    """ends the Dear ImGui frame. automatically called by Render(). If you don't need to render data (skipping rendering) you may call EndFrame() without Render()... but you'll have wasted CPU already! If you don't need to render, better to not create any windows and not call NewFrame() at all!"""
    pass

# IMGUI_API void          Render();                                       /* original C++ signature */
def render() -> None:
    """ends the Dear ImGui frame, finalize the draw data. You can then get call GetDrawData()."""
    pass

# IMGUI_API ImDrawData*   GetDrawData();                                  /* original C++ signature */
def get_draw_data() -> ImDrawData:
    """valid after Render() and until the next call to NewFrame(). this is what you have to render."""
    pass

# Demo, Debug, Information
# IMGUI_API void          ShowDemoWindow(bool* p_open = NULL);            /* original C++ signature */
def show_demo_window(p_open: Optional[bool] = None) -> Optional[bool]:
    """create Demo window. demonstrate most ImGui features. call this to learn about the library! try to make it always available in your application!"""
    pass

# IMGUI_API void          ShowMetricsWindow(bool* p_open = NULL);         /* original C++ signature */
def show_metrics_window(p_open: Optional[bool] = None) -> Optional[bool]:
    """create Metrics/Debugger window. display Dear ImGui internals: windows, draw commands, various internal state, etc."""
    pass

# IMGUI_API void          ShowDebugLogWindow(bool* p_open = NULL);        /* original C++ signature */
def show_debug_log_window(p_open: Optional[bool] = None) -> Optional[bool]:
    """create Debug Log window. display a simplified log of important dear imgui events."""
    pass

# IMGUI_API void          ShowIDStackToolWindow(bool* p_open = NULL);     /* original C++ signature */
def show_id_stack_tool_window(p_open: Optional[bool] = None) -> Optional[bool]:
    """create Stack Tool window. hover items with mouse to query information about the source of their unique ID."""
    pass

# IMGUI_API void          ShowAboutWindow(bool* p_open = NULL);           /* original C++ signature */
def show_about_window(p_open: Optional[bool] = None) -> Optional[bool]:
    """create About window. display Dear ImGui version, credits and build/system information."""
    pass

# IMGUI_API void          ShowStyleEditor(ImGuiStyle* ref = NULL);        /* original C++ signature */
def show_style_editor(ref: Optional[Style] = None) -> None:
    """add style editor block (not a window). you can pass in a reference ImGuiStyle structure to compare to, revert to and save to (else it uses the default style)"""
    pass

# IMGUI_API bool          ShowStyleSelector(const char* label);           /* original C++ signature */
def show_style_selector(label: str) -> bool:
    """add style selector block (not a window), essentially a combo listing the default styles."""
    pass

# IMGUI_API void          ShowFontSelector(const char* label);            /* original C++ signature */
def show_font_selector(label: str) -> None:
    """add font selector block (not a window), essentially a combo listing the loaded fonts."""
    pass

# IMGUI_API void          ShowUserGuide();                                /* original C++ signature */
def show_user_guide() -> None:
    """add basic help/info block (not a window): how to manipulate ImGui as an end-user (mouse/keyboard controls)."""
    pass

# IMGUI_API const char*   GetVersion();                                   /* original C++ signature */
def get_version() -> str:
    """get the compiled version string e.g. "1.80 WIP" (essentially the value for IMGUI_VERSION from the compiled version of imgui.cpp)"""
    pass

# Styles
# IMGUI_API void          StyleColorsDark(ImGuiStyle* dst = NULL);        /* original C++ signature */
def style_colors_dark(dst: Optional[Style] = None) -> None:
    """new, recommended style (default)"""
    pass

# IMGUI_API void          StyleColorsLight(ImGuiStyle* dst = NULL);       /* original C++ signature */
def style_colors_light(dst: Optional[Style] = None) -> None:
    """best used with borders and a custom, thicker font"""
    pass

# IMGUI_API void          StyleColorsClassic(ImGuiStyle* dst = NULL);     /* original C++ signature */
def style_colors_classic(dst: Optional[Style] = None) -> None:
    """classic imgui style"""
    pass

# Windows
# - Begin() = push window to the stack and start appending to it. End() = pop window from the stack.
# - Passing 'bool* p_open != None' shows a window-closing widget in the upper-right corner of the window,
#   which clicking will set the boolean to False when clicked.
# - You may append multiple times to the same window during the same frame by calling Begin()/End() pairs multiple times.
#   Some information such as 'flags' or 'p_open' will only be considered by the first call to Begin().
# - Begin() return False to indicate the window is collapsed or fully clipped, so you may early out and omit submitting
#   anything to the window. Always call a matching End() for each Begin() call, regardless of its return value!
#   [Important: due to legacy reason, Begin/End and BeginChild/EndChild are inconsistent with all other functions
#    such as BeginMenu/EndMenu, BeginPopup/EndPopup, etc. where the EndXXX call should only be called if the corresponding
#    BeginXXX function returned True. Begin and BeginChild are the only odd ones out. Will be fixed in a future update.]
# - Note that the bottom of window stack always contains a window called "Debug".
# IMGUI_API bool          Begin(const char* name, bool* p_open = NULL, ImGuiWindowFlags flags = 0);    /* original C++ signature */
def begin(name: str, p_open: Optional[bool] = None, flags: WindowFlags = 0) -> Tuple[bool, Optional[bool]]:
    pass

# IMGUI_API void          End();    /* original C++ signature */
def end() -> None:
    pass

# Child Windows
# - Use child windows to begin into a self-contained independent scrolling/clipping regions within a host window. Child windows can embed their own child.
# - Before 1.90 (November 2023), the "ImGuiChildFlags child_flags = 0" parameter was "bool border = False".
#   This API is backward compatible with old code, as we guarantee that ImGuiChildFlags_Borders == True.
#   Consider updating your old code:
#      BeginChild("Name", size, False)   -> Begin("Name", size, 0); or Begin("Name", size, ImGuiChildFlags_None);
#      BeginChild("Name", size, True)    -> Begin("Name", size, ImGuiChildFlags_Borders);
# - Manual sizing (each axis can use a different setting e.g. ImVec2(0.0, 400.0)):
#     == 0.0: use remaining parent window size for this axis.
#      > 0.0: use specified size for this axis.
#      < 0.0: right/bottom-align to specified distance from available content boundaries.
# - Specifying ImGuiChildFlags_AutoResizeX or ImGuiChildFlags_AutoResizeY makes the sizing automatic based on child contents.
#   Combining both ImGuiChildFlags_AutoResizeX _and_ ImGuiChildFlags_AutoResizeY defeats purpose of a scrolling region and is NOT recommended.
# - BeginChild() returns False to indicate the window is collapsed or fully clipped, so you may early out and omit submitting
#   anything to the window. Always call a matching EndChild() for each BeginChild() call, regardless of its return value.
#   [Important: due to legacy reason, Begin/End and BeginChild/EndChild are inconsistent with all other functions
#    such as BeginMenu/EndMenu, BeginPopup/EndPopup, etc. where the EndXXX call should only be called if the corresponding
#    BeginXXX function returned True. Begin and BeginChild are the only odd ones out. Will be fixed in a future update.]
# IMGUI_API bool          BeginChild(const char* str_id, const ImVec2& size = ImVec2(0, 0), ImGuiChildFlags child_flags = 0, ImGuiWindowFlags window_flags = 0);    /* original C++ signature */
@overload
def begin_child(
    str_id: str, size: Optional[ImVec2Like] = None, child_flags: ChildFlags = 0, window_flags: WindowFlags = 0
) -> bool:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API bool          BeginChild(ImGuiID id, const ImVec2& size = ImVec2(0, 0), ImGuiChildFlags child_flags = 0, ImGuiWindowFlags window_flags = 0);    /* original C++ signature */
@overload
def begin_child(
    id_: ID, size: Optional[ImVec2Like] = None, child_flags: ChildFlags = 0, window_flags: WindowFlags = 0
) -> bool:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void          EndChild();    /* original C++ signature */
def end_child() -> None:
    pass

# Windows Utilities
# - 'current window' = the window we are appending into while inside a Begin()/End() block. 'next window' = next window we will Begin() into.
# IMGUI_API bool          IsWindowAppearing();    /* original C++ signature */
def is_window_appearing() -> bool:
    pass

# IMGUI_API bool          IsWindowCollapsed();    /* original C++ signature */
def is_window_collapsed() -> bool:
    pass

# IMGUI_API bool          IsWindowFocused(ImGuiFocusedFlags flags=0);     /* original C++ signature */
def is_window_focused(flags: FocusedFlags = 0) -> bool:
    """is current window focused? or its root/child, depending on flags. see flags for options."""
    pass

# IMGUI_API bool          IsWindowHovered(ImGuiHoveredFlags flags=0);     /* original C++ signature */
def is_window_hovered(flags: HoveredFlags = 0) -> bool:
    """is current window hovered and hoverable (e.g. not blocked by a popup/modal)? See ImGuiHoveredFlags_ for options. IMPORTANT: If you are trying to check whether your mouse should be dispatched to Dear ImGui or to your underlying app, you should not use this function! Use the 'io.WantCaptureMouse' boolean for that! Refer to FAQ entry "How can I tell whether to dispatch mouse/keyboard to Dear ImGui or my application?" for details."""
    pass

# IMGUI_API ImDrawList*   GetWindowDrawList();                            /* original C++ signature */
def get_window_draw_list() -> ImDrawList:
    """get draw list associated to the current window, to append your own drawing primitives"""
    pass

# IMGUI_API float         GetWindowDpiScale();                            /* original C++ signature */
def get_window_dpi_scale() -> float:
    """get DPI scale currently associated to the current window's viewport."""
    pass

# IMGUI_API ImVec2        GetWindowPos();                                 /* original C++ signature */
def get_window_pos() -> ImVec2:
    """get current window position in screen space (IT IS UNLIKELY YOU EVER NEED TO USE THIS. Consider always using GetCursorScreenPos() and GetContentRegionAvail() instead)"""
    pass

# IMGUI_API ImVec2        GetWindowSize();                                /* original C++ signature */
def get_window_size() -> ImVec2:
    """get current window size (IT IS UNLIKELY YOU EVER NEED TO USE THIS. Consider always using GetCursorScreenPos() and GetContentRegionAvail() instead)"""
    pass

# IMGUI_API float         GetWindowWidth();                               /* original C++ signature */
def get_window_width() -> float:
    """get current window width (IT IS UNLIKELY YOU EVER NEED TO USE THIS). Shortcut for GetWindowSize().x."""
    pass

# IMGUI_API float         GetWindowHeight();                              /* original C++ signature */
def get_window_height() -> float:
    """get current window height (IT IS UNLIKELY YOU EVER NEED TO USE THIS). Shortcut for GetWindowSize().y."""
    pass

# IMGUI_API ImGuiViewport*GetWindowViewport();                            /* original C++ signature */
def get_window_viewport() -> Viewport:
    """get viewport currently associated to the current window."""
    pass

# Window manipulation
# - Prefer using SetNextXXX functions (before Begin) rather that SetXXX functions (after Begin).
# IMGUI_API void          SetNextWindowPos(const ImVec2& pos, ImGuiCond cond = 0, const ImVec2& pivot = ImVec2(0, 0));     /* original C++ signature */
def set_next_window_pos(pos: ImVec2Like, cond: Cond = 0, pivot: Optional[ImVec2Like] = None) -> None:
    """---
    Python bindings defaults:
        If pivot is None, then its default value will be: ImVec2(0, 0)

     set next window position. call before Begin(). use pivot=(0.5,0.5) to center on given point, etc.
    """
    pass

# IMGUI_API void          SetNextWindowSize(const ImVec2& size, ImGuiCond cond = 0);                      /* original C++ signature */
def set_next_window_size(size: ImVec2Like, cond: Cond = 0) -> None:
    """set next window size. set axis to 0.0 to force an auto-fit on this axis. call before Begin()"""
    pass

# IMGUI_API void          SetNextWindowSizeConstraints(const ImVec2& size_min, const ImVec2& size_max, ImGuiSizeCallback custom_callback = NULL, void* custom_callback_data = NULL);     /* original C++ signature */
def set_next_window_size_constraints(
    size_min: ImVec2Like,
    size_max: ImVec2Like,
    custom_callback: SizeCallback = None,
    custom_callback_data: Optional[Any] = None,
) -> None:
    """set next window size limits. use 0.0 or FLT_MAX if you don't want limits. Use -1 for both min and max of same axis to preserve current size (which itself is a constraint). Use callback to apply non-trivial programmatic constraints."""
    pass

# IMGUI_API void          SetNextWindowContentSize(const ImVec2& size);                                   /* original C++ signature */
def set_next_window_content_size(size: ImVec2Like) -> None:
    """set next window content size (~ scrollable client area, which enforce the range of scrollbars). Not including window decorations (title bar, menu bar, etc.) nor WindowPadding. set an axis to 0.0 to leave it automatic. call before Begin()"""
    pass

# IMGUI_API void          SetNextWindowCollapsed(bool collapsed, ImGuiCond cond = 0);                     /* original C++ signature */
def set_next_window_collapsed(collapsed: bool, cond: Cond = 0) -> None:
    """set next window collapsed state. call before Begin()"""
    pass

# IMGUI_API void          SetNextWindowFocus();                                                           /* original C++ signature */
def set_next_window_focus() -> None:
    """set next window to be focused / top-most. call before Begin()"""
    pass

# IMGUI_API void          SetNextWindowScroll(const ImVec2& scroll);                                      /* original C++ signature */
def set_next_window_scroll(scroll: ImVec2Like) -> None:
    """set next window scrolling value (use < 0.0 to not affect a given axis)."""
    pass

# IMGUI_API void          SetNextWindowBgAlpha(float alpha);                                              /* original C++ signature */
def set_next_window_bg_alpha(alpha: float) -> None:
    """set next window background color alpha. helper to easily override the Alpha component of ImGuiCol_WindowBg/ChildBg/PopupBg. you may also use ImGuiWindowFlags_NoBackground."""
    pass

# IMGUI_API void          SetNextWindowViewport(ImGuiID viewport_id);                                     /* original C++ signature */
def set_next_window_viewport(viewport_id: ID) -> None:
    """set next window viewport"""
    pass

# IMGUI_API void          SetWindowPos(const ImVec2& pos, ImGuiCond cond = 0);                            /* original C++ signature */
@overload
def set_window_pos(pos: ImVec2Like, cond: Cond = 0) -> None:
    """(not recommended) set current window position - call within Begin()/End(). prefer using SetNextWindowPos(), as this may incur tearing and side-effects."""
    pass

# IMGUI_API void          SetWindowSize(const ImVec2& size, ImGuiCond cond = 0);                          /* original C++ signature */
@overload
def set_window_size(size: ImVec2Like, cond: Cond = 0) -> None:
    """(not recommended) set current window size - call within Begin()/End(). set to ImVec2(0, 0) to force an auto-fit. prefer using SetNextWindowSize(), as this may incur tearing and minor side-effects."""
    pass

# IMGUI_API void          SetWindowCollapsed(bool collapsed, ImGuiCond cond = 0);                         /* original C++ signature */
@overload
def set_window_collapsed(collapsed: bool, cond: Cond = 0) -> None:
    """(not recommended) set current window collapsed state. prefer using SetNextWindowCollapsed()."""
    pass

# IMGUI_API void          SetWindowFocus();                                                               /* original C++ signature */
@overload
def set_window_focus() -> None:
    """(not recommended) set current window to be focused / top-most. prefer using SetNextWindowFocus()."""
    pass

# IMGUI_API void          SetWindowFontScale(float scale);                                                /* original C++ signature */
def set_window_font_scale(scale: float) -> None:
    """[OBSOLETE] set font scale. Adjust IO.FontGlobalScale if you want to scale all windows. This is an old API! For correct scaling, prefer to reload font + rebuild ImFontAtlas + call style.ScaleAllSizes()."""
    pass

# IMGUI_API void          SetWindowPos(const char* name, const ImVec2& pos, ImGuiCond cond = 0);          /* original C++ signature */
@overload
def set_window_pos(name: str, pos: ImVec2Like, cond: Cond = 0) -> None:
    """set named window position."""
    pass

# IMGUI_API void          SetWindowSize(const char* name, const ImVec2& size, ImGuiCond cond = 0);        /* original C++ signature */
@overload
def set_window_size(name: str, size: ImVec2Like, cond: Cond = 0) -> None:
    """set named window size. set axis to 0.0 to force an auto-fit on this axis."""
    pass

# IMGUI_API void          SetWindowCollapsed(const char* name, bool collapsed, ImGuiCond cond = 0);       /* original C++ signature */
@overload
def set_window_collapsed(name: str, collapsed: bool, cond: Cond = 0) -> None:
    """set named window collapsed state"""
    pass

# IMGUI_API void          SetWindowFocus(const char* name);                                               /* original C++ signature */
@overload
def set_window_focus(name: str) -> None:
    """set named window to be focused / top-most. use None to remove focus."""
    pass

# Windows Scrolling
# - Any change of Scroll will be applied at the beginning of next frame in the first call to Begin().
# - You may instead use SetNextWindowScroll() prior to calling Begin() to avoid this delay, as an alternative to using SetScrollX()/SetScrollY().
# IMGUI_API float         GetScrollX();                                                       /* original C++ signature */
def get_scroll_x() -> float:
    """get scrolling amount [0 .. GetScrollMaxX()]"""
    pass

# IMGUI_API float         GetScrollY();                                                       /* original C++ signature */
def get_scroll_y() -> float:
    """get scrolling amount [0 .. GetScrollMaxY()]"""
    pass

# IMGUI_API void          SetScrollX(float scroll_x);                                         /* original C++ signature */
def set_scroll_x(scroll_x: float) -> None:
    """set scrolling amount [0 .. GetScrollMaxX()]"""
    pass

# IMGUI_API void          SetScrollY(float scroll_y);                                         /* original C++ signature */
def set_scroll_y(scroll_y: float) -> None:
    """set scrolling amount [0 .. GetScrollMaxY()]"""
    pass

# IMGUI_API float         GetScrollMaxX();                                                    /* original C++ signature */
def get_scroll_max_x() -> float:
    """get maximum scrolling amount ~~ ContentSize.x - WindowSize.x - DecorationsSize.x"""
    pass

# IMGUI_API float         GetScrollMaxY();                                                    /* original C++ signature */
def get_scroll_max_y() -> float:
    """get maximum scrolling amount ~~ ContentSize.y - WindowSize.y - DecorationsSize.y"""
    pass

# IMGUI_API void          SetScrollHereX(float center_x_ratio = 0.5f);                        /* original C++ signature */
def set_scroll_here_x(center_x_ratio: float = 0.5) -> None:
    """adjust scrolling amount to make current cursor position visible. center_x_ratio=0.0: left, 0.5: center, 1.0: right. When using to make a "default/current item" visible, consider using SetItemDefaultFocus() instead."""
    pass

# IMGUI_API void          SetScrollHereY(float center_y_ratio = 0.5f);                        /* original C++ signature */
def set_scroll_here_y(center_y_ratio: float = 0.5) -> None:
    """adjust scrolling amount to make current cursor position visible. center_y_ratio=0.0: top, 0.5: center, 1.0: bottom. When using to make a "default/current item" visible, consider using SetItemDefaultFocus() instead."""
    pass

# IMGUI_API void          SetScrollFromPosX(float local_x, float center_x_ratio = 0.5f);      /* original C++ signature */
def set_scroll_from_pos_x(local_x: float, center_x_ratio: float = 0.5) -> None:
    """adjust scrolling amount to make given position visible. Generally GetCursorStartPos() + offset to compute a valid position."""
    pass

# IMGUI_API void          SetScrollFromPosY(float local_y, float center_y_ratio = 0.5f);      /* original C++ signature */
def set_scroll_from_pos_y(local_y: float, center_y_ratio: float = 0.5) -> None:
    """adjust scrolling amount to make given position visible. Generally GetCursorStartPos() + offset to compute a valid position."""
    pass

# Parameters stacks (shared)
# IMGUI_API void          PushFont(ImFont* font);                                             /* original C++ signature */
def push_font(font: ImFont) -> None:
    """use None as a shortcut to push default font"""
    pass

# IMGUI_API void          PopFont();    /* original C++ signature */
def pop_font() -> None:
    pass

# IMGUI_API void          PushStyleColor(ImGuiCol idx, ImU32 col);                            /* original C++ signature */
@overload
def push_style_color(idx: Col, col: ImU32) -> None:
    """modify a style color. always use this if you modify the style after NewFrame()."""
    pass

# IMGUI_API void          PushStyleColor(ImGuiCol idx, const ImVec4& col);    /* original C++ signature */
@overload
def push_style_color(idx: Col, col: ImVec4Like) -> None:
    pass

# IMGUI_API void          PopStyleColor(int count = 1);    /* original C++ signature */
def pop_style_color(count: int = 1) -> None:
    pass

# IMGUI_API void          PushStyleVar(ImGuiStyleVar idx, float val);                         /* original C++ signature */
@overload
def push_style_var(idx: StyleVar, val: float) -> None:
    """modify a style float variable. always use this if you modify the style after NewFrame()!"""
    pass

# IMGUI_API void          PushStyleVar(ImGuiStyleVar idx, const ImVec2& val);                 /* original C++ signature */
@overload
def push_style_var(idx: StyleVar, val: ImVec2Like) -> None:
    """modify a style ImVec2 variable. " """
    pass

# IMGUI_API void          PushStyleVarX(ImGuiStyleVar idx, float val_x);                      /* original C++ signature */
def push_style_var_x(idx: StyleVar, val_x: float) -> None:
    """modify X component of a style ImVec2 variable. " """
    pass

# IMGUI_API void          PushStyleVarY(ImGuiStyleVar idx, float val_y);                      /* original C++ signature */
def push_style_var_y(idx: StyleVar, val_y: float) -> None:
    """modify Y component of a style ImVec2 variable. " """
    pass

# IMGUI_API void          PopStyleVar(int count = 1);    /* original C++ signature */
def pop_style_var(count: int = 1) -> None:
    pass

# IMGUI_API void          PushItemFlag(ImGuiItemFlags option, bool enabled);                  /* original C++ signature */
def push_item_flag(option: ItemFlags, enabled: bool) -> None:
    """modify specified shared item flag, e.g. PushItemFlag(ImGuiItemFlags_NoTabStop, True)"""
    pass

# IMGUI_API void          PopItemFlag();    /* original C++ signature */
def pop_item_flag() -> None:
    pass

# Parameters stacks (current window)
# IMGUI_API void          PushItemWidth(float item_width);                                    /* original C++ signature */
def push_item_width(item_width: float) -> None:
    """push width of items for common large "item+label" widgets. >0.0: width in pixels, <0.0 align xx pixels to the right of window (so -FLT_MIN always align width to the right side)."""
    pass

# IMGUI_API void          PopItemWidth();    /* original C++ signature */
def pop_item_width() -> None:
    pass

# IMGUI_API void          SetNextItemWidth(float item_width);                                 /* original C++ signature */
def set_next_item_width(item_width: float) -> None:
    """set width of the _next_ common large "item+label" widget. >0.0: width in pixels, <0.0 align xx pixels to the right of window (so -FLT_MIN always align width to the right side)"""
    pass

# IMGUI_API float         CalcItemWidth();                                                    /* original C++ signature */
def calc_item_width() -> float:
    """width of item given pushed settings and current cursor position. NOT necessarily the width of last item unlike most 'Item' functions."""
    pass

# IMGUI_API void          PushTextWrapPos(float wrap_local_pos_x = 0.0f);                     /* original C++ signature */
def push_text_wrap_pos(wrap_local_pos_x: float = 0.0) -> None:
    """push word-wrapping position for Text*() commands. < 0.0: no wrapping; 0.0: wrap to end of window (or column); > 0.0: wrap at 'wrap_pos_x' position in window local space"""
    pass

# IMGUI_API void          PopTextWrapPos();    /* original C++ signature */
def pop_text_wrap_pos() -> None:
    pass

# Style read access
# - Use the ShowStyleEditor() function to interactively see/edit the colors.
# IMGUI_API ImFont*       GetFont();                                                          /* original C++ signature */
def get_font() -> ImFont:
    """get current font"""
    pass

# IMGUI_API float         GetFontSize();                                                      /* original C++ signature */
def get_font_size() -> float:
    """get current font size (= height in pixels) of current font with current scale applied"""
    pass

# IMGUI_API ImVec2        GetFontTexUvWhitePixel();                                           /* original C++ signature */
def get_font_tex_uv_white_pixel() -> ImVec2:
    """get UV coordinate for a white pixel, useful to draw custom shapes via the ImDrawList API"""
    pass

# IMGUI_API ImU32         GetColorU32(ImGuiCol idx, float alpha_mul = 1.0f);                  /* original C++ signature */
@overload
def get_color_u32(idx: Col, alpha_mul: float = 1.0) -> ImU32:
    """retrieve given style color with style alpha applied and optional extra alpha multiplier, packed as a 32-bit value suitable for ImDrawList"""
    pass

# IMGUI_API ImU32         GetColorU32(const ImVec4& col);                                     /* original C++ signature */
@overload
def get_color_u32(col: ImVec4Like) -> ImU32:
    """retrieve given color with style alpha applied, packed as a 32-bit value suitable for ImDrawList"""
    pass

# IMGUI_API ImU32         GetColorU32(ImU32 col, float alpha_mul = 1.0f);                     /* original C++ signature */
@overload
def get_color_u32(col: ImU32, alpha_mul: float = 1.0) -> ImU32:
    """retrieve given color with style alpha applied, packed as a 32-bit value suitable for ImDrawList"""
    pass

# IMGUI_API const ImVec4& GetStyleColorVec4(ImGuiCol idx);                                    /* original C++ signature */
def get_style_color_vec4(idx: Col) -> ImVec4:
    """retrieve style color as stored in ImGuiStyle structure. use to feed back into PushStyleColor(), otherwise use GetColorU32() to get style color with style alpha baked in."""
    pass

# Layout cursor positioning
# - By "cursor" we mean the current output position.
# - The typical widget behavior is to output themselves at the current cursor position, then move the cursor one line down.
# - You can call SameLine() between widgets to undo the last carriage return and output at the right of the preceding widget.
# - YOU CAN DO 99% OF WHAT YOU NEED WITH ONLY GetCursorScreenPos() and GetContentRegionAvail().
# - Attention! We currently have inconsistencies between window-local and absolute positions we will aim to fix with future API:
#    - Absolute coordinate:        GetCursorScreenPos(), SetCursorScreenPos(), all ImDrawList:: functions. -> this is the preferred way forward.
#    - Window-local coordinates:   SameLine(offset), GetCursorPos(), SetCursorPos(), GetCursorStartPos(), PushTextWrapPos()
#    - Window-local coordinates:   GetContentRegionMax(), GetWindowContentRegionMin(), GetWindowContentRegionMax() --> all obsoleted. YOU DON'T NEED THEM.
# - GetCursorScreenPos() = GetCursorPos() + GetWindowPos(). GetWindowPos() is almost only ever useful to convert from window-local to absolute coordinates. Try not to use it.
# IMGUI_API ImVec2        GetCursorScreenPos();                                               /* original C++ signature */
def get_cursor_screen_pos() -> ImVec2:
    """cursor position, absolute coordinates. THIS IS YOUR BEST FRIEND (prefer using this rather than GetCursorPos(), also more useful to work with ImDrawList API)."""
    pass

# IMGUI_API void          SetCursorScreenPos(const ImVec2& pos);                              /* original C++ signature */
def set_cursor_screen_pos(pos: ImVec2Like) -> None:
    """cursor position, absolute coordinates. THIS IS YOUR BEST FRIEND."""
    pass

# IMGUI_API ImVec2        GetContentRegionAvail();                                            /* original C++ signature */
def get_content_region_avail() -> ImVec2:
    """available space from current position. THIS IS YOUR BEST FRIEND."""
    pass

# IMGUI_API ImVec2        GetCursorPos();                                                     /* original C++ signature */
def get_cursor_pos() -> ImVec2:
    """[window-local] cursor position in window-local coordinates. This is not your best friend."""
    pass

# IMGUI_API float         GetCursorPosX();                                                    /* original C++ signature */
def get_cursor_pos_x() -> float:
    """[window-local] " """
    pass

# IMGUI_API float         GetCursorPosY();                                                    /* original C++ signature */
def get_cursor_pos_y() -> float:
    """[window-local] " """
    pass

# IMGUI_API void          SetCursorPos(const ImVec2& local_pos);                              /* original C++ signature */
def set_cursor_pos(local_pos: ImVec2Like) -> None:
    """[window-local] " """
    pass

# IMGUI_API void          SetCursorPosX(float local_x);                                       /* original C++ signature */
def set_cursor_pos_x(local_x: float) -> None:
    """[window-local] " """
    pass

# IMGUI_API void          SetCursorPosY(float local_y);                                       /* original C++ signature */
def set_cursor_pos_y(local_y: float) -> None:
    """[window-local] " """
    pass

# IMGUI_API ImVec2        GetCursorStartPos();                                                /* original C++ signature */
def get_cursor_start_pos() -> ImVec2:
    """[window-local] initial cursor position, in window-local coordinates. Call GetCursorScreenPos() after Begin() to get the absolute coordinates version."""
    pass

# Other layout functions
# IMGUI_API void          Separator();                                                        /* original C++ signature */
def separator() -> None:
    """separator, generally horizontal. inside a menu bar or in horizontal layout mode, this becomes a vertical separator."""
    pass

# IMGUI_API void          SameLine(float offset_from_start_x=0.0f, float spacing=-1.0f);      /* original C++ signature */
def same_line(offset_from_start_x: float = 0.0, spacing: float = -1.0) -> None:
    """call between widgets or groups to layout them horizontally. X position given in window coordinates."""
    pass

# IMGUI_API void          NewLine();                                                          /* original C++ signature */
def new_line() -> None:
    """undo a SameLine() or force a new line when in a horizontal-layout context."""
    pass

# IMGUI_API void          Spacing();                                                          /* original C++ signature */
def spacing() -> None:
    """add vertical spacing."""
    pass

# IMGUI_API void          Dummy(const ImVec2& size);                                          /* original C++ signature */
def dummy(size: ImVec2Like) -> None:
    """add a dummy item of given size. unlike InvisibleButton(), Dummy() won't take the mouse click or be navigable into."""
    pass

# IMGUI_API void          Indent(float indent_w = 0.0f);                                      /* original C++ signature */
def indent(indent_w: float = 0.0) -> None:
    """move content position toward the right, by indent_w, or style.IndentSpacing if indent_w <= 0"""
    pass

# IMGUI_API void          Unindent(float indent_w = 0.0f);                                    /* original C++ signature */
def unindent(indent_w: float = 0.0) -> None:
    """move content position back to the left, by indent_w, or style.IndentSpacing if indent_w <= 0"""
    pass

# IMGUI_API void          BeginGroup();                                                       /* original C++ signature */
def begin_group() -> None:
    """lock horizontal starting position"""
    pass

# IMGUI_API void          EndGroup();                                                         /* original C++ signature */
def end_group() -> None:
    """unlock horizontal starting position + capture the whole group bounding box into one "item" (so you can use IsItemHovered() or layout primitives such as SameLine() on whole group, etc.)"""
    pass

# IMGUI_API void          AlignTextToFramePadding();                                          /* original C++ signature */
def align_text_to_frame_padding() -> None:
    """vertically align upcoming text baseline to FramePadding.y so that it will align properly to regularly framed items (call if you have text on a line before a framed item)"""
    pass

# IMGUI_API float         GetTextLineHeight();                                                /* original C++ signature */
def get_text_line_height() -> float:
    """~ FontSize"""
    pass

# IMGUI_API float         GetTextLineHeightWithSpacing();                                     /* original C++ signature */
def get_text_line_height_with_spacing() -> float:
    """~ FontSize + style.ItemSpacing.y (distance in pixels between 2 consecutive lines of text)"""
    pass

# IMGUI_API float         GetFrameHeight();                                                   /* original C++ signature */
def get_frame_height() -> float:
    """~ FontSize + style.FramePadding.y * 2"""
    pass

# IMGUI_API float         GetFrameHeightWithSpacing();                                        /* original C++ signature */
def get_frame_height_with_spacing() -> float:
    """~ FontSize + style.FramePadding.y * 2 + style.ItemSpacing.y (distance in pixels between 2 consecutive lines of framed widgets)"""
    pass

# ID stack/scopes
# Read the FAQ (docs/FAQ.md or http://dearimgui.com/faq) for more details about how ID are handled in dear imgui.
# - Those questions are answered and impacted by understanding of the ID stack system:
#   - "Q: Why is my widget not reacting when I click on it?"
#   - "Q: How can I have widgets with an empty label?"
#   - "Q: How can I have multiple widgets with the same label?"
# - Short version: ID are hashes of the entire ID stack. If you are creating widgets in a loop you most likely
#   want to push a unique identifier (e.g. object pointer, loop index) to uniquely differentiate them.
# - You can also use the "Label##foobar" syntax within widget label to distinguish them from each others.
# - In this header file we use the "label"/"name" terminology to denote a string that will be displayed + used as an ID,
#   whereas "str_id" denote a string that is only used as an ID and not normally displayed.
# IMGUI_API void          PushID(const char* str_id);                                         /* original C++ signature */
@overload
def push_id(str_id: str) -> None:
    """push string into the ID stack (will hash string)."""
    pass

# IMGUI_API void          PushID(const char* str_id_begin, const char* str_id_end);           /* original C++ signature */
@overload
def push_id(str_id_begin: str, str_id_end: str) -> None:
    """push string into the ID stack (will hash string)."""
    pass

# IMGUI_API void          PushID(const void* ptr_id);                                         /* original C++ signature */
@overload
def push_id(ptr_id: Any) -> None:
    """push pointer into the ID stack (will hash pointer)."""
    pass

# IMGUI_API void          PushID(int int_id);                                                 /* original C++ signature */
@overload
def push_id(int_id: int) -> None:
    """push integer into the ID stack (will hash integer)."""
    pass

# IMGUI_API void          PopID();                                                            /* original C++ signature */
def pop_id() -> None:
    """pop from the ID stack."""
    pass

# IMGUI_API ImGuiID       GetID(const char* str_id);                                          /* original C++ signature */
@overload
def get_id(str_id: str) -> ID:
    """calculate unique ID (hash of whole ID stack + given parameter). e.g. if you want to query into ImGuiStorage yourself"""
    pass

# IMGUI_API ImGuiID       GetID(const char* str_id_begin, const char* str_id_end);    /* original C++ signature */
@overload
def get_id(str_id_begin: str, str_id_end: str) -> ID:
    pass

# IMGUI_API ImGuiID       GetID(const void* ptr_id);    /* original C++ signature */
@overload
def get_id(ptr_id: Any) -> ID:
    pass

# IMGUI_API ImGuiID       GetID(int int_id);    /* original C++ signature */
@overload
def get_id(int_id: int) -> ID:
    pass

# Widgets: Text
# IMGUI_API void          TextUnformatted(const char* text, const char* text_end = NULL);     /* original C++ signature */
def text_unformatted(text: str, text_end: Optional[str] = None) -> None:
    """raw text without formatting. Roughly equivalent to Text("%s", text) but: A) doesn't require null terminated string if 'text_end' is specified, B) it's faster, no memory copy is done, no buffer size limits, recommended for long chunks of text."""
    pass

# IMGUI_API void          Text(const char* fmt, ...)                                      ;     /* original C++ signature */
def text(fmt: str) -> None:
    """formatted text"""
    pass

# IMGUI_API void          TextColored(const ImVec4& col, const char* fmt, ...)            ;     /* original C++ signature */
def text_colored(col: ImVec4Like, fmt: str) -> None:
    """shortcut for PushStyleColor(ImGuiCol_Text, col); Text(fmt, ...); PopStyleColor();"""
    pass

# IMGUI_API void          TextDisabled(const char* fmt, ...)                              ;     /* original C++ signature */
def text_disabled(fmt: str) -> None:
    """shortcut for PushStyleColor(ImGuiCol_Text, style.Colors[ImGuiCol_TextDisabled]); Text(fmt, ...); PopStyleColor();"""
    pass

# IMGUI_API void          TextWrapped(const char* fmt, ...)                               ;     /* original C++ signature */
def text_wrapped(fmt: str) -> None:
    """shortcut for PushTextWrapPos(0.0); Text(fmt, ...); PopTextWrapPos();. Note that this won't work on an auto-resizing window if there's no other widgets to extend the window width, yoy may need to set a size using SetNextWindowSize()."""
    pass

# IMGUI_API void          LabelText(const char* label, const char* fmt, ...)              ;     /* original C++ signature */
def label_text(label: str, fmt: str) -> None:
    """display text+label aligned the same way as value+label widgets"""
    pass

# IMGUI_API void          BulletText(const char* fmt, ...)                                ;     /* original C++ signature */
def bullet_text(fmt: str) -> None:
    """shortcut for Bullet()+Text()"""
    pass

# IMGUI_API void          SeparatorText(const char* label);                                   /* original C++ signature */
def separator_text(label: str) -> None:
    """currently: formatted text with an horizontal line"""
    pass

# Widgets: Main
# - Most widgets return True when the value has been changed or when pressed/selected
# - You may also use one of the many IsItemXXX functions (e.g. IsItemActive, IsItemHovered, etc.) to query widget state.
# IMGUI_API bool          Button(const char* label, const ImVec2& size = ImVec2(0, 0));       /* original C++ signature */
def button(label: str, size: Optional[ImVec2Like] = None) -> bool:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)

     button
    """
    pass

# IMGUI_API bool          SmallButton(const char* label);                                     /* original C++ signature */
def small_button(label: str) -> bool:
    """button with (FramePadding.y == 0) to easily embed within text"""
    pass

# IMGUI_API bool          InvisibleButton(const char* str_id, const ImVec2& size, ImGuiButtonFlags flags = 0);     /* original C++ signature */
def invisible_button(str_id: str, size: ImVec2Like, flags: ButtonFlags = 0) -> bool:
    """flexible button behavior without the visuals, frequently useful to build custom behaviors using the public api (along with IsItemActive, IsItemHovered, etc.)"""
    pass

# IMGUI_API bool          ArrowButton(const char* str_id, ImGuiDir dir);                      /* original C++ signature */
def arrow_button(str_id: str, dir: Dir) -> bool:
    """square button with an arrow shape"""
    pass

# IMGUI_API bool          Checkbox(const char* label, bool* v);    /* original C++ signature */
def checkbox(label: str, v: bool) -> Tuple[bool, bool]:
    pass

# IMGUI_API bool          CheckboxFlags(const char* label, int* flags, int flags_value);    /* original C++ signature */
@overload
def checkbox_flags(label: str, flags: int, flags_value: int) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          CheckboxFlags(const char* label, unsigned int* flags, unsigned int flags_value);    /* original C++ signature */
@overload
def checkbox_flags(label: str, flags: int, flags_value: int) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          RadioButton(const char* label, bool active);                        /* original C++ signature */
@overload
def radio_button(label: str, active: bool) -> bool:
    """use with e.g. if (RadioButton("one", my_value==1)) { my_value = 1; }"""
    pass

# IMGUI_API bool          RadioButton(const char* label, int* v, int v_button);               /* original C++ signature */
@overload
def radio_button(label: str, v: int, v_button: int) -> Tuple[bool, int]:
    """shortcut to handle the above pattern when value is an integer"""
    pass

# IMGUI_API void          ProgressBar(float fraction, const ImVec2& size_arg = ImVec2(-FLT_MIN, 0), const char* overlay = NULL);    /* original C++ signature */
def progress_bar(fraction: float, size_arg: Optional[ImVec2Like] = None, overlay: Optional[str] = None) -> None:
    """---
    Python bindings defaults:
        If size_arg is None, then its default value will be: ImVec2(-sys.float_info.min, 0)
    """
    pass

# IMGUI_API void          Bullet();                                                           /* original C++ signature */
def bullet() -> None:
    """draw a small circle + keep the cursor on the same line. advance cursor x position by GetTreeNodeToLabelSpacing(), same distance that TreeNode() uses"""
    pass

# IMGUI_API bool          TextLink(const char* label);                                        /* original C++ signature */
def text_link(label: str) -> bool:
    """hyperlink text button, return True when clicked"""
    pass

# IMGUI_API void          TextLinkOpenURL(const char* label, const char* url = NULL);         /* original C++ signature */
def text_link_open_url(label: str, url: Optional[str] = None) -> None:
    """hyperlink text button, automatically open file/url when clicked"""
    pass

# Widgets: Images
# - Read about ImTextureID here: https://github.com/ocornut/imgui/wiki/Image-Loading-and-Displaying-Examples
# - 'uv0' and 'uv1' are texture coordinates. Read about them from the same link above.
# - Note that Image() may add +2.0 to provided size if a border is visible, ImageButton() adds style.FramePadding*2.0 to provided size.
# - ImageButton() draws a background based on regular Button() color + optionally an inner background if specified.
# IMGUI_API void          Image(ImTextureID user_texture_id, const ImVec2& image_size, const ImVec2& uv0 = ImVec2(0, 0), const ImVec2& uv1 = ImVec2(1, 1), const ImVec4& tint_col = ImVec4(1, 1, 1, 1), const ImVec4& border_col = ImVec4(0, 0, 0, 0));    /* original C++ signature */
def image(
    user_texture_id: ImTextureID,
    image_size: ImVec2Like,
    uv0: Optional[ImVec2Like] = None,
    uv1: Optional[ImVec2Like] = None,
    tint_col: Optional[ImVec4Like] = None,
    border_col: Optional[ImVec4Like] = None,
) -> None:
    """---
    Python bindings defaults:
        If any of the params below is None, then its default value below will be used:
            uv0: ImVec2(0, 0)
            uv1: ImVec2(1, 1)
            tint_col: ImVec4(1, 1, 1, 1)
            border_col: ImVec4(0, 0, 0, 0)
    """
    pass

# IMGUI_API bool          ImageButton(const char* str_id, ImTextureID user_texture_id, const ImVec2& image_size, const ImVec2& uv0 = ImVec2(0, 0), const ImVec2& uv1 = ImVec2(1, 1), const ImVec4& bg_col = ImVec4(0, 0, 0, 0), const ImVec4& tint_col = ImVec4(1, 1, 1, 1));    /* original C++ signature */
def image_button(
    str_id: str,
    user_texture_id: ImTextureID,
    image_size: ImVec2Like,
    uv0: Optional[ImVec2Like] = None,
    uv1: Optional[ImVec2Like] = None,
    bg_col: Optional[ImVec4Like] = None,
    tint_col: Optional[ImVec4Like] = None,
) -> bool:
    """---
    Python bindings defaults:
        If any of the params below is None, then its default value below will be used:
            uv0: ImVec2(0, 0)
            uv1: ImVec2(1, 1)
            bg_col: ImVec4(0, 0, 0, 0)
            tint_col: ImVec4(1, 1, 1, 1)
    """
    pass

# Widgets: Combo Box (Dropdown)
# - The BeginCombo()/EndCombo() api allows you to manage your contents and selection state however you want it, by creating e.g. Selectable() items.
# - The old Combo() api are helpers over BeginCombo()/EndCombo() which are kept available for convenience purpose. This is analogous to how ListBox are created.
# IMGUI_API bool          BeginCombo(const char* label, const char* preview_value, ImGuiComboFlags flags = 0);    /* original C++ signature */
def begin_combo(label: str, preview_value: str, flags: ComboFlags = 0) -> bool:
    pass

# IMGUI_API void          EndCombo();     /* original C++ signature */
def end_combo() -> None:
    """only call EndCombo() if BeginCombo() returns True!"""
    pass

# IMGUI_API bool          Combo(const char* label, int* current_item, const char* const items[], int items_count, int popup_max_height_in_items = -1);    /* original C++ signature */
@overload
def combo(label: str, current_item: int, items: List[str], popup_max_height_in_items: int = -1) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          Combo(const char* label, int* current_item, const char* items_separated_by_zeros, int popup_max_height_in_items = -1);          /* original C++ signature */
@overload
def combo(
    label: str, current_item: int, items_separated_by_zeros: str, popup_max_height_in_items: int = -1
) -> Tuple[bool, int]:
    """Separate items with \0 within a string, end item-list with \0\0. e.g. "One\0Two\0Three\0" """
    pass

# Widgets: Drag Sliders
# - CTRL+Click on any drag box to turn them into an input box. Manually input values aren't clamped by default and can go off-bounds. Use ImGuiSliderFlags_AlwaysClamp to always clamp.
# - For all the Float2/Float3/Float4/Int2/Int3/Int4 versions of every function, note that a 'float v[X]' function argument is the same as 'float* v',
#   the array syntax is just a way to document the number of elements that are expected to be accessible. You can pass address of your first element out of a contiguous set, e.g. &myvector.x
# - Adjust format string to decorate the value with a prefix, a suffix, or adapt the editing and display precision e.g. "%.3" -> 1.234; "%5.2 secs" -> 01.23 secs; "Biscuit: %.0" -> Biscuit: 1; etc.
# - Format string may also be set to None or use the default format ("%f" or "%d").
# - Speed are per-pixel of mouse movement (v_speed=0.2: mouse needs to move by 5 pixels to increase value by 1). For keyboard/gamepad navigation, minimum speed is Max(v_speed, minimum_step_at_given_precision).
# - Use v_min < v_max to clamp edits to given limits. Note that CTRL+Click manual input can override those limits if ImGuiSliderFlags_AlwaysClamp is not used.
# - Use v_max = FLT_MAX / INT_MAX etc to avoid clamping to a maximum, same with v_min = -FLT_MAX / INT_MIN to avoid clamping to a minimum.
# - We use the same sets of flags for DragXXX() and SliderXXX() functions as the features are the same and it makes it easier to swap them.
# - Legacy: Pre-1.78 there are DragXXX() function signatures that take a final `float power=1.0' argument instead of the `ImGuiSliderFlags flags=0' argument.
#   If you get a warning converting a float to ImGuiSliderFlags, read https://github.com/ocornut/imgui/issues/3361
# IMGUI_API bool          DragFloat(const char* label, float* v, float v_speed = 1.0f, float v_min = 0.0f, float v_max = 0.0f, const char* format = "%.3f", ImGuiSliderFlags flags = 0);         /* original C++ signature */
def drag_float(
    label: str,
    v: float,
    v_speed: float = 1.0,
    v_min: float = 0.0,
    v_max: float = 0.0,
    format: str = "%.3",
    flags: SliderFlags = 0,
) -> Tuple[bool, float]:
    """If v_min >= v_max we have no bound"""
    pass

# IMGUI_API bool          DragFloat2(const char* label, float v[2], float v_speed = 1.0f, float v_min = 0.0f, float v_max = 0.0f, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_float2(
    label: str,
    v: List[float],
    v_speed: float = 1.0,
    v_min: float = 0.0,
    v_max: float = 0.0,
    format: str = "%.3",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          DragFloat3(const char* label, float v[3], float v_speed = 1.0f, float v_min = 0.0f, float v_max = 0.0f, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_float3(
    label: str,
    v: List[float],
    v_speed: float = 1.0,
    v_min: float = 0.0,
    v_max: float = 0.0,
    format: str = "%.3",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          DragFloat4(const char* label, float v[4], float v_speed = 1.0f, float v_min = 0.0f, float v_max = 0.0f, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_float4(
    label: str,
    v: List[float],
    v_speed: float = 1.0,
    v_min: float = 0.0,
    v_max: float = 0.0,
    format: str = "%.3",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          DragFloatRange2(const char* label, float* v_current_min, float* v_current_max, float v_speed = 1.0f, float v_min = 0.0f, float v_max = 0.0f, const char* format = "%.3f", const char* format_max = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_float_range2(
    label: str,
    v_current_min: float,
    v_current_max: float,
    v_speed: float = 1.0,
    v_min: float = 0.0,
    v_max: float = 0.0,
    format: str = "%.3",
    format_max: Optional[str] = None,
    flags: SliderFlags = 0,
) -> Tuple[bool, float, float]:
    pass

# IMGUI_API bool          DragInt(const char* label, int* v, float v_speed = 1.0f, int v_min = 0, int v_max = 0, const char* format = "%d", ImGuiSliderFlags flags = 0);      /* original C++ signature */
def drag_int(
    label: str, v: int, v_speed: float = 1.0, v_min: int = 0, v_max: int = 0, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, int]:
    """If v_min >= v_max we have no bound"""
    pass

# IMGUI_API bool          DragInt2(const char* label, int v[2], float v_speed = 1.0f, int v_min = 0, int v_max = 0, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_int2(
    label: str,
    v: List[int],
    v_speed: float = 1.0,
    v_min: int = 0,
    v_max: int = 0,
    format: str = "%d",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          DragInt3(const char* label, int v[3], float v_speed = 1.0f, int v_min = 0, int v_max = 0, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_int3(
    label: str,
    v: List[int],
    v_speed: float = 1.0,
    v_min: int = 0,
    v_max: int = 0,
    format: str = "%d",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          DragInt4(const char* label, int v[4], float v_speed = 1.0f, int v_min = 0, int v_max = 0, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_int4(
    label: str,
    v: List[int],
    v_speed: float = 1.0,
    v_min: int = 0,
    v_max: int = 0,
    format: str = "%d",
    flags: SliderFlags = 0,
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          DragIntRange2(const char* label, int* v_current_min, int* v_current_max, float v_speed = 1.0f, int v_min = 0, int v_max = 0, const char* format = "%d", const char* format_max = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_int_range2(
    label: str,
    v_current_min: int,
    v_current_max: int,
    v_speed: float = 1.0,
    v_min: int = 0,
    v_max: int = 0,
    format: str = "%d",
    format_max: Optional[str] = None,
    flags: SliderFlags = 0,
) -> Tuple[bool, int, int]:
    pass

# IMGUI_API bool          DragScalar(const char* label, ImGuiDataType data_type, void* p_data, float v_speed = 1.0f, const void* p_min = NULL, const void* p_max = NULL, const char* format = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_scalar(
    label: str,
    data_type: DataType,
    p_data: Any,
    v_speed: float = 1.0,
    p_min: Optional[Any] = None,
    p_max: Optional[Any] = None,
    format: Optional[str] = None,
    flags: SliderFlags = 0,
) -> bool:
    pass

# IMGUI_API bool          DragScalarN(const char* label, ImGuiDataType data_type, void* p_data, int components, float v_speed = 1.0f, const void* p_min = NULL, const void* p_max = NULL, const char* format = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def drag_scalar_n(
    label: str,
    data_type: DataType,
    p_data: Any,
    components: int,
    v_speed: float = 1.0,
    p_min: Optional[Any] = None,
    p_max: Optional[Any] = None,
    format: Optional[str] = None,
    flags: SliderFlags = 0,
) -> bool:
    pass

# Widgets: Regular Sliders
# - CTRL+Click on any slider to turn them into an input box. Manually input values aren't clamped by default and can go off-bounds. Use ImGuiSliderFlags_AlwaysClamp to always clamp.
# - Adjust format string to decorate the value with a prefix, a suffix, or adapt the editing and display precision e.g. "%.3" -> 1.234; "%5.2 secs" -> 01.23 secs; "Biscuit: %.0" -> Biscuit: 1; etc.
# - Format string may also be set to None or use the default format ("%f" or "%d").
# - Legacy: Pre-1.78 there are SliderXXX() function signatures that take a final `float power=1.0' argument instead of the `ImGuiSliderFlags flags=0' argument.
#   If you get a warning converting a float to ImGuiSliderFlags, read https://github.com/ocornut/imgui/issues/3361
# IMGUI_API bool          SliderFloat(const char* label, float* v, float v_min, float v_max, const char* format = "%.3f", ImGuiSliderFlags flags = 0);         /* original C++ signature */
def slider_float(
    label: str, v: float, v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
) -> Tuple[bool, float]:
    """adjust format to decorate the value with a prefix or a suffix for in-slider labels or unit display."""
    pass

# IMGUI_API bool          SliderFloat2(const char* label, float v[2], float v_min, float v_max, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_float2(
    label: str, v: List[float], v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          SliderFloat3(const char* label, float v[3], float v_min, float v_max, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_float3(
    label: str, v: List[float], v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          SliderFloat4(const char* label, float v[4], float v_min, float v_max, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_float4(
    label: str, v: List[float], v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          SliderAngle(const char* label, float* v_rad, float v_degrees_min = -360.0f, float v_degrees_max = +360.0f, const char* format = "%.0f deg", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_angle(
    label: str,
    v_rad: float,
    v_degrees_min: float = -360.0,
    v_degrees_max: float = +360.0,
    format: str = "%.0 deg",
    flags: SliderFlags = 0,
) -> Tuple[bool, float]:
    pass

# IMGUI_API bool          SliderInt(const char* label, int* v, int v_min, int v_max, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_int(
    label: str, v: int, v_min: int, v_max: int, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          SliderInt2(const char* label, int v[2], int v_min, int v_max, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_int2(
    label: str, v: List[int], v_min: int, v_max: int, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          SliderInt3(const char* label, int v[3], int v_min, int v_max, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_int3(
    label: str, v: List[int], v_min: int, v_max: int, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          SliderInt4(const char* label, int v[4], int v_min, int v_max, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_int4(
    label: str, v: List[int], v_min: int, v_max: int, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          SliderScalar(const char* label, ImGuiDataType data_type, void* p_data, const void* p_min, const void* p_max, const char* format = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_scalar(
    label: str,
    data_type: DataType,
    p_data: Any,
    p_min: Any,
    p_max: Any,
    format: Optional[str] = None,
    flags: SliderFlags = 0,
) -> bool:
    pass

# IMGUI_API bool          SliderScalarN(const char* label, ImGuiDataType data_type, void* p_data, int components, const void* p_min, const void* p_max, const char* format = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def slider_scalar_n(
    label: str,
    data_type: DataType,
    p_data: Any,
    components: int,
    p_min: Any,
    p_max: Any,
    format: Optional[str] = None,
    flags: SliderFlags = 0,
) -> bool:
    pass

# IMGUI_API bool          VSliderFloat(const char* label, const ImVec2& size, float* v, float v_min, float v_max, const char* format = "%.3f", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def v_slider_float(
    label: str, size: ImVec2Like, v: float, v_min: float, v_max: float, format: str = "%.3", flags: SliderFlags = 0
) -> Tuple[bool, float]:
    pass

# IMGUI_API bool          VSliderInt(const char* label, const ImVec2& size, int* v, int v_min, int v_max, const char* format = "%d", ImGuiSliderFlags flags = 0);    /* original C++ signature */
def v_slider_int(
    label: str, size: ImVec2Like, v: int, v_min: int, v_max: int, format: str = "%d", flags: SliderFlags = 0
) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          VSliderScalar(const char* label, const ImVec2& size, ImGuiDataType data_type, void* p_data, const void* p_min, const void* p_max, const char* format = NULL, ImGuiSliderFlags flags = 0);    /* original C++ signature */
def v_slider_scalar(
    label: str,
    size: ImVec2Like,
    data_type: DataType,
    p_data: Any,
    p_min: Any,
    p_max: Any,
    format: Optional[str] = None,
    flags: SliderFlags = 0,
) -> bool:
    pass

# Widgets: Input with Keyboard
# - If you want to use InputText() with std::string or any custom dynamic string type, see misc/cpp/imgui_stdlib.h and comments in imgui_demo.cpp.
# - Most of the ImGuiInputTextFlags flags are only useful for InputText() and not for InputFloatX, InputIntX, InputDouble etc.
# IMGUI_API bool          InputFloat(const char* label, float* v, float step = 0.0f, float step_fast = 0.0f, const char* format = "%.3f", ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_float(
    label: str, v: float, step: float = 0.0, step_fast: float = 0.0, format: str = "%.3", flags: InputTextFlags = 0
) -> Tuple[bool, float]:
    pass

# IMGUI_API bool          InputFloat2(const char* label, float v[2], const char* format = "%.3f", ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_float2(
    label: str, v: List[float], format: str = "%.3", flags: InputTextFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          InputFloat3(const char* label, float v[3], const char* format = "%.3f", ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_float3(
    label: str, v: List[float], format: str = "%.3", flags: InputTextFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          InputFloat4(const char* label, float v[4], const char* format = "%.3f", ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_float4(
    label: str, v: List[float], format: str = "%.3", flags: InputTextFlags = 0
) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          InputInt(const char* label, int* v, int step = 1, int step_fast = 100, ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_int(label: str, v: int, step: int = 1, step_fast: int = 100, flags: InputTextFlags = 0) -> Tuple[bool, int]:
    pass

# IMGUI_API bool          InputInt2(const char* label, int v[2], ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_int2(label: str, v: List[int], flags: InputTextFlags = 0) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          InputInt3(const char* label, int v[3], ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_int3(label: str, v: List[int], flags: InputTextFlags = 0) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          InputInt4(const char* label, int v[4], ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_int4(label: str, v: List[int], flags: InputTextFlags = 0) -> Tuple[bool, List[int]]:
    pass

# IMGUI_API bool          InputDouble(const char* label, double* v, double step = 0.0, double step_fast = 0.0, const char* format = "%.6f", ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_double(
    label: str, v: float, step: float = 0.0, step_fast: float = 0.0, format: str = "%.6", flags: InputTextFlags = 0
) -> Tuple[bool, float]:
    pass

# IMGUI_API bool          InputScalar(const char* label, ImGuiDataType data_type, void* p_data, const void* p_step = NULL, const void* p_step_fast = NULL, const char* format = NULL, ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_scalar(
    label: str,
    data_type: DataType,
    p_data: Any,
    p_step: Optional[Any] = None,
    p_step_fast: Optional[Any] = None,
    format: Optional[str] = None,
    flags: InputTextFlags = 0,
) -> bool:
    pass

# IMGUI_API bool          InputScalarN(const char* label, ImGuiDataType data_type, void* p_data, int components, const void* p_step = NULL, const void* p_step_fast = NULL, const char* format = NULL, ImGuiInputTextFlags flags = 0);    /* original C++ signature */
def input_scalar_n(
    label: str,
    data_type: DataType,
    p_data: Any,
    components: int,
    p_step: Optional[Any] = None,
    p_step_fast: Optional[Any] = None,
    format: Optional[str] = None,
    flags: InputTextFlags = 0,
) -> bool:
    pass

# Widgets: Color Editor/Picker (tip: the ColorEdit* functions have a little color square that can be left-clicked to open a picker, and right-clicked to open an option menu.)
# - Note that in C++ a 'float v[X]' function argument is the _same_ as 'float* v', the array syntax is just a way to document the number of elements that are expected to be accessible.
# - You can pass the address of a first float element out of a contiguous structure, e.g. &myvector.x
# IMGUI_API bool          ColorEdit3(const char* label, float col[3], ImGuiColorEditFlags flags = 0);    /* original C++ signature */
def color_edit3(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          ColorEdit4(const char* label, float col[4], ImGuiColorEditFlags flags = 0);    /* original C++ signature */
def color_edit4(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
    pass

# IMGUI_API bool          ColorPicker3(const char* label, float col[3], ImGuiColorEditFlags flags = 0);    /* original C++ signature */
def color_picker3(label: str, col: List[float], flags: ColorEditFlags = 0) -> Tuple[bool, List[float]]:
    pass

# #ifdef IMGUI_BUNDLE_PYTHON_API
#
# IMGUI_API std::tuple<bool, ImVec4> ColorPicker4(const std::string& label, ImVec4 col, ImGuiColorEditFlags flags = 0, std::optional<ImVec4> ref_col = std::nullopt);    /* original C++ signature */
def color_picker4(
    label: str, col: ImVec4Like, flags: ColorEditFlags = 0, ref_col: Optional[ImVec4Like] = None
) -> Tuple[bool, ImVec4]:
    pass

# #endif
#

# IMGUI_API bool          ColorButton(const char* desc_id, const ImVec4& col, ImGuiColorEditFlags flags = 0, const ImVec2& size = ImVec2(0, 0));     /* original C++ signature */
def color_button(desc_id: str, col: ImVec4Like, flags: ColorEditFlags = 0, size: Optional[ImVec2Like] = None) -> bool:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)

     display a color square/button, hover for details, return True when pressed.
    """
    pass

# IMGUI_API void          SetColorEditOptions(ImGuiColorEditFlags flags);                         /* original C++ signature */
def set_color_edit_options(flags: ColorEditFlags) -> None:
    """initialize current options (generally on application startup) if you want to select a default format, picker type, etc. User will be able to change many settings, unless you pass the _NoOptions flag to your calls."""
    pass

# Widgets: Trees
# - TreeNode functions return True when the node is open, in which case you need to also call TreePop() when you are finished displaying the tree node contents.
# IMGUI_API bool          TreeNode(const char* label);    /* original C++ signature */
@overload
def tree_node(label: str) -> bool:
    pass

# IMGUI_API bool          TreeNode(const char* str_id, const char* fmt, ...) ;       /* original C++ signature */
@overload
def tree_node(str_id: str, fmt: str) -> bool:
    """helper variation to easily decorelate the id from the displayed string. Read the FAQ about why and how to use ID. to align arbitrary text at the same level as a TreeNode() you can use Bullet()."""
    pass

# IMGUI_API bool          TreeNode(const void* ptr_id, const char* fmt, ...) ;       /* original C++ signature */
@overload
def tree_node(ptr_id: Any, fmt: str) -> bool:
    """ " """
    pass

# IMGUI_API bool          TreeNodeEx(const char* label, ImGuiTreeNodeFlags flags = 0);    /* original C++ signature */
@overload
def tree_node_ex(label: str, flags: TreeNodeFlags = 0) -> bool:
    pass

# IMGUI_API bool          TreeNodeEx(const char* str_id, ImGuiTreeNodeFlags flags, const char* fmt, ...) ;    /* original C++ signature */
@overload
def tree_node_ex(str_id: str, flags: TreeNodeFlags, fmt: str) -> bool:
    pass

# IMGUI_API bool          TreeNodeEx(const void* ptr_id, ImGuiTreeNodeFlags flags, const char* fmt, ...) ;    /* original C++ signature */
@overload
def tree_node_ex(ptr_id: Any, flags: TreeNodeFlags, fmt: str) -> bool:
    pass

# IMGUI_API void          TreePush(const char* str_id);                                           /* original C++ signature */
@overload
def tree_push(str_id: str) -> None:
    """~ Indent()+PushID(). Already called by TreeNode() when returning True, but you can call TreePush/TreePop yourself if desired."""
    pass

# IMGUI_API void          TreePush(const void* ptr_id);                                           /* original C++ signature */
@overload
def tree_push(ptr_id: Any) -> None:
    """ " """
    pass

# IMGUI_API void          TreePop();                                                              /* original C++ signature */
def tree_pop() -> None:
    """~ Unindent()+PopID()"""
    pass

# IMGUI_API float         GetTreeNodeToLabelSpacing();                                            /* original C++ signature */
def get_tree_node_to_label_spacing() -> float:
    """horizontal distance preceding label when using TreeNode*() or Bullet() == (g.FontSize + style.FramePadding.x*2) for a regular unframed TreeNode"""
    pass

# IMGUI_API bool          CollapsingHeader(const char* label, ImGuiTreeNodeFlags flags = 0);      /* original C++ signature */
@overload
def collapsing_header(label: str, flags: TreeNodeFlags = 0) -> bool:
    """if returning 'True' the header is open. doesn't indent nor push on ID stack. user doesn't have to call TreePop()."""
    pass

# IMGUI_API bool          CollapsingHeader(const char* label, bool* p_visible, ImGuiTreeNodeFlags flags = 0);     /* original C++ signature */
@overload
def collapsing_header(label: str, p_visible: bool, flags: TreeNodeFlags = 0) -> Tuple[bool, bool]:
    """when 'p_visible != None': if '*p_visible==True' display an additional small close button on upper right of the header which will set the bool to False when clicked, if '*p_visible==False' don't display the header."""
    pass

# IMGUI_API void          SetNextItemOpen(bool is_open, ImGuiCond cond = 0);                      /* original C++ signature */
def set_next_item_open(is_open: bool, cond: Cond = 0) -> None:
    """set next TreeNode/CollapsingHeader open state."""
    pass

# IMGUI_API void          SetNextItemStorageID(ImGuiID storage_id);                               /* original C++ signature */
def set_next_item_storage_id(storage_id: ID) -> None:
    pass

# set id to use for open/close storage (default to same as item id).

# [ADAPT_IMGUI_BUNDLE]
# Widgets: Selectables
# - A selectable highlights when hovered, and can display another color when selected.
# - Neighbors selectable extend their highlight bounds in order to leave no gap between them. This is so a series of selected Selectable appear contiguous.
# IMGUI_API bool          Selectable(const char* label, bool* p_selected, ImGuiSelectableFlags flags = 0, const ImVec2& size = ImVec2(0, 0));          /* original C++ signature */
def selectable(
    label: str, p_selected: bool, flags: SelectableFlags = 0, size: Optional[ImVec2Like] = None
) -> Tuple[bool, bool]:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)

     "bool* p_selected" point to the selection state (read-write), as a convenient helper.
    """
    pass

# [/ADAPT_IMGUI_BUNDLE]

# Multi-selection system for Selectable(), Checkbox(), TreeNode() functions [BETA]
# - This enables standard multi-selection/range-selection idioms (CTRL+Mouse/Keyboard, SHIFT+Mouse/Keyboard, etc.) in a way that also allow a clipper to be used.
# - ImGuiSelectionUserData is often used to store your item index within the current view (but may store something else).
# - Read comments near ImGuiMultiSelectIO for instructions/details and see 'Demo->Widgets->Selection State & Multi-Select' for demo.
# - TreeNode() is technically supported but... using this correctly is more complicated. You need some sort of linear/random access to your tree,
#   which is suited to advanced trees setups already implementing filters and clipper. We will work simplifying the current demo.
# - 'selection_size' and 'items_count' parameters are optional and used by a few features. If they are costly for you to compute, you may avoid them.
# IMGUI_API ImGuiMultiSelectIO*   BeginMultiSelect(ImGuiMultiSelectFlags flags, int selection_size = -1, int items_count = -1);    /* original C++ signature */
def begin_multi_select(flags: MultiSelectFlags, selection_size: int = -1, items_count: int = -1) -> MultiSelectIO:
    pass

# IMGUI_API ImGuiMultiSelectIO*   EndMultiSelect();    /* original C++ signature */
def end_multi_select() -> MultiSelectIO:
    pass

# IMGUI_API void                  SetNextItemSelectionUserData(ImGuiSelectionUserData selection_user_data);    /* original C++ signature */
def set_next_item_selection_user_data(selection_user_data: SelectionUserData) -> None:
    pass

# IMGUI_API bool                  IsItemToggledSelection();                                       /* original C++ signature */
def is_item_toggled_selection() -> bool:
    """Was the last item selection state toggled? Useful if you need the per-item information _before_ reaching EndMultiSelect(). We only returns toggle _event_ in order to handle clipping correctly."""
    pass

# Widgets: List Boxes
# - This is essentially a thin wrapper to using BeginChild/EndChild with the ImGuiChildFlags_FrameStyle flag for stylistic changes + displaying a label.
# - If you don't need a label you can probably simply use BeginChild() with the ImGuiChildFlags_FrameStyle flag for the same result.
# - You can submit contents and manage your selection state however you want it, by creating e.g. Selectable() or any other items.
# - The simplified/old ListBox() api are helpers over BeginListBox()/EndListBox() which are kept available for convenience purpose. This is analoguous to how Combos are created.
# - Choose frame width:   size.x > 0.0: custom  /  size.x < 0.0 or -FLT_MIN: right-align   /  size.x = 0.0 (default): use current ItemWidth
# - Choose frame height:  size.y > 0.0: custom  /  size.y < 0.0 or -FLT_MIN: bottom-align  /  size.y = 0.0 (default): arbitrary default height which can fit ~7 items
# IMGUI_API bool          BeginListBox(const char* label, const ImVec2& size = ImVec2(0, 0));     /* original C++ signature */
def begin_list_box(label: str, size: Optional[ImVec2Like] = None) -> bool:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)

     open a framed scrolling region
    """
    pass

# IMGUI_API void          EndListBox();                                                           /* original C++ signature */
def end_list_box() -> None:
    """only call EndListBox() if BeginListBox() returned True!"""
    pass

# IMGUI_API bool          ListBox(const char* label, int* current_item, const char* const items[], int items_count, int height_in_items = -1);    /* original C++ signature */
def list_box(label: str, current_item: int, items: List[str], height_in_items: int = -1) -> Tuple[bool, int]:
    pass

# Widgets: Data Plotting
# - Consider using ImPlot (https://github.com/epezent/implot) which is much better!
# IMGUI_API void          PlotLines(const char* label, const float* values, int values_count, int values_offset = 0, const char* overlay_text = NULL, float scale_min = FLT_MAX, float scale_max = FLT_MAX, ImVec2 graph_size = ImVec2(0, 0), int stride = sizeof(float));    /* original C++ signature */
def plot_lines(
    label: str,
    values: np.ndarray,
    values_offset: int = 0,
    overlay_text: Optional[str] = None,
    scale_min: float = sys.float_info.max,
    scale_max: float = sys.float_info.max,
    graph_size: Optional[ImVec2Like] = None,
    stride: int = -1,
) -> None:
    """---
    Python bindings defaults:
        If graph_size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void          PlotHistogram(const char* label, const float* values, int values_count, int values_offset = 0, const char* overlay_text = NULL, float scale_min = FLT_MAX, float scale_max = FLT_MAX, ImVec2 graph_size = ImVec2(0, 0), int stride = sizeof(float));    /* original C++ signature */
def plot_histogram(
    label: str,
    values: np.ndarray,
    values_offset: int = 0,
    overlay_text: Optional[str] = None,
    scale_min: float = sys.float_info.max,
    scale_max: float = sys.float_info.max,
    graph_size: Optional[ImVec2Like] = None,
    stride: int = -1,
) -> None:
    """---
    Python bindings defaults:
        If graph_size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# Widgets: Value() Helpers.
# - Those are merely shortcut to calling Text() with a format string. Output single value in "name: value" format (tip: freely declare more in your code to handle your types. you can add functions to the ImGui namespace)
# IMGUI_API void          Value(const char* prefix, bool b);    /* original C++ signature */
@overload
def value(prefix: str, b: bool) -> None:
    pass

# IMGUI_API void          Value(const char* prefix, int v);    /* original C++ signature */
@overload
def value(prefix: str, v: int) -> None:
    pass

# IMGUI_API void          Value(const char* prefix, unsigned int v);    /* original C++ signature */
@overload
def value(prefix: str, v: int) -> None:
    pass

# IMGUI_API void          Value(const char* prefix, float v, const char* float_format = NULL);    /* original C++ signature */
@overload
def value(prefix: str, v: float, float_format: Optional[str] = None) -> None:
    pass

# Widgets: Menus
# - Use BeginMenuBar() on a window ImGuiWindowFlags_MenuBar to append to its menu bar.
# - Use BeginMainMenuBar() to create a menu bar at the top of the screen and append to it.
# - Use BeginMenu() to create a menu. You can call BeginMenu() multiple time with the same identifier to append more items to it.
# - Not that MenuItem() keyboardshortcuts are displayed as a convenience but _not processed_ by Dear ImGui at the moment.
# IMGUI_API bool          BeginMenuBar();                                                         /* original C++ signature */
def begin_menu_bar() -> bool:
    """append to menu-bar of current window (requires ImGuiWindowFlags_MenuBar flag set on parent window)."""
    pass

# IMGUI_API void          EndMenuBar();                                                           /* original C++ signature */
def end_menu_bar() -> None:
    """only call EndMenuBar() if BeginMenuBar() returns True!"""
    pass

# IMGUI_API bool          BeginMainMenuBar();                                                     /* original C++ signature */
def begin_main_menu_bar() -> bool:
    """create and append to a full screen menu-bar."""
    pass

# IMGUI_API void          EndMainMenuBar();                                                       /* original C++ signature */
def end_main_menu_bar() -> None:
    """only call EndMainMenuBar() if BeginMainMenuBar() returns True!"""
    pass

# IMGUI_API bool          BeginMenu(const char* label, bool enabled = true);                      /* original C++ signature */
def begin_menu(label: str, enabled: bool = True) -> bool:
    """create a sub-menu entry. only call EndMenu() if this returns True!"""
    pass

# [ADAPT_IMGUI_BUNDLE]

# IMGUI_API void          EndMenu();    /* original C++ signature */
def end_menu() -> None:
    """only call EndMenu() if BeginMenu() returns True!"""
    pass

# #ifdef IMGUI_BUNDLE_PYTHON_API
#
# inline bool          MenuItemSimple(const char* label, const char* shortcut = NULL, bool selected = false, bool enabled = true) { return MenuItem(label, shortcut, selected, enabled); }    /* original C++ signature */
def menu_item_simple(label: str, shortcut: Optional[str] = None, selected: bool = False, enabled: bool = True) -> bool:
    """(private API)"""
    pass

# #endif
#
# IMGUI_API bool          MenuItem(const char* label, const char* shortcut, bool* p_selected, bool enabled = true);                  /* original C++ signature */
def menu_item(label: str, shortcut: str, p_selected: bool, enabled: bool = True) -> Tuple[bool, bool]:
    """return True when activated + toggle (*p_selected) if p_selected != None"""
    pass

# [/ADAPT_IMGUI_BUNDLE]

# Tooltips
# - Tooltips are windows following the mouse. They do not take focus away.
# - A tooltip window can contain items of any types.
# - SetTooltip() is more or less a shortcut for the 'if (BeginTooltip()) { Text(...); EndTooltip(); }' idiom (with a subtlety that it discard any previously submitted tooltip)
# IMGUI_API bool          BeginTooltip();                                                         /* original C++ signature */
def begin_tooltip() -> bool:
    """begin/append a tooltip window."""
    pass

# IMGUI_API void          EndTooltip();                                                           /* original C++ signature */
def end_tooltip() -> None:
    """only call EndTooltip() if BeginTooltip()/BeginItemTooltip() returns True!"""
    pass

# IMGUI_API void          SetTooltip(const char* fmt, ...) ;                         /* original C++ signature */
def set_tooltip(fmt: str) -> None:
    """set a text-only tooltip. Often used after a ImGui::IsItemHovered() check. Override any previous call to SetTooltip()."""
    pass

# Tooltips: helpers for showing a tooltip when hovering an item
# - BeginItemTooltip() is a shortcut for the 'if (IsItemHovered(ImGuiHoveredFlags_ForTooltip) && BeginTooltip())' idiom.
# - SetItemTooltip() is a shortcut for the 'if (IsItemHovered(ImGuiHoveredFlags_ForTooltip)) { SetTooltip(...); }' idiom.
# - Where 'ImGuiHoveredFlags_ForTooltip' itself is a shortcut to use 'style.HoverFlagsForTooltipMouse' or 'style.HoverFlagsForTooltipNav' depending on active input type. For mouse it defaults to 'ImGuiHoveredFlags_Stationary | ImGuiHoveredFlags_DelayShort'.
# IMGUI_API bool          BeginItemTooltip();                                                     /* original C++ signature */
def begin_item_tooltip() -> bool:
    """begin/append a tooltip window if preceding item was hovered."""
    pass

# IMGUI_API void          SetItemTooltip(const char* fmt, ...) ;                     /* original C++ signature */
def set_item_tooltip(fmt: str) -> None:
    """set a text-only tooltip if preceding item was hovered. override any previous call to SetTooltip()."""
    pass

# Popups, Modals
#  - They block normal mouse hovering detection (and therefore most mouse interactions) behind them.
#  - If not modal: they can be closed by clicking anywhere outside them, or by pressing ESCAPE.
#  - Their visibility state (~bool) is held internally instead of being held by the programmer as we are used to with regular Begin*() calls.
#  - The 3 properties above are related: we need to retain popup visibility state in the library because popups may be closed as any time.
#  - You can bypass the hovering restriction by using ImGuiHoveredFlags_AllowWhenBlockedByPopup when calling IsItemHovered() or IsWindowHovered().
#  - IMPORTANT: Popup identifiers are relative to the current ID stack, so OpenPopup and BeginPopup generally needs to be at the same level of the stack.
#    This is sometimes leading to confusing mistakes. May rework this in the future.
#  - BeginPopup(): query popup state, if open start appending into the window. Call EndPopup() afterwards if returned True. ImGuiWindowFlags are forwarded to the window.
#  - BeginPopupModal(): block every interaction behind the window, cannot be closed by user, add a dimming background, has a title bar.
# IMGUI_API bool          BeginPopup(const char* str_id, ImGuiWindowFlags flags = 0);                             /* original C++ signature */
def begin_popup(str_id: str, flags: WindowFlags = 0) -> bool:
    """return True if the popup is open, and you can start outputting to it."""
    pass

# IMGUI_API bool          BeginPopupModal(const char* name, bool* p_open = NULL, ImGuiWindowFlags flags = 0);     /* original C++ signature */
def begin_popup_modal(name: str, p_open: Optional[bool] = None, flags: WindowFlags = 0) -> Tuple[bool, Optional[bool]]:
    """return True if the modal is open, and you can start outputting to it."""
    pass

# IMGUI_API void          EndPopup();                                                                             /* original C++ signature */
def end_popup() -> None:
    """only call EndPopup() if BeginPopupXXX() returns True!"""
    pass

# Popups: open/close functions
#  - OpenPopup(): set popup state to open. ImGuiPopupFlags are available for opening options.
#  - If not modal: they can be closed by clicking anywhere outside them, or by pressing ESCAPE.
#  - CloseCurrentPopup(): use inside the BeginPopup()/EndPopup() scope to close manually.
#  - CloseCurrentPopup() is called by default by Selectable()/MenuItem() when activated (FIXME: need some options).
#  - Use ImGuiPopupFlags_NoOpenOverExistingPopup to avoid opening a popup if there's already one at the same level. This is equivalent to e.g. testing for !IsAnyPopupOpen() prior to OpenPopup().
#  - Use IsWindowAppearing() after BeginPopup() to tell if a window just opened.
#  - IMPORTANT: Notice that for OpenPopupOnItemClick() we exceptionally default flags to 1 (== ImGuiPopupFlags_MouseButtonRight) for backward compatibility with older API taking 'int mouse_button = 1' parameter
# IMGUI_API void          OpenPopup(const char* str_id, ImGuiPopupFlags popup_flags = 0);                         /* original C++ signature */
@overload
def open_popup(str_id: str, popup_flags: PopupFlags = 0) -> None:
    """call to mark popup as open (don't call every frame!)."""
    pass

# IMGUI_API void          OpenPopup(ImGuiID id, ImGuiPopupFlags popup_flags = 0);                                 /* original C++ signature */
@overload
def open_popup(id_: ID, popup_flags: PopupFlags = 0) -> None:
    """id overload to facilitate calling from nested stacks"""
    pass

# IMGUI_API void          OpenPopupOnItemClick(const char* str_id = NULL, ImGuiPopupFlags popup_flags = 1);       /* original C++ signature */
def open_popup_on_item_click(str_id: Optional[str] = None, popup_flags: PopupFlags = 1) -> None:
    """helper to open popup when clicked on last item. Default to ImGuiPopupFlags_MouseButtonRight == 1. (note: actually triggers on the mouse _released_ event to be consistent with popup behaviors)"""
    pass

# IMGUI_API void          CloseCurrentPopup();                                                                    /* original C++ signature */
def close_current_popup() -> None:
    """manually close the popup we have begin-ed into."""
    pass

# Popups: open+begin combined functions helpers
#  - Helpers to do OpenPopup+BeginPopup where the Open action is triggered by e.g. hovering an item and right-clicking.
#  - They are convenient to easily create context menus, hence the name.
#  - IMPORTANT: Notice that BeginPopupContextXXX takes ImGuiPopupFlags just like OpenPopup() and unlike BeginPopup(). For full consistency, we may add ImGuiWindowFlags to the BeginPopupContextXXX functions in the future.
#  - IMPORTANT: Notice that we exceptionally default their flags to 1 (== ImGuiPopupFlags_MouseButtonRight) for backward compatibility with older API taking 'int mouse_button = 1' parameter, so if you add other flags remember to re-add the ImGuiPopupFlags_MouseButtonRight.
# IMGUI_API bool          BeginPopupContextItem(const char* str_id = NULL, ImGuiPopupFlags popup_flags = 1);      /* original C++ signature */
def begin_popup_context_item(str_id: Optional[str] = None, popup_flags: PopupFlags = 1) -> bool:
    """open+begin popup when clicked on last item. Use str_id==None to associate the popup to previous item. If you want to use that on a non-interactive item such as Text() you need to pass in an explicit ID here. read comments in .cpp!"""
    pass

# IMGUI_API bool          BeginPopupContextWindow(const char* str_id = NULL, ImGuiPopupFlags popup_flags = 1);    /* original C++ signature */
def begin_popup_context_window(str_id: Optional[str] = None, popup_flags: PopupFlags = 1) -> bool:
    """open+begin popup when clicked on current window."""
    pass

# IMGUI_API bool          BeginPopupContextVoid(const char* str_id = NULL, ImGuiPopupFlags popup_flags = 1);      /* original C++ signature */
def begin_popup_context_void(str_id: Optional[str] = None, popup_flags: PopupFlags = 1) -> bool:
    """open+begin popup when clicked in None (where there are no windows)."""
    pass

# Popups: query functions
#  - IsPopupOpen(): return True if the popup is open at the current BeginPopup() level of the popup stack.
#  - IsPopupOpen() with ImGuiPopupFlags_AnyPopupId: return True if any popup is open at the current BeginPopup() level of the popup stack.
#  - IsPopupOpen() with ImGuiPopupFlags_AnyPopupId + ImGuiPopupFlags_AnyPopupLevel: return True if any popup is open.
# IMGUI_API bool          IsPopupOpen(const char* str_id, ImGuiPopupFlags flags = 0);                             /* original C++ signature */
def is_popup_open(str_id: str, flags: PopupFlags = 0) -> bool:
    """return True if the popup is open."""
    pass

# Tables
# - Full-featured replacement for old Columns API.
# - See Demo->Tables for demo code. See top of imgui_tables.cpp for general commentary.
# - See ImGuiTableFlags_ and ImGuiTableColumnFlags_ enums for a description of available flags.
# The typical call flow is:
# - 1. Call BeginTable(), early out if returning False.
# - 2. Optionally call TableSetupColumn() to submit column name/flags/defaults.
# - 3. Optionally call TableSetupScrollFreeze() to request scroll freezing of columns/rows.
# - 4. Optionally call TableHeadersRow() to submit a header row. Names are pulled from TableSetupColumn() data.
# - 5. Populate contents:
#    - In most situations you can use TableNextRow() + TableSetColumnIndex(N) to start appending into a column.
#    - If you are using tables as a sort of grid, where every column is holding the same type of contents,
#      you may prefer using TableNextColumn() instead of TableNextRow() + TableSetColumnIndex().
#      TableNextColumn() will automatically wrap-around into the next row if needed.
#    - IMPORTANT: Comparatively to the old Columns() API, we need to call TableNextColumn() for the first column!
#    - Summary of possible call flow:
#        - TableNextRow() -> TableSetColumnIndex(0) -> Text("Hello 0") -> TableSetColumnIndex(1) -> Text("Hello 1")  // OK
#        - TableNextRow() -> TableNextColumn()      -> Text("Hello 0") -> TableNextColumn()      -> Text("Hello 1")  // OK
#        -                   TableNextColumn()      -> Text("Hello 0") -> TableNextColumn()      -> Text("Hello 1")  // OK: TableNextColumn() automatically gets to next row!
#        - TableNextRow()                           -> Text("Hello 0")                                               // Not OK! Missing TableSetColumnIndex() or TableNextColumn()! Text will not appear!
# - 5. Call EndTable()
# IMGUI_API bool          BeginTable(const char* str_id, int columns, ImGuiTableFlags flags = 0, const ImVec2& outer_size = ImVec2(0.0f, 0.0f), float inner_width = 0.0f);    /* original C++ signature */
def begin_table(
    str_id: str, columns: int, flags: TableFlags = 0, outer_size: Optional[ImVec2Like] = None, inner_width: float = 0.0
) -> bool:
    """---
    Python bindings defaults:
        If outer_size is None, then its default value will be: ImVec2(0.0, 0.0)
    """
    pass

# IMGUI_API void          EndTable();                                             /* original C++ signature */
def end_table() -> None:
    """only call EndTable() if BeginTable() returns True!"""
    pass

# IMGUI_API void          TableNextRow(ImGuiTableRowFlags row_flags = 0, float min_row_height = 0.0f);     /* original C++ signature */
def table_next_row(row_flags: TableRowFlags = 0, min_row_height: float = 0.0) -> None:
    """append into the first cell of a new row."""
    pass

# IMGUI_API bool          TableNextColumn();                                      /* original C++ signature */
def table_next_column() -> bool:
    """append into the next column (or first column of next row if currently in last column). Return True when column is visible."""
    pass

# IMGUI_API bool          TableSetColumnIndex(int column_n);                      /* original C++ signature */
def table_set_column_index(column_n: int) -> bool:
    """append into the specified column. Return True when column is visible."""
    pass

# Tables: Headers & Columns declaration
# - Use TableSetupColumn() to specify label, resizing policy, default width/weight, id, various other flags etc.
# - Use TableHeadersRow() to create a header row and automatically submit a TableHeader() for each column.
#   Headers are required to perform: reordering, sorting, and opening the context menu.
#   The context menu can also be made available in columns body using ImGuiTableFlags_ContextMenuInBody.
# - You may manually submit headers using TableNextRow() + TableHeader() calls, but this is only useful in
#   some advanced use cases (e.g. adding custom widgets in header row).
# - Use TableSetupScrollFreeze() to lock columns/rows so they stay visible when scrolled.
# IMGUI_API void          TableSetupColumn(const char* label, ImGuiTableColumnFlags flags = 0, float init_width_or_weight = 0.0f, ImGuiID user_id = 0);    /* original C++ signature */
def table_setup_column(
    label: str, flags: TableColumnFlags = 0, init_width_or_weight: float = 0.0, user_id: ID = 0
) -> None:
    pass

# IMGUI_API void          TableSetupScrollFreeze(int cols, int rows);             /* original C++ signature */
def table_setup_scroll_freeze(cols: int, rows: int) -> None:
    """lock columns/rows so they stay visible when scrolled."""
    pass

# IMGUI_API void          TableHeader(const char* label);                         /* original C++ signature */
def table_header(label: str) -> None:
    """submit one header cell manually (rarely used)"""
    pass

# IMGUI_API void          TableHeadersRow();                                      /* original C++ signature */
def table_headers_row() -> None:
    """submit a row with headers cells based on data provided to TableSetupColumn() + submit context menu"""
    pass

# IMGUI_API void          TableAngledHeadersRow();                                /* original C++ signature */
def table_angled_headers_row() -> None:
    """submit a row with angled headers for every column with the ImGuiTableColumnFlags_AngledHeader flag. MUST BE FIRST ROW."""
    pass

# Tables: Sorting & Miscellaneous functions
# - Sorting: call TableGetSortSpecs() to retrieve latest sort specs for the table. None when not sorting.
#   When 'sort_specs->SpecsDirty == True' you should sort your data. It will be True when sorting specs have
#   changed since last call, or the first time. Make sure to set 'SpecsDirty = False' after sorting,
#   else you may wastefully sort your data every frame!
# - Functions args 'int column_n' treat the default value of -1 as the same as passing the current column index.
# IMGUI_API ImGuiTableSortSpecs*  TableGetSortSpecs();                            /* original C++ signature */
def table_get_sort_specs() -> TableSortSpecs:
    """get latest sort specs for the table (None if not sorting).  Lifetime: don't hold on this pointer over multiple frames or past any subsequent call to BeginTable()."""
    pass

# IMGUI_API int                   TableGetColumnCount();                          /* original C++ signature */
def table_get_column_count() -> int:
    """return number of columns (value passed to BeginTable)"""
    pass

# IMGUI_API int                   TableGetColumnIndex();                          /* original C++ signature */
def table_get_column_index() -> int:
    """return current column index."""
    pass

# IMGUI_API int                   TableGetRowIndex();                             /* original C++ signature */
def table_get_row_index() -> int:
    """return current row index."""
    pass

# IMGUI_API const char*           TableGetColumnName(int column_n = -1);          /* original C++ signature */
def table_get_column_name(column_n: int = -1) -> str:
    """return "" if column didn't have a name declared by TableSetupColumn(). Pass -1 to use current column."""
    pass

# IMGUI_API ImGuiTableColumnFlags TableGetColumnFlags(int column_n = -1);         /* original C++ signature */
def table_get_column_flags(column_n: int = -1) -> TableColumnFlags:
    """return column flags so you can query their Enabled/Visible/Sorted/Hovered status flags. Pass -1 to use current column."""
    pass

# IMGUI_API void                  TableSetColumnEnabled(int column_n, bool v);    /* original C++ signature */
def table_set_column_enabled(column_n: int, v: bool) -> None:
    """change user accessible enabled/disabled state of a column. Set to False to hide the column. User can use the context menu to change this themselves (right-click in headers, or right-click in columns body with ImGuiTableFlags_ContextMenuInBody)"""
    pass

# IMGUI_API int                   TableGetHoveredColumn();                        /* original C++ signature */
def table_get_hovered_column() -> int:
    """return hovered column. return -1 when table is not hovered. return columns_count if the unused space at the right of visible columns is hovered. Can also use (TableGetColumnFlags() & ImGuiTableColumnFlags_IsHovered) instead."""
    pass

# IMGUI_API void                  TableSetBgColor(ImGuiTableBgTarget target, ImU32 color, int column_n = -1);      /* original C++ signature */
def table_set_bg_color(target: TableBgTarget, color: ImU32, column_n: int = -1) -> None:
    """change the color of a cell, row, or column. See ImGuiTableBgTarget_ flags for details."""
    pass

# Legacy Columns API (prefer using Tables!)
# - You can also use SameLine(pos_x) to mimic simplified columns.
# IMGUI_API void          Columns(int count = 1, const char* id = NULL, bool borders = true);    /* original C++ signature */
def columns(count: int = 1, id_: Optional[str] = None, borders: bool = True) -> None:
    pass

# IMGUI_API void          NextColumn();                                                           /* original C++ signature */
def next_column() -> None:
    """next column, defaults to current row or next row if the current row is finished"""
    pass

# IMGUI_API int           GetColumnIndex();                                                       /* original C++ signature */
def get_column_index() -> int:
    """get current column index"""
    pass

# IMGUI_API float         GetColumnWidth(int column_index = -1);                                  /* original C++ signature */
def get_column_width(column_index: int = -1) -> float:
    """get column width (in pixels). pass -1 to use current column"""
    pass

# IMGUI_API void          SetColumnWidth(int column_index, float width);                          /* original C++ signature */
def set_column_width(column_index: int, width: float) -> None:
    """set column width (in pixels). pass -1 to use current column"""
    pass

# IMGUI_API float         GetColumnOffset(int column_index = -1);                                 /* original C++ signature */
def get_column_offset(column_index: int = -1) -> float:
    """get position of column line (in pixels, from the left side of the contents region). pass -1 to use current column, otherwise 0..GetColumnsCount() inclusive. column 0 is typically 0.0"""
    pass

# IMGUI_API void          SetColumnOffset(int column_index, float offset_x);                      /* original C++ signature */
def set_column_offset(column_index: int, offset_x: float) -> None:
    """set position of column line (in pixels, from the left side of the contents region). pass -1 to use current column"""
    pass

# IMGUI_API int           GetColumnsCount();    /* original C++ signature */
def get_columns_count() -> int:
    pass

# Tab Bars, Tabs
# - Note: Tabs are automatically created by the docking system (when in 'docking' branch). Use this to create tab bars/tabs yourself.
# IMGUI_API bool          BeginTabBar(const char* str_id, ImGuiTabBarFlags flags = 0);            /* original C++ signature */
def begin_tab_bar(str_id: str, flags: TabBarFlags = 0) -> bool:
    """create and append into a TabBar"""
    pass

# IMGUI_API void          EndTabBar();                                                            /* original C++ signature */
def end_tab_bar() -> None:
    """only call EndTabBar() if BeginTabBar() returns True!"""
    pass

# IMGUI_API bool          BeginTabItem(const char* label, bool* p_open = NULL, ImGuiTabItemFlags flags = 0);     /* original C++ signature */
def begin_tab_item(label: str, p_open: Optional[bool] = None, flags: TabItemFlags = 0) -> Tuple[bool, Optional[bool]]:
    pass

# create a Tab. Returns True if the Tab is selected.
# #ifdef IMGUI_BUNDLE_PYTHON_API
#
# IMGUI_API bool          BeginTabItemSimple(const char* label, ImGuiTabItemFlags flags = 0);     /* original C++ signature */
def begin_tab_item_simple(label: str, flags: TabItemFlags = 0) -> bool:
    pass

# create a Tab (non-closable). Returns True if the Tab is selected.
# #endif
#
# IMGUI_API void          EndTabItem();                                                           /* original C++ signature */
def end_tab_item() -> None:
    """only call EndTabItem() if BeginTabItem() returns True!"""
    pass

# IMGUI_API bool          TabItemButton(const char* label, ImGuiTabItemFlags flags = 0);          /* original C++ signature */
def tab_item_button(label: str, flags: TabItemFlags = 0) -> bool:
    """create a Tab behaving like a button. return True when clicked. cannot be selected in the tab bar."""
    pass

# IMGUI_API void          SetTabItemClosed(const char* tab_or_docked_window_label);               /* original C++ signature */
def set_tab_item_closed(tab_or_docked_window_label: str) -> None:
    """notify TabBar or Docking system of a closed tab/window ahead (useful to reduce visual flicker on reorderable tab bars). For tab-bar: call after BeginTabBar() and before Tab submissions. Otherwise call with a window name."""
    pass

# Docking
# [BETA API] Enable with io.ConfigFlags |= ImGuiConfigFlags_DockingEnable.
# Note: You can use most Docking facilities without calling any API. You DO NOT need to call DockSpace() to use Docking!
# - Drag from window title bar or their tab to dock/undock. Hold SHIFT to disable docking.
# - Drag from window menu button (upper-left button) to undock an entire node (all windows).
# - When io.ConfigDockingWithShift == True, you instead need to hold SHIFT to enable docking.
# About dockspaces:
# - Use DockSpaceOverViewport() to create a window covering the screen or a specific viewport + a dockspace inside it.
#   This is often used with ImGuiDockNodeFlags_PassthruCentralNode to make it transparent.
# - Use DockSpace() to create an explicit dock node _within_ an existing window. See Docking demo for details.
# - Important: Dockspaces need to be submitted _before_ any window they can host. Submit it early in your frame!
# - Important: Dockspaces need to be kept alive if hidden, otherwise windows docked into it will be undocked.
#   e.g. if you have multiple tabs with a dockspace inside each tab: submit the non-visible dockspaces with ImGuiDockNodeFlags_KeepAliveOnly.
# IMGUI_API ImGuiID       DockSpace(ImGuiID dockspace_id, const ImVec2& size = ImVec2(0, 0), ImGuiDockNodeFlags flags = 0, const ImGuiWindowClass* window_class = NULL);    /* original C++ signature */
def dock_space(
    dockspace_id: ID,
    size: Optional[ImVec2Like] = None,
    flags: DockNodeFlags = 0,
    window_class: Optional[WindowClass] = None,
) -> ID:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API ImGuiID       DockSpaceOverViewport(ImGuiID dockspace_id = 0, const ImGuiViewport* viewport = NULL, ImGuiDockNodeFlags flags = 0, const ImGuiWindowClass* window_class = NULL);    /* original C++ signature */
def dock_space_over_viewport(
    dockspace_id: ID = 0,
    viewport: Optional[Viewport] = None,
    flags: DockNodeFlags = 0,
    window_class: Optional[WindowClass] = None,
) -> ID:
    pass

# IMGUI_API void          SetNextWindowDockID(ImGuiID dock_id, ImGuiCond cond = 0);               /* original C++ signature */
def set_next_window_dock_id(dock_id: ID, cond: Cond = 0) -> None:
    """set next window dock id"""
    pass

# IMGUI_API void          SetNextWindowClass(const ImGuiWindowClass* window_class);               /* original C++ signature */
def set_next_window_class(window_class: WindowClass) -> None:
    """set next window class (control docking compatibility + provide hints to platform backend via custom viewport flags and platform parent/child relationship)"""
    pass

# IMGUI_API ImGuiID       GetWindowDockID();    /* original C++ signature */
def get_window_dock_id() -> ID:
    pass

# IMGUI_API bool          IsWindowDocked();                                                       /* original C++ signature */
def is_window_docked() -> bool:
    """is current window docked into another window?"""
    pass

# Logging/Capture
# - All text output from the interface can be captured into tty/file/clipboard. By default, tree nodes are automatically opened during logging.
# IMGUI_API void          LogToTTY(int auto_open_depth = -1);                                     /* original C++ signature */
def log_to_tty(auto_open_depth: int = -1) -> None:
    """start logging to tty (stdout)"""
    pass

# IMGUI_API void          LogToFile(int auto_open_depth = -1, const char* filename = NULL);       /* original C++ signature */
def log_to_file(auto_open_depth: int = -1, filename: Optional[str] = None) -> None:
    """start logging to file"""
    pass

# IMGUI_API void          LogToClipboard(int auto_open_depth = -1);                               /* original C++ signature */
def log_to_clipboard(auto_open_depth: int = -1) -> None:
    """start logging to OS clipboard"""
    pass

# IMGUI_API void          LogFinish();                                                            /* original C++ signature */
def log_finish() -> None:
    """stop logging (close file, etc.)"""
    pass

# IMGUI_API void          LogButtons();                                                           /* original C++ signature */
def log_buttons() -> None:
    """helper to display buttons for logging to tty/file/clipboard"""
    pass

# IMGUI_API void          LogText(const char* fmt, ...) ;                            /* original C++ signature */
def log_text(fmt: str) -> None:
    """pass text data straight to log (without being displayed)"""
    pass

# Drag and Drop
# - On source items, call BeginDragDropSource(), if it returns True also call SetDragDropPayload() + EndDragDropSource().
# - On target candidates, call BeginDragDropTarget(), if it returns True also call AcceptDragDropPayload() + EndDragDropTarget().
# - If you stop calling BeginDragDropSource() the payload is preserved however it won't have a preview tooltip (we currently display a fallback "..." tooltip, see #1725)
# - An item can be both drag source and drop target.
# IMGUI_API bool          BeginDragDropSource(ImGuiDragDropFlags flags = 0);                                          /* original C++ signature */
def begin_drag_drop_source(flags: DragDropFlags = 0) -> bool:
    """call after submitting an item which may be dragged. when this return True, you can call SetDragDropPayload() + EndDragDropSource()"""
    pass

# IMGUI_API bool          SetDragDropPayload(const char* type, const void* data, size_t sz, ImGuiCond cond = 0);      /* original C++ signature */
def set_drag_drop_payload(type: str, data: Any, sz: int, cond: Cond = 0) -> bool:
    """type is a user defined string of maximum 32 characters. Strings starting with '_' are reserved for dear imgui internal types. Data is copied and held by imgui. Return True when payload has been accepted."""
    pass

# IMGUI_API void          EndDragDropSource();                                                                        /* original C++ signature */
def end_drag_drop_source() -> None:
    """only call EndDragDropSource() if BeginDragDropSource() returns True!"""
    pass

# IMGUI_API bool                  BeginDragDropTarget();                                                              /* original C++ signature */
def begin_drag_drop_target() -> bool:
    """call after submitting an item that may receive a payload. If this returns True, you can call AcceptDragDropPayload() + EndDragDropTarget()"""
    pass

# IMGUI_API void                  EndDragDropTarget();                                                                /* original C++ signature */
def end_drag_drop_target() -> None:
    """only call EndDragDropTarget() if BeginDragDropTarget() returns True!"""
    pass

# Disabling [BETA API]
# - Disable all user interactions and dim items visuals (applying style.DisabledAlpha over current colors)
# - Those can be nested but it cannot be used to enable an already disabled section (a single BeginDisabled(True) in the stack is enough to keep everything disabled)
# - Tooltips windows by exception are opted out of disabling.
# - BeginDisabled(False)/EndDisabled() essentially does nothing but is provided to facilitate use of boolean expressions (as a micro-optimization: if you have tens of thousands of BeginDisabled(False)/EndDisabled() pairs, you might want to reformulate your code to avoid making those calls)
# IMGUI_API void          BeginDisabled(bool disabled = true);    /* original C++ signature */
def begin_disabled(disabled: bool = True) -> None:
    pass

# IMGUI_API void          EndDisabled();    /* original C++ signature */
def end_disabled() -> None:
    pass

# Clipping
# - Mouse hovering is affected by ImGui::PushClipRect() calls, unlike direct calls to ImDrawList::PushClipRect() which are render only.
# IMGUI_API void          PushClipRect(const ImVec2& clip_rect_min, const ImVec2& clip_rect_max, bool intersect_with_current_clip_rect);    /* original C++ signature */
def push_clip_rect(
    clip_rect_min: ImVec2Like, clip_rect_max: ImVec2Like, intersect_with_current_clip_rect: bool
) -> None:
    pass

# IMGUI_API void          PopClipRect();    /* original C++ signature */
def pop_clip_rect() -> None:
    pass

# Focus, Activation
# IMGUI_API void          SetItemDefaultFocus();                                                  /* original C++ signature */
def set_item_default_focus() -> None:
    """make last item the default focused item of of a newly appearing window."""
    pass

# IMGUI_API void          SetKeyboardFocusHere(int offset = 0);                                   /* original C++ signature */
def set_keyboard_focus_here(offset: int = 0) -> None:
    """focus keyboard on the next widget. Use positive 'offset' to access sub components of a multiple component widget. Use -1 to access previous widget."""
    pass

# Keyboard/Gamepad Navigation
# IMGUI_API void          SetNavCursorVisible(bool visible);                                      /* original C++ signature */
def set_nav_cursor_visible(visible: bool) -> None:
    """alter visibility of keyboard/gamepad cursor. by default: show when using an arrow key, hide when clicking with mouse."""
    pass

# Overlapping mode
# IMGUI_API void          SetNextItemAllowOverlap();                                              /* original C++ signature */
def set_next_item_allow_overlap() -> None:
    """allow next item to be overlapped by a subsequent item. Useful with invisible buttons, selectable, treenode covering an area where subsequent items may need to be added. Note that both Selectable() and TreeNode() have dedicated flags doing this."""
    pass

# Item/Widgets Utilities and Query Functions
# - Most of the functions are referring to the previous Item that has been submitted.
# - See Demo Window under "Widgets->Querying Status" for an interactive visualization of most of those functions.
# IMGUI_API bool          IsItemHovered(ImGuiHoveredFlags flags = 0);                             /* original C++ signature */
def is_item_hovered(flags: HoveredFlags = 0) -> bool:
    """is the last item hovered? (and usable, aka not blocked by a popup, etc.). See ImGuiHoveredFlags for more options."""
    pass

# IMGUI_API bool          IsItemActive();                                                         /* original C++ signature */
def is_item_active() -> bool:
    """is the last item active? (e.g. button being held, text field being edited. This will continuously return True while holding mouse button on an item. Items that don't interact will always return False)"""
    pass

# IMGUI_API bool          IsItemFocused();                                                        /* original C++ signature */
def is_item_focused() -> bool:
    """is the last item focused for keyboard/gamepad navigation?"""
    pass

# IMGUI_API bool          IsItemClicked(ImGuiMouseButton mouse_button = 0);                       /* original C++ signature */
def is_item_clicked(mouse_button: MouseButton = 0) -> bool:
    """is the last item hovered and mouse clicked on? (**)  == IsMouseClicked(mouse_button) && IsItemHovered()Important. (**) this is NOT equivalent to the behavior of e.g. Button(). Read comments in function definition."""
    pass

# IMGUI_API bool          IsItemVisible();                                                        /* original C++ signature */
def is_item_visible() -> bool:
    """is the last item visible? (items may be out of sight because of clipping/scrolling)"""
    pass

# IMGUI_API bool          IsItemEdited();                                                         /* original C++ signature */
def is_item_edited() -> bool:
    """did the last item modify its underlying value this frame? or was pressed? This is generally the same as the "bool" return value of many widgets."""
    pass

# IMGUI_API bool          IsItemActivated();                                                      /* original C++ signature */
def is_item_activated() -> bool:
    """was the last item just made active (item was previously inactive)."""
    pass

# IMGUI_API bool          IsItemDeactivated();                                                    /* original C++ signature */
def is_item_deactivated() -> bool:
    """was the last item just made inactive (item was previously active). Useful for Undo/Redo patterns with widgets that require continuous editing."""
    pass

# IMGUI_API bool          IsItemDeactivatedAfterEdit();                                           /* original C++ signature */
def is_item_deactivated_after_edit() -> bool:
    """was the last item just made inactive and made a value change when it was active? (e.g. Slider/Drag moved). Useful for Undo/Redo patterns with widgets that require continuous editing. Note that you may get False positives (some widgets such as Combo()/ListBox()/Selectable() will return True even when clicking an already selected item)."""
    pass

# IMGUI_API bool          IsItemToggledOpen();                                                    /* original C++ signature */
def is_item_toggled_open() -> bool:
    """was the last item open state toggled? set by TreeNode()."""
    pass

# IMGUI_API bool          IsAnyItemHovered();                                                     /* original C++ signature */
def is_any_item_hovered() -> bool:
    """is any item hovered?"""
    pass

# IMGUI_API bool          IsAnyItemActive();                                                      /* original C++ signature */
def is_any_item_active() -> bool:
    """is any item active?"""
    pass

# IMGUI_API bool          IsAnyItemFocused();                                                     /* original C++ signature */
def is_any_item_focused() -> bool:
    """is any item focused?"""
    pass

# IMGUI_API ImGuiID       GetItemID();                                                            /* original C++ signature */
def get_item_id() -> ID:
    """get ID of last item (~~ often same ImGui::GetID(label) beforehand)"""
    pass

# IMGUI_API ImVec2        GetItemRectMin();                                                       /* original C++ signature */
def get_item_rect_min() -> ImVec2:
    """get upper-left bounding rectangle of the last item (screen space)"""
    pass

# IMGUI_API ImVec2        GetItemRectMax();                                                       /* original C++ signature */
def get_item_rect_max() -> ImVec2:
    """get lower-right bounding rectangle of the last item (screen space)"""
    pass

# IMGUI_API ImVec2        GetItemRectSize();                                                      /* original C++ signature */
def get_item_rect_size() -> ImVec2:
    """get size of last item"""
    pass

# Viewports
# - Currently represents the Platform Window created by the application which is hosting our Dear ImGui windows.
# - In 'docking' branch with multi-viewport enabled, we extend this concept to have multiple active viewports.
# - In the future we will extend this concept further to also represent Platform Monitor and support a "no main platform window" operation mode.
# IMGUI_API ImGuiViewport* GetMainViewport();                                                     /* original C++ signature */
def get_main_viewport() -> Viewport:
    """return primary/default viewport. This can never be None."""
    pass

# Background/Foreground Draw Lists
# IMGUI_API ImDrawList*   GetBackgroundDrawList(ImGuiViewport* viewport = NULL);                  /* original C++ signature */
def get_background_draw_list(viewport: Optional[Viewport] = None) -> ImDrawList:
    """get background draw list for the given viewport or viewport associated to the current window. this draw list will be the first rendering one. Useful to quickly draw shapes/text behind dear imgui contents."""
    pass

# IMGUI_API ImDrawList*   GetForegroundDrawList(ImGuiViewport* viewport = NULL);                  /* original C++ signature */
def get_foreground_draw_list(viewport: Optional[Viewport] = None) -> ImDrawList:
    """get foreground draw list for the given viewport or viewport associated to the current window. this draw list will be the top-most rendered one. Useful to quickly draw shapes/text over dear imgui contents."""
    pass

# Miscellaneous Utilities
# IMGUI_API bool          IsRectVisible(const ImVec2& size);                                      /* original C++ signature */
@overload
def is_rect_visible(size: ImVec2Like) -> bool:
    """test if rectangle (of given size, starting from cursor position) is visible / not clipped."""
    pass

# IMGUI_API bool          IsRectVisible(const ImVec2& rect_min, const ImVec2& rect_max);          /* original C++ signature */
@overload
def is_rect_visible(rect_min: ImVec2Like, rect_max: ImVec2Like) -> bool:
    """test if rectangle (in screen space) is visible / not clipped. to perform coarse clipping on user's side."""
    pass

# IMGUI_API double        GetTime();                                                              /* original C++ signature */
def get_time() -> float:
    """get global imgui time. incremented by io.DeltaTime every frame."""
    pass

# IMGUI_API int           GetFrameCount();                                                        /* original C++ signature */
def get_frame_count() -> int:
    """get global imgui frame count. incremented by 1 every frame."""
    pass

# IMGUI_API ImDrawListSharedData* GetDrawListSharedData();                                        /* original C++ signature */
def get_draw_list_shared_data() -> ImDrawListSharedData:
    """you may use this when creating your own ImDrawList instances."""
    pass

# IMGUI_API const char*   GetStyleColorName(ImGuiCol idx);                                        /* original C++ signature */
def get_style_color_name(idx: Col) -> str:
    """get a string corresponding to the enum value (for display, saving, etc.)."""
    pass

# IMGUI_API void          SetStateStorage(ImGuiStorage* storage);                                 /* original C++ signature */
def set_state_storage(storage: Storage) -> None:
    """replace current window storage with our own (if you want to manipulate it yourself, typically clear subsection of it)"""
    pass

# IMGUI_API ImGuiStorage* GetStateStorage();    /* original C++ signature */
def get_state_storage() -> Storage:
    pass

# IMGUI_API ImVec2        CalcTextSize(const char* text, const char* text_end = NULL, bool hide_text_after_double_hash = false, float wrap_width = -1.0f);    /* original C++ signature */
def calc_text_size(
    text: str, text_end: Optional[str] = None, hide_text_after_double_hash: bool = False, wrap_width: float = -1.0
) -> ImVec2:
    """Text Utilities"""
    pass

# Color Utilities
# IMGUI_API ImVec4        ColorConvertU32ToFloat4(ImU32 in);    /* original C++ signature */
def color_convert_u32_to_float4(in_: ImU32) -> ImVec4:
    pass

# IMGUI_API ImU32         ColorConvertFloat4ToU32(const ImVec4& in);    /* original C++ signature */
def color_convert_float4_to_u32(in_: ImVec4Like) -> ImU32:
    pass

# IMGUI_API void          ColorConvertRGBtoHSV(float r, float g, float b, float& out_h, float& out_s, float& out_v);    /* original C++ signature */
def color_convert_rgb_to_hsv(
    r: float, g: float, b: float, out_h: float, out_s: float, out_v: float
) -> Tuple[float, float, float]:
    pass

# IMGUI_API void          ColorConvertHSVtoRGB(float h, float s, float v, float& out_r, float& out_g, float& out_b);    /* original C++ signature */
def color_convert_hsv_to_rgb(
    h: float, s: float, v: float, out_r: float, out_g: float, out_b: float
) -> Tuple[float, float, float]:
    pass

# Inputs Utilities: Keyboard/Mouse/Gamepad
# - the ImGuiKey enum contains all possible keyboard, mouse and gamepad inputs (e.g. ImGuiKey_A, ImGuiKey_MouseLeft, ImGuiKey_GamepadDpadUp...).
# - (legacy: before v1.87, we used ImGuiKey to carry native/user indices as defined by each backends. This was obsoleted in 1.87 (2022-02) and completely removed in 1.91.5 (2024-11). See https://github.com/ocornut/imgui/issues/4921)
# - (legacy: any use of ImGuiKey will assert when key < 512 to detect passing legacy native/user indices)
# IMGUI_API bool          IsKeyDown(ImGuiKey key);                                                /* original C++ signature */
def is_key_down(key: Key) -> bool:
    """is key being held."""
    pass

# IMGUI_API bool          IsKeyPressed(ImGuiKey key, bool repeat = true);                         /* original C++ signature */
def is_key_pressed(key: Key, repeat: bool = True) -> bool:
    """was key pressed (went from !Down to Down)? if repeat=True, uses io.KeyRepeatDelay / KeyRepeatRate"""
    pass

# IMGUI_API bool          IsKeyReleased(ImGuiKey key);                                            /* original C++ signature */
def is_key_released(key: Key) -> bool:
    """was key released (went from Down to !Down)?"""
    pass

# IMGUI_API bool          IsKeyChordPressed(ImGuiKeyChord key_chord);                             /* original C++ signature */
def is_key_chord_pressed(key_chord: KeyChord) -> bool:
    """was key chord (mods + key) pressed, e.g. you can pass 'ImGuiMod_Ctrl | ImGuiKey_S' as a key-chord. This doesn't do any routing or focus check, please consider using Shortcut() function instead."""
    pass

# IMGUI_API int           GetKeyPressedAmount(ImGuiKey key, float repeat_delay, float rate);      /* original C++ signature */
def get_key_pressed_amount(key: Key, repeat_delay: float, rate: float) -> int:
    """uses provided repeat rate/delay. return a count, most often 0 or 1 but might be >1 if RepeatRate is small enough that DeltaTime > RepeatRate"""
    pass

# IMGUI_API const char*   GetKeyName(ImGuiKey key);                                               /* original C++ signature */
def get_key_name(key: Key) -> str:
    """[DEBUG] returns English name of the key. Those names a provided for debugging purpose and are not meant to be saved persistently not compared."""
    pass

# IMGUI_API void          SetNextFrameWantCaptureKeyboard(bool want_capture_keyboard);            /* original C++ signature */
def set_next_frame_want_capture_keyboard(want_capture_keyboard: bool) -> None:
    """Override io.WantCaptureKeyboard flag next frame (said flag is left for your application to handle, typically when True it instructs your app to ignore inputs). e.g. force capture keyboard when your widget is being hovered. This is equivalent to setting "io.WantCaptureKeyboard = want_capture_keyboard"; after the next NewFrame() call."""
    pass

# Inputs Utilities: Shortcut Testing & Routing [BETA]
# - ImGuiKeyChord = a ImGuiKey + optional ImGuiMod_Alt/ImGuiMod_Ctrl/ImGuiMod_Shift/ImGuiMod_Super.
#       ImGuiKey_C                          // Accepted by functions taking ImGuiKey or ImGuiKeyChord arguments)
#       ImGuiMod_Ctrl | ImGuiKey_C          // Accepted by functions taking ImGuiKeyChord arguments)
#   only ImGuiMod_XXX values are legal to combine with an ImGuiKey. You CANNOT combine two ImGuiKey values.
# - The general idea is that several callers may register interest in a shortcut, and only one owner gets it.
#      Parent   -> call Shortcut(Ctrl+S)    // When Parent is focused, Parent gets the shortcut.
#        Child1 -> call Shortcut(Ctrl+S)    // When Child1 is focused, Child1 gets the shortcut (Child1 overrides Parent shortcuts)
#        Child2 -> no call                  // When Child2 is focused, Parent gets the shortcut.
#   The whole system is order independent, so if Child1 makes its calls before Parent, results will be identical.
#   This is an important property as it facilitate working with foreign code or larger codebase.
# - To understand the difference:
#   - IsKeyChordPressed() compares mods and call IsKeyPressed() -> function has no side-effect.
#   - Shortcut() submits a route, routes are resolved, if it currently can be routed it calls IsKeyChordPressed() -> function has (desirable) side-effects as it can prevents another call from getting the route.
# - Visualize registered routes in 'Metrics/Debugger->Inputs'.
# IMGUI_API bool          Shortcut(ImGuiKeyChord key_chord, ImGuiInputFlags flags = 0);    /* original C++ signature */
def shortcut(key_chord: KeyChord, flags: InputFlags = 0) -> bool:
    pass

# IMGUI_API void          SetNextItemShortcut(ImGuiKeyChord key_chord, ImGuiInputFlags flags = 0);    /* original C++ signature */
def set_next_item_shortcut(key_chord: KeyChord, flags: InputFlags = 0) -> None:
    pass

# Inputs Utilities: Key/Input Ownership [BETA]
# - One common use case would be to allow your items to disable standard inputs behaviors such
#   as Tab or Alt key handling, Mouse Wheel scrolling, etc.
#   e.g. Button(...); SetItemKeyOwner(ImGuiKey_MouseWheelY); to make hovering/activating a button disable wheel for scrolling.
# - Reminder ImGuiKey enum include access to mouse buttons and gamepad, so key ownership can apply to them.
# - Many related features are still in imgui_internal.h. For instance, most IsKeyXXX()/IsMouseXXX() functions have an owner-id-aware version.
# IMGUI_API void          SetItemKeyOwner(ImGuiKey key);                                          /* original C++ signature */
def set_item_key_owner(key: Key) -> None:
    """Set key owner to last item ID if it is hovered or active. Equivalent to 'if (IsItemHovered() || IsItemActive()) { SetKeyOwner(key, GetItemID());'."""
    pass

# Inputs Utilities: Mouse
# - To refer to a mouse button, you may use named enums in your code e.g. ImGuiMouseButton_Left, ImGuiMouseButton_Right.
# - You can also use regular integer: it is forever guaranteed that 0=Left, 1=Right, 2=Middle.
# - Dragging operations are only reported after mouse has moved a certain distance away from the initial clicking position (see 'lock_threshold' and 'io.MouseDraggingThreshold')
# IMGUI_API bool          IsMouseDown(ImGuiMouseButton button);                                   /* original C++ signature */
def is_mouse_down(button: MouseButton) -> bool:
    """is mouse button held?"""
    pass

# IMGUI_API bool          IsMouseClicked(ImGuiMouseButton button, bool repeat = false);           /* original C++ signature */
def is_mouse_clicked(button: MouseButton, repeat: bool = False) -> bool:
    """did mouse button clicked? (went from !Down to Down). Same as GetMouseClickedCount() == 1."""
    pass

# IMGUI_API bool          IsMouseReleased(ImGuiMouseButton button);                               /* original C++ signature */
def is_mouse_released(button: MouseButton) -> bool:
    """did mouse button released? (went from Down to !Down)"""
    pass

# IMGUI_API bool          IsMouseDoubleClicked(ImGuiMouseButton button);                          /* original C++ signature */
def is_mouse_double_clicked(button: MouseButton) -> bool:
    """did mouse button double-clicked? Same as GetMouseClickedCount() == 2. (note that a double-click will also report IsMouseClicked() == True)"""
    pass

# IMGUI_API int           GetMouseClickedCount(ImGuiMouseButton button);                          /* original C++ signature */
def get_mouse_clicked_count(button: MouseButton) -> int:
    """return the number of successive mouse-clicks at the time where a click happen (otherwise 0)."""
    pass

# IMGUI_API bool          IsMouseHoveringRect(const ImVec2& r_min, const ImVec2& r_max, bool clip = true);    /* original C++ signature */
def is_mouse_hovering_rect(r_min: ImVec2Like, r_max: ImVec2Like, clip: bool = True) -> bool:
    """is mouse hovering given bounding rect (in screen space). clipped by current clipping settings, but disregarding of other consideration of focus/window ordering/popup-block."""
    pass

# IMGUI_API bool          IsMousePosValid(const ImVec2* mouse_pos = NULL);                        /* original C++ signature */
def is_mouse_pos_valid(mouse_pos: Optional[ImVec2Like] = None) -> bool:
    """by convention we use (-FLT_MAX,-FLT_MAX) to denote that there is no mouse available"""
    pass

# IMGUI_API bool          IsAnyMouseDown();                                                       /* original C++ signature */
def is_any_mouse_down() -> bool:
    """[WILL OBSOLETE] is any mouse button held? This was designed for backends, but prefer having backend maintain a mask of held mouse buttons, because upcoming input queue system will make this invalid."""
    pass

# IMGUI_API ImVec2        GetMousePos();                                                          /* original C++ signature */
def get_mouse_pos() -> ImVec2:
    """shortcut to ImGui::GetIO().MousePos provided by user, to be consistent with other calls"""
    pass

# IMGUI_API ImVec2        GetMousePosOnOpeningCurrentPopup();                                     /* original C++ signature */
def get_mouse_pos_on_opening_current_popup() -> ImVec2:
    """retrieve mouse position at the time of opening popup we have BeginPopup() into (helper to avoid user backing that value themselves)"""
    pass

# IMGUI_API bool          IsMouseDragging(ImGuiMouseButton button, float lock_threshold = -1.0f);             /* original C++ signature */
def is_mouse_dragging(button: MouseButton, lock_threshold: float = -1.0) -> bool:
    """is mouse dragging? (uses io.MouseDraggingThreshold if lock_threshold < 0.0)"""
    pass

# IMGUI_API ImVec2        GetMouseDragDelta(ImGuiMouseButton button = 0, float lock_threshold = -1.0f);       /* original C++ signature */
def get_mouse_drag_delta(button: MouseButton = 0, lock_threshold: float = -1.0) -> ImVec2:
    """return the delta from the initial clicking position while the mouse button is pressed or was just released. This is locked and return 0.0 until the mouse moves past a distance threshold at least once (uses io.MouseDraggingThreshold if lock_threshold < 0.0)"""
    pass

# IMGUI_API void          ResetMouseDragDelta(ImGuiMouseButton button = 0);                       /* original C++ signature */
def reset_mouse_drag_delta(button: MouseButton = 0) -> None:
    pass

# IMGUI_API ImGuiMouseCursor GetMouseCursor();                                                    /* original C++ signature */
def get_mouse_cursor() -> MouseCursor:
    """get desired mouse cursor shape. Important: reset in ImGui::NewFrame(), this is updated during the frame. valid before Render(). If you use software rendering by setting io.MouseDrawCursor ImGui will render those for you"""
    pass

# IMGUI_API void          SetMouseCursor(ImGuiMouseCursor cursor_type);                           /* original C++ signature */
def set_mouse_cursor(cursor_type: MouseCursor) -> None:
    """set desired mouse cursor shape"""
    pass

# IMGUI_API void          SetNextFrameWantCaptureMouse(bool want_capture_mouse);                  /* original C++ signature */
def set_next_frame_want_capture_mouse(want_capture_mouse: bool) -> None:
    """Override io.WantCaptureMouse flag next frame (said flag is left for your application to handle, typical when True it instucts your app to ignore inputs). This is equivalent to setting "io.WantCaptureMouse = want_capture_mouse;" after the next NewFrame() call."""
    pass

# Clipboard Utilities
# - Also see the LogToClipboard() function to capture GUI into clipboard, or easily output text data to the clipboard.
# IMGUI_API const char*   GetClipboardText();    /* original C++ signature */
def get_clipboard_text() -> str:
    pass

# IMGUI_API void          SetClipboardText(const char* text);    /* original C++ signature */
def set_clipboard_text(text: str) -> None:
    pass

# Settings/.Ini Utilities
# - The disk functions are automatically called if io.IniFilename != None (default is "imgui.ini").
# - Set io.IniFilename to None to load/save manually. Read io.WantSaveIniSettings description about handling .ini saving manually.
# - Important: default value "imgui.ini" is relative to current working dir! Most apps will want to lock this to an absolute path (e.g. same path as executables).
# IMGUI_API void          LoadIniSettingsFromDisk(const char* ini_filename);                      /* original C++ signature */
def load_ini_settings_from_disk(ini_filename: str) -> None:
    """call after CreateContext() and before the first call to NewFrame(). NewFrame() automatically calls LoadIniSettingsFromDisk(io.IniFilename)."""
    pass

# IMGUI_API void          LoadIniSettingsFromMemory(const char* ini_data, size_t ini_size=0);     /* original C++ signature */
def load_ini_settings_from_memory(ini_data: str, ini_size: int = 0) -> None:
    """call after CreateContext() and before the first call to NewFrame() to provide .ini data from your own data source."""
    pass

# IMGUI_API void          SaveIniSettingsToDisk(const char* ini_filename);                        /* original C++ signature */
def save_ini_settings_to_disk(ini_filename: str) -> None:
    """this is automatically called (if io.IniFilename is not empty) a few seconds after any modification that should be reflected in the .ini file (and also by DestroyContext)."""
    pass

# IMGUI_API const char*   SaveIniSettingsToMemory(size_t* out_ini_size = NULL);                   /* original C++ signature */
def save_ini_settings_to_memory() -> str:
    """return a zero-terminated string with the .ini data which you can save by your own mean. call when io.WantSaveIniSettings is set, then save data by your own mean and clear io.WantSaveIniSettings."""
    pass

# Debug Utilities
# - Your main debugging friend is the ShowMetricsWindow() function, which is also accessible from Demo->Tools->Metrics Debugger
# IMGUI_API void          DebugTextEncoding(const char* text);    /* original C++ signature */
def debug_text_encoding(text: str) -> None:
    pass

# IMGUI_API void          DebugFlashStyleColor(ImGuiCol idx);    /* original C++ signature */
def debug_flash_style_color(idx: Col) -> None:
    pass

# IMGUI_API void          DebugStartItemPicker();    /* original C++ signature */
def debug_start_item_picker() -> None:
    pass

# IMGUI_API bool          DebugCheckVersionAndDataLayout(const char* version_str, size_t sz_io, size_t sz_style, size_t sz_vec2, size_t sz_vec4, size_t sz_drawvert, size_t sz_drawidx);     /* original C++ signature */
def debug_check_version_and_data_layout(
    version_str: str, sz_io: int, sz_style: int, sz_vec2: int, sz_vec4: int, sz_drawvert: int, sz_drawidx: int
) -> bool:
    pass

# This is called by IMGUI_CHECKVERSION() macro.

# Memory Allocators
# - Those functions are not reliant on the current context.
# - DLL users: heaps and globals are not shared across DLL boundaries! You will need to call SetCurrentContext() + SetAllocatorFunctions()
#   for each static/DLL boundary you are calling from. Read "Context and Memory Allocators" section of imgui.cpp for more details.

# (Optional) Platform/OS interface for multi-viewport support
# Read comments around the ImGuiPlatformIO structure for more details.
# Note: You may use GetWindowViewport() to get the current viewport of the current window.
# IMGUI_API void              UpdatePlatformWindows();                                            /* original C++ signature */
def update_platform_windows() -> None:
    """call in main loop. will call CreateWindow/ResizeWindow/etc. platform functions for each secondary viewport, and DestroyWindow for each inactive viewport."""
    pass

# IMGUI_API void              RenderPlatformWindowsDefault(void* platform_render_arg = NULL, void* renderer_render_arg = NULL);     /* original C++ signature */
def render_platform_windows_default(
    platform_render_arg: Optional[Any] = None, renderer_render_arg: Optional[Any] = None
) -> None:
    """call in main loop. will call RenderWindow/SwapBuffers platform functions for each secondary viewport which doesn't have the ImGuiViewportFlags_Minimized flag set. May be reimplemented by user for custom rendering needs."""
    pass

# IMGUI_API void              DestroyPlatformWindows();                                           /* original C++ signature */
def destroy_platform_windows() -> None:
    """call DestroyWindow platform functions for all viewports. call from backend Shutdown() if you need to close platform windows before imgui shutdown. otherwise will be called by DestroyContext()."""
    pass

# IMGUI_API ImGuiViewport*    FindViewportByID(ImGuiID id);                                       /* original C++ signature */
def find_viewport_by_id(id_: ID) -> Viewport:
    """this is a helper for backends."""
    pass

# IMGUI_API ImGuiViewport*    FindViewportByPlatformHandle(void* platform_handle);                /* original C++ signature */
def find_viewport_by_platform_handle(platform_handle: Any) -> Viewport:
    """this is a helper for backends. the type platform_handle is decided by the backend (e.g. HWND, MyWindow*, GLFWwindow* etc.)"""
    pass

# -----------------------------------------------------------------------------
# [SECTION] Flags & Enumerations
# -----------------------------------------------------------------------------

class WindowFlags_(enum.Enum):
    """Flags for ImGui::Begin()
    (Those are per-window flags. There are shared flags in ImGuiIO: io.ConfigWindowsResizeFromEdges and io.ConfigWindowsMoveFromTitleBarOnly)
    """

    # ImGuiWindowFlags_None                   = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiWindowFlags_NoTitleBar             = 1 << 0,       /* original C++ signature */
    no_title_bar = enum.auto()  # (= 1 << 0)  # Disable title-bar
    # ImGuiWindowFlags_NoResize               = 1 << 1,       /* original C++ signature */
    no_resize = enum.auto()  # (= 1 << 1)  # Disable user resizing with the lower-right grip
    # ImGuiWindowFlags_NoMove                 = 1 << 2,       /* original C++ signature */
    no_move = enum.auto()  # (= 1 << 2)  # Disable user moving the window
    # ImGuiWindowFlags_NoScrollbar            = 1 << 3,       /* original C++ signature */
    no_scrollbar = (
        enum.auto()
    )  # (= 1 << 3)  # Disable scrollbars (window can still scroll with mouse or programmatically)
    # ImGuiWindowFlags_NoScrollWithMouse      = 1 << 4,       /* original C++ signature */
    no_scroll_with_mouse = (
        enum.auto()
    )  # (= 1 << 4)  # Disable user vertically scrolling with mouse wheel. On child window, mouse wheel will be forwarded to the parent unless NoScrollbar is also set.
    # ImGuiWindowFlags_NoCollapse             = 1 << 5,       /* original C++ signature */
    no_collapse = (
        enum.auto()
    )  # (= 1 << 5)  # Disable user collapsing window by double-clicking on it. Also referred to as Window Menu Button (e.g. within a docking node).
    # ImGuiWindowFlags_AlwaysAutoResize       = 1 << 6,       /* original C++ signature */
    always_auto_resize = enum.auto()  # (= 1 << 6)  # Resize every window to its content every frame
    # ImGuiWindowFlags_NoBackground           = 1 << 7,       /* original C++ signature */
    no_background = (
        enum.auto()
    )  # (= 1 << 7)  # Disable drawing background color (WindowBg, etc.) and outside border. Similar as using SetNextWindowBgAlpha(0.0).
    # ImGuiWindowFlags_NoSavedSettings        = 1 << 8,       /* original C++ signature */
    no_saved_settings = enum.auto()  # (= 1 << 8)  # Never load/save settings in .ini file
    # ImGuiWindowFlags_NoMouseInputs          = 1 << 9,       /* original C++ signature */
    no_mouse_inputs = enum.auto()  # (= 1 << 9)  # Disable catching mouse, hovering test with pass through.
    # ImGuiWindowFlags_MenuBar                = 1 << 10,      /* original C++ signature */
    menu_bar = enum.auto()  # (= 1 << 10)  # Has a menu-bar
    # ImGuiWindowFlags_HorizontalScrollbar    = 1 << 11,      /* original C++ signature */
    horizontal_scrollbar = (
        enum.auto()
    )  # (= 1 << 11)  # Allow horizontal scrollbar to appear (off by default). You may use SetNextWindowContentSize(ImVec2(width,0.0)); prior to calling Begin() to specify width. Read code in imgui_demo in the "Horizontal Scrolling" section.
    # ImGuiWindowFlags_NoFocusOnAppearing     = 1 << 12,      /* original C++ signature */
    no_focus_on_appearing = (
        enum.auto()
    )  # (= 1 << 12)  # Disable taking focus when transitioning from hidden to visible state
    # ImGuiWindowFlags_NoBringToFrontOnFocus  = 1 << 13,      /* original C++ signature */
    no_bring_to_front_on_focus = (
        enum.auto()
    )  # (= 1 << 13)  # Disable bringing window to front when taking focus (e.g. clicking on it or programmatically giving it focus)
    # ImGuiWindowFlags_AlwaysVerticalScrollbar= 1 << 14,      /* original C++ signature */
    always_vertical_scrollbar = (
        enum.auto()
    )  # (= 1 << 14)  # Always show vertical scrollbar (even if ContentSize.y < Size.y)
    # ImGuiWindowFlags_AlwaysHorizontalScrollbar=1<< 15,      /* original C++ signature */
    always_horizontal_scrollbar = (
        enum.auto()
    )  # (= 1<< 15)  # Always show horizontal scrollbar (even if ContentSize.x < Size.x)
    # ImGuiWindowFlags_NoNavInputs            = 1 << 16,      /* original C++ signature */
    no_nav_inputs = enum.auto()  # (= 1 << 16)  # No keyboard/gamepad navigation within the window
    # ImGuiWindowFlags_NoNavFocus             = 1 << 17,      /* original C++ signature */
    no_nav_focus = (
        enum.auto()
    )  # (= 1 << 17)  # No focusing toward this window with keyboard/gamepad navigation (e.g. skipped by CTRL+TAB)
    # ImGuiWindowFlags_UnsavedDocument        = 1 << 18,      /* original C++ signature */
    unsaved_document = (
        enum.auto()
    )  # (= 1 << 18)  # Display a dot next to the title. When used in a tab/docking context, tab is selected when clicking the X + closure is not assumed (will wait for user to stop submitting the tab). Otherwise closure is assumed when pressing the X, so if you keep submitting the tab may reappear at end of tab bar.
    # ImGuiWindowFlags_NoDocking              = 1 << 19,      /* original C++ signature */
    no_docking = enum.auto()  # (= 1 << 19)  # Disable docking of this window
    # ImGuiWindowFlags_NoNav                  = ImGuiWindowFlags_NoNavInputs | ImGuiWindowFlags_NoNavFocus,    /* original C++ signature */
    no_nav = enum.auto()  # (= WindowFlags_NoNavInputs | WindowFlags_NoNavFocus)
    # ImGuiWindowFlags_NoDecoration           = ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoCollapse,    /* original C++ signature */
    no_decoration = (
        enum.auto()
    )  # (= WindowFlags_NoTitleBar | WindowFlags_NoResize | WindowFlags_NoScrollbar | WindowFlags_NoCollapse)
    # ImGuiWindowFlags_NoInputs               = ImGuiWindowFlags_NoMouseInputs | ImGuiWindowFlags_NoNavInputs | ImGuiWindowFlags_NoNavFocus,    /* original C++ signature */
    no_inputs = enum.auto()  # (= WindowFlags_NoMouseInputs | WindowFlags_NoNavInputs | WindowFlags_NoNavFocus)

    # [Internal]
    # ImGuiWindowFlags_ChildWindow            = 1 << 24,      /* original C++ signature */
    child_window = enum.auto()  # (= 1 << 24)  # Don't use! For internal use by BeginChild()
    # ImGuiWindowFlags_Tooltip                = 1 << 25,      /* original C++ signature */
    tooltip = enum.auto()  # (= 1 << 25)  # Don't use! For internal use by BeginTooltip()
    # ImGuiWindowFlags_Popup                  = 1 << 26,      /* original C++ signature */
    popup = enum.auto()  # (= 1 << 26)  # Don't use! For internal use by BeginPopup()
    # ImGuiWindowFlags_Modal                  = 1 << 27,      /* original C++ signature */
    modal = enum.auto()  # (= 1 << 27)  # Don't use! For internal use by BeginPopupModal()
    # ImGuiWindowFlags_ChildMenu              = 1 << 28,      /* original C++ signature */
    child_menu = enum.auto()  # (= 1 << 28)  # Don't use! For internal use by BeginMenu()
    # ImGuiWindowFlags_DockNodeHost           = 1 << 29,      /* original C++ signature */
    dock_node_host = enum.auto()  # (= 1 << 29)  # Don't use! For internal use by Begin()/NewFrame()

    # Obsolete names

class ChildFlags_(enum.Enum):
    """Flags for ImGui::BeginChild()
    (Legacy: bit 0 must always correspond to ImGuiChildFlags_Borders to be backward compatible with old API using 'bool border = False'.
    About using AutoResizeX/AutoResizeY flags:
    - May be combined with SetNextWindowSizeConstraints() to set a min/max size for each axis (see "Demo->Child->Auto-resize with Constraints").
    - Size measurement for a given axis is only performed when the child window is within visible boundaries, or is just appearing.
      - This allows BeginChild() to return False when not within boundaries (e.g. when scrolling), which is more optimal. BUT it won't update its auto-size while clipped.
        While not perfect, it is a better default behavior as the always-on performance gain is more valuable than the occasional "resizing after becoming visible again" glitch.
      - You may also use ImGuiChildFlags_AlwaysAutoResize to force an update even when child window is not in view.
        HOWEVER PLEASE UNDERSTAND THAT DOING SO WILL PREVENT BeginChild() FROM EVER RETURNING FALSE, disabling benefits of coarse clipping.
    """

    # ImGuiChildFlags_None                    = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiChildFlags_Borders                 = 1 << 0,       /* original C++ signature */
    borders = (
        enum.auto()
    )  # (= 1 << 0)  # Show an outer border and enable WindowPadding. (IMPORTANT: this is always == 1 == True for legacy reason)
    # ImGuiChildFlags_AlwaysUseWindowPadding  = 1 << 1,       /* original C++ signature */
    always_use_window_padding = (
        enum.auto()
    )  # (= 1 << 1)  # Pad with style.WindowPadding even if no border are drawn (no padding by default for non-bordered child windows because it makes more sense)
    # ImGuiChildFlags_ResizeX                 = 1 << 2,       /* original C++ signature */
    resize_x = (
        enum.auto()
    )  # (= 1 << 2)  # Allow resize from right border (layout direction). Enable .ini saving (unless ImGuiWindowFlags_NoSavedSettings passed to window flags)
    # ImGuiChildFlags_ResizeY                 = 1 << 3,       /* original C++ signature */
    resize_y = enum.auto()  # (= 1 << 3)  # Allow resize from bottom border (layout direction). "
    # ImGuiChildFlags_AutoResizeX             = 1 << 4,       /* original C++ signature */
    auto_resize_x = (
        enum.auto()
    )  # (= 1 << 4)  # Enable auto-resizing width. Read "IMPORTANT: Size measurement" details above.
    # ImGuiChildFlags_AutoResizeY             = 1 << 5,       /* original C++ signature */
    auto_resize_y = (
        enum.auto()
    )  # (= 1 << 5)  # Enable auto-resizing height. Read "IMPORTANT: Size measurement" details above.
    # ImGuiChildFlags_AlwaysAutoResize        = 1 << 6,       /* original C++ signature */
    always_auto_resize = (
        enum.auto()
    )  # (= 1 << 6)  # Combined with AutoResizeX/AutoResizeY. Always measure size even when child is hidden, always return True, always disable clipping optimization! NOT RECOMMENDED.
    # ImGuiChildFlags_FrameStyle              = 1 << 7,       /* original C++ signature */
    frame_style = (
        enum.auto()
    )  # (= 1 << 7)  # Style the child window like a framed item: use FrameBg, FrameRounding, FrameBorderSize, FramePadding instead of ChildBg, ChildRounding, ChildBorderSize, WindowPadding.
    # ImGuiChildFlags_NavFlattened            = 1 << 8,       /* original C++ signature */
    nav_flattened = (
        enum.auto()
    )  # (= 1 << 8)  # [BETA] Share focus scope, allow keyboard/gamepad navigation to cross over parent border to this child or between sibling child windows.

    # Obsolete names

class ItemFlags_(enum.Enum):
    """Flags for ImGui::PushItemFlag()
    (Those are shared by all items)
    """

    # ImGuiItemFlags_None                     = 0,            /* original C++ signature */
    none = enum.auto()  # (= 0)  # (Default)
    # ImGuiItemFlags_NoTabStop                = 1 << 0,       /* original C++ signature */
    no_tab_stop = (
        enum.auto()
    )  # (= 1 << 0)  # False    // Disable keyboard tabbing. This is a "lighter" version of ImGuiItemFlags_NoNav.
    # ImGuiItemFlags_NoNav                    = 1 << 1,       /* original C++ signature */
    no_nav = (
        enum.auto()
    )  # (= 1 << 1)  # False    // Disable any form of focusing (keyboard/gamepad directional navigation and SetKeyboardFocusHere() calls).
    # ImGuiItemFlags_NoNavDefaultFocus        = 1 << 2,       /* original C++ signature */
    no_nav_default_focus = (
        enum.auto()
    )  # (= 1 << 2)  # False    // Disable item being a candidate for default focus (e.g. used by title bar items).
    # ImGuiItemFlags_ButtonRepeat             = 1 << 3,       /* original C++ signature */
    button_repeat = (
        enum.auto()
    )  # (= 1 << 3)  # False    // Any button-like behavior will have repeat mode enabled (based on io.KeyRepeatDelay and io.KeyRepeatRate values). Note that you can also call IsItemActive() after any button to tell if it is being held.
    # ImGuiItemFlags_AutoClosePopups          = 1 << 4,       /* original C++ signature */
    auto_close_popups = (
        enum.auto()
    )  # (= 1 << 4)  # True     // MenuItem()/Selectable() automatically close their parent popup window.
    # ImGuiItemFlags_AllowDuplicateId         = 1 << 5,       /* original C++ signature */
    allow_duplicate_id = (
        enum.auto()
    )  # (= 1 << 5)  # False    // Allow submitting an item with the same identifier as an item already submitted this frame without triggering a warning tooltip if io.ConfigDebugHighlightIdConflicts is set.

class InputTextFlags_(enum.Enum):
    """Flags for ImGui::InputText()
    (Those are per-item flags. There are shared flags in ImGuiIO: io.ConfigInputTextCursorBlink and io.ConfigInputTextEnterKeepActive)
    """

    # Basic filters (also see ImGuiInputTextFlags_CallbackCharFilter)
    # ImGuiInputTextFlags_None                = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiInputTextFlags_CharsDecimal        = 1 << 0,       /* original C++ signature */
    chars_decimal = enum.auto()  # (= 1 << 0)  # Allow 0123456789.+-*/
    # ImGuiInputTextFlags_CharsHexadecimal    = 1 << 1,       /* original C++ signature */
    chars_hexadecimal = enum.auto()  # (= 1 << 1)  # Allow 0123456789ABCDEFabcdef
    # ImGuiInputTextFlags_CharsScientific     = 1 << 2,       /* original C++ signature */
    chars_scientific = enum.auto()  # (= 1 << 2)  # Allow 0123456789.+-*/eE (Scientific notation input)
    # ImGuiInputTextFlags_CharsUppercase      = 1 << 3,       /* original C++ signature */
    chars_uppercase = enum.auto()  # (= 1 << 3)  # Turn a..z into A..Z
    # ImGuiInputTextFlags_CharsNoBlank        = 1 << 4,       /* original C++ signature */
    chars_no_blank = enum.auto()  # (= 1 << 4)  # Filter out spaces, tabs

    # Inputs
    # ImGuiInputTextFlags_AllowTabInput       = 1 << 5,       /* original C++ signature */
    allow_tab_input = enum.auto()  # (= 1 << 5)  # Pressing TAB input a '\t' character into the text field
    # ImGuiInputTextFlags_EnterReturnsTrue    = 1 << 6,       /* original C++ signature */
    enter_returns_true = (
        enum.auto()
    )  # (= 1 << 6)  # Return 'True' when Enter is pressed (as opposed to every time the value was modified). Consider using IsItemDeactivatedAfterEdit() instead!
    # ImGuiInputTextFlags_EscapeClearsAll     = 1 << 7,       /* original C++ signature */
    escape_clears_all = (
        enum.auto()
    )  # (= 1 << 7)  # Escape key clears content if not empty, and deactivate otherwise (contrast to default behavior of Escape to revert)
    # ImGuiInputTextFlags_CtrlEnterForNewLine = 1 << 8,       /* original C++ signature */
    ctrl_enter_for_new_line = (
        enum.auto()
    )  # (= 1 << 8)  # In multi-line mode, validate with Enter, add new line with Ctrl+Enter (default is opposite: validate with Ctrl+Enter, add line with Enter).

    # Other options
    # ImGuiInputTextFlags_ReadOnly            = 1 << 9,       /* original C++ signature */
    read_only = enum.auto()  # (= 1 << 9)  # Read-only mode
    # ImGuiInputTextFlags_Password            = 1 << 10,      /* original C++ signature */
    password = enum.auto()  # (= 1 << 10)  # Password mode, display all characters as '*', disable copy
    # ImGuiInputTextFlags_AlwaysOverwrite     = 1 << 11,      /* original C++ signature */
    always_overwrite = enum.auto()  # (= 1 << 11)  # Overwrite mode
    # ImGuiInputTextFlags_AutoSelectAll       = 1 << 12,      /* original C++ signature */
    auto_select_all = enum.auto()  # (= 1 << 12)  # Select entire text when first taking mouse focus
    # ImGuiInputTextFlags_ParseEmptyRefVal    = 1 << 13,      /* original C++ signature */
    parse_empty_ref_val = (
        enum.auto()
    )  # (= 1 << 13)  # InputFloat(), InputInt(), InputScalar() etc. only: parse empty string as zero value.
    # ImGuiInputTextFlags_DisplayEmptyRefVal  = 1 << 14,      /* original C++ signature */
    display_empty_ref_val = (
        enum.auto()
    )  # (= 1 << 14)  # InputFloat(), InputInt(), InputScalar() etc. only: when value is zero, do not display it. Generally used with ImGuiInputTextFlags_ParseEmptyRefVal.
    # ImGuiInputTextFlags_NoHorizontalScroll  = 1 << 15,      /* original C++ signature */
    no_horizontal_scroll = enum.auto()  # (= 1 << 15)  # Disable following the cursor horizontally
    # ImGuiInputTextFlags_NoUndoRedo          = 1 << 16,      /* original C++ signature */
    no_undo_redo = (
        enum.auto()
    )  # (= 1 << 16)  # Disable undo/redo. Note that input text owns the text data while active, if you want to provide your own undo/redo stack you need e.g. to call ClearActiveID().

    # Elide display / Alignment
    # ImGuiInputTextFlags_ElideLeft			= 1 << 17,	    /* original C++ signature */
    elide_left = (
        enum.auto()
    )  # (= 1 << 17)  # When text doesn't fit, elide left side to ensure right side stays visible. Useful for path/filenames. Single-line only!

    # Callback features
    # ImGuiInputTextFlags_CallbackCompletion  = 1 << 18,      /* original C++ signature */
    callback_completion = enum.auto()  # (= 1 << 18)  # Callback on pressing TAB (for completion handling)
    # ImGuiInputTextFlags_CallbackHistory     = 1 << 19,      /* original C++ signature */
    callback_history = enum.auto()  # (= 1 << 19)  # Callback on pressing Up/Down arrows (for history handling)
    # ImGuiInputTextFlags_CallbackAlways      = 1 << 20,      /* original C++ signature */
    callback_always = (
        enum.auto()
    )  # (= 1 << 20)  # Callback on each iteration. User code may query cursor position, modify text buffer.
    # ImGuiInputTextFlags_CallbackCharFilter  = 1 << 21,      /* original C++ signature */
    callback_char_filter = (
        enum.auto()
    )  # (= 1 << 21)  # Callback on character inputs to replace or discard them. Modify 'EventChar' to replace or discard, or return 1 in callback to discard.
    # ImGuiInputTextFlags_CallbackResize      = 1 << 22,      /* original C++ signature */
    callback_resize = (
        enum.auto()
    )  # (= 1 << 22)  # Callback on buffer capacity changes request (beyond 'buf_size' parameter value), allowing the string to grow. Notify when the string wants to be resized (for string types which hold a cache of their Size). You will be provided a new BufSize in the callback and NEED to honor it. (see misc/cpp/imgui_stdlib.h for an example of using this)
    # ImGuiInputTextFlags_CallbackEdit        = 1 << 23,      /* original C++ signature */
    callback_edit = (
        enum.auto()
    )  # (= 1 << 23)  # Callback on any edit (note that InputText() already returns True on edit, the callback is useful mainly to manipulate the underlying buffer while focus is active)

    # Obsolete names
    # ImGuiInputTextFlags_AlwaysInsertMode  = ImGuiInputTextFlags_AlwaysOverwrite   // [renamed in 1.82] name was not matching behavior

class TreeNodeFlags_(enum.Enum):
    """Flags for ImGui::TreeNodeEx(), ImGui::CollapsingHeader*()"""

    # ImGuiTreeNodeFlags_None                 = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTreeNodeFlags_Selected             = 1 << 0,       /* original C++ signature */
    selected = enum.auto()  # (= 1 << 0)  # Draw as selected
    # ImGuiTreeNodeFlags_Framed               = 1 << 1,       /* original C++ signature */
    framed = enum.auto()  # (= 1 << 1)  # Draw frame with background (e.g. for CollapsingHeader)
    # ImGuiTreeNodeFlags_AllowOverlap         = 1 << 2,       /* original C++ signature */
    allow_overlap = enum.auto()  # (= 1 << 2)  # Hit testing to allow subsequent widgets to overlap this one
    # ImGuiTreeNodeFlags_NoTreePushOnOpen     = 1 << 3,       /* original C++ signature */
    no_tree_push_on_open = (
        enum.auto()
    )  # (= 1 << 3)  # Don't do a TreePush() when open (e.g. for CollapsingHeader) = no extra indent nor pushing on ID stack
    # ImGuiTreeNodeFlags_NoAutoOpenOnLog      = 1 << 4,       /* original C++ signature */
    no_auto_open_on_log = (
        enum.auto()
    )  # (= 1 << 4)  # Don't automatically and temporarily open node when Logging is active (by default logging will automatically open tree nodes)
    # ImGuiTreeNodeFlags_DefaultOpen          = 1 << 5,       /* original C++ signature */
    default_open = enum.auto()  # (= 1 << 5)  # Default node to be open
    # ImGuiTreeNodeFlags_OpenOnDoubleClick    = 1 << 6,       /* original C++ signature */
    open_on_double_click = (
        enum.auto()
    )  # (= 1 << 6)  # Open on double-click instead of simple click (default for multi-select unless any _OpenOnXXX behavior is set explicitly). Both behaviors may be combined.
    # ImGuiTreeNodeFlags_OpenOnArrow          = 1 << 7,       /* original C++ signature */
    open_on_arrow = (
        enum.auto()
    )  # (= 1 << 7)  # Open when clicking on the arrow part (default for multi-select unless any _OpenOnXXX behavior is set explicitly). Both behaviors may be combined.
    # ImGuiTreeNodeFlags_Leaf                 = 1 << 8,       /* original C++ signature */
    leaf = enum.auto()  # (= 1 << 8)  # No collapsing, no arrow (use as a convenience for leaf nodes).
    # ImGuiTreeNodeFlags_Bullet               = 1 << 9,       /* original C++ signature */
    bullet = (
        enum.auto()
    )  # (= 1 << 9)  # Display a bullet instead of arrow. IMPORTANT: node can still be marked open/close if you don't set the _Leaf flag!
    # ImGuiTreeNodeFlags_FramePadding         = 1 << 10,      /* original C++ signature */
    frame_padding = (
        enum.auto()
    )  # (= 1 << 10)  # Use FramePadding (even for an unframed text node) to vertically align text baseline to regular widget height. Equivalent to calling AlignTextToFramePadding() before the node.
    # ImGuiTreeNodeFlags_SpanAvailWidth       = 1 << 11,      /* original C++ signature */
    span_avail_width = (
        enum.auto()
    )  # (= 1 << 11)  # Extend hit box to the right-most edge, even if not framed. This is not the default in order to allow adding other items on the same line without using AllowOverlap mode.
    # ImGuiTreeNodeFlags_SpanFullWidth        = 1 << 12,      /* original C++ signature */
    span_full_width = (
        enum.auto()
    )  # (= 1 << 12)  # Extend hit box to the left-most and right-most edges (cover the indent area).
    # ImGuiTreeNodeFlags_SpanTextWidth        = 1 << 13,      /* original C++ signature */
    span_text_width = (
        enum.auto()
    )  # (= 1 << 13)  # Narrow hit box + narrow hovering highlight, will only cover the label text.
    # ImGuiTreeNodeFlags_SpanAllColumns       = 1 << 14,      /* original C++ signature */
    span_all_columns = (
        enum.auto()
    )  # (= 1 << 14)  # Frame will span all columns of its container table (text will still fit in current column)
    # ImGuiTreeNodeFlags_NavLeftJumpsBackHere = 1 << 15,      /* original C++ signature */
    nav_left_jumps_back_here = (
        enum.auto()
    )  # (= 1 << 15)  # (WIP) Nav: left direction may move to this TreeNode() from any of its child (items submitted between TreeNode and TreePop)
    # ImGuiTreeNodeFlags_CollapsingHeader     = ImGuiTreeNodeFlags_Framed | ImGuiTreeNodeFlags_NoTreePushOnOpen | ImGuiTreeNodeFlags_NoAutoOpenOnLog,    /* original C++ signature */
    # ImGuiTreeNodeFlags_NoScrollOnOpen     = 1 << 16,  // FIXME: TODO: Disable automatic scroll on TreePop() if node got just open and contents is not visible
    collapsing_header = (
        enum.auto()
    )  # (= TreeNodeFlags_Framed | TreeNodeFlags_NoTreePushOnOpen | TreeNodeFlags_NoAutoOpenOnLog)

class PopupFlags_(enum.Enum):
    """Flags for OpenPopup*(), BeginPopupContext*(), IsPopupOpen() functions.
    - To be backward compatible with older API which took an 'int mouse_button = 1' argument instead of 'ImGuiPopupFlags flags',
      we need to treat small flags values as a mouse button index, so we encode the mouse button in the first few bits of the flags.
      It is therefore guaranteed to be legal to pass a mouse button index in ImGuiPopupFlags.
    - For the same reason, we exceptionally default the ImGuiPopupFlags argument of BeginPopupContextXXX functions to 1 instead of 0.
      IMPORTANT: because the default parameter is 1 (==ImGuiPopupFlags_MouseButtonRight), if you rely on the default parameter
      and want to use another flag, you need to pass in the ImGuiPopupFlags_MouseButtonRight flag explicitly.
    - Multiple buttons currently cannot be combined/or-ed in those functions (we could allow it later).
    """

    # ImGuiPopupFlags_None                    = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiPopupFlags_MouseButtonLeft         = 0,            /* original C++ signature */
    mouse_button_left = (
        enum.auto()
    )  # (= 0)  # For BeginPopupContext*(): open on Left Mouse release. Guaranteed to always be == 0 (same as ImGuiMouseButton_Left)
    # ImGuiPopupFlags_MouseButtonRight        = 1,            /* original C++ signature */
    mouse_button_right = (
        enum.auto()
    )  # (= 1)  # For BeginPopupContext*(): open on Right Mouse release. Guaranteed to always be == 1 (same as ImGuiMouseButton_Right)
    # ImGuiPopupFlags_MouseButtonMiddle       = 2,            /* original C++ signature */
    mouse_button_middle = (
        enum.auto()
    )  # (= 2)  # For BeginPopupContext*(): open on Middle Mouse release. Guaranteed to always be == 2 (same as ImGuiMouseButton_Middle)
    # ImGuiPopupFlags_MouseButtonMask_        = 0x1F,    /* original C++ signature */
    mouse_button_mask_ = enum.auto()  # (= 0x1F)
    # ImGuiPopupFlags_MouseButtonDefault_     = 1,    /* original C++ signature */
    mouse_button_default_ = enum.auto()  # (= 1)
    # ImGuiPopupFlags_NoReopen                = 1 << 5,       /* original C++ signature */
    no_reopen = (
        enum.auto()
    )  # (= 1 << 5)  # For OpenPopup*(), BeginPopupContext*(): don't reopen same popup if already open (won't reposition, won't reinitialize navigation)
    # ImGuiPopupFlags_NoReopenAlwaysNavInit = 1 << 6,   // For OpenPopup*(), BeginPopupContext*(): focus and initialize navigation even when not reopening.
    # ImGuiPopupFlags_NoOpenOverExistingPopup = 1 << 7,       /* original C++ signature */
    no_open_over_existing_popup = (
        enum.auto()
    )  # (= 1 << 7)  # For OpenPopup*(), BeginPopupContext*(): don't open if there's already a popup at the same level of the popup stack
    # ImGuiPopupFlags_NoOpenOverItems         = 1 << 8,       /* original C++ signature */
    no_open_over_items = (
        enum.auto()
    )  # (= 1 << 8)  # For BeginPopupContextWindow(): don't return True when hovering items, only when hovering empty space
    # ImGuiPopupFlags_AnyPopupId              = 1 << 10,      /* original C++ signature */
    any_popup_id = enum.auto()  # (= 1 << 10)  # For IsPopupOpen(): ignore the ImGuiID parameter and test for any popup.
    # ImGuiPopupFlags_AnyPopupLevel           = 1 << 11,      /* original C++ signature */
    any_popup_level = (
        enum.auto()
    )  # (= 1 << 11)  # For IsPopupOpen(): search/test at any level of the popup stack (default test in the current level)
    # ImGuiPopupFlags_AnyPopup                = ImGuiPopupFlags_AnyPopupId | ImGuiPopupFlags_AnyPopupLevel,    /* original C++ signature */
    # }
    any_popup = enum.auto()  # (= PopupFlags_AnyPopupId | PopupFlags_AnyPopupLevel)

class SelectableFlags_(enum.Enum):
    """Flags for ImGui::Selectable()"""

    # ImGuiSelectableFlags_None               = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiSelectableFlags_NoAutoClosePopups  = 1 << 0,       /* original C++ signature */
    no_auto_close_popups = (
        enum.auto()
    )  # (= 1 << 0)  # Clicking this doesn't close parent popup window (overrides ImGuiItemFlags_AutoClosePopups)
    # ImGuiSelectableFlags_SpanAllColumns     = 1 << 1,       /* original C++ signature */
    span_all_columns = (
        enum.auto()
    )  # (= 1 << 1)  # Frame will span all columns of its container table (text will still fit in current column)
    # ImGuiSelectableFlags_AllowDoubleClick   = 1 << 2,       /* original C++ signature */
    allow_double_click = enum.auto()  # (= 1 << 2)  # Generate press events on double clicks too
    # ImGuiSelectableFlags_Disabled           = 1 << 3,       /* original C++ signature */
    disabled = enum.auto()  # (= 1 << 3)  # Cannot be selected, display grayed out text
    # ImGuiSelectableFlags_AllowOverlap       = 1 << 4,       /* original C++ signature */
    allow_overlap = enum.auto()  # (= 1 << 4)  # (WIP) Hit testing to allow subsequent widgets to overlap this one
    # ImGuiSelectableFlags_Highlight          = 1 << 5,       /* original C++ signature */
    highlight = enum.auto()  # (= 1 << 5)  # Make the item be displayed as if it is hovered

class ComboFlags_(enum.Enum):
    """Flags for ImGui::BeginCombo()"""

    # ImGuiComboFlags_None                    = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiComboFlags_PopupAlignLeft          = 1 << 0,       /* original C++ signature */
    popup_align_left = enum.auto()  # (= 1 << 0)  # Align the popup toward the left by default
    # ImGuiComboFlags_HeightSmall             = 1 << 1,       /* original C++ signature */
    height_small = (
        enum.auto()
    )  # (= 1 << 1)  # Max ~4 items visible. Tip: If you want your combo popup to be a specific size you can use SetNextWindowSizeConstraints() prior to calling BeginCombo()
    # ImGuiComboFlags_HeightRegular           = 1 << 2,       /* original C++ signature */
    height_regular = enum.auto()  # (= 1 << 2)  # Max ~8 items visible (default)
    # ImGuiComboFlags_HeightLarge             = 1 << 3,       /* original C++ signature */
    height_large = enum.auto()  # (= 1 << 3)  # Max ~20 items visible
    # ImGuiComboFlags_HeightLargest           = 1 << 4,       /* original C++ signature */
    height_largest = enum.auto()  # (= 1 << 4)  # As many fitting items as possible
    # ImGuiComboFlags_NoArrowButton           = 1 << 5,       /* original C++ signature */
    no_arrow_button = enum.auto()  # (= 1 << 5)  # Display on the preview box without the square arrow button
    # ImGuiComboFlags_NoPreview               = 1 << 6,       /* original C++ signature */
    no_preview = enum.auto()  # (= 1 << 6)  # Display only a square arrow button
    # ImGuiComboFlags_WidthFitPreview         = 1 << 7,       /* original C++ signature */
    width_fit_preview = enum.auto()  # (= 1 << 7)  # Width dynamically calculated from preview contents
    # ImGuiComboFlags_HeightMask_             = ImGuiComboFlags_HeightSmall | ImGuiComboFlags_HeightRegular | ImGuiComboFlags_HeightLarge | ImGuiComboFlags_HeightLargest,    /* original C++ signature */
    # }
    height_mask_ = (
        enum.auto()
    )  # (= ComboFlags_HeightSmall | ComboFlags_HeightRegular | ComboFlags_HeightLarge | ComboFlags_HeightLargest)

class TabBarFlags_(enum.Enum):
    """Flags for ImGui::BeginTabBar()"""

    # ImGuiTabBarFlags_None                           = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTabBarFlags_Reorderable                    = 1 << 0,       /* original C++ signature */
    reorderable = (
        enum.auto()
    )  # (= 1 << 0)  # Allow manually dragging tabs to re-order them + New tabs are appended at the end of list
    # ImGuiTabBarFlags_AutoSelectNewTabs              = 1 << 1,       /* original C++ signature */
    auto_select_new_tabs = enum.auto()  # (= 1 << 1)  # Automatically select new tabs when they appear
    # ImGuiTabBarFlags_TabListPopupButton             = 1 << 2,       /* original C++ signature */
    tab_list_popup_button = enum.auto()  # (= 1 << 2)  # Disable buttons to open the tab list popup
    # ImGuiTabBarFlags_NoCloseWithMiddleMouseButton   = 1 << 3,       /* original C++ signature */
    no_close_with_middle_mouse_button = (
        enum.auto()
    )  # (= 1 << 3)  # Disable behavior of closing tabs (that are submitted with p_open != None) with middle mouse button. You may handle this behavior manually on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = False.
    # ImGuiTabBarFlags_NoTabListScrollingButtons      = 1 << 4,       /* original C++ signature */
    no_tab_list_scrolling_buttons = (
        enum.auto()
    )  # (= 1 << 4)  # Disable scrolling buttons (apply when fitting policy is ImGuiTabBarFlags_FittingPolicyScroll)
    # ImGuiTabBarFlags_NoTooltip                      = 1 << 5,       /* original C++ signature */
    no_tooltip = enum.auto()  # (= 1 << 5)  # Disable tooltips when hovering a tab
    # ImGuiTabBarFlags_DrawSelectedOverline           = 1 << 6,       /* original C++ signature */
    draw_selected_overline = enum.auto()  # (= 1 << 6)  # Draw selected overline markers over selected tab
    # ImGuiTabBarFlags_FittingPolicyResizeDown        = 1 << 7,       /* original C++ signature */
    fitting_policy_resize_down = enum.auto()  # (= 1 << 7)  # Resize tabs when they don't fit
    # ImGuiTabBarFlags_FittingPolicyScroll            = 1 << 8,       /* original C++ signature */
    fitting_policy_scroll = enum.auto()  # (= 1 << 8)  # Add scroll buttons when tabs don't fit
    # ImGuiTabBarFlags_FittingPolicyMask_             = ImGuiTabBarFlags_FittingPolicyResizeDown | ImGuiTabBarFlags_FittingPolicyScroll,    /* original C++ signature */
    fitting_policy_mask_ = enum.auto()  # (= TabBarFlags_FittingPolicyResizeDown | TabBarFlags_FittingPolicyScroll)
    # ImGuiTabBarFlags_FittingPolicyDefault_          = ImGuiTabBarFlags_FittingPolicyResizeDown,    /* original C++ signature */
    # }
    fitting_policy_default_ = enum.auto()  # (= TabBarFlags_FittingPolicyResizeDown)

class TabItemFlags_(enum.Enum):
    """Flags for ImGui::BeginTabItem()"""

    # ImGuiTabItemFlags_None                          = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTabItemFlags_UnsavedDocument               = 1 << 0,       /* original C++ signature */
    unsaved_document = (
        enum.auto()
    )  # (= 1 << 0)  # Display a dot next to the title + set ImGuiTabItemFlags_NoAssumedClosure.
    # ImGuiTabItemFlags_SetSelected                   = 1 << 1,       /* original C++ signature */
    set_selected = (
        enum.auto()
    )  # (= 1 << 1)  # Trigger flag to programmatically make the tab selected when calling BeginTabItem()
    # ImGuiTabItemFlags_NoCloseWithMiddleMouseButton  = 1 << 2,       /* original C++ signature */
    no_close_with_middle_mouse_button = (
        enum.auto()
    )  # (= 1 << 2)  # Disable behavior of closing tabs (that are submitted with p_open != None) with middle mouse button. You may handle this behavior manually on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = False.
    # ImGuiTabItemFlags_NoPushId                      = 1 << 3,       /* original C++ signature */
    no_push_id = enum.auto()  # (= 1 << 3)  # Don't call PushID()/PopID() on BeginTabItem()/EndTabItem()
    # ImGuiTabItemFlags_NoTooltip                     = 1 << 4,       /* original C++ signature */
    no_tooltip = enum.auto()  # (= 1 << 4)  # Disable tooltip for the given tab
    # ImGuiTabItemFlags_NoReorder                     = 1 << 5,       /* original C++ signature */
    no_reorder = enum.auto()  # (= 1 << 5)  # Disable reordering this tab or having another tab cross over this tab
    # ImGuiTabItemFlags_Leading                       = 1 << 6,       /* original C++ signature */
    leading = (
        enum.auto()
    )  # (= 1 << 6)  # Enforce the tab position to the left of the tab bar (after the tab list popup button)
    # ImGuiTabItemFlags_Trailing                      = 1 << 7,       /* original C++ signature */
    trailing = (
        enum.auto()
    )  # (= 1 << 7)  # Enforce the tab position to the right of the tab bar (before the scrolling buttons)
    # ImGuiTabItemFlags_NoAssumedClosure              = 1 << 8,       /* original C++ signature */
    no_assumed_closure = (
        enum.auto()
    )  # (= 1 << 8)  # Tab is selected when trying to close + closure is not immediately assumed (will wait for user to stop submitting the tab). Otherwise closure is assumed when pressing the X, so if you keep submitting the tab may reappear at end of tab bar.

class FocusedFlags_(enum.Enum):
    """Flags for ImGui::IsWindowFocused()"""

    # ImGuiFocusedFlags_None                          = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiFocusedFlags_ChildWindows                  = 1 << 0,       /* original C++ signature */
    child_windows = enum.auto()  # (= 1 << 0)  # Return True if any children of the window is focused
    # ImGuiFocusedFlags_RootWindow                    = 1 << 1,       /* original C++ signature */
    root_window = enum.auto()  # (= 1 << 1)  # Test from root window (top most parent of the current hierarchy)
    # ImGuiFocusedFlags_AnyWindow                     = 1 << 2,       /* original C++ signature */
    any_window = (
        enum.auto()
    )  # (= 1 << 2)  # Return True if any window is focused. Important: If you are trying to tell how to dispatch your low-level inputs, do NOT use this. Use 'io.WantCaptureMouse' instead! Please read the FAQ!
    # ImGuiFocusedFlags_NoPopupHierarchy              = 1 << 3,       /* original C++ signature */
    no_popup_hierarchy = (
        enum.auto()
    )  # (= 1 << 3)  # Do not consider popup hierarchy (do not treat popup emitter as parent of popup) (when used with _ChildWindows or _RootWindow)
    # ImGuiFocusedFlags_DockHierarchy                 = 1 << 4,       /* original C++ signature */
    dock_hierarchy = (
        enum.auto()
    )  # (= 1 << 4)  # Consider docking hierarchy (treat dockspace host as parent of docked window) (when used with _ChildWindows or _RootWindow)
    # ImGuiFocusedFlags_RootAndChildWindows           = ImGuiFocusedFlags_RootWindow | ImGuiFocusedFlags_ChildWindows,    /* original C++ signature */
    # }
    root_and_child_windows = enum.auto()  # (= FocusedFlags_RootWindow | FocusedFlags_ChildWindows)

class HoveredFlags_(enum.Enum):
    """Flags for ImGui::IsItemHovered(), ImGui::IsWindowHovered()
    Note: if you are trying to check whether your mouse should be dispatched to Dear ImGui or to your app, you should use 'io.WantCaptureMouse' instead! Please read the FAQ!
    Note: windows with the ImGuiWindowFlags_NoInputs flag are ignored by IsWindowHovered() calls.
    """

    # ImGuiHoveredFlags_None                          = 0,            /* original C++ signature */
    none = (
        enum.auto()
    )  # (= 0)  # Return True if directly over the item/window, not obstructed by another window, not obstructed by an active popup or modal blocking inputs under them.
    # ImGuiHoveredFlags_ChildWindows                  = 1 << 0,       /* original C++ signature */
    child_windows = (
        enum.auto()
    )  # (= 1 << 0)  # IsWindowHovered() only: Return True if any children of the window is hovered
    # ImGuiHoveredFlags_RootWindow                    = 1 << 1,       /* original C++ signature */
    root_window = (
        enum.auto()
    )  # (= 1 << 1)  # IsWindowHovered() only: Test from root window (top most parent of the current hierarchy)
    # ImGuiHoveredFlags_AnyWindow                     = 1 << 2,       /* original C++ signature */
    any_window = enum.auto()  # (= 1 << 2)  # IsWindowHovered() only: Return True if any window is hovered
    # ImGuiHoveredFlags_NoPopupHierarchy              = 1 << 3,       /* original C++ signature */
    no_popup_hierarchy = (
        enum.auto()
    )  # (= 1 << 3)  # IsWindowHovered() only: Do not consider popup hierarchy (do not treat popup emitter as parent of popup) (when used with _ChildWindows or _RootWindow)
    # ImGuiHoveredFlags_DockHierarchy                 = 1 << 4,       /* original C++ signature */
    dock_hierarchy = (
        enum.auto()
    )  # (= 1 << 4)  # IsWindowHovered() only: Consider docking hierarchy (treat dockspace host as parent of docked window) (when used with _ChildWindows or _RootWindow)
    # ImGuiHoveredFlags_AllowWhenBlockedByPopup       = 1 << 5,       /* original C++ signature */
    allow_when_blocked_by_popup = (
        enum.auto()
    )  # (= 1 << 5)  # Return True even if a popup window is normally blocking access to this item/window
    # ImGuiHoveredFlags_AllowWhenBlockedByModal     = 1 << 6,   // Return True even if a modal popup window is normally blocking access to this item/window. FIXME-TODO: Unavailable yet.
    # ImGuiHoveredFlags_AllowWhenBlockedByActiveItem  = 1 << 7,       /* original C++ signature */
    allow_when_blocked_by_active_item = (
        enum.auto()
    )  # (= 1 << 7)  # Return True even if an active item is blocking access to this item/window. Useful for Drag and Drop patterns.
    # ImGuiHoveredFlags_AllowWhenOverlappedByItem     = 1 << 8,       /* original C++ signature */
    allow_when_overlapped_by_item = (
        enum.auto()
    )  # (= 1 << 8)  # IsItemHovered() only: Return True even if the item uses AllowOverlap mode and is overlapped by another hoverable item.
    # ImGuiHoveredFlags_AllowWhenOverlappedByWindow   = 1 << 9,       /* original C++ signature */
    allow_when_overlapped_by_window = (
        enum.auto()
    )  # (= 1 << 9)  # IsItemHovered() only: Return True even if the position is obstructed or overlapped by another window.
    # ImGuiHoveredFlags_AllowWhenDisabled             = 1 << 10,      /* original C++ signature */
    allow_when_disabled = enum.auto()  # (= 1 << 10)  # IsItemHovered() only: Return True even if the item is disabled
    # ImGuiHoveredFlags_NoNavOverride                 = 1 << 11,      /* original C++ signature */
    no_nav_override = (
        enum.auto()
    )  # (= 1 << 11)  # IsItemHovered() only: Disable using keyboard/gamepad navigation state when active, always query mouse
    # ImGuiHoveredFlags_AllowWhenOverlapped           = ImGuiHoveredFlags_AllowWhenOverlappedByItem | ImGuiHoveredFlags_AllowWhenOverlappedByWindow,    /* original C++ signature */
    allow_when_overlapped = (
        enum.auto()
    )  # (= HoveredFlags_AllowWhenOverlappedByItem | HoveredFlags_AllowWhenOverlappedByWindow)
    # ImGuiHoveredFlags_RectOnly                      = ImGuiHoveredFlags_AllowWhenBlockedByPopup | ImGuiHoveredFlags_AllowWhenBlockedByActiveItem | ImGuiHoveredFlags_AllowWhenOverlapped,    /* original C++ signature */
    rect_only = (
        enum.auto()
    )  # (= HoveredFlags_AllowWhenBlockedByPopup | HoveredFlags_AllowWhenBlockedByActiveItem | HoveredFlags_AllowWhenOverlapped)
    # ImGuiHoveredFlags_RootAndChildWindows           = ImGuiHoveredFlags_RootWindow | ImGuiHoveredFlags_ChildWindows,    /* original C++ signature */
    root_and_child_windows = enum.auto()  # (= HoveredFlags_RootWindow | HoveredFlags_ChildWindows)

    # Tooltips mode
    # - typically used in IsItemHovered() + SetTooltip() sequence.
    # - this is a shortcut to pull flags from 'style.HoverFlagsForTooltipMouse' or 'style.HoverFlagsForTooltipNav' where you can reconfigure desired behavior.
    #   e.g. 'TooltipHoveredFlagsForMouse' defaults to 'ImGuiHoveredFlags_Stationary | ImGuiHoveredFlags_DelayShort'.
    # - for frequently actioned or hovered items providing a tooltip, you want may to use ImGuiHoveredFlags_ForTooltip (stationary + delay) so the tooltip doesn't show too often.
    # - for items which main purpose is to be hovered, or items with low affordance, or in less consistent apps, prefer no delay or shorter delay.
    # ImGuiHoveredFlags_ForTooltip                    = 1 << 12,      /* original C++ signature */
    for_tooltip = (
        enum.auto()
    )  # (= 1 << 12)  # Shortcut for standard flags when using IsItemHovered() + SetTooltip() sequence.

    # (Advanced) Mouse Hovering delays.
    # - generally you can use ImGuiHoveredFlags_ForTooltip to use application-standardized flags.
    # - use those if you need specific overrides.
    # ImGuiHoveredFlags_Stationary                    = 1 << 13,      /* original C++ signature */
    stationary = (
        enum.auto()
    )  # (= 1 << 13)  # Require mouse to be stationary for style.HoverStationaryDelay (~0.15 sec) _at least one time_. After this, can move on same item/window. Using the stationary test tends to reduces the need for a long delay.
    # ImGuiHoveredFlags_DelayNone                     = 1 << 14,      /* original C++ signature */
    delay_none = (
        enum.auto()
    )  # (= 1 << 14)  # IsItemHovered() only: Return True immediately (default). As this is the default you generally ignore this.
    # ImGuiHoveredFlags_DelayShort                    = 1 << 15,      /* original C++ signature */
    delay_short = (
        enum.auto()
    )  # (= 1 << 15)  # IsItemHovered() only: Return True after style.HoverDelayShort elapsed (~0.15 sec) (shared between items) + requires mouse to be stationary for style.HoverStationaryDelay (once per item).
    # ImGuiHoveredFlags_DelayNormal                   = 1 << 16,      /* original C++ signature */
    delay_normal = (
        enum.auto()
    )  # (= 1 << 16)  # IsItemHovered() only: Return True after style.HoverDelayNormal elapsed (~0.40 sec) (shared between items) + requires mouse to be stationary for style.HoverStationaryDelay (once per item).
    # ImGuiHoveredFlags_NoSharedDelay                 = 1 << 17,      /* original C++ signature */
    no_shared_delay = (
        enum.auto()
    )  # (= 1 << 17)  # IsItemHovered() only: Disable shared delay system where moving from one item to the next keeps the previous timer for a short time (standard for tooltips with long delays)

class DockNodeFlags_(enum.Enum):
    """Flags for ImGui::DockSpace(), shared/inherited by child nodes.
    (Some flags can be applied to individual nodes directly)
    FIXME-DOCK: Also see ImGuiDockNodeFlagsPrivate_ which may involve using the WIP and internal DockBuilder api.
    """

    # ImGuiDockNodeFlags_None                         = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiDockNodeFlags_KeepAliveOnly                = 1 << 0,       /* original C++ signature */
    keep_alive_only = (
        enum.auto()
    )  # (= 1 << 0)  #       // Don't display the dockspace node but keep it alive. Windows docked into this dockspace node won't be undocked.
    # ImGuiDockNodeFlags_NoCentralNode              = 1 << 1,   //       // Disable Central Node (the node which can stay empty)
    # ImGuiDockNodeFlags_NoDockingOverCentralNode     = 1 << 2,       /* original C++ signature */
    no_docking_over_central_node = (
        enum.auto()
    )  # (= 1 << 2)  #       // Disable docking over the Central Node, which will be always kept empty.
    # ImGuiDockNodeFlags_PassthruCentralNode          = 1 << 3,       /* original C++ signature */
    passthru_central_node = (
        enum.auto()
    )  # (= 1 << 3)  #       // Enable passthru dockspace: 1) DockSpace() will render a ImGuiCol_WindowBg background covering everything excepted the Central Node when empty. Meaning the host window should probably use SetNextWindowBgAlpha(0.0) prior to Begin() when using this. 2) When Central Node is empty: let inputs pass-through + won't display a DockingEmptyBg background. See demo for details.
    # ImGuiDockNodeFlags_NoDockingSplit               = 1 << 4,       /* original C++ signature */
    no_docking_split = enum.auto()  # (= 1 << 4)  #       // Disable other windows/nodes from splitting this node.
    # ImGuiDockNodeFlags_NoResize                     = 1 << 5,       /* original C++ signature */
    no_resize = (
        enum.auto()
    )  # (= 1 << 5)  # Saved // Disable resizing node using the splitter/separators. Useful with programmatically setup dockspaces.
    # ImGuiDockNodeFlags_AutoHideTabBar               = 1 << 6,       /* original C++ signature */
    auto_hide_tab_bar = (
        enum.auto()
    )  # (= 1 << 6)  #       // Tab bar will automatically hide when there is a single window in the dock node.
    # ImGuiDockNodeFlags_NoUndocking                  = 1 << 7,       /* original C++ signature */
    no_undocking = enum.auto()  # (= 1 << 7)  #       // Disable undocking this node.

class DragDropFlags_(enum.Enum):
    """Flags for ImGui::BeginDragDropSource(), ImGui::AcceptDragDropPayload()"""

    # ImGuiDragDropFlags_None                         = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # BeginDragDropSource() flags
    # ImGuiDragDropFlags_SourceNoPreviewTooltip       = 1 << 0,       /* original C++ signature */
    source_no_preview_tooltip = (
        enum.auto()
    )  # (= 1 << 0)  # Disable preview tooltip. By default, a successful call to BeginDragDropSource opens a tooltip so you can display a preview or description of the source contents. This flag disables this behavior.
    # ImGuiDragDropFlags_SourceNoDisableHover         = 1 << 1,       /* original C++ signature */
    source_no_disable_hover = (
        enum.auto()
    )  # (= 1 << 1)  # By default, when dragging we clear data so that IsItemHovered() will return False, to avoid subsequent user code submitting tooltips. This flag disables this behavior so you can still call IsItemHovered() on the source item.
    # ImGuiDragDropFlags_SourceNoHoldToOpenOthers     = 1 << 2,       /* original C++ signature */
    source_no_hold_to_open_others = (
        enum.auto()
    )  # (= 1 << 2)  # Disable the behavior that allows to open tree nodes and collapsing header by holding over them while dragging a source item.
    # ImGuiDragDropFlags_SourceAllowNullID            = 1 << 3,       /* original C++ signature */
    source_allow_null_id = (
        enum.auto()
    )  # (= 1 << 3)  # Allow items such as Text(), Image() that have no unique identifier to be used as drag source, by manufacturing a temporary identifier based on their window-relative position. This is extremely unusual within the dear imgui ecosystem and so we made it explicit.
    # ImGuiDragDropFlags_SourceExtern                 = 1 << 4,       /* original C++ signature */
    source_extern = (
        enum.auto()
    )  # (= 1 << 4)  # External source (from outside of dear imgui), won't attempt to read current item/window info. Will always return True. Only one Extern source can be active simultaneously.
    # ImGuiDragDropFlags_PayloadAutoExpire            = 1 << 5,       /* original C++ signature */
    payload_auto_expire = (
        enum.auto()
    )  # (= 1 << 5)  # Automatically expire the payload if the source cease to be submitted (otherwise payloads are persisting while being dragged)
    # ImGuiDragDropFlags_PayloadNoCrossContext        = 1 << 6,       /* original C++ signature */
    payload_no_cross_context = (
        enum.auto()
    )  # (= 1 << 6)  # Hint to specify that the payload may not be copied outside current dear imgui context.
    # ImGuiDragDropFlags_PayloadNoCrossProcess        = 1 << 7,       /* original C++ signature */
    payload_no_cross_process = (
        enum.auto()
    )  # (= 1 << 7)  # Hint to specify that the payload may not be copied outside current process.
    # AcceptDragDropPayload() flags
    # ImGuiDragDropFlags_AcceptBeforeDelivery         = 1 << 10,      /* original C++ signature */
    accept_before_delivery = (
        enum.auto()
    )  # (= 1 << 10)  # AcceptDragDropPayload() will returns True even before the mouse button is released. You can then call IsDelivery() to test if the payload needs to be delivered.
    # ImGuiDragDropFlags_AcceptNoDrawDefaultRect      = 1 << 11,      /* original C++ signature */
    accept_no_draw_default_rect = (
        enum.auto()
    )  # (= 1 << 11)  # Do not draw the default highlight rectangle when hovering over target.
    # ImGuiDragDropFlags_AcceptNoPreviewTooltip       = 1 << 12,      /* original C++ signature */
    accept_no_preview_tooltip = (
        enum.auto()
    )  # (= 1 << 12)  # Request hiding the BeginDragDropSource tooltip from the BeginDragDropTarget site.
    # ImGuiDragDropFlags_AcceptPeekOnly               = ImGuiDragDropFlags_AcceptBeforeDelivery | ImGuiDragDropFlags_AcceptNoDrawDefaultRect,     /* original C++ signature */
    accept_peek_only = (
        enum.auto()
    )  # (= DragDropFlags_AcceptBeforeDelivery | DragDropFlags_AcceptNoDrawDefaultRect)  # For peeking ahead and inspecting the payload before delivery.

# Standard Drag and Drop payload types. You can define you own payload types using short strings. Types starting with '_' are defined by Dear ImGui.

class DataType_(enum.Enum):
    """A primary data type"""

    # ImGuiDataType_S8,           /* original C++ signature */
    s8 = enum.auto()  # (= 0)  # signed char / char (with sensible compilers)
    # ImGuiDataType_U8,           /* original C++ signature */
    u8 = enum.auto()  # (= 1)  # uchar
    # ImGuiDataType_S16,          /* original C++ signature */
    s16 = enum.auto()  # (= 2)  # short
    # ImGuiDataType_U16,          /* original C++ signature */
    u16 = enum.auto()  # (= 3)  # unsigned short
    # ImGuiDataType_S32,          /* original C++ signature */
    s32 = enum.auto()  # (= 4)  # int
    # ImGuiDataType_U32,          /* original C++ signature */
    u32 = enum.auto()  # (= 5)  # unsigned int
    # ImGuiDataType_S64,          /* original C++ signature */
    s64 = enum.auto()  # (= 6)  # long long / __int64
    # ImGuiDataType_U64,          /* original C++ signature */
    u64 = enum.auto()  # (= 7)  # unsigned long long / unsigned __int64
    # ImGuiDataType_Float,        /* original C++ signature */
    float = enum.auto()  # (= 8)  # float
    # ImGuiDataType_Double,       /* original C++ signature */
    double = enum.auto()  # (= 9)  # double
    # ImGuiDataType_Bool,         /* original C++ signature */
    bool = enum.auto()  # (= 10)  # bool (provided for user convenience, not supported by scalar widgets)
    # ImGuiDataType_COUNT    /* original C++ signature */
    # }
    count = enum.auto()  # (= 11)

class Dir(enum.Enum):
    """A cardinal direction"""

    # ImGuiDir_None    = -1,    /* original C++ signature */
    none = enum.auto()  # (= -1)
    # ImGuiDir_Left    = 0,    /* original C++ signature */
    left = enum.auto()  # (= 0)
    # ImGuiDir_Right   = 1,    /* original C++ signature */
    right = enum.auto()  # (= 1)
    # ImGuiDir_Up      = 2,    /* original C++ signature */
    up = enum.auto()  # (= 2)
    # ImGuiDir_Down    = 3,    /* original C++ signature */
    down = enum.auto()  # (= 3)
    # ImGuiDir_COUNT    /* original C++ signature */
    # }
    count = enum.auto()  # (= 4)

class SortDirection(enum.Enum):
    """A sorting direction"""

    # ImGuiSortDirection_None         = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiSortDirection_Ascending    = 1,        /* original C++ signature */
    ascending = enum.auto()  # (= 1)  # Ascending = 0->9, A->Z etc.
    # ImGuiSortDirection_Descending   = 2         /* original C++ signature */
    descending = enum.auto()  # (= 2)  # Descending = 9->0, Z->A etc.

class Key(enum.Enum):
    """A key identifier (ImGuiKey_XXX or ImGuiMod_XXX value): can represent Keyboard, Mouse and Gamepad values.
    All our named keys are >= 512. Keys value 0 to 511 are left unused and were legacy native/opaque key values (< 1.87).
    Support for legacy keys was completely removed in 1.91.5.
    Read details about the 1.87+ transition : https://github.com/ocornut/imgui/issues/4921
    Note that "Keys" related to physical keys and are not the same concept as input "Characters", the later are submitted via io.AddInputCharacter().
    The keyboard key enum values are named after the keys on a standard US keyboard, and on other keyboard types the keys reported may not match the keycaps.
    """

    # Keyboard
    # ImGuiKey_None = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiKey_NamedKey_BEGIN = 512,      /* original C++ signature */
    named_key_begin = enum.auto()  # (= 512)  # First valid key value (other than 0)

    # ImGuiKey_Tab = 512,                 /* original C++ signature */
    tab = enum.auto()  # (= 512)  # == ImGuiKey_NamedKey_BEGIN
    # ImGuiKey_LeftArrow,    /* original C++ signature */
    left_arrow = enum.auto()  # (= 513)
    # ImGuiKey_RightArrow,    /* original C++ signature */
    right_arrow = enum.auto()  # (= 514)
    # ImGuiKey_UpArrow,    /* original C++ signature */
    up_arrow = enum.auto()  # (= 515)
    # ImGuiKey_DownArrow,    /* original C++ signature */
    down_arrow = enum.auto()  # (= 516)
    # ImGuiKey_PageUp,    /* original C++ signature */
    page_up = enum.auto()  # (= 517)
    # ImGuiKey_PageDown,    /* original C++ signature */
    page_down = enum.auto()  # (= 518)
    # ImGuiKey_Home,    /* original C++ signature */
    home = enum.auto()  # (= 519)
    # ImGuiKey_End,    /* original C++ signature */
    end = enum.auto()  # (= 520)
    # ImGuiKey_Insert,    /* original C++ signature */
    insert = enum.auto()  # (= 521)
    # ImGuiKey_Delete,    /* original C++ signature */
    delete = enum.auto()  # (= 522)
    # ImGuiKey_Backspace,    /* original C++ signature */
    backspace = enum.auto()  # (= 523)
    # ImGuiKey_Space,    /* original C++ signature */
    space = enum.auto()  # (= 524)
    # ImGuiKey_Enter,    /* original C++ signature */
    enter = enum.auto()  # (= 525)
    # ImGuiKey_Escape,    /* original C++ signature */
    escape = enum.auto()  # (= 526)
    # ImGuiKey_LeftCtrl,     /* original C++ signature */
    left_ctrl = enum.auto()  # (= 527)
    # ImGuiKey_LeftShift,     /* original C++ signature */
    left_shift = enum.auto()  # (= 528)
    # ImGuiKey_LeftAlt,     /* original C++ signature */
    left_alt = enum.auto()  # (= 529)
    # ImGuiKey_LeftSuper,    /* original C++ signature */
    left_super = enum.auto()  # (= 530)
    # ImGuiKey_RightCtrl,     /* original C++ signature */
    right_ctrl = enum.auto()  # (= 531)
    # ImGuiKey_RightShift,     /* original C++ signature */
    right_shift = enum.auto()  # (= 532)
    # ImGuiKey_RightAlt,     /* original C++ signature */
    right_alt = enum.auto()  # (= 533)
    # ImGuiKey_RightSuper,    /* original C++ signature */
    right_super = enum.auto()  # (= 534)
    # ImGuiKey_Menu,    /* original C++ signature */
    menu = enum.auto()  # (= 535)
    # ImGuiKey_0,     /* original C++ signature */
    _0 = enum.auto()  # (= 536)
    # ImGuiKey_1,     /* original C++ signature */
    _1 = enum.auto()  # (= 537)
    # ImGuiKey_2,     /* original C++ signature */
    _2 = enum.auto()  # (= 538)
    # ImGuiKey_3,     /* original C++ signature */
    _3 = enum.auto()  # (= 539)
    # ImGuiKey_4,     /* original C++ signature */
    _4 = enum.auto()  # (= 540)
    # ImGuiKey_5,     /* original C++ signature */
    _5 = enum.auto()  # (= 541)
    # ImGuiKey_6,     /* original C++ signature */
    _6 = enum.auto()  # (= 542)
    # ImGuiKey_7,     /* original C++ signature */
    _7 = enum.auto()  # (= 543)
    # ImGuiKey_8,     /* original C++ signature */
    _8 = enum.auto()  # (= 544)
    # ImGuiKey_9,    /* original C++ signature */
    _9 = enum.auto()  # (= 545)
    # ImGuiKey_A,     /* original C++ signature */
    a = enum.auto()  # (= 546)
    # ImGuiKey_B,     /* original C++ signature */
    b = enum.auto()  # (= 547)
    # ImGuiKey_C,     /* original C++ signature */
    c = enum.auto()  # (= 548)
    # ImGuiKey_D,     /* original C++ signature */
    d = enum.auto()  # (= 549)
    # ImGuiKey_E,     /* original C++ signature */
    e = enum.auto()  # (= 550)
    # ImGuiKey_F,     /* original C++ signature */
    f = enum.auto()  # (= 551)
    # ImGuiKey_G,     /* original C++ signature */
    g = enum.auto()  # (= 552)
    # ImGuiKey_H,     /* original C++ signature */
    h = enum.auto()  # (= 553)
    # ImGuiKey_I,     /* original C++ signature */
    i = enum.auto()  # (= 554)
    # ImGuiKey_J,    /* original C++ signature */
    j = enum.auto()  # (= 555)
    # ImGuiKey_K,     /* original C++ signature */
    k = enum.auto()  # (= 556)
    # ImGuiKey_L,     /* original C++ signature */
    l = enum.auto()  # (= 557)
    # ImGuiKey_M,     /* original C++ signature */
    m = enum.auto()  # (= 558)
    # ImGuiKey_N,     /* original C++ signature */
    n = enum.auto()  # (= 559)
    # ImGuiKey_O,     /* original C++ signature */
    o = enum.auto()  # (= 560)
    # ImGuiKey_P,     /* original C++ signature */
    p = enum.auto()  # (= 561)
    # ImGuiKey_Q,     /* original C++ signature */
    q = enum.auto()  # (= 562)
    # ImGuiKey_R,     /* original C++ signature */
    r = enum.auto()  # (= 563)
    # ImGuiKey_S,     /* original C++ signature */
    s = enum.auto()  # (= 564)
    # ImGuiKey_T,    /* original C++ signature */
    t = enum.auto()  # (= 565)
    # ImGuiKey_U,     /* original C++ signature */
    u = enum.auto()  # (= 566)
    # ImGuiKey_V,     /* original C++ signature */
    v = enum.auto()  # (= 567)
    # ImGuiKey_W,     /* original C++ signature */
    w = enum.auto()  # (= 568)
    # ImGuiKey_X,     /* original C++ signature */
    x = enum.auto()  # (= 569)
    # ImGuiKey_Y,     /* original C++ signature */
    y = enum.auto()  # (= 570)
    # ImGuiKey_Z,    /* original C++ signature */
    z = enum.auto()  # (= 571)
    # ImGuiKey_F1,     /* original C++ signature */
    f1 = enum.auto()  # (= 572)
    # ImGuiKey_F2,     /* original C++ signature */
    f2 = enum.auto()  # (= 573)
    # ImGuiKey_F3,     /* original C++ signature */
    f3 = enum.auto()  # (= 574)
    # ImGuiKey_F4,     /* original C++ signature */
    f4 = enum.auto()  # (= 575)
    # ImGuiKey_F5,     /* original C++ signature */
    f5 = enum.auto()  # (= 576)
    # ImGuiKey_F6,    /* original C++ signature */
    f6 = enum.auto()  # (= 577)
    # ImGuiKey_F7,     /* original C++ signature */
    f7 = enum.auto()  # (= 578)
    # ImGuiKey_F8,     /* original C++ signature */
    f8 = enum.auto()  # (= 579)
    # ImGuiKey_F9,     /* original C++ signature */
    f9 = enum.auto()  # (= 580)
    # ImGuiKey_F10,     /* original C++ signature */
    f10 = enum.auto()  # (= 581)
    # ImGuiKey_F11,     /* original C++ signature */
    f11 = enum.auto()  # (= 582)
    # ImGuiKey_F12,    /* original C++ signature */
    f12 = enum.auto()  # (= 583)
    # ImGuiKey_F13,     /* original C++ signature */
    f13 = enum.auto()  # (= 584)
    # ImGuiKey_F14,     /* original C++ signature */
    f14 = enum.auto()  # (= 585)
    # ImGuiKey_F15,     /* original C++ signature */
    f15 = enum.auto()  # (= 586)
    # ImGuiKey_F16,     /* original C++ signature */
    f16 = enum.auto()  # (= 587)
    # ImGuiKey_F17,     /* original C++ signature */
    f17 = enum.auto()  # (= 588)
    # ImGuiKey_F18,    /* original C++ signature */
    f18 = enum.auto()  # (= 589)
    # ImGuiKey_F19,     /* original C++ signature */
    f19 = enum.auto()  # (= 590)
    # ImGuiKey_F20,     /* original C++ signature */
    f20 = enum.auto()  # (= 591)
    # ImGuiKey_F21,     /* original C++ signature */
    f21 = enum.auto()  # (= 592)
    # ImGuiKey_F22,     /* original C++ signature */
    f22 = enum.auto()  # (= 593)
    # ImGuiKey_F23,     /* original C++ signature */
    f23 = enum.auto()  # (= 594)
    # ImGuiKey_F24,    /* original C++ signature */
    f24 = enum.auto()  # (= 595)
    # ImGuiKey_Apostrophe,            /* original C++ signature */
    apostrophe = enum.auto()  # (= 596)  # '
    # ImGuiKey_Comma,                 /* original C++ signature */
    comma = enum.auto()  # (= 597)  # ,
    # ImGuiKey_Minus,                 /* original C++ signature */
    minus = enum.auto()  # (= 598)  # -
    # ImGuiKey_Period,                /* original C++ signature */
    period = enum.auto()  # (= 599)  # .
    # ImGuiKey_Slash,                 /* original C++ signature */
    slash = enum.auto()  # (= 600)  # /
    # ImGuiKey_Semicolon,             /* original C++ signature */
    semicolon = enum.auto()  # (= 601)  # ;
    # ImGuiKey_Equal,                 /* original C++ signature */
    equal = enum.auto()  # (= 602)  # =
    # ImGuiKey_LeftBracket,           /* original C++ signature */
    left_bracket = enum.auto()  # (= 603)  # [
    # ImGuiKey_Backslash,             /* original C++ signature */
    backslash = enum.auto()  # (= 604)  # \ (this text inhibit multiline comment caused by backslash)
    # ImGuiKey_RightBracket,          /* original C++ signature */
    right_bracket = enum.auto()  # (= 605)  # ]
    # ImGuiKey_GraveAccent,           /* original C++ signature */
    grave_accent = enum.auto()  # (= 606)  # `
    # ImGuiKey_CapsLock,    /* original C++ signature */
    caps_lock = enum.auto()  # (= 607)
    # ImGuiKey_ScrollLock,    /* original C++ signature */
    scroll_lock = enum.auto()  # (= 608)
    # ImGuiKey_NumLock,    /* original C++ signature */
    num_lock = enum.auto()  # (= 609)
    # ImGuiKey_PrintScreen,    /* original C++ signature */
    print_screen = enum.auto()  # (= 610)
    # ImGuiKey_Pause,    /* original C++ signature */
    pause = enum.auto()  # (= 611)
    # ImGuiKey_Keypad0,     /* original C++ signature */
    keypad0 = enum.auto()  # (= 612)
    # ImGuiKey_Keypad1,     /* original C++ signature */
    keypad1 = enum.auto()  # (= 613)
    # ImGuiKey_Keypad2,     /* original C++ signature */
    keypad2 = enum.auto()  # (= 614)
    # ImGuiKey_Keypad3,     /* original C++ signature */
    keypad3 = enum.auto()  # (= 615)
    # ImGuiKey_Keypad4,    /* original C++ signature */
    keypad4 = enum.auto()  # (= 616)
    # ImGuiKey_Keypad5,     /* original C++ signature */
    keypad5 = enum.auto()  # (= 617)
    # ImGuiKey_Keypad6,     /* original C++ signature */
    keypad6 = enum.auto()  # (= 618)
    # ImGuiKey_Keypad7,     /* original C++ signature */
    keypad7 = enum.auto()  # (= 619)
    # ImGuiKey_Keypad8,     /* original C++ signature */
    keypad8 = enum.auto()  # (= 620)
    # ImGuiKey_Keypad9,    /* original C++ signature */
    keypad9 = enum.auto()  # (= 621)
    # ImGuiKey_KeypadDecimal,    /* original C++ signature */
    keypad_decimal = enum.auto()  # (= 622)
    # ImGuiKey_KeypadDivide,    /* original C++ signature */
    keypad_divide = enum.auto()  # (= 623)
    # ImGuiKey_KeypadMultiply,    /* original C++ signature */
    keypad_multiply = enum.auto()  # (= 624)
    # ImGuiKey_KeypadSubtract,    /* original C++ signature */
    keypad_subtract = enum.auto()  # (= 625)
    # ImGuiKey_KeypadAdd,    /* original C++ signature */
    keypad_add = enum.auto()  # (= 626)
    # ImGuiKey_KeypadEnter,    /* original C++ signature */
    keypad_enter = enum.auto()  # (= 627)
    # ImGuiKey_KeypadEqual,    /* original C++ signature */
    keypad_equal = enum.auto()  # (= 628)
    # ImGuiKey_AppBack,                   /* original C++ signature */
    app_back = enum.auto()  # (= 629)  # Available on some keyboard/mouses. Often referred as "Browser Back"
    # ImGuiKey_AppForward,    /* original C++ signature */
    app_forward = enum.auto()  # (= 630)

    # Gamepad (some of those are analog values, 0.0 to 1.0)                          // NAVIGATION ACTION
    # (download controller mapping PNG/PSD at http://dearimgui.com/controls_sheets)
    # ImGuiKey_GamepadStart,              /* original C++ signature */
    gamepad_start = enum.auto()  # (= 631)  # Menu (Xbox)      + (Switch)   Start/Options (PS)
    # ImGuiKey_GamepadBack,               /* original C++ signature */
    gamepad_back = enum.auto()  # (= 632)  # View (Xbox)      - (Switch)   Share (PS)
    # ImGuiKey_GamepadFaceLeft,           /* original C++ signature */
    gamepad_face_left = (
        enum.auto()
    )  # (= 633)  # X (Xbox)         Y (Switch)   Square (PS)        // Tap: Toggle Menu. Hold: Windowing mode (Focus/Move/Resize windows)
    # ImGuiKey_GamepadFaceRight,          /* original C++ signature */
    gamepad_face_right = (
        enum.auto()
    )  # (= 634)  # B (Xbox)         A (Switch)   Circle (PS)        // Cancel / Close / Exit
    # ImGuiKey_GamepadFaceUp,             /* original C++ signature */
    gamepad_face_up = (
        enum.auto()
    )  # (= 635)  # Y (Xbox)         X (Switch)   Triangle (PS)      // Text Input / On-screen Keyboard
    # ImGuiKey_GamepadFaceDown,           /* original C++ signature */
    gamepad_face_down = (
        enum.auto()
    )  # (= 636)  # A (Xbox)         B (Switch)   Cross (PS)         // Activate / Open / Toggle / Tweak
    # ImGuiKey_GamepadDpadLeft,           /* original C++ signature */
    gamepad_dpad_left = (
        enum.auto()
    )  # (= 637)  # D-pad Left                                       // Move / Tweak / Resize Window (in Windowing mode)
    # ImGuiKey_GamepadDpadRight,          /* original C++ signature */
    gamepad_dpad_right = (
        enum.auto()
    )  # (= 638)  # D-pad Right                                      // Move / Tweak / Resize Window (in Windowing mode)
    # ImGuiKey_GamepadDpadUp,             /* original C++ signature */
    gamepad_dpad_up = (
        enum.auto()
    )  # (= 639)  # D-pad Up                                         // Move / Tweak / Resize Window (in Windowing mode)
    # ImGuiKey_GamepadDpadDown,           /* original C++ signature */
    gamepad_dpad_down = (
        enum.auto()
    )  # (= 640)  # D-pad Down                                       // Move / Tweak / Resize Window (in Windowing mode)
    # ImGuiKey_GamepadL1,                 /* original C++ signature */
    gamepad_l1 = (
        enum.auto()
    )  # (= 641)  # L Bumper (Xbox)  L (Switch)   L1 (PS)            // Tweak Slower / Focus Previous (in Windowing mode)
    # ImGuiKey_GamepadR1,                 /* original C++ signature */
    gamepad_r1 = (
        enum.auto()
    )  # (= 642)  # R Bumper (Xbox)  R (Switch)   R1 (PS)            // Tweak Faster / Focus Next (in Windowing mode)
    # ImGuiKey_GamepadL2,                 /* original C++ signature */
    gamepad_l2 = enum.auto()  # (= 643)  # L Trig. (Xbox)   ZL (Switch)  L2 (PS) [Analog]
    # ImGuiKey_GamepadR2,                 /* original C++ signature */
    gamepad_r2 = enum.auto()  # (= 644)  # R Trig. (Xbox)   ZR (Switch)  R2 (PS) [Analog]
    # ImGuiKey_GamepadL3,                 /* original C++ signature */
    gamepad_l3 = enum.auto()  # (= 645)  # L Stick (Xbox)   L3 (Switch)  L3 (PS)
    # ImGuiKey_GamepadR3,                 /* original C++ signature */
    gamepad_r3 = enum.auto()  # (= 646)  # R Stick (Xbox)   R3 (Switch)  R3 (PS)
    # ImGuiKey_GamepadLStickLeft,         /* original C++ signature */
    gamepad_l_stick_left = (
        enum.auto()
    )  # (= 647)  # [Analog]                                         // Move Window (in Windowing mode)
    # ImGuiKey_GamepadLStickRight,        /* original C++ signature */
    gamepad_l_stick_right = (
        enum.auto()
    )  # (= 648)  # [Analog]                                         // Move Window (in Windowing mode)
    # ImGuiKey_GamepadLStickUp,           /* original C++ signature */
    gamepad_l_stick_up = (
        enum.auto()
    )  # (= 649)  # [Analog]                                         // Move Window (in Windowing mode)
    # ImGuiKey_GamepadLStickDown,         /* original C++ signature */
    gamepad_l_stick_down = (
        enum.auto()
    )  # (= 650)  # [Analog]                                         // Move Window (in Windowing mode)
    # ImGuiKey_GamepadRStickLeft,         /* original C++ signature */
    gamepad_r_stick_left = enum.auto()  # (= 651)  # [Analog]
    # ImGuiKey_GamepadRStickRight,        /* original C++ signature */
    gamepad_r_stick_right = enum.auto()  # (= 652)  # [Analog]
    # ImGuiKey_GamepadRStickUp,           /* original C++ signature */
    gamepad_r_stick_up = enum.auto()  # (= 653)  # [Analog]
    # ImGuiKey_GamepadRStickDown,         /* original C++ signature */
    gamepad_r_stick_down = enum.auto()  # (= 654)  # [Analog]

    # ImGuiKey_MouseLeft,     /* original C++ signature */
    # Aliases: Mouse Buttons (auto-submitted from AddMouseButtonEvent() calls)
    # - This is mirroring the data also written to io.MouseDown[], io.MouseWheel, in a format allowing them to be accessed via standard key API.
    mouse_left = enum.auto()  # (= 655)
    # ImGuiKey_MouseRight,     /* original C++ signature */
    mouse_right = enum.auto()  # (= 656)
    # ImGuiKey_MouseMiddle,     /* original C++ signature */
    mouse_middle = enum.auto()  # (= 657)
    # ImGuiKey_MouseX1,     /* original C++ signature */
    mouse_x1 = enum.auto()  # (= 658)
    # ImGuiKey_MouseX2,     /* original C++ signature */
    mouse_x2 = enum.auto()  # (= 659)
    # ImGuiKey_MouseWheelX,     /* original C++ signature */
    mouse_wheel_x = enum.auto()  # (= 660)
    # ImGuiKey_MouseWheelY,    /* original C++ signature */
    mouse_wheel_y = enum.auto()  # (= 661)

    # ImGuiKey_ReservedForModCtrl,     /* original C++ signature */
    # [Internal] Reserved for mod storage
    reserved_for_mod_ctrl = enum.auto()  # (= 662)
    # ImGuiKey_ReservedForModShift,     /* original C++ signature */
    reserved_for_mod_shift = enum.auto()  # (= 663)
    # ImGuiKey_ReservedForModAlt,     /* original C++ signature */
    reserved_for_mod_alt = enum.auto()  # (= 664)
    # ImGuiKey_ReservedForModSuper,    /* original C++ signature */
    reserved_for_mod_super = enum.auto()  # (= 665)
    # ImGuiKey_NamedKey_END,    /* original C++ signature */
    named_key_end = enum.auto()  # (= 666)

    # Keyboard Modifiers (explicitly submitted by backend via AddKeyEvent() calls)
    # - This is mirroring the data also written to io.KeyCtrl, io.KeyShift, io.KeyAlt, io.KeySuper, in a format allowing
    #   them to be accessed via standard key API, allowing calls such as IsKeyPressed(), IsKeyReleased(), querying duration etc.
    # - Code polling every key (e.g. an interface to detect a key press for input mapping) might want to ignore those
    #   and prefer using the real keys (e.g. ImGuiKey_LeftCtrl, ImGuiKey_RightCtrl instead of ImGuiMod_Ctrl).
    # - In theory the value of keyboard modifiers should be roughly equivalent to a logical or of the equivalent left/right keys.
    #   In practice: it's complicated; mods are often provided from different sources. Keyboard layout, IME, sticky keys and
    #   backends tend to interfere and break that equivalence. The safer decision is to relay that ambiguity down to the end-user...
    # - On macOS, we swap Cmd(Super) and Ctrl keys at the time of the io.AddKeyEvent() call.
    # ImGuiMod_None                   = 0,    /* original C++ signature */
    mod_none = enum.auto()  # (= 0)
    # ImGuiMod_Ctrl                   = 1 << 12,     /* original C++ signature */
    mod_ctrl = enum.auto()  # (= 1 << 12)  # Ctrl (non-macOS), Cmd (macOS)
    # ImGuiMod_Shift                  = 1 << 13,     /* original C++ signature */
    mod_shift = enum.auto()  # (= 1 << 13)  # Shift
    # ImGuiMod_Alt                    = 1 << 14,     /* original C++ signature */
    mod_alt = enum.auto()  # (= 1 << 14)  # Option/Menu
    # ImGuiMod_Super                  = 1 << 15,     /* original C++ signature */
    mod_super = enum.auto()  # (= 1 << 15)  # Windows/Super (non-macOS), Ctrl (macOS)
    # ImGuiMod_Mask_                  = 0xF000,      /* original C++ signature */
    mod_mask_ = enum.auto()  # (= 0xF000)  # 4-bits

    # ImGuiKey_NamedKey_COUNT         = ImGuiKey_NamedKey_END - ImGuiKey_NamedKey_BEGIN,    /* original C++ signature */
    # [Internal] If you need to iterate all keys (for e.g. an input mapper) you may use ImGuiKey_NamedKey_BEGIN..ImGuiKey_NamedKey_END.
    named_key_count = enum.auto()  # (= Key_NamedKey_END - Key_NamedKey_BEGIN)
    # ImGuiKey_KeysData_SIZE        = ImGuiKey_NamedKey_COUNT,  // Size of KeysData[]: only hold named keys
    # ImGuiKey_KeysData_OFFSET      = ImGuiKey_NamedKey_BEGIN,  // Accesses to io.KeysData[] must use (key - ImGuiKey_NamedKey_BEGIN) index.

class InputFlags_(enum.Enum):
    """Flags for Shortcut(), SetNextItemShortcut(),
    (and for upcoming extended versions of IsKeyPressed(), IsMouseClicked(), Shortcut(), SetKeyOwner(), SetItemKeyOwner() that are still in imgui_internal.h)
    Don't mistake with ImGuiInputTextFlags! (which is for ImGui::InputText() function)
    """

    # ImGuiInputFlags_None                    = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiInputFlags_Repeat                  = 1 << 0,       /* original C++ signature */
    repeat = (
        enum.auto()
    )  # (= 1 << 0)  # Enable repeat. Return True on successive repeats. Default for legacy IsKeyPressed(). NOT Default for legacy IsMouseClicked(). MUST BE == 1.

    # Flags for Shortcut(), SetNextItemShortcut()
    # - Routing policies: RouteGlobal+OverActive >> RouteActive or RouteFocused (if owner is active item) >> RouteGlobal+OverFocused >> RouteFocused (if in focused window stack) >> RouteGlobal.
    # - Default policy is RouteFocused. Can select only 1 policy among all available.
    # ImGuiInputFlags_RouteActive             = 1 << 10,      /* original C++ signature */
    route_active = enum.auto()  # (= 1 << 10)  # Route to active item only.
    # ImGuiInputFlags_RouteFocused            = 1 << 11,      /* original C++ signature */
    route_focused = (
        enum.auto()
    )  # (= 1 << 11)  # Route to windows in the focus stack (DEFAULT). Deep-most focused window takes inputs. Active item takes inputs over deep-most focused window.
    # ImGuiInputFlags_RouteGlobal             = 1 << 12,      /* original C++ signature */
    route_global = (
        enum.auto()
    )  # (= 1 << 12)  # Global route (unless a focused window or active item registered the route).
    # ImGuiInputFlags_RouteAlways             = 1 << 13,      /* original C++ signature */
    route_always = enum.auto()  # (= 1 << 13)  # Do not register route, poll keys directly.
    # - Routing options
    # ImGuiInputFlags_RouteOverFocused        = 1 << 14,      /* original C++ signature */
    route_over_focused = (
        enum.auto()
    )  # (= 1 << 14)  # Option: global route: higher priority than focused route (unless active item in focused route).
    # ImGuiInputFlags_RouteOverActive         = 1 << 15,      /* original C++ signature */
    route_over_active = (
        enum.auto()
    )  # (= 1 << 15)  # Option: global route: higher priority than active item. Unlikely you need to use that: will interfere with every active items, e.g. CTRL+A registered by InputText will be overridden by this. May not be fully honored as user/internal code is likely to always assume they can access keys when active.
    # ImGuiInputFlags_RouteUnlessBgFocused    = 1 << 16,      /* original C++ signature */
    route_unless_bg_focused = (
        enum.auto()
    )  # (= 1 << 16)  # Option: global route: will not be applied if underlying background/None is focused (== no Dear ImGui windows are focused). Useful for overlay applications.
    # ImGuiInputFlags_RouteFromRootWindow     = 1 << 17,      /* original C++ signature */
    route_from_root_window = (
        enum.auto()
    )  # (= 1 << 17)  # Option: route evaluated from the point of view of root window rather than current window.

    # Flags for SetNextItemShortcut()
    # ImGuiInputFlags_Tooltip                 = 1 << 18,      /* original C++ signature */
    tooltip = (
        enum.auto()
    )  # (= 1 << 18)  # Automatically display a tooltip when hovering item [BETA] Unsure of right api (opt-in/opt-out)

class ConfigFlags_(enum.Enum):
    """Configuration flags stored in io.ConfigFlags. Set by user/application."""

    # ImGuiConfigFlags_None                   = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiConfigFlags_NavEnableKeyboard      = 1 << 0,       /* original C++ signature */
    nav_enable_keyboard = (
        enum.auto()
    )  # (= 1 << 0)  # Master keyboard navigation enable flag. Enable full Tabbing + directional arrows + space/enter to activate.
    # ImGuiConfigFlags_NavEnableGamepad       = 1 << 1,       /* original C++ signature */
    nav_enable_gamepad = (
        enum.auto()
    )  # (= 1 << 1)  # Master gamepad navigation enable flag. Backend also needs to set ImGuiBackendFlags_HasGamepad.
    # ImGuiConfigFlags_NoMouse                = 1 << 4,       /* original C++ signature */
    no_mouse = enum.auto()  # (= 1 << 4)  # Instruct dear imgui to disable mouse inputs and interactions.
    # ImGuiConfigFlags_NoMouseCursorChange    = 1 << 5,       /* original C++ signature */
    no_mouse_cursor_change = (
        enum.auto()
    )  # (= 1 << 5)  # Instruct backend to not alter mouse cursor shape and visibility. Use if the backend cursor changes are interfering with yours and you don't want to use SetMouseCursor() to change mouse cursor. You may want to honor requests from imgui by reading GetMouseCursor() yourself instead.
    # ImGuiConfigFlags_NoKeyboard             = 1 << 6,       /* original C++ signature */
    no_keyboard = (
        enum.auto()
    )  # (= 1 << 6)  # Instruct dear imgui to disable keyboard inputs and interactions. This is done by ignoring keyboard events and clearing existing states.

    # [BETA] Docking
    # ImGuiConfigFlags_DockingEnable          = 1 << 7,       /* original C++ signature */
    docking_enable = enum.auto()  # (= 1 << 7)  # Docking enable flags.

    # [BETA] Viewports
    # When using viewports it is recommended that your default value for ImGuiCol_WindowBg is opaque (Alpha=1.0) so transition to a viewport won't be noticeable.
    # ImGuiConfigFlags_ViewportsEnable        = 1 << 10,      /* original C++ signature */
    viewports_enable = (
        enum.auto()
    )  # (= 1 << 10)  # Viewport enable flags (require both ImGuiBackendFlags_PlatformHasViewports + ImGuiBackendFlags_RendererHasViewports set by the respective backends)
    # ImGuiConfigFlags_DpiEnableScaleViewports= 1 << 14,      /* original C++ signature */
    dpi_enable_scale_viewports = (
        enum.auto()
    )  # (= 1 << 14)  # [BETA: Don't use] FIXME-DPI: Reposition and resize imgui windows when the DpiScale of a viewport changed (mostly useful for the main viewport hosting other window). Note that resizing the main window itself is up to your application.
    # ImGuiConfigFlags_DpiEnableScaleFonts    = 1 << 15,      /* original C++ signature */
    dpi_enable_scale_fonts = (
        enum.auto()
    )  # (= 1 << 15)  # [BETA: Don't use] FIXME-DPI: Request bitmap-scaled fonts to match DpiScale. This is a very low-quality workaround. The correct way to handle DPI is _currently_ to replace the atlas and/or fonts in the Platform_OnChangedViewport callback, but this is all early work in progress.

    # User storage (to allow your backend/engine to communicate to code that may be shared between multiple projects. Those flags are NOT used by core Dear ImGui)
    # ImGuiConfigFlags_IsSRGB                 = 1 << 20,      /* original C++ signature */
    is_srgb = enum.auto()  # (= 1 << 20)  # Application is SRGB-aware.
    # ImGuiConfigFlags_IsTouchScreen          = 1 << 21,      /* original C++ signature */
    is_touch_screen = enum.auto()  # (= 1 << 21)  # Application is using a touch screen instead of a mouse.

class BackendFlags_(enum.Enum):
    """Backend capabilities flags stored in io.BackendFlags. Set by imgui_impl_xxx or custom backend."""

    # ImGuiBackendFlags_None                  = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiBackendFlags_HasGamepad            = 1 << 0,       /* original C++ signature */
    has_gamepad = enum.auto()  # (= 1 << 0)  # Backend Platform supports gamepad and currently has one connected.
    # ImGuiBackendFlags_HasMouseCursors       = 1 << 1,       /* original C++ signature */
    has_mouse_cursors = (
        enum.auto()
    )  # (= 1 << 1)  # Backend Platform supports honoring GetMouseCursor() value to change the OS cursor shape.
    # ImGuiBackendFlags_HasSetMousePos        = 1 << 2,       /* original C++ signature */
    has_set_mouse_pos = (
        enum.auto()
    )  # (= 1 << 2)  # Backend Platform supports io.WantSetMousePos requests to reposition the OS mouse position (only used if io.ConfigNavMoveSetMousePos is set).
    # ImGuiBackendFlags_RendererHasVtxOffset  = 1 << 3,       /* original C++ signature */
    renderer_has_vtx_offset = (
        enum.auto()
    )  # (= 1 << 3)  # Backend Renderer supports ImDrawCmd::VtxOffset. This enables output of large meshes (64K+ vertices) while still using 16-bit indices.

    # [BETA] Viewports
    # ImGuiBackendFlags_PlatformHasViewports  = 1 << 10,      /* original C++ signature */
    platform_has_viewports = enum.auto()  # (= 1 << 10)  # Backend Platform supports multiple viewports.
    # ImGuiBackendFlags_HasMouseHoveredViewport=1 << 11,      /* original C++ signature */
    has_mouse_hovered_viewport = (
        enum.auto()
    )  # (= 1 << 11)  # Backend Platform supports calling io.AddMouseViewportEvent() with the viewport under the mouse. IF POSSIBLE, ignore viewports with the ImGuiViewportFlags_NoInputs flag (Win32 backend, GLFW 3.30+ backend can do this, SDL backend cannot). If this cannot be done, Dear ImGui needs to use a flawed heuristic to find the viewport under.
    # ImGuiBackendFlags_RendererHasViewports  = 1 << 12,      /* original C++ signature */
    renderer_has_viewports = enum.auto()  # (= 1 << 12)  # Backend Renderer supports multiple viewports.

class Col_(enum.Enum):
    """Enumeration for PushStyleColor() / PopStyleColor()"""

    # ImGuiCol_Text,    /* original C++ signature */
    text = enum.auto()  # (= 0)
    # ImGuiCol_TextDisabled,    /* original C++ signature */
    text_disabled = enum.auto()  # (= 1)
    # ImGuiCol_WindowBg,                  /* original C++ signature */
    window_bg = enum.auto()  # (= 2)  # Background of normal windows
    # ImGuiCol_ChildBg,                   /* original C++ signature */
    child_bg = enum.auto()  # (= 3)  # Background of child windows
    # ImGuiCol_PopupBg,                   /* original C++ signature */
    popup_bg = enum.auto()  # (= 4)  # Background of popups, menus, tooltips windows
    # ImGuiCol_Border,    /* original C++ signature */
    border = enum.auto()  # (= 5)
    # ImGuiCol_BorderShadow,    /* original C++ signature */
    border_shadow = enum.auto()  # (= 6)
    # ImGuiCol_FrameBg,                   /* original C++ signature */
    frame_bg = enum.auto()  # (= 7)  # Background of checkbox, radio button, plot, slider, text input
    # ImGuiCol_FrameBgHovered,    /* original C++ signature */
    frame_bg_hovered = enum.auto()  # (= 8)
    # ImGuiCol_FrameBgActive,    /* original C++ signature */
    frame_bg_active = enum.auto()  # (= 9)
    # ImGuiCol_TitleBg,                   /* original C++ signature */
    title_bg = enum.auto()  # (= 10)  # Title bar
    # ImGuiCol_TitleBgActive,             /* original C++ signature */
    title_bg_active = enum.auto()  # (= 11)  # Title bar when focused
    # ImGuiCol_TitleBgCollapsed,          /* original C++ signature */
    title_bg_collapsed = enum.auto()  # (= 12)  # Title bar when collapsed
    # ImGuiCol_MenuBarBg,    /* original C++ signature */
    menu_bar_bg = enum.auto()  # (= 13)
    # ImGuiCol_ScrollbarBg,    /* original C++ signature */
    scrollbar_bg = enum.auto()  # (= 14)
    # ImGuiCol_ScrollbarGrab,    /* original C++ signature */
    scrollbar_grab = enum.auto()  # (= 15)
    # ImGuiCol_ScrollbarGrabHovered,    /* original C++ signature */
    scrollbar_grab_hovered = enum.auto()  # (= 16)
    # ImGuiCol_ScrollbarGrabActive,    /* original C++ signature */
    scrollbar_grab_active = enum.auto()  # (= 17)
    # ImGuiCol_CheckMark,                 /* original C++ signature */
    check_mark = enum.auto()  # (= 18)  # Checkbox tick and RadioButton circle
    # ImGuiCol_SliderGrab,    /* original C++ signature */
    slider_grab = enum.auto()  # (= 19)
    # ImGuiCol_SliderGrabActive,    /* original C++ signature */
    slider_grab_active = enum.auto()  # (= 20)
    # ImGuiCol_Button,    /* original C++ signature */
    button = enum.auto()  # (= 21)
    # ImGuiCol_ButtonHovered,    /* original C++ signature */
    button_hovered = enum.auto()  # (= 22)
    # ImGuiCol_ButtonActive,    /* original C++ signature */
    button_active = enum.auto()  # (= 23)
    # ImGuiCol_Header,                    /* original C++ signature */
    header = enum.auto()  # (= 24)  # Header* colors are used for CollapsingHeader, TreeNode, Selectable, MenuItem
    # ImGuiCol_HeaderHovered,    /* original C++ signature */
    header_hovered = enum.auto()  # (= 25)
    # ImGuiCol_HeaderActive,    /* original C++ signature */
    header_active = enum.auto()  # (= 26)
    # ImGuiCol_Separator,    /* original C++ signature */
    separator = enum.auto()  # (= 27)
    # ImGuiCol_SeparatorHovered,    /* original C++ signature */
    separator_hovered = enum.auto()  # (= 28)
    # ImGuiCol_SeparatorActive,    /* original C++ signature */
    separator_active = enum.auto()  # (= 29)
    # ImGuiCol_ResizeGrip,                /* original C++ signature */
    resize_grip = enum.auto()  # (= 30)  # Resize grip in lower-right and lower-left corners of windows.
    # ImGuiCol_ResizeGripHovered,    /* original C++ signature */
    resize_grip_hovered = enum.auto()  # (= 31)
    # ImGuiCol_ResizeGripActive,    /* original C++ signature */
    resize_grip_active = enum.auto()  # (= 32)
    # ImGuiCol_TabHovered,                /* original C++ signature */
    tab_hovered = enum.auto()  # (= 33)  # Tab background, when hovered
    # ImGuiCol_Tab,                       /* original C++ signature */
    tab = enum.auto()  # (= 34)  # Tab background, when tab-bar is focused & tab is unselected
    # ImGuiCol_TabSelected,               /* original C++ signature */
    tab_selected = enum.auto()  # (= 35)  # Tab background, when tab-bar is focused & tab is selected
    # ImGuiCol_TabSelectedOverline,       /* original C++ signature */
    tab_selected_overline = enum.auto()  # (= 36)  # Tab horizontal overline, when tab-bar is focused & tab is selected
    # ImGuiCol_TabDimmed,                 /* original C++ signature */
    tab_dimmed = enum.auto()  # (= 37)  # Tab background, when tab-bar is unfocused & tab is unselected
    # ImGuiCol_TabDimmedSelected,         /* original C++ signature */
    tab_dimmed_selected = enum.auto()  # (= 38)  # Tab background, when tab-bar is unfocused & tab is selected
    # ImGuiCol_TabDimmedSelectedOverline,    /* original C++ signature */
    tab_dimmed_selected_overline = (
        enum.auto()
    )  # (= 39)  #..horizontal overline, when tab-bar is unfocused & tab is selected
    # ImGuiCol_DockingPreview,            /* original C++ signature */
    docking_preview = enum.auto()  # (= 40)  # Preview overlay color when about to docking something
    # ImGuiCol_DockingEmptyBg,            /* original C++ signature */
    docking_empty_bg = (
        enum.auto()
    )  # (= 41)  # Background color for empty node (e.g. CentralNode with no window docked into it)
    # ImGuiCol_PlotLines,    /* original C++ signature */
    plot_lines = enum.auto()  # (= 42)
    # ImGuiCol_PlotLinesHovered,    /* original C++ signature */
    plot_lines_hovered = enum.auto()  # (= 43)
    # ImGuiCol_PlotHistogram,    /* original C++ signature */
    plot_histogram = enum.auto()  # (= 44)
    # ImGuiCol_PlotHistogramHovered,    /* original C++ signature */
    plot_histogram_hovered = enum.auto()  # (= 45)
    # ImGuiCol_TableHeaderBg,             /* original C++ signature */
    table_header_bg = enum.auto()  # (= 46)  # Table header background
    # ImGuiCol_TableBorderStrong,         /* original C++ signature */
    table_border_strong = enum.auto()  # (= 47)  # Table outer and header borders (prefer using Alpha=1.0 here)
    # ImGuiCol_TableBorderLight,          /* original C++ signature */
    table_border_light = enum.auto()  # (= 48)  # Table inner borders (prefer using Alpha=1.0 here)
    # ImGuiCol_TableRowBg,                /* original C++ signature */
    table_row_bg = enum.auto()  # (= 49)  # Table row background (even rows)
    # ImGuiCol_TableRowBgAlt,             /* original C++ signature */
    table_row_bg_alt = enum.auto()  # (= 50)  # Table row background (odd rows)
    # ImGuiCol_TextLink,                  /* original C++ signature */
    text_link = enum.auto()  # (= 51)  # Hyperlink color
    # ImGuiCol_TextSelectedBg,    /* original C++ signature */
    text_selected_bg = enum.auto()  # (= 52)
    # ImGuiCol_DragDropTarget,            /* original C++ signature */
    drag_drop_target = enum.auto()  # (= 53)  # Rectangle highlighting a drop target
    # ImGuiCol_NavCursor,                 /* original C++ signature */
    nav_cursor = enum.auto()  # (= 54)  # Color of keyboard/gamepad navigation cursor/rectangle, when visible
    # ImGuiCol_NavWindowingHighlight,     /* original C++ signature */
    nav_windowing_highlight = enum.auto()  # (= 55)  # Highlight window when using CTRL+TAB
    # ImGuiCol_NavWindowingDimBg,         /* original C++ signature */
    nav_windowing_dim_bg = (
        enum.auto()
    )  # (= 56)  # Darken/colorize entire screen behind the CTRL+TAB window list, when active
    # ImGuiCol_ModalWindowDimBg,          /* original C++ signature */
    modal_window_dim_bg = (
        enum.auto()
    )  # (= 57)  # Darken/colorize entire screen behind a modal window, when one is active
    # ImGuiCol_COUNT,    /* original C++ signature */
    count = enum.auto()  # (= 58)

class StyleVar_(enum.Enum):
    """Enumeration for PushStyleVar() / PopStyleVar() to temporarily modify the ImGuiStyle structure.
    - The enum only refers to fields of ImGuiStyle which makes sense to be pushed/popped inside UI code.
      During initialization or between frames, feel free to just poke into ImGuiStyle directly.
    - Tip: Use your programming IDE navigation facilities on the names in the _second column_ below to find the actual members and their description.
      - In Visual Studio: CTRL+comma ("Edit.GoToAll") can follow symbols inside comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
      - In Visual Studio w/ Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols inside comments.
      - In VS Code, CLion, etc.: CTRL+click can follow symbols inside comments.
    - When changing this enum, you need to update the associated internal table GStyleVarInfo[] accordingly. This is where we link enum values to members offset/type.
    """

    # Enum name -------------------------- // Member in ImGuiStyle structure (see ImGuiStyle for descriptions)
    # ImGuiStyleVar_Alpha,                        /* original C++ signature */
    alpha = enum.auto()  # (= 0)  # float     Alpha
    # ImGuiStyleVar_DisabledAlpha,                /* original C++ signature */
    disabled_alpha = enum.auto()  # (= 1)  # float     DisabledAlpha
    # ImGuiStyleVar_WindowPadding,                /* original C++ signature */
    window_padding = enum.auto()  # (= 2)  # ImVec2    WindowPadding
    # ImGuiStyleVar_WindowRounding,               /* original C++ signature */
    window_rounding = enum.auto()  # (= 3)  # float     WindowRounding
    # ImGuiStyleVar_WindowBorderSize,             /* original C++ signature */
    window_border_size = enum.auto()  # (= 4)  # float     WindowBorderSize
    # ImGuiStyleVar_WindowMinSize,                /* original C++ signature */
    window_min_size = enum.auto()  # (= 5)  # ImVec2    WindowMinSize
    # ImGuiStyleVar_WindowTitleAlign,             /* original C++ signature */
    window_title_align = enum.auto()  # (= 6)  # ImVec2    WindowTitleAlign
    # ImGuiStyleVar_ChildRounding,                /* original C++ signature */
    child_rounding = enum.auto()  # (= 7)  # float     ChildRounding
    # ImGuiStyleVar_ChildBorderSize,              /* original C++ signature */
    child_border_size = enum.auto()  # (= 8)  # float     ChildBorderSize
    # ImGuiStyleVar_PopupRounding,                /* original C++ signature */
    popup_rounding = enum.auto()  # (= 9)  # float     PopupRounding
    # ImGuiStyleVar_PopupBorderSize,              /* original C++ signature */
    popup_border_size = enum.auto()  # (= 10)  # float     PopupBorderSize
    # ImGuiStyleVar_FramePadding,                 /* original C++ signature */
    frame_padding = enum.auto()  # (= 11)  # ImVec2    FramePadding
    # ImGuiStyleVar_FrameRounding,                /* original C++ signature */
    frame_rounding = enum.auto()  # (= 12)  # float     FrameRounding
    # ImGuiStyleVar_FrameBorderSize,              /* original C++ signature */
    frame_border_size = enum.auto()  # (= 13)  # float     FrameBorderSize
    # ImGuiStyleVar_ItemSpacing,                  /* original C++ signature */
    item_spacing = enum.auto()  # (= 14)  # ImVec2    ItemSpacing
    # ImGuiStyleVar_ItemInnerSpacing,             /* original C++ signature */
    item_inner_spacing = enum.auto()  # (= 15)  # ImVec2    ItemInnerSpacing
    # ImGuiStyleVar_IndentSpacing,                /* original C++ signature */
    indent_spacing = enum.auto()  # (= 16)  # float     IndentSpacing
    # ImGuiStyleVar_CellPadding,                  /* original C++ signature */
    cell_padding = enum.auto()  # (= 17)  # ImVec2    CellPadding
    # ImGuiStyleVar_ScrollbarSize,                /* original C++ signature */
    scrollbar_size = enum.auto()  # (= 18)  # float     ScrollbarSize
    # ImGuiStyleVar_ScrollbarRounding,            /* original C++ signature */
    scrollbar_rounding = enum.auto()  # (= 19)  # float     ScrollbarRounding
    # ImGuiStyleVar_GrabMinSize,                  /* original C++ signature */
    grab_min_size = enum.auto()  # (= 20)  # float     GrabMinSize
    # ImGuiStyleVar_GrabRounding,                 /* original C++ signature */
    grab_rounding = enum.auto()  # (= 21)  # float     GrabRounding
    # ImGuiStyleVar_LayoutAlign,                  /* original C++ signature */
    layout_align = enum.auto()  # (= 22)  # float     LayoutAlign
    # ImGuiStyleVar_TabRounding,                  /* original C++ signature */
    tab_rounding = enum.auto()  # (= 23)  # float     TabRounding
    # ImGuiStyleVar_TabBorderSize,                /* original C++ signature */
    tab_border_size = enum.auto()  # (= 24)  # float     TabBorderSize
    # ImGuiStyleVar_TabBarBorderSize,             /* original C++ signature */
    tab_bar_border_size = enum.auto()  # (= 25)  # float     TabBarBorderSize
    # ImGuiStyleVar_TabBarOverlineSize,           /* original C++ signature */
    tab_bar_overline_size = enum.auto()  # (= 26)  # float     TabBarOverlineSize
    # ImGuiStyleVar_TableAngledHeadersAngle,      /* original C++ signature */
    table_angled_headers_angle = enum.auto()  # (= 27)  # float     TableAngledHeadersAngle
    # ImGuiStyleVar_TableAngledHeadersTextAlign,    /* original C++ signature */
    table_angled_headers_text_align = enum.auto()  # (= 28)  # ImVec2  TableAngledHeadersTextAlign
    # ImGuiStyleVar_ButtonTextAlign,              /* original C++ signature */
    button_text_align = enum.auto()  # (= 29)  # ImVec2    ButtonTextAlign
    # ImGuiStyleVar_SelectableTextAlign,          /* original C++ signature */
    selectable_text_align = enum.auto()  # (= 30)  # ImVec2    SelectableTextAlign
    # ImGuiStyleVar_SeparatorTextBorderSize,      /* original C++ signature */
    separator_text_border_size = enum.auto()  # (= 31)  # float     SeparatorTextBorderSize
    # ImGuiStyleVar_SeparatorTextAlign,           /* original C++ signature */
    separator_text_align = enum.auto()  # (= 32)  # ImVec2    SeparatorTextAlign
    # ImGuiStyleVar_SeparatorTextPadding,         /* original C++ signature */
    separator_text_padding = enum.auto()  # (= 33)  # ImVec2    SeparatorTextPadding
    # ImGuiStyleVar_DockingSeparatorSize,         /* original C++ signature */
    docking_separator_size = enum.auto()  # (= 34)  # float     DockingSeparatorSize
    # ImGuiStyleVar_COUNT    /* original C++ signature */
    # }
    count = enum.auto()  # (= 35)

class ButtonFlags_(enum.Enum):
    """Flags for InvisibleButton() [extended in imgui_internal.h]"""

    # ImGuiButtonFlags_None                   = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiButtonFlags_MouseButtonLeft        = 1 << 0,       /* original C++ signature */
    mouse_button_left = enum.auto()  # (= 1 << 0)  # React on left mouse button (default)
    # ImGuiButtonFlags_MouseButtonRight       = 1 << 1,       /* original C++ signature */
    mouse_button_right = enum.auto()  # (= 1 << 1)  # React on right mouse button
    # ImGuiButtonFlags_MouseButtonMiddle      = 1 << 2,       /* original C++ signature */
    mouse_button_middle = enum.auto()  # (= 1 << 2)  # React on center mouse button
    # ImGuiButtonFlags_MouseButtonMask_       = ImGuiButtonFlags_MouseButtonLeft | ImGuiButtonFlags_MouseButtonRight | ImGuiButtonFlags_MouseButtonMiddle,     /* original C++ signature */
    mouse_button_mask_ = (
        enum.auto()
    )  # (= ButtonFlags_MouseButtonLeft | ButtonFlags_MouseButtonRight | ButtonFlags_MouseButtonMiddle)  # [Internal]
    # ImGuiButtonFlags_EnableNav              = 1 << 3,       /* original C++ signature */
    enable_nav = (
        enum.auto()
    )  # (= 1 << 3)  # InvisibleButton(): do not disable navigation/tabbing. Otherwise disabled by default.

class ColorEditFlags_(enum.Enum):
    """Flags for ColorEdit3() / ColorEdit4() / ColorPicker3() / ColorPicker4() / ColorButton()"""

    # ImGuiColorEditFlags_None            = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiColorEditFlags_NoAlpha         = 1 << 1,       /* original C++ signature */
    no_alpha = (
        enum.auto()
    )  # (= 1 << 1)  #              // ColorEdit, ColorPicker, ColorButton: ignore Alpha component (will only read 3 components from the input pointer).
    # ImGuiColorEditFlags_NoPicker        = 1 << 2,       /* original C++ signature */
    no_picker = enum.auto()  # (= 1 << 2)  #              // ColorEdit: disable picker when clicking on color square.
    # ImGuiColorEditFlags_NoOptions       = 1 << 3,       /* original C++ signature */
    no_options = (
        enum.auto()
    )  # (= 1 << 3)  #              // ColorEdit: disable toggling options menu when right-clicking on inputs/small preview.
    # ImGuiColorEditFlags_NoSmallPreview  = 1 << 4,       /* original C++ signature */
    no_small_preview = (
        enum.auto()
    )  # (= 1 << 4)  #              // ColorEdit, ColorPicker: disable color square preview next to the inputs. (e.g. to show only the inputs)
    # ImGuiColorEditFlags_NoInputs        = 1 << 5,       /* original C++ signature */
    no_inputs = (
        enum.auto()
    )  # (= 1 << 5)  #              // ColorEdit, ColorPicker: disable inputs sliders/text widgets (e.g. to show only the small preview color square).
    # ImGuiColorEditFlags_NoTooltip       = 1 << 6,       /* original C++ signature */
    no_tooltip = (
        enum.auto()
    )  # (= 1 << 6)  #              // ColorEdit, ColorPicker, ColorButton: disable tooltip when hovering the preview.
    # ImGuiColorEditFlags_NoLabel         = 1 << 7,       /* original C++ signature */
    no_label = (
        enum.auto()
    )  # (= 1 << 7)  #              // ColorEdit, ColorPicker: disable display of inline text label (the label is still forwarded to the tooltip and picker).
    # ImGuiColorEditFlags_NoSidePreview   = 1 << 8,       /* original C++ signature */
    no_side_preview = (
        enum.auto()
    )  # (= 1 << 8)  #              // ColorPicker: disable bigger color preview on right side of the picker, use small color square preview instead.
    # ImGuiColorEditFlags_NoDragDrop      = 1 << 9,       /* original C++ signature */
    no_drag_drop = (
        enum.auto()
    )  # (= 1 << 9)  #              // ColorEdit: disable drag and drop target. ColorButton: disable drag and drop source.
    # ImGuiColorEditFlags_NoBorder        = 1 << 10,      /* original C++ signature */
    no_border = enum.auto()  # (= 1 << 10)  #              // ColorButton: disable border (which is enforced by default)

    # User Options (right-click on widget to change some of them).
    # ImGuiColorEditFlags_AlphaBar        = 1 << 16,      /* original C++ signature */
    alpha_bar = (
        enum.auto()
    )  # (= 1 << 16)  #              // ColorEdit, ColorPicker: show vertical alpha bar/gradient in picker.
    # ImGuiColorEditFlags_AlphaPreview    = 1 << 17,      /* original C++ signature */
    alpha_preview = (
        enum.auto()
    )  # (= 1 << 17)  #              // ColorEdit, ColorPicker, ColorButton: display preview as a transparent color over a checkerboard, instead of opaque.
    # ImGuiColorEditFlags_AlphaPreviewHalf= 1 << 18,      /* original C++ signature */
    alpha_preview_half = (
        enum.auto()
    )  # (= 1 << 18)  #              // ColorEdit, ColorPicker, ColorButton: display half opaque / half checkerboard, instead of opaque.
    # ImGuiColorEditFlags_HDR             = 1 << 19,      /* original C++ signature */
    hdr = (
        enum.auto()
    )  # (= 1 << 19)  #              // (WIP) ColorEdit: Currently only disable 0.0..1.0 limits in RGBA edition (note: you probably want to use ImGuiColorEditFlags_Float flag as well).
    # ImGuiColorEditFlags_DisplayRGB      = 1 << 20,      /* original C++ signature */
    display_rgb = (
        enum.auto()
    )  # (= 1 << 20)  # [Display]    // ColorEdit: override _display_ type among RGB/HSV/Hex. ColorPicker: select any combination using one or more of RGB/HSV/Hex.
    # ImGuiColorEditFlags_DisplayHSV      = 1 << 21,      /* original C++ signature */
    display_hsv = enum.auto()  # (= 1 << 21)  # [Display]    // "
    # ImGuiColorEditFlags_DisplayHex      = 1 << 22,      /* original C++ signature */
    display_hex = enum.auto()  # (= 1 << 22)  # [Display]    // "
    # ImGuiColorEditFlags_Uint8           = 1 << 23,      /* original C++ signature */
    uint8 = (
        enum.auto()
    )  # (= 1 << 23)  # [DataType]   // ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0..255.
    # ImGuiColorEditFlags_Float           = 1 << 24,      /* original C++ signature */
    float = (
        enum.auto()
    )  # (= 1 << 24)  # [DataType]   // ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0.0..1.0 floats instead of 0..255 integers. No round-trip of value via integers.
    # ImGuiColorEditFlags_PickerHueBar    = 1 << 25,      /* original C++ signature */
    picker_hue_bar = enum.auto()  # (= 1 << 25)  # [Picker]     // ColorPicker: bar for Hue, rectangle for Sat/Value.
    # ImGuiColorEditFlags_PickerHueWheel  = 1 << 26,      /* original C++ signature */
    picker_hue_wheel = enum.auto()  # (= 1 << 26)  # [Picker]     // ColorPicker: wheel for Hue, triangle for Sat/Value.
    # ImGuiColorEditFlags_InputRGB        = 1 << 27,      /* original C++ signature */
    input_rgb = (
        enum.auto()
    )  # (= 1 << 27)  # [Input]      // ColorEdit, ColorPicker: input and output data in RGB format.
    # ImGuiColorEditFlags_InputHSV        = 1 << 28,      /* original C++ signature */
    input_hsv = (
        enum.auto()
    )  # (= 1 << 28)  # [Input]      // ColorEdit, ColorPicker: input and output data in HSV format.

    # ImGuiColorEditFlags_DefaultOptions_ = ImGuiColorEditFlags_Uint8 | ImGuiColorEditFlags_DisplayRGB | ImGuiColorEditFlags_InputRGB | ImGuiColorEditFlags_PickerHueBar,    /* original C++ signature */
    # Defaults Options. You can set application defaults using SetColorEditOptions(). The intent is that you probably don't want to
    # override them in most of your calls. Let the user choose via the option menu and/or call SetColorEditOptions() once during startup.
    default_options_ = (
        enum.auto()
    )  # (= ColorEditFlags_Uint8 | ColorEditFlags_DisplayRGB | ColorEditFlags_InputRGB | ColorEditFlags_PickerHueBar)

    # [Internal] Masks
    # ImGuiColorEditFlags_DisplayMask_    = ImGuiColorEditFlags_DisplayRGB | ImGuiColorEditFlags_DisplayHSV | ImGuiColorEditFlags_DisplayHex,    /* original C++ signature */
    display_mask_ = enum.auto()  # (= ColorEditFlags_DisplayRGB | ColorEditFlags_DisplayHSV | ColorEditFlags_DisplayHex)
    # ImGuiColorEditFlags_DataTypeMask_   = ImGuiColorEditFlags_Uint8 | ImGuiColorEditFlags_Float,    /* original C++ signature */
    data_type_mask_ = enum.auto()  # (= ColorEditFlags_Uint8 | ColorEditFlags_Float)
    # ImGuiColorEditFlags_PickerMask_     = ImGuiColorEditFlags_PickerHueWheel | ImGuiColorEditFlags_PickerHueBar,    /* original C++ signature */
    picker_mask_ = enum.auto()  # (= ColorEditFlags_PickerHueWheel | ColorEditFlags_PickerHueBar)
    # ImGuiColorEditFlags_InputMask_      = ImGuiColorEditFlags_InputRGB | ImGuiColorEditFlags_InputHSV,    /* original C++ signature */
    input_mask_ = enum.auto()  # (= ColorEditFlags_InputRGB | ColorEditFlags_InputHSV)

    # Obsolete names
    # ImGuiColorEditFlags_RGB = ImGuiColorEditFlags_DisplayRGB, ImGuiColorEditFlags_HSV = ImGuiColorEditFlags_DisplayHSV, ImGuiColorEditFlags_HEX = ImGuiColorEditFlags_DisplayHex  // [renamed in 1.69]

class SliderFlags_(enum.Enum):
    """Flags for DragFloat(), DragInt(), SliderFloat(), SliderInt() etc.
    We use the same sets of flags for DragXXX() and SliderXXX() functions as the features are the same and it makes it easier to swap them.
    (Those are per-item flags. There is shared behavior flag too: ImGuiIO: io.ConfigDragClickToInputText)
    """

    # ImGuiSliderFlags_None               = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiSliderFlags_Logarithmic        = 1 << 5,           /* original C++ signature */
    logarithmic = (
        enum.auto()
    )  # (= 1 << 5)  # Make the widget logarithmic (linear otherwise). Consider using ImGuiSliderFlags_NoRoundToFormat with this if using a format-string with small amount of digits.
    # ImGuiSliderFlags_NoRoundToFormat    = 1 << 6,           /* original C++ signature */
    no_round_to_format = (
        enum.auto()
    )  # (= 1 << 6)  # Disable rounding underlying value to match precision of the display format string (e.g. %.3 values are rounded to those 3 digits).
    # ImGuiSliderFlags_NoInput            = 1 << 7,           /* original C++ signature */
    no_input = (
        enum.auto()
    )  # (= 1 << 7)  # Disable CTRL+Click or Enter key allowing to input text directly into the widget.
    # ImGuiSliderFlags_WrapAround         = 1 << 8,           /* original C++ signature */
    wrap_around = (
        enum.auto()
    )  # (= 1 << 8)  # Enable wrapping around from max to min and from min to max. Only supported by DragXXX() functions for now.
    # ImGuiSliderFlags_ClampOnInput       = 1 << 9,           /* original C++ signature */
    clamp_on_input = (
        enum.auto()
    )  # (= 1 << 9)  # Clamp value to min/max bounds when input manually with CTRL+Click. By default CTRL+Click allows going out of bounds.
    # ImGuiSliderFlags_ClampZeroRange     = 1 << 10,          /* original C++ signature */
    clamp_zero_range = (
        enum.auto()
    )  # (= 1 << 10)  # Clamp even if min==max==0.0. Otherwise due to legacy reason DragXXX functions don't clamp with those values. When your clamping limits are dynamic you almost always want to use it.
    # ImGuiSliderFlags_NoSpeedTweaks      = 1 << 11,          /* original C++ signature */
    no_speed_tweaks = (
        enum.auto()
    )  # (= 1 << 11)  # Disable keyboard modifiers altering tweak speed. Useful if you want to alter tweak speed yourself based on your own logic.
    # ImGuiSliderFlags_AlwaysClamp        = ImGuiSliderFlags_ClampOnInput | ImGuiSliderFlags_ClampZeroRange,    /* original C++ signature */
    always_clamp = enum.auto()  # (= SliderFlags_ClampOnInput | SliderFlags_ClampZeroRange)
    # ImGuiSliderFlags_InvalidMask_       = 0x7000000F,       /* original C++ signature */
    invalid_mask_ = (
        enum.auto()
    )  # (= 0x7000000F)  # [Internal] We treat using those bits as being potentially a 'float power' argument from the previous API that has got miscast to this enum, and will trigger an assert if needed.

class MouseButton_(enum.Enum):
    """Identify a mouse button.
    Those values are guaranteed to be stable and we frequently use 0/1 directly. Named enums provided for convenience.
    """

    # ImGuiMouseButton_Left = 0,    /* original C++ signature */
    left = enum.auto()  # (= 0)
    # ImGuiMouseButton_Right = 1,    /* original C++ signature */
    right = enum.auto()  # (= 1)
    # ImGuiMouseButton_Middle = 2,    /* original C++ signature */
    middle = enum.auto()  # (= 2)
    # ImGuiMouseButton_COUNT = 5    /* original C++ signature */
    # }
    count = enum.auto()  # (= 5)

class MouseCursor_(enum.Enum):
    """Enumeration for GetMouseCursor()
    User code may request backend to display given cursor by calling SetMouseCursor(), which is why we have some cursors that are marked unused here
    """

    # ImGuiMouseCursor_None = -1,    /* original C++ signature */
    none = enum.auto()  # (= -1)
    # ImGuiMouseCursor_Arrow = 0,    /* original C++ signature */
    arrow = enum.auto()  # (= 0)
    # ImGuiMouseCursor_TextInput,             /* original C++ signature */
    text_input = enum.auto()  # (= 1)  # When hovering over InputText, etc.
    # ImGuiMouseCursor_ResizeAll,             /* original C++ signature */
    resize_all = enum.auto()  # (= 2)  # (Unused by Dear ImGui functions)
    # ImGuiMouseCursor_ResizeNS,              /* original C++ signature */
    resize_ns = enum.auto()  # (= 3)  # When hovering over a horizontal border
    # ImGuiMouseCursor_ResizeEW,              /* original C++ signature */
    resize_ew = enum.auto()  # (= 4)  # When hovering over a vertical border or a column
    # ImGuiMouseCursor_ResizeNESW,            /* original C++ signature */
    resize_nesw = enum.auto()  # (= 5)  # When hovering over the bottom-left corner of a window
    # ImGuiMouseCursor_ResizeNWSE,            /* original C++ signature */
    resize_nwse = enum.auto()  # (= 6)  # When hovering over the bottom-right corner of a window
    # ImGuiMouseCursor_Hand,                  /* original C++ signature */
    hand = enum.auto()  # (= 7)  # (Unused by Dear ImGui functions. Use for e.g. hyperlinks)
    # ImGuiMouseCursor_NotAllowed,            /* original C++ signature */
    not_allowed = enum.auto()  # (= 8)  # When hovering something with disallowed interaction. Usually a crossed circle.
    # ImGuiMouseCursor_COUNT    /* original C++ signature */
    # }
    count = enum.auto()  # (= 9)

class MouseSource(enum.Enum):
    """Enumeration for AddMouseSourceEvent() actual source of Mouse Input data.
    Historically we use "Mouse" terminology everywhere to indicate pointer data, e.g. MousePos, IsMousePressed(), io.AddMousePosEvent()
    But that "Mouse" data can come from different source which occasionally may be useful for application to know about.
    You can submit a change of pointer type using io.AddMouseSourceEvent().
    """

    # ImGuiMouseSource_Mouse = 0,             /* original C++ signature */
    mouse = enum.auto()  # (= 0)  # Input is coming from an actual mouse.
    # ImGuiMouseSource_TouchScreen,           /* original C++ signature */
    touch_screen = (
        enum.auto()
    )  # (= 1)  # Input is coming from a touch screen (no hovering prior to initial press, less precise initial press aiming, dual-axis wheeling possible).
    # ImGuiMouseSource_Pen,                   /* original C++ signature */
    pen = (
        enum.auto()
    )  # (= 2)  # Input is coming from a pressure/magnetic pen (often used in conjunction with high-sampling rates).
    # ImGuiMouseSource_COUNT    /* original C++ signature */
    # }
    count = enum.auto()  # (= 3)

class Cond_(enum.Enum):
    """Enumeration for ImGui::SetNextWindow***(), SetWindow***(), SetNextItem***() functions
    Represent a condition.
    Important: Treat as a regular enum! Do NOT combine multiple values using binary operators! All the functions above treat 0 as a shortcut to ImGuiCond_Always.
    """

    # ImGuiCond_None          = 0,            /* original C++ signature */
    none = enum.auto()  # (= 0)  # No condition (always set the variable), same as _Always
    # ImGuiCond_Always        = 1 << 0,       /* original C++ signature */
    always = enum.auto()  # (= 1 << 0)  # No condition (always set the variable), same as _None
    # ImGuiCond_Once          = 1 << 1,       /* original C++ signature */
    once = enum.auto()  # (= 1 << 1)  # Set the variable once per runtime session (only the first call will succeed)
    # ImGuiCond_FirstUseEver  = 1 << 2,       /* original C++ signature */
    first_use_ever = (
        enum.auto()
    )  # (= 1 << 2)  # Set the variable if the object/window has no persistently saved data (no entry in .ini file)
    # ImGuiCond_Appearing     = 1 << 3,       /* original C++ signature */
    appearing = (
        enum.auto()
    )  # (= 1 << 3)  # Set the variable if the object/window is appearing after being hidden/inactive (or the first time)

# -----------------------------------------------------------------------------
# [SECTION] Tables API flags and structures (ImGuiTableFlags, ImGuiTableColumnFlags, ImGuiTableRowFlags, ImGuiTableBgTarget, ImGuiTableSortSpecs, ImGuiTableColumnSortSpecs)
# -----------------------------------------------------------------------------

class TableFlags_(enum.Enum):
    """Flags for ImGui::BeginTable()
    - Important! Sizing policies have complex and subtle side effects, much more so than you would expect.
      Read comments/demos carefully + experiment with live demos to get acquainted with them.
    - The DEFAULT sizing policies are:
       - Default to ImGuiTableFlags_SizingFixedFit    if ScrollX is on, or if host window has ImGuiWindowFlags_AlwaysAutoResize.
       - Default to ImGuiTableFlags_SizingStretchSame if ScrollX is off.
    - When ScrollX is off:
       - Table defaults to ImGuiTableFlags_SizingStretchSame -> all Columns defaults to ImGuiTableColumnFlags_WidthStretch with same weight.
       - Columns sizing policy allowed: Stretch (default), Fixed/Auto.
       - Fixed Columns (if any) will generally obtain their requested width (unless the table cannot fit them all).
       - Stretch Columns will share the remaining width according to their respective weight.
       - Mixed Fixed/Stretch columns is possible but has various side-effects on resizing behaviors.
         The typical use of mixing sizing policies is: any number of LEADING Fixed columns, followed by one or two TRAILING Stretch columns.
         (this is because the visible order of columns have subtle but necessary effects on how they react to manual resizing).
    - When ScrollX is on:
       - Table defaults to ImGuiTableFlags_SizingFixedFit -> all Columns defaults to ImGuiTableColumnFlags_WidthFixed
       - Columns sizing policy allowed: Fixed/Auto mostly.
       - Fixed Columns can be enlarged as needed. Table will show a horizontal scrollbar if needed.
       - When using auto-resizing (non-resizable) fixed columns, querying the content width to use item right-alignment e.g. SetNextItemWidth(-FLT_MIN) doesn't make sense, would create a feedback loop.
       - Using Stretch columns OFTEN DOES NOT MAKE SENSE if ScrollX is on, UNLESS you have specified a value for 'inner_width' in BeginTable().
         If you specify a value for 'inner_width' then effectively the scrolling space is known and Stretch or mixed Fixed/Stretch columns become meaningful again.
    - Read on documentation at the top of imgui_tables.cpp for details.
    """

    # Features
    # ImGuiTableFlags_None                       = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTableFlags_Resizable                  = 1 << 0,       /* original C++ signature */
    resizable = enum.auto()  # (= 1 << 0)  # Enable resizing columns.
    # ImGuiTableFlags_Reorderable                = 1 << 1,       /* original C++ signature */
    reorderable = (
        enum.auto()
    )  # (= 1 << 1)  # Enable reordering columns in header row (need calling TableSetupColumn() + TableHeadersRow() to display headers)
    # ImGuiTableFlags_Hideable                   = 1 << 2,       /* original C++ signature */
    hideable = enum.auto()  # (= 1 << 2)  # Enable hiding/disabling columns in context menu.
    # ImGuiTableFlags_Sortable                   = 1 << 3,       /* original C++ signature */
    sortable = (
        enum.auto()
    )  # (= 1 << 3)  # Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
    # ImGuiTableFlags_NoSavedSettings            = 1 << 4,       /* original C++ signature */
    no_saved_settings = (
        enum.auto()
    )  # (= 1 << 4)  # Disable persisting columns order, width and sort settings in the .ini file.
    # ImGuiTableFlags_ContextMenuInBody          = 1 << 5,       /* original C++ signature */
    context_menu_in_body = (
        enum.auto()
    )  # (= 1 << 5)  # Right-click on columns body/contents will display table context menu. By default it is available in TableHeadersRow().
    # Decorations
    # ImGuiTableFlags_RowBg                      = 1 << 6,       /* original C++ signature */
    row_bg = (
        enum.auto()
    )  # (= 1 << 6)  # Set each RowBg color with ImGuiCol_TableRowBg or ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with ImGuiTableBgFlags_RowBg0 on each row manually)
    # ImGuiTableFlags_BordersInnerH              = 1 << 7,       /* original C++ signature */
    borders_inner_h = enum.auto()  # (= 1 << 7)  # Draw horizontal borders between rows.
    # ImGuiTableFlags_BordersOuterH              = 1 << 8,       /* original C++ signature */
    borders_outer_h = enum.auto()  # (= 1 << 8)  # Draw horizontal borders at the top and bottom.
    # ImGuiTableFlags_BordersInnerV              = 1 << 9,       /* original C++ signature */
    borders_inner_v = enum.auto()  # (= 1 << 9)  # Draw vertical borders between columns.
    # ImGuiTableFlags_BordersOuterV              = 1 << 10,      /* original C++ signature */
    borders_outer_v = enum.auto()  # (= 1 << 10)  # Draw vertical borders on the left and right sides.
    # ImGuiTableFlags_BordersH                   = ImGuiTableFlags_BordersInnerH | ImGuiTableFlags_BordersOuterH,     /* original C++ signature */
    borders_h = enum.auto()  # (= TableFlags_BordersInnerH | TableFlags_BordersOuterH)  # Draw horizontal borders.
    # ImGuiTableFlags_BordersV                   = ImGuiTableFlags_BordersInnerV | ImGuiTableFlags_BordersOuterV,     /* original C++ signature */
    borders_v = enum.auto()  # (= TableFlags_BordersInnerV | TableFlags_BordersOuterV)  # Draw vertical borders.
    # ImGuiTableFlags_BordersInner               = ImGuiTableFlags_BordersInnerV | ImGuiTableFlags_BordersInnerH,     /* original C++ signature */
    borders_inner = enum.auto()  # (= TableFlags_BordersInnerV | TableFlags_BordersInnerH)  # Draw inner borders.
    # ImGuiTableFlags_BordersOuter               = ImGuiTableFlags_BordersOuterV | ImGuiTableFlags_BordersOuterH,     /* original C++ signature */
    borders_outer = enum.auto()  # (= TableFlags_BordersOuterV | TableFlags_BordersOuterH)  # Draw outer borders.
    # ImGuiTableFlags_Borders                    = ImGuiTableFlags_BordersInner | ImGuiTableFlags_BordersOuter,       /* original C++ signature */
    borders = enum.auto()  # (= TableFlags_BordersInner | TableFlags_BordersOuter)  # Draw all borders.
    # ImGuiTableFlags_NoBordersInBody            = 1 << 11,      /* original C++ signature */
    no_borders_in_body = (
        enum.auto()
    )  # (= 1 << 11)  # [ALPHA] Disable vertical borders in columns Body (borders will always appear in Headers). -> May move to style
    # ImGuiTableFlags_NoBordersInBodyUntilResize = 1 << 12,      /* original C++ signature */
    no_borders_in_body_until_resize = (
        enum.auto()
    )  # (= 1 << 12)  # [ALPHA] Disable vertical borders in columns Body until hovered for resize (borders will always appear in Headers). -> May move to style
    # Sizing Policy (read above for defaults)
    # ImGuiTableFlags_SizingFixedFit             = 1 << 13,      /* original C++ signature */
    sizing_fixed_fit = (
        enum.auto()
    )  # (= 1 << 13)  # Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching contents width.
    # ImGuiTableFlags_SizingFixedSame            = 2 << 13,      /* original C++ signature */
    sizing_fixed_same = (
        enum.auto()
    )  # (= 2 << 13)  # Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching the maximum contents width of all columns. Implicitly enable ImGuiTableFlags_NoKeepColumnsVisible.
    # ImGuiTableFlags_SizingStretchProp          = 3 << 13,      /* original C++ signature */
    sizing_stretch_prop = (
        enum.auto()
    )  # (= 3 << 13)  # Columns default to _WidthStretch with default weights proportional to each columns contents widths.
    # ImGuiTableFlags_SizingStretchSame          = 4 << 13,      /* original C++ signature */
    sizing_stretch_same = (
        enum.auto()
    )  # (= 4 << 13)  # Columns default to _WidthStretch with default weights all equal, unless overridden by TableSetupColumn().
    # Sizing Extra Options
    # ImGuiTableFlags_NoHostExtendX              = 1 << 16,      /* original C++ signature */
    no_host_extend_x = (
        enum.auto()
    )  # (= 1 << 16)  # Make outer width auto-fit to columns, overriding outer_size.x value. Only available when ScrollX/ScrollY are disabled and Stretch columns are not used.
    # ImGuiTableFlags_NoHostExtendY              = 1 << 17,      /* original C++ signature */
    no_host_extend_y = (
        enum.auto()
    )  # (= 1 << 17)  # Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit). Only available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.
    # ImGuiTableFlags_NoKeepColumnsVisible       = 1 << 18,      /* original C++ signature */
    no_keep_columns_visible = (
        enum.auto()
    )  # (= 1 << 18)  # Disable keeping column always minimally visible when ScrollX is off and table gets too small. Not recommended if columns are resizable.
    # ImGuiTableFlags_PreciseWidths              = 1 << 19,      /* original C++ signature */
    precise_widths = (
        enum.auto()
    )  # (= 1 << 19)  # Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns: Without this flag: 33,33,34. With this flag: 33,33,33). With larger number of columns, resizing will appear to be less smooth.
    # Clipping
    # ImGuiTableFlags_NoClip                     = 1 << 20,      /* original C++ signature */
    no_clip = (
        enum.auto()
    )  # (= 1 << 20)  # Disable clipping rectangle for every individual columns (reduce draw command count, items will be able to overflow into other columns). Generally incompatible with TableSetupScrollFreeze().
    # Padding
    # ImGuiTableFlags_PadOuterX                  = 1 << 21,      /* original C++ signature */
    pad_outer_x = (
        enum.auto()
    )  # (= 1 << 21)  # Default if BordersOuterV is on. Enable outermost padding. Generally desirable if you have headers.
    # ImGuiTableFlags_NoPadOuterX                = 1 << 22,      /* original C++ signature */
    no_pad_outer_x = enum.auto()  # (= 1 << 22)  # Default if BordersOuterV is off. Disable outermost padding.
    # ImGuiTableFlags_NoPadInnerX                = 1 << 23,      /* original C++ signature */
    no_pad_inner_x = (
        enum.auto()
    )  # (= 1 << 23)  # Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off).
    # Scrolling
    # ImGuiTableFlags_ScrollX                    = 1 << 24,      /* original C++ signature */
    scroll_x = (
        enum.auto()
    )  # (= 1 << 24)  # Enable horizontal scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size. Changes default sizing policy. Because this creates a child window, ScrollY is currently generally recommended when using ScrollX.
    # ImGuiTableFlags_ScrollY                    = 1 << 25,      /* original C++ signature */
    scroll_y = (
        enum.auto()
    )  # (= 1 << 25)  # Enable vertical scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size.
    # Sorting
    # ImGuiTableFlags_SortMulti                  = 1 << 26,      /* original C++ signature */
    sort_multi = (
        enum.auto()
    )  # (= 1 << 26)  # Hold shift when clicking headers to sort on multiple column. TableGetSortSpecs() may return specs where (SpecsCount > 1).
    # ImGuiTableFlags_SortTristate               = 1 << 27,      /* original C++ signature */
    sort_tristate = (
        enum.auto()
    )  # (= 1 << 27)  # Allow no sorting, disable default sorting. TableGetSortSpecs() may return specs where (SpecsCount == 0).
    # Miscellaneous
    # ImGuiTableFlags_HighlightHoveredColumn     = 1 << 28,      /* original C++ signature */
    highlight_hovered_column = (
        enum.auto()
    )  # (= 1 << 28)  # Highlight column headers when hovered (may evolve into a fuller highlight)

    # ImGuiTableFlags_SizingMask_                = ImGuiTableFlags_SizingFixedFit | ImGuiTableFlags_SizingFixedSame | ImGuiTableFlags_SizingStretchProp | ImGuiTableFlags_SizingStretchSame,    /* original C++ signature */
    # }
    # [Internal] Combinations and masks
    sizing_mask_ = (
        enum.auto()
    )  # (= TableFlags_SizingFixedFit | TableFlags_SizingFixedSame | TableFlags_SizingStretchProp | TableFlags_SizingStretchSame)

class TableColumnFlags_(enum.Enum):
    """Flags for ImGui::TableSetupColumn()"""

    # Input configuration flags
    # ImGuiTableColumnFlags_None                  = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTableColumnFlags_Disabled              = 1 << 0,       /* original C++ signature */
    disabled = (
        enum.auto()
    )  # (= 1 << 0)  # Overriding/master disable flag: hide column, won't show in context menu (unlike calling TableSetColumnEnabled() which manipulates the user accessible state)
    # ImGuiTableColumnFlags_DefaultHide           = 1 << 1,       /* original C++ signature */
    default_hide = enum.auto()  # (= 1 << 1)  # Default as a hidden/disabled column.
    # ImGuiTableColumnFlags_DefaultSort           = 1 << 2,       /* original C++ signature */
    default_sort = enum.auto()  # (= 1 << 2)  # Default as a sorting column.
    # ImGuiTableColumnFlags_WidthStretch          = 1 << 3,       /* original C++ signature */
    width_stretch = (
        enum.auto()
    )  # (= 1 << 3)  # Column will stretch. Preferable with horizontal scrolling disabled (default if table sizing policy is _SizingStretchSame or _SizingStretchProp).
    # ImGuiTableColumnFlags_WidthFixed            = 1 << 4,       /* original C++ signature */
    width_fixed = (
        enum.auto()
    )  # (= 1 << 4)  # Column will not stretch. Preferable with horizontal scrolling enabled (default if table sizing policy is _SizingFixedFit and table is resizable).
    # ImGuiTableColumnFlags_NoResize              = 1 << 5,       /* original C++ signature */
    no_resize = enum.auto()  # (= 1 << 5)  # Disable manual resizing.
    # ImGuiTableColumnFlags_NoReorder             = 1 << 6,       /* original C++ signature */
    no_reorder = (
        enum.auto()
    )  # (= 1 << 6)  # Disable manual reordering this column, this will also prevent other columns from crossing over this column.
    # ImGuiTableColumnFlags_NoHide                = 1 << 7,       /* original C++ signature */
    no_hide = enum.auto()  # (= 1 << 7)  # Disable ability to hide/disable this column.
    # ImGuiTableColumnFlags_NoClip                = 1 << 8,       /* original C++ signature */
    no_clip = (
        enum.auto()
    )  # (= 1 << 8)  # Disable clipping for this column (all NoClip columns will render in a same draw command).
    # ImGuiTableColumnFlags_NoSort                = 1 << 9,       /* original C++ signature */
    no_sort = (
        enum.auto()
    )  # (= 1 << 9)  # Disable ability to sort on this field (even if ImGuiTableFlags_Sortable is set on the table).
    # ImGuiTableColumnFlags_NoSortAscending       = 1 << 10,      /* original C++ signature */
    no_sort_ascending = enum.auto()  # (= 1 << 10)  # Disable ability to sort in the ascending direction.
    # ImGuiTableColumnFlags_NoSortDescending      = 1 << 11,      /* original C++ signature */
    no_sort_descending = enum.auto()  # (= 1 << 11)  # Disable ability to sort in the descending direction.
    # ImGuiTableColumnFlags_NoHeaderLabel         = 1 << 12,      /* original C++ signature */
    no_header_label = (
        enum.auto()
    )  # (= 1 << 12)  # TableHeadersRow() will submit an empty label for this column. Convenient for some small columns. Name will still appear in context menu or in angled headers. You may append into this cell by calling TableSetColumnIndex() right after the TableHeadersRow() call.
    # ImGuiTableColumnFlags_NoHeaderWidth         = 1 << 13,      /* original C++ signature */
    no_header_width = enum.auto()  # (= 1 << 13)  # Disable header text width contribution to automatic column width.
    # ImGuiTableColumnFlags_PreferSortAscending   = 1 << 14,      /* original C++ signature */
    prefer_sort_ascending = (
        enum.auto()
    )  # (= 1 << 14)  # Make the initial sort direction Ascending when first sorting on this column (default).
    # ImGuiTableColumnFlags_PreferSortDescending  = 1 << 15,      /* original C++ signature */
    prefer_sort_descending = (
        enum.auto()
    )  # (= 1 << 15)  # Make the initial sort direction Descending when first sorting on this column.
    # ImGuiTableColumnFlags_IndentEnable          = 1 << 16,      /* original C++ signature */
    indent_enable = enum.auto()  # (= 1 << 16)  # Use current Indent value when entering cell (default for column 0).
    # ImGuiTableColumnFlags_IndentDisable         = 1 << 17,      /* original C++ signature */
    indent_disable = (
        enum.auto()
    )  # (= 1 << 17)  # Ignore current Indent value when entering cell (default for columns > 0). Indentation changes _within_ the cell will still be honored.
    # ImGuiTableColumnFlags_AngledHeader          = 1 << 18,      /* original C++ signature */
    angled_header = (
        enum.auto()
    )  # (= 1 << 18)  # TableHeadersRow() will submit an angled header row for this column. Note this will add an extra row.

    # Output status flags, read-only via TableGetColumnFlags()
    # ImGuiTableColumnFlags_IsEnabled             = 1 << 24,      /* original C++ signature */
    is_enabled = (
        enum.auto()
    )  # (= 1 << 24)  # Status: is enabled == not hidden by user/api (referred to as "Hide" in _DefaultHide and _NoHide) flags.
    # ImGuiTableColumnFlags_IsVisible             = 1 << 25,      /* original C++ signature */
    is_visible = enum.auto()  # (= 1 << 25)  # Status: is visible == is enabled AND not clipped by scrolling.
    # ImGuiTableColumnFlags_IsSorted              = 1 << 26,      /* original C++ signature */
    is_sorted = enum.auto()  # (= 1 << 26)  # Status: is currently part of the sort specs
    # ImGuiTableColumnFlags_IsHovered             = 1 << 27,      /* original C++ signature */
    is_hovered = enum.auto()  # (= 1 << 27)  # Status: is hovered by mouse

    # [Internal] Combinations and masks
    # ImGuiTableColumnFlags_WidthMask_            = ImGuiTableColumnFlags_WidthStretch | ImGuiTableColumnFlags_WidthFixed,    /* original C++ signature */
    width_mask_ = enum.auto()  # (= TableColumnFlags_WidthStretch | TableColumnFlags_WidthFixed)
    # ImGuiTableColumnFlags_IndentMask_           = ImGuiTableColumnFlags_IndentEnable | ImGuiTableColumnFlags_IndentDisable,    /* original C++ signature */
    indent_mask_ = enum.auto()  # (= TableColumnFlags_IndentEnable | TableColumnFlags_IndentDisable)
    # ImGuiTableColumnFlags_StatusMask_           = ImGuiTableColumnFlags_IsEnabled | ImGuiTableColumnFlags_IsVisible | ImGuiTableColumnFlags_IsSorted | ImGuiTableColumnFlags_IsHovered,    /* original C++ signature */
    status_mask_ = (
        enum.auto()
    )  # (= TableColumnFlags_IsEnabled | TableColumnFlags_IsVisible | TableColumnFlags_IsSorted | TableColumnFlags_IsHovered)
    # ImGuiTableColumnFlags_NoDirectResize_       = 1 << 30,      /* original C++ signature */
    no_direct_resize_ = (
        enum.auto()
    )  # (= 1 << 30)  # [Internal] Disable user resizing this column directly (it may however we resized indirectly from its left edge)

class TableRowFlags_(enum.Enum):
    """Flags for ImGui::TableNextRow()"""

    # ImGuiTableRowFlags_None                     = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTableRowFlags_Headers                  = 1 << 0,       /* original C++ signature */
    headers = (
        enum.auto()
    )  # (= 1 << 0)  # Identify header row (set default background color + width of its contents accounted differently for auto column width)

class TableBgTarget_(enum.Enum):
    """Enum for ImGui::TableSetBgColor()
    Background colors are rendering in 3 layers:
     - Layer 0: draw with RowBg0 color if set, otherwise draw with ColumnBg0 if set.
     - Layer 1: draw with RowBg1 color if set, otherwise draw with ColumnBg1 if set.
     - Layer 2: draw with CellBg color if set.
    The purpose of the two row/columns layers is to let you decide if a background color change should override or blend with the existing color.
    When using ImGuiTableFlags_RowBg on the table, each row has the RowBg0 color automatically set for odd/even rows.
    If you set the color of RowBg0 target, your color will override the existing RowBg0 color.
    If you set the color of RowBg1 or ColumnBg1 target, your color will blend over the RowBg0 color.
    """

    # ImGuiTableBgTarget_None                     = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiTableBgTarget_RowBg0                   = 1,            /* original C++ signature */
    row_bg0 = (
        enum.auto()
    )  # (= 1)  # Set row background color 0 (generally used for background, automatically set when ImGuiTableFlags_RowBg is used)
    # ImGuiTableBgTarget_RowBg1                   = 2,            /* original C++ signature */
    row_bg1 = enum.auto()  # (= 2)  # Set row background color 1 (generally used for selection marking)
    # ImGuiTableBgTarget_CellBg                   = 3,            /* original C++ signature */
    cell_bg = enum.auto()  # (= 3)  # Set cell background color (top-most color)

class TableSortSpecs:
    """Sorting specifications for a table (often handling sort specs for a single column, occasionally more)
    Obtained by calling TableGetSortSpecs().
    When 'SpecsDirty == True' you can sort your data. It will be True with sorting specs have changed since last call, or the first time.
    Make sure to set 'SpecsDirty = False' after sorting, else you may wastefully sort your data every frame!
    """

    # const ImGuiTableColumnSortSpecs* Specs;    /* original C++ signature */
    specs: TableColumnSortSpecs  # Pointer to sort spec array. # (const)
    # int                         SpecsCount;    /* original C++ signature */
    specs_count: int  # Sort spec count. Most often 1. May be > 1 when ImGuiTableFlags_SortMulti is enabled. May be == 0 when ImGuiTableFlags_SortTristate is enabled.
    # bool                        SpecsDirty;    /* original C++ signature */
    specs_dirty: (
        bool  # Set to True when specs have changed since last time! Use this to sort again, then clear the flag.
    )

    # ImGuiTableSortSpecs()       { memset(this, 0, sizeof(*this)); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # [ADAPT_IMGUI_BUNDLE]
    #                            #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # IMGUI_API const ImGuiTableColumnSortSpecs& GetSpecs(size_t idx) const;    /* original C++ signature */
    def get_specs(self, idx: int) -> TableColumnSortSpecs:
        pass
    #                            #endif
    #
    # [/ADAPT_IMGUI_BUNDLE]

class TableColumnSortSpecs:
    """Sorting specification for one column of a table (sizeof == 12 bytes)"""

    # ImGuiID                     ColumnUserID;    /* original C++ signature */
    column_user_id: ID  # User id of the column (if specified by a TableSetupColumn() call)
    # ImS16                       ColumnIndex;    /* original C++ signature */
    column_index: ImS16  # Index of the column
    # ImS16                       SortOrder;    /* original C++ signature */
    sort_order: ImS16  # Index within parent ImGuiTableSortSpecs (always stored in order starting from 0, tables sorted on a single criteria will always have a 0 here)
    # ImGuiSortDirection          SortDirection;    /* original C++ signature */
    sort_direction: SortDirection  # ImGuiSortDirection_Ascending or ImGuiSortDirection_Descending

    # ImGuiTableColumnSortSpecs() { memset(this, 0, sizeof(*this)); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # [ADAPT_IMGUI_BUNDLE]
    #                              #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # inline IMGUI_API ImGuiSortDirection GetSortDirection() { return SortDirection; }    /* original C++ signature */
    def get_sort_direction(self) -> SortDirection:
        pass
    # inline IMGUI_API void SetSortDirection(ImGuiSortDirection direction) { SortDirection = direction; }    /* original C++ signature */
    def set_sort_direction(self, direction: SortDirection) -> None:
        pass
    #                              #endif
    #
    # [/ADAPT_IMGUI_BUNDLE]

# -----------------------------------------------------------------------------
# [SECTION] Helpers: Debug log, memory allocations macros, ImVector<>
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Debug Logging into ShowDebugLogWindow(), tty and more.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# IM_MALLOC(), IM_FREE(), IM_NEW(), IM_PLACEMENT_NEW(), IM_DELETE()
# We call C++ constructor on own allocated memory via the placement "new(ptr) Type()" syntax.
# Defining a custom placement new() with a custom parameter allows us to bypass including <new> which on some platforms complains when user has disabled exceptions.
# -----------------------------------------------------------------------------

class ImNewWrapper:
    # ImNewWrapper();    /* original C++ signature */
    def __init__(self) -> None:
        """Auto-generated default constructor"""
        pass

# This is only required so we can use the symmetrical new()

# -----------------------------------------------------------------------------
# ImVector<>
# Lightweight std::vector<>-like class to avoid dragging dependencies (also, some implementations of STL with debug enabled are absurdly slow, we bypass it so our code runs fast in debug).
# -----------------------------------------------------------------------------
# - You generally do NOT need to care or use this ever. But we need to make it available in imgui.h because some of our public structures are relying on it.
# - We use std-like naming convention here, which is a little unusual for this codebase.
# - Important: clear() frees memory, resize(0) keep the allocated buffer. We use resize(0) a lot to intentionally recycle allocated buffers across frames and amortize our costs.
# - Important: our implementation does NOT call C++ constructors/destructors, we treat everything as raw data! This is intentional but be extra mindful of that,
#   Do NOT use this class as a std::vector replacement in your own code! Many of the structures used by dear imgui can be safely initialized by a zero-memset.
# -----------------------------------------------------------------------------

#  ------------------------------------------------------------------------
#      <template specializations for class ImVector>
class ImVector_int:  # Python specialization for ImVector<int>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_int) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> int:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> int:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: int) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: int) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[int]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_uint:  # Python specialization for ImVector<uint>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_uint) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> uint:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> uint:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: uint) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: uint) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[uint]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_float:  # Python specialization for ImVector<float>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_float) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> float:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> float:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: float) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: float) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[float]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_char:  # Python specialization for ImVector<char>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_char) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> str:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> char:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: str) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: str) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[char]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_uchar:  # Python specialization for ImVector<uchar>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_uchar) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> uchar:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> uchar:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: uchar) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: uchar) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[uchar]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImDrawCmd:  # Python specialization for ImVector<ImDrawCmd>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImDrawCmd) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawCmd:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawCmd:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImDrawCmd) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImDrawCmd) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImDrawCmd]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImDrawChannel:  # Python specialization for ImVector<ImDrawChannel>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImDrawChannel) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawChannel:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawChannel:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImDrawChannel) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImDrawChannel) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImDrawChannel]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImDrawVert:  # Python specialization for ImVector<ImDrawVert>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImDrawVert) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawVert:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawVert:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImDrawVert) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImDrawVert) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImDrawVert]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImVec4:  # Python specialization for ImVector<ImVec4>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImVec4Like) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImVec4:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImVec4:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImVec4Like) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImVec4Like) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImVec4]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImVec2:  # Python specialization for ImVector<ImVec2>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImVec2Like) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImVec2:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImVec2:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImVec2Like) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImVec2Like) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImVec2]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImDrawList_ptr:  # Python specialization for ImVector<ImDrawList *>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImDrawList_ptr) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawList:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImDrawList:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImDrawList) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImDrawList) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImDrawList]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImFont_ptr:  # Python specialization for ImVector<ImFont *>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImFont_ptr) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFont:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFont:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImFont) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImFont) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImFont]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImFontGlyph:  # Python specialization for ImVector<ImFontGlyph>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImFontGlyph) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontGlyph:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontGlyph:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImFontGlyph) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImFontGlyph) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImFontGlyph]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_PlatformMonitor:  # Python specialization for ImVector<ImGuiPlatformMonitor>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_PlatformMonitor) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PlatformMonitor:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PlatformMonitor:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: PlatformMonitor) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: PlatformMonitor) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[PlatformMonitor]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_Viewport_ptr:  # Python specialization for ImVector<ImGuiViewport *>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_Viewport_ptr) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> Viewport:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> Viewport:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: Viewport) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: Viewport) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[Viewport]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_Window_ptr:  # Python specialization for ImVector<ImGuiWindow *>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_Window_ptr) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> Window:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> Window:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: Window) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: Window) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[Window]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImFontAtlasCustomRect:  # Python specialization for ImVector<ImFontAtlasCustomRect>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImFontAtlasCustomRect) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontAtlasCustomRect:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontAtlasCustomRect:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImFontAtlasCustomRect) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImFontAtlasCustomRect) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImFontAtlasCustomRect]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImFontConfig:  # Python specialization for ImVector<ImFontConfig>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImFontConfig) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontConfig:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImFontConfig:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImFontConfig) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImFontConfig) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImFontConfig]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_FocusScopeData:  # Python specialization for ImVector<ImGuiFocusScopeData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_FocusScopeData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> FocusScopeData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> FocusScopeData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: FocusScopeData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: FocusScopeData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[FocusScopeData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_SelectionRequest:  # Python specialization for ImVector<ImGuiSelectionRequest>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_SelectionRequest) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> SelectionRequest:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> SelectionRequest:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: SelectionRequest) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: SelectionRequest) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[SelectionRequest]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ImRect:  # Python specialization for ImVector<ImRect>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ImRect) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImRect:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ImRect:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ImRect) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ImRect) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ImRect]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ColorMod:  # Python specialization for ImVector<ImGuiColorMod>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ColorMod) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ColorMod:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ColorMod:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ColorMod) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ColorMod) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ColorMod]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_GroupData:  # Python specialization for ImVector<ImGuiGroupData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_GroupData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> GroupData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> GroupData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: GroupData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: GroupData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[GroupData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_PopupData:  # Python specialization for ImVector<ImGuiPopupData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_PopupData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PopupData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PopupData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: PopupData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: PopupData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[PopupData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ViewportP_ptr:  # Python specialization for ImVector<ImGuiViewportP *>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ViewportP_ptr) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ViewportP:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ViewportP:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ViewportP) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ViewportP) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ViewportP]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_InputEvent:  # Python specialization for ImVector<ImGuiInputEvent>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_InputEvent) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> InputEvent:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> InputEvent:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: InputEvent) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: InputEvent) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[InputEvent]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_WindowStackData:  # Python specialization for ImVector<ImGuiWindowStackData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_WindowStackData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> WindowStackData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> WindowStackData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: WindowStackData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: WindowStackData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[WindowStackData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TableColumnSortSpecs:  # Python specialization for ImVector<ImGuiTableColumnSortSpecs>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TableColumnSortSpecs) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableColumnSortSpecs:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableColumnSortSpecs:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TableColumnSortSpecs) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TableColumnSortSpecs) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TableColumnSortSpecs]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TableInstanceData:  # Python specialization for ImVector<ImGuiTableInstanceData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TableInstanceData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableInstanceData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableInstanceData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TableInstanceData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TableInstanceData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TableInstanceData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TableTempData:  # Python specialization for ImVector<ImGuiTableTempData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TableTempData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableTempData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableTempData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TableTempData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TableTempData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TableTempData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_PtrOrIndex:  # Python specialization for ImVector<ImGuiPtrOrIndex>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_PtrOrIndex) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PtrOrIndex:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> PtrOrIndex:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: PtrOrIndex) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: PtrOrIndex) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[PtrOrIndex]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_SettingsHandler:  # Python specialization for ImVector<ImGuiSettingsHandler>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_SettingsHandler) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> SettingsHandler:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> SettingsHandler:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: SettingsHandler) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: SettingsHandler) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[SettingsHandler]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ShrinkWidthItem:  # Python specialization for ImVector<ImGuiShrinkWidthItem>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ShrinkWidthItem) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ShrinkWidthItem:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ShrinkWidthItem:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ShrinkWidthItem) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ShrinkWidthItem) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ShrinkWidthItem]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_StackLevelInfo:  # Python specialization for ImVector<ImGuiStackLevelInfo>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_StackLevelInfo) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> StackLevelInfo:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> StackLevelInfo:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: StackLevelInfo) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: StackLevelInfo) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[StackLevelInfo]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TabItem:  # Python specialization for ImVector<ImGuiTabItem>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TabItem) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TabItem:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TabItem:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TabItem) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TabItem) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TabItem]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_KeyRoutingData:  # Python specialization for ImVector<ImGuiKeyRoutingData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_KeyRoutingData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> KeyRoutingData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> KeyRoutingData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: KeyRoutingData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: KeyRoutingData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[KeyRoutingData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ListClipperData:  # Python specialization for ImVector<ImGuiListClipperData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ListClipperData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ListClipperData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ListClipperData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ListClipperData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ListClipperData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ListClipperData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_ListClipperRange:  # Python specialization for ImVector<ImGuiListClipperRange>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_ListClipperRange) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ListClipperRange:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> ListClipperRange:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: ListClipperRange) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: ListClipperRange) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[ListClipperRange]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_OldColumnData:  # Python specialization for ImVector<ImGuiOldColumnData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_OldColumnData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> OldColumnData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> OldColumnData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: OldColumnData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: OldColumnData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[OldColumnData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_OldColumns:  # Python specialization for ImVector<ImGuiOldColumns>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_OldColumns) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> OldColumns:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> OldColumns:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: OldColumns) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: OldColumns) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[OldColumns]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_StyleMod:  # Python specialization for ImVector<ImGuiStyleMod>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_StyleMod) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> StyleMod:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> StyleMod:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: StyleMod) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: StyleMod) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[StyleMod]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TableHeaderData:  # Python specialization for ImVector<ImGuiTableHeaderData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TableHeaderData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableHeaderData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TableHeaderData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TableHeaderData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TableHeaderData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TableHeaderData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_TreeNodeStackData:  # Python specialization for ImVector<ImGuiTreeNodeStackData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_TreeNodeStackData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TreeNodeStackData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> TreeNodeStackData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: TreeNodeStackData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: TreeNodeStackData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[TreeNodeStackData]:
        pass

    def __len__(self) -> int:
        pass

class ImVector_MultiSelectTempData:  # Python specialization for ImVector<ImGuiMultiSelectTempData>
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # size_t DataAddress()  { return (size_t)(Data); }    /* original C++ signature */
    def data_address(self) -> int:
        """(private API)"""
        pass
    # #endif
    #

    # inline ImVector()                                       { Size = Capacity = 0; Data = NULL; }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # inline ImVector(const ImVector<T>& src)                 { Size = Capacity = 0; Data = NULL; operator=(src); }    /* original C++ signature */
    @overload
    def __init__(self, src: ImVector_MultiSelectTempData) -> None:
        pass
    # inline void         clear()                             { if (Data) { Size = Capacity = 0; IM_FREE(Data); Data = NULL; } }    /* original C++ signature */
    def clear(self) -> None:
        """Important: does not destruct anything
        (private API)
        """
        pass
    # inline void         clear_destruct()                    { for (int n = 0; n < Size; n++) Data[n].~T(); clear(); }    /* original C++ signature */
    def clear_destruct(self) -> None:
        """Important: never called automatically! always explicit.
        (private API)
        """
        pass
    # inline bool         empty() const                       { return Size == 0; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # inline int          size() const                        { return Size; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # inline const T&     operator[](int i) const             { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> MultiSelectTempData:
        """(private API)"""
        pass
    # inline T&           operator[](int i)                   { IM_ASSERT(i >= 0 && i < Size); return Data[i]; }    /* original C++ signature */
    @overload
    def __getitem__(self, i: int) -> MultiSelectTempData:
        """(private API)"""
        pass
    # NB: It is illegal to call push_back/push_front/insert with a reference pointing inside the ImVector data itself! e.g. v.push_back(v[10]) is forbidden.
    # inline void         push_back(const T& v)               { if (Size == Capacity) reserve(_grow_capacity(Size + 1)); memcpy(&Data[Size], &v, sizeof(v)); Size++; }    /* original C++ signature */
    def push_back(self, v: MultiSelectTempData) -> None:
        """(private API)"""
        pass
    # inline void         pop_back()                          { IM_ASSERT(Size > 0); Size--; }    /* original C++ signature */
    def pop_back(self) -> None:
        """(private API)"""
        pass
    # inline void         push_front(const T& v)              { if (Size == 0) push_back(v); else insert(Data, v); }    /* original C++ signature */
    def push_front(self, v: MultiSelectTempData) -> None:
        """(private API)"""
        pass

    def __iter__(self) -> Iterator[MultiSelectTempData]:
        pass

    def __len__(self) -> int:
        pass

ImVector_ImTextureID = ImVector_int

ImVector_ImDrawIdx = ImVector_uint

ImVector_ID = ImVector_uint

ImVector_ImU32 = ImVector_uint

ImVector_ImWchar32 = ImVector_uint

ImVector_ImWchar = ImVector_ImWchar32

ImVector_ItemFlags = ImVector_int

ImVector_ImU8 = ImVector_uchar

#      </template specializations for class ImVector>
#  ------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# [SECTION] ImGuiStyle
# -----------------------------------------------------------------------------
# You may modify the ImGui::GetStyle() main instance during initialization and before NewFrame().
# During the frame, use ImGui::PushStyleVar(ImGuiStyleVar_XXXX)/PopStyleVar() to alter the main style values,
# and ImGui::PushStyleColor(ImGuiCol_XXX)/PopStyleColor() for colors.
# -----------------------------------------------------------------------------

class Style:
    # float       Alpha;    /* original C++ signature */
    alpha: float  # Global alpha applies to everything in Dear ImGui.
    # float       DisabledAlpha;    /* original C++ signature */
    disabled_alpha: (
        float  # Additional alpha multiplier applied by BeginDisabled(). Multiply over current value of Alpha.
    )
    # ImVec2      WindowPadding;    /* original C++ signature */
    window_padding: ImVec2  # Padding within a window.
    # float       WindowRounding;    /* original C++ signature */
    window_rounding: float  # Radius of window corners rounding. Set to 0.0 to have rectangular windows. Large values tend to lead to variety of artifacts and are not recommended.
    # float       WindowBorderSize;    /* original C++ signature */
    window_border_size: float  # Thickness of border around windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).
    # ImVec2      WindowMinSize;    /* original C++ signature */
    window_min_size: ImVec2  # Minimum window size. This is a global setting. If you want to constrain individual windows, use SetNextWindowSizeConstraints().
    # ImVec2      WindowTitleAlign;    /* original C++ signature */
    window_title_align: (
        ImVec2  # Alignment for title bar text. Defaults to (0.0,0.5) for left-aligned,vertically centered.
    )
    # ImGuiDir    WindowMenuButtonPosition;    /* original C++ signature */
    window_menu_button_position: (
        Dir  # Side of the collapsing/docking button in the title bar (None/Left/Right). Defaults to ImGuiDir_Left.
    )
    # float       ChildRounding;    /* original C++ signature */
    child_rounding: float  # Radius of child window corners rounding. Set to 0.0 to have rectangular windows.
    # float       ChildBorderSize;    /* original C++ signature */
    child_border_size: float  # Thickness of border around child windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).
    # float       PopupRounding;    /* original C++ signature */
    popup_rounding: float  # Radius of popup window corners rounding. (Note that tooltip windows use WindowRounding)
    # float       PopupBorderSize;    /* original C++ signature */
    popup_border_size: float  # Thickness of border around popup/tooltip windows. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).
    # ImVec2      FramePadding;    /* original C++ signature */
    frame_padding: ImVec2  # Padding within a framed rectangle (used by most widgets).
    # float       FrameRounding;    /* original C++ signature */
    frame_rounding: (
        float  # Radius of frame corners rounding. Set to 0.0 to have rectangular frame (used by most widgets).
    )
    # float       FrameBorderSize;    /* original C++ signature */
    frame_border_size: float  # Thickness of border around frames. Generally set to 0.0 or 1.0. (Other values are not well tested and more CPU/GPU costly).
    # ImVec2      ItemSpacing;    /* original C++ signature */
    item_spacing: ImVec2  # Horizontal and vertical spacing between widgets/lines.
    # ImVec2      ItemInnerSpacing;    /* original C++ signature */
    item_inner_spacing: ImVec2  # Horizontal and vertical spacing between within elements of a composed widget (e.g. a slider and its label).
    # ImVec2      CellPadding;    /* original C++ signature */
    cell_padding: ImVec2  # Padding within a table cell. Cellpadding.x is locked for entire table. CellPadding.y may be altered between different rows.
    # ImVec2      TouchExtraPadding;    /* original C++ signature */
    touch_extra_padding: ImVec2  # Expand reactive bounding box for touch-based system where touch position is not accurate enough. Unfortunately we don't sort widgets so priority on overlap will always be given to the first widget. So don't grow this too much!
    # float       IndentSpacing;    /* original C++ signature */
    indent_spacing: (
        float  # Horizontal indentation when e.g. entering a tree node. Generally == (FontSize + FramePadding.x*2).
    )
    # float       ColumnsMinSpacing;    /* original C++ signature */
    columns_min_spacing: float  # Minimum horizontal spacing between two columns. Preferably > (FramePadding.x + 1).
    # float       ScrollbarSize;    /* original C++ signature */
    scrollbar_size: float  # Width of the vertical scrollbar, Height of the horizontal scrollbar.
    # float       ScrollbarRounding;    /* original C++ signature */
    scrollbar_rounding: float  # Radius of grab corners for scrollbar.
    # float       GrabMinSize;    /* original C++ signature */
    grab_min_size: float  # Minimum width/height of a grab box for slider/scrollbar.
    # float       GrabRounding;    /* original C++ signature */
    grab_rounding: float  # Radius of grabs corners rounding. Set to 0.0 to have rectangular slider grabs.
    # float       LayoutAlign;    /* original C++ signature */
    layout_align: float  # Element alignment inside horizontal and vertical layouts (0.0 - left/top, 1.0 - right/bottom, 0.5 - center).
    # float       LogSliderDeadzone;    /* original C++ signature */
    log_slider_deadzone: (
        float  # The size in pixels of the dead-zone around zero on logarithmic sliders that cross zero.
    )
    # float       TabRounding;    /* original C++ signature */
    tab_rounding: float  # Radius of upper corners of a tab. Set to 0.0 to have rectangular tabs.
    # float       TabBorderSize;    /* original C++ signature */
    tab_border_size: float  # Thickness of border around tabs.
    # float       TabMinWidthForCloseButton;    /* original C++ signature */
    tab_min_width_for_close_button: float  # Minimum width for close button to appear on an unselected tab when hovered. Set to 0.0 to always show when hovering, set to FLT_MAX to never show close button unless selected.
    # float       TabBarBorderSize;    /* original C++ signature */
    tab_bar_border_size: float  # Thickness of tab-bar separator, which takes on the tab active color to denote focus.
    # float       TabBarOverlineSize;    /* original C++ signature */
    tab_bar_overline_size: float  # Thickness of tab-bar overline, which highlights the selected tab-bar.
    # float       TableAngledHeadersAngle;    /* original C++ signature */
    table_angled_headers_angle: (
        float  # Angle of angled headers (supported values range from -50.0 degrees to +50.0 degrees).
    )
    # ImVec2      TableAngledHeadersTextAlign;    /* original C++ signature */
    table_angled_headers_text_align: ImVec2  # Alignment of angled headers within the cell
    # ImGuiDir    ColorButtonPosition;    /* original C++ signature */
    color_button_position: (
        Dir  # Side of the color button in the ColorEdit4 widget (left/right). Defaults to ImGuiDir_Right.
    )
    # ImVec2      ButtonTextAlign;    /* original C++ signature */
    button_text_align: (
        ImVec2  # Alignment of button text when button is larger than text. Defaults to (0.5, 0.5) (centered).
    )
    # ImVec2      SelectableTextAlign;    /* original C++ signature */
    selectable_text_align: ImVec2  # Alignment of selectable text. Defaults to (0.0, 0.0) (top-left aligned). It's generally important to keep this left-aligned if you want to lay multiple items on a same line.
    # float       SeparatorTextBorderSize;    /* original C++ signature */
    separator_text_border_size: float  # Thickness of border in SeparatorText()
    # ImVec2      SeparatorTextAlign;    /* original C++ signature */
    separator_text_align: (
        ImVec2  # Alignment of text within the separator. Defaults to (0.0, 0.5) (left aligned, center).
    )
    # ImVec2      SeparatorTextPadding;    /* original C++ signature */
    separator_text_padding: ImVec2  # Horizontal offset of text from each edge of the separator + spacing on other axis. Generally small values. .y is recommended to be == FramePadding.y.
    # ImVec2      DisplayWindowPadding;    /* original C++ signature */
    display_window_padding: ImVec2  # Apply to regular windows: amount which we enforce to keep visible when moving near edges of your screen.
    # ImVec2      DisplaySafeAreaPadding;    /* original C++ signature */
    display_safe_area_padding: ImVec2  # Apply to every windows, menus, popups, tooltips: amount where we avoid displaying contents. Adjust if you cannot see the edges of your screen (e.g. on a TV where scaling has not been configured).
    # float       DockingSeparatorSize;    /* original C++ signature */
    docking_separator_size: float  # Thickness of resizing border between docked windows
    # float       MouseCursorScale;    /* original C++ signature */
    mouse_cursor_scale: float  # Scale software rendered mouse cursor (when io.MouseDrawCursor is enabled). We apply per-monitor DPI scaling over this scale. May be removed later.
    # bool        AntiAliasedLines;    /* original C++ signature */
    anti_aliased_lines: bool  # Enable anti-aliased lines/borders. Disable if you are really tight on CPU/GPU. Latched at the beginning of the frame (copied to ImDrawList).
    # bool        AntiAliasedLinesUseTex;    /* original C++ signature */
    anti_aliased_lines_use_tex: bool  # Enable anti-aliased lines/borders using textures where possible. Require backend to render with bilinear filtering (NOT point/nearest filtering). Latched at the beginning of the frame (copied to ImDrawList).
    # bool        AntiAliasedFill;    /* original C++ signature */
    anti_aliased_fill: bool  # Enable anti-aliased edges around filled shapes (rounded rectangles, circles, etc.). Disable if you are really tight on CPU/GPU. Latched at the beginning of the frame (copied to ImDrawList).
    # float       CurveTessellationTol;    /* original C++ signature */
    curve_tessellation_tol: float  # Tessellation tolerance when using PathBezierCurveTo() without a specific number of segments. Decrease for highly tessellated curves (higher quality, more polygons), increase to reduce quality.
    # float       CircleTessellationMaxError;    /* original C++ signature */
    circle_tessellation_max_error: float  # Maximum error (in pixels) allowed when using AddCircle()/AddCircleFilled() or drawing rounded corner rectangles with no explicit segment count specified. Decrease for higher quality but more geometry.

    # Behaviors
    # (It is possible to modify those fields mid-frame if specific behavior need it, unlike e.g. configuration fields in ImGuiIO)
    # float             HoverStationaryDelay;    /* original C++ signature */
    hover_stationary_delay: (
        float  # Delay for IsItemHovered(ImGuiHoveredFlags_Stationary). Time required to consider mouse stationary.
    )
    # float             HoverDelayShort;    /* original C++ signature */
    hover_delay_short: (
        float  # Delay for IsItemHovered(ImGuiHoveredFlags_DelayShort). Usually used along with HoverStationaryDelay.
    )
    # float             HoverDelayNormal;    /* original C++ signature */
    hover_delay_normal: float  # Delay for IsItemHovered(ImGuiHoveredFlags_DelayNormal). "
    # ImGuiHoveredFlags HoverFlagsForTooltipMouse;    /* original C++ signature */
    hover_flags_for_tooltip_mouse: HoveredFlags  # Default flags when using IsItemHovered(ImGuiHoveredFlags_ForTooltip) or BeginItemTooltip()/SetItemTooltip() while using mouse.
    # ImGuiHoveredFlags HoverFlagsForTooltipNav;    /* original C++ signature */
    hover_flags_for_tooltip_nav: HoveredFlags
    # Default flags when using IsItemHovered(ImGuiHoveredFlags_ForTooltip) or BeginItemTooltip()/SetItemTooltip() while using keyboard/gamepad.

    # [ADAPT_IMGUI_BUNDLE]
    #                                            #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # python adapter for ImGuiStyle::Colors[ImGuiCol_COUNT]
    # You can query and modify those values (0 <= idxColor < Col_.count)
    # inline IMGUI_API  ImVec4& Color_(size_t idxColor) { IM_ASSERT( (idxColor >=0) && (idxColor < ImGuiCol_COUNT)); return Colors[idxColor]; }    /* original C++ signature */
    def color_(self, idx_color: int) -> ImVec4:
        pass
    # inline IMGUI_API  void SetColor_(size_t idxColor, ImVec4 color) { IM_ASSERT( (idxColor >=0) && (idxColor < ImGuiCol_COUNT)); Colors[idxColor] = color; }    /* original C++ signature */
    def set_color_(self, idx_color: int, color: ImVec4Like) -> None:
        pass
    #                                            #endif
    #
    # [/ADAPT_IMGUI_BUNDLE]

    # IMGUI_API ImGuiStyle();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # IMGUI_API void ScaleAllSizes(float scale_factor);    /* original C++ signature */
    def scale_all_sizes(self, scale_factor: float) -> None:
        pass

# -----------------------------------------------------------------------------
# [SECTION] ImGuiIO
# -----------------------------------------------------------------------------
# Communicate most settings and inputs/outputs to Dear ImGui using this structure.
# Access via ImGui::GetIO(). Read 'Programmer guide' section in .cpp file for general usage.
# It is generally expected that:
# - initialization: backends and user code writes to ImGuiIO.
# - main loop: backends writes to ImGuiIO, user code and imgui code reads from ImGuiIO.
# -----------------------------------------------------------------------------
# Also see ImGui::GetPlatformIO() and ImGuiPlatformIO struct for OS/platform related functions: clipboard, IME etc.
# -----------------------------------------------------------------------------

class KeyData:
    """[Internal] Storage used by IsKeyDown(), IsKeyPressed() etc functions.
    If prior to 1.87 you used io.KeysDownDuration[] (which was marked as internal), you should use GetKeyData(key)->DownDuration and *NOT* io.KeysData[key]->DownDuration.
    """

    # bool        Down;    /* original C++ signature */
    down: bool  # True for if key is down
    # float       DownDuration;    /* original C++ signature */
    down_duration: float  # Duration the key has been down (<0.0: not pressed, 0.0: just pressed, >0.0: time held)
    # float       DownDurationPrev;    /* original C++ signature */
    down_duration_prev: float  # Last frame duration the key has been down
    # float       AnalogValue;    /* original C++ signature */
    analog_value: float  # 0.0..1.0 for gamepad values
    # ImGuiKeyData(bool Down = bool(), float DownDuration = float(), float DownDurationPrev = float(), float AnalogValue = float());    /* original C++ signature */
    def __init__(
        self,
        down: bool = bool(),
        down_duration: float = float(),
        down_duration_prev: float = float(),
        analog_value: float = float(),
    ) -> None:
        """Auto-generated default constructor with named params"""
        pass

class IO:
    # ------------------------------------------------------------------
    # Configuration                            // Default value
    # ------------------------------------------------------------------

    # ImGuiConfigFlags   ConfigFlags;    /* original C++ signature */
    config_flags: ConfigFlags  # = 0              // See ImGuiConfigFlags_ enum. Set by user/application. Keyboard/Gamepad navigation options, etc.
    # ImGuiBackendFlags  BackendFlags;    /* original C++ signature */
    backend_flags: BackendFlags  # = 0              // See ImGuiBackendFlags_ enum. Set by backend (imgui_impl_xxx files or custom backend) to communicate features supported by the backend.
    # ImVec2      DisplaySize;    /* original C++ signature */
    display_size: ImVec2  # <unset>          // Main display size, in pixels (generally == GetMainViewport()->Size). May change every frame.
    # float       DeltaTime;    /* original C++ signature */
    delta_time: float  # = 1.0/60.0     // Time elapsed since last frame, in seconds. May change every frame.
    # float       IniSavingRate;    /* original C++ signature */
    ini_saving_rate: float
    # = 5.0           // Minimum time between saving positions/sizes to .ini file, in seconds.

    # void*       UserData;    /* original C++ signature */
    user_data: Any  # = None           // Store your own data.
    # Font system
    # ImFontAtlas*Fonts;    /* original C++ signature */
    fonts: (
        ImFontAtlas  # <auto>           // Font atlas: load, rasterize and pack one or more fonts into a single texture.
    )
    # float       FontGlobalScale;    /* original C++ signature */
    font_global_scale: float  # = 1.0           // Global scale all fonts
    # bool        FontAllowUserScaling;    /* original C++ signature */
    font_allow_user_scaling: (
        bool  # = False          // [OBSOLETE] Allow user scaling text of individual window with CTRL+Wheel.
    )
    # ImFont*     FontDefault;    /* original C++ signature */
    font_default: ImFont  # = None           // Font to use on NewFrame(). Use None to uses Fonts->Fonts[0].
    # ImVec2      DisplayFramebufferScale;    /* original C++ signature */
    display_framebuffer_scale: ImVec2  # = (1, 1)         // For retina display or other situations where window coordinates are different from framebuffer coordinates. This generally ends up in ImDrawData::FramebufferScale.

    # Keyboard/Gamepad Navigation options
    # bool        ConfigNavSwapGamepadButtons;    /* original C++ signature */
    config_nav_swap_gamepad_buttons: bool  # = False          // Swap Activate<>Cancel (A<>B) buttons, matching typical "Nintendo/Japanese style" gamepad layout.
    # bool        ConfigNavMoveSetMousePos;    /* original C++ signature */
    config_nav_move_set_mouse_pos: bool  # = False          // Directional/tabbing navigation teleports the mouse cursor. May be useful on TV/console systems where moving a virtual mouse is difficult. Will update io.MousePos and set io.WantSetMousePos=True.
    # bool        ConfigNavCaptureKeyboard;    /* original C++ signature */
    config_nav_capture_keyboard: bool  # = True           // Sets io.WantCaptureKeyboard when io.NavActive is set.
    # bool        ConfigNavEscapeClearFocusItem;    /* original C++ signature */
    config_nav_escape_clear_focus_item: bool  # = True           // Pressing Escape can clear focused item + navigation id/highlight. Set to False if you want to always keep highlight on.
    # bool        ConfigNavEscapeClearFocusWindow;    /* original C++ signature */
    config_nav_escape_clear_focus_window: bool  # = False          // Pressing Escape can clear focused window as well (super set of io.ConfigNavEscapeClearFocusItem).
    # bool        ConfigNavCursorVisibleAuto;    /* original C++ signature */
    config_nav_cursor_visible_auto: bool  # = True           // Using directional navigation key makes the cursor visible. Mouse click hides the cursor.
    # bool        ConfigNavCursorVisibleAlways;    /* original C++ signature */
    config_nav_cursor_visible_always: bool  # = False          // Navigation cursor is always visible.

    # Docking options (when ImGuiConfigFlags_DockingEnable is set)
    # bool        ConfigDockingNoSplit;    /* original C++ signature */
    config_docking_no_split: bool  # = False          // Simplified docking mode: disable window splitting, so docking is limited to merging multiple windows together into tab-bars.
    # bool        ConfigDockingWithShift;    /* original C++ signature */
    config_docking_with_shift: bool  # = False          // Enable docking with holding Shift key (reduce visual noise, allows dropping in wider space)
    # bool        ConfigDockingAlwaysTabBar;    /* original C++ signature */
    config_docking_always_tab_bar: bool  # = False          // [BETA] [FIXME: This currently creates regression with auto-sizing and general overhead] Make every single floating window display within a docking node.
    # bool        ConfigDockingTransparentPayload;    /* original C++ signature */
    config_docking_transparent_payload: bool  # = False          // [BETA] Make window or viewport transparent when docking and only display docking boxes on the target viewport. Useful if rendering of multiple viewport cannot be synced. Best used with ConfigViewportsNoAutoMerge.

    # Viewport options (when ImGuiConfigFlags_ViewportsEnable is set)
    # bool        ConfigViewportsNoAutoMerge;    /* original C++ signature */
    config_viewports_no_auto_merge: bool  # = False;         // Set to make all floating imgui windows always create their own viewport. Otherwise, they are merged into the main host viewports when overlapping it. May also set ImGuiViewportFlags_NoAutoMerge on individual viewport.
    # bool        ConfigViewportsNoTaskBarIcon;    /* original C++ signature */
    config_viewports_no_task_bar_icon: bool  # = False          // Disable default OS task bar icon flag for secondary viewports. When a viewport doesn't want a task bar icon, ImGuiViewportFlags_NoTaskBarIcon will be set on it.
    # bool        ConfigViewportsNoDecoration;    /* original C++ signature */
    config_viewports_no_decoration: bool  # = True           // Disable default OS window decoration flag for secondary viewports. When a viewport doesn't want window decorations, ImGuiViewportFlags_NoDecoration will be set on it. Enabling decoration can create subsequent issues at OS levels (e.g. minimum window size).
    # bool        ConfigViewportsNoDefaultParent;    /* original C++ signature */
    config_viewports_no_default_parent: bool  # = False          // Disable default OS parenting to main viewport for secondary viewports. By default, viewports are marked with ParentViewportId = <main_viewport>, expecting the platform backend to setup a parent/child relationship between the OS windows (some backend may ignore this). Set to True if you want the default to be 0, then all viewports will be top-level OS windows.

    # Miscellaneous options
    # (you can visualize and interact with all options in 'Demo->Configuration')
    # bool        MouseDrawCursor;    /* original C++ signature */
    mouse_draw_cursor: bool  # = False          // Request ImGui to draw a mouse cursor for you (if you are on a platform without a mouse cursor). Cannot be easily renamed to 'io.ConfigXXX' because this is frequently used by backend implementations.
    # bool        ConfigMacOSXBehaviors;    /* original C++ signature */
    config_mac_osx_behaviors: bool  # = defined(__APPLE__) // Swap Cmd<>Ctrl keys + OS X style text editing cursor movement using Alt instead of Ctrl, Shortcuts using Cmd/Super instead of Ctrl, Line/Text Start and End using Cmd+Arrows instead of Home/End, Double click selects by word instead of selecting whole text, Multi-selection in lists uses Cmd/Super instead of Ctrl.
    # bool        ConfigInputTrickleEventQueue;    /* original C++ signature */
    config_input_trickle_event_queue: bool  # = True           // Enable input queue trickling: some types of events submitted during the same frame (e.g. button down + up) will be spread over multiple frames, improving interactions with low framerates.
    # bool        ConfigInputTextCursorBlink;    /* original C++ signature */
    config_input_text_cursor_blink: (
        bool  # = True           // Enable blinking cursor (optional as some users consider it to be distracting).
    )
    # bool        ConfigInputTextEnterKeepActive;    /* original C++ signature */
    config_input_text_enter_keep_active: (
        bool  # = False          // [BETA] Pressing Enter will keep item active and select contents (single-line only).
    )
    # bool        ConfigDragClickToInputText;    /* original C++ signature */
    config_drag_click_to_input_text: bool  # = False          // [BETA] Enable turning DragXXX widgets into text input with a simple mouse click-release (without moving). Not desirable on devices without a keyboard.
    # bool        ConfigWindowsResizeFromEdges;    /* original C++ signature */
    config_windows_resize_from_edges: bool  # = True           // Enable resizing of windows from their edges and from the lower-left corner. This requires ImGuiBackendFlags_HasMouseCursors for better mouse cursor feedback. (This used to be a per-window ImGuiWindowFlags_ResizeFromAnySide flag)
    # bool        ConfigWindowsMoveFromTitleBarOnly;    /* original C++ signature */
    config_windows_move_from_title_bar_only: bool  # = False      // Enable allowing to move windows only when clicking on their title bar. Does not apply to windows without a title bar.
    # bool        ConfigWindowsCopyContentsWithCtrlC;    /* original C++ signature */
    config_windows_copy_contents_with_ctrl_c: bool  # = False      // [EXPERIMENTAL] CTRL+C copy the contents of focused window into the clipboard. Experimental because: (1) has known issues with nested Begin/End pairs (2) text output quality varies (3) text output is in submission order rather than spatial order.
    # bool        ConfigScrollbarScrollByPage;    /* original C++ signature */
    config_scrollbar_scroll_by_page: bool  # = True           // Enable scrolling page by page when clicking outside the scrollbar grab. When disabled, always scroll to clicked location. When enabled, Shift+Click scrolls to clicked location.
    # float       ConfigMemoryCompactTimer;    /* original C++ signature */
    config_memory_compact_timer: float  # = 60.0          // Timer (in seconds) to free transient windows/tables memory buffers when unused. Set to -1.0 to disable.

    # Inputs Behaviors
    # (other variables, ones which are expected to be tweaked within UI code, are exposed in ImGuiStyle)
    # float       MouseDoubleClickTime;    /* original C++ signature */
    mouse_double_click_time: float  # = 0.30          // Time for a double-click, in seconds.
    # float       MouseDoubleClickMaxDist;    /* original C++ signature */
    mouse_double_click_max_dist: (
        float  # = 6.0           // Distance threshold to stay in to validate a double-click, in pixels.
    )
    # float       MouseDragThreshold;    /* original C++ signature */
    mouse_drag_threshold: float  # = 6.0           // Distance threshold before considering we are dragging.
    # float       KeyRepeatDelay;    /* original C++ signature */
    key_repeat_delay: float  # = 0.275         // When holding a key/button, time before it starts repeating, in seconds (for buttons in Repeat mode, etc.).
    # float       KeyRepeatRate;    /* original C++ signature */
    key_repeat_rate: float  # = 0.050         // When holding a key/button, rate at which it repeats, in seconds.

    # ------------------------------------------------------------------
    # Debug options
    # ------------------------------------------------------------------

    # Options to configure Error Handling and how we handle recoverable errors [EXPERIMENTAL]
    # - Error recovery is provided as a way to facilitate:
    #    - Recovery after a programming error (native code or scripting language - the later tends to facilitate iterating on code while running).
    #    - Recovery after running an exception handler or any error processing which may skip code after an error has been detected.
    # - Error recovery is not perfect nor guaranteed! It is a feature to ease development.
    #   You not are not supposed to rely on it in the course of a normal application run.
    # - Functions that support error recovery are using IM_ASSERT_USER_ERROR() instead of IM_ASSERT().
    # - By design, we do NOT allow error recovery to be 100% silent. One of the three options needs to be checked!
    # - Always ensure that on programmers seats you have at minimum Asserts or Tooltips enabled when making direct imgui API calls!
    #   Otherwise it would severely hinder your ability to catch and correct mistakes!
    # Read https://github.com/ocornut/imgui/wiki/Error-Handling for details.
    # - Programmer seats: keep asserts (default), or disable asserts and keep error tooltips (new and nice!)
    # - Non-programmer seats: maybe disable asserts, but make sure errors are resurfaced (tooltips, visible log entries, use callback etc.)
    # - Recovery after error/exception: record stack sizes with ErrorRecoveryStoreState(), disable assert, set log callback (to e.g. trigger high-level breakpoint), recover with ErrorRecoveryTryToRecoverState(), restore settings.
    # bool        ConfigErrorRecovery;    /* original C++ signature */
    config_error_recovery: bool  # = True       // Enable error recovery support. Some errors won't be detected and lead to direct crashes if recovery is disabled.
    # bool        ConfigErrorRecoveryEnableAssert;    /* original C++ signature */
    config_error_recovery_enable_assert: bool  # = True       // Enable asserts on recoverable error. By default call IM_ASSERT() when returning from a failing IM_ASSERT_USER_ERROR()
    # bool        ConfigErrorRecoveryEnableDebugLog;    /* original C++ signature */
    config_error_recovery_enable_debug_log: bool  # = True       // Enable debug log output on recoverable errors.
    # bool        ConfigErrorRecoveryEnableTooltip;    /* original C++ signature */
    config_error_recovery_enable_tooltip: bool  # = True       // Enable tooltip on recoverable errors. The tooltip include a way to enable asserts if they were disabled.

    # Option to enable various debug tools showing buttons that will call the IM_DEBUG_BREAK() macro.
    # - The Item Picker tool will be available regardless of this being enabled, in order to maximize its discoverability.
    # - Requires a debugger being attached, otherwise IM_DEBUG_BREAK() options will appear to crash your application.
    #   e.g. io.ConfigDebugIsDebuggerPresent = ::IsDebuggerPresent() on Win32, or refer to ImOsIsDebuggerPresent() imgui_test_engine/imgui_te_utils.cpp for a Unix compatible version).
    # bool        ConfigDebugIsDebuggerPresent;    /* original C++ signature */
    config_debug_is_debugger_present: bool  # = False          // Enable various tools calling IM_DEBUG_BREAK().

    # Tools to detect code submitting items with conflicting/duplicate IDs
    # - Code should use PushID()/PopID() in loops, or append "##xx" to same-label identifiers.
    # - Empty label e.g. Button("") == same ID as parent widget/node. Use Button("##xx") instead!
    # - See FAQ https://github.com/ocornut/imgui/blob/master/docs/FAQ.md#q-about-the-id-stack-system
    # bool        ConfigDebugHighlightIdConflicts;    /* original C++ signature */
    config_debug_highlight_id_conflicts: bool  # = True           // Highlight and show an error message when multiple items have conflicting identifiers.

    # Tools to test correct Begin/End and BeginChild/EndChild behaviors.
    # - Presently Begin()/End() and BeginChild()/EndChild() needs to ALWAYS be called in tandem, regardless of return value of BeginXXX()
    # - This is inconsistent with other BeginXXX functions and create confusion for many users.
    # - We expect to update the API eventually. In the meanwhile we provide tools to facilitate checking user-code behavior.
    # bool        ConfigDebugBeginReturnValueOnce;    /* original C++ signature */
    config_debug_begin_return_value_once: bool  # = False          // First-time calls to Begin()/BeginChild() will return False. NEEDS TO BE SET AT APPLICATION BOOT TIME if you don't want to miss windows.
    # bool        ConfigDebugBeginReturnValueLoop;    /* original C++ signature */
    config_debug_begin_return_value_loop: bool  # = False          // Some calls to Begin()/BeginChild() will return False. Will cycle through window depths then repeat. Suggested use: add "io.ConfigDebugBeginReturnValue = io.KeyShift" in your main loop then occasionally press SHIFT. Windows should be flickering while running.

    # Option to deactivate io.AddFocusEvent(False) handling.
    # - May facilitate interactions with a debugger when focus loss leads to clearing inputs data.
    # - Backends may have other side-effects on focus loss, so this will reduce side-effects but not necessary remove all of them.
    # bool        ConfigDebugIgnoreFocusLoss;    /* original C++ signature */
    config_debug_ignore_focus_loss: bool  # = False          // Ignore io.AddFocusEvent(False), consequently not calling io.ClearInputKeys()/io.ClearInputMouse() in input processing.

    # Option to audit .ini data
    # bool        ConfigDebugIniSettings;    /* original C++ signature */
    config_debug_ini_settings: bool  # = False          // Save .ini data with extra comments (particularly helpful for Docking, but makes saving slower)

    # ------------------------------------------------------------------
    # Platform Identifiers
    # (the imgui_impl_xxxx backend files are setting those up for you)
    # ------------------------------------------------------------------

    # Nowadays those would be stored in ImGuiPlatformIO but we are leaving them here for legacy reasons.
    # Optional: Platform/Renderer backend name (informational only! will be displayed in About Window) + User data for backend/wrappers to store their own stuff.
    # const char* BackendPlatformName;    /* original C++ signature */
    backend_platform_name: str  # = None # (const)
    # const char* BackendRendererName;    /* original C++ signature */
    backend_renderer_name: str  # = None # (const)
    # void*       BackendPlatformUserData;    /* original C++ signature */
    backend_platform_user_data: Any  # = None           // User data for platform backend
    # void*       BackendRendererUserData;    /* original C++ signature */
    backend_renderer_user_data: Any  # = None           // User data for renderer backend
    # void*       BackendLanguageUserData;    /* original C++ signature */
    backend_language_user_data: Any  # = None           // User data for non C++ programming language backend

    # ------------------------------------------------------------------
    # Input - Call before calling NewFrame()
    # ------------------------------------------------------------------

    # Input Functions
    # IMGUI_API void  AddKeyEvent(ImGuiKey key, bool down);                       /* original C++ signature */
    def add_key_event(self, key: Key, down: bool) -> None:
        """Queue a new key down/up event. Key should be "translated" (as in, generally ImGuiKey_A matches the key end-user would use to emit an 'A' character)"""
        pass
    # IMGUI_API void  AddKeyAnalogEvent(ImGuiKey key, bool down, float v);        /* original C++ signature */
    def add_key_analog_event(self, key: Key, down: bool, v: float) -> None:
        """Queue a new key down/up event for analog values (e.g. ImGuiKey_Gamepad_ values). Dead-zones should be handled by the backend."""
        pass
    # IMGUI_API void  AddMousePosEvent(float x, float y);                         /* original C++ signature */
    def add_mouse_pos_event(self, x: float, y: float) -> None:
        """Queue a mouse position update. Use -FLT_MAX,-FLT_MAX to signify no mouse (e.g. app not focused and not hovered)"""
        pass
    # IMGUI_API void  AddMouseButtonEvent(int button, bool down);                 /* original C++ signature */
    def add_mouse_button_event(self, button: int, down: bool) -> None:
        """Queue a mouse button change"""
        pass
    # IMGUI_API void  AddMouseWheelEvent(float wheel_x, float wheel_y);           /* original C++ signature */
    def add_mouse_wheel_event(self, wheel_x: float, wheel_y: float) -> None:
        """Queue a mouse wheel update. wheel_y<0: scroll down, wheel_y>0: scroll up, wheel_x<0: scroll right, wheel_x>0: scroll left."""
        pass
    # IMGUI_API void  AddMouseSourceEvent(ImGuiMouseSource source);               /* original C++ signature */
    def add_mouse_source_event(self, source: MouseSource) -> None:
        """Queue a mouse source change (Mouse/TouchScreen/Pen)"""
        pass
    # IMGUI_API void  AddMouseViewportEvent(ImGuiID id);                          /* original C++ signature */
    def add_mouse_viewport_event(self, id_: ID) -> None:
        """Queue a mouse hovered viewport. Requires backend to set ImGuiBackendFlags_HasMouseHoveredViewport to call this (for multi-viewport support)."""
        pass
    # IMGUI_API void  AddFocusEvent(bool focused);                                /* original C++ signature */
    def add_focus_event(self, focused: bool) -> None:
        """Queue a gain/loss of focus for the application (generally based on OS/platform focus of your window)"""
        pass
    # IMGUI_API void  AddInputCharacter(unsigned int c);                          /* original C++ signature */
    def add_input_character(self, c: int) -> None:
        """Queue a new character input"""
        pass
    # IMGUI_API void  AddInputCharacterUTF16(ImWchar16 c);                        /* original C++ signature */
    def add_input_character_utf16(self, c: ImWchar16) -> None:
        """Queue a new character input from a UTF-16 character, it can be a surrogate"""
        pass
    # IMGUI_API void  AddInputCharactersUTF8(const char* str);                    /* original C++ signature */
    def add_input_characters_utf8(self, str: str) -> None:
        """Queue a new characters input from a UTF-8 string"""
        pass
    # IMGUI_API void  SetKeyEventNativeData(ImGuiKey key, int native_keycode, int native_scancode, int native_legacy_index = -1);     /* original C++ signature */
    def set_key_event_native_data(
        self, key: Key, native_keycode: int, native_scancode: int, native_legacy_index: int = -1
    ) -> None:
        """[Optional] Specify index for legacy <1.87 IsKeyXXX() functions with native indices + specify native keycode, scancode."""
        pass
    # IMGUI_API void  SetAppAcceptingEvents(bool accepting_events);               /* original C++ signature */
    def set_app_accepting_events(self, accepting_events: bool) -> None:
        """Set master flag for accepting key/mouse/text events (default to True). Useful if you have native dialog boxes that are interrupting your application loop/refresh, and you want to disable events being queued while your app is frozen."""
        pass
    # IMGUI_API void  ClearEventsQueue();                                         /* original C++ signature */
    def clear_events_queue(self) -> None:
        """Clear all incoming events."""
        pass
    # IMGUI_API void  ClearInputKeys();                                           /* original C++ signature */
    def clear_input_keys(self) -> None:
        """Clear current keyboard/gamepad state + current frame text input buffer. Equivalent to releasing all keys/buttons."""
        pass
    # IMGUI_API void  ClearInputMouse();                                          /* original C++ signature */
    def clear_input_mouse(self) -> None:
        pass
    # Clear current mouse state.

    # ------------------------------------------------------------------
    # Output - Updated by NewFrame() or EndFrame()/Render()
    # (when reading from the io.WantCaptureMouse, io.WantCaptureKeyboard flags to dispatch your inputs, it is
    #  generally easier and more correct to use their state BEFORE calling NewFrame(). See FAQ for details!)
    # ------------------------------------------------------------------

    # bool        WantCaptureMouse;    /* original C++ signature */
    want_capture_mouse: bool  # Set when Dear ImGui will use mouse inputs, in this case do not dispatch them to your main game/application (either way, always pass on mouse inputs to imgui). (e.g. unclicked mouse is hovering over an imgui window, widget is active, mouse was clicked over an imgui window, etc.).
    # bool        WantCaptureKeyboard;    /* original C++ signature */
    want_capture_keyboard: bool  # Set when Dear ImGui will use keyboard inputs, in this case do not dispatch them to your main game/application (either way, always pass keyboard inputs to imgui). (e.g. InputText active, or an imgui window is focused and navigation is enabled, etc.).
    # bool        WantTextInput;    /* original C++ signature */
    want_text_input: bool  # Mobile/console: when set, you may display an on-screen keyboard. This is set by Dear ImGui when it wants textual keyboard input to happen (e.g. when a InputText widget is active).
    # bool        WantSetMousePos;    /* original C++ signature */
    want_set_mouse_pos: bool  # MousePos has been altered, backend should reposition mouse on next frame. Rarely used! Set only when io.ConfigNavMoveSetMousePos is enabled.
    # bool        WantSaveIniSettings;    /* original C++ signature */
    want_save_ini_settings: bool  # When manual .ini load/save is active (io.IniFilename == None), this will be set to notify your application that you can call SaveIniSettingsToMemory() and save yourself. Important: clear io.WantSaveIniSettings yourself after saving!
    # bool        NavActive;    /* original C++ signature */
    nav_active: bool  # Keyboard/Gamepad navigation is currently allowed (will handle ImGuiKey_NavXXX events) = a window is focused and it doesn't use the ImGuiWindowFlags_NoNavInputs flag.
    # bool        NavVisible;    /* original C++ signature */
    nav_visible: (
        bool  # Keyboard/Gamepad navigation highlight is visible and allowed (will handle ImGuiKey_NavXXX events).
    )
    # float       Framerate;    /* original C++ signature */
    framerate: float  # Estimate of application framerate (rolling average over 60 frames, based on io.DeltaTime), in frame per second. Solely for convenience. Slow applications may not want to use a moving average or may want to reset underlying buffers occasionally.
    # int         MetricsRenderVertices;    /* original C++ signature */
    metrics_render_vertices: int  # Vertices output during last call to Render()
    # int         MetricsRenderIndices;    /* original C++ signature */
    metrics_render_indices: int  # Indices output during last call to Render() = number of triangles * 3
    # int         MetricsRenderWindows;    /* original C++ signature */
    metrics_render_windows: int  # Number of visible windows
    # int         MetricsActiveWindows;    /* original C++ signature */
    metrics_active_windows: int  # Number of active windows
    # ImVec2      MouseDelta;    /* original C++ signature */
    mouse_delta: ImVec2  # Mouse delta. Note that this is zero if either current or previous position are invalid (-FLT_MAX,-FLT_MAX), so a disappearing/reappearing mouse won't have a huge delta.

    # ------------------------------------------------------------------
    # [Internal] Dear ImGui will maintain those fields. Forward compatibility not guaranteed!
    # ------------------------------------------------------------------

    # ImGuiContext* Ctx;    /* original C++ signature */
    ctx: Context  # Parent UI context (needs to be set explicitly by parent).

    # Main Input State
    # (this block used to be written by backend, since 1.87 it is best to NOT write to those directly, call the AddXXX functions above instead)
    # (reading from those variables is fair game, as they are extremely unlikely to be moving anywhere)
    # ImVec2      MousePos;    /* original C++ signature */
    mouse_pos: ImVec2  # Mouse position, in pixels. Set to ImVec2(-FLT_MAX, -FLT_MAX) if mouse is unavailable (on another screen, etc.)
    # bool        MouseDown[5];    /* original C++ signature */
    mouse_down: (
        np.ndarray
    )  # ndarray[type=bool, size=5]  # Mouse buttons: 0=left, 1=right, 2=middle + extras (ImGuiMouseButton_COUNT == 5). Dear ImGui mostly uses left and right buttons. Other buttons allow us to track if the mouse is being used by your application + available to user as a convenience via IsMouse** API.
    # float       MouseWheel;    /* original C++ signature */
    mouse_wheel: float  # Mouse wheel Vertical: 1 unit scrolls about 5 lines text. >0 scrolls Up, <0 scrolls Down. Hold SHIFT to turn vertical scroll into horizontal scroll.
    # float       MouseWheelH;    /* original C++ signature */
    mouse_wheel_h: float  # Mouse wheel Horizontal. >0 scrolls Left, <0 scrolls Right. Most users don't have a mouse with a horizontal wheel, may not be filled by all backends.
    # ImGuiMouseSource MouseSource;    /* original C++ signature */
    mouse_source: MouseSource  # Mouse actual input peripheral (Mouse/TouchScreen/Pen).
    # ImGuiID     MouseHoveredViewport;    /* original C++ signature */
    mouse_hovered_viewport: ID  # (Optional) Modify using io.AddMouseViewportEvent(). With multi-viewports: viewport the OS mouse is hovering. If possible _IGNORING_ viewports with the ImGuiViewportFlags_NoInputs flag is much better (few backends can handle that). Set io.BackendFlags |= ImGuiBackendFlags_HasMouseHoveredViewport if you can provide this info. If you don't imgui will infer the value using the rectangles and last focused time of the viewports it knows about (ignoring other OS windows).
    # bool        KeyCtrl;    /* original C++ signature */
    key_ctrl: bool  # Keyboard modifier down: Control
    # bool        KeyShift;    /* original C++ signature */
    key_shift: bool  # Keyboard modifier down: Shift
    # bool        KeyAlt;    /* original C++ signature */
    key_alt: bool  # Keyboard modifier down: Alt
    # bool        KeySuper;    /* original C++ signature */
    key_super: bool  # Keyboard modifier down: Cmd/Super/Windows

    # Other state maintained from data above + IO function calls
    # ImGuiKeyChord KeyMods;    /* original C++ signature */
    key_mods: KeyChord  # Key mods flags (any of ImGuiMod_Ctrl/ImGuiMod_Shift/ImGuiMod_Alt/ImGuiMod_Super flags, same as io.KeyCtrl/KeyShift/KeyAlt/KeySuper but merged into flags. Read-only, updated by NewFrame()
    # bool        WantCaptureMouseUnlessPopupClose;    /* original C++ signature */
    want_capture_mouse_unless_popup_close: bool  # Alternative to WantCaptureMouse: (WantCaptureMouse == True && WantCaptureMouseUnlessPopupClose == False) when a click over None is expected to close a popup.
    # ImVec2      MousePosPrev;    /* original C++ signature */
    mouse_pos_prev: ImVec2  # Previous mouse position (note that MouseDelta is not necessary == MousePos-MousePosPrev, in case either position is invalid)
    # double      MouseClickedTime[5];    /* original C++ signature */
    mouse_clicked_time: (
        np.ndarray
    )  # ndarray[type=double, size=5]  # Time of last click (used to figure out double-click)
    # bool        MouseClicked[5];    /* original C++ signature */
    mouse_clicked: (
        np.ndarray
    )  # ndarray[type=bool, size=5]  # Mouse button went from !Down to Down (same as MouseClickedCount[x] != 0)
    # bool        MouseDoubleClicked[5];    /* original C++ signature */
    mouse_double_clicked: (
        np.ndarray
    )  # ndarray[type=bool, size=5]  # Has mouse button been double-clicked? (same as MouseClickedCount[x] == 2)
    # ImU16       MouseClickedCount[5];    /* original C++ signature */
    mouse_clicked_count: (
        np.ndarray
    )  # ndarray[type=ImU16, size=5]  # == 0 (not clicked), == 1 (same as MouseClicked[]), == 2 (double-clicked), == 3 (triple-clicked) etc. when going from !Down to Down
    # ImU16       MouseClickedLastCount[5];    /* original C++ signature */
    mouse_clicked_last_count: (
        np.ndarray
    )  # ndarray[type=ImU16, size=5]  # Count successive number of clicks. Stays valid after mouse release. Reset after another click is done.
    # bool        MouseReleased[5];    /* original C++ signature */
    mouse_released: np.ndarray  # ndarray[type=bool, size=5]  # Mouse button went from Down to !Down
    # bool        MouseDownOwned[5];    /* original C++ signature */
    mouse_down_owned: (
        np.ndarray
    )  # ndarray[type=bool, size=5]  # Track if button was clicked inside a dear imgui window or over None blocked by a popup. We don't request mouse capture from the application if click started outside ImGui bounds.
    # bool        MouseDownOwnedUnlessPopupClose[5];    /* original C++ signature */
    mouse_down_owned_unless_popup_close: (
        np.ndarray
    )  # ndarray[type=bool, size=5]  # Track if button was clicked inside a dear imgui window.
    # bool        MouseWheelRequestAxisSwap;    /* original C++ signature */
    mouse_wheel_request_axis_swap: bool  # On a non-Mac system, holding SHIFT requests WheelY to perform the equivalent of a WheelX event. On a Mac system this is already enforced by the system.
    # bool        MouseCtrlLeftAsRightClick;    /* original C++ signature */
    mouse_ctrl_left_as_right_click: (
        bool  # (OSX) Set to True when the current click was a ctrl-click that spawned a simulated right click
    )
    # float       MouseDownDuration[5];    /* original C++ signature */
    mouse_down_duration: (
        np.ndarray
    )  # ndarray[type=float, size=5]  # Duration the mouse button has been down (0.0 == just clicked)
    # float       MouseDownDurationPrev[5];    /* original C++ signature */
    mouse_down_duration_prev: np.ndarray  # ndarray[type=float, size=5]  # Previous time the mouse button has been down
    # float       MouseDragMaxDistanceSqr[5];    /* original C++ signature */
    mouse_drag_max_distance_sqr: (
        np.ndarray
    )  # ndarray[type=float, size=5]  # Squared maximum distance of how much mouse has traveled from the clicking point (used for moving thresholds)
    # float       PenPressure;    /* original C++ signature */
    pen_pressure: float  # Touch/Pen pressure (0.0 to 1.0, should be >0.0 only when MouseDown[0] == True). Helper storage currently unused by Dear ImGui.
    # bool        AppFocusLost;    /* original C++ signature */
    app_focus_lost: bool  # Only modify via AddFocusEvent()
    # bool        AppAcceptingEvents;    /* original C++ signature */
    app_accepting_events: bool  # Only modify via SetAppAcceptingEvents()
    # ImWchar16   InputQueueSurrogate;    /* original C++ signature */
    input_queue_surrogate: ImWchar16  # For AddInputCharacterUTF16()
    # ImVector<ImWchar> InputQueueCharacters;    /* original C++ signature */
    input_queue_characters: ImVector_ImWchar
    # Queue of _characters_ input (obtained by platform backend). Fill using AddInputCharacter() helper.

    # Legacy: before 1.87, we required backend to fill io.KeyMap[] (imgui->native map) during initialization and io.KeysDown[] (native indices) every frame.
    # This is still temporarily supported as a legacy feature. However the new preferred scheme is for backend to call io.AddKeyEvent().
    #   Old (<1.87):  ImGui::IsKeyPressed(ImGui::GetIO().KeyMap[ImGuiKey_Space]) --> New (1.87+) ImGui::IsKeyPressed(ImGuiKey_Space)
    #   Old (<1.87):  ImGui::IsKeyPressed(MYPLATFORM_KEY_SPACE)                  --> New (1.87+) ImGui::IsKeyPressed(ImGuiKey_Space)
    # Read https://github.com/ocornut/imgui/issues/4921 for details.
    # int       KeyMap[ImGuiKey_COUNT];             // [LEGACY] Input: map of indices into the KeysDown[512] entries array which represent your "native" keyboard state. The first 512 are now unused and should be kept zero. Legacy backend will write into KeyMap[] using ImGuiKey_ indices which are always >512.
    # bool      KeysDown[ImGuiKey_COUNT];           // [LEGACY] Input: Keyboard keys that are pressed (ideally left in the "native" order your engine has access to keyboard keys, so you can use your own defines/enums for keys). This used to be [512] sized. It is now ImGuiKey_COUNT to allow legacy io.KeysDown[GetKeyIndex(...)] to work without an overflow.
    # float     NavInputs[ImGuiNavInput_COUNT];     // [LEGACY] Since 1.88, NavInputs[] was removed. Backends from 1.60 to 1.86 won't build. Feed gamepad inputs via io.AddKeyEvent() and ImGuiKey_GamepadXXX enums.
    # None*     ImeWindowHandle;                    // [Obsoleted in 1.87] Set ImGuiViewport::PlatformHandleRaw instead. Set this to your HWND to get automatic IME cursor positioning.

    # Legacy: before 1.91.1, clipboard functions were stored in ImGuiIO instead of ImGuiPlatformIO.
    # As this is will affect all users of custom engines/backends, we are providing proper legacy redirection (will obsolete).

    # IMGUI_API   ImGuiIO();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # [ADAPT_IMGUI_BUNDLE]

    #                                                                   #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # IMGUI_API void SetIniFilename(const char* filename);    /* original C++ signature */
    def set_ini_filename(self, filename: str) -> None:
        pass
    # IMGUI_API void SetLogFilename(const char* filename);    /* original C++ signature */
    def set_log_filename(self, filename: str) -> None:
        pass
    # IMGUI_API std::string GetIniFilename();    /* original C++ signature */
    def get_ini_filename(self) -> str:
        pass
    # IMGUI_API std::string GetLogFilename();    /* original C++ signature */
    def get_log_filename(self) -> str:
        pass
    #                                                                   #endif
    #
    # [/ADAPT_IMGUI_BUNDLE]

# -----------------------------------------------------------------------------
# [SECTION] Misc data structures (ImGuiInputTextCallbackData, ImGuiSizeCallbackData, ImGuiPayload)
# -----------------------------------------------------------------------------

class InputTextCallbackData:
    """Shared state of InputText(), passed as an argument to your callback when a ImGuiInputTextFlags_Callback* flag is used.
    The callback function should return 0 by default.
    Callbacks (follow a flag name and see comments in ImGuiInputTextFlags_ declarations for more details)
    - ImGuiInputTextFlags_CallbackEdit:        Callback on buffer edit (note that InputText() already returns True on edit, the callback is useful mainly to manipulate the underlying buffer while focus is active)
    - ImGuiInputTextFlags_CallbackAlways:      Callback on each iteration
    - ImGuiInputTextFlags_CallbackCompletion:  Callback on pressing TAB
    - ImGuiInputTextFlags_CallbackHistory:     Callback on pressing Up/Down arrows
    - ImGuiInputTextFlags_CallbackCharFilter:  Callback on character inputs to replace or discard them. Modify 'EventChar' to replace or discard, or return 1 in callback to discard.
    - ImGuiInputTextFlags_CallbackResize:      Callback on buffer capacity changes request (beyond 'buf_size' parameter value), allowing the string to grow.
    """

    # ImGuiContext*       Ctx;    /* original C++ signature */
    ctx: Context  # Parent UI context
    # ImGuiInputTextFlags EventFlag;    /* original C++ signature */
    event_flag: InputTextFlags  # One ImGuiInputTextFlags_Callback*    // Read-only
    # ImGuiInputTextFlags Flags;    /* original C++ signature */
    flags: InputTextFlags  # What user passed to InputText()      // Read-only
    # void*               UserData;    /* original C++ signature */
    user_data: Any  # What user passed to InputText()      // Read-only

    # Arguments for the different callback events
    # - During Resize callback, Buf will be same as your input buffer.
    # - However, during Completion/History/Always callback, Buf always points to our own internal data (it is not the same as your buffer)! Changes to it will be reflected into your own buffer shortly after the callback.
    # - To modify the text buffer in a callback, prefer using the InsertChars() / DeleteChars() function. InsertChars() will take care of calling the resize callback if necessary.
    # - If you know your edits are not going to resize the underlying buffer allocation, you may modify the contents of 'Buf[]' directly. You need to update 'BufTextLen' accordingly (0 <= BufTextLen < BufSize) and set 'BufDirty'' to True so InputText can update its internal state.
    # ImWchar             EventChar;    /* original C++ signature */
    event_char: ImWchar  # Character input                      // Read-write   // [CharFilter] Replace character with another one, or set to zero to drop. return 1 is equivalent to setting EventChar=0;
    # ImGuiKey            EventKey;    /* original C++ signature */
    event_key: Key  # Key pressed (Up/Down/TAB)            // Read-only    // [Completion,History]
    # char*               Buf;    /* original C++ signature */
    buf: char  # Text buffer                          // Read-write   // [Resize] Can replace pointer / [Completion,History,Always] Only write to pointed data, don't replace the actual pointer! # (read-only)
    # int                 BufTextLen;    /* original C++ signature */
    buf_text_len: int  # Text length (in bytes)               // Read-write   // [Resize,Completion,History,Always] Exclude zero-terminator storage. In C land: == strlen(some_text), in C++ land: string.length()
    # int                 BufSize;    /* original C++ signature */
    buf_size: int  # Buffer size (in bytes) = capacity+1  // Read-only    // [Resize,Completion,History,Always] Include zero-terminator storage. In C land == ARRAYSIZE(my_char_array), in C++ land: string.capacity()+1
    # bool                BufDirty;    /* original C++ signature */
    buf_dirty: bool  # Set if you modify Buf/BufTextLen!    // Write        // [Completion,History,Always]
    # int                 CursorPos;    /* original C++ signature */
    cursor_pos: int  #                                      // Read-write   // [Completion,History,Always]
    # int                 SelectionStart;    /* original C++ signature */
    selection_start: int  #                                      // Read-write   // [Completion,History,Always] == to SelectionEnd when no selection)
    # int                 SelectionEnd;    /* original C++ signature */
    selection_end: int  #                                      // Read-write   // [Completion,History,Always]

    # Helper functions for text manipulation.
    # Use those function to benefit from the CallbackResize behaviors. Calling those function reset the selection.
    # IMGUI_API ImGuiInputTextCallbackData();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # IMGUI_API void      DeleteChars(int pos, int bytes_count);    /* original C++ signature */
    def delete_chars(self, pos: int, bytes_count: int) -> None:
        pass
    # IMGUI_API void      InsertChars(int pos, const char* text, const char* text_end = NULL);    /* original C++ signature */
    def insert_chars(self, pos: int, text: str, text_end: Optional[str] = None) -> None:
        pass
    # void                SelectAll()             { SelectionStart = 0; SelectionEnd = BufTextLen; }    /* original C++ signature */
    def select_all(self) -> None:
        """(private API)"""
        pass
    # void                ClearSelection()        { SelectionStart = SelectionEnd = BufTextLen; }    /* original C++ signature */
    def clear_selection(self) -> None:
        """(private API)"""
        pass
    # bool                HasSelection() const    { return SelectionStart != SelectionEnd; }    /* original C++ signature */
    def has_selection(self) -> bool:
        """(private API)"""
        pass

class SizeCallbackData:
    """Resizing callback data to apply custom constraint. As enabled by SetNextWindowSizeConstraints(). Callback is called during the next Begin().
    NB: For basic min/max size constraint on each axis you don't need to use the callback! The SetNextWindowSizeConstraints() parameters are enough.
    """

    # void*   UserData;    /* original C++ signature */
    user_data: Any  # Read-only.   What user passed to SetNextWindowSizeConstraints(). Generally store an integer or float in here (need reinterpret_cast<>).
    # ImVec2  Pos;    /* original C++ signature */
    pos: ImVec2  # Read-only.   Window position, for reference.
    # ImVec2  CurrentSize;    /* original C++ signature */
    current_size: ImVec2  # Read-only.   Current window size.
    # ImVec2  DesiredSize;    /* original C++ signature */
    desired_size: (
        ImVec2  # Read-write.  Desired size, based on user's mouse position. Write to this field to restrain resizing.
    )
    # ImGuiSizeCallbackData(ImVec2 Pos = ImVec2(), ImVec2 CurrentSize = ImVec2(), ImVec2 DesiredSize = ImVec2());    /* original C++ signature */
    def __init__(
        self,
        pos: Optional[ImVec2Like] = None,
        current_size: Optional[ImVec2Like] = None,
        desired_size: Optional[ImVec2Like] = None,
    ) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                Pos: ImVec2()
                CurrentSize: ImVec2()
                DesiredSize: ImVec2()
        """
        pass

class WindowClass:
    """[ALPHA] Rarely used / very advanced uses only. Use with SetNextWindowClass() and DockSpace() functions.
    Important: the content of this class is still highly WIP and likely to change and be refactored
    before we stabilize Docking features. Please be mindful if using this.
    Provide hints:
    - To the platform backend via altered viewport flags (enable/disable OS decoration, OS task bar icons, etc.)
    - To the platform backend for OS level parent/child relationships of viewport.
    - To the docking system for various options and filtering.
    """

    # ImGuiID             ClassId;    /* original C++ signature */
    class_id: (
        ID  # User data. 0 = Default class (unclassed). Windows of different classes cannot be docked with each others.
    )
    # ImGuiID             ParentViewportId;    /* original C++ signature */
    parent_viewport_id: ID  # Hint for the platform backend. -1: use default. 0: request platform backend to not parent the platform. != 0: request platform backend to create a parent<>child relationship between the platform windows. Not conforming backends are free to e.g. parent every viewport to the main viewport or not.
    # ImGuiID             FocusRouteParentWindowId;    /* original C++ signature */
    focus_route_parent_window_id: ID  # ID of parent window for shortcut focus route evaluation, e.g. Shortcut() call from Parent Window will succeed when this window is focused.
    # ImGuiViewportFlags  ViewportFlagsOverrideSet;    /* original C++ signature */
    viewport_flags_override_set: ViewportFlags  # Viewport flags to set when a window of this class owns a viewport. This allows you to enforce OS decoration or task bar icon, override the defaults on a per-window basis.
    # ImGuiViewportFlags  ViewportFlagsOverrideClear;    /* original C++ signature */
    viewport_flags_override_clear: ViewportFlags  # Viewport flags to clear when a window of this class owns a viewport. This allows you to enforce OS decoration or task bar icon, override the defaults on a per-window basis.
    # ImGuiTabItemFlags   TabItemFlagsOverrideSet;    /* original C++ signature */
    tab_item_flags_override_set: TabItemFlags  # [EXPERIMENTAL] TabItem flags to set when a window of this class gets submitted into a dock node tab bar. May use with ImGuiTabItemFlags_Leading or ImGuiTabItemFlags_Trailing.
    # ImGuiDockNodeFlags  DockNodeFlagsOverrideSet;    /* original C++ signature */
    dock_node_flags_override_set: DockNodeFlags  # [EXPERIMENTAL] Dock node flags to set when a window of this class is hosted by a dock node (it doesn't have to be selected!)
    # bool                DockingAlwaysTabBar;    /* original C++ signature */
    docking_always_tab_bar: bool  # Set to True to enforce single floating windows of this class always having their own docking node (equivalent of setting the global io.ConfigDockingAlwaysTabBar)
    # bool                DockingAllowUnclassed;    /* original C++ signature */
    docking_allow_unclassed: bool  # Set to True to allow windows of this class to be docked/merged with an unclassed window. // FIXME-DOCK: Move to DockNodeFlags override?

    # ImGuiWindowClass() { memset(this, 0, sizeof(*this)); ParentViewportId = (ImGuiID)-1; DockingAllowUnclassed = true; }    /* original C++ signature */
    def __init__(self) -> None:
        pass

class Payload:
    """Data payload for Drag and Drop operations: AcceptDragDropPayload(), GetDragDropPayload()"""

    # Members
    # void*           Data;    /* original C++ signature */
    data: Any  # Data (copied and owned by dear imgui)
    # int             DataSize;    /* original C++ signature */
    data_size: int  # Data size

    # [Internal]
    # ImGuiID         SourceId;    /* original C++ signature */
    source_id: ID  # Source item id
    # ImGuiID         SourceParentId;    /* original C++ signature */
    source_parent_id: ID  # Source parent id (if available)
    # int             DataFrameCount;    /* original C++ signature */
    data_frame_count: int  # Data timestamp
    # bool            Preview;    /* original C++ signature */
    preview: bool  # Set when AcceptDragDropPayload() was called and mouse has been hovering the target item (nb: handle overlapping drag targets)
    # bool            Delivery;    /* original C++ signature */
    delivery: bool  # Set when AcceptDragDropPayload() was called and mouse button is released over the target item.

    # ImGuiPayload()  { Clear(); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # void Clear()    { SourceId = SourceParentId = 0; Data = NULL; DataSize = 0; memset(DataType, 0, sizeof(DataType)); DataFrameCount = -1; Preview = Delivery = false; }    /* original C++ signature */
    def clear(self) -> None:
        """(private API)"""
        pass
    # bool IsDataType(const char* type) const { return DataFrameCount != -1 && strcmp(type, DataType) == 0; }    /* original C++ signature */
    def is_data_type(self, type: str) -> bool:
        """(private API)"""
        pass
    # bool IsPreview() const                  { return Preview; }    /* original C++ signature */
    def is_preview(self) -> bool:
        """(private API)"""
        pass
    # bool IsDelivery() const                 { return Delivery; }    /* original C++ signature */
    def is_delivery(self) -> bool:
        """(private API)"""
        pass

# -----------------------------------------------------------------------------
# [SECTION] Helpers (ImGuiOnceUponAFrame, ImGuiTextFilter, ImGuiTextBuffer, ImGuiStorage, ImGuiListClipper, Math Operators, ImColor)
# -----------------------------------------------------------------------------

# Helper: Unicode defines

class OnceUponAFrame:
    """Helper: Execute a block of code at maximum once a frame. Convenient if you want to quickly create a UI within deep-nested code that runs multiple times every frame.
    Usage: static ImGuiOnceUponAFrame oaf; if (oaf) ImGui::Text("This will be called only once per frame");
    """

    # ImGuiOnceUponAFrame() { RefFrame = -1; }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # mutable int RefFrame;    /* original C++ signature */
    ref_frame: int
    # operator bool() const { int current_frame = ImGui::GetFrameCount(); if (RefFrame == current_frame) return false; RefFrame = current_frame; return true; }    /* original C++ signature */
    def __bool__(self) -> bool:
        pass

class TextFilter:
    """Helper: Parse and apply text filters. In format "aaaaa[,bbbb][,ccccc]" """

    # IMGUI_API           ImGuiTextFilter(const char* default_filter = "");    /* original C++ signature */
    def __init__(self, default_filter: str = "") -> None:
        pass
    # IMGUI_API bool      Draw(const char* label = "Filter (inc,-exc)", float width = 0.0f);      /* original C++ signature */
    def draw(self, label: str = "Filter (inc,-exc)", width: float = 0.0) -> bool:
        """Helper calling InputText+Build"""
        pass
    # IMGUI_API bool      PassFilter(const char* text, const char* text_end = NULL) const;    /* original C++ signature */
    def pass_filter(self, text: str, text_end: Optional[str] = None) -> bool:
        pass
    # IMGUI_API void      Build();    /* original C++ signature */
    def build(self) -> None:
        pass
    # void                Clear()          { InputBuf[0] = 0; Build(); }    /* original C++ signature */
    def clear(self) -> None:
        """(private API)"""
        pass
    # bool                IsActive() const { return !Filters.empty(); }    /* original C++ signature */
    def is_active(self) -> bool:
        """(private API)"""
        pass

    class TextRange:
        """[Internal]"""

        # const char*     b;    /* original C++ signature */
        b: str  # (const)
        # const char*     e;    /* original C++ signature */
        e: str  # (const)

        # ImGuiTextRange()                                { b = e = NULL; }    /* original C++ signature */
        @overload
        def __init__(self) -> None:
            pass
        # ImGuiTextRange(const char* _b, const char* _e)  { b = _b; e = _e; }    /* original C++ signature */
        @overload
        def __init__(self, _b: str, _e: str) -> None:
            pass
        # bool            empty() const                   { return b == e; }    /* original C++ signature */
        def empty(self) -> bool:
            """(private API)"""
            pass

    # int                     CountGrep;    /* original C++ signature */
    count_grep: int

class TextBuffer:
    """Helper: Growable text buffer for logging/accumulating text
    (this could be called 'ImGuiTextBuilder' / 'ImGuiStringBuilder')
    """

    # ImVector<char>      Buf;    /* original C++ signature */
    buf: ImVector_char

    # ImGuiTextBuffer()   { }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # inline char         operator[](int i) const { IM_ASSERT(Buf.Data != NULL); return Buf.Data[i]; }    /* original C++ signature */
    def __getitem__(self, i: int) -> int:
        """(private API)"""
        pass
    # const char*         begin() const           { return Buf.Data ? &Buf.front() : EmptyString; }    /* original C++ signature */
    def begin(self) -> str:
        """(private API)"""
        pass
    # const char*         end() const             { return Buf.Data ? &Buf.back() : EmptyString; }       /* original C++ signature */
    def end(self) -> str:
        """(private API)

        Buf is zero-terminated, so end() will point on the zero-terminator
        """
        pass
    # int                 size() const            { return Buf.Size ? Buf.Size - 1 : 0; }    /* original C++ signature */
    def size(self) -> int:
        """(private API)"""
        pass
    # bool                empty() const           { return Buf.Size <= 1; }    /* original C++ signature */
    def empty(self) -> bool:
        """(private API)"""
        pass
    # void                clear()                 { Buf.clear(); }    /* original C++ signature */
    def clear(self) -> None:
        """(private API)"""
        pass
    # void                reserve(int capacity)   { Buf.reserve(capacity); }    /* original C++ signature */
    def reserve(self, capacity: int) -> None:
        """(private API)"""
        pass
    # const char*         c_str() const           { return Buf.Data ? Buf.Data : EmptyString; }    /* original C++ signature */
    def c_str(self) -> str:
        """(private API)"""
        pass
    # IMGUI_API void      append(const char* str, const char* str_end = NULL);    /* original C++ signature */
    def append(self, str: str, str_end: Optional[str] = None) -> None:
        pass
    # IMGUI_API void      appendf(const char* fmt, ...) ;    /* original C++ signature */
    def appendf(self, fmt: str) -> None:
        pass

class StoragePair:
    """[Internal] Key+Value for ImGuiStorage"""

    # ImGuiID     key;    /* original C++ signature */
    key: ID
    # ImGuiStoragePair(ImGuiID _key, int _val)    { key = _key; val_i = _val; }    /* original C++ signature */
    @overload
    def __init__(self, _key: ID, _val: int) -> None:
        pass
    # ImGuiStoragePair(ImGuiID _key, float _val)  { key = _key; val_f = _val; }    /* original C++ signature */
    @overload
    def __init__(self, _key: ID, _val: float) -> None:
        pass
    # ImGuiStoragePair(ImGuiID _key, void* _val)  { key = _key; val_p = _val; }    /* original C++ signature */
    @overload
    def __init__(self, _key: ID, _val: Any) -> None:
        pass

class Storage:
    """Helper: Key->Value storage
    Typically you don't have to worry about this since a storage is held within each Window.
    We use it to e.g. store collapse state for a tree (Int 0/1)
    This is optimized for efficient lookup (dichotomy into a contiguous buffer) and rare insertion (typically tied to user interactions aka max once a frame)
    You can use it as custom user storage for temporary values. Declare your own storage if, for example:
    - You want to manipulate the open/close state of a particular sub-tree in your interface (tree node uses Int 0/1 to store their state).
    - You want to store custom debug data easily without adding or editing structures in your code (probably not efficient, but convenient)
    Types are NOT stored, so it is up to you to make sure your Key don't collide with different types.
    """

    # void                Clear() { Data.clear(); }    /* original C++ signature */
    def clear(self) -> None:
        """- Get***() functions find pair, never add/allocate. Pairs are sorted so a query is O(log N)
         - Set***() functions find pair, insertion on demand if missing.
         - Sorted insertion is costly, paid once. A typical frame shouldn't need to insert any new pair.
        (private API)
        """
        pass
    # IMGUI_API int       GetInt(ImGuiID key, int default_val = 0) const;    /* original C++ signature */
    def get_int(self, key: ID, default_val: int = 0) -> int:
        pass
    # IMGUI_API void      SetInt(ImGuiID key, int val);    /* original C++ signature */
    def set_int(self, key: ID, val: int) -> None:
        pass
    # IMGUI_API bool      GetBool(ImGuiID key, bool default_val = false) const;    /* original C++ signature */
    def get_bool(self, key: ID, default_val: bool = False) -> bool:
        pass
    # IMGUI_API void      SetBool(ImGuiID key, bool val);    /* original C++ signature */
    def set_bool(self, key: ID, val: bool) -> None:
        pass
    # IMGUI_API float     GetFloat(ImGuiID key, float default_val = 0.0f) const;    /* original C++ signature */
    def get_float(self, key: ID, default_val: float = 0.0) -> float:
        pass
    # IMGUI_API void      SetFloat(ImGuiID key, float val);    /* original C++ signature */
    def set_float(self, key: ID, val: float) -> None:
        pass
    # IMGUI_API void*     GetVoidPtr(ImGuiID key) const;     /* original C++ signature */
    def get_void_ptr(self, key: ID) -> Any:
        """default_val is None"""
        pass
    # IMGUI_API void      SetVoidPtr(ImGuiID key, void* val);    /* original C++ signature */
    def set_void_ptr(self, key: ID, val: Any) -> None:
        pass
    # - Get***Ref() functions finds pair, insert on demand if missing, return pointer. Useful if you intend to do Get+Set.
    # - References are only valid until a new value is added to the storage. Calling a Set***() function or a Get***Ref() function invalidates the pointer.
    # - A typical use case where this is convenient for quick hacking (e.g. add storage during a live Edit&Continue session if you can't modify existing struct)
    #      float* pvar = ImGui::GetFloatRef(key); ImGui::SliderFloat("var", pvar, 0, 100.0); some_var += *pvar;
    # IMGUI_API int*      GetIntRef(ImGuiID key, int default_val = 0);    /* original C++ signature */
    def get_int_ref(self, key: ID, default_val: int = 0) -> int:
        pass
    # IMGUI_API bool*     GetBoolRef(ImGuiID key, bool default_val = false);    /* original C++ signature */
    def get_bool_ref(self, key: ID, default_val: bool = False) -> bool:
        pass
    # IMGUI_API float*    GetFloatRef(ImGuiID key, float default_val = 0.0f);    /* original C++ signature */
    def get_float_ref(self, key: ID, default_val: float = 0.0) -> float:
        pass
    # IMGUI_API void      BuildSortByKey();    /* original C++ signature */
    def build_sort_by_key(self) -> None:
        """Advanced: for quicker full rebuild of a storage (instead of an incremental one), you may add all your contents and then sort once."""
        pass
    # IMGUI_API void      SetAllInt(int val);    /* original C++ signature */
    def set_all_int(self, val: int) -> None:
        """Obsolete: use on your own storage if you know only integer are being stored (open/close all tree nodes)"""
        pass
    # ImGuiStorage();    /* original C++ signature */
    def __init__(self) -> None:
        """Auto-generated default constructor"""
        pass

class ListClipper:
    """Helper: Manually clip large list of items.
    If you have lots evenly spaced items and you have random access to the list, you can perform coarse
    clipping based on visibility to only submit items that are in view.
    The clipper calculates the range of visible items and advance the cursor to compensate for the non-visible items we have skipped.
    (Dear ImGui already clip items based on their bounds but: it needs to first layout the item to do so, and generally
     fetching/submitting your own data incurs additional cost. Coarse clipping using ImGuiListClipper allows you to easily
     scale using lists with tens of thousands of items without a problem)
    Usage:
      ImGuiListClipper clipper;
      clipper.Begin(1000);         // We have 1000 elements, evenly spaced.
      while (clipper.Step())
          for (int i = clipper.DisplayStart; i < clipper.DisplayEnd; i++)
              ImGui::Text("line number %d", i);
    Generally what happens is:
    - Clipper lets you process the first element (DisplayStart = 0, DisplayEnd = 1) regardless of it being visible or not.
    - User code submit that one element.
    - Clipper can measure the height of the first element
    - Clipper calculate the actual range of elements to display based on the current clipping rectangle, position the cursor before the first visible element.
    - User code submit visible elements.
    - The clipper also handles various subtleties related to keyboard/gamepad navigation, wrapping etc.
    """

    # ImGuiContext*   Ctx;    /* original C++ signature */
    ctx: Context  # Parent UI context
    # int             DisplayStart;    /* original C++ signature */
    display_start: int  # First item to display, updated by each call to Step()
    # int             DisplayEnd;    /* original C++ signature */
    display_end: int  # End of items to display (exclusive)
    # int             ItemsCount;    /* original C++ signature */
    items_count: int  # [Internal] Number of items
    # float           ItemsHeight;    /* original C++ signature */
    items_height: float  # [Internal] Height of item after a first step and item submission can calculate it
    # float           StartPosY;    /* original C++ signature */
    start_pos_y: float  # [Internal] Cursor position at the time of Begin() or after table frozen rows are all processed
    # double          StartSeekOffsetY;    /* original C++ signature */
    start_seek_offset_y: (
        float  # [Internal] Account for frozen rows in a table and initial loss of precision in very large windows.
    )
    # void*           TempData;    /* original C++ signature */
    temp_data: Any  # [Internal] Internal data

    # IMGUI_API ImGuiListClipper();    /* original C++ signature */
    def __init__(self) -> None:
        """items_count: Use INT_MAX if you don't know how many items you have (in which case the cursor won't be advanced in the final step, and you can call SeekCursorForItem() manually if you need)
        items_height: Use -1.0 to be calculated automatically on first step. Otherwise pass in the distance between your items, typically GetTextLineHeightWithSpacing() or GetFrameHeightWithSpacing().
        """
        pass
    # IMGUI_API void  Begin(int items_count, float items_height = -1.0f);    /* original C++ signature */
    def begin(self, items_count: int, items_height: float = -1.0) -> None:
        pass
    # IMGUI_API void  End();                 /* original C++ signature */
    def end(self) -> None:
        """Automatically called on the last call of Step() that returns False."""
        pass
    # IMGUI_API bool  Step();                /* original C++ signature */
    def step(self) -> bool:
        """Call until it returns False. The DisplayStart/DisplayEnd fields will be set and you can process/draw those items."""
        pass
    # inline void     IncludeItemByIndex(int item_index)                  { IncludeItemsByIndex(item_index, item_index + 1); }    /* original C++ signature */
    def include_item_by_index(self, item_index: int) -> None:
        """Call IncludeItemByIndex() or IncludeItemsByIndex() *BEFORE* first call to Step() if you need a range of items to not be clipped, regardless of their visibility.
         (Due to alignment / padding of certain items it is possible that an extra item may be included on either end of the display range).
        (private API)
        """
        pass
    # IMGUI_API void  IncludeItemsByIndex(int item_begin, int item_end);      /* original C++ signature */
    def include_items_by_index(self, item_begin: int, item_end: int) -> None:
        """item_end is exclusive e.g. use (42, 42+1) to make item 42 never clipped."""
        pass
    # IMGUI_API void  SeekCursorForItem(int item_index);    /* original C++ signature */
    def seek_cursor_for_item(self, item_index: int) -> None:
        """Seek cursor toward given item. This is automatically called while stepping.
        - The only reason to call this is: you can use ImGuiListClipper::Begin(INT_MAX) if you don't know item count ahead of time.
        - In this case, after all steps are done, you'll want to call SeekCursorForItem(item_count).
        """
        pass

# Helpers: ImVec2/ImVec4 operators
# - It is important that we are keeping those disabled by default so they don't leak in user space.
# - This is in order to allow user enabling implicit cast operators between ImVec2/ImVec4 and their own types (using IM_VEC2_CLASS_EXTRA in imconfig.h)
# - Add '#define IMGUI_DEFINE_MATH_OPERATORS' before including this file (or in imconfig.h) to access courtesy maths operators for ImVec2 and ImVec4.

# Helpers macros to generate 32-bit encoded colors
# - User can declare their own format by #defining the 5 _SHIFT/_MASK macros in their imconfig file.
# - Any setting other than the default will need custom backend support. The only standard backend that supports anything else than the default is DirectX9.

class ImColor:
    """Helper: ImColor() implicitly converts colors to either ImU32 (packed 4x1 byte) or ImVec4 (4x1 float)
    Prefer using IM_COL32() macros if you want a guaranteed compile-time ImU32 for usage with ImDrawList API.
    **Avoid storing ImColor! Store either u32 of ImVec4. This is not a full-featured color class. MAY OBSOLETE.
    **None of the ImGui API are using ImColor directly but you can use it as a convenience to pass colors in either ImU32 or ImVec4 formats. Explicitly cast to ImU32 or ImVec4 if needed.
    """

    # ImVec4          Value;    /* original C++ signature */
    value: ImVec4

    # constexpr ImColor()                                             { }    /* original C++ signature */
    @overload
    def __init__(self) -> None:
        pass
    # constexpr ImColor(float r, float g, float b, float a = 1.0f)    : Value(r, g, b, a) { }    /* original C++ signature */
    @overload
    def __init__(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        pass
    # constexpr ImColor(const ImVec4& col)                            : Value(col) {}    /* original C++ signature */
    @overload
    def __init__(self, col: ImVec4Like) -> None:
        pass
    # constexpr ImColor(int r, int g, int b, int a = 255)             : Value((float)r * (1.0f / 255.0f), (float)g * (1.0f / 255.0f), (float)b * (1.0f / 255.0f), (float)a* (1.0f / 255.0f)) {}    /* original C++ signature */
    @overload
    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        pass
    # constexpr ImColor(ImU32 rgba)                                   : Value((float)((rgba >> IM_COL32_R_SHIFT) & 0xFF) * (1.0f / 255.0f), (float)((rgba >> IM_COL32_G_SHIFT) & 0xFF) * (1.0f / 255.0f), (float)((rgba >> IM_COL32_B_SHIFT) & 0xFF) * (1.0f / 255.0f), (float)((rgba >> IM_COL32_A_SHIFT) & 0xFF) * (1.0f / 255.0f)) {}    /* original C++ signature */
    @overload
    def __init__(self, rgba: ImU32) -> None:
        pass
    # FIXME-OBSOLETE: May need to obsolete/cleanup those helpers.
    # inline void    SetHSV(float h, float s, float v, float a = 1.0f){ ImGui::ColorConvertHSVtoRGB(h, s, v, Value.x, Value.y, Value.z); Value.w = a; }    /* original C++ signature */
    def set_hsv(self, h: float, s: float, v: float, a: float = 1.0) -> None:
        """(private API)"""
        pass
    # static ImColor HSV(float h, float s, float v, float a = 1.0f)   { float r, g, b; ImGui::ColorConvertHSVtoRGB(h, s, v, r, g, b); return ImColor(r, g, b, a); }    /* original C++ signature */
    @staticmethod
    def hsv(h: float, s: float, v: float, a: float = 1.0) -> ImColor:
        """(private API)"""
        pass
    # #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # std::map<std::string, float> to_dict() const { return {{"x", Value.x}, {"y", Value.x}, {"z", Value.x}, {"w", Value.x}}; }    /* original C++ signature */
    def to_dict(self) -> Dict[str, float]:
        """(private API)"""
        pass
    # static ImVec4 from_dict(const std::map<std::string, float>& d) { IM_ASSERT((d.find("x") != d.end()) && (d.find("y") != d.end()) && (d.find("z") != d.end()) && (d.find("w") != d.end()) && "ImVec4.from_dict() requires a dictionary with keys 'x', 'y', 'z', 'w'"); ImVec4 v = ImVec4(d.at("x"), d.at("y"), d.at("z"), d.at("w")); return ImColor(v); }    /* original C++ signature */
    @staticmethod
    def from_dict(d: Dict[str, float]) -> ImVec4:
        """(private API)"""
        pass
    # #endif
    #

# -----------------------------------------------------------------------------
# [SECTION] Multi-Select API flags and structures (ImGuiMultiSelectFlags, ImGuiSelectionRequestType, ImGuiSelectionRequest, ImGuiMultiSelectIO, ImGuiSelectionBasicStorage)
# -----------------------------------------------------------------------------

# Multi-selection system
# Documentation at: https://github.com/ocornut/imgui/wiki/Multi-Select
# - Refer to 'Demo->Widgets->Selection State & Multi-Select' for demos using this.
# - This system implements standard multi-selection idioms (CTRL+Mouse/Keyboard, SHIFT+Mouse/Keyboard, etc)
#   with support for clipper (skipping non-visible items), box-select and many other details.
# - Selectable(), Checkbox() are supported but custom widgets may use it as well.
# - TreeNode() is technically supported but... using this correctly is more complicated: you need some sort of linear/random access to your tree,
#   which is suited to advanced trees setups also implementing filters and clipper. We will work toward simplifying and demoing it.
# - In the spirit of Dear ImGui design, your code owns actual selection data.
#   This is designed to allow all kinds of selection storage you may use in your application e.g. set/map/hash.
# About ImGuiSelectionBasicStorage:
# - This is an optional helper to store a selection state and apply selection requests.
# - It is used by our demos and provided as a convenience to quickly implement multi-selection.
# Usage:
# - Identify submitted items with SetNextItemSelectionUserData(), most likely using an index into your current data-set.
# - Store and maintain actual selection data using persistent object identifiers.
# - Usage flow:
#     BEGIN - (1) Call BeginMultiSelect() and retrieve the ImGuiMultiSelectIO* result.
#           - (2) Honor request list (SetAll/SetRange requests) by updating your selection data. Same code as Step 6.
#           - (3) [If using clipper] You need to make sure RangeSrcItem is always submitted. Calculate its index and pass to clipper.IncludeItemByIndex(). If storing indices in ImGuiSelectionUserData, a simple clipper.IncludeItemByIndex(ms_io->RangeSrcItem) call will work.
#     LOOP  - (4) Submit your items with SetNextItemSelectionUserData() + Selectable()/TreeNode() calls.
#     END   - (5) Call EndMultiSelect() and retrieve the ImGuiMultiSelectIO* result.
#           - (6) Honor request list (SetAll/SetRange requests) by updating your selection data. Same code as Step 2.
#     If you submit all items (no clipper), Step 2 and 3 are optional and will be handled by each item themselves. It is fine to always honor those steps.
# About ImGuiSelectionUserData:
# - This can store an application-defined identifier (e.g. index or pointer) submitted via SetNextItemSelectionUserData().
# - In return we store them into RangeSrcItem/RangeFirstItem/RangeLastItem and other fields in ImGuiMultiSelectIO.
# - Most applications will store an object INDEX, hence the chosen name and type. Storing an index is natural, because
#   SetRange requests will give you two end-points and you will need to iterate/interpolate between them to update your selection.
# - However it is perfectly possible to store a POINTER or another IDENTIFIER inside ImGuiSelectionUserData.
#   Our system never assume that you identify items by indices, it never attempts to interpolate between two values.
# - If you enable ImGuiMultiSelectFlags_NoRangeSelect then it is guaranteed that you will never have to interpolate
#   between two ImGuiSelectionUserData, which may be a convenient way to use part of the feature with less code work.
# - As most users will want to store an index, for convenience and to reduce confusion we use ImS64 instead of None*,
#   being syntactically easier to downcast. Feel free to reinterpret_cast and store a pointer inside.

class MultiSelectFlags_(enum.Enum):
    """Flags for BeginMultiSelect()"""

    # ImGuiMultiSelectFlags_None                  = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiMultiSelectFlags_SingleSelect          = 1 << 0,       /* original C++ signature */
    single_select = (
        enum.auto()
    )  # (= 1 << 0)  # Disable selecting more than one item. This is available to allow single-selection code to share same code/logic if desired. It essentially disables the main purpose of BeginMultiSelect() tho!
    # ImGuiMultiSelectFlags_NoSelectAll           = 1 << 1,       /* original C++ signature */
    no_select_all = enum.auto()  # (= 1 << 1)  # Disable CTRL+A shortcut to select all.
    # ImGuiMultiSelectFlags_NoRangeSelect         = 1 << 2,       /* original C++ signature */
    no_range_select = (
        enum.auto()
    )  # (= 1 << 2)  # Disable Shift+selection mouse/keyboard support (useful for unordered 2D selection). With BoxSelect is also ensure contiguous SetRange requests are not combined into one. This allows not handling interpolation in SetRange requests.
    # ImGuiMultiSelectFlags_NoAutoSelect          = 1 << 3,       /* original C++ signature */
    no_auto_select = (
        enum.auto()
    )  # (= 1 << 3)  # Disable selecting items when navigating (useful for e.g. supporting range-select in a list of checkboxes).
    # ImGuiMultiSelectFlags_NoAutoClear           = 1 << 4,       /* original C++ signature */
    no_auto_clear = (
        enum.auto()
    )  # (= 1 << 4)  # Disable clearing selection when navigating or selecting another one (generally used with ImGuiMultiSelectFlags_NoAutoSelect. useful for e.g. supporting range-select in a list of checkboxes).
    # ImGuiMultiSelectFlags_NoAutoClearOnReselect = 1 << 5,       /* original C++ signature */
    no_auto_clear_on_reselect = (
        enum.auto()
    )  # (= 1 << 5)  # Disable clearing selection when clicking/selecting an already selected item.
    # ImGuiMultiSelectFlags_BoxSelect1d           = 1 << 6,       /* original C++ signature */
    box_select1d = (
        enum.auto()
    )  # (= 1 << 6)  # Enable box-selection with same width and same x pos items (e.g. full row Selectable()). Box-selection works better with little bit of spacing between items hit-box in order to be able to aim at empty space.
    # ImGuiMultiSelectFlags_BoxSelect2d           = 1 << 7,       /* original C++ signature */
    box_select2d = (
        enum.auto()
    )  # (= 1 << 7)  # Enable box-selection with varying width or varying x pos items support (e.g. different width labels, or 2D layout/grid). This is slower: alters clipping logic so that e.g. horizontal movements will update selection of normally clipped items.
    # ImGuiMultiSelectFlags_BoxSelectNoScroll     = 1 << 8,       /* original C++ signature */
    box_select_no_scroll = enum.auto()  # (= 1 << 8)  # Disable scrolling when box-selecting near edges of scope.
    # ImGuiMultiSelectFlags_ClearOnEscape         = 1 << 9,       /* original C++ signature */
    clear_on_escape = enum.auto()  # (= 1 << 9)  # Clear selection when pressing Escape while scope is focused.
    # ImGuiMultiSelectFlags_ClearOnClickVoid      = 1 << 10,      /* original C++ signature */
    clear_on_click_void = enum.auto()  # (= 1 << 10)  # Clear selection when clicking on empty location within scope.
    # ImGuiMultiSelectFlags_ScopeWindow           = 1 << 11,      /* original C++ signature */
    scope_window = (
        enum.auto()
    )  # (= 1 << 11)  # Scope for _BoxSelect and _ClearOnClickVoid is whole window (Default). Use if BeginMultiSelect() covers a whole window or used a single time in same window.
    # ImGuiMultiSelectFlags_ScopeRect             = 1 << 12,      /* original C++ signature */
    scope_rect = (
        enum.auto()
    )  # (= 1 << 12)  # Scope for _BoxSelect and _ClearOnClickVoid is rectangle encompassing BeginMultiSelect()/EndMultiSelect(). Use if BeginMultiSelect() is called multiple times in same window.
    # ImGuiMultiSelectFlags_SelectOnClick         = 1 << 13,      /* original C++ signature */
    select_on_click = (
        enum.auto()
    )  # (= 1 << 13)  # Apply selection on mouse down when clicking on unselected item. (Default)
    # ImGuiMultiSelectFlags_SelectOnClickRelease  = 1 << 14,      /* original C++ signature */
    select_on_click_release = (
        enum.auto()
    )  # (= 1 << 14)  # Apply selection on mouse release when clicking an unselected item. Allow dragging an unselected item without altering selection.
    # ImGuiMultiSelectFlags_RangeSelect2       = 1 << 15,  // Shift+Selection uses 2 geometry instead of linear sequence, so possible to use Shift+up/down to select vertically in grid. Analogous to what BoxSelect does.
    # ImGuiMultiSelectFlags_NavWrapX              = 1 << 16,      /* original C++ signature */
    nav_wrap_x = (
        enum.auto()
    )  # (= 1 << 16)  # [Temporary] Enable navigation wrapping on X axis. Provided as a convenience because we don't have a design for the general Nav API for this yet. When the more general feature be public we may obsolete this flag in favor of new one.

class MultiSelectIO:
    """Main IO structure returned by BeginMultiSelect()/EndMultiSelect().
    This mainly contains a list of selection requests.
    - Use 'Demo->Tools->Debug Log->Selection' to see requests as they happen.
    - Some fields are only useful if your list is dynamic and allows deletion (getting post-deletion focus/state right is shown in the demo)
    - Below: who reads/writes each fields? 'r'=read, 'w'=write, 'ms'=multi-select code, 'app'=application/user code.
    """

    # ------------------------------------------// BeginMultiSelect / EndMultiSelect
    # ImVector<ImGuiSelectionRequest> Requests;    /* original C++ signature */
    requests: (
        ImVector_SelectionRequest  #  ms:w, app:r     /  ms:w  app:r   // Requests to apply to your selection data.
    )
    # ImGuiSelectionUserData      RangeSrcItem;    /* original C++ signature */
    range_src_item: SelectionUserData  #  ms:w  app:r     /                // (If using clipper) Begin: Source item (often the first selected item) must never be clipped: use clipper.IncludeItemByIndex() to ensure it is submitted.
    # ImGuiSelectionUserData      NavIdItem;    /* original C++ signature */
    nav_id_item: SelectionUserData  #  ms:w, app:r     /                // (If using deletion) Last known SetNextItemSelectionUserData() value for NavId (if part of submitted items).
    # bool                        NavIdSelected;    /* original C++ signature */
    nav_id_selected: bool  #  ms:w, app:r     /        app:r   // (If using deletion) Last known selection state for NavId (if part of submitted items).
    # bool                        RangeSrcReset;    /* original C++ signature */
    range_src_reset: bool  #        app:w     /  ms:r          // (If using deletion) Set before EndMultiSelect() to reset ResetSrcItem (e.g. if deleted selection).
    # int                         ItemsCount;    /* original C++ signature */
    items_count: int  #  ms:w, app:r     /        app:r   // 'int items_count' parameter to BeginMultiSelect() is copied here for convenience, allowing simpler calls to your ApplyRequests handler. Not used internally.
    # ImGuiMultiSelectIO(ImVector<ImGuiSelectionRequest> Requests = ImVector<ImGuiSelectionRequest>(), ImGuiSelectionUserData RangeSrcItem = ImGuiSelectionUserData(), ImGuiSelectionUserData NavIdItem = ImGuiSelectionUserData(), bool NavIdSelected = bool(), bool RangeSrcReset = bool(), int ItemsCount = int());    /* original C++ signature */
    def __init__(
        self,
        requests: Optional[ImVector_SelectionRequest] = None,
        range_src_item: Optional[SelectionUserData] = None,
        nav_id_item: Optional[SelectionUserData] = None,
        nav_id_selected: bool = bool(),
        range_src_reset: bool = bool(),
        items_count: int = int(),
    ) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                Requests: ImVector_SelectionRequest()
                RangeSrcItem: SelectionUserData()
                NavIdItem: SelectionUserData()
        """
        pass

class SelectionRequestType(enum.Enum):
    """Selection request type"""

    # ImGuiSelectionRequestType_None = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiSelectionRequestType_SetAll,               /* original C++ signature */
    set_all = (
        enum.auto()
    )  # (= 1)  # Request app to clear selection (if Selected==False) or select all items (if Selected==True). We cannot set RangeFirstItem/RangeLastItem as its contents is entirely up to user (not necessarily an index)
    # ImGuiSelectionRequestType_SetRange,             /* original C++ signature */
    set_range = (
        enum.auto()
    )  # (= 2)  # Request app to select/unselect [RangeFirstItem..RangeLastItem] items (inclusive) based on value of Selected. Only EndMultiSelect() request this, app code can read after BeginMultiSelect() and it will always be False.

class SelectionRequest:
    """Selection request item"""

    # ------------------------------------------// BeginMultiSelect / EndMultiSelect
    # ImGuiSelectionRequestType   Type;    /* original C++ signature */
    type: SelectionRequestType  #  ms:w, app:r     /  ms:w, app:r   // Request type. You'll most often receive 1 Clear + 1 SetRange with a single-item range.
    # bool                        Selected;    /* original C++ signature */
    selected: bool  #  ms:w, app:r     /  ms:w, app:r   // Parameter for SetAll/SetRange requests (True = select, False = unselect)
    # ImS8                        RangeDirection;    /* original C++ signature */
    range_direction: ImS8  #                  /  ms:w  app:r   // Parameter for SetRange request: +1 when RangeFirstItem comes before RangeLastItem, -1 otherwise. Useful if you want to preserve selection order on a backward Shift+Click.
    # ImGuiSelectionUserData      RangeFirstItem;    /* original C++ signature */
    range_first_item: SelectionUserData  #                  /  ms:w, app:r   // Parameter for SetRange request (this is generally == RangeSrcItem when shift selecting from top to bottom).
    # ImGuiSelectionUserData      RangeLastItem;    /* original C++ signature */
    range_last_item: SelectionUserData  #                  /  ms:w, app:r   // Parameter for SetRange request (this is generally == RangeSrcItem when shift selecting from bottom to top). Inclusive!
    # ImGuiSelectionRequest(ImGuiSelectionRequestType Type = ImGuiSelectionRequestType(), bool Selected = bool(), ImS8 RangeDirection = ImS8(), ImGuiSelectionUserData RangeFirstItem = ImGuiSelectionUserData(), ImGuiSelectionUserData RangeLastItem = ImGuiSelectionUserData());    /* original C++ signature */
    def __init__(
        self,
        type: SelectionRequestType = SelectionRequestType(),
        selected: bool = bool(),
        range_direction: ImS8 = ImS8(),
        range_first_item: Optional[SelectionUserData] = None,
        range_last_item: Optional[SelectionUserData] = None,
    ) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                RangeFirstItem: SelectionUserData()
                RangeLastItem: SelectionUserData()
        """
        pass

class SelectionBasicStorage:
    """Optional helper to store multi-selection state + apply multi-selection requests.
    - Used by our demos and provided as a convenience to easily implement basic multi-selection.
    - Iterate selection with 'None* it = None; ImGuiID id; while (selection.GetNextSelectedItem(&it, &id)) { ... }'
      Or you can check 'if (Contains(id)) { ... }' for each possible object if their number is not too high to iterate.
    - USING THIS IS NOT MANDATORY. This is only a helper and not a required API.
    To store a multi-selection, in your application you could:
    - Use this helper as a convenience. We use our simple key->value ImGuiStorage as a std::set<ImGuiID> replacement.
    - Use your own external storage: e.g. std::set<MyObjectId>, std::vector<MyObjectId>, interval trees, intrusively stored selection etc.
    In ImGuiSelectionBasicStorage we:
    - always use indices in the multi-selection API (passed to SetNextItemSelectionUserData(), retrieved in ImGuiMultiSelectIO)
    - use the AdapterIndexToStorageId() indirection layer to abstract how persistent selection data is derived from an index.
    - use decently optimized logic to allow queries and insertion of very large selection sets.
    - do not preserve selection order.
    Many combinations are possible depending on how you prefer to store your items and how you prefer to store your selection.
    Large applications are likely to eventually want to get rid of this indirection layer and do their own thing.
    See https://github.com/ocornut/imgui/wiki/Multi-Select for details and pseudo-code using this helper.
    """

    # Members
    # int             Size;    /* original C++ signature */
    size: int  #          // Number of selected items, maintained by this helper.
    # bool            PreserveOrder;    /* original C++ signature */
    preserve_order: bool  # = False  // GetNextSelectedItem() will return ordered selection (currently implemented by two additional sorts of selection. Could be improved)
    # void*           UserData;    /* original C++ signature */
    user_data: (
        Any  # = None   // User data for use by adapter function        // e.g. selection.UserData = (None*)my_items;
    )
    # int             _SelectionOrder;    /* original C++ signature */
    _selection_order: int  # [Internal] Increasing counter to store selection order
    # ImGuiStorage    _Storage;    /* original C++ signature */
    _storage: Storage  # [Internal] Selection set. Think of this as similar to e.g. std::set<ImGuiID>. Prefer not accessing directly: iterate with GetNextSelectedItem().

    # Methods
    # IMGUI_API ImGuiSelectionBasicStorage();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # IMGUI_API void  ApplyRequests(ImGuiMultiSelectIO* ms_io);       /* original C++ signature */
    def apply_requests(self, ms_io: MultiSelectIO) -> None:
        """Apply selection requests coming from BeginMultiSelect() and EndMultiSelect() functions. It uses 'items_count' passed to BeginMultiSelect()"""
        pass
    # IMGUI_API bool  Contains(ImGuiID id) const;                     /* original C++ signature */
    def contains(self, id_: ID) -> bool:
        """Query if an item id is in selection."""
        pass
    # IMGUI_API void  Clear();                                        /* original C++ signature */
    def clear(self) -> None:
        """Clear selection"""
        pass
    # IMGUI_API void  Swap(ImGuiSelectionBasicStorage& r);            /* original C++ signature */
    def swap(self, r: SelectionBasicStorage) -> None:
        """Swap two selections"""
        pass
    # IMGUI_API void  SetItemSelected(ImGuiID id, bool selected);     /* original C++ signature */
    def set_item_selected(self, id_: ID, selected: bool) -> None:
        """Add/remove an item from selection (generally done by ApplyRequests() function)"""
        pass
    # inline ImGuiID  GetStorageIdFromIndex(int idx)              { return AdapterIndexToStorageId(this, idx); }      /* original C++ signature */
    def get_storage_id_from_index(self, idx: int) -> ID:
        """(private API)

        Convert index to item id based on provided adapter.
        """
        pass

class SelectionExternalStorage:
    """Optional helper to apply multi-selection requests to existing randomly accessible storage.
    Convenient if you want to quickly wire multi-select API on e.g. an array of bool or items storing their own selection state.
    """

    # Members
    # void*           UserData;    /* original C++ signature */
    user_data: Any  # User data for use by adapter function                                // e.g. selection.UserData = (None*)my_items;

    # Methods
    # IMGUI_API ImGuiSelectionExternalStorage();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # IMGUI_API void  ApplyRequests(ImGuiMultiSelectIO* ms_io);       /* original C++ signature */
    def apply_requests(self, ms_io: MultiSelectIO) -> None:
        """Apply selection requests by using AdapterSetItemSelected() calls"""
        pass

# -----------------------------------------------------------------------------
# [SECTION] Drawing API (ImDrawCmd, ImDrawIdx, ImDrawVert, ImDrawChannel, ImDrawListSplitter, ImDrawListFlags, ImDrawList, ImDrawData)
# Hold a series of drawing commands. The user provides a renderer for ImDrawData which essentially contains an array of ImDrawList.
# -----------------------------------------------------------------------------

# The maximum line width to bake anti-aliased textures for. Build atlas with ImFontAtlasFlags_NoBakedLines to disable baking.

# ImDrawCallback: Draw callbacks for advanced uses [configurable type: override in imconfig.h]
# NB: You most likely do NOT need to use draw callbacks just to create your own widget or customized UI rendering,
# you can poke into the draw list for that! Draw callback may be useful for example to:
#  A) Change your GPU render state,
#  B) render a complex 3D scene inside a UI element without an intermediate texture/render target, etc.
# The expected behavior from your rendering function is 'if (cmd.UserCallback != None) { cmd.UserCallback(parent_list, cmd); } else { RenderTriangles() }'
# If you want to override the signature of ImDrawCallback, you can simply use e.g. '#define ImDrawCallback MyDrawCallback' (in imconfig.h) + update rendering backend accordingly.

class ImDrawCmd:
    """Typically, 1 command = 1 GPU draw call (unless command is a callback)
    - VtxOffset: When 'io.BackendFlags & ImGuiBackendFlags_RendererHasVtxOffset' is enabled,
      this fields allow us to render meshes larger than 64K vertices while keeping 16-bit indices.
      Backends made for <1.71. will typically ignore the VtxOffset fields.
    - The ClipRect/TextureId/VtxOffset fields must be contiguous as we memcmp() them together (this is asserted for).
    """

    # ImVec4          ClipRect;    /* original C++ signature */
    clip_rect: ImVec4  # 4*4  // Clipping rectangle (x1, y1, x2, y2). Subtract ImDrawData->DisplayPos to get clipping rectangle in "viewport" coordinates
    # ImTextureID     TextureId;    /* original C++ signature */
    texture_id: ImTextureID  # 4-8  // User-provided texture ID. Set by user in ImfontAtlas::SetTexID() for fonts or passed to Image*() functions. Ignore if never using images or multiple fonts atlas.
    # unsigned int    VtxOffset;    /* original C++ signature */
    vtx_offset: int  # 4    // Start offset in vertex buffer. ImGuiBackendFlags_RendererHasVtxOffset: always 0, otherwise may be >0 to support meshes larger than 64K vertices with 16-bit indices.
    # unsigned int    IdxOffset;    /* original C++ signature */
    idx_offset: int  # 4    // Start offset in index buffer.
    # unsigned int    ElemCount;    /* original C++ signature */
    elem_count: int  # 4    // Number of indices (multiple of 3) to be rendered as triangles. Vertices are stored in the callee ImDrawList's vtx_buffer[] array, indices in idx_buffer[].
    # void*           UserCallbackData;    /* original C++ signature */
    user_callback_data: Any  # 4-8  // Callback user data (when UserCallback != None). If called AddCallback() with size == 0, this is a copy of the AddCallback() argument. If called AddCallback() with size > 0, this is pointing to a buffer where data is stored.
    # int             UserCallbackDataSize;    /* original C++ signature */
    user_callback_data_size: int  # 4 // Size of callback user data when using storage, otherwise 0.
    # int             UserCallbackDataOffset;    /* original C++ signature */
    user_callback_data_offset: int  # 4 // [Internal] Offset of callback user data when using storage, otherwise -1.

    # ImDrawCmd()     { memset(this, 0, sizeof(*this)); }     /* original C++ signature */
    def __init__(self) -> None:
        """Also ensure our padding fields are zeroed"""
        pass
    # inline ImTextureID GetTexID() const { return TextureId; }    /* original C++ signature */
    def get_tex_id(self) -> ImTextureID:
        """Since 1.83: returns ImTextureID associated with this draw call. Warning: DO NOT assume this is always same as 'TextureId' (we will change this function for an upcoming feature)
        (private API)
        """
        pass

# Vertex layout
# #ifndef IMGUI_OVERRIDE_DRAWVERT_STRUCT_LAYOUT
#
class ImDrawVert:
    # ImVec2  pos;    /* original C++ signature */
    pos: ImVec2
    # ImVec2  uv;    /* original C++ signature */
    uv: ImVec2
    # ImU32   col;    /* original C++ signature */
    col: ImU32
    # ImDrawVert(ImVec2 pos = ImVec2(), ImVec2 uv = ImVec2(), ImU32 col = ImU32());    /* original C++ signature */
    def __init__(self, pos: Optional[ImVec2Like] = None, uv: Optional[ImVec2Like] = None, col: ImU32 = ImU32()) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                pos: ImVec2()
                uv: ImVec2()
        """
        pass

# #else
#
# #endif
#

class ImDrawCmdHeader:
    """[Internal] For use by ImDrawList"""

    # ImVec4          ClipRect;    /* original C++ signature */
    clip_rect: ImVec4
    # ImTextureID     TextureId;    /* original C++ signature */
    texture_id: ImTextureID
    # unsigned int    VtxOffset;    /* original C++ signature */
    vtx_offset: int
    # ImDrawCmdHeader(ImVec4 ClipRect = ImVec4(), ImTextureID TextureId = ImTextureID());    /* original C++ signature */
    def __init__(self, clip_rect: Optional[ImVec4Like] = None, texture_id: Optional[ImTextureID] = None) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                ClipRect: ImVec4()
                TextureId: ImTextureID()
        """
        pass

class ImDrawChannel:
    """[Internal] For use by ImDrawListSplitter"""

    # ImVector<ImDrawCmd>         _CmdBuffer;    /* original C++ signature */
    _cmd_buffer: ImVector_ImDrawCmd
    # ImVector<ImDrawIdx>         _IdxBuffer;    /* original C++ signature */
    _idx_buffer: ImVector_ImDrawIdx
    # ImDrawChannel(ImVector<ImDrawCmd> _CmdBuffer = ImVector<ImDrawCmd>(), ImVector<ImDrawIdx> _IdxBuffer = ImVector<ImDrawIdx>());    /* original C++ signature */
    def __init__(
        self, _cmd_buffer: Optional[ImVector_ImDrawCmd] = None, _idx_buffer: Optional[ImVector_ImDrawIdx] = None
    ) -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                _CmdBuffer: ImVector_ImDrawCmd()
                _IdxBuffer: ImVector_ImDrawIdx()
        """
        pass

class ImDrawListSplitter:
    """Split/Merge functions are used to split the draw list into different layers which can be drawn into out of order.
    This is used by the Columns/Tables API, so items of each column can be batched together in a same draw call.
    """

    # int                         _Current;    /* original C++ signature */
    _current: int  # Current channel number (0)
    # int                         _Count;    /* original C++ signature */
    _count: int  # Number of active channels (1+)
    # ImVector<ImDrawChannel>     _Channels;    /* original C++ signature */
    _channels: ImVector_ImDrawChannel  # Draw channels (not resized down so _Count might be < Channels.Size)

    # inline ImDrawListSplitter()  { memset(this, 0, sizeof(*this)); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # inline void                 Clear() { _Current = 0; _Count = 1; }     /* original C++ signature */
    def clear(self) -> None:
        """(private API)

        Do not clear Channels[] so our allocations are reused next frame
        """
        pass
    # IMGUI_API void              ClearFreeMemory();    /* original C++ signature */
    def clear_free_memory(self) -> None:
        pass
    # IMGUI_API void              Split(ImDrawList* draw_list, int count);    /* original C++ signature */
    def split(self, draw_list: ImDrawList, count: int) -> None:
        pass
    # IMGUI_API void              Merge(ImDrawList* draw_list);    /* original C++ signature */
    def merge(self, draw_list: ImDrawList) -> None:
        pass
    # IMGUI_API void              SetCurrentChannel(ImDrawList* draw_list, int channel_idx);    /* original C++ signature */
    def set_current_channel(self, draw_list: ImDrawList, channel_idx: int) -> None:
        pass

class ImDrawFlags_(enum.Enum):
    """Flags for ImDrawList functions
    (Legacy: bit 0 must always correspond to ImDrawFlags_Closed to be backward compatible with old API using a bool. Bits 1..3 must be unused)
    """

    # ImDrawFlags_None                        = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImDrawFlags_Closed                      = 1 << 0,     /* original C++ signature */
    closed = (
        enum.auto()
    )  # (= 1 << 0)  # PathStroke(), AddPolyline(): specify that shape should be closed (Important: this is always == 1 for legacy reason)
    # ImDrawFlags_RoundCornersTopLeft         = 1 << 4,     /* original C++ signature */
    round_corners_top_left = (
        enum.auto()
    )  # (= 1 << 4)  # AddRect(), AddRectFilled(), PathRect(): enable rounding top-left corner only (when rounding > 0.0, we default to all corners). Was 0x01.
    # ImDrawFlags_RoundCornersTopRight        = 1 << 5,     /* original C++ signature */
    round_corners_top_right = (
        enum.auto()
    )  # (= 1 << 5)  # AddRect(), AddRectFilled(), PathRect(): enable rounding top-right corner only (when rounding > 0.0, we default to all corners). Was 0x02.
    # ImDrawFlags_RoundCornersBottomLeft      = 1 << 6,     /* original C++ signature */
    round_corners_bottom_left = (
        enum.auto()
    )  # (= 1 << 6)  # AddRect(), AddRectFilled(), PathRect(): enable rounding bottom-left corner only (when rounding > 0.0, we default to all corners). Was 0x04.
    # ImDrawFlags_RoundCornersBottomRight     = 1 << 7,     /* original C++ signature */
    round_corners_bottom_right = (
        enum.auto()
    )  # (= 1 << 7)  # AddRect(), AddRectFilled(), PathRect(): enable rounding bottom-right corner only (when rounding > 0.0, we default to all corners). Wax 0x08.
    # ImDrawFlags_RoundCornersNone            = 1 << 8,     /* original C++ signature */
    round_corners_none = (
        enum.auto()
    )  # (= 1 << 8)  # AddRect(), AddRectFilled(), PathRect(): disable rounding on all corners (when rounding > 0.0). This is NOT zero, NOT an implicit flag!
    # ImDrawFlags_RoundCornersTop             = ImDrawFlags_RoundCornersTopLeft | ImDrawFlags_RoundCornersTopRight,    /* original C++ signature */
    round_corners_top = enum.auto()  # (= ImDrawFlags_.round_corners_top_left | ImDrawFlags_.round_corners_top_right)
    # ImDrawFlags_RoundCornersBottom          = ImDrawFlags_RoundCornersBottomLeft | ImDrawFlags_RoundCornersBottomRight,    /* original C++ signature */
    round_corners_bottom = (
        enum.auto()
    )  # (= ImDrawFlags_.round_corners_bottom_left | ImDrawFlags_.round_corners_bottom_right)
    # ImDrawFlags_RoundCornersLeft            = ImDrawFlags_RoundCornersBottomLeft | ImDrawFlags_RoundCornersTopLeft,    /* original C++ signature */
    round_corners_left = enum.auto()  # (= ImDrawFlags_.round_corners_bottom_left | ImDrawFlags_.round_corners_top_left)
    # ImDrawFlags_RoundCornersRight           = ImDrawFlags_RoundCornersBottomRight | ImDrawFlags_RoundCornersTopRight,    /* original C++ signature */
    round_corners_right = (
        enum.auto()
    )  # (= ImDrawFlags_.round_corners_bottom_right | ImDrawFlags_.round_corners_top_right)
    # ImDrawFlags_RoundCornersAll             = ImDrawFlags_RoundCornersTopLeft | ImDrawFlags_RoundCornersTopRight | ImDrawFlags_RoundCornersBottomLeft | ImDrawFlags_RoundCornersBottomRight,    /* original C++ signature */
    round_corners_all = (
        enum.auto()
    )  # (= ImDrawFlags_.round_corners_top_left | ImDrawFlags_.round_corners_top_right | ImDrawFlags_.round_corners_bottom_left | ImDrawFlags_.round_corners_bottom_right)
    # ImDrawFlags_RoundCornersDefault_        = ImDrawFlags_RoundCornersAll,     /* original C++ signature */
    round_corners_default_ = (
        enum.auto()
    )  # (= ImDrawFlags_.round_corners_all)  # Default to ALL corners if none of the _RoundCornersXX flags are specified.
    # ImDrawFlags_RoundCornersMask_           = ImDrawFlags_RoundCornersAll | ImDrawFlags_RoundCornersNone,    /* original C++ signature */
    # }
    round_corners_mask_ = enum.auto()  # (= ImDrawFlags_.round_corners_all | ImDrawFlags_.round_corners_none)

class ImDrawListFlags_(enum.Enum):
    """Flags for ImDrawList instance. Those are set automatically by ImGui:: functions from ImGuiIO settings, and generally not manipulated directly.
    It is however possible to temporarily alter flags between calls to ImDrawList:: functions.
    """

    # ImDrawListFlags_None                    = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImDrawListFlags_AntiAliasedLines        = 1 << 0,      /* original C++ signature */
    anti_aliased_lines = (
        enum.auto()
    )  # (= 1 << 0)  # Enable anti-aliased lines/borders (*2 the number of triangles for 1.0 wide line or lines thin enough to be drawn using textures, otherwise *3 the number of triangles)
    # ImDrawListFlags_AntiAliasedLinesUseTex  = 1 << 1,      /* original C++ signature */
    anti_aliased_lines_use_tex = (
        enum.auto()
    )  # (= 1 << 1)  # Enable anti-aliased lines/borders using textures when possible. Require backend to render with bilinear filtering (NOT point/nearest filtering).
    # ImDrawListFlags_AntiAliasedFill         = 1 << 2,      /* original C++ signature */
    anti_aliased_fill = (
        enum.auto()
    )  # (= 1 << 2)  # Enable anti-aliased edge around filled shapes (rounded rectangles, circles).
    # ImDrawListFlags_AllowVtxOffset          = 1 << 3,      /* original C++ signature */
    allow_vtx_offset = (
        enum.auto()
    )  # (= 1 << 3)  # Can emit 'VtxOffset > 0' to allow large meshes. Set when 'ImGuiBackendFlags_RendererHasVtxOffset' is enabled.

class ImDrawList:
    """Draw command list
    This is the low-level list of polygons that ImGui:: functions are filling. At the end of the frame,
    all command lists are passed to your ImGuiIO::RenderDrawListFn function for rendering.
    Each dear imgui window contains its own ImDrawList. You can use ImGui::GetWindowDrawList() to
    access the current window draw list and draw custom primitives.
    You can interleave normal ImGui:: calls and adding primitives to the current draw list.
    In single viewport mode, top-left is == GetMainViewport()->Pos (generally 0,0), bottom-right is == GetMainViewport()->Pos+Size (generally io.DisplaySize).
    You are totally free to apply whatever transformation matrix you want to the data (depending on the use of the transformation you may want to apply it to ClipRect as well!)
    Important: Primitives are always added to the list and not culled (culling is done at higher-level by ImGui:: functions), if you use this API a lot consider coarse culling your drawn objects.
    """

    # This is what you have to render
    # ImVector<ImDrawCmd>     CmdBuffer;    /* original C++ signature */
    cmd_buffer: (
        ImVector_ImDrawCmd  # Draw commands. Typically 1 command = 1 GPU draw call, unless the command is a callback.
    )
    # ImVector<ImDrawIdx>     IdxBuffer;    /* original C++ signature */
    idx_buffer: ImVector_ImDrawIdx  # Index buffer. Each command consume ImDrawCmd::ElemCount of those
    # ImVector<ImDrawVert>    VtxBuffer;    /* original C++ signature */
    vtx_buffer: ImVector_ImDrawVert  # Vertex buffer.
    # ImDrawListFlags         Flags;    /* original C++ signature */
    flags: ImDrawListFlags  # Flags, you may poke into these to adjust anti-aliasing settings per-primitive.

    # [Internal, used while building lists]
    # unsigned int            _VtxCurrentIdx;    /* original C++ signature */
    _vtx_current_idx: int  # [Internal] generally == VtxBuffer.Size unless we are past 64K vertices, in which case this gets reset to 0.
    # ImDrawListSharedData*   _Data;    /* original C++ signature */
    _data: ImDrawListSharedData  # Pointer to shared draw data (you can use ImGui::GetDrawListSharedData() to get the one from current ImGui context)
    # ImDrawVert*             _VtxWritePtr;    /* original C++ signature */
    _vtx_write_ptr: ImDrawVert  # [Internal] point within VtxBuffer.Data after each add command (to avoid using the ImVector<> operators too much)
    # ImDrawIdx*              _IdxWritePtr;    /* original C++ signature */
    _idx_write_ptr: ImDrawIdx  # [Internal] point within IdxBuffer.Data after each add command (to avoid using the ImVector<> operators too much)
    # ImVector<ImVec2>        _Path;    /* original C++ signature */
    _path: ImVector_ImVec2  # [Internal] current path building
    # ImDrawCmdHeader         _CmdHeader;    /* original C++ signature */
    _cmd_header: (
        ImDrawCmdHeader  # [Internal] template of active commands. Fields should match those of CmdBuffer.back().
    )
    # ImDrawListSplitter      _Splitter;    /* original C++ signature */
    _splitter: ImDrawListSplitter  # [Internal] for channels api (note: prefer using your own persistent instance of ImDrawListSplitter!)
    # ImVector<ImVec4>        _ClipRectStack;    /* original C++ signature */
    _clip_rect_stack: ImVector_ImVec4  # [Internal]
    # ImVector<ImTextureID>   _TextureIdStack;    /* original C++ signature */
    _texture_id_stack: ImVector_ImTextureID  # [Internal]
    # ImVector<ImU8>          _CallbacksDataBuf;    /* original C++ signature */
    _callbacks_data_buf: ImVector_ImU8  # [Internal]
    # float                   _FringeScale;    /* original C++ signature */
    _fringe_scale: float  # [Internal] anti-alias fringe is scaled by this value, this helps to keep things sharp while zooming at vertex buffer content
    # const char*             _OwnerName;    /* original C++ signature */
    _owner_name: str  # Pointer to owner window's name for debugging # (const)

    # IMGUI_API ImDrawList(ImDrawListSharedData* shared_data);    /* original C++ signature */
    def __init__(self, shared_data: ImDrawListSharedData) -> None:
        """If you want to create ImDrawList instances, pass them ImGui::GetDrawListSharedData().
        (advanced: you may create and use your own ImDrawListSharedData so you can use ImDrawList without ImGui, but that's more involved)
        """
        pass
    # IMGUI_API void  PushClipRect(const ImVec2& clip_rect_min, const ImVec2& clip_rect_max, bool intersect_with_current_clip_rect = false);      /* original C++ signature */
    def push_clip_rect(
        self, clip_rect_min: ImVec2Like, clip_rect_max: ImVec2Like, intersect_with_current_clip_rect: bool = False
    ) -> None:
        """Render-level scissoring. This is passed down to your render function but not used for CPU-side coarse clipping. Prefer using higher-level ImGui::PushClipRect() to affect logic (hit-testing and widget culling)"""
        pass
    # IMGUI_API void  PushClipRectFullScreen();    /* original C++ signature */
    def push_clip_rect_full_screen(self) -> None:
        pass
    # IMGUI_API void  PopClipRect();    /* original C++ signature */
    def pop_clip_rect(self) -> None:
        pass
    # IMGUI_API void  PushTextureID(ImTextureID texture_id);    /* original C++ signature */
    def push_texture_id(self, texture_id: ImTextureID) -> None:
        pass
    # IMGUI_API void  PopTextureID();    /* original C++ signature */
    def pop_texture_id(self) -> None:
        pass
    # inline ImVec2   GetClipRectMin() const { const ImVec4& cr = _ClipRectStack.back(); return ImVec2(cr.x, cr.y); }    /* original C++ signature */
    def get_clip_rect_min(self) -> ImVec2:
        """(private API)"""
        pass
    # inline ImVec2   GetClipRectMax() const { const ImVec4& cr = _ClipRectStack.back(); return ImVec2(cr.z, cr.w); }    /* original C++ signature */
    def get_clip_rect_max(self) -> ImVec2:
        """(private API)"""
        pass
    # Primitives
    # - Filled shapes must always use clockwise winding order. The anti-aliasing fringe depends on it. Counter-clockwise shapes will have "inward" anti-aliasing.
    # - For rectangular primitives, "p_min" and "p_max" represent the upper-left and lower-right corners.
    # - For circle primitives, use "num_segments == 0" to automatically calculate tessellation (preferred).
    #   In older versions (until Dear ImGui 1.77) the AddCircle functions defaulted to num_segments == 12.
    #   In future versions we will use textures to provide cheaper and higher-quality circles.
    #   Use AddNgon() and AddNgonFilled() functions if you need to guarantee a specific number of sides.
    # IMGUI_API void  AddLine(const ImVec2& p1, const ImVec2& p2, ImU32 col, float thickness = 1.0f);    /* original C++ signature */
    def add_line(self, p1: ImVec2Like, p2: ImVec2Like, col: ImU32, thickness: float = 1.0) -> None:
        pass
    # IMGUI_API void  AddRect(const ImVec2& p_min, const ImVec2& p_max, ImU32 col, float rounding = 0.0f, ImDrawFlags flags = 0, float thickness = 1.0f);       /* original C++ signature */
    def add_rect(
        self,
        p_min: ImVec2Like,
        p_max: ImVec2Like,
        col: ImU32,
        rounding: float = 0.0,
        flags: ImDrawFlags = 0,
        thickness: float = 1.0,
    ) -> None:
        """a: upper-left, b: lower-right (== upper-left + size)"""
        pass
    # IMGUI_API void  AddRectFilled(const ImVec2& p_min, const ImVec2& p_max, ImU32 col, float rounding = 0.0f, ImDrawFlags flags = 0);                         /* original C++ signature */
    def add_rect_filled(
        self, p_min: ImVec2Like, p_max: ImVec2Like, col: ImU32, rounding: float = 0.0, flags: ImDrawFlags = 0
    ) -> None:
        """a: upper-left, b: lower-right (== upper-left + size)"""
        pass
    # IMGUI_API void  AddRectFilledMultiColor(const ImVec2& p_min, const ImVec2& p_max, ImU32 col_upr_left, ImU32 col_upr_right, ImU32 col_bot_right, ImU32 col_bot_left);    /* original C++ signature */
    def add_rect_filled_multi_color(
        self,
        p_min: ImVec2Like,
        p_max: ImVec2Like,
        col_upr_left: ImU32,
        col_upr_right: ImU32,
        col_bot_right: ImU32,
        col_bot_left: ImU32,
    ) -> None:
        pass
    # IMGUI_API void  AddQuad(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, ImU32 col, float thickness = 1.0f);    /* original C++ signature */
    def add_quad(
        self, p1: ImVec2Like, p2: ImVec2Like, p3: ImVec2Like, p4: ImVec2Like, col: ImU32, thickness: float = 1.0
    ) -> None:
        pass
    # IMGUI_API void  AddQuadFilled(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, ImU32 col);    /* original C++ signature */
    def add_quad_filled(self, p1: ImVec2Like, p2: ImVec2Like, p3: ImVec2Like, p4: ImVec2Like, col: ImU32) -> None:
        pass
    # IMGUI_API void  AddTriangle(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, ImU32 col, float thickness = 1.0f);    /* original C++ signature */
    def add_triangle(self, p1: ImVec2Like, p2: ImVec2Like, p3: ImVec2Like, col: ImU32, thickness: float = 1.0) -> None:
        pass
    # IMGUI_API void  AddTriangleFilled(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, ImU32 col);    /* original C++ signature */
    def add_triangle_filled(self, p1: ImVec2Like, p2: ImVec2Like, p3: ImVec2Like, col: ImU32) -> None:
        pass
    # IMGUI_API void  AddCircle(const ImVec2& center, float radius, ImU32 col, int num_segments = 0, float thickness = 1.0f);    /* original C++ signature */
    def add_circle(
        self, center: ImVec2Like, radius: float, col: ImU32, num_segments: int = 0, thickness: float = 1.0
    ) -> None:
        pass
    # IMGUI_API void  AddCircleFilled(const ImVec2& center, float radius, ImU32 col, int num_segments = 0);    /* original C++ signature */
    def add_circle_filled(self, center: ImVec2Like, radius: float, col: ImU32, num_segments: int = 0) -> None:
        pass
    # IMGUI_API void  AddNgon(const ImVec2& center, float radius, ImU32 col, int num_segments, float thickness = 1.0f);    /* original C++ signature */
    def add_ngon(
        self, center: ImVec2Like, radius: float, col: ImU32, num_segments: int, thickness: float = 1.0
    ) -> None:
        pass
    # IMGUI_API void  AddNgonFilled(const ImVec2& center, float radius, ImU32 col, int num_segments);    /* original C++ signature */
    def add_ngon_filled(self, center: ImVec2Like, radius: float, col: ImU32, num_segments: int) -> None:
        pass
    # IMGUI_API void  AddEllipse(const ImVec2& center, const ImVec2& radius, ImU32 col, float rot = 0.0f, int num_segments = 0, float thickness = 1.0f);    /* original C++ signature */
    def add_ellipse(
        self,
        center: ImVec2Like,
        radius: ImVec2Like,
        col: ImU32,
        rot: float = 0.0,
        num_segments: int = 0,
        thickness: float = 1.0,
    ) -> None:
        pass
    # IMGUI_API void  AddEllipseFilled(const ImVec2& center, const ImVec2& radius, ImU32 col, float rot = 0.0f, int num_segments = 0);    /* original C++ signature */
    def add_ellipse_filled(
        self, center: ImVec2Like, radius: ImVec2Like, col: ImU32, rot: float = 0.0, num_segments: int = 0
    ) -> None:
        pass
    # IMGUI_API void  AddText(const ImVec2& pos, ImU32 col, const char* text_begin, const char* text_end = NULL);    /* original C++ signature */
    @overload
    def add_text(self, pos: ImVec2Like, col: ImU32, text_begin: str, text_end: Optional[str] = None) -> None:
        pass
    # IMGUI_API void  AddText(ImFont* font, float font_size, const ImVec2& pos, ImU32 col, const char* text_begin, const char* text_end = NULL, float wrap_width = 0.0f, const ImVec4* cpu_fine_clip_rect = NULL);    /* original C++ signature */
    @overload
    def add_text(
        self,
        font: ImFont,
        font_size: float,
        pos: ImVec2Like,
        col: ImU32,
        text_begin: str,
        text_end: Optional[str] = None,
        wrap_width: float = 0.0,
        cpu_fine_clip_rect: Optional[ImVec4Like] = None,
    ) -> None:
        pass
    # IMGUI_API void  AddBezierCubic(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, ImU32 col, float thickness, int num_segments = 0);     /* original C++ signature */
    def add_bezier_cubic(
        self,
        p1: ImVec2Like,
        p2: ImVec2Like,
        p3: ImVec2Like,
        p4: ImVec2Like,
        col: ImU32,
        thickness: float,
        num_segments: int = 0,
    ) -> None:
        """Cubic Bezier (4 control points)"""
        pass
    # IMGUI_API void  AddBezierQuadratic(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, ImU32 col, float thickness, int num_segments = 0);                   /* original C++ signature */
    def add_bezier_quadratic(
        self, p1: ImVec2Like, p2: ImVec2Like, p3: ImVec2Like, col: ImU32, thickness: float, num_segments: int = 0
    ) -> None:
        pass
    # Quadratic Bezier (3 control points)

    #                                        #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # - Only simple polygons are supported by filling functions (no self-intersections, no holes).
    # - Concave polygon fill is more expensive than convex one: it has O(N^2) complexity. Provided as a convenience fo user but not used by main library.
    # IMGUI_API void  AddPolyline(const std::vector<ImVec2>& points, ImU32 col, ImDrawFlags flags, float thickness);    /* original C++ signature */
    def add_polyline(self, points: List[ImVec2Like], col: ImU32, flags: ImDrawFlags, thickness: float) -> None:
        pass
    # IMGUI_API void  AddConvexPolyFilled(const std::vector<ImVec2>& points, ImU32 col);    /* original C++ signature */
    def add_convex_poly_filled(self, points: List[ImVec2Like], col: ImU32) -> None:
        pass
    # IMGUI_API void  AddConcavePolyFilled(const std::vector<ImVec2>& points, ImU32 col);    /* original C++ signature */
    def add_concave_poly_filled(self, points: List[ImVec2Like], col: ImU32) -> None:
        pass
    #                                        #endif
    #

    # Image primitives
    # - Read FAQ to understand what ImTextureID is.
    # - "p_min" and "p_max" represent the upper-left and lower-right corners of the rectangle.
    # - "uv_min" and "uv_max" represent the normalized texture coordinates to use for those corners. Using (0,0)->(1,1) texture coordinates will generally display the entire texture.
    # IMGUI_API void  AddImage(ImTextureID user_texture_id, const ImVec2& p_min, const ImVec2& p_max, const ImVec2& uv_min = ImVec2(0, 0), const ImVec2& uv_max = ImVec2(1, 1), ImU32 col = IM_COL32_WHITE);    /* original C++ signature */
    def add_image(
        self,
        user_texture_id: ImTextureID,
        p_min: ImVec2Like,
        p_max: ImVec2Like,
        uv_min: Optional[ImVec2Like] = None,
        uv_max: Optional[ImVec2Like] = None,
        col: ImU32 = IM_COL32_WHITE,
    ) -> None:
        """---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                uv_min: ImVec2(0, 0)
                uv_max: ImVec2(1, 1)
        """
        pass
    # IMGUI_API void  AddImageQuad(ImTextureID user_texture_id, const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, const ImVec2& uv1 = ImVec2(0, 0), const ImVec2& uv2 = ImVec2(1, 0), const ImVec2& uv3 = ImVec2(1, 1), const ImVec2& uv4 = ImVec2(0, 1), ImU32 col = IM_COL32_WHITE);    /* original C++ signature */
    def add_image_quad(
        self,
        user_texture_id: ImTextureID,
        p1: ImVec2Like,
        p2: ImVec2Like,
        p3: ImVec2Like,
        p4: ImVec2Like,
        uv1: Optional[ImVec2Like] = None,
        uv2: Optional[ImVec2Like] = None,
        uv3: Optional[ImVec2Like] = None,
        uv4: Optional[ImVec2Like] = None,
        col: ImU32 = IM_COL32_WHITE,
    ) -> None:
        """---
        Python bindings defaults:
            If any of the params below is None, then its default value below will be used:
                uv1: ImVec2(0, 0)
                uv2: ImVec2(1, 0)
                uv3: ImVec2(1, 1)
                uv4: ImVec2(0, 1)
        """
        pass
    # IMGUI_API void  AddImageRounded(ImTextureID user_texture_id, const ImVec2& p_min, const ImVec2& p_max, const ImVec2& uv_min, const ImVec2& uv_max, ImU32 col, float rounding, ImDrawFlags flags = 0);    /* original C++ signature */
    def add_image_rounded(
        self,
        user_texture_id: ImTextureID,
        p_min: ImVec2Like,
        p_max: ImVec2Like,
        uv_min: ImVec2Like,
        uv_max: ImVec2Like,
        col: ImU32,
        rounding: float,
        flags: ImDrawFlags = 0,
    ) -> None:
        pass
    # Stateful path API, add points then finish with PathFillConvex() or PathStroke()
    # - Important: filled shapes must always use clockwise winding order! The anti-aliasing fringe depends on it. Counter-clockwise shapes will have "inward" anti-aliasing.
    #   so e.g. 'PathArcTo(center, radius, PI * -0.5, PI)' is ok, whereas 'PathArcTo(center, radius, PI, PI * -0.5)' won't have correct anti-aliasing when followed by PathFillConvex().
    # inline    void  PathClear()                                                 { _Path.Size = 0; }    /* original C++ signature */
    def path_clear(self) -> None:
        """(private API)"""
        pass
    # inline    void  PathLineTo(const ImVec2& pos)                               { _Path.push_back(pos); }    /* original C++ signature */
    def path_line_to(self, pos: ImVec2Like) -> None:
        """(private API)"""
        pass
    # inline    void  PathLineToMergeDuplicate(const ImVec2& pos)                 { if (_Path.Size == 0 || memcmp(&_Path.Data[_Path.Size - 1], &pos, 8) != 0) _Path.push_back(pos); }    /* original C++ signature */
    def path_line_to_merge_duplicate(self, pos: ImVec2Like) -> None:
        """(private API)"""
        pass
    # inline    void  PathFillConvex(ImU32 col)                                   { AddConvexPolyFilled(_Path.Data, _Path.Size, col); _Path.Size = 0; }    /* original C++ signature */
    def path_fill_convex(self, col: ImU32) -> None:
        """(private API)"""
        pass
    # inline    void  PathFillConcave(ImU32 col)                                  { AddConcavePolyFilled(_Path.Data, _Path.Size, col); _Path.Size = 0; }    /* original C++ signature */
    def path_fill_concave(self, col: ImU32) -> None:
        """(private API)"""
        pass
    # inline    void  PathStroke(ImU32 col, ImDrawFlags flags = 0, float thickness = 1.0f) { AddPolyline(_Path.Data, _Path.Size, col, flags, thickness); _Path.Size = 0; }    /* original C++ signature */
    def path_stroke(self, col: ImU32, flags: ImDrawFlags = 0, thickness: float = 1.0) -> None:
        """(private API)"""
        pass
    # IMGUI_API void  PathArcTo(const ImVec2& center, float radius, float a_min, float a_max, int num_segments = 0);    /* original C++ signature */
    def path_arc_to(self, center: ImVec2Like, radius: float, a_min: float, a_max: float, num_segments: int = 0) -> None:
        pass
    # IMGUI_API void  PathArcToFast(const ImVec2& center, float radius, int a_min_of_12, int a_max_of_12);                    /* original C++ signature */
    def path_arc_to_fast(self, center: ImVec2Like, radius: float, a_min_of_12: int, a_max_of_12: int) -> None:
        """Use precomputed angles for a 12 steps circle"""
        pass
    # IMGUI_API void  PathEllipticalArcTo(const ImVec2& center, const ImVec2& radius, float rot, float a_min, float a_max, int num_segments = 0);     /* original C++ signature */
    def path_elliptical_arc_to(
        self, center: ImVec2Like, radius: ImVec2Like, rot: float, a_min: float, a_max: float, num_segments: int = 0
    ) -> None:
        """Ellipse"""
        pass
    # IMGUI_API void  PathBezierCubicCurveTo(const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, int num_segments = 0);     /* original C++ signature */
    def path_bezier_cubic_curve_to(self, p2: ImVec2Like, p3: ImVec2Like, p4: ImVec2Like, num_segments: int = 0) -> None:
        """Cubic Bezier (4 control points)"""
        pass
    # IMGUI_API void  PathBezierQuadraticCurveTo(const ImVec2& p2, const ImVec2& p3, int num_segments = 0);                   /* original C++ signature */
    def path_bezier_quadratic_curve_to(self, p2: ImVec2Like, p3: ImVec2Like, num_segments: int = 0) -> None:
        """Quadratic Bezier (3 control points)"""
        pass
    # IMGUI_API void  PathRect(const ImVec2& rect_min, const ImVec2& rect_max, float rounding = 0.0f, ImDrawFlags flags = 0);    /* original C++ signature */
    def path_rect(
        self, rect_min: ImVec2Like, rect_max: ImVec2Like, rounding: float = 0.0, flags: ImDrawFlags = 0
    ) -> None:
        pass
    # Advanced: Miscellaneous
    # IMGUI_API void  AddDrawCmd();                                                   /* original C++ signature */
    def add_draw_cmd(self) -> None:
        """This is useful if you need to forcefully create a new draw call (to allow for dependent rendering / blending). Otherwise primitives are merged into the same draw-call as much as possible"""
        pass
    # IMGUI_API ImDrawList* CloneOutput() const;                                      /* original C++ signature */
    def clone_output(self) -> ImDrawList:
        """Create a clone of the CmdBuffer/IdxBuffer/VtxBuffer."""
        pass
    # Advanced: Channels
    # - Use to split render into layers. By switching channels to can render out-of-order (e.g. submit FG primitives before BG primitives)
    # - Use to minimize draw calls (e.g. if going back-and-forth between multiple clipping rectangles, prefer to append into separate channels then merge at the end)
    # - This API shouldn't have been in ImDrawList in the first place!
    #   Prefer using your own persistent instance of ImDrawListSplitter as you can stack them.
    #   Using the ImDrawList::ChannelsXXXX you cannot stack a split over another.
    # inline void     ChannelsSplit(int count)    { _Splitter.Split(this, count); }    /* original C++ signature */
    def channels_split(self, count: int) -> None:
        """(private API)"""
        pass
    # inline void     ChannelsMerge()             { _Splitter.Merge(this); }    /* original C++ signature */
    def channels_merge(self) -> None:
        """(private API)"""
        pass
    # inline void     ChannelsSetCurrent(int n)   { _Splitter.SetCurrentChannel(this, n); }    /* original C++ signature */
    def channels_set_current(self, n: int) -> None:
        """(private API)"""
        pass
    # Advanced: Primitives allocations
    # - We render triangles (three vertices)
    # - All primitives needs to be reserved via PrimReserve() beforehand.
    # IMGUI_API void  PrimReserve(int idx_count, int vtx_count);    /* original C++ signature */
    def prim_reserve(self, idx_count: int, vtx_count: int) -> None:
        pass
    # IMGUI_API void  PrimUnreserve(int idx_count, int vtx_count);    /* original C++ signature */
    def prim_unreserve(self, idx_count: int, vtx_count: int) -> None:
        pass
    # IMGUI_API void  PrimRect(const ImVec2& a, const ImVec2& b, ImU32 col);          /* original C++ signature */
    def prim_rect(self, a: ImVec2Like, b: ImVec2Like, col: ImU32) -> None:
        """Axis aligned rectangle (composed of two triangles)"""
        pass
    # IMGUI_API void  PrimRectUV(const ImVec2& a, const ImVec2& b, const ImVec2& uv_a, const ImVec2& uv_b, ImU32 col);    /* original C++ signature */
    def prim_rect_uv(self, a: ImVec2Like, b: ImVec2Like, uv_a: ImVec2Like, uv_b: ImVec2Like, col: ImU32) -> None:
        pass
    # IMGUI_API void  PrimQuadUV(const ImVec2& a, const ImVec2& b, const ImVec2& c, const ImVec2& d, const ImVec2& uv_a, const ImVec2& uv_b, const ImVec2& uv_c, const ImVec2& uv_d, ImU32 col);    /* original C++ signature */
    def prim_quad_uv(
        self,
        a: ImVec2Like,
        b: ImVec2Like,
        c: ImVec2Like,
        d: ImVec2Like,
        uv_a: ImVec2Like,
        uv_b: ImVec2Like,
        uv_c: ImVec2Like,
        uv_d: ImVec2Like,
        col: ImU32,
    ) -> None:
        pass
    # inline    void  PrimWriteVtx(const ImVec2& pos, const ImVec2& uv, ImU32 col)    { _VtxWritePtr->pos = pos; _VtxWritePtr->uv = uv; _VtxWritePtr->col = col; _VtxWritePtr++; _VtxCurrentIdx++; }    /* original C++ signature */
    def prim_write_vtx(self, pos: ImVec2Like, uv: ImVec2Like, col: ImU32) -> None:
        """(private API)"""
        pass
    # inline    void  PrimWriteIdx(ImDrawIdx idx)                                     { *_IdxWritePtr = idx; _IdxWritePtr++; }    /* original C++ signature */
    def prim_write_idx(self, idx: ImDrawIdx) -> None:
        """(private API)"""
        pass
    # inline    void  PrimVtx(const ImVec2& pos, const ImVec2& uv, ImU32 col)         { PrimWriteIdx((ImDrawIdx)_VtxCurrentIdx); PrimWriteVtx(pos, uv, col); }     /* original C++ signature */
    def prim_vtx(self, pos: ImVec2Like, uv: ImVec2Like, col: ImU32) -> None:
        """(private API)

        Write vertex with unique index
        """
        pass
    # Obsolete names
    # inline  None  AddEllipse(const ImVec2& center, float radius_x, float radius_y, ImU32 col, float rot = 0.0, int num_segments = 0, float thickness = 1.0) { AddEllipse(center, ImVec2(radius_x, radius_y), col, rot, num_segments, thickness); } // OBSOLETED in 1.90.5 (Mar 2024)
    # inline  None  AddEllipseFilled(const ImVec2& center, float radius_x, float radius_y, ImU32 col, float rot = 0.0, int num_segments = 0) { AddEllipseFilled(center, ImVec2(radius_x, radius_y), col, rot, num_segments); }                        // OBSOLETED in 1.90.5 (Mar 2024)
    # inline  None  PathEllipticalArcTo(const ImVec2& center, float radius_x, float radius_y, float rot, float a_min, float a_max, int num_segments = 0) { PathEllipticalArcTo(center, ImVec2(radius_x, radius_y), rot, a_min, a_max, num_segments); } // OBSOLETED in 1.90.5 (Mar 2024)
    # inline  None  AddBezierCurve(const ImVec2& p1, const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, ImU32 col, float thickness, int num_segments = 0) { AddBezierCubic(p1, p2, p3, p4, col, thickness, num_segments); }                         // OBSOLETED in 1.80 (Jan 2021)
    # inline  None  PathBezierCurveTo(const ImVec2& p2, const ImVec2& p3, const ImVec2& p4, int num_segments = 0) { PathBezierCubicCurveTo(p2, p3, p4, num_segments); }                                                                                // OBSOLETED in 1.80 (Jan 2021)

    # [Internal helpers]
    # IMGUI_API void  _ResetForNewFrame();    /* original C++ signature */
    def _reset_for_new_frame(self) -> None:
        pass
    # IMGUI_API void  _ClearFreeMemory();    /* original C++ signature */
    def _clear_free_memory(self) -> None:
        pass
    # IMGUI_API void  _PopUnusedDrawCmd();    /* original C++ signature */
    def _pop_unused_draw_cmd(self) -> None:
        pass
    # IMGUI_API void  _TryMergeDrawCmds();    /* original C++ signature */
    def _try_merge_draw_cmds(self) -> None:
        pass
    # IMGUI_API void  _OnChangedClipRect();    /* original C++ signature */
    def _on_changed_clip_rect(self) -> None:
        pass
    # IMGUI_API void  _OnChangedTextureID();    /* original C++ signature */
    def _on_changed_texture_id(self) -> None:
        pass
    # IMGUI_API void  _OnChangedVtxOffset();    /* original C++ signature */
    def _on_changed_vtx_offset(self) -> None:
        pass
    # IMGUI_API void  _SetTextureID(ImTextureID texture_id);    /* original C++ signature */
    def _set_texture_id(self, texture_id: ImTextureID) -> None:
        pass
    # IMGUI_API int   _CalcCircleAutoSegmentCount(float radius) const;    /* original C++ signature */
    def _calc_circle_auto_segment_count(self, radius: float) -> int:
        pass
    # IMGUI_API void  _PathArcToFastEx(const ImVec2& center, float radius, int a_min_sample, int a_max_sample, int a_step);    /* original C++ signature */
    def _path_arc_to_fast_ex(
        self, center: ImVec2Like, radius: float, a_min_sample: int, a_max_sample: int, a_step: int
    ) -> None:
        pass
    # IMGUI_API void  _PathArcToN(const ImVec2& center, float radius, float a_min, float a_max, int num_segments);    /* original C++ signature */
    def _path_arc_to_n(self, center: ImVec2Like, radius: float, a_min: float, a_max: float, num_segments: int) -> None:
        pass

class ImDrawData:
    """All draw data to render a Dear ImGui frame
    (NB: the style and the naming convention here is a little inconsistent, we currently preserve them for backward compatibility purpose,
    as this is one of the oldest structure exposed by the library! Basically, ImDrawList == CmdList)
    """

    # bool                Valid;    /* original C++ signature */
    valid: bool  # Only valid after Render() is called and before the next NewFrame() is called.
    # int                 CmdListsCount;    /* original C++ signature */
    cmd_lists_count: int  # Number of ImDrawList* to render
    # int                 TotalIdxCount;    /* original C++ signature */
    total_idx_count: int  # For convenience, sum of all ImDrawList's IdxBuffer.Size
    # int                 TotalVtxCount;    /* original C++ signature */
    total_vtx_count: int  # For convenience, sum of all ImDrawList's VtxBuffer.Size
    # ImVector<ImDrawList*> CmdLists;    /* original C++ signature */
    cmd_lists: ImVector_ImDrawList_ptr  # Array of ImDrawList* to render. The ImDrawLists are owned by ImGuiContext and only pointed to from here.
    # ImVec2              DisplayPos;    /* original C++ signature */
    display_pos: ImVec2  # Top-left position of the viewport to render (== top-left of the orthogonal projection matrix to use) (== GetMainViewport()->Pos for the main viewport, == (0.0) in most single-viewport applications)
    # ImVec2              DisplaySize;    /* original C++ signature */
    display_size: ImVec2  # Size of the viewport to render (== GetMainViewport()->Size for the main viewport, == io.DisplaySize in most single-viewport applications)
    # ImVec2              FramebufferScale;    /* original C++ signature */
    framebuffer_scale: ImVec2  # Amount of pixels for each unit of DisplaySize. Based on io.DisplayFramebufferScale. Generally (1,1) on normal display, (2,2) on OSX with Retina display.
    # ImGuiViewport*      OwnerViewport;    /* original C++ signature */
    owner_viewport: (
        Viewport  # Viewport carrying the ImDrawData instance, might be of use to the renderer (generally not).
    )

    # ImDrawData()    { Clear(); }    /* original C++ signature */
    def __init__(self) -> None:
        """Functions"""
        pass
    # IMGUI_API void  Clear();    /* original C++ signature */
    def clear(self) -> None:
        pass
    # IMGUI_API void  AddDrawList(ImDrawList* draw_list);         /* original C++ signature */
    def add_draw_list(self, draw_list: ImDrawList) -> None:
        """Helper to add an external draw list into an existing ImDrawData."""
        pass
    # IMGUI_API void  DeIndexAllBuffers();                        /* original C++ signature */
    def de_index_all_buffers(self) -> None:
        """Helper to convert all buffers from indexed to non-indexed, in case you cannot render indexed. Note: this is slow and most likely a waste of resources. Always prefer indexed rendering!"""
        pass
    # IMGUI_API void  ScaleClipRects(const ImVec2& fb_scale);     /* original C++ signature */
    def scale_clip_rects(self, fb_scale: ImVec2Like) -> None:
        """Helper to scale the ClipRect field of each ImDrawCmd. Use if your final output buffer is at a different scale than Dear ImGui expects, or if there is a difference between your window resolution and framebuffer resolution."""
        pass

# -----------------------------------------------------------------------------
# [SECTION] Font API (ImFontConfig, ImFontGlyph, ImFontAtlasFlags, ImFontAtlas, ImFontGlyphRangesBuilder, ImFont)
# -----------------------------------------------------------------------------

class ImFontConfig:
    # void*           FontData;    /* original C++ signature */
    font_data: Any  #          // TTF/OTF data
    # int             FontDataSize;    /* original C++ signature */
    font_data_size: int  #          // TTF/OTF data size
    # bool            FontDataOwnedByAtlas;    /* original C++ signature */
    font_data_owned_by_atlas: (
        bool  # True     // TTF/OTF data ownership taken by the container ImFontAtlas (will delete memory itself).
    )
    # int             FontNo;    /* original C++ signature */
    font_no: int  # 0        // Index of font within TTF/OTF file
    # float           SizePixels;    /* original C++ signature */
    size_pixels: float  #          // Size in pixels for rasterizer (more or less maps to the resulting font height).
    # int             OversampleH;    /* original C++ signature */
    oversample_h: int  # 2        // Rasterize at higher quality for sub-pixel positioning. Note the difference between 2 and 3 is minimal. You can reduce this to 1 for large glyphs save memory. Read https://github.com/nothings/stb/blob/master/tests/oversample/README.md for details.
    # int             OversampleV;    /* original C++ signature */
    oversample_v: int  # 1        // Rasterize at higher quality for sub-pixel positioning. This is not really useful as we don't use sub-pixel positions on the Y axis.
    # bool            PixelSnapH;    /* original C++ signature */
    pixel_snap_h: bool  # False    // Align every glyph AdvanceX to pixel boundaries. Useful e.g. if you are merging a non-pixel aligned font with the default font. If enabled, you can set OversampleH/V to 1.
    # ImVec2          GlyphExtraSpacing;    /* original C++ signature */
    glyph_extra_spacing: ImVec2  # 0, 0     // Extra spacing (in pixels) between glyphs when rendered: essentially add to glyph->AdvanceX. Only X axis is supported for now.
    # ImVec2          GlyphOffset;    /* original C++ signature */
    glyph_offset: ImVec2  # 0, 0     // Offset all glyphs from this font input.
    # float           GlyphMinAdvanceX;    /* original C++ signature */
    glyph_min_advance_x: float  # 0        // Minimum AdvanceX for glyphs, set Min to align font icons, set both Min/Max to enforce mono-space font
    # float           GlyphMaxAdvanceX;    /* original C++ signature */
    glyph_max_advance_x: float  # FLT_MAX  // Maximum AdvanceX for glyphs
    # bool            MergeMode;    /* original C++ signature */
    merge_mode: bool  # False    // Merge into previous ImFont, so you can combine multiple inputs font into one ImFont (e.g. ASCII font + icons + Japanese glyphs). You may want to use GlyphOffset.y when merge font of different heights.
    # unsigned int    FontBuilderFlags;    /* original C++ signature */
    font_builder_flags: int  # 0        // Settings for custom font builder. THIS IS BUILDER IMPLEMENTATION DEPENDENT. Leave as zero if unsure.
    # float           RasterizerMultiply;    /* original C++ signature */
    rasterizer_multiply: float  # 1.0     // Linearly brighten (>1.0) or darken (<1.0) font output. Brightening small fonts may be a good workaround to make them more readable. This is a silly thing we may remove in the future.
    # float           RasterizerDensity;    /* original C++ signature */
    rasterizer_density: float  # 1.0     // DPI scale for rasterization, not altering other font metrics: make it easy to swap between e.g. a 100% and a 400% fonts for a zooming display. IMPORTANT: If you increase this it is expected that you increase font scale accordingly, otherwise quality may look lowered.
    # ImWchar         EllipsisChar;    /* original C++ signature */
    ellipsis_char: ImWchar  # 0        // Explicitly specify unicode codepoint of ellipsis character. When fonts are being merged first specified ellipsis will be used.

    # [Internal]
    # ImFont*         DstFont;    /* original C++ signature */
    dst_font: ImFont

    # IMGUI_API ImFontConfig();    /* original C++ signature */
    def __init__(self) -> None:
        pass

class ImFontGlyph:
    """Hold rendering data for one glyph.
    (Note: some language parsers may fail to convert the 31+1 bitfield members, in this case maybe drop store a single u32 or we can rework this)
    """

    # float           AdvanceX;    /* original C++ signature */
    advance_x: float  # Distance to next character (= data from font + ImFontConfig::GlyphExtraSpacing.x baked in)
    # float           X0,     /* original C++ signature */
    x0: float  # Glyph corners
    # Y0,     /* original C++ signature */
    y0: float  # Glyph corners
    # X1,     /* original C++ signature */
    x1: float  # Glyph corners
    # Y1;    /* original C++ signature */
    y1: float  # Glyph corners
    # float           U0,     /* original C++ signature */
    u0: float
    # V0,     /* original C++ signature */
    v0: float
    # U1,     /* original C++ signature */
    u1: float
    # V1;    /* original C++ signature */
    v1: float
    # Texture coordinates

    #                 #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # [ADAPT_IMGUI_BUNDLE]
    # bool isColored() const { return Colored != 0; }    /* original C++ signature */
    def is_colored(self) -> bool:
        """(private API)"""
        pass
    # bool isVisible() const { return Visible != 0; }    /* original C++ signature */
    def is_visible(self) -> bool:
        """(private API)"""
        pass
    # unsigned int getCodepoint() const { return Codepoint; }    /* original C++ signature */
    def get_codepoint(self) -> int:
        """(private API)"""
        pass
    # [/ADAPT_IMGUI_BUNDLE]
    #                 #endif
    # ImFontGlyph(float AdvanceX = float(), float X0 = float(), float Y0 = float(), float X1 = float(), float Y1 = float(), float U0 = float(), float V0 = float(), float U1 = float(), float V1 = float());    /* original C++ signature */
    def __init__(
        self,
        advance_x: float = float(),
        x0: float = float(),
        y0: float = float(),
        x1: float = float(),
        y1: float = float(),
        u0: float = float(),
        v0: float = float(),
        u1: float = float(),
        v1: float = float(),
    ) -> None:
        """Auto-generated default constructor with named params"""
        pass

class ImFontGlyphRangesBuilder:
    """Helper to build glyph ranges from text/string data. Feed your application strings/characters to it then call BuildRanges().
    This is essentially a tightly packed of vector of 64k booleans = 8KB storage.
    """

    # ImVector<ImU32> UsedChars;    /* original C++ signature */
    used_chars: ImVector_ImU32  # Store 1-bit per Unicode code point (0=unused, 1=used)

    # ImFontGlyphRangesBuilder()              { Clear(); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # inline void     Clear()                 { int size_in_bytes = (IM_UNICODE_CODEPOINT_MAX + 1) / 8; UsedChars.resize(size_in_bytes / (int)sizeof(ImU32)); memset(UsedChars.Data, 0, (size_t)size_in_bytes); }    /* original C++ signature */
    def clear(self) -> None:
        """(private API)"""
        pass
    # inline bool     GetBit(size_t n) const  { int off = (int)(n >> 5); ImU32 mask = 1u << (n & 31); return (UsedChars[off] & mask) != 0; }      /* original C++ signature */
    def get_bit(self, n: int) -> bool:
        """(private API)

        Get bit n in the array
        """
        pass
    # inline void     SetBit(size_t n)        { int off = (int)(n >> 5); ImU32 mask = 1u << (n & 31); UsedChars[off] |= mask; }                   /* original C++ signature */
    def set_bit(self, n: int) -> None:
        """(private API)

        Set bit n in the array
        """
        pass
    # inline void     AddChar(ImWchar c)      { SetBit(c); }                          /* original C++ signature */
    def add_char(self, c: ImWchar) -> None:
        """(private API)

        Add character
        """
        pass
    # IMGUI_API void  AddText(const char* text, const char* text_end = NULL);         /* original C++ signature */
    def add_text(self, text: str, text_end: Optional[str] = None) -> None:
        """Add string (each character of the UTF-8 string are added)"""
        pass
    # IMGUI_API void  BuildRanges(ImVector<ImWchar>* out_ranges);                     /* original C++ signature */
    def build_ranges(self, out_ranges: ImVector_ImWchar) -> None:
        """Output new ranges"""
        pass

class ImFontAtlasCustomRect:
    """See ImFontAtlas::AddCustomRectXXX functions."""

    # unsigned short  X,     /* original C++ signature */
    x: int  # Output   // Packed position in Atlas
    # Y;    /* original C++ signature */
    y: int  # Output   // Packed position in Atlas

    # [Internal]
    # unsigned short  Width,     /* original C++ signature */
    width: int  # Input    // Desired rectangle dimension
    # Height;    /* original C++ signature */
    height: int  # Input    // Desired rectangle dimension
    # float           GlyphAdvanceX;    /* original C++ signature */
    glyph_advance_x: float  # Input    // For custom font glyphs only: glyph xadvance
    # ImVec2          GlyphOffset;    /* original C++ signature */
    glyph_offset: ImVec2  # Input    // For custom font glyphs only: glyph display offset
    # ImFont*         Font;    /* original C++ signature */
    font: ImFont  # Input    // For custom font glyphs only: target font
    # ImFontAtlasCustomRect()         { X = Y = 0xFFFF; Width = Height = 0; GlyphID = 0; GlyphColored = 0; GlyphAdvanceX = 0.0f; GlyphOffset = ImVec2(0, 0); Font = NULL; }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # bool IsPacked() const           { return X != 0xFFFF; }    /* original C++ signature */
    def is_packed(self) -> bool:
        """(private API)"""
        pass

class ImFontAtlasFlags_(enum.Enum):
    """Flags for ImFontAtlas build"""

    # ImFontAtlasFlags_None               = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImFontAtlasFlags_NoPowerOfTwoHeight = 1 << 0,       /* original C++ signature */
    no_power_of_two_height = enum.auto()  # (= 1 << 0)  # Don't round the height to next power of two
    # ImFontAtlasFlags_NoMouseCursors     = 1 << 1,       /* original C++ signature */
    no_mouse_cursors = (
        enum.auto()
    )  # (= 1 << 1)  # Don't build software mouse cursors into the atlas (save a little texture memory)
    # ImFontAtlasFlags_NoBakedLines       = 1 << 2,       /* original C++ signature */
    no_baked_lines = (
        enum.auto()
    )  # (= 1 << 2)  # Don't build thick line textures into the atlas (save a little texture memory, allow support for point/nearest filtering). The AntiAliasedLinesUseTex features uses them, otherwise they will be rendered using polygons (more expensive for CPU/GPU).

class ImFontAtlas:
    """Load and rasterize multiple TTF/OTF fonts into a same texture. The font atlas will build a single texture holding:
     - One or more fonts.
     - Custom graphics data needed to render the shapes needed by Dear ImGui.
     - Mouse cursor shapes for software cursor rendering (unless setting 'Flags |= ImFontAtlasFlags_NoMouseCursors' in the font atlas).
    It is the user-code responsibility to setup/build the atlas, then upload the pixel data into a texture accessible by your graphics api.
     - Optionally, call any of the AddFont*** functions. If you don't call any, the default font embedded in the code will be loaded for you.
     - Call GetTexDataAsAlpha8() or GetTexDataAsRGBA32() to build and retrieve pixels data.
     - Upload the pixels data into a texture within your graphics system (see imgui_impl_xxxx.cpp examples)
     - Call SetTexID(my_tex_id); and pass the pointer/identifier to your texture in a format natural to your graphics API.
       This value will be passed back to you during rendering to identify the texture. Read FAQ entry about ImTextureID for more details.
    Common pitfalls:
    - If you pass a 'glyph_ranges' array to AddFont*** functions, you need to make sure that your array persist up until the
      atlas is build (when calling GetTexData*** or Build()). We only copy the pointer, not the data.
    - Important: By default, AddFontFromMemoryTTF() takes ownership of the data. Even though we are not writing to it, we will free the pointer on destruction.
      You can set font_cfg->FontDataOwnedByAtlas=False to keep ownership of your data and it won't be freed,
    - Even though many functions are suffixed with "TTF", OTF data is supported just as well.
    - This is an old API and it is currently awkward for those and various other reasons! We will address them in the future!
    """

    # IMGUI_API ImFontAtlas();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # IMGUI_API ImFont*           AddFont(const ImFontConfig* font_cfg);    /* original C++ signature */
    def add_font(self, font_cfg: ImFontConfig) -> ImFont:
        pass
    # IMGUI_API ImFont*           AddFontDefault(const ImFontConfig* font_cfg = NULL);    /* original C++ signature */
    def add_font_default(self, font_cfg: Optional[ImFontConfig] = None) -> ImFont:
        pass
    # IMGUI_API void              ClearInputData();               /* original C++ signature */
    def clear_input_data(self) -> None:
        """Clear input data (all ImFontConfig structures including sizes, TTF data, glyph ranges, etc.) = all the data used to build the texture and fonts."""
        pass
    # IMGUI_API void              ClearTexData();                 /* original C++ signature */
    def clear_tex_data(self) -> None:
        """Clear output texture data (CPU side). Saves RAM once the texture has been copied to graphics memory."""
        pass
    # IMGUI_API void              ClearFonts();                   /* original C++ signature */
    def clear_fonts(self) -> None:
        """Clear output font data (glyphs storage, UV coordinates)."""
        pass
    # IMGUI_API void              Clear();                        /* original C++ signature */
    def clear(self) -> None:
        """Clear all input and output."""
        pass
    # Build atlas, retrieve pixel data.
    # User is in charge of copying the pixels into graphics memory (e.g. create a texture with your engine). Then store your texture handle with SetTexID().
    # The pitch is always = Width * BytesPerPixels (1 or 4)
    # Building in RGBA32 format is provided for convenience and compatibility, but note that unless you manually manipulate or copy color data into
    # the texture (e.g. when using the AddCustomRect*** api), then the RGB pixels emitted will always be white (~75% of memory/bandwidth waste.
    # IMGUI_API bool              Build();                        /* original C++ signature */
    def build(self) -> bool:
        """Build pixels data. This is called automatically for you by the GetTexData*** functions."""
        pass
    # bool                        IsBuilt() const             { return Fonts.Size > 0 && TexReady; }     /* original C++ signature */
    def is_built(self) -> bool:
        """(private API)

        Bit ambiguous: used to detect when user didn't build texture but effectively we should check TexID != 0 except that would be backend dependent...
        """
        pass
    # void                        SetTexID(ImTextureID id)    { TexID = id; }    /* original C++ signature */
    def set_tex_id(self, id_: ImTextureID) -> None:
        """(private API)"""
        pass
    # -------------------------------------------
    # Glyph Ranges
    # -------------------------------------------

    # Helpers to retrieve list of common Unicode ranges (2 value per range, values are inclusive, zero-terminated list)
    # NB: Make sure that your string are UTF-8 and NOT in your local code page.
    # Read https://github.com/ocornut/imgui/blob/master/docs/FONTS.md/#about-utf-8-encoding for details.
    # NB: Consider using ImFontGlyphRangesBuilder to build glyph ranges from textual data.
    # Default + Vietnamese characters

    # -------------------------------------------
    # [ADAPT_IMGUI_BUNDLE]
    # -------------------------------------------

    #                                                                 #ifdef IMGUI_BUNDLE_PYTHON_API
    #
    # IMGUI_API ImFont* _AddFontFromFileTTF(    /* original C++ signature */
    #         const char* filename,
    #         float size_pixels,
    #         const ImFontConfig* font_cfg = NULL,
    #         std::optional<std::vector<ImWchar>> glyph_ranges_as_int_list = std::nullopt);
    def add_font_from_file_ttf(
        self,
        filename: str,
        size_pixels: float,
        font_cfg: Optional[ImFontConfig] = None,
        glyph_ranges_as_int_list: Optional[List[ImWchar]] = None,
    ) -> ImFont:
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesDefault()                // Basic Latin, Extended Latin    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesDefault()); }
    def get_glyph_ranges_default(self) -> List[ImWchar]:
        """// Basic Latin, Extended Latin"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesGreek()                  // Default + Greek and Coptic    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesGreek()); }
    def get_glyph_ranges_greek(self) -> List[ImWchar]:
        """// Default + Greek and Coptic"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesKorean()                 // Default + Korean characters    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesKorean()); }
    def get_glyph_ranges_korean(self) -> List[ImWchar]:
        """// Default + Korean characters"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesJapanese()               // Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesJapanese()); }
    def get_glyph_ranges_japanese(self) -> List[ImWchar]:
        """// Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesChineseFull()            // Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesChineseFull()); }
    def get_glyph_ranges_chinese_full(self) -> List[ImWchar]:
        """// Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesChineseSimplifiedCommon()// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesChineseSimplifiedCommon()); }
    def get_glyph_ranges_chinese_simplified_common(self) -> List[ImWchar]:
        """// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesCyrillic()               // Default + about 400 Cyrillic characters    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesCyrillic()); }
    def get_glyph_ranges_cyrillic(self) -> List[ImWchar]:
        """// Default + about 400 Cyrillic characters"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesThai()                   // Default + Thai characters    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesThai()); }
    def get_glyph_ranges_thai(self) -> List[ImWchar]:
        """// Default + Thai characters"""
        pass
    # IMGUI_API inline std::vector<ImWchar>    _GetGlyphRangesVietnamese()             // Default + Vietnamese characters    /* original C++ signature */
    #     { return _ImWcharRangeToVec(GetGlyphRangesVietnamese()); }
    def get_glyph_ranges_vietnamese(self) -> List[ImWchar]:
        """// Default + Vietnamese characters"""
        pass
    #                                                                 #endif
    #
    # [/ADAPT_IMGUI_BUNDLE]

    # -------------------------------------------
    # [BETA] Custom Rectangles/Glyphs API
    # -------------------------------------------

    # You can request arbitrary rectangles to be packed into the atlas, for your own purposes.
    # - After calling Build(), you can query the rectangle position and render your pixels.
    # - If you render colored output, set 'atlas->TexPixelsUseColors = True' as this may help some backends decide of preferred texture format.
    # - You can also request your rectangles to be mapped as font glyph (given a font + Unicode point),
    #   so you can render e.g. custom colorful icons and use them as regular glyphs.
    # - Read docs/FONTS.md for more details about using colorful icons.
    # - Note: this API may be redesigned later in order to support multi-monitor varying DPI settings.
    # IMGUI_API int               AddCustomRectRegular(int width, int height);    /* original C++ signature */
    def add_custom_rect_regular(self, width: int, height: int) -> int:
        pass
    # IMGUI_API int               AddCustomRectFontGlyph(ImFont* font, ImWchar id, int width, int height, float advance_x, const ImVec2& offset = ImVec2(0, 0));    /* original C++ signature */
    def add_custom_rect_font_glyph(
        self, font: ImFont, id_: ImWchar, width: int, height: int, advance_x: float, offset: Optional[ImVec2Like] = None
    ) -> int:
        """---
        Python bindings defaults:
            If offset is None, then its default value will be: ImVec2(0, 0)
        """
        pass
    # ImFontAtlasCustomRect*      GetCustomRectByIndex(int index) { IM_ASSERT(index >= 0); return &CustomRects[index]; }    /* original C++ signature */
    def get_custom_rect_by_index(self, index: int) -> ImFontAtlasCustomRect:
        """(private API)"""
        pass
    # [Internal]
    # IMGUI_API void              CalcCustomRectUV(const ImFontAtlasCustomRect* rect, ImVec2* out_uv_min, ImVec2* out_uv_max) const;    /* original C++ signature */
    def calc_custom_rect_uv(self, rect: ImFontAtlasCustomRect, out_uv_min: ImVec2Like, out_uv_max: ImVec2Like) -> None:
        pass
    # IMGUI_API bool              GetMouseCursorTexData(ImGuiMouseCursor cursor, ImVec2* out_offset, ImVec2* out_size, ImVec2 out_uv_border[2], ImVec2 out_uv_fill[2]);    /* original C++ signature */
    def get_mouse_cursor_tex_data(
        self,
        cursor: MouseCursor,
        out_offset: ImVec2Like,
        out_size: ImVec2Like,
        out_uv_border: ImVec2Like,
        out_uv_fill: ImVec2Like,
    ) -> bool:
        pass
    # -------------------------------------------
    # Members
    # -------------------------------------------

    # ImFontAtlasFlags            Flags;    /* original C++ signature */
    flags: ImFontAtlasFlags  # Build flags (see ImFontAtlasFlags_)
    # ImTextureID                 TexID;    /* original C++ signature */
    tex_id: ImTextureID  # User data to refer to the texture once it has been uploaded to user's graphic systems. It is passed back to you during rendering via the ImDrawCmd structure.
    # int                         TexDesiredWidth;    /* original C++ signature */
    tex_desired_width: int  # Texture width desired by user before Build(). Must be a power-of-two. If have many glyphs your graphics API have texture size restrictions you may want to increase texture width to decrease height.
    # int                         TexGlyphPadding;    /* original C++ signature */
    tex_glyph_padding: int  # FIXME: Should be called "TexPackPadding". Padding between glyphs within texture in pixels. Defaults to 1. If your rendering method doesn't rely on bilinear filtering you may set this to 0 (will also need to set AntiAliasedLinesUseTex = False).
    # bool                        Locked;    /* original C++ signature */
    locked: bool  # Marked as Locked by ImGui::NewFrame() so attempt to modify the atlas will assert.
    # void*                       UserData;    /* original C++ signature */
    user_data: Any  # Store your own atlas related user-data (if e.g. you have multiple font atlas).

    # [Internal]
    # NB: Access texture data via GetTexData*() calls! Which will setup a default font for you.
    # bool                        TexReady;    /* original C++ signature */
    tex_ready: bool  # Set when texture was built matching current font input
    # bool                        TexPixelsUseColors;    /* original C++ signature */
    tex_pixels_use_colors: bool  # Tell whether our texture data is known to use colors (rather than just alpha channel), in order to help backend select a format.
    # int                         TexWidth;    /* original C++ signature */
    tex_width: int  # Texture width calculated during Build().
    # int                         TexHeight;    /* original C++ signature */
    tex_height: int  # Texture height calculated during Build().
    # ImVec2                      TexUvScale;    /* original C++ signature */
    tex_uv_scale: ImVec2  # = (1.0/TexWidth, 1.0/TexHeight)
    # ImVec2                      TexUvWhitePixel;    /* original C++ signature */
    tex_uv_white_pixel: ImVec2  # Texture coordinates to a white pixel
    # ImVector<ImFont*>           Fonts;    /* original C++ signature */
    fonts: ImVector_ImFont_ptr  # Hold all the fonts returned by AddFont*. Fonts[0] is the default font upon calling ImGui::NewFrame(), use ImGui::PushFont()/PopFont() to change the current font.
    # ImVector<ImFontAtlasCustomRect> CustomRects;    /* original C++ signature */
    custom_rects: ImVector_ImFontAtlasCustomRect  # Rectangles for packing custom texture data into the atlas.
    # ImVector<ImFontConfig>      ConfigData;    /* original C++ signature */
    config_data: ImVector_ImFontConfig  # Configuration data

    # [Internal] Font builder
    # const ImFontBuilderIO*      FontBuilderIO;    /* original C++ signature */
    font_builder_io: ImFontBuilderIO  # Opaque interface to a font builder (default to stb_truetype, can be changed to use FreeType by defining IMGUI_ENABLE_FREETYPE). # (const)
    # unsigned int                FontBuilderFlags;    /* original C++ signature */
    font_builder_flags: int  # Shared flags (for all fonts) for custom font builder. THIS IS BUILD IMPLEMENTATION DEPENDENT. Per-font override is also available in ImFontConfig.

    # [Internal] Packing data
    # int                         PackIdMouseCursors;    /* original C++ signature */
    pack_id_mouse_cursors: int  # Custom texture rectangle ID for white pixel and mouse cursors
    # int                         PackIdLines;    /* original C++ signature */
    pack_id_lines: int  # Custom texture rectangle ID for baked anti-aliased lines

    # [Obsolete]
    # typedef ImFontAtlasCustomRect    CustomRect;         // OBSOLETED in 1.72+
    # typedef ImFontGlyphRangesBuilder GlyphRangesBuilder; // OBSOLETED in 1.67+

class ImFont:
    """Font runtime data and rendering
    ImFontAtlas automatically loads a default embedded font for you when you call GetTexDataAsAlpha8() or GetTexDataAsRGBA32().
    """

    # [Internal] Members: Hot ~20/24 bytes (for CalcTextSize)
    # ImVector<float>             IndexAdvanceX;    /* original C++ signature */
    index_advance_x: ImVector_float  # 12-16 // out //            // Sparse. Glyphs->AdvanceX in a directly indexable way (cache-friendly for CalcTextSize functions which only this info, and are often bottleneck in large UI).
    # float                       FallbackAdvanceX;    /* original C++ signature */
    fallback_advance_x: float  # 4     // out // = FallbackGlyph->AdvanceX
    # float                       FontSize;    /* original C++ signature */
    font_size: float  # 4     // in  //            // Height of characters/line, set during loading (don't change after loading)

    # [Internal] Members: Hot ~28/40 bytes (for RenderText loop)
    # ImVector<ImWchar>           IndexLookup;    /* original C++ signature */
    index_lookup: ImVector_ImWchar  # 12-16 // out //            // Sparse. Index glyphs by Unicode code-point.
    # ImVector<ImFontGlyph>       Glyphs;    /* original C++ signature */
    glyphs: ImVector_ImFontGlyph  # 12-16 // out //            // All glyphs.
    # const ImFontGlyph*          FallbackGlyph;    /* original C++ signature */
    fallback_glyph: ImFontGlyph  # 4-8   // out // = FindGlyph(FontFallbackChar) # (const)

    # [Internal] Members: Cold ~32/40 bytes
    # Conceptually ConfigData[] is the list of font sources merged to create this font.
    # ImFontAtlas*                ContainerAtlas;    /* original C++ signature */
    container_atlas: ImFontAtlas  # 4-8   // out //            // What we has been loaded into
    # const ImFontConfig*         ConfigData;    /* original C++ signature */
    config_data: ImFontConfig  # 4-8   // in  //            // Pointer within ContainerAtlas->ConfigData to ConfigDataCount instances # (const)
    # short                       ConfigDataCount;    /* original C++ signature */
    config_data_count: int  # 2     // in  // ~ 1        // Number of ImFontConfig involved in creating this font. Bigger than 1 when merging multiple font sources into one ImFont.
    # short                       EllipsisCharCount;    /* original C++ signature */
    ellipsis_char_count: int  # 1     // out // 1 or 3
    # ImWchar                     EllipsisChar;    /* original C++ signature */
    ellipsis_char: ImWchar  # 2-4   // out // = '...'/'.'// Character used for ellipsis rendering.
    # ImWchar                     FallbackChar;    /* original C++ signature */
    fallback_char: ImWchar  # 2-4   // out // = FFFD/'?' // Character used if a glyph isn't found.
    # float                       EllipsisWidth;    /* original C++ signature */
    ellipsis_width: float  # 4     // out               // Width
    # float                       EllipsisCharStep;    /* original C++ signature */
    ellipsis_char_step: float  # 4     // out               // Step between characters when EllipsisCount > 0
    # bool                        DirtyLookupTables;    /* original C++ signature */
    dirty_lookup_tables: bool  # 1     // out //
    # float                       Scale;    /* original C++ signature */
    scale: float  # 4     // in  // = 1.      // Base font scale, multiplied by the per-window font scale which you can adjust with SetWindowFontScale()
    # float                       Ascent,     /* original C++ signature */
    ascent: (
        float  # 4+4   // out //            // Ascent: distance from top to bottom of e.g. 'A' [0..FontSize] (unscaled)
    )
    # Descent;    /* original C++ signature */
    descent: (
        float  # 4+4   // out //            // Ascent: distance from top to bottom of e.g. 'A' [0..FontSize] (unscaled)
    )
    # int                         MetricsTotalSurface;    /* original C++ signature */
    metrics_total_surface: int  # 4     // out //            // Total surface in pixels to get an idea of the font rasterization/texture cost (not exact, we approximate the cost of padding between glyphs)

    # IMGUI_API ImFont();    /* original C++ signature */
    def __init__(self) -> None:
        """Methods"""
        pass
    # IMGUI_API const ImFontGlyph*FindGlyph(ImWchar c);    /* original C++ signature */
    def find_glyph(self, c: ImWchar) -> ImFontGlyph:
        pass
    # IMGUI_API const ImFontGlyph*FindGlyphNoFallback(ImWchar c);    /* original C++ signature */
    def find_glyph_no_fallback(self, c: ImWchar) -> ImFontGlyph:
        pass
    # float                       GetCharAdvance(ImWchar c)           { return ((int)c < IndexAdvanceX.Size) ? IndexAdvanceX[(int)c] : FallbackAdvanceX; }    /* original C++ signature */
    def get_char_advance(self, c: ImWchar) -> float:
        """(private API)"""
        pass
    # bool                        IsLoaded() const                    { return ContainerAtlas != NULL; }    /* original C++ signature */
    def is_loaded(self) -> bool:
        """(private API)"""
        pass
    # const char*                 GetDebugName() const                { return ConfigData ? ConfigData->Name : "<unknown>"; }    /* original C++ signature */
    def get_debug_name(self) -> str:
        """(private API)"""
        pass
    # 'max_width' stops rendering after a certain width (could be turned into a 2 size). FLT_MAX to disable.
    # 'wrap_width' enable automatic word-wrapping across multiple lines to fit into given width. 0.0 to disable.
    # IMGUI_API const char*       CalcWordWrapPositionA(float scale, const char* text, const char* text_end, float wrap_width);    /* original C++ signature */
    def calc_word_wrap_position_a(self, scale: float, text: str, text_end: str, wrap_width: float) -> str:
        pass
    # IMGUI_API void              RenderChar(ImDrawList* draw_list, float size, const ImVec2& pos, ImU32 col, ImWchar c);    /* original C++ signature */
    def render_char(self, draw_list: ImDrawList, size: float, pos: ImVec2Like, col: ImU32, c: ImWchar) -> None:
        pass
    # IMGUI_API void              RenderText(ImDrawList* draw_list, float size, const ImVec2& pos, ImU32 col, const ImVec4& clip_rect, const char* text_begin, const char* text_end, float wrap_width = 0.0f, bool cpu_fine_clip = false);    /* original C++ signature */
    def render_text(
        self,
        draw_list: ImDrawList,
        size: float,
        pos: ImVec2Like,
        col: ImU32,
        clip_rect: ImVec4Like,
        text_begin: str,
        text_end: str,
        wrap_width: float = 0.0,
        cpu_fine_clip: bool = False,
    ) -> None:
        pass
    # [Internal] Don't use!
    # IMGUI_API void              BuildLookupTable();    /* original C++ signature */
    def build_lookup_table(self) -> None:
        pass
    # IMGUI_API void              ClearOutputData();    /* original C++ signature */
    def clear_output_data(self) -> None:
        pass
    # IMGUI_API void              GrowIndex(int new_size);    /* original C++ signature */
    def grow_index(self, new_size: int) -> None:
        pass
    # IMGUI_API void              AddGlyph(const ImFontConfig* src_cfg, ImWchar c, float x0, float y0, float x1, float y1, float u0, float v0, float u1, float v1, float advance_x);    /* original C++ signature */
    def add_glyph(
        self,
        src_cfg: ImFontConfig,
        c: ImWchar,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        u0: float,
        v0: float,
        u1: float,
        v1: float,
        advance_x: float,
    ) -> None:
        pass
    # IMGUI_API void              AddRemapChar(ImWchar dst, ImWchar src, bool overwrite_dst = true);     /* original C++ signature */
    def add_remap_char(self, dst: ImWchar, src: ImWchar, overwrite_dst: bool = True) -> None:
        """Makes 'dst' character/glyph points to 'src' character/glyph. Currently needs to be called AFTER fonts have been built."""
        pass
    # IMGUI_API void              SetGlyphVisible(ImWchar c, bool visible);    /* original C++ signature */
    def set_glyph_visible(self, c: ImWchar, visible: bool) -> None:
        pass
    # IMGUI_API bool              IsGlyphRangeUnused(unsigned int c_begin, unsigned int c_last);    /* original C++ signature */
    def is_glyph_range_unused(self, c_begin: int, c_last: int) -> bool:
        pass

# -----------------------------------------------------------------------------
# [SECTION] Viewports
# -----------------------------------------------------------------------------

class ViewportFlags_(enum.Enum):
    """Flags stored in ImGuiViewport::Flags, giving indications to the platform backends."""

    # ImGuiViewportFlags_None                     = 0,    /* original C++ signature */
    none = enum.auto()  # (= 0)
    # ImGuiViewportFlags_IsPlatformWindow         = 1 << 0,       /* original C++ signature */
    is_platform_window = enum.auto()  # (= 1 << 0)  # Represent a Platform Window
    # ImGuiViewportFlags_IsPlatformMonitor        = 1 << 1,       /* original C++ signature */
    is_platform_monitor = enum.auto()  # (= 1 << 1)  # Represent a Platform Monitor (unused yet)
    # ImGuiViewportFlags_OwnedByApp               = 1 << 2,       /* original C++ signature */
    owned_by_app = (
        enum.auto()
    )  # (= 1 << 2)  # Platform Window: Is created/managed by the user application? (rather than our backend)
    # ImGuiViewportFlags_NoDecoration             = 1 << 3,       /* original C++ signature */
    no_decoration = (
        enum.auto()
    )  # (= 1 << 3)  # Platform Window: Disable platform decorations: title bar, borders, etc. (generally set all windows, but if ImGuiConfigFlags_ViewportsDecoration is set we only set this on popups/tooltips)
    # ImGuiViewportFlags_NoTaskBarIcon            = 1 << 4,       /* original C++ signature */
    no_task_bar_icon = (
        enum.auto()
    )  # (= 1 << 4)  # Platform Window: Disable platform task bar icon (generally set on popups/tooltips, or all windows if ImGuiConfigFlags_ViewportsNoTaskBarIcon is set)
    # ImGuiViewportFlags_NoFocusOnAppearing       = 1 << 5,       /* original C++ signature */
    no_focus_on_appearing = enum.auto()  # (= 1 << 5)  # Platform Window: Don't take focus when created.
    # ImGuiViewportFlags_NoFocusOnClick           = 1 << 6,       /* original C++ signature */
    no_focus_on_click = enum.auto()  # (= 1 << 6)  # Platform Window: Don't take focus when clicked on.
    # ImGuiViewportFlags_NoInputs                 = 1 << 7,       /* original C++ signature */
    no_inputs = (
        enum.auto()
    )  # (= 1 << 7)  # Platform Window: Make mouse pass through so we can drag this window while peaking behind it.
    # ImGuiViewportFlags_NoRendererClear          = 1 << 8,       /* original C++ signature */
    no_renderer_clear = (
        enum.auto()
    )  # (= 1 << 8)  # Platform Window: Renderer doesn't need to clear the framebuffer ahead (because we will fill it entirely).
    # ImGuiViewportFlags_NoAutoMerge              = 1 << 9,       /* original C++ signature */
    no_auto_merge = (
        enum.auto()
    )  # (= 1 << 9)  # Platform Window: Avoid merging this window into another host window. This can only be set via ImGuiWindowClass viewport flags override (because we need to now ahead if we are going to create a viewport in the first place!).
    # ImGuiViewportFlags_TopMost                  = 1 << 10,      /* original C++ signature */
    top_most = enum.auto()  # (= 1 << 10)  # Platform Window: Display on top (for tooltips only).
    # ImGuiViewportFlags_CanHostOtherWindows      = 1 << 11,      /* original C++ signature */
    can_host_other_windows = (
        enum.auto()
    )  # (= 1 << 11)  # Viewport can host multiple imgui windows (secondary viewports are associated to a single window). // FIXME: In practice there's still probably code making the assumption that this is always and only on the MainViewport. Will fix once we add support for "no main viewport".

    # Output status flags (from Platform)
    # ImGuiViewportFlags_IsMinimized              = 1 << 12,      /* original C++ signature */
    is_minimized = (
        enum.auto()
    )  # (= 1 << 12)  # Platform Window: Window is minimized, can skip render. When minimized we tend to avoid using the viewport pos/size for clipping window or testing if they are contained in the viewport.
    # ImGuiViewportFlags_IsFocused                = 1 << 13,      /* original C++ signature */
    is_focused = (
        enum.auto()
    )  # (= 1 << 13)  # Platform Window: Window is focused (last call to Platform_GetWindowFocus() returned True)

class Viewport:
    """- Currently represents the Platform Window created by the application which is hosting our Dear ImGui windows.
    - With multi-viewport enabled, we extend this concept to have multiple active viewports.
    - In the future we will extend this concept further to also represent Platform Monitor and support a "no main platform window" operation mode.
    - About Main Area vs Work Area:
      - Main Area = entire viewport.
      - Work Area = entire viewport minus sections used by main menu bars (for platform windows), or by task bar (for platform monitor).
      - Windows are generally trying to stay within the Work Area of their host viewport.
    """

    # ImGuiID             ID;    /* original C++ signature */
    id_: ID  # Unique identifier for the viewport
    # ImGuiViewportFlags  Flags;    /* original C++ signature */
    flags: ViewportFlags  # See ImGuiViewportFlags_
    # ImVec2              Pos;    /* original C++ signature */
    pos: ImVec2  # Main Area: Position of the viewport (Dear ImGui coordinates are the same as OS desktop/native coordinates)
    # ImVec2              Size;    /* original C++ signature */
    size: ImVec2  # Main Area: Size of the viewport.
    # ImVec2              WorkPos;    /* original C++ signature */
    work_pos: ImVec2  # Work Area: Position of the viewport minus task bars, menus bars, status bars (>= Pos)
    # ImVec2              WorkSize;    /* original C++ signature */
    work_size: ImVec2  # Work Area: Size of the viewport minus task bars, menu bars, status bars (<= Size)
    # float               DpiScale;    /* original C++ signature */
    dpi_scale: float  # 1.0 = 96 DPI = No extra scale.
    # ImGuiID             ParentViewportId;    /* original C++ signature */
    parent_viewport_id: ID  # (Advanced) 0: no parent. Instruct the platform backend to setup a parent/child relationship between platform windows.
    # ImDrawData*         DrawData;    /* original C++ signature */
    draw_data: ImDrawData  # The ImDrawData corresponding to this viewport. Valid after Render() and until the next call to NewFrame().

    # Platform/Backend Dependent Data
    # Our design separate the Renderer and Platform backends to facilitate combining default backends with each others.
    # When our create your own backend for a custom engine, it is possible that both Renderer and Platform will be handled
    # by the same system and you may not need to use all the UserData/Handle fields.
    # The library never uses those fields, they are merely storage to facilitate backend implementation.
    # void*               RendererUserData;    /* original C++ signature */
    renderer_user_data: Any  # None* to hold custom data structure for the renderer (e.g. swap chain, framebuffers etc.). generally set by your Renderer_CreateWindow function.
    # void*               PlatformUserData;    /* original C++ signature */
    platform_user_data: Any  # None* to hold custom data structure for the OS / platform (e.g. windowing info, render context). generally set by your Platform_CreateWindow function.
    # void*               PlatformHandle;    /* original C++ signature */
    platform_handle: Any  # None* to hold higher-level, platform window handle (e.g. HWND, GLFWWindow*, SDL_Window*), for FindViewportByPlatformHandle().
    # void*               PlatformHandleRaw;    /* original C++ signature */
    platform_handle_raw: Any  # None* to hold lower-level, platform-native window handle (under Win32 this is expected to be a HWND, unused for other platforms), when using an abstraction layer like GLFW or SDL (where PlatformHandle would be a SDL_Window*)
    # bool                PlatformWindowCreated;    /* original C++ signature */
    platform_window_created: bool  # Platform window has been created (Platform_CreateWindow() has been called). This is False during the first frame where a viewport is being created.
    # bool                PlatformRequestMove;    /* original C++ signature */
    platform_request_move: bool  # Platform window requested move (e.g. window was moved by the OS / host window manager, authoritative position will be OS window position)
    # bool                PlatformRequestResize;    /* original C++ signature */
    platform_request_resize: bool  # Platform window requested resize (e.g. window was resized by the OS / host window manager, authoritative size will be OS window size)
    # bool                PlatformRequestClose;    /* original C++ signature */
    platform_request_close: bool  # Platform window requested closure (e.g. window was moved by the OS / host window manager, e.g. pressing ALT-F4)

    # ImGuiViewport()     { memset(this, 0, sizeof(*this)); }    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # [/ADAPT_IMGUI_BUNDLE]

    # Helpers
    # ImVec2              GetCenter() const       { return ImVec2(Pos.x + Size.x * 0.5f, Pos.y + Size.y * 0.5f); }    /* original C++ signature */
    def get_center(self) -> ImVec2:
        """(private API)"""
        pass
    # ImVec2              GetWorkCenter() const   { return ImVec2(WorkPos.x + WorkSize.x * 0.5f, WorkPos.y + WorkSize.y * 0.5f); }    /* original C++ signature */
    def get_work_center(self) -> ImVec2:
        """(private API)"""
        pass

# -----------------------------------------------------------------------------
# [SECTION] ImGuiPlatformIO + other Platform Dependent Interfaces (ImGuiPlatformMonitor, ImGuiPlatformImeData)
# -----------------------------------------------------------------------------

# [BETA] (Optional) Multi-Viewport Support!
# If you are new to Dear ImGui and trying to integrate it into your engine, you can probably ignore this for now.
#
# This feature allows you to seamlessly drag Dear ImGui windows outside of your application viewport.
# This is achieved by creating new Platform/OS windows on the fly, and rendering into them.
# Dear ImGui manages the viewport structures, and the backend create and maintain one Platform/OS window for each of those viewports.
#
# See Recap:   https://github.com/ocornut/imgui/wiki/Multi-Viewports
# See Glossary https://github.com/ocornut/imgui/wiki/Glossary for details about some of the terminology.
#
# About the coordinates system:
# - When multi-viewports are enabled, all Dear ImGui coordinates become absolute coordinates (same as OS coordinates!)
# - So e.g. ImGui::SetNextWindowPos(ImVec2(0,0)) will position a window relative to your primary monitor!
# - If you want to position windows relative to your main application viewport, use ImGui::GetMainViewport()->Pos as a base position.
#
# Steps to use multi-viewports in your application, when using a default backend from the examples/ folder:
# - Application:  Enable feature with 'io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable'.
# - Backend:      The backend initialization will setup all necessary ImGuiPlatformIO's functions and update monitors info every frame.
# - Application:  In your main loop, call ImGui::UpdatePlatformWindows(), ImGui::RenderPlatformWindowsDefault() after EndFrame() or Render().
# - Application:  Fix absolute coordinates used in ImGui::SetWindowPos() or ImGui::SetNextWindowPos() calls.
#
# Steps to use multi-viewports in your application, when using a custom backend:
# - Important:    THIS IS NOT EASY TO DO and comes with many subtleties not described here!
#                 It's also an experimental feature, so some of the requirements may evolve.
#                 Consider using default backends if you can. Either way, carefully follow and refer to examples/ backends for details.
# - Application:  Enable feature with 'io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable'.
# - Backend:      Hook ImGuiPlatformIO's Platform_* and Renderer_* callbacks (see below).
#                 Set 'io.BackendFlags |= ImGuiBackendFlags_PlatformHasViewports' and 'io.BackendFlags |= ImGuiBackendFlags_PlatformHasViewports'.
#                 Update ImGuiPlatformIO's Monitors list every frame.
#                 Update MousePos every frame, in absolute coordinates.
# - Application:  In your main loop, call ImGui::UpdatePlatformWindows(), ImGui::RenderPlatformWindowsDefault() after EndFrame() or Render().
#                 You may skip calling RenderPlatformWindowsDefault() if its API is not convenient for your needs. Read comments below.
# - Application:  Fix absolute coordinates used in ImGui::SetWindowPos() or ImGui::SetNextWindowPos() calls.
#
# About ImGui::RenderPlatformWindowsDefault():
# - This function is a mostly a _helper_ for the common-most cases, and to facilitate using default backends.
# - You can check its simple source code to understand what it does.
#   It basically iterates secondary viewports and call 4 functions that are setup in ImGuiPlatformIO, if available:
#     Platform_RenderWindow(), Renderer_RenderWindow(), Platform_SwapBuffers(), Renderer_SwapBuffers()
#   Those functions pointers exists only for the benefit of RenderPlatformWindowsDefault().
# - If you have very specific rendering needs (e.g. flipping multiple swap-chain simultaneously, unusual sync/threading issues, etc.),
#   you may be tempted to ignore RenderPlatformWindowsDefault() and write customized code to perform your renderingg.
#   You may decide to setup the platform_io's *RenderWindow and *SwapBuffers pointers and call your functions through those pointers,
#   or you may decide to never setup those pointers and call your code directly. They are a convenience, not an obligatory interface.
# -----------------------------------------------------------------------------

class PlatformIO:
    """Access via ImGui::GetPlatformIO()"""

    # IMGUI_API ImGuiPlatformIO();    /* original C++ signature */
    def __init__(self) -> None:
        pass
    # ------------------------------------------------------------------
    # Interface with OS and Platform backend (basic)
    # ------------------------------------------------------------------

    # Optional: Access OS clipboard
    # (default to use native Win32 clipboard on Windows, otherwise uses a private clipboard. Override to access OS clipboard on other architectures)
    # [ADAPT_IMGUI_BUNDLE]
    # const char* (*Platform_GetClipboardTextFn)(ImGuiContext* ctx);
    # None        (*Platform_SetClipboardTextFn)(ImGuiContext* ctx, const char* text);
    # std::function<std::string(ImGuiContext*)> Platform_GetClipboardTextFn;    /* original C++ signature */
    platform_get_clipboard_text_fn: Callable[[Context], str]
    # std::function<void(ImGuiContext*, const char*)> Platform_SetClipboardTextFn;    /* original C++ signature */
    platform_set_clipboard_text_fn: Callable[[Context, str], None]
    # void*       Platform_ClipboardUserData;    /* original C++ signature */
    # [/ADAPT_IMGUI_BUNDLE]
    platform_clipboard_user_data: Any

    # std::function<bool(ImGuiContext*, const char*)> Platform_OpenInShellFn;    /* original C++ signature */
    # Optional: Open link/folder/file in OS Shell
    # (default to use ShellExecuteA() on Windows, system() on Linux/Mac)
    # [ADAPT_IMGUI_BUNDLE]
    # bool        (*Platform_OpenInShellFn)(ImGuiContext* ctx, const char* path);
    platform_open_in_shell_fn: Callable[[Context, str], bool]
    # void*       Platform_OpenInShellUserData;    /* original C++ signature */
    # [/ADAPT_IMGUI_BUNDLE]
    platform_open_in_shell_user_data: Any

    # void*       Platform_ImeUserData;    /* original C++ signature */
    platform_ime_user_data: Any
    # None      (*SetPlatformImeDataFn)(ImGuiViewport* viewport, ImGuiPlatformImeData* data); // [Renamed to platform_io.PlatformSetImeDataFn in 1.91.1]

    # Optional: Platform locale
    # [Experimental] Configure decimal point e.g. '.' or ',' useful for some languages (e.g. German), generally pulled from *localeconv()->decimal_point
    # ImWchar     Platform_LocaleDecimalPoint;    /* original C++ signature */
    platform_locale_decimal_point: ImWchar  # '.'

    # ------------------------------------------------------------------
    # Interface with Renderer Backend
    # ------------------------------------------------------------------

    # void*       Renderer_RenderState;    /* original C++ signature */
    # Written by some backends during ImGui_ImplXXXX_RenderDrawData() call to point backend_specific ImGui_ImplXXXX_RenderState* structure.
    renderer_render_state: Any

    # ------------------------------------------------------------------
    # Input - Interface with OS/backends (Multi-Viewport support!)
    # ------------------------------------------------------------------

    # For reference, the second column shows which function are generally calling the Platform Functions:
    #   N = ImGui::NewFrame()                        ~ beginning of the dear imgui frame: read info from platform/OS windows (latest size/position)
    #   F = ImGui::Begin(), ImGui::EndFrame()        ~ during the dear imgui frame
    #   U = ImGui::UpdatePlatformWindows()           ~ after the dear imgui frame: create and update all platform/OS windows
    #   R = ImGui::RenderPlatformWindowsDefault()    ~ render
    #   D = ImGui::DestroyPlatformWindows()          ~ shutdown
    # The general idea is that NewFrame() we will read the current Platform/OS state, and UpdatePlatformWindows() will write to it.

    # The handlers are designed so we can mix and match two imgui_impl_xxxx files, one Platform backend and one Renderer backend.
    # Custom engine backends will often provide both Platform and Renderer interfaces together and so may not need to use all functions.
    # Platform functions are typically called _before_ their Renderer counterpart, apart from Destroy which are called the other way.

    # Platform Backend functions (e.g. Win32, GLFW, SDL) ------------------- Called by -----

    # Renderer Backend functions (e.g. DirectX, OpenGL, Vulkan) ------------ Called by -----

    # ImVector<ImGuiPlatformMonitor>  Monitors;    /* original C++ signature */
    # (Optional) Monitor list
    # - Updated by: app/backend. Update every frame to dynamically support changing monitor or DPI configuration.
    # - Used by: dear imgui to query DPI info, clamp popups/tooltips within same monitor and not have them straddle monitors.
    monitors: ImVector_PlatformMonitor

    # ------------------------------------------------------------------
    # Output - List of viewports to render into platform windows
    # ------------------------------------------------------------------

    # Viewports list (the list is updated by calling ImGui::EndFrame or ImGui::Render)
    # (in the future we will attempt to organize this feature to remove the need for a "main viewport")
    # ImVector<ImGuiViewport*>        Viewports;    /* original C++ signature */
    viewports: ImVector_Viewport_ptr  # Main viewports, followed by all secondary viewports.

class PlatformMonitor:
    """(Optional) This is required when enabling multi-viewport. Represent the bounds of each connected monitor/display and their DPI.
    We use this information for multiple DPI support + clamping the position of popups and tooltips so they don't straddle multiple monitors.
    """

    # ImVec2  MainPos,     /* original C++ signature */
    main_pos: ImVec2  # Coordinates of the area displayed on this monitor (Min = upper left, Max = bottom right)
    # MainSize;    /* original C++ signature */
    main_size: ImVec2  # Coordinates of the area displayed on this monitor (Min = upper left, Max = bottom right)
    # ImVec2  WorkPos,     /* original C++ signature */
    work_pos: ImVec2  # Coordinates without task bars / side bars / menu bars. Used to avoid positioning popups/tooltips inside this region. If you don't have this info, please copy the value for MainPos/MainSize.
    # WorkSize;    /* original C++ signature */
    work_size: ImVec2  # Coordinates without task bars / side bars / menu bars. Used to avoid positioning popups/tooltips inside this region. If you don't have this info, please copy the value for MainPos/MainSize.
    # float   DpiScale;    /* original C++ signature */
    dpi_scale: float  # 1.0 = 96 DPI
    # void*   PlatformHandle;    /* original C++ signature */
    platform_handle: Any  # Backend dependant data (e.g. HMONITOR, GLFWmonitor*, SDL Display Index, NSScreen*)
    # ImGuiPlatformMonitor()          { MainPos = MainSize = WorkPos = WorkSize = ImVec2(0, 0); DpiScale = 1.0f; PlatformHandle = NULL; }    /* original C++ signature */
    def __init__(self) -> None:
        pass

class PlatformImeData:
    """(Optional) Support for IME (Input Method Editor) via the platform_io.Platform_SetImeDataFn() function."""

    # bool    WantVisible;    /* original C++ signature */
    want_visible: bool  # A widget wants the IME to be visible
    # ImVec2  InputPos;    /* original C++ signature */
    input_pos: ImVec2  # Position of the input cursor
    # float   InputLineHeight;    /* original C++ signature */
    input_line_height: float  # Line height

    # ImGuiPlatformImeData() { memset(this, 0, sizeof(*this)); }    /* original C++ signature */
    def __init__(self) -> None:
        pass

# -----------------------------------------------------------------------------
# [SECTION] Obsolete functions and types
# (Will be removed! Read 'API BREAKING CHANGES' section in imgui.cpp for details)
# Please keep your copy of dear imgui up to date! Occasionally set '#define IMGUI_DISABLE_OBSOLETE_FUNCTIONS' in imconfig.h to stay ahead.
# -----------------------------------------------------------------------------

# RENAMED IMGUI_DISABLE_METRICS_WINDOW > IMGUI_DISABLE_DEBUG_TOOLS in 1.88 (from June 2022)

# -----------------------------------------------------------------------------

# Include imgui_user.h at the end of imgui.h
# May be convenient for some users to only explicitly include vanilla imgui.h and have extra stuff included.
# #ifdef IMGUI_INCLUDE_IMGUI_USER_H
#
# #endif
#

# #endif
####################    </generated_from:imgui.h>    ####################

####################    <generated_from:imgui_stacklayout.h>    ####################
# dear imgui, v1.86 WIP
# (stack layout headers)

#
#
# Index of this file:
# // [SECTION] Stack Layout API
#
#

# #ifndef IMGUI_DISABLE
#

# -----------------------------------------------------------------------------
# [SECTION] Stack Layout API
# -----------------------------------------------------------------------------

# IMGUI_API void BeginHorizontal(const char* str_id, const ImVec2& size = ImVec2(0, 0), float align = -1.0f);    /* original C++ signature */
@overload
def begin_horizontal(str_id: str, size: Optional[ImVec2Like] = None, align: float = -1.0) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void BeginHorizontal(const void* ptr_id, const ImVec2& size = ImVec2(0, 0), float align = -1.0f);    /* original C++ signature */
@overload
def begin_horizontal(ptr_id: Any, size: Optional[ImVec2Like] = None, align: float = -1.0) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void BeginHorizontal(int id, const ImVec2& size = ImVec2(0, 0), float align = -1);    /* original C++ signature */
@overload
def begin_horizontal(id_: int, size: Optional[ImVec2Like] = None, align: float = -1) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void EndHorizontal();    /* original C++ signature */
def end_horizontal() -> None:
    pass

# IMGUI_API void BeginVertical(const char* str_id, const ImVec2& size = ImVec2(0, 0), float align = -1.0f);    /* original C++ signature */
@overload
def begin_vertical(str_id: str, size: Optional[ImVec2Like] = None, align: float = -1.0) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void BeginVertical(const void* ptr_id, const ImVec2& size = ImVec2(0, 0), float align = -1.0f);    /* original C++ signature */
@overload
def begin_vertical(ptr_id: Any, size: Optional[ImVec2Like] = None, align: float = -1.0) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void BeginVertical(int id, const ImVec2& size = ImVec2(0, 0), float align = -1);    /* original C++ signature */
@overload
def begin_vertical(id_: int, size: Optional[ImVec2Like] = None, align: float = -1) -> None:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API void EndVertical();    /* original C++ signature */
def end_vertical() -> None:
    pass

# IMGUI_API void Spring(float weight = 1.0f, float spacing = -1.0f);    /* original C++ signature */
def spring(weight: float = 1.0, spacing: float = -1.0) -> None:
    pass

# IMGUI_API void SuspendLayout();    /* original C++ signature */
def suspend_layout() -> None:
    pass

# IMGUI_API void ResumeLayout();    /* original C++ signature */
def resume_layout() -> None:
    pass

# namespace ImGui

# #endif
####################    </generated_from:imgui_stacklayout.h>    ####################

####################    <generated_from:imgui_stacklayout_internal.h>    ####################
# dear imgui, v1.86 WIP
# (stack layout headers)

#
#
# Index of this file:
# // [SECTION] Stack Layout Internal API
#
#

# #ifndef IMGUI_DISABLE
#

# -----------------------------------------------------------------------------
# [SECTION] Stack Layout Internal API
# -----------------------------------------------------------------------------

# namespace ImGuiInternal

# #endif
####################    </generated_from:imgui_stacklayout_internal.h>    ####################

####################    <generated_from:imgui_stdlib.h>    ####################
# dear imgui: wrappers for C++ standard library (STL) types (std::string, etc.)
# This is also an example of how you may wrap your own similar types.

# Changelog:
# - v0.10: Initial version. Added InputText() / InputTextMultiline() calls with std::string

# See more C++ related extension (fmt, RAII, syntaxis sugar) on Wiki:
#   https://github.com/ocornut/imgui/wiki/Useful-Extensions#cness

# ImGui::InputText() with std::string
# Because text input needs dynamic resizing, we need to setup a callback to grow the capacity
# IMGUI_API bool  InputText(const char* label, std::string* str, ImGuiInputTextFlags flags = 0, ImGuiInputTextCallback callback = nullptr, void* user_data = nullptr);    /* original C++ signature */
def input_text(
    label: str, str: str, flags: InputTextFlags = 0, callback: InputTextCallback = None, user_data: Optional[Any] = None
) -> Tuple[bool, str]:
    pass

# IMGUI_API bool  InputTextMultiline(const char* label, std::string* str, const ImVec2& size = ImVec2(0, 0), ImGuiInputTextFlags flags = 0, ImGuiInputTextCallback callback = nullptr, void* user_data = nullptr);    /* original C++ signature */
def input_text_multiline(
    label: str,
    str: str,
    size: Optional[ImVec2Like] = None,
    flags: InputTextFlags = 0,
    callback: InputTextCallback = None,
    user_data: Optional[Any] = None,
) -> Tuple[bool, str]:
    """---
    Python bindings defaults:
        If size is None, then its default value will be: ImVec2(0, 0)
    """
    pass

# IMGUI_API bool  InputTextWithHint(const char* label, const char* hint, std::string* str, ImGuiInputTextFlags flags = 0, ImGuiInputTextCallback callback = nullptr, void* user_data = nullptr);    /* original C++ signature */
# }
def input_text_with_hint(
    label: str,
    hint: str,
    str: str,
    flags: InputTextFlags = 0,
    callback: InputTextCallback = None,
    user_data: Optional[Any] = None,
) -> Tuple[bool, str]:
    pass

####################    </generated_from:imgui_stdlib.h>    ####################

####################    <generated_from:imgui_pywrappers.h>    ####################
# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
# Handwritten wrappers around parts of the imgui API, when needed for the python bindings

class Payload_PyId:
    # ImGuiPayloadId DataId;    /* original C++ signature */
    # Stores an id that represents the payload. For example, this could be given by python `id(object)`
    data_id: PayloadId

    # std::string Type;    /* original C++ signature */
    # A string representing the type of payload. It cannot exceed 32 characters.
    type: str
    # ImGuiPayload_PyId(ImGuiPayloadId DataId = ImGuiPayloadId(), std::string Type = std::string());    /* original C++ signature */
    def __init__(self, data_id: Optional[PayloadId] = None, type: str = "") -> None:
        """Auto-generated default constructor with named params
        ---
        Python bindings defaults:
            If DataId is None, then its default value will be: PayloadId()
        """
        pass

# Note: the drag and drop API differs a bit between C++ and Python.
# * In C++, ImGui::SetDragDropPayload and AcceptDragDropPayload are able to accept any kind of object
#   (by storing a buffer whose size is the object size).
#
# Unfortunately, this behaviour cannot be reproduced in python.
#
# * In Python, you can use imgui.set_drag_drop_payload_py_id and imgui.accept_drag_drop_payload_py_id.
#   These versions can only store an integer id for the payload
#   (so that you may have to store the corresponding payload somewhere else)
# IMGUI_API bool                               SetDragDropPayload_PyId(const char* type, ImGuiPayloadId dataId, ImGuiCond cond = 0);    /* original C++ signature */
def set_drag_drop_payload_py_id(type: str, data_id: PayloadId, cond: Cond = 0) -> bool:
    pass

# IMGUI_API std::optional<ImGuiPayload_PyId>   AcceptDragDropPayload_PyId(const char* type, ImGuiDragDropFlags flags = 0);    /* original C++ signature */
def accept_drag_drop_payload_py_id(type: str, flags: DragDropFlags = 0) -> Optional[Payload_PyId]:
    pass

# IMGUI_API std::optional<ImGuiPayload_PyId>   GetDragDropPayload_PyId();    /* original C++ signature */
# }
def get_drag_drop_payload_py_id() -> Optional[Payload_PyId]:
    pass

####################    </generated_from:imgui_pywrappers.h>    ####################

# </litgen_stub>

##################################################
#    Manually inserted code (additional methods, etc.)
##################################################
ImFontAtlas.get_tex_data_as_rgba32 = font_atlas_get_tex_data_as_rgba32  # type: ignore

# API for imgui_demo.cpp (specific to ImGui Bundle)
def set_imgui_demo_window_pos(pos: ImVec2, size: ImVec2, cond: Cond) -> None:
    pass

def set_imgui_demo_code_window_pos(pos: ImVec2, size: ImVec2, cond: Cond) -> None:
    pass

def set_imgui_demo_marker_is_active(b: bool) -> None:
    pass

def get_imgui_demo_marker_is_active() -> bool:
    pass

def set_imgui_demo_show_python_code(b: bool) -> None:
    pass

ImVector_ImVec4Like = ImVector_ImVec4
ImVector_ImVec2Like = ImVector_ImVec2
