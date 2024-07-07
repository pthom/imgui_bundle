# Port of imgui_demo.cpp
#
###############################################################################
#
#              IMPORTANT
#  This file is a port of imgui_demo.cpp to Python, using Dear ImGui Bundle.
#
#  The port was done once, based on version 1.90 WIP (Oct 2023).
#  It is not guaranteed to be up-to-date with the latest version of the C++
#  code, but it should be close enough.
#
#  Official source for this file:
#  https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/imgui_demo.py
#
###############################################################################


# fmt: off
# mypy: disable_error_code=attr-defined
# mypy: disable_error_code=no-untyped-call

# dear imgui, v1.90 WIP
# (demo code)
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
import inspect
from typing import Optional, List, Callable


IMGUI_DISABLE_DEBUG_TOOLS = False  # or True, depending on your configuration


# [SECTION] Forward Declarations, Helpers

# Forward Declarations
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
    return True



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
        io.config_flags |= imgui.ConfigFlags_.docking_enable.value


# Helper to wire demo markers located in code to an interactive browser
# typedef void (*ImGuiDemoMarkerCallback)(const char* file, int line, const char* section, void* user_data);
# extern ImGuiDemoMarkerCallback      GImGuiDemoMarkerCallback;
# extern void*                        GImGuiDemoMarkerCallbackUserData;
# ImGuiDemoMarkerCallback             GImGuiDemoMarkerCallback = NULL;
# void*                               GImGuiDemoMarkerCallbackUserData = NULL;
#define IMGUI_DEMO_MARKER(section)  do { if (GImGuiDemoMarkerCallback != NULL) GImGuiDemoMarkerCallback(__FILE__, __LINE__, section, GImGuiDemoMarkerCallbackUserData); } while (0)
IMGUI_DEMO_MARKER_IS_ACTIVE = True


def IMGUI_DEMO_MARKER(section: str):
    imgui_demo_marker_callback_default(section)


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

def show_demo_window(p_open: Optional[bool]) -> Optional[bool]:
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
        _, static.show_tool_style_editor = imgui.begin("Dear ImGui Style Editor", static.show_tool_style_editor)
        imgui.show_style_editor()
        imgui.end()
    if static.show_tool_about:
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
    if static.no_titlebar:        window_flags |= imgui.WindowFlags_.no_title_bar.value
    if static.no_scrollbar:       window_flags |= imgui.WindowFlags_.no_scrollbar.value
    if not static.no_menu:        window_flags |= imgui.WindowFlags_.menu_bar.value
    if static.no_move:            window_flags |= imgui.WindowFlags_.no_move.value
    if static.no_resize:          window_flags |= imgui.WindowFlags_.no_resize.value
    if static.no_collapse:        window_flags |= imgui.WindowFlags_.no_collapse.value
    if static.no_nav:             window_flags |= imgui.WindowFlags_.no_nav.value
    if static.no_background:      window_flags |= imgui.WindowFlags_.no_background.value
    if static.no_bring_to_front:  window_flags |= imgui.WindowFlags_.no_bring_to_front_on_focus.value
    if static.no_docking:         window_flags |= imgui.WindowFlags_.no_docking.value
    if static.unsaved_document:   window_flags |= imgui.WindowFlags_.unsaved_document.value
    if static.no_close:
        p_open = None  # Don't pass our bool* to Begin

    # We specify a default position/size in case there's no data in the .ini file.
    # We only do it to make the demo applications a little more welcoming, but typically this isn't required.
    main_viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(ImVec2(main_viewport.work_pos.x + 650, main_viewport.work_pos.y + 20), imgui.Cond_.first_use_ever.value)
    imgui.set_next_window_size(ImVec2(550, 680), imgui.Cond_.first_use_ever.value)

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

    imgui_demo_marker_gui_toggle()
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
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NavEnableKeyboard", io.config_flags, imgui.ConfigFlags_.nav_enable_keyboard.value)
            imgui.same_line(); help_marker("Enable keyboard controls.")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NavEnableGamepad", io.config_flags, imgui.ConfigFlags_.nav_enable_gamepad.value)
            imgui.same_line(); help_marker("Enable gamepad controls. Require backend to set io.BackendFlags |= ImGuiBackendFlags_HasGamepad.\n\nRead instructions in imgui.cpp for details.")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NavEnableSetMousePos", io.config_flags, imgui.ConfigFlags_.nav_enable_set_mouse_pos.value)
            imgui.same_line(); help_marker("Instruct navigation to move the mouse cursor. See comment for ImGuiConfigFlags_NavEnableSetMousePos.")
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NoMouse", io.config_flags, imgui.ConfigFlags_.no_mouse.value)
            if io.config_flags & imgui.ConfigFlags_.no_mouse.value:
                # The "NoMouse" option can get us stuck with a disabled mouse! Let's provide an alternative way to fix it:
                if math.fmod(time.time(), 0.40) < 0.20:
                    imgui.same_line()
                    imgui.text("<<PRESS SPACE TO DISABLE>>")
                if imgui.is_key_pressed(imgui.Key.space):
                    io.config_flags &= ~imgui.ConfigFlags_.no_mouse.value
            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: NoMouseCursorChange", io.config_flags, imgui.ConfigFlags_.no_mouse_cursor_change.value)
            imgui.same_line(); help_marker("Instruct backend to not alter mouse cursor shape and visibility.")

            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: DockingEnable", io.config_flags, imgui.ConfigFlags_.docking_enable.value)
            imgui.same_line()
            if io.config_docking_with_shift:
                help_marker("Drag from window title bar or their tab to dock/undock. Hold SHIFT to enable docking.\n\nDrag from window menu button (upper-left button) to undock an entire node (all windows).")
            else:
                help_marker("Drag from window title bar or their tab to dock/undock. Hold SHIFT to disable docking.\n\nDrag from window menu button (upper-left button) to undock an entire node (all windows).")
            if io.config_flags & imgui.ConfigFlags_.docking_enable.value:
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

            _, io.config_flags = imgui.checkbox_flags("io.ConfigFlags: ViewportsEnable", io.config_flags, imgui.ConfigFlags_.viewports_enable.value)
            imgui.same_line(); help_marker("[beta] Enable beta multi-viewports support. See ImGuiPlatformIO for details.")
            if io.config_flags & imgui.ConfigFlags_.viewports_enable.value:
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

        IMGUI_DEMO_MARKER("Configuration/Backend Flags")
        if imgui.tree_node("Backend Flags"):
            help_marker(
                "Those flags are set by the backends (imgui_impl_xxx files) to specify their capabilities.\n"
                "Here we expose them as read-only fields to avoid breaking interactions with your backend.")

            # Make a local copy to avoid modifying actual backend flags.
            imgui.begin_disabled()
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasGamepad", io.backend_flags, imgui.BackendFlags_.has_gamepad.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasMouseCursors", io.backend_flags, imgui.BackendFlags_.has_mouse_cursors.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasSetMousePos", io.backend_flags, imgui.BackendFlags_.has_set_mouse_pos.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: PlatformHasViewports", io.backend_flags, imgui.BackendFlags_.platform_has_viewports.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: HasMouseHoveredViewport", io.backend_flags, imgui.BackendFlags_.has_mouse_hovered_viewport.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: RendererHasVtxOffset", io.backend_flags, imgui.BackendFlags_.renderer_has_vtx_offset.value)
            _, io.backend_flags = imgui.checkbox_flags("io.BackendFlags: RendererHasViewports", io.backend_flags, imgui.BackendFlags_.renderer_has_viewports.value)
            imgui.end_disabled()
            imgui.tree_pop()
            imgui.spacing()

        IMGUI_DEMO_MARKER("Configuration/Style")
        if imgui.tree_node("Style"):
            help_marker("The same contents can be accessed in 'Tools->Style Editor' or by calling the ShowStyleEditor() function.")
            imgui.show_style_editor()
            imgui.tree_pop()
            imgui.spacing()

        IMGUI_DEMO_MARKER("Configuration/Capture, Logging")
        if imgui.tree_node("Capture/Logging"):
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
    imgui.end()
    return True


