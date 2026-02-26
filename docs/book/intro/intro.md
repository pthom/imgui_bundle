# Dear ImGui Bundle

> From expressive code to powerful GUIs in no time: a fast, feature-rich, cross-platform toolkit for C++ & Python.

<a href="https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html">
    <img src="../../../logo/logo_imgui_bundle_1024.png" width="80"/>
</a>

_Click the logo to launch the interactive manual in your browser!_

---

## What is Dear ImGui Bundle?

Dear ImGui Bundle is a "batteries included" framework built on [Dear ImGui](https://github.com/ocornut/imgui). It bundles 20+ libraries for plotting, markdown, node editors, 3D gizmos, and more — all working seamlessly in **C++ and Python**, on **all major platforms** (Windows, Linux, macOS, iOS, Android, WebAssembly).

If you are building scientific tools, game tools, visualization applications, developer tools, or creative apps, give it a try.
You'll soon see that GUI code can be clear, readable, and easy to maintain. The immediate mode paradigm makes it a joy to reason about your app logic.


**Key highlights:**

- **Immediate mode**: Your code reads like a book. No widget trees, no callbacks, no synchronization headaches.
- **Cross-platform**: Same code runs on desktop, mobile, and web (via Emscripten or Pyodide).
- **Python-first**: Full Python bindings with type hints and IDE autocompletion.
- **Always up-to-date**: Tracks Dear ImGui upstream closely; Python bindings are auto-generated.



:::{note}
* Dear ImGui Bundle may not be the best choice for applications that need to match OS look-and-feel exactly, or for projects where accessibility is critical.
* Being able to work with readable code is getting more and more important as LLMs are now widely used to generate code. Dear ImGui Bundle's immediate mode paradigm naturally leads to code that is easy to understand, both for humans and for AI tools.
:::




---

## Code That Reads Like a Book

The immediate mode paradigm means your UI code is simple and direct:

```python
from imgui_bundle import imgui, hello_imgui

selected_idx = 0
items = ["Apple", "Banana", "Cherry"]

def gui():
    global selected_idx
    imgui.text("Choose a fruit:")
    _, selected_idx = imgui.list_box("##fruits", selected_idx, items)
    imgui.text(f"You selected: {items[selected_idx]}")

hello_imgui.run(gui, window_title="Fruit Picker")
```

![Fruit picker app](../images/choose_fruit.jpg)

No widget objects. No signals/slots. State lives in your code. Changes are immediate. [Compare with alternatives](key_features.md#comparison-with-alternatives)

---

## Learn More

- **[Key Features](key_features.md)** — Detailed comparisons with Qt, Streamlit, Gradio, and more.
- **[Immediate Mode Explained](imm_gui.md)** — Understand the paradigm that makes ImGui different.
- **[Interactive Manuals & Demos](interactive_manuals.md)** — Try the demos in your browser.

```{include} resources.md
```
