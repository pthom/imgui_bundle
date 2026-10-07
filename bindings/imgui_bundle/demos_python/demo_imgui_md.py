# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Markdown: a tour of rich_md

Markdown rendered in an ImGui window: styled text, tables, code, images, math, diagrams, admonitions and more. Each
section shows its source, ready to copy. The page is a document: a table of contents, a search, headings that fold.
"""
from imgui_bundle import imgui, rich_md, immapp
from imgui_bundle.immapp import icons_fontawesome_6 as fa

# Filled by the on_heading callback (set when this demo runs standalone: see main())
_headings: list[str] = []
# True when main() enabled the options that the hosted demo (Dear ImGui Bundle explorer) does not set
_standalone_options = False


def example_markdown_string() -> str:
    markdown = r"""
# Markdown in Dear ImGui

`rich_md` draws markdown directly in an ImGui window: no browser, no HTML engine, no external renderer. This page is a
tour of what it renders, each feature with its source.

> [!TIP]
> The table of contents on the left lists the sections, and Ctrl+F (Cmd+F on macOS) searches the page. The arrow at
> the left of a heading (under the mouse) folds its section; the "..." menu of the table of contents folds or unfolds
> them all. Open *Show source* for a snippet to copy.

## @@ICON_TEXT@@ Text

### Styles

All the usual inline styling works:

- *emphasis*, **bold**, ***both***, ~~strikethrough~~, <u>underlined</u>
- <mark>highlighted passages</mark>, for what must stand out
- inline `code`, for tokens, flags and short snippets

HTML-like spans render natively too, with no callback:

- keyboard shortcuts: press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, or <kbd>Cmd</kbd>+<kbd>K</kbd> on a Mac
- chemistry: H<sub>2</sub>O, CO<sub>2</sub>, C<sub>8</sub>H<sub>10</sub>N<sub>4</sub>O<sub>2</sub>
- exponents: x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>

For an HTML span outside this set, wire `MarkdownCallbacks.on_html_span`.

<details>
<summary>Show source</summary>

```
*emphasis*, **bold**, ***both***, ~~strikethrough~~, <u>underlined</u>
<mark>highlighted</mark>, inline `code`
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>
H<sub>2</sub>O, x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>
```

</details>

### Headings, lists and quotes

The bones of a document. **Headings** go from `#` to `######`; this page uses three levels, and the sample below
shows five:

<details>
<summary>The heading levels</summary>

# Title 1

A quick intro in normal text.

## Title 2

### Title 3

#### Title 4

##### Title 5

</details>

**Ordered and unordered lists**, nested:

1. First
2. Second
    - Nested bullet
    - Another one
        1. Deeper still
3. Third

**Blockquotes**, for callouts that are not admonitions:

> Markdown inside an ImGui window: the best of both worlds.

**Horizontal rules**, three dashes on a line:

---

<details>
<summary>Show source</summary>

```
# H1
## H2
### H3

1. First
2. Second
    - Nested bullet
        1. Deeper still

> A blockquote.

---
```

</details>

### Links

The markdown syntax: [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle).

Autolinks turn bare URLs, `www.` hosts and email addresses into links:

- https://github.com/pthom/imgui_bundle
- www.dearimgui.org
- Contact: pthomet@gmail.com