def show_demo_window_widgets():
    IMGUI_DEMO_MARKER("Widgets")
    if not imgui.collapsing_header("Widgets"):
        return

    static = show_demo_window_widgets
    if not hasattr(static, "disable_all"):
        static.disable_all = False  # The Checkbox for that is inside the "Disabled" section at the bottom
    if static.disable_all:
        imgui.begin_disabled()

    IMGUI_DEMO_MARKER("Widgets/Basic")
    if imgui.tree_node("Basic"):
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
            imgui.push_style_color(imgui.Col_.button.value, imgui.ImColor.hsv(hue, 0.6, 0.6).value)
            imgui.push_style_color(imgui.Col_.button_hovered.value, imgui.ImColor.hsv(hue, 0.7, 0.7).value)
            imgui.push_style_color(imgui.Col_.button_active.value, imgui.ImColor.hsv(hue, 0.8, 0.8).value)
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
        imgui.push_button_repeat(True)
        if imgui.arrow_button("##left", imgui.Dir.left.value):
            static.counter -= 1
        imgui.same_line(0.0, spacing)
        if imgui.arrow_button("##right", imgui.Dir.right.value):
            static.counter += 1
        imgui.pop_button_repeat()
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

            changed, static.i2 = imgui.drag_int("drag int 0..100", static.i2, 1, 0, 100, "%d%%", imgui.SliderFlags_.always_clamp.value)

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
            changed, static.fff2 = imgui.slider_float("slider float (log)", static.fff2, -10.0, 10.0, "%.4f", imgui.SliderFlags_.logarithmic.value)

            IMGUI_DEMO_MARKER("Widgets/Basic/SliderAngle")
            if not hasattr(static, 'angle'): static.angle = 0.0
            changed, static.angle = imgui.slider_angle("slider angle", static.angle)

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
            if not hasattr(static, 'col1'): static.col1 = [1.0, 0.0, 0.2]
            if not hasattr(static, 'col2'): static.col2 = [0.4, 0.7, 0.0, 0.5]
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

    IMGUI_DEMO_MARKER("Widgets/Tooltips")
    if imgui.tree_node("Tooltips"):
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
        if imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip.value):
            imgui.set_tooltip("I am a manually emitted tooltip.")

        # No delay tooltip example
        imgui.button("DelayNone")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_none.value):
            imgui.set_tooltip("I am a tooltip with no delay.")

        # Short delay tooltip example
        imgui.button("DelayShort")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_short.value | imgui.HoveredFlags_.no_shared_delay.value):
            imgui.set_tooltip(f"I am a tooltip with a short delay ({imgui.get_style().hover_delay_short:.2f} sec).")

        imgui.button("DelayLong")
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal.value | imgui.HoveredFlags_.no_shared_delay.value):
            imgui.set_tooltip(f"I am a tooltip with a long delay ({imgui.get_style().hover_delay_normal:.2f} sec).")

        imgui.button("Stationary")
        if imgui.is_item_hovered(imgui.HoveredFlags_.stationary.value):
            imgui.set_tooltip("I am a tooltip requiring mouse to be stationary before activating.")

        # Tooltips can also be shown for disabled items
        imgui.begin_disabled()
        imgui.button("Disabled item")
        imgui.end_disabled()
        if imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip.value):
            imgui.set_tooltip("I am a a tooltip for a disabled item.")

        # Close the tree node for "Tooltips"
        imgui.tree_pop()

    # Testing ImGuiOnceUponAFrame helper.
    #static ImGuiOnceUponAFrame once;
    #for (int i = 0; i < 5; i++)
    #    if (once)
    #        ImGui::Text("This will be displayed only once.");

    IMGUI_DEMO_MARKER("Widgets/Tree Nodes")
    if imgui.tree_node("Tree Nodes"):
        IMGUI_DEMO_MARKER("Widgets/Tree Nodes/Basic trees")
        if imgui.tree_node("Basic trees"):
            for i in range(5):
                # Use SetNextItemOpen() to set the default state of a node to be open. We could
                # also use TreeNodeEx() with the ImGuiTreeNodeFlags_DefaultOpen flag to achieve the same thing!
                if i == 0:
                    imgui.set_next_item_open(True, imgui.Cond_.once.value)

                if imgui.tree_node(str(i), f"Child {i}"):
                    imgui.text("blah blah")
                    imgui.same_line()
                    if imgui.small_button("button"):
                        pass  # Here you can handle the button press.
                    imgui.tree_pop()
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Tree Nodes/Advanced, with Selectable nodes")
        if imgui.tree_node("Advanced, with Selectable nodes"):
            # Help marker with explanation
            help_marker(
                "This is a more typical looking tree with selectable nodes.\n"
                "Click to select, CTRL+Click to toggle, click on arrows or double-click to open.")

            if not hasattr(static, 'base_flags'): static.base_flags = imgui.TreeNodeFlags_.open_on_arrow.value | imgui.TreeNodeFlags_.open_on_double_click.value | imgui.TreeNodeFlags_.span_avail_width.value
            if not hasattr(static, 'align_label_with_current_x_position'): static.align_label_with_current_x_position = False
            if not hasattr(static, 'test_drag_and_drop'): static.test_drag_and_drop = False
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_OpenOnArrow", static.base_flags, imgui.TreeNodeFlags_.open_on_arrow.value)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_OpenOnDoubleClick", static.base_flags, imgui.TreeNodeFlags_.open_on_double_click.value)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanAvailWidth", static.base_flags, imgui.TreeNodeFlags_.span_avail_width.value); imgui.same_line(); help_marker("Extend hit area to all available width instead of allowing more items to be laid out after the node.")
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanFullWidth", static.base_flags, imgui.TreeNodeFlags_.span_full_width.value)
            _, static.base_flags = imgui.checkbox_flags("ImGuiTreeNodeFlags_SpanAllColumns", static.base_flags, imgui.TreeNodeFlags_.span_all_columns.value); imgui.same_line(); help_marker("For use in Tables only.")
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
                    node_flags |= imgui.TreeNodeFlags_.leaf.value | imgui.TreeNodeFlags_.no_tree_push_on_open.value
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

        # End of the "Tree Nodes" tree node
        imgui.tree_pop()

    IMGUI_DEMO_MARKER("Widgets/Collapsing Headers")
    if imgui.tree_node("Collapsing Headers"):
        # Initialize static variable for the checkbox state
        if not hasattr(static, 'closable_group'): static.closable_group = True
        # Checkbox to toggle the visibility of the second header
        _, static.closable_group = imgui.checkbox("Show 2nd header", static.closable_group)

        # First collapsible header
        if imgui.collapsing_header("Header", imgui.TreeNodeFlags_.none.value):
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

    IMGUI_DEMO_MARKER("Widgets/Bullets")
    if imgui.tree_node("Bullets"):
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

    IMGUI_DEMO_MARKER("Widgets/Text")
    if imgui.tree_node("Text"):
        IMGUI_DEMO_MARKER("Widgets/Text/Colored Text")
        if imgui.tree_node("Colorful Text"):
            # Shortcuts for colored text
            imgui.text_colored(ImVec4(1.0, 0.0, 1.0, 1.0), "Pink")
            imgui.text_colored(ImVec4(1.0, 1.0, 0.0, 1.0), "Yellow")
            imgui.text_disabled("Disabled")
            imgui.same_line()
            help_marker("The TextDisabled color is stored in ImGuiStyle.")
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Text/Word Wrapping")
        if imgui.tree_node("Word Wrapping"):
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

        IMGUI_DEMO_MARKER("Widgets/Text/UTF-8 Text")
        if imgui.tree_node("UTF-8 Text"):
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
        imgui.tree_pop()

    IMGUI_DEMO_MARKER("Widgets/Images")
    if imgui.tree_node("Images"):
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
        my_tex_id = io.fonts.tex_id
        my_tex_w = float(io.fonts.tex_width)
        my_tex_h = float(io.fonts.tex_height)

        # Option to use text color for tinting the image
        if not hasattr(static, 'use_text_color_for_tint'):
            static.use_text_color_for_tint = False
        _, static.use_text_color_for_tint = imgui.checkbox("Use Text Color for Tint", static.use_text_color_for_tint)

        imgui.text(f"{my_tex_w:.0f}x{my_tex_h:.0f}")
        pos = imgui.get_cursor_screen_pos()
        uv_min = ImVec2(0.0, 0.0)  # Top-left
        uv_max = ImVec2(1.0, 1.0)  # Lower-right
        tint_col = imgui.get_style_color_vec4(imgui.Col_.text.value) if static.use_text_color_for_tint else (1.0, 1.0, 1.0, 1.0)
        border_col = imgui.get_style_color_vec4(imgui.Col_.border.value)

        imgui.image(my_tex_id, ImVec2(my_tex_w, my_tex_h), uv_min, uv_max, tint_col, border_col)
        if imgui.begin_item_tooltip():
            # Define the region for the zoomed tooltip
            region_sz = 32.0
            region_x = max(min(io.mouse_pos.x - pos.x - region_sz * 0.5, my_tex_w - region_sz), 0.0)
            region_y = max(min(io.mouse_pos.y - pos.y - region_sz * 0.5, my_tex_h - region_sz), 0.0)
            imgui.text(f"Min: ({region_x:.2f}, {region_y:.2f})")
            imgui.text(f"Max: ({region_x + region_sz:.2f}, {region_y + region_sz:.2f})")
            uv0 = ImVec2((region_x) / my_tex_w, (region_y) / my_tex_h)
            uv1 = ImVec2((region_x + region_sz) / my_tex_w, (region_y + region_sz) / my_tex_h)
            imgui.image(my_tex_id, ImVec2(region_sz * 4.0, region_sz * 4.0), uv0, uv1, tint_col, border_col)
            imgui.end_tooltip()

        # Textured buttons
        IMGUI_DEMO_MARKER("Widgets/Images/Textured buttons")
        imgui.text_wrapped("And now some textured buttons..")
        if not hasattr(static, 'pressed_count'):
            static.pressed_count = 0
        for i in range(8):
            imgui.push_id(i)
            if i > 0:
                imgui.push_style_var(imgui.StyleVar_.frame_padding.value, ImVec2(i - 1.0, i - 1.0))
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

    IMGUI_DEMO_MARKER("Widgets/Combo")
    if imgui.tree_node("Combo"):
        # Expose flags as checkboxes for the demo
        if not hasattr(static, 'flags'): static.flags = 0
        _, static.flags = imgui.checkbox_flags("ImGuiComboFlags_PopupAlignLeft", static.flags, imgui.ComboFlags_.popup_align_left.value)
        imgui.same_line(); help_marker("Only makes a difference if the popup is larger than the combo")
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_NoArrowButton", static.flags, imgui.ComboFlags_.no_arrow_button.value)
        if changed:
            static.flags &= ~imgui.ComboFlags_.no_preview.value  # Clear the other flag, as we cannot combine both
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_NoPreview", static.flags, imgui.ComboFlags_.no_preview.value)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.no_arrow_button.value | imgui.ComboFlags_.width_fit_preview.value)  # Clear the other flag, as we cannot combine both
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_WidthFitPreview", static.flags, imgui.ComboFlags_.width_fit_preview.value)
        if changed:
            static.flags &= ~imgui.ComboFlags_.no_preview.value

        # Override default popup height
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightSmall", static.flags, imgui.ComboFlags_.height_small.value)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_.value & ~imgui.ComboFlags_.height_small.value)
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightRegular", static.flags, imgui.ComboFlags_.height_regular.value)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_.value & ~imgui.ComboFlags_.height_regular.value)
        changed, static.flags = imgui.checkbox_flags("ImGuiComboFlags_HeightLargest", static.flags, imgui.ComboFlags_.height_largest.value)
        if changed:
            static.flags &= ~(imgui.ComboFlags_.height_mask_.value & ~imgui.ComboFlags_.height_largest.value)

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

    IMGUI_DEMO_MARKER("Widgets/List Boxes")
    if imgui.tree_node("List boxes"):
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

    IMGUI_DEMO_MARKER("Widgets/Selectables")
    if imgui.tree_node("Selectables"):
        # Basic example of Selectable widgets
        IMGUI_DEMO_MARKER("Widgets/Selectables/Basic")
        if imgui.tree_node("Basic"):
            if not hasattr(static, 'selection'): static.selection = [False, True, False, False]
            _, static.selection[0] = imgui.selectable("1. I am selectable", static.selection[0])
            _, static.selection[1] = imgui.selectable("2. I am selectable", static.selection[1])
            _, static.selection[2] = imgui.selectable("3. I am selectable", static.selection[2])
            if imgui.selectable("4. I am double clickable", static.selection[3], imgui.SelectableFlags_.allow_double_click.value):
                if imgui.is_mouse_double_clicked(0):
                    static.selection[3] = not static.selection[3]
            imgui.tree_pop()

        # Example of single selection using Selectable widgets
        IMGUI_DEMO_MARKER("Widgets/Selectables/Single Selection")
        if imgui.tree_node("Selection State: Single Selection"):
            if not hasattr(static, 'single_selected'): static.single_selected = -1
            for n in range(5):
                buf = f"Object {n}"
                _, clicked = imgui.selectable(buf, static.single_selected == n)
                if clicked:
                    static.single_selected = n
            imgui.tree_pop()

        # Example of multiple selection using Selectable widgets
        IMGUI_DEMO_MARKER("Widgets/Selectables/Multiple Selection")
        if imgui.tree_node("Selection State: Multiple Selection"):
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
        if imgui.tree_node("Rendering more items on the same line"):
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
            imgui.tree_pop()

        # Example of Selectable widgets in columns
        IMGUI_DEMO_MARKER("Widgets/Selectables/In columns")
        if imgui.tree_node("In columns"):
            if not hasattr(static, 'selected_in_columns'): static.selected_in_columns = [False] * 10

            if imgui.begin_table("split1", 3, imgui.TableFlags_.resizable.value | imgui.TableFlags_.no_saved_settings.value | imgui.TableFlags_.borders.value):
                for i in range(10):
                    label = f"Item {i}"
                    imgui.table_next_column()
                    _, static.selected_in_columns[i] = imgui.selectable(label, static.selected_in_columns[i])  # FIXME-TABLE: Selection overlap
                imgui.end_table()
            imgui.spacing()

            if imgui.begin_table("split2", 3, imgui.TableFlags_.resizable.value | imgui.TableFlags_.no_saved_settings.value | imgui.TableFlags_.borders.value):
                for i in range(10):
                    label = f"Item {i}"
                    imgui.table_next_row()
                    imgui.table_next_column()
                    _, static.selected_in_columns[i] = imgui.selectable(label, static.selected_in_columns[i], imgui.SelectableFlags_.span_all_columns.value)
                    imgui.table_next_column()
                    imgui.text("Some other contents")
                    imgui.table_next_column()
                    imgui.text("123456")
                imgui.end_table()
            imgui.tree_pop()

        # Example of a Selectable grid
        IMGUI_DEMO_MARKER("Widgets/Selectables/Grid")
        if imgui.tree_node("Grid"):
            if not hasattr(static, 'grid_selected'): static.grid_selected = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

            time = imgui.get_time()
            winning_state = all(val == 1 for row in static.grid_selected for val in row)  # Check if all cells are selected
            if winning_state:
                imgui.push_style_var(imgui.StyleVar_.selectable_text_align.value, ImVec2(0.5 + 0.5 * math.cos(time * 2), 0.5 + 0.5 * math.sin(time * 3)))

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
        IMGUI_DEMO_MARKER("Widgets/Selectables/Alignment")
        if imgui.tree_node("Alignment"):
            help_marker("By default, Selectables use style.SelectableTextAlign but it can be overridden on a per-item basis using PushStyleVar().")
            if not hasattr(static, 'selectable_alignment'): static.selectable_alignment = [True, False, True, False, True, False, True, False, True]
            for y in range(3):
                for x in range(3):
                    alignment = ImVec2(float(x) / 2.0, float(y) / 2.0)
                    name = f"({alignment[0]:.1f},{alignment[1]:.1f})"
                    if x > 0: imgui.same_line()
                    imgui.push_style_var(imgui.StyleVar_.selectable_text_align.value, alignment)
                    _, static.selectable_alignment[3 * y + x] = imgui.selectable(name, static.selectable_alignment[3 * y + x], imgui.SelectableFlags_.none.value, ImVec2(80, 80))
                    imgui.pop_style_var()
            imgui.tree_pop()
        imgui.tree_pop()

    # We are using a fixed-sized buffer for simplicity here.
    # See imgui.INPUT_TEXT_FLAGS_CALLBACK_RESIZE and the code in misc/cpp/imgui_stdlib.h
    # for how to set up InputText() for dynamically resizing strings.
    IMGUI_DEMO_MARKER("Widgets/Text Input")
    if imgui.tree_node("Text Input"):
        IMGUI_DEMO_MARKER("Widgets/Text Input/Multi-line Text Input")
        if imgui.tree_node("Multi-line Text Input"):
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
                static.text_input_flags = imgui.InputTextFlags_.allow_tab_input.value
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_ReadOnly", static.text_input_flags, imgui.InputTextFlags_.read_only.value)
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_AllowTabInput", static.text_input_flags, imgui.InputTextFlags_.allow_tab_input.value)
            _, static.text_input_flags = imgui.checkbox_flags("ImGuiInputTextFlags_CtrlEnterForNewLine", static.text_input_flags, imgui.InputTextFlags_.ctrl_enter_for_new_line.value)

            # Use InputTextMultiline for a multi-line resizable input box.
            changed, static.text_input_text = imgui.input_text_multiline("##source", static.text_input_text, ImVec2(-1, imgui.get_text_line_height() * 16), static.text_input_flags)
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Text Input/Filtered Text Input")
        if imgui.tree_node("Filtered Text Input"):
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
            _, static.filtered_text_input_buf2 = imgui.input_text("decimal", static.filtered_text_input_buf2, flags=imgui.InputTextFlags_.chars_decimal.value)

            if not hasattr(static, "filtered_text_input_buf3"):
                static.filtered_text_input_buf3 = ""
            _, static.filtered_text_input_buf3 = imgui.input_text("hexadecimal", static.filtered_text_input_buf3, flags=imgui.InputTextFlags_.chars_hexadecimal.value | imgui.InputTextFlags_.chars_uppercase.value)

            if not hasattr(static, "filtered_text_input_buf4"):
                static.filtered_text_input_buf4 = ""
            _, static.filtered_text_input_buf4 = imgui.input_text("uppercase", static.filtered_text_input_buf4, flags=imgui.InputTextFlags_.chars_uppercase.value)

            if not hasattr(static, "filtered_text_input_buf5"):
                static.filtered_text_input_buf5 = ""
            _, static.filtered_text_input_buf5 = imgui.input_text("no blank", static.filtered_text_input_buf5, flags=imgui.InputTextFlags_.chars_no_blank.value)

            # if "filtered_text_input_buf6" not in static:
            #     static.filtered_text_input_buf6 = ""
            # _, static.filtered_text_input_buf6 = imgui.input_text("casing swap", static.filtered_text_input_buf6, flags=imgui.InputTextFlags_.callback_char_filter.value, callback=TextFilters.filter_casing_swap)
            #
            # if "filtered_text_input_buf7" not in static:
            #     static.filtered_text_input_buf7 = ""
            # _, static.filtered_text_input_buf7 = imgui.input_text("\"imgui\"", static.filtered_text_input_buf7, flags=imgui.InputTextFlags_.callback_char_filter.value, callback=TextFilters.filter_imgui_letters)

            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Text Input/Password input")
        if imgui.tree_node("Password Input"):
            if not hasattr(static, "password"):
                static.password = "password123"

            _, static.password = imgui.input_text("password", static.password, imgui.InputTextFlags_.password.value)
            imgui.same_line(); help_marker("Display all characters as '*'.\nDisable clipboard cut and copy.\nDisable logging.")
            _, static.password = imgui.input_text_with_hint("password (w/ hint)", "<password>", static.password, imgui.InputTextFlags_.password.value)
            _, static.password = imgui.input_text("password (clear)", static.password)
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Text Input/Miscellaneous")
        if imgui.tree_node("Miscellaneous"):
            if not hasattr(static, "misc_buf1"): static.misc_buf1 = ""
            if not hasattr(static, "misc_flags"): static.misc_flags = imgui.InputTextFlags_.escape_clears_all.value
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_EscapeClearsAll", static.misc_flags, imgui.InputTextFlags_.escape_clears_all.value)
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_ReadOnly", static.misc_flags, imgui.InputTextFlags_.read_only.value)
            changed, static.misc_flags = imgui.checkbox_flags("ImGuiInputTextFlags_NoUndoRedo", static.misc_flags, imgui.InputTextFlags_.no_undo_redo.value)
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
    IMGUI_DEMO_MARKER("Widgets/Tabs")
    if imgui.tree_node("Tabs"):
        IMGUI_DEMO_MARKER("Widgets/Tabs/Basic")
        if imgui.tree_node("Basic"):
            tab_bar_flags = imgui.TabBarFlags_.none.value
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

        IMGUI_DEMO_MARKER("Widgets/Tabs/Advanced & Close Button")
        if imgui.tree_node("Advanced & Close Button"):
            # Expose a couple of the available flags. In most cases, you may just call begin_tab_bar() with no flags (0).
            if not hasattr(static, "adv_tab_bar_flags"):
                static.adv_tab_bar_flags = imgui.TabBarFlags_.reorderable.value
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_Reorderable", static.adv_tab_bar_flags, imgui.TabBarFlags_.reorderable.value)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_AutoSelectNewTabs", static.adv_tab_bar_flags, imgui.TabBarFlags_.auto_select_new_tabs.value)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_TabListPopupButton", static.adv_tab_bar_flags, imgui.TabBarFlags_.tab_list_popup_button.value)
            _, static.adv_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_NoCloseWithMiddleMouseButton", static.adv_tab_bar_flags, imgui.TabBarFlags_.no_close_with_middle_mouse_button.value)
            if (static.adv_tab_bar_flags & imgui.TabBarFlags_.fitting_policy_mask_.value) == 0:
                static.adv_tab_bar_flags |= imgui.TabBarFlags_.fitting_policy_default_.value
            if imgui.checkbox_flags("ImGuiTabBarFlags_FittingPolicyResizeDown", static.adv_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_resize_down.value):
                static.adv_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_.value ^ imgui.TabBarFlags_.fitting_policy_resize_down.value)
            if imgui.checkbox_flags("ImGuiTabBarFlags_FittingPolicyScroll", static.adv_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_scroll.value):
                static.adv_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_.value ^ imgui.TabBarFlags_.fitting_policy_scroll.value)

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
                    if static.opened[n] and imgui.begin_tab_item(names[n], static.opened[n], imgui.TabItemFlags_.none.value)[0]:
                        imgui.text("This is the %s tab!" % names[n])
                        if n & 1:
                            imgui.text("I am an odd tab.")
                        imgui.end_tab_item()
                imgui.end_tab_bar()
            imgui.separator()
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Widgets/Tabs/TabItemButton & Leading-Trailing flags")
        if imgui.tree_node("TabItemButton & Leading/Trailing flags"):
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
                        imgui.TabBarFlags_.auto_select_new_tabs.value
                        | imgui.TabBarFlags_.reorderable.value
                        | imgui.TabBarFlags_.fitting_policy_resize_down.value
                )
            _, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_TabListPopupButton", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.tab_list_popup_button.value)
            changed, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_FittingPolicyResizeDown", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_resize_down.value)
            if changed:
                static.lead_trail_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_.value ^ imgui.TabBarFlags_.fitting_policy_resize_down.value)
            changed, static.lead_trail_tab_bar_flags = imgui.checkbox_flags("ImGuiTabBarFlags_FittingPolicyScroll", static.lead_trail_tab_bar_flags, imgui.TabBarFlags_.fitting_policy_scroll.value)
            if changed:
                static.lead_trail_tab_bar_flags &= ~(imgui.TabBarFlags_.fitting_policy_mask_.value ^ imgui.TabBarFlags_.fitting_policy_scroll)

            if imgui.begin_tab_bar("MyTabBar", static.lead_trail_tab_bar_flags):
                # Demo a Leading TabItemButton(): click the "?" button to open a menu
                if static.show_leading_button:
                    if imgui.tab_item_button("?", imgui.TabItemFlags_.leading.value | imgui.TabItemFlags_.no_tooltip.value):
                        imgui.open_popup("MyHelpMenu")
                if imgui.begin_popup("MyHelpMenu"):
                    imgui.selectable("Hello!", False)
                    imgui.end_popup()

                # Demo Trailing Tabs: click the "+" button to add a new tab (in your app you may want to use a font icon instead of the "+")
                # Note that we submit it before the regular tabs, but because of the ImGuiTabItemFlags_Trailing flag it will always appear at the end.
                if static.show_trailing_button:
                    if imgui.tab_item_button("+", imgui.TabItemFlags_.trailing.value | imgui.TabItemFlags_.no_tooltip.value):
                        static.active_tabs.append(static.next_tab_id)  # Add new tab
                        static.next_tab_id += 1

                # Submit our regular tabs
                n = 0
                while n < len(static.active_tabs):
                    open = True
                    name = "%04d" % static.active_tabs[n]
                    if imgui.begin_tab_item(name, open, imgui.TabItemFlags_.none.value)[0]:
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

    IMGUI_DEMO_MARKER("Widgets/Color")
    if imgui.tree_node("Color/Picker Widgets"):
        if not hasattr(static, "color"):
            static.color = ImVec4(114.0 / 255.0, 144.0 / 255.0, 154.0 / 255.0, 200.0 / 255.0)
        if not hasattr(static, "color3"):
            static.color3 = [114.0 / 255.0, 144.0 / 255.0, 154.0 / 255.0]

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
        misc_flags = (imgui.ColorEditFlags_.hdr.value if static.hdr else 0) | (0 if static.drag_and_drop else imgui.ColorEditFlags_.no_drag_drop.value) | (
            imgui.ColorEditFlags_.alpha_preview_half.value if static.alpha_half_preview else (imgui.ColorEditFlags_.alpha_preview.value if static.alpha_preview else 0)) | (
                         0 if static.options_menu else imgui.ColorEditFlags_.no_options.value)

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
        _, static.color = imgui.color_edit4("MyColor##2", static.color, flags=imgui.ColorEditFlags_.display_hsv.value | misc_flags)  # type: ignore

        IMGUI_DEMO_MARKER("Widgets/Color/ColorEdit (float display)")
        imgui.text("Color widget with Float Display:")
        _, static.color = imgui.color_edit4("MyColor##2f", static.color, flags=imgui.ColorEditFlags_.float.value | misc_flags)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorButton (with Picker)")
        imgui.text("Color button with Picker:")
        imgui.same_line()
        help_marker(
            "With the ImGuiColorEditFlags_NoInputs flag you can hide all the slider/text inputs.\n"
            "With the ImGuiColorEditFlags_NoLabel flag you can pass a non-empty label which will only "
            "be used for the tooltip and picker popup.")
        _, static.color = imgui.color_edit4("MyColor##3", static.color, flags=imgui.ColorEditFlags_.no_inputs.value | imgui.ColorEditFlags_.no_label.value | misc_flags)

        IMGUI_DEMO_MARKER("Widgets/Color/ColorButton (simple)")
        imgui.text("Color button only:")
        if not hasattr(static, "no_border"): static.no_border = False
        _, static.no_border = imgui.checkbox("ImGuiColorEditFlags_NoBorder", static.no_border)
        imgui.color_button("MyColor##3c", static.color, misc_flags | (imgui.ColorEditFlags_.no_border.value if static.no_border else 0), (80, 80))  # type: ignore

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
        _, static.color_hsv = imgui.color_edit4("HSV shown as RGB##1", static.color_hsv, imgui.ColorEditFlags_.display_rgb.value | imgui.ColorEditFlags_.input_hsv.value | imgui.ColorEditFlags_.float.value)   # type: ignore
        _, static.color_hsv = imgui.color_edit4("HSV shown as HSV##1", static.color_hsv, imgui.ColorEditFlags_.display_hsv.value | imgui.ColorEditFlags_.input_hsv.value | imgui.ColorEditFlags_.float.value)   # type: ignore
        # imgui.drag_float4("Raw HSV values", static.color_hsv, 0.01, 0.0, 1.0)

        imgui.tree_pop()

    # Drag and Slider Flags
    IMGUI_DEMO_MARKER("Widgets/Drag and Slider Flags")
    if imgui.tree_node("Drag/Slider Flags"):
        # Demonstrate using advanced flags for DragXXX and SliderXXX functions. Note that the flags are the same!
        if not hasattr(static, "drag_slider_flags"): static.drag_slider_flags = imgui.SliderFlags_.none.value
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_AlwaysClamp", static.drag_slider_flags, imgui.SliderFlags_.always_clamp.value)
        imgui.same_line(); help_marker("Always clamp value to min/max bounds (if any) when input manually with CTRL+Click.")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_Logarithmic", static.drag_slider_flags, imgui.SliderFlags_.logarithmic.value)
        imgui.same_line(); help_marker("Enable logarithmic editing (more precision for small values).")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_NoRoundToFormat", static.drag_slider_flags, imgui.SliderFlags_.no_round_to_format.value)
        imgui.same_line(); help_marker("Disable rounding underlying value to match precision of the format string (e.g. %.3f values are rounded to those 3 digits).")
        changed, static.drag_slider_flags = imgui.checkbox_flags("ImGuiSliderFlags_NoInput", static.drag_slider_flags, imgui.SliderFlags_.no_input.value)
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
    IMGUI_DEMO_MARKER("Widgets/Range Widgets")
    if imgui.tree_node("Range Widgets"):
        if not hasattr(static, "begin_range_f"):
            static.begin_range_f = 10
            static.end_range_f = 90
            static.begin_i = 100
            static.end_i = 1000
        # _, static.begin_range_f, static.end_range_f = imgui.drag_float_range2("range float", static.begin_range_f, static.end_range_f, 0.25, 0.0, 100.0, "Min: %d units", "Max: %d units")
        _, static.begin_i, static.end_i = imgui.drag_int_range2("range int (no bounds)", static.begin_i, static.end_i, 5, 0, 0, "Min: %d units", "Max: %d units")
        imgui.tree_pop()

    # Multi-component Widgets
    IMGUI_DEMO_MARKER("Widgets/Multi-component Widgets")
    if imgui.tree_node("Multi-component Widgets"):
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
    IMGUI_DEMO_MARKER("Widgets/Vertical Sliders")
    if imgui.tree_node("Vertical Sliders"):
        spacing = 4
        imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(spacing, spacing))

        if not hasattr(static, "sliderv_int_value"): static.sliderv_int_value = 0
        imgui.v_slider_int("##int", ImVec2(18, 160), static.sliderv_int_value, 0, 5)
        imgui.same_line()

        if not hasattr(static, "sliderv_values"): static.sliderv_values = [0.0, 0.60, 0.35, 0.9, 0.70, 0.20, 0.0]
        imgui.push_id("set1")
        for i in range(7):
            if i > 0:
                imgui.same_line()
            imgui.push_id(i)
            imgui.push_style_color(imgui.Col_.frame_bg.value, imgui.ImColor.hsv(i / 7.0, 0.5, 0.5).value)
            imgui.push_style_color(imgui.Col_.frame_bg_hovered.value, imgui.ImColor.hsv(i / 7.0, 0.6, 0.5).value)
            imgui.push_style_color(imgui.Col_.frame_bg_active.value, imgui.ImColor.hsv(i / 7.0, 0.7, 0.5).value)
            imgui.push_style_color(imgui.Col_.slider_grab.value, imgui.ImColor.hsv(i / 7.0, 0.9, 0.9).value)
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
            imgui.push_style_var(imgui.StyleVar_.grab_min_size.value, 40)
            _, static.sliderv_values[i] = imgui.v_slider_float("##v", ImVec2(40, 160), static.sliderv_values[i], 0.0, 1.0, "%.2f\nsec")
            imgui.pop_style_var()
            imgui.pop_id()
        imgui.pop_id()
        imgui.pop_style_var()
        imgui.tree_pop()

    # Text Filter
    IMGUI_DEMO_MARKER("Widgets/Text Filter")
    if imgui.tree_node("Text Filter"):
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


