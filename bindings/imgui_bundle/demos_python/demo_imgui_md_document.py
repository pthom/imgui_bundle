# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Markdown: a document with a table of contents and a search

Markdown as a document: a table of contents beside it, links between its sections, and a search (Ctrl+F). Several
renders and a section of widgets (a plot) share them, in one scroll area. The search also finds the text of the code
blocks and of the collapsed sections. The headings fold.
"""
import numpy as np
from imgui_bundle import imgui, implot, rich_md, immapp, hello_imgui

# The paragraphs of the long section: enough text to scroll
PARAGRAPHS = 12

INTRO = r"""
# A document

`with rich_md.document("id"):` (or `rich_md.begin_document()` and `rich_md.end_document()`) frames the renders and the
widgets of a document. They share a scroll area, and a table of contents on the left: its edge can be dragged, and the
arrow at its top hides it.

Inside it, call `rich_md.render()` as many times as you like, and any other widget, as the plot below: they all belong
to the document, with one table of contents and one search (see the code in "The search").

Links to the sections, wherever they are: [the widgets](#a-section-of-widgets), [the collapsed
section](#inside-a-collapsed-section), [the end](#the-end).

The headings fold: the arrow at their left, shown under the mouse, hides their section. The menu of a right click,
and the "..." menu at the top of the table of contents, fold or unfold them all.

## Headings and anchors

Each heading has a *slug*, made from its text as GitHub does: `## Headings and anchors` is `#headings-and-anchors`. A
link to it scrolls the document there, also when the heading is in another render of the document.

A repeated title gets a number: the second "Notes" below is `#notes-1`.

## Notes

The first section named "Notes".

## Collapsed sections

<details>
<summary>A collapsed section</summary>

### Inside a collapsed section

A heading hidden in a collapsed section is listed in the table of contents, dimmed. A click on it, or a link to it,
opens the section.

</details>
"""

SECOND_RENDER = r"""
## Notes

The second section named "Notes", in the second render of the document: its slug is `#notes-1`.

## The search

Ctrl+F (Cmd+F on macOS) opens the find bar. The search also finds the text of the collapsed sections (a jump to one of
their matches opens them), and of the code blocks:

```python
options = rich_md.DocumentOptions()
options.foldable_headings = True  # an arrow at the left of each heading folds its section
with rich_md.document("document", options=options):
    rich_md.render(intro)  # markdown: as many renders as you like

    # Widgets, under a heading of the document (False: its section is folded)
    if rich_md.document_heading(2, "A section of widgets"):
        _, frequency = imgui.slider_float("Frequency", frequency, 0.5, 5.0)
        if implot.begin_plot("##wave"):
            implot.plot_line("sin(f x)", xs, ys)
            implot.end_plot()

    rich_md.render(more_markdown)  # the same document: one table of contents, one search
```

## Long text

The table of contents marks the section at the top of the view, and follows it as the document scrolls.

"""


def _long_text() -> str:
    md = SECOND_RENDER
    for i in range(1, PARAGRAPHS + 1):
        md += (
            f"Paragraph {i}: some text to scroll through, long enough to wrap on a narrow window, so that the document "
            "has a length worth a table of contents.\n\n"
        )
    md += "## The end\n\nBack to [the top](#a-document).\n"
    return md


LONG_TEXT = _long_text()
_frequency = 2.0


def _widgets_section() -> None:
    """A section made of widgets: a slider and the plot it drives"""
    global _frequency
    _, _frequency = imgui.slider_float("Frequency", _frequency, 0.5, 5.0)
    xs = np.linspace(0.0, 10.0, 400)
    ys = np.sin(_frequency * xs)
    if implot.begin_plot("##wave", (-1, hello_imgui.em_size(12))):
        implot.plot_line("sin(f x)", xs, ys)
        implot.end_plot()


def gui() -> None:
    options = rich_md.DocumentOptions()
    options.foldable_headings = True  # an arrow at the left of each heading folds its section
    with rich_md.document("document", options=options):
        rich_md.render(INTRO)
        # document_heading() draws its title as a markdown heading, and gives it a slug: the widgets below are a
        # section. It returns False when the section is folded: its widgets are skipped.
        if rich_md.document_heading(2, "A section of widgets"):
            _widgets_section()
        rich_md.render(LONG_TEXT)


def main() -> None:
    immapp.run(gui, window_title="A markdown document", window_size=(1000, 800), with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
