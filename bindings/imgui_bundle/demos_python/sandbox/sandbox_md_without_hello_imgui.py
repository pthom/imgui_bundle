"""Demonstrates how to use imgui_md (Markdown) without using Hello ImGui.
"""

import os
if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
    os.environ["PYOPENGL_PLATFORM"] = "x11"


import OpenGL.GL as gl  # pip install PyOpenGL
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
# When using a pure python backend, prefer to import glfw before imgui_bundle (so that you end up using the standard glfw, not the one provided by imgui_bundle)
import glfw  # type: ignore
from imgui_bundle import imgui
from imgui_bundle import imgui_md
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""


app_state = AppState()


def example_markdown_string() -> str:
    markdown = r"""
# Markdown example (H1)

> **Running without HelloImGui** — pure GLFW + PyOpenGL backend.
> imgui_md.initialize_markdown() takes care of the GL loader and other
> setup automatically; no `hello_imgui.*` ceremony required.

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

| Continent | Population | Number of Countries |
|----------------|-------------|---------------------|
| Africa         | 1.3 billion | 54                  |
| Antarctica     | 0           | 0                   |
| Asia           | 4.5 billion | 48                  |
| Europe         | 743 million | 44                  |
| North America  | 579 million | 23                  |
| Oceania        | 41 million  | 14                  |
| South America  | 422 million | 12                  |

Can be created with this code

```
| Continent      | Population  | Number of Countries |
|----------------|-------------|---------------------|
| Africa         | 1.3 billion | 54                  |
| Antarctica     | 0           | 0                   |
| Asia           | 4.5 billion | 48                  |
| Europe         | 743 million | 44                  |
| North America  | 579 million | 23                  |
| Oceania        | 41 million  | 14                  |
| South America  | 422 million | 12                  |
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


def init_fonts_and_markdown():
    # uncomment to keep using the default hardcoded font, or load your default font here
    # imgui.get_io().fonts.add_font_default()

    # Enable native LaTeX math via MicroTeX (otherwise $...$ stays literal).
    md_options = imgui_md.MarkdownOptions()
    md_options.with_latex = True
    imgui_md.initialize_markdown(md_options)
    font_loader = imgui_md.get_font_loader_function()
    font_loader()


def gui():
    imgui_md.render_unindented(example_markdown_string())


def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)
    init_fonts_and_markdown()  # also calls HelloImGui::InitGlLoader() internally

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        gui()

        gl.glClearColor(1.0, 1.0, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    imgui_md.de_initialize_markdown()  # also frees the image cache internally
    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "imgui_md demo"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


if __name__ == "__main__":
    main()
