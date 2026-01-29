<a href="https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_interactive_manual.png" alt="interactive manual" height="25"/>
</a>
&nbsp;
<a href="https://pthom.github.io/imgui_bundle/">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_view_docs.png" alt="view docs" height="25"/>
</a>

# Dear ImGui Bundle

> “Dear ImGui Bundle: easily create applications in Python and C++. Batteries included! With very few lines of code, you can build a responsive GUI, and deploy it to desktop or directly in the browser.”

Dear ImGui Bundle is a collection of libraries around [Dear ImGui](https://github.com/ocornut/imgui), for both C++ and Python. It focuses on app development, rapid prototyping, tooling, and educational demonstrations.

## Key features

- Cross‑platform: Windows, macOS, Linux, iOS, Android, and WebAssembly.
- C++ and Python APIs with very similar structure.
- Integrated ecosystem:
    - Dear ImGui (core widgets)
    - ImPlot / ImPlot3D (2D and 3D plotting)
    - ImmVision (image inspection)
    - imgui-node-editor, ImGuizmo, file dialogs, knobs, spinners, toggles, command palette, and more.
- Optional high‑level runners:
    - Hello ImGui: window, backend, docking, and assets management.
    - ImmApp: easy activation of add‑ons (ImPlot, Markdown, etc.).
- Web‑ready:
    - C++ via Emscripten
    - Python via Pyodide (online playground and deployable HTML templates)

> “Think of it as a toolbox where all the pieces are pre‑wired to play well together: plotting, Markdown, node editors, image inspection, and more, ready to drop into your app.”

***

## Documentation and interactive manuals

### Documentation site

Click the image below to visit the documentation site:

<a href="https://pthom.github.io/imgui_bundle/">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_view_docs.png" alt="view docs" height="25"/>
</a>

This site contains the full documentation for Dear ImGui Bundle, including install instructions, conceptual introductions, step‑by‑step tutorials, deployment recipes, etc. It is a companion to the interactive manual below.

### Interactive manual & demo

Click the image below to launch the interactive manual in your web browser:

<a href="https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_interactive_manual.png" alt="interactive manual" height="25"/>
</a>

The interactive manual showcases almost every part of the bundle with runnable examples. You can:
- Explore core Dear ImGui widgets.
- Try plotting, node editors, image viewers, test engine, and more.
- Inspect and copy the C++ and Python source code for each demo.

> “The interactive manual is intended to be your live reference: browse widgets, run demos, and copy code snippets directly into your own projects.”


### DeepWiki

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/pthom/imgui_bundle)

_DeepWiki is an AI based website where you can ask questions about the Dear ImGui Bundle usage and get answers. It is trained on the full documentation and the source code of the Dear ImGui Bundle. Expect some inconsistencies, but it is still helpful._

### Online playground (Pyodide):
Run and edit Python ImGui Bundle apps directly in your browser:
- No installation.
- Type code on the left, see the interactive GUI on the right.
- Great for experimentation, teaching, and sharing small examples.

Open the [playground](https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/).



## Build status

| OpenGL renderer | Python bindings | Alternative renderers | Mobile |
|-----------------|-----------------|-----------------------|--------|
| [![CppLib](https://github.com/pthom/imgui_bundle/workflows/CppLib/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib.yml)<br>[![Emscripten](https://github.com/pthom/imgui_bundle/workflows/Emscripten/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/emscripten.yml) | [![Pip](https://github.com/pthom/imgui_bundle/workflows/Pip/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/pip.yml)<br>[![Wheels](https://github.com/pthom/imgui_bundle/workflows/Wheels/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/wheels.yml)<br>[![Pyodide](https://github.com/pthom/imgui_bundle/workflows/Pyodide/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/pyodide.yml)<br>[![CppLib_WithBindings](https://github.com/pthom/imgui_bundle/workflows/CppLib_WithBindings/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib_with_bindings.yml) | [![Metal](https://github.com/pthom/imgui_bundle/workflows/Metal/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/Metal.yml)<br>[![DirectX](https://github.com/pthom/imgui_bundle/workflows/DirectX/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/DirectX.yml)<br>[![Vulkan](https://github.com/pthom/imgui_bundle/workflows/Vulkan/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/Vulkan.yml) | [![iOS](https://github.com/pthom/imgui_bundle/workflows/ios/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/ios.yml)<br>[![Android](https://github.com/pthom/imgui_bundle/workflows/android/badge.svg)](https://github.com/pthom/imgui_bundle/actions/workflows/android.yml) |


***
