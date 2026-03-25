# Build Guide

This page documents CMake options, presets, the justfile task runner, and common build scenarios.

## CMake presets

The repo ships a `CMakePresets.json` with these presets:

| Preset | Description |
|--------|-------------|
| `default` | Desktop C++ with GLFW + OpenGL3 |
| `default_sdl` | Desktop C++ with SDL2 + OpenGL3 |
| `python_bindings` | Python bindings (forces GLFW + OpenGL3) |
| `all_cpp_options` | Everything enabled: all backends, demos, tests, ImmVision with OpenCV |

Usage:
```bash
mkdir -p builds/my_build && cd builds/my_build
cmake ../.. --preset python_bindings -DPython_EXECUTABLE=$(which python)
cmake --build . -j
```


## Module selection (`IMGUI_BUNDLE_WITH_*`)

Each library can be individually enabled or disabled. All default to ON.

| Option | Library | Notes |
|--------|---------|-------|
| `IMGUI_BUNDLE_WITH_HELLO_IMGUI` | Hello ImGui | Disabling also disables immapp, imgui_md, test_engine |
| `IMGUI_BUNDLE_WITH_IMMAPP` | ImmApp | Depends on hello_imgui + imgui_node_editor |
| `IMGUI_BUNDLE_WITH_IMPLOT` | ImPlot | 2D plotting |
| `IMGUI_BUNDLE_WITH_IMPLOT3D` | ImPlot3D | 3D plotting |
| `IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR` | Node editor | |
| `IMGUI_BUNDLE_WITH_IMGUI_MD` | Markdown | Depends on immapp |
| `IMGUI_BUNDLE_WITH_IMGUIZMO` | ImGuizmo | 3D gizmos |
| `IMGUI_BUNDLE_WITH_NANOVG` | NanoVG | Needs OpenGL3 or Metal |
| `IMGUI_BUNDLE_WITH_IMFILEDIALOG` | ImFileDialog | Needs OpenGL3 |
| `IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT` | Texture inspector | Needs OpenGL3 |
| `IMGUI_BUNDLE_WITH_IMMVISION` | ImmVision | Needs OpenGL3 |
| `IMGUI_BUNDLE_WITH_IMANIM` | ImAnim | Animation library |
| `IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB` | ImGui Explorer | Interactive widget explorer |

**Dependency chain**: CMake automatically disables dependent modules. For example, setting `IMGUI_BUNDLE_WITH_HELLO_IMGUI=OFF` also disables immapp, imgui_md, test_engine, and the GLFW backend.

**Convention**: CMake option names and C++ `#define` names are identical. For example, `IMGUI_BUNDLE_WITH_IMANIM` is both the `option()` and the `#ifdef` guard in C++.

**Legacy options**: `IMGUI_BUNDLE_DISABLE_*` options are deprecated (removal ~January 2028). Use `IMGUI_BUNDLE_WITH_*=OFF` instead.


## Backend selection

You need at least one platform backend and one rendering backend:

**Platform backends:**
| Option | Backend |
|--------|---------|
| `HELLOIMGUI_USE_GLFW3` | GLFW3 (recommended default) |
| `HELLOIMGUI_USE_SDL2` | SDL2 |

**Rendering backends:**
| Option | Backend | Notes |
|--------|---------|-------|
| `HELLOIMGUI_HAS_OPENGL3` | OpenGL3 | Recommended, especially for beginners |
| `HELLOIMGUI_HAS_METAL` | Metal | macOS/iOS only |
| `HELLOIMGUI_HAS_VULKAN` | Vulkan | Advanced |
| `HELLOIMGUI_HAS_DIRECTX11` | DirectX 11 | Windows only, experimental |
| `HELLOIMGUI_HAS_DIRECTX12` | DirectX 12 | Windows only, experimental |

If you make no choice, the default is **GLFW3 + OpenGL3**.

:::{note}
Python bindings always force GLFW3 + OpenGL3. Pyodide forces SDL2 + OpenGL3.
:::


## Other build options

| Option | Default | Description |
|--------|---------|-------------|
| `IMGUI_BUNDLE_BUILD_PYTHON` | OFF (ON via pip) | Build Python bindings |
| `IMGUI_BUNDLE_BUILD_DEMOS` | ON (top-level) | Build C++ demo executables |
| `IMGUI_BUNDLE_BUILD_IMGUI_EXPLORER_APP` | OFF | Build ImGui Explorer standalone app |
| `IMGUI_BUNDLE_INSTALL_CPP` | ON (top-level, non-Python) | Install C++ targets |
| `IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES` | ON | Auto-clone submodules during configure |
| `HELLOIMGUI_WITH_TEST_ENGINE` | ON (desktop) | Include ImGui Test Engine |
| `HELLOIMGUI_USE_FREETYPE` | auto | Use FreeType for font rendering |
| `IMMVISION_FETCH_OPENCV` | OFF | Fetch & build OpenCV for ImmVision |
| `IMGUI_BUNDLE_BUILD_CI_AUTOMATION_TESTS` | OFF | Build CI automation tests |
| `IMGUI_BUNDLE_WITH_IMANIM_FULL_DEMOS` | ON | Include all ImAnim author demos in manual |

