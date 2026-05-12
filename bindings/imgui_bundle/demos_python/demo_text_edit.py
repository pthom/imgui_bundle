# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import inspect
import textwrap
from typing import Callable, Any

from imgui_bundle import imgui, imgui_color_text_edit as ed, imgui_md, ImVec2
from imgui_bundle.immapp import static

TextEditor = ed.TextEditor
TextDiff = ed.TextDiff


# ============================================================================
# Source display helper: shows the code of a demo function in a collapsible section
# ============================================================================
_source_show_flags: dict[str, bool] = {}
_source_editors: dict[str, TextEditor] = {}
# Map function names to their actual function objects (filled by each demo function)
_source_functions: dict[str, Callable[..., Any]] = {}


def _show_source_toggle(func: Callable[..., Any]) -> None:
    """Show a 'Show source' checkbox. When checked, displays the function's source
    (obtained via inspect.getsource) in a read-only editor with light theme."""
    func_name = func.__name__
    if func_name not in _source_show_flags:
        _source_show_flags[func_name] = False

    _, _source_show_flags[func_name] = imgui.checkbox("Show source", _source_show_flags[func_name])
    if _source_show_flags[func_name]:
        imgui.separator_text("Source")
        if func_name not in _source_editors:
            source = textwrap.dedent(inspect.getsource(func))
            editor = TextEditor()
            editor.set_text(source)
            editor.set_language(TextEditor.Language.python())
            editor.set_palette(TextEditor.get_light_palette())
            editor.set_read_only_enabled(True)
            editor.set_carets_visible(False)
            _source_editors[func_name] = editor
        code_font = imgui_md.get_code_font()
        imgui.push_font(code_font.font, code_font.size)
        _source_editors[func_name].render(f"##src_{func_name}", ImVec2(-1, imgui.get_text_line_height() * 15), False)
        imgui.pop_font()
        imgui.separator_text("Demo")


# ============================================================================
# Tab 1: Basic Editor
# Demonstrates: text loading, language selection, palette switching
# ============================================================================
@static(initialized=False, editor=None, lang_idx=3)  # default: Python
def demo_basic_editor():
    _show_source_toggle(demo_basic_editor)
    statics = demo_basic_editor
    if not statics.initialized:
        statics.editor = TextEditor()
        with open(__file__, encoding="utf8") as f:
            code = f.read()
        statics.editor.set_text(code)
        statics.editor.set_language(TextEditor.Language.python())
        statics.initialized = True
    editor = statics.editor

    # Palette buttons
    if imgui.small_button("Dark"):
        editor.set_palette(TextEditor.get_dark_palette())
    imgui.same_line()
    if imgui.small_button("Light"):
        editor.set_palette(TextEditor.get_light_palette())

    # Language selection
    imgui.same_line()
    imgui.set_next_item_width(imgui.calc_text_size("AngelScript__").x)
    lang_names = ["None", "C++", "C", "Python", "GLSL", "HLSL", "Lua", "SQL", "AngelScript", "C#", "JSON", "Markdown"]
    changed, statics.lang_idx = imgui.combo("Language", statics.lang_idx, lang_names)
    if changed:
        langs = [
            None,
            TextEditor.Language.cpp(), TextEditor.Language.c(),
            TextEditor.Language.python(), TextEditor.Language.glsl(),
            TextEditor.Language.hlsl(), TextEditor.Language.lua(),
            TextEditor.Language.sql(), TextEditor.Language.angel_script(),
            TextEditor.Language.cs(), TextEditor.Language.json(),
            TextEditor.Language.markdown(),
        ]
        editor.set_language(langs[statics.lang_idx])

    # Cursor position display (doc coords: row != line once word-wrap is on)
    imgui.same_line()
    pos = editor.get_main_cursor_position()
    imgui.text(f"Line: {pos.line + 1}  Col: {pos.index + 1}  (doc)")

    # Second row: editor view/behavior toggles
    wrap = editor.is_word_wrap_enabled()
    changed, wrap = imgui.checkbox("Word Wrap", wrap)
    if changed:
        editor.set_word_wrap_enabled(wrap)
    imgui.same_line()
    read_only = editor.is_read_only_enabled()
    changed, read_only = imgui.checkbox("Read Only", read_only)
    if changed:
        editor.set_read_only_enabled(read_only)
    imgui.same_line()
    folding = editor.is_line_folding_enabled()
    changed, folding = imgui.checkbox("Line Folding", folding)
    if changed:
        editor.set_line_folding_enabled(folding)
    imgui.same_line()
    imgui.begin_disabled(not folding)
    if imgui.small_button("Unfold All"):
        editor.unfold_all()
    imgui.end_disabled()
    imgui.same_line()
    mini_map = editor.is_show_mini_map_enabled()
    changed, mini_map = imgui.checkbox("Show Mini Map", mini_map)
    if changed:
        editor.set_show_mini_map_enabled(mini_map)
    imgui.text_disabled("(folding uses brackets for C/C++, indentation for Python)")

    # Render editor: we shall use a monospace font
    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##basic")
    imgui.pop_font()


