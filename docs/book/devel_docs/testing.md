# Testing

## Quick start

```bash
just test_pytest    # Run the test suite
just mypy           # Type-check the Python bindings
```

Or without `just`:
```bash
pytest                            # from repo root
cd bindings && ./mypy_bindings.sh # mypy
```

## What the test suite covers

- **`tests/lg_imgui_bundle_test.py`** — Main test file: exercises the litgen binding generation for imgui_bundle.
- **`just mypy`** — Runs mypy on all `.pyi` stubs to verify type consistency.
- **`tests/test_imgui_md_compat.py`**: `imgui_md`, the former name of the markdown module, still offers the API of v1.92.900 (the last release before `rich_md`).
- **`tests/cpp_compat/`**: the C++ side of the same promise (`imgui_md_wrapper.h`, namespace `ImGuiMd`) compiles and links against the installed package. Built by `just test_cpp_compat` (after `just cpp_package_install`), and by the CI workflow `cpp_install_package.yml` on the three desktop platforms.

## GUI tests

GUI tests live in `tests/tests_python_gui/` and require a display (they open windows). The CI runs them on Linux (under Xvfb) and on Windows (with Mesa's software OpenGL), not on macOS (`pip.yml`).

To run them locally:
```bash
pytest tests/tests_python_gui/
```

These tests verify:
- Widget rendering (e.g. `test_color_edit3_tuple.py`)
- RunnerParams identity across Python/C++ boundary (`test_runner_params_identity.py`)
- Async integration (`async/`)

### Hidden windows

The environment variable `HELLOIMGUI_TEST_HIDDEN_WINDOWS=1` keeps every window of a Hello ImGui app hidden, the viewports' windows included. The app still renders: the tests, the test engine's captures and the screenshots work, and nothing shows on the screen.

```bash
HELLOIMGUI_TEST_HIDDEN_WINDOWS=1 pytest tests/tests_python_gui/
HELLOIMGUI_TEST_HIDDEN_WINDOWS=1 ./ci_node_editor_tests --auto
```

- Use it for local runs: the GUI tests, the test apps of `.github/ci_automation_tests` (`ci_node_editor_tests --auto`, `ci_wheel_claims_tests`), the screenshots of `immapp.testing`.
- Checked on macOS. On Windows and Linux, a hidden OpenGL window may render nothing: the CI keeps a visible window (Xvfb on Linux).
- On macOS, the hidden windows also work while the display sleeps: macOS then reports no monitor, and Hello ImGui uses a default work area. Not with viewports (`--viewports`): Dear ImGui needs a monitor for them. Run `caffeinate -u -d -t 240 &` first.

## Manual smoke testing

The most thorough manual test is to run the main demo application, which exercises most libraries:

**C++:**
```bash
cd builds/my_build
./demo_imgui_bundle
```

**Python:**
```bash
python bindings/imgui_bundle/demos_python/demos_immapp/demo_hello_world.py
```

## CI workflows

The project has extensive CI via GitHub Actions (`.github/workflows/`):

| Workflow | What it tests |
|----------|---------------|
| `cpp_lib.yml` | C++ library build (multiple platforms) |
| `cpp_lib_with_bindings.yml` | C++ build with Python bindings |
| `pip.yml` | `pip install` from source |
| `wheels.yml` | Build distributable wheels (cibuildwheel) |
| `emscripten.yml` | Emscripten / WebAssembly build |
| `pyodide.yml` | Pyodide / browser build |
| `Metal.yml` | macOS Metal renderer |
| `Vulkan.yml` | Vulkan renderer |
| `DirectX.yml` | Windows DirectX |
| `android.yml` | Android build |
| `ios.yml` | iOS build |
| `ci_automation_test.yml` | Automated GUI tests (Linux, Xvfb): a demo app, the node editor's tests, the zoomable widgets' wheel claims (`.github/ci_automation_tests`) |

Most workflows trigger on push to main and on pull requests.
