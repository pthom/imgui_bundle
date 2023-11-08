// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/animate_logo.h"
#include "immapp/browse_to_url.h"


void demo_imgui_show_demo_window()
{
    ImGuiMd::RenderUnindented(R"(
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm.

         Advice: the best way to learn about the numerous ImGui widgets usage is to use the online "ImGui Manual" (once inside the manual, you may want to click the "Python" checkbox)
    )");
    if (ImGui::Button("Open ImGui Manual"))
        ImmApp::BrowseToUrl("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html");

    ImGui::NewLine();
    ImGui::Separator();
    ImGui::ShowDemoWindow();
    AnimateLogo("images/logo_imgui_600.png", 2.f, ImVec2(1.f, 4.8f), 0.45f, "https://github.com/ocornut/imgui");
}
