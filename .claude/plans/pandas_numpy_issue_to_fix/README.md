# Pandas/NumPy Array Compatibility Issue - TODO

## Status: Fixed in Demo, Pending C++ Error Messages

### What Was Done ✅
- **Fixed:** `demo_implot_stock.py` now works by wrapping pandas arrays with `np.array()`
- **Root cause identified:** Pandas operations create read-only numpy arrays (`writeable=False`)
- **Complete analysis:** See documentation files below

### Files in This Directory

1. **`FINAL_STATUS.md`** - Start here! Current state summary and recommendations
2. **`LITGEN_MODIFICATION_GUIDE.md`** - Complete guide for implementing C++ error messages
3. **`PATCH_EXAMPLE.cpp`** - Working C++ code example for better error handling
4. **`ISSUE_RESOLUTION.md`** - Technical deep-dive into the issue

### What Needs To Be Done

Implement better C++ error messages so users get:

**Instead of:**
```
TypeError: plot_line(): incompatible function arguments...
Invoked with types: str, ndarray, ndarray
```

**They get:**
```
RuntimeError: Parameter 'xs' is a read-only numpy array, commonly from:
  df.index.map(lambda ts: ts.timestamp()).to_numpy()

Fix: Create a writable copy:
  xs = np.array(xs)
```

### Implementation Options

**Option A: Quick Manual Patch** (~1-2 hours)
- Edit `external/implot/bindings/pybind_implot.cpp` directly
- Add helper function and modify plot_line bindings
- See `PATCH_EXAMPLE.cpp` for exact code

**Option B: Proper Litgen Solution** (~1-2 days)
- Modify litgen template to generate better error handling
- See `LITGEN_MODIFICATION_GUIDE.md` for complete guide

### Key Files in Main Codebase

**Already Fixed:**
- `bindings/imgui_bundle/demos_python/demos_implot/demo_implot_stock.py`

**To Modify (for C++ errors):**
- `external/implot/bindings/pybind_implot.cpp` (manual patch)
- OR litgen templates (proper solution)

### Detection Logic (For Reference)

```python
# An array will fail if:
not arr.flags.writeable  # Read-only (DEFINITE failure)

# Optionally also check:
not arr.flags.owndata and 'pandas' in type(arr.base).__module__
```

### Next Session TODO

1. Review `FINAL_STATUS.md` for current state
2. Decide: manual patch vs. litgen modification
3. Follow `LITGEN_MODIFICATION_GUIDE.md` for implementation
4. Test with pandas arrays to verify error message
5. Consider applying to all ImPlot array-accepting functions

---

**Date:** February 20, 2026  
**Session:** Completed analysis and demo fix  
**Collaborators:** Pascal + AI assistant
