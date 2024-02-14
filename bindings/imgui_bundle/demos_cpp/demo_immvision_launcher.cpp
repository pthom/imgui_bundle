// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/api_demos.h"

#ifndef IMGUI_BUNDLE_WITH_IMMVISION
void demo_immvision_launcher()
{
    ImGui::Text("Dear ImGui Bundle was compiled without support for ImmVision (this requires OpenCV and OpenGl)");
}

#else
#include "immvision/immvision.h"

void demo_immvision_display();
void demo_immvision_link();
void demo_immvision_inspector();
void demo_immvision_process();


void demo_immvision_launcher()
{
    if (HelloImGui::GetRunnerParams()->rendererBackendType != HelloImGui::RendererBackendType::OpenGL3)
    {
        ImGui::Text("ImmVision is only supported with OpenGL renderer");
        return;
    }

    ImGuiMd::RenderUnindented(R"(
        # ImmVision
        [ImmVision](https://github.com/pthom/immvision) is an immediate image debugger.
        It is based on OpenCv and can analyse RGB & float, images with 1 to 4 channels.

        Whereas *imgui_tex_inspect* is dedicated to texture analysis, *immvision* is more dedicated to image processing and computer vision.

        Open the demos below by clicking on their title.
    )");

    if (ImGui::CollapsingHeader("Display images"))
    {
        demo_immvision_display();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_display");
    }
    if (ImGui::CollapsingHeader("Link images zoom"))
    {
        demo_immvision_link();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_link");
    }
    if (ImGui::CollapsingHeader("Image inspector"))
    {
        demo_immvision_inspector();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_inspector");
    }
    if (ImGui::CollapsingHeader("Example with image processing"))
    {
        demo_immvision_process();
        ShowPythonVsCppFile("demos_immvision/demo_immvision_process", 40);
    }
}

#endif
