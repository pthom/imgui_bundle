# Dear ImGui Bundle

> *Interactive Python & C++ apps for desktop, mobile, and web - powered by Dear ImGui.*
>
> Stop fighting GUI frameworks. Start building.
>
> [https:://imgui-bundle.pages.dev](https://imgui-bundle.pages.dev)

Dear ImGui Bundle is a batteries-included collection of libraries around [Dear ImGui](https://github.com/ocornut/imgui), for both C++ and Python. All the pieces are pre-wired to play well together: plotting, Markdown, node editors, image inspection, and more - ready to drop into your app.

**See it in action:**

*No install needed!*

* Launch the [Interactive Explorer](https://imgui-bundle.pages.dev/explorer/): a full demonstration: showcases all libraries with browsable C++ and Python source. Acts as a living reference manual.
* Ppen the [Playground](https://imgui-bundle.pages.dev/playground/): a live python sandbox with ready to use demos, based on pyodide.  Edit code, see results instantly.

[![Dear ImGui Bundle Explorer](https://imgui-bundle.pages.dev/resources/bundle_explorer_vid.gif)](https://imgui-bundle.pages.dev/explorer/)

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


### Documentation

The documentation is [available here](https://imgui-bundle.pages.dev/doc).


### Community

Join the [Discord server](https://discord.gg/xkzpKMeYN3) for questions, showcase, and discussion (new!).

### DeepWiki

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/pthom/imgui_bundle)

_DeepWiki is an AI based doc where you can ask questions about Dear ImGui Bundle and get answers. It is trained on the full documentation and the source code of the Dear ImGui Bundle. Expect some inconsistencies, but it is still helpful._


### Build status

| OpenGL renderer | Python bindings | Alternative renderers | Mobile |
|-----------------|-----------------|-----------------------|--------|
| [![CppLib](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib.yml)<br>[![Emscripten](https://github.com/pthom/imgui_bundle/actions/workflows/emscripten.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/emscripten.yml) | [![Pip](https://github.com/pthom/imgui_bundle/actions/workflows/pip.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/pip.yml)<br>[![Wheels](https://github.com/pthom/imgui_bundle/actions/workflows/wheels.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/wheels.yml)<br>[![Pyodide](https://github.com/pthom/imgui_bundle/actions/workflows/pyodide.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/pyodide.yml)<br>[![CppLib_WithBindings](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib_with_bindings.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/cpp_lib_with_bindings.yml) | [![Metal](https://github.com/pthom/imgui_bundle/actions/workflows/Metal.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/Metal.yml)<br>[![DirectX](https://github.com/pthom/imgui_bundle/actions/workflows/DirectX.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/DirectX.yml)<br>[![Vulkan](https://github.com/pthom/imgui_bundle/actions/workflows/Vulkan.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/Vulkan.yml) | [![iOS](https://github.com/pthom/imgui_bundle/actions/workflows/ios.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/ios.yml)<br>[![Android](https://github.com/pthom/imgui_bundle/actions/workflows/android.yml/badge.svg?branch=main)](https://github.com/pthom/imgui_bundle/actions/workflows/android.yml) |

