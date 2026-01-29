# Pyodide Local Build Environment

## Goal

This folder contains tools for building imgui-bundle as a Pyodide package locally (out-of-tree).

**What's included:**
- Python virtual environment with `pyodide-build` installed
- Emscripten SDK (emsdk) with the correct version for Pyodide
- Setup scripts for installation
- Build scripts for creating wheels

## Directory Structure

```
ci_scripts/pyodide_local_build/
├── Readme.md                      # This file
├── config_versions_pyodide.sh     # Version configuration (edit this to change versions)
├── setup_pyodide_local_build.sh   # Automated setup script
├── .gitignore                     # Ignores venv_pyo/ and emsdk/
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

Run the provided setup script, which follows best practices from
https://pyodide.org/en/stable/development/building-packages.html

```bash
cd ci_scripts/pyodide_local_build
./setup_pyodide_local_build.sh
```

This script will:
1. Load version configuration from `config_versions_pyodide.sh`
2. Create the Python virtual environment (`venv_pyo/`)
3. Install `pyodide-build`
4. Install the Pyodide cross-compilation toolchain (xbuildenv)
5. Clone and configure Emscripten SDK with the correct version
6. Verify the installation



## Building imgui-bundle

### Quick Build (Recommended)

From the repository root, use the justfile target:

```bash
# From imgui_bundle root directory
just pyodide_build
```

This automatically:
1. Activates the virtual environment
2. Sources the Emscripten environment
3. Builds the wheel with `pyodide build`
4. Fixes the wheel name on macOS (workaround for scikit-build-core issue)

### Manual Build

If you prefer to run steps manually:

```bash
# 1. Activate environments
source ci_scripts/pyodide_local_build/venv_pyo/bin/activate
source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh

# 2. Build from repository root
cd ../..  # Go to imgui_bundle root
pyodide build

# 3. Fix wheel name (macOS only)
python ci_scripts/fix_pyodide_wheel_name.py
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


## References

- **Pyodide Build Docs**: https://pyodide.org/en/stable/development/building-packages.html
- **Pyodide ABI**: https://pyodide.org/en/stable/development/abi.html
- **Emscripten SDK**: https://emscripten.org/docs/getting_started/downloads.html
- **scikit-build-core issue #920**: https://github.com/scikit-build/scikit-build-core/issues/920

