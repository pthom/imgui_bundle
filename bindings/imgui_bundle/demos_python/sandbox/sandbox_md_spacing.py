"""Sandbox: visual diagnosis of inter-block spacing in imgui_md.

Lays out every block-to-block transition we care about so the gaps can
be eyeballed side-by-side.
  A. content right after <summary>
  B. block-to-block transitions (P/UL/OL/quote/code/table/HR)
  C. header levels H1..H5
  D. nested lists and adjacent lists
"""

from imgui_bundle import immapp, imgui, imgui_md


SECTIONS = {
    "A. content right after <summary>": r"""
<details open>
<summary>Open summary, then a paragraph</summary>

Paragraph immediately after the summary closes. Note the gap above.

</details>

<details open>
<summary>Open summary, then a UL</summary>

- list item right after summary
- second item

</details>

<details open>
<summary>Open summary, then a code block</summary>

```python
print("hello")
```

</details>

<details open>
<summary>Open summary, then a quote</summary>

> A blockquote right after the summary.

</details>
""",

    "B. block-to-block transitions": r"""
A short paragraph.

Another paragraph. Gap should equal P->P baseline.

* bullet 1
* bullet 2
* bullet 3

Paragraph right after a UL. **Gap above** should equal "UL -> P".

Another paragraph. **Gap below** is "P -> UL" — currently larger than P->P.

* second list, item 1
* second list, item 2

A paragraph. Then an OL:

1. first
2. second

Paragraph after OL.

1. another OL
2. another item

> A blockquote.

Paragraph after quote.

```
fenced code block
spans two lines
```

Paragraph after code.

| col A | col B |
|-------|-------|
| 1     | 2     |
| 3     | 4     |

Paragraph after table.

---

Paragraph after horizontal rule.
""",

    "C. header levels h1..h5": r"""
Paragraph before H1.

# H1 heading

Paragraph after H1.

## H2 heading

Paragraph after H2.

### H3 heading

Paragraph after H3.

#### H4 heading

Paragraph after H4.

##### H5 heading

Paragraph after H5.

Paragraph between H5 and H1.

# Another H1

End paragraph.
""",

    "D. nested lists and adjacent lists": r"""
Intro paragraph.

* outer 1
    * nested 1
    * nested 2
* outer 2

Paragraph between two ULs.

- second UL item 1
- second UL item 2

* third UL right after (no blank-line paragraph between)
* third UL item 2

1. ordered after unordered
2. ordered item 2

End paragraph.
""",
}


def gui():
    for title, md in SECTIONS.items():
        if imgui.collapsing_header(title, imgui.TreeNodeFlags_.default_open.value):
            imgui_md.render(md)
            imgui.dummy(imgui.ImVec2(0, 12))


def main():
    immapp.run(gui, with_markdown=True, window_size=(900, 1000), window_title="md gap diagnosis")


if __name__ == "__main__":
    main()
