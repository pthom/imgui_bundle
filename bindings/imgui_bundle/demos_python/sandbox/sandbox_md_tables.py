"""Sandbox for Markdown table rendering."""
from imgui_bundle import immapp, imgui_md


MARKDOWN = r"""

### Test 0 — empty header + various cell content

|          |                                                                  |
|----------|-------------------------------------------------------------------------|
| Emphasis | *italic*, **bold**, ***both***                                          |
| Code     | `inline_code()`                                                         |
| Links    | [Example](https://example.com)                                          |
| Math     | $e^{i\theta} = \cos(\theta) + i \sin(\theta)$                           |
| Image    | ![random image](https://picsum.photos/160/120)                          |


### Test 1 — header highlight + basic rendering

| Name  | Role      | Notes        |
|-------|-----------|--------------|
| Alice | Engineer  | Works remote |
| Bob   | Designer  | In-office    |
| Carol | PM        | Hybrid       |

Check: the header row (Name / Role / Notes) is **bold**; body cells are regular.

### Test 2 — emphasis inside cells

| Label  | Sample         |
|--------|----------------|
| Plain  | regular        |
| Italic | *italic*       |
| Bold   | **bold**       |
| Both   | ***bold-it***  |
| Code   | `inline()`     |

Check: the italic row renders in italic (not forced plain bold). Same for the other styles. Also verify an `*italic*` header cell below renders bold-italic.

| *Italic head* | **Bold head** | `code head` |
|---------------|---------------|-------------|
| a             | b             | c           |

### Test 3 — two tables back-to-back (PushID isolation)

| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |

| X | Y |
|---|---|
| 9 | 8 |
| 7 | 6 |

Check: no ImGui assertion fires; you can drag the column separator of table 2 independently from table 1 (each has its own `PushID` scope).

### Test 4 — column alignment (GFM `:---`, `:---:`, `---:`)

| Left      | Center     | Right     |
|:----------|:----------:|----------:|
| a         | b          | c         |
| long text | long text  | long text long text long text |
| *em*      | **bold**   | `code`    |

Check: column 1 left-aligned (default), column 2 centered, column 3 right-aligned. Emphasis / code in aligned cells should also shift correctly.

### Test 5 — table between other blocks

Some paragraph text above the table.

| Key | Value |
|-----|-------|
| foo | 1     |
| bar | 2    |

Some paragraph text below the table. The gaps above and below should match the spacing between regular paragraphs.

Here is another pararaph.
"""


def gui():
    imgui_md.render_unindented(MARKDOWN)


def main():
    immapp.run(
        gui_function=gui,
        window_title="Markdown table smoke test",
        with_markdown=True,
        with_latex=True,
        window_size=(900, 900),
    )


if __name__ == "__main__":
    main()
