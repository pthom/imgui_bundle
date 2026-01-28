# Plan: Docker-Based Pyodide Build System for imgui-bundle

Create a Docker-based build environment to compile imgui-bundle for Pyodide on Linux, addressing the macOS scikit-build-core limitation. The solution will provide a persistent container with pre-installed build tools, mounted source code, automated build triggers, and local testing capabilities.

## Steps

1. **Create Dockerfile and directory structure** in `ci_scripts/docker_pyodide/` with:
   - `Dockerfile` - Base image with all build dependencies
   - `docker_pyodide.py` - Container management script (adapted from `docker_ubuntu_dev/docker_run.py`)
   - `build_imgui_bundle.sh` - Build script to run inside container
   - `test_pyodide.html` - HTML test file for browser testing
   - `serve_test.py` - HTTP server with CORS headers for testing
   
   No symlinks to parent imgui_bundle to avoid infinite recursion.

2. **Build base Docker image** with:
   - Ubuntu base with Python 3.13 (matches Pyodide's `Makefile.env`)
   - Build tools: cmake, ninja, git, ccache
   - Clone and build Pyodide repository (includes emsdk)
   - Clone pyodide-recipes repository
   - Create venv with pyodide-build installed
   
   Python version is dictated by Pyodide; may need updates if Pyodide changes.

3. **Implement container management script** (`docker_pyodide.py`) with commands:
   - `build` - Build Docker image and create container
   - `bash` - Interactive shell in container
   - `exec <cmd>` - Run command in container
   - `build-package` - Build imgui-bundle wheel (updates meta.yaml, runs pyodide build-recipes)
   - `extract-dist` - Copy built wheel and pyodide dist files to host
   - `serve` - Start local test server
   - `remove` / `remove_image` - Cleanup commands
   
   Adapted from `docker_ubuntu_dev/docker_run.py`, removing VNC code, adding pyodide-specific commands.

4. **Configure volume mounts**:
   - Host `imgui_bundle/` → Container `/mnt/imgui_bundle` (read-only source)
   - Host `ci_scripts/docker_pyodide/output/` → Container `/mnt/output` (build artifacts)
   
   Pyodide and pyodide-recipes are cloned inside the container during image build (not mounted).

5. **Add build automation** (`build_imgui_bundle.sh`):
   - Source emsdk environment
   - Extract version from `/mnt/imgui_bundle/pyproject.toml`
   - Update `meta.yaml` with source path and version automatically
   - Run `pyodide build-recipes imgui-bundle --recipe-dir ... --install`
   - Copy wheel from `pyodide/dist/` to `/mnt/output/`
   - Copy pyodide runtime files needed for testing

6. **Create test infrastructure**:
   - `test_pyodide.html` - Loads local pyodide.js and imgui-bundle wheel
   - `serve_test.py` - Python HTTP server with CORS headers
   - Test at `http://localhost:8000/test_pyodide.html`

## Decisions

1. **Cache strategy**: ccache installed in image; scikit-build-core uses it automatically. Pyodide build artifacts persist in container between runs.

2. **Version management**: Build script automatically extracts version from `pyproject.toml` and updates `meta.yaml` before each build.

3. **Multi-platform**: ARM64 Docker on M4 Mac is fine - emscripten produces platform-independent wasm32 code. Wheels named `*-pyodide_2025_0_wasm32`.

4. **Integration**: Python script (`docker_pyodide.py`) sufficient for now. Justfile integration deferred.

## Directory Structure

```
ci_scripts/docker_pyodide/
├── Dockerfile
├── docker_pyodide.py        # Container management
├── build_imgui_bundle.sh    # Build script (runs inside container)
├── test_pyodide.html        # Browser test page
├── serve_test.py            # Local test server
├── Readme.md                # Usage documentation
└── output/                  # Created at runtime
    ├── imgui_bundle-*.whl   # Built wheel
    └── pyodide_dist/        # Pyodide runtime for testing
```

## Questions:

Python version is dictated by Pyodide; may need updates if Pyodide changes.
=> How to handle Python version updates in the Dockerfile when Pyodide updates its required Python version?

