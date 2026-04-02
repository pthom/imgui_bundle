// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Acknowledgments
// This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "immapp/immapp.h"

std::string exampleMarkdownString()
{
    std::string md = R"(
# Markdown example (H1)

Hello World!

## Acknowledgments (H2)
This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

### Supported features (H3)

imgui_md currently supports the following markdown functionality.

#### Text formatting (H4)

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
* Block code like this (using \`\`\`)
```
int answer()
{
    return 42;
}
```
* Separator (see below)

#### Images (H4)

Images can be loaded from local assets:

![World](images/world.png)
)";

#ifdef IMGUI_MARKDOWN_WITH_DOWNLOAD_IMAGES
    md += R"(
Fetching images from an url also works

![Photo](https://picsum.photos/id/1018/300/200)

You can also use HTML img tags to control the size:

<img src="https://picsum.photos/id/237/300/200" width="100">
)";
#endif

    md += R"(
----

#### Tables (H4)

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
