# Plan: Add Configurable Python Wheel Builds to Exclude Submodules

This plan addresses building Python wheels for imgui_bundle with selective module inclusion/exclusion. We desire to be able to exclude HelloImGui, Immapp, and optionally other heavy dependencies like OpenCV (immvision), while keeping core Dear ImGui widgets. The existing C++ system already has `IMGUI_BUNDLE_DISABLE_*` options, but these need to be extended to Python builds.
Ideally, users can specify which modules to exclude during `pip install`, resulting in smaller wheels tailored to their needs.

Related discussion: https://github.com/pthom/imgui_bundle/discussions/433

## Background

### Current State

The project already has infrastructure for conditional compilation:

1. **C++ side**: CMake options like `IMGUI_BUNDLE_DISABLE_NANOVG`, `IMGUI_BUNDLE_DISABLE_IMPLOT`, etc. that conditionally exclude libraries from C++ builds
2. **Python side**: The `__init__.py` uses `has_submodule()` to check `__bundle_submodules__` list and conditionally import available modules
3. **Bindings**: `pybind_imgui_bundle.cpp` uses `#ifdef` preprocessor directives (e.g., `IMGUI_BUNDLE_WITH_IMPLOT`) to conditionally register Python submodules

### Module Dependencies

Understanding the dependency structure is critical for this implementation:

```
hello_imgui (window management + OpenGL context)
├── immapp (depends on hello_imgui)
│   └── Python immapp package (depends on immapp_cpp)
├── im_file_dialog (needs OpenGL from hello_imgui)
├── imgui_tex_inspect (needs OpenGL from hello_imgui)
├── imgui_test_engine (needs GIL management from hello_imgui)
└── GLFW backend (no point without hello_imgui)

Independent modules (can work without hello_imgui):
├── implot
├── implot3d
├── imgui_node_editor
├── imgui_knobs
├── nanovg (has its own OpenGL context)
├── imguizmo
└── other widget libraries
```

When `IMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON`, all dependent modules must be auto-disabled.


## Steps

### 0. Create Environment Variable Handling Macro

**File**: `imgui_bundle_cmake/imgui_bundle_build_lib.cmake`

**Actions**:
- Create a reusable macro to handle environment variable overrides for all disable options
- This keeps CMakeLists.txt clean and maintainable

**Implementation**:
```cmake
# Add this macro to imgui_bundle_build_lib.cmake
macro(imgui_bundle_apply_env_var_overrides)
    if(IMGUI_BUNDLE_BUILD_PYTHON)
        # List of all disable options that can be controlled via environment variables
        set(_disable_options
            HELLO_IMGUI
            IMMAPP
            NANOVG
            IMPLOT
            IMPLOT3D
            IMGUI_NODE_EDITOR
            IMGUIZMO
            IMGUI_TEX_INSPECT
            IMFILEDIALOG
            IMMVISION
        )

        foreach(_opt ${_disable_options})
            if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_${_opt}})
                set(IMGUI_BUNDLE_DISABLE_${_opt} "$ENV{IMGUI_BUNDLE_DISABLE_${_opt}}" CACHE BOOL "Set from environment variable" FORCE)
                message(STATUS "IMGUI_BUNDLE_DISABLE_${_opt} set to $ENV{IMGUI_BUNDLE_DISABLE_${_opt}} from environment")
            endif()
        endforeach()
    endif()
endmacro()
```

### 1. Add New CMake Options for Python-Specific Disables

**File**: `CMakeLists.txt`

**Location**: After the existing `IMGUI_BUNDLE_DISABLE_*` options (search for "Some included libraries can be disabled individually")

**Actions**:
- Add `option(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI "Disable hello_imgui" OFF)`
- Add `option(IMGUI_BUNDLE_DISABLE_IMMAPP "Disable immapp" OFF)`
- Create a dependency chain logic: if `IMGUI_BUNDLE_DISABLE_HELLO_IMGUI` is ON:
  - Force `IMGUI_BUNDLE_DISABLE_IMMAPP=ON` (immapp depends on hello_imgui)
  - Force `HELLOIMGUI_USE_GLFW3=OFF` (no need for GLFW without hello_imgui)
  - Force disable `IMGUI_BUNDLE_DISABLE_IMFILEDIALOG=ON` (depends on OpenGL from hello_imgui)
  - Force disable `IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT=ON` (depends on OpenGL from hello_imgui)
  - Emit warning messages about auto-disabled dependencies

