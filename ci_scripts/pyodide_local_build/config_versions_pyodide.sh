#!/bin/bash
# =============================================================================
# Pyodide Build Configuration
# =============================================================================
# Central configuration file for Pyodide build environment versions.
#
# This file is sourced by:
#   - setup_pyodide_local_build.sh (environment setup)
#   - Other build scripts that need version information
#
# Update these values to change the build environment:
# =============================================================================

# Pyodide version to use (determines ABI compatibility)
# See: https://github.com/pyodide/pyodide/releases
PYODIDE_VERSION="0.29.3"

# Python version (major.minor, e.g., "3.13", "3.12", "3.11")
# Must match a version supported by the Pyodide version above
PYTHON_VERSION="3.13"

# =============================================================================
# Note: Emscripten version is automatically determined from Pyodide version
# =============================================================================
