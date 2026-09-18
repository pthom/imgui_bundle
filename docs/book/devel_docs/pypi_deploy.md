# PyPI package distribution

## Release process

1. Update the version number in `pyproject.toml` and `CMakeLists.txt` (they must match).
   Version scheme: `ImGui patch × 100 + bundle release` (e.g. `1.92.601` = ImGui 1.92.6, bundle release 1).
   Also update Pyodide wheel filenames hardcoded in demos / docs — see
   [cloudflare_deploy.md → wheel filename references](cloudflare_deploy.md#when-to-update-wheel-filename-references).
2. Check the web builds (Emscripten and Pyodide): see [Web checks before a release](#web-checks-before-a-release).
3. Create a GitHub release with a new tag (e.g. `v1.92.601`).
   The `wheels.yml` CI workflow builds and uploads wheels to PyPI automatically.
4. Manually build and upload the macOS arm64 wheel (see below).


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


## Web checks before a release

The web builds are not covered by the test suite: check them by hand, in a browser, before tagging.

**ImGui Bundle Explorer (Emscripten)**
```bash
just ibex_build
just ibex_serve     # then open http://localhost:8642/demo_imgui_bundle.html
```
Try a few demos (for example the test engine and the docking demos).

**ImGui Explorer (Emscripten)**
```bash
just imex_ems_build
just imex_ems_serve     # then open http://localhost:7006/
```
Check that the Dear ImGui version displayed is the expected one.

**Pyodide**
```bash
just pyodide_build
just pyodide_serve_projects
```
Then open:

| Page | Expected |
|------|----------|
| http://localhost:6456/local_wheels/ | Offers the wheel of the new version (see [wheel filename references](cloudflare_deploy.md#when-to-update-wheel-filename-references)) |
| http://localhost:6456/playground/ | The demos work; the intro page displays the new version |
| http://localhost:6456/min_pyodide_app/demo_heart.html | Works. It installs `imgui-bundle` from PyPI, so it displays the last *released* version until the new one is published: open it again after the release to check that PyPI serves the new wheel |

**Deploy**: `just cf_deploy_all_in_one`, see [Cloudflare deploy](cloudflare_deploy.md).