**Implementation**:
```cmake
# After existing IMGUI_BUNDLE_DISABLE options, add:
option(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI "Disable hello_imgui (window management)" OFF)
option(IMGUI_BUNDLE_DISABLE_IMMAPP "Disable immapp (internal high-level app framework)" OFF)

# Apply environment variable overrides (call the macro from Step 0)
imgui_bundle_apply_env_var_overrides()

# Dependency chain logic - add this after backend options (after HELLOIMGUI_HAS_* options)
if(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    message(STATUS "═══════════════════════════════════════════════════════════")
    message(STATUS "IMGUI_BUNDLE_DISABLE_HELLO_IMGUI is ON")
    message(STATUS "Auto-disabling dependent modules:")
    message(STATUS "  - immapp (depends on hello_imgui)")
    message(STATUS "  - im_file_dialog (needs OpenGL context from hello_imgui)")
    message(STATUS "  - imgui_tex_inspect (needs OpenGL context from hello_imgui)")
    message(STATUS "  - imgui_test_engine (needs GIL management from hello_imgui)")
    message(STATUS "  - GLFW backend (not needed without hello_imgui)")
    message(STATUS "═══════════════════════════════════════════════════════════")

    set(IMGUI_BUNDLE_DISABLE_IMMAPP ON CACHE BOOL "Auto-disabled: depends on hello_imgui" FORCE)
    set(IMGUI_BUNDLE_DISABLE_IMFILEDIALOG ON CACHE BOOL "Auto-disabled: needs OpenGL from hello_imgui" FORCE)
    set(IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT ON CACHE BOOL "Auto-disabled: needs OpenGL from hello_imgui" FORCE)
    set(HELLOIMGUI_WITH_TEST_ENGINE OFF CACHE BOOL "Auto-disabled: test_engine needs GIL context switching from hello_imgui" FORCE)
    set(HELLOIMGUI_USE_GLFW3 OFF CACHE BOOL "Auto-disabled: not needed without hello_imgui" FORCE)
    set(HELLOIMGUI_HAS_OPENGL3 OFF CACHE BOOL "Auto-disabled: not needed without hello_imgui" FORCE)
endif()

# Validate that IMMAPP isn't enabled if HELLO_IMGUI is disabled
if(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI AND NOT IMGUI_BUNDLE_DISABLE_IMMAPP)
    message(WARNING "IMMAPP requires HELLO_IMGUI. Auto-disabling IMMAPP.")
    set(IMGUI_BUNDLE_DISABLE_IMMAPP ON CACHE BOOL "Auto-disabled: depends on hello_imgui" FORCE)
endif()
```

### 2. Update pybind_imgui_bundle.cpp Conditionals

**File**: `external/bindings_generation/cpp/pybind_imgui_bundle.cpp`

**Actions**:
- Wrap `hello_imgui` module registration with `#ifndef IMGUI_BUNDLE_DISABLE_HELLO_IMGUI`
- Wrap `immapp_cpp` module registration with `#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP`
- Ensure `_register_submodule()` calls are also wrapped
- Add conditional for `with_glfw` registration

**Location**: Search for "hello_imgui", "immapp_cpp", and "with_glfw" in the file

**Implementation**:
```cpp
// Find the hello_imgui registration and wrap it:
#ifndef IMGUI_BUNDLE_DISABLE_HELLO_IMGUI
    _register_submodule("hello_imgui");
    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);
#endif

// Find the immapp_cpp registration and wrap it:
#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP
    _register_submodule("immapp_cpp");
    auto module_immapp_cpp = m.def_submodule("immapp_cpp");
    py_init_module_immapp_cpp(module_immapp_cpp);
#endif

// Find the with_glfw registration and update it:
#if defined(HELLOIMGUI_USE_GLFW3) && !defined(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    _register_submodule("with_glfw");
#endif

// Note: The test_engine registration is already conditional on HELLOIMGUI_WITH_TEST_ENGINE,
// which we set to OFF in Step 1 when hello_imgui is disabled, so no changes needed there.
```

### 3. Update external/CMakeLists.txt

**File**: `external/CMakeLists.txt`

