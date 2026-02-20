# Guide: Enhancing Litgen to Generate Better Error Messages for Readonly Arrays

## Goal
Modify litgen's nanobind template to generate code that detects readonly numpy arrays (common with pandas) and provides helpful error messages.

## Current Problem

**Current Error (unhelpful):**
```
TypeError: plot_line(): incompatible function arguments. The following argument types are supported:
    1. plot_line(label_id: str, values: ndarray[], ...)
    2. plot_line(label_id: str, xs: ndarray[], ys: ndarray[], ...)

Invoked with types: str, ndarray, ndarray
```

**Desired Error (helpful):**
```
RuntimeError: Parameter 'xs' is a read-only numpy array, commonly from pandas operations like:
  df.index.map(lambda ts: ts.timestamp()).to_numpy()

These arrays are incompatible with ImPlot's nanobind bindings.

Fix: Create a writable copy:
  xs = np.array(xs)
```

## Implementation Strategy

### Step 1: Add Helper Function to Generated Code

In the generated C++ file (e.g., `pybind_implot.cpp`), add this helper near the top:

```cpp
namespace {
    // Helper to check array writability with helpful error messages
    nb::ndarray<> check_array_writable(nb::handle obj, const char* param_name) {
        // Check if it's an array at all
        if (!nb::isinstance<nb::ndarray<>>(obj)) {
            throw std::runtime_error(
                std::string("Parameter '") + param_name + 
                "' must be a numpy array"
            );
        }
        
        // Try to cast - this fails for readonly arrays
        try {
            return nb::cast<nb::ndarray<>>(obj);
        } catch (const nb::cast_error&) {
            // Readonly array - provide actionable error!
            throw std::runtime_error(
                std::string("Parameter '") + param_name + 
                "' is a read-only numpy array, commonly from pandas operations like:\\n"
                "  df.index.map(lambda ts: ts.timestamp()).to_numpy()\\n\\n"
                "These arrays are incompatible with ImPlot's nanobind bindings.\\n\\n"
                "Fix: Create a writable copy:\\n"
                "  " + std::string(param_name) + " = np.array(" + std::string(param_name) + ")\\n"
            );
        }
    }
}
```

### Step 2: Modify Function Signature Generation

**Current litgen output:**
```cpp
m.def("plot_line",
    [](const char* label_id, const nb::ndarray<>& xs, const nb::ndarray<>& ys, ...)
    {
        // ... function body ...
    },
    nb::arg("label_id"), nb::arg("xs"), nb::arg("ys"), ...
);
```

**Enhanced litgen output:**
```cpp
m.def("plot_line",
    [](const char* label_id, nb::handle xs_obj, nb::handle ys_obj, ...)
    {
        // Check arrays with helpful error messages
        nb::ndarray<> xs = check_array_writable(xs_obj, "xs");
        nb::ndarray<> ys = check_array_writable(ys_obj, "ys");
        
        // Continue with existing generated code (unchanged)
        auto PlotLine_adapt_c_buffers = [](const char* label_id, 
            const nb::ndarray<>& xs, const nb::ndarray<>& ys, ...)
        {
            // ... existing checks and logic ...
        };
        
        // ... rest of function ...
    },
    nb::arg("label_id"), nb::arg("xs"), nb::arg("ys"), ...
);
```

### Step 3: Locate Litgen Template

The template to modify is likely in one of these locations:

1. **litgen package** (external dependency):
   - Look in your Python environment: `site-packages/litgen/`
   - GitHub: https://github.com/pthom/litgen
   - Template files handling nanobind buffer parameters

2. **ImGui Bundle bindings generation**:
   - `external/bindings_generation/`
   - Look for templates or code that generates `nb::ndarray<>` handling

3. **Specific to ImPlot**:
   - `external/implot/bindings/generate_implot.py`
   - `external/implot/bindings/litgen_options_implot.py`

### Step 4: Modify Litgen Template

Look for the template code that generates buffer parameter handling. It likely looks something like:

**Current template pattern:**
```python
# In litgen template
def generate_buffer_param(param_name, param_type):
    return f"const nb::ndarray<>& {param_name}"
```

**Enhanced template pattern:**
```python
def generate_buffer_param(param_name, param_type):
    # Generate object handle instead of direct ndarray
    return f"nb::handle {param_name}_obj"

def generate_buffer_check(param_name):
    # Generate the conversion with error checking
    return f"nb::ndarray<> {param_name} = check_array_writable({param_name}_obj, \"{param_name}\");"
```

### Step 5: Testing the Change

After modifying the template:

1. Regenerate bindings:
   ```bash
   cd external/implot/bindings
   python generate_implot.py
   ```

2. Rebuild the C++ extension:
   ```bash
   cd ../../..
   # Your build command
   ```

3. Test with problematic pandas array:
   ```python
   import pandas as pd
   import numpy as np
   from imgui_bundle import implot
   
   df = pd.DataFrame({'val': [1,2,3]}, 
                     index=pd.date_range('2024-01-01', periods=3))
   timestamps = df.index.map(lambda ts: ts.timestamp()).to_numpy()
   
   # Should now give helpful error!
   try:
       implot.plot_line("test", timestamps, df['val'].to_numpy())
   except RuntimeError as e:
       print(e)
       # Should show: "Parameter 'timestamps' is a read-only numpy array..."
   ```

## Alternative: Quick Manual Patch

If modifying litgen is too complex, you can manually patch the generated file:

1. Open `external/implot/bindings/pybind_implot.cpp`
2. Add the `check_array_writable` helper function
3. Manually modify the `plot_line` bindings (lines ~892 and ~976)
4. Add a comment noting it's a manual patch
5. Repeat for other critical functions

**Pros:** Quick fix, immediate results
**Cons:** Lost on next regeneration, need to maintain manually

## Recommended Approach

1. **Short term:** Manual patch `pybind_implot.cpp` for `plot_line` as proof of concept
2. **Long term:** Work with litgen to add this as a standard feature
3. **Document:** Add note in ImGui Bundle docs about pandas arrays

## Files to Investigate

Priority order:
1. `external/implot/bindings/generate_implot.py` - Entry point
2. `external/implot/bindings/litgen_options_implot.py` - Options configuration  
3. Litgen source code - Buffer parameter templates
4. `external/bindings_generation/` - Shared templates

## Success Criteria

✅ Readonly arrays produce clear, actionable error
✅ Error message mentions pandas as common cause
✅ Error shows exact code fix: `np.array(your_array)`
✅ No performance impact on valid arrays
✅ Works for all array-accepting ImPlot functions
