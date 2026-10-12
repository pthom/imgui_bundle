# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Markdown editor: the source and its live preview

A markdown editor in a few lines: ImGuiColorTextEdit edits the source, rich_md previews it as you type. On a narrow
screen (a phone), two tabs show one of them at a time.
"""
from imgui_bundle import imgui, imgui_color_text_edit as ed, rich_md, immapp, hello_imgui, ImVec2

TextEditor = ed.TextEditor

# Below this width (in em), one panel at a time
NARROW_WIDTH_EM = 50.0

SAMPLE = r"""# A markdown editor

Edit this text: the preview follows as you type.

The editor is [ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit), with its markdown colors. The preview is [rich_md](https://github.com/pthom/imgui_rich_md). Both are Dear ImGui widgets: no browser, no HTML engine.

## Text

*Emphasis*, **bold**, ~~strikethrough~~, `inline code`, and [links](https://github.com/pthom/imgui_bundle).

- [x] write a list
- [ ] add a heading: a line that starts with `## `
- [ ] change the table below

> [!TIP]
> A quote that starts with `[!TIP]`, `[!NOTE]` or `[!WARNING]` becomes a callout.

## A table

| Panel   | Library            | Role    |
|---------|--------------------|---------|
| Source  | ImGuiColorTextEdit | edits   |
| Preview | rich_md            | renders |

## Code

The two lines that join them:

```python
self.editor.set_change_callback(self.on_change)
rich_md.render_document("##preview", self.markdown, size)
```

## Math

The roots of $ax^2 + bx + c = 0$ are

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
"""


def theme_palette() -> TextEditor.Palette:
    """The editor's palette follows the app's theme: light on a light background"""
    bg = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    light = 0.299 * bg.x + 0.587 * bg.y + 0.114 * bg.z > 0.5
    return TextEditor.get_light_palette() if light else TextEditor.get_dark_palette()


class MarkdownEditor:
    def __init__(self) -> None:
        self.editor = TextEditor()
        self.markdown = SAMPLE  # what the preview shows: a copy of the editor's text
        self.editor.set_text(self.markdown)
        self.editor.set_language(TextEditor.Language.markdown())
        self.editor.set_word_wrap_enabled(True)
        self.editor.set_show_whitespaces_enabled(False)  # prose, not code: no dots for the spaces
        # Called after each change: the preview reads the new text (get_text() makes a copy: not at every frame)
        self.editor.set_change_callback(self.on_change)

    def on_change(self) -> None:
        self.markdown = self.editor.get_text()

    def source(self, size: ImVec2) -> None:
        self.editor.set_palette(theme_palette())
        code_font = rich_md.get_code_font()  # a monospaced font
        imgui.push_font(code_font.font, code_font.size)
        self.editor.render("##source", size)
        imgui.pop_font()

    def preview(self, size: ImVec2) -> None:
        rich_md.render_document("##preview", self.markdown, size)


_md: MarkdownEditor | None = None


def gui() -> None:
    global _md
    if _md is None:
        _md = MarkdownEditor()
    avail = imgui.get_content_region_avail()
    if avail.x < hello_imgui.em_size(NARROW_WIDTH_EM):
        if imgui.begin_tab_bar("##panels"):
            if imgui.begin_tab_item("Source")[0]:
                _md.source(imgui.get_content_region_avail())
                imgui.end_tab_item()
            if imgui.begin_tab_item("Preview")[0]:
                _md.preview(imgui.get_content_region_avail())
                imgui.end_tab_item()
            imgui.end_tab_bar()
        return
    gap = imgui.get_style().item_spacing.x
    half = ImVec2((avail.x - gap) * 0.5, avail.y)
    _md.source(half)
    imgui.same_line(0.0, gap)
    _md.preview(half)


def main() -> None:
    # with_latex: markdown, with its math formulas
    immapp.run(gui, window_title="Markdown editor", window_size=(1200, 800), with_latex=True)


if __name__ == "__main__":
    main()
