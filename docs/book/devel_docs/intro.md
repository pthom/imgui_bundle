# Intro - Developer docs

This section is for developers willing to build and modify the imgui_bundle library. It covers topics such as building the library, updating dependencies, and adding new features or bindings.

## Architecture Overview

ImGui Bundle implements a **four-layer architecture**:

1. **Rendering Backends** – GLFW/SDL + OpenGL/Metal/DirectX/Vulkan
2. **Dear ImGui Core** – immediate-mode widget system
3. **Hello ImGui Framework** – window lifecycle, docking, DPI handling, asset management
4. **ImmApp Layer** – simplified runner with automatic add-on initialization

Users can work at their preferred abstraction level, from raw ImGui calls to the high-level `immapp.run()` API.

## Python Bindings

The bindings are auto-generated using [litgen](https://pthom.github.io/litgen), a code generator that transforms C++ headers into:
- **nanobind C++ code** – the actual binding implementation
- **`.pyi` type stubs** – for IDE autocompletion and type checking

All 23+ C++ libraries compile into a single `_imgui_bundle` native extension, with submodules conditionally available based on build configuration.

## Key Concepts

- **Add-On System**: ImmApp manages automatic context creation for optional libraries via `AddOnsParams` flags (`with_implot`, `with_markdown`, etc.)
- **Cross-Platform**: Same codebase deploys to desktop (Windows/macOS/Linux), mobile (iOS/Android), and web (Emscripten/Pyodide)
- **DPI-Aware Sizing**: Helper functions like `EmToVec2()` enable responsive layouts across high-DPI displays

## More Resources

- **[DeepWiki - ImGui Bundle](https://deepwiki.com/pthom/imgui_bundle)** – AI-powered documentation explorer for in-depth architecture questions
- **[Litgen Documentation](https://pthom.github.io/litgen)** – the bindings generator used by this project

## In This Section

- [Repository Structure](structure.md) – folder organization
- [Bindings Introduction](bindings_intro.md) – how the generator works
- [Update Bindings](bindings_update.md) – updating existing library bindings
- [Add New Library](bindings_newlib.md) – adding a new library to the bundle
- [Debug Native C++](bindings_debug.md) – debugging C++ code from Python
