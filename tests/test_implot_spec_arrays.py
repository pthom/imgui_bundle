# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Test that ImPlotSpec array fields accept correct numpy dtypes and reject wrong ones."""

import gc

import numpy as np
import pytest
from imgui_bundle import implot, implot3d

# ImPlot and ImPlot3D share the same Spec array API (see generate_implot*.py).
COLOR_FIELDS = ("line_colors", "fill_colors", "marker_line_colors", "marker_fill_colors")
SPEC_CLASSES = (implot.Spec, implot3d.Spec)


def test_spec_color_fields_accept_uint32():
    spec = implot.Spec()
    arr = np.array([0xFF0000FF, 0x00FF00FF], dtype=np.uint32)
    spec.line_colors = arr
    spec.fill_colors = arr
    spec.marker_line_colors = arr
    spec.marker_fill_colors = arr


def test_spec_marker_sizes_accepts_float32():
    spec = implot.Spec()
    spec.marker_sizes = np.array([2.0, 4.0], dtype=np.float32)


def test_spec_color_fields_reject_wrong_dtype():
    spec = implot.Spec()
    for field in ("line_colors", "fill_colors", "marker_line_colors", "marker_fill_colors"):
        for bad_dtype in (np.float32, np.float64, np.int32):
            with pytest.raises(TypeError, match="np.uint32"):
                setattr(spec, field, np.array([1], dtype=bad_dtype))


def test_spec_marker_sizes_rejects_wrong_dtype():
    spec = implot.Spec()
    for bad_dtype in (np.float64, np.uint32, np.int32):
        with pytest.raises(TypeError, match="np.float32"):
            spec.marker_sizes = np.array([1], dtype=bad_dtype)


# --- Regression tests for issue #484 (array lifetime + honest read-back) ------

@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_keeps_temporary_array_alive(spec_cls):
    """A temporary array assigned to a color field must survive garbage
    collection: Spec keeps a reference to it (otherwise the raw pointer dangles).
    """
    spec = spec_cls()
    spec.line_colors = np.array([0xFF0000FF, 0x00FF00FF, 0x0000FFFF], dtype=np.uint32)
    gc.collect()
    got = spec.line_colors
    assert isinstance(got, np.ndarray)
    assert got.dtype == np.uint32
    assert list(got) == [0xFF0000FF, 0x00FF00FF, 0x0000FFFF]


@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_readback_returns_same_array(spec_cls):
    """Read-back returns the very array that was assigned (a real np.ndarray,
    not the raw pointer address)."""
    spec = spec_cls()
    arr = np.array([1, 2, 3], dtype=np.uint32)
    spec.line_colors = arr
    assert spec.line_colors is arr
    sizes = np.array([2.0, 4.0], dtype=np.float32)
    spec.marker_sizes = sizes
    assert spec.marker_sizes is sizes


@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_field_defaults_to_none(spec_cls):
    spec = spec_cls()
    for field in COLOR_FIELDS + ("marker_sizes",):
        assert getattr(spec, field) is None


@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_none_clears_field(spec_cls):
    spec = spec_cls()
    spec.line_colors = np.array([1, 2, 3], dtype=np.uint32)
    assert spec.line_colors is not None
    spec.line_colors = None
    assert spec.line_colors is None


@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_rejects_non_contiguous(spec_cls):
    """A non-contiguous array (e.g. a slice) is rejected: we keep the raw data
    pointer, so a contiguous copy would dangle."""
    spec = spec_cls()
    non_contiguous = np.arange(8, dtype=np.uint32)[::2]
    with pytest.raises(ValueError, match="contiguous"):
        spec.line_colors = non_contiguous
    # The contiguous version is accepted.
    spec.line_colors = np.ascontiguousarray(non_contiguous)


@pytest.mark.parametrize("spec_cls", SPEC_CLASSES)
def test_spec_rejects_non_array(spec_cls):
    spec = spec_cls()
    with pytest.raises(TypeError, match="np.uint32"):
        spec.line_colors = [1, 2, 3]