**Actions**:
- Wrap the `add_hello_imgui()` call with a conditional check for `IMGUI_BUNDLE_DISABLE_HELLO_IMGUI`
- When hello_imgui is disabled, build imgui standalone using `add_imgui.cmake`
- Wrap immapp subdirectory addition with conditional for `IMGUI_BUNDLE_DISABLE_IMMAPP`
- Update existing conditionals for im_file_dialog and imgui_tex_inspect to also check for hello_imgui availability

**Locations**:
- Search for "add_hello_imgui()" near the top of the file
- Search for "add_subdirectory(immapp/immapp)" near the end
- Search for im_file_dialog and imgui_tex_inspect conditionals

**Implementation**:
```cmake
# Replace the add_hello_imgui() section with:
if(NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    # Standard path: build hello_imgui (which includes imgui)
    include(../imgui_bundle_cmake/internal/add_hello_imgui.cmake)
    add_hello_imgui()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
    endif()
    set(IMGUI_BUNDLE_WITH_HELLO_IMGUI ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_HELLO_IMGUI)
else()
    # Library-only mode: build imgui standalone without hello_imgui
    message(STATUS "═══════════════════════════════════════════════════════════")
    message(STATUS "Building imgui_bundle in LIBRARY-ONLY mode")
    message(STATUS "  - No window management (no hello_imgui)")
    message(STATUS "  - No high-level app framework (no immapp)")
    message(STATUS "  - Core ImGui + widget libraries only")
    message(STATUS "═══════════════════════════════════════════════════════════")

    # Build imgui standalone using the bundle's modified version
    # (external/imgui/imgui contains Python binding modifications)
    include(../imgui_bundle_cmake/internal/add_imgui.cmake)
    add_imgui(${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)

    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
    endif()
endif()

# Update im_file_dialog conditional to check for hello_imgui
# (Find the existing im_file_dialog section and wrap it)
if(NOT IMGUI_BUNDLE_DISABLE_IMFILEDIALOG AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    if(HELLOIMGUI_HAS_OPENGL)
        # ... existing im_file_dialog code ...
    endif()
endif()

# Update imgui_tex_inspect conditional to check for hello_imgui
# (Find the existing imgui_tex_inspect section and wrap it)
if(NOT IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    if(HELLOIMGUI_HAS_OPENGL)
        # ... existing imgui_tex_inspect code ...
    endif()
endif()

# Update immapp conditional
# (Find "add_subdirectory(immapp/immapp)" and wrap it)
if(NOT IMGUI_BUNDLE_DISABLE_IMMAPP AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    add_subdirectory(immapp/immapp)
    target_link_libraries(immapp PUBLIC imgui_bundle)
    set(IMGUI_BUNDLE_WITH_IMMAPP ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMMAPP)
else()
    message(STATUS "Skipping immapp (disabled or hello_imgui not available)")
endif()
```

### 4. Update Python __init__.py Conditional Imports

**File**: `bindings/imgui_bundle/__init__.py`

**Actions**:
- Ensure hello_imgui imports are properly guarded (already done via `has_submodule`)
- **FIX CRITICAL BUG**: The `hello_imgui.override_assets_folder()` call at line ~192 is unconditional and will crash if hello_imgui is disabled
- Ensure immapp imports are properly guarded (already done)
- Wrap all hello_imgui-dependent code in conditional blocks

**Location**: Search for "hello_imgui.override_assets_folder"

**Implementation**:
```toml
# Add these comments in the pyproject.toml file after the existing tool.cibuildwheel section:

# ═══════════════════════════════════════════════════════════════════════════
# Custom Build Configurations
# ═══════════════════════════════════════════════════════════════════════════
# You can customize which modules are included in the wheel using environment
# variables or CMAKE_ARGS during pip install.
#
# EXAMPLES:
#
# 1. Minimal build (no window management, no heavy dependencies):
#    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install .
#
# 2. Exclude specific modules:
#    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_NANOVG=ON -DIMGUI_BUNDLE_DISABLE_IMMVISION=ON" pip install .
#
# 3. Using environment variables (cleaner for multiple options):
#    export IMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON
#    export IMMVISION_FETCH_OPENCV=OFF
#    pip install .
#
# 4. Development build with specific modules:
#    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e . -v
#
# ═══════════════════════════════════════════════════════════════════════════
# cibuildwheel Configuration for Custom Wheel Variants
# ═══════════════════════════════════════════════════════════════════════════
#
# To build custom wheel variants in CI, you can create overrides:
#
# Example 1: Minimal wheels for Linux (uncomment to use):
# [[tool.cibuildwheel.overrides]]
# select = "*-manylinux*"
# environment = {
#     IMGUI_BUNDLE_DISABLE_HELLO_IMGUI="ON",
#     IMMVISION_FETCH_OPENCV="OFF",
#     IMGUI_BUNDLE_DISABLE_NANOVG="ON"
# }
#
# Example 2: No OpenCV variant:
# [[tool.cibuildwheel.overrides]]
# select = "*"
# environment = { IMMVISION_FETCH_OPENCV="OFF" }
#
# ═══════════════════════════════════════════════════════════════════════════
```

