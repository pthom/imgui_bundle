# I Just Want Python! Build Real-Time Python  applications with Zero  Fuss

## 1. Introduction:&#x20;

*The web development environment is a jungle for the Python developer*

Tools like **Streamlit**, **Gradio**, and **Jupyter** have gone a long way in simplifying the bridge between Python and the browser. They abstract away much of the boilerplate when building a Web Gui with Python.&#x20;

However, when things break, you're suddenly wrestling with JavaScript errors, layout issues in CSS, or debugging the front-end / back-end synchronization. 

*And you might think*

\[insert humorous image "I just want Python"]

But what if you could skip all that and just write Python? What if your GUI code could be:

* clean and reactive
* Pure Python
* easy to write like `print()` statements,
* and even run directly in the browser, without requiring a distant server?

Welcome to the Immediate Mode GUI paradigm — and the world of **Dear ImGui** and **ImGui Bundle**.

In this article:

* We explain how Immediate Mode GUI works
* We introduce Dear ImGui, a reputable Immediate Mode GUI library (C++)
* We explore **ImGui Bundle**, which brings Dear ImGui to Python, together with lots of utilities
* And we show how it all works **in your browser**, with Pyodide&#x20;


\[Insert link and screenshot of Interactive Playground]

---

## 2. The Immediate Mode GUI Paradigm

* **What is Immediate Mode GUI?**

Immediate Mode GUIs (IMGUI) differ from traditional retained-mode frameworks. Instead of building and maintaining an abstract UI tree, you declare your widgets anew each frame — just like calling `print()` repeatedly in a loop.

This approach leads to:

* Simple, stateless, and readable code
* Full control over rendering and logic, frame-by-frame 
* Great debugging and introspection: there's no hidden state behind the GUI

For instance, displaying button and handling its action in ImGui might just look like:

```python
if imgui.button("Click me"):  # Display a button
    do_something()            # Call this action on click 
```

* **Compared to retained-mode and web-based GUIs**

Frameworks like **Streamlit**, **Gradio**, and **Dash** rely on a layered architecture that separates logic from rendering. When things go wrong, you often find yourself debugging JavaScript, CSS, or frontend/backend sync issues.

*In contrast, Immediate Mode GUIs are radically simple.*

There’s no event queue to wire, no hidden reactive state — just Python code running in a loop, directly rendering the GUI. Whether you run it natively or in the browser via Pyodide, your UI logic stays local, explicit, and easy to debug.

### 📊 Comparison: Immediate Mode vs classic Python Web GUIs

| Feature                     | Immediate Mode GUI (e.g. ImGui)          | Python Web GUI (Streamlit, Gradio) |
| --------------------------- | ---------------------------------------- | ---------------------------------- |
| **Frontend stack**          | None (single process)                    | HTML + CSS + JS + Python           |
| **Architecture**            | Monolithic loop                          | Client–server (multi-process)      |
| **GUI logic location**      | In the Python loop                       | Split between Python and JS        |
| **Event model**             | Immediate / synchronous                  | Asynchronous / message-passing     |
| **State handling**          | Explicit, local                          | Hidden reactive model              |
| **Debuggability**           | Direct (print/debug in place)            | Sometimes requires JS inspection   |
| **Deployment**              | Native or via Pyodide (static web pages) | Requires server or hosted infra    |
| **Custom styling / layout** | Code-driven, limited theming             | HTML/CSS-driven                    |
| **Performance**             | High (real-time loop)                    | Variable (network + rendering)     |

---

## 3. Enter **Dear ImGui**

**Dear ImGui** is a fast, lightweight C++ library designed for building rich graphical user interfaces in real-time applications. Originally developed for debugging tools in game engines, it's now used across industries for visualization, simulation, embedded UIs, and more.

ImGui follows the Immediate Mode GUI paradigm: widgets are declared directly in your rendering loop, which makes it incredibly responsive, debuggable, and easy to integrate.

It’s known for:

* Extremely low overhead and high performance
* Plug-and-play usability — no GUI designer, no layout files
* A focus on developer productivity and iteration speed
* A powerful ecosystem: docking, plots (ImPlot), markdown, node editors, fonts, multi-viewports, and more

With 66k+ GitHub stars and a passionate community, ImGui has become a go-to for developers who want **full control** and **minimal friction** when building UIs.

---

## 4. Meet **Dear ImGui Bundle**

**Dear ImGui Bundle** builds on top of Dear ImGui to offer a ready-to-use, cross-platform toolkit for both C++ and Python. It wraps the core ImGui API with batteries included: advanced widgets, plotting (ImPlot), image handling, markdown rendering, node editors, and more.

With full Python bindings and API consistency with C++, it’s a great match for data scientists, educators, and toolmakers who want to go fast — without giving up control.

* One codebase, runs natively or in the browser (via Pyodide)
* Great for interactive prototypes, apps, and scientific GUIs
* Same API across platforms and languages

---

## 🌐 6. ImGui Bundle **in the Browser** (via Pyodide)



ImGui Bundle isn't just another GUI library — it offers something rare:

* ✅ **Immediate feedback**: tweak parameters and visualize instantly
* ✅ **Same code everywhere**: write once, run natively or in the browser
* ✅ **No web stack**: skip the complexity of JS, CSS, and frontend frameworks
* ✅ **Perfect for prototypes & notebooks**: interactive tools, small apps, scientific GUIs
* ✅ **Performance that scales**: real-time updates, native responsiveness

For anyone building internal tools, teaching environments, or portable visual apps, this approach offers unmatched simplicity and power.

🌀 **Live demo**: [Lorenz Attractor / Butterfly Effect](https://traineq.org/pyobun2/demo_butterfly.html)
💡 **Interactive playground**: [Try it in your browser](https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/)

This makes ImGui Bundle a rare breed: a Python GUI framework that works identically across desktop and browser — with the same codebase.

---

## 🚀 8. Try It Yourself

* Link to interactive playground
* How to get started:

    * pip install
    * minimal example
    * link to demos and templates

---

## 🔗 9. Resources & Links

* GitHub repos
* Documentation
* Community / Discussions

---

## 💬 10. Share & Feedback

* Invite comments, bug reports, suggestions
* Link to Reddit / Hacker News post if applicable

---

## Optional: FAQ Section (or separate page)

* Can I use this with Jupyter?
* How is this different from Streamlit?
* Does it work with Pyodide 0.25+?
* Is mobile supported?
