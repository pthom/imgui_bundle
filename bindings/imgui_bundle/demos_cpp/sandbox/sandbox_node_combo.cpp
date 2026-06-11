#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include <string>

namespace ed = ax::NodeEditor;


void Gui()
{
    static std::string text = "Hello, World!";
    static ImVec4 clearColor = ImVec4(0, 0, 0, 0);
    const char* items[] = { "AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIII", "JJJJ", "KKKK", "LLLLLLL", "MMMM", "OOOOOOO" };
    static int item_selected_idx = 0; // Here we store our selection data as an index.


    ImGui::Text("Hello, world!");

    ed::Begin("My Node Editor");

    ed::BeginNode(ed::NodeId(1));
    ImGui::Text("Hello");
    ImGui::SetNextItemWidth(200);
    ImGui::InputTextMultiline("Text", &text);

    // Pass in the preview value visible before opening the combo (it could technically be different contents or not pulled from items[])
    const char* combo_preview_value = items[item_selected_idx];
    ImGui::SetNextItemWidth(200);
    if (ImGui::BeginCombo("combo 1", combo_preview_value))
    {
        for (int n = 0; n < IM_COUNTOF(items); n++)
        {
            const bool is_selected = (item_selected_idx == n);
            if (ImGui::Selectable(items[n], is_selected))
                item_selected_idx = n;

            // Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
            if (is_selected)
                ImGui::SetItemDefaultFocus();
        }
        ImGui::EndCombo();
    }

    ImGui::ColorEdit4("Color", &clearColor.x);

    ed::EndNode();

    ed::End();
}

int main()
{
    ImmApp::AddOnsParams addonsParams;
    addonsParams.withNodeEditor = true;

    HelloImGui::RunnerParams runnerParams;
    // runnerParams.iniDisable = true;
    runnerParams.callbacks.ShowGui = Gui;

    ImmApp::Run(runnerParams, addonsParams);

    return 0;
}
#else
int main() { return 0; }
#endif
