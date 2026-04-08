#!/bin/bash
set -e

# Pyodide Local Build Environment Setup Script
# ==============================================
# This script automates the setup of the pyodide build environment.
# Run from: ci_scripts/pyodide_local_build/

# Make sure we are in the script directory
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $THIS_DIR

# Load version configuration
source config_versions_pyodide.sh

echo "========================================"
echo "Pyodide Build Environment Setup"
echo "========================================"
echo ""
echo "Configuration:"
echo "  Pyodide Version:       $PYODIDE_VERSION"
echo "  pyodide-build Version: $PYODIDE_BUILD_VERSION"
echo "  Python Version:        $PYTHON_VERSION"
echo ""


# Check Python version
echo "1. Checking Python version..."
PYTHON_EXECUTABLE="python${PYTHON_VERSION}"
PYTHON_VERSION_FULL=$($PYTHON_EXECUTABLE --version 2>&1 || echo "not found")
if [[ "$PYTHON_VERSION_FULL" == *"not found"* ]]; then
    echo "✗ Error: Python $PYTHON_VERSION not found"
    echo "  Looking for: $PYTHON_EXECUTABLE"
    echo "  Please install Python $PYTHON_VERSION first"
    exit 1
fi
echo "✓ Found: $PYTHON_VERSION_FULL"
echo ""

# Create venv
echo "2. Creating virtual environment..."
if [ -d "venv_pyo" ]; then
    echo "⚠️  venv_pyo already exists, skipping"
else
    $PYTHON_EXECUTABLE -m venv venv_pyo
    echo "✓ Created venv_pyo"
fi
echo ""

# Activate and install pyodide-build
echo "3. Installing pyodide-build..."
source venv_pyo/bin/activate
pip install --upgrade pip > /dev/null
# Pin pyodide-build to match the Pyodide runtime — newer pyodide-build
# releases changed the wheel platform tag and break ABI compatibility
# with older Pyodide runtimes. See config_versions_pyodide.sh for the
# full upgrade runbook.
#
# !!! REMOVE ON UPGRADE !!!
# The `wheel<0.46` pin is a targeted workaround for the pyodide-build
# 0.29.3 era only: it pulls auditwheel_emscripten 0.0.16, which does
# `from wheel.cli.pack import pack as pack_wheel`. The `wheel.cli`
# module was removed in wheel 0.46.0, so any unpinned install with
# current pip picks up wheel 0.46.x and the `pyodide` CLI immediately
# crashes at import with:
#   ModuleNotFoundError: No module named 'wheel.cli'
# wheel 0.45.x is the last release that still exposes wheel.cli.pack.
#
# When bumping PYODIDE_BUILD_VERSION beyond 0.29.x, drop this constraint:
# newer pyodide-build releases pull a newer auditwheel_emscripten that
# does not rely on wheel.cli, so the pin is unnecessary there and would
# just needlessly hold `wheel` back.
pip install "pyodide-build==$PYODIDE_BUILD_VERSION" "wheel<0.46"
echo "✓ Installed pyodide-build $PYODIDE_BUILD_VERSION (with wheel<0.46 workaround)"
echo ""

# Install xbuildenv
echo "4. Installing Pyodide cross-compilation toolchain..."
echo "   Target: Pyodide $PYODIDE_VERSION (ABI: pyodide_2025_0_wasm32)"
pyodide xbuildenv install $PYODIDE_VERSION
echo "✓ Installed xbuildenv for Pyodide $PYODIDE_VERSION"
echo ""

# Clone and setup emsdk
echo "5. Setting up Emscripten SDK..."
if [ -d "emsdk" ]; then
    echo "⚠️  emsdk directory already exists, skipping clone"
    cd emsdk
else
    git clone https://github.com/emscripten-core/emsdk
    cd emsdk
    echo "✓ Cloned emsdk"
fi

PYODIDE_EMSCRIPTEN_VERSION=$(pyodide config get emscripten_version)
echo "   Installing Emscripten $PYODIDE_EMSCRIPTEN_VERSION (matches Pyodide $PYODIDE_VERSION)"

./emsdk install ${PYODIDE_EMSCRIPTEN_VERSION}
./emsdk activate ${PYODIDE_EMSCRIPTEN_VERSION}
cd ..
echo "✓ Configured emsdk"
echo ""

# Verify installation
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "Verification:"
source emsdk/emsdk_env.sh > /dev/null 2>&1
EMCC_VERSION=$(emcc --version 2>&1 | head -1)
echo "  Emscripten: $EMCC_VERSION"
echo "  Python: $PYTHON_VERSION_FULL"
echo "  Pyodide: $PYODIDE_VERSION"
echo ""
echo "Next steps:"
echo "  1. Build imgui-bundle wheel:"
echo "     just pyodide_build"
echo ""
echo "  2. Or activate the environment manually:"
echo "     source ci_scripts/pyodide_local_build/venv_pyo/bin/activate"
echo "     source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh"
echo ""
