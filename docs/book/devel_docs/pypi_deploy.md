# PyPI package distribution

## Release process

1. Update the version number in `pyproject.toml` and `CMakeLists.txt` (they must match).
   Version scheme: `ImGui patch × 100 + bundle release` (e.g. `1.92.601` = ImGui 1.92.6, bundle release 1).
   Also update Pyodide wheel filenames hardcoded in demos / docs — see
   [cloudflare_deploy.md → wheel filename references](cloudflare_deploy.md#when-to-update-wheel-filename-references).
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

Since Pyodide 314 / pyodide-build 0.35, Pyodide wheels (platform tag
`pyemscripten_YYYY_P_wasm32`, cf [PEP 783](https://peps.python.org/pep-0783/))
can be published on PyPI alongside the desktop wheels. micropip then installs
them directly: `micropip.install("imgui-bundle")`.

1. Build locally: `just pyodide_setup_local_build` (once), then `just pyodide_build`.
2. Test in a browser: `just pyodide_serve_projects`, then open
   http://localhost:6456/pyodide_test_bundle/test_cdn_pyodide_local_wheel.html
3. Upload to PyPI (can be added to an existing release version):
   ```bash
   uv tool run twine upload dist/imgui_bundle-*pyemscripten*.whl
   ```

See the [Pyodide build guide](Readme_pyodide_bundle.md) for details on the
build environment. Note: the legacy distribution channel (pyodide-recipes
repository) is deprecated for imgui-bundle; the recipe there is disabled, so
micropip falls through to PyPI.
