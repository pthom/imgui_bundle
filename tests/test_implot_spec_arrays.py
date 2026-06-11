# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Test that ImPlotSpec array fields accept correct numpy dtypes and reject wrong ones."""

import numpy as np
import pytest
from imgui_bundle import implot


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
