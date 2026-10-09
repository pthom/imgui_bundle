"""Rich Markdown: a narrated tour

Markdown drawn by Dear ImGui as you type: styles, a table, math, code, a diagram. Then a document, with its table of
contents, its search, its folds and its selection. A voice tells; the cursor of the test engine types and clicks.
"""
import sys
from pathlib import Path
from typing import Any, Optional

from imgui_bundle import hello_imgui, imgui, immapp, rich_md, imgui_color_text_edit as ed
from imgui_bundle import ImVec2

sys.path.insert(0, str(Path(__file__).parent.parent / "grokking"))   # the player, shared with the grokking lesson
import narrator  # noqa: E402

SPLIT_BELOW_EM = 44.0          # a narrower stage stacks the source above the page
SOURCE_SHARE = 0.42            # the source's share of the stage, beside or above the page
FIRST_LINE_EM = 2.85           # from the top of a ## heading to the middle of the first line under it
FOLLOW_END_CHARS = 300         # an edit closer than this to the end of the text: the page scrolls to its end
DARK, LIGHT = hello_imgui.ImGuiTheme_.darcula_darker, hello_imgui.ImGuiTheme_.white_is_white

# The document, part by part: the lesson types the short ones and pastes the long ones (part(name)); upto(name) is
# the document from its start to a part, the state at a chapter's start
PARTS: list[tuple[str, str]] = [
    ("title", "# The Solar System\n\n"),
    ("intro", "Eight planets circle the Sun: four *rocky* ones, and four **giants** of gas and ice. "
              "~~Pluto~~ was demoted in 2006.\n\n"),
    ("table", "## The planets\n\n"
              "| Planet  | Distance (AU) | Year (days) |\n"
              "|---------|--------------:|------------:|\n"
              "| Mercury | 0.39 | 88 |\n"
              "| Venus   | 0.72 | 225 |\n"
              "| Earth   | 1.00 | 365 |\n"
              "| Mars    | 1.52 | 687 |\n"
              "| Jupiter | 5.20 | 4,333 |\n"
              "| Saturn  | 9.58 | 10,759 |\n"
              "| Uranus  | 19.2 | 30,687 |\n"
              "| Neptune | 30.1 | 60,190 |\n\n"),
    ("kepler", "## Kepler's law\n\n"
               "The farther the planet, the longer its year: $T^2 = a^3$, in years and AU.\n\n"),
    ("newton", "Newton explained it with gravity:\n\n"
               "$$\nT = 2\\pi \\sqrt{\\frac{a^3}{G M}}\n$$\n\n"),
    ("code", "The year of Mars, in Python:\n\n"
             "```python\n"
             "a = 1.524                  # the distance of Mars, in AU\n"
             "T = a ** 1.5               # Kepler: T² = a³\n"
             "print(f\"{T:.2f} years\")    # 1.88 years: 687 days\n"
             "```\n\n"),
    ("families", "## The families\n\n"
                 "[The table](#the-planets) lists the planets from the Sun outwards. They form three families:\n\n"
                 "```mermaid\n"
                 "flowchart LR\n"),
    ("fam_sun", "    Sun((Sun)) --> Rocky[Rocky planets]\n"),
    ("fam_gas", "    Sun --> Gas[Gas giants]\n"),
    ("fam_ice", "    Sun --> Ice[Ice giants]\n"),
    ("fam_examples", "    Rocky --> Earth\n"
                     "    Gas --> Jupiter\n"
                     "    Ice --> Neptune\n"),
    ("families_end", "```\n"),
    ("exploration", "\n## Exploration\n\n"
                    "> [!NOTE]\n"
                    "> A spacecraft has visited every planet. People have walked on the Moon only.\n\n"
                    "- [x] The Moon, 1969\n"
                    "- [x] A rover on Mars, 1997\n"
                    "- [x] Pluto, by New Horizons, 2015\n"
                    "- [ ] People on Mars\n\n"
                    "<details>\n"
                    "<summary>The dwarf planets</summary>\n\n"
                    "Pluto, Eris, Haumea, Makemake and Ceres. Ceres orbits between Mars and Jupiter, in the "
                    "asteroid belt.\n\n"
                    "</details>\n"),
]
PART_NAMES = [name for name, _ in PARTS]