# ============================================================================
# Tab 2: Change Callback
# Demonstrates: detecting edits via set_change_callback
# ============================================================================
@static(initialized=False, editor=None, change_count=0)
def demo_change_callback():
    _show_source_toggle(demo_change_callback)
    statics = demo_change_callback
    if not statics.initialized:
        statics.editor = TextEditor()
        statics.editor.set_text("Edit this text to see the change callback in action.\n\nTry typing, deleting, or pasting.\n")
        statics.editor.set_language(TextEditor.Language.python())
        statics.editor.set_change_callback(lambda: setattr(statics, 'change_count', statics.change_count + 1), 200)
        statics.initialized = True
    editor = statics.editor

    imgui.text(f"Change count: {statics.change_count}")

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##changes")
    imgui.pop_font()


# ============================================================================
# Tab 3: Filters
# Demonstrates: filter_selections to transform selected text
# ============================================================================
@static(initialized=False, editor=None)
def demo_filters():
    _show_source_toggle(demo_filters)
    statics = demo_filters
    if not statics.initialized:
        statics.editor = TextEditor()
        statics.editor.set_text(
            "Select some text below, then click a filter button.\n"
            "\n"
            "Hello World\n"
            "the quick brown fox jumps over the lazy dog\n"
            "SOME UPPERCASE TEXT\n"
            "mixed Case Text Here\n"
        )
        statics.initialized = True
    editor = statics.editor

    imgui.text("Select text, then apply a filter:")
    imgui.same_line()
    if imgui.small_button("UPPER"):
        editor.filter_selections(lambda text: text.upper())
    imgui.same_line()
    if imgui.small_button("lower"):
        editor.filter_selections(lambda text: text.lower())
    imgui.same_line()
    if imgui.small_button("Strip trailing spaces"):
        editor.strip_trailing_whitespaces()

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##filters")
    imgui.pop_font()


