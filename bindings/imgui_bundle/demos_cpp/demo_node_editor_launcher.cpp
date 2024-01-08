// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"
#include "immapp/immapp.h"

void demo_romeo_and_juliet();


void demo_node_editor_launcher()
{
    ImGuiMd::RenderUnindented(R"(
        # imgui-node-editor
        [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a zoomable and node Editor built using Dear ImGui.

        Open the demos below by clicking on their title.
    )");

    if (ImGui::CollapsingHeader("Screenshot - BluePrint"))
    {
        ImGuiMd::RenderUnindented(R"(
            This is a screenshot showing the possibilities of the node editor
        )");
        HelloImGui::ImageFromAsset("images/node_editor_screenshot.jpg", ImmApp::EmToVec2(40.f, 0.f));
    }
    if (ImGui::CollapsingHeader("Screenshot - Image editing"))
    {
        ImGuiMd::RenderUnindented(R"(
            This is another screenshot showing the possibilities of the node editor, when combined with immvision
        )");
        HelloImGui::ImageFromAsset("images/node_editor_fiat.jpg", ImmApp::EmToVec2(60.f, 0.f));
    }
    if (ImGui::CollapsingHeader("demo basic interaction"))
    {
        if (ImGui::Button("Launch demo"))
            SpawnDemo("demo_node_editor_basic");
        ShowPythonVsCppFile("demos_node_editor/demo_node_editor_basic", 30);
    }
    if (ImGui::CollapsingHeader("Haiku - Romeo and Juliet"))
    {
        demo_romeo_and_juliet();
        ShowPythonVsCppFile("demos_node_editor/demo_romeo_and_juliet", 30);
    }
}
