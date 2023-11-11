#include "imgui.h"
#include "immapp/immapp.h"
#include <vector>
#include <string>


enum class DragMode
{
    Copy,
    Move,
    Swap
};


struct DemoState
{
    DragMode Mode = DragMode::Copy;
    std::vector<std::string> Names = {
        "Bobby", "Beatrice", "Betty",
        "Brianna", "Barry", "Bernard",
        "Bibi", "Blaine", "Bryn"
    };
};


void gui_drag_and_drop(DemoState& state)
{
    if (ImGui::RadioButton("Copy", state.Mode == DragMode::Copy))
        state.Mode = DragMode::Copy;
    ImGui::SameLine();
    if (ImGui::RadioButton("Move", state.Mode == DragMode::Move))
        state.Mode = DragMode::Move;
    ImGui::SameLine();
    if (ImGui::RadioButton("Swap", state.Mode == DragMode::Swap))
        state.Mode = DragMode::Swap;

    for (int n = 0; n < state.Names.size(); n++)
    {
        ImGui::PushID(n);
        if ((n % 3) != 0)
            ImGui::SameLine();
        ImGui::Button(state.Names[n].c_str(), ImmApp::EmToVec2(5.f, 5.f));

        // Our buttons are both drag sources and drag targets here!
        if (ImGui::BeginDragDropSource(ImGuiDragDropFlags_None))
        {
            // Set payload to carry the index of our item (could be anything)
            ImGui::SetDragDropPayload("DND_DEMO_CELL", &n, sizeof(int));

            // Display preview (could be anything, e.g. when dragging an image we could decide to display
            // the filename and a small preview of the image, etc.)
            if (state.Mode == DragMode::Copy) { ImGui::Text("Copy %s", state.Names[n].c_str()); }
            if (state.Mode == DragMode::Move) { ImGui::Text("Move %s", state.Names[n].c_str()); }
            if (state.Mode == DragMode::Swap) { ImGui::Text("Swap %s", state.Names[n].c_str()); }
            ImGui::EndDragDropSource();
        }
        if (ImGui::BeginDragDropTarget())
        {
            if (const ImGuiPayload* payload = ImGui::AcceptDragDropPayload("DND_DEMO_CELL"))
            {
                IM_ASSERT(payload->DataSize == sizeof(int));
                int payload_n = *(const int*)payload->Data;
                if (state.Mode == DragMode::Copy)
                {
                    state.Names[n] = state.Names[payload_n];
                }
                if (state.Mode == DragMode::Move)
                {
                    state.Names[n] = state.Names[payload_n];
                    state.Names[payload_n] = "";
                }
                if (state.Mode == DragMode::Swap)
                {
                    std::string tmp = state.Names[n];
                    state.Names[n] = state.Names[payload_n];
                    state.Names[payload_n] = tmp;
                }
            }
            ImGui::EndDragDropTarget();
        }
        ImGui::PopID();
    }

}


int main(int, char**)
{
    DemoState state;
    auto gui = [&state]() { gui_drag_and_drop(state); };
    ImmApp::Run(gui);
}
