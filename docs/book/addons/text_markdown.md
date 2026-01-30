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

### Full Demo

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_md.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_imgui_md.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demo_imgui_md.cpp)

### Documented APIs

- **Python:** [imgui_md.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_md.pyi)
- **C++:** [imgui_md_wrapper.h](https://github.com/pthom/imgui_bundle/blob/main/external/imgui_md/imgui_md_wrapper/imgui_md_wrapper.h)


## ImGuiColorTextEdit - Syntax Highlighting Editor

### Introduction

[ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit) is a colorizing text editor for ImGui. It supports syntax highlighting for C, C++, Python, HLSL, SQL, AngelScript, Lua, and more.

Dear ImGui Bundle uses a [fork](https://github.com/pthom/ImGuiColorTextEdit/tree/imgui_bundle) with additional fixes and features.

::::{card}
:link: https://github.com/BalazsJako/ImGuiColorTextEdit
```{figure} https://raw.githubusercontent.com/wiki/BalazsJako/ImGuiColorTextEdit/ImGuiTextEdit.png
:width: 350
ImGuiColorTextEdit: syntax highlighting editor with multiple color palettes.
```
::::

**Features:**
- Multiple color palettes (dark, light, retro blue, mariana)
- Language definitions for common languages
- Line numbers, error markers, breakpoints
- Undo/redo, copy/paste, find/replace

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

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_text_edit.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_text_edit.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demo_text_edit.cpp)

### Documented APIs

- **Python:** [imgui_color_text_edit.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_color_text_edit.pyi)
- **C++:** [TextEditor.h](https://github.com/pthom/ImGuiColorTextEdit/blob/imgui_bundle/TextEditor.h)