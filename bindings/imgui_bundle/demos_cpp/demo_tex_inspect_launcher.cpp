// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/api_demos.h"

void demo_tex_inspect_simple();


void demo_tex_inspect_launcher()
{
    ImGuiMd::RenderUnindented(R"(
    # imgui_tex_inspect
    [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect) is a texture inspector tool for Dear ImGui
    ImGuiTexInspect is a texture inspector tool for Dear ImGui. It's a debug tool that allows you to easily inspect the data in any texture.

    Whereas *imgui_tex_inspect* is dedicated to texture analysis, *immvision* is more dedicated to image processing and computer vision.

    Open the demos below by clicking on their title.
    )");

    if (ImGui::CollapsingHeader("Simple Demo"))
    {
        demo_tex_inspect_simple();
        ShowPythonVsCppFile("demos_tex_inspect/demo_tex_inspect_simple");
    }
    if (ImGui::CollapsingHeader("Full Demo"))
    {
        ImGui::Text("Click the button below to launch the demo");
        if (ImGui::Button("Run demo"))
        {
            SpawnDemo("demo_tex_inspect_demo_window");
            ShowPythonVsCppFile("demos_tex_inspect/demo_tex_inspect_demo_window");
        }
    }
}
