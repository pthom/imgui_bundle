# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui_md, immapp


def example_markdown_string() -> str:
    markdown = r"""
# Dear ImGui Bundle — Markdown tour

`imgui_md` renders markdown directly inside an ImGui window — no browser,
no HTML, no external renderer.

> [!TIP]
> Use this demo as a reference when writing markdown in your own application.
> Expand the *"Show source"* sections to get copyable snippets.

---

# Basics

<details open>
<summary>Text and typography</summary>

All the usual inline styling works:

- *emphasis*, **bold**, ***both***, ~~strikethrough~~, <u>underlined</u>
- <mark>highlighted passages</mark> for things that need to stand out
- Inline `code` — handy for tokens, flags, and short snippets

HTML-like spans render natively too, no callbacks needed:

- Keyboard shortcuts read naturally: press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, or <kbd>Cmd</kbd>+<kbd>K</kbd> on a Mac
- Chemistry: H<sub>2</sub>O, CO<sub>2</sub>, C<sub>8</sub>H<sub>10</sub>N<sub>4</sub>O<sub>2</sub>
- Exponents: x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>

For any HTML span not in the default set, wire `MarkdownCallbacks.on_html_span`.

<details>
<summary>Show source</summary>

```
*emphasis*, **bold**, ***both***, ~~strikethrough~~, <u>underlined</u>
<mark>highlighted</mark>, inline `code`
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>
H<sub>2</sub>O, x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>
```

</details>
</details>
<details>
<summary>Structure: headers, lists, quotes, rules</summary>

Markdown handles the bones of a document out of the box.

**Headers** go from `#` (H1) to `###` (H3); all render as ImGui-styled headings.

<details>
<summary>Test Headers</summary>

# Title 1

A quick intro in normal text.

## Title 2

### Title 3

#### Title 4

##### Title 5

</details>

**Ordered and unordered lists**, including nesting:

1. First
2. Second
    - Nested bullet
    - Another one
        1. Deeper still
3. Third

**Blockquotes** for callouts that aren't admonitions:

> Markdown inside an ImGui window — the best of both worlds.

**Horizontal rules** to separate sections (three dashes on a line):

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
</details>
<details>
<summary>Links and autolinks</summary>

Explicit markdown link syntax: [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle).

Autolinks turn bare URLs, `www.` hosts, and email addresses into clickable
links automatically:

- https://github.com/pthom/imgui_bundle
- www.dearimgui.org
- Contact: pthomet@gmail.com

Disable with `MarkdownOptions.autolinks = False` for strict CommonMark
behavior.

<details>
<summary>Show source</summary>

```
[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle)

https://github.com/pthom/imgui_bundle
www.dearimgui.org
Contact: pthomet@gmail.com
```

</details>
</details>
<details>
<summary>Images</summary>

Images load from local assets with a relative path:

![World](images/world.png)

Remote URLs load asynchronously — a spinner is shown while downloading:

![Photo](https://picsum.photos/id/1018/300/200)

Use `<img>` when you need to control the size:

<img src="https://picsum.photos/id/237/300/200" width="100">

<details>
<summary>Show source</summary>

```
![World](images/world.png)
![Photo](https://picsum.photos/id/1018/300/200)
<img src="https://picsum.photos/id/237/300/200" width="100">
```

</details>
</details>

# Tables and code blocks


<details>
<summary>Code blocks</summary>

**Inline snippets**

Inline snippets are rendered like code inside a regular paragraph, like this: `result = 37`.

They are written like this:
<pre>
`result = 37`
</pre>

**Code blocks**

Code blocks preserve layout and use a monospaced font.

A small Python example:

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

Code blocks are delimited by three backticks, plus an optional language. See example below:

<pre>
```python
int main()
{
    return 0;
}
```
</pre>

</details>
<details>
<summary>Tables</summary>

Columns are resizable at runtime — grab a column border and drag. First-row
widths drive column layout, so use `&nbsp;` in that row to enforce a
minimum width where needed.

Column alignment is controlled by colons in the separator row:

```
:---    left
---:    right
:---:   centre
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
</details>

# Useful extensions

<details>
<summary>GitHub-style admonitions</summary>

Blockquotes that start with `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`
or `[!CAUTION]` render as coloured callouts — great for in-app help and
onboarding:

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
</details>
<details>
<summary>Task lists</summary>

GitHub-style task lists render as checkbox glyphs. Handy for changelogs
and roadmap-style content embedded inside your app:

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
</details>
<details>
<summary>Math with LaTeX</summary>

Requires `immapp.run(..., with_latex=True)`. Rendering is powered by
[MicroTeX](https://github.com/NanoMichael/MicroTeX).

**Inline math** uses single dollars: Euler's identity $e^{i\pi} + 1 = 0$
is a consequence of the more general $e^{i\theta} = \cos\theta + i\sin\theta$.

**Display math** uses double dollars on their own line. The quadratic
formula:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

Sums, integrals and matrices all work:

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
</details>
<details>
<summary>Preformatted text with the pre tag</summary>

`<pre>` renders a block of monospaced text **without** the styling of a
fenced code block — no background frame, no syntax coloring. Use it
for ASCII layouts, aligned data, and anything where "monospace" is
what you want but "this is source code" is not the right message:

<pre>
Metric        Aligned        Value
--------      ---------      -----
Ping          right           12ms
Throughput    right          42MB/s
Latency       right           87us
</pre>

Same content in a fenced code block, for comparison:

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
</details>

---

# Under the hood: how this page is built

<details>
<summary>It's collapsibles all the way down</summary>

Every section above — and every "Show source" inside them — is a
`<details>` block. The tags render as `CollapsingHeader` widgets,
and blank lines around the opening / closing tags let the inner
content be parsed as regular markdown:

<details>
<summary>A nested collapsible</summary>

Hidden until you click. The content is regular markdown.

- One
- Two

<details>
<summary>Going deeper</summary>

Another level. Indentation doesn't matter; what matters is the blank
lines around the tags.

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
</details>

"""
    return markdown


def demo_gui():
    # from imgui_bundle import hello_imgui
    # hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.white_is_white)
    s = example_markdown_string()
    imgui_md.render(s)
    # Note: you may also use:
    #   imgui_md.render_unindented(s)
    # (it will remove the main indentation of the Markdown string before rendering it,
    # which is useful when the string is defined inside a function with indentation)

def main():
    immapp.run(demo_gui, with_latex=True, window_size=(800, 800))


if __name__ == "__main__":
    main()
