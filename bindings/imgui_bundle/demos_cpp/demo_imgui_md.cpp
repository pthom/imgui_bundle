// Acknowledgments
// This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.

#include "imgui_md/imgui_md_wrapper.h"
#include "immapp/immapp.h"

std::string exampleMardownString()
{
    return R"(
# Markdown example

Hello World! <br>
![World](images/world.jpg)

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

Most format tags can be mixed!

### Known limitations

1. table rendering: text might overflow the borders
2. div: needs to be corrected
)";
}


void DemoImGuiMd()
{
    ImGuiMd::Render(exampleMardownString());
}


int main()
{
    ImmApp::RunWithMarkdown(DemoImGuiMd, "Markdown", false, false, {800, 800});
}
