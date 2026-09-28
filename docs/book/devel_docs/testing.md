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

GUI tests live in `tests/tests_python_gui/` and require a display (they open windows). They are not run by default in CI.

To run them locally:
```bash
pytest tests/tests_python_gui/
```

These tests verify:
- Widget rendering (e.g. `test_color_edit3_tuple.py`)
- RunnerParams identity across Python/C++ boundary (`test_runner_params_identity.py`)
- Async integration (`async/`)

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
| `ci_automation_test.yml` | Automated GUI test (runs demo, takes screenshots) |

Most workflows trigger on push to main and on pull requests.
