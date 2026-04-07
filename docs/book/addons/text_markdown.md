# Text Editing & Markdown

Dear ImGui Bundle includes libraries for syntax-highlighted text editing and markdown rendering.

## imgui_md - Markdown Rendering

### Introduction

[imgui_md](https://github.com/mekhontsev/imgui_md) renders markdown content directly in your ImGui interface. Supports headers, bold, italic, links, code blocks, lists, and more.

**Quick example:**

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui_md, immapp

def gui():
    imgui_md.render("""
# Hello Markdown

This is **bold** and this is *italic*.

- List item 1
- List item 2
    """)

immapp.run(gui, with_markdown=True)
```

You may also use `imgui_md.render_unindented(s)` – it removes the leading indentation of the markdown string before rendering, which is useful when the string is defined inside a function with indentation.
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

void gui() {
    ImGuiMd::Render(R"(
# Hello Markdown

This is **bold** and this is *italic*.

- List item 1
- List item 2
    )");
}

int main() {
    ImmApp::RunWithMarkdown(gui);
    return 0;
}
```
:::

::::

:::{tip}
Enable markdown by passing `with_markdown=True` to `immapp.run()` (Python) or use `ImmApp::RunWithMarkdown()` (C++).
:::

### Images

imgui_md supports images from local assets and from URLs.

**Standard markdown images:**
```markdown
![local image](images/world.png)
![online image](https://example.com/photo.jpg)
```

**HTML img tags with explicit size:**
```html
<img src="https://example.com/photo.jpg" width="200">
<img src="images/logo.png" width="100" height="50">
```

:::{note}
**Python:** URL images are downloaded asynchronously (a loading spinner is shown while downloading). This works automatically when using `immapp.run(with_markdown=True)`. The download callback can be customized via `MarkdownCallbacks.on_download_data`.

**C++ (Emscripten):** URL images are downloaded automatically using `emscripten_fetch` (non-blocking, async).

**C++ (desktop):** URL images are not downloaded by default. To enable them, set `MarkdownCallbacks::OnDownloadData` to a function that downloads data from a URL (e.g. using libcurl). The callback should return a `MarkdownDownloadResult` with `Ready`/`Downloading`/`Failed` status.
:::

### LaTeX math

imgui_md can render inline and display LaTeX math via the bundled [imgui_microtex](https://github.com/pthom/MicroTeX) library — a thin wrapper  around [MicroTeX](https://github.com/NanoMichael/MicroTeX).

**Quick example:**

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui_md, immapp

def gui():
    imgui_md.render_unindented(r"""
# Math in markdown

Inline math sits on the text baseline: $E = mc^2$, $\sqrt{a^2 + b^2}$,
$\sum_{i=0}^{n} i = \frac{n(n+1)}{2}$.

Display math is centered on its own line:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

Sums, integrals, matrices all work:

$$
\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}
\qquad
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
\qquad
e^{i\pi} + 1 = 0
$$
    """)

immapp.run(gui, with_latex=True)   # implies with_markdown=True
```

Note the **raw string** (`r"""..."""`): without it, Python would interpret sequences like `\theta` as escape characters and silently corrupt the LaTeX.
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

void gui() {
    ImGuiMd::Render(R"(
# Math in markdown

Inline math: $E = mc^2$, $\sqrt{a^2 + b^2}$.

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
    )");
}

int main() {
    ImmApp::AddOnsParams addons;
    addons.withLatex = true;        // implies withMarkdown=true
    HelloImGui::SimpleRunnerParams simple;
    simple.guiFunction = gui;
    ImmApp::Run(simple, addons);
    return 0;
}
```
:::

::::

:::{tip}
Enable LaTeX math by passing `with_latex=True` to `immapp.run()` (Python)
or setting `addOnsParams.withLatex = true` (C++). Both imply markdown
support — you do not need to also set `with_markdown=True`.

- When LaTeX is **disabled** (the default), `$` is displayed as a normaly
- When LaTeX is **enabled**, `$` is treated as math delimiters. To include a literal `$`, escape it like this: `\$`.
:::

:::{note} Pyodide note
Pyodide wheels do not include the math fonts required for rendering LaTeX (to save space, since they occupy about 500KB). They will be downloaded when needed:  the download is triggered by a call to `immapp.run(with_latex=True)`.
:::


### Full Demo

[Try online](https://traineq.org/imgui_bundle_explorer/demo_imgui_md.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_imgui_md.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demo_imgui_md.cpp)

### Documented APIs

- **Python:** [imgui_md.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_md.pyi)
- **C++:** [imgui_md_wrapper.h](https://github.com/pthom/imgui_bundle/blob/main/external/imgui_md/imgui_md_wrapper/imgui_md_wrapper.h)


## ImGuiColorTextEdit - Syntax Highlighting Editor & Diff Viewer

### Introduction

[ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit) is a syntax highlighting text editor and diff viewer for ImGui (originally by BalazsJako, rewritten from scratch by Johan A. Goossens).

Dear ImGui Bundle uses a [fork](https://github.com/pthom/ImGuiColorTextEdit/tree/imgui_bundle) with a few additions for Python bindings.

**Features:**
- Syntax highlighting for C, C++, Python, GLSL, HLSL, Lua, SQL, AngelScript, C#, JSON, Markdown
- Multiple color palettes (dark, light)
- Find/replace UI with keyboard shortcuts
- Text markers (colored line highlights with tooltips)
- Bracket matching with visual indicators
- Line decorators (custom gutter content per line, e.g. breakpoints)
- Context menu callbacks (separate for line numbers and text area)
- Change and transaction callbacks
- Filter selections/lines (transform text via callbacks)
- Autocomplete framework
- Undo/redo, copy/paste, multi-cursor support
- **TextDiff widget**: combined and side-by-side diff view for comparing two texts

:::{tip}
The text editor requires a fixed-width font. If you are using ImmApp with Markdown enabled, you may use its code font:

```python
code_font = imgui_md.get_code_font()
imgui.push_font(code_font.font, code_font.size)
editor.render("Code")
imgui.pop_font()
```
:::

### Full Demo

[Try online](https://traineq.org/imgui_bundle_explorer/demo_text_edit.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_text_edit.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demo_text_edit.cpp)

### Documented APIs

- **Python:** [imgui_color_text_edit.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_color_text_edit.pyi)
- **C++:** [TextEditor.h](https://github.com/pthom/ImGuiColorTextEdit/blob/imgui_bundle/TextEditor.h) | [TextDiff.h](https://github.com/pthom/ImGuiColorTextEdit/blob/imgui_bundle/TextDiff.h)