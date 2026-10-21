# Dear ImGui Bundle

> “Dear ImGui Bundle: easily create applications in Python and C++. Batteries included! With very few lines of code, you can build a responsive GUI, and deploy it to desktop or directly in the browser.”

Dear ImGui Bundle is a collection of libraries around [Dear ImGui](https://github.com/ocornut/imgui), for both C++ and Python.

Use it for real-time tools (live data, instruments, simulations, scientific viewers, dashboards), and for playful sketches with sliders (creative coding, math toys) that friends open from a link. The same code runs on the desktop, in the browser and on phones. In the browser, no server is needed: a static page is enough.

Projects that use the bundle include [Newton](https://github.com/newton-physics/newton) and [Isaac Lab](https://github.com/isaac-sim/IsaacLab) (robotics simulation), [Genesis](https://github.com/Genesis-Embodied-AI/Genesis) (physics for robotics, 30k stars), the [Gaussian splatting viewer](https://github.com/graphdeco-inria/graphdecoviewer) of Inria's GRAPHDECO lab, [splatviz](https://github.com/Florian-Barthel/splatviz), Meta's [Nymeria](https://github.com/facebookresearch/nymeria_dataset), and [fastplotlib](https://github.com/fastplotlib/fastplotlib). More on the [home page](https://imgui-bundle.pages.dev).

**Install:** `pip install imgui-bundle`, then `from imgui_bundle import imgui`. Not to be confused with pyimgui (`pip install imgui`, then `import imgui`): another Python binding of Dear ImGui, with another API.

## Key features

- Cross‑platform: Windows, macOS, Linux, iOS, Android, and WebAssembly.
- C++ and Python APIs with very similar structure.
- Made for AI assistants: given [llms.txt](https://imgui-bundle.pages.dev/llms.txt), an AI can write an app with the bundle, run it, and check it with screenshots and the test engine, even in a chat's sandbox.
- Integrated ecosystem:
  - Dear ImGui (core widgets)
  - ImPlot / ImPlot3D (2D and 3D plotting)
  - ImmVision (image inspection)
  - ImAnim (animations), and your Matplotlib figures inside the GUI (`imgui_fig`)
  - imgui-node-editor, ImGuizmo, file dialogs, knobs, spinners, toggles, command palette, a terminal, and more.
- Optional high‑level runners:
  - Hello ImGui: window, backend, docking, and assets management.
  - ImmApp: easy activation of add‑ons (ImPlot, Markdown, etc.).
- Web‑ready:
  - C++ via Emscripten
  - Python via Pyodide (online playground and deployable HTML templates)
  - Touch screens: on a phone, a swipe scrolls, a pinch scales the app, and a keyboard button appears next to a text field.
- Jupyter: the notebook stays usable while your app runs (`immapp.nb.start()`).
- 17 themes, tweaked live. Power save: an idle app lowers its frame rate.
- Tests and automation: [ImGui Test Engine](https://github.com/ocornut/imgui_test_engine) drives your GUI from a script, for tests, demos or screenshots (it has [its own license](https://www.dearimgui.com/licenses)).

> “Think of it as a toolbox where all the pieces are pre‑wired to play well together: plotting, Markdown, node editors, image inspection, and more, ready to drop into your app.”

***

## Links:

* [Documentation site](https://imgui-bundle.pages.dev/doc/): Full documentation for Dear ImGui Bundle.
* [Dear ImGui Bundle Explorer](https://imgui-bundle.pages.dev/explorer/): interactive reference manual - browse demos, see the code, try the widgets. All 23 libraries demonstrated with browsable C++ and Python source.
* [Online Python Playground](https://imgui-bundle.pages.dev/playground/): live Python sandbox with ready-to-run demos - edit code, see results instantly. No installation needed.
* [Discord](https://discord.gg/xkzpKMeYN3): join the community for questions, showcase, and discussion
* [GitHub](https://github.com/pthom/imgui_bundle): source code, issues, discussions
* [Guide for AI assistants](https://imgui-bundle.pages.dev/llms.txt): llms.txt, to write apps with the bundle, and to run and check them
* [FAQ](https://github.com/pthom/imgui_bundle/issues?q=is%3Aissue+label%3AFAQ): answers to common questions