def show_demo_window_layout():
    static = show_demo_window_layout

    IMGUI_DEMO_MARKER("Layout")
    if not imgui.collapsing_header("Layout & Scrolling"):
        return

    IMGUI_DEMO_MARKER("Layout/Child windows")
    if imgui.tree_node("Child windows"):
        imgui.separator_text("Child windows")

        help_marker("Use child windows to begin into self-contained independent scrolling/clipping regions within a host window.")
        if not hasattr(static, "disable_mouse_wheel"):
            static.disable_mouse_wheel = False
        if not hasattr(static, "disable_menu"):
            static.disable_menu = False
        _, static.disable_mouse_wheel = imgui.checkbox("Disable Mouse Wheel", static.disable_mouse_wheel)
        _, static.disable_menu = imgui.checkbox("Disable Menu", static.disable_menu)

        # Child 1: no border, enable horizontal scrollbar
        window_flags = imgui.WindowFlags_.horizontal_scrollbar.value
        if static.disable_mouse_wheel:
            window_flags |= imgui.WindowFlags_.no_scroll_with_mouse.value
        imgui.begin_child("ChildL", ImVec2(imgui.get_content_region_avail().x * 0.5, 260), False, window_flags)
        for i in range(100):
            imgui.text("%04d: scrollable region" % i)
        imgui.end_child()

        imgui.same_line()

        # Child 2: rounded border
        if hasattr(static, "disable_mouse_wheel"): static.disable_mouse_wheel = False
        if hasattr(static, "disable_menu"): static.disable_menu = False
        window_flags = imgui.WindowFlags_.none.value
        if static.disable_mouse_wheel:
            window_flags |= imgui.WindowFlags_.no_scroll_with_mouse.value
        if not static.disable_menu:
            window_flags |= imgui.WindowFlags_.menu_bar.value
        imgui.push_style_var(imgui.StyleVar_.child_rounding.value, 5.0)
        if imgui.begin_child("ChildR", ImVec2(0, 260), True, window_flags):
            if not static.disable_menu and imgui.begin_menu_bar():
                if imgui.begin_menu("Menu"):
                    show_example_menu_file()
                    imgui.end_menu()
                imgui.end_menu_bar()
            if imgui.begin_table("split", 2, flags=(imgui.TableFlags_.resizable.value | imgui.TableFlags_.no_saved_settings.value)):
                for i in range(100):
                    buf = f"{i:03d}"
                    imgui.table_next_column()
                    imgui.button(buf, ImVec2(-1, 0.0))
                imgui.end_table()
            imgui.end_child()
        imgui.pop_style_var()

        imgui.tree_pop()

    # Basic Horizontal Layout
    IMGUI_DEMO_MARKER("Layout/Basic Horizontal Layout")
    if imgui.tree_node("Basic Horizontal Layout"):
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
        window_visible_x2 = imgui.get_window_pos().x + imgui.get_window_content_region_max().x
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
    IMGUI_DEMO_MARKER("Layout/Groups")
    if imgui.tree_node("Groups"):
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

    # Scrolling
    IMGUI_DEMO_MARKER("Layout/Scrolling")
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

            child_flags = imgui.WindowFlags_.menu_bar.value if static.enable_extra_decorations else 0
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
            child_flags = imgui.WindowFlags_.horizontal_scrollbar.value | (imgui.WindowFlags_.always_vertical_scrollbar.value if static.enable_extra_decorations else 0)
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

        imgui.tree_pop()


