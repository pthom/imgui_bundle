# Enums and TextInput

In the example below, two differences are important:

## InputText functions:

`imgui.input_text` (Python) is equivalent to `ImGui::InputText` (C++)

-   In C++, it uses two parameters for the text: the text pointer, and its length.

-   In Python, you can simply pass a string, and get back its modified value in the returned tuple.

## Enums handling:

-   `ImGuiInputTextFlags_` (C++) corresponds to `imgui.InputTextFlags_` (python) and it is an *enum* (note the trailing underscore).

-   `ImGuiInputTextFlags` (C++) corresponds to `imgui.InputTextFlags` (python) and it is an *int* (note: no trailing underscore)

You will find many similar enums.

The dichotomy between int and enums, enables you to write flags that are a combinations of values from the enum (see example below).

## Example

C++

``` cpp
void DemoInputTextUpperCase()
{
    static char text[64] = "";
    ImGuiInputTextFlags flags = (
        ImGuiInputTextFlags_CharsUppercase
        | ImGuiInputTextFlags_CharsNoBlank
    );
    /*bool changed = */ ImGui::InputText("Upper case, no spaces", text, 64, flags);
}
```

Python

``` python
@immapp.static(text="")
def demo_input_text_decimal() -> None:
    static = demo_input_text_decimal
    flags:imgui.InputTextFlags = (
            imgui.InputTextFlags_.chars_uppercase.value
          | imgui.InputTextFlags_.chars_no_blank.value
        )
    changed, static.text = imgui.input_text("Upper case, no spaces", static.text, flags)
```

Note: in C++, by using `imgui_stdlib.h`, it is also possible to write:

``` cpp
#include "imgui/misc/cpp/imgui_stdlib.h"

void DemoInputTextUpperCase_StdString()
{
    static std::string text;
    ImGuiInputTextFlags flags = (
        ImGuiInputTextFlags_CharsUppercase
        | ImGuiInputTextFlags_CharsNoBlank
    );
    /*bool changed = */ ImGui::InputText("Upper case, no spaces", &text, flags);
}
```
