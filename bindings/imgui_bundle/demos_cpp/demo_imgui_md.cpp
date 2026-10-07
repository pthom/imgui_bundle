// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Markdown: a tour of rich_md. Each section shows its source, ready to copy; the page is a document (a table of
// contents, a search, headings that fold).
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_6.h"
#include "imgui_rich_md/rich_md.h"
#include "immapp/immapp.h"

#include <string>
#include <vector>

// Filled by the OnHeading callback (set when this demo runs standalone: see main())
static std::vector<std::string> gHeadings;
// True when main() enabled the options that the hosted demo (Dear ImGui Bundle explorer) does not set
static bool gStandaloneOptions = false;

std::string exampleMarkdownString()
{
    std::string md = R"md(
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

For an HTML span outside this set, wire `MarkdownCallbacks::OnHtmlSpan`.

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

`MarkdownOptions::autolinks = false` gives the strict CommonMark behavior. A link to a heading of the page,
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
(`RichMd::HasCodeEditor()`). It is written between three backticks, with an optional language:

<pre>
```cpp
int main()
{
    return 0;
}
```
</pre>

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

With `addons.withLatex = true` (`ImmApp::AddOnsParams`), drawn by [MicroTeX](https://github.com/NanoMichael/MicroTeX).

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
line of the error. `RichMd::RenderMermaid(source)` draws one outside of markdown. More diagrams, to edit, in the
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
    App->>+MD: Render(markdown)
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

<pre>
```mermaid
flowchart LR
    A[Markdown] --> B{Mermaid block?}
    B -->|yes| C([Parse]) --> D[Layout] --> E[(ImDrawList)]
    B -->|no| F[Code block]
```
</pre>

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

### Icons, emoji and other fonts

Dear ImGui Bundle merges Font Awesome into the markdown fonts: its icons work in every style, @@ICON_ROCKET@@ regular,
**@@ICON_HEART@@ bold**, *@@ICON_CHECK@@ italic*, `@@ICON_COPY@@ code`, and in the headings of this page.

Any other font can be merged into all the markdown fonts with `fontOptions.mergeFonts`: an emoji font, a CJK font
(Dear ImGui loads its glyphs on demand: a large font costs nothing until it is used), your own icons...

<details>
<summary>Show source</summary>

```cpp
#include "hello_imgui/icons_font_awesome_6.h"
RichMd::Render("Launch " ICON_FA_ROCKET);

RichMd::MarkdownOptions options;
options.fontOptions.mergeFonts = {"fonts/NotoEmoji-Regular.ttf", "fonts/NotoSansCJKjp-Regular.otf"};
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
and widgets can share one document; `RichMd::RenderDocument(id, markdown)` is the one-call form. With
`foldableHeadings`, an arrow folds a heading's section. The demo "Markdown: a document" shows more.

<details>
<summary>Show source</summary>

```cpp
RichMd::DocumentOptions options;
options.foldableHeadings = true;  // an arrow at the left of each heading folds its section
RichMd::BeginDocument("tour", ImVec2(0.f, 0.f), options);
RichMd::Render(markdown);  // as many renders and widgets as you like
RichMd::EndDocument();
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

```cpp
void RenderCsv(const std::string& code)
{
    std::vector<std::vector<std::string>> rows = SplitCsv(code);  // one vector per line
    if (ImGui::BeginTable("csv", (int)rows[0].size(), ImGuiTableFlags_Borders))
    {
        for (const auto& row : rows)
        {
            ImGui::TableNextRow();
            for (const auto& cell : row)
            {
                ImGui::TableNextColumn();
                ImGui::TextUnformatted(cell.c_str());
            }
        }
        ImGui::EndTable();
    }
}

RichMd::RegisterFencedBlockRenderer("csv", RenderCsv);
```

Then in the markdown:
<pre>
```csv
name,score
Alice,10
```
</pre>

</details>

### Wikilinks and hard line breaks

Two options of `MarkdownOptions`, set before the first render:

- **Wikilinks**: `[[target]]` and `[[target|label]]` become links, and a click calls `callbacks.OnWikiLink(target)`:
  navigation between notes, pages of an app... @@WIKILINKS_STATUS@@
- **Hard line breaks**: with `hardSoftBreaks = true`, a newline in the source is a line break (as in GitHub
  comments and chat messages) instead of a space. It applies to the whole text, so it is not enabled here.

A wikilink to [[Home]] and one with a label: [[Notes/todo|my todo list]].

<details>
<summary>Show source</summary>

```cpp
RichMd::MarkdownOptions options;
options.callbacks.OnWikiLink = [](const std::string& target) { printf("go to %s\n", target.c_str()); };
options.hardSoftBreaks = true;   // for chat-like text
ImmApp::AddOnsParams addons;
addons.withMarkdownOptions = options;
ImmApp::Run(runnerParams, addons);
```

```
A wikilink to [[Home]] and one with a label: [[Notes/todo|my todo list]].
```

</details>

### The headings callback

`callbacks.OnHeading(level, text)` is called after each heading is drawn: a table of contents of your own, the
section under the mouse...

@@HEADINGS_STATUS@@

<details>
<summary>Show source</summary>

```cpp
std::vector<std::string> toc;
options.callbacks.OnHeading = [&](int level, const std::string& text) {
    toc.push_back(std::string(2 * (level - 1), ' ') + text);
};
```

</details>

### Rendering and fonts

- `RichMd::Render(text)` removes the common indentation first, so that a markdown string written inside an indented
  function renders as expected (`RenderRaw()` renders as is).
- The markdown fonts load at the first render: `CreateContext()` can be called any time after the ImGui context
  exists (ImmApp makes one for you).
- Each `Render()` call is a fragment with its own id scope: render prose between widgets, the same fragment twice,
  and nothing collides.

### What this build supports

@@SUPPORT_STATUS@@

`RichMd::HasLatex()`, `HasUrlImages()` and `HasCodeEditor()` tell what the library was built with and what the
host provides.
)md";
    return md;
}