### 5. Handle Python immapp Package

**File**: `bindings/imgui_bundle/immapp/__init__.py`

**Actions**:
- Verify that the Python `immapp` package properly handles missing `immapp_cpp` module
- The package should gracefully degrade if `immapp_cpp` is not available

**Current State**: The immapp Python package is already guarded by `has_submodule("immapp_cpp")` in the main `__init__.py`, so it should be safe. However, we should verify that importing `from imgui_bundle import immapp` when immapp_cpp is missing doesn't crash.

**Implementation**: No changes needed if current guards are sufficient. If issues arise during testing, add additional guards in `bindings/imgui_bundle/immapp/__init__.py`.

### 6. Extend pyproject.toml

**File**: `pyproject.toml`

**Actions**:
- Document how to use environment variables to control builds
- Add examples in comments showing different build configurations
- Add concrete cibuildwheel configuration examples

**Location**: Add after the tool.cibuildwheel section

**Actions**:
- Create or update documentation showing:
    - How to build minimal wheels
    - How to build for "library only" use case (no window management)
    - List of available disable flags and their dependencies
    - Examples for different use cases


### 7. Create Documentation File

**File**: Create `docs/custom_wheel_builds.md` (new file)

**Actions**:
- Create comprehensive documentation for custom wheel builds
- Include dependency graph
- Provide concrete examples for common use cases
- Document all available disable flags

**Implementation**:
```python
# Find the section that adds async support to hello_imgui (search for "hello_imgui_run_async")
# Wrap ALL hello_imgui-dependent code including the assets folder override:

if has_submodule("hello_imgui"):
    from imgui_bundle.hello_imgui_run_async import run_async as _hello_imgui_run_async
    hello_imgui.run_async = _hello_imgui_run_async  # type: ignore

    # Add notebook convenience API
    from imgui_bundle import hello_imgui_nb as _hello_imgui_nb_module
    hello_imgui.nb = _hello_imgui_nb_module  # type: ignore

    # Override assets folder (CRITICAL: this was previously unconditional!)
    import os
    THIS_DIR = os.path.dirname(__file__)
    hello_imgui.override_assets_folder(THIS_DIR + "/assets")
```


**Content** (`docs/custom_wheel_builds.md`):

```markdown
# Custom Wheel Builds for ImGui Bundle

This guide explains how to build custom Python wheels for ImGui Bundle with selective module inclusion/exclusion.

## Overview

ImGui Bundle allows you to customize which modules are included during the build process. This enables:
- **Smaller wheel sizes** by excluding unnecessary modules
- **Reduced dependencies** (e.g., no OpenCV)
- **Library-only mode** for users with their own window management

## Module Dependencies

Understanding module dependencies is critical:

```
hello_imgui (window management + OpenGL context)
├── immapp (depends on hello_imgui)
│   ├── immapp_cpp (C++ bindings)
│   └── immapp (Python package)
├── im_file_dialog (needs OpenGL from hello_imgui)
├── imgui_tex_inspect (needs OpenGL from hello_imgui)
├── imgui_test_engine (needs GIL management from hello_imgui)
└── GLFW backend (no point without hello_imgui)

