#include "imgui.h"
#include "imgui/misc/cpp/imgui_stdlib.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "demo_utils/api_demos.h"

#include <string>


class AppState {
public:
    int counter = 0;
    std::string name = "";
};

void DemoRadioButton()
{
    static int value = 0;
    bool clicked;
    clicked = ImGui::RadioButton("radio a", &value, 0);
    ImGui::SameLine();
    clicked = ImGui::RadioButton("radio b", &value, 1);
    ImGui::SameLine();
    clicked = ImGui::RadioButton("radio c", &value, 2);
    (void) clicked;
}

void ShowCodeAdvices()
{
    const char *cpp_code = R"(
        void DemoRadioButton()
        {
            static int value = 0;
            ImGui::RadioButton("radio a", &value, 0); ImGui::SameLine();
            ImGui::RadioButton("radio b", &value, 1); ImGui::SameLine();
            ImGui::RadioButton("radio c", &value, 2);
        }
    )";

    const char *python_code = R"(
        @immapp.static(value=0)
        def demo_radio_button():
            static = demo_radio_button
            clicked, static.value = imgui.radio_button("radio a", static.value, 0)
            imgui.same_line()
            clicked, static.value = imgui.radio_button("radio b", static.value, 1)
            imgui.same_line()
            clicked, static.value = imgui.radio_button("radio c", static.value, 2)
    )";

    ImGuiMd::RenderUnindented(R"(
    ImGui is a C++ library that was ported to Python. In order to work with it you will often refer to its [demo](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html), which shows example code in C++.

    In order to translate from C++ to Python:
    1. Change the function names and parameters' names from `CamelCase` to `snake_case`
    2. Change the way the output are handled.
        a. in C++ `ImGui::RadioButton` modifies its second parameter (which is passed by address) and returns true if the user clicked the radio button.
        b. In python, the (possibly modified) value is transmitted via the return: `imgui.radio_button` returns a `Tuple[bool, str]` which contains `(user_clicked, new_value)`.
    3. if porting some code that uses static variables, use the `@static` decorator.
        In this case, this decorator simply adds a variable `value` at  the function scope. It is is preserved between calls.
       Normally, this variable should be accessed via `demo_radio_button.value`, however the first line of the function adds a synonym named static for more clarity.
       Do not overuse them! Static variable suffer from almost the same shortcomings as global variables, so you should prefer to modify an application state.
    )");
    ImGui::NewLine();

    DemoRadioButton();
    ShowPythonVsCppCode(python_code, cpp_code);
}


void DemoInputTextUpperCase()
{
    static char text[64] = "";
    ImGuiInputTextFlags flags = (
          ImGuiInputTextFlags_CharsUppercase
        | ImGuiInputTextFlags_CharsNoBlank
    );
    /*bool changed = */ ImGui::InputText("Upper case, no spaces", text, 64, flags);
}

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


