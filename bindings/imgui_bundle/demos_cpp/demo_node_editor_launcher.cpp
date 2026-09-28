// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "demo_utils/api_demos.h"

void demo_romeo_and_juliet();


void demo_node_editor_launcher()
{
    RichMd::Render(R"(
        # imgui-node-editor
        [imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a zoomable and node Editor built using Dear ImGui.

        Open the demos below by clicking on their title.
    )");

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
