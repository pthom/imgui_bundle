// Test patch proposed ad https://github.com/thedmd/imgui-node-editor/issues/242
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui-node-editor/imgui_node_editor.h"

namespace ed = ax::NodeEditor;

ImVec4 gColor(0.1, 0.2, 0.8, 1);
std::string gText = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";

void Gui()
{
    ed::Begin("My Node Editor");

    ed::BeginNode(1);

    ImGui::Text("Node 1");
    ImGui::ColorEdit4("Color", &gColor.x);

    static bool item_highlight = false;
    int item_highlighted_idx = -1; // Here we store our highlighted data as an index.
    ImGui::Checkbox("Check!", &item_highlight);

//    {
//        const char* items[] = { "AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIII", "JJJJ", "KKKK", "LLLLLLL", "MMMM", "OOOOOOO" };
//        static int item_selected_idx = 0; // Here we store our selected data as an index.
//        if (ImGui::BeginListBox("listbox 1"))
//        {
//            for (int n = 0; n < IM_ARRAYSIZE(items); n++)
//            {
//                const bool is_selected = (item_selected_idx == n);
//                if (ImGui::Selectable(items[n], is_selected))
//                    item_selected_idx = n;
//
//                if (item_highlight && ImGui::IsItemHovered())
//                    item_highlighted_idx = n;
//
//                // Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
//                if (is_selected)
//                    ImGui::SetItemDefaultFocus();
//            }
//            ImGui::EndListBox();
//        }
//    }

    {
        // Simplified one-liner Combo() API, using values packed in a single constant string
        // This is a convenience for when the selection set is small and known at compile-time.
        static int item_current_2 = 0;
        ImGui::Combo("combo", &item_current_2, "aaaa\0bbbb\0cccc\0dddd\0eeee\0\0");
    }

    {
        ImGui::InputTextMultiline("source##truc", &gText, ImVec2(0, ImGui::GetTextLineHeight() * 16));
    }

    ed::EndNode();

    ed::End();
}


int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;
    ImmApp::AddOnsParams addOnsParams;
    runnerParams.callbacks.ShowGui = Gui;
    addOnsParams.withNodeEditor = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}