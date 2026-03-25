# PyPI package distribution

## Release process

1. Update the version number in `pyproject.toml` and `CMakeLists.txt` (they must match).
   Version scheme: `ImGui patch × 100 + bundle release` (e.g. `1.92.601` = ImGui 1.92.6, bundle release 1).
2. Create a GitHub release with a new tag (e.g. `v1.92.601`).
   The `wheels.yml` CI workflow builds and uploads wheels to PyPI automatically.
3. Manually build and upload the macOS arm64 wheel (see below).


## About cibuildwheel

[cibuildwheel](https://cibuildwheel.pypa.io/) is a tool that builds Python wheels for multiple platforms and Python versions in a consistent, reproducible way. It:

- Runs your build inside isolated environments (Docker on Linux, native on macOS/Windows)
- Builds wheels for all supported Python versions (3.8–3.13+)
- Handles platform-specific quirks (manylinux, musllinux, macOS universal2, etc.)
- Is used both in CI (`wheels.yml`) and for manual local builds

The project's cibuildwheel configuration is in `pyproject.toml` under `[tool.cibuildwheel]`.


## Manual build using cibuildwheel

To target specific Python versions:
```bash
CIBW_ARCHS_MACOS="arm64" CIBW_BUILD="cp311-* cp312-*" uv tool run cibuildwheel --platform=macos
```

To build for macOS 11 (disables FreeType): in `pyproject.toml`, change `MACOSX_DEPLOYMENT_TARGET="14.0"` to `"11.0"`.

Upload wheels to PyPI:
```bash
uv tool run twine upload wheelhouse/*
```


## Pyodide release

Pyodide (Python-in-the-browser via WebAssembly) has its own build and release process. See the [Pyodide build guide](Readme_pyodide_bundle.md) for:
- Local build environment setup (`just pyodide_setup_local_build`)
- Building the Pyodide wheel (`just pyodide_build`)
- Browser testing (`just pyodide_test_serve`)
- Publishing to the pyodide-recipes repository
