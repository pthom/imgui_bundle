# Pyodide Local Build Environment

## Goal

This folder contains tools for building imgui-bundle as a Pyodide package locally (out-of-tree).

**Recommended usage:** Use the `justfile` targets from the repository root for a streamlined workflow.

**What's included:**
- Python virtual environment with `pyodide-build` installed
- Emscripten SDK (emsdk) with the correct version for Pyodide
- Setup and build scripts
- Browser testing infrastructure

## Directory Structure

```
ci_scripts/pyodide_local_build/
├── Readme.md                      # This file
├── config_versions_pyodide.sh     # Version configuration (edit this to change versions)
├── setup_pyodide_local_build.sh   # Automated setup script
├── .gitignore                     # Ignores venv_pyo/ and emsdk/
├── test_browser/                  # Browser testing tools and HTML test pages
├── venv_pyo/                      # Python virtual environment (created during setup)
└── emsdk/                         # Emscripten SDK (created during setup)
```

Both `venv_pyo/` and `emsdk/` are gitignored and must be set up locally.


## Configuration

**Before setup**, you can customize versions by editing `config_versions_pyodide.sh`:

```bash
# Pyodide version to use (determines ABI compatibility)
PYODIDE_VERSION="0.29.3"

# Python version (major.minor, e.g., "3.13", "3.12", "3.11")
PYTHON_VERSION="3.13"
```

This central configuration file is used by all build scripts in this directory.


## Setup Instructions

### Quick Setup (Recommended)

From the repository root, use the justfile target:

```bash
just pyodide_setup_local_build
```

This will automatically set up the complete build environment.

### Manual Setup

Alternatively, run the setup script directly:

```bash
cd ci_scripts/pyodide_local_build
./setup_pyodide_local_build.sh
```

The setup script will:
1. Load version configuration from `config_versions_pyodide.sh`
2. Create the Python virtual environment (`venv_pyo/`)
3. Install `pyodide-build`
4. Install the Pyodide cross-compilation toolchain (xbuildenv)
5. Clone and configure Emscripten SDK with the correct version
6. Download the Pyodide distribution for browser testing
7. Verify the installation

**Reference:** https://pyodide.org/en/stable/development/building-packages.html



## Building imgui-bundle

### Quick Build (Recommended)

From the repository root, use the justfile target:

```bash
just pyodide_build
```

This automatically:
1. Activates the virtual environment
2. Sources the Emscripten environment
3. Builds the wheel with `pyodide build`
4. Fixes the wheel name on macOS (workaround for scikit-build-core issue #920)
5. Copies the wheel to `test_browser/local_wheels/` for testing

### Manual Build

If you prefer to run steps manually:

```bash
# 1. Activate environments
source ci_scripts/pyodide_local_build/venv_pyo/bin/activate
source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh

# 2. Build from repository root
cd ../..  # Go to imgui_bundle root
pyodide build
```

## Output

After building, you'll find the wheel in the `dist/` directory:

```
dist/imgui_bundle-X.Y.Z-cp313-cp313-pyodide_2025_0_wasm32.whl
```


## Browser Testing

Test your locally built wheel in a browser with Pyodide:

```bash
just pyodide_test_serve
```

This starts a CORS-enabled web server at http://localhost:8123/ with three test pages:
- `test_local_pyodide.html` - Local Pyodide + local wheel
- `test_cdn_pyodide_local_wheel.html` - CDN Pyodide + local wheel
- `test_cdn_all.html` - Full CDN (official Pyodide package)

See `test_browser/` directory for more details.


## Cleanup

Remove build artifacts:
```bash
just pyodide_clean
```

Deep clean (removes build artifacts, downloaded Pyodide distribution, and build environment):
```bash
just pyodide_deep_clean
```


## References

- **Pyodide Build Docs**: https://pyodide.org/en/stable/development/building-packages.html
- **Pyodide ABI**: https://pyodide.org/en/stable/development/abi.html
- **Emscripten SDK**: https://emscripten.org/docs/getting_started/downloads.html
- **scikit-build-core issue #920**: https://github.com/scikit-build/scikit-build-core/issues/920

