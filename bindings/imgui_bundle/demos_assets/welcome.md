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
- **The web**: Python apps run in the browser with [Pyodide](https://imgui-bundle.pages.dev/doc/python/python-pyodide/), C++ apps with Emscripten. No server, no JavaScript.
- **Mobile**: the same apps on iOS and Android, with touch gestures.
- **Notebooks**: a GUI [beside a Jupyter notebook](https://imgui-bundle.pages.dev/doc/python/notebook-runners/), live while the cells run.

## The library teaches itself

Four interactive manuals (Dear ImGui, ImPlot, ImPlot3D, ImAnim) show every section with its code beside its widgets. For your AI assistant: [the guide for AI assistants](https://imgui-bundle.pages.dev/llms.txt) and the [API reference in plain text](https://imgui-bundle.pages.dev/llms/api/index.txt).

![[resources.md#Start here]]
