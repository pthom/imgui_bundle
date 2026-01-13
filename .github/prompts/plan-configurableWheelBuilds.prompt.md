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


## Steps

### 1. Add New CMake Options for Python-Specific Disables

**File**: `CMakeLists.txt` (around line 147-154, where other `IMGUI_BUNDLE_DISABLE_*` options are defined)

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
# Around line 154, after existing IMGUI_BUNDLE_DISABLE options
option(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI "Disable hello_imgui" OFF)
option(IMGUI_BUNDLE_DISABLE_IMMAPP "Disable immapp (internal lib)" OFF)


# Dependency chain logic (add this around line 200, after backend options)
if(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    message(STATUS "IMGUI_BUNDLE_DISABLE_HELLO_IMGUI is ON - auto-disabling dependent modules")
    set(IMGUI_BUNDLE_DISABLE_IMMAPP ON CACHE BOOL "Auto-disabled due to HELLO_IMGUI disable" FORCE)
    set(IMGUI_BUNDLE_DISABLE_IMFILEDIALOG ON CACHE BOOL "Auto-disabled due to HELLO_IMGUI disable" FORCE)
    set(IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT ON CACHE BOOL "Auto-disabled due to HELLO_IMGUI disable" FORCE)
    set(HELLOIMGUI_USE_GLFW3 OFF CACHE BOOL "Auto-disabled due to HELLO_IMGUI disable" FORCE)
    set(HELLOIMGUI_HAS_OPENGL3 OFF CACHE BOOL "Auto-disabled due to HELLO_IMGUI disable" FORCE)
endif()
Note for claude: imgui_test_engine should probably be disabled too if hello_imgui is disabled. Add that as well (with an explanatory message like: "imgui_test_engine requires careful GIL context switching between c++ and python, which is implemented only in hello imgui"). (please ask for clarification if needed)


# For Python builds, allow environment variables to set these options
if(IMGUI_BUNDLE_BUILD_PYTHON)
    if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_HELLO_IMGUI})
        set(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI "$ENV{IMGUI_BUNDLE_DISABLE_HELLO_IMGUI}" CACHE BOOL "" FORCE)
    endif()
    if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_IMMAPP})
        set(IMGUI_BUNDLE_DISABLE_IMMAPP "$ENV{IMGUI_BUNDLE_DISABLE_IMMAPP}" CACHE BOOL "" FORCE)
    endif()
    # Extend for other disable options
    if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_NANOVG})
        set(IMGUI_BUNDLE_DISABLE_NANOVG "$ENV{IMGUI_BUNDLE_DISABLE_NANOVG}" CACHE BOOL "" FORCE)
    endif()
    if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_IMPLOT})
        set(IMGUI_BUNDLE_DISABLE_IMPLOT "$ENV{IMGUI_BUNDLE_DISABLE_IMPLOT}" CACHE BOOL "" FORCE)
    endif()
    # ... add more as needed
endif()

Note for Claude: please create a macro or function for this in imgui_bundle_cmake/imgui_bundle_build_lib.cmake and call it to keep the CMakeLists.txt clean.


```

### 2. Update pybind_imgui_bundle.cpp Conditionals

**File**: `external/bindings_generation/cpp/pybind_imgui_bundle.cpp`

**Actions**:
- Wrap `hello_imgui` module registration (lines 76-78) with `#ifndef IMGUI_BUNDLE_DISABLE_HELLO_IMGUI`
- Wrap `immapp_cpp` module registration (lines 153-155) with `#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP`
- Ensure `_register_submodule()` calls are also wrapped
- Add conditional for `with_glfw` registration (line 172-174)

**Implementation**:
```cpp
// Around line 76
#ifndef IMGUI_BUNDLE_DISABLE_HELLO_IMGUI
    _register_submodule("hello_imgui");
    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);
#endif

// Around line 153
#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP
    _register_submodule("immapp_cpp");
    auto module_immapp_cpp = m.def_submodule("immapp_cpp");
    py_init_module_immapp_cpp(module_immapp_cpp);
#endif

// Around line 171-174
#if defined(HELLOIMGUI_USE_GLFW3) && !defined(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    _register_submodule("with_glfw");
#endif
```