Independent modules (work without hello_imgui):
├── Dear ImGui core (always included)
├── implot
├── implot3d
├── imgui_node_editor
├── imgui_knobs
├── nanovg (has its own OpenGL context)
├── imguizmo
├── imgui_toggle
├── portable_file_dialogs
└── other widget libraries
```

**Important**: When you disable hello_imgui, all dependent modules are automatically disabled.

## Use Cases

#### 1. Library Only Mode (No Window Management)

If you have your own window management and rendering backend:

```bash
CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e .
```

This disables:
- hello_imgui (window management)
- immapp (high-level app framework)
- GLFW backend
- Modules that depend on hello_imgui's OpenGL context:
  - im_file_dialog
  - imgui_tex_inspect

You'll still get:
- Dear ImGui core
- implot, implot3d
- imgui_node_editor
- imgui_knobs
- All other widget libraries

#### 2. Minimal Dependencies (No OpenCV)

To exclude OpenCV and immvision:

```bash
export IMMVISION_FETCH_OPENCV=OFF
pip install -e .
```

Or:

```bash
CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_IMMVISION=ON" pip install -e .
```

#### 3. Exclude Specific Modules

```bash
CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_NANOVG=ON -DIMGUI_BUNDLE_DISABLE_IMPLOT3D=ON" pip install -e .
```

### Available Disable Flags

- `IMGUI_BUNDLE_DISABLE_HELLO_IMGUI` - Disables window management (auto-disables immapp, glfw)
- `IMGUI_BUNDLE_DISABLE_IMMAPP` - Disables high-level app framework
- `IMGUI_BUNDLE_DISABLE_IMMVISION` - Disables immvision (excludes OpenCV dependency)
- `IMGUI_BUNDLE_DISABLE_NANOVG` - Disables NanoVG vector graphics
- `IMGUI_BUNDLE_DISABLE_IMPLOT` - Disables ImPlot plotting library
- `IMGUI_BUNDLE_DISABLE_IMPLOT3D` - Disables ImPlot3D
- `IMGUI_BUNDLE_DISABLE_IMGUI_NODE_EDITOR` - Disables node editor
- `IMGUI_BUNDLE_DISABLE_IMGUIZMO` - Disables ImGuizmo
- `IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT` - Disables texture inspector
- `IMGUI_BUNDLE_DISABLE_IMFILEDIALOG` - Disables file dialog
- `IMMVISION_FETCH_OPENCV=OFF` - Don't fetch/build OpenCV (alternative to disable immvision)

### Building Custom Wheels with cibuildwheel

In `pyproject.toml`:

```toml
[[tool.cibuildwheel.overrides]]
select = "*linux*"
environment = {
    IMGUI_BUNDLE_DISABLE_HELLO_IMGUI="ON",
    IMMVISION_FETCH_OPENCV="OFF"
}
```

## Verification After Build

After building with custom options, verify the configuration:

```python
from imgui_bundle import has_submodule

print("hello_imgui available:", has_submodule("hello_imgui"))
print("immapp available:", has_submodule("immapp_cpp"))
print("implot available:", has_submodule("implot"))
print("immvision available:", has_submodule("immvision"))

# List all available modules
from imgui_bundle._imgui_bundle import __bundle_submodules__
print("\nAvailable modules:", __bundle_submodules__)
```

## Troubleshooting

**Problem**: Import fails after disabling hello_imgui
**Solution**: Ensure you're not importing hello_imgui directly. Use `has_submodule("hello_imgui")` to check availability first.

**Problem**: Wheel size didn't decrease significantly
**Solution**: Check that dependencies were actually excluded. The build log should show "Auto-disabled" messages.

**Problem**: Module X doesn't work without hello_imgui
**Solution**: Check the dependency graph above. Some modules require hello_imgui's OpenGL context.
```

**Also update the main README**: Add a link to this documentation in the main README.md under installation instructions.

## Further Considerations

### 1. Dependency Validation

**Question**: Should the build system warn or fail if someone tries to disable hello_imgui but enable modules that depend on it?

**Recommendation**: Auto-disable dependent modules and emit warnings (already covered in Step 1).
=> Agreed

**Implementation Status**: Handled in CMakeLists.txt dependency chain logic.

### 2. Multiple Wheel Variants

**Question**: Should this project maintain separate PyPI packages (e.g., `imgui-bundle-minimal`) or rely on users building custom wheels?

**Recommendation**:
- Official PyPI wheels remain full-featured (current behavior)
- Document custom builds for users who need minimal variants
- Power users can fork and publish their own minimal variants if desired
- Could consider CI jobs to build and test minimal configurations (but not necessarily publish them)

**Rationale**: Multiple package variants increase maintenance burden significantly. Better to provide the tools and documentation for users to build what they need.

=> Let's add a CI job to test minimal builds

### 3. Test Coverage

**Question**: How should the test suite handle optional modules?

