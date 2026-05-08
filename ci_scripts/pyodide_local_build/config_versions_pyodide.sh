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
# Update these values to change the build environment.
#
# -----------------------------------------------------------------------------
# UPGRADE RUNBOOK — read this before bumping any version
# -----------------------------------------------------------------------------
# When a new Pyodide runtime release appears
# (https://github.com/pyodide/pyodide/releases):
#
#   1. Bump `PYODIDE_VERSION` below (the runtime).
#   2. Check if `PYODIDE_BUILD_VERSION` needs to move. The two version
#      streams are independent: pyodide-build is published on PyPI with
#      its own release cadence and supports a range of Pyodide runtimes
#      via `min_pyodide_build_version` in the upstream cross-build-env
#      metadata at
#      https://pyodide.github.io/pyodide/api/pyodide-cross-build-environments.json
#      You only need to bump pyodide-build when the new runtime requires
#      a newer build, or to pick up a needed bugfix/feature.
#   3. Check the wheel platform tag produced by the chosen pyodide-build.
#      pyodide-build 0.34.1+ produces `pyemscripten_YYYY_M_wasm32`
#      (PEP 783); 0.29.x and earlier produced `pyodide_YYYY_M_wasm32`.
#      Pyodide runtime 0.29.4 added support for `pyemscripten`-tagged
#      wheels, which is what unblocked moving to pyodide-build 0.34.x.
#      If the tag changes again, update the wheel globs in
#      `.github/workflows/pyodide.yml`, `justfile` (pyodide_build,
#      pyodide_clean), the docs (`.github/workflows/PYODIDE_WORKFLOW.md`,
#      `Readme_pyodide_bundle.md`), and the hard-coded wheel filenames
#      under `pyodide_projects/`.
#   4. Whether the `pyodide xbuildenv install <version>` CLI changed
#      (rarely does, but test with `just pyodide_setup_local_build` after
#      the bump).
#   5. The Python version supported by the new Pyodide — bump
#      `PYTHON_VERSION` below if needed.
#
# Sanity check after upgrading:
#   $ just pyodide_deep_clean
#   $ just pyodide_setup_local_build    # should complete cleanly
#   $ just pyodide_build                # should produce a wheel in dist/
#   $ # load the wheel in a browser via a pyodide test page and confirm
#   $ # micropip accepts it (no "Wheel was built with Emscripten ..." error)
# -----------------------------------------------------------------------------

# Pyodide version to use (determines ABI compatibility)
# See: https://github.com/pyodide/pyodide/releases
PYODIDE_VERSION="0.29.4"

# pyodide-build version. Independent from PYODIDE_VERSION above (see runbook).
# 0.34.3 builds wheels tagged `pyemscripten_2025_0_wasm32`, which Pyodide
# runtime 0.29.4 accepts (0.29.4 added `pyemscripten` tag compatibility).
# See: https://github.com/pyodide/pyodide-build/releases
PYODIDE_BUILD_VERSION="0.34.3"

# Python version (major.minor, e.g., "3.13", "3.12", "3.11")
# Must match a version supported by the Pyodide version above
PYTHON_VERSION="3.13"

# =============================================================================
# Note: Emscripten version is automatically determined from Pyodide version
# =============================================================================
