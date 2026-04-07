# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle

"""Tests for imgui_microtex (Level 1 API: LaTeX -> RGBA pixel buffer).

These tests don't require a GUI context - they only test the CPU rendering.
Run with: pytest tests/test_imgui_microtex.py
"""

import sys
import os
from pathlib import Path


def _find_font_files():
    """Find the MicroTeX font files (clm1 + otf) relative to the repo root."""
    repo_root = Path(__file__).resolve().parent.parent
    font_dir = repo_root / "external" / "imgui_microtex" / "MicroTeX" / "res" / "lm-math"
    return str(font_dir / "latinmodern-math.clm1"), str(font_dir / "latinmodern-math.otf")


def _ensure_initialized():
    """Init once, safe to call multiple times (MicroTeX does not support re-init)."""
    from imgui_bundle import imgui_microtex
    if not imgui_microtex.is_initialized():
        clm_file, otf_file = _find_font_files()
        if not os.path.exists(clm_file):
            raise FileNotFoundError(f"Font file not found: {clm_file}")
        imgui_microtex.init(clm_file, otf_file)


def test_render_basic():
    """Test that a simple formula renders to a non-empty pixel buffer."""
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui_microtex
    _ensure_initialized()

    formula = imgui_microtex.render("x^2 + y^2 = r^2", 20.0)
    assert formula.width > 0
    assert formula.height > 0


def test_render_pixels_as_array():
    """Test that pixels_as_array returns a numpy array with correct shape."""
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui_microtex
    import numpy as np
    _ensure_initialized()

    formula = imgui_microtex.render(r"\frac{a}{b}", 30.0)
    pixels = formula.pixels_as_array()

    assert isinstance(pixels, np.ndarray)
    assert pixels.shape == (formula.height, formula.width, 4)
    assert pixels.dtype == np.uint8

    # The formula should have some non-zero pixels (not all transparent)
    assert pixels[:, :, 3].max() > 0, "Formula rendered as all-transparent"


def test_render_multiple_formulas():
    """Test rendering multiple formulas without crash."""
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui_microtex
    _ensure_initialized()

    formulas = [
        r"E = mc^2",
        r"\int_0^\infty e^{-x^2} dx",
        r"\sum_{n=0}^{\infty} \frac{x^n}{n!}",
        r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
    ]

    for latex in formulas:
        formula = imgui_microtex.render(latex, 20.0)
        assert formula.width > 0
        assert formula.height > 0


def test_baseline_y():
    """Test that baseline_y is a valid pixel y-offset within the image.

    `baseline_y` is the absolute pixel distance from the TOP of the
    (padded) image down to the typographic baseline. It must therefore
    be a non-negative integer no larger than the image height.
    """
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui_microtex
    _ensure_initialized()

    formula = imgui_microtex.render("x^2", 20.0)
    assert isinstance(formula.baseline_y, int), \
        f"baseline_y is {type(formula.baseline_y).__name__}, expected int"
    assert 0 <= formula.baseline_y <= formula.height, \
        f"baseline_y ({formula.baseline_y}) out of range [0, {formula.height}]"


def test_rendering_structure():
    """Test structural properties of rendered formulas (catches layout regressions)."""
    if sys.platform == "win32":
        return

    from imgui_bundle import imgui_microtex
    _ensure_initialized()

    x = imgui_microtex.render("x", 20.0)
    x2 = imgui_microtex.render("x^2", 20.0)
    frac = imgui_microtex.render(r"\frac{a}{b}", 20.0)
    big = imgui_microtex.render(r"\sum_{n=0}^{\infty} \frac{x^n}{n!}", 20.0)

    # x^2 should be wider than x (superscript adds width)
    assert x2.width > x.width, f"x^2 ({x2.width}) should be wider than x ({x.width})"

    # x^2 should be taller than x (superscript adds height)
    assert x2.height > x.height, f"x^2 ({x2.height}) should be taller than x ({x.height})"

    # a fraction should be taller than a simple letter
    assert frac.height > x.height, f"frac ({frac.height}) should be taller than x ({x.height})"

    # a complex formula should be wider than a simple one
    assert big.width > x2.width, f"sum formula ({big.width}) should be wider than x^2 ({x2.width})"


# def test_save_formula_images():
#     """Render formulas and save as PNG images in a temporary directory."""
#     if sys.platform == "win32":
#         return
#
#     from imgui_bundle import imgui_microtex
#     from PIL import Image
#     import tempfile
#     _ensure_initialized()
#
#     formulas = {
#         "quadratic": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
#         "euler": r"e^{i\pi} + 1 = 0",
#         "gaussian": r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
#         "maxwell": r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}",
#         "schrodinger": r"i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi",
#         "matrix": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}^{-1} = \frac{1}{ad-bc}\begin{pmatrix} d & -b \\ -c & a \end{pmatrix}",
#         "continued_frac": r"\phi = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}}",
#         "fourier": r"\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) \, e^{-2\pi i x \xi} \, dx",
#     }
#
#     out_dir = os.path.join(tempfile.gettempdir(), "imgui_microtex_formulas")
#     os.makedirs(out_dir, exist_ok=True)
#
#     for name, latex in formulas.items():
#         formula = imgui_microtex.render(latex, 40.0)
#         pixels = formula.pixels_as_array()
#         img = Image.fromarray(pixels, "RGBA")
#         path = os.path.join(out_dir, f"{name}.png")
#         img.save(path)
#         print(f"  {name}: {formula.width}x{formula.height} -> {path}")
#
#     print(f"\nFormula images saved to: {out_dir}")


if __name__ == "__main__":
    test_render_basic()
    test_render_pixels_as_array()
    test_render_multiple_formulas()
    test_baseline_y()
    # test_save_formula_images()
    print("All tests passed!")