void ShowTextInputAdvice()
{
    std::string cppCode = R"(
        void DemoInputTextUpperCase()
        {
            static char text[64] = "";
            ImGuiInputTextFlags flags = (
                ImGuiInputTextFlags_CharsUppercase
                | ImGuiInputTextFlags_CharsNoBlank
            );
            /*bool changed = */ ImGui::InputText("Upper case, no spaces", text, 64, flags);
        }
    )";

    std::string pythonCode = R"(
        @immapp.static(text="")
        def demo_input_text_decimal() -> None:
            static = demo_input_text_decimal
            flags:imgui.InputTextFlags = (
                    imgui.InputTextFlags_.chars_uppercase.value
                  | imgui.InputTextFlags_.chars_no_blank.value
                )
            changed, static.text = imgui.input_text("Upper case, no spaces", static.text, flags)
    )";

    ImGuiMd::RenderUnindented(R"(
        In the example below, two differences are important:

        ## InputText functions:
        imgui.input_text (Python) is equivalent to ImGui::InputText (C++)

        * In C++, it uses two parameters for the text: the text pointer, and its length.
        * In python, you can simply pass a string, and get back its modified value in the returned tuple.

        ## Enums handling:

        * `ImGuiInputTextFlags_` (C++) corresponds to `imgui.InputTextFlags_` (python) and it is an _enum_ (note the trailing underscore).
        * `ImGuiInputTextFlags` (C++) corresponds to `imgui.InputTextFlags` (python) and it is an _int_  (note: no trailing underscore)

        You will find many similar enums.

        The dichotomy between int and enums, enables you to write flags that are a combinations of values from the enum (see example below).
    )");

    ImGui::NewLine();
    DemoInputTextUpperCase();
    ShowPythonVsCppCode(pythonCode, cppCode);

    ImGuiMd::RenderUnindented(R"(
        ---
        Note: by using imgui_stdlib.h, it is also possible to write:

        ```cpp
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
    )");
}



void demo_imgui_bundle()
{
    static AppState app_state;

    ImGuiMd::RenderUnindented(R"(
        # ImGui Bundle
        [ImGui Bundle](https://github.com/pthom/imgui_bundle) is a collection of python bindings for [Dear ImGui](https://github.com/ocornut/imgui.git), and various libraries from its ecosystem.
        The bindings were autogenerated from the original C++ code, so that they are easier to keep up to date, and the python API closely matches the C++ api.
    )");
    ImGui::Separator();

    if (ImGui::CollapsingHeader("About"))
    {
        ImGuiMd::RenderUnindented(R"(
            ### Batteries included
            ImGui Bundle includes:
            * [imgui](https://github.com/ocornut/imgui.git) : Dear ImGui: Bloat-free Graphical User interface for C++ with minimal dependencies
            * [implot](https://github.com/epezent/implot): Immediate Mode Plotting
            * [Hello ImGui](https://github.com/pthom/hello_imgui.git): cross-platform Gui apps with the simplicity of a "Hello World" app
            * [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo.git): Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui
            * [ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit): Colorizing text editor for ImGui
            * [imgui-node-editor](https://github.com/thedmd/imgui-node-editor): Node Editor built using Dear ImGui
            * [imgui-knobs](https://github.com/altschuler/imgui-knobs): Knobs widgets for ImGui
            * [ImFileDialog](https://github.com/pthom/ImFileDialog.git): A file dialog library for Dear ImGui
            * [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs)  Portable GUI dialogs library (C++11, single-header)
            * [imgui_md](https://github.com/mekhontsev/imgui_md.git): Markdown renderer for Dear ImGui using MD4C parser
            * [imspinner](https://github.com/dalerank/imspinner): Set of nice spinners for imgui
            * [imgui_toggle](https://github.com/cmdwtf/imgui_toggle): A toggle switch widget for Dear ImGui. [Homepage](https://cmd.wtf/projects#imgui-toggle)
            * [ImmVision](https://github.com/pthom/immvision.git): immediate image debugger and insights
            * [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect): A texture inspector tool for Dear ImGui
            * [imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette.git): a Sublime Text or VSCode style command palette in ImGui

            ### Philosophy
            * Mirror the original API of ImGui and other libraries
            * Original code documentation is consciously kept inside the python stubs. See for example the documentation for:
                * [imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi)
                * [implot](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot.pyi)
                * [hello imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi)
            * Fully typed bindings, so that code completion works like a charm

            ### About Dear ImGui
            [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm.
        )");
    }

    if (ImGui::CollapsingHeader("Immediate mode gui"))
    {
        auto immediate_gui_example = []() {
            // Display a text
            ImGui::Text("Counter = %i", app_state.counter);
            ImGui::SameLine(); // by default ImGui starts a new line at each widget

            // The following line displays a button
            if (ImGui::Button("increment counter"))
                // And returns true if it was clicked: you can *immediately* handle the click
                app_state.counter += 1;

            // Input a text: in python, input_text returns a tuple(modified, new_value)
            bool changed = ImGui::InputText("Your name?", &app_state.name);
            ImGui::Text("Hello %s!", app_state.name.c_str());
        };
        ImGuiMd::RenderUnindented(R"(
            An example is often worth a thousand words. The following code:

            C++
            ```cpp
            // Display a text
            ImGui::Text("Counter = %i", app_state.counter);
            ImGui::SameLine(); // by default ImGui starts a new line at each widget

            // The following line displays a button
            if (ImGui::Button("increment counter"))
                // And returns true if it was clicked: you can *immediately* handle the click
                app_state.counter += 1;

            // Input a text: in C++, InputText returns a bool and modifies the text directly
            bool changed = ImGui::InputText("Your name?", &app_state.name);
            ImGui::Text("Hello %s!", app_state.name.c_str());
            ```

            Python
            ```python
            # Display a text
            imgui.text(f"Counter = {app_state.counter}")
            imgui.same_line()  # by default ImGui starts a new line at each widget

            # The following line displays a button
            if imgui.button("increment counter"):
                # And returns true if it was clicked: you can *immediately* handle the click
                app_state.counter += 1

            # Input a text: in python, input_text returns a tuple(modified, new_value)
            changed, app_state.name = imgui.input_text("Your name?", app_state.name)
            imgui.text(f"Hello {app_state.name}!")
            ```

            Displays this:
        )");
        immediate_gui_example();
        ImGui::Separator();
    }

    if (ImGui::CollapsingHeader("Consult the ImGui interactive manual!"))
    {
        ImGuiMd::RenderUnindented(R"(
        Dear ImGui comes with a complete demo. It demonstrates all of the widgets, together with an example code on how to use them.

        [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html) is an easy way to consult this demo, and to see the corresponding code. The demo code is in C++, but read the part "Code advices" below for advices on how to translate from C++ to python.
        )");
    }

    if (ImGui::CollapsingHeader("Advices"))
        ShowCodeAdvices();

    if (ImGui::CollapsingHeader("TextInput and enums"))
        ShowTextInputAdvice();
}
