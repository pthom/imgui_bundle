# PyPI package distribution

## Release process

1. Update the version number in `pyproject.toml` and `CMakeLists.txt` (they must match).
   Version scheme: `ImGui patch × 100 + bundle release` (e.g. `1.92.601` = ImGui 1.92.6, bundle release 1).
2. Create a GitHub release with a new tag (e.g. `v1.92.601`).
   The `wheels.yml` CI workflow builds and uploads wheels to PyPI automatically.
3. Manually build and upload the macOS arm64 wheel (see below).

## macOS arm64 wheel (manual)

:::{note}
The macOS arm64 wheel must be built on an Apple Silicon Mac. Building on Intel may fail due to iPPIcv loading issues.
:::

```bash
rm -rf _skbuild
CIBW_ARCHS_MACOS="arm64" pipx run cibuildwheel --platform=macos

# Upload
pipx run twine upload wheelhouse/*
# or
uv tool run twine upload wheelhouse/*
```

To target specific Python versions:
```bash
CIBW_ARCHS_MACOS="arm64" CIBW_BUILD="cp311-* cp312-*" uv tool run cibuildwheel --platform=macos
```

To build for macOS 11 (disables FreeType): in `pyproject.toml`, change `MACOSX_DEPLOYMENT_TARGET="14.0"` to `"11.0"`.
