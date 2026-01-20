# Jupyter Notebooks support

ImGui Bundle provides two modes for running applications in Jupyter notebooks: **blocking mode** (traditional with screenshots) and **non-blocking mode** (interactive with live updates).

## Overview

The notebook module (`immapp.nb` and `hello_imgui.nb`) provides convenient functions for Jupyter integration:

| Function | Mode | Description |
|----------|------|-------------|
| `nb.start()` | Non-blocking | Start GUI, notebook stays responsive |
| `nb.stop()` | - | Stop the running GUI |
| `nb.is_running()` | - | Check if GUI is active |
| `nb.run()` | Blocking | Traditional mode with screenshot |

## Quick Comparison

### Non-blocking Mode (Interactive ⭐ Recommended)

```python
from imgui_bundle import immapp, imgui

counter = {"value": 0}

def gui():
    imgui.text(f"Count: {counter['value']}")
    if imgui.button("+"):
        counter["value"] += 1

# Start GUI - returns immediately!
immapp.nb.start(gui, window_title="Counter", window_size_auto=True)
```

```python
# You can modify variables from other cells!
counter["value"] = 100  # Updates in the GUI immediately!
```

```python
# Stop when done
immapp.nb.stop()
```

### Blocking Mode (Traditional)

```python
# This will block until you close the window,
# then display a screenshot
immapp.nb.run(gui, window_title="Counter", window_size_auto=True)
# Screenshot appears here after closing ⬇️
```

## Non-Blocking Mode: Interactive Notebooks

The non-blocking mode is the most powerful feature for notebooks, enabling **live interaction** between your Python code and the running GUI.

### Basic Workflow

1. **Start the GUI** with `nb.start()` - returns immediately
2. **Run notebook cells** - modify variables, update data
3. **GUI updates in real-time** - sees all your changes
4. **Stop when done** with `nb.stop()`

### Complete Example: Live Data Visualization

```python
import numpy as np
from imgui_bundle import immapp, imgui, implot
import math

# Shared data that both GUI and notebook can access
plot_data = {
    "x": np.linspace(0, 10, 100, dtype=np.float32),
    "y": np.sin(np.linspace(0, 10, 100, dtype=np.float32))
}

def plot_gui():
    imgui.text("Live Plot Visualization")
    imgui.text(f"Data points: {len(plot_data['x'])}")

    if implot.begin_plot("Live Data"):
        implot.plot_line("Signal", plot_data["x"], plot_data["y"])
        implot.end_plot()

    if imgui.button("Close"):
        hello_imgui.get_runner_params().app_shall_exit = True

# Start the GUI with ImPlot support
addons = immapp.AddOnsParams()
addons.with_implot = True

immapp.nb.start(plot_gui, window_title="Live Plot", addons_params=addons)
```

Now in another cell, update the data:

```python
# Change to cosine - watch the GUI update immediately!
plot_data["y"] = np.cos(plot_data["x"])
print("Updated to cosine wave")
```

```python
# Increase resolution
plot_data["x"] = np.linspace(0, 10, 500, dtype=np.float32)
plot_data["y"] = np.sin(plot_data["x"] * 2)
print(f"Updated to {len(plot_data['x'])} points")
```

```python
# Stop the GUI
immapp.nb.stop()
```

### Use Cases for Non-Blocking Mode

#### 1. Live Data Visualization

Perfect for exploring datasets interactively:

```python
data = load_large_dataset()

def visualize():
    # Display current slice
    implot.plot_line("Data", data["x"], data["y"])

immapp.nb.start(visualize, window_title="Data Explorer")

# Try different data slices in notebook cells
data = filter_outliers(data)  # GUI updates!
data = smooth(data, window=5)  # GUI updates again!
```

#### 2. ML Training Dashboard

Monitor training in real-time:

```python
training_metrics = {
    "loss": [],
    "accuracy": [],
    "epoch": 0
}

def training_dashboard():
    imgui.text(f"Epoch: {training_metrics['epoch']}")
    if len(training_metrics['loss']) > 0:
        imgui.text(f"Loss: {training_metrics['loss'][-1]:.4f}")
        imgui.text(f"Accuracy: {training_metrics['accuracy'][-1]:.4f}")

        if implot.begin_plot("Training Progress"):
            if len(training_metrics['loss']) > 0:
                implot.plot_line("Loss",
                    np.arange(len(training_metrics['loss'])),
                    np.array(training_metrics['loss']))
            implot.end_plot()

immapp.nb.start(training_dashboard, window_title="Training")

# Run training - metrics update in GUI
for epoch in range(100):
    loss, acc = train_epoch(model, data)
    training_metrics['loss'].append(loss)
    training_metrics['accuracy'].append(acc)
    training_metrics['epoch'] = epoch
    time.sleep(0.1)  # GUI stays responsive!
```

