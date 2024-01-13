// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"


void demo_nanovg_launcher()
{
    static bool isFullDemoOpened = false, isSimpleDemoOpened = false;
    ImGuiMd::RenderUnindented(R"(
        # NanoVG
        [NanoVG](https://github.com/memononen/nanovg) Antialiased 2D vector drawing library on top of OpenGL for UI and visualizations.
    )");

    if (!isFullDemoOpened && !isSimpleDemoOpened)
    {
        ImGui::SameLine(ImGui::GetWindowWidth() - HelloImGui::EmSize(14.0f));
        if (HelloImGui::ImageButtonFromAsset("images/nanovg_full_demo.jpg", ImVec2(HelloImGui::EmSize(11.0f), 0.f)))
            SpawnDemo("demo_nanovg_full");
    }

    int nbCodeLines = 35;
    if (ImGui::CollapsingHeader("Full Demo"))
    {
        isFullDemoOpened = true;
        ImGui::BeginGroup();
        ImGui::Text(
            "This is the original NanoVG demo, integrated to ImGui Bundle (and also ported to python).\n"
            "Click the button below to launch the demo"
        );
        ImGui::NewLine();
        if (ImGui::Button("Run full demo"))
            SpawnDemo("demo_nanovg_full");
        ImGui::EndGroup();

        ImGui::SameLine(ImGui::GetWindowWidth() - HelloImGui::EmSize(14.0f));
        if (HelloImGui::ImageButtonFromAsset("images/nanovg_full_demo.jpg", ImVec2(HelloImGui::EmSize(11.0f), 0.f)))
            SpawnDemo("demo_nanovg_full");

        ImGui::BeginTabBar("##tabs_nano_vg_code");
        if (ImGui::BeginTabItem("Launcher Code"))
        {
            ShowPythonVsCppFile("demos_nanovg/demo_nanovg_full", nbCodeLines);
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Rendering Code"))
        {
            ShowPythonVsCppFile("demos_nanovg/demo_nanovg_full/demo_nanovg_full_impl", nbCodeLines);
            ImGui::EndTabItem();
        }
        ImGui::EndTabBar();
    }
    else
        isFullDemoOpened = false;

    if (ImGui::CollapsingHeader("Simple Demo"))
    {
        isSimpleDemoOpened = true;
        ImGui::BeginGroup();
        ImGui::Text(
            "This is a simpler demo, that shows how to display NanoVG as the background, or as a texture.\n"
            "(via a framebuffer object)\n"
            "Click the button below to launch the demo"
        );
        ImGui::NewLine();
        if (ImGui::Button("Run simple demo"))
            SpawnDemo("demo_nanovg_heart");
        ImGui::EndGroup();
        ImGui::SameLine(ImGui::GetWindowWidth() - HelloImGui::EmSize(14.0f));
        if (HelloImGui::ImageButtonFromAsset("images/nanovg_demo_heart.jpg", ImVec2(HelloImGui::EmSize(11.0f), 0.f)))
            SpawnDemo("demo_nanovg_heart");
        ShowPythonVsCppFile("demos_nanovg/demo_nanovg_heart", nbCodeLines);
    }
    else
        isSimpleDemoOpened = false;
}