`MarkdownOptions.autolinks = False` gives the strict CommonMark behavior. A link to a heading of the page,
`[text](#slug)`, scrolls there: [the tables](#tables).

<details>
<summary>Show source</summary>

```
[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle)

https://github.com/pthom/imgui_bundle
www.dearimgui.org
Contact: pthomet@gmail.com

[the tables](#tables)
```

</details>

### Images

From the assets, with a relative path:

![World](images/world.png)

From a URL, downloaded in the background (a spinner shows meanwhile):

![Photo](https://picsum.photos/id/1018/300/200)

`<img>` sets the size:

<img src="https://picsum.photos/id/237/300/200" width="100">

<details>
<summary>Show source</summary>

```
![World](images/world.png)
![Photo](https://picsum.photos/id/1018/300/200)
<img src="https://picsum.photos/id/237/300/200" width="100">
```

</details>

## @@ICON_CODE@@ Code and tables

### Code blocks

Inline code sits in a paragraph, like `result = 37`; it is written between backticks:
<pre>
`result = 37`
</pre>

A code block keeps its layout, in a monospaced font. A small Python example:

```python
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Hello, World!")

immapp.run(gui, window_title="My App")
```

And its C++ equivalent:

```cpp
#include "imgui.h"
#include "immapp/immapp.h"

void gui() {
    ImGui::Text("Hello, World!");
}

int main() {
    ImmApp::Run(gui);
}
```

A code block has a copy button, and syntax highlighting when the library is built with its code editor
(`rich_md.has_code_editor()`). It is written between three backticks, with an optional language:

````markdown
```python
def main():
    return 0
```
````

A block that shows a fence, as this one, is written between four backticks (or tildes): a fence
closes only on as many backticks as it opened with, or more.

<details>
<summary>Show source</summary>

`````markdown
````markdown
```python
def main():
    return 0
```
````
`````

</details>

### Tables

Columns can be resized: drag a column's border. The widths of the first row drive the layout: `&nbsp;` there
enforces a minimum width. Colons in the separator row align the columns:

```
:---    left
---:    right
:---:   center
```

| Continent      |   Population  | Countries |
|----------------|--------------:|:---------:|
| Africa         | 1300 million  |    54     |
| Asia           | 4500 million  |    48     |
| Europe         |  743 million  |    44     |
| North America  |  579 million  |    23     |
| Oceania        |   41 million  |    14     |
| South America  |  422 million  |    12     |
| Antarctica     |           0   |     0     |

<details>
<summary>Show source</summary>

```
| Continent      |   Population  | Countries |
|----------------|--------------:|:---------:|
| Africa         | 1300 million  |    54     |
| Asia           | 4500 million  |    48     |
```

</details>

## @@ICON_EXTENSIONS@@ Extensions

### Admonitions

A blockquote that starts with `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]` or `[!CAUTION]` is a colored callout,
as on GitHub: in-app help, onboarding...

> [!NOTE]
> A note provides useful context that a reader should know.

> [!TIP]
> A small hint that saves the reader time.

> [!IMPORTANT]
> Required information to complete a task.

> [!WARNING]
> Heads up: something can subtly go wrong here.

> [!CAUTION]
> A negative outcome is likely without care.

<details>
<summary>Show source</summary>

```
> [!NOTE]
> A note provides useful context that a reader should know.

> [!WARNING]
> Heads up: something can subtly go wrong here.
```

</details>

### Task lists

GitHub's task lists, as check boxes: a changelog, a roadmap...

- [x] Design the UI
- [x] Wire up the data layer
- [x] Write the onboarding flow
- [ ] Polish documentation
- [ ] Record a demo video
- [ ] Ship it

<details>
<summary>Show source</summary>

```
- [x] Done item
- [ ] Pending item
```

</details>

### Math with LaTeX

With `immapp.run(..., with_latex=True)`, drawn by [MicroTeX](https://github.com/NanoMichael/MicroTeX).

**Inline math**, between single dollars: Euler's identity $e^{i\pi} + 1 = 0$ is a consequence of the more general
$e^{i\theta} = \cos\theta + i\sin\theta$.

**Display math**, between double dollars on their own lines. The quadratic formula:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

Sums, integrals and matrices:

$$
\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}
\qquad
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
\qquad
\sum_{i=0}^{n} i = \frac{n(n+1)}{2}
$$

<details>
<summary>Show source</summary>

```
Inline: $e^{i\pi} + 1 = 0$

Display:
$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

</details>

### Mermaid diagrams

A ` ```mermaid ` block is drawn natively, with `ImDrawList` and the colors of the ImGui style (no web view, no
JavaScript): flowcharts, sequence diagrams and class diagrams. A diagram that cannot be parsed shows as code, with the
line of the error. `rich_md.render_mermaid(source)` draws one outside of markdown. More diagrams, to edit, in the
[Mermaid tour](https://pthom.github.io/imgui_rich_md/mermaid.html).

```mermaid
flowchart LR
    A[Markdown] --> B{Mermaid block?}
    B -->|yes| C([Parse]) --> D[Layout] --> E[(ImDrawList)]
    B -->|no| F[Code block]
```

```mermaid
sequenceDiagram
    participant App
    participant MD as rich_md
    App->>+MD: render(markdown)
    MD->>MD: parse, lay out
    MD-->>-App: drawn
```

```mermaid
classDiagram
    class Diagram {
        +kind
        +error
    }
    class Graph {
        +nodes
        +edges
    }
    class Sequence {
        +participants
        +rows
    }
    Diagram *-- Graph
    Diagram *-- Sequence
```

<details>
<summary>Show source</summary>

````markdown
```mermaid
flowchart LR
    A[Markdown] --> B{Mermaid block?}
    B -->|yes| C([Parse]) --> D[Layout] --> E[(ImDrawList)]
    B -->|no| F[Code block]
```
````

</details>

### Centered blocks

`<center>` centers a block. As with `<div>` and `<details>`, put the tags on their own lines, with blank lines around
them, so that the content inside is parsed as markdown:

<center>

**Centered**, with *markdown* inside: $E = mc^2$

</center>

<details>
<summary>Show source</summary>

```
<center>

**Centered**, with *markdown* inside: $E = mc^2$

</center>
```

</details>

### Preformatted text

`<pre>` renders monospaced text **without** the styling of a code block: no frame, no syntax coloring. For ASCII
layouts and aligned data, where "monospace" is right but "source code" is not:

<pre>
Metric        Aligned        Value
--------      ---------      -----
Ping          right           12ms
Throughput    right          42MB/s
Latency       right           87us
</pre>

The same in a code block, for comparison:

```
Metric        Aligned        Value
--------      ---------      -----
Ping          right           12ms
```

<details>
<summary>Show source</summary>

```
<pre>
First line
    Indented line
Last line
</pre>
```

</details>

### Icons, emoji and fonts

Dear ImGui Bundle merges Font Awesome into the markdown fonts: its icons work in every style, @@ICON_ROCKET@@ regular,
**@@ICON_HEART@@ bold**, *@@ICON_CHECK@@ italic*, `@@ICON_COPY@@ code`, and in the headings of this page.

Any other font can be merged into all the markdown fonts with `font_options.merge_fonts`: an emoji font, a CJK font
(Dear ImGui loads its glyphs on demand: a large font costs nothing until it is used), your own icons...

<details>
<summary>Show source</summary>

```python
from imgui_bundle.immapp import icons_fontawesome_6 as fa
rich_md.render("Launch " + fa.ICON_FA_ROCKET)

options = rich_md.MarkdownOptions()
options.font_options.merge_fonts = ["fonts/NotoEmoji-Regular.ttf", "fonts/NotoSansCJKjp-Regular.otf"]
```

</details>

### Collapsible sections

`<details>` and `<summary>` draw a collapsing header, as the *Show source* blocks of this page. Blank lines around
the tags let the content inside be parsed as markdown, and they nest:

<details>
<summary>A collapsible section</summary>

Hidden until you click. The content is regular markdown.

- One
- Two

<details>
<summary>Going deeper</summary>

Another level. The indentation does not matter: the blank lines around the tags do.

</details>
</details>

<details>
<summary>Show source</summary>

```
<details>
<summary>Click me</summary>

Hidden content (regular markdown here).

</details>
```

</details>

## @@ICON_DEVELOPERS@@ For developers

### Documents and folds

This page is a document: a scroll area of its own, a table of contents beside it, links `[text](#slug)` between its
sections, and a search that also finds the text of the code blocks and of the collapsed sections. Several renders
and widgets can share one document; `rich_md.render_document(id, markdown)` is the one-call form. With
`foldable_headings`, an arrow folds a heading's section. The demo "Markdown: a document" shows more.

<details>
<summary>Show source</summary>

```python
options = rich_md.DocumentOptions()
options.foldable_headings = True  # an arrow at the left of each heading folds its section
with rich_md.document("tour", options=options):
    rich_md.render(markdown)  # as many renders and widgets as you like
```

</details>

### Custom fenced blocks

A fenced block whose language you registered is drawn by your own function instead of the code renderer: tables from
`csv`, live widgets... This demo registers `csv`:

```csv
name,score,rank
Alice,10,1
Bob,7,2
Carol,4,3
```

<details>
<summary>Show source</summary>

```python
def render_csv(code: str) -> None:
    rows = [row.split(",") for row in code.strip().splitlines()]
    if imgui.begin_table("csv", len(rows[0]), imgui.TableFlags_.borders.value):
        for row in rows:
            imgui.table_next_row()
            for cell in row:
                imgui.table_next_column()
                imgui.text(cell)
        imgui.end_table()

rich_md.register_fenced_block_renderer("csv", render_csv)
```

Then in the markdown:
````markdown
```csv
name,score
Alice,10
```
````

</details>

### Wikilinks and line breaks

Two options of `MarkdownOptions`, set before the first render:

- **Wikilinks**: `[[target]]` and `[[target|label]]` become links, and a click calls `callbacks.on_wiki_link(target)`:
  navigation between notes, pages of an app... @@WIKILINKS_STATUS@@
- **Hard line breaks**: with `hard_soft_breaks = True`, a newline in the source is a line break (as in GitHub
  comments and chat messages) instead of a space. It applies to the whole text, so it is not enabled here.

A wikilink to [[Home]] and one with a label: [[Notes/todo|my todo list]].

<details>
<summary>Show source</summary>

```python
options = rich_md.MarkdownOptions()
options.callbacks.on_wiki_link = lambda target: print("go to", target)
options.hard_soft_breaks = True   # for chat-like text
immapp.run(gui, with_markdown_options=options)
```

```
A wikilink to [[Home]] and one with a label: [[Notes/todo|my todo list]].
```

</details>

### The headings callback

`callbacks.on_heading(level, text)` is called after each heading is drawn: a table of contents of your own, the
section under the mouse...

@@HEADINGS_STATUS@@

<details>
<summary>Show source</summary>

```python
toc: list[str] = []
options.callbacks.on_heading = lambda level, text: toc.append("  " * (level - 1) + text)
```

</details>

### Rendering and fonts

- `rich_md.render(text)` removes the common indentation first, so that a markdown string written inside an indented
  function renders as expected (`render_raw` renders as is).
- The markdown fonts load at the first render: `create_context()` can be called any time after the ImGui context
  exists (ImmApp makes one for you).
- Each `render()` call is a fragment with its own id scope: render prose between widgets, the same fragment twice,
  and nothing collides.

### What this build supports

@@SUPPORT_STATUS@@

`rich_md.has_latex()`, `has_url_images()` and `has_code_editor()` tell what the library was built with and what the
host provides.
"""
    return markdown


def _render_csv(code: str) -> None:
    """Renders a ```csv fenced block as a table (see register_fenced_block_renderer below)."""
    rows = [row.split(",") for row in code.strip().splitlines()]
    if imgui.begin_table("csv", len(rows[0]), imgui.TableFlags_.borders.value):
        for row in rows:
            imgui.table_next_row()
            for cell in row:
                imgui.table_next_column()
                imgui.text(cell)
        imgui.end_table()


def _fill_dynamic_parts(markdown: str, headings: list[str]) -> str:
    if _standalone_options:
        wikilinks_status = "*(Enabled in this run: the wikilink below is clickable, see the console.)*"
        headings_status = "This run collects the headings of this page: " + (
            ", ".join(f"`{h.strip()}`" for h in headings[:6]) + ("..." if len(headings) > 6 else "")
        )
    else:
        wikilinks_status = (
            "*(Not enabled in this hosted run: the wikilink below shows as text. "
            "Run this demo standalone, `python demo_imgui_md.py`, to see it live.)*"
        )
        headings_status = "*(Not enabled in this hosted run.)*"
    support_status = "This build: LaTeX **{}**, URL images **{}**, code editor **{}**.".format(
        "yes" if rich_md.has_latex() else "no",
        "yes" if rich_md.has_url_images() else "no",
        "yes" if rich_md.has_code_editor() else "no",
    )
    return (
        markdown.replace("@@WIKILINKS_STATUS@@", wikilinks_status)
        .replace("@@HEADINGS_STATUS@@", headings_status)
        .replace("@@SUPPORT_STATUS@@", support_status)
        .replace("@@ICON_TEXT@@", fa.ICON_FA_FONT)
        .replace("@@ICON_CODE@@", fa.ICON_FA_CODE)
        .replace("@@ICON_EXTENSIONS@@", fa.ICON_FA_PUZZLE_PIECE)
        .replace("@@ICON_DEVELOPERS@@", fa.ICON_FA_GEARS)
        .replace("@@ICON_ROCKET@@", fa.ICON_FA_ROCKET)
        .replace("@@ICON_HEART@@", fa.ICON_FA_HEART)
        .replace("@@ICON_CHECK@@", fa.ICON_FA_CHECK)
        .replace("@@ICON_COPY@@", fa.ICON_FA_COPY)
    )


_csv_renderer_registered = False


def gui():
    global _csv_renderer_registered
    if not _csv_renderer_registered:
        rich_md.register_fenced_block_renderer("csv", _render_csv)
        _csv_renderer_registered = True
    # from imgui_bundle import hello_imgui
    # hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.white_is_white)
    # The headings rendered during the previous frame are listed in this one
    headings_last_frame = list(_headings)
    _headings.clear()
    # The page is a document: a table of contents, a search, and headings that fold
    options = rich_md.DocumentOptions()
    options.foldable_headings = True
    with rich_md.document("markdown_tour", options=options):
        rich_md.render(_fill_dynamic_parts(example_markdown_string(), headings_last_frame))


def main():
    global _standalone_options
    # Options that must be set before the first render: wikilinks, headings callback
    options = rich_md.MarkdownOptions()
    options.callbacks.on_wiki_link = lambda target: print("wikilink clicked:", target)
    options.callbacks.on_heading = lambda level, text: _headings.append("  " * (level - 1) + text)
    _standalone_options = True
    immapp.run(gui, with_latex=True, with_markdown_options=options, window_size=(1100, 850))


if __name__ == "__main__":
    main()