def part(name: str) -> str:
    return dict(PARTS)[name]


def upto(name: str) -> str:
    """The document from its start to the part `name`, included; a code fence left open is closed"""
    text = "".join(t for _, t in PARTS[:PART_NAMES.index(name) + 1])
    if text.count("```") % 2 == 1:
        text += "```\n"
    return text


FULL = upto(PART_NAMES[-1])


class AppState:
    def __init__(self) -> None:
        self.source = FULL           # the markdown, in the editor and on the page
        self.view = "split"          # "split": the source and the page; "page": the page alone
        self.page_width = 1.0        # the page's share of the stage's width ("page" view): a narrow page, shown
        self.theme = "dark"          # "dark" or "light"
        self.page_id = 0             # a new id: a fresh document (no fold, no search, at the top)
        self._theme_applied = "dark"

    def reset_page(self) -> None:
        self.page_id += 1


class PageGeometry:
    """Where the page's parts were drawn in the last frame: the gestures' targets are computed from it"""

    def __init__(self) -> None:
        self.headings: list[rich_md.Heading] = []
        self.content_pos = ImVec2(0, 0)   # the content window's position, and its scroll
        self.scroll_y = 0.0
        self.fold_left = 0.0              # the left of the fold arrows' margin
        self.text_left = 0.0              # the left of the text
        self.text_right = 0.0
        self.content_bottom = 0.0
        self.toc_window = ""              # the table of contents' window, and the document's
        self.document_window = ""
        self.page_rect: Optional[narrator.Rect] = None
        self.follow_end = False           # the lesson typed in this frame: the page shows its end
        self.editor_rect: Optional[narrator.Rect] = None

    def record(self) -> None:
        """Called in the document, after its render"""
        window = imgui.internal.get_current_window()
        document = window.parent_window
        self.headings = list(rich_md.last_render_headings())
        self.content_pos = imgui.get_window_pos()
        self.scroll_y = imgui.get_scroll_y()
        self.fold_left = self.content_pos.x + imgui.get_cursor_start_pos().x
        self.text_left = imgui.get_cursor_screen_pos().x
        self.text_right = self.text_left + imgui.get_content_region_avail().x
        self.content_bottom = self.content_pos.y + imgui.get_window_height()
        self.toc_window = f"{document.name}/##toc_{document.get_id('##toc'):08X}"
        self.document_window = document.name


app_state = AppState()
page = PageGeometry()
editor = ed.TextEditor()
editor.set_language(ed.TextEditor.Language.markdown())
editor.set_show_line_numbers_enabled(False)
editor.set_show_whitespaces_enabled(False)
editor.set_word_wrap_enabled(True)
editor.set_auto_indent_enabled(False)          # the lesson types its text as it is
editor.set_complete_paired_glyphs(False)
_editor_text = ""                     # the text the editor shows


# =============================================================================
# The gestures' targets: rectangles on screen, computed when a gesture plays
# =============================================================================

def _heading(text: str) -> Optional[rich_md.Heading]:
    return next((h for h in page.headings if h.text == text and not h.hidden), None)


def _heading_top(h: rich_md.Heading) -> float:
    return page.content_pos.y + h.y - page.scroll_y


def _heading_height(h: rich_md.Heading) -> float:
    return rich_md.get_font(rich_md.MarkdownFontSpec(False, False, h.level)).size


def _visible(rect: narrator.Rect) -> Optional[narrator.Rect]:
    """The rectangle, if it lies in the page's visible content"""
    top, bottom = page.content_pos.y, page.content_bottom
    return rect if rect[0].y >= top and rect[1].y <= bottom else None


def target_heading(text: str, ctx: Any) -> Optional[narrator.Rect]:
    """A heading's title"""
    h = _heading(text)
    if h is None:
        return None
    y = _heading_top(h)
    return _visible((ImVec2(page.text_left, y), ImVec2(page.text_right, y + _heading_height(h))))


