// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/animate_logo.h"


void demo_imgui_show_demo_window()
{
    ImGuiMd::RenderUnindented(R"(
        # Dear ImGui demo
         [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm.

         Advices:
         * The best way to learn about the numerous ImGui widgets is to open [Dear ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html).
         * Dear ImGui Manual shows code snippets in C++, but you can refer to [these instructions](https://pthom.github.io/imgui_bundle/porting.html) on how to easily convert C++ ImGui code to Python.
    )");

    ImGui::NewLine();
    ImGui::Separator();
    ImGui::ShowDemoWindow();
    AnimateLogo("images/logo_imgui_600.png", 2.f, ImVec2(1.f, 4.8f), 0.45f, "https://github.com/ocornut/imgui");
}