def show_demo_window_popups():
    static = show_demo_window

    IMGUI_DEMO_MARKER("Popups")
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

    IMGUI_DEMO_MARKER("Popups/Popups")
    if imgui.tree_node("Popups"):
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
    IMGUI_DEMO_MARKER("Popups/Context menus")
    if imgui.tree_node("Context menus"):
        help_marker("\"Context\" functions are simple helpers to associate a Popup to a given Item or Window identifier.")

        # Example 1
        # When used after an item that has an ID (e.g. Button), we can skip providing an ID to BeginPopupContextItem(),
        # and BeginPopupContextItem() will use the last item ID as the popup ID.
        names = ["Label1", "Label2", "Label3", "Label4", "Label5"]
        selected = -1
        for n in range(5):
            if imgui.selectable(names[n], selected == n):
                selected = n
            if imgui.begin_popup_context_item():  # <-- use last item id as popup id
                selected = n
                imgui.text(f"This a popup for \"{names[n]}\"!")
                if imgui.button("Close"):
                    imgui.close_current_popup()
                imgui.end_popup()
            imgui.set_item_tooltip("Right-click to open popup")

        imgui.tree_pop()

    # Modals
    IMGUI_DEMO_MARKER("Popups/Modals")
    if imgui.tree_node("Modals"):
        imgui.text_wrapped("Modal windows are like popups but the user cannot close them by clicking outside.")

        if imgui.button("Delete.."):
            imgui.open_popup("Delete?")

        # Always center this window when appearing
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing.value, ImVec2(0.5, 0.5))

        if not hasattr(static, "dont_ask_me_next_time"):
            static.dont_ask_me_next_time = False  # Equivalent to static bool dont_ask_me_next_time = false;

        if imgui.begin_popup_modal("Delete?", None, imgui.WindowFlags_.always_auto_resize.value)[0]:
            imgui.text("All those beautiful files will be deleted.\nThis operation cannot be undone!")
            imgui.separator()

            imgui.push_style_var(imgui.StyleVar_.frame_padding.value, ImVec2(0, 0))
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
        if imgui.begin_popup_modal("Stacked 1", None, imgui.WindowFlags_.menu_bar.value)[0]:
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