static std::vector<std::vector<std::string>> SplitCsv(const std::string& code)
{
    std::vector<std::vector<std::string>> rows;
    size_t lineStart = 0;
    while (lineStart < code.size())
    {
        size_t lineEnd = code.find('\n', lineStart);
        if (lineEnd == std::string::npos)
            lineEnd = code.size();
        std::string line = code.substr(lineStart, lineEnd - lineStart);
        lineStart = lineEnd + 1;
        if (line.empty())
            continue;
        std::vector<std::string> cells;
        size_t cellStart = 0;
        while (true)
        {
            size_t comma = line.find(',', cellStart);
            cells.push_back(line.substr(cellStart, comma == std::string::npos ? std::string::npos : comma - cellStart));
            if (comma == std::string::npos)
                break;
            cellStart = comma + 1;
        }
        rows.push_back(cells);
    }
    return rows;
}

// Renders a ```csv fenced block as a table (see RegisterFencedBlockRenderer below)
static void RenderCsv(const std::string& code)
{
    auto rows = SplitCsv(code);
    if (rows.empty())
        return;
    if (ImGui::BeginTable("csv", (int)rows[0].size(), ImGuiTableFlags_Borders))
    {
        for (const auto& row : rows)
        {
            ImGui::TableNextRow();
            for (const auto& cell : row)
            {
                ImGui::TableNextColumn();
                ImGui::TextUnformatted(cell.c_str());
            }
        }
        ImGui::EndTable();
    }
}

static std::string ReplaceAll(std::string text, const std::string& from, const std::string& to)
{
    for (size_t pos = text.find(from); pos != std::string::npos; pos = text.find(from, pos + to.size()))
        text.replace(pos, from.size(), to);
    return text;
}

