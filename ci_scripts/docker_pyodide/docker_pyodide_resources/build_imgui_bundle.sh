#!/bin/bash
# Build script for imgui-bundle Pyodide wheel
# This script runs inside the Docker container

set -e  # Exit on error

echo "========================================"
echo "Building imgui-bundle for Pyodide"
echo "========================================"

# Paths
PYODIDE_DIR="/opt/pyodide"
RECIPES_DIR="/opt/pyodide-recipes"
IMGUI_BUNDLE_SRC="/mnt/imgui_bundle_sdist"
OUTPUT_DIR="/mnt/output"

# Activate the virtual environment
source /opt/venv_pyodide/bin/activate

# Source emsdk environment
source "${PYODIDE_DIR}/emsdk/emsdk/emsdk_env.sh"

echo ""
echo ">>> Building imgui-bundle wheel..."
echo "    Source: ${IMGUI_BUNDLE_SRC}"
echo "    Recipes: ${RECIPES_DIR}"

cd "${PYODIDE_DIR}"

# Build imgui-bundle
# Note: meta.yaml must be manually configured to point to the correct source path
pyodide build-recipes imgui-bundle --recipe-dir "${RECIPES_DIR}/packages" --install

echo ""
echo ">>> Copying build artifacts to output directory..."

# Create output directory if needed
mkdir -p "${OUTPUT_DIR}"

# Find and copy the built wheel
WHEEL=$(find "${PYODIDE_DIR}/dist" -name "imgui_bundle-*.whl" -type f | head -1)

if [ -n "$WHEEL" ]; then
    cp "$WHEEL" "${OUTPUT_DIR}/"
    echo "    Wheel copied: $(basename $WHEEL)"
else
    echo "Warning: No wheel found in ${PYODIDE_DIR}/dist"
fi

# Copy pyodide dist files for testing
mkdir -p "${OUTPUT_DIR}/pyodide_dist"
cp -r "${PYODIDE_DIR}/dist/"* "${OUTPUT_DIR}/pyodide_dist/" 2>/dev/null || true

echo ""
echo "========================================"
echo "Build complete!"
echo "========================================"
echo ""
echo "Output files in ${OUTPUT_DIR}:"
ls -la "${OUTPUT_DIR}"/*.whl 2>/dev/null || echo "  (no wheel files)"
echo ""
