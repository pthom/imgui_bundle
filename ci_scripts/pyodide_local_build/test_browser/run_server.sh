#!/bin/bash
set -e

# Pyodide Browser Test Runner
# ============================
# Orchestrates browser testing for imgui-bundle + Pyodide

# Navigate to script directory
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$THIS_DIR"

# Load version configuration
source ../config_versions_pyodide.sh

# Configuration
PORT=8123
REPO_ROOT="../../.."

echo "========================================"
echo "Pyodide Browser Test Runner"
echo "========================================"
echo ""
echo "Configuration:"
echo "  Pyodide Version: $PYODIDE_VERSION"
echo "  Python Version: $PYTHON_VERSION"
echo "  Server Port: $PORT"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# 1. Check if Pyodide distribution is downloaded
if [ ! -d "pyodide_dist" ]; then
    echo "⚠️  Pyodide distribution not found"
    echo "   Run: ./download_pyodide_dist.sh"
    exit 1
fi

# 2. Check if imgui-bundle wheel exists
WHEEL_PATTERN="${REPO_ROOT}/dist/imgui_bundle-*-pyodide_*.whl"
WHEEL_COUNT=$(ls $WHEEL_PATTERN 2>/dev/null | wc -l | xargs)

if [ "$WHEEL_COUNT" -eq 0 ]; then
    echo "⚠️  imgui-bundle wheel not found in ${REPO_ROOT}/dist/"
    echo "   Build command: cd ${REPO_ROOT} && just pyodide_build"
    exit 1
fi

WHEEL_FILE=$(ls $WHEEL_PATTERN | head -1)
WHEEL_NAME=$(basename "$WHEEL_FILE")
echo "✓ imgui-bundle wheel found: $WHEEL_NAME"

echo ""
echo "========================================"
echo "Starting Test Server"
echo "========================================"
echo ""

# Start the server
./_serve_cors.py --port $PORT
