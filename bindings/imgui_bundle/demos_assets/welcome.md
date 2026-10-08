*Interactive Python & C++ apps for desktop, mobile, and the web. The same code runs in the browser: no server, no rewrite.*

Put sliders on your equations. Plots that move, lessons students can touch.

## Batteries included

Built on [Dear ImGui](https://github.com/ocornut/imgui), the immediate-mode GUI library used across game studios and tools teams. Dear ImGui Bundle wraps it with 20+ integrated libraries, including:

- **Plotting**: ImPlot, ImPlot3D
- **Image analysis**: ImmVision
- **Rich content**: markdown with math, code editors
- **Graphs**: node editors, 3D gizmos
- **Custom widgets**: knobs, toggles, and more

The immediate mode paradigm leads to code that is concise and [easy to understand](https://imgui-bundle.pages.dev/doc/intro/what-is-imgui-bundle/#code-that-reads-like-a-book), for humans and for AI tools alike. A first app takes two lines:

```python
from imgui_bundle import imgui, immapp
immapp.run(lambda: imgui.text("Hello!"))
```

## The same code everywhere

- **Desktop**: Windows, macOS and Linux, in Python (`pip install imgui-bundle`) and in C++.
- **The web**: Python apps with Pyodide (below), C++ apps with Emscripten.
- **Mobile**: the same apps on iOS and Android, with touch gestures.
- **Notebooks**: a GUI [beside a Jupyter notebook](https://imgui-bundle.pages.dev/doc/python/notebook-runners/), live while the cells run.

## Web apps in pure Python

With [Pyodide](https://imgui-bundle.pages.dev/doc/python/python-pyodide/), a Python app runs in the browser as it is: an instant web GUI, from live code. The page is fully static: no server, and no HTML, CSS, React or JavaScript to write. No fuss.

A whole app fits in one HTML page: [a minimal example](https://imgui-bundle.pages.dev/min_pyodide_app/demo_heart.html), and [its source](https://imgui-bundle.pages.dev/min_pyodide_app/demo_heart.source.txt).

## The library teaches itself

Four interactive manuals (Dear ImGui, ImPlot, ImPlot3D, ImAnim) show every section with its code beside its widgets. For your AI assistant: [the guide for AI assistants](https://imgui-bundle.pages.dev/llms.txt) and the [API reference in plain text](https://imgui-bundle.pages.dev/llms/api/index.txt).

![[resources.md#Start here]]
