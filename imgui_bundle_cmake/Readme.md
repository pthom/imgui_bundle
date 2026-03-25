# imgui_bundle_cmake/ — CMake build infrastructure

CMake modules that build the imgui_bundle library and provide helpers for downstream apps.

**Key files:**
- `imgui_bundle_build_lib.cmake` — Main build logic (dependency resolution, module toggling)
- `imgui_bundle_add_app.cmake` — `imgui_bundle_add_app()`: create an app in one CMake call
- `imgui_bundle_config.h` — C++ config header (`#define` flags for enabled modules)
- `internal/` — Helpers for integrating individual libraries (add_imgui, add_hello_imgui, etc.)

**Documentation:** [Build Guide](../docs/book/devel_docs/build_guide.md) | [Repository Structure](../docs/book/devel_docs/structure.md)
