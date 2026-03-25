###############################################################################
# This file is a part of Dear ImGui Bundle, NOT a part of Dear ImGui
# -----------------------------------------------------------------------------
# imgui_demo.py is a port of imgui_demo.cpp using the bindings provided
# by Dear ImGui Bundle. It is not guaranteed to be up-to-date with the
# latest version of the C++ code, but it should be close enough.
###############################################################################

# fmt: off
# mypy: disable_error_code=attr-defined
# mypy: disable_error_code=no-untyped-call

# Originally ported from imgui_demo.cpp, v1.90
# noqa: E701
# noqa: E702
# noqa: E501
# ruff: noqa: E701, E702

# Help:
# - Read FAQ at http://dearimgui.com/faq
# - Call and read ImGui::ShowDemoWindow() in imgui_demo.cpp. All applications in examples/ are doing that.
# - Need help integrating Dear ImGui in your codebase?
#   - Read Getting Started https://github.com/ocornut/imgui/wiki/Getting-Started
#   - Read 'Programmer guide' in imgui.cpp for notes on how to setup Dear ImGui in your codebase.
# Read imgui.cpp for more details, documentation and comments.
# Get the latest version at https://github.com/ocornut/imgui

# ---------------------------------------------------
# PLEASE DO NOT REMOVE THIS FILE FROM YOUR PROJECT!
# ---------------------------------------------------
# Message to the person tempted to delete this file when integrating Dear ImGui into their codebase:
# Think again! It is the most useful reference code that you and other coders will want to refer to and call.
# Have the ImGui::ShowDemoWindow() function wired in an always-available debug menu of your game/app!
# Also include Metrics! ItemPicker! DebugLog! and other debug features.
# Removing this file from your project is hindering access to documentation for everyone in your team,
# likely leading you to poorer usage of the library.
# Everything in this file will be stripped out by the linker if you don't call ImGui::ShowDemoWindow().
# If you want to link core Dear ImGui in your shipped builds but want a thorough guarantee that the demo will not be
# linked, you can setup your imconfig.h with #define IMGUI_DISABLE_DEMO_WINDOWS and those functions will be empty.
# In another situation, whenever you have Dear ImGui available you probably want this to be available for reference.
# Thank you,
# -Your beloved friend, imgui_demo.cpp (which you won't delete)

# --------------------------------------------
# ABOUT THE MEANING OF THE 'static' KEYWORD:
# --------------------------------------------
# In this demo code, we frequently use 'static' variables inside functions.
# A static variable persists across calls. It is essentially a global variable but declared inside the scope of the function.
# Think of "static int n = 0;" as "global int n = 0;" !
# We do this IN THE DEMO because we want:
# - to gather code and data in the same place.
# - to make the demo source code faster to read, faster to change, smaller in size.
# - it is also a convenient way of storing simple UI related information as long as your function
#   doesn't need to be reentrant or used in multiple threads.
# This might be a pattern you will want to use in your code, but most of the data you would be working
# with in a complex codebase is likely going to be stored outside your functions.

# -----------------------------------------
# ABOUT THE CODING STYLE OF OUR DEMO CODE
# -----------------------------------------
# The Demo code in this file is designed to be easy to copy-and-paste into your application!
# Because of this:
# - We never omit the ImGui:: prefix when calling functions, even though most code here is in the same namespace.
# - We try to declare static variables in the local scope, as close as possible to the code using them.
# - We never use any of the helpers/facilities used internally by Dear ImGui, unless available in the public API.
# - We never use maths operators on ImVec2/ImVec4. For our other sources files we use them, and they are provided
#   by imgui.h using the IMGUI_DEFINE_MATH_OPERATORS define. For your own sources file they are optional
#   and require you either enable those, either provide your own via IM_VEC2_CLASS_EXTRA in imconfig.h.
#   Because we can't assume anything about your support of maths operators, we cannot use them in imgui_demo.cpp.

# Navigating this file:
# - In Visual Studio IDE: CTRL+comma ("Edit.GoToAll") can follow symbols in comments, whereas CTRL+F12 ("Edit.GoToImplementation") cannot.
# - With Visual Assist installed: ALT+G ("VAssistX.GoToImplementation") can also follow symbols in comments.


# Index of this file:

# [SECTION] Forward Declarations
# [SECTION] Helpers
# [SECTION] Demo Window / ShowDemoWindow()
# - ShowDemoWindow()
# - sub section: ShowDemoWindowWidgets()
# - sub section: ShowDemoWindowLayout()
# - sub section: ShowDemoWindowPopups()
# - sub section: ShowDemoWindowTables()
# - sub section: ShowDemoWindowInputs()
# [SECTION] About Window / ShowAboutWindow()
# [SECTION] Style Editor / ShowStyleEditor()
# [SECTION] User Guide / ShowUserGuide()
# [SECTION] Example App: Main Menu Bar / ShowExampleAppMainMenuBar()
# [SECTION] Example App: Debug Console / ShowExampleAppConsole()
# [SECTION] Example App: Debug Log / ShowExampleAppLog()
# [SECTION] Example App: Simple Layout / ShowExampleAppLayout()
# [SECTION] Example App: Property Editor / ShowExampleAppPropertyEditor()
# [SECTION] Example App: Long Text / ShowExampleAppLongText()
# [SECTION] Example App: Auto Resize / ShowExampleAppAutoResize()
# [SECTION] Example App: Constrained Resize / ShowExampleAppConstrainedResize()
# [SECTION] Example App: Simple overlay / ShowExampleAppSimpleOverlay()
# [SECTION] Example App: Fullscreen window / ShowExampleAppFullscreen()
# [SECTION] Example App: Manipulating window titles / ShowExampleAppWindowTitles()
# [SECTION] Example App: Custom Rendering using ImDrawList API / ShowExampleAppCustomRendering()
# [SECTION] Example App: Docking, DockSpace / ShowExampleAppDockSpace()
# [SECTION] Example App: Documents Handling / ShowExampleAppDocuments()


from imgui_bundle import imgui
from imgui_bundle import ImVec2, ImVec4

import time
import math
import numpy as np
from typing import Optional


IMGUI_DISABLE_DEBUG_TOOLS = False  # or True, depending on your configuration


# [SECTION] Forward Declarations, Helpers

# Forward Declarations (implemented below the main demo code)
# These are defined here as stubs to allow forward references from show_demo_window().
# The actual implementations follow after show_example_menu_file().

def show_example_app_main_menu_bar():
    pass

def show_example_app_console(p_open: bool) -> bool:
    return True

def show_example_app_custom_rendering(p_open: bool) -> bool:
    return True

def show_example_app_dock_space(p_open: bool) -> bool:
    return True

def show_example_app_documents(p_open: bool) -> bool:
    return True

def show_example_app_log(p_open: bool) -> bool:
    return True

def show_example_app_layout(p_open: bool) -> bool:
    return True

def show_example_app_property_editor(p_open: bool) -> bool:
    return True

def show_example_app_simple_overlay(p_open: bool) -> bool:
    return True

def show_example_app_auto_resize(p_open: bool) -> bool:
    return True

def show_example_app_constrained_resize(p_open: bool) -> bool:
    return True

def show_example_app_fullscreen(p_open: bool) -> bool:
    return True

def show_example_app_long_text(p_open: bool) -> bool:
    return True

def show_example_app_window_titles(p_open: bool) -> bool:
    return True

def show_demo_window_columns():
    # Demonstrate old/legacy Columns API!
    open = imgui.tree_node("Legacy Columns API")
    imgui.same_line()
    help_marker("Columns() is an old API! Prefer using the more flexible and powerful BeginTable() API!")
    if not open:
        return

    static = show_demo_window_columns

    # Basic columns
    if imgui.tree_node("Basic"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Basic")
        imgui.text("Without border:")
        imgui.columns(3, "mycolumns3", False)
        imgui.separator()
        for n in range(14):
            label = f"Item {n}"
            imgui.selectable(label, False)
            imgui.next_column()
        imgui.columns(1)
        imgui.separator()

        imgui.text("With border:")
        imgui.columns(4, "mycolumns")
        imgui.separator()
        imgui.text("ID"); imgui.next_column()
        imgui.text("Name"); imgui.next_column()
        imgui.text("Path"); imgui.next_column()
        imgui.text("Hovered"); imgui.next_column()
        imgui.separator()
        names = ["One", "Two", "Three"]
        paths = ["/path/one", "/path/two", "/path/three"]
        if not hasattr(static, "col_selected"):
            static.col_selected = -1
        for i in range(3):
            label = f"{i:04d}"
            clicked, _ = imgui.selectable(label, static.col_selected == i, imgui.SelectableFlags_.span_all_columns)
            if clicked:
                static.col_selected = i
            hovered = imgui.is_item_hovered()
            imgui.next_column()
            imgui.text(names[i]); imgui.next_column()
            imgui.text(paths[i]); imgui.next_column()
            imgui.text(str(int(hovered))); imgui.next_column()
        imgui.columns(1)
        imgui.separator()
        imgui.tree_pop()

    if imgui.tree_node("Borders"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Borders")
        if not hasattr(static, "h_borders"):
            static.h_borders = True
            static.v_borders = True
            static.columns_count = 4
        lines_count = 3
        imgui.set_next_item_width(imgui.get_font_size() * 8)
        _, static.columns_count = imgui.drag_int("##columns_count", static.columns_count, 0.1, 2, 10, "%d columns")
        if static.columns_count < 2:
            static.columns_count = 2
        imgui.same_line()
        _, static.h_borders = imgui.checkbox("horizontal", static.h_borders)
        imgui.same_line()
        _, static.v_borders = imgui.checkbox("vertical", static.v_borders)
        imgui.columns(static.columns_count, None, static.v_borders)
        for i in range(static.columns_count * lines_count):
            if static.h_borders and imgui.get_column_index() == 0:
                imgui.separator()
            imgui.push_id(i)
            c = chr(ord('a') + i)
            imgui.text(f"{c}{c}{c}")
            imgui.text(f"Width {imgui.get_column_width():.2f}")
            imgui.text(f"Avail {imgui.get_content_region_avail().x:.2f}")
            imgui.text(f"Offset {imgui.get_column_offset():.2f}")
            imgui.text("Long text that is likely to clip")
            imgui.button("Button", ImVec2(-imgui.FLT_MIN, 0.0))
            imgui.pop_id()
            imgui.next_column()
        imgui.columns(1)
        if static.h_borders:
            imgui.separator()
        imgui.tree_pop()

    # Create multiple items in a same cell before switching to next column
    if imgui.tree_node("Mixed items"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Mixed items")
        imgui.columns(3, "mixed")
        imgui.separator()

        imgui.text("Hello")
        imgui.button("Banana")
        imgui.next_column()

        imgui.text("ImGui")
        imgui.button("Apple")
        if not hasattr(static, "mi_foo"):
            static.mi_foo = 1.0
            static.mi_bar = 1.0
        _, static.mi_foo = imgui.input_float("red", static.mi_foo, 0.05, 0, "%.3f")
        imgui.text("An extra line here.")
        imgui.next_column()

        imgui.text("Sailor")
        imgui.button("Corniflower")
        _, static.mi_bar = imgui.input_float("blue", static.mi_bar, 0.05, 0, "%.3f")
        imgui.next_column()

        if imgui.collapsing_header("Category A"):
            imgui.text("Blah blah blah")
        imgui.next_column()
        if imgui.collapsing_header("Category B"):
            imgui.text("Blah blah blah")
        imgui.next_column()
        if imgui.collapsing_header("Category C"):
            imgui.text("Blah blah blah")
        imgui.next_column()
        imgui.columns(1)
        imgui.separator()
        imgui.tree_pop()

    # Word wrapping
    if imgui.tree_node("Word-wrapping"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Word-wrapping")
        imgui.columns(2, "word-wrapping")
        imgui.separator()
        imgui.text_wrapped("The quick brown fox jumps over the lazy dog.")
        imgui.text_wrapped("Hello Left")
        imgui.next_column()
        imgui.text_wrapped("The quick brown fox jumps over the lazy dog.")
        imgui.text_wrapped("Hello Right")
        imgui.columns(1)
        imgui.separator()
        imgui.tree_pop()

    if imgui.tree_node("Horizontal Scrolling"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Horizontal Scrolling")
        imgui.set_next_window_content_size(ImVec2(1500.0, 0.0))
        child_size = ImVec2(0, imgui.get_font_size() * 20.0)
        imgui.begin_child("##ScrollingRegion", child_size, imgui.ChildFlags_.none, imgui.WindowFlags_.horizontal_scrollbar)
        imgui.columns(10)

        ITEMS_COUNT = 2000
        clipper = imgui.ListClipper()
        clipper.begin(ITEMS_COUNT)
        while clipper.step():
            for i in range(clipper.display_start, clipper.display_end):
                for j in range(10):
                    imgui.text(f"Line {i} Column {j}...")
                    imgui.next_column()
        imgui.columns(1)
        imgui.end_child()
        imgui.tree_pop()

    if imgui.tree_node("Tree"):
        IMGUI_DEMO_MARKER("Columns (legacy API)/Tree")
        imgui.columns(2, "tree", True)
        for x in range(3):
            open1 = imgui.tree_node(f"Node{x}##col{x}")
            imgui.next_column()
            imgui.text("Node contents")
            imgui.next_column()
            if open1:
                for y in range(3):
                    open2 = imgui.tree_node(f"Node{x}.{y}##col{x}{y}")
                    imgui.next_column()
                    imgui.text("Node contents")
                    if open2:
                        imgui.text("Even more contents")
                        if imgui.tree_node("Tree in column"):
                            imgui.text("The quick brown fox jumps over the lazy dog")
                            imgui.tree_pop()
                    imgui.next_column()
                    if open2:
                        imgui.tree_pop()
                imgui.tree_pop()
        imgui.columns(1)
        imgui.tree_pop()

    imgui.tree_pop()



# [SECTION] Helpers

class indented_block:
    """A fake context manager in order to get comparable layout for C++ anonymous blocks"""
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        pass


def help_marker(desc: str) -> None:
    imgui.text_disabled("(?)")
    if imgui.begin_item_tooltip():
        imgui.push_text_wrap_pos(imgui.get_font_size() * 35.0)
        imgui.text_unformatted(desc)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()

def show_docking_disabled_message():
    io = imgui.get_io()
    imgui.text("ERROR: Docking is not enabled! See Demo > Configuration.")
    imgui.text("Set io.config_flags |= imgui.ConfigFlags.DockingEnable in your code, or ")
    imgui.same_line(0.0, 0.0)
    if imgui.small_button("click here"):
        io.config_flags |= imgui.ConfigFlags_.docking_enable


# Helper to wire demo markers located in code to an interactive browser
# typedef void (*ImGuiDemoMarkerCallback)(const char* file, int line, const char* section, void* user_data);
# extern ImGuiDemoMarkerCallback      GImGuiDemoMarkerCallback;
# extern void*                        GImGuiDemoMarkerCallbackUserData;
# ImGuiDemoMarkerCallback             GImGuiDemoMarkerCallback = NULL;
# void*                               GImGuiDemoMarkerCallbackUserData = NULL;
#define IMGUI_DEMO_MARKER(section)  do { if (GImGuiDemoMarkerCallback != NULL) GImGuiDemoMarkerCallback(__FILE__, __LINE__, section, GImGuiDemoMarkerCallbackUserData); } while (0)
IMGUI_DEMO_MARKER_IS_ACTIVE = True


def IMGUI_DEMO_MARKER(section: str):
    pass


# [SECTION] Demo Window / ShowDemoWindow()
# - show_demo_window()
# - show_demo_window_widgets()
# - show_demo_window_layout()
# - show_demo_window_popups()
# - show_demo_window_tables()
# - show_demo_window_columns()
# - show_demo_window_inputs()

# Demonstrate most Dear ImGui features (this is big function!)
# You may execute this function to experiment with the UI and understand what it does.
# You may then search for keywords in the code when you are interested by a specific feature.
def show_demo_window(p_open: Optional[bool]=None) -> Optional[bool]:
    return show_demo_window_maybe_docked(True, p_open)


def show_demo_window_maybe_docked(create_window: bool, p_open: Optional[bool] = None) -> Optional[bool]:
    # Exceptionally add an extra assert here for people confused about initial Dear ImGui setup
    # Most functions would normally just assert/crash if the context is missing.
    assert imgui.get_current_context() is not None, "Missing Dear ImGui context. Refer to examples app!"

    static = show_demo_window
    if not hasattr(static, "show_app_main_menu_bar"):
        # Examples Apps (accessible from the "Examples" menu)
        static.show_app_main_menu_bar = False
        static.show_app_console = False
        static.show_app_custom_rendering = False
        static.show_app_dockspace = False
        static.show_app_documents = False
        static.show_app_log = False
        static.show_app_layout = False
        static.show_app_property_editor = False
        static.show_app_simple_overlay = False
        static.show_app_auto_resize = False
        static.show_app_constrained_resize = False
        static.show_app_fullscreen = False
        static.show_app_long_text = False
        static.show_app_window_titles = False

    # Process the examples apps
    if static.show_app_main_menu_bar:       show_example_app_main_menu_bar()
    # Process the Docking app first, as explicit DockSpace() nodes needs to be submitted early
    if static.show_app_dockspace:           static.show_app_dockspace = show_example_app_dock_space(static.show_app_dockspace)
    # Process the Document app next, as it may also use a DockSpace()
    if static.show_app_documents:           static.show_app_documents = show_example_app_documents(static.show_app_documents)
    if static.show_app_console:             static.show_app_console = show_example_app_console(static.show_app_console)
    if static.show_app_custom_rendering:    static.show_app_custom_rendering = show_example_app_custom_rendering(static.show_app_custom_rendering)
    if static.show_app_log:                 static.show_app_log = show_example_app_log(static.show_app_log)
    if static.show_app_layout:              static.show_app_layout = show_example_app_layout(static.show_app_layout)
    if static.show_app_property_editor:     static.show_app_property_editor = show_example_app_property_editor(static.show_app_property_editor)
    if static.show_app_simple_overlay:      static.show_app_simple_overlay = show_example_app_simple_overlay(static.show_app_simple_overlay)
    if static.show_app_auto_resize:         static.show_app_auto_resize = show_example_app_auto_resize(static.show_app_auto_resize)
    if static.show_app_constrained_resize:  static.show_app_constrained_resize = show_example_app_constrained_resize(static.show_app_constrained_resize)
    if static.show_app_fullscreen:          static.show_app_fullscreen = show_example_app_fullscreen(static.show_app_fullscreen)
    if static.show_app_long_text:           static.show_app_long_text = show_example_app_long_text(static.show_app_long_text)
    if static.show_app_window_titles:       static.show_app_window_titles = show_example_app_window_titles(static.show_app_window_titles)


    # Dear ImGui Tools (accessible from the "Tools" menu)
    if not hasattr(static, "show_tool_metrics"):
        static.show_tool_metrics = False
        static.show_tool_debug_log = False
        static.show_tool_id_stack_tool = False
        static.show_tool_style_editor = False
        static.show_tool_about = False

    # Dear ImGui Tools (accessible from the "Tools" menu)
    if static.show_tool_metrics:
        imgui.show_metrics_window(static.show_tool_metrics)
    if static.show_tool_debug_log:
        imgui.show_debug_log_window(static.show_tool_debug_log)
    if static.show_tool_id_stack_tool:
        imgui.show_id_stack_tool_window(static.show_tool_id_stack_tool)
    if static.show_tool_style_editor:
        IMGUI_DEMO_MARKER("Tools/Style Editor")
        _, static.show_tool_style_editor = imgui.begin("Dear ImGui Style Editor", static.show_tool_style_editor)
        imgui.show_style_editor()
        imgui.end()
    if static.show_tool_about:
        IMGUI_DEMO_MARKER("Tools/About Dear ImGui")
        imgui.show_about_window(static.show_tool_about)

    # Demonstrate the various window flags. Typically you would just use the default!
    if not hasattr(static, "no_titlebar"):
        static.no_titlebar = False
        static.no_scrollbar = False
        static.no_menu = False
        static.no_move = False
        static.no_resize = False
        static.no_collapse = False
        static.no_close = False
        static.no_nav = False
        static.no_background = False
        static.no_bring_to_front = False
        static.no_docking = False
        static.unsaved_document = False

    window_flags = 0
    if static.no_titlebar:        window_flags |= imgui.WindowFlags_.no_title_bar
    if static.no_scrollbar:       window_flags |= imgui.WindowFlags_.no_scrollbar
    if not static.no_menu:        window_flags |= imgui.WindowFlags_.menu_bar
    if static.no_move:            window_flags |= imgui.WindowFlags_.no_move
    if static.no_resize:          window_flags |= imgui.WindowFlags_.no_resize
    if static.no_collapse:        window_flags |= imgui.WindowFlags_.no_collapse
    if static.no_nav:             window_flags |= imgui.WindowFlags_.no_nav
    if static.no_background:      window_flags |= imgui.WindowFlags_.no_background
    if static.no_bring_to_front:  window_flags |= imgui.WindowFlags_.no_bring_to_front_on_focus
    if static.no_docking:         window_flags |= imgui.WindowFlags_.no_docking
    if static.unsaved_document:   window_flags |= imgui.WindowFlags_.unsaved_document
    if static.no_close:
        p_open = None  # Don't pass our bool* to Begin

    # We specify a default position/size in case there's no data in the .ini file.
    # We only do it to make the demo applications a little more welcoming, but typically this isn't required.
    main_viewport = imgui.get_main_viewport()

    if create_window:
        imgui.set_next_window_pos(ImVec2(main_viewport.work_pos.x + 650, main_viewport.work_pos.y + 20), imgui.Cond_.first_use_ever)
        imgui.set_next_window_size(ImVec2(550, 680), imgui.Cond_.first_use_ever)

        # Main body of the Demo window starts here.
        if not imgui.begin("Dear ImGui Demo", p_open, window_flags):
            # Early out if the window is collapsed, as an optimization.
            imgui.end()
            return p_open

    # Most "big" widgets share a common width settings by default. See 'Demo->Layout->Widgets Width' for details.
    # e.g. Use 2/3 of the space for widgets and 1/3 for labels (right align)
    #imgui.push_item_width(-imgui.get_window_width() * 0.35)
    # e.g. Leave a fixed amount of width for labels (by passing a negative value), the rest goes to widgets.
    imgui.push_item_width(imgui.get_font_size() * -12)

    # Menu Bar
    if imgui.begin_menu_bar():
        if imgui.begin_menu("Menu"):
            IMGUI_DEMO_MARKER("Menu/File")
            show_example_menu_file()
            imgui.end_menu()

        if imgui.begin_menu("Examples"):
            IMGUI_DEMO_MARKER("Menu/Examples")
            _, static.show_app_main_menu_bar = imgui.menu_item("Main menu bar", "", static.show_app_main_menu_bar)

            imgui.separator_text("Mini apps")
            _, static.show_app_console = imgui.menu_item("Console", "", static.show_app_console)
            _, static.show_app_custom_rendering = imgui.menu_item("Custom rendering", "", static.show_app_custom_rendering)
            _, static.show_app_dockspace = imgui.menu_item("Dockspace", "", static.show_app_dockspace)
            _, static.show_app_documents = imgui.menu_item("Documents", "", static.show_app_documents)
            _, static.show_app_log = imgui.menu_item("Log", "", static.show_app_log)
            _, static.show_app_property_editor = imgui.menu_item("Property editor", "", static.show_app_property_editor)
            _, static.show_app_layout = imgui.menu_item("Simple layout", "", static.show_app_layout)
            _, static.show_app_simple_overlay = imgui.menu_item("Simple overlay", "", static.show_app_simple_overlay)

            imgui.separator_text("Concepts")
            _, static.show_app_auto_resize = imgui.menu_item("Auto-resizing window", "", static.show_app_auto_resize)
            _, static.show_app_constrained_resize = imgui.menu_item("Constrained-resizing window", "", static.show_app_constrained_resize)
            _, static.show_app_fullscreen = imgui.menu_item("Fullscreen window", "", static.show_app_fullscreen)
            _, static.show_app_long_text = imgui.menu_item("Long text display", "", static.show_app_long_text)
            _, static.show_app_window_titles = imgui.menu_item("Manipulating window titles", "", static.show_app_window_titles)

            imgui.end_menu()

        # Continuing inside the show_demo_window function
        if imgui.begin_menu("Tools"):
            IMGUI_DEMO_MARKER("Menu/Tools")
            has_debug_tools = not IMGUI_DISABLE_DEBUG_TOOLS

            _, static.show_tool_metrics = imgui.menu_item("Metrics/Debugger", "", static.show_tool_metrics, has_debug_tools)
            _, static.show_tool_debug_log = imgui.menu_item("Debug Log", "", static.show_tool_debug_log, has_debug_tools)
            _, static.show_tool_id_stack_tool = imgui.menu_item("ID Stack Tool", "", static.show_tool_id_stack_tool, has_debug_tools)
            _, static.show_tool_style_editor = imgui.menu_item("Style Editor", "", static.show_tool_style_editor)
            _, static.show_tool_about = imgui.menu_item("About Dear ImGui", "", static.show_tool_about)
            imgui.end_menu()

        imgui.end_menu_bar()

    imgui.text(f"dear imgui says hello! ({imgui.get_version()})")
    imgui.spacing()

    imgui.begin_child("Demos")

    IMGUI_DEMO_MARKER("Help")
    if imgui.collapsing_header("Help"):
        imgui.separator_text("ABOUT THIS DEMO:")
        imgui.bullet_text("Sections below are demonstrating many aspects of the library.")
        imgui.bullet_text("The \"Examples\" menu above leads to more demo contents.")
        imgui.bullet_text("The \"Tools\" menu above gives access to: About Box, Style Editor,\n"
                          "and Metrics/Debugger (general purpose Dear ImGui debugging tool).")

        imgui.separator_text("PROGRAMMER GUIDE:")
        imgui.bullet_text("See the show_demo_window() code in imgui_demo.py. <- you are here!")
        imgui.bullet_text("See comments in imgui.py.")
        imgui.bullet_text("See example applications in the examples/ folder.")
        imgui.bullet_text("Read the FAQ at https://www.dearimgui.com/faq/")
        imgui.bullet_text("Set 'io.config_flags |= NavEnableKeyboard' for keyboard controls.")
        imgui.bullet_text("Set 'io.config_flags |= NavEnableGamepad' for gamepad controls.")

        imgui.separator_text("USER GUIDE:")
        imgui.show_user_guide()

    IMGUI_DEMO_MARKER("Configuration")
    if imgui.collapsing_header("Configuration"):
        io = imgui.get_io()

        if imgui.tree_node("Configuration##2"):
            imgui.separator_text("General")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NavEnableKeyboard", io.config_flags, imgui.ConfigFlags_.nav_enable_keyboard)
            imgui.same_line(); help_marker("Enable keyboard controls.")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NavEnableGamepad", io.config_flags, imgui.ConfigFlags_.nav_enable_gamepad)
            imgui.same_line(); help_marker("Enable gamepad controls. Require backend to set io.BackendFlags |= ImGuiBackendFlags_HasGamepad.\n\nRead instructions in imgui.cpp for details.")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NoMouse", io.config_flags, imgui.ConfigFlags_.no_mouse)
            if io.config_flags & imgui.ConfigFlags_.no_mouse:
                # The "NoMouse" option can get us stuck with a disabled mouse! Let's provide an alternative way to fix it:
                if math.fmod(time.time(), 0.40) < 0.20:
                    imgui.same_line()
                    imgui.text("<<PRESS SPACE TO DISABLE>>")
                if imgui.is_key_pressed(imgui.Key.space):
                    io.config_flags &= ~imgui.ConfigFlags_.no_mouse
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NoMouseCursorChange", io.config_flags, imgui.ConfigFlags_.no_mouse_cursor_change)
            imgui.same_line(); help_marker("Instruct backend to not alter mouse cursor shape and visibility.")

            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: DockingEnable", io.config_flags, imgui.ConfigFlags_.docking_enable)
            imgui.same_line()
            if io.config_docking_with_shift:
                help_marker("Drag from window title bar or their tab to dock/undock. Hold SHIFT to enable docking.\n\nDrag from window menu button (upper-left button) to undock an entire node (all windows).")
            else:
                help_marker("Drag from window title bar or their tab to dock/undock. Hold SHIFT to disable docking.\n\nDrag from window menu button (upper-left button) to undock an entire node (all windows).")
            if io.config_flags & imgui.ConfigFlags_.docking_enable:
                imgui.indent()
                _, io.config_docking_no_split = imgui.checkbox("io.ConfigDockingNoSplit", io.config_docking_no_split)
                imgui.same_line(); help_marker("Simplified docking mode: disable window splitting, so docking is limited to merging multiple windows together into tab-bars.")
                _, io.config_docking_with_shift = imgui.checkbox("io.ConfigDockingWithShift", io.config_docking_with_shift)
                imgui.same_line(); help_marker("Enable docking when holding Shift only (allow to drop in wider space, reduce visual noise)")
                _, io.config_docking_always_tab_bar = imgui.checkbox("io.ConfigDockingAlwaysTabBar", io.config_docking_always_tab_bar)
                imgui.same_line(); help_marker("Create a docking node and tab-bar on single floating windows.")
                _, io.config_docking_transparent_payload = imgui.checkbox("io.ConfigDockingTransparentPayload", io.config_docking_transparent_payload)
                imgui.same_line(); help_marker("Make window or viewport transparent when docking and only display docking boxes on the target viewport. Useful if rendering of multiple viewport cannot be synced. Best used with ConfigViewportsNoAutoMerge.")
                imgui.unindent()

            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: ViewportsEnable", io.config_flags, imgui.ConfigFlags_.viewports_enable)
            imgui.same_line(); help_marker("[beta] Enable beta multi-viewports support. See ImGuiPlatformIO for details.")
            if io.config_flags & imgui.ConfigFlags_.viewports_enable:
                imgui.indent()
                _, io.config_viewports_no_auto_merge = imgui.checkbox("io.ConfigViewportsNoAutoMerge", io.config_viewports_no_auto_merge)
                imgui.same_line(); help_marker("Set to make all floating imgui windows always create their own viewport. Otherwise, they are merged into the main host viewports when overlapping it.")
                _, io.config_viewports_no_task_bar_icon = imgui.checkbox("io.ConfigViewportsNoTaskBarIcon", io.config_viewports_no_task_bar_icon)
                imgui.same_line(); help_marker("Toggling this at runtime is normally unsupported (most platform backends won't refresh the task bar icon state right away).")
                _, io.config_viewports_no_decoration = imgui.checkbox("io.ConfigViewportsNoDecoration", io.config_viewports_no_decoration)
                imgui.same_line(); help_marker("Toggling this at runtime is normally unsupported (most platform backends won't refresh the decoration right away).")
                _, io.config_viewports_no_default_parent = imgui.checkbox("io.ConfigViewportsNoDefaultParent", io.config_viewports_no_default_parent)
                imgui.same_line(); help_marker("Toggling this at runtime is normally unsupported (most platform backends won't refresh the parenting right away).")
                imgui.unindent()

            _, io.config_input_trickle_event_queue = imgui.checkbox("io.ConfigInputTrickleEventQueue", io.config_input_trickle_event_queue)
            imgui.same_line(); help_marker("Enable input queue trickling: some types of events submitted during the same frame (e.g. button down + up) will be spread over multiple frames, improving interactions with low framerates.")
            _, io.mouse_draw_cursor = imgui.checkbox("io.MouseDrawCursor", io.mouse_draw_cursor)
            imgui.same_line(); help_marker("Instruct Dear ImGui to render a mouse cursor itself. Note that a mouse cursor rendered via your application GPU rendering path will feel more laggy than hardware cursor, but will be more in sync with your other visuals.\n\nSome desktop applications may use both kinds of cursors (e.g. enable software cursor only when resizing/dragging something).")

            imgui.separator_text("Widgets")
            _, io.config_input_text_cursor_blink = imgui.checkbox("io.ConfigInputTextCursorBlink", io.config_input_text_cursor_blink)
            imgui.same_line(); help_marker("Enable blinking cursor (optional as some users consider it to be distracting).")
            _, io.config_input_text_enter_keep_active = imgui.checkbox("io.ConfigInputTextEnterKeepActive", io.config_input_text_enter_keep_active)
            imgui.same_line(); help_marker("Pressing Enter will keep item active and select contents (single-line only).")
            _, io.config_drag_click_to_input_text = imgui.checkbox("io.ConfigDragClickToInputText", io.config_drag_click_to_input_text)
            imgui.same_line(); help_marker("Enable turning DragXXX widgets into text input with a simple mouse click-release (without moving).")
            _, io.config_windows_resize_from_edges = imgui.checkbox("io.ConfigWindowsResizeFromEdges", io.config_windows_resize_from_edges)
            imgui.same_line(); help_marker("Enable resizing of windows from their edges and from the lower-left corner.\nThis requires (io.BackendFlags & ImGuiBackendFlags_HasMouseCursors) because it needs mouse cursor feedback.")
            _, io.config_windows_move_from_title_bar_only = imgui.checkbox("io.ConfigWindowsMoveFromTitleBarOnly", io.config_windows_move_from_title_bar_only)
            _, io.config_mac_osx_behaviors = imgui.checkbox("io.ConfigMacOSXBehaviors", io.config_mac_osx_behaviors)
            imgui.text("Also see Style->Rendering for rendering options.")

            imgui.separator_text("Debug")
            imgui.begin_disabled()
            _, io.config_debug_begin_return_value_once = imgui.checkbox("io.ConfigDebugBeginReturnValueOnce", io.config_debug_begin_return_value_once)
            imgui.end_disabled()
            imgui.same_line(); help_marker("First calls to Begin()/BeginChild() will return false.\n\nTHIS OPTION IS DISABLED because it needs to be set at application boot-time to make sense. Showing the disabled option is a way to make this feature easier to discover")
            _, io.config_debug_begin_return_value_loop = imgui.checkbox("io.ConfigDebugBeginReturnValueLoop", io.config_debug_begin_return_value_loop)
            imgui.same_line(); help_marker("Some calls to Begin()/BeginChild() will return false.\n\nWill cycle through window depths then repeat. Windows should be flickering while running.")
            _, io.config_debug_ignore_focus_loss = imgui.checkbox("io.ConfigDebugIgnoreFocusLoss", io.config_debug_ignore_focus_loss)
            imgui.same_line(); help_marker("Option to deactivate io.AddFocusEvent(false) handling. May facilitate interactions with a debugger when focus loss leads to clearing inputs data.")
            _, io.config_debug_ini_settings = imgui.checkbox("io.ConfigDebugIniSettings", io.config_debug_ini_settings)
            imgui.same_line(); help_marker("Option to save .ini data with extra comments (particularly helpful for Docking, but makes saving slower).")

            imgui.tree_pop()
            imgui.spacing()

        if imgui.tree_node("Backend Flags"):
            IMGUI_DEMO_MARKER("Configuration/Backend Flags")
            help_marker(
                "Those flags are set by the backends (imgui_impl_xxx files) to specify their capabilities.\n"
                "Here we expose them as read-only fields to avoid breaking interactions with your backend.")

            # Make a local copy to avoid modifying actual backend flags.
            imgui.begin_disabled()
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasGamepad", io.backend_flags, imgui.BackendFlags_.has_gamepad)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasMouseCursors", io.backend_flags, imgui.BackendFlags_.has_mouse_cursors)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasSetMousePos", io.backend_flags, imgui.BackendFlags_.has_set_mouse_pos)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: PlatformHasViewports", io.backend_flags, imgui.BackendFlags_.platform_has_viewports)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasMouseHoveredViewport", io.backend_flags, imgui.BackendFlags_.has_mouse_hovered_viewport)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: RendererHasVtxOffset", io.backend_flags, imgui.BackendFlags_.renderer_has_vtx_offset)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: RendererHasViewports", io.backend_flags, imgui.BackendFlags_.renderer_has_viewports)
            imgui.end_disabled()
            imgui.tree_pop()
            imgui.spacing()

        if imgui.tree_node("Style, Fonts"):
            IMGUI_DEMO_MARKER("Configuration/Style, Fonts")
            help_marker("The same contents can be accessed in 'Tools->Style Editor' or by calling the ShowStyleEditor() function.")
            imgui.show_style_editor()
            imgui.tree_pop()
            imgui.spacing()

        if imgui.tree_node("Capture/Logging"):
            IMGUI_DEMO_MARKER("Configuration/Capture, Logging")
            help_marker(
                "The logging API redirects all text output so you can easily capture the content of "
                "a window or a block. Tree nodes can be automatically expanded.\n"
                "Try opening any of the contents below in this window and then click one of the \"Log To\" button.")
            imgui.log_buttons()

            help_marker("You can also call imgui.log_text() to output directly to the log without a visual output.")
            if imgui.button("Copy \"Hello, world!\" to clipboard"):
                imgui.log_to_clipboard()
                imgui.log_text("Hello, world!")
                imgui.log_finish()
            imgui.tree_pop()

    IMGUI_DEMO_MARKER("Window options")
    if imgui.collapsing_header("Window options"):
        if imgui.begin_table("split", 3):
            imgui.table_next_column(); _, static.no_titlebar = imgui.checkbox("No titlebar", static.no_titlebar)
            imgui.table_next_column(); _, static.no_scrollbar = imgui.checkbox("No scrollbar", static.no_scrollbar)
            imgui.table_next_column(); _, static.no_menu = imgui.checkbox("No menu", static.no_menu)
            imgui.table_next_column(); _, static.no_move = imgui.checkbox("No move", static.no_move)
            imgui.table_next_column(); _, static.no_resize = imgui.checkbox("No resize", static.no_resize)
            imgui.table_next_column(); _, static.no_collapse = imgui.checkbox("No collapse", static.no_collapse)
            imgui.table_next_column(); _, static.no_close = imgui.checkbox("No close", static.no_close)
            imgui.table_next_column(); _, static.no_nav = imgui.checkbox("No nav", static.no_nav)
            imgui.table_next_column(); _, static.no_background = imgui.checkbox("No background", static.no_background)
            imgui.table_next_column(); _, static.no_bring_to_front = imgui.checkbox("No bring to front", static.no_bring_to_front)
            imgui.table_next_column(); _, static.no_docking = imgui.checkbox("No docking", static.no_docking)
            imgui.table_next_column(); _, static.unsaved_document = imgui.checkbox("Unsaved document", static.unsaved_document)
            imgui.end_table()

    # All demo contents
    show_demo_window_widgets()
    show_demo_window_layout()
    show_demo_window_popups()
    show_demo_window_tables()
    show_demo_window_inputs()

    # End of show_demo_window()
    imgui.end_child()  # </imgui.begin_child("Demos")>
    imgui.pop_item_width()

    if create_window:
        imgui.end()
    return True


def show_demo_window_widgets():
    IMGUI_DEMO_MARKER("Widgets")
    if not imgui.collapsing_header("Widgets"):
        return

    static = show_demo_window_widgets
    if not hasattr(static, "disable_all"):
        static.disable_all = False

    if static.disable_all:
        imgui.begin_disabled()

    if imgui.tree_node("Basic"):
        IMGUI_DEMO_MARKER("Widgets/Basic")
        imgui.separator_text("General")

        IMGUI_DEMO_MARKER("Widgets/Basic/Button")
        if not hasattr(static, "clicked"):
            static.clicked = 0
        if imgui.button("Button"):
            static.clicked += 1
        if static.clicked & 1:
            imgui.same_line()
            imgui.text("Thanks for clicking me!")

        IMGUI_DEMO_MARKER("Widgets/Basic/Checkbox")
        if not hasattr(static, "check"):
            static.check = True
        _, static.check = imgui.checkbox("checkbox", static.check)

        IMGUI_DEMO_MARKER("Widgets/Basic/RadioButton")
        if not hasattr(static, "e"):
            static.e = 0
        if imgui.radio_button("radio a", static.e == 0):
            static.e = 0
        imgui.same_line()
        if imgui.radio_button("radio b", static.e == 1):
            static.e = 1
        imgui.same_line()
        if imgui.radio_button("radio c", static.e == 2):
            static.e = 2

        # Color buttons, demonstrate using PushID() to add unique identifier in the ID stack, and changing style.
        IMGUI_DEMO_MARKER("Widgets/Basic/Buttons (Colored)")
        for i in range(7):
            if i > 0:
                imgui.same_line()
            imgui.push_id(i)
            hue = i / 7.0
            imgui.push_style_color(imgui.Col_.button, imgui.ImColor.hsv(hue, 0.6, 0.6).value)
            imgui.push_style_color(imgui.Col_.button_hovered, imgui.ImColor.hsv(hue, 0.7, 0.7).value)
            imgui.push_style_color(imgui.Col_.button_active, imgui.ImColor.hsv(hue, 0.8, 0.8).value)
            imgui.button("Click")
            imgui.pop_style_color(3)
            imgui.pop_id()

        # Use AlignTextToFramePadding() to align text baseline to the baseline of framed widgets elements
        imgui.align_text_to_frame_padding()
        imgui.text("Hold to repeat:")
        imgui.same_line()

        IMGUI_DEMO_MARKER("Widgets/Basic/Buttons (Repeating)")
        if not hasattr(static, "counter"): static.counter = 0
        spacing = imgui.get_style().item_inner_spacing.x
        imgui.push_item_flag(imgui.ItemFlags_.button_repeat, True)
        if imgui.arrow_button("##left", imgui.Dir.left):
            static.counter -= 1
        imgui.same_line(0.0, spacing)
        if imgui.arrow_button("##right", imgui.Dir.right):
            static.counter += 1
        imgui.pop_item_flag()
        imgui.same_line()
        imgui.text(f"{static.counter}")

        imgui.button("Tooltip")
        imgui.set_item_tooltip("I am a tooltip")

        imgui.label_text("label", "Value")

        imgui.separator_text("Inputs")

        with indented_block():
            IMGUI_DEMO_MARKER("Widgets/Basic/InputText")
            if not hasattr(static, 'str0'): static.str0 = "Hello, world!"
            changed, static.str0 = imgui.input_text("input text", static.str0, 128)
            imgui.same_line()
            help_marker(
                "USER:\n"
                "Hold SHIFT or use mouse to select text.\n"
                "CTRL+Left/Right to word jump.\n"
                "CTRL+A or Double-Click to select all.\n"
                "CTRL+X,CTRL+C,CTRL+V clipboard.\n"
                "CTRL+Z,CTRL+Y undo/redo.\n"
                "ESCAPE to revert.\n\n"
                "PROGRAMMER:\n"
                "You can use the ImGuiInputTextFlags_CallbackResize facility if you need to wire InputText() "
                "to a dynamic string type. See misc/cpp/imgui_stdlib.h for an example (this is not demonstrated "
                "in imgui_demo.cpp).")

            if not hasattr(static, 'str1'): static.str1 = ""
            changed, static.str1 = imgui.input_text_with_hint("input text (w/ hint)", "enter text here", static.str1, 128)

            IMGUI_DEMO_MARKER("Widgets/Basic/InputInt, InputFloat")
            if not hasattr(static, 'i0'): static.i0 = 123
            changed, static.i0 = imgui.input_int("input int", static.i0)

            if not hasattr(static, 'f0'): static.f0 = 0.001
            changed, static.f0 = imgui.input_float("input float", static.f0, 0.01, 1.0, "%.3f")

            if not hasattr(static, 'd0'): static.d0 = 999999.00000001
            changed, static.d0 = imgui.input_double("input double", static.d0, 0.01, 1.0, "%.8f")

            if not hasattr(static, 'f1'): static.f1 = 1.e10
            changed, static.f1 = imgui.input_float("input scientific", static.f1, 0.0, 0.0, "%e")
            imgui.same_line()
            help_marker(
                "You can input value using the scientific notation,\n"
                "e.g. \"1e+8\" becomes \"100000000\".")

            if not hasattr(static, 'vec4a'): static.vec4a = [0.10, 0.20, 0.30]
            changed, static.vec4a = imgui.input_float3("input float3", static.vec4a)

        imgui.separator_text("Drags")

        with indented_block():
            IMGUI_DEMO_MARKER("Widgets/Basic/DragInt, DragFloat")
            if not hasattr(static, 'i1'): static.i1 = 50
            if not hasattr(static, 'i2'): static.i2 = 42
            changed, static.i1 = imgui.drag_int("drag int", static.i1, 1)
            imgui.same_line()
            help_marker(
                "Click and drag to edit value.\n"
                "Hold SHIFT/ALT for faster/slower edit.\n"
                "Double-click or CTRL+click to input value.")

            changed, static.i2 = imgui.drag_int("drag int 0..100", static.i2, 1, 0, 100, "%d%%", imgui.SliderFlags_.always_clamp)

            if not hasattr(static, 'ff1'): static.ff1 = 1.00
            if not hasattr(static, 'ff2'): static.ff2 = 0.0067
            changed, static.ff1 = imgui.drag_float("drag float", static.ff1, 0.005)
            changed, static.ff2 = imgui.drag_float("drag small float", static.ff2, 0.0001, 0.0, 0.0, "%.06f ns")

        imgui.separator_text("Sliders")

        with indented_block():
            IMGUI_DEMO_MARKER("Widgets/Basic/SliderInt, SliderFloat")
            if not hasattr(static, 'iii1'): static.iii1 = 0
            changed, static.iii1 = imgui.slider_int("slider int", static.iii1, -1, 3)
            imgui.same_line()
            help_marker("CTRL+click to input value.")

            if not hasattr(static, 'fff1'): static.fff1 = 0.123
            if not hasattr(static, 'fff2'): static.fff2 = 0.0
            changed, static.fff1 = imgui.slider_float("slider float", static.fff1, 0.0, 1.0, "ratio = %.3f")
            changed, static.fff2 = imgui.slider_float("slider float (log)", static.fff2, -10.0, 10.0, "%.4f", imgui.SliderFlags_.logarithmic)

            IMGUI_DEMO_MARKER("Widgets/Basic/SliderAngle")
            if not hasattr(static, 'angle'): static.angle = 0.0
            changed, static.angle = imgui.slider_angle("slider angle", static.angle)

            IMGUI_DEMO_MARKER("Widgets/Basic/Slider (enum)")
            # Using the format string to display a name instead of an integer.
            # Here we completely omit '%d' from the format string, so it'll only display a name.
            # This technique can also be used with DragInt().
            Element = {'Fire': 0, 'Earth': 1, 'Air': 2, 'Water': 3}
            if not hasattr(static, 'elem'): static.elem = Element['Fire']
            elem_names = ["Fire", "Earth", "Air", "Water"]
            elem_name = elem_names[static.elem]
            changed, static.elem = imgui.slider_int("slider enum", static.elem, 0, len(Element) - 1, elem_name)
            imgui.same_line(); help_marker("Using the format string parameter to display a name instead of the underlying integer.")

        imgui.separator_text("Selectors/Pickers")

        with indented_block():
            # Color editor widgets
            IMGUI_DEMO_MARKER("Widgets/Basic/ColorEdit3, ColorEdit4")
            if not hasattr(static, 'col1'): static.col1 = ImVec4(1.0, 0.0, 0.2, 1.0)
            if not hasattr(static, 'col2'): static.col2 = ImVec4(0.4, 0.7, 0.0, 0.5)
            changed, static.col1 = imgui.color_edit3("color 1", static.col1)
            imgui.same_line()
            help_marker(
                "Click on the color square to open a color picker.\n"
                "Click and hold to use drag and drop.\n"
                "Right-click on the color square to show options.\n"
                "CTRL+click on individual component to input value.\n")

            changed, static.col2 = imgui.color_edit4("color 2", static.col2)

        with indented_block():
            # Using the _simplified_ one-liner Combo() api here
            # See "Combo" section for examples of how to use the more flexible BeginCombo()/EndCombo() api.
            IMGUI_DEMO_MARKER("Widgets/Basic/Combo")
            items = ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIIIIII", "JJJJ", "KKKKKKK"]
            if not hasattr(static, 'item_current'): static.item_current = 0
            # The third parameter is the number of items visible in the drop-down list before scrolling.
            changed, static.item_current = imgui.combo("combo", static.item_current, items, len(items))
            imgui.same_line()
            # Explanation of how to use the more flexible and general BeginCombo()/EndCombo() API.
            help_marker(
                "Using the simplified one-liner Combo API here.\n"
                "Refer to the \"Combo\" section below for an explanation of how to use the more flexible "
                "and general BeginCombo/EndCombo API.")

        with indented_block():
            # Using the _simplified_ one-liner ListBox() api here
            # See "List boxes" section for examples of how to use the more flexible BeginListBox()/EndListBox() api.
            IMGUI_DEMO_MARKER("Widgets/Basic/ListBox")
            items = ["Apple", "Banana", "Cherry", "Kiwi", "Mango", "Orange", "Pineapple", "Strawberry", "Watermelon"]
            if not hasattr(static, 'item_current'): static.item_current = 1
            # The fourth parameter is the number of items visible before the listbox needs to scroll
            changed, static.item_current = imgui.list_box("listbox", static.item_current, items, 4)
            imgui.same_line()
            # Explanation of how to use the more flexible and general BeginListBox()/EndListBox() API.
            help_marker(
                "Using the simplified one-liner ListBox API here.\n"
                "Refer to the \"List boxes\" section below for an explanation of how to use the more flexible "
                "and general BeginListBox/EndListBox API.")

        imgui.tree_pop()

    if imgui.tree_node("Tooltips"):
        IMGUI_DEMO_MARKER("Widgets/Tooltips")
        # Tooltips are windows following the mouse. They do not take focus away.
        imgui.separator_text("General")

        # Explanation about tooltips
        help_marker(
            "Tooltip are typically created by using a IsItemHovered() + SetTooltip() sequence.\n\n"
            "We provide a helper SetItemTooltip() function to perform the two with standards flags.")

        # Set a button and a basic tooltip
        imgui.button("Basic")
        imgui.set_item_tooltip("I am a tooltip")

        # Set a button and a more complex tooltip with additional contents
        imgui.button("Fancy")
        if imgui.begin_item_tooltip():
            imgui.text("I am a fancy tooltip")
            static.arr = [0.6, 0.1, 1.0, 0.5, 0.92, 0.1, 0.2] if not hasattr(static, 'arr') else static.arr
            imgui.plot_lines("Curve", np.array(static.arr, np.float32))
            imgui.text(f"Sin(time) = {math.sin(imgui.get_time())}")
            imgui.end_tooltip()

        imgui.separator_text("Always On")

        # Showcase NOT relying on IsItemHovered() to emit a tooltip.
        # Here the tooltip is always emitted when 'always_on' is true.
        if not hasattr(static, 'always_on'): static.always_on = 0
        if imgui.radio_button("Off", static.always_on == 0): static.always_on = 0
        imgui.same_line()
        if imgui.radio_button("Always On (Simple)", static.always_on == 1): static.always_on = 1
        imgui.same_line()
        if imgui.radio_button("Always On (Advanced)", static.always_on == 2): static.always_on = 2

        if static.always_on == 1:
            imgui.set_tooltip("I am following you around.")
        elif static.always_on == 2 and imgui.begin_tooltip():
            imgui.progress_bar(math.sin(imgui.get_time()) * 0.5 + 0.5, ImVec2(imgui.get_font_size() * 25, 0.0))
            imgui.end_tooltip()

        # Custom tooltip behavior
        imgui.separator_text("Custom")

        help_marker(
            "Passing ImGuiHoveredFlags_ForTooltip to IsItemHovered() is the preferred way to standardize "
            "tooltip activation details across your application. You may however decide to use custom "
            "flags for a specific tooltip instance.")

        # Manual tooltip emission example
        imgui.button("Manual")
        if imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip):
            imgui.set_tooltip("I am a manually emitted tooltip.")

        # No delay tooltip example
        imgui.button("DelayNone")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_none):
            imgui.set_tooltip("I am a tooltip with no delay.")

        # Short delay tooltip example
        imgui.button("DelayShort")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_short | imgui.HoveredFlags_.no_shared_delay):
            imgui.set_tooltip(f"I am a tooltip with a short delay ({imgui.get_style().hover_delay_short:.2f} sec).")

        imgui.button("DelayLong")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal | imgui.HoveredFlags_.no_shared_delay):
            imgui.set_tooltip(f"I am a tooltip with a long delay ({imgui.get_style().hover_delay_normal:.2f} sec).")

        imgui.button("Stationary")
        if imgui.is_item_hovered(imgui.HoveredFlags_.stationary):
            imgui.set_tooltip("I am a tooltip requiring mouse to be stationary before activating.")

        # Tooltips can also be shown for disabled items
        imgui.begin_disabled()
        imgui.button("Disabled item")
        imgui.end_disabled()
        if imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip):
            imgui.set_tooltip("I am a a tooltip for a disabled item.")

        # Close the tree node for "Tooltips"
        imgui.tree_pop()

    # Testing ImGuiOnceUponAFrame helper.
    #static ImGuiOnceUponAFrame once;
    #for (int i = 0; i < 5; i++)
    #    if (once)
    #        ImGui::Text("This will be displayed only once.");

    if imgui.tree_node("Tree Nodes"):
        IMGUI_DEMO_MARKER("Widgets/Tree Nodes")
        if imgui.tree_node("Basic trees"):
            IMGUI_DEMO_MARKER("Widgets/Tree Nodes/Basic trees")
            for i in range(5):
                # Use SetNextItemOpen() to set the default state of a node to be open. We could
                # also use TreeNodeEx() with the ImGuiTreeNodeFlags_DefaultOpen flag to achieve the same thing!
                if i == 0:
                    imgui.set_next_item_open(True, imgui.Cond_.once)

                if imgui.tree_node(str(i), f"Child {i}"):
                    imgui.text("blah blah")
                    imgui.same_line()
                    if imgui.small_button("button"):
                        pass  # Here you can handle the button press.
                    imgui.tree_pop()
            imgui.tree_pop()

        if imgui.tree_node("Advanced, with Selectable nodes"):
            IMGUI_DEMO_MARKER("Widgets/Tree Nodes/Advanced, with Selectable nodes")
            # Help marker with explanation
            help_marker(
                "This is a more typical looking tree with selectable nodes.\n"
                "Click to select, CTRL+Click to toggle, click on arrows or double-click to open.")

            if not hasattr(static, 'base_flags'): static.base_flags = imgui.TreeNodeFlags_.open_on_arrow | imgui.TreeNodeFlags_.open_on_double_click | imgui.TreeNodeFlags_.span_avail_width
            if not hasattr(static, 'align_label_with_current_x_position'): static.align_label_with_current_x_position = False
            if not hasattr(static, 'test_drag_and_drop'): static.test_drag_and_drop = False
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_OpenOnArrow", static.base_flags, imgui.TreeNodeFlags_.open_on_arrow)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_OpenOnDoubleClick", static.base_flags, imgui.TreeNodeFlags_.open_on_double_click)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanAvailWidth", static.base_flags, imgui.TreeNodeFlags_.span_avail_width); imgui.same_line(); help_marker("Extend hit area to all available width instead of allowing more items to be laid out after the node.")
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanFullWidth", static.base_flags, imgui.TreeNodeFlags_.span_full_width)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanAllColumns", static.base_flags, imgui.TreeNodeFlags_.span_all_columns); imgui.same_line(); help_marker("For use in Tables only.")
            _, static.align_label_with_current_x_position = imgui.checkbox("Align label with current X position", static.align_label_with_current_x_position)
            _, static.test_drag_and_drop = imgui.checkbox("Test tree node as drag source", static.test_drag_and_drop)
            imgui.text("Hello!")
            if static.align_label_with_current_x_position:
                imgui.unindent(imgui.get_tree_node_to_label_spacing())

            # 'selection_mask' is a simple representation of what may be the user-side selection state.
            # 'node_clicked' is temporary storage of what node we have clicked to process selection at the end of the loop.
            if not hasattr(static, 'selection_mask'): static.selection_mask = (1 << 2)
            node_clicked = -1
            for i in range(6):
                # Set node flags based on the selection state.
                node_flags = static.base_flags
                is_selected = (static.selection_mask & (1 << i)) != 0
                if is_selected:
                    node_flags |= imgui.TreeNodeFlags_.selected
                if i < 3:
                    # Items 0..2 are Tree Nodes.
                    node_open = imgui.tree_node_ex(str(i), node_flags, f"Selectable Node {i}")
                    if imgui.is_item_clicked() and not imgui.is_item_toggled_open():
                        node_clicked = i
                    if static.test_drag_and_drop and imgui.begin_drag_drop_source():
                        imgui.set_drag_drop_payload("_TREENODE", None, 0)
                        imgui.text("This is a drag and drop source")
                        imgui.end_drag_drop_source()
                    if node_open:
                        imgui.bullet_text("Blah blah\nBlah Blah")
                        imgui.tree_pop()

                else:
                    # Items 3..5 are Tree Leaves.
                    node_flags |= imgui.TreeNodeFlags_.leaf | imgui.TreeNodeFlags_.no_tree_push_on_open
                    imgui.tree_node_ex(str(i), node_flags, f"Selectable Leaf {i}")
                    if imgui.is_item_clicked() and not imgui.is_item_toggled_open():
                        node_clicked = i
                    if static.test_drag_and_drop and imgui.begin_drag_drop_source():
                        imgui.set_drag_drop_payload("_TREENODE", None, 0)
                        imgui.text("This is a drag and drop source")
                        imgui.end_drag_drop_source()

            # Update selection state outside of the tree loop
            if node_clicked != -1:
                if imgui.get_io().key_ctrl:
                    static.selection_mask ^= (1 << node_clicked)  # CTRL+click to toggle
                else:
                    static.selection_mask = (1 << node_clicked)  # Click to single-select

            # Adjust the indentation if aligning the label with the current X position
            if static.align_label_with_current_x_position:
                imgui.indent(imgui.get_tree_node_to_label_spacing())

            # End of the "Advanced, with Selectable nodes" tree node
            imgui.tree_pop()

        if imgui.tree_node("Hierarchy lines"):
            IMGUI_DEMO_MARKER("Widgets/Tree Nodes/Hierarchy lines")
            if not hasattr(static, "tree_lines_flags"):
                static.tree_lines_flags = imgui.TreeNodeFlags_.draw_lines_full | imgui.TreeNodeFlags_.default_open
            help_marker("Default option for DrawLinesXXX is stored in style.TreeLinesFlags")
            _, static.tree_lines_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_DrawLinesNone", static.tree_lines_flags, imgui.TreeNodeFlags_.draw_lines_none)
            _, static.tree_lines_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_DrawLinesFull", static.tree_lines_flags, imgui.TreeNodeFlags_.draw_lines_full)
            _, static.tree_lines_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_DrawLinesToNodes", static.tree_lines_flags, imgui.TreeNodeFlags_.draw_lines_to_nodes)

            if imgui.tree_node_ex("Parent", static.tree_lines_flags):
                if imgui.tree_node_ex("Child 1", static.tree_lines_flags):
                    imgui.button("Button for Child 1")
                    imgui.tree_pop()
                if imgui.tree_node_ex("Child 2", static.tree_lines_flags):
                    imgui.button("Button for Child 2")
                    imgui.tree_pop()
                imgui.text("Remaining contents")
                imgui.text("Remaining contents")
                imgui.tree_pop()

            imgui.tree_pop()

        # End of the "Tree Nodes" tree node
        imgui.tree_pop()

    if imgui.tree_node("Collapsing Headers"):
        IMGUI_DEMO_MARKER("Widgets/Collapsing Headers")
        # Initialize static variable for the checkbox state
        if not hasattr(static, 'closable_group'): static.closable_group = True
        # Checkbox to toggle the visibility of the second header
        _, static.closable_group = imgui.checkbox("Show 2nd header", static.closable_group)

        # First collapsible header
        if imgui.collapsing_header("Header", imgui.TreeNodeFlags_.none):
            # Display hover state and some content within the header
            imgui.text(f"IsItemHovered: {int(imgui.is_item_hovered())}")
            for i in range(5):
                imgui.text(f"Some content {i}")

        # Second collapsible header with a close button
        if imgui.collapsing_header("Header with a close button", static.closable_group):
            # Display hover state and more content within the second header
            imgui.text(f"IsItemHovered: {int(imgui.is_item_hovered())}")
            for i in range(5):
                imgui.text(f"More content {i}")

        # The third header with a bullet is commented out in the original C++ code,
        # so it's not active in this translation either.

        # End of the "Collapsing Headers" tree node
        imgui.tree_pop()

    if imgui.tree_node("Bullets"):
        IMGUI_DEMO_MARKER("Widgets/Bullets")
        # Simple bullet points
        imgui.bullet_text("Bullet point 1")
        imgui.bullet_text("Bullet point 2\nOn multiple lines")

        # Tree node with bullet point
        if imgui.tree_node("Tree node"):
            imgui.bullet_text("Another bullet point")
            imgui.tree_pop()

        # Separate bullet point and text/button
        imgui.bullet()
        imgui.text("Bullet point 3 (two calls)")

        imgui.bullet()
        if imgui.small_button("Button"):
            pass  # Placeholder for button action

        imgui.tree_pop()

    if imgui.tree_node("Text"):
        IMGUI_DEMO_MARKER("Widgets/Text")
        if imgui.tree_node("Colorful Text"):
            IMGUI_DEMO_MARKER("Widgets/Text/Colored Text")
            # Shortcuts for colored text
            imgui.text_colored(ImVec4(1.0, 0.0, 1.0, 1.0), "Pink")
            imgui.text_colored(ImVec4(1.0, 1.0, 0.0, 1.0), "Yellow")
            imgui.text_disabled("Disabled")
            imgui.same_line()
            help_marker("The TextDisabled color is stored in ImGuiStyle.")
            imgui.tree_pop()

        if imgui.tree_node("Word Wrapping"):
            IMGUI_DEMO_MARKER("Widgets/Text/Word Wrapping")
            # Shortcuts for word-wrapped text
            imgui.text_wrapped(
                "This text should automatically wrap on the edge of the window. The current implementation "
                "for text wrapping follows simple rules suitable for English and possibly other languages.")
            imgui.spacing()

            if not hasattr(static, 'wrap_width'): static.wrap_width = 200.0
            changed, static.wrap_width = imgui.slider_float("Wrap width", static.wrap_width, -20, 600, "%.0f")

            # Retrieve the draw list to render primitives
            draw_list = imgui.get_window_draw_list()
            for n in range(2):
                imgui.text(f"Test paragraph {n}:")
                pos = imgui.get_cursor_screen_pos()
                marker_min = ImVec2(pos[0] + static.wrap_width, pos[1])
                marker_max = ImVec2(pos[0] + static.wrap_width + 10, pos[1] + imgui.get_text_line_height())
                imgui.push_text_wrap_pos(imgui.get_cursor_pos()[0] + static.wrap_width)

                # Display wrapped text and its bounding box
                if n == 0:
                    imgui.text(f"The lazy dog is a good dog. This paragraph should fit within {static.wrap_width:.0f} pixels. "
                               "Testing a 1 character word. The quick brown fox jumps over the lazy dog.")
                else:
                    imgui.text("aaaaaaaa bbbbbbbb, c cccccccc,dddddddd. d eeeeeeee   ffffffff. gggggggg!hhhhhhhh")

                # Draw the bounding box and a marker for the wrap width
                draw_list.add_rect(imgui.get_item_rect_min(), imgui.get_item_rect_max(), imgui.IM_COL32(255, 255, 0, 255))
                draw_list.add_rect_filled(marker_min, marker_max, imgui.IM_COL32(255, 0, 255, 255))
                imgui.pop_text_wrap_pos()

            imgui.tree_pop()

        if imgui.tree_node("UTF-8 Text"):
            IMGUI_DEMO_MARKER("Widgets/Text/UTF-8 Text")
            # Explanation about UTF-8 encoding
            imgui.text_wrapped(
                "CJK text will only appear if the font was loaded with the appropriate CJK character ranges. "
                "Call io.Fonts->AddFontFromFileTTF() manually to load extra character ranges. "
                "Read docs/FONTS.md for details.")
            # Display UTF-8 encoded Japanese characters
            imgui.text("Hiragana: かきくけこ (kakikukeko)")  # Using the actual unicode characters for clarity
            imgui.text("Kanjis: 日本語 (nihongo)")

            # Input field for UTF-8 text
            if not hasattr(static, 'buf'): static.buf = "日本語"  # Initial buffer with UTF-8 encoded Japanese
            _, static.buf = imgui.input_text("UTF-8 input", static.buf, 32)

            imgui.tree_pop()

        if imgui.tree_node("Font Size"):
            IMGUI_DEMO_MARKER("Widgets/Text/Font Size")
            style = imgui.get_style()
            global_scale = style.font_scale_main * style.font_scale_dpi
            imgui.text(f"style.FontScaleMain = {style.font_scale_main:.2f}")
            imgui.text(f"style.FontScaleDpi = {style.font_scale_dpi:.2f}")
            imgui.text(f"global_scale = ~{global_scale:.2f}")
            imgui.text(f"FontSize = {imgui.get_font_size():.2f}")

            imgui.separator_text("")
            if not hasattr(static, "custom_size"): static.custom_size = 16.0
            _, static.custom_size = imgui.slider_float("custom_size", static.custom_size, 10.0, 100.0, "%.0f")
            imgui.text("imgui.push_font(None, custom_size)")
            imgui.push_font(None, static.custom_size)
            imgui.text(f"FontSize = {imgui.get_font_size():.2f} (== {static.custom_size:.2f} * global_scale)")
            imgui.pop_font()

            imgui.separator_text("")
            if not hasattr(static, "custom_scale"): static.custom_scale = 1.0
            _, static.custom_scale = imgui.slider_float("custom_scale", static.custom_scale, 0.5, 4.0, "%.2f")
            imgui.text("imgui.push_font(None, style.font_size_base * custom_scale)")
            imgui.push_font(None, style.font_size_base * static.custom_scale)
            imgui.text(f"FontSize = {imgui.get_font_size():.2f} (== style.FontSizeBase * {static.custom_scale:.2f} * global_scale)")
            imgui.pop_font()

            imgui.separator_text("")
            scaling = 0.5
            while scaling <= 4.0:
                imgui.push_font(None, style.font_size_base * scaling)
                imgui.text(f"FontSize = {imgui.get_font_size():.2f} (== style.FontSizeBase * {scaling:.2f} * global_scale)")
                imgui.pop_font()
                scaling += 0.5

            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Images"):
        IMGUI_DEMO_MARKER("Widgets/Images")
        io = imgui.get_io()
        imgui.text_wrapped(
            "Below we are displaying the font texture (which is the only texture we have access to in this demo). "
            "Use the 'ImTextureID' type as storage to pass pointers or identifier to your own texture data. "
            "Hover the texture for a zoomed view!")

        # -Below we are displaying the font texture because it is the only texture we have access to inside the demo!
        # -Remember that ImTextureID is just storage for whatever you want it to be. It is essentially a value that
        # -will be passed to the rendering backend via the ImDrawCmd structure.
        # -If you use one of the default imgui_impl_XXXX.cpp rendering backend, they all have comments at the top
        # -of their respective source file to specify what they expect to be stored in ImTextureID, for example:
        # -- The imgui_impl_dx11.cpp renderer expect a 'ID3D11ShaderResourceView*' pointer
        # -- The imgui_impl_opengl3.cpp renderer expect a GLuint OpenGL texture identifier, etc.
        # -More:
        # -- If you decided that ImTextureID = MyEngineTexture*, then you can pass your MyEngineTexture* pointers
        # -  to ImGui::Image(), and gather width/height through your own functions, etc.
        # -- You can use ShowMetricsWindow() to inspect the draw data that are being passed to your renderer,
        # -  it will help you debug issues if you are confused about it.
        # -- Consider using the lower-level ImDrawList::AddImage() API, via ImGui::GetWindowDrawList()->AddImage().
        # -- Read https://github.com/ocornut/imgui/blob/master/docs/FAQ.md
        # -- Read https://github.com/ocornut/imgui/wiki/Image-Loading-and-Displaying-Examples
        # Fetch the font texture ID and its size
        my_tex_id = imgui.ImTextureRef(io.fonts.python_get_texture_id())
        my_tex_w = float(io.fonts.tex_data.width)
        my_tex_h = float(io.fonts.tex_data.height)

        # Option to use text color for tinting the image
        if not hasattr(static, 'use_text_color_for_tint'):
            static.use_text_color_for_tint = False
        _, static.use_text_color_for_tint = imgui.checkbox("Use Text Color for Tint", static.use_text_color_for_tint)

        imgui.text(f"{my_tex_w:.0f}x{my_tex_h:.0f}")
        pos = imgui.get_cursor_screen_pos()
        uv_min = ImVec2(0.0, 0.0)  # Top-left
        uv_max = ImVec2(1.0, 1.0)  # Lower-right
        tint_col = imgui.get_style_color_vec4(imgui.Col_.text) if static.use_text_color_for_tint else (1.0, 1.0, 1.0, 1.0)
        border_col = imgui.get_style_color_vec4(imgui.Col_.border)

        imgui.image_with_bg(my_tex_id, ImVec2(my_tex_w, my_tex_h), uv_min, uv_max, tint_col, border_col)  # type: ignore
        if imgui.begin_item_tooltip():
            # Define the region for the zoomed tooltip
            region_sz = 32.0
            region_x = max(min(io.mouse_pos.x - pos.x - region_sz * 0.5, my_tex_w - region_sz), 0.0)
            region_y = max(min(io.mouse_pos.y - pos.y - region_sz * 0.5, my_tex_h - region_sz), 0.0)
            imgui.text(f"Min: ({region_x:.2f}, {region_y:.2f})")
            imgui.text(f"Max: ({region_x + region_sz:.2f}, {region_y + region_sz:.2f})")
            uv0 = ImVec2((region_x) / my_tex_w, (region_y) / my_tex_h)
            uv1 = ImVec2((region_x + region_sz) / my_tex_w, (region_y + region_sz) / my_tex_h)
            imgui.image_with_bg(my_tex_id, ImVec2(region_sz * 4.0, region_sz * 4.0), uv0, uv1, tint_col, border_col)  # type: ignore
            imgui.end_tooltip()

        # Textured buttons
        IMGUI_DEMO_MARKER("Widgets/Images/Textured buttons")
        imgui.text_wrapped("And now some textured buttons..")
        if not hasattr(static, 'pressed_count'):
            static.pressed_count = 0
        for i in range(8):
            imgui.push_id(i)
            if i > 0:
                imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(i - 1.0, i - 1.0))
            size = ImVec2(32.0, 32.0)
            uv0 = ImVec2(0.0, 0.0)
            uv1 = ImVec2(32.0 / my_tex_w, 32.0 / my_tex_h)
            bg_col = ImVec4(0.0, 0.0, 0.0, 1.0)  # Black background
            tint_col = ImVec4(1.0, 1.0, 1.0, 1.0)  # No tint
            if imgui.image_button("", my_tex_id, size, uv0, uv1, bg_col, tint_col):
                static.pressed_count += 1
            if i > 0:
                imgui.pop_style_var()
            imgui.pop_id()
            imgui.same_line()
        imgui.new_line()
        imgui.text(f"Pressed {static.pressed_count} times.")
        imgui.tree_pop()

    if imgui.tree_node("Combo"):
        IMGUI_DEMO_MARKER("Widgets/Combo")
        # Expose flags as checkboxes for the demo
        if not hasattr(static, 'flags'): static.flags = 0
        _, static.flags = imgui.checkbox_flags("ImGuiComboFlags_PopupAlignLeft", static.flags, imgui.ComboFlags_.popup_align_left)
        imgui.same_line(); help_marker("Only makes a difference if the popup is larger than the combo")
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_NoArrowButton", static.flags, imgui.ComboFlags_.no_arrow_button)
        if changed:
            static.flags &= ~imgui.ComboFlags_.no_preview  # Clear the other flag, as we cannot combine both
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_NoPreview", static.flags, imgui.ComboFlags_.no_preview)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.no_arrow_button | imgui.ComboFlags_.width_fit_preview)  # Clear the other flag, as we cannot combine both
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_WidthFitPreview", static.flags, imgui.ComboFlags_.width_fit_preview)
        if changed:
            static.flags &= ~imgui.ComboFlags_.no_preview

        # Override default popup height
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightSmall", static.flags, imgui.ComboFlags_.height_small)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_ & ~imgui.ComboFlags_.height_small)
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightRegular", static.flags, imgui.ComboFlags_.height_regular)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_ & ~imgui.ComboFlags_.height_regular)
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightLargest", static.flags, imgui.ComboFlags_.height_largest)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_ & ~imgui.ComboFlags_.height_largest)

        # Generic BeginCombo() API, displaying items with selectable behavior
        items = ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIII", "JJJJ", "KKKK", "LLLLLLL", "MMMM", "OOOOOOO"]
        if not hasattr(static, 'item_current_idx'): static.item_current_idx = 0
        combo_preview_value = items[static.item_current_idx]
        if imgui.begin_combo("combo 1", combo_preview_value, static.flags):
            for n in range(len(items)):
                is_selected = (static.item_current_idx == n)
                if imgui.selectable(items[n], is_selected):
                    static.item_current_idx = n
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        imgui.spacing()
        imgui.separator_text("One-liner variants")
        help_marker("Flags above don't apply to this section.")

        # Simplified Combo() API using a single constant string
        if not hasattr(static, 'item_current_2'): static.item_current_2 = 0
        _, static.item_current_2 = imgui.combo("combo 2 (one-liner)", static.item_current_2, "aaaa\0bbbb\0cccc\0dddd\0eeee\0\0")

        # Simplified Combo() using an array of const char*
        if not hasattr(static, 'item_current_3'): static.item_current_3 = -1
        _, static.item_current_3 = imgui.combo("combo 3 (array)", static.item_current_3, items, len(items))

        # Simplified Combo() using an accessor function: unavailable in python
        # if not hasattr(static, 'item_current_4'): static.item_current_4 = 0
        # _, static.item_current_4 = imgui.combo("combo 4 (function)", static.item_current_4, lambda data, n: (items[n]), items, len(items))

        imgui.tree_pop()

    if imgui.tree_node("List Boxes"):
        IMGUI_DEMO_MARKER("Widgets/List Boxes")
        # List of items for the list box
        items = ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIII", "JJJJ", "KKKK", "LLLLLLL", "MMMM", "OOOOOOO"]

        # Index of the currently selected item
        if not hasattr(static, 'item_current_idx'):
            static.item_current_idx = 0

        # Begin list box 1 and list its contents
        if imgui.begin_list_box("listbox 1"):
            for n, item in enumerate(items):
                # Determine if the current item is selected
                is_selected = (static.item_current_idx == n)
                if imgui.selectable(item, is_selected):
                    static.item_current_idx = n
                # Set the default focus to the selected item
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_list_box()

        # Text before the custom sized list box
        imgui.text("Full-width:")

        # Custom size list box: full width and 5 items tall
        full_width = -imgui.FLT_MIN
        item_height = imgui.get_text_line_height_with_spacing()
        if imgui.begin_list_box("##listbox 2", ImVec2(full_width, 5 * item_height)):
            for n, item in enumerate(items):
                # Determine if the current item is selected
                is_selected = (static.item_current_idx == n)
                if imgui.selectable(item, is_selected):
                    static.item_current_idx = n
                # Set the default focus to the selected item
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_list_box()

        imgui.tree_pop()

    if imgui.tree_node("Selectables"):
        IMGUI_DEMO_MARKER("Widgets/Selectables")
        # Basic example of Selectable widgets
        if imgui.tree_node("Basic"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Basic")
            if not hasattr(static, 'selection'): static.selection = [False, True, False, False]
            _, static.selection[0] = imgui.selectable("1. I am selectable", static.selection[0])
            _, static.selection[1] = imgui.selectable("2. I am selectable", static.selection[1])
            _, static.selection[2] = imgui.selectable("3. I am selectable", static.selection[2])
            if imgui.selectable("4. I am double clickable", static.selection[3], imgui.SelectableFlags_.allow_double_click):
                if imgui.is_mouse_double_clicked(0):
                    static.selection[3] = not static.selection[3]
            imgui.tree_pop()

        # Example of single selection using Selectable widgets
        if imgui.tree_node("Selection State: Single Selection"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Single Selection")
            if not hasattr(static, 'single_selected'): static.single_selected = -1
            for n in range(5):
                buf = f"Object {n}"
                _, clicked = imgui.selectable(buf, static.single_selected == n)
                if clicked:
                    static.single_selected = n
            imgui.tree_pop()

        # Example of multiple selection using Selectable widgets
        if imgui.tree_node("Selection State: Multiple Selection"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Multiple Selection")
            help_marker("Hold CTRL and click to select multiple items.")
            if not hasattr(static, 'multi_selection'): static.multi_selection = [False] * 5
            for n in range(5):
                buf = f"Object {n}"
                _, clicked = imgui.selectable(buf, static.multi_selection[n])
                if clicked:
                    if not imgui.get_io().key_ctrl:  # Clear selection when CTRL is not held
                        static.multi_selection = [False] * len(static.multi_selection)
                    static.multi_selection[n] = not static.multi_selection[n]
            imgui.tree_pop()

        # Example of rendering Selectable widgets next to other widgets
        IMGUI_DEMO_MARKER("Widgets/Selectables/Rendering more items on the same line")
        if imgui.tree_node("Multiple items on the same line"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Multiple items on the same line")
            # (1) Using SetNextItemAllowOverlap()
            if not hasattr(static, 'selectables_selected'): static.selectables_selected = [False, False, False]
            imgui.set_next_item_allow_overlap()
            _, static.selectables_selected[0] = imgui.selectable("main.c", static.selectables_selected[0])
            imgui.same_line()
            imgui.small_button("Link 1")

            imgui.set_next_item_allow_overlap()
            _, static.selectables_selected[1] = imgui.selectable("Hello.cpp", static.selectables_selected[1])
            imgui.same_line()
            imgui.small_button("Link 2")

            imgui.set_next_item_allow_overlap()
            _, static.selectables_selected[2] = imgui.selectable("Hello.h", static.selectables_selected[2])
            imgui.same_line()
            imgui.small_button("Link 3")

            # (2) Using ImGuiSelectableFlags_AllowOverlap
            imgui.spacing()
            if not hasattr(static, "sel_checked"): static.sel_checked = [False] * 5
            if not hasattr(static, "sel_selected_n"): static.sel_selected_n = 0
            color_marker_w = imgui.calc_text_size("x").x
            for n in range(5):
                imgui.push_id(n)
                imgui.align_text_to_frame_padding()
                if imgui.selectable("##selectable", static.sel_selected_n == n, imgui.SelectableFlags_.allow_overlap)[0]:
                    static.sel_selected_n = n
                imgui.same_line(0, 0)
                _, static.sel_checked[n] = imgui.checkbox("##check", static.sel_checked[n])
                imgui.same_line()
                color = ImVec4(1.0 if (n & 1) else 0.2, 1.0 if (n & 2) else 0.2, 0.2, 1.0)
                imgui.color_button("##color", color, imgui.ColorEditFlags_.no_tooltip, ImVec2(color_marker_w, 0))
                imgui.same_line()
                imgui.text("Some label")
                imgui.pop_id()

            imgui.tree_pop()

        # Example of Selectable widgets in columns
        if imgui.tree_node("In Tables"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/In Tables")
            if not hasattr(static, 'selected_in_columns'): static.selected_in_columns = [False] * 10

            if imgui.begin_table("split1", 3, imgui.TableFlags_.resizable | imgui.TableFlags_.no_saved_settings | imgui.TableFlags_.borders):
                for i in range(10):
                    label = f"Item {i}"
                    imgui.table_next_column()
                    _, static.selected_in_columns[i] = imgui.selectable(label, static.selected_in_columns[i])  # FIXME-TABLE: Selection overlap
                imgui.end_table()
            imgui.spacing()

            if imgui.begin_table("split2", 3, imgui.TableFlags_.resizable | imgui.TableFlags_.no_saved_settings | imgui.TableFlags_.borders):
                for i in range(10):
                    label = f"Item {i}"
                    imgui.table_next_row()
                    imgui.table_next_column()
                    _, static.selected_in_columns[i] = imgui.selectable(label, static.selected_in_columns[i], imgui.SelectableFlags_.span_all_columns)
                    imgui.table_next_column()
                    imgui.text("Some other contents")
                    imgui.table_next_column()
                    imgui.text("123456")
                imgui.end_table()
            imgui.tree_pop()

        # Example of a Selectable grid
        if imgui.tree_node("Grid"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Grid")
            if not hasattr(static, 'grid_selected'): static.grid_selected = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

            time = imgui.get_time()
            winning_state = all(val == 1 for row in static.grid_selected for val in row)  # Check if all cells are selected
            if winning_state:
                imgui.push_style_var(imgui.StyleVar_.selectable_text_align, ImVec2(0.5 + 0.5 * math.cos(time * 2), 0.5 + 0.5 * math.sin(time * 3)))

            for y in range(4):
                for x in range(4):
                    if x > 0:
                        imgui.same_line()
                    imgui.push_id(y * 4 + x)
                    if imgui.selectable("Sailor", static.grid_selected[y][x] == 1, 0, ImVec2(50, 50)):
                        # Toggle the clicked cell and its neighbors
                        static.grid_selected[y][x] ^= 1
                        if x > 0: static.grid_selected[y][x - 1] ^= 1
                        if x < 3: static.grid_selected[y][x + 1] ^= 1
                        if y > 0: static.grid_selected[y - 1][x] ^= 1
                        if y < 3: static.grid_selected[y + 1][x] ^= 1
                    imgui.pop_id()

            if winning_state:
                imgui.pop_style_var()
            imgui.tree_pop()

        # Example of Selectable alignment
        if imgui.tree_node("Alignment"):
            IMGUI_DEMO_MARKER("Widgets/Selectables/Alignment")
            help_marker("By default, Selectables use style.SelectableTextAlign but it can be overridden on a per-item basis using PushStyleVar().")
            if not hasattr(static, 'selectable_alignment'): static.selectable_alignment = [True, False, True, False, True, False, True, False, True]
            for y in range(3):
                for x in range(3):
                    alignment = ImVec2(float(x) / 2.0, float(y) / 2.0)
                    name = f"({alignment[0]:.1f},{alignment[1]:.1f})"
                    if x > 0: imgui.same_line()
                    imgui.push_style_var(imgui.StyleVar_.selectable_text_align, alignment)
                    _, static.selectable_alignment[3 * y + x] = imgui.selectable(name, static.selectable_alignment[3 * y + x], imgui.SelectableFlags_.none, ImVec2(80, 80))
                    imgui.pop_style_var()
            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Selection State & Multi-Select"):
        IMGUI_DEMO_MARKER("Widgets/Selection State & Multi-Select")
        help_marker("Selections can be built using Selectable(), TreeNode() or other widgets. Selection state is owned by application code/data.")

        imgui.bullet_text("Wiki page:")
        imgui.same_line()
        imgui.text_link_open_url("imgui/wiki/Multi-Select", "https://github.com/ocornut/imgui/wiki/Multi-Select")

        EXAMPLE_NAMES = [
            "Artichoke", "Arugula", "Asparagus", "Avocado", "Bamboo Shoots", "Bean Sprouts", "Beans", "Beet",
            "Belgian Endive", "Bell Pepper", "Bitter Gourd", "Bok Choy", "Broccoli", "Brussels Sprouts",
            "Burdock Root", "Cabbage", "Calabash", "Capers", "Carrot", "Cassava",
            "Cauliflower", "Celery", "Celery Root", "Celcuce", "Chayote", "Chinese Broccoli", "Corn", "Cucumber",
        ]

        # Without any fancy API: manage single-selection yourself.
        if imgui.tree_node("Single-Select"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Single-Select")
            if not hasattr(static, "ss_selected"): static.ss_selected = -1
            for n in range(5):
                buf = f"Object {n}"
                if imgui.selectable(buf, static.ss_selected == n)[0]:
                    static.ss_selected = n
            imgui.tree_pop()

        # Demonstrate implementation a most-basic form of multi-selection manually
        # This doesn't support the Shift modifier which requires BeginMultiSelect()!
        if imgui.tree_node("Multi-Select (manual/simplified, without BeginMultiSelect)"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select (manual/simplified, without BeginMultiSelect)")
            help_marker("Hold Ctrl and Click to select multiple items.")
            if not hasattr(static, "ms_manual_sel"): static.ms_manual_sel = [False] * 5
            for n in range(5):
                buf = f"Object {n}"
                if imgui.selectable(buf, static.ms_manual_sel[n])[0]:
                    if not imgui.get_io().key_ctrl:  # Clear selection when Ctrl is not held
                        static.ms_manual_sel = [False] * 5
                    static.ms_manual_sel[n] = not static.ms_manual_sel[n]  # Toggle current item
            imgui.tree_pop()

        # Demonstrate handling proper multi-selection using the BeginMultiSelect/EndMultiSelect API.
        if imgui.tree_node("Multi-Select"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select")
            imgui.text("Supported features:")
            imgui.bullet_text("Keyboard navigation (arrows, page up/down, home/end, space).")
            imgui.bullet_text("Ctrl modifier to preserve and toggle selection.")
            imgui.bullet_text("Shift modifier for range selection.")
            imgui.bullet_text("Ctrl+A to select all.")
            imgui.bullet_text("Escape to clear selection.")
            imgui.bullet_text("Click and drag to box-select.")
            imgui.text("Tip: Use 'Demo->Tools->Debug Log->Selection' to see selection requests as they happen.")

            # Use default selection.Adapter: Pass index to SetNextItemSelectionUserData(), store index in Selection
            ITEMS_COUNT = 50
            if not hasattr(static, "ms_selection"): static.ms_selection = imgui.SelectionBasicStorage()
            selection = static.ms_selection
            imgui.text(f"Selection: {selection.size}/{ITEMS_COUNT}")

            # The BeginChild() has no purpose for selection logic, other that offering a scrolling region.
            if imgui.begin_child("##Basket", ImVec2(-imgui.FLT_MIN, imgui.get_font_size() * 20), imgui.ChildFlags_.frame_style | imgui.ChildFlags_.resize_y):
                flags = imgui.MultiSelectFlags_.clear_on_escape | imgui.MultiSelectFlags_.box_select1d
                ms_io = imgui.begin_multi_select(flags, selection.size, ITEMS_COUNT)
                selection.apply_requests(ms_io)

                for n in range(ITEMS_COUNT):
                    label = f"Object {n:05d}: {EXAMPLE_NAMES[n % len(EXAMPLE_NAMES)]}"
                    item_is_selected = selection.contains(n)
                    imgui.set_next_item_selection_user_data(n)
                    imgui.selectable(label, item_is_selected)

                ms_io = imgui.end_multi_select()
                selection.apply_requests(ms_io)
            imgui.end_child()
            imgui.tree_pop()

        # Demonstrate using the clipper with BeginMultiSelect()/EndMultiSelect()
        if imgui.tree_node("Multi-Select (with clipper)"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select (with clipper)")
            # Use default selection.Adapter: Pass index to SetNextItemSelectionUserData(), store index in Selection
            if not hasattr(static, "ms_clipper_sel"): static.ms_clipper_sel = imgui.SelectionBasicStorage()
            selection = static.ms_clipper_sel

            imgui.text("Added features:")
            imgui.bullet_text("Using ImGuiListClipper.")

            ITEMS_COUNT = 10000
            imgui.text(f"Selection: {selection.size}/{ITEMS_COUNT}")
            if imgui.begin_child("##Basket", ImVec2(-imgui.FLT_MIN, imgui.get_font_size() * 20), imgui.ChildFlags_.frame_style | imgui.ChildFlags_.resize_y):
                flags = imgui.MultiSelectFlags_.clear_on_escape | imgui.MultiSelectFlags_.box_select1d
                ms_io = imgui.begin_multi_select(flags, selection.size, ITEMS_COUNT)
                selection.apply_requests(ms_io)

                clipper = imgui.ListClipper()
                clipper.begin(ITEMS_COUNT)
                if ms_io.range_src_item != -1:
                    clipper.include_item_by_index(int(ms_io.range_src_item))  # Ensure RangeSrc item is not clipped.
                while clipper.step():
                    for n in range(clipper.display_start, clipper.display_end):
                        label = f"Object {n:05d}: {EXAMPLE_NAMES[n % len(EXAMPLE_NAMES)]}"
                        item_is_selected = selection.contains(n)
                        imgui.set_next_item_selection_user_data(n)
                        imgui.selectable(label, item_is_selected)

                ms_io = imgui.end_multi_select()
                selection.apply_requests(ms_io)
            imgui.end_child()
            imgui.tree_pop()

        # Demonstrate using the clipper with BeginMultiSelect()/EndMultiSelect() in a table
        if imgui.tree_node("Multi-Select (in a table)"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select (in a table)")
            if not hasattr(static, "ms_table_sel"): static.ms_table_sel = imgui.SelectionBasicStorage()
            selection = static.ms_table_sel

            ITEMS_COUNT = 10000
            imgui.text(f"Selection: {selection.size}/{ITEMS_COUNT}")
            if imgui.begin_table("##Basket", 2, imgui.TableFlags_.scroll_y | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_outer, ImVec2(0.0, imgui.get_font_size() * 20)):
                imgui.table_setup_column("Object")
                imgui.table_setup_column("Action")
                imgui.table_setup_scroll_freeze(0, 1)
                imgui.table_headers_row()

                flags = imgui.MultiSelectFlags_.clear_on_escape | imgui.MultiSelectFlags_.box_select1d
                ms_io = imgui.begin_multi_select(flags, selection.size, ITEMS_COUNT)
                selection.apply_requests(ms_io)

                clipper = imgui.ListClipper()
                clipper.begin(ITEMS_COUNT)
                if ms_io.range_src_item != -1:
                    clipper.include_item_by_index(int(ms_io.range_src_item))  # Ensure RangeSrc item is not clipped.
                while clipper.step():
                    for n in range(clipper.display_start, clipper.display_end):
                        imgui.table_next_row()
                        imgui.table_next_column()
                        imgui.push_id(n)
                        label = f"Object {n:05d}: {EXAMPLE_NAMES[n % len(EXAMPLE_NAMES)]}"
                        item_is_selected = selection.contains(n)
                        imgui.set_next_item_selection_user_data(n)
                        imgui.selectable(label, item_is_selected, imgui.SelectableFlags_.span_all_columns | imgui.SelectableFlags_.allow_overlap)
                        imgui.table_next_column()
                        imgui.small_button("hello")
                        imgui.pop_id()

                ms_io = imgui.end_multi_select()
                selection.apply_requests(ms_io)
                imgui.end_table()
            imgui.tree_pop()

        if imgui.tree_node("Multi-Select (checkboxes)"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select (checkboxes)")
            imgui.text("In a list of checkboxes (not selectable):")
            imgui.bullet_text("Using _NoAutoSelect + _NoAutoClear flags.")
            imgui.bullet_text("Shift+Click to check multiple boxes.")
            imgui.bullet_text("Shift+Keyboard to copy current value to other boxes.")

            if not hasattr(static, "ms_cb_items"): static.ms_cb_items = [False] * 20
            if not hasattr(static, "ms_cb_flags"): static.ms_cb_flags = int(imgui.MultiSelectFlags_.no_auto_select | imgui.MultiSelectFlags_.no_auto_clear | imgui.MultiSelectFlags_.clear_on_escape)
            _, static.ms_cb_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_NoAutoSelect", static.ms_cb_flags, imgui.MultiSelectFlags_.no_auto_select)
            _, static.ms_cb_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_NoAutoClear", static.ms_cb_flags, imgui.MultiSelectFlags_.no_auto_clear)
            _, static.ms_cb_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_BoxSelect2d", static.ms_cb_flags, imgui.MultiSelectFlags_.box_select2d)

            if imgui.begin_child("##Basket", ImVec2(-imgui.FLT_MIN, imgui.get_font_size() * 20), imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_y):
                ms_io = imgui.begin_multi_select(imgui.MultiSelectFlags_(static.ms_cb_flags), -1, 20)
                # Manually apply requests (SelectionExternalStorage.AdapterSetItemSelected not exposed in Python)
                for req in ms_io.requests:
                    if req.type == imgui.SelectionRequestType.set_all:
                        for i in range(20):
                            static.ms_cb_items[i] = req.selected
                    elif req.type == imgui.SelectionRequestType.set_range:
                        first = int(req.range_first_item)
                        last = int(req.range_last_item)
                        lo, hi = min(first, last), max(first, last)
                        for i in range(lo, hi + 1):
                            static.ms_cb_items[i] = req.selected
                for n in range(20):
                    label = f"Item {n}"
                    imgui.set_next_item_selection_user_data(n)
                    _, static.ms_cb_items[n] = imgui.checkbox(label, static.ms_cb_items[n])
                ms_io = imgui.end_multi_select()
                for req in ms_io.requests:
                    if req.type == imgui.SelectionRequestType.set_all:
                        for i in range(20):
                            static.ms_cb_items[i] = req.selected
                    elif req.type == imgui.SelectionRequestType.set_range:
                        first = int(req.range_first_item)
                        last = int(req.range_last_item)
                        lo, hi = min(first, last), max(first, last)
                        for i in range(lo, hi + 1):
                            static.ms_cb_items[i] = req.selected
            imgui.end_child()

            imgui.tree_pop()

        # Demonstrate individual selection scopes in same window
        if imgui.tree_node("Multi-Select (multiple scopes)"):
            IMGUI_DEMO_MARKER("Widgets/Selection State/Multi-Select (multiple scopes)")
            SCOPES_COUNT = 3
            ITEMS_COUNT_SCOPE = 8  # Per scope
            if not hasattr(static, "ms_scope_sels"): static.ms_scope_sels = [imgui.SelectionBasicStorage() for _ in range(SCOPES_COUNT)]
            if not hasattr(static, "ms_scope_flags"): static.ms_scope_flags = int(imgui.MultiSelectFlags_.scope_rect | imgui.MultiSelectFlags_.clear_on_escape)

            # Use ImGuiMultiSelectFlags_ScopeRect to not affect other selections in same window.
            changed, static.ms_scope_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_ScopeWindow", static.ms_scope_flags, imgui.MultiSelectFlags_.scope_window)
            if changed and (static.ms_scope_flags & int(imgui.MultiSelectFlags_.scope_window)):
                static.ms_scope_flags &= ~int(imgui.MultiSelectFlags_.scope_rect)
            changed, static.ms_scope_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_ScopeRect", static.ms_scope_flags, imgui.MultiSelectFlags_.scope_rect)
            if changed and (static.ms_scope_flags & int(imgui.MultiSelectFlags_.scope_rect)):
                static.ms_scope_flags &= ~int(imgui.MultiSelectFlags_.scope_window)
            _, static.ms_scope_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_ClearOnClickVoid", static.ms_scope_flags, imgui.MultiSelectFlags_.clear_on_click_void)
            _, static.ms_scope_flags = imgui.checkbox_flags("ImGuiMultiSelectFlags_BoxSelect1d", static.ms_scope_flags, imgui.MultiSelectFlags_.box_select1d)

            for selection_scope_n in range(SCOPES_COUNT):
                imgui.push_id(selection_scope_n)
                selection = static.ms_scope_sels[selection_scope_n]
                ms_io = imgui.begin_multi_select(imgui.MultiSelectFlags_(static.ms_scope_flags), selection.size, ITEMS_COUNT_SCOPE)
                selection.apply_requests(ms_io)

                imgui.separator_text("Selection scope")
                imgui.text(f"Selection size: {selection.size}/{ITEMS_COUNT_SCOPE}")

                for n in range(ITEMS_COUNT_SCOPE):
                    label = f"Object {n:05d}: {EXAMPLE_NAMES[n % len(EXAMPLE_NAMES)]}"
                    item_is_selected = selection.contains(n)
                    imgui.set_next_item_selection_user_data(n)
                    imgui.selectable(label, item_is_selected)

                # Apply multi-select requests
                ms_io = imgui.end_multi_select()
                selection.apply_requests(ms_io)
                imgui.pop_id()
            imgui.tree_pop()

        imgui.tree_pop()

    # We are using a fixed-sized buffer for simplicity here.
    # See imgui.INPUT_TEXT_FLAGS_CALLBACK_RESIZE and the code in misc/cpp/imgui_stdlib.h
    # for how to set up InputText() for dynamically resizing strings.
    if imgui.tree_node("Text Input"):
        IMGUI_DEMO_MARKER("Widgets/Text Input")
        if imgui.tree_node("Multi-line Text Input"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Multi-line Text Input")
            # In Python, we don't need to define the size of the buffer upfront.
            # We initialize a string with enough space and let Python handle the memory.
            if not hasattr(static, 'text_input_text'):
                static.text_input_text = (
                    "/*\n"
                    " The Pentium F00F bug, shorthand for F0 0F C7 C8,\n"
                    " the hexadecimal encoding of one offending instruction,\n"
                    " more formally, the invalid operand with locked CMPXCHG8B\n"
                    " instruction bug, is a design flaw in the majority of\n"
                    " Intel Pentium, Pentium MMX, and Pentium OverDrive\n"
                    " processors (all in the P5 microarchitecture).\n"
                    "*/\n\n"
                    "label:\n"
                    "\tlock cmpxchg8b eax\n"
                )

            # The flags are used to configure the behavior of the InputText widget.
            # In Python, we can directly use the flags provided by the imgui library.
            if not hasattr(static, 'text_input_flags'):
                static.text_input_flags = imgui.InputTextFlags_.allow_tab_input
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_ReadOnly", static.text_input_flags, imgui.InputTextFlags_.read_only)
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_AllowTabInput", static.text_input_flags, imgui.InputTextFlags_.allow_tab_input)
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_CtrlEnterForNewLine", static.text_input_flags, imgui.InputTextFlags_.ctrl_enter_for_new_line)

            # Use InputTextMultiline for a multi-line resizable input box.
            changed, static.text_input_text = imgui.input_text_multiline("##source", static.text_input_text, ImVec2(-1, imgui.get_text_line_height() * 16), static.text_input_flags)
            imgui.tree_pop()

        if imgui.tree_node("Filtered Text Input"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Filtered Text Input")
            # class TextFilters:
            #     @staticmethod
            #     def filter_casing_swap(data):
            #         if 'a' <= data.EventChar <= 'z':
            #             data.EventChar = chr(ord(data.EventChar) - ord('a') + ord('A'))  # Lowercase becomes uppercase
            #         elif 'A' <= data.EventChar <= 'Z':
            #             data.EventChar = chr(ord(data.EventChar) + ord('a') - ord('A'))  # Uppercase becomes lowercase
            #         return 0
            #
            #     @staticmethod
            #     def filter_imgui_letters(data):
            #         if 0 <= ord(data.EventChar) < 256 and chr(ord(data.EventChar)) in "imgui":
            #             return 0
            #         return 1

            if not hasattr(static, "filtered_text_input_buf1"):
                static.filtered_text_input_buf1 = ""
            _, static.filtered_text_input_buf1 = imgui.input_text("default", static.filtered_text_input_buf1)

            if not hasattr(static, "filtered_text_input_buf2"):
                static.filtered_text_input_buf2 = ""
            _, static.filtered_text_input_buf2 = imgui.input_text("decimal", static.filtered_text_input_buf2, flags=imgui.InputTextFlags_.chars_decimal)

            if not hasattr(static, "filtered_text_input_buf3"):
                static.filtered_text_input_buf3 = ""
            _, static.filtered_text_input_buf3 = imgui.input_text("hexadecimal", static.filtered_text_input_buf3, flags=imgui.InputTextFlags_.chars_hexadecimal | imgui.InputTextFlags_.chars_uppercase)

            if not hasattr(static, "filtered_text_input_buf4"):
                static.filtered_text_input_buf4 = ""
            _, static.filtered_text_input_buf4 = imgui.input_text("uppercase", static.filtered_text_input_buf4, flags=imgui.InputTextFlags_.chars_uppercase)

            if not hasattr(static, "filtered_text_input_buf5"):
                static.filtered_text_input_buf5 = ""
            _, static.filtered_text_input_buf5 = imgui.input_text("no blank", static.filtered_text_input_buf5, flags=imgui.InputTextFlags_.chars_no_blank)

            # if "filtered_text_input_buf6" not in static:
            #     static.filtered_text_input_buf6 = ""
            # _, static.filtered_text_input_buf6 = imgui.input_text("casing swap", static.filtered_text_input_buf6, flags=imgui.InputTextFlags_.callback_char_filter, callback=TextFilters.filter_casing_swap)
            #
            # if "filtered_text_input_buf7" not in static:
            #     static.filtered_text_input_buf7 = ""
            # _, static.filtered_text_input_buf7 = imgui.input_text("\"imgui\"", static.filtered_text_input_buf7, flags=imgui.InputTextFlags_.callback_char_filter, callback=TextFilters.filter_imgui_letters)

            imgui.tree_pop()

        if imgui.tree_node("Password Input"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Password input")
            if not hasattr(static, "password"):
                static.password = "password123"

            _, static.password = imgui.input_text("password", static.password, imgui.InputTextFlags_.password)
            imgui.same_line(); help_marker("Display all characters as '*'.\nDisable clipboard cut and copy.\nDisable logging.")
            _, static.password = imgui.input_text_with_hint("password (w/ hint)", "<password>", static.password, imgui.InputTextFlags_.password)
            _, static.password = imgui.input_text("password (clear)", static.password)
            imgui.tree_pop()

        if imgui.tree_node("Completion, History, Edit Callbacks"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Completion, History, Edit Callbacks")

            if not hasattr(static, "cb_edit_count"): static.cb_edit_count = 0

            def my_callback(data: imgui.InputTextCallbackData) -> int:
                if data.event_flag == imgui.InputTextFlags_.callback_completion:
                    data.insert_chars(data.cursor_pos, "..")
                elif data.event_flag == imgui.InputTextFlags_.callback_history:
                    if data.event_key == imgui.Key.up_arrow:
                        data.delete_chars(0, data.buf_text_len)
                        data.insert_chars(0, "Pressed Up!")
                        data.select_all()
                    elif data.event_key == imgui.Key.down_arrow:
                        data.delete_chars(0, data.buf_text_len)
                        data.insert_chars(0, "Pressed Down!")
                        data.select_all()
                elif data.event_flag == imgui.InputTextFlags_.callback_edit:
                    # Toggle casing of first character
                    if data.buf_text_len > 0:
                        c = data.buf[0]
                        if c.isalpha():
                            # Toggle case by swapping
                            new_c = c.swapcase()
                            data.delete_chars(0, 1)
                            data.insert_chars(0, new_c)
                            data.cursor_pos = max(data.cursor_pos, 1)  # Restore cursor
                    static.cb_edit_count += 1
                return 0

            if not hasattr(static, "cb_buf1"): static.cb_buf1 = ""
            _, static.cb_buf1 = imgui.input_text("Completion", static.cb_buf1, imgui.InputTextFlags_.callback_completion, my_callback)
            imgui.same_line(); help_marker(
                "Here we append \"..\" each time Tab is pressed. "
                "See 'Examples>Console' for a more meaningful demonstration of using this callback.")

            if not hasattr(static, "cb_buf2"): static.cb_buf2 = ""
            _, static.cb_buf2 = imgui.input_text("History", static.cb_buf2, imgui.InputTextFlags_.callback_history, my_callback)
            imgui.same_line(); help_marker(
                "Here we replace and select text each time Up/Down are pressed. "
                "See 'Examples>Console' for a more meaningful demonstration of using this callback.")

            if not hasattr(static, "cb_buf3"): static.cb_buf3 = ""
            _, static.cb_buf3 = imgui.input_text("Edit", static.cb_buf3, imgui.InputTextFlags_.callback_edit, my_callback)
            imgui.same_line(); help_marker(
                "Here we toggle the casing of the first character on every edit + count edits.")
            imgui.same_line(); imgui.text(f"({static.cb_edit_count})")

            imgui.tree_pop()

        if imgui.tree_node("Resize Callback"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Resize Callback")
            # In Python, strings are immutable and InputText handles resizing automatically.
            # This section demonstrates that InputTextMultiline works with dynamic strings.
            help_marker(
                "In C++, using ImGuiInputTextFlags_CallbackResize to wire custom string types to InputText().\n"
                "In Python, strings are handled automatically - no resize callback needed.")

            if not hasattr(static, "resize_flags"): static.resize_flags = imgui.InputTextFlags_.none
            _, static.resize_flags = imgui.checkbox_flags("ImGuiInputTextFlags_WordWrap", static.resize_flags, imgui.InputTextFlags_.word_wrap)

            if not hasattr(static, "resize_str"): static.resize_str = ""
            _, static.resize_str = imgui.input_text_multiline("##MyStr", static.resize_str, ImVec2(-1, imgui.get_text_line_height() * 16), static.resize_flags)
            imgui.text(f"Size: {len(static.resize_str)}")
            imgui.tree_pop()

        if imgui.tree_node("Eliding, Alignment"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Eliding, Alignment")
            if not hasattr(static, "elide_buf"): static.elide_buf = "/path/to/some/folder/with/long/filename.cpp"
            if not hasattr(static, "elide_flags"): static.elide_flags = imgui.InputTextFlags_.elide_left
            _, static.elide_flags = imgui.checkbox_flags("ImGuiInputTextFlags_ElideLeft", static.elide_flags, imgui.InputTextFlags_.elide_left)
            _, static.elide_buf = imgui.input_text("Path", static.elide_buf, static.elide_flags)
            imgui.tree_pop()

        if imgui.tree_node("Miscellaneous"):
            IMGUI_DEMO_MARKER("Widgets/Text Input/Miscellaneous")
            if not hasattr(static, "misc_buf1"): static.misc_buf1 = ""
            if not hasattr(static, "misc_flags"): static.misc_flags = imgui.InputTextFlags_.escape_clears_all
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_EscapeClearsAll", static.misc_flags, imgui.InputTextFlags_.escape_clears_all)
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_ReadOnly", static.misc_flags, imgui.InputTextFlags_.read_only)
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_NoUndoRedo", static.misc_flags, imgui.InputTextFlags_.no_undo_redo)
            _, static.misc_buf1 = imgui.input_text("Hello", static.misc_buf1, flags=static.misc_flags)
            imgui.tree_pop()

        imgui.tree_pop()

    # Tabs
    #
    # Note: the signature of begin_tab_item is:
    #     def begin_tab_item(
    #             label: str, p_open: Optional[bool] = None, flags: TabItemFlags = 0
    #     ) -> Tuple[bool, Optional[bool]]:
    #
    # The returned tuple contains [is_visible, p_open]
    # So, to test if a tab_item should be displayed we need to test
    #      imgui.begin_tab_item("Avocado")[0]
    #
    if imgui.tree_node("Tabs"):
        IMGUI_DEMO_MARKER("Widgets/Tabs")
        if imgui.tree_node("Basic"):
            IMGUI_DEMO_MARKER("Widgets/Tabs/Basic")
            tab_bar_flags = imgui.TabBarFlags_.none
            if imgui.begin_tab_bar("MyTabBar", tab_bar_flags):
                if imgui.begin_tab_item("Avocado")[0]:
                    imgui.text("This is the Avocado tab!\nblah blah blah blah blah")
                    imgui.end_tab_item()
                if imgui.begin_tab_item("Broccoli")[0]:
                    imgui.text("This is the Broccoli tab!\nblah blah blah blah blah")
                    imgui.end_tab_item()
                if imgui.begin_tab_item("Cucumber")[0]:
                    imgui.text("This is the Cucumber tab!\nblah blah blah blah blah")
                    imgui.end_tab_item()
                imgui.end_tab_bar()
            imgui.separator()
            imgui.tree_pop()

        if imgui.tree_node("Advanced & Close Button"):
            IMGUI_DEMO_MARKER("Widgets/Tabs/Advanced & Close Button")
            # Expose a couple of the available flags. In most cases, you may just call begin_tab_bar() with no flags (0).
            if not hasattr(static, "adv_tab_bar_flags"):
                static.adv_tab_bar_flags = imgui.TabBarFlags_.reorderable
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_Reorderable", static.adv_tab_bar_flags, imgui.TabBarFlags_.reorderable)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_AutoSelectNewTabs", static.adv_tab_bar_flags, imgui.TabBarFlags_.auto_select_new_tabs)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_TabListPopupButton", static.adv_tab_bar_flags, imgui.TabBarFlags_.tab_list_popup_button)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_NoCloseWithMiddleMouseButton", static.adv_tab_bar_flags, imgui.TabBarFlags_.no_close_with_middle_mouse_button)
            if (static.adv_tab_bar_flags & imgui.TabBarFlags_.fitting_policy_mask_) == 0:
                static.adv_tab_bar_flags |= imgui.TabBarFlags_.fitting_policy_default_
            if imgui.checkbox_flags("ImGuiTabBarFlags_DrawSelectedOverline", static.adv_tab_bar_flags, imgui.TabBarFlags_.draw_selected_overline):
                static.adv_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_ ^ imgui.TabBarFlags_.draw_selected_overline)

            # Tab Bar
            names = ["Artichoke", "Beetroot", "Celery", "Daikon"]
            if not hasattr(static, "opened"):
                static.opened = [True, True, True, True]  # Persistent user state
            for n in range(len(static.opened)):
                if n > 0:
                    imgui.same_line()
                _, static.opened[n] = imgui.checkbox(names[n], static.opened[n])

            # Passing a bool* to begin_tab_item() is similar to passing one to begin():
            # the underlying bool will be set to False when the tab is closed.
            if imgui.begin_tab_bar("MyTabBar", static.adv_tab_bar_flags):
                for n in range(len(static.opened)):
                    if static.opened[n] and imgui.begin_tab_item(names[n], static.opened[n], imgui.TabItemFlags_.none)[0]:
                        imgui.text("This is the %s tab!" % names[n])
                        if n & 1:
                            imgui.text("I am an odd tab.")
                        imgui.end_tab_item()
                imgui.end_tab_bar()
            imgui.separator()
            imgui.tree_pop()

        if imgui.tree_node("TabItemButton & Leading/Trailing flags"):
            IMGUI_DEMO_MARKER("Widgets/Tabs/TabItemButton & Leading-Trailing flags")
            if not hasattr(static, "active_tabs"):
                static.active_tabs = []
            if not hasattr(static, "next_tab_id"):
                static.next_tab_id = 0
            if static.next_tab_id == 0:  # Initialize with some default tabs
                for _ in range(3):
                    static.active_tabs.append(static.next_tab_id)
                    static.next_tab_id += 1

            # TabItemButton() and Leading/Trailing flags are distinct features which we will demo together.
            # (It is possible to submit regular tabs with Leading/Trailing flags, or TabItemButton tabs without Leading/Trailing flags...
            # but they tend to make more sense together)
            if not hasattr(static, "show_leading_button"):
                static.show_leading_button = True
            if not hasattr(static, "show_trailing_button"):
                static.show_trailing_button = True
            _, static.show_leading_button = imgui.checkbox("Show Leading TabItemButton()", static.show_leading_button)
            _, static.show_trailing_button = imgui.checkbox("Show Trailing TabItemButton()", static.show_trailing_button)

            # Expose some other flags which are useful to showcase how they interact with Leading/Trailing tabs
            if not hasattr(static, "lead_trail_tab_bar_flags"):
                static.lead_trail_tab_bar_flags = (
                        imgui.TabBarFlags_.auto_select_new_tabs
                        | imgui.TabBarFlags_.reorderable
                        | imgui.TabBarFlags_.fitting_policy_shrink
                )
            _, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("tab_list_popup_button", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.tab_list_popup_button)
            changed, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("fitting_policy_shrink", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_shrink)
            if changed:
                static.lead_trail_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_ ^ imgui.TabBarFlags_.fitting_policy_shrink)
            changed, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_FittingPolicyScroll", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_scroll)
            if changed:
                static.lead_trail_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_ ^ imgui.TabBarFlags_.fitting_policy_scroll)  # type: ignore

            if imgui.begin_tab_bar("MyTabBar", static.lead_trail_tab_bar_flags):
                # Demo a Leading TabItemButton(): click the "?" button to open a menu
                if static.show_leading_button:
                    if imgui.tab_item_button("?", imgui.TabItemFlags_.leading | imgui.TabItemFlags_.no_tooltip):
                        imgui.open_popup("MyHelpMenu")
                if imgui.begin_popup("MyHelpMenu"):
                    imgui.selectable("Hello!", False)
                    imgui.end_popup()

                # Demo Trailing Tabs: click the "+" button to add a new tab (in your app you may want to use a font icon instead of the "+")
                # Note that we submit it before the regular tabs, but because of the ImGuiTabItemFlags_Trailing flag it will always appear at the end.
                if static.show_trailing_button:
                    if imgui.tab_item_button("+", imgui.TabItemFlags_.trailing | imgui.TabItemFlags_.no_tooltip):
                        static.active_tabs.append(static.next_tab_id)  # Add new tab
                        static.next_tab_id += 1

                # Submit our regular tabs
                n = 0
                while n < len(static.active_tabs):
                    open = True
                    name = "%04d" % static.active_tabs[n]
                    if imgui.begin_tab_item(name, open, imgui.TabItemFlags_.none)[0]:
                        imgui.text("This is the %s tab!" % name)
                        imgui.end_tab_item()

                    if not open:
                        del static.active_tabs[n]
                    else:
                        n += 1

                imgui.end_tab_bar()
            imgui.separator()
            imgui.tree_pop()
        imgui.tree_pop()

    if imgui.tree_node("Color/Picker Widgets"):
        IMGUI_DEMO_MARKER("Widgets/Color")
        if not hasattr(static, "color"):
            static.color = ImVec4(114.0 / 255.0, 144.0 / 255.0, 154.0 / 255.0, 200.0 / 255.0)
        if not hasattr(static, "color3"):
            static.color3 = ImVec4(114.0 / 255.0, 144.0 / 255.0, 154.0 / 255.0, 1.0) # last component is ignored

        if not hasattr(static, "alpha_preview"):
            static.alpha_preview = True
        if not hasattr(static, "alpha_half_preview"):
            static.alpha_half_preview = False
        if not hasattr(static, "drag_and_drop"):
            static.drag_and_drop = True
        if not hasattr(static, "options_menu"):
            static.options_menu = True
        if not hasattr(static, "hdr"):
            static.hdr = False

        imgui.separator_text("Options")
        _, static.alpha_preview = imgui.checkbox("With Alpha Preview", static.alpha_preview)
        _, static.alpha_half_preview = imgui.checkbox("With Half Alpha Preview", static.alpha_half_preview)
        _, static.drag_and_drop = imgui.checkbox("With Drag and Drop", static.drag_and_drop)
        _, static.options_menu = imgui.checkbox("With Options Menu", static.options_menu)
        imgui.same_line()
        help_marker("Right-click on the individual color widget to show options.")
        _, static.hdr = imgui.checkbox("With HDR", static.hdr)
        imgui.same_line()
        help_marker("Currently all this does is to lift the 0..1 limits on dragging widgets.")
        misc_flags = (imgui.ColorEditFlags_.hdr if static.hdr else 0) | (0 if static.drag_and_drop else imgui.ColorEditFlags_.no_drag_drop) | (
            imgui.ColorEditFlags_.alpha_preview_half if static.alpha_half_preview else 0) | (
                         0 if static.options_menu else imgui.ColorEditFlags_.no_options)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorEdit")
        imgui.separator_text("Inline color editor")
        imgui.text("Color widget:")
        imgui.same_line()
        help_marker(
            "Click on the color square to open a color picker.\n"
            "CTRL+click on individual component to input value.\n")
        _, static.color3 = imgui.color_edit3("MyColor##1", static.color3, misc_flags)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorEdit (HSV, with Alpha)")
        imgui.text("Color widget HSV with Alpha:")
        _, static.color = imgui.color_edit4("MyColor##2", static.color, flags=imgui.ColorEditFlags_.display_hsv | misc_flags)  # type: ignore

        IMGUI_DEMO_MARKER("Widgets/Color/ColorEdit (float display)")
        imgui.text("Color widget with Float Display:")
        _, static.color = imgui.color_edit4("MyColor##2f", static.color, flags=imgui.ColorEditFlags_.float | misc_flags)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorButton (with Picker)")
        imgui.text("Color button with Picker:")
        imgui.same_line()
        help_marker(
            "With the ImGuiColorEditFlags_NoInputs flag you can hide all the slider/text inputs.\n"
            "With the ImGuiColorEditFlags_NoLabel flag you can pass a non-empty label which will only "
            "be used for the tooltip and picker popup.")
        _, static.color = imgui.color_edit4("MyColor##3", static.color, flags=imgui.ColorEditFlags_.no_inputs | imgui.ColorEditFlags_.no_label | misc_flags)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorButton (with custom Picker popup)")
        imgui.text("Color button with Custom Picker Popup:")

        # Generate a default palette. The palette will persist and can be edited.
        if not hasattr(static, "saved_palette"):
            static.saved_palette = []
            for n in range(32):
                r, g, b = imgui.color_convert_hsv_to_rgb(n / 31.0, 0.8, 0.8, 0.0, 0.0, 0.0)
                static.saved_palette.append(ImVec4(r, g, b, 1.0))

        if not hasattr(static, "backup_color"): static.backup_color = ImVec4()
        open_popup = imgui.color_button("MyColor##3b", static.color, misc_flags)
        imgui.same_line(0, imgui.get_style().item_inner_spacing.x)
        if imgui.button("Palette"):
            open_popup = True
        if open_popup:
            imgui.open_popup("mypicker")
            static.backup_color = ImVec4(static.color.x, static.color.y, static.color.z, static.color.w)
        if imgui.begin_popup("mypicker"):
            imgui.text("MY CUSTOM COLOR PICKER WITH AN AMAZING PALETTE!")
            imgui.separator()
            _, static.color = imgui.color_picker4("##picker", static.color, misc_flags | imgui.ColorEditFlags_.no_side_preview | imgui.ColorEditFlags_.no_small_preview)
            imgui.same_line()

            imgui.begin_group()  # Lock X position
            imgui.text("Current")
            imgui.color_button("##current", static.color, imgui.ColorEditFlags_.no_picker | imgui.ColorEditFlags_.alpha_preview_half, ImVec2(60, 40))
            imgui.text("Previous")
            if imgui.color_button("##previous", static.backup_color, imgui.ColorEditFlags_.no_picker | imgui.ColorEditFlags_.alpha_preview_half, ImVec2(60, 40)):
                static.color = ImVec4(static.backup_color.x, static.backup_color.y, static.backup_color.z, static.backup_color.w)
            imgui.separator()
            imgui.text("Palette")
            for n in range(32):
                imgui.push_id(n)
                if (n % 8) != 0:
                    imgui.same_line(0.0, imgui.get_style().item_spacing.y)

                palette_button_flags = imgui.ColorEditFlags_.no_alpha | imgui.ColorEditFlags_.no_picker | imgui.ColorEditFlags_.no_tooltip
                if imgui.color_button("##palette", static.saved_palette[n], palette_button_flags, ImVec2(20, 20)):
                    static.color = ImVec4(static.saved_palette[n].x, static.saved_palette[n].y, static.saved_palette[n].z, static.color.w)  # Preserve alpha!

                # Allow user to drop colors into each palette entry
                if imgui.begin_drag_drop_target():
                    payload = imgui.accept_drag_drop_payload_py_id("_COL3F")
                    if payload is not None:
                        pass  # Color drag/drop with raw payload not directly available in Python
                    payload = imgui.accept_drag_drop_payload_py_id("_COL4F")
                    if payload is not None:
                        pass
                    imgui.end_drag_drop_target()

                imgui.pop_id()
            imgui.end_group()
            imgui.end_popup()

        IMGUI_DEMO_MARKER("Widgets/Color/ColorButton (simple)")
        imgui.text("Color button only:")
        if not hasattr(static, "no_border"): static.no_border = False
        _, static.no_border = imgui.checkbox("ImGuiColorEditFlags_NoBorder", static.no_border)
        imgui.color_button("MyColor##3c", static.color, misc_flags | (imgui.ColorEditFlags_.no_border if static.no_border else 0), (80, 80))  # type: ignore

        IMGUI_DEMO_MARKER("Widgets/Color/ColorPicker")
        imgui.separator_text("Color picker")

        if not hasattr(static, "ref_color"): static.ref_color = False
        if not hasattr(static, "ref_color_v"): static.ref_color_v = ImVec4(1.0, 0.0, 1.0, 0.5)
        if not hasattr(static, "picker_mode"): static.picker_mode = 0
        if not hasattr(static, "display_mode"): static.display_mode = 0
        if not hasattr(static, "color_picker_flags"): static.color_picker_flags = imgui.ColorEditFlags_.alpha_bar

        imgui.push_id("Color picker")
        _, static.color_picker_flags = imgui.checkbox_flags("ImGuiColorEditFlags_NoAlpha", static.color_picker_flags, imgui.ColorEditFlags_.no_alpha)
        _, static.color_picker_flags = imgui.checkbox_flags("ImGuiColorEditFlags_AlphaBar", static.color_picker_flags, imgui.ColorEditFlags_.alpha_bar)
        _, static.color_picker_flags = imgui.checkbox_flags("ImGuiColorEditFlags_NoSidePreview", static.color_picker_flags, imgui.ColorEditFlags_.no_side_preview)
        if static.color_picker_flags & imgui.ColorEditFlags_.no_side_preview:
            imgui.same_line()
            _, static.ref_color = imgui.checkbox("With Ref Color", static.ref_color)
            if static.ref_color:
                imgui.same_line()
                _, static.ref_color_v = imgui.color_edit4("##RefColor", static.ref_color_v, imgui.ColorEditFlags_.no_inputs | misc_flags)

        _, static.picker_mode = imgui.combo("Picker Mode", static.picker_mode, ["Auto/Current", "ImGuiColorEditFlags_PickerHueBar", "ImGuiColorEditFlags_PickerHueWheel"])
        imgui.same_line(); help_marker("When not specified explicitly, user can right-click the picker to change mode.")

        _, static.display_mode = imgui.combo("Display Mode", static.display_mode, ["Auto/Current", "ImGuiColorEditFlags_NoInputs", "ImGuiColorEditFlags_DisplayRGB", "ImGuiColorEditFlags_DisplayHSV", "ImGuiColorEditFlags_DisplayHex"])
        imgui.same_line(); help_marker(
            "ColorEdit defaults to displaying RGB inputs if you don't specify a display mode, "
            "but the user can change it with a right-click on those inputs.\n\nColorPicker defaults to displaying RGB+HSV+Hex "
            "if you don't specify a display mode.\n\nYou can change the defaults using SetColorEditOptions().")

        picker_flags = misc_flags | static.color_picker_flags
        if static.picker_mode == 1: picker_flags |= imgui.ColorEditFlags_.picker_hue_bar
        if static.picker_mode == 2: picker_flags |= imgui.ColorEditFlags_.picker_hue_wheel
        if static.display_mode == 1: picker_flags |= imgui.ColorEditFlags_.no_inputs
        if static.display_mode == 2: picker_flags |= imgui.ColorEditFlags_.display_rgb
        if static.display_mode == 3: picker_flags |= imgui.ColorEditFlags_.display_hsv
        if static.display_mode == 4: picker_flags |= imgui.ColorEditFlags_.display_hex
        ref_col = static.ref_color_v if static.ref_color else None
        _, static.color = imgui.color_picker4("MyColor##4", static.color, picker_flags, ref_col)

        imgui.text("Set defaults in code:")
        imgui.same_line(); help_marker(
            "SetColorEditOptions() is designed to allow you to set boot-time default.\n"
            "We don't have Push/Pop functions because you can force options on a per-widget basis if needed, "
            "and the user can change non-forced ones with the options menu.\nWe don't have a getter to avoid "
            "encouraging you to persistently save values that aren't forward-compatible.")
        if imgui.button("Default: Uint8 + HSV + Hue Bar"):
            imgui.set_color_edit_options(imgui.ColorEditFlags_.uint8 | imgui.ColorEditFlags_.display_hsv | imgui.ColorEditFlags_.picker_hue_bar)
        if imgui.button("Default: Float + HDR + Hue Wheel"):
            imgui.set_color_edit_options(imgui.ColorEditFlags_.float | imgui.ColorEditFlags_.hdr | imgui.ColorEditFlags_.picker_hue_wheel)

        # Always display a small version of both types of pickers
        imgui.text("Both types:")
        w = (imgui.get_content_region_avail().x - imgui.get_style().item_spacing.y) * 0.40
        imgui.set_next_item_width(w)
        imgui.color_picker3("##MyColor##5", static.color, imgui.ColorEditFlags_.picker_hue_bar | imgui.ColorEditFlags_.no_side_preview | imgui.ColorEditFlags_.no_inputs | imgui.ColorEditFlags_.no_alpha)
        imgui.same_line()
        imgui.set_next_item_width(w)
        imgui.color_picker3("##MyColor##6", static.color, imgui.ColorEditFlags_.picker_hue_wheel | imgui.ColorEditFlags_.no_side_preview | imgui.ColorEditFlags_.no_inputs | imgui.ColorEditFlags_.no_alpha)
        imgui.pop_id()

        # HSV encoded support (to avoid RGB<>HSV round trips and singularities when S==0 or V==0)
        if not hasattr(static, "color_hsv"): static.color_hsv = ImVec4(0.23, 1.0, 1.0, 1.0)  # Stored as HSV!
        imgui.spacing()
        imgui.text("HSV encoded colors")
        imgui.same_line()
        help_marker(
            "By default, colors are given to ColorEdit and ColorPicker in RGB, but ImGuiColorEditFlags.InputHSV"
            "allows you to store colors as HSV and pass them to ColorEdit and ColorPicker as HSV. This comes with the"
            "added benefit that you can manipulate hue values with the picker even when saturation or value are zero."
        )
        imgui.text("Color widget with InputHSV:")
        _, static.color_hsv = imgui.color_edit4("HSV shown as RGB##1", static.color_hsv, imgui.ColorEditFlags_.display_rgb | imgui.ColorEditFlags_.input_hsv | imgui.ColorEditFlags_.float)   # type: ignore
        _, static.color_hsv = imgui.color_edit4("HSV shown as HSV##1", static.color_hsv, imgui.ColorEditFlags_.display_hsv | imgui.ColorEditFlags_.input_hsv | imgui.ColorEditFlags_.float)   # type: ignore
        # imgui.drag_float4("Raw HSV values", static.color_hsv, 0.01, 0.0, 1.0)

        imgui.tree_pop()

    if static.disable_all:
        imgui.end_disabled()

    if imgui.tree_node("Disable Blocks"):
        IMGUI_DEMO_MARKER("Widgets/Disable Blocks")
        _, static.disable_all = imgui.checkbox("Disable entire section above", static.disable_all)
        imgui.same_line(); help_marker("Demonstrate using BeginDisabled()/EndDisabled() across this section.")
        imgui.tree_pop()

    if static.disable_all:
        imgui.begin_disabled()

    if imgui.tree_node("Drag and drop"):
        IMGUI_DEMO_MARKER("Widgets/Drag and drop")
        if imgui.tree_node("Drag and drop in standard widgets"):
            IMGUI_DEMO_MARKER("Widgets/Drag and drop/Standard widgets")
            # ColorEdit widgets automatically act as drag source and drag target.
            help_marker("You can drag from the color squares.")
            if not hasattr(static, "dnd_col1"): static.dnd_col1 = ImVec4(1.0, 0.0, 0.2, 1.0)
            if not hasattr(static, "dnd_col2"): static.dnd_col2 = ImVec4(0.4, 0.7, 0.0, 0.5)
            _, static.dnd_col1 = imgui.color_edit3("color 1##dnd", static.dnd_col1)
            _, static.dnd_col2 = imgui.color_edit4("color 2##dnd", static.dnd_col2)
            imgui.tree_pop()

        if imgui.tree_node("Drag and drop to copy/swap items"):
            IMGUI_DEMO_MARKER("Widgets/Drag and drop/Copy-swap items")
            MODE_COPY, MODE_MOVE, MODE_SWAP = 0, 1, 2
            if not hasattr(static, "dnd_mode"): static.dnd_mode = 0
            if imgui.radio_button("Copy", static.dnd_mode == MODE_COPY): static.dnd_mode = MODE_COPY
            imgui.same_line()
            if imgui.radio_button("Move", static.dnd_mode == MODE_MOVE): static.dnd_mode = MODE_MOVE
            imgui.same_line()
            if imgui.radio_button("Swap", static.dnd_mode == MODE_SWAP): static.dnd_mode = MODE_SWAP
            if not hasattr(static, "dnd_names"):
                static.dnd_names = ["Bobby", "Beatrice", "Betty", "Brianna", "Barry", "Bernard", "Bibi", "Blaine", "Bryn"]
            for n in range(len(static.dnd_names)):
                imgui.push_id(n)
                if (n % 3) != 0:
                    imgui.same_line()
                imgui.button(static.dnd_names[n], ImVec2(60, 60))

                # Our buttons are both drag sources and drag targets here!
                if imgui.begin_drag_drop_source(imgui.DragDropFlags_.none):
                    imgui.set_drag_drop_payload_py_id("DND_DEMO_CELL", n)
                    if static.dnd_mode == MODE_COPY: imgui.text(f"Copy {static.dnd_names[n]}")
                    if static.dnd_mode == MODE_MOVE: imgui.text(f"Move {static.dnd_names[n]}")
                    if static.dnd_mode == MODE_SWAP: imgui.text(f"Swap {static.dnd_names[n]}")
                    imgui.end_drag_drop_source()
                if imgui.begin_drag_drop_target():
                    payload = imgui.accept_drag_drop_payload_py_id("DND_DEMO_CELL")
                    if payload is not None:
                        payload_n = payload.data_id
                        if static.dnd_mode == MODE_COPY:
                            static.dnd_names[n] = static.dnd_names[payload_n]
                        if static.dnd_mode == MODE_MOVE:
                            static.dnd_names[n] = static.dnd_names[payload_n]
                            static.dnd_names[payload_n] = ""
                        if static.dnd_mode == MODE_SWAP:
                            tmp = static.dnd_names[n]
                            static.dnd_names[n] = static.dnd_names[payload_n]
                            static.dnd_names[payload_n] = tmp
                    imgui.end_drag_drop_target()
                imgui.pop_id()
            imgui.tree_pop()

        if imgui.tree_node("Drag to reorder items (simple)"):
            IMGUI_DEMO_MARKER("Widgets/Drag and Drop/Drag to reorder items (simple)")
            imgui.push_item_flag(imgui.ItemFlags_.allow_duplicate_id, True)
            help_marker(
                "We don't use the drag and drop api at all here! "
                "Instead we query when the item is held but not hovered, and order items accordingly.")
            if not hasattr(static, "reorder_names"):
                static.reorder_names = ["Item One", "Item Two", "Item Three", "Item Four", "Item Five"]
            for n in range(len(static.reorder_names)):
                item = static.reorder_names[n]
                imgui.selectable(item, False)

                if imgui.is_item_active() and not imgui.is_item_hovered():
                    n_next = n + (-1 if imgui.get_mouse_drag_delta(0).y < 0.0 else 1)
                    if 0 <= n_next < len(static.reorder_names):
                        static.reorder_names[n] = static.reorder_names[n_next]
                        static.reorder_names[n_next] = item
                        imgui.reset_mouse_drag_delta()

            imgui.pop_item_flag()
            imgui.tree_pop()

        if imgui.tree_node("Tooltip at target location"):
            IMGUI_DEMO_MARKER("Widgets/Drag and Drop/Tooltip at target location")
            if not hasattr(static, "dnd_tooltip_col4"): static.dnd_tooltip_col4 = ImVec4(1.0, 0.0, 0.2, 1.0)
            for n in range(2):
                # Drop targets
                imgui.button("drop here##1" if n else "drop here##0")
                if imgui.begin_drag_drop_target():
                    drop_target_flags = imgui.DragDropFlags_.accept_before_delivery | imgui.DragDropFlags_.accept_no_preview_tooltip
                    payload = imgui.accept_drag_drop_payload_py_id("_COL4F", drop_target_flags)
                    if payload is not None:
                        imgui.set_mouse_cursor(imgui.MouseCursor_.not_allowed)
                        imgui.set_tooltip("Cannot drop here!")
                    imgui.end_drag_drop_target()

                # Drop source
                if n == 0:
                    imgui.color_button("drag me", static.dnd_tooltip_col4)

            imgui.tree_pop()

        imgui.tree_pop()

    # Drag and Slider Flags
    if imgui.tree_node("Drag/Slider Flags"):
        IMGUI_DEMO_MARKER("Widgets/Drag and Slider Flags")
        # Demonstrate using advanced flags for DragXXX and SliderXXX functions. Note that the flags are the same!
        if not hasattr(static, "drag_slider_flags"): static.drag_slider_flags = imgui.SliderFlags_.none
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_AlwaysClamp", static.drag_slider_flags, imgui.SliderFlags_.always_clamp)
        imgui.same_line(); help_marker("Always clamp value to min/max bounds (if any) when input manually with CTRL+Click.")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_Logarithmic", static.drag_slider_flags, imgui.SliderFlags_.logarithmic)
        imgui.same_line(); help_marker("Enable logarithmic editing (more precision for small values).")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_NoRoundToFormat", static.drag_slider_flags, imgui.SliderFlags_.no_round_to_format)
        imgui.same_line(); help_marker("Disable rounding underlying value to match precision of the format string (e.g. %.3f values are rounded to those 3 digits).")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_NoInput", static.drag_slider_flags, imgui.SliderFlags_.no_input)
        imgui.same_line(); help_marker("Disable CTRL+Click or Enter key allowing to input text directly into the widget.")

        # Drags
        if not hasattr(static, "drag_f"): static.drag_f = 0.5
        if not hasattr(static, "drag_i"): static.drag_i = 50
        imgui.text("Underlying float value: %f" % static.drag_f)
        _, static.drag_f = imgui.drag_float("DragFloat (0 -> 1)", static.drag_f, 0.005, 0.0, 1.0, "%.3f", flags=static.drag_slider_flags)
        _, static.drag_f = imgui.drag_float("DragFloat (0 -> +inf)", static.drag_f, 0.005, 0.0, float("inf"), "%.3f", flags=static.drag_slider_flags)
        _, static.drag_f = imgui.drag_float("DragFloat (-inf -> 1)", static.drag_f, 0.005, -float("inf"), 1.0, "%.3f", flags=static.drag_slider_flags)
        _, static.drag_f = imgui.drag_float("DragFloat (-inf -> +inf)", static.drag_f, 0.005, -float("inf"), float("inf"), "%.3f", flags=static.drag_slider_flags)
        _, static.drag_i = imgui.drag_int("DragInt (0 -> 100)", static.drag_i, 0.5, 0, 100, "%d", flags=static.drag_slider_flags)

        # Sliders
        if not hasattr(static, "slider_f"): static.slider_f = 0.5
        if not hasattr(static, "slider_i"): static.slider_i = 50
        imgui.text("Underlying float value: %f" % static.slider_f)
        _, static.slider_f = imgui.slider_float("SliderFloat (0 -> 1)", static.slider_f, 0.0, 1.0, "%.3f", flags=static.drag_slider_flags)
        _, static.slider_i = imgui.slider_int("SliderInt (0 -> 100)", static.slider_i, 0, 100, "%d", flags=static.drag_slider_flags)

        imgui.tree_pop()

    # Range Widgets
    if imgui.tree_node("Range Widgets"):
        IMGUI_DEMO_MARKER("Widgets/Range Widgets")
        if not hasattr(static, "begin_range_f"):
            static.begin_range_f = 10
            static.end_range_f = 90
            static.begin_i = 100
            static.end_i = 1000
        # _, static.begin_range_f, static.end_range_f = imgui.drag_float_range2("range float", static.begin_range_f, static.end_range_f, 0.25, 0.0, 100.0, "Min: %d units", "Max: %d units")
        _, static.begin_i, static.end_i = imgui.drag_int_range2("range int (no bounds)", static.begin_i, static.end_i, 5, 0, 0, "Min: %d units", "Max: %d units")
        imgui.tree_pop()

    # Multi-component Widgets
    if imgui.tree_node("Multi-component Widgets"):
        IMGUI_DEMO_MARKER("Widgets/Multi-component Widgets")
        if not hasattr(static, "vec4f"):
            static.vec4f = [0.10, 0.20, 0.30, 0.44]
            static.vec4i = [1, 5, 100, 255]
            static.vec3f = [0.10, 0.20, 0.30]
            static.vec3i = [1, 5, 100]
            static.vec2f = [0.10, 0.20]
            static.vec2i = [1, 5]

        imgui.separator_text("2-wide")
        _, static.vec2f = imgui.input_float2("input float2", static.vec2f)
        _, static.vec2f = imgui.drag_float2("drag float2", static.vec2f, 0.01, 0.0, 1.0)
        _, static.vec2f = imgui.slider_float2("slider float2", static.vec2f, 0.0, 1.0)
        _, static.vec2i = imgui.input_int2("input int2", static.vec2i)
        _, static.vec2i = imgui.drag_int2("drag int2", static.vec2i, 1, 0, 255)
        _, static.vec2i = imgui.slider_int2("slider int2", static.vec2i, 0, 255)

        imgui.separator_text("3-wide")
        _, static.vec3f = imgui.input_float3("input float3", static.vec3f)
        _, static.vec3f = imgui.drag_float3("drag float3", static.vec3f, 0.01, 0.0, 1.0)
        _, static.vec3f = imgui.slider_float3("slider float3", static.vec3f, 0.0, 1.0)
        _, static.vec3i = imgui.input_int3("input int3", static.vec3i)
        _, static.vec3i = imgui.drag_int3("drag int3", static.vec3i, 1, 0, 255)
        _, static.vec3i = imgui.slider_int3("slider int3", static.vec3i, 0, 255)

        imgui.separator_text("4-wide")
        _, static.vec4f = imgui.input_float4("input float4", static.vec4f)
        _, static.vec4f = imgui.drag_float4("drag float4", static.vec4f, 0.01, 0.0, 1.0)
        _, static.vec4f = imgui.slider_float4("slider float4", static.vec4f, 0.0, 1.0)
        _, static.vec4i = imgui.input_int4("input int4", static.vec4i)
        _, static.vec4i = imgui.drag_int4("drag int4", static.vec4i, 1, 0, 255)
        _, static.vec4i = imgui.slider_int4("slider int4", static.vec4i, 0, 255)

        imgui.tree_pop()

    # Vertical Sliders
    if imgui.tree_node("Vertical Sliders"):
        IMGUI_DEMO_MARKER("Widgets/Vertical Sliders")
        spacing = 4
        imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(spacing, spacing))

        if not hasattr(static, "sliderv_int_value"): static.sliderv_int_value = 0
        imgui.v_slider_int("##int", ImVec2(18, 160), static.sliderv_int_value, 0, 5)
        imgui.same_line()

        if not hasattr(static, "sliderv_values"): static.sliderv_values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]
        imgui.push_id("set1")
        for i in range(7):
            if i > 0:
                imgui.same_line()
            imgui.push_id(i)
            imgui.push_style_color(imgui.Col_.frame_bg, imgui.ImColor.hsv(i / 7.0, 0.5, 0.5).value)
            imgui.push_style_color(imgui.Col_.frame_bg_hovered, imgui.ImColor.hsv(i / 7.0, 0.6, 0.5).value)
            imgui.push_style_color(imgui.Col_.frame_bg_active, imgui.ImColor.hsv(i / 7.0, 0.7, 0.5).value)
            imgui.push_style_color(imgui.Col_.slider_grab, imgui.ImColor.hsv(i / 7.0, 0.9, 0.9).value)
            _, static.sliderv_values[i] = imgui.v_slider_float("##v", ImVec2(18, 160), static.sliderv_values[i], 0.0, 1.0, "")
            if imgui.is_item_active() or imgui.is_item_hovered():
                imgui.set_tooltip("%.3f" % static.sliderv_values[i])
            imgui.pop_style_color(4)
            imgui.pop_id()
        imgui.pop_id()

        imgui.same_line()
        imgui.push_id("set2")
        if not hasattr(static, "sliderv_values2"): static.sliderv_values2 = [0.20, 0.80, 0.40, 0.25]
        rows = 3
        small_slider_size = ImVec2(18, (160.0 - (rows - 1) * spacing) / rows)
        for nx in range(4):
            if nx > 0:
                imgui.same_line()
            imgui.begin_group()
            for ny in range(rows):
                imgui.push_id(nx * rows + ny)
                _, static.sliderv_values2[nx] = imgui.v_slider_float("##v", small_slider_size, static.sliderv_values2[nx], 0.0, 1.0, "")
                if imgui.is_item_active() or imgui.is_item_hovered():
                    imgui.set_tooltip("%.3f" % static.sliderv_values2[nx])
                imgui.pop_id()
            imgui.end_group()
        imgui.pop_id()

        imgui.same_line()
        imgui.push_id("set3")
        for i in range(4):
            if i > 0:
                imgui.same_line()
            imgui.push_id(i)
            imgui.push_style_var(imgui.StyleVar_.grab_min_size, 40)
            _, static.sliderv_values[i] = imgui.v_slider_float("##v", ImVec2(40, 160), static.sliderv_values[i], 0.0, 1.0, "%.2f\nsec")
            imgui.pop_style_var()
            imgui.pop_id()
        imgui.pop_id()
        imgui.pop_style_var()
        imgui.tree_pop()

    # Text Filter
    if imgui.tree_node("Text Filter"):
        IMGUI_DEMO_MARKER("Widgets/Text Filter")
        # Helper class to easy setup a text filter.
        # You may want to implement a more feature-full filtering scheme in your own application.
        help_marker("Not a widget per-se, but ImGuiTextFilter is a helper to perform simple filtering on text strings.")
        if not hasattr(static, "text_filter"): static.text_filter = imgui.TextFilter()
        imgui.text("Filter usage:\n"
                   "  \"\"         display all lines\n"
                   "  \"xxx\"      display lines containing \"xxx\"\n"
                   "  \"xxx,yyy\"  display lines containing \"xxx\" or \"yyy\"\n"
                   "  \"-xxx\"     hide lines containing \"xxx\"")
        static.text_filter.draw()
        lines = ["aaa1.c", "bbb1.c", "ccc1.c", "aaa2.cpp", "bbb2.cpp", "ccc2.cpp", "abc.h", "hello, world"]
        for line in lines:
            if static.text_filter.pass_filter(line):
                imgui.bullet_text("%s" % line)
        imgui.tree_pop()

    if imgui.tree_node("Fonts"):
        IMGUI_DEMO_MARKER("Widgets/Fonts")
        atlas = imgui.get_io().fonts
        imgui.internal.show_font_atlas(atlas)
        imgui.tree_pop()

    if imgui.tree_node("Plotting"):
        IMGUI_DEMO_MARKER("Widgets/Plotting")
        imgui.text("Need better plotting and graphing? Consider using ImPlot:")
        imgui.text_link_open_url("https://github.com/epezent/implot")
        imgui.separator()

        if not hasattr(static, "plot_animate"): static.plot_animate = True
        _, static.plot_animate = imgui.checkbox("Animate", static.plot_animate)

        # Plot as lines and plot as histogram
        if not hasattr(static, "plot_arr"): static.plot_arr = np.array([0.6, 0.1, 1.0, 0.5, 0.92, 0.1, 0.2], dtype=np.float32)
        imgui.plot_lines("Frame Times", static.plot_arr)
        imgui.plot_histogram("Histogram", static.plot_arr, 0, None, 0.0, 1.0, ImVec2(0, 80.0))

        # Fill an array of contiguous float values to plot
        if not hasattr(static, "plot_values"): static.plot_values = np.zeros(90, dtype=np.float32)
        if not hasattr(static, "plot_values_offset"): static.plot_values_offset = 0
        if not hasattr(static, "plot_refresh_time"): static.plot_refresh_time = 0.0
        if not hasattr(static, "plot_phase"): static.plot_phase = 0.0
        if not static.plot_animate or static.plot_refresh_time == 0.0:
            static.plot_refresh_time = imgui.get_time()
        while static.plot_refresh_time < imgui.get_time():
            static.plot_values[static.plot_values_offset] = math.cos(static.plot_phase)
            static.plot_values_offset = (static.plot_values_offset + 1) % len(static.plot_values)
            static.plot_phase += 0.10 * static.plot_values_offset
            static.plot_refresh_time += 1.0 / 60.0

        # Plots can display overlay texts
        average = float(np.mean(static.plot_values))
        overlay = f"avg {average:f}"
        imgui.plot_lines("Lines", static.plot_values, static.plot_values_offset, overlay, -1.0, 1.0, ImVec2(0, 80.0))

        # Use functions to generate output
        if not hasattr(static, "plot_func_type"): static.plot_func_type = 0
        if not hasattr(static, "plot_display_count"): static.plot_display_count = 70
        imgui.separator_text("Functions")
        imgui.set_next_item_width(imgui.get_font_size() * 8)
        _, static.plot_func_type = imgui.combo("func", static.plot_func_type, ["Sin", "Saw"])
        imgui.same_line()
        _, static.plot_display_count = imgui.slider_int("Sample count", static.plot_display_count, 1, 400)
        if static.plot_func_type == 0:
            func_values = np.array([math.sin(i * 0.1) for i in range(static.plot_display_count)], dtype=np.float32)
        else:
            func_values = np.array([1.0 if (i & 1) else -1.0 for i in range(static.plot_display_count)], dtype=np.float32)
        imgui.plot_lines("Lines##2", func_values, 0, None, -1.0, 1.0, ImVec2(0, 80))
        imgui.plot_histogram("Histogram##2", func_values, 0, None, -1.0, 1.0, ImVec2(0, 80))

        imgui.tree_pop()

    if imgui.tree_node("Progress Bars"):
        IMGUI_DEMO_MARKER("Widgets/Progress Bars")
        # Animate a simple progress bar
        if not hasattr(static, "progress_accum"): static.progress_accum = 0.0
        if not hasattr(static, "progress_dir"): static.progress_dir = 1.0
        static.progress_accum += static.progress_dir * 0.4 * imgui.get_io().delta_time
        if static.progress_accum >= 1.1:
            static.progress_accum = 1.1
            static.progress_dir *= -1.0
        if static.progress_accum <= -0.1:
            static.progress_accum = -0.1
            static.progress_dir *= -1.0

        progress = max(0.0, min(static.progress_accum, 1.0))

        imgui.progress_bar(progress, ImVec2(0.0, 0.0))
        imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
        imgui.text("Progress Bar")

        imgui.progress_bar(progress, ImVec2(0.0, 0.0), f"{int(progress * 1753)}/{1753}")

        # Pass an animated negative value for indeterminate progress
        imgui.progress_bar(-1.0 * imgui.get_time(), ImVec2(0.0, 0.0), "Searching..")
        imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
        imgui.text("Indeterminate")

        imgui.tree_pop()

    if imgui.tree_node("Querying Item Status (Edited/Active/Hovered etc.)"):
        IMGUI_DEMO_MARKER("Widgets/Querying Item Status (Edited,Active,Hovered etc.)")
        # Select an item type
        item_names = [
            "Text", "Button", "Button (w/ repeat)", "Checkbox", "SliderFloat", "InputText", "InputTextMultiline", "InputFloat",
            "InputFloat3", "ColorEdit4", "Selectable", "MenuItem", "TreeNode", "TreeNode (w/ double-click)", "Combo", "ListBox"
        ]
        if not hasattr(static, "qi_item_type"): static.qi_item_type = 4
        if not hasattr(static, "qi_item_disabled"): static.qi_item_disabled = False
        if not hasattr(static, "qi_b"): static.qi_b = False
        if not hasattr(static, "qi_col4f"): static.qi_col4f = [1.0, 0.5, 0.0, 1.0]
        if not hasattr(static, "qi_str"): static.qi_str = ""
        if not hasattr(static, "qi_current"): static.qi_current = 1
        _, static.qi_item_type = imgui.combo("Item Type", static.qi_item_type, item_names, len(item_names))
        imgui.same_line()
        help_marker("Testing how various types of items are interacting with the IsItemXXX functions. Note that the bool return value of most ImGui function is generally equivalent to calling ImGui::IsItemHovered().")
        _, static.qi_item_disabled = imgui.checkbox("Item Disabled", static.qi_item_disabled)

        # Submit selected items so we can query their status
        ret = False
        if static.qi_item_disabled:
            imgui.begin_disabled(True)
        if static.qi_item_type == 0: imgui.text("ITEM: Text")
        if static.qi_item_type == 1: ret = imgui.button("ITEM: Button")
        if static.qi_item_type == 2:
            imgui.push_item_flag(imgui.ItemFlags_.button_repeat, True); ret = imgui.button("ITEM: Button"); imgui.pop_item_flag()
        if static.qi_item_type == 3: ret, static.qi_b = imgui.checkbox("ITEM: Checkbox", static.qi_b)
        if static.qi_item_type == 4: ret, static.qi_col4f[0] = imgui.slider_float("ITEM: SliderFloat", static.qi_col4f[0], 0.0, 1.0)
        if static.qi_item_type == 5: ret, static.qi_str = imgui.input_text("ITEM: InputText", static.qi_str)
        if static.qi_item_type == 6: ret, static.qi_str = imgui.input_text_multiline("ITEM: InputTextMultiline", static.qi_str)
        if static.qi_item_type == 7: ret, static.qi_col4f[0] = imgui.input_float("ITEM: InputFloat", static.qi_col4f[0], 1.0)
        if static.qi_item_type == 8: ret, static.qi_col4f[:3] = imgui.input_float3("ITEM: InputFloat3", static.qi_col4f[:3])
        if static.qi_item_type == 9: ret, static.qi_col4f = imgui.color_edit4("ITEM: ColorEdit4", static.qi_col4f)
        if static.qi_item_type == 10: ret, _ = imgui.selectable("ITEM: Selectable", False)
        if static.qi_item_type == 11: ret, _ = imgui.menu_item("ITEM: MenuItem", "", False)
        if static.qi_item_type == 12:
            ret = imgui.tree_node("ITEM: TreeNode")
            if ret: imgui.tree_pop()
        if static.qi_item_type == 13:
            ret = imgui.tree_node_ex("ITEM: TreeNode w/ ImGuiTreeNodeFlags_OpenOnDoubleClick", imgui.TreeNodeFlags_.open_on_double_click | imgui.TreeNodeFlags_.no_tree_push_on_open)
        if static.qi_item_type == 14:
            items = ["Apple", "Banana", "Cherry", "Kiwi"]
            ret, static.qi_current = imgui.combo("ITEM: Combo", static.qi_current, items)
        if static.qi_item_type == 15:
            items = ["Apple", "Banana", "Cherry", "Kiwi"]
            ret, static.qi_current = imgui.list_box("ITEM: ListBox", static.qi_current, items)

        hovered_delay_none = imgui.is_item_hovered()
        hovered_delay_stationary = imgui.is_item_hovered(imgui.HoveredFlags_.stationary)
        hovered_delay_short = imgui.is_item_hovered(imgui.HoveredFlags_.delay_short)
        hovered_delay_normal = imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal)
        hovered_delay_tooltip = imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip)

        imgui.bullet_text(
            f"Return value = {int(ret)}\n"
            f"IsItemFocused() = {int(imgui.is_item_focused())}\n"
            f"IsItemHovered() = {int(imgui.is_item_hovered())}\n"
            f"IsItemHovered(_AllowWhenBlockedByPopup) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_blocked_by_popup))}\n"
            f"IsItemHovered(_AllowWhenBlockedByActiveItem) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_blocked_by_active_item))}\n"
            f"IsItemHovered(_AllowWhenOverlappedByItem) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_overlapped_by_item))}\n"
            f"IsItemHovered(_AllowWhenOverlappedByWindow) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_overlapped_by_window))}\n"
            f"IsItemHovered(_AllowWhenDisabled) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_disabled))}\n"
            f"IsItemHovered(_RectOnly) = {int(imgui.is_item_hovered(imgui.HoveredFlags_.rect_only))}\n"
            f"IsItemActive() = {int(imgui.is_item_active())}\n"
            f"IsItemEdited() = {int(imgui.is_item_edited())}\n"
            f"IsItemActivated() = {int(imgui.is_item_activated())}\n"
            f"IsItemDeactivated() = {int(imgui.is_item_deactivated())}\n"
            f"IsItemDeactivatedAfterEdit() = {int(imgui.is_item_deactivated_after_edit())}\n"
            f"IsItemVisible() = {int(imgui.is_item_visible())}\n"
            f"IsItemClicked() = {int(imgui.is_item_clicked())}\n"
            f"IsItemToggledOpen() = {int(imgui.is_item_toggled_open())}\n"
            f"GetItemRectMin() = ({imgui.get_item_rect_min().x:.1f}, {imgui.get_item_rect_min().y:.1f})\n"
            f"GetItemRectMax() = ({imgui.get_item_rect_max().x:.1f}, {imgui.get_item_rect_max().y:.1f})\n"
            f"GetItemRectSize() = ({imgui.get_item_rect_size().x:.1f}, {imgui.get_item_rect_size().y:.1f})"
        )
        imgui.bullet_text(
            f"with Hovering Delay or Stationary test:\n"
            f"IsItemHovered() = {int(hovered_delay_none)}\n"
            f"IsItemHovered(_Stationary) = {int(hovered_delay_stationary)}\n"
            f"IsItemHovered(_DelayShort) = {int(hovered_delay_short)}\n"
            f"IsItemHovered(_DelayNormal) = {int(hovered_delay_normal)}\n"
            f"IsItemHovered(_Tooltip) = {int(hovered_delay_tooltip)}"
        )

        if static.qi_item_disabled:
            imgui.end_disabled()

        _, _ = imgui.input_text("unused", "", imgui.InputTextFlags_.read_only)
        imgui.same_line()
        help_marker("This widget is only here to be able to tab-out of the widgets above and see e.g. Deactivated() status.")

        imgui.tree_pop()

    if imgui.tree_node("Querying Window Status (Focused/Hovered etc.)"):
        IMGUI_DEMO_MARKER("Widgets/Querying Window Status (Focused,Hovered etc.)")
        if not hasattr(static, "qw_embed_all"): static.qw_embed_all = False
        _, static.qw_embed_all = imgui.checkbox("Embed everything inside a child window for testing _RootWindow flag.", static.qw_embed_all)
        if static.qw_embed_all:
            imgui.begin_child("outer_child", ImVec2(0, imgui.get_font_size() * 20.0), imgui.ChildFlags_.borders)

        # Testing IsWindowFocused() function with its various flags
        imgui.bullet_text(
            f"IsWindowFocused() = {int(imgui.is_window_focused())}\n"
            f"IsWindowFocused(_ChildWindows) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows))}\n"
            f"IsWindowFocused(_ChildWindows|_NoPopupHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows | imgui.FocusedFlags_.no_popup_hierarchy))}\n"
            f"IsWindowFocused(_ChildWindows|_DockHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows | imgui.FocusedFlags_.dock_hierarchy))}\n"
            f"IsWindowFocused(_ChildWindows|_RootWindow) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows | imgui.FocusedFlags_.root_window))}\n"
            f"IsWindowFocused(_ChildWindows|_RootWindow|_NoPopupHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows | imgui.FocusedFlags_.root_window | imgui.FocusedFlags_.no_popup_hierarchy))}\n"
            f"IsWindowFocused(_ChildWindows|_RootWindow|_DockHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.child_windows | imgui.FocusedFlags_.root_window | imgui.FocusedFlags_.dock_hierarchy))}\n"
            f"IsWindowFocused(_RootWindow) = {int(imgui.is_window_focused(imgui.FocusedFlags_.root_window))}\n"
            f"IsWindowFocused(_RootWindow|_NoPopupHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.root_window | imgui.FocusedFlags_.no_popup_hierarchy))}\n"
            f"IsWindowFocused(_RootWindow|_DockHierarchy) = {int(imgui.is_window_focused(imgui.FocusedFlags_.root_window | imgui.FocusedFlags_.dock_hierarchy))}\n"
            f"IsWindowFocused(_AnyWindow) = {int(imgui.is_window_focused(imgui.FocusedFlags_.any_window))}"
        )

        # Testing IsWindowHovered() function with its various flags
        imgui.bullet_text(
            f"IsWindowHovered() = {int(imgui.is_window_hovered())}\n"
            f"IsWindowHovered(_AllowWhenBlockedByPopup) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.allow_when_blocked_by_popup))}\n"
            f"IsWindowHovered(_AllowWhenBlockedByActiveItem) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.allow_when_blocked_by_active_item))}\n"
            f"IsWindowHovered(_ChildWindows) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows))}\n"
            f"IsWindowHovered(_ChildWindows|_NoPopupHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.no_popup_hierarchy))}\n"
            f"IsWindowHovered(_ChildWindows|_DockHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.dock_hierarchy))}\n"
            f"IsWindowHovered(_ChildWindows|_RootWindow) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.root_window))}\n"
            f"IsWindowHovered(_ChildWindows|_RootWindow|_NoPopupHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.root_window | imgui.HoveredFlags_.no_popup_hierarchy))}\n"
            f"IsWindowHovered(_ChildWindows|_RootWindow|_DockHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.root_window | imgui.HoveredFlags_.dock_hierarchy))}\n"
            f"IsWindowHovered(_RootWindow) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.root_window))}\n"
            f"IsWindowHovered(_RootWindow|_NoPopupHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.root_window | imgui.HoveredFlags_.no_popup_hierarchy))}\n"
            f"IsWindowHovered(_RootWindow|_DockHierarchy) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.root_window | imgui.HoveredFlags_.dock_hierarchy))}\n"
            f"IsWindowHovered(_ChildWindows|_AllowWhenBlockedByPopup) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.child_windows | imgui.HoveredFlags_.allow_when_blocked_by_popup))}\n"
            f"IsWindowHovered(_AnyWindow) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.any_window))}\n"
            f"IsWindowHovered(_Stationary) = {int(imgui.is_window_hovered(imgui.HoveredFlags_.stationary))}"
        )

        imgui.begin_child("child", ImVec2(0, 50), imgui.ChildFlags_.borders)
        imgui.text("This is another child window for testing the _ChildWindows flag.")
        imgui.end_child()
        if static.qw_embed_all:
            imgui.end_child()

        # Calling IsItemHovered() after begin returns the hovered status of the title bar
        if not hasattr(static, "qw_test_window"): static.qw_test_window = False
        _, static.qw_test_window = imgui.checkbox("Hovered/Active tests after Begin() for title bar testing", static.qw_test_window)
        if static.qw_test_window:
            visible, static.qw_test_window = imgui.begin("Title bar Hovered/Active tests", static.qw_test_window)
            if imgui.begin_popup_context_item():
                if imgui.menu_item("Close")[0]:
                    static.qw_test_window = False
                imgui.end_popup()
            imgui.text(
                f"IsItemHovered() after begin = {int(imgui.is_item_hovered())} (== is title bar hovered)\n"
                f"IsItemActive() after begin = {int(imgui.is_item_active())} (== is window being clicked/moved)"
            )
            imgui.end()

        imgui.tree_pop()

    if static.disable_all:
        imgui.end_disabled()


def show_demo_window_layout():
    static = show_demo_window_layout

    if not imgui.collapsing_header("Layout & Scrolling"):
        return

    if imgui.tree_node("Child windows"):
        IMGUI_DEMO_MARKER("Layout/Child windows")
        imgui.separator_text("Child windows")

        help_marker("Use child windows to begin into self-contained independent scrolling/clipping regions within a host window.")
        if not hasattr(static, "disable_mouse_wheel"):
            static.disable_mouse_wheel = False
        if not hasattr(static, "disable_menu"):
            static.disable_menu = False
        _, static.disable_mouse_wheel = imgui.checkbox("Disable Mouse Wheel", static.disable_mouse_wheel)
        _, static.disable_menu = imgui.checkbox("Disable Menu", static.disable_menu)

        # Child 1: no border, enable horizontal scrollbar
        window_flags = imgui.WindowFlags_.horizontal_scrollbar
        if static.disable_mouse_wheel:
            window_flags |= imgui.WindowFlags_.no_scroll_with_mouse
        imgui.begin_child("ChildL", ImVec2(imgui.get_content_region_avail().x * 0.5, 260), False, window_flags)
        for i in range(100):
            imgui.text("%04d: scrollable region" % i)
        imgui.end_child()

        imgui.same_line()

        # Child 2: rounded border
        if hasattr(static, "disable_mouse_wheel"): static.disable_mouse_wheel = False
        if hasattr(static, "disable_menu"): static.disable_menu = False
        window_flags = imgui.WindowFlags_.none
        if static.disable_mouse_wheel:
            window_flags |= imgui.WindowFlags_.no_scroll_with_mouse
        if not static.disable_menu:
            window_flags |= imgui.WindowFlags_.menu_bar
        imgui.push_style_var(imgui.StyleVar_.child_rounding, 5.0)
        if imgui.begin_child("ChildR", ImVec2(0, 260), True, window_flags):
            if not static.disable_menu and imgui.begin_menu_bar():
                if imgui.begin_menu("Menu"):
                    show_example_menu_file()
                    imgui.end_menu()
                imgui.end_menu_bar()
            if imgui.begin_table("split", 2, flags=(imgui.TableFlags_.resizable | imgui.TableFlags_.no_saved_settings)):
                for i in range(100):
                    buf = f"{i:03d}"
                    imgui.table_next_column()
                    imgui.button(buf, ImVec2(-1, 0.0))
                imgui.end_table()
            imgui.end_child()
        imgui.pop_style_var()

        imgui.tree_pop()

    if imgui.tree_node("Widgets Width"):
        IMGUI_DEMO_MARKER("Layout/Widgets Width")
        if not hasattr(static, "ww_f"): static.ww_f = 0.0
        if not hasattr(static, "ww_show_indented"): static.ww_show_indented = True
        _, static.ww_show_indented = imgui.checkbox("Show indented items", static.ww_show_indented)

        imgui.text("set_next_item_width/push_item_width(100)")
        imgui.same_line(); help_marker("Fixed width.")
        imgui.push_item_width(100)
        _, static.ww_f = imgui.drag_float("float##1b", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##1b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.text("set_next_item_width/push_item_width(-100)")
        imgui.same_line(); help_marker("Align to right edge minus 100")
        imgui.push_item_width(-100)
        _, static.ww_f = imgui.drag_float("float##2a", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##2b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.text("set_next_item_width/push_item_width(get_content_region_avail().x * 0.5)")
        imgui.same_line(); help_marker("Half of available width.\n(~ right-cursor_pos)\n(works within a column set)")
        imgui.push_item_width(imgui.get_content_region_avail().x * 0.5)
        _, static.ww_f = imgui.drag_float("float##3a", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##3b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.text("set_next_item_width/push_item_width(-get_content_region_avail().x * 0.5)")
        imgui.same_line(); help_marker("Align to right edge minus half")
        imgui.push_item_width(-imgui.get_content_region_avail().x * 0.5)
        _, static.ww_f = imgui.drag_float("float##4a", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##4b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.text("set_next_item_width/push_item_width(-min(...))")
        imgui.push_item_width(-min(imgui.get_font_size() * 12, imgui.get_content_region_avail().x * 0.40))
        _, static.ww_f = imgui.drag_float("float##5a", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##5b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.text("set_next_item_width/push_item_width(-FLT_MIN)")
        imgui.same_line(); help_marker("Align to right edge")
        imgui.push_item_width(-imgui.FLT_MIN)
        _, static.ww_f = imgui.drag_float("##float6a", static.ww_f)
        if static.ww_show_indented:
            imgui.indent()
            _, static.ww_f = imgui.drag_float("float (indented)##6b", static.ww_f)
            imgui.unindent()
        imgui.pop_item_width()

        imgui.tree_pop()

    # Basic Horizontal Layout
    if imgui.tree_node("Basic Horizontal Layout"):
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout")
        imgui.text_wrapped("(Use imgui.same_line() to keep adding items to the right of the preceding item)")

        # Text
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout/SameLine")
        imgui.text("Two items: Hello")
        imgui.same_line()
        imgui.text_colored(ImVec4(1, 1, 0, 1), "Sailor")

        # Adjust spacing
        imgui.text("More spacing: Hello")
        imgui.same_line(0, 20)
        imgui.text_colored(ImVec4(1, 1, 0, 1), "Sailor")

        # Button
        imgui.align_text_to_frame_padding()
        imgui.text("Normal buttons")
        imgui.same_line()
        imgui.button("Banana")
        imgui.same_line()
        imgui.button("Apple")
        imgui.same_line()
        imgui.button("Corniflower")

        # Button
        imgui.text("Small buttons")
        imgui.same_line()
        imgui.small_button("Like this one")
        imgui.same_line()
        imgui.text("can fit within a text block.")

        # Aligned to arbitrary position. Easy/cheap column.
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout/SameLine (with offset)")
        imgui.text("Aligned")
        imgui.same_line(150)
        imgui.text("x=150")
        imgui.same_line(300)
        imgui.text("x=300")
        imgui.text("Aligned")
        imgui.same_line(150)
        imgui.small_button("x=150")
        imgui.same_line(300)
        imgui.small_button("x=300")

        # Checkbox
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout/SameLine (more)")
        if not hasattr(static, "c1"):
            static.c1 = False
            static.c2 = False
            static.c3 = False
            static.c4 = False
        _, static.c1 = imgui.checkbox("My", static.c1)
        imgui.same_line()
        _, static.c2 = imgui.checkbox("Tailor", static.c2)
        imgui.same_line()
        _, static.c3 = imgui.checkbox("Is", static.c3)
        imgui.same_line()
        _, static.c4 = imgui.checkbox("Rich", static.c4)

        # Various
        if not hasattr(static, "f0"):
            static.f0 = 1.0
            static.f1 = 2.0
            static.f2 = 3.0
            static.item = -1
        imgui.push_item_width(80)
        items = ["AAAA", "BBBB", "CCCC", "DDDD"]
        _, static.item = imgui.combo("Combo", static.item, items)
        imgui.same_line()
        _, static.f0 = imgui.slider_float("X", static.f0, 0.0, 5.0)
        imgui.same_line()
        _, static.f1 = imgui.slider_float("Y", static.f1, 0.0, 5.0)
        imgui.same_line()
        _, static.f2 = imgui.slider_float("Z", static.f2, 0.0, 5.0)
        imgui.pop_item_width()

        imgui.push_item_width(80)
        imgui.text("Lists:")
        if not hasattr(static, "selection"): static.selection = [0, 1, 2, 3]
        for i in range(4):
            if i > 0: imgui.same_line()
            imgui.push_id(i)
            _, static.selection[i] = imgui.list_box("", static.selection[i], items)
            imgui.pop_id()
            #imgui.set_item_tooltip("ListBox %d hovered" % i)
        imgui.pop_item_width()

        # Dummy
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout/Dummy")
        button_sz = ImVec2(40, 40)
        imgui.button("A", button_sz)
        imgui.same_line()
        imgui.dummy(button_sz)
        imgui.same_line()
        imgui.button("B", button_sz)

        # Manually wrapping
        # (we should eventually provide this as an automatic layout feature, but for now you can do it manually)
        IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout/Manual wrapping")
        imgui.text("Manual wrapping:")
        style = imgui.get_style()
        buttons_count = 20
        window_visible_x2 = imgui.get_window_pos().x + imgui.get_content_region_avail().x
        for n in range(buttons_count):
            imgui.push_id(n)
            imgui.button("Box", button_sz)
            last_button_x2 = imgui.get_item_rect_max().x
            next_button_x2 = last_button_x2 + style.item_spacing.x + button_sz.x  # Expected position if next button was on same line
            if n + 1 < buttons_count and next_button_x2 < window_visible_x2:
                imgui.same_line()
            imgui.pop_id()

        imgui.tree_pop()

    # Groups
    if imgui.tree_node("Groups"):
        IMGUI_DEMO_MARKER("Layout/Groups")
        help_marker(
            "BeginGroup() basically locks the horizontal position for new line. "
            "EndGroup() bundles the whole group so that you can use \"item\" functions such as "
            "IsItemHovered()/IsItemActive() or SameLine() etc. on the whole group.")
        imgui.begin_group()

        imgui.begin_group()
        imgui.button("AAA")
        imgui.same_line()
        imgui.button("BBB")
        imgui.same_line()
        imgui.begin_group()
        imgui.button("CCC")
        imgui.button("DDD")
        imgui.end_group()
        imgui.same_line()
        imgui.button("EEE")
        imgui.end_group()
        imgui.set_item_tooltip("First group hovered")

        # Capture the group size and create widgets using the same size
        size = imgui.get_item_rect_size()
        values = np.array([0.5, 0.20, 0.80, 0.60, 0.25], np.float32)
        imgui.plot_histogram("##values", values, 0, None, 0.0, 1.0, size)

        imgui.button("ACTION", ImVec2(size.x - imgui.get_style().item_spacing.x * 0.5, size.y))
        imgui.same_line()
        imgui.button("REACTION", ImVec2(size.x - imgui.get_style().item_spacing.x * 0.5, size.y))
        imgui.end_group()
        imgui.same_line()

        imgui.button("LEVERAGE\nBUZZWORD", size)
        imgui.same_line()

        if imgui.begin_list_box("List", size):
            imgui.selectable("Selected", True)
            imgui.selectable("Not Selected", False)
            imgui.end_list_box()
        imgui.tree_pop()

    if imgui.tree_node("Text Baseline Alignment"):
        IMGUI_DEMO_MARKER("Layout/Text Baseline Alignment")
        with indented_block():
            imgui.bullet_text("Text baseline:")
            imgui.same_line(); help_marker(
                "This is testing the vertical alignment that gets applied on text to keep it aligned with widgets. "
                "Lines only composed of text or \"small\" widgets use less vertical space than lines with framed widgets.")
            imgui.indent()

            imgui.text("KO Blahblah"); imgui.same_line()
            imgui.button("Some framed item"); imgui.same_line()
            help_marker("Baseline of button will look misaligned with text..")

            imgui.align_text_to_frame_padding()
            imgui.text("OK Blahblah"); imgui.same_line()
            imgui.button("Some framed item##2"); imgui.same_line()
            help_marker("We call AlignTextToFramePadding() to vertically align the text baseline by +FramePadding.y")

            imgui.button("TEST##1"); imgui.same_line()
            imgui.text("TEST"); imgui.same_line()
            imgui.small_button("TEST##2")

            imgui.align_text_to_frame_padding()
            imgui.text("Text aligned to framed item"); imgui.same_line()
            imgui.button("Item##1"); imgui.same_line()
            imgui.text("Item"); imgui.same_line()
            imgui.small_button("Item##2"); imgui.same_line()
            imgui.button("Item##3")

            imgui.unindent()

        imgui.spacing()

        with indented_block():
            imgui.bullet_text("Multi-line text:")
            imgui.indent()
            imgui.text("One\nTwo\nThree"); imgui.same_line()
            imgui.text("Hello\nWorld"); imgui.same_line()
            imgui.text("Banana")

            imgui.text("Banana"); imgui.same_line()
            imgui.text("Hello\nWorld"); imgui.same_line()
            imgui.text("One\nTwo\nThree")

            imgui.button("HOP##1"); imgui.same_line()
            imgui.text("Banana"); imgui.same_line()
            imgui.text("Hello\nWorld"); imgui.same_line()
            imgui.text("Banana")

            imgui.button("HOP##2"); imgui.same_line()
            imgui.text("Hello\nWorld"); imgui.same_line()
            imgui.text("Banana")
            imgui.unindent()

        imgui.spacing()

        with indented_block():
            imgui.bullet_text("Misc items:")
            imgui.indent()

            imgui.button("80x80", ImVec2(80, 80))
            imgui.same_line()
            imgui.button("50x50", ImVec2(50, 50))
            imgui.same_line()
            imgui.button("Button()")
            imgui.same_line()
            imgui.small_button("SmallButton()")

            spacing = imgui.get_style().item_inner_spacing.x
            imgui.button("Button##1")
            imgui.same_line(0.0, spacing)
            if imgui.tree_node_ex("Node##1", imgui.TreeNodeFlags_.draw_lines_none):
                for i in range(6):
                    imgui.bullet_text(f"Item {i}..")
                imgui.tree_pop()

            padding = int(imgui.get_font_size() * 1.20)
            imgui.push_style_var_y(imgui.StyleVar_.frame_padding, padding)
            imgui.button("Button##2")
            imgui.pop_style_var()
            imgui.same_line(0.0, spacing)
            if imgui.tree_node_ex("Node##2", imgui.TreeNodeFlags_.draw_lines_none):
                imgui.tree_pop()

            imgui.align_text_to_frame_padding()
            node_open = imgui.tree_node("Node##3")
            imgui.same_line(0.0, spacing); imgui.button("Button##3")
            if node_open:
                for i in range(6):
                    imgui.bullet_text(f"Item {i}..")
                imgui.tree_pop()

            imgui.button("Button##4")
            imgui.same_line(0.0, spacing)
            imgui.bullet_text("Bullet text")

            imgui.align_text_to_frame_padding()
            imgui.bullet_text("Node")
            imgui.same_line(0.0, spacing); imgui.button("Button##5")
            imgui.unindent()

        imgui.tree_pop()

    # Scrolling
    if imgui.tree_node("Scrolling"):
        # Vertical scroll functions
        IMGUI_DEMO_MARKER("Layout/Scrolling/Vertical")
        help_marker("Use SetScrollHereY() or SetScrollFromPosY() to scroll to a given vertical position.")

        if not hasattr(static, "track_item"): static.track_item = 50
        if not hasattr(static, "enable_track"): static.enable_track = True
        if not hasattr(static, "enable_extra_decorations"): static.enable_extra_decorations = False
        if not hasattr(static, "scroll_to_off_px"): static.scroll_to_off_px = 0.0
        if not hasattr(static, "scroll_to_pos_px"): static.scroll_to_pos_px = 200.0

        _, static.enable_extra_decorations = imgui.checkbox("Decoration", static.enable_extra_decorations)
        _, static.enable_track = imgui.checkbox("Track", static.enable_track)
        imgui.push_item_width(100)
        imgui.same_line(140)
        changed, static.track_item = imgui.drag_int("##item", static.track_item, 0.25, 0, 99, "Item = %d")
        static.enable_track |= changed

        scroll_to_off = imgui.button("Scroll Offset")
        imgui.same_line(140)
        changed, static.scroll_to_off_px = imgui.drag_float("##off", static.scroll_to_off_px, 1.00, 0, float("inf"), "+%.0f px")
        scroll_to_off |= changed

        scroll_to_pos = imgui.button("Scroll To Pos")
        imgui.same_line(140)
        changed, static.scroll_to_pos_px = imgui.drag_float("##pos", static.scroll_to_pos_px, 1.00, -10, float("inf"), "X/Y = %.0f px")
        scroll_to_pos |= changed
        imgui.pop_item_width()

        if scroll_to_off or scroll_to_pos:
            static.enable_track = False

        style = imgui.get_style()
        child_w = (imgui.get_content_region_avail().x - 4 * style.item_spacing.x) / 5
        if child_w < 1.0:
            child_w = 1.0
        imgui.push_id("##VerticalScrolling")
        for i in range(5):
            if i > 0:
                imgui.same_line()
            imgui.begin_group()
            names = ["Top", "25%", "Center", "75%", "Bottom"]
            imgui.text_unformatted(names[i])

            child_flags = imgui.WindowFlags_.menu_bar if static.enable_extra_decorations else 0
            child_id = imgui.get_id(f"{i}")
            child_is_visible = imgui.begin_child(child_id, ImVec2(child_w, 200.0), True, child_flags)
            if imgui.begin_menu_bar():
                imgui.text_unformatted("abc")
                imgui.end_menu_bar()
            if scroll_to_off:
                imgui.set_scroll_y(static.scroll_to_off_px)
            if scroll_to_pos:
                imgui.set_scroll_from_pos_y(imgui.get_cursor_start_pos().y + static.scroll_to_pos_px, i * 0.25)
            if child_is_visible:
                for item in range(100):
                    if static.enable_track and item == static.track_item:
                        imgui.text_colored(ImVec4(1, 1, 0, 1), f"Item {item}")
                        imgui.set_scroll_here_y(i * 0.25)
                    else:
                        imgui.text(f"Item {item}")
            scroll_y = imgui.get_scroll_y()
            scroll_max_y = imgui.get_scroll_max_y()
            imgui.end_child()
            imgui.text(f"{scroll_y:.0f}/{scroll_max_y:.0f}")
            imgui.end_group()
        imgui.pop_id()

        # Horizontal scroll functions
        IMGUI_DEMO_MARKER("Layout/Scrolling/Horizontal")
        imgui.spacing()
        help_marker(
            "Use SetScrollHereX() or SetScrollFromPosX() to scroll to a given horizontal position.\n\n"
            "Because the clipping rectangle of most window hides half worth of WindowPadding on the "
            "left/right, using SetScrollFromPosX(+1) will usually result in clipped text whereas the "
            "equivalent SetScrollFromPosY(+1) wouldn't.")
        imgui.push_id("##HorizontalScrolling")
        for i in range(5):
            child_height = imgui.get_text_line_height() + style.scrollbar_size + style.window_padding.y * 2.0
            child_flags = imgui.WindowFlags_.horizontal_scrollbar | (imgui.WindowFlags_.always_vertical_scrollbar if static.enable_extra_decorations else 0)
            child_id = imgui.get_id(str(i))
            child_is_visible = imgui.begin_child(child_id, ImVec2(-100, child_height), True, child_flags)
            if scroll_to_off:
                imgui.set_scroll_x(static.scroll_to_off_px)
            if scroll_to_pos:
                imgui.set_scroll_from_pos_x(imgui.get_cursor_start_pos().x + static.scroll_to_pos_px, i * 0.25)
            if child_is_visible:
                for item in range(100):
                    if item > 0:
                        imgui.same_line()
                    if static.enable_track and item == static.track_item:
                        imgui.text_colored(ImVec4(1, 1, 0, 1), f"Item {item}")
                        imgui.set_scroll_here_x(i * 0.25)  # 0.0:left, 0.5:center, 1.0:right
                    else:
                        imgui.text(f"Item {item}")
            scroll_x = imgui.get_scroll_x()
            scroll_max_x = imgui.get_scroll_max_x()
            imgui.end_child()
            imgui.same_line()
            names = ["Left", "25%", "Center", "75%", "Right"]
            imgui.text(f"{names[i]}\n{scroll_x:.0f}/{scroll_max_x:.0f}")
            imgui.spacing()
        imgui.pop_id()

        # Horizontal scrolling (more)
        IMGUI_DEMO_MARKER("Layout/Scrolling/Horizontal (more)")
        help_marker(
            "Horizontal scrolling for a window is enabled via the ImGuiWindowFlags_HorizontalScrollbar flag.\n\n"
            "You may want to also explicitly specify content width by using SetNextWindowContentWidth() before Begin().")
        if not hasattr(static, "hscroll_lines"): static.hscroll_lines = 7
        _, static.hscroll_lines = imgui.slider_int("Lines", static.hscroll_lines, 1, 15)
        imgui.push_style_var(imgui.StyleVar_.frame_rounding, 3.0)
        imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(2.0, 1.0))
        scrolling_child_size = ImVec2(0, imgui.get_frame_height_with_spacing() * 7 + 30)
        imgui.begin_child("scrolling", scrolling_child_size, imgui.ChildFlags_.borders, imgui.WindowFlags_.horizontal_scrollbar)
        for line in range(static.hscroll_lines):
            num_buttons = 10 + ((line * 9) if (line & 1) else (line * 3))
            for n in range(num_buttons):
                if n > 0: imgui.same_line()
                imgui.push_id(n + line * 1000)
                if not (n % 15): label = "FizzBuzz"
                elif not (n % 3): label = "Fizz"
                elif not (n % 5): label = "Buzz"
                else: label = str(n)
                hue = n * 0.05
                r, g, b = imgui.color_convert_hsv_to_rgb(hue, 0.6, 0.6, 0, 0, 0)
                imgui.push_style_color(imgui.Col_.button, ImVec4(r, g, b, 1))
                r2, g2, b2 = imgui.color_convert_hsv_to_rgb(hue, 0.7, 0.7, 0, 0, 0)
                imgui.push_style_color(imgui.Col_.button_hovered, ImVec4(r2, g2, b2, 1))
                r3, g3, b3 = imgui.color_convert_hsv_to_rgb(hue, 0.8, 0.8, 0, 0, 0)
                imgui.push_style_color(imgui.Col_.button_active, ImVec4(r3, g3, b3, 1))
                imgui.button(label, ImVec2(40.0 + math.sin(float(line + n)) * 20.0, 0.0))
                imgui.pop_style_color(3)
                imgui.pop_id()
        scroll_x = imgui.get_scroll_x()
        scroll_max_x = imgui.get_scroll_max_x()
        imgui.end_child()
        imgui.pop_style_var(2)
        scroll_x_delta = 0.0
        imgui.small_button("<<")
        if imgui.is_item_active():
            scroll_x_delta = -imgui.get_io().delta_time * 1000.0
        imgui.same_line()
        imgui.text("Scroll from code"); imgui.same_line()
        imgui.small_button(">>")
        if imgui.is_item_active():
            scroll_x_delta = +imgui.get_io().delta_time * 1000.0
        imgui.same_line()
        imgui.text(f"{scroll_x:.0f}/{scroll_max_x:.0f}")
        if scroll_x_delta != 0.0:
            imgui.begin_child("scrolling")
            imgui.set_scroll_x(imgui.get_scroll_x() + scroll_x_delta)
            imgui.end_child()
        imgui.spacing()

        # Horizontal contents size demo window
        if not hasattr(static, "show_hcsd_window"): static.show_hcsd_window = False
        _, static.show_hcsd_window = imgui.checkbox("Show Horizontal contents size demo window", static.show_hcsd_window)

        if static.show_hcsd_window:
            if not hasattr(static, "hcsd_show_h_scrollbar"): static.hcsd_show_h_scrollbar = True
            if not hasattr(static, "hcsd_show_button"): static.hcsd_show_button = True
            if not hasattr(static, "hcsd_show_tree_nodes"): static.hcsd_show_tree_nodes = True
            if not hasattr(static, "hcsd_show_text_wrapped"): static.hcsd_show_text_wrapped = False
            if not hasattr(static, "hcsd_show_columns"): static.hcsd_show_columns = True
            if not hasattr(static, "hcsd_show_tab_bar"): static.hcsd_show_tab_bar = True
            if not hasattr(static, "hcsd_show_child"): static.hcsd_show_child = False
            if not hasattr(static, "hcsd_explicit_content_size"): static.hcsd_explicit_content_size = False
            if not hasattr(static, "hcsd_contents_size_x"): static.hcsd_contents_size_x = 300.0
            if static.hcsd_explicit_content_size:
                imgui.set_next_window_content_size(ImVec2(static.hcsd_contents_size_x, 0.0))
            window_visible, static.show_hcsd_window = imgui.begin("Horizontal contents size demo window", static.show_hcsd_window, imgui.WindowFlags_.horizontal_scrollbar if static.hcsd_show_h_scrollbar else 0)
            IMGUI_DEMO_MARKER("Layout/Scrolling/Horizontal contents size demo window")
            imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(2, 0))
            imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(2, 0))
            help_marker(
                "Test how different widgets react and impact the work rectangle growing when horizontal scrolling is enabled.\n\n"
                "Use 'Metrics->Tools->Show windows rectangles' to visualize rectangles.")
            _, static.hcsd_show_h_scrollbar = imgui.checkbox("H-scrollbar", static.hcsd_show_h_scrollbar)
            _, static.hcsd_show_button = imgui.checkbox("Button", static.hcsd_show_button)
            _, static.hcsd_show_tree_nodes = imgui.checkbox("Tree nodes", static.hcsd_show_tree_nodes)
            _, static.hcsd_show_text_wrapped = imgui.checkbox("Text wrapped", static.hcsd_show_text_wrapped)
            _, static.hcsd_show_columns = imgui.checkbox("Columns", static.hcsd_show_columns)
            _, static.hcsd_show_tab_bar = imgui.checkbox("Tab bar", static.hcsd_show_tab_bar)
            _, static.hcsd_show_child = imgui.checkbox("Child", static.hcsd_show_child)
            _, static.hcsd_explicit_content_size = imgui.checkbox("Explicit content size", static.hcsd_explicit_content_size)
            imgui.text(f"Scroll {imgui.get_scroll_x():.1f}/{imgui.get_scroll_max_x():.1f} {imgui.get_scroll_y():.1f}/{imgui.get_scroll_max_y():.1f}")
            if static.hcsd_explicit_content_size:
                imgui.same_line()
                imgui.set_next_item_width(imgui.calc_text_size("123456").x)
                _, static.hcsd_contents_size_x = imgui.drag_float("##csx", static.hcsd_contents_size_x)
                p = imgui.get_cursor_screen_pos()
                draw_list = imgui.get_window_draw_list()
                draw_list.add_rect_filled(p, ImVec2(p.x + 10, p.y + 10), imgui.get_color_u32(ImVec4(1, 1, 1, 1)))
                draw_list.add_rect_filled(ImVec2(p.x + static.hcsd_contents_size_x - 10, p.y), ImVec2(p.x + static.hcsd_contents_size_x, p.y + 10), imgui.get_color_u32(ImVec4(1, 1, 1, 1)))
                imgui.dummy(ImVec2(0, 10))
            imgui.pop_style_var(2)
            imgui.separator()
            if static.hcsd_show_button:
                imgui.button("this is a 300-wide button", ImVec2(300, 0))
            if static.hcsd_show_tree_nodes:
                if imgui.tree_node("this is a tree node"):
                    if imgui.tree_node("another one of those tree node..."):
                        imgui.text("Some tree contents")
                        imgui.tree_pop()
                    imgui.tree_pop()
                if not hasattr(static, "hcsd_open"): static.hcsd_open = True
                _, static.hcsd_open = imgui.collapsing_header("CollapsingHeader", static.hcsd_open)
            if static.hcsd_show_text_wrapped:
                imgui.text_wrapped("This text should automatically wrap on the edge of the work rectangle.")
            if static.hcsd_show_columns:
                imgui.text("Tables:")
                if imgui.begin_table("table", 4, imgui.TableFlags_.borders):
                    for n in range(4):
                        imgui.table_next_column()
                        imgui.text(f"Width {imgui.get_content_region_avail().x:.2f}")
                    imgui.end_table()
                imgui.text("Columns:")
                imgui.columns(4)
                for n in range(4):
                    imgui.text(f"Width {imgui.get_column_width():.2f}")
                    imgui.next_column()
                imgui.columns(1)
            if static.hcsd_show_tab_bar and imgui.begin_tab_bar("Hello"):
                if imgui.begin_tab_item("OneOneOne")[0]: imgui.end_tab_item()
                if imgui.begin_tab_item("TwoTwoTwo")[0]: imgui.end_tab_item()
                if imgui.begin_tab_item("ThreeThreeThree")[0]: imgui.end_tab_item()
                if imgui.begin_tab_item("FourFourFour")[0]: imgui.end_tab_item()
                imgui.end_tab_bar()
            if static.hcsd_show_child:
                imgui.begin_child("child", ImVec2(0, 0), imgui.ChildFlags_.borders)
                imgui.end_child()
            imgui.end()

        imgui.tree_pop()

    if imgui.tree_node("Text Clipping"):
        IMGUI_DEMO_MARKER("Layout/Text Clipping")
        if not hasattr(static, "tc_size"): static.tc_size = [100.0, 100.0]
        if not hasattr(static, "tc_offset"): static.tc_offset = [30.0, 30.0]
        _, static.tc_size = imgui.drag_float2("size", static.tc_size, 0.5, 1.0, 200.0, "%.0f")
        imgui.text_wrapped("(Click and drag to scroll)")

        help_marker(
            "(Left) Using ImGui::PushClipRect():\n"
            "Will alter ImGui hit-testing logic + ImDrawList rendering.\n"
            "(use this if you want your clipping rectangle to affect interactions)\n\n"
            "(Center) Using ImDrawList::PushClipRect():\n"
            "Will alter ImDrawList rendering only.\n"
            "(use this as a shortcut if you are only using ImDrawList calls)\n\n"
            "(Right) Using ImDrawList::AddText() with a fine ClipRect:\n"
            "Will alter only this specific ImDrawList::AddText() rendering.\n"
            "This is often used internally to avoid altering the clipping rectangle and minimize draw calls.")

        for n in range(3):
            if n > 0:
                imgui.same_line()

            imgui.push_id(n)
            imgui.invisible_button("##canvas", static.tc_size)
            if imgui.is_item_active() and imgui.is_mouse_dragging(imgui.MouseButton_.left):
                static.tc_offset[0] += imgui.get_io().mouse_delta.x
                static.tc_offset[1] += imgui.get_io().mouse_delta.y
            imgui.pop_id()
            if not imgui.is_item_visible():
                continue

            p0 = imgui.get_item_rect_min()
            p1 = imgui.get_item_rect_max()
            text_str = "Line 1 hello\nLine 2 clip me!"
            text_pos = ImVec2(p0.x + static.tc_offset[0], p0.y + static.tc_offset[1])
            draw_list = imgui.get_window_draw_list()
            white = imgui.get_color_u32(ImVec4(1, 1, 1, 1))
            bg = imgui.get_color_u32(ImVec4(90 / 255.0, 90 / 255.0, 120 / 255.0, 1))
            if n == 0:
                imgui.push_clip_rect(p0, p1, True)
                draw_list.add_rect_filled(p0, p1, bg)
                draw_list.add_text(text_pos, white, text_str)
                imgui.pop_clip_rect()
            elif n == 1:
                draw_list.push_clip_rect(p0, p1, True)
                draw_list.add_rect_filled(p0, p1, bg)
                draw_list.add_text(text_pos, white, text_str)
                draw_list.pop_clip_rect()
            elif n == 2:
                clip_rect = ImVec4(p0.x, p0.y, p1.x, p1.y)
                draw_list.add_rect_filled(p0, p1, bg)
                draw_list.add_text(imgui.get_font(), imgui.get_font_size(), text_pos, white, text_str, None, 0.0, clip_rect)

        imgui.tree_pop()

    if imgui.tree_node("Overlap Mode"):
        IMGUI_DEMO_MARKER("Layout/Overlap Mode")
        if not hasattr(static, "enable_allow_overlap"): static.enable_allow_overlap = True

        help_marker(
            "Hit-testing is by default performed in item submission order, which generally is perceived as 'back-to-front'.\n\n"
            "By using SetNextItemAllowOverlap() you can notify that an item may be overlapped by another. "
            "Doing so alters the hovering logic: items using AllowOverlap mode requires an extra frame to accept hovered state.")
        _, static.enable_allow_overlap = imgui.checkbox("Enable AllowOverlap", static.enable_allow_overlap)

        button1_pos = imgui.get_cursor_screen_pos()
        button2_pos = ImVec2(button1_pos.x + 50.0, button1_pos.y + 50.0)
        if static.enable_allow_overlap:
            imgui.set_next_item_allow_overlap()
        imgui.button("Button 1", ImVec2(80, 80))
        imgui.set_cursor_screen_pos(button2_pos)
        imgui.button("Button 2", ImVec2(80, 80))

        if static.enable_allow_overlap:
            imgui.set_next_item_allow_overlap()
        imgui.selectable("Some Selectable", False)
        imgui.same_line()
        imgui.small_button("++")

        imgui.tree_pop()

    if imgui.tree_node("Stack Layout"):
        IMGUI_DEMO_MARKER("Layout/Stack Layout")
        if not hasattr(static, "sl_widget_a"): static.sl_widget_a = True
        if not hasattr(static, "sl_widget_b"): static.sl_widget_b = True
        if not hasattr(static, "sl_widget_c"): static.sl_widget_c = True
        if not hasattr(static, "sl_spring_a"): static.sl_spring_a = True
        if not hasattr(static, "sl_spring_ab"): static.sl_spring_ab = True
        if not hasattr(static, "sl_spring_bc"): static.sl_spring_bc = True
        if not hasattr(static, "sl_spring_c"): static.sl_spring_c = True
        if not hasattr(static, "sl_minimize_width"): static.sl_minimize_width = False
        if not hasattr(static, "sl_minimize_height"): static.sl_minimize_height = True
        if not hasattr(static, "sl_horizontal"): static.sl_horizontal = True
        if not hasattr(static, "sl_draw_springs"): static.sl_draw_springs = True
        if not hasattr(static, "sl_item_spacing"): static.sl_item_spacing = [imgui.get_style().item_spacing.x, imgui.get_style().item_spacing.y]
        if not hasattr(static, "sl_a_c_spring_weight"): static.sl_a_c_spring_weight = 0.0
        if not hasattr(static, "sl_ab_spring_weight"): static.sl_ab_spring_weight = 0.5
        if not hasattr(static, "sl_alignment"): static.sl_alignment = 0.5

        _, static.sl_widget_a = imgui.checkbox("Widget A", static.sl_widget_a); imgui.same_line()
        _, static.sl_widget_b = imgui.checkbox("Widget B", static.sl_widget_b); imgui.same_line()
        _, static.sl_widget_c = imgui.checkbox("Widget C", static.sl_widget_c)
        _, static.sl_spring_a = imgui.checkbox("Spring A", static.sl_spring_a); imgui.same_line()
        _, static.sl_spring_ab = imgui.checkbox("Spring AB", static.sl_spring_ab); imgui.same_line()
        _, static.sl_spring_bc = imgui.checkbox("Spring BC", static.sl_spring_bc); imgui.same_line()
        _, static.sl_spring_c = imgui.checkbox("Spring C", static.sl_spring_c)
        _, static.sl_horizontal = imgui.checkbox("Horizontal", static.sl_horizontal); imgui.same_line()
        _, static.sl_minimize_width = imgui.checkbox("Minimize Width", static.sl_minimize_width); imgui.same_line()
        _, static.sl_minimize_height = imgui.checkbox("Minimize Height", static.sl_minimize_height)
        _, static.sl_draw_springs = imgui.checkbox("Draw Springs", static.sl_draw_springs)
        _, static.sl_item_spacing[0 if static.sl_horizontal else 1] = imgui.drag_float("Item Spacing", static.sl_item_spacing[0 if static.sl_horizontal else 1], 0.1, 0.0, 50.0)
        _, static.sl_a_c_spring_weight = imgui.drag_float("A & C Spring Weight", static.sl_a_c_spring_weight, 0.002, 0.0, 1.0)
        _, static.sl_ab_spring_weight = imgui.drag_float("AB Spring Weight", static.sl_ab_spring_weight, 0.002, 0.0, 1.0)
        if imgui.is_item_hovered(): imgui.set_tooltip("BC Spring Weight = 1 - AB Spring Weight")
        _, static.sl_alignment = imgui.drag_float("Minor Axis Alignment", static.sl_alignment, 0.002, 0.0, 1.0)
        if imgui.is_item_hovered(): imgui.set_tooltip("This is vertical alignment for horizontal layouts and horizontal alignment for vertical layouts.")
        imgui.text("Layout widgets:")
        imgui.text("| Spring A | Widget A | Spring AB | Widget B | Spring BC | Widget C | Spring C |")

        imgui.spacing()

        avail_w = imgui.get_content_region_avail().x
        widget_w = int(avail_w / 4)
        widget_h = int(widget_w / 3) if static.sl_horizontal else widget_w
        widget_size = ImVec2(widget_w, widget_h)

        small_widget_size = ImVec2(widget_w, int(widget_h / 2)) if static.sl_horizontal else ImVec2(int(widget_w / 2), widget_h)

        layout_w = widget_w * 4 if not static.sl_minimize_width else 0.0
        layout_h = widget_h * 4 if not static.sl_minimize_height else 0.0
        layout_size = ImVec2(layout_w, layout_h)

        imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(int(static.sl_item_spacing[0]), int(static.sl_item_spacing[1])))

        if static.sl_horizontal:
            imgui.begin_horizontal("h1", layout_size, static.sl_alignment)
        else:
            imgui.begin_vertical("v1", layout_size, static.sl_alignment)
        if static.sl_spring_a: imgui.spring(static.sl_a_c_spring_weight)
        if static.sl_widget_a: imgui.button("Widget A", widget_size)
        if static.sl_spring_ab: imgui.spring(static.sl_ab_spring_weight)
        if static.sl_widget_b: imgui.button("Widget B", small_widget_size)
        if static.sl_spring_bc: imgui.spring(1.0 - static.sl_ab_spring_weight)
        if static.sl_widget_c: imgui.button("Widget C", widget_size)
        if static.sl_spring_c: imgui.spring(static.sl_a_c_spring_weight)
        if static.sl_horizontal:
            imgui.end_horizontal()
        else:
            imgui.end_vertical()

        imgui.pop_style_var()

        draw_list = imgui.get_window_draw_list()
        draw_list.add_rect(imgui.get_item_rect_min(), imgui.get_item_rect_max(), imgui.get_color_u32(imgui.Col_.border))

        imgui.tree_pop()


def show_demo_window_popups():
    static = show_demo_window

    if not imgui.collapsing_header("Popups & Modal windows"):
        return

    # The properties of popups windows are:
    # - They block normal mouse hovering detection outside them. (*)
    # - Unless modal, they can be closed by clicking anywhere outside them, or by pressing ESCAPE.
    # - Their visibility state (~bool) is held internally by Dear ImGui instead of being held by the programmer as
    #   we are used to with regular Begin() calls. User can manipulate the visibility state by calling OpenPopup().
    # (*) One can use IsItemHovered(ImGuiHoveredFlags_AllowWhenBlockedByPopup) to bypass it and detect hovering even
    #     when normally blocked by a popup.
    # Those three properties are connected. The library needs to hold their visibility state BECAUSE it can close
    # popups at any time.

    # Typical use for regular windows:
    #   bool my_tool_is_active = false; if (ImGui::Button("Open")) my_tool_is_active = true; [...] if (my_tool_is_active) Begin("My Tool", &my_tool_is_active) { [...] } End();
    # Typical use for popups:
    #   if (ImGui::Button("Open")) ImGui::OpenPopup("MyPopup"); if (ImGui::BeginPopup("MyPopup") { [...] EndPopup(); }

    # With popups we have to go through a library call (here OpenPopup) to manipulate the visibility state.
    # This may be a bit confusing at first but it should quickly make sense. Follow on the examples below.

    if imgui.tree_node("Popups"):
        IMGUI_DEMO_MARKER("Popups/Popups")
        imgui.text_wrapped(
            "When a popup is active, it inhibits interacting with windows that are behind the popup. "
            "Clicking outside the popup closes it.")

        if not hasattr(static, "selected_fish"): static.selected_fish = -1
        names = ["Bream", "Haddock", "Mackerel", "Pollock", "Tilefish"]
        toggles = [True, False, False, False, False]

        # Simple selection popup (if you want to show the current selection inside the Button itself,
        # you may want to build a string using the "###" operator to preserve a constant ID with a variable label)
        if imgui.button("Select.."):
            imgui.open_popup("my_select_popup")
        imgui.same_line()
        imgui.text_unformatted("<None>" if static.selected_fish == -1 else names[static.selected_fish])
        if imgui.begin_popup("my_select_popup"):
            imgui.separator_text("Aquarium")
            for i in range(len(names)):
                _, selected = imgui.selectable(names[i], i == static.selected_fish)
                if selected:
                    static.selected_fish = i
            imgui.end_popup()

        # Showing a menu with toggles
        if imgui.button("Toggle.."):
            imgui.open_popup("my_toggle_popup")
        if imgui.begin_popup("my_toggle_popup"):
            for i in range(len(names)):
                imgui.menu_item(names[i], "", toggles[i])
            if imgui.begin_menu("Sub-menu"):
                imgui.menu_item("Click me", "", False)
                imgui.end_menu()

            imgui.separator()
            imgui.text("Tooltip here")
            imgui.set_item_tooltip("I am a tooltip over a popup")

            if imgui.button("Stacked Popup"):
                imgui.open_popup("another popup")
            if imgui.begin_popup("another popup"):
                for i in range(len(names)):
                    imgui.menu_item(names[i], "", toggles[i])
                if imgui.begin_menu("Sub-menu"):
                    imgui.menu_item("Click me", "", False)
                    if imgui.button("Stacked Popup"):
                        imgui.open_popup("another popup")
                    if imgui.begin_popup("another popup"):
                        imgui.text("I am the last one here.")
                        imgui.end_popup()
                    imgui.end_menu()
                imgui.end_popup()
            imgui.end_popup()

        imgui.tree_pop()

    # Context menus
    if imgui.tree_node("Context menus"):
        IMGUI_DEMO_MARKER("Popups/Context menus")
        help_marker("\"Context\" functions are simple helpers to associate a Popup to a given Item or Window identifier.")

        # Example 1
        # When used after an item that has an ID (e.g. Button), we can skip providing an ID to BeginPopupContextItem(),
        # and BeginPopupContextItem() will use the last item ID as the popup ID.
        names = ["Label1", "Label2", "Label3", "Label4", "Label5"]
        selected_2 = -1
        for n in range(5):
            if imgui.selectable(names[n], selected_2 == n):
                selected_2 = n
            if imgui.begin_popup_context_item():  # <-- use last item id as popup id
                selected_2 = n   # type: ignore
                imgui.text(f"This a popup for \"{names[n]}\"!")
                if imgui.button("Close"):
                    imgui.close_current_popup()
                imgui.end_popup()
            imgui.set_item_tooltip("Right-click to open popup")

        imgui.tree_pop()

    # Modals
    if imgui.tree_node("Modals"):
        IMGUI_DEMO_MARKER("Popups/Modals")
        imgui.text_wrapped("Modal windows are like popups but the user cannot close them by clicking outside.")

        if imgui.button("Delete.."):
            imgui.open_popup("Delete?")

        # Always center this window when appearing
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing, ImVec2(0.5, 0.5))

        if not hasattr(static, "dont_ask_me_next_time"):
            static.dont_ask_me_next_time = False  # Equivalent to static bool dont_ask_me_next_time = false;

        if imgui.begin_popup_modal("Delete?", None, imgui.WindowFlags_.always_auto_resize)[0]:
            imgui.text("All those beautiful files will be deleted.\nThis operation cannot be undone!")
            imgui.separator()

            imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(0, 0))
            _, static.dont_ask_me_next_time = imgui.checkbox("Don't ask me next time", static.dont_ask_me_next_time)
            imgui.pop_style_var()

            if imgui.button("OK", ImVec2(120, 0)):
                imgui.close_current_popup()
            imgui.set_item_default_focus()
            imgui.same_line()
            if imgui.button("Cancel", ImVec2(120, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

        if imgui.button("Stacked modals.."):
            imgui.open_popup("Stacked 1")
        if imgui.begin_popup_modal("Stacked 1", None, imgui.WindowFlags_.menu_bar)[0]:
            if imgui.begin_menu_bar():
                if imgui.begin_menu("File"):
                    if imgui.menu_item_simple("Some menu item"):
                        pass
                    imgui.end_menu()
                imgui.end_menu_bar()
            imgui.text("Hello from Stacked The First\nUsing style.Colors[ImGuiCol_ModalWindowDimBg] behind it.")

            # Testing behavior of widgets stacking their own regular popups over the modal.
            if not hasattr(static, "item"):
                static.item = 1  # Equivalent to static int item = 1;

            if not hasattr(static, "color"):
                static.color = [0.4, 0.7, 0.0, 0.5]  # Equivalent to static float color[4] = { 0.4f, 0.7f, 0.0f, 0.5f };

            imgui.combo("Combo", static.item, "aaaa\0bbbb\0cccc\0dddd\0eeee\0\0")
            imgui.color_edit4("color", static.color)

            if imgui.button("Add another modal.."):
                imgui.open_popup("Stacked 2")

            # Also demonstrate passing a bool* to BeginPopupModal(), this will create a regular close button which
            # will close the popup. Note that the visibility state of popups is owned by imgui, so the input value
            # of the bool actually doesn't matter here.
            if not hasattr(static, "unused_open"):
                static.unused_open = True  # Equivalent to static bool unused_open = true;

            if imgui.begin_popup_modal("Stacked 2", static.unused_open)[0]:
                imgui.text("Hello from Stacked The Second!")
                if imgui.button("Close"):
                    imgui.close_current_popup()
                imgui.end_popup()

            if imgui.button("Close"):
                imgui.close_current_popup()
            imgui.end_popup()

        imgui.tree_pop()

    if imgui.tree_node("Menus inside a regular window"):
        IMGUI_DEMO_MARKER("Popups/Menus inside a regular window")
        imgui.text_wrapped("Below we are testing adding menu items to a regular window. It's rather unusual but should work!")
        imgui.separator()

        imgui.menu_item_simple("Menu item", "Ctrl+M")
        if imgui.begin_menu("Menu inside a regular window"):
            show_example_menu_file()
            imgui.end_menu()
        imgui.separator()
        imgui.tree_pop()


def show_demo_window_inputs():
    if imgui.collapsing_header("Inputs & Focus"):
        io = imgui.get_io()

        # Display inputs submitted to ImGuiIO
        IMGUI_DEMO_MARKER("Inputs & Focus/Inputs")
        imgui.set_next_item_open(True, imgui.Cond_.once)
        if imgui.tree_node("Inputs"):
            help_marker(
                "This is a simplified view. See more detailed input state:\n"
                "- in 'Tools->Metrics/Debugger->Inputs'.\n"
                "- in 'Tools->Debug Log->IO'.")
            if imgui.is_mouse_pos_valid():
                imgui.text("Mouse pos: (%g, %g)" % (io.mouse_pos.x, io.mouse_pos.y))
            else:
                imgui.text("Mouse pos: <INVALID>")
            imgui.text("Mouse delta: (%g, %g)" % (io.mouse_delta.x, io.mouse_delta.y))
            imgui.text("Mouse down:")
            for i in range(len(io.mouse_down)):
                if imgui.is_mouse_down(i):
                    imgui.same_line()
                    imgui.text("b%d (%.02f secs)" % (i, io.mouse_down_duration[i]))
            imgui.text("Mouse wheel: %.1f" % io.mouse_wheel)
            imgui.tree_pop()

        # Display ImGuiIO output flags
        IMGUI_DEMO_MARKER("Inputs & Focus/Outputs")
        imgui.set_next_item_open(True, imgui.Cond_.once)
        if imgui.tree_node("Outputs"):
            help_marker(
                "The value of io.WantCaptureMouse and io.WantCaptureKeyboard are normally set by Dear ImGui "
                "to instruct your application of how to route inputs. Typically, when a value is true, it means "
                "Dear ImGui wants the corresponding inputs and we expect the underlying application to ignore them.\n\n"
                "The most typical case is: when hovering a window, Dear ImGui set io.WantCaptureMouse to true, "
                "and underlying application should ignore mouse inputs (in practice there are many and more subtle "
                "rules leading to how those flags are set).")
            imgui.text("io.WantCaptureMouse: %d" % io.want_capture_mouse)
            imgui.text("io.WantCaptureMouseUnlessPopupClose: %d" % io.want_capture_mouse_unless_popup_close)
            imgui.text("io.WantCaptureKeyboard: %d" % io.want_capture_keyboard)
            imgui.text("io.WantTextInput: %d" % io.want_text_input)
            imgui.text("io.WantSetMousePos: %d" % io.want_set_mouse_pos)
            imgui.text("io.NavActive: %d, io.NavVisible: %d" % (io.nav_active, io.nav_visible))

            if imgui.tree_node("WantCapture override"):
                IMGUI_DEMO_MARKER("Inputs & Focus/Outputs/WantCapture override")
                help_marker(
                    "Hovering the colored canvas will override io.WantCaptureXXX fields.\n"
                    "Notice how normally (when set to none), the value of io.WantCaptureKeyboard would be false when hovering and true when clicking.")
                capture_override_mouse = -1
                capture_override_keyboard = -1
                capture_override_desc = ["None", "Set to false", "Set to true"]
                imgui.set_next_item_width(imgui.get_font_size() * 15)
                imgui.slider_int("SetNextFrameWantCaptureMouse() on hover", capture_override_mouse, -1, +1, capture_override_desc[capture_override_mouse + 1], imgui.SliderFlags_.always_clamp)
                imgui.set_next_item_width(imgui.get_font_size() * 15)
                imgui.slider_int("SetNextFrameWantCaptureKeyboard() on hover", capture_override_keyboard, -1, +1, capture_override_desc[capture_override_keyboard + 1], imgui.SliderFlags_.always_clamp)

                imgui.color_button("##panel", ImVec4(0.7, 0.1, 0.7, 1.0), imgui.ColorEditFlags_.no_tooltip | imgui.ColorEditFlags_.no_drag_drop, ImVec2(128.0, 96.0)) # Dummy item
                if imgui.is_item_hovered() and capture_override_mouse != -1:
                    imgui.set_next_frame_want_capture_mouse(capture_override_mouse == 1)
                if imgui.is_item_hovered() and capture_override_keyboard != -1:
                    imgui.set_next_frame_want_capture_keyboard(capture_override_keyboard == 1)

                imgui.tree_pop()
            imgui.tree_pop()

        if imgui.tree_node("Shortcuts"):
            IMGUI_DEMO_MARKER("Inputs & Focus/Shortcuts")
            static = show_demo_window_inputs
            if not hasattr(static, "sc_route_options"):
                static.sc_route_options = imgui.InputFlags_.repeat.value
                static.sc_route_type = imgui.InputFlags_.route_focused.value
                static.sc_f = 0.5

            _, static.sc_route_options = imgui.checkbox_flags("ImGuiInputFlags_Repeat", static.sc_route_options, imgui.InputFlags_.repeat)
            if imgui.radio_button("ImGuiInputFlags_RouteActive", static.sc_route_type == imgui.InputFlags_.route_active):
                static.sc_route_type = imgui.InputFlags_.route_active.value
            if imgui.radio_button("ImGuiInputFlags_RouteFocused (default)", static.sc_route_type == imgui.InputFlags_.route_focused):
                static.sc_route_type = imgui.InputFlags_.route_focused.value
            imgui.indent()
            imgui.begin_disabled(static.sc_route_type != imgui.InputFlags_.route_focused)
            _, static.sc_route_options = imgui.checkbox_flags("ImGuiInputFlags_RouteOverActive##0", static.sc_route_options, imgui.InputFlags_.route_over_active)
            imgui.end_disabled()
            imgui.unindent()
            if imgui.radio_button("ImGuiInputFlags_RouteGlobal", static.sc_route_type == imgui.InputFlags_.route_global):
                static.sc_route_type = imgui.InputFlags_.route_global.value
            imgui.indent()
            imgui.begin_disabled(static.sc_route_type != imgui.InputFlags_.route_global)
            _, static.sc_route_options = imgui.checkbox_flags("ImGuiInputFlags_RouteOverFocused", static.sc_route_options, imgui.InputFlags_.route_over_focused)
            _, static.sc_route_options = imgui.checkbox_flags("ImGuiInputFlags_RouteOverActive", static.sc_route_options, imgui.InputFlags_.route_over_active)
            _, static.sc_route_options = imgui.checkbox_flags("ImGuiInputFlags_RouteUnlessBgFocused", static.sc_route_options, imgui.InputFlags_.route_unless_bg_focused)
            imgui.end_disabled()
            imgui.unindent()
            if imgui.radio_button("ImGuiInputFlags_RouteAlways", static.sc_route_type == imgui.InputFlags_.route_always):
                static.sc_route_type = imgui.InputFlags_.route_always.value
            flags = static.sc_route_type | static.sc_route_options
            if static.sc_route_type != imgui.InputFlags_.route_global:
                flags &= ~(imgui.InputFlags_.route_over_focused | imgui.InputFlags_.route_over_active | imgui.InputFlags_.route_unless_bg_focused)

            imgui.separator_text("Using SetNextItemShortcut()")
            imgui.text("Ctrl+S")
            imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.s, flags | imgui.InputFlags_.tooltip)
            imgui.button("Save")
            imgui.text("Alt+F")
            imgui.set_next_item_shortcut(imgui.Key.mod_alt | imgui.Key.f, flags | imgui.InputFlags_.tooltip)
            _, static.sc_f = imgui.slider_float("Factor", static.sc_f, 0.0, 1.0)

            imgui.separator_text("Using Shortcut()")
            line_height = imgui.get_text_line_height_with_spacing()
            key_chord = imgui.Key.mod_ctrl | imgui.Key.a

            imgui.text("Ctrl+A")
            imgui.text(f"IsWindowFocused: {int(imgui.is_window_focused())}, Shortcut: {'PRESSED' if imgui.shortcut(key_chord, flags) else '...'}")

            imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(1.0, 0.0, 1.0, 0.1))

            imgui.begin_child("WindowA", ImVec2(-imgui.FLT_MIN, line_height * 14), True)
            imgui.text("Press Ctrl+A and see who receives it!")
            imgui.separator()

            imgui.text("(in WindowA)")
            imgui.text(f"IsWindowFocused: {int(imgui.is_window_focused())}, Shortcut: {'PRESSED' if imgui.shortcut(key_chord, flags) else '...'}")

            # Dummy child is not claiming the route
            imgui.begin_child("ChildD", ImVec2(-imgui.FLT_MIN, line_height * 4), True)
            imgui.text("(in ChildD: not using same Shortcut)")
            imgui.text(f"IsWindowFocused: {int(imgui.is_window_focused())}")
            imgui.end_child()

            # Child window polling for Ctrl+A
            imgui.begin_child("ChildE", ImVec2(-imgui.FLT_MIN, line_height * 4), True)
            imgui.text("(in ChildE: using same Shortcut)")
            imgui.text(f"IsWindowFocused: {int(imgui.is_window_focused())}, Shortcut: {'PRESSED' if imgui.shortcut(key_chord, flags) else '...'}")
            imgui.end_child()

            # In a popup
            if imgui.button("Open Popup"):
                imgui.open_popup("PopupF")
            if imgui.begin_popup("PopupF"):
                imgui.text("(in PopupF)")
                imgui.text(f"IsWindowFocused: {int(imgui.is_window_focused())}, Shortcut: {'PRESSED' if imgui.shortcut(key_chord, flags) else '...'}")
                imgui.end_popup()
            imgui.end_child()
            imgui.pop_style_color()

            imgui.tree_pop()

        # Display mouse cursors
        if imgui.tree_node("Mouse Cursors"):
            IMGUI_DEMO_MARKER("Inputs & Focus/Mouse Cursors")
            mouse_cursors_names = ["Arrow", "TextInput", "ResizeAll", "ResizeNS", "ResizeEW", "ResizeNESW", "ResizeNWSE", "Hand", "Wait", "Progress", "NotAllowed"]

            current = imgui.get_mouse_cursor()
            cursor_name = mouse_cursors_names[current] if 0 <= current < len(mouse_cursors_names) else "N/A"
            imgui.text(f"Current mouse cursor = {current}: {cursor_name}")
            imgui.begin_disabled(True)
            imgui.checkbox_flags("io.BackendFlags: HasMouseCursors", io.backend_flags, imgui.BackendFlags_.has_mouse_cursors)
            imgui.end_disabled()

            imgui.text("Hover to see mouse cursors:")
            imgui.same_line()
            help_marker(
                "Your application can render a different mouse cursor based on what ImGui::GetMouseCursor() returns. "
                "If software cursor rendering (io.MouseDrawCursor) is set ImGui will draw the right cursor for you, "
                "otherwise your backend needs to handle it.")
            for i in range(len(mouse_cursors_names)):
                label = f"Mouse cursor {i}: {mouse_cursors_names[i]}"
                imgui.bullet()
                imgui.selectable(label, False)
                if imgui.is_item_hovered():
                    imgui.set_mouse_cursor(i)
            imgui.tree_pop()

        if imgui.tree_node("Tabbing"):
            IMGUI_DEMO_MARKER("Inputs & Focus/Tabbing")
            imgui.text("Use TAB/SHIFT+TAB to cycle through keyboard editable fields.")
            buf = "hello"
            imgui.input_text("1", buf)
            imgui.input_text("2", buf)
            imgui.input_text("3", buf)
            imgui.push_tab_stop(False)
            imgui.input_text("4 (tab skip)", buf)
            imgui.same_line()
            help_marker("Item won't be cycled through when using TAB or Shift+Tab.")
            imgui.pop_tab_stop()
            imgui.input_text("5", buf)
            imgui.tree_pop()

        if imgui.tree_node("Focus from code"):
            IMGUI_DEMO_MARKER("Inputs & Focus/Focus from code")
            focus_1 = imgui.button("Focus on 1")
            imgui.same_line()
            focus_2 = imgui.button("Focus on 2")
            imgui.same_line()
            focus_3 = imgui.button("Focus on 3")
            has_focus = 0
            buf = "click on a button to set focus"

            if focus_1:
                imgui.set_keyboard_focus_here()
            imgui.input_text("1", buf)
            if imgui.is_item_active():
                has_focus = 1

            if focus_2:
                imgui.set_keyboard_focus_here()
            imgui.input_text("2", buf)
            if imgui.is_item_active():
                has_focus = 2

            imgui.push_tab_stop(False)
            if focus_3:
                imgui.set_keyboard_focus_here()
            imgui.input_text("3 (tab skip)", buf)
            if imgui.is_item_active():
                has_focus = 3
            imgui.same_line()
            help_marker("Item won't be cycled through when using TAB or Shift+Tab.")
            imgui.pop_tab_stop()

            if has_focus:
                imgui.text("Item with focus: %d" % has_focus)
            else:
                imgui.text("Item with focus: <none>")

            # Use >= 0 parameter to SetKeyboardFocusHere() to focus an upcoming item
            f3 = [0.0, 0.0, 0.0]
            focus_ahead = -1
            if imgui.button("Focus on X"):
                focus_ahead = 0
            imgui.same_line()
            if imgui.button("Focus on Y"):
                focus_ahead = 1
            imgui.same_line()
            if imgui.button("Focus on Z"):
                focus_ahead = 2
            if focus_ahead != -1:
                imgui.set_keyboard_focus_here(focus_ahead)
            imgui.slider_float3("Float3", f3, 0.0, 1.0)

            imgui.text_wrapped("NB: Cursor & selection are preserved when refocusing last used item in code.")
            imgui.tree_pop()

        if imgui.tree_node("Dragging"):
            IMGUI_DEMO_MARKER("Inputs & Focus/Dragging")
            imgui.text_wrapped("You can use imgui.get_mouse_drag_delta(0) to query for the dragged amount on any widget.")
            for button in range(3):
                imgui.text("IsMouseDragging(%d):" % button)
                imgui.text("  w/ default threshold: %d," % imgui.is_mouse_dragging(button))
                imgui.text("  w/ zero threshold: %d," % imgui.is_mouse_dragging(button, 0.0))
                imgui.text("  w/ large threshold: %d," % imgui.is_mouse_dragging(button, 20.0))

            imgui.button("Drag Me")
            cur_pos = imgui.get_cursor_screen_pos()
            if imgui.is_item_active():
                imgui.get_foreground_draw_list().add_line(cur_pos, io.mouse_pos, imgui.get_color_u32(imgui.Col_.button), 4.0) # Draw a line between the button and the mouse cursor

            # Drag operations gets "unlocked" when the mouse has moved past a certain threshold
            # (the default threshold is stored in io.MouseDragThreshold). You can request a lower or higher
            # threshold using the second parameter of IsMouseDragging() and GetMouseDragDelta().
            value_raw = imgui.get_mouse_drag_delta(0, 0.0)
            value_with_lock_threshold = imgui.get_mouse_drag_delta(0)
            mouse_delta = io.mouse_delta
            imgui.text("GetMouseDragDelta(0):")
            imgui.text("  w/ default threshold: (%.1f, %.1f)" % (value_with_lock_threshold.x, value_with_lock_threshold.y))
            imgui.text("  w/ zero threshold: (%.1f, %.1f)" % (value_raw.x, value_raw.y))
            imgui.text("io.MouseDelta: (%.1f, %.1f)" % (mouse_delta.x, mouse_delta.y))
            imgui.tree_pop()


# Make the UI compact because there are so many fields
def push_style_compact():
    style = imgui.get_style()
    imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(style.frame_padding.x, style.frame_padding.y * 0.60))
    imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(style.item_spacing.x, style.item_spacing.y * 0.60))


def pop_style_compact():
    imgui.pop_style_var(2)


# Show a combo box with a choice of sizing policies
def edit_table_sizing_flags(flags: int) -> int:
    policies = [
        (imgui.TableFlags_.none.value, "Default",
         "Use default sizing policy:\n- ImGuiTableFlags_SizingFixedFit if ScrollX is on or if host window has ImGuiWindowFlags_AlwaysAutoResize.\n- ImGuiTableFlags_SizingStretchSame otherwise."),
        (imgui.TableFlags_.sizing_fixed_fit.value, "ImGuiTableFlags_SizingFixedFit",
         "Columns default to _WidthFixed (if resizable) or _WidthAuto (if not resizable), matching contents width."),
        (imgui.TableFlags_.sizing_fixed_same.value, "ImGuiTableFlags_SizingFixedSame",
         "Columns are all the same width, matching the maximum contents width.\nImplicitly disable ImGuiTableFlags_Resizable and enable ImGuiTableFlags_NoKeepColumnsVisible."),
        (imgui.TableFlags_.sizing_stretch_prop.value, "ImGuiTableFlags_SizingStretchProp",
         "Columns default to _WidthStretch with weights proportional to their widths."),
        (imgui.TableFlags_.sizing_stretch_same.value, "ImGuiTableFlags_SizingStretchSame",
         "Columns default to _WidthStretch with same weights."),
    ]
    sizing_mask = imgui.TableFlags_.sizing_mask_.value
    current_val = flags & sizing_mask
    idx = 0
    for i, (val, name, _) in enumerate(policies):
        if val == current_val:
            idx = i
            break
    preview = policies[idx][1] if idx < len(policies) else ""
    if idx > 0:
        preview = preview[len("ImGuiTableFlags"):]
    if imgui.begin_combo("Sizing Policy", preview):
        for n, (val, name, _) in enumerate(policies):
            if imgui.selectable(name, idx == n)[0]:
                flags = (flags & ~sizing_mask) | val
        imgui.end_combo()
    imgui.same_line()
    imgui.text_disabled("(?)")
    if imgui.begin_item_tooltip():
        imgui.push_text_wrap_pos(imgui.get_font_size() * 50.0)
        for val, name, tooltip in policies:
            imgui.separator()
            imgui.text(f"{name}:")
            imgui.separator()
            imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + imgui.get_style().indent_spacing * 0.5)
            imgui.text_unformatted(tooltip)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()
    return flags


def edit_table_columns_flags(flags: int) -> int:
    _, flags = imgui.checkbox_flags("_Disabled", flags, imgui.TableColumnFlags_.disabled); imgui.same_line(); help_marker("Master disable flag (also hide from context menu)")
    _, flags = imgui.checkbox_flags("_DefaultHide", flags, imgui.TableColumnFlags_.default_hide)
    _, flags = imgui.checkbox_flags("_DefaultSort", flags, imgui.TableColumnFlags_.default_sort)
    changed, flags = imgui.checkbox_flags("_WidthStretch", flags, imgui.TableColumnFlags_.width_stretch)
    if changed:
        flags &= ~(imgui.TableColumnFlags_.width_mask_.value ^ imgui.TableColumnFlags_.width_stretch.value)
    changed, flags = imgui.checkbox_flags("_WidthFixed", flags, imgui.TableColumnFlags_.width_fixed)
    if changed:
        flags &= ~(imgui.TableColumnFlags_.width_mask_.value ^ imgui.TableColumnFlags_.width_fixed.value)
    _, flags = imgui.checkbox_flags("_NoResize", flags, imgui.TableColumnFlags_.no_resize)
    _, flags = imgui.checkbox_flags("_NoReorder", flags, imgui.TableColumnFlags_.no_reorder)
    _, flags = imgui.checkbox_flags("_NoHide", flags, imgui.TableColumnFlags_.no_hide)
    _, flags = imgui.checkbox_flags("_NoClip", flags, imgui.TableColumnFlags_.no_clip)
    _, flags = imgui.checkbox_flags("_NoSort", flags, imgui.TableColumnFlags_.no_sort)
    _, flags = imgui.checkbox_flags("_NoSortAscending", flags, imgui.TableColumnFlags_.no_sort_ascending)
    _, flags = imgui.checkbox_flags("_NoSortDescending", flags, imgui.TableColumnFlags_.no_sort_descending)
    _, flags = imgui.checkbox_flags("_NoHeaderLabel", flags, imgui.TableColumnFlags_.no_header_label)
    _, flags = imgui.checkbox_flags("_NoHeaderWidth", flags, imgui.TableColumnFlags_.no_header_width)
    _, flags = imgui.checkbox_flags("_PreferSortAscending", flags, imgui.TableColumnFlags_.prefer_sort_ascending)
    _, flags = imgui.checkbox_flags("_PreferSortDescending", flags, imgui.TableColumnFlags_.prefer_sort_descending)
    _, flags = imgui.checkbox_flags("_IndentEnable", flags, imgui.TableColumnFlags_.indent_enable); imgui.same_line(); help_marker("Default for column 0")
    _, flags = imgui.checkbox_flags("_IndentDisable", flags, imgui.TableColumnFlags_.indent_disable); imgui.same_line(); help_marker("Default for column >0")
    _, flags = imgui.checkbox_flags("_AngledHeader", flags, imgui.TableColumnFlags_.angled_header)
    return flags


def show_table_columns_status_flags(flags: int) -> None:
    imgui.checkbox_flags("_IsEnabled", flags, imgui.TableColumnFlags_.is_enabled)
    imgui.checkbox_flags("_IsVisible", flags, imgui.TableColumnFlags_.is_visible)
    imgui.checkbox_flags("_IsSorted", flags, imgui.TableColumnFlags_.is_sorted)
    imgui.checkbox_flags("_IsHovered", flags, imgui.TableColumnFlags_.is_hovered)


# Constants for MyItem column IDs (used in Sorting and Advanced table demos)
MY_ITEM_COLUMN_ID_ID = 0
MY_ITEM_COLUMN_ID_NAME = 1
MY_ITEM_COLUMN_ID_ACTION = 2
MY_ITEM_COLUMN_ID_QUANTITY = 3
MY_ITEM_COLUMN_ID_DESCRIPTION = 4


class MyItem:
    def __init__(self, id: int = 0, name: str = "", quantity: int = 0):
        self.id = id
        self.name = name
        self.quantity = quantity

    @staticmethod
    def sort_with_sort_specs(sort_specs: imgui.TableSortSpecs, items: list) -> None:
        """Sort items list in-place according to sort_specs."""
        import functools
        def compare(a: "MyItem", b: "MyItem") -> int:
            for n in range(sort_specs.specs_count):
                spec = sort_specs.get_specs(n)
                delta = 0
                if spec.column_user_id == MY_ITEM_COLUMN_ID_ID:
                    delta = a.id - b.id
                elif spec.column_user_id == MY_ITEM_COLUMN_ID_NAME:
                    delta = (a.name > b.name) - (a.name < b.name)
                elif spec.column_user_id == MY_ITEM_COLUMN_ID_QUANTITY:
                    delta = a.quantity - b.quantity
                elif spec.column_user_id == MY_ITEM_COLUMN_ID_DESCRIPTION:
                    delta = (a.name > b.name) - (a.name < b.name)
                if delta > 0:
                    return 1 if spec.sort_direction == imgui.SortDirection_.ascending else -1
                if delta < 0:
                    return -1 if spec.sort_direction == imgui.SortDirection_.ascending else 1
            return a.id - b.id
        items.sort(key=functools.cmp_to_key(compare))


TEMPLATE_ITEMS_NAMES = [
    "Banana", "Apple", "Cherry", "Watermelon", "Grapefruit", "Strawberry", "Mango",
    "Kiwi", "Orange", "Pineapple", "Blueberry", "Plum", "Coconut", "Pear", "Apricot"
]


def show_demo_window_tables():
    static = show_demo_window_tables

    if not imgui.collapsing_header("Tables & Columns"):
        return

    # Using these as base values to create width/height that are a factor of the size of our font
    text_base_width = imgui.calc_text_size("A").x
    text_base_height = imgui.get_text_line_height_with_spacing()

    imgui.push_id("Tables")

    open_action = -1
    if imgui.button("Expand all"):
        open_action = 1
    imgui.same_line()
    if imgui.button("Collapse all"):
        open_action = 0
    imgui.same_line()

    # Options
    if not hasattr(static, "disable_indent"): static.disable_indent = False
    _, static.disable_indent = imgui.checkbox("Disable tree indentation", static.disable_indent)
    imgui.same_line()
    help_marker("Disable the indenting of tree nodes so demo tables can use the full window width.")
    imgui.separator()
    if static.disable_indent:
        imgui.push_style_var(imgui.StyleVar_.indent_spacing, 0.0)

    # About Styling of tables
    # Most settings are configured on a per-table basis via the flags passed to BeginTable() and TableSetupColumns APIs.
    # There are however a few settings that a shared and part of the ImGuiStyle structure:
    #   style.CellPadding                          # Padding within each cell
    #   style.Colors[ImGuiCol_TableHeaderBg]       # Table header background
    #   style.Colors[ImGuiCol_TableBorderStrong]   # Table outer and header borders
    #   style.Colors[ImGuiCol_TableBorderLight]    # Table inner borders
    #   style.Colors[ImGuiCol_TableRowBg]          # Table row background when ImGuiTableFlags_RowBg is enabled (even rows)
    #   style.Colors[ImGuiCol_TableRowBgAlt]       # Table row background when ImGuiTableFlags_RowBg is enabled (odds rows)

    # Demos
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Basic"):
        IMGUI_DEMO_MARKER("Tables/Basic")
        # Here we will showcase three different ways to output a table.
        # They are very simple variations of a same thing!

        # [Method 1] Using TableNextRow() to create a new row, and TableSetColumnIndex() to select the column.
        # In many situations, this is the most flexible and easy to use pattern.
        help_marker("Using TableNextRow() + calling TableSetColumnIndex() _before_ each cell, in a loop.")
        if imgui.begin_table("table1", 3):
            for row in range(4):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text("Row %d Column %d" % (row, column))
            imgui.end_table()

        # [Method 2] Using TableNextColumn() called multiple times, instead of using a for loop + TableSetColumnIndex().
        # This is generally more convenient when you have code manually submitting the contents of each column.
        help_marker("Using TableNextRow() + calling TableNextColumn() _before_ each cell, manually.")
        if imgui.begin_table("table2", 3):
            for row in range(4):
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Row %d" % row)
                imgui.table_next_column()
                imgui.text("Some contents")
                imgui.table_next_column()
                imgui.text("123.456")
            imgui.end_table()

        # [Method 3] We call TableNextColumn() _before_ each cell. We never call TableNextRow(),
        # as TableNextColumn() will automatically wrap around and create new rows as needed.
        # This is generally more convenient when your cells all contain the same type of data.
        help_marker(
            "Only using TableNextColumn(), which tends to be convenient for tables where every cell contains the same type of contents.\n"
            "This is also more similar to the old NextColumn() function of the Columns API, and provided to facilitate the Columns->Tables API transition.")
        if imgui.begin_table("table3", 3):
            for item in range(14):
                imgui.table_next_column()
                imgui.text("Item %d" % item)
            imgui.end_table()

        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Borders, background"):
        IMGUI_DEMO_MARKER("Tables/Borders, background")
        # Expose a few Borders related flags interactively
        class ContentsType:
            CT_Text = 0
            CT_FillButton = 1

        if not hasattr(static, "bb_flags"):
            static.bb_flags = imgui.TableFlags_.borders | imgui.TableFlags_.row_bg
            static.display_headers = False
            static.contents_type = ContentsType.CT_Text

        push_style_compact()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.bb_flags, imgui.TableFlags_.row_bg)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_Borders", static.bb_flags, imgui.TableFlags_.borders)
        imgui.same_line()
        help_marker("ImGuiTableFlags_Borders\n = ImGuiTableFlags_BordersInnerV\n | ImGuiTableFlags_BordersOuterV\n | ImGuiTableFlags_BordersInnerV\n | ImGuiTableFlags_BordersOuterH")
        imgui.indent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersH", static.bb_flags, imgui.TableFlags_.borders_h)
        imgui.indent()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterH", static.bb_flags, imgui.TableFlags_.borders_outer_h)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerH", static.bb_flags, imgui.TableFlags_.borders_inner_h)
        imgui.unindent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.bb_flags, imgui.TableFlags_.borders_v)
        imgui.indent()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.bb_flags, imgui.TableFlags_.borders_outer_v)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.bb_flags, imgui.TableFlags_.borders_inner_v)
        imgui.unindent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuter", static.bb_flags, imgui.TableFlags_.borders_outer)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInner", static.bb_flags, imgui.TableFlags_.borders_inner)
        imgui.unindent()

        imgui.align_text_to_frame_padding()
        imgui.text("Cell contents:")
        imgui.same_line()
        _, static.contents_type = imgui.radio_button("Text", static.contents_type, ContentsType.CT_Text)
        imgui.same_line()
        _, static.contents_type = imgui.radio_button("FillButton", static.contents_type, ContentsType.CT_FillButton)
        _, static.display_headers = imgui.checkbox("Display headers", static.display_headers)
        _, static.flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBody", static.bb_flags, imgui.TableFlags_.no_borders_in_body); imgui.same_line(); help_marker("Disable vertical borders in columns Body (borders will always appear in Headers)")
        pop_style_compact()

        if imgui.begin_table("table1", 3, static.bb_flags):
            # Display headers so we can inspect their interaction with borders.
            # (Headers are not the main purpose of this section of the demo, so we are not elaborating on them too much. See other sections for details)
            if static.display_headers:
                imgui.table_setup_column("One")
                imgui.table_setup_column("Two")
                imgui.table_setup_column("Three")
                imgui.table_headers_row()

            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    buf = f"Hello {column},{row}"
                    if static.contents_type == ContentsType.CT_Text:
                        imgui.text_unformatted(buf)
                    elif static.contents_type == ContentsType.CT_FillButton:
                        imgui.button(buf, ImVec2(-1, 0.0))
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Resizable, stretch"):
        IMGUI_DEMO_MARKER("Tables/Resizable, stretch")
        # By default, if we don't enable ScrollX, the sizing policy for each column is "Stretch".
        # All columns maintain a sizing weight, and they will occupy all available width.
        if not hasattr(static, "rs_flags"):
            static.rs_flags = (imgui.TableFlags_.sizing_stretch_same |
                            imgui.TableFlags_.resizable |
                            imgui.TableFlags_.borders_outer |
                            imgui.TableFlags_.borders_v |
                            imgui.TableFlags_.context_menu_in_body)
        push_style_compact()
        _, static.rs_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.rs_flags, imgui.TableFlags_.resizable)
        _, static.rs_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.rs_flags, imgui.TableFlags_.borders_v)
        imgui.same_line()
        help_marker("Using the _Resizable flag automatically enables the _BordersInnerV flag as well, this is why the resize borders are still showing when unchecking this.")
        pop_style_compact()

        if imgui.begin_table("table1", 3, static.rs_flags):
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text(f"Hello {column},{row}")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Resizable, fixed"):
        IMGUI_DEMO_MARKER("Tables/Resizable, fixed")
        # Here we use ImGuiTableFlags_SizingFixedFit (even though _ScrollX is not set)
        # So columns will adopt the "Fixed" policy and will maintain a fixed width regardless of the whole available width (unless table is small)
        # If there is not enough available width to fit all columns, they will, however, be resized down.
        # FIXME-TABLE: Providing a stretch-on-init would make sense especially for tables which don't have saved settings
        help_marker(
            "Using _Resizable + _SizingFixedFit flags.\n"
            "Fixed-width columns generally make more sense if you want to use horizontal scrolling.\n\n"
            "Double-click a column border to auto-fit the column to its contents.")
        push_style_compact()
        if not hasattr(static, "rf_flags"):
            static.rf_flags = (imgui.TableFlags_.sizing_fixed_fit |
                               imgui.TableFlags_.resizable |
                               imgui.TableFlags_.borders_outer |
                               imgui.TableFlags_.borders_v |
                               imgui.TableFlags_.context_menu_in_body)
        _, static.rf_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendX", static.rf_flags, imgui.TableFlags_.no_host_extend_x)
        pop_style_compact()

        if imgui.begin_table("table1", 3, static.rf_flags):
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text(f"Hello {column},{row}")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Resizable, mixed"):
        IMGUI_DEMO_MARKER("Tables/Resizable, mixed")
        help_marker(
            "Using TableSetupColumn() to alter resizing policy on a per-column basis.\n\n"
            "When combining Fixed and Stretch columns, generally you only want one, maybe two trailing columns to use _WidthStretch.")
        if not hasattr(static, "rm_flags"):
            static.rm_flags = (imgui.TableFlags_.sizing_fixed_fit |
                               imgui.TableFlags_.row_bg |
                               imgui.TableFlags_.borders |
                               imgui.TableFlags_.resizable |
                               imgui.TableFlags_.reorderable |
                               imgui.TableFlags_.hideable)

        if imgui.begin_table("table1", 3, static.rm_flags):
            imgui.table_setup_column("AAA", imgui.TableColumnFlags_.width_fixed)
            imgui.table_setup_column("BBB", imgui.TableColumnFlags_.width_fixed)
            imgui.table_setup_column("CCC", imgui.TableColumnFlags_.width_stretch)
            imgui.table_headers_row()
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text("%s %d,%d" % ("Stretch" if column == 2 else "Fixed", column, row))
            imgui.end_table()

        if imgui.begin_table("table2", 6, static.rm_flags):
            imgui.table_setup_column("AAA", imgui.TableColumnFlags_.width_fixed)
            imgui.table_setup_column("BBB", imgui.TableColumnFlags_.width_fixed)
            imgui.table_setup_column("CCC", imgui.TableColumnFlags_.width_fixed | imgui.TableColumnFlags_.default_hide)
            imgui.table_setup_column("DDD", imgui.TableColumnFlags_.width_stretch)
            imgui.table_setup_column("EEE", imgui.TableColumnFlags_.width_stretch)
            imgui.table_setup_column("FFF", imgui.TableColumnFlags_.width_stretch | imgui.TableColumnFlags_.default_hide)
            imgui.table_headers_row()
            for row in range(5):
                imgui.table_next_row()
                for column in range(6):
                    imgui.table_set_column_index(column)
                    imgui.text("%s %d,%d" % ("Stretch" if column >= 3 else "Fixed", column, row))
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Reorderable, hideable, with headers"):
        IMGUI_DEMO_MARKER("Tables/Reorderable, hideable, with headers")
        help_marker(
            "Click and drag column headers to reorder columns.\n\n"
            "Right-click on a header to open a context menu.")
        if not hasattr(static, "rh_flags"):
            static.rh_flags = (imgui.TableFlags_.resizable |
                               imgui.TableFlags_.reorderable |
                               imgui.TableFlags_.hideable |
                               imgui.TableFlags_.borders_outer |
                               imgui.TableFlags_.borders_v)

        push_style_compact()
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.rh_flags, imgui.TableFlags_.resizable)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Reorderable", static.rh_flags, imgui.TableFlags_.reorderable)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Hideable", static.rh_flags, imgui.TableFlags_.hideable)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBody", static.rh_flags, imgui.TableFlags_.no_borders_in_body)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBodyUntilResize", static.rh_flags, imgui.TableFlags_.no_borders_in_body_until_resize)
        imgui.same_line()
        help_marker("Disable vertical borders in columns Body until hovered for resize (borders will always appear in Headers)")
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_HighlightHoveredColumn", static.rh_flags, imgui.TableFlags_.highlight_hovered_column)
        pop_style_compact()

        if imgui.begin_table("table1", 3, static.rh_flags):
            # Submit columns name with TableSetupColumn() and call TableHeadersRow() to create a row with a header in each column.
            # (Later we will show how TableSetupColumn() has other uses, optional flags, sizing weight etc.)
            imgui.table_setup_column("One")
            imgui.table_setup_column("Two")
            imgui.table_setup_column("Three")
            imgui.table_headers_row()
            for row in range(6):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text("Hello %d,%d" % (column, row))
            imgui.end_table()

        # Use outer_size.x == 0.0f instead of default to make the table as tight as possible (only valid when no scrolling and no stretch column)
        if imgui.begin_table("table2", 3, static.rh_flags | imgui.TableFlags_.sizing_fixed_fit, ImVec2(0.0, 0.0)):
            imgui.table_setup_column("One")
            imgui.table_setup_column("Two")
            imgui.table_setup_column("Three")
            imgui.table_headers_row()
            for row in range(6):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text("Fixed %d,%d" % (column, row))
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Padding"):
        IMGUI_DEMO_MARKER("Tables/Padding")
        # First example: showcase use of padding flags and effect of BorderOuterV/BorderInnerV on X padding.
        # We don't expose BorderOuterH/BorderInnerH here because they have no effect on X padding.
        help_marker(
            "We often want outer padding activated when any using features which makes the edges of a column visible:\n"
            "e.g.:\n"
            "- BorderOuterV\n"
            "- any form of row selection\n"
            "Because of this, activating BorderOuterV sets the default to PadOuterX. Using PadOuterX or NoPadOuterX you can override the default.\n\n"
            "Actual padding values are using style.CellPadding.\n\n"
            "In this demo we don't show horizontal borders to emphasize how they don't affect default horizontal padding.")

        if not hasattr(static, "padding_flags"):
            static.padding_flags = (imgui.TableFlags_.borders_v)
            static.show_headers = False

        push_style_compact()
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_PadOuterX", static.padding_flags, imgui.TableFlags_.pad_outer_x)
        imgui.same_line()
        help_marker("Enable outer-most padding (default if ImGuiTableFlags_BordersOuterV is set)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadOuterX", static.padding_flags, imgui.TableFlags_.no_pad_outer_x)
        imgui.same_line()
        help_marker("Disable outer-most padding (default if ImGuiTableFlags_BordersOuterV is not set)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadInnerX", static.padding_flags, imgui.TableFlags_.no_pad_inner_x)
        imgui.same_line()
        help_marker("Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.padding_flags, imgui.TableFlags_.borders_outer_v)
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.padding_flags, imgui.TableFlags_.borders_inner_v)
        _, static.show_headers = imgui.checkbox("show_headers", static.show_headers)
        pop_style_compact()

        if imgui.begin_table("table_padding", 3, static.padding_flags):
            if static.show_headers:
                imgui.table_setup_column("One")
                imgui.table_setup_column("Two")
                imgui.table_setup_column("Three")
                imgui.table_headers_row()

            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    if row == 0:
                        imgui.text("Avail %.2f" % imgui.get_content_region_avail().x)
                    else:
                        buf = "Hello %d,%d" % (column, row)
                        imgui.button(buf, ImVec2(-1, 0.0))
                    #if imgui.table_get_column_flags() & imgui.TableColumnFlags_.is_hovered:
                    #    imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, imgui.IM_COL32(0, 100, 0, 255))
            imgui.end_table()

        # Second example: set style.CellPadding to (0.0) or a custom value.
        # FIXME-TABLE: Vertical border effectively not displayed the same way as horizontal one...
        help_marker("Setting style.CellPadding to (0,0) or a custom value.")
        if not hasattr(static, "padding_flags2"):
            static.padding_flags2 = (imgui.TableFlags_.borders | imgui.TableFlags_.row_bg)
            static.cell_padding = [0.0, 0.0]
            static.show_widget_frame_bg = True

        push_style_compact()
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_Borders", static.padding_flags2, imgui.TableFlags_.borders)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersH", static.padding_flags2, imgui.TableFlags_.borders_h)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.padding_flags2, imgui.TableFlags_.borders_v)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersInner", static.padding_flags2, imgui.TableFlags_.borders_inner)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersOuter", static.padding_flags2, imgui.TableFlags_.borders_outer)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.padding_flags2, imgui.TableFlags_.row_bg)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.padding_flags2, imgui.TableFlags_.resizable)
        _, static.show_widget_frame_bg = imgui.checkbox("show_widget_frame_bg", static.show_widget_frame_bg)
        _, static.cell_padding = imgui.slider_float2("CellPadding", static.cell_padding, 0.0, 10.0, "%.0f")
        pop_style_compact()

        imgui.push_style_var(imgui.StyleVar_.cell_padding, static.cell_padding)  # type: ignore
        if imgui.begin_table("table_padding_2", 3, static.padding_flags2):
            if not hasattr(static, "text_bufs"):
                static.text_bufs = ["" for _ in range(3 * 5)]  # Mini text storage for 3x5 cells
                static.init = True
            if not static.show_widget_frame_bg:
                imgui.push_style_color(imgui.Col_.frame_bg, 0)
            for cell in range(3 * 5):
                imgui.table_next_column()
                if static.init:
                    static.text_bufs[cell] = "edit me"
                imgui.set_next_item_width(-1)
                imgui.push_id(cell)
                imgui.input_text("##cell", static.text_bufs[cell])
                imgui.pop_id()
            if not static.show_widget_frame_bg:
                imgui.pop_style_color()
            static.init = False
            imgui.end_table()
        imgui.pop_style_var()

        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Explicit widths"):
        IMGUI_DEMO_MARKER("Tables/Explicit widths")
        if not hasattr(static, "ew_flags1"):
            static.ew_flags1 = imgui.TableFlags_.borders_v | imgui.TableFlags_.borders_outer_h | imgui.TableFlags_.row_bg | imgui.TableFlags_.context_menu_in_body
        push_style_compact()
        _, static.ew_flags1 = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.ew_flags1, imgui.TableFlags_.resizable)
        _, static.ew_flags1 = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendX", static.ew_flags1, imgui.TableFlags_.no_host_extend_x)
        pop_style_compact()

        if not hasattr(static, "ew_sizing_policy_flags"):
            static.ew_sizing_policy_flags = [
                imgui.TableFlags_.sizing_fixed_fit.value,
                imgui.TableFlags_.sizing_fixed_same.value,
                imgui.TableFlags_.sizing_stretch_prop.value,
                imgui.TableFlags_.sizing_stretch_same.value,
            ]
        for table_n in range(4):
            imgui.push_id(table_n)
            imgui.set_next_item_width(text_base_width * 30)
            static.ew_sizing_policy_flags[table_n] = edit_table_sizing_flags(static.ew_sizing_policy_flags[table_n])

            if imgui.begin_table("table1", 3, static.ew_sizing_policy_flags[table_n] | static.ew_flags1):
                for row in range(3):
                    imgui.table_next_row()
                    imgui.table_next_column(); imgui.text("Oh dear")
                    imgui.table_next_column(); imgui.text("Oh dear")
                    imgui.table_next_column(); imgui.text("Oh dear")
                imgui.end_table()
            if imgui.begin_table("table2", 3, static.ew_sizing_policy_flags[table_n] | static.ew_flags1):
                for row in range(3):
                    imgui.table_next_row()
                    imgui.table_next_column(); imgui.text("AAAA")
                    imgui.table_next_column(); imgui.text("BBBBBBBB")
                    imgui.table_next_column(); imgui.text("CCCCCCCCCCCC")
                imgui.end_table()
            imgui.pop_id()

        imgui.spacing()
        imgui.text_unformatted("Advanced")
        imgui.same_line()
        help_marker(
            "This section allows you to interact and see the effect of various sizing policies "
            "depending on whether Scroll is enabled and the contents of your columns.")

        CT_SHOW_WIDTH, CT_SHORT_TEXT, CT_LONG_TEXT, CT_BUTTON, CT_FILL_BUTTON, CT_INPUT_TEXT = range(6)
        if not hasattr(static, "ew_flags"):
            static.ew_flags = imgui.TableFlags_.scroll_y | imgui.TableFlags_.borders | imgui.TableFlags_.row_bg | imgui.TableFlags_.resizable
            static.ew_contents_type = CT_SHOW_WIDTH
            static.ew_column_count = 3

        push_style_compact()
        imgui.push_id("Advanced")
        imgui.push_item_width(text_base_width * 30)
        static.ew_flags = edit_table_sizing_flags(static.ew_flags)
        _, static.ew_contents_type = imgui.combo("Contents", static.ew_contents_type, "Show width\0Short Text\0Long Text\0Button\0Fill Button\0InputText\0")
        if static.ew_contents_type == CT_FILL_BUTTON:
            imgui.same_line()
            help_marker(
                "Be mindful that using right-alignment (e.g. size.x = -FLT_MIN) creates a feedback loop "
                "where contents width can feed into auto-column width can feed into contents width.")
        _, static.ew_column_count = imgui.drag_int("Columns", static.ew_column_count, 0.1, 1, 64, "%d", imgui.SliderFlags_.always_clamp)
        _, static.ew_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.ew_flags, imgui.TableFlags_.resizable)
        _, static.ew_flags = imgui.checkbox_flags("ImGuiTableFlags_PreciseWidths", static.ew_flags, imgui.TableFlags_.precise_widths)
        imgui.same_line(); help_marker("Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns: Without this flag: 33,33,34. With this flag: 33,33,33). With larger number of columns, resizing will appear to be less smooth.")
        _, static.ew_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollX", static.ew_flags, imgui.TableFlags_.scroll_x)
        _, static.ew_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollY", static.ew_flags, imgui.TableFlags_.scroll_y)
        _, static.ew_flags = imgui.checkbox_flags("ImGuiTableFlags_NoClip", static.ew_flags, imgui.TableFlags_.no_clip)
        imgui.pop_item_width()
        imgui.pop_id()
        pop_style_compact()

        if not hasattr(static, "ew_text_buf"):
            static.ew_text_buf = ""

        if imgui.begin_table("table2", static.ew_column_count, static.ew_flags, ImVec2(0.0, text_base_height * 7)):
            for cell in range(10 * static.ew_column_count):
                imgui.table_next_column()
                column = imgui.table_get_column_index()
                row = imgui.table_get_row_index()

                imgui.push_id(cell)
                label = f"Hello {column},{row}"
                if static.ew_contents_type == CT_SHORT_TEXT:
                    imgui.text_unformatted(label)
                elif static.ew_contents_type == CT_LONG_TEXT:
                    imgui.text(f"Some {'long' if column == 0 else 'longeeer'} text {column},{row}\nOver two lines..")
                elif static.ew_contents_type == CT_SHOW_WIDTH:
                    imgui.text(f"W: {imgui.get_content_region_avail().x:.1f}")
                elif static.ew_contents_type == CT_BUTTON:
                    imgui.button(label)
                elif static.ew_contents_type == CT_FILL_BUTTON:
                    imgui.button(label, ImVec2(-imgui.FLT_MIN, 0.0))
                elif static.ew_contents_type == CT_INPUT_TEXT:
                    imgui.set_next_item_width(-imgui.FLT_MIN)
                    _, static.ew_text_buf = imgui.input_text("##", static.ew_text_buf)
                imgui.pop_id()
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Vertical scrolling, with clipping"):
        IMGUI_DEMO_MARKER("Tables/Vertical scrolling, with clipping")
        help_marker(
            "Here we activate ScrollY, which will create a child window container to allow hosting scrollable contents.\n\n"
            "We also demonstrate using ImGuiListClipper to virtualize the submission of many items.")
        if not hasattr(static, "vs_flags"):
            static.vs_flags = imgui.TableFlags_.scroll_y | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_v | imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable

        push_style_compact()
        _, static.vs_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollY", static.vs_flags, imgui.TableFlags_.scroll_y)
        pop_style_compact()

        outer_size = ImVec2(0.0, text_base_height * 8)
        if imgui.begin_table("table_scrolly", 3, static.vs_flags, outer_size):
            imgui.table_setup_scroll_freeze(0, 1)
            imgui.table_setup_column("One", imgui.TableColumnFlags_.none)
            imgui.table_setup_column("Two", imgui.TableColumnFlags_.none)
            imgui.table_setup_column("Three", imgui.TableColumnFlags_.none)
            imgui.table_headers_row()

            clipper = imgui.ListClipper()
            clipper.begin(1000)
            while clipper.step():
                for row in range(clipper.display_start, clipper.display_end):
                    imgui.table_next_row()
                    for column in range(3):
                        imgui.table_set_column_index(column)
                        imgui.text(f"Hello {column},{row}")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Horizontal scrolling"):
        IMGUI_DEMO_MARKER("Tables/Horizontal scrolling")
        help_marker(
            "When ScrollX is enabled, the default sizing policy becomes ImGuiTableFlags_SizingFixedFit, "
            "as automatically stretching columns doesn't make much sense with horizontal scrolling.\n\n"
            "Also note that as of the current version, you will almost always want to enable ScrollY along with ScrollX, "
            "because the container window won't automatically extend vertically to fix contents "
            "(this may be improved in future versions).")
        if not hasattr(static, "hs_flags"):
            static.hs_flags = imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_v | imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable
            static.hs_freeze_cols = 1
            static.hs_freeze_rows = 1

        push_style_compact()
        _, static.hs_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.hs_flags, imgui.TableFlags_.resizable)
        _, static.hs_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollX", static.hs_flags, imgui.TableFlags_.scroll_x)
        _, static.hs_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollY", static.hs_flags, imgui.TableFlags_.scroll_y)
        imgui.set_next_item_width(imgui.get_frame_height())
        _, static.hs_freeze_cols = imgui.drag_int("freeze_cols", static.hs_freeze_cols, 0.2, 0, 9, "%d", imgui.SliderFlags_.no_input)
        imgui.set_next_item_width(imgui.get_frame_height())
        _, static.hs_freeze_rows = imgui.drag_int("freeze_rows", static.hs_freeze_rows, 0.2, 0, 9, "%d", imgui.SliderFlags_.no_input)
        pop_style_compact()

        outer_size = ImVec2(0.0, text_base_height * 8)
        if imgui.begin_table("table_scrollx", 7, static.hs_flags, outer_size):
            imgui.table_setup_scroll_freeze(static.hs_freeze_cols, static.hs_freeze_rows)
            imgui.table_setup_column("Line #", imgui.TableColumnFlags_.no_hide)
            imgui.table_setup_column("One")
            imgui.table_setup_column("Two")
            imgui.table_setup_column("Three")
            imgui.table_setup_column("Four")
            imgui.table_setup_column("Five")
            imgui.table_setup_column("Six")
            imgui.table_headers_row()
            for row in range(20):
                imgui.table_next_row()
                for column in range(7):
                    if not imgui.table_set_column_index(column) and column > 0:
                        continue
                    if column == 0:
                        imgui.text(f"Line {row}")
                    else:
                        imgui.text(f"Hello world {column},{row}")
            imgui.end_table()

        imgui.spacing()
        imgui.text_unformatted("Stretch + ScrollX")
        imgui.same_line()
        help_marker(
            "Showcase using Stretch columns + ScrollX together: "
            "this is rather unusual and only makes sense when specifying an 'inner_width' for the table!\n"
            "Without an explicit value, inner_width is == outer_size.x and therefore using Stretch columns "
            "along with ScrollX doesn't make sense.")
        if not hasattr(static, "hs_flags2"):
            static.hs_flags2 = imgui.TableFlags_.sizing_stretch_same | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y | imgui.TableFlags_.borders_outer | imgui.TableFlags_.row_bg | imgui.TableFlags_.context_menu_in_body
            static.hs_inner_width = 1000.0
        push_style_compact()
        imgui.push_id("flags3")
        imgui.push_item_width(text_base_width * 30)
        _, static.hs_flags2 = imgui.checkbox_flags("ImGuiTableFlags_ScrollX", static.hs_flags2, imgui.TableFlags_.scroll_x)
        _, static.hs_inner_width = imgui.drag_float("inner_width", static.hs_inner_width, 1.0, 0.0, imgui.FLT_MAX, "%.1f")
        imgui.pop_item_width()
        imgui.pop_id()
        pop_style_compact()
        if imgui.begin_table("table2", 7, static.hs_flags2, outer_size, static.hs_inner_width):
            for cell in range(20 * 7):
                imgui.table_next_column()
                imgui.text(f"Hello world {imgui.table_get_column_index()},{imgui.table_get_row_index()}")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Columns flags"):
        IMGUI_DEMO_MARKER("Tables/Columns flags")
        column_count = 3
        column_names = ["One", "Two", "Three"]
        if not hasattr(static, "cf_column_flags"):
            static.cf_column_flags = [
                imgui.TableColumnFlags_.default_sort.value,
                imgui.TableColumnFlags_.none.value,
                imgui.TableColumnFlags_.default_hide.value,
            ]
            static.cf_column_flags_out = [0, 0, 0]

        if imgui.begin_table("table_columns_flags_checkboxes", column_count, imgui.TableFlags_.none):
            push_style_compact()
            for column in range(column_count):
                imgui.table_next_column()
                imgui.push_id(column)
                imgui.align_text_to_frame_padding()
                imgui.text(f"'{column_names[column]}'")
                imgui.spacing()
                imgui.text("Input flags:")
                static.cf_column_flags[column] = edit_table_columns_flags(static.cf_column_flags[column])
                imgui.spacing()
                imgui.text("Output flags:")
                imgui.begin_disabled()
                show_table_columns_status_flags(static.cf_column_flags_out[column])
                imgui.end_disabled()
                imgui.pop_id()
            pop_style_compact()
            imgui.end_table()

        flags = (imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y
                 | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_v
                 | imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable | imgui.TableFlags_.sortable)
        outer_size = ImVec2(0.0, text_base_height * 9)
        if imgui.begin_table("table_columns_flags", column_count, flags, outer_size):
            has_angled_header = False
            for column in range(column_count):
                has_angled_header = has_angled_header or (static.cf_column_flags[column] & imgui.TableColumnFlags_.angled_header.value) != 0
                imgui.table_setup_column(column_names[column], static.cf_column_flags[column])
            if has_angled_header:
                imgui.table_angled_headers_row()
            imgui.table_headers_row()
            for column in range(column_count):
                static.cf_column_flags_out[column] = imgui.table_get_column_flags(column)
            indent_step = int(text_base_width) // 2
            for row in range(8):
                imgui.indent(indent_step)
                imgui.table_next_row()
                for column in range(column_count):
                    imgui.table_set_column_index(column)
                    imgui.text(f"{'Indented' if column == 0 else 'Hello'} {imgui.table_get_column_name(column)}")
            imgui.unindent(indent_step * 8.0)
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Columns widths"):
        IMGUI_DEMO_MARKER("Tables/Columns widths")
        help_marker("Using TableSetupColumn() to setup default width.")

        if not hasattr(static, "cw_flags1"):
            static.cw_flags1 = imgui.TableFlags_.borders | imgui.TableFlags_.no_borders_in_body_until_resize
        push_style_compact()
        _, static.cw_flags1 = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.cw_flags1, imgui.TableFlags_.resizable)
        _, static.cw_flags1 = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBodyUntilResize", static.cw_flags1, imgui.TableFlags_.no_borders_in_body_until_resize)
        pop_style_compact()
        if imgui.begin_table("table1", 3, static.cw_flags1):
            imgui.table_setup_column("one", imgui.TableColumnFlags_.width_fixed, 100.0)
            imgui.table_setup_column("two", imgui.TableColumnFlags_.width_fixed, 200.0)
            imgui.table_setup_column("three", imgui.TableColumnFlags_.width_fixed)
            imgui.table_headers_row()
            for row in range(4):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    if row == 0:
                        imgui.text(f"(w: {imgui.get_content_region_avail().x:5.1f})")
                    else:
                        imgui.text(f"Hello {column},{row}")
            imgui.end_table()

        help_marker(
            "Using TableSetupColumn() to setup explicit width.\n\nUnless _NoKeepColumnsVisible is set, "
            "fixed columns with set width may still be shrunk down if there's not enough space in the host.")

        if not hasattr(static, "cw_flags2"):
            static.cw_flags2 = imgui.TableFlags_.none.value
        push_style_compact()
        _, static.cw_flags2 = imgui.checkbox_flags("ImGuiTableFlags_NoKeepColumnsVisible", static.cw_flags2, imgui.TableFlags_.no_keep_columns_visible)
        _, static.cw_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.cw_flags2, imgui.TableFlags_.borders_inner_v)
        _, static.cw_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.cw_flags2, imgui.TableFlags_.borders_outer_v)
        pop_style_compact()
        if imgui.begin_table("table2", 4, static.cw_flags2):
            imgui.table_setup_column("", imgui.TableColumnFlags_.width_fixed, 100.0)
            imgui.table_setup_column("", imgui.TableColumnFlags_.width_fixed, text_base_width * 15.0)
            imgui.table_setup_column("", imgui.TableColumnFlags_.width_fixed, text_base_width * 30.0)
            imgui.table_setup_column("", imgui.TableColumnFlags_.width_fixed, text_base_width * 15.0)
            for row in range(5):
                imgui.table_next_row()
                for column in range(4):
                    imgui.table_set_column_index(column)
                    if row == 0:
                        imgui.text(f"(w: {imgui.get_content_region_avail().x:5.1f})")
                    else:
                        imgui.text(f"Hello {column},{row}")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Nested tables"):
        IMGUI_DEMO_MARKER("Tables/Nested tables")
        help_marker("This demonstrates embedding a table into another table cell.")

        if imgui.begin_table("table_nested1", 2, imgui.TableFlags_.borders | imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable):
            imgui.table_setup_column("A0")
            imgui.table_setup_column("A1")
            imgui.table_headers_row()

            imgui.table_next_column()
            imgui.text("A0 Row 0")
            rows_height = (text_base_height * 2.0) + (imgui.get_style().cell_padding.y * 2.0)
            if imgui.begin_table("table_nested2", 2, imgui.TableFlags_.borders | imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable):
                imgui.table_setup_column("B0")
                imgui.table_setup_column("B1")
                imgui.table_headers_row()

                imgui.table_next_row(imgui.TableRowFlags_.none, rows_height)
                imgui.table_next_column(); imgui.text("B0 Row 0")
                imgui.table_next_column(); imgui.text("B1 Row 0")
                imgui.table_next_row(imgui.TableRowFlags_.none, rows_height)
                imgui.table_next_column(); imgui.text("B0 Row 1")
                imgui.table_next_column(); imgui.text("B1 Row 1")

                imgui.end_table()
            imgui.table_next_column(); imgui.text("A1 Row 0")
            imgui.table_next_column(); imgui.text("A0 Row 1")
            imgui.table_next_column(); imgui.text("A1 Row 1")
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Row height"):
        IMGUI_DEMO_MARKER("Tables/Row height")
        help_marker(
            "You can pass a 'min_row_height' to TableNextRow().\n\nRows are padded with 'style.CellPadding.y' on top and bottom, "
            "so effectively the minimum row height will always be >= 'style.CellPadding.y * 2.0f'.\n\n"
            "We cannot honor a _maximum_ row height as that would require a unique clipping rectangle per row.")
        if imgui.begin_table("table_row_height", 1, imgui.TableFlags_.borders):
            for row in range(8):
                min_row_height = float(int(text_base_height * 0.30 * row + imgui.get_style().cell_padding.y * 2.0))
                imgui.table_next_row(imgui.TableRowFlags_.none, min_row_height)
                imgui.table_next_column()
                imgui.text(f"min_row_height = {min_row_height:.2f}")
            imgui.end_table()

        help_marker(
            "Showcase using SameLine(0,0) to share Current Line Height between cells.\n\n"
            "Please note that Tables Row Height is not the same thing as Current Line Height, "
            "as a table cell may contains multiple lines.")
        if imgui.begin_table("table_share_lineheight", 2, imgui.TableFlags_.borders):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.color_button("##1", imgui.ImVec4(0.13, 0.26, 0.40, 1.0), imgui.ColorEditFlags_.none, ImVec2(40, 40))
            imgui.table_next_column()
            imgui.text("Line 1")
            imgui.text("Line 2")

            imgui.table_next_row()
            imgui.table_next_column()
            imgui.color_button("##2", imgui.ImVec4(0.13, 0.26, 0.40, 1.0), imgui.ColorEditFlags_.none, ImVec2(40, 40))
            imgui.table_next_column()
            imgui.same_line(0.0, 0.0)
            imgui.text("Line 1, with SameLine(0,0)")
            imgui.text("Line 2")
            imgui.end_table()

        help_marker("Showcase altering CellPadding.y between rows. Note that CellPadding.x is locked for the entire table.")
        if imgui.begin_table("table_changing_cellpadding_y", 1, imgui.TableFlags_.borders):
            style = imgui.get_style()
            for row in range(8):
                if (row % 3) == 2:
                    imgui.push_style_var_y(imgui.StyleVar_.cell_padding, 20.0)
                imgui.table_next_row(imgui.TableRowFlags_.none)
                imgui.table_next_column()
                imgui.text(f"CellPadding.y = {style.cell_padding.y:.2f}")
                if (row % 3) == 2:
                    imgui.pop_style_var()
            imgui.end_table()

        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Outer size"):
        IMGUI_DEMO_MARKER("Tables/Outer size")
        imgui.text("Using NoHostExtendX and NoHostExtendY:")
        if not hasattr(static, "os_flags"):
            static.os_flags = imgui.TableFlags_.borders | imgui.TableFlags_.resizable | imgui.TableFlags_.context_menu_in_body | imgui.TableFlags_.row_bg | imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.no_host_extend_x
        push_style_compact()
        _, static.os_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendX", static.os_flags, imgui.TableFlags_.no_host_extend_x)
        imgui.same_line(); help_marker("Make outer width auto-fit to columns, overriding outer_size.x value.\n\nOnly available when ScrollX/ScrollY are disabled and Stretch columns are not used.")
        _, static.os_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendY", static.os_flags, imgui.TableFlags_.no_host_extend_y)
        imgui.same_line(); help_marker("Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit).\n\nOnly available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.")
        pop_style_compact()

        outer_size = ImVec2(0.0, text_base_height * 5.5)
        if imgui.begin_table("table1", 3, static.os_flags, outer_size):
            for row in range(10):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_next_column()
                    imgui.text(f"Cell {column},{row}")
            imgui.end_table()
        imgui.same_line()
        imgui.text("Hello!")

        imgui.spacing()

        imgui.text("Using explicit size:")
        if imgui.begin_table("table2", 3, imgui.TableFlags_.borders | imgui.TableFlags_.row_bg, ImVec2(text_base_width * 30, 0.0)):
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_next_column()
                    imgui.text(f"Cell {column},{row}")
            imgui.end_table()
        imgui.same_line()
        if imgui.begin_table("table3", 3, imgui.TableFlags_.borders | imgui.TableFlags_.row_bg, ImVec2(text_base_width * 30, 0.0)):
            rows_height = text_base_height * 1.5 + imgui.get_style().cell_padding.y * 2.0
            for row in range(3):
                imgui.table_next_row(0, rows_height)
                for column in range(3):
                    imgui.table_next_column()
                    imgui.text(f"Cell {column},{row}")
            imgui.end_table()

        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Background color"):
        IMGUI_DEMO_MARKER("Tables/Background color")
        if not hasattr(static, "bg_flags"):
            static.bg_flags = imgui.TableFlags_.row_bg.value
            static.bg_row_bg_type = 1
            static.bg_row_bg_target = 1
            static.bg_cell_bg_type = 1

        push_style_compact()
        _, static.bg_flags = imgui.checkbox_flags("ImGuiTableFlags_Borders", static.bg_flags, imgui.TableFlags_.borders)
        _, static.bg_flags = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.bg_flags, imgui.TableFlags_.row_bg)
        imgui.same_line(); help_marker("ImGuiTableFlags_RowBg automatically sets RowBg0 to alternative colors pulled from the Style.")
        _, static.bg_row_bg_type = imgui.combo("row bg type", static.bg_row_bg_type, "None\0Red\0Gradient\0")
        _, static.bg_row_bg_target = imgui.combo("row bg target", static.bg_row_bg_target, "RowBg0\0RowBg1\0")
        imgui.same_line(); help_marker("Target RowBg0 to override the alternating odd/even colors,\nTarget RowBg1 to blend with them.")
        _, static.bg_cell_bg_type = imgui.combo("cell bg type", static.bg_cell_bg_type, "None\0Blue\0")
        imgui.same_line(); help_marker("We are colorizing cells to B1->C2 here.")
        pop_style_compact()

        if imgui.begin_table("table1", 5, static.bg_flags):
            for row in range(6):
                imgui.table_next_row()

                if static.bg_row_bg_type != 0:
                    if static.bg_row_bg_type == 1:
                        row_bg_color = imgui.get_color_u32(imgui.ImVec4(0.7, 0.3, 0.3, 0.65))
                    else:
                        row_bg_color = imgui.get_color_u32(imgui.ImVec4(0.2 + row * 0.1, 0.2, 0.2, 0.65))
                    imgui.table_set_bg_color(imgui.TableBgTarget_.row_bg0.value + static.bg_row_bg_target, row_bg_color)

                for column in range(5):
                    imgui.table_set_column_index(column)
                    imgui.text(f"{chr(ord('A') + row)}{chr(ord('0') + column)}")

                    if row >= 1 and row <= 2 and column >= 1 and column <= 2 and static.bg_cell_bg_type == 1:
                        cell_bg_color = imgui.get_color_u32(imgui.ImVec4(0.3, 0.3, 0.7, 0.65))
                        imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, cell_bg_color)
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Tree view"):
        IMGUI_DEMO_MARKER("Tables/Tree view")
        if not hasattr(static, "tv_table_flags"):
            static.tv_table_flags = imgui.TableFlags_.borders_v | imgui.TableFlags_.borders_outer_h | imgui.TableFlags_.resizable | imgui.TableFlags_.row_bg | imgui.TableFlags_.no_borders_in_body
            static.tv_tree_node_flags_base = imgui.TreeNodeFlags_.span_all_columns | imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.draw_lines_full

        _, static.tv_tree_node_flags_base = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanFullWidth", static.tv_tree_node_flags_base, imgui.TreeNodeFlags_.span_full_width)
        _, static.tv_tree_node_flags_base = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanLabelWidth", static.tv_tree_node_flags_base, imgui.TreeNodeFlags_.span_label_width)
        _, static.tv_tree_node_flags_base = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanAllColumns", static.tv_tree_node_flags_base, imgui.TreeNodeFlags_.span_all_columns)
        _, static.tv_tree_node_flags_base = imgui.checkbox_flags("ImGuiTreeNodeFlags_LabelSpanAllColumns", static.tv_tree_node_flags_base, imgui.TreeNodeFlags_.label_span_all_columns)
        imgui.same_line(); help_marker("Useful if you know that you aren't displaying contents in other columns")

        help_marker("See \"Columns flags\" section to configure how indentation is applied to individual columns.")

        # Simple storage to output a dummy file-system.
        nodes = [
            ("Root with Long Name",          "Folder",      -1,   1, 3),   # 0
            ("Music",                         "Folder",      -1,   4, 2),   # 1
            ("Textures",                      "Folder",      -1,   6, 3),   # 2
            ("desktop.ini",                   "System file", 1024, -1, -1), # 3
            ("File1_a.wav",                   "Audio file",  123000, -1, -1), # 4
            ("File1_b.wav",                   "Audio file",  456000, -1, -1), # 5
            ("Image001.png",                  "Image file",  203128, -1, -1), # 6
            ("Copy of Image001.png",          "Image file",  203256, -1, -1), # 7
            ("Copy of Image001 (Final2).png", "Image file",  203512, -1, -1), # 8
        ]

        def display_node(node_idx):
            name, type_str, size, child_idx, child_count = nodes[node_idx]
            is_folder = child_count > 0

            node_flags = static.tv_tree_node_flags_base
            if node_idx != 0:
                node_flags = node_flags & ~imgui.TreeNodeFlags_.label_span_all_columns

            imgui.table_next_row()
            imgui.table_next_column()
            if is_folder:
                open = imgui.tree_node_ex(name, node_flags)
                if (node_flags & imgui.TreeNodeFlags_.label_span_all_columns) == 0:
                    imgui.table_next_column()
                    imgui.text_disabled("--")
                    imgui.table_next_column()
                    imgui.text_unformatted(type_str)
                if open:
                    for child_n in range(child_count):
                        display_node(child_idx + child_n)
                    imgui.tree_pop()
            else:
                imgui.tree_node_ex(name, node_flags | imgui.TreeNodeFlags_.leaf | imgui.TreeNodeFlags_.bullet | imgui.TreeNodeFlags_.no_tree_push_on_open)
                imgui.table_next_column()
                imgui.text(str(size))
                imgui.table_next_column()
                imgui.text_unformatted(type_str)

        if imgui.begin_table("3ways", 3, static.tv_table_flags):
            imgui.table_setup_column("Name", imgui.TableColumnFlags_.no_hide)
            imgui.table_setup_column("Size", imgui.TableColumnFlags_.width_fixed, text_base_width * 12.0)
            imgui.table_setup_column("Type", imgui.TableColumnFlags_.width_fixed, text_base_width * 18.0)
            imgui.table_headers_row()
            display_node(0)
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Item width"):
        IMGUI_DEMO_MARKER("Tables/Item width")
        help_marker(
            "Showcase using PushItemWidth() and how it is preserved on a per-column basis.\n\n"
            "Note that on auto-resizing non-resizable fixed columns, querying the content width for "
            "e.g. right-alignment doesn't make sense.")
        if not hasattr(static, "iw_dummy_f"):
            static.iw_dummy_f = 0.0
        if imgui.begin_table("table_item_width", 3, imgui.TableFlags_.borders):
            imgui.table_setup_column("small")
            imgui.table_setup_column("half")
            imgui.table_setup_column("right-align")
            imgui.table_headers_row()

            for row in range(3):
                imgui.table_next_row()
                if row == 0:
                    imgui.table_set_column_index(0)
                    imgui.push_item_width(text_base_width * 3.0)
                    imgui.table_set_column_index(1)
                    imgui.push_item_width(-imgui.get_content_region_avail().x * 0.5)
                    imgui.table_set_column_index(2)
                    imgui.push_item_width(-imgui.FLT_MIN)

                imgui.push_id(row)
                imgui.table_set_column_index(0)
                _, static.iw_dummy_f = imgui.slider_float("float0", static.iw_dummy_f, 0.0, 1.0)
                imgui.table_set_column_index(1)
                _, static.iw_dummy_f = imgui.slider_float("float1", static.iw_dummy_f, 0.0, 1.0)
                imgui.table_set_column_index(2)
                _, static.iw_dummy_f = imgui.slider_float("##float2", static.iw_dummy_f, 0.0, 1.0)
                imgui.pop_id()
            imgui.end_table()
        imgui.tree_pop()

    # Demonstrate using TableHeader() calls instead of TableHeadersRow()
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Custom headers"):
        IMGUI_DEMO_MARKER("Tables/Custom headers")
        COLUMNS_COUNT = 3
        if not hasattr(static, "ch_column_selected"):
            static.ch_column_selected = [False, False, False]
        if imgui.begin_table("table_custom_headers", COLUMNS_COUNT, imgui.TableFlags_.borders | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable):
            imgui.table_setup_column("Apricot")
            imgui.table_setup_column("Banana")
            imgui.table_setup_column("Cherry")

            imgui.table_next_row(imgui.TableRowFlags_.headers)
            for column in range(COLUMNS_COUNT):
                imgui.table_set_column_index(column)
                column_name = imgui.table_get_column_name(column)
                imgui.push_id(column)
                imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(0, 0))
                _, static.ch_column_selected[column] = imgui.checkbox("##checkall", static.ch_column_selected[column])
                imgui.pop_style_var()
                imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
                imgui.table_header(column_name)
                imgui.pop_id()

            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    buf = f"Cell {column},{row}"
                    imgui.table_set_column_index(column)
                    imgui.selectable(buf, static.ch_column_selected[column])
            imgui.end_table()
        imgui.tree_pop()

    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Angled headers"):
        IMGUI_DEMO_MARKER("Tables/Angled headers")
        column_names = ["Track", "cabasa", "ride", "smash", "tom-hi", "tom-mid", "tom-low",
                        "hihat-o", "hihat-c", "snare-s", "snare-c", "clap", "rim", "kick"]
        columns_count = len(column_names)
        rows_count = 12

        if not hasattr(static, "table_flags_ah"):
            static.table_flags_ah = (imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y |
                                     imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_inner_h |
                                     imgui.TableFlags_.hideable | imgui.TableFlags_.resizable |
                                     imgui.TableFlags_.reorderable | imgui.TableFlags_.highlight_hovered_column)

            static.column_flags_ah = imgui.TableColumnFlags_.angled_header | imgui.TableColumnFlags_.width_fixed
            static.bools_ah = [False] * (columns_count * rows_count)  # Dummy selection storage
            static.frozen_cols_ah = 1
            static.frozen_rows_ah = 2

        _, static.table_flags_ah = imgui.checkbox_flags("_ScrollX", static.table_flags_ah, imgui.TableFlags_.scroll_x)
        _, static.table_flags_ah = imgui.checkbox_flags("_ScrollY", static.table_flags_ah, imgui.TableFlags_.scroll_y)
        _, static.table_flags_ah = imgui.checkbox_flags("_Resizable", static.table_flags_ah, imgui.TableFlags_.resizable)
        _, static.table_flags_ah = imgui.checkbox_flags("_Sortable", static.table_flags_ah, imgui.TableFlags_.sortable)
        _, static.table_flags_ah = imgui.checkbox_flags("_NoBordersInBody", static.table_flags_ah, imgui.TableFlags_.no_borders_in_body)
        _, static.table_flags_ah = imgui.checkbox_flags("_HighlightHoveredColumn", static.table_flags_ah, imgui.TableFlags_.highlight_hovered_column)

        imgui.set_next_item_width(imgui.get_font_size() * 8)
        _, static.frozen_cols_ah = imgui.slider_int("Frozen columns", static.frozen_cols_ah, 0, 2)

        imgui.set_next_item_width(imgui.get_font_size() * 8)
        _, static.frozen_rows_ah = imgui.slider_int("Frozen rows", static.frozen_rows_ah, 0, 2)

        _, static.column_flags_ah = imgui.checkbox_flags("Disable header contributing to column width",
                                                         static.column_flags_ah, imgui.TableColumnFlags_.no_header_width)

        if imgui.tree_node("Style settings"):
            imgui.same_line()
            imgui.set_next_item_width(imgui.get_font_size() * 8)
            _, imgui.get_style().table_angled_headers_angle = imgui.slider_angle(
                "style.TableAngledHeadersAngle", imgui.get_style().table_angled_headers_angle, -50.0, +50.0)

            imgui.set_next_item_width(imgui.get_font_size() * 8)
            table_angled_headers_text_align_list = [imgui.get_style().table_angled_headers_text_align.x, imgui.get_style().table_angled_headers_text_align.y]
            changed_it, table_angled_headers_text_align_list = imgui.slider_float2(
                "style.TableAngledHeadersTextAlign",
                table_angled_headers_text_align_list, 0.0, 1.0, "%.2f")
            if changed_it:
                imgui.get_style().table_angled_headers_text_align.x = table_angled_headers_text_align_list[0]
                imgui.get_style().table_angled_headers_text_align.y = table_angled_headers_text_align_list[1]

            imgui.tree_pop()

        text_base_height = imgui.get_text_line_height_with_spacing()
        if imgui.begin_table("table_angled_headers", columns_count, static.table_flags_ah, (0.0, text_base_height * 12)):
            imgui.table_setup_column(column_names[0], imgui.TableColumnFlags_.no_hide | imgui.TableColumnFlags_.no_reorder)

            for n in range(1, columns_count):
                imgui.table_setup_column(column_names[n], static.column_flags_ah)

            imgui.table_setup_scroll_freeze(static.frozen_cols_ah, static.frozen_rows_ah)

            imgui.table_angled_headers_row()  # Draw angled headers for all columns with angled header flag
            imgui.table_headers_row()  # Draw remaining headers

            for row in range(rows_count):
                imgui.push_id(row)
                imgui.table_next_row()
                imgui.table_set_column_index(0)
                imgui.align_text_to_frame_padding()
                imgui.text(f"Track {row}")

                for column in range(1, columns_count):
                    if imgui.table_set_column_index(column):
                        imgui.push_id(column)
                        _, static.bools_ah[row * columns_count + column] = imgui.checkbox("", static.bools_ah[row * columns_count + column])
                        imgui.pop_id()

                imgui.pop_id()

            imgui.end_table()

        imgui.tree_pop()

    # Demonstrate creating custom context menus inside columns,
    # while playing it nice with context menus provided by TableHeadersRow()/TableHeader()
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Context menus"):
        IMGUI_DEMO_MARKER("Tables/Context menus")
        help_marker(
            "By default, right-clicking over a TableHeadersRow()/TableHeader() line will open the default context-menu.\n"
            "Using ImGuiTableFlags_ContextMenuInBody we also allow right-clicking over columns body.")
        if not hasattr(static, "cm_flags1"):
            static.cm_flags1 = imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable | imgui.TableFlags_.borders | imgui.TableFlags_.context_menu_in_body

        push_style_compact()
        _, static.cm_flags1 = imgui.checkbox_flags("ImGuiTableFlags_ContextMenuInBody", static.cm_flags1, imgui.TableFlags_.context_menu_in_body)
        pop_style_compact()

        # Context Menus: first example
        COLUMNS_COUNT = 3
        if imgui.begin_table("table_context_menu", COLUMNS_COUNT, static.cm_flags1):
            imgui.table_setup_column("One")
            imgui.table_setup_column("Two")
            imgui.table_setup_column("Three")
            imgui.table_headers_row()

            for row in range(4):
                imgui.table_next_row()
                for column in range(COLUMNS_COUNT):
                    imgui.table_set_column_index(column)
                    imgui.text(f"Cell {column},{row}")
            imgui.end_table()

        # Context Menus: second example
        help_marker(
            "Demonstrate mixing table context menu (over header), item context button (over button) "
            "and custom per-column context menu (over column body).")
        flags2 = imgui.TableFlags_.resizable | imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable | imgui.TableFlags_.borders
        if imgui.begin_table("table_context_menu_2", COLUMNS_COUNT, flags2):
            imgui.table_setup_column("One")
            imgui.table_setup_column("Two")
            imgui.table_setup_column("Three")
            imgui.table_headers_row()
            for row in range(4):
                imgui.table_next_row()
                for column in range(COLUMNS_COUNT):
                    imgui.table_set_column_index(column)
                    imgui.text(f"Cell {column},{row}")
                    imgui.same_line()

                    imgui.push_id(row * COLUMNS_COUNT + column)
                    imgui.small_button("..")
                    if imgui.begin_popup_context_item():
                        imgui.text(f"This is the popup for Button(\"..\") in Cell {column},{row}")
                        if imgui.button("Close"):
                            imgui.close_current_popup()
                        imgui.end_popup()
                    imgui.pop_id()

            hovered_column = -1
            for column in range(COLUMNS_COUNT + 1):
                imgui.push_id(column)
                if imgui.table_get_column_flags(column) & imgui.TableColumnFlags_.is_hovered:
                    hovered_column = column
                if hovered_column == column and not imgui.is_any_item_hovered() and imgui.is_mouse_released(1):
                    imgui.open_popup("MyPopup")
                if imgui.begin_popup("MyPopup"):
                    if column == COLUMNS_COUNT:
                        imgui.text("This is a custom popup for unused space after the last column.")
                    else:
                        imgui.text(f"This is a custom popup for Column {column}")
                    if imgui.button("Close"):
                        imgui.close_current_popup()
                    imgui.end_popup()
                imgui.pop_id()

            imgui.end_table()
            imgui.text(f"Hovered column: {hovered_column}")
        imgui.tree_pop()

    # Demonstrate creating multiple tables with the same ID
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Synced instances"):
        IMGUI_DEMO_MARKER("Tables/Synced instances")
        help_marker("Multiple tables with the same identifier will share their settings, width, visibility, order etc.")

        if not hasattr(static, "si_flags"):
            static.si_flags = imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable | imgui.TableFlags_.borders | imgui.TableFlags_.sizing_fixed_fit | imgui.TableFlags_.no_saved_settings
        _, static.si_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.si_flags, imgui.TableFlags_.resizable)
        _, static.si_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollY", static.si_flags, imgui.TableFlags_.scroll_y)
        _, static.si_flags = imgui.checkbox_flags("ImGuiTableFlags_SizingFixedFit", static.si_flags, imgui.TableFlags_.sizing_fixed_fit)
        _, static.si_flags = imgui.checkbox_flags("ImGuiTableFlags_HighlightHoveredColumn", static.si_flags, imgui.TableFlags_.highlight_hovered_column)
        for n in range(3):
            buf = f"Synced Table {n}"
            open = imgui.collapsing_header(buf, imgui.TreeNodeFlags_.default_open)
            if open and imgui.begin_table("Table", 3, static.si_flags, ImVec2(0.0, imgui.get_text_line_height_with_spacing() * 5)):
                imgui.table_setup_column("One")
                imgui.table_setup_column("Two")
                imgui.table_setup_column("Three")
                imgui.table_headers_row()
                cell_count = 27 if n == 1 else 9
                for cell in range(cell_count):
                    imgui.table_next_column()
                    imgui.text(f"this cell {cell}")
                imgui.end_table()
        imgui.tree_pop()

    # Demonstrate using Sorting facilities
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Sorting"):
        IMGUI_DEMO_MARKER("Tables/Sorting")
        if not hasattr(static, "sort_items"):
            static.sort_items = []
            for n in range(50):
                template_n = n % len(TEMPLATE_ITEMS_NAMES)
                static.sort_items.append(MyItem(n, TEMPLATE_ITEMS_NAMES[template_n], (n * n - n) % 20))

        if not hasattr(static, "sort_flags"):
            static.sort_flags = (imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable | imgui.TableFlags_.sortable | imgui.TableFlags_.sort_multi
                                 | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_v | imgui.TableFlags_.no_borders_in_body
                                 | imgui.TableFlags_.scroll_y)
        push_style_compact()
        _, static.sort_flags = imgui.checkbox_flags("ImGuiTableFlags_SortMulti", static.sort_flags, imgui.TableFlags_.sort_multi)
        imgui.same_line(); help_marker("When sorting is enabled: hold shift when clicking headers to sort on multiple column. TableGetSortSpecs() may return specs where (SpecsCount > 1).")
        _, static.sort_flags = imgui.checkbox_flags("ImGuiTableFlags_SortTristate", static.sort_flags, imgui.TableFlags_.sort_tristate)
        imgui.same_line(); help_marker("When sorting is enabled: allow no sorting, disable default sorting. TableGetSortSpecs() may return specs where (SpecsCount == 0).")
        pop_style_compact()

        if imgui.begin_table("table_sorting", 4, static.sort_flags, ImVec2(0.0, text_base_height * 15), 0.0):
            imgui.table_setup_column("ID", imgui.TableColumnFlags_.default_sort | imgui.TableColumnFlags_.width_fixed, 0.0, MY_ITEM_COLUMN_ID_ID)
            imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_fixed, 0.0, MY_ITEM_COLUMN_ID_NAME)
            imgui.table_setup_column("Action", imgui.TableColumnFlags_.no_sort | imgui.TableColumnFlags_.width_fixed, 0.0, MY_ITEM_COLUMN_ID_ACTION)
            imgui.table_setup_column("Quantity", imgui.TableColumnFlags_.prefer_sort_descending | imgui.TableColumnFlags_.width_stretch, 0.0, MY_ITEM_COLUMN_ID_QUANTITY)
            imgui.table_setup_scroll_freeze(0, 1)
            imgui.table_headers_row()

            sort_specs = imgui.table_get_sort_specs()
            if sort_specs is not None and sort_specs.specs_dirty:
                MyItem.sort_with_sort_specs(sort_specs, static.sort_items)
                sort_specs.specs_dirty = False

            clipper = imgui.ListClipper()
            clipper.begin(len(static.sort_items))
            while clipper.step():
                for row_n in range(clipper.display_start, clipper.display_end):
                    item = static.sort_items[row_n]
                    imgui.push_id(item.id)
                    imgui.table_next_row()
                    imgui.table_next_column()
                    imgui.text(f"{item.id:04d}")
                    imgui.table_next_column()
                    imgui.text_unformatted(item.name)
                    imgui.table_next_column()
                    imgui.small_button("None")
                    imgui.table_next_column()
                    imgui.text(str(item.quantity))
                    imgui.pop_id()
            imgui.end_table()
        imgui.tree_pop()

    # In this example we'll expose most table flags and settings.
    if open_action != -1:
        imgui.set_next_item_open(open_action != 0)
    if imgui.tree_node("Advanced"):
        IMGUI_DEMO_MARKER("Tables/Advanced")
        CT_TEXT, CT_BUTTON, CT_SMALL_BUTTON, CT_FILL_BUTTON, CT_SELECTABLE, CT_SELECTABLE_SPAN_ROW = range(6)
        contents_type_names = ["Text", "Button", "SmallButton", "FillButton", "Selectable", "Selectable (span row)"]
        if not hasattr(static, "adv_flags"):
            static.adv_flags = (imgui.TableFlags_.resizable | imgui.TableFlags_.reorderable | imgui.TableFlags_.hideable
                                | imgui.TableFlags_.sortable | imgui.TableFlags_.sort_multi
                                | imgui.TableFlags_.row_bg | imgui.TableFlags_.borders | imgui.TableFlags_.no_borders_in_body
                                | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y
                                | imgui.TableFlags_.sizing_fixed_fit)
            static.adv_columns_base_flags = imgui.TableColumnFlags_.none.value
            static.adv_contents_type = CT_SELECTABLE_SPAN_ROW
            static.adv_freeze_cols = 1
            static.adv_freeze_rows = 1
            static.adv_items_count = len(TEMPLATE_ITEMS_NAMES) * 2
            static.adv_outer_size_value = [0.0, text_base_height * 12]
            static.adv_row_min_height = 0.0
            static.adv_inner_width_with_scroll = 0.0
            static.adv_outer_size_enabled = True
            static.adv_show_headers = True
            static.adv_show_wrapped_text = False
            static.adv_items = []
            static.adv_selection = []
            static.adv_items_need_sort = False

        if imgui.tree_node("Options"):
            push_style_compact()
            imgui.push_item_width(text_base_width * 28.0)

            if imgui.tree_node_ex("Features:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.adv_flags, imgui.TableFlags_.resizable)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_Reorderable", static.adv_flags, imgui.TableFlags_.reorderable)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_Hideable", static.adv_flags, imgui.TableFlags_.hideable)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_Sortable", static.adv_flags, imgui.TableFlags_.sortable)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoSavedSettings", static.adv_flags, imgui.TableFlags_.no_saved_settings)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_ContextMenuInBody", static.adv_flags, imgui.TableFlags_.context_menu_in_body)
                imgui.tree_pop()

            if imgui.tree_node_ex("Decorations:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.adv_flags, imgui.TableFlags_.row_bg)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.adv_flags, imgui.TableFlags_.borders_v)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.adv_flags, imgui.TableFlags_.borders_outer_v)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.adv_flags, imgui.TableFlags_.borders_inner_v)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersH", static.adv_flags, imgui.TableFlags_.borders_h)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterH", static.adv_flags, imgui.TableFlags_.borders_outer_h)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerH", static.adv_flags, imgui.TableFlags_.borders_inner_h)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBody", static.adv_flags, imgui.TableFlags_.no_borders_in_body); imgui.same_line(); help_marker("Disable vertical borders in columns Body (borders will always appear in Headers)")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBodyUntilResize", static.adv_flags, imgui.TableFlags_.no_borders_in_body_until_resize); imgui.same_line(); help_marker("Disable vertical borders in columns Body until hovered for resize (borders will always appear in Headers)")
                imgui.tree_pop()

            if imgui.tree_node_ex("Sizing:", imgui.TreeNodeFlags_.default_open):
                static.adv_flags = edit_table_sizing_flags(static.adv_flags)
                imgui.same_line(); help_marker("In the Advanced demo we override the policy of each column so those table-wide settings have less effect that typical.")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendX", static.adv_flags, imgui.TableFlags_.no_host_extend_x)
                imgui.same_line(); help_marker("Make outer width auto-fit to columns, overriding outer_size.x value.\n\nOnly available when ScrollX/ScrollY are disabled and Stretch columns are not used.")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendY", static.adv_flags, imgui.TableFlags_.no_host_extend_y)
                imgui.same_line(); help_marker("Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit).\n\nOnly available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoKeepColumnsVisible", static.adv_flags, imgui.TableFlags_.no_keep_columns_visible)
                imgui.same_line(); help_marker("Only available if ScrollX is disabled.")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_PreciseWidths", static.adv_flags, imgui.TableFlags_.precise_widths)
                imgui.same_line(); help_marker("Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns: Without this flag: 33,33,34. With this flag: 33,33,33). With larger number of columns, resizing will appear to be less smooth.")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoClip", static.adv_flags, imgui.TableFlags_.no_clip)
                imgui.same_line(); help_marker("Disable clipping rectangle for every individual columns (reduce draw command count, items will be able to overflow into other columns). Generally incompatible with ScrollFreeze options.")
                imgui.tree_pop()

            if imgui.tree_node_ex("Padding:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_PadOuterX", static.adv_flags, imgui.TableFlags_.pad_outer_x)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadOuterX", static.adv_flags, imgui.TableFlags_.no_pad_outer_x)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadInnerX", static.adv_flags, imgui.TableFlags_.no_pad_inner_x)
                imgui.tree_pop()

            if imgui.tree_node_ex("Scrolling:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollX", static.adv_flags, imgui.TableFlags_.scroll_x)
                imgui.same_line()
                imgui.set_next_item_width(imgui.get_frame_height())
                _, static.adv_freeze_cols = imgui.drag_int("freeze_cols", static.adv_freeze_cols, 0.2, 0, 9, "%d", imgui.SliderFlags_.no_input)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_ScrollY", static.adv_flags, imgui.TableFlags_.scroll_y)
                imgui.same_line()
                imgui.set_next_item_width(imgui.get_frame_height())
                _, static.adv_freeze_rows = imgui.drag_int("freeze_rows", static.adv_freeze_rows, 0.2, 0, 9, "%d", imgui.SliderFlags_.no_input)
                imgui.tree_pop()

            if imgui.tree_node_ex("Sorting:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_SortMulti", static.adv_flags, imgui.TableFlags_.sort_multi)
                imgui.same_line(); help_marker("When sorting is enabled: hold shift when clicking headers to sort on multiple column. TableGetSortSpecs() may return specs where (SpecsCount > 1).")
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_SortTristate", static.adv_flags, imgui.TableFlags_.sort_tristate)
                imgui.same_line(); help_marker("When sorting is enabled: allow no sorting, disable default sorting. TableGetSortSpecs() may return specs where (SpecsCount == 0).")
                imgui.tree_pop()

            if imgui.tree_node_ex("Headers:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_show_headers = imgui.checkbox("show_headers", static.adv_show_headers)
                _, static.adv_flags = imgui.checkbox_flags("ImGuiTableFlags_HighlightHoveredColumn", static.adv_flags, imgui.TableFlags_.highlight_hovered_column)
                _, static.adv_columns_base_flags = imgui.checkbox_flags("ImGuiTableColumnFlags_AngledHeader", static.adv_columns_base_flags, imgui.TableColumnFlags_.angled_header)
                imgui.same_line(); help_marker("Enable AngledHeader on all columns. Best enabled on selected narrow columns (see \"Angled headers\" section of the demo).")
                imgui.tree_pop()

            if imgui.tree_node_ex("Other:", imgui.TreeNodeFlags_.default_open):
                _, static.adv_show_wrapped_text = imgui.checkbox("show_wrapped_text", static.adv_show_wrapped_text)

                _, static.adv_outer_size_value = imgui.drag_float2("##OuterSize", static.adv_outer_size_value)
                imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
                _, static.adv_outer_size_enabled = imgui.checkbox("outer_size", static.adv_outer_size_enabled)
                imgui.same_line()
                help_marker("If scrolling is disabled (ScrollX and ScrollY not set):\n"
                    "- The table is output directly in the parent window.\n"
                    "- OuterSize.x < 0.0f will right-align the table.\n"
                    "- OuterSize.x = 0.0f will narrow fit the table unless there are any Stretch columns.\n"
                    "- OuterSize.y then becomes the minimum size for the table, which will extend vertically if there are more rows (unless NoHostExtendY is set).")

                _, static.adv_inner_width_with_scroll = imgui.drag_float("inner_width (when ScrollX active)", static.adv_inner_width_with_scroll, 1.0, 0.0, imgui.FLT_MAX)

                _, static.adv_row_min_height = imgui.drag_float("row_min_height", static.adv_row_min_height, 1.0, 0.0, imgui.FLT_MAX)
                imgui.same_line(); help_marker("Specify height of the Selectable item.")

                _, static.adv_items_count = imgui.drag_int("items_count", static.adv_items_count, 0.1, 0, 9999)
                _, static.adv_contents_type = imgui.combo("items_type (first column)", static.adv_contents_type, contents_type_names)
                imgui.tree_pop()

            imgui.pop_item_width()
            pop_style_compact()
            imgui.spacing()
            imgui.tree_pop()

        # Update item list if we changed the number of items
        if len(static.adv_items) != static.adv_items_count:
            static.adv_items = []
            for n in range(static.adv_items_count):
                template_n = n % len(TEMPLATE_ITEMS_NAMES)
                item = MyItem(n, TEMPLATE_ITEMS_NAMES[template_n], 10 if template_n == 3 else (20 if template_n == 4 else 0))
                static.adv_items.append(item)

        parent_draw_list = imgui.get_window_draw_list()
        parent_draw_list_draw_cmd_count = parent_draw_list.cmd_buffer.size()
        table_scroll_cur = ImVec2(0, 0)
        table_scroll_max = ImVec2(0, 0)
        table_draw_list = None

        # Submit table
        inner_width_to_use = static.adv_inner_width_with_scroll if (static.adv_flags & imgui.TableFlags_.scroll_x) else 0.0
        outer_size = ImVec2(static.adv_outer_size_value[0], static.adv_outer_size_value[1]) if static.adv_outer_size_enabled else ImVec2(0, 0)
        if imgui.begin_table("table_advanced", 6, static.adv_flags, outer_size, inner_width_to_use):
            imgui.table_setup_column("ID", static.adv_columns_base_flags | imgui.TableColumnFlags_.default_sort | imgui.TableColumnFlags_.width_fixed | imgui.TableColumnFlags_.no_hide, 0.0, MY_ITEM_COLUMN_ID_ID)
            imgui.table_setup_column("Name", static.adv_columns_base_flags | imgui.TableColumnFlags_.width_fixed, 0.0, MY_ITEM_COLUMN_ID_NAME)
            imgui.table_setup_column("Action", static.adv_columns_base_flags | imgui.TableColumnFlags_.no_sort | imgui.TableColumnFlags_.width_fixed, 0.0, MY_ITEM_COLUMN_ID_ACTION)
            imgui.table_setup_column("Quantity", static.adv_columns_base_flags | imgui.TableColumnFlags_.prefer_sort_descending, 0.0, MY_ITEM_COLUMN_ID_QUANTITY)
            no_host_extend_x = imgui.TableColumnFlags_.width_stretch if not (static.adv_flags & imgui.TableFlags_.no_host_extend_x) else imgui.TableColumnFlags_.none
            imgui.table_setup_column("Description", static.adv_columns_base_flags | no_host_extend_x, 0.0, MY_ITEM_COLUMN_ID_DESCRIPTION)
            imgui.table_setup_column("Hidden", static.adv_columns_base_flags | imgui.TableColumnFlags_.default_hide | imgui.TableColumnFlags_.no_sort)
            imgui.table_setup_scroll_freeze(static.adv_freeze_cols, static.adv_freeze_rows)

            # Sort our data if sort specs have been changed!
            sort_specs = imgui.table_get_sort_specs()
            if sort_specs is not None and sort_specs.specs_dirty:
                static.adv_items_need_sort = True
            if sort_specs is not None and static.adv_items_need_sort and len(static.adv_items) > 1:
                MyItem.sort_with_sort_specs(sort_specs, static.adv_items)
                sort_specs.specs_dirty = False
            static.adv_items_need_sort = False

            sorts_specs_using_quantity = (imgui.table_get_column_flags(3) & imgui.TableColumnFlags_.is_sorted) != 0

            # Show headers
            if static.adv_show_headers and (static.adv_columns_base_flags & imgui.TableColumnFlags_.angled_header) != 0:
                imgui.table_angled_headers_row()
            if static.adv_show_headers:
                imgui.table_headers_row()

            # Show data
            clipper = imgui.ListClipper()
            clipper.begin(len(static.adv_items))
            while clipper.step():
                for row_n in range(clipper.display_start, clipper.display_end):
                    item = static.adv_items[row_n]
                    item_is_selected = item.id in static.adv_selection
                    imgui.push_id(item.id)
                    imgui.table_next_row(imgui.TableRowFlags_.none, static.adv_row_min_height)

                    # First column
                    imgui.table_set_column_index(0)
                    label = f"{item.id:04d}"
                    if static.adv_contents_type == CT_TEXT:
                        imgui.text_unformatted(label)
                    elif static.adv_contents_type == CT_BUTTON:
                        imgui.button(label)
                    elif static.adv_contents_type == CT_SMALL_BUTTON:
                        imgui.small_button(label)
                    elif static.adv_contents_type == CT_FILL_BUTTON:
                        imgui.button(label, ImVec2(-imgui.FLT_MIN, 0.0))
                    elif static.adv_contents_type in (CT_SELECTABLE, CT_SELECTABLE_SPAN_ROW):
                        selectable_flags = (imgui.SelectableFlags_.span_all_columns | imgui.SelectableFlags_.allow_overlap) if static.adv_contents_type == CT_SELECTABLE_SPAN_ROW else imgui.SelectableFlags_.none
                        clicked, _ = imgui.selectable(label, item_is_selected, selectable_flags, ImVec2(0, static.adv_row_min_height))
                        if clicked:
                            if imgui.get_io().key_ctrl:
                                if item_is_selected:
                                    static.adv_selection.remove(item.id)
                                else:
                                    static.adv_selection.append(item.id)
                            else:
                                static.adv_selection.clear()
                                static.adv_selection.append(item.id)

                    if imgui.table_set_column_index(1):
                        imgui.text_unformatted(item.name)

                    if imgui.table_set_column_index(2):
                        if imgui.small_button("Chop"):
                            item.quantity += 1
                        if sorts_specs_using_quantity and imgui.is_item_deactivated():
                            static.adv_items_need_sort = True
                        imgui.same_line()
                        if imgui.small_button("Eat"):
                            item.quantity -= 1
                        if sorts_specs_using_quantity and imgui.is_item_deactivated():
                            static.adv_items_need_sort = True

                    if imgui.table_set_column_index(3):
                        imgui.text(str(item.quantity))

                    imgui.table_set_column_index(4)
                    if static.adv_show_wrapped_text:
                        imgui.text_wrapped("Lorem ipsum dolor sit amet")
                    else:
                        imgui.text("Lorem ipsum dolor sit amet")

                    if imgui.table_set_column_index(5):
                        imgui.text("1234")

                    imgui.pop_id()

            table_scroll_cur = ImVec2(imgui.get_scroll_x(), imgui.get_scroll_y())
            table_scroll_max = ImVec2(imgui.get_scroll_max_x(), imgui.get_scroll_max_y())
            table_draw_list = imgui.get_window_draw_list()
            imgui.end_table()

        if not hasattr(static, "adv_show_debug_details"):
            static.adv_show_debug_details = False
        _, static.adv_show_debug_details = imgui.checkbox("Debug details", static.adv_show_debug_details)
        if static.adv_show_debug_details and table_draw_list is not None:
            imgui.same_line(0.0, 0.0)
            table_draw_list_draw_cmd_count = table_draw_list.cmd_buffer.size()
            if table_draw_list == parent_draw_list:
                imgui.text(f": DrawCmd: +{table_draw_list_draw_cmd_count - parent_draw_list_draw_cmd_count} (in same window)")
            else:
                imgui.text(f": DrawCmd: +{table_draw_list_draw_cmd_count - 1} (in child window), Scroll: ({table_scroll_cur.x:.0f}/{table_scroll_max.x:.0f}) ({table_scroll_cur.y:.0f}/{table_scroll_max.y:.0f})")
        imgui.tree_pop()

    show_demo_window_columns()

    if static.disable_indent:
        imgui.pop_style_var()

    imgui.pop_id() ## tables


# Note that shortcuts are currently provided for display only
# (future version will add explicit flags to BeginMenu() to request processing shortcuts)
def show_example_menu_file():
    static = show_example_menu_file

    IMGUI_DEMO_MARKER("Examples/Menu")
    imgui.menu_item_simple("(demo menu)")
    if imgui.menu_item_simple("New"):
        pass
    if imgui.menu_item_simple("Open", "Ctrl+O"):
        pass
    if imgui.begin_menu("Open Recent"):
        imgui.menu_item_simple("fish_hat.c")
        imgui.menu_item_simple("fish_hat.inl")
        imgui.menu_item_simple("fish_hat.h")
        if imgui.begin_menu("More.."):
            imgui.menu_item_simple("Hello")
            imgui.menu_item_simple("Sailor")
            if imgui.begin_menu("Recurse.."):
                show_example_menu_file()
                imgui.end_menu()
            imgui.end_menu()
        imgui.end_menu()
    if imgui.menu_item_simple("Save", "Ctrl+S"):
        pass
    if imgui.menu_item_simple("Save As.."):
        pass

    imgui.separator()
    IMGUI_DEMO_MARKER("Examples/Menu/Options")
    if imgui.begin_menu("Options"):
        if not hasattr(static, "enabled"):
            static.enabled = True
        _, static.enabled = imgui.menu_item("Enabled", "", static.enabled)
        imgui.begin_child("child", ImVec2(0, 60), True)
        for i in range(10):
            imgui.text("Scrolling Text %d" % i)
        imgui.end_child()
        if not hasattr(static, "f"):
            static.f = 0.5
            static.n = 0
        _, static.f = imgui.slider_float("Value", static.f, 0.0, 1.0)
        _, static.f = imgui.input_float("Input", static.f, 0.1)
        items = ["Yes", "No", "Maybe", ""]
        _, static.n = imgui.combo("Combo", static.n, items)
        imgui.end_menu()

    IMGUI_DEMO_MARKER("Examples/Menu/Colors")
    if imgui.begin_menu("Colors"):
        sz = imgui.get_text_line_height()
        for i in range(imgui.Col_.count):
            name = imgui.get_style_color_name(i)
            p = imgui.get_cursor_screen_pos()
            imgui.get_window_draw_list().add_rect_filled(p, ImVec2(p.x + sz, p.y + sz), imgui.get_color_u32(i))
            imgui.dummy(ImVec2(sz, sz))
            imgui.same_line()
            imgui.menu_item_simple(name)
        imgui.end_menu()

    # Here we demonstrate appending again to the "Options" menu (which we already created above)
    # Of course in this demo it is a little bit silly that this function calls BeginMenu("Options") twice.
    # In a real code-base using it would make sense to use this feature from very different code locations.
    if imgui.begin_menu("Options"):  # <-- Append!
        IMGUI_DEMO_MARKER("Examples/Menu/Append to an existing menu")
        if not hasattr(static, "b"):
            static.b = True
        _, static.b = imgui.checkbox("SomeOption", static.b)
        imgui.end_menu()

    if imgui.begin_menu("Disabled", False):  # Disabled
        raise Exception("should not happen")
    if imgui.menu_item_simple("Checked", None, True):
        pass
    imgui.separator()
    if imgui.menu_item_simple("Quit", "Alt+F4"):
        pass


# -----------------------------------------------------------------------------
# [SECTION] Example App: Main Menu Bar / ShowExampleAppMainMenuBar()
# -----------------------------------------------------------------------------

def _show_example_app_main_menu_bar_impl():
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File"):
            IMGUI_DEMO_MARKER("ShowExampleAppMainMenuBar - Menu File")
            show_example_menu_file()
            imgui.end_menu()
        if imgui.begin_menu("Edit"):
            IMGUI_DEMO_MARKER("ShowExampleAppMainMenuBar - Menu Edit")
            if imgui.menu_item_simple("Undo", "Ctrl+Z"):
                pass
            if imgui.menu_item("Redo", "Ctrl+Y", False, False)[0]:  # Disabled item
                pass
            imgui.separator()
            if imgui.menu_item_simple("Cut", "Ctrl+X"):
                pass
            if imgui.menu_item_simple("Copy", "Ctrl+C"):
                pass
            if imgui.menu_item_simple("Paste", "Ctrl+V"):
                pass
            imgui.end_menu()
        imgui.end_main_menu_bar()

show_example_app_main_menu_bar = _show_example_app_main_menu_bar_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Auto Resize / ShowExampleAppAutoResize()
# -----------------------------------------------------------------------------

def _show_example_app_auto_resize_impl(p_open: bool) -> bool:
    static = _show_example_app_auto_resize_impl
    visible, p_open = imgui.begin("Example: Auto-resizing window", p_open, imgui.WindowFlags_.always_auto_resize.value)
    if not visible:
        imgui.end()
        return p_open
    IMGUI_DEMO_MARKER("ShowExampleAppAutoResize")

    if not hasattr(static, "lines"):
        static.lines = 10
    imgui.text_unformatted(
        "Window will resize every-frame to the size of its content.\n"
        "Note that you probably don't want to query the window size to\n"
        "output your content because that would create a feedback loop."
    )
    _, static.lines = imgui.slider_int("Number of lines", static.lines, 1, 20)
    for i in range(static.lines):
        imgui.text("%sThis is line %d" % (" " * (i * 4), i))
    imgui.end()
    return p_open

show_example_app_auto_resize = _show_example_app_auto_resize_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Constrained Resize / ShowExampleAppConstrainedResize()
# -----------------------------------------------------------------------------

def _show_example_app_constrained_resize_impl(p_open: bool) -> bool:
    static = _show_example_app_constrained_resize_impl
    IMGUI_DEMO_MARKER("ShowExampleAppConstrainedResize")

    if not hasattr(static, "auto_resize"):
        static.auto_resize = False
        static.window_padding = True
        static.type = 6  # Aspect Ratio
        static.display_lines = 10

    test_desc = [
        "Between 100x100 and 500x500",
        "At least 100x100",
        "Resize vertical + lock current width",
        "Resize horizontal + lock current height",
        "Width Between 400 and 500",
        "Height at least 400",
        "Custom: Aspect Ratio 16:9",
        "Custom: Always Square",
        "Custom: Fixed Steps (100)",
    ]

    # Custom constraint callbacks
    def aspect_ratio_cb(data: imgui.SizeCallbackData):
        ratio = 16.0 / 9.0
        data.desired_size = ImVec2(data.desired_size.x, int(data.desired_size.x / ratio))

    def square_cb(data: imgui.SizeCallbackData):
        s = max(data.desired_size.x, data.desired_size.y)
        data.desired_size = ImVec2(s, s)

    def step_cb(data: imgui.SizeCallbackData):
        step = 100.0
        data.desired_size = ImVec2(
            int(data.desired_size.x / step + 0.5) * step,
            int(data.desired_size.y / step + 0.5) * step,
        )

    FLT_MAX = 3.402823466e+38
    t = static.type
    if t == 0:
        imgui.set_next_window_size_constraints(ImVec2(100, 100), ImVec2(500, 500))
    elif t == 1:
        imgui.set_next_window_size_constraints(ImVec2(100, 100), ImVec2(FLT_MAX, FLT_MAX))
    elif t == 2:
        imgui.set_next_window_size_constraints(ImVec2(-1, 0), ImVec2(-1, FLT_MAX))
    elif t == 3:
        imgui.set_next_window_size_constraints(ImVec2(0, -1), ImVec2(FLT_MAX, -1))
    elif t == 4:
        imgui.set_next_window_size_constraints(ImVec2(400, -1), ImVec2(500, -1))
    elif t == 5:
        imgui.set_next_window_size_constraints(ImVec2(-1, 400), ImVec2(-1, FLT_MAX))
    elif t == 6:
        imgui.set_next_window_size_constraints(ImVec2(0, 0), ImVec2(FLT_MAX, FLT_MAX), aspect_ratio_cb)
    elif t == 7:
        imgui.set_next_window_size_constraints(ImVec2(0, 0), ImVec2(FLT_MAX, FLT_MAX), square_cb)
    elif t == 8:
        imgui.set_next_window_size_constraints(ImVec2(0, 0), ImVec2(FLT_MAX, FLT_MAX), step_cb)

    if not static.window_padding:
        imgui.push_style_var(imgui.StyleVar_.window_padding, ImVec2(0.0, 0.0))
    window_flags = imgui.WindowFlags_.always_auto_resize.value if static.auto_resize else 0
    window_open, p_open = imgui.begin("Example: Constrained Resize", p_open, window_flags)
    if not static.window_padding:
        imgui.pop_style_var()
    if window_open:
        IMGUI_DEMO_MARKER("ShowExampleAppConstrainedResize")
        if imgui.get_io().key_shift:
            avail_size = imgui.get_content_region_avail()
            pos = imgui.get_cursor_screen_pos()
            imgui.color_button(
                "viewport",
                ImVec4(0.5, 0.2, 0.5, 1.0),
                imgui.ColorEditFlags_.no_tooltip.value | imgui.ColorEditFlags_.no_drag_drop.value,
                avail_size,
            )
            imgui.set_cursor_screen_pos(ImVec2(pos.x + 10, pos.y + 10))
            imgui.text("%.2f x %.2f" % (avail_size.x, avail_size.y))
        else:
            imgui.text("(Hold Shift to display a dummy viewport)")
            if imgui.is_window_docked():
                imgui.text("Warning: Sizing Constraints won't work if the window is docked!")
            if imgui.button("Set 200x200"):
                imgui.set_window_size("Example: Constrained Resize", ImVec2(200, 200))
            imgui.same_line()
            if imgui.button("Set 500x500"):
                imgui.set_window_size("Example: Constrained Resize", ImVec2(500, 500))
            imgui.same_line()
            if imgui.button("Set 800x200"):
                imgui.set_window_size("Example: Constrained Resize", ImVec2(800, 200))
            imgui.set_next_item_width(imgui.get_font_size() * 20)
            _, static.type = imgui.combo("Constraint", static.type, test_desc)
            imgui.set_next_item_width(imgui.get_font_size() * 20)
            _, static.display_lines = imgui.drag_int("Lines", static.display_lines, 0.2, 1, 100)
            _, static.auto_resize = imgui.checkbox("Auto-resize", static.auto_resize)
            _, static.window_padding = imgui.checkbox("Window padding", static.window_padding)
            for i in range(static.display_lines):
                imgui.text("%sHello, sailor! Making this line long enough for the example." % (" " * (i * 4)))
    imgui.end()
    return p_open

show_example_app_constrained_resize = _show_example_app_constrained_resize_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Simple overlay / ShowExampleAppSimpleOverlay()
# -----------------------------------------------------------------------------

def _show_example_app_simple_overlay_impl(p_open: bool) -> bool:
    static = _show_example_app_simple_overlay_impl
    if not hasattr(static, "location"):
        static.location = 0

    io = imgui.get_io()
    window_flags = (
        imgui.WindowFlags_.no_decoration.value
        | imgui.WindowFlags_.no_docking.value
        | imgui.WindowFlags_.always_auto_resize.value
        | imgui.WindowFlags_.no_saved_settings.value
        | imgui.WindowFlags_.no_focus_on_appearing.value
        | imgui.WindowFlags_.no_nav.value
    )
    if static.location >= 0:
        PAD = 10.0
        viewport = imgui.get_main_viewport()
        work_pos = viewport.work_pos
        work_size = viewport.work_size
        window_pos = ImVec2(
            (work_pos.x + work_size.x - PAD) if (static.location & 1) else (work_pos.x + PAD),
            (work_pos.y + work_size.y - PAD) if (static.location & 2) else (work_pos.y + PAD),
        )
        window_pos_pivot = ImVec2(
            1.0 if (static.location & 1) else 0.0,
            1.0 if (static.location & 2) else 0.0,
        )
        imgui.set_next_window_pos(window_pos, imgui.Cond_.always.value, window_pos_pivot)
        imgui.set_next_window_viewport(viewport.id_)
        window_flags |= imgui.WindowFlags_.no_move.value
    elif static.location == -2:
        imgui.set_next_window_pos(
            imgui.get_main_viewport().get_center(), imgui.Cond_.always.value, ImVec2(0.5, 0.5)
        )
        window_flags |= imgui.WindowFlags_.no_move.value

    imgui.set_next_window_bg_alpha(0.35)
    visible, p_open = imgui.begin("Example: Simple overlay", p_open, window_flags)
    if visible:
        IMGUI_DEMO_MARKER("ShowExampleAppSimpleOverlay")
        imgui.text("Simple overlay\n(right-click to change position)")
        imgui.separator()
        if imgui.is_mouse_pos_valid():
            imgui.text("Mouse Position: (%.1f,%.1f)" % (io.mouse_pos.x, io.mouse_pos.y))
        else:
            imgui.text("Mouse Position: <invalid>")
        if imgui.begin_popup_context_window():
            if imgui.menu_item_simple("Custom", None, static.location == -1):
                static.location = -1
            if imgui.menu_item_simple("Center", None, static.location == -2):
                static.location = -2
            if imgui.menu_item_simple("Top-left", None, static.location == 0):
                static.location = 0
            if imgui.menu_item_simple("Top-right", None, static.location == 1):
                static.location = 1
            if imgui.menu_item_simple("Bottom-left", None, static.location == 2):
                static.location = 2
            if imgui.menu_item_simple("Bottom-right", None, static.location == 3):
                static.location = 3
            if p_open and imgui.menu_item_simple("Close"):
                p_open = False
            imgui.end_popup()
    imgui.end()
    return p_open

show_example_app_simple_overlay = _show_example_app_simple_overlay_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Fullscreen window / ShowExampleAppFullscreen()
# -----------------------------------------------------------------------------

def _show_example_app_fullscreen_impl(p_open: bool) -> bool:
    static = _show_example_app_fullscreen_impl
    if not hasattr(static, "use_work_area"):
        static.use_work_area = True
        static.flags = imgui.WindowFlags_.no_decoration.value | imgui.WindowFlags_.no_move.value | imgui.WindowFlags_.no_saved_settings.value

    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.work_pos if static.use_work_area else viewport.pos)
    imgui.set_next_window_size(viewport.work_size if static.use_work_area else viewport.size)

    visible, p_open = imgui.begin("Example: Fullscreen window", p_open, static.flags)
    if visible:
        IMGUI_DEMO_MARKER("ShowExampleAppFullscreen")
        _, static.use_work_area = imgui.checkbox("Use work area instead of main area", static.use_work_area)
        imgui.same_line()
        help_marker(
            "Main Area = entire viewport,\n"
            "Work Area = entire viewport minus sections used by the main menu bars, task bars etc.\n\n"
            "Enable the main-menu bar in Examples menu to see the difference."
        )

        _, static.flags = imgui.checkbox_flags("ImGuiWindowFlags_NoBackground", static.flags, imgui.WindowFlags_.no_background.value)
        _, static.flags = imgui.checkbox_flags("ImGuiWindowFlags_NoDecoration", static.flags, imgui.WindowFlags_.no_decoration.value)
        imgui.indent()
        _, static.flags = imgui.checkbox_flags("ImGuiWindowFlags_NoTitleBar", static.flags, imgui.WindowFlags_.no_title_bar.value)
        _, static.flags = imgui.checkbox_flags("ImGuiWindowFlags_NoCollapse", static.flags, imgui.WindowFlags_.no_collapse.value)
        _, static.flags = imgui.checkbox_flags("ImGuiWindowFlags_NoScrollbar", static.flags, imgui.WindowFlags_.no_scrollbar.value)
        imgui.unindent()

        if p_open and imgui.button("Close this window"):
            p_open = False
    imgui.end()
    return p_open

show_example_app_fullscreen = _show_example_app_fullscreen_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Manipulating Window Titles / ShowExampleAppWindowTitles()
# -----------------------------------------------------------------------------

def _show_example_app_window_titles_impl(p_open: bool) -> bool:
    viewport = imgui.get_main_viewport()
    base_pos = viewport.pos

    imgui.set_next_window_pos(ImVec2(base_pos.x + 100, base_pos.y + 100), imgui.Cond_.first_use_ever.value)
    imgui.begin("Same title as another window##1")
    IMGUI_DEMO_MARKER("ShowExampleAppWindowTitles - window##1")
    imgui.text("This is window 1.\nMy title is the same as window 2, but my identifier is unique.")
    imgui.end()

    imgui.set_next_window_pos(ImVec2(base_pos.x + 100, base_pos.y + 200), imgui.Cond_.first_use_ever.value)
    imgui.begin("Same title as another window##2")
    IMGUI_DEMO_MARKER("ShowExampleAppWindowTitles - window##2")
    imgui.text("This is window 2.\nMy title is the same as window 1, but my identifier is unique.")
    imgui.end()

    chars = "|/-\\"
    idx = int(imgui.get_time() / 0.25) & 3
    buf = f"Animated title {chars[idx]} {imgui.get_frame_count()}###AnimatedTitle"
    imgui.set_next_window_pos(ImVec2(base_pos.x + 100, base_pos.y + 300), imgui.Cond_.first_use_ever.value)
    imgui.begin(buf)
    IMGUI_DEMO_MARKER("ShowExampleAppWindowTitles - window##3")
    imgui.text("This window has a changing title.")
    imgui.end()
    return p_open

show_example_app_window_titles = _show_example_app_window_titles_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Long Text / ShowExampleAppLongText()
# -----------------------------------------------------------------------------

def _show_example_app_long_text_impl(p_open: bool) -> bool:
    static = _show_example_app_long_text_impl

    imgui.set_next_window_size(ImVec2(520, 600), imgui.Cond_.first_use_ever.value)
    visible, p_open = imgui.begin("Example: Long text display", p_open)
    if not visible:
        imgui.end()
        return p_open
    IMGUI_DEMO_MARKER("ShowExampleAppLongText")

    if not hasattr(static, "test_type"):
        static.test_type = 0
        static.log_lines: list[str] = []

    imgui.text("Printing unusually long amount of text.")
    _, static.test_type = imgui.combo(
        "Test type",
        static.test_type,
        ["Single call to TextUnformatted()", "Multiple calls to Text(), clipped", "Multiple calls to Text(), not clipped (slow)"],
    )
    imgui.text("Buffer contents: %d lines" % len(static.log_lines))
    if imgui.button("Clear"):
        static.log_lines.clear()
    imgui.same_line()
    if imgui.button("Add 1000 lines"):
        base = len(static.log_lines)
        for i in range(1000):
            static.log_lines.append("%i The quick brown fox jumps over the lazy dog" % (base + i))

    imgui.begin_child("Log")
    if static.test_type == 0:
        # Single call to TextUnformatted() with a big buffer
        imgui.text_unformatted("\n".join(static.log_lines))
    elif static.test_type == 1:
        # Multiple calls to Text(), manually coarsely clipped
        imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(0, 0))
        clipper = imgui.ListClipper()
        clipper.begin(len(static.log_lines))
        while clipper.step():
            for i in range(clipper.display_start, clipper.display_end):
                imgui.text(static.log_lines[i])
        imgui.pop_style_var()
    elif static.test_type == 2:
        # Multiple calls to Text(), not clipped (slow)
        imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(0, 0))
        for line in static.log_lines:
            imgui.text(line)
        imgui.pop_style_var()
    imgui.end_child()
    imgui.end()
    return p_open

show_example_app_long_text = _show_example_app_long_text_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Simple Layout / ShowExampleAppLayout()
# -----------------------------------------------------------------------------

def _show_example_app_layout_impl(p_open: bool) -> bool:
    static = _show_example_app_layout_impl

    imgui.set_next_window_size(ImVec2(500, 440), imgui.Cond_.first_use_ever.value)
    visible, p_open = imgui.begin("Example: Simple layout", p_open, imgui.WindowFlags_.menu_bar.value)
    if visible:
        IMGUI_DEMO_MARKER("ShowExampleAppLayout")
        if imgui.begin_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item_simple("Close", "Ctrl+W"):
                    p_open = False
                imgui.end_menu()
            imgui.end_menu_bar()

        # Left
        if not hasattr(static, "selected"):
            static.selected = 0
        imgui.begin_child(
            "left pane",
            ImVec2(150, 0),
            imgui.ChildFlags_.borders.value | imgui.ChildFlags_.resize_x.value,
        )
        for i in range(100):
            label = "MyObject %d" % i
            if imgui.selectable(label, static.selected == i, imgui.SelectableFlags_.select_on_nav.value)[0]:
                static.selected = i
        imgui.end_child()
        imgui.same_line()

        # Right
        imgui.begin_group()
        imgui.begin_child("item view", ImVec2(0, -imgui.get_frame_height_with_spacing()))
        imgui.text("MyObject: %d" % static.selected)
        imgui.separator()
        if imgui.begin_tab_bar("##Tabs", imgui.TabBarFlags_.none.value):
            if imgui.begin_tab_item("Description")[0]:
                imgui.text_wrapped(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                    "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                )
                imgui.end_tab_item()
            if imgui.begin_tab_item("Details")[0]:
                imgui.text("ID: 0123456789")
                imgui.end_tab_item()
            imgui.end_tab_bar()
        imgui.end_child()
        if imgui.button("Revert"):
            pass
        imgui.same_line()
        if imgui.button("Save"):
            pass
        imgui.end_group()
    imgui.end()
    return p_open

show_example_app_layout = _show_example_app_layout_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Debug Log / ShowExampleAppLog()
# -----------------------------------------------------------------------------

class ExampleAppLog:
    """Simple log window with basic filtering."""

    def __init__(self):
        self.lines: list[str] = []
        self.filter = imgui.TextFilter()
        self.auto_scroll = True

    def clear(self):
        self.lines.clear()

    def add_log(self, msg: str):
        self.lines.append(msg)

    def draw(self, title: str, p_open: bool) -> bool:
        visible, p_open = imgui.begin(title, p_open)
        if not visible:
            imgui.end()
            return p_open

        # Options menu
        if imgui.begin_popup("Options"):
            _, self.auto_scroll = imgui.checkbox("Auto-scroll", self.auto_scroll)
            imgui.end_popup()

        # Main window
        if imgui.button("Options"):
            imgui.open_popup("Options")
        imgui.same_line()
        clear_pressed = imgui.button("Clear")
        imgui.same_line()
        copy_pressed = imgui.button("Copy")
        imgui.same_line()
        self.filter.draw("Filter", -100.0)

        imgui.separator()

        if imgui.begin_child("scrolling", ImVec2(0, 0), imgui.ChildFlags_.none.value, imgui.WindowFlags_.horizontal_scrollbar.value):
            if clear_pressed:
                self.clear()
            if copy_pressed:
                imgui.log_to_clipboard()

            imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(0, 0))
            if self.filter.is_active():
                for line in self.lines:
                    if self.filter.pass_filter(line):
                        imgui.text_unformatted(line)
            else:
                clipper = imgui.ListClipper()
                clipper.begin(len(self.lines))
                while clipper.step():
                    for i in range(clipper.display_start, clipper.display_end):
                        imgui.text_unformatted(self.lines[i])
            imgui.pop_style_var()

            if self.auto_scroll and imgui.get_scroll_y() >= imgui.get_scroll_max_y():
                imgui.set_scroll_here_y(1.0)
        imgui.end_child()
        imgui.end()
        return p_open


def _show_example_app_log_impl(p_open: bool) -> bool:
    static = _show_example_app_log_impl
    if not hasattr(static, "log"):
        static.log = ExampleAppLog()
        static.counter = 0

    # Add a debug button BEFORE the normal log window contents
    imgui.set_next_window_size(ImVec2(500, 400), imgui.Cond_.first_use_ever.value)
    _, p_open = imgui.begin("Example: Log", p_open)
    IMGUI_DEMO_MARKER("ShowExampleAppLog")
    if imgui.small_button("[Debug] Add 5 entries"):
        categories = ["info", "warn", "error"]
        words = ["Bumfuzzled", "Cattywampus", "Snickersnee", "Abibliophobia", "Absquatulate", "Nincompoop", "Pauciloquent"]
        for n in range(5):
            category = categories[static.counter % len(categories)]
            word = words[static.counter % len(words)]
            static.log.add_log(
                "[%05d] [%s] Hello, current time is %.1f, here's a word: '%s'"
                % (imgui.get_frame_count(), category, imgui.get_time(), word)
            )
            static.counter += 1
    imgui.end()

    # Actually call in the regular Log helper
    p_open = static.log.draw("Example: Log", p_open)
    return p_open

show_example_app_log = _show_example_app_log_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Debug Console / ShowExampleAppConsole()
# -----------------------------------------------------------------------------

class ExampleAppConsole:
    """Simple console with basic coloring, completion (TAB key) and history (Up/Down keys)."""

    def __init__(self):
        self.input_buf = ""
        self.items: list[str] = []
        self.commands = ["HELP", "HISTORY", "CLEAR", "CLASSIFY"]
        self.history: list[str] = []
        self.history_pos = -1
        self.auto_scroll = True
        self.scroll_to_bottom = False
        self.add_log("Welcome to Dear ImGui!")

    def clear_log(self):
        self.items.clear()

    def add_log(self, msg: str):
        self.items.append(msg)

    def exec_command(self, command_line: str):
        self.add_log("# %s" % command_line)

        # Insert into history (remove duplicate first)
        self.history_pos = -1
        for i in range(len(self.history) - 1, -1, -1):
            if self.history[i].upper() == command_line.upper():
                self.history.pop(i)
                break
        self.history.append(command_line)

        # Process command
        cmd = command_line.strip().upper()
        if cmd == "CLEAR":
            self.clear_log()
        elif cmd == "HELP":
            self.add_log("Commands:")
            for c in self.commands:
                self.add_log("- %s" % c)
        elif cmd == "HISTORY":
            first = max(0, len(self.history) - 10)
            for i in range(first, len(self.history)):
                self.add_log("%3d: %s" % (i, self.history[i]))
        else:
            self.add_log("Unknown command: '%s'" % command_line)

        self.scroll_to_bottom = True

    def text_edit_callback(self, data: imgui.InputTextCallbackData) -> int:
        if data.event_flag == imgui.InputTextFlags_.callback_completion.value:
            # Tab completion
            word = data.buf[:data.cursor_pos].split()[-1] if data.buf[:data.cursor_pos].split() else ""
            candidates = [c for c in self.commands if c.upper().startswith(word.upper())]

            if len(candidates) == 0:
                self.add_log('No match for "%s"!' % word)
            elif len(candidates) == 1:
                data.delete_chars(data.cursor_pos - len(word), len(word))
                data.insert_chars(data.cursor_pos, candidates[0] + " ")
            else:
                # Complete as much as possible
                match_len = len(word)
                while True:
                    c = candidates[0][match_len].upper() if match_len < len(candidates[0]) else 0
                    all_match = all(
                        match_len < len(cand) and cand[match_len].upper() == c for cand in candidates
                    )
                    if not all_match or c == 0:
                        break
                    match_len += 1

                if match_len > 0:
                    data.delete_chars(data.cursor_pos - len(word), len(word))
                    data.insert_chars(data.cursor_pos, candidates[0][:match_len])

                self.add_log("Possible matches:")
                for cand in candidates:
                    self.add_log("- %s" % cand)

        elif data.event_flag == imgui.InputTextFlags_.callback_history.value:
            prev_history_pos = self.history_pos
            if data.event_key == imgui.Key.up_arrow:
                if self.history_pos == -1:
                    self.history_pos = len(self.history) - 1
                elif self.history_pos > 0:
                    self.history_pos -= 1
            elif data.event_key == imgui.Key.down_arrow:
                if self.history_pos != -1:
                    self.history_pos += 1
                    if self.history_pos >= len(self.history):
                        self.history_pos = -1

            if prev_history_pos != self.history_pos:
                history_str = self.history[self.history_pos] if self.history_pos >= 0 else ""
                data.delete_chars(0, data.buf_text_len)
                data.insert_chars(0, history_str)

        return 0

    def draw(self, title: str, p_open: bool) -> bool:
        imgui.set_next_window_size(ImVec2(520, 600), imgui.Cond_.first_use_ever.value)
        visible, p_open = imgui.begin(title, p_open)
        if not visible:
            imgui.end()
            return p_open

        if imgui.begin_popup_context_item():
            if imgui.menu_item_simple("Close Console"):
                p_open = False
            imgui.end_popup()

        IMGUI_DEMO_MARKER("ExamplesAppConsole::Draw")

        imgui.text_wrapped(
            "This example implements a console with basic coloring, completion (TAB key) and history (Up/Down keys). "
            "A more elaborate implementation may want to store entries along with extra data such as timestamp, emitter, etc."
        )
        imgui.text_wrapped("Enter 'HELP' for help.")

        if imgui.small_button("Add Debug Text"):
            self.add_log("%d some text" % len(self.items))
            self.add_log("some more text")
            self.add_log("display very important message here!")
        imgui.same_line()
        if imgui.small_button("Add Debug Error"):
            self.add_log("[error] something went wrong")
        imgui.same_line()
        if imgui.small_button("Clear"):
            self.clear_log()
        imgui.same_line()
        copy_to_clipboard = imgui.small_button("Copy")

        imgui.separator()

        # Options menu
        if imgui.begin_popup("Options"):
            _, self.auto_scroll = imgui.checkbox("Auto-scroll", self.auto_scroll)
            imgui.end_popup()

        imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.o, imgui.InputFlags_.tooltip.value)
        if imgui.button("Options"):
            imgui.open_popup("Options")
        imgui.same_line()
        self.filter = getattr(self, "filter", imgui.TextFilter())
        self.filter.draw('Filter ("incl,-excl") ("error")', 180)
        imgui.separator()

        footer_height = imgui.get_style().item_spacing.y + imgui.get_frame_height_with_spacing()
        if imgui.begin_child(
            "ScrollingRegion",
            ImVec2(0, -footer_height),
            imgui.ChildFlags_.nav_flattened.value,
            imgui.WindowFlags_.horizontal_scrollbar.value,
        ):
            if imgui.begin_popup_context_window():
                if imgui.selectable("Clear", False)[0]:
                    self.clear_log()
                imgui.end_popup()

            imgui.push_style_var(imgui.StyleVar_.item_spacing, ImVec2(4, 1))
            if copy_to_clipboard:
                imgui.log_to_clipboard()
            for item in self.items:
                if not self.filter.pass_filter(item):
                    continue
                color = None
                if "[error]" in item:
                    color = ImVec4(1.0, 0.4, 0.4, 1.0)
                elif item.startswith("# "):
                    color = ImVec4(1.0, 0.8, 0.6, 1.0)
                if color:
                    imgui.push_style_color(imgui.Col_.text.value, color)
                imgui.text_unformatted(item)
                if color:
                    imgui.pop_style_color()
            if copy_to_clipboard:
                imgui.log_finish()

            if self.scroll_to_bottom or (self.auto_scroll and imgui.get_scroll_y() >= imgui.get_scroll_max_y()):
                imgui.set_scroll_here_y(1.0)
            self.scroll_to_bottom = False

            imgui.pop_style_var()
        imgui.end_child()
        imgui.separator()

        # Command-line
        reclaim_focus = False
        input_text_flags = (
            imgui.InputTextFlags_.enter_returns_true.value
            | imgui.InputTextFlags_.escape_clears_all.value
            | imgui.InputTextFlags_.callback_completion.value
            | imgui.InputTextFlags_.callback_history.value
        )
        changed, self.input_buf = imgui.input_text("Input", self.input_buf, input_text_flags, self.text_edit_callback)
        if changed:
            s = self.input_buf.strip()
            if s:
                self.exec_command(s)
            self.input_buf = ""
            reclaim_focus = True

        imgui.set_item_default_focus()
        if reclaim_focus:
            imgui.set_keyboard_focus_here(-1)

        imgui.end()
        return p_open


def _show_example_app_console_impl(p_open: bool) -> bool:
    static = _show_example_app_console_impl
    if not hasattr(static, "console"):
        static.console = ExampleAppConsole()
    return static.console.draw("Example: Console", p_open)

show_example_app_console = _show_example_app_console_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Custom Rendering using ImDrawList API / ShowExampleAppCustomRendering()
# -----------------------------------------------------------------------------

def _path_concave_shape(draw_list, x: float, y: float, sz: float):
    """Add a |_| looking shape."""
    pos_norms = [(0.0, 0.0), (0.3, 0.0), (0.3, 0.7), (0.7, 0.7), (0.7, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for px, py in pos_norms:
        draw_list.path_line_to(ImVec2(x + 0.5 + int(sz * px), y + 0.5 + int(sz * py)))


def _show_example_app_custom_rendering_impl(p_open: bool) -> bool:
    static = _show_example_app_custom_rendering_impl

    visible, p_open = imgui.begin("Example: Custom rendering", p_open)
    if not visible:
        imgui.end()
        return p_open
    IMGUI_DEMO_MARKER("ShowExampleAppCustomRendering")

    if imgui.begin_tab_bar("##TabBar"):
        if imgui.begin_tab_item("Primitives")[0]:
            IMGUI_DEMO_MARKER("ShowExampleAppCustomRendering - Primitives")
            imgui.push_item_width(-imgui.get_font_size() * 15)
            draw_list = imgui.get_window_draw_list()

            if not hasattr(static, "sz"):
                static.sz = 36.0
                static.thickness = 3.0
                static.ngon_sides = 6
                static.circle_segments_override = False
                static.circle_segments_override_v = 12
                static.curve_segments_override = False
                static.curve_segments_override_v = 8
                static.colf = ImVec4(1.0, 1.0, 0.4, 1.0)

            # Draw gradients
            imgui.text("Gradients")
            gradient_size = ImVec2(imgui.calc_item_width(), imgui.get_frame_height())
            p0 = imgui.get_cursor_screen_pos()
            p1 = ImVec2(p0.x + gradient_size.x, p0.y + gradient_size.y)
            col_a = imgui.get_color_u32(imgui.IM_COL32(0, 0, 0, 255))
            col_b = imgui.get_color_u32(imgui.IM_COL32(255, 255, 255, 255))
            draw_list.add_rect_filled_multi_color(p0, p1, col_a, col_b, col_b, col_a)
            imgui.invisible_button("##gradient1", gradient_size)

            p0 = imgui.get_cursor_screen_pos()
            p1 = ImVec2(p0.x + gradient_size.x, p0.y + gradient_size.y)
            col_a = imgui.get_color_u32(imgui.IM_COL32(0, 255, 0, 255))
            col_b = imgui.get_color_u32(imgui.IM_COL32(255, 0, 0, 255))
            draw_list.add_rect_filled_multi_color(p0, p1, col_a, col_b, col_b, col_a)
            imgui.invisible_button("##gradient2", gradient_size)

            # Draw a bunch of primitives
            imgui.text("All primitives")
            _, static.sz = imgui.drag_float("Size", static.sz, 0.2, 2.0, 100.0, "%.0f")
            _, static.thickness = imgui.drag_float("Thickness", static.thickness, 0.05, 1.0, 8.0, "%.02f")
            _, static.ngon_sides = imgui.slider_int("N-gon sides", static.ngon_sides, 3, 12)
            _, static.circle_segments_override = imgui.checkbox("##circlesegmentoverride", static.circle_segments_override)
            imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
            changed_cs, static.circle_segments_override_v = imgui.slider_int("Circle segments override", static.circle_segments_override_v, 3, 40)
            static.circle_segments_override = static.circle_segments_override or changed_cs
            _, static.curve_segments_override = imgui.checkbox("##curvessegmentoverride", static.curve_segments_override)
            imgui.same_line(0.0, imgui.get_style().item_inner_spacing.x)
            changed_cv, static.curve_segments_override_v = imgui.slider_int("Curves segments override", static.curve_segments_override_v, 3, 40)
            static.curve_segments_override = static.curve_segments_override or changed_cv
            _, static.colf = imgui.color_edit4("Color", static.colf)

            p = imgui.get_cursor_screen_pos()
            col = imgui.color_convert_float4_to_u32(static.colf)
            spacing = 10.0
            corners_tl_br = imgui.ImDrawFlags_.round_corners_top_left.value | imgui.ImDrawFlags_.round_corners_bottom_right.value
            rounding = static.sz / 5.0
            circle_segments = static.circle_segments_override_v if static.circle_segments_override else 0
            curve_segments = static.curve_segments_override_v if static.curve_segments_override else 0
            sz = static.sz
            cp3 = [ImVec2(0.0, sz * 0.6), ImVec2(sz * 0.5, -sz * 0.4), ImVec2(sz, sz)]
            cp4 = [ImVec2(0.0, 0.0), ImVec2(sz * 1.3, sz * 0.3), ImVec2(sz - sz * 1.3, sz - sz * 0.3), ImVec2(sz, sz)]

            x = p.x + 4.0
            y = p.y + 4.0
            for n in range(2):
                th = 1.0 if n == 0 else static.thickness
                draw_list.add_ngon(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, col, static.ngon_sides, th); x += sz + spacing
                draw_list.add_circle(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, col, circle_segments, th); x += sz + spacing
                draw_list.add_ellipse(ImVec2(x + sz*0.5, y + sz*0.5), ImVec2(sz*0.5, sz*0.3), col, -0.3, circle_segments, th); x += sz + spacing
                draw_list.add_rect(ImVec2(x, y), ImVec2(x + sz, y + sz), col, 0.0, imgui.ImDrawFlags_.none.value, th); x += sz + spacing
                draw_list.add_rect(ImVec2(x, y), ImVec2(x + sz, y + sz), col, rounding, imgui.ImDrawFlags_.none.value, th); x += sz + spacing
                draw_list.add_rect(ImVec2(x, y), ImVec2(x + sz, y + sz), col, rounding, corners_tl_br, th); x += sz + spacing
                draw_list.add_triangle(ImVec2(x+sz*0.5, y), ImVec2(x+sz, y+sz-0.5), ImVec2(x, y+sz-0.5), col, th); x += sz + spacing
                _path_concave_shape(draw_list, x, y, sz); draw_list.path_stroke(col, imgui.ImDrawFlags_.closed.value, th); x += sz + spacing
                draw_list.add_line(ImVec2(x, y), ImVec2(x + sz, y), col, th); x += sz + spacing
                draw_list.add_line(ImVec2(x, y), ImVec2(x, y + sz), col, th); x += spacing
                draw_list.add_line(ImVec2(x, y), ImVec2(x + sz, y + sz), col, th); x += sz + spacing

                # Path arc
                draw_list.path_arc_to(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, 3.141592, 3.141592 * -0.5)
                draw_list.path_stroke(col, imgui.ImDrawFlags_.none.value, th)
                x += sz + spacing

                # Quadratic Bezier
                draw_list.add_bezier_quadratic(
                    ImVec2(x + cp3[0].x, y + cp3[0].y), ImVec2(x + cp3[1].x, y + cp3[1].y),
                    ImVec2(x + cp3[2].x, y + cp3[2].y), col, th, curve_segments
                )
                x += sz + spacing

                # Cubic Bezier
                draw_list.add_bezier_cubic(
                    ImVec2(x + cp4[0].x, y + cp4[0].y), ImVec2(x + cp4[1].x, y + cp4[1].y),
                    ImVec2(x + cp4[2].x, y + cp4[2].y), ImVec2(x + cp4[3].x, y + cp4[3].y),
                    col, th, curve_segments
                )

                x = p.x + 4
                y += sz + spacing

            # Filled shapes
            draw_list.add_ngon_filled(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, col, static.ngon_sides); x += sz + spacing
            draw_list.add_circle_filled(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, col, circle_segments); x += sz + spacing
            draw_list.add_ellipse_filled(ImVec2(x + sz*0.5, y + sz*0.5), ImVec2(sz*0.5, sz*0.3), col, -0.3, circle_segments); x += sz + spacing
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + sz, y + sz), col); x += sz + spacing
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + sz, y + sz), col, 10.0); x += sz + spacing
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + sz, y + sz), col, 10.0, corners_tl_br); x += sz + spacing
            draw_list.add_triangle_filled(ImVec2(x+sz*0.5, y), ImVec2(x+sz, y+sz-0.5), ImVec2(x, y+sz-0.5), col); x += sz + spacing
            _path_concave_shape(draw_list, x, y, sz); draw_list.path_fill_concave(col); x += sz + spacing
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + sz, y + static.thickness), col); x += sz + spacing
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + static.thickness, y + sz), col); x += spacing * 2.0
            draw_list.add_rect_filled(ImVec2(x, y), ImVec2(x + 1, y + 1), col); x += sz

            # Path arc filled
            draw_list.path_arc_to(ImVec2(x + sz*0.5, y + sz*0.5), sz*0.5, 3.141592 * -0.5, 3.141592)
            draw_list.path_fill_convex(col)
            x += sz + spacing

            # Quadratic Bezier filled
            draw_list.path_line_to(ImVec2(x + cp3[0].x, y + cp3[0].y))
            draw_list.path_bezier_quadratic_curve_to(ImVec2(x + cp3[1].x, y + cp3[1].y), ImVec2(x + cp3[2].x, y + cp3[2].y), curve_segments)
            draw_list.path_fill_convex(col)
            x += sz + spacing

            draw_list.add_rect_filled_multi_color(
                ImVec2(x, y), ImVec2(x + sz, y + sz),
                imgui.IM_COL32(0, 0, 0, 255), imgui.IM_COL32(255, 0, 0, 255),
                imgui.IM_COL32(255, 255, 0, 255), imgui.IM_COL32(0, 255, 0, 255),
            )
            x += sz + spacing

            imgui.dummy(ImVec2((sz + spacing) * 13.2, (sz + spacing) * 3.0))
            imgui.pop_item_width()
            imgui.end_tab_item()

        if imgui.begin_tab_item("Canvas")[0]:
            IMGUI_DEMO_MARKER("ShowExampleAppCustomRendering - Canvas")
            if not hasattr(static, "canvas_points"):
                static.canvas_points: list[ImVec2] = []
                static.canvas_scrolling = ImVec2(0.0, 0.0)
                static.canvas_opt_enable_grid = True
                static.canvas_opt_enable_context_menu = True
                static.canvas_adding_line = False

            _, static.canvas_opt_enable_grid = imgui.checkbox("Enable grid", static.canvas_opt_enable_grid)
            _, static.canvas_opt_enable_context_menu = imgui.checkbox("Enable context menu", static.canvas_opt_enable_context_menu)
            imgui.text("Mouse Left: drag to add lines,\nMouse Right: drag to scroll, click for context menu.")

            canvas_p0 = imgui.get_cursor_screen_pos()
            canvas_sz = imgui.get_content_region_avail()
            if canvas_sz.x < 50.0:
                canvas_sz = ImVec2(50.0, canvas_sz.y)
            if canvas_sz.y < 50.0:
                canvas_sz = ImVec2(canvas_sz.x, 50.0)
            canvas_p1 = ImVec2(canvas_p0.x + canvas_sz.x, canvas_p0.y + canvas_sz.y)

            io = imgui.get_io()
            draw_list = imgui.get_window_draw_list()
            draw_list.add_rect_filled(canvas_p0, canvas_p1, imgui.IM_COL32(50, 50, 50, 255))
            draw_list.add_rect(canvas_p0, canvas_p1, imgui.IM_COL32(255, 255, 255, 255))

            imgui.invisible_button("canvas", canvas_sz, imgui.ButtonFlags_.mouse_button_left.value | imgui.ButtonFlags_.mouse_button_right.value)
            is_hovered = imgui.is_item_hovered()
            is_active = imgui.is_item_active()
            origin = ImVec2(canvas_p0.x + static.canvas_scrolling.x, canvas_p0.y + static.canvas_scrolling.y)
            mouse_pos_in_canvas = ImVec2(io.mouse_pos.x - origin.x, io.mouse_pos.y - origin.y)

            if is_hovered and not static.canvas_adding_line and imgui.is_mouse_clicked(imgui.MouseButton_.left):
                static.canvas_points.append(ImVec2(mouse_pos_in_canvas.x, mouse_pos_in_canvas.y))
                static.canvas_points.append(ImVec2(mouse_pos_in_canvas.x, mouse_pos_in_canvas.y))
                static.canvas_adding_line = True
            if static.canvas_adding_line:
                static.canvas_points[-1] = ImVec2(mouse_pos_in_canvas.x, mouse_pos_in_canvas.y)
                if not imgui.is_mouse_down(imgui.MouseButton_.left):
                    static.canvas_adding_line = False

            mouse_threshold_for_pan = -1.0 if static.canvas_opt_enable_context_menu else 0.0
            if is_active and imgui.is_mouse_dragging(imgui.MouseButton_.right, mouse_threshold_for_pan):
                static.canvas_scrolling = ImVec2(
                    static.canvas_scrolling.x + io.mouse_delta.x,
                    static.canvas_scrolling.y + io.mouse_delta.y,
                )

            drag_delta = imgui.get_mouse_drag_delta(imgui.MouseButton_.right)
            if static.canvas_opt_enable_context_menu and drag_delta.x == 0.0 and drag_delta.y == 0.0:
                imgui.open_popup_on_item_click("context", imgui.PopupFlags_.mouse_button_right.value)
            if imgui.begin_popup("context"):
                if static.canvas_adding_line:
                    static.canvas_points = static.canvas_points[:-2]
                    static.canvas_adding_line = False
                if imgui.menu_item_simple("Remove one", None, False, len(static.canvas_points) > 0):
                    static.canvas_points = static.canvas_points[:-2]
                if imgui.menu_item_simple("Remove all", None, False, len(static.canvas_points) > 0):
                    static.canvas_points.clear()
                imgui.end_popup()

            draw_list.push_clip_rect(canvas_p0, canvas_p1, True)
            if static.canvas_opt_enable_grid:
                GRID_STEP = 64.0
                x = math.fmod(static.canvas_scrolling.x, GRID_STEP)
                while x < canvas_sz.x:
                    draw_list.add_line(ImVec2(canvas_p0.x + x, canvas_p0.y), ImVec2(canvas_p0.x + x, canvas_p1.y), imgui.IM_COL32(200, 200, 200, 40))
                    x += GRID_STEP
                y = math.fmod(static.canvas_scrolling.y, GRID_STEP)
                while y < canvas_sz.y:
                    draw_list.add_line(ImVec2(canvas_p0.x, canvas_p0.y + y), ImVec2(canvas_p1.x, canvas_p0.y + y), imgui.IM_COL32(200, 200, 200, 40))
                    y += GRID_STEP

            n = 0
            while n < len(static.canvas_points):
                draw_list.add_line(
                    ImVec2(origin.x + static.canvas_points[n].x, origin.y + static.canvas_points[n].y),
                    ImVec2(origin.x + static.canvas_points[n+1].x, origin.y + static.canvas_points[n+1].y),
                    imgui.IM_COL32(255, 255, 0, 255), 2.0,
                )
                n += 2
            draw_list.pop_clip_rect()

            imgui.end_tab_item()

        if imgui.begin_tab_item("BG/FG draw lists")[0]:
            IMGUI_DEMO_MARKER("ShowExampleAppCustomRendering - BG/FG draw lists")
            if not hasattr(static, "draw_bg"):
                static.draw_bg = True
                static.draw_fg = True
            _, static.draw_bg = imgui.checkbox("Draw in Background draw list", static.draw_bg)
            imgui.same_line()
            help_marker("The Background draw list will be rendered below every Dear ImGui windows.")
            _, static.draw_fg = imgui.checkbox("Draw in Foreground draw list", static.draw_fg)
            imgui.same_line()
            help_marker("The Foreground draw list will be rendered over every Dear ImGui windows.")
            window_pos = imgui.get_window_pos()
            window_size = imgui.get_window_size()
            window_center = ImVec2(window_pos.x + window_size.x * 0.5, window_pos.y + window_size.y * 0.5)
            if static.draw_bg:
                imgui.get_background_draw_list().add_circle(window_center, window_size.x * 0.6, imgui.IM_COL32(255, 0, 0, 200), 0, 10 + 4)
            if static.draw_fg:
                imgui.get_foreground_draw_list().add_circle(window_center, window_size.y * 0.6, imgui.IM_COL32(0, 255, 0, 200), 0, 10)
            imgui.end_tab_item()

        if imgui.begin_tab_item("Draw Channels")[0]:
            IMGUI_DEMO_MARKER("ShowExampleAppCustomRendering - Draw Channels")
            draw_list = imgui.get_window_draw_list()

            imgui.text("Blue shape is drawn first: appears in back")
            imgui.text("Red shape is drawn after: appears in front")
            p0 = imgui.get_cursor_screen_pos()
            draw_list.add_rect_filled(ImVec2(p0.x, p0.y), ImVec2(p0.x + 50, p0.y + 50), imgui.IM_COL32(0, 0, 255, 255))
            draw_list.add_rect_filled(ImVec2(p0.x + 25, p0.y + 25), ImVec2(p0.x + 75, p0.y + 75), imgui.IM_COL32(255, 0, 0, 255))
            imgui.dummy(ImVec2(75, 75))

            imgui.separator()

            imgui.text("Blue shape is drawn first, into channel 1: appears in front")
            imgui.text("Red shape is drawn after, into channel 0: appears in back")
            p1 = imgui.get_cursor_screen_pos()
            draw_list.channels_split(2)
            draw_list.channels_set_current(1)
            draw_list.add_rect_filled(ImVec2(p1.x, p1.y), ImVec2(p1.x + 50, p1.y + 50), imgui.IM_COL32(0, 0, 255, 255))
            draw_list.channels_set_current(0)
            draw_list.add_rect_filled(ImVec2(p1.x + 25, p1.y + 25), ImVec2(p1.x + 75, p1.y + 75), imgui.IM_COL32(255, 0, 0, 255))
            draw_list.channels_merge()
            imgui.dummy(ImVec2(75, 75))
            imgui.text("After reordering, contents of channel 0 appears below channel 1.")
            imgui.end_tab_item()

        imgui.end_tab_bar()

    imgui.end()
    return p_open

show_example_app_custom_rendering = _show_example_app_custom_rendering_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Docking, DockSpace / ShowExampleAppDockSpace()
# -----------------------------------------------------------------------------

def _show_example_app_dock_space_impl(p_open: bool) -> bool:
    static = _show_example_app_dock_space_impl
    if not hasattr(static, "keep_window_padding"):
        static.keep_window_padding = False
        static.dockspace_flags = 0  # ImGuiDockNodeFlags_None

    window_flags = imgui.WindowFlags_.no_docking.value

    if not static.keep_window_padding:
        imgui.push_style_var(imgui.StyleVar_.window_padding, ImVec2(0.0, 0.0))
    imgui.set_next_window_size(ImVec2(400, 600), imgui.Cond_.once.value)
    _, p_open = imgui.begin("Window with a DockSpace", p_open, window_flags)
    IMGUI_DEMO_MARKER("Using Dockspace")
    #
    # Here we are creating a dockspace in a window.
    #
    # But, for most apps, you will want to dock to the full viewport.
    # In that case, the basic version which you can use is:
    #   imgui.dock_space_over_viewport()
    # or:
    #   imgui.dock_space_over_viewport(0, None, imgui.DockNodeFlags_.passthru_central_node.value)  # Central node will be transparent
    # or:
    #   viewport = imgui.get_main_viewport()
    #   imgui.dock_space_over_viewport(0, viewport, imgui.DockNodeFlags_.none.value)

    if not static.keep_window_padding:
        imgui.pop_style_var()

    dockspace_id = imgui.get_id("MyDockSpace")
    imgui.dock_space(dockspace_id, ImVec2(0.0, 0.0), static.dockspace_flags)

    imgui.end()

    # Create 3 windows for the user to play with docking
    for i in range(3):
        window_name = "Dockable window #%i" % (i + 1)
        pos = ImVec2(100, 100 + i * 50)
        imgui.set_next_window_pos(pos, imgui.Cond_.once.value)
        imgui.begin(window_name)
        imgui.text("Hello from %s" % window_name)
        imgui.end()

    # Options window
    _, p_open = imgui.begin("Examples: Dockspace", p_open, imgui.WindowFlags_.menu_bar.value)
    if (imgui.get_io().config_flags & imgui.ConfigFlags_.docking_enable.value) == 0:
        imgui.text_colored(ImVec4(1, 0.6, 0.6, 1), "ERROR: Docking is not enabled!")
    else:
        imgui.checkbox("Keep Window Padding", static.keep_window_padding)
        imgui.same_line()
        help_marker("This is mostly exposed to facilitate understanding that a DockSpace() is _inside_ a window.")
        _, static.dockspace_flags = imgui.checkbox_flags("Flag: NoDockingOverCentralNode", static.dockspace_flags, imgui.DockNodeFlags_.no_docking_over_central_node.value)
        _, static.dockspace_flags = imgui.checkbox_flags("Flag: NoDockingSplit", static.dockspace_flags, imgui.DockNodeFlags_.no_docking_split.value)
        _, static.dockspace_flags = imgui.checkbox_flags("Flag: NoUndocking", static.dockspace_flags, imgui.DockNodeFlags_.no_undocking.value)
        _, static.dockspace_flags = imgui.checkbox_flags("Flag: NoResize", static.dockspace_flags, imgui.DockNodeFlags_.no_resize.value)
        _, static.dockspace_flags = imgui.checkbox_flags("Flag: AutoHideTabBar", static.dockspace_flags, imgui.DockNodeFlags_.auto_hide_tab_bar.value)

    if imgui.begin_menu_bar():
        if imgui.begin_menu("Help"):
            imgui.text_unformatted(
                'This demonstrates the use of ImGui::DockSpace() which allows you to manually\n'
                'create a docking node _within_ another window.\n\n'
                'When docking is enabled, you can ALWAYS dock MOST window into another! Try it now!\n'
                '- Drag from window title bar or their tab to dock/undock.\n'
                '- Drag from window menu button (upper-left button) to undock an entire node (all windows).\n'
            )
            imgui.end_menu()
        imgui.end_menu_bar()

    imgui.end()
    return p_open

show_example_app_dock_space = _show_example_app_dock_space_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Documents Handling / ShowExampleAppDocuments()
# -----------------------------------------------------------------------------

class MyDocument:
    """Simplified structure to mimic a Document model."""

    def __init__(self, uid: int, name: str, open_: bool = True, color: ImVec4 = ImVec4(1.0, 1.0, 1.0, 1.0)):
        self.uid = uid
        self.name = name
        self.open = open_
        self.open_prev = open_
        self.dirty = False
        self.color = color

    def do_open(self):
        self.open = True

    def do_force_close(self):
        self.open = False
        self.dirty = False

    def do_save(self):
        self.dirty = False


class ExampleAppDocuments:

    def __init__(self):
        self.documents = [
            MyDocument(0, "Lettuce", True, ImVec4(0.4, 0.8, 0.4, 1.0)),
            MyDocument(1, "Eggplant", True, ImVec4(0.8, 0.5, 1.0, 1.0)),
            MyDocument(2, "Carrot", True, ImVec4(1.0, 0.8, 0.5, 1.0)),
            MyDocument(3, "Tomato", False, ImVec4(1.0, 0.3, 0.4, 1.0)),
            MyDocument(4, "A Rather Long Title", False, ImVec4(0.4, 0.8, 0.8, 1.0)),
            MyDocument(5, "Some Document", False, ImVec4(0.8, 0.8, 1.0, 1.0)),
        ]
        self.close_queue: list[MyDocument] = []
        self.renaming_doc: Optional[MyDocument] = None
        self.renaming_started = False

    def get_tab_name(self, doc: MyDocument) -> str:
        return "%s###doc%d" % (doc.name, doc.uid)

    def display_doc_contents(self, doc: MyDocument):
        imgui.push_id(doc.uid)
        imgui.text('Document "%s"' % doc.name)
        imgui.push_style_color(imgui.Col_.text.value, doc.color)
        imgui.text_wrapped(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        )
        imgui.pop_style_color()

        imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.r, imgui.InputFlags_.tooltip.value)
        if imgui.button("Rename.."):
            self.renaming_doc = doc
            self.renaming_started = True
        imgui.same_line()

        imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.m, imgui.InputFlags_.tooltip.value)
        if imgui.button("Modify"):
            doc.dirty = True

        imgui.same_line()
        imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.s, imgui.InputFlags_.tooltip.value)
        if imgui.button("Save"):
            doc.do_save()

        imgui.same_line()
        imgui.set_next_item_shortcut(imgui.Key.mod_ctrl | imgui.Key.w, imgui.InputFlags_.tooltip.value)
        if imgui.button("Close"):
            self.close_queue.append(doc)
        _, doc.color = imgui.color_edit3("color", doc.color)
        imgui.pop_id()

    def display_doc_context_menu(self, doc: MyDocument):
        if not imgui.begin_popup_context_item():
            return
        if imgui.menu_item_simple("Save %s" % doc.name, "Ctrl+S", False, doc.open):
            doc.do_save()
        if imgui.menu_item_simple("Rename...", "Ctrl+R", False, doc.open):
            self.renaming_doc = doc
        if imgui.menu_item_simple("Close", "Ctrl+W", False, doc.open):
            self.close_queue.append(doc)
        imgui.end_popup()

    def notify_of_documents_closed_elsewhere(self):
        for doc in self.documents:
            if not doc.open and doc.open_prev:
                imgui.set_tab_item_closed(doc.name)
            doc.open_prev = doc.open


def _show_example_app_documents_impl(p_open: bool) -> bool:
    static = _show_example_app_documents_impl
    if not hasattr(static, "app"):
        static.app = ExampleAppDocuments()
        static.opt_target = 1  # 0=None, 1=Tab, 2=DockSpaceAndWindow
        static.opt_reorderable = True
        static.opt_fitting_flags = 0  # ImGuiTabBarFlags_FittingPolicyDefault_

    app = static.app

    window_contents_visible, p_open = imgui.begin("Example: Documents", p_open, imgui.WindowFlags_.menu_bar.value)
    if not window_contents_visible and static.opt_target != 2:
        imgui.end()
        return p_open

    IMGUI_DEMO_MARKER("ShowExampleAppDocuments")

    # Menu
    if imgui.begin_menu_bar():
        if imgui.begin_menu("File"):
            open_count = sum(1 for doc in app.documents if doc.open)
            if imgui.begin_menu("Open", open_count < len(app.documents)):
                for doc in app.documents:
                    if not doc.open and imgui.menu_item_simple(doc.name):
                        doc.do_open()
                imgui.end_menu()
            if imgui.menu_item_simple("Close All Documents", None, False, open_count > 0):
                for doc in app.documents:
                    app.close_queue.append(doc)
            if imgui.menu_item_simple("Exit"):
                p_open = False
            imgui.end_menu()
        imgui.end_menu_bar()

    # [Debug] List documents with one checkbox for each
    for doc_n, doc in enumerate(app.documents):
        if doc_n > 0:
            imgui.same_line()
        imgui.push_id(doc.uid)
        changed, doc.open = imgui.checkbox(doc.name, doc.open)
        if changed and not doc.open:
            doc.do_force_close()
        imgui.pop_id()
    imgui.push_item_width(imgui.get_font_size() * 12)
    _, static.opt_target = imgui.combo("Output", static.opt_target, ["None", "TabBar+Tabs", "DockSpace+Window"])
    imgui.pop_item_width()
    redock_all = False
    if static.opt_target == 1:
        imgui.same_line()
        _, static.opt_reorderable = imgui.checkbox("Reorderable Tabs", static.opt_reorderable)
    if static.opt_target == 2:
        imgui.same_line()
        redock_all = imgui.button("Redock all")

    imgui.separator()

    # Tabs
    if static.opt_target == 1:
        tab_bar_flags = static.opt_fitting_flags | (imgui.TabBarFlags_.reorderable.value if static.opt_reorderable else 0)
        tab_bar_flags |= imgui.TabBarFlags_.draw_selected_overline.value
        if imgui.begin_tab_bar("##tabs", tab_bar_flags):
            if static.opt_reorderable:
                app.notify_of_documents_closed_elsewhere()

            for doc in app.documents:
                if not doc.open:
                    continue

                doc_name_buf = app.get_tab_name(doc)
                tab_flags = imgui.TabItemFlags_.unsaved_document.value if doc.dirty else 0
                visible, doc.open = imgui.begin_tab_item(doc_name_buf, doc.open, tab_flags)

                # Cancel attempt to close when unsaved
                if not doc.open and doc.dirty:
                    doc.open = True
                    app.close_queue.append(doc)

                app.display_doc_context_menu(doc)
                if visible:
                    app.display_doc_contents(doc)
                    imgui.end_tab_item()

            imgui.end_tab_bar()
    elif static.opt_target == 2:
        if imgui.get_io().config_flags & imgui.ConfigFlags_.docking_enable.value:
            app.notify_of_documents_closed_elsewhere()

            dockspace_id = imgui.get_id("MyDockSpace")
            imgui.dock_space(dockspace_id)

            for doc in app.documents:
                if not doc.open:
                    continue

                imgui.set_next_window_dock_id(dockspace_id, imgui.Cond_.always.value if redock_all else imgui.Cond_.first_use_ever.value)
                window_flags = imgui.WindowFlags_.unsaved_document.value if doc.dirty else 0
                visible, doc.open = imgui.begin(doc.name, doc.open, window_flags)

                if not doc.open and doc.dirty:
                    doc.open = True
                    app.close_queue.append(doc)

                app.display_doc_context_menu(doc)
                if visible:
                    app.display_doc_contents(doc)

                imgui.end()
        else:
            imgui.text_colored(ImVec4(1, 0.6, 0.6, 1), "ERROR: Docking is not enabled!")

    # Early out
    if not window_contents_visible:
        imgui.end()
        return p_open

    # Display renaming UI
    if app.renaming_doc is not None:
        if app.renaming_started:
            imgui.open_popup("Rename")
        if imgui.begin_popup("Rename"):
            imgui.set_next_item_width(imgui.get_font_size() * 30)
            changed, app.renaming_doc.name = imgui.input_text(
                "###Name", app.renaming_doc.name, imgui.InputTextFlags_.enter_returns_true.value
            )
            if changed:
                imgui.close_current_popup()
                app.renaming_doc = None
            if app.renaming_started:
                imgui.set_keyboard_focus_here(-1)
            imgui.end_popup()
        else:
            app.renaming_doc = None
        app.renaming_started = False

    # Display closing confirmation UI
    if len(app.close_queue) > 0:
        close_queue_unsaved = sum(1 for doc in app.close_queue if doc.dirty)

        if close_queue_unsaved == 0:
            for doc in app.close_queue:
                doc.do_force_close()
            app.close_queue.clear()
        else:
            if not imgui.is_popup_open("Save?"):
                imgui.open_popup("Save?")
            if imgui.begin_popup_modal("Save?", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
                imgui.text("Save change to the following items?")
                item_height = imgui.get_text_line_height_with_spacing()
                if imgui.begin_child(
                    imgui.get_id("frame"),
                    ImVec2(-3.402823466e+38, 6.25 * item_height),
                    imgui.ChildFlags_.frame_style.value,
                ):
                    for doc in app.close_queue:
                        if doc.dirty:
                            imgui.text(doc.name)
                imgui.end_child()

                button_size = ImVec2(imgui.get_font_size() * 7.0, 0.0)
                if imgui.button("Yes", button_size):
                    for doc in app.close_queue:
                        if doc.dirty:
                            doc.do_save()
                        doc.do_force_close()
                    app.close_queue.clear()
                    imgui.close_current_popup()
                imgui.same_line()
                if imgui.button("No", button_size):
                    for doc in app.close_queue:
                        doc.do_force_close()
                    app.close_queue.clear()
                    imgui.close_current_popup()
                imgui.same_line()
                if imgui.button("Cancel", button_size):
                    app.close_queue.clear()
                    imgui.close_current_popup()
                imgui.end_popup()

    imgui.end()
    return p_open

show_example_app_documents = _show_example_app_documents_impl


# -----------------------------------------------------------------------------
# [SECTION] Example App: Property Editor / ShowExampleAppPropertyEditor()
# Note: This demo uses complex C++ data structures (ExampleTreeNode, ExampleMemberInfo
# with offsetof) that don't translate directly to Python. Kept as stub.
# -----------------------------------------------------------------------------

# show_example_app_property_editor stays as a stub (defined in Forward Declarations above)


# -----------------------------------------------------------------------------
# [SECTION] Runner
# -----------------------------------------------------------------------------

def main():
    from imgui_bundle import immapp
    immapp.run(lambda: show_demo_window(None), window_size=(600, 900))



if __name__ == "__main__":
    main()
