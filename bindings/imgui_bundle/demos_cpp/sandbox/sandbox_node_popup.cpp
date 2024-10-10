// Test patch proposed ad https://github.com/thedmd/imgui-node-editor/issues/242
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui-node-editor/imgui_node_editor.h"

namespace ed = ax::NodeEditor;

ImVec4 gColor(0.1, 0.2, 0.8, 1);
std::string gText = "Lorem ipsum dolor sit amet, consectetur adipiscing, \n"
                    "sed do eiusmod tempor incididunt \n"
                    "ut labore et dolore magna aliqua. "
                    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. \n"
                    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \n"
                    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

void Gui()
{
    ed::Begin("My Node Editor");

    ed::BeginNode(1);

    ImGui::Text("Node 1");
    ImGui::ColorEdit4("Color", &gColor.x);

    static bool item_highlight = false;
    int item_highlighted_idx = -1; // Here we store our highlighted data as an index.
    ImGui::Checkbox("Check!", &item_highlight);

//    IMGUI_API bool      Combo(const char* label, int* current_item, bool (*old_callback)(void* user_data, int idx, const char** out_text), void* user_data, int items_count, int popup_max_height_in_items = -1);
//    IMGUI_API bool      ListBox(const char* label, int* current_item, bool (*old_callback)(void* user_data, int idx, const char** out_text), void* user_data, int items_count, int height_in_items = -1);

//    IMGUI_API bool          BeginCombo(const char* label, const char* preview_value, ImGuiComboFlags flags = 0);
//    IMGUI_API void          EndCombo(); // only call EndCombo() if BeginCombo() returns true!
//    IMGUI_API bool          Combo(const char* label, int* current_item, const char* const items[], int items_count, int popup_max_height_in_items = -1);
//    IMGUI_API bool          Combo(const char* label, int* current_item, const char* items_separated_by_zeros, int popup_max_height_in_items = -1);      // Separate items with \0 within a string, end item-list with \0\0. e.g. "One\0Two\0Three\0"
//    IMGUI_API bool          Combo(const char* label, int* current_item, const char* (*getter)(void* user_data, int idx), void* user_data, int items_count, int popup_max_height_in_items = -1);

//    // Widgets: List Boxes
//    // - This is essentially a thin wrapper to using BeginChild/EndChild with the ImGuiChildFlags_FrameStyle flag for stylistic changes + displaying a label.
//    // - You can submit contents and manage your selection state however you want it, by creating e.g. Selectable() or any other items.
//    // - The simplified/old ListBox() api are helpers over BeginListBox()/EndListBox() which are kept available for convenience purpose. This is analoguous to how Combos are created.
//    // - Choose frame width:   size.x > 0.0f: custom  /  size.x < 0.0f or -FLT_MIN: right-align   /  size.x = 0.0f (default): use current ItemWidth
//    // - Choose frame height:  size.y > 0.0f: custom  /  size.y < 0.0f or -FLT_MIN: bottom-align  /  size.y = 0.0f (default): arbitrary default height which can fit ~7 items
//    IMGUI_API bool          BeginListBox(const char* label, const ImVec2& size = ImVec2(0, 0)); // open a framed scrolling region
//    IMGUI_API void          EndListBox();                                                       // only call EndListBox() if BeginListBox() returned true!
//    IMGUI_API bool          ListBox(const char* label, int* current_item, const char* const items[], int items_count, int height_in_items = -1);
//    IMGUI_API bool          ListBox(const char* label, int* current_item, const char* (*getter)(void* user_data, int idx), void* user_data, int items_count, int height_in_items = -1);


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
        //ImGui::SetNextItemWidth(200);
        ImGui::InputTextMultiline("source##truc", &gText, ImVec2(0, ImGui::GetTextLineHeight() * 16));
    }

    ImGui::ColorEdit4("Color2", &gColor.x);

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