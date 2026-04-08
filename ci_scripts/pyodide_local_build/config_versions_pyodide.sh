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
# (https://github.com/pyodide/pyodide/releases), you MUST bump three things
# together, as one atomic change, to avoid ABI skew between runtime and
# build-time tooling:
#
#   1. `PYODIDE_VERSION` below (the runtime)
#   2. `PYODIDE_BUILD_VERSION` below (the build tool — keep in lockstep
#      with the runtime version; see the comment on that variable)
#   3. The `wheel<0.46` pin in `setup_pyodide_local_build.sh` — this only
#      exists to unstick the 0.29.x generation of auditwheel_emscripten
#      that ships with pyodide-build 0.29.3. Later pyodide-build releases
#      pull a newer auditwheel_emscripten that works with recent wheel,
#      so this pin should be removed on upgrade (leaving it would just
#      needlessly hold `wheel` back). See the comment at that line.
#
# Additionally check:
#   - Whether the new pyodide-build still uses `pyodide_YYYY_M_wasm32`
#     as its wheel platform tag, or the newer `pyemscripten_YYYY_M_wasm32`.
#     If the tag changed, update the wheel globs in `.github/workflows/pyodide.yml`,
#     `justfile` (pyodide_build, pyodide_clean targets), and the docs
#     (`.github/workflows/PYODIDE_WORKFLOW.md` and `Readme_pyodide_bundle.md`)
#     from `*pyodide*.whl` to match the new tag.
#   - Whether the `pyodide xbuildenv install <version>` CLI changed
#     (rarely does, but test with `just pyodide_setup_local_build` after
#     the bump).
#   - The Python version supported by the new Pyodide — bump `PYTHON_VERSION`
#     below if needed.
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
PYODIDE_VERSION="0.29.3"

# pyodide-build version to use — MUST match the Pyodide runtime above.
# pyodide-build is published on PyPI with its own release cadence that
# races ahead of the Pyodide runtime; pinning here is required to avoid
# ABI skew.
#
# Concretely: pyodide-build 0.30.x changed the wheel platform tag from
# `pyodide_2025_0_wasm32` to `pyemscripten_2025_0_wasm32`, but the
# micropip shipped inside Pyodide runtime 0.29.3 only knows how to
# validate the old tag — installing a pyemscripten-tagged wheel at
# runtime fails with:
#   ValueError: Wheel was built with Emscripten vpyemscripten.2025.0
#               but Pyodide was built with Emscripten v4.0.9
# See: https://github.com/pyodide/pyodide-build/releases
#
# Rule of thumb: PYODIDE_BUILD_VERSION should match PYODIDE_VERSION.
# See the UPGRADE RUNBOOK at the top of this file.
PYODIDE_BUILD_VERSION="0.29.3"

# Python version (major.minor, e.g., "3.13", "3.12", "3.11")
# Must match a version supported by the Pyodide version above
PYTHON_VERSION="3.13"

# =============================================================================
# Note: Emscripten version is automatically determined from Pyodide version
# =============================================================================
