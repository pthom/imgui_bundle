# Plan: Async Jupyter Notebook Support for ImGui Bundle

Add non-blocking async GUI support for Jupyter notebooks, enabling interactive development where users can modify variables in cells while the GUI runs and updates in real-time.

## Implementation Order

**Rationale:** Implement `run_async()` first since `start()` will use it internally. This promotes code reuse and allows incremental testing.

## Steps

### 1. Add `run_async()` to `bindings/imgui_bundle/immapp/__init__.py`

Implement `async def run_async()` with overloads matching `immapp.run()` signatures:
- `run_async(runner_params: RunnerParams, addons_params: Optional[AddOnsParams] = None)`
- `run_async(simple_params: SimpleRunnerParams, addons_params: Optional[AddOnsParams] = None)`
- `run_async(gui_function, **kwargs)` with addon parameters

Implementation:
- Use `manual_render.setup_from_*()` for initialization (all three methods)
- Run async render loop with `await asyncio.sleep(0)` to yield to event loop
- Use try/finally to ensure `tear_down()` is called even on exceptions
- Proper Python async/await pattern for advanced users who need full control

**Why first:** This is the core async functionality that `start()` will delegate to.

### 2. Add `run_async()` to hello_imgui module

Similar to immapp but simpler (no AddOnsParams). Implement same three overloads:
- `run_async(runner_params: RunnerParams)`
- `run_async(simple_params: SimpleRunnerParams)`
- `run_async(gui_function, **kwargs)`

Use `hello_imgui.manual_render` for setup/render/teardown.

### 3. Create `bindings/imgui_bundle/immapp/nb.py`

Implement `immapp.nb` submodule with:
- `run()` - Blocking + screenshot, delegates to existing patched behavior
- `start()` - Non-blocking wrapper that calls `asyncio.create_task(immapp.run_async(...))` with notebook-friendly defaults
- `stop()` - Sets `hello_imgui.get_runner_params().app_shall_exit = True` and tracks global task state
- `is_running()` - Check if async GUI is currently running

`start()` implementation:
- Check if GUI already running, auto-stop with warning if needed
- Apply notebook-friendly defaults (light theme, window_size_auto, top_most)
- Delegate to `immapp.run_async()` and wrap in `asyncio.create_task()`
- Track task in global state

Handle all three input signatures (matching `run_async()`):
- `start(runner_params, addons_params=None)`
- `start(simple_params, addons_params=None)`
- `start(gui_function, **kwargs)` with addon parameters

### 4. Create `bindings/imgui_bundle/hello_imgui_nb.py`

Implement `hello_imgui.nb` module mirroring immapp but without `AddOnsParams`. Same API:
- `run()` - Blocking + screenshot
- `start()` - Non-blocking, delegates to `hello_imgui.run_async()`
- `stop()` - Stop the running GUI
- `is_running()` - Check GUI state

Handle all three input signatures (matching `run_async()`):
- `start(runner_params)`
- `start(simple_params)`
- `start(gui_function, **kwargs)`

### 5. Add type hints to stub files

Update type stubs with proper signatures:
- `immapp_cpp.pyi` - Add `run_async()` and `nb` submodule
- `hello_imgui.pyi` - Add `run_async()` and `nb` module

### 6. Update `test.ipynb`

Replace manual `immapp_run_async()` with `immapp.nb.start()`. Add cells demonstrating:
- Blocking mode with `immapp.nb.run()` (screenshot output)
- Non-blocking mode with `task = immapp.nb.start()` (no screenshot, stays open)
- Live variable updates in subsequent cells
- `immapp.nb.stop()` to close programmatically
- Comparison with Qt demo pattern

## Further Considerations

### 1. Single GUI constraint

Should `start()` auto-stop existing GUI or raise error?

**Recommendation:** Warn + auto-stop in Python (C++ already does this). Check `is_running()` and call `stop()` automatically with a warning message.
=> Agreed, implement auto-stop with warning.

### 2. Error handling

Ensure `tear_down()` called even on exceptions. Use try/finally in async render loop:

```python
async def _render_loop():
    try:
        while not hello_imgui.get_runner_params().app_shall_exit:
            immapp.manual_render.render()
            await asyncio.sleep(0)
    finally:
        immapp.manual_render.tear_down()
```
=> Agreed, implement robust error handling.

### 3. Task lifecycle

Add `is_running()` helper to check GUI state before starting new one. Track global task state to prevent multiple simultaneous GUIs.
=> Yes

### 4. Module structure

- `immapp.nb` as a submodule (proxy class pattern like `manual_render`)
- `hello_imgui.nb` as a top-level module (simpler, imported separately)

### 5. Testing

Create comprehensive test notebooks demonstrating:
- Basic blocking usage
- Basic non-blocking usage
- Variable updates from notebook
- Error handling
- Multiple sequential GUIs (close one, open another)
- Comparison with Qt integration pattern

## Implementation Notes

### Key patterns from research

**Async render loop pattern:**
```python
async def _render_loop():
    while not hello_imgui.get_runner_params().app_shall_exit:
        immapp.manual_render.render()
        await asyncio.sleep(0)  # Yield to Jupyter event loop
    immapp.manual_render.tear_down()
```

**Light theme wrapper:**
```python
from imgui_bundle.immapp.immapp_notebook import _make_gui_with_light_theme
gui_with_theme = _make_gui_with_light_theme(gui_function)
```

**Task management:**
```python
_current_task = None

def is_running() -> bool:
    return _current_task is not None and not _current_task.done()

def start(...) -> asyncio.Task:
    global _current_task
    if is_running():
        print("Warning: A GUI is already running. Stopping it first.")
        stop()
    # ... setup ...
    _current_task = asyncio.create_task(_render_loop())
    return _current_task
```

### API Design Summary

```python
# Blocking mode with screenshot (current behavior, now explicit)
immapp.nb.run(gui, with_implot=True)
hello_imgui.nb.run(runner_params)

# Non-blocking mode for notebooks (new)
task = immapp.nb.start(gui, with_implot=True)
task = hello_imgui.nb.start(runner_params)

# Stop programmatically (new)
immapp.nb.stop()
hello_imgui.nb.stop()

# Check state (new)
if immapp.nb.is_running():
    print("GUI is running")

# Advanced async/await for general Python use (new)
async def my_app():
    await immapp.run_async(gui, with_implot=True)
    # GUI runs until closed
    print("GUI closed")

asyncio.run(my_app())
```
