# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""ImPlot accepts read-only numpy arrays (np.frombuffer, pandas columns, np.asarray of an image): it only reads them.

The generated functions take nb::ndarray<nb::ro>; this tests a hand-written one that needs no frame (add_colormap).
plot_heatmap, also hand-written, needs a plot: see tests_python_gui/test_implot_read_only_gui.py.
"""
import sys

import numpy as np


def test_add_colormap_accepts_read_only_array() -> None:
    # We skip windows, see note at the top of lg_imgui_bundle_test.py
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui, implot

    imgui_context = imgui.create_context()
    implot_context = implot.create_context()
    colors = np.array([0xFF0000FF, 0xFF00FF00, 0xFFFF0000], dtype=np.uint32)
    colors.setflags(write=False)
    implot.add_colormap("read_only_colors", colors)
    assert implot.get_colormap_size(implot.get_colormap_index("read_only_colors")) == 3
    implot.destroy_context(implot_context)
    imgui.destroy_context(imgui_context)
