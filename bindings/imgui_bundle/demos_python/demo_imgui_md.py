# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui_md, immapp


def example_markdown_string() -> str:
    markdown = r"""
# Markdown example (H1)

Hello World!

## Acknowledgments (H2)
This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

## Supported features (H2)

imgui_md currently supports the following markdown functionality.

### Text formatting (H3)

* Wrapped text
* Headers
* *Emphasis* (\*Emphasis\*)
* **Bold** (\*\*Bold\*\*)
* Ordered and unordered list, sub-lists
* [Link](https://github.com/mekhontsev/imgui_md)  ( \[Link\](https://github.com/mekhontsev/imgui_md) )
* Image
* Horizontal rule (add "\-\-\-" on a line)
* Tables
* <u>Underline</u> via \<u>...\</u>
* ~~Strikethrough~~
* HTML elements: \<br> \<hr> \<u> \<div> \&nbsp;
* Backslash Escapes
* Inline `code element` (using \`code element\`)
* Tables
* Native LaTeX math, inline (`$...$`) and display (`$$...$$`)
* Block code like this (using \`\`\`)
```
int answer()
{
    return 42;
}
```
* Separator (see below)

---

### Images

Images can be loaded from local assets or from URLs:

![World](images/world.png)

Online images are downloaded asynchronously (a spinner is shown while loading):

![Photo](https://picsum.photos/id/1018/300/200)

You can also use HTML img tags to control the size:

<img src="https://picsum.photos/id/237/300/200" width="100">

----

### Tables

*Warning about tables layout*: the first row will impose the columns widths.
Use nbsp\; to increase the columns sizes on the first row if required.

As an example, the table below (where columns are resizable!)

| Continent      |   Population  | Number of Countries |
|----------------|--------------:|:-------------------:|
| Africa         |1300 million   |54                   |
| Antarctica     |0              |0                    |
| Asia           |4500 million   |48                   |
| Europe         | 743 million   |44                   |
| North America  | 579 million   |23                   |
| Oceania        |  41 million   |14                   |
| South America  | 422 million   |12                   |

Can be created with this code

```
| Continent      |   Population  | Number of Countries |
|----------------|--------------:|:-------------------:|
| Africa         |1300 million   |54                   |
| Antarctica     |0              |0                    |
| Asia           |4500 million   |48                   |
| Europe         | 743 million   |44                   |
| North America  | 579 million   |23                   |
| Oceania        |  41 million   |14                   |
| South America  | 422 million   |12                   |
```

---

### Math formulas

**Inline math with \$...\$**

Inline math uses single dollar delimiters. For example the line below

A famous math equality: $\sum_{i=0}^{n} i = \frac{n(n+1)}{2}$.

Is generated with

```
A famous math equality: $\sum_{i=0}^{n} i = \frac{n(n+1)}{2}$.
```

**Display math with \$\$...\$\$**

Display math uses double dollars on its own line. The quadratic formula:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

Is generated with

```
$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

Sums, integrals, matrices all work:

$$
\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}
\qquad
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}
\qquad
e^{i\pi} + 1 = 0
$$

> **Note**
> Rendering is powered by [MicroTeX](https://github.com/NanoMichael/MicroTeX)
> Enable it by passing `with_latex=True` to `immapp.run()`.
    """
    return markdown


def demo_gui():
    s = example_markdown_string()
    imgui_md.render(s)
    # Note: you may also use:
    #   imgui_md.render_unindented(s)
    # (it will remove the main indentation of the Markdown string before rendering it,
    # which is useful when the string is defined inside a function with indentation)

def main():
    immapp.run(demo_gui, with_latex=True, window_size=(800, 800))


if __name__ == "__main__":
    main()
