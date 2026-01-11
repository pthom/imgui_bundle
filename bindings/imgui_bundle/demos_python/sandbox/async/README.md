# Async Support Testing

This directory contains tests and examples for ImGui Bundle's async support.

## Test Files

### test_immapp_run_async.py
Comprehensive test suite for `immapp.run_async()` covering all three overloads:

1. **Test 1**: `run_async(gui_function, **kwargs)` - Simple GUI function with keyword arguments
2. **Test 2**: `run_async(gui_function, with_implot=True)` - GUI with ImPlot addon
3. **Test 3**: `run_async(SimpleRunnerParams)` - Using SimpleRunnerParams
4. **Test 4**: `run_async(RunnerParams, AddOnsParams)` - Full RunnerParams with addons
5. **Test 5**: Programmatic exit - Auto-closing GUI after timeout

### test_hello_imgui_run_async.py
Test suite for `hello_imgui.run_async()` covering all three overloads:

1. **Test 1**: `run_async(gui_function, **kwargs)` - Simple GUI function with keyword arguments
2. **Test 2**: `run_async(SimpleRunnerParams)` - Using SimpleRunnerParams
3. **Test 3**: `run_async(RunnerParams)` - Full RunnerParams
4. **Test 4**: Programmatic exit - Auto-closing GUI after timeout

## Running Tests

### Run all tests for immapp:
```bash
cd bindings/imgui_bundle/demos_python/sandbox/async
python test_run_async.py
```

### Run all tests for hello_imgui:
```bash
cd bindings/imgui_bundle/demos_python/sandbox/async
python test_hello_imgui_run_async.py
```

### Run individual tests:
```python
from test_run_async import run_test_1, run_test_2, run_test_3, run_test_4, run_test_5

# Run only test 2 (with ImPlot)
run_test_2()

# Or for hello_imgui:
from test_hello_imgui_run_async import run_test_1 as hi_test_1
hi_test_1()
```

## Expected Behavior

Each test will:
1. Open a GUI window
2. Allow interaction (move slider, etc.)
3. Close when you close the window (or after timeout for auto-close tests)
4. Report success with frame count

All tests should pass without errors.
