// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "demo_utils/api_demos.h"

#ifndef IMGUI_BUNDLE_WITH_IMMVISION
void gui_demo_immvision_launcher()
{
    ImGui::Text("Dear ImGui Bundle was compiled without support for ImmVision (this requires OpenGL)");
}

#else
#include "immvision/immvision.h"

void gui_demo_immvision_display();
void gui_demo_immvision_link();
void gui_demo_immvision_inspector();
void gui_demo_immvision_process();


void gui_demo_immvision_launcher()
{
    if (HelloImGui::GetRunnerParams()->rendererBackendType != HelloImGui::RendererBackendType::OpenGL3)
    {
        ImGui::Text("ImmVision is only supported with OpenGL renderer");
        return;
    }

    RichMd::Render(R"(
        [ImmVision](https://github.com/pthom/immvision) is an immediate image debugger and inspector. It can display and analyse RGB & float images with 1 to 4 channels, with zoom, pan, pixel inspection, and colormaps.
    )");

    if (ImGui::CollapsingHeader("Display images"))
    {
        gui_demo_immvision_display();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_display");
    }
    if (ImGui::CollapsingHeader("Link images zoom"))
    {
        gui_demo_immvision_link();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_link");
    }
    if (ImGui::CollapsingHeader("Image inspector"))
    {
        gui_demo_immvision_inspector();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_inspector");
    }
    if (ImGui::CollapsingHeader("Example with image processing"))
    {
        gui_demo_immvision_process();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_process", 40);
    }
}

#endif