**Recommendation**: Use `pytest.mark.skipif(not has_submodule("module"))` to conditionally skip tests for disabled modules.

**Implementation**:

```python
# In test files
import pytest
from imgui_bundle import has_submodule

@pytest.mark.skipif(not has_submodule("hello_imgui"), reason="hello_imgui not available")
def test_hello_imgui_feature():
    from imgui_bundle import hello_imgui
    # test code...

@pytest.mark.skipif(not has_submodule("immvision"), reason="immvision not available")
def test_immvision_feature():
    from imgui_bundle import immvision
    # test code...
```

### 4. Minimal ImGui Build

**Resolution**: ✅ Handled in Step 3

The `imgui_bundle_cmake/internal/add_imgui.cmake` file provides the `add_imgui()` function that builds imgui standalone. When hello_imgui is disabled, we use this to build from `external/imgui/imgui` (which contains Python binding modifications) instead of the version bundled with hello_imgui.

### 5. CI/CD Implementation

**Actions**:
- Add CI job to test minimal build configuration
- Add CI job to test library-only mode
- Ensure tests pass with various module combinations

**File**: Create `.github/workflows/test_custom_builds.yml`

**Implementation**:

```yaml
name: Test Custom Build Configurations

on:
  pull_request:
    paths:
      - 'CMakeLists.txt'
      - 'external/CMakeLists.txt'
      - 'imgui_bundle_cmake/**'
      - '.github/workflows/test_custom_builds.yml'
  workflow_dispatch:

jobs:
  test-minimal-build:
    name: Test Minimal Build (No hello_imgui)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build minimal wheel
        run: |
          CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e . -v

      - name: Verify configuration
        run: |
          python -c "from imgui_bundle import has_submodule; \
            assert not has_submodule('hello_imgui'), 'hello_imgui should be disabled'; \
            assert not has_submodule('immapp_cpp'), 'immapp should be auto-disabled'; \
            assert has_submodule('implot'), 'implot should be available'; \
            print('✓ Minimal build configuration verified')"

      - name: Run tests
        run: |
          pip install pytest
          pytest tests/ -m "not requires_hello_imgui" -v

  test-no-opencv:
    name: Test Without OpenCV
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build without OpenCV
        run: |
          CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_IMMVISION=ON" pip install -e . -v

      - name: Verify configuration
        run: |
          python -c "from imgui_bundle import has_submodule; \
            assert not has_submodule('immvision'), 'immvision should be disabled'; \
            assert has_submodule('hello_imgui'), 'hello_imgui should be available'; \
            print('✓ No OpenCV build configuration verified')"

  test-multiple-disables:
    name: Test Multiple Disabled Modules
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build with multiple disables
        env:
          IMGUI_BUNDLE_DISABLE_NANOVG: "ON"
          IMGUI_BUNDLE_DISABLE_IMPLOT3D: "ON"
          IMMVISION_FETCH_OPENCV: "OFF"
        run: |
          pip install -e . -v

      - name: Verify configuration
        run: |
          python -c "from imgui_bundle import has_submodule; \
            assert not has_submodule('nanovg'), 'nanovg should be disabled'; \
            assert not has_submodule('implot3d'), 'implot3d should be disabled'; \
            assert not has_submodule('immvision'), 'immvision should be disabled'; \
            assert has_submodule('implot'), 'implot should be available'; \
            print('✓ Multiple disables configuration verified')"
```

## Implementation Order

Follow these steps in order for a systematic implementation:

1. **Step 0**: Create environment variable handling macro in `imgui_bundle_build_lib.cmake`
2. **Step 1**: Add CMake options and dependency chain logic in `CMakeLists.txt`
3. **Step 3**: Update `external/CMakeLists.txt` to conditionally build modules (includes minimal imgui build)
4. **Step 2**: Update `pybind_imgui_bundle.cpp` conditionals
5. **Step 4**: Fix critical bug in `__init__.py` (unconditional hello_imgui call)
6. **Step 5**: Verify `immapp` Python package handling
7. **Step 6**: Add documentation to `pyproject.toml`
8. **Step 7**: Create `docs/custom_wheel_builds.md` with full documentation
9. **Further Consideration 3**: Add test markers and conditional tests
10. **Further Consideration 5**: Create and add CI workflow file for testing custom builds

### After Implementation Checklist

