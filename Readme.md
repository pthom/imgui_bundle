<a href="https://traineq.org/imgui_bundle_explorer">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_interactive_explorer.png" alt="interactive explorer" height="25"/>
</a>
&nbsp;
<a href="https://pthom.github.io/imgui_bundle/">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_view_docs.png" alt="view docs" height="25"/>
</a>

# Dear ImGui Bundle

> *Interactive Python & C++ apps for desktop, mobile, and web - powered by Dear ImGui.*
>
> Stop fighting GUI frameworks. Start building.

Dear ImGui Bundle is a batteries-included collection of libraries around [Dear ImGui](https://github.com/ocornut/imgui), for both C++ and Python. All the pieces are pre-wired to play well together: plotting, Markdown, node editors, image inspection, and more - ready to drop into your app.

**See it in action:** [launch the Interactive Explorer in your browser](https://traineq.org/imgui_bundle_explorer/)

[![Dear ImGui Bundle Explorer](https://traineq.org/ImGuiBundle/bundle_explorer_vid.gif)](https://traineq.org/imgui_bundle_explorer/)

## Key features

- Cross-platform: Windows, macOS, Linux, iOS, Android, and WebAssembly.
- C++ and Python APIs with very similar structure.
- Integrated ecosystem:
    - Dear ImGui (core widgets)
    - ImPlot / ImPlot3D (2D and 3D plotting)
    - ImmVision (image inspection)
    - imgui-node-editor, ImGuizmo, file dialogs, knobs, spinners, toggles, command palette, and more.
- Optional high-level runners:
    - Hello ImGui: window, backend, docking, and assets management.
    - ImmApp: easy activation of add-ons (ImPlot, Markdown, etc.).
- Web-ready:
    - C++ via Emscripten
    - Python via Pyodide (online playground and deployable HTML templates)

***

## Try it now

### Online playground
Live Python sandbox with ready-to-run demos - edit code, see results instantly. No installation needed.

Open the **[playground](https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/)**.

### Interactive explorer

Interactive reference manual - browse demos, see the code, try the widgets. Showcases all 23 libraries with browsable C++ and Python source.

**[Launch the Interactive Explorer](https://traineq.org/imgui_bundle_explorer)**

### Community

Join the **[Discord server](https://discord.gg/xkzpKMeYN3)** for questions, showcase, and discussion (new!).

## Documentation

<a href="https://pthom.github.io/imgui_bundle/">
<img src="https://raw.githubusercontent.com/pthom/imgui_bundle/refs/heads/main/bindings/imgui_bundle/demos_assets/images/badge_view_docs.png" alt="view docs" height="25"/>
</a>

Full documentation: install instructions, conceptual introductions, step-by-step tutorials, deployment recipes, and API guides.

### DeepWiki

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/pthom/imgui_bundle)

_DeepWiki is an AI based website where you can ask questions about the Dear ImGui Bundle usage and get answers. It is trained on the full documentation and the source code of the Dear ImGui Bundle. Expect some inconsistencies, but it is still helpful._


## Build status

| OpenGL renderer | Python bindings | Alternative renderers | Mobile |
|-----------------|-----------------|-----------------------|--------|
| [![CppLib](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib.yml)<br>[![Emscripten](https://github.com/pthom/imgui_bundle/actions/workflows/emscripten.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/emscripten.yml) | [![Pip](https://github.com/pthom/imgui_bundle/actions/workflows/pip.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/pip.yml)<br>[![Wheels](https://github.com/pthom/imgui_bundle/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/wheels.yml)<br>[![Pyodide](https://github.com/pthom/imgui_bundle/actions/workflows/pyodide.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/pyodide.yml)<br>[![CppLib_WithBindings](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib_with_bindings.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib_with_bindings.yml) | [![Metal](https://github.com/pthom/imgui_bundle/actions/workflows/Metal.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/Metal.yml)<br>[![DirectX](https://github.com/pthom/imgui_bundle/actions/workflows/DirectX.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/DirectX.yml)<br>[![Vulkan](https://github.com/pthom/imgui_bundle/actions/workflows/Vulkan.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/Vulkan.yml) | [![iOS](https://github.com/pthom/imgui_bundle/actions/workflows/ios.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/ios.yml)<br>[![Android](https://github.com/pthom/imgui_bundle/actions/workflows/android.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/android.yml) |


***
