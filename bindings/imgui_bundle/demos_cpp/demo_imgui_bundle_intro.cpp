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

void ShowPortingAdvices()
{
    ShowMarkdownDocFile("ibd_port_general_advices");
    DemoRadioButton();

    ImGui::NewLine(); ImGui::NewLine(); ImGui::NewLine();

    ShowMarkdownDocFile("ibd_port_enums");
    DemoInputTextUpperCase();
}


void demo_imgui_bundle_intro()
{
    static AppState app_state;

    ShowMarkdownDocFile("ibd_front_matter");
    ImGui::Separator();

    if (ImGui::CollapsingHeader("Introduction"))
        ShowMarkdownDocFile("ibd_intro");

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

        ShowMarkdownDocFile("ibd_manual_imgui");
        immediate_gui_example();
        ImGui::Separator();
    }

    if (ImGui::CollapsingHeader("C++ / Python porting advices"))
        ShowPortingAdvices();

}