def target_fold(text: str, ctx: Any) -> Optional[narrator.Rect]:
    """The fold arrow of a heading, in the margin at its left (shown under the mouse)"""
    h = _heading(text)
    if h is None:
        return None
    y = _heading_top(h)
    return _visible((ImVec2(page.fold_left, y), ImVec2(page.text_left, y + _heading_height(h))))


def target_line(text: str, ctx: Any) -> Optional[narrator.Rect]:
    """The first line of text under a ## heading"""
    h = _heading(text)
    if h is None:
        return None
    y = _heading_top(h) + FIRST_LINE_EM * hello_imgui.em_size()
    line = imgui.get_text_line_height()
    return _visible((ImVec2(page.text_left, y - line / 2), ImVec2(page.text_right, y + line / 2)))


def _window_items(ctx: Any, window_name: str) -> list[Any]:
    window = imgui.internal.find_window_by_name(window_name)
    if window is None or not window.active:
        return []
    items = imgui.test_engine.TestItemList()
    ctx.gather_items(items, imgui.test_engine.TestRef(window.id_), -1)
    return [items.get_by_index(i) for i in range(items.get_size())]


def target_toc(text: str, ctx: Any) -> Optional[narrator.Rect]:
    """An entry of the table of contents (its rows are as wide as the panel, in the order of the headings)"""
    window = imgui.internal.find_window_by_name(page.toc_window)
    if window is None or not window.active:
        return None
    rows = [it for it in _window_items(ctx, page.toc_window)
            if it.rect_full.max.x - it.rect_full.min.x > 0.6 * window.size.x]
    rows.sort(key=lambda it: it.rect_full.min.y)
    listed = [h.text for h in page.headings if h.level <= rich_md.DocumentOptions().toc_max_level]
    if text not in listed or len(rows) != len(listed):
        return None
    row = rows[listed.index(text)]
    return row.rect_full.min, row.rect_full.max


def _button(window_name: str, label: str, ctx: Any) -> Optional[narrator.Rect]:
    window = imgui.internal.find_window_by_name(window_name)
    if window is None or not window.active:
        return None
    info = ctx.item_info(imgui.test_engine.TestRef(window.get_id(label)))
    return (info.rect_full.min, info.rect_full.max) if info.id_ != 0 else None


def target_toc_hide(_: str, ctx: Any) -> Optional[narrator.Rect]:
    """The arrow that hides the table of contents"""
    return _button(page.toc_window, "##hide", ctx)


def target_toc_show(_: str, ctx: Any) -> Optional[narrator.Rect]:
    """The arrow that shows the table of contents again (in the line above the page)"""
    return _button(page.document_window, "##show", ctx)


def target_page(_: str, ctx: Any) -> Optional[narrator.Rect]:
    return page.page_rect


def target_editor(_: str, ctx: Any) -> Optional[narrator.Rect]:
    return page.editor_rect


# =============================================================================
# The lesson
# =============================================================================

lesson = narrator.Lesson(Path(__file__).parent / "scenario.md", program=__file__)   # the script, watched: edit it live
lesson.param(name="source", owner=app_state)
lesson.param(name="view", owner=app_state)
lesson.param(name="page_width", owner=app_state, range=(0.2, 1.0))
lesson.param(name="theme", owner=app_state)
lesson.action(name="reset_page", function=app_state.reset_page)
lesson.constant(name="upto", value=upto)
lesson.constant(name="part", value=part)
lesson.constant(name="FULL", value=FULL)
for _name, _resolver in (("heading", target_heading), ("fold", target_fold), ("line", target_line),
                         ("toc", target_toc), ("toc_hide", target_toc_hide), ("toc_show", target_toc_show),
                         ("page", target_page), ("editor", target_editor)):
    lesson.target(_name, _resolver)


# =============================================================================
# The stage
# =============================================================================

def _common_end(a: str, b: str) -> int:
    """The length of the end that two texts share"""
    n = 0
    while n < min(len(a), len(b)) and a[len(a) - 1 - n] == b[len(b) - 1 - n]:
        n += 1
    return n


def _doc_pos(text: str, index: int) -> ed.TextEditor.DocPos:
    line = text.count("\n", 0, index)
    return ed.TextEditor.DocPos(line, index - (text.rfind("\n", 0, index) + 1))