### 3. Update external/CMakeLists.txt

**File**: `external/CMakeLists.txt`

**Actions**:
- Wrap the `add_hello_imgui()` call (line 28) with a conditional check for `IMGUI_BUNDLE_DISABLE_HELLO_IMGUI`
- Wrap immapp subdirectory addition (line 270) with conditional for `IMGUI_BUNDLE_DISABLE_IMMAPP`
- Update existing conditionals for im_file_dialog (line 117), imgui_tex_inspect (line 148) to also check for hello_imgui availability

**Implementation**:
```cmake
# Around line 28
if(NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    include(../imgui_bundle_cmake/internal/add_hello_imgui.cmake)
    add_hello_imgui()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
    endif()
    set(IMGUI_BUNDLE_WITH_HELLO_IMGUI ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_HELLO_IMGUI)
else()
    # Still need imgui even without hello_imgui
    # Add minimal imgui build here if needed for "library only" mode
    message(STATUS "Building imgui_bundle without hello_imgui - library only mode")
endif()

# Around line 117 - im_file_dialog already has HELLOIMGUI_HAS_OPENGL check
if(NOT IMGUI_BUNDLE_DISABLE_IMFILEDIALOG AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    if(HELLOIMGUI_HAS_OPENGL)
        # ... existing code ...
    endif()
endif()

# Around line 148 - imgui_tex_inspect
if(NOT IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    if(HELLOIMGUI_HAS_OPENGL)
        # ... existing code ...
    endif()
endif()

# Around line 270 - immapp
if(NOT IMGUI_BUNDLE_DISABLE_IMMAPP AND NOT IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    add_subdirectory(immapp/immapp)
    target_link_libraries(immapp PUBLIC imgui_bundle)
    set(IMGUI_BUNDLE_WITH_IMMAPP ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMMAPP)
else()
    message(STATUS "Building imgui_bundle without immapp")
endif()
```

### 4. Extend pyproject.toml

**File**: `pyproject.toml`

**Actions**:
- Document how to use environment variables to control builds
- Add examples in comments showing different build configurations
- Consider adding build matrix examples for cibuildwheel

**Implementation**:
```toml
# After line 143, add documentation comments:

# Custom Build Configurations
# ============================
# You can customize which modules are included in the wheel using environment variables
# or CMAKE_ARGS during pip install. Examples:
#
# 1. Minimal build (no hello_imgui, no immapp):
#    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install .
#
# 2. Exclude specific modules:
#    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_NANOVG=ON -DIMGUI_BUNDLE_DISABLE_IMMVISION=ON" pip install .
#
# 3. Using environment variables (alternative method):
#    export IMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON
#    export IMMVISION_FETCH_OPENCV=OFF
#    pip install .
#
# 4. For cibuildwheel, use the environment field:
#    environment = {
#        IMGUI_BUNDLE_DISABLE_HELLO_IMGUI="ON",
#        IMMVISION_FETCH_OPENCV="OFF"
#    }

# Example: Build configuration for minimal wheels
# [[tool.cibuildwheel.overrides]]
# select = "*-minimal"
# environment = {
#     IMGUI_BUNDLE_DISABLE_HELLO_IMGUI="ON",
#     IMGUI_BUNDLE_DISABLE_IMMVISION="ON",
#     IMGUI_BUNDLE_DISABLE_NANOVG="ON"
# }
```

### 5. Update __init__.py Conditional Imports

**File**: `bindings/imgui_bundle/__init__.py`

**Actions**:
- Ensure hello_imgui imports (lines 76-79) are already properly guarded - ✓ (already using `has_submodule`)
- Ensure immapp imports (lines 149-152) are properly guarded - ✓ (already using `has_submodule`)
- Update hello_imgui-dependent code (lines 189-192) to be more defensive
- Update the final `hello_imgui.override_assets_folder` call (line 192) to be conditional