def show_demo_window_inputs():
    IMGUI_DEMO_MARKER("Inputs & Focus")
    if imgui.collapsing_header("Inputs & Focus"):
        io = imgui.get_io()

        # Display inputs submitted to ImGuiIO
        IMGUI_DEMO_MARKER("Inputs & Focus/Inputs")
        imgui.set_next_item_open(True, imgui.Cond_.once.value)
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
        imgui.set_next_item_open(True, imgui.Cond_.once.value)
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

            IMGUI_DEMO_MARKER("Inputs & Focus/Outputs/WantCapture override")
            if imgui.tree_node("WantCapture override"):
                help_marker(
                    "Hovering the colored canvas will override io.WantCaptureXXX fields.\n"
                    "Notice how normally (when set to none), the value of io.WantCaptureKeyboard would be false when hovering and true when clicking.")
                capture_override_mouse = -1
                capture_override_keyboard = -1
                capture_override_desc = ["None", "Set to false", "Set to true"]
                imgui.set_next_item_width(imgui.get_font_size() * 15)
                imgui.slider_int("SetNextFrameWantCaptureMouse() on hover", capture_override_mouse, -1, +1, capture_override_desc[capture_override_mouse + 1], imgui.SliderFlags_.always_clamp.value)
                imgui.set_next_item_width(imgui.get_font_size() * 15)
                imgui.slider_int("SetNextFrameWantCaptureKeyboard() on hover", capture_override_keyboard, -1, +1, capture_override_desc[capture_override_keyboard + 1], imgui.SliderFlags_.always_clamp.value)

                imgui.color_button("##panel", ImVec4(0.7, 0.1, 0.7, 1.0), imgui.ColorEditFlags_.no_tooltip.value | imgui.ColorEditFlags_.no_drag_drop.value, ImVec2(128.0, 96.0)) # Dummy item
                if imgui.is_item_hovered() and capture_override_mouse != -1:
                    imgui.set_next_frame_want_capture_mouse(capture_override_mouse == 1)
                if imgui.is_item_hovered() and capture_override_keyboard != -1:
                    imgui.set_next_frame_want_capture_keyboard(capture_override_keyboard == 1)

                imgui.tree_pop()
            imgui.tree_pop()

        IMGUI_DEMO_MARKER("Inputs & Focus/Tabbing")
        if imgui.tree_node("Tabbing"):
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

        IMGUI_DEMO_MARKER("Inputs & Focus/Focus from code")
        if imgui.tree_node("Focus from code"):
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

        IMGUI_DEMO_MARKER("Inputs & Focus/Dragging")
        if imgui.tree_node("Dragging"):
            imgui.text_wrapped("You can use imgui.get_mouse_drag_delta(0) to query for the dragged amount on any widget.")
            for button in range(3):
                imgui.text("IsMouseDragging(%d):" % button)
                imgui.text("  w/ default threshold: %d," % imgui.is_mouse_dragging(button))
                imgui.text("  w/ zero threshold: %d," % imgui.is_mouse_dragging(button, 0.0))
                imgui.text("  w/ large threshold: %d," % imgui.is_mouse_dragging(button, 20.0))

            imgui.button("Drag Me")
            cur_pos = imgui.get_cursor_screen_pos()
            if imgui.is_item_active():
                imgui.get_foreground_draw_list().add_line(cur_pos, io.mouse_pos, imgui.get_color_u32(imgui.Col_.button.value), 4.0) # Draw a line between the button and the mouse cursor

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
    imgui.push_style_var(imgui.StyleVar_.frame_padding.value, ImVec2(style.frame_padding.x, style.frame_padding.y * 0.60))
    imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(style.item_spacing.x, style.item_spacing.y * 0.60))