- [ ] All CMake files updated with conditionals
- [ ] All C++ files updated with preprocessor directives
- [ ] Python files handle missing modules gracefully
- [ ] Documentation created and linked from README
- [ ] CI workflow created
- [ ] Manual testing completed (see Testing Strategy below)

## Testing Strategy

After implementation, systematically test the following configurations.

### Manual Testing Configurations

Create a test script `test_configuration.py`:

```python
#!/usr/bin/env python3
"""Verify imgui_bundle build configuration."""

from imgui_bundle import has_submodule, __bundle_submodules__

def test_configuration():
    print("=" * 60)
    print("ImGui Bundle Configuration Verification")
    print("=" * 60)

    modules = [
        "hello_imgui", "immapp_cpp", "implot", "implot3d",
        "immvision", "nanovg", "imgui_node_editor", "imguizmo",
        "im_file_dialog", "imgui_tex_inspect", "with_glfw"
    ]

    print("\nModule Availability:")
    for module in modules:
        status = "✓ AVAILABLE" if has_submodule(module) else "✗ DISABLED"
        print(f"  {module:30} {status}")

    print(f"\nTotal modules: {len(__bundle_submodules__)}")
    print("\nAll registered modules:")
    for mod in sorted(__bundle_submodules__):
        print(f"  - {mod}")

    # Test imports
    print("\nTesting imports...")
    try:
        from imgui_bundle import imgui
        print("  ✓ imgui (core) imported successfully")
    except ImportError as e:
        print(f"  ✗ imgui import failed: {e}")
        return False

    if has_submodule("hello_imgui"):
        try:
            from imgui_bundle import hello_imgui
            print("  ✓ hello_imgui imported successfully")
        except ImportError as e:
            print(f"  ✗ hello_imgui import failed: {e}")
            return False

    if has_submodule("implot"):
        try:
            from imgui_bundle import implot
            print("  ✓ implot imported successfully")
        except ImportError as e:
            print(f"  ✗ implot import failed: {e}")
            return False

    print("\n" + "=" * 60)
    print("Configuration verification PASSED")
    print("=" * 60)
    return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_configuration() else 1)
```

### Test Each Configuration

Run these builds and verify with the script above:

1. **Full build** (default):
   ```bash
   pip uninstall -y imgui_bundle
   pip install -e . -v
   python test_configuration.py
   ```

2. **Library-only mode** (no hello_imgui):
   ```bash
   pip uninstall -y imgui_bundle
   CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e . -v
   python test_configuration.py
   # Should show: hello_imgui ✗ DISABLED, immapp_cpp ✗ DISABLED, implot ✓ AVAILABLE
   ```

3. **No immvision** (no OpenCV):
   ```bash
   pip uninstall -y imgui_bundle
   IMMVISION_FETCH_OPENCV=OFF pip install -e . -v
   python test_configuration.py
   # Should show: immvision ✗ DISABLED
   ```

4. **No nanovg**:
   ```bash
   pip uninstall -y imgui_bundle
   CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_NANOVG=ON" pip install -e . -v
   python test_configuration.py
   # Should show: nanovg ✗ DISABLED
   ```

5. **Multiple disables**:
   ```bash
   pip uninstall -y imgui_bundle
   export IMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON
   export IMGUI_BUNDLE_DISABLE_NANOVG=ON
   export IMMVISION_FETCH_OPENCV=OFF
   pip install -e . -v
   python test_configuration.py
   ```

### Verify Each Configuration

For each configuration above:
- ✅ Wheel builds successfully (no compilation errors)
- ✅ `has_submodule()` returns correct values for all modules
- ✅ Imports work correctly (present modules import, absent modules gracefully skipped)
- ✅ CMake output shows expected "Auto-disabled" messages
- ✅ Build log shows correct modules being compiled
- ✅ Wheel size is appropriate (smaller for minimal builds)
- ✅ Run test script passes

## Success Criteria

- ✅ User can build wheel without hello_imgui using `CMAKE_ARGS`
- ✅ User can build wheel without immvision/OpenCV
- ✅ User can build wheel without specific widget libraries
- ✅ Python code gracefully handles missing modules
- ✅ Dependencies are auto-disabled when required (e.g., immapp when hello_imgui is disabled)
- ✅ Clear documentation exists for all disable flags
- ✅ Tests pass for various build configurations
- ✅ Wheel size is reduced appropriately when modules are excluded

