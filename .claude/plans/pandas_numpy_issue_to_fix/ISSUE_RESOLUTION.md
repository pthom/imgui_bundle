# Issue Resolution: ImPlot plot_line() TypeError with Pandas Arrays

## The Problem

The `demo_implot_stock.py` was failing with this error:

```
TypeError: plot_line(): incompatible function arguments. The following argument types are supported:
    1. plot_line(label_id: str, values: ndarray[], ...)
    2. plot_line(label_id: str, xs: ndarray[], ys: ndarray[], ...)

Invoked with types: str, ndarray, ndarray
```

## Root Cause

**Pandas-derived numpy arrays are incompatible with nanobind's array matching.**

When arrays are created directly from pandas operations (e.g., `df.index.map().to_numpy()` or `df['Column'].to_numpy().flatten()`), they have internal metadata or memory layout that prevents nanobind from recognizing them as valid `ndarray[]` types, even though they ARE valid numpy arrays.

## The Evidence

Testing showed:
- ✓ **Pure numpy arrays** (`np.linspace`, `np.sin`, etc.) - **WORK**
- ✗ **Direct pandas-derived arrays** - **FAIL with TypeError**
- ✓ **Copied pandas arrays** (`np.array(pandas_array)`) - **WORK**
- ✓ **Arrays from `np.empty_like`** - **WORK**

The arrays that fail have `owndata=False` flag, but copying them resolves the issue.

## The Fix

Wrap pandas-derived arrays with `np.array()` to create a clean copy:

```python
# Before (FAILS):
timestamps = df.index.map(lambda ts: ts.timestamp()).to_numpy(np.float64)
opens = df["Open"].to_numpy().flatten()

# After (WORKS):
timestamps = np.array(df.index.map(lambda ts: ts.timestamp()).to_numpy(np.float64))
opens = np.array(df["Open"].to_numpy().flatten())
```

## Why ImPlot Has Worked for 3 Years

Most users create data using pure numpy operations (`np.linspace`, `np.arange`, arithmetic operations, etc.), which don't have this issue. The problem only appears when using pandas-derived data directly without copying.

## Technical Details

### What I Initially Suspected (WRONG)
I initially thought there was a bug in the stride check in `pybind_implot.cpp`:
```cpp
if (! (values.ndim() == 1 && values.stride(0) == 1))
```

I thought `stride(0)` returned bytes (8 for float64), but nanobind actually normalizes strides to element units, so `stride(0) == 1` means "1 element stride" which is correct for contiguous arrays.

### The Real Issue
Nanobind's type matching for `nb::ndarray<>` is stricter than expected. Pandas arrays have some property (possibly related to memory ownership, view vs copy, or internal buffer protocol details) that prevents them from matching the `ndarray[]` type signature, even though they're valid numpy arrays.

The solution is simple: always copy pandas-derived arrays before passing to ImPlot.

## Files Modified

- `demo_implot_stock.py`: Added `np.array()` wrapping around all pandas-derived arrays in `fetch_data()` method

## Verification

The stock demo now runs without errors and displays charts correctly.