def pop_style_compact():
    imgui.pop_style_var(2)


def show_demo_window_tables():
    static = show_demo_window_tables

    IMGUI_DEMO_MARKER("Tables")
    if not imgui.collapsing_header("Tables & Columns"):
        return

    # Using these as base values to create width/height that are a factor of the size of our font
    # imgui.calc_text_size("A").x
    # imgui.get_text_line_height_with_spacing()

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
        imgui.push_style_var(imgui.StyleVar_.indent_spacing.value, 0.0)

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
    IMGUI_DEMO_MARKER("Tables/Basic")
    if imgui.tree_node("Basic"):
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
    IMGUI_DEMO_MARKER("Tables/Borders, background")
    if imgui.tree_node("Borders, background"):
        # Expose a few Borders related flags interactively
        class ContentsType:
            CT_Text = 0
            CT_FillButton = 1

        if not hasattr(static, "bb_flags"):
            static.bb_flags = imgui.TableFlags_.borders.value | imgui.TableFlags_.row_bg.value
            static.display_headers = False
            static.contents_type = ContentsType.CT_Text

        push_style_compact()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.bb_flags, imgui.TableFlags_.row_bg.value)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_Borders", static.bb_flags, imgui.TableFlags_.borders.value)
        imgui.same_line()
        help_marker("ImGuiTableFlags_Borders\n = ImGuiTableFlags_BordersInnerV\n | ImGuiTableFlags_BordersOuterV\n | ImGuiTableFlags_BordersInnerV\n | ImGuiTableFlags_BordersOuterH")
        imgui.indent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersH", static.bb_flags, imgui.TableFlags_.borders_h.value)
        imgui.indent()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterH", static.bb_flags, imgui.TableFlags_.borders_outer_h.value)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerH", static.bb_flags, imgui.TableFlags_.borders_inner_h.value)
        imgui.unindent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.bb_flags, imgui.TableFlags_.borders_v.value)
        imgui.indent()
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.bb_flags, imgui.TableFlags_.borders_outer_v.value)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.bb_flags, imgui.TableFlags_.borders_inner_v.value)
        imgui.unindent()

        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuter", static.bb_flags, imgui.TableFlags_.borders_outer.value)
        _, static.bb_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInner", static.bb_flags, imgui.TableFlags_.borders_inner.value)
        imgui.unindent()

        imgui.align_text_to_frame_padding()
        imgui.text("Cell contents:")
        imgui.same_line()
        _, static.contents_type = imgui.radio_button("Text", static.contents_type, ContentsType.CT_Text)
        imgui.same_line()
        _, static.contents_type = imgui.radio_button("FillButton", static.contents_type, ContentsType.CT_FillButton)
        _, static.display_headers = imgui.checkbox("Display headers", static.display_headers)
        _, static.flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBody", static.bb_flags, imgui.TableFlags_.no_borders_in_body.value); imgui.same_line(); help_marker("Disable vertical borders in columns Body (borders will always appear in Headers)")
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
    IMGUI_DEMO_MARKER("Tables/Resizable, stretch")
    if imgui.tree_node("Resizable, stretch"):
        # By default, if we don't enable ScrollX, the sizing policy for each column is "Stretch".
        # All columns maintain a sizing weight, and they will occupy all available width.
        if not hasattr(static, "rs_flags"):
            static.rs_flags = (imgui.TableFlags_.sizing_stretch_same.value |
                            imgui.TableFlags_.resizable.value |
                            imgui.TableFlags_.borders_outer.value |
                            imgui.TableFlags_.borders_v.value |
                            imgui.TableFlags_.context_menu_in_body.value)
        push_style_compact()
        _, static.rs_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.rs_flags, imgui.TableFlags_.resizable.value)
        _, static.rs_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.rs_flags, imgui.TableFlags_.borders_v.value)
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
    IMGUI_DEMO_MARKER("Tables/Resizable, fixed")
    if imgui.tree_node("Resizable, fixed"):
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
            static.rf_flags = (imgui.TableFlags_.sizing_fixed_fit.value |
                               imgui.TableFlags_.resizable.value |
                               imgui.TableFlags_.borders_outer.value |
                               imgui.TableFlags_.borders_v.value |
                               imgui.TableFlags_.context_menu_in_body.value)
        _, static.rf_flags = imgui.checkbox_flags("ImGuiTableFlags_NoHostExtendX", static.rf_flags, imgui.TableFlags_.no_host_extend_x.value)
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
    IMGUI_DEMO_MARKER("Tables/Resizable, mixed")
    if imgui.tree_node("Resizable, mixed"):
        help_marker(
            "Using TableSetupColumn() to alter resizing policy on a per-column basis.\n\n"
            "When combining Fixed and Stretch columns, generally you only want one, maybe two trailing columns to use _WidthStretch.")
        if not hasattr(static, "rm_flags"):
            static.rm_flags = (imgui.TableFlags_.sizing_fixed_fit.value |
                               imgui.TableFlags_.row_bg.value |
                               imgui.TableFlags_.borders.value |
                               imgui.TableFlags_.resizable.value |
                               imgui.TableFlags_.reorderable.value |
                               imgui.TableFlags_.hideable.value)

        if imgui.begin_table("table1", 3, static.rm_flags):
            imgui.table_setup_column("AAA", imgui.TableColumnFlags_.width_fixed.value)
            imgui.table_setup_column("BBB", imgui.TableColumnFlags_.width_fixed.value)
            imgui.table_setup_column("CCC", imgui.TableColumnFlags_.width_stretch.value)
            imgui.table_headers_row()
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_set_column_index(column)
                    imgui.text("%s %d,%d" % ("Stretch" if column == 2 else "Fixed", column, row))
            imgui.end_table()

        if imgui.begin_table("table2", 6, static.rm_flags):
            imgui.table_setup_column("AAA", imgui.TableColumnFlags_.width_fixed.value)
            imgui.table_setup_column("BBB", imgui.TableColumnFlags_.width_fixed.value)
            imgui.table_setup_column("CCC", imgui.TableColumnFlags_.width_fixed.value | imgui.TableColumnFlags_.default_hide.value)
            imgui.table_setup_column("DDD", imgui.TableColumnFlags_.width_stretch.value)
            imgui.table_setup_column("EEE", imgui.TableColumnFlags_.width_stretch.value)
            imgui.table_setup_column("FFF", imgui.TableColumnFlags_.width_stretch.value | imgui.TableColumnFlags_.default_hide.value)
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
    IMGUI_DEMO_MARKER("Tables/Reorderable, hideable, with headers")
    if imgui.tree_node("Reorderable, hideable, with headers"):
        help_marker(
            "Click and drag column headers to reorder columns.\n\n"
            "Right-click on a header to open a context menu.")
        if not hasattr(static, "rh_flags"):
            static.rh_flags = (imgui.TableFlags_.resizable.value |
                               imgui.TableFlags_.reorderable.value |
                               imgui.TableFlags_.hideable.value |
                               imgui.TableFlags_.borders_outer.value |
                               imgui.TableFlags_.borders_v.value)

        push_style_compact()
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.rh_flags, imgui.TableFlags_.resizable.value)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Reorderable", static.rh_flags, imgui.TableFlags_.reorderable.value)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_Hideable", static.rh_flags, imgui.TableFlags_.hideable.value)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBody", static.rh_flags, imgui.TableFlags_.no_borders_in_body.value)
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_NoBordersInBodyUntilResize", static.rh_flags, imgui.TableFlags_.no_borders_in_body_until_resize.value)
        imgui.same_line()
        help_marker("Disable vertical borders in columns Body until hovered for resize (borders will always appear in Headers)")
        _, static.rh_flags = imgui.checkbox_flags("ImGuiTableFlags_HighlightHoveredColumn", static.rh_flags, imgui.TableFlags_.highlight_hovered_column.value)
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
        if imgui.begin_table("table2", 3, static.rh_flags | imgui.TableFlags_.sizing_fixed_fit.value, ImVec2(0.0, 0.0)):
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
    IMGUI_DEMO_MARKER("Tables/Padding")
    if imgui.tree_node("Padding"):
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
            static.padding_flags = (imgui.TableFlags_.borders_v.value)
            static.show_headers = False

        push_style_compact()
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_PadOuterX", static.padding_flags, imgui.TableFlags_.pad_outer_x.value)
        imgui.same_line()
        help_marker("Enable outer-most padding (default if ImGuiTableFlags_BordersOuterV is set)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadOuterX", static.padding_flags, imgui.TableFlags_.no_pad_outer_x.value)
        imgui.same_line()
        help_marker("Disable outer-most padding (default if ImGuiTableFlags_BordersOuterV is not set)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_NoPadInnerX", static.padding_flags, imgui.TableFlags_.no_pad_inner_x.value)
        imgui.same_line()
        help_marker("Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off)")
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersOuterV", static.padding_flags, imgui.TableFlags_.borders_outer_v.value)
        _, static.padding_flags = imgui.checkbox_flags("ImGuiTableFlags_BordersInnerV", static.padding_flags, imgui.TableFlags_.borders_inner_v.value)
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
            static.padding_flags2 = (imgui.TableFlags_.borders.value | imgui.TableFlags_.row_bg.value)
            static.cell_padding = [0.0, 0.0]
            static.show_widget_frame_bg = True

        push_style_compact()
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_Borders", static.padding_flags2, imgui.TableFlags_.borders.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersH", static.padding_flags2, imgui.TableFlags_.borders_h.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersV", static.padding_flags2, imgui.TableFlags_.borders_v.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersInner", static.padding_flags2, imgui.TableFlags_.borders_inner.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_BordersOuter", static.padding_flags2, imgui.TableFlags_.borders_outer.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_RowBg", static.padding_flags2, imgui.TableFlags_.row_bg.value)
        _, static.padding_flags2 = imgui.checkbox_flags("ImGuiTableFlags_Resizable", static.padding_flags2, imgui.TableFlags_.resizable.value)
        _, static.show_widget_frame_bg = imgui.checkbox("show_widget_frame_bg", static.show_widget_frame_bg)
        _, static.cell_padding = imgui.slider_float2("CellPadding", static.cell_padding, 0.0, 10.0, "%.0f")
        pop_style_compact()

        imgui.push_style_var(imgui.StyleVar_.cell_padding.value, static.cell_padding)  # type: ignore
        if imgui.begin_table("table_padding_2", 3, static.padding_flags2):
            if not hasattr(static, "text_bufs"):
                static.text_bufs = ["" for _ in range(3 * 5)]  # Mini text storage for 3x5 cells
                static.init = True
            if not static.show_widget_frame_bg:
                imgui.push_style_color(imgui.Col_.frame_bg.value, 0)
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

    if imgui.tree_node("etc. ..."):
        imgui.text("There are lots of other examples in the imgui C++ demo.")
        imgui.text("You can see it online within ImGui Manual:")
        imgui.text("    https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html")
        if imgui.small_button("Copy url"):
            imgui.set_clipboard_text("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html")
        imgui.tree_pop()

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
        for i in range(imgui.Col_.count.value):
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
# [SECTION] IMGUI_DEMO_MARKER utilities
# Utilities that provide an interactive "code lookup" via the IMGUI_DEMO_MARKER macro
# -----------------------------------------------------------------------------

