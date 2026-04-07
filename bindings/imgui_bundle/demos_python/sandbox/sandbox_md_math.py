"""Phase 3 sandbox: native LaTeX math in markdown via MicroTeX.

Run with the venv python that has imgui_bundle installed from the local build:
    v314/bin/python sandbox_phase3_latex.py           # LaTeX ON (default)
    v314/bin/python sandbox_phase3_latex.py --no-latex # LaTeX OFF (legacy: $ is literal)
"""
import sys
from imgui_bundle import imgui, immapp, imgui_md


MARKDOWN = r"""
# Phase 3: native LaTeX in markdown

This markdown is rendered by **imgui_md**.
Inline math like $E = mc^2$ should sit on the baseline of this text,
as should $\sqrt{a^2 + b^2}$ and $\sum_{i=0}^{n} i$.

## Display math

A quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Gaussian integral:

$$\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}$$

Matrix:

$$A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$$

## Mixed content

The Euler identity $e^{i\pi} + 1 = 0$ is sometimes called the most beautiful
equation in mathematics. Compare with the series expansion

$$e^x = \sum_{k=0}^{\infty} \frac{x^k}{k!}$$

and note how the sum in display mode looks bigger than the inline
$\sum_{k=0}^{\infty} \frac{x^k}{k!}$ version.

## Price list (stress-test $ as literal)

When LaTeX is **off**, the `$` signs below should appear as literal
dollar characters. When LaTeX is **on**, md4c parses them as math
delimiters, so unbalanced `$` may render oddly.

- Apples: $1.50
- Oranges: $2.00
- Total: $3.50
"""


def gui() -> None:
    imgui.text("Phase 3 sandbox — close window to exit")
    imgui.separator()
    imgui_md.render_unindented(MARKDOWN)


def main() -> None:
    with_latex = "--no-latex" not in sys.argv
    title = "Phase 3 LaTeX sandbox (LaTeX ON)" if with_latex else "Phase 3 LaTeX sandbox (LaTeX OFF)"
    immapp.run(
        gui_function=gui,
        window_title=title,
        window_size=(900, 900),
        with_latex=True,
        with_markdown=True,
    )


if __name__ == "__main__":
    main()
