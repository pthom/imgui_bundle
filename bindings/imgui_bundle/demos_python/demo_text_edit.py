# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import inspect
import textwrap

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
_source_functions: dict[str, object] = {}


def _show_source_toggle(func: object) -> None:
    """Show a 'Show source' checkbox. When checked, displays the function's source
    (obtained via inspect.getsource) in a read-only editor with light theme."""
    func_name = func.__name__  # type: ignore
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

    # Cursor position display
    imgui.same_line()
    pos = editor.get_main_cursor_position()
    imgui.text(f"Line: {pos.line + 1}  Col: {pos.column + 1}")

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
# Tab 4: Decorators & Context Menus
# Demonstrates: line decorators + context menus working together
#   - Right-click a line number to toggle a breakpoint
#   - Right-click in the text for "Go to definition" / "Find references"
#   - Breakpoints are shown as red circles via a line decorator
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
            "\n"
            "def greet(name):\n"
            '    print(f"Hello {name}")\n'
            "    x = 42\n"
            "    pi = math.pi\n"
            "    return x\n"
        )
        statics.editor.set_language(TextEditor.Language.python())

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
        def line_number_context_menu(line: int):
            has = line in statics.breakpoints
            label = ("Remove breakpoint" if has else "Set breakpoint") + f" (line {line + 1})"
            if imgui.menu_item_simple(label):
                if has:
                    statics.breakpoints.discard(line)
                else:
                    statics.breakpoints.add(line)

        statics.editor.set_line_number_context_menu_callback(line_number_context_menu)

        # Right-click in the text: different context menu
        def text_context_menu(line: int, column: int):
            if imgui.menu_item_simple("Go to definition"):
                statics.last_action = f"Go to definition at {line + 1}:{column + 1}"
            if imgui.menu_item_simple("Find references"):
                statics.last_action = f"Find references at {line + 1}:{column + 1}"

        statics.editor.set_text_context_menu_callback(text_context_menu)
        statics.initialized = True

    editor = statics.editor

    imgui.text("Right-click line numbers or press F9 to toggle breakpoints, right-click text for other actions.")
    if statics.last_action:
        imgui.same_line()
        imgui.text_colored(imgui.ImVec4(0.5, 0.8, 1.0, 1.0), f"  {statics.last_action}")

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    editor.render("##decorators_ctx")
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
        left = (
            "import math\n"
            "\n"
            "def greet():\n"
            '    print("Hello")\n'
            "    return 0\n"
        )
        right = (
            "import math\n"
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

    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    statics.diff.render("##diff")
    imgui.pop_font()


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
        if imgui.begin_tab_item("Decorators & Menus")[0]:
            demo_decorators_and_context_menus()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Filters")[0]:
            demo_filters()
            imgui.end_tab_item()
        if imgui.begin_tab_item("Text Diff")[0]:
            demo_text_diff()
            imgui.end_tab_item()
        imgui.end_tab_bar()


def main():
    from imgui_bundle import immapp

    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
