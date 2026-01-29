#!/bin/bash
set -e

# Download Pyodide distribution for local testing

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$THIS_DIR"

source ../config_versions_pyodide.sh

DOWNLOAD_URL="https://github.com/pyodide/pyodide/releases/download/${PYODIDE_VERSION}/pyodide-${PYODIDE_VERSION}.tar.bz2"
TARBALL_NAME="pyodide-${PYODIDE_VERSION}.tar.bz2"
EXTRACT_DIR="pyodide_dist"

# Check if already exists
if [ -d "$EXTRACT_DIR" ]; then
    echo "✗ Directory '$EXTRACT_DIR' already exists"
    echo "  To re-download: rm -rf $EXTRACT_DIR (or run: just pyodide_deep_clean)"
    exit 1
fi

echo "Downloading Pyodide ${PYODIDE_VERSION}..."
wget -q --show-progress -O "$TARBALL_NAME" "$DOWNLOAD_URL"

echo "Extracting..."
mkdir -p "$EXTRACT_DIR"
tar -xjf "$TARBALL_NAME" -C "$EXTRACT_DIR" --strip-components=1
rm "$TARBALL_NAME"

# Verify and count
[ -f "$EXTRACT_DIR/pyodide.js" ] || { echo "✗ Error: pyodide.js not found"; exit 1; }
[ -f "$EXTRACT_DIR/pyodide.asm.wasm" ] || { echo "✗ Error: pyodide.asm.wasm not found"; exit 1; }

WHEEL_COUNT=$(find "$EXTRACT_DIR" -name "*.whl" | wc -l | xargs)
echo "✓ Pyodide ${PYODIDE_VERSION} ready ($WHEEL_COUNT packages)"