def gui_source(size: ImVec2) -> None:
    """The markdown source: the lesson types in it (its cursor follows), and the learner may edit it"""
    global _editor_text
    if app_state.source != _editor_text:          # typed by the lesson: the cursor at the end of the change
        before, after = _editor_text, app_state.source
        cursor = _doc_pos(after, len(after) - _common_end(before, after))
        editor.set_text(after)
        editor.set_cursor(cursor)
        editor.scroll_to_line(cursor.line, ed.TextEditor.Scroll.align_middle)
        _editor_text = after
        page.follow_end = True
    editor.render("##source", size)
    page.editor_rect = (imgui.get_item_rect_min(), imgui.get_item_rect_max())
    text = editor.get_text()
    if text != _editor_text:                      # edited by the learner: the lesson lets it be for a while
        if _common_end(_editor_text, text) < FOLLOW_END_CHARS:   # an edit near the end: the page shows it
            page.follow_end = True
        if len(text) - len(_editor_text) > 1:                    # a paste: the editor shows where it landed
            editor.scroll_to_line(editor.get_main_cursor_position().line, ed.TextEditor.Scroll.align_middle)
        app_state.source = _editor_text = text
        lesson.touched("source")
    lesson.widget("source")


def gui_page(size: ImVec2) -> None:
    """The page: the source rendered as a document (a table of contents, a search, headings that fold)"""
    options = rich_md.DocumentOptions()
    options.foldable_headings = True
    options.toc = app_state.view == "page"       # beside the source, the page is a preview
    start = imgui.get_cursor_screen_pos()
    with rich_md.document(f"page_{app_state.page_id}", size, options):
        rich_md.render(app_state.source)
        if page.follow_end:                      # the text grows at its end: the page follows, as a terminal
            imgui.set_scroll_here_y(1.0)
            page.follow_end = False
        page.record()
    page.page_rect = (start, start + size)
    lesson.widget("page_width")


def gui_stage() -> None:
    """The source and the page: side by side, or stacked on a narrow stage; or the page alone"""
    em = hello_imgui.em_size()
    spacing = imgui.get_style().item_spacing
    avail = imgui.get_content_region_avail()
    if app_state.view == "page":
        width = max(18 * em, avail.x * app_state.page_width)
        pos = imgui.get_cursor_screen_pos() + ImVec2((avail.x - width) / 2, 0)
        if app_state.page_width < 0.99:            # a narrow page: its edges, as a device's
            color = imgui.get_color_u32(imgui.Col_.text_disabled)
            imgui.get_window_draw_list().add_rect(pos - ImVec2(3, 3), pos + ImVec2(width, avail.y) + ImVec2(3, 3),
                                                  color, rounding=0.6 * em, thickness=2.0)
        imgui.set_cursor_screen_pos(pos)
        gui_page(ImVec2(width, avail.y))
    elif avail.x < SPLIT_BELOW_EM * em:
        source_height = avail.y * SOURCE_SHARE
        gui_source(ImVec2(avail.x, source_height))
        gui_page(ImVec2(avail.x, avail.y - source_height - spacing.y))
    else:
        source_width = avail.x * SOURCE_SHARE
        gui_source(ImVec2(source_width, avail.y))
        imgui.same_line()
        gui_page(ImVec2(avail.x - source_width - spacing.x, avail.y))


def apply_theme() -> None:
    """The theme of the lesson's cue: the app's, and the editor's palette"""
    if app_state.theme == app_state._theme_applied:
        return
    light = app_state.theme == "light"
    hello_imgui.apply_theme(LIGHT if light else DARK)
    editor.set_palette(ed.TextEditor.get_light_palette() if light else ed.TextEditor.get_dark_palette())
    app_state._theme_applied = app_state.theme


def gui() -> None:
    apply_theme()
    lesson.gui(stage=gui_stage)


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Rich Markdown: a narrated tour"
    params.app_window_params.window_geometry.size = (1200, 900)
    params.ini_disable = True
    params.use_imgui_test_engine = True          # the gestures: the engine's cursor clicks and types
    params.callbacks.show_gui = gui
    immapp.run(params, immapp.AddOnsParams(with_markdown=True, with_latex=True))


if __name__ == "__main__":
    main()
