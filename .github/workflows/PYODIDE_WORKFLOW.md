# Pyodide CI Workflow Documentation

## Overview

The Pyodide CI workflow (`.github/workflows/pyodide.yml`) automates the building and distribution of imgui-bundle Pyodide wheels.

## Workflow Structure

### Job 1: `build_pyodide_wheel`

**Purpose:** Build the Pyodide wheel on Ubuntu

**Steps:**
1. Checkout repository with submodules
2. Set up Python 3.13
3. Install system dependencies (wget, bzip2)
4. Run setup script: `setup_pyodide_local_build.sh`
   - Creates venv_pyo/
   - Installs pyodide-build
   - Installs xbuildenv for Pyodide 0.29.3
   - Clones and configures emsdk
   - Takes ~30 seconds
5. Build wheel with `pyodide build`
6. Apply wheel naming fix (macOS workaround, safe on Linux)
7. Upload wheel as artifact named `pyodide-wheel`

**Outputs:** 
- Artifact: `dist/imgui_bundle-X.Y.Z-cp313-cp313-pyodide_2025_0_wasm32.whl`

**Performance:**
- Total build time: ~5-7 minutes
  - Setup: ~30 seconds
  - Build: ~4-6 minutes

### Job 2: `upload_to_release`

**Purpose:** Attach Pyodide wheel to GitHub releases

**Trigger:** Only runs when a release is published

**Steps:**
1. Download `pyodide-wheel` artifact
2. Upload wheel to the GitHub release

**Permissions:** Requires `contents: write`

## Triggers

The workflow runs on:
- **workflow_dispatch**: Manual trigger from GitHub UI
- **pull_request**: On all PRs (for testing)
- **release (published)**: When a release is created
- **push to main/master**: On commits to main branches

## Configuration

Versions are managed via `ci_scripts/pyodide_local_build/config_versions_pyodide.sh`:
- Pyodide version: 0.29.3
- Python version: 3.13

## Artifacts

**During PR/Push:**
- Artifact name: `pyodide-wheel`
- Retention: 90 days (GitHub default)
- Access: Download from workflow run page

**During Release:**
- Attached to GitHub release page
- Permanent storage
- Public download link

## Testing Locally

To test the same build process locally:

```bash
# Setup (once)
just pyodide_setup_local_build

# Build
just pyodide_build

# Result
ls dist/*pyodide*.whl
```

## Comparison with Other Workflows

| Workflow | Platform | Output | PyPI Upload |
|----------|----------|--------|-------------|
| `wheels.yml` | Linux/macOS/Windows | Native wheels | Yes (on release) |
| `pyodide.yml` | WASM (Linux build) | Pyodide wheel | No |
| `emscripten.yml` | WASM | Static site | No |

## Future Enhancements

### 1. Browser Testing

Add headless browser tests using Playwright:

```yaml
- name: Test wheel in browser
  run: |
    pip install playwright
    playwright install chromium
    # Run browser tests here
```

### 2. Multi-platform Builds

Test on macOS (though WASM is platform-independent):

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
```

### 3. Version Matrix

Test multiple Python/Pyodide versions:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    pyodide-version: ["0.29.3", "0.30.0"]
```

## References

- Pyodide build docs: https://pyodide.org/en/stable/development/building-packages.html
- GitHub Actions artifacts: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
- Release uploads: https://github.com/softprops/action-gh-release