#### 3. Interactive Parameter Tuning

Adjust algorithm parameters and see results immediately:

```python
params = {
    "threshold": 0.5,
    "smoothing": 3,
    "processed_data": None
}

def process_data():
    # Apply parameters
    result = apply_algorithm(
        raw_data,
        threshold=params["threshold"],
        smoothing=params["smoothing"]
    )
    params["processed_data"] = result

def param_gui():
    imgui.text("Parameter Tuning")
    changed, params["threshold"] = imgui.slider_float(
        "Threshold", params["threshold"], 0.0, 1.0
    )
    if changed:
        process_data()

    changed, params["smoothing"] = imgui.slider_int(
        "Smoothing", params["smoothing"], 1, 10
    )
    if changed:
        process_data()

    # Display result
    if params["processed_data"] is not None:
        imgui.text(f"Result: {params['processed_data'].mean():.2f}")

immapp.nb.start(param_gui)

# You can also adjust from notebook
params["threshold"] = 0.7
process_data()
```

## API Reference

### immapp.nb Module

The `immapp.nb` module provides the richest feature set with addon support.

#### immapp.nb.start()

Start a GUI non-blocking. Three signatures supported:

**1. Simple function** (recommended):

```python
immapp.nb.start(
    gui_function,
    window_title="My App",
    window_size_auto=True,
    window_size=(800, 600),
    top_most=True,
    # Addon flags (immapp only)
    with_implot=True,
    with_markdown=True,
    with_node_editor=False,
    with_tex_inspect=False
) -> asyncio.Task
```

**2. SimpleRunnerParams**:

```python
params = hello_imgui.SimpleRunnerParams()
params.gui_function = my_gui
params.window_title = "My App"
params.window_size_auto = True

immapp.nb.start(params) -> asyncio.Task
```

**3. Full RunnerParams + AddOnsParams**:

```python
runner = hello_imgui.RunnerParams()
runner.callbacks.show_gui = my_gui

addons = immapp.AddOnsParams()
addons.with_implot = True

immapp.nb.start(runner, addons) -> asyncio.Task
```

**Automatic Notebook-Friendly Defaults**:
- Light theme applied automatically
- `top_most=True` by default (window stays above browser)
- `window_size_auto=True` by default
- Optimal FPS settings for notebook responsiveness

**Returns**: An `asyncio.Task` representing the running GUI (usually you can ignore this)

**Auto-Stop Behavior**: If you call `start()` while another GUI is running, it will automatically stop the previous one and display a warning.

#### immapp.nb.stop()

```python
immapp.nb.stop() -> None
```

Stops the currently running GUI. Sets `app_shall_exit` flag and waits for clean shutdown.

#### immapp.nb.is_running()

```python
immapp.nb.is_running() -> bool
```

Returns `True` if a GUI is currently running via `nb.start()`.

#### immapp.nb.run()

```python
immapp.nb.run(
    gui_function,
    window_title="My App",
    window_size_auto=True,
    # ... same parameters as start()
) -> None
```

**Blocking mode**: Runs the GUI and blocks until the window is closed. After closing, a screenshot is displayed in the notebook output.

This is equivalent to the traditional `immapp.run()` but with notebook-optimized defaults (light theme, screenshot).

### hello_imgui.nb Module

The `hello_imgui.nb` module provides similar functionality without addon support:

```python
from imgui_bundle import hello_imgui

# Same API as immapp.nb, but:
# - No AddOnsParams support
# - No light theme injection
# - No screenshot in run() mode
# - Simpler, minimal implementation

hello_imgui.nb.start(gui_function, window_title="App")
hello_imgui.nb.stop()
hello_imgui.nb.is_running()
hello_imgui.nb.run(gui_function)  # No screenshot
```

**When to use**: When you only need basic HelloImGui features without ImPlot, markdown, node editor, etc.

## Blocking Mode: Screenshots

The traditional blocking mode is still useful for documentation and simple demonstrations:

```python
def simple_demo():
    imgui.text("Hello from ImGui!")
    imgui.button("Click me")
    imgui.plot_lines("Plot", np.sin(np.linspace(0, 10, 100)))

# Blocks until window closed, then shows screenshot
immapp.nb.run(simple_demo, window_title="Demo", window_size_auto=True)
```

**Features**:
- Automatically captures a screenshot when the window closes
- Displays screenshot in notebook output
- Applies light theme automatically
- Useful for creating documentation with embedded visuals

**Limitations**:
- Blocks notebook execution
- No live interaction with variables
- Cannot run cells while GUI is open

**Requirements**: Requires a window server (X11, Wayland, macOS WindowServer, etc.). Will not work on Google Colab or other headless environments.

## Differences: immapp.nb vs hello_imgui.nb

