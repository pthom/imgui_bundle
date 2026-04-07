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

## Literal `$` and edge cases

md4c uses pandoc-style flank rules for `$...$`: a `$` is **opener-eligible**
when the character BEFORE it is whitespace or punctuation (looks like a
word start), and **closer-eligible** when the character AFTER it is
whitespace or punctuation (looks like a word end). To form a math span,
md4c needs an opener-eligible `$` followed (later) by a closer-eligible `$`.
Contents in between can be anything.

**Cases that stay literal (no math rendering):**

- Apples: $1.50, oranges: $2.00, total: $3.50.
  (every `$` is followed by a digit, so NONE of them is closer-eligible —
  no pair forms, all dollars stay as literal text)
- A single `$` alone in a paragraph is also literal (no closer to pair with):
  Bring me $5.

**Cases that DO parse as math (sometimes surprisingly):**

- `$5 + 5 = 10$` actually renders as math — try it: $5 + 5 = 10$.
  (the trailing `$` is at end-of-sentence, so it IS closer-eligible)
- `$1.50$` with a balanced trailing `$` also renders as math: $1.50$.

**Forcing literal `$` with backslash escapes:**

If you want literal `$`-delimited text in prose, escape with `\` :

- `\$5 + 5 = 10\$` renders as: \$5 + 5 = 10\$
- `Total: \$3.50` renders as: Total: \$3.50
"""


def gui() -> None:
    _, imgui.get_style().font_scale_main = imgui.slider_float("Font scale", imgui.get_style().font_scale_main, 0.25, 4.0)
    imgui.text("Phase 3 sandbox — close window to exit")
    imgui.separator()
    imgui_md.render_unindented(MARKDOWN)


def main() -> None:
    immapp.run(
        gui_function=gui,
        window_size=(900, 900),
        with_latex=True,
        with_markdown=True,
    )


if __name__ == "__main__":
    main()