# [sub section] ImGuiDemoMarker_GuiToggle()
# Display a "Code Lookup" checkbox that toggles interactive code browsing
def imgui_demo_marker_gui_toggle():
    global IMGUI_DEMO_MARKER_IS_ACTIVE
    _, IMGUI_DEMO_MARKER_IS_ACTIVE = imgui.checkbox("Code Lookup", IMGUI_DEMO_MARKER_IS_ACTIVE)
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            "Check this box and hover any demo to pinpoint its location inside the code.\n"
            "\n"
            "(you can also press \"Ctrl-Alt-C\" at any time to toggle this mode)"
        )
    if imgui.is_key_pressed(imgui.Key.c) and imgui.get_io().key_ctrl and imgui.get_io().key_alt:
        IMGUI_DEMO_MARKER_IS_ACTIVE = not IMGUI_DEMO_MARKER_IS_ACTIVE
    if IMGUI_DEMO_MARKER_IS_ACTIVE and imgui.is_key_pressed(imgui.Key.escape):
        IMGUI_DEMO_MARKER_IS_ACTIVE = False


CALLBACK_NAVIGATE_TO_MARKER: Optional[Callable[[str], None]] = None

# [sub section] ImGuiDemoMarkerCallback_Default()
# ImGuiDemoMarkerCallback_Default is the default callback used by IMGUI_DEMO_MARKER,
# but this can be overridden via GImGuiDemoMarkerCallback
def imgui_demo_marker_callback_default(marker):
    def get_caller_line_number() -> int:
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back.f_back  # type: ignore
            return caller_frame.f_lineno  # type: ignore
        finally:
            del frame
    if not IMGUI_DEMO_MARKER_IS_ACTIVE:
        return
    line = get_caller_line_number()
    if imgui_demo_marker_highlight_zone(line):
        imgui.set_tooltip(
            "Code Lookup\n"
            f"IMGUI_DEMO_MARKER(\"{marker}\")\n\n"
            "Press \"Esc\" to exit this mode")

        if CALLBACK_NAVIGATE_TO_MARKER is not None:
            CALLBACK_NAVIGATE_TO_MARKER(marker)