| Feature | `immapp.nb` | `hello_imgui.nb` |
|---------|------------|-----------------|
| Basic start/stop/run | ✅ | ✅ |
| AddOnsParams support | ✅ ImPlot, markdown, etc. | ❌ |
| Light theme auto-apply | ✅ | ❌ |
| Screenshot in run() | ✅ | ❌ |
| Function signature shortcuts | ✅ with addon flags | ✅ basic only |
| Notebook-friendly defaults | ✅ | ✅ |

**Recommendation**: Use `immapp.nb` unless you specifically need a minimal HelloImGui-only solution.

## Complete Demo Notebook

For a comprehensive, working demonstration, see:

**📓 [demo_interactive_notebook.ipynb](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/notebooks/demo_interactive_notebook.ipynb)**

This notebook demonstrates:
- Simple counter with real-time updates
- Live plotting with ImPlot
- Data visualization dashboard
- Practical use cases

For extensive testing coverage, see:
- [test_immapp_nb.ipynb](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/notebooks/test_immapp_nb.ipynb)
- [test_hello_imgui_nb.ipynb](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/notebooks/test_hello_imgui_nb.ipynb)

## Async Foundation

Under the hood, `nb.start()` uses `run_async()` to enable the non-blocking behavior. For more details on the async architecture, see [Async Execution](python_async.md).

## Tips & Best Practices

### 1. Use Mutable Containers

Use dictionaries or lists for shared state (not primitive values):

```python
# ✅ Good - mutable container
state = {"value": 0}

def gui():
    imgui.text(f"Value: {state['value']}")

# Can update from notebook
state["value"] = 100
```

```python
# ❌ Bad - reassignment doesn't work
value = 0

def gui():
    imgui.text(f"Value: {value}")  # Won't see changes!

# This creates a new variable, doesn't update GUI's reference
value = 100
```

### 2. Always Stop Before Starting New GUI

```python
# Stop previous GUI first
if immapp.nb.is_running():
    immapp.nb.stop()

# Now start new one
immapp.nb.start(new_gui)
```

Or rely on auto-stop (but you'll see a warning):

```python
immapp.nb.start(gui1)  # First GUI
immapp.nb.start(gui2)  # Automatically stops gui1 (with warning)
```

### 3. Use `window_size_auto=True` for Responsive GUIs

```python
# GUI adapts to content size
immapp.nb.start(gui, window_size_auto=True)
```

### 4. Keep GUI Window Visible with `top_most=True`

```python
# Window stays above browser (default in nb module)
immapp.nb.start(gui, top_most=True)
```

### 5. Check Status Before Operations

```python
if immapp.nb.is_running():
    print("GUI is active")
    # Update data
else:
    print("Start GUI first")
```

## Troubleshooting

### GUI Not Updating When I Change Variables

**Problem**: You modify a variable in a notebook cell but the GUI doesn't reflect changes.

**Solution**: Ensure you're using mutable containers (dict, list) and modifying their contents, not reassigning variables.

### Window Disappears Behind Browser

**Problem**: GUI window gets hidden behind the browser.

**Solution**: Use `top_most=True` (enabled by default with `nb.start()`):

```python
immapp.nb.start(gui, top_most=True)
```

### "Already Running" Warning

**Problem**: You see a warning about a GUI already running.

**Solution**: Stop the previous GUI first:

```python
immapp.nb.stop()  # Stop old GUI
immapp.nb.start(new_gui)  # Start new one
```

### Notebook Becomes Unresponsive

**Problem**: Notebook cells won't execute after starting GUI.

**Solution**: You might be using blocking `run()` instead of non-blocking `start()`:

```python
# ❌ Blocks notebook
immapp.nb.run(gui)

# ✅ Keeps notebook responsive
immapp.nb.start(gui)
```

### No Screenshot Appears (Blocking Mode)

**Problem**: Using `immapp.nb.run()` but no screenshot displays.

**Solution**:
1. Make sure to close the window (screenshot is captured on close)
2. Check that you're in a notebook environment with display support
3. Verify not running on headless system (Google Colab, remote server)

## Platform Support

| Platform | Non-blocking | Blocking + Screenshot |
|----------|-------------|---------------------|
| macOS | ✅ | ✅ |
| Windows | ✅ | ✅ |
| Linux (X11/Wayland) | ✅ | ✅ |
| Google Colab | ❌ | ❌ |
| Remote Jupyter | ⚠️ Requires X11 forwarding | ⚠️ |
| JupyterLab/Notebook | ✅ | ✅ |
| VS Code Jupyter | ✅ | ✅ |

## See Also

- [Async Execution](python_async.md): Understanding the async foundation
- [HelloImGui Runner](../runners/hello_imgui.md): Full RunnerParams documentation
- [ImmApp](../runners/immapp.md): AddOns and integration details
- [Demo Notebook](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/notebooks/demo_interactive_notebook.ipynb): Working examples
