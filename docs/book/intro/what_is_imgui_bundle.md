# What is Dear ImGui Bundle?

Dear ImGui Bundle is a "batteries included" framework built on [Dear ImGui](https://github.com/ocornut/imgui). It bundles 20+ libraries for plotting, markdown, node editors, 3D gizmos, and more - all working seamlessly in **C++ and Python**, on **all major platforms** (Windows, Linux, macOS, iOS, Android, WebAssembly).

If you are building scientific tools, game tools, visualization applications, developer tools, or creative apps, give it a try.
You'll soon see that GUI code can be clear, readable, and easy to maintain. The immediate mode paradigm makes it a joy to reason about your app logic.


**Key highlights:**

- **Immediate mode**: Your code reads like a book. No widget trees, no callbacks, no synchronization headaches.
- **Cross-platform**: Same code runs on desktop, mobile, and web (via Emscripten or Pyodide).
- **Python-first**: Full Python bindings with type hints and IDE autocompletion.
- **Always up-to-date**: Tracks Dear ImGui upstream closely; Python bindings are auto-generated.


---

## Code That Reads Like a Book

The immediate mode paradigm means your UI code is simple and direct: the app below can be coded with just 9 readable lines of Python:

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

The relation between code and behavior is direct: what you write is what runs. There are no hidden widget trees, no callback chains, and no implicit state synchronization. This makes it easier to reason about your app's logic and flow.

**Easy to understand for humans**

Being able to work with readable code is getting more and more important as LLMs are now widely used to generate code: *You*, the human, still need to understand, review, and maintain that code. Immediate mode makes this easier.

**Easy to understand for AI**

And the same clarity that helps humans also helps AI: with no implicit state to get wrong, LLMs can read and generate ImGui code reliably. The [full PDF manuals](https://imgui-bundle.pages.dev/doc/assets/imgui_bundle_book.pdf) give an AI assistant all the context it needs.

:::{tip}
**Try it in your browser — no install needed:** [Open the Online Python Playground](https://imgui-bundle.pages.dev/playground/)
:::

---

## Who is it for?

- **beginners and developers**: go from idea to GUI prototype in minutes, without learning a complex framework. Deploy to almost any platform.
- **ML/AI researchers**: visualize training in real time, tune hyperparameters mid-run, inside Jupyter
- **Computer vision engineers**: inspect images and tensors at the pixel level with ImmVision
- **Robotics developers**: fast, readable debug UIs in Python or C++
- **Scientific instrument builders**: cross-platform GUIs that deploy to desktop and web from the same code
- **Technical tool makers**: build node editors, gizmos, code editors without a web stack


**Who is this project not for**

You should prefer a more complete framework (such as Qt for example) if your intent is to build a fully fledged application, with support for accessibility, internationalization, advanced styling, etc.

---

## Learn More

- **[Key Features](key_features.md)** — Library list, FAQ, and more details.
- **[Immediate Mode Explained](imm_gui.md)** — Understand the paradigm that makes ImGui different.
- **[Interactive Manuals & Demos](interactive_manuals.md)** — Try the demos in your browser.
- **[Hello ImGui and ImmApp](../core_libs/hello_imgui_immapp.md)** — High-level runners that take care of the app loop, windowing, and assets management, so that you can start an app with a single line of code.
- **[Jupyter Notebooks](../python/notebook_runners.ipynb)** — Interactive GUIs inside Jupyter. Your training loop keeps running while you tune hyperparameters.
