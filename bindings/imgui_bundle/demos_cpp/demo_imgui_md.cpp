// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Acknowledgments
// This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "immapp/immapp.h"

std::string exampleMarkdownString()
{
    return R"(
# Markdown example

Hello World! <br>
![World](images/world.png)

## Acknowledgments
This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

### Supported features

imgui_md currently supports the following markdown functionality:

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

----

*Warning about tables layout*: the first row will impose the columns widths.
Use nbsp\; to increase the columns sizes on the first row if required.

As an example, the table below:

| Continent&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Population&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Number of Countries |
|-----------|------------|---------------------|
| Africa    | 1.3 billion | 54                  |
| Antarctica | 0 | 0          |
| Asia      | 4.5 billion | 48                  |
| Europe    | 743 million | 44                  |
| North America | 579 million | 23              |
| Oceania   | 41 million  | 14                  |
| South America | 422 million | 12              |

Can be created with this code (where lots of nbsp\; were added to enforce the column widths on the first row):<br><br>

```
| Continent&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Population&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Number of Countries |
|-----------|------------|---------------------|
| Africa    | 1.3 billion | 54                  |
| Antarctica | 0 | 0          |
| Asia      | 4.5 billion | 48                  |
| Europe    | 743 million | 44                  |
| North America | 579 million | 23              |
| Oceania   | 41 million  | 14                  |
| South America | 422 million | 12              |
```
)";
}


void demo_imgui_md()
{
    ImGuiMd::Render(exampleMarkdownString());
}