static std::string FillDynamicParts(const std::string& markdown, const std::vector<std::string>& headings)
{
    std::string wikilinksStatus, headingsStatus;
    if (gStandaloneOptions)
    {
        wikilinksStatus = "*(Enabled in this run: the wikilink below is clickable, see the console.)*";
        headingsStatus = "This run collects the headings of this page: ";
        for (size_t i = 0; i < headings.size() && i < 6; ++i)
            headingsStatus += (i > 0 ? ", `" : "`") + headings[i].substr(headings[i].find_first_not_of(' ')) + "`";
        if (headings.size() > 6)
            headingsStatus += "...";
    }
    else
    {
        wikilinksStatus = "*(Not enabled in this hosted run: the wikilink below shows as text. "
                          "Run this demo standalone, `demo_imgui_md`, to see it live.)*";
        headingsStatus = "*(Not enabled in this hosted run.)*";
    }
    std::string supportStatus = std::string("This build: LaTeX **") + (RichMd::HasLatex() ? "yes" : "no")
        + "**, URL images **" + (RichMd::HasUrlImages() ? "yes" : "no")
        + "**, code editor **" + (RichMd::HasCodeEditor() ? "yes" : "no") + "**.";
    std::string r = markdown;
    r = ReplaceAll(r, "@@WIKILINKS_STATUS@@", wikilinksStatus);
    r = ReplaceAll(r, "@@HEADINGS_STATUS@@", headingsStatus);
    r = ReplaceAll(r, "@@SUPPORT_STATUS@@", supportStatus);
    r = ReplaceAll(r, "@@ICON_TEXT@@", ICON_FA_FONT);
    r = ReplaceAll(r, "@@ICON_CODE@@", ICON_FA_CODE);
    r = ReplaceAll(r, "@@ICON_EXTENSIONS@@", ICON_FA_PUZZLE_PIECE);
    r = ReplaceAll(r, "@@ICON_DEVELOPERS@@", ICON_FA_GEARS);
    r = ReplaceAll(r, "@@ICON_ROCKET@@", ICON_FA_ROCKET);
    r = ReplaceAll(r, "@@ICON_HEART@@", ICON_FA_HEART);
    r = ReplaceAll(r, "@@ICON_CHECK@@", ICON_FA_CHECK);
    r = ReplaceAll(r, "@@ICON_COPY@@", ICON_FA_COPY);
    return r;
}

void gui_demo_imgui_md()
{
    static bool csvRendererRegistered = false;
    if (!csvRendererRegistered)
    {
        RichMd::RegisterFencedBlockRenderer("csv", RenderCsv);
        csvRendererRegistered = true;
    }
    // The headings rendered during the previous frame are listed in this one
    std::vector<std::string> headingsLastFrame;
    std::swap(headingsLastFrame, gHeadings);
    // The page is a document: a table of contents, a search, and headings that fold
    RichMd::DocumentOptions options;
    options.foldableHeadings = true;
    RichMd::BeginDocument("markdown_tour", ImVec2(0.f, 0.f), options);
    RichMd::Render(FillDynamicParts(exampleMarkdownString(), headingsLastFrame));
    RichMd::EndDocument();
}


// Standalone main(): bypasses the auto-generated main from ibd_add_auto_demo,
// which would only enable withMarkdown. We need withLatex=true (which implies
// withMarkdown=true) so the LaTeX section actually renders.
// When this file is built as part of the demo_imgui_bundle aggregator
// (IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY), this main() is excluded.
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui_demo_imgui_md;
    runnerParams.windowTitle = "Dear ImGui Bundle - Markdown demo";
    runnerParams.windowSize = {1100, 850};

    // Options that must be set before the first render: wikilinks, headings callback
    RichMd::MarkdownOptions options;
    options.callbacks.OnWikiLink = [](const std::string& target) { printf("wikilink clicked: %s\n", target.c_str()); };
    options.callbacks.OnHeading = [](int level, const std::string& text) {
        gHeadings.push_back(std::string(2 * (level - 1), ' ') + text);
    };
    gStandaloneOptions = true;

    ImmApp::AddOnsParams addons;
    addons.withLatex = true;  // implies withMarkdown=true
    addons.withMarkdownOptions = options;

    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
