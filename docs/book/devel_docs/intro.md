# Intro - Developer docs

This section is for developers willing to build and modify the imgui_bundle library. It covers topics such as building the library, updating dependencies, and adding new features or bindings.

:::{tip}
**New here?** Start with [Getting Started (Developer)](getting_started_dev.md) — it takes you from clone to working build in 5 minutes.
:::

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

## Glossary

Terms used throughout the developer docs:

| Term                | Meaning                                                                                                                                                                      |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dear ImGui**      | The core C++ immediate-mode GUI library by Omar Cornut                                                                                                                       |
| **Hello ImGui**     | Framework layer on top of Dear ImGui: window lifecycle, docking, DPI, asset management, multi-platform deployment                                                            |
| **ImmApp**          | High-level runner that wraps Hello ImGui and auto-initializes add-ons (ImPlot, Markdown, etc.) via simple flags                                                              |
| **litgen**          | [Literate Generator](https://pthom.github.io/litgen) — the tool that reads C++ headers and generates Python bindings (nanobind C++ code + `.pyi` stubs)                      |
| **nanobind**        | C++ library used to create Python extension modules. Successor to pybind11; used by litgen's generated code                                                                  |
| **srcML**           | XML representation of C++ source code; used internally by litgen to parse headers                                                                                            |
| **`.pyi` stubs**    | Python type stub files providing IDE autocompletion and type checking for the native extension                                                                               |
| **pybind**          | Legacy naming seen in generated filenames (`pybind_*.cpp`). These files actually use nanobind, not pybind11 — the name is historical                                         |
| **ibex**            | Abbreviation fo [Dear ImGui Bundle Explorer](https://traineq.org/imgui_bundle_explorer) — the full demo app showcasing all libraries, used in just recipes (`just ibex_...`) |
| **imex**            | Abbreviation for [Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/) - source code in external/imgui_explorer. Used just recipes `just imex_...`                  |
| **`_imgui_bundle`** | The single compiled native extension (`.so`/`.pyd`) containing all 23+ C++ libraries                                                                                         |
| **justfile**        | Task runner config at repo root; provides shortcuts like `just libs_bindings`, `just test_pytest`, etc.                                                                      |

## More Resources

- **[DeepWiki - ImGui Bundle](https://deepwiki.com/pthom/imgui_bundle)** – AI-powered documentation explorer for in-depth architecture questions
- **[Litgen Documentation](https://pthom.github.io/litgen)** – the bindings generator used by this project

## In This Section

- [Getting Started (Developer)](getting_started_dev.md) – clone, build, run, test
- [Repository Structure](structure.md) – folder organization
- [Build Guide](build_guide.md) – CMake options, presets, justfile commands
- [Testing](testing.md) – running tests, CI workflows
- [Bindings Introduction](bindings_intro.md) – how the generator works
- [Update Bindings](bindings_update.md) – updating existing library bindings
- [Add New Library](bindings_newlib.md) – adding a new library to the bundle
- [Debug Native C++](bindings_debug.md) – debugging C++ code from Python
- [PyPI Deployment](pypi_deploy.md) – releasing to PyPI
- [Pyodide Build Guide](Readme_pyodide_bundle.md) – building for Python-in-the-browser
- [OpenCV Build Guide](build_opencv_immvision.md) – building with OpenCV / ImmVision
