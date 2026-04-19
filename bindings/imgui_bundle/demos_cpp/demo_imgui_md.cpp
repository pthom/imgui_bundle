// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Acknowledgments
// This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

#include "hello_imgui/hello_imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "immapp/immapp.h"

std::string exampleMarkdownString()
{
    std::string md = R"(
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
)";

#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
    md += R"(
Online images are downloaded asynchronously (a spinner is shown while loading):

![Photo](https://picsum.photos/id/1018/300/200)

You can also use HTML img tags to control the size:

<img src="https://picsum.photos/id/237/300/200" width="100">
)";
#endif

    md += R"(
----
### Tables

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
)";
    return md;
}


void demo_imgui_md()
{
    ImGuiMd::Render(exampleMarkdownString());
    // Note: you may also use:
    //   ImGuiMd::RenderUnindented(exampleMarkdownString());
    // (it will remove the main indentation of the Markdown string before rendering it,
    // which is useful when the string is defined inside a function with indentation)
}


// Standalone main(): bypasses the auto-generated main from ibd_add_auto_demo,
// which would only enable withMarkdown. We need withLatex=true (which implies
// withMarkdown=true) so the LaTeX section actually renders.
// When this file is built as part of the demo_imgui_bundle aggregator
// (IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY), this main() is excluded.
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = demo_imgui_md;
    runnerParams.windowTitle = "Dear ImGui Bundle - Markdown demo";
    runnerParams.windowSize = {800, 800};

    ImmApp::AddOnsParams addons;
    addons.withLatex = true;  // implies withMarkdown=true

    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
