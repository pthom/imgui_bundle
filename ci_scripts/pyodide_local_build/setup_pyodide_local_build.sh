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
echo "  Pyodide Version: $PYODIDE_VERSION"
echo "  Python Version: $PYTHON_VERSION"
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
pip install pyodide-build
echo "✓ Installed pyodide-build"
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