**Implementation**:
```python
# Around line 189-192, make these sections conditional
if has_submodule("hello_imgui"):
    from imgui_bundle.hello_imgui_run_async import run_async as _hello_imgui_run_async
    hello_imgui.run_async = _hello_imgui_run_async  # type: ignore

    # Add notebook convenience API
    from imgui_bundle import hello_imgui_nb as _hello_imgui_nb_module
    hello_imgui.nb = _hello_imgui_nb_module  # type: ignore

    # Override assets folder
    import os
    THIS_DIR = os.path.dirname(__file__)
    hello_imgui.override_assets_folder(THIS_DIR + "/assets")
```

### 6. Document Usage Patterns

**Actions**:
- Create or update documentation showing:
  - How to build minimal wheels
  - How to build for "library only" use case (no window management)
  - List of available disable flags and their dependencies
  - Examples for different use cases

**Content**:

```markdown
## Custom Wheel Builds

### Use Cases

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
```

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

**Question**: When hello_imgui is disabled, how do we build just imgui without the full hello_imgui infrastructure?

**Challenge**: Currently, imgui is built as part of hello_imgui. We need a fallback to build imgui standalone.


**Recommendation**:

Note for claude: See imgui_bundle_cmake/internal/add_imgui.cmake: this can be used imgui even without hello_imgui.
(Using the folder external/imgui/imgui, *not* external/hello_imgui/hello_imgui/external/imgui), because this version contains specific modifications for the python bindings.

### 5. CI/CD Considerations

**Actions**:
- Add CI job to test minimal build configuration
- Add CI job to test library-only mode
- Ensure tests pass with various module combinations

**Example GitHub Actions** (pseudo-code):

```yaml
- name: Test minimal build
  run: |
    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e .
    pytest tests/ -m "not requires_hello_imgui"

- name: Test without immvision
  run: |
    CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_IMMVISION=ON" pip install -e .
    pytest tests/ -m "not requires_immvision"
```

## Implementation Order

1. **Step 1**: Add CMake options and environment variable handling
2. **Step 4** (partial): Document the new options in comments
3. **Step 3**: Update external/CMakeLists.txt to respect the new flags
4. **Step 2**: Update pybind_imgui_bundle.cpp conditionals
5. **Step 5**: Update __init__.py (mostly already correct, minor tweaks)
6. **Step 6**: Create full documentation
7. **Further Consideration 4**: Implement minimal imgui build fallback
8. **Further Consideration 3**: Add test markers and conditional tests
9. **Further Consideration 5**: Add CI jobs for testing

## Testing Strategy

After implementation, test the following configurations:

1. **Full build** (default): `pip install -e .`
2. **Library-only mode**: `CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON" pip install -e .`
3. **No immvision**: `IMMVISION_FETCH_OPENCV=OFF pip install -e .`
4. **No nanovg**: `CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_NANOVG=ON" pip install -e .`
5. **Multiple disables**: `CMAKE_ARGS="-DIMGUI_BUNDLE_DISABLE_HELLO_IMGUI=ON -DIMGUI_BUNDLE_DISABLE_NANOVG=ON" pip install -e .`

For each configuration:
- Verify wheel builds successfully
- Verify `has_submodule()` returns correct values
- Verify imports work correctly (present modules import, absent modules gracefully skipped)
- Run relevant subset of tests

## Success Criteria

- ✅ User can build wheel without hello_imgui using `CMAKE_ARGS`
- ✅ User can build wheel without immvision/OpenCV
- ✅ User can build wheel without specific widget libraries
- ✅ Python code gracefully handles missing modules
- ✅ Dependencies are auto-disabled when required (e.g., immapp when hello_imgui is disabled)
- ✅ Clear documentation exists for all disable flags
- ✅ Tests pass for various build configurations
- ✅ Wheel size is reduced appropriately when modules are excluded

