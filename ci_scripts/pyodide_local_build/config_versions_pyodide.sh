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
#   3. Check the wheel platform tag (`pyemscripten_YYYY_P_wasm32`, PEP 783;
#      e.g. `pyemscripten_2026_0` for Python 3.14). Since Pyodide 314, the
#      ABI is stable across a whole Pyodide major (314.x <-> Python 3.14)
#      and only changes when the Python version bumps (annually). When the
#      tag changes, update the wheel globs in `.github/workflows/pyodide.yml`
#      and `justfile` (pyodide_build, pyodide_clean), the docs
#      (`.github/workflows/PYODIDE_WORKFLOW.md`, `Readme_pyodide_bundle.md`),
#      and the hard-coded wheel filenames in pages and docs (find them with
#      the rg command in docs/book/devel_docs/cloudflare_deploy.md).
#   4. Whether the `pyodide xbuildenv install <version>` CLI changed
#      (rarely does, but test with `just pyodide_setup_local_build` after
#      the bump).
#   5. The Python version supported by the new Pyodide — bump
#      `PYTHON_VERSION` below if needed (the host python must match it).
#
# Sanity check after upgrading:
#   $ just pyodide_deep_clean
#   $ just pyodide_setup_local_build    # should complete cleanly
#   $ just pyodide_build                # should produce a wheel in dist/
#   $ # load the wheel in a browser via a pyodide test page and confirm
#   $ # micropip accepts it (no "Wheel was built with Emscripten ..." error)
# -----------------------------------------------------------------------------

# Pyodide version to use (determines ABI compatibility)
# Since 314.0.0, Pyodide versions follow the Python version (314.x <-> Python 3.14)
# and the ABI is stable across all 314.x releases (PEP 783).
# See: https://github.com/pyodide/pyodide/releases
PYODIDE_VERSION="314.0.0"

# pyodide-build version. Independent from PYODIDE_VERSION above (see runbook).
# 0.35.x (released alongside Pyodide 314.0.0) builds wheels tagged
# `pyemscripten_2026_0_wasm32` (Python 3.14 ABI). 0.35.1 is required on macOS
# with homebrew Python (fixes host headers leaking into the cross-compile).
# See: https://github.com/pyodide/pyodide-build/releases
PYODIDE_BUILD_VERSION="0.35.1"

# Python version (major.minor, e.g., "3.14", "3.13")
# Must match a version supported by the Pyodide version above
PYTHON_VERSION="3.14"

# =============================================================================
# Note: Emscripten version is automatically determined from Pyodide version
# =============================================================================
