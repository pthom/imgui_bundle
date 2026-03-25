# Getting Started (Developer)

This guide gets you from a fresh clone to a working build with demos and tests. It targets contributors and developers who want to build imgui_bundle from source.

:::{tip}
If you just want to **use** imgui_bundle as a Python package, run `pip install imgui-bundle` and see the [Python install guide](../python/python_install.md). This page is for people who want to **build and modify** the library itself.
:::

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| **git** | any recent | With submodule support |
| **CMake** | >= 3.18 | |
| **C++ compiler** | C++17 | GCC 9+, Clang 10+, MSVC 2019+, or Apple Clang 12+ |
| **Python** | >= 3.8 | Only needed if building Python bindings |
| **just** | any | Optional but recommended — task runner for common commands (`brew install just` / `cargo install just`) |

**Linux only:** install `libglfw3-dev` (or pass `-DHELLOIMGUI_DOWNLOAD_GLFW_IF_NEEDED=ON`).

## Clone & init submodules

```bash
git clone --recursive https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
```

If you already cloned without `--recursive`:
```bash
git submodule update --init --recursive
```

Submodules are auto-cloned during CMake configure by default (via `IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES=ON`), so this step is often optional.


## Quick build: C++ only (desktop)

```bash
mkdir -p builds/my_build && cd builds/my_build
cmake ../.. --preset default
cmake --build . -j
```

This builds with GLFW + OpenGL3 (the default). Run the demos:
```bash
./demo_imgui_bundle          # Main demo showcasing all libraries
```

## Quick build: Python bindings

```bash
# Create a venv
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt   # numpy, pytest, mypy, etc.

# Build
mkdir -p builds/my_python && cd builds/my_python
cmake ../.. --preset python_bindings -DPython_EXECUTABLE=$(which python)
cmake --build . -j
```

Then set your `PYTHONPATH` to include the build output, and run:
```bash
cd ../..
python bindings/imgui_bundle/demos_python/demos_immapp/demo_hello_world.py
```

:::{note}
Python bindings force GLFW + OpenGL3 as the backend. For other backends, build C++ only.
:::

### Alternative: editable pip install

For a development workflow where changes are picked up without rebuilding manually:
```bash
pip install -v -e .
```

This uses scikit-build-core under the hood and takes longer the first time.

## Build with ImmVision (OpenCV)

ImmVision works without OpenCV (using `ImageBuffer` / numpy arrays). To also enable `cv::Mat` interop:

```bash
cmake ../.. --preset python_bindings \
    -DPython_EXECUTABLE=$(which python) \
    -DIMMVISION_FETCH_OPENCV=ON
```

This fetches and builds a minimal OpenCV in the build directory. See [build_opencv_immvision.md](build_opencv_immvision.md) for platform-specific details.


## Run the tests

```bash
# From the repo root
just test_pytest    # Run pytest
just test_mypy      # Run mypy type checking on bindings
```

Or without `just`:
```bash
pytest
cd bindings && ./mypy_bindings.sh
```

See [testing.md](testing.md) for details on GUI tests and CI.


## Build the docs

```bash
just doc_serve_interactive    # Live-reload dev server
# or
just doc_build_static         # Static HTML build
just doc_serve_static         # Serve the static build on port 7005
```

## Useful justfile commands

Run `just` (no arguments) to see all available commands. Key groups:

| Command | What it does |
|---------|-------------|
| `just libs_info` | Show all external libraries with their remotes and branches |
| `just libs_bindings <name>` | Regenerate Python bindings for one library |
| `just libs_bindings_all` | Regenerate all Python bindings |
| `just libs_check_upstream` | Check which fork libraries have new upstream changes |
| `just test_pytest` | Run pytest |
| `just test_mypy` | Run mypy on bindings |
| `just doc_serve_interactive` | Build & serve docs with live reload |

See [build_guide.md](build_guide.md) for the full command reference.

## What next?

| I want to... | See |
|---|---|
| Understand the folder layout | [Repository structure](structure.md) |
| Learn about the build system & CMake options | [Build guide](build_guide.md) |
| Understand how bindings are generated | [Bindings introduction](bindings_intro.md) |
| Update an existing library's bindings | [Update bindings](bindings_update.md) |
| Add a new C++ library to the bundle | [Add new library](bindings_newlib.md) |
| Debug native C++ code from Python | [Debug bindings](bindings_debug.md) |
| Run and write tests | [Testing](testing.md) |
| Deploy to PyPI | [PyPI deployment](pypi_deploy.md) |
| Build with OpenCV / ImmVision | [OpenCV build guide](build_opencv_immvision.md) |