# A ZoneBoundings specifies a rectangular bounding for the widgets whose code is given
# *after* a call to IMGUI_DEMO_MARKER. This bounding will extend down to the next IMGUI_DEMO_MARKER macro call.
# It always occupies the full width of the current window.
class _ZoneBoundings:
    source_line_number: int # Source code location
    min_y: int; max_y: int  # Location of this zone inside its parent window
    window: Optional[imgui.internal.Window]  # Current window when IMGUI_DEMO_MARKER was called
    def __init__(self):
        self.source_line_number = -1
        self.min_y = 1
        self.max_y = -1
        self.Window = None


# [sub section] ImGuiDemoMarkerHighlightZone()
# `bool ImGuiDemoMarkerHighlightZone(int line_number)` is able to graphically highlight a *hovered* section
# of the demo (it keeps track of graphical location of each section).
# Each zone is identified by its source code line number, and ImGuiDemoMarkerHighlightZone will return true if
# it is currently highlighted.

# "namespace ImGuiDemoMarkerHighlight_Impl"
# The DemoMarkersRegistry class stores the boundings for the different calls to the IMGUI_DEMO_MARKER macro.
# It handles the display and handling of the "Help/Code lookup" button.
class ImGuiDemoMarkerHighlight_Impl_DemoMarkersRegistry:
    # Members
    all_zones_boundings: List[_ZoneBoundings] # All boundings for all the calls to DEMO_MARKERS
    previous_zone_source_line: int            # Location of the previous call to DEMO_MARKERS (used to end the previous bounding)

    def __init__(self):
        self.all_zones_boundings = []
        self.previous_zone_source_line = -1

    # highlight starts a demo marker zone.
    # If the highlight mode is active and the demo marker zone is hovered, it will highlight it,
    # display a tooltip and return true. Otherwise it will return false.
    def highlight(self, line_number) -> bool:
        # This will store the bounding for the next widgets, and this bounding will extend until the next call to DemoMarker
        self._store_zone_boundings(line_number)
        zone_boundings = self._get_zone_boundings_for_line(line_number)

        # Handle mouse and keyboard actions if the zone is hovered
        is_mouse_hovering_zone = self._is_mouse_hovering_zone_boundings(zone_boundings)
        if not is_mouse_hovering_zone:
            return False

        self._highlight_zone(zone_boundings)
        return True

    # StoreZoneBoundings stores information about the marker zone.
    def _store_zone_boundings(self, line_number):
        # Store info about the marker
        current_zone_boundings = _ZoneBoundings()
        if self._has_zone_boundings_for_line(line_number):
            current_zone_boundings = self._get_zone_boundings_for_line(line_number)
        else:
            current_zone_boundings.source_line_number = line_number

        # Store min_y position for the current marker
        current_zone_boundings.window = imgui.internal.get_current_window()
        current_zone_boundings.min_y = imgui.get_cursor_screen_pos().y

        # Store the current marker in the list
        self._set_zone_boundings_for_line(line_number, current_zone_boundings)

        # Store max position for the previous marker
        if self._has_zone_boundings_for_line(self.previous_zone_source_line):
            previous_zone_boundings = self._get_zone_boundings_for_line(self.previous_zone_source_line)
            if previous_zone_boundings.window == imgui.internal.get_current_window():
                previous_zone_boundings.max_y = imgui.get_cursor_screen_pos().y

        self.previous_zone_source_line = line_number

    # Check if the mouse is hovering over the zone_boundings
    def _is_mouse_hovering_zone_boundings(self, zone_boundings):
        if not imgui.is_window_hovered(
                imgui.HoveredFlags_.allow_when_blocked_by_active_item.value |
                imgui.HoveredFlags_.root_and_child_windows.value |
                imgui.HoveredFlags_.no_popup_hierarchy.value):
            return False
        y_mouse = imgui.get_mouse_pos().y
        x_mouse = imgui.get_mouse_pos().x
        return (
                (y_mouse >= zone_boundings.min_y)
                and ((y_mouse < zone_boundings.max_y) or (zone_boundings.max_y < 0.0))
                and ((x_mouse >= imgui.get_window_pos().x) and (x_mouse < imgui.get_window_pos().x + imgui.get_window_size().x))
        )

    # Highlight the specified zone_boundings
    def _highlight_zone(self, zone_boundings):
        # tl_dim / br_dim: top_left and bottom_right corners of the dimmed zone
        tl_dim = imgui.get_window_pos()
        br_dim = ImVec2(imgui.get_window_pos().x + imgui.get_window_size().x, imgui.get_window_pos().y + imgui.get_window_size().y)

        # tl_zone / br_zone: top_left and bottom_right corners of the highlighted zone
        min_y = zone_boundings.min_y if zone_boundings.min_y >= imgui.get_window_pos().y else imgui.get_window_pos().y
        tl_zone = ImVec2(imgui.get_window_pos().x, min_y)
        max_y = zone_boundings.max_y if zone_boundings.max_y > 0.0 else imgui.get_window_pos().y + imgui.get_window_height()
        br_zone = ImVec2(imgui.get_window_pos().x + imgui.get_window_width(), max_y)

        draw_list = imgui.get_foreground_draw_list()
        dim_color = imgui.IM_COL32(127, 127, 127, 100)

        draw_list.add_rect_filled(tl_dim, ImVec2(br_dim.x, tl_zone.y), dim_color)

        draw_list.add_rect_filled(ImVec2(tl_dim.x, tl_zone.y), ImVec2(tl_zone.x, br_zone.y), dim_color)
        draw_list.add_rect_filled(ImVec2(br_zone.x, tl_zone.y), ImVec2(br_dim.x, br_zone.y), dim_color)

        draw_list.add_rect_filled(ImVec2(tl_dim.x, br_zone.y), ImVec2(br_dim.x, br_dim.y), dim_color)

    # Check if there are zone boundings for the given line_number
    def _has_zone_boundings_for_line(self, line_number):
        for zone in self.all_zones_boundings:
            if zone.source_line_number == line_number:
                return True
        return False

    # Get zone boundings for the given line_number
    def _get_zone_boundings_for_line(self, line_number):
        assert self._has_zone_boundings_for_line(line_number), "Please call has_zone_boundings_for_line before!"
        for zone in self.all_zones_boundings:
            if zone.source_line_number == line_number:
                return zone
        raise Exception("We should never get there!")

    # Set zone boundings for the given line_number
    def _set_zone_boundings_for_line(self, line_number, zone_boundings):
        if self._has_zone_boundings_for_line(line_number):
            self._get_zone_boundings_for_line(line_number)
        else:
            self.all_zones_boundings.append(zone_boundings)

G_DEMO_MARKERS_REGISTRY = ImGuiDemoMarkerHighlight_Impl_DemoMarkersRegistry()


def imgui_demo_marker_highlight_zone(line_number: int) -> bool:
    return G_DEMO_MARKERS_REGISTRY.highlight(line_number)


# -----------------------------------------------------------------------------
# [SECTION] Runner
# -----------------------------------------------------------------------------

def main():
    from imgui_bundle import hello_imgui, imgui_color_text_edit as ed

    global CALLBACK_NAVIGATE_TO_MARKER

    code_editor = ed.TextEditor()
    with open(__file__) as f:
        code = f.read()
        code_lines = code.splitlines()
        code_editor.set_text(code)

    def gui_demo():
        show_demo_window(True)

    def gui_code():
        code_editor.render("Code")

    def navigate_to_marker(marker):
        for i, line in enumerate(code_lines):
            if line.strip().startswith("IMGUI_DEMO_MARKER("):
                tokens = line.split('"')
                line_marker = tokens[1]
                if line_marker == marker:
                    coords_start = ed.TextEditor.Coordinates()
                    coords_start.m_line = i
                    coords_start.m_column = 1
                    coords_end = ed.TextEditor.Coordinates()
                    coords_end.m_line = i
                    coords_end.m_column = len(line)
                    code_editor.set_cursor_position(coords_start)
                    code_editor.set_selection(coords_start, coords_end)

    CALLBACK_NAVIGATE_TO_MARKER = navigate_to_marker

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "ImGui Demo - Python"
    runner_params.app_window_params.window_geometry.size = (1200, 900)
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space

    split = hello_imgui.DockingSplit(
        initial_dock_="MainDockSpace",
        direction_=imgui.Dir.left,
        ratio_=0.5,
        new_dock_="Dear ImGui Demo"
    )
    runner_params.docking_params.docking_splits = [split]

    win_demo = hello_imgui.DockableWindow(
        label_="Dear ImGui Demo",
        dock_space_name_="Dear ImGui Demo",
        gui_function_=gui_demo
    )
    win_code = hello_imgui.DockableWindow(
        label_="Code",
        dock_space_name_="MainDockSpace",
        gui_function_=gui_code
    )

    runner_params.docking_params.dockable_windows = [win_demo, win_code]

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
