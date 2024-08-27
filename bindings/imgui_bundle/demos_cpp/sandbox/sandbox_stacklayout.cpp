#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "imgui.h"
#include "immapp/immapp.h"
#include "imgui-node-editor/imgui_node_editor.h"

namespace ed = ax::NodeEditor;


void GuiNode()
{
    // Basically a vertical layout with 2 inner horizontal layouts that contain text elements + a spring element
    ImGui::BeginVertical("V");
    {
        ImGui::BeginHorizontal("H");
        {
            ImGui::Text("Hello");
            ImGui::Spring();
            ImGui::Text("world");  // With the new version, this is clipped out!
        }
        ImGui::EndHorizontal();

        ImGui::BeginHorizontal("H2");
        {
            ImGui::Text("Hello");
            ImGui::Spring();
            ImGui::Text("world");
            ImGui::Text("And again");
        }
        ImGui::EndHorizontal();
    }
    ImGui::EndVertical();
}


void Gui()
{
    // A simple node editor with a single node
    ed::Begin("Node editor");
    ed::BeginNode(ed::NodeId(1));
    {
        GuiNode();
    }
    ed::EndNode();
    ed::End();
}


int main(int, char**)
{
    // Run the application using ImmApp (from ImGui Bundle)
    // This is simply a way to quickly setup an application with ImGui + Node Editor
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withNodeEditor = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
#else // #if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
int main() {}
#endif
