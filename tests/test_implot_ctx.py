# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Smoke test for implot_ctx (context managers for implot).

No GUI needed: the context managers tested here only require imgui/implot
contexts, not a running frame. begin_plot/begin_subplots/push_plot_clip_rect
need a real frame and are tested in tests_python_gui/test_implot_ctx_gui.py.
"""
import sys


def test_implot_ctx_headless() -> None:
    # We skip windows, see note at the top of lg_imgui_bundle_test.py
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui, implot, implot_ctx

    imgui_context = imgui.create_context()
    with implot_ctx.create_context():
        # push/pop pairs which do not require a running frame
        with implot_ctx.push_style_color(implot.Col_.plot_bg, (1.0, 0.0, 0.0, 1.0)):
            pass
        with implot_ctx.push_style_var(implot.StyleVar_.plot_border_size, 2.0):
            pass
        with implot_ctx.push_colormap(implot.Colormap_.deep):
            pass
        with implot_ctx.push_colormap("Paired"):  # colormap by name
            pass
    imgui.destroy_context(imgui_context)