**For pip builds**, pass CMake options via the `CMAKE_ARGS` environment variable:
```bash
CMAKE_ARGS="-DIMGUI_BUNDLE_WITH_IMMVISION=OFF" pip install -v -e .
```


## Common build scenarios

### Desktop C++ (minimal)

```bash
mkdir -p builds/desktop && cd builds/desktop
cmake ../.. --preset default
cmake --build . -j
```

### Python bindings with ImmVision

```bash
mkdir -p builds/python && cd builds/python
cmake ../.. --preset python_bindings \
    -DPython_EXECUTABLE=$(which python) \
    -DIMMVISION_FETCH_OPENCV=ON
cmake --build . -j
```

### Emscripten (ImGui Bundle Explorer)

```bash
just ibex_build       # builds into build_ibex_ems/
just ibex_serve       # serve on port 8642
```

Or manually:
```bash
mkdir -p builds/ems && cd builds/ems
source ~/emsdk/emsdk_env.sh
emcmake cmake ../.. -DCMAKE_BUILD_TYPE=Release
make -j
```

### Emscripten (ImGui Explorer, lightweight)

```bash
just imex_ems_build   # builds into build_imex_ems/
just imex_ems_serve   # serve on port 7006, add ?lib=imgui etc. to URL
```

### Pyodide (Python in the browser)

```bash
just pyodide_setup_local_build    # one-time setup
just pyodide_build                # build wheel
just pyodide_test_serve           # serve test page
```

See also `ci_scripts/pyodide_local_build/Readme.md`.

### Offline build (vcpkg)

```bash
git clone https://github.com/microsoft/vcpkg && ./vcpkg/bootstrap-vcpkg.sh
./vcpkg/vcpkg install opencv freetype glfw3 lunasvg
export CMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake
mkdir build && cd build && cmake ..
```


## justfile reference

The `justfile` at the repo root provides shortcuts for common tasks. Run `just` to list all commands.

### Library management (`just libs_*`)

| Command | Description |
|---------|-------------|
| `just libs_info` | Show all libraries with their remotes and branches |
| `just libs_reattach` | Reattach all submodules to branches (fork + official) |
| `just libs_fetch` | Fetch all remotes for all submodules |
| `just libs_pull` | Pull all submodules |
| `just libs_check_upstream` | Check which forks have new upstream changes |
| `just libs_log <name>` | Show new upstream commits for a fork library |
| `just libs_rebase <name>` | Tag and rebase a fork on its upstream |
| `just libs_tag <name>` | Push a date tag to a fork library |
| `just libs_bindings <name>` | Regenerate bindings for one library |
| `just libs_bindings_all` | Regenerate all bindings |

### Build & deploy

| Command | Description |
|---------|-------------|
| `just ibex_build` | Build ImGui Bundle Explorer (Emscripten + OpenCV) |
| `just ibex_serve` | Serve explorer on port 8642 |
| `just ibex_deploy` | Deploy explorer to traineq.org |
| `just imex_ems_build` | Build ImGui Explorer (Emscripten, lightweight) |
| `just imex_ems_serve` | Serve ImGui Explorer on port 7006 |
| `just imex_ems_deploy` | Deploy ImGui Explorer to GitHub Pages |

### Documentation

| Command | Description |
|---------|-------------|
| `just doc_serve_interactive` | Build docs with live reload |
| `just doc_build_static` | Build static HTML |
| `just doc_serve_static` | Serve static HTML on port 7005 |
| `just doc_build_pdf` | Build PDF |

### Testing

| Command | Description |
|---------|-------------|
| `just test_pytest` | Run pytest |
| `just test_mypy` | Run mypy on bindings |

### Pyodide

| Command | Description |
|---------|-------------|
| `just pyodide_setup_local_build` | Install tools for local Pyodide builds |
| `just pyodide_build` | Build Pyodide wheel |
| `just pyodide_test_serve` | Serve browser test page |
| `just pyodide_clean` | Clean Pyodide build artifacts |

### CI / Docker

| Command | Description |
|---------|-------------|
| `just cibuild_docker_musllinux` | Run a musllinux Docker container with repo mounted |
| `just cibuild_docker_manylinux` | Run a manylinux Docker container with repo mounted |
