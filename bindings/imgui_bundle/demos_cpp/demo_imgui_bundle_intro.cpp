#include "imgui.h"
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"
#include "imgui/misc/cpp/imgui_stdlib.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "immapp/clock.h"
#include "demo_utils/api_demos.h"
#include "demo_utils/animate_logo.h"

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
    if (ImGui::CollapsingHeader("Repository folders structure"))
        ShowMarkdownDocFile("ibd_folders_structure");
    if (ImGui::CollapsingHeader("Build and install instruction"))
        ShowMarkdownDocFile("ibd_install");

    if (ImGui::CollapsingHeader("Dear ImGui - Immediate gui"))
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

    if (ImGui::CollapsingHeader("Hello ImGui - Starter pack"))
        ShowMarkdownDocFile("ibd_manual_himgui");

    if (ImGui::CollapsingHeader("ImmApp - Immediate App"))
        ShowMarkdownDocFile("ibd_manual_immapp");

    if (ImGui::CollapsingHeader("C++ / Python porting advices"))
        ShowPortingAdvices();

    if (ImGui::CollapsingHeader("Words from the author"))
        ShowMarkdownDocFile("ibd_words_author");

    AnimateLogo("images/logo_imgui_bundle_512.png", 1., ImVec2(0.5f, 3.f), 0.45f);
}