# ============================================================================
# Tab 4: Annotations & Interactivity
# Demonstrates four ways to annotate or react inside an editor:
#   - Line decorator (custom-drawn gutter): red circle on breakpoint lines
#   - Line markers (colored gutter + tooltips): error & warning markers
#   - Context menus on line numbers and on text (right-click)
#   - Hover callback in text: live popup showing the word under the cursor
# ============================================================================
@static(initialized=False, editor=None, breakpoints=None, last_action="")
def demo_decorators_and_context_menus():
    _show_source_toggle(demo_decorators_and_context_menus)
    statics = demo_decorators_and_context_menus
    if not statics.initialized:
        statics.breakpoints = set()
        statics.editor = TextEditor()
        statics.editor.set_text(
            "import math\n"
            "from typing import List\n"
            "\n"
            "# Compute summary statistics for a list of numbers.\n"
            "def stats(values):\n"
            "    if not values:\n"
            "        return None\n"
            "    total = sum(values)\n"
            "    count = len(values)\n"
            "    mean = total / count\n"
            "    variance = sum((v - mean) ** 2 for v in values) / count\n"
            "    unused = 'leftover'\n"
            "    return mean, math.sqrt(variance)\n"
            "\n"
            "def greet(name):\n"
            '    print(f"Hello {name}")\n'
            "    return name\n"
            "\n"
            "def divide(a, b):\n"
            "    return a // b\n"
            "\n"
            "def main():\n"
            "    data = [1, 2, 3, 4, 5]\n"
            "    m, s = stats(data)\n"
            '    print(f"mean={m} std={s}")\n'
            '    greet("world")\n'
            "    print(divide(10, 0))\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        )
        statics.editor.set_language(TextEditor.Language.python())

        # Markers: persistent colored bands in the gutter / text background,
        # with built-in tooltips on hover (no callback needed for the tooltip).
        # Spread across the file so the scrollbar mini map has visible ticks.
        # Line numbers are zero-based.
        warning_color = imgui.IM_COL32(180, 140, 0, 255)
        warning_bg    = imgui.IM_COL32(180, 140, 0, 48)
        error_color   = imgui.IM_COL32(220, 50, 50, 255)
        error_bg      = imgui.IM_COL32(220, 50, 50, 56)
        statics.editor.add_marker(
            1, warning_color, warning_bg,
            "warning", "Imported but never used: 'List'",
        )
        statics.editor.add_marker(
            11, warning_color, warning_bg,
            "warning", "Unused variable: 'unused'",
        )
        statics.editor.add_marker(
            19, error_color, error_bg,
            "error", "Unchecked division: b may be zero",
        )
        statics.editor.add_marker(
            26, error_color, error_bg,
            "error", "ZeroDivisionError at runtime: divide(10, 0)",
        )

        # Decorator: draw a red circle on lines that have a breakpoint
        def decorator_callback(decorator: TextEditor.Decorator):
            if decorator.line in statics.breakpoints:
                cursor_pos = imgui.get_cursor_screen_pos()
                center = ImVec2(
                    cursor_pos.x + decorator.glyph_size.x * 0.5,
                    cursor_pos.y + decorator.glyph_size.y * 0.5,
                )
                radius = decorator.glyph_size.y * 0.35
                imgui.get_window_draw_list().add_circle_filled(center, radius, imgui.IM_COL32(255, 60, 60, 255))

        statics.editor.set_line_decorator(-2.0, decorator_callback)

        # Right-click on line numbers: toggle breakpoint
        def line_number_context_menu(data: TextEditor.PopupData):
            line = data.pos.line
            has = line in statics.breakpoints
            label = ("Remove breakpoint" if has else "Set breakpoint") + f" (line {line + 1})"
            if imgui.menu_item_simple(label):
                if has:
                    statics.breakpoints.discard(line)
                else:
                    statics.breakpoints.add(line)

        statics.editor.set_line_number_context_menu_callback(line_number_context_menu)

        # Right-click in the text: different context menu
        def text_context_menu(data: TextEditor.PopupData):
            line = data.pos.line
            column = data.pos.index
            if imgui.menu_item_simple("Go to definition"):
                statics.last_action = f"Go to definition at {line + 1}:{column + 1}"
            if imgui.menu_item_simple("Find references"):
                statics.last_action = f"Find references at {line + 1}:{column + 1}"

        statics.editor.set_text_context_menu_callback(text_context_menu)

        # Hover in text: live popup with the word under the mouse
        # (think IDE quick-info / type-on-hover).
        def text_hover(data: TextEditor.PopupData):
            word = statics.editor.get_word_at_mouse_pos(imgui.get_mouse_pos())
            imgui.text(f"Hovered: line {data.pos.line + 1}, col {data.pos.index + 1}")
            if word:
                imgui.text(f"Word: {word}")

        statics.text_hover = text_hover  # kept so the toggle can re-install it
        statics.editor.set_text_hover_callback(text_hover)

        statics.initialized = True

    editor = statics.editor

    imgui.text(
        "Right-click line numbers (or F9) to toggle breakpoints. "
        "Right-click in text for a menu. Hover text for live info. "
        "Hover the colored gutter bands for marker tooltips."
    )
    if statics.last_action:
        imgui.text_colored(imgui.ImVec4(0.5, 0.8, 1.0, 1.0), statics.last_action)

    imgui.begin_disabled(not editor.has_markers())
    if imgui.small_button("Clear markers"):
        editor.clear_markers()
    imgui.end_disabled()
    imgui.same_line()
    mini_map = editor.is_show_mini_map_enabled()
    changed, mini_map = imgui.checkbox("Show Mini Map", mini_map)
    if changed:
        editor.set_show_mini_map_enabled(mini_map)
    imgui.same_line()
    hover_on = editor.has_text_hover_callback()
    changed, hover_on = imgui.checkbox("Hover hints", hover_on)
    if changed:
        if hover_on:
            editor.set_text_hover_callback(statics.text_hover)
        else:
            editor.clear_text_hover_callback()
    imgui.same_line()
    scrollbar_mini = editor.is_show_scrollbar_mini_map_enabled()
    changed, scrollbar_mini = imgui.checkbox("Show Scrollbar Mini Map", scrollbar_mini)
    if changed:
        editor.set_show_scrollbar_mini_map_enabled(scrollbar_mini)
    imgui.same_line()
    imgui.text_disabled("(ticks in the scrollbar at marker / selection lines)")

    imgui.new_line()
    imgui.new_line()
    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##decorators_ctx", ImVec2(-1, imgui.get_text_line_height() * 20))
    imgui.pop_font()

    # F9: toggle breakpoint on current line
    if imgui.shortcut(imgui.Key.f9):
        line = editor.get_main_cursor_position().line
        if line in statics.breakpoints:
            statics.breakpoints.discard(line)
        else:
            statics.breakpoints.add(line)


# ============================================================================
# Tab 5: Text Diff
# Demonstrates: side-by-side text comparison with TextDiff
# ============================================================================
@static(initialized=False, diff=None, side_by_side=False)
def demo_text_diff():
    _show_source_toggle(demo_text_diff)
    statics = demo_text_diff
    if not statics.initialized:
        # The long docstring line on the second row exists so that toggling
        # the Word Wrap checkbox produces a visible effect on the diff.
        left = (
            "import math\n"
            '"""Module that says hello. A tiny example used in the ImGui Bundle TextDiff demo to show how line-by-line comparison works."""\n'
            "\n"
            "def greet():\n"
            '    print("Hello")\n'
            "    return 0\n"
        )
        right = (
            "import math\n"
            '"""Module that says hello to anyone by name. A tiny example used in the ImGui Bundle TextDiff demo to show how line-by-line comparison and word-wrap work together."""\n'
            "import os\n"
            "\n"
            "def greet(name):\n"
            '    print(f"Hello, {name}")\n'
            "    return 0\n"
        )
        statics.diff = TextDiff()
        statics.diff.set_text(left, right)
        statics.diff.set_language(TextEditor.Language.python())
        statics.initialized = True

    changed, statics.side_by_side = imgui.checkbox("Side by side", statics.side_by_side)
    if changed:
        statics.diff.set_side_by_side_mode(statics.side_by_side)
    imgui.same_line()
    wrap = statics.diff.is_word_wrap_enabled()
    changed, wrap = imgui.checkbox("Word Wrap", wrap)
    if changed:
        statics.diff.set_word_wrap_enabled(wrap)

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    statics.diff.render("##diff")
    imgui.pop_font()


# ============================================================================
# Tab 6: Editor with Menus
# Demonstrates how menus can be added to supplement the editor
# ============================================================================


@static(initialized=False, editor=None, find_text="", replace_text="", case_sensitive=True, whole_word=False)
def demo_editor_with_menus():
    _show_source_toggle(demo_editor_with_menus)
    statics = demo_editor_with_menus
    if not statics.initialized:
        statics.editor = TextEditor()
        statics.editor.set_text(
            "import math\n"
            "\n"
            "def greet(name):\n"
            '    print(f"Hello {name}")\n'
            "    x = 42\n"
            "    pi = math.pi\n"
            "    return x\n"
        )
        statics.editor.set_language(TextEditor.Language.python())
        statics.initialized = True
    editor = statics.editor

    imgui.begin_child("editor_with_menus", ImVec2(0, 0), 0, imgui.WindowFlags_.menu_bar.value)

    import platform
    _shortcut = "Cmd-" if platform.system() == "Darwin" else "Ctrl-"

    if imgui.begin_menu_bar():
        if imgui.begin_menu("Edit"):
            if imgui.menu_item_simple("Undo", f"{_shortcut}Z", enabled=editor.can_undo()):
                editor.undo()
            if imgui.menu_item_simple("Redo", f"{_shortcut}Y", enabled=editor.can_redo()):
                editor.redo()
            imgui.separator()
            if imgui.menu_item_simple("Cut", f"{_shortcut}X", enabled=editor.any_cursor_has_selection()):
                editor.cut()
            if imgui.menu_item_simple("Copy", f"{_shortcut}C", enabled=editor.any_cursor_has_selection()):
                editor.copy()
            if imgui.menu_item_simple("Paste", f"{_shortcut}V"):
                editor.paste()
            imgui.separator()
            _, flag = imgui.menu_item("Insert Spaces on Tabs", "", editor.is_insert_spaces_on_tabs())
            if _:
                editor.set_insert_spaces_on_tabs(flag)
            if imgui.menu_item_simple("Tabs To Spaces"):
                editor.tabs_to_spaces()
            if imgui.menu_item_simple("Spaces To Tabs", enabled=not editor.is_insert_spaces_on_tabs()):
                editor.spaces_to_tabs()
            if imgui.menu_item_simple("Strip Trailing Whitespaces"):
                editor.strip_trailing_whitespaces()
            imgui.end_menu()

        if imgui.begin_menu("Selection"):
            if imgui.menu_item_simple("Select All", f"{_shortcut}A", enabled=not editor.is_empty()):
                editor.select_all()
            imgui.separator()
            if imgui.menu_item_simple("Indent Line(s)", f"{_shortcut}]", enabled=not editor.is_empty()):
                editor.indent_lines()
            if imgui.menu_item_simple("Deindent Line(s)", f"{_shortcut}[", enabled=not editor.is_empty()):
                editor.deindent_lines()
            if imgui.menu_item_simple("Move Line(s) Up", "Alt-Up", enabled=not editor.is_empty()):
                editor.move_up_lines()
            if imgui.menu_item_simple("Move Line(s) Down", "Alt-Down ", enabled=not editor.is_empty()):
                editor.move_down_lines()
            if imgui.menu_item_simple("Toggle Comments", f"{_shortcut}/", enabled=editor.has_language()):
                editor.toggle_comments()
            imgui.separator()
            if imgui.menu_item_simple("To Uppercase", enabled=editor.any_cursor_has_selection()):
                editor.selection_to_upper_case()
            if imgui.menu_item_simple("To Lowercase", enabled=editor.any_cursor_has_selection()):
                editor.selection_to_lower_case()
            imgui.separator()
            if imgui.menu_item_simple("Add Next Occurrence", f"{_shortcut}D", enabled=editor.current_cursor_has_selection()):
                editor.add_next_occurrence()
            if imgui.menu_item_simple("Select All Occurrences",  f"^{_shortcut}D", enabled=editor.current_cursor_has_selection()):
                editor.select_all_occurrences()
            imgui.end_menu()

        if imgui.begin_menu("View"):
            _, flag = imgui.menu_item("Show Whitespaces", "", editor.is_show_whitespaces_enabled())
            if _:
                editor.set_show_whitespaces_enabled(flag)
            _, flag = imgui.menu_item("Show Spaces", "", editor.is_show_spaces_enabled())
            if _:
                editor.set_show_spaces_enabled(flag)
            _, flag = imgui.menu_item("Show Tabs", "", editor.is_show_tabs_enabled())
            if _:
                editor.set_show_tabs_enabled(flag)
            _, flag = imgui.menu_item("Show Line Numbers", "", editor.is_show_line_numbers_enabled())
            if _:
                editor.set_show_line_numbers_enabled(flag)
            _, flag = imgui.menu_item("Show Matching Brackets", "", editor.is_showing_matching_brackets())
            if _:
                editor.set_show_matching_brackets(flag)
            _, flag = imgui.menu_item("Complete Matching Glyphs", "", editor.is_completing_paired_glyphs())
            if _:
                editor.set_complete_paired_glyphs(flag)
            _, flag = imgui.menu_item("Show Pan/Scroll Indicator", "", editor.is_show_pan_scroll_indicator_enabled())
            if _:
                editor.set_show_pan_scroll_indicator_enabled(flag)
            _, flag = imgui.menu_item("Middle Mouse Pan Mode", "", editor.is_middle_mouse_pan_mode())
            if _:
                if flag:
                    editor.set_middle_mouse_pan_mode()
                else:
                    editor.set_middle_mouse_scroll_mode()
            imgui.separator()
            _, flag = imgui.menu_item("Word Wrap", "", editor.is_word_wrap_enabled())
            if _:
                editor.set_word_wrap_enabled(flag)
            _, flag = imgui.menu_item("Line Folding", "", editor.is_line_folding_enabled())
            if _:
                editor.set_line_folding_enabled(flag)
            _, flag = imgui.menu_item("Show Mini Map", "", editor.is_show_mini_map_enabled())
            if _:
                editor.set_show_mini_map_enabled(flag)
            _, flag = imgui.menu_item("Show Scrollbar Mini Map", "", editor.is_show_scrollbar_mini_map_enabled())
            if _:
                editor.set_show_scrollbar_mini_map_enabled(flag)
            imgui.end_menu()

        if imgui.begin_menu("Find"):
            if imgui.menu_item_simple("Find", f"{_shortcut}F"):
                editor.open_find_replace_window()
            if imgui.menu_item_simple("Find Next",  f"{_shortcut}G", enabled=editor.has_find_string()):
                editor.find_next()
            # if imgui.menu_item_simple(f"Find All",  f"Shift {_shortcut}G", enabled=editor.has_find_string()):
            #     editor.find_all()
            imgui.end_menu()

        imgui.end_menu_bar()


    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##editor_menus")
    imgui.pop_font()

    imgui.end_child()


# ============================================================================
# Tab 7: Multi-Cursor
# Demonstrates: multiple simultaneous cursors and selections.
# get_number_of_cursors / get_cursor_selection / get_cursor_text.
# ============================================================================
@static(initialized=False, editor=None)
def demo_multi_cursor():
    def _init_statics():
        statics = demo_multi_cursor
        if not statics.initialized:
            statics.editor = TextEditor()
            statics.editor.set_text(
                "# Multi-cursor playground.\n"
                "# - Alt-click (Mac) / Ctrl-click (Windows, Linux) to add a cursor\n"
                "#   at the click location.\n"
                "# - Hold the same modifier and drag to add a cursor and extend its selection\n"
                "# - Double-click a word to select it, then Ctrl-D (or Command-D on Mac)\n"
                "#   to add a cursor at the next occurrence of the same word.\n"
                "\n"
                "value = 1\n"
                "value = value + 1\n"
                "value = value * value\n"
                "value = value - 1\n"
                "print(value, value, value)\n"
            )
            statics.editor.set_language(TextEditor.Language.python())
            statics.initialized = True

    def _gui_select_occurrences():
        editor = demo_multi_cursor.editor

        # Quick-action buttons. add_next_occurrence / select_all_occurrences
        # require the current cursor to have a selection (a word to match).
        imgui.begin_disabled(not editor.current_cursor_has_selection())
        if imgui.small_button("Add Next Occurrence"):
            editor.add_next_occurrence()
        imgui.same_line()
        if imgui.small_button("Select All Occurrences"):
            editor.select_all_occurrences()
        imgui.end_disabled()
        imgui.same_line()

        imgui.begin_disabled(editor.get_number_of_cursors() <= 1)
        if imgui.small_button("Clear Extra Cursors"):
            editor.clear_cursors()  # leaves a single cursor at the main location
        imgui.end_disabled()

    def _gui_editor():
        editor = demo_multi_cursor.editor
        code_font = imgui_md.get_code_font()
        imgui.push_font(code_font.font, code_font.size)
        editor_height = imgui.get_text_line_height() * 20
        editor.render("##multi_cursor", size=ImVec2(0, editor_height))
        imgui.pop_font()

    # Live cursor status panel
    def _gui_cursors_info():
        editor = demo_multi_cursor.editor
        n_cursors = editor.get_number_of_cursors()
        imgui.text(f"Cursors: {n_cursors}")
        for i in range(n_cursors):
            sel = editor.get_cursor_selection(i)
            text = editor.get_cursor_text(i)
            if not text:
                imgui.bullet_text(
                    f"[{i}] L:{sel.start.line + 1} C:{sel.start.index + 1}"
                )
            else:
                imgui.bullet_text(
                    f"[{i}] L:{sel.start.line + 1} C:{sel.start.index + 1} "
                    f"-> L:{sel.end.line + 1} C:{sel.end.index + 1}  "
                    f"selected: {text!r}"
                )

    # Main gui for demo_multi_cursors
    _init_statics()
    _show_source_toggle(demo_multi_cursor)
    _gui_select_occurrences()
    _gui_editor()
    _gui_cursors_info()

# ============================================================================
# Main demo function
# ============================================================================
def demo_gui():
    imgui_md.render(
        """
# ImGuiColorTextEdit
[ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit) is a syntax highlighting text editor for Dear ImGui (originally by BalazsJako, rewritten by Johan A. Goossens)
    """
    )

    if imgui.begin_tab_bar("##TextEditorDemos"):
        if imgui.begin_tab_item("Basic Editor")[0]:
            demo_basic_editor()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Change Callback")[0]:
            demo_change_callback()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Annotations & Interactivity")[0]:
            demo_decorators_and_context_menus()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Filters")[0]:
            demo_filters()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Text Diff")[0]:
            demo_text_diff()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Multi-Cursor")[0]:
            demo_multi_cursor()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Editor with Menus")[0]:
            demo_editor_with_menus()
            imgui.end_tab_item()
        imgui.end_tab_bar()


def main():
    from imgui_bundle import immapp

    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
