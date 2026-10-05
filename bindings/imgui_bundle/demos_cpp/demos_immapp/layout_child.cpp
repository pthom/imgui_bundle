// Resizable layouts with BeginChild: child windows with ImGuiChildFlags_ResizeX / ResizeY have draggable borders.
// See the Python version (layout_child.py) for the full explanation.
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include <string>
#include <vector>

// All the demos of this folder are also compiled together (in the explorer): their own names stay in this file
namespace
{

// Sample content for each panel
void SidebarContent()
{
    ImGui::Text("Sidebar");
    ImGui::Separator();
    const std::vector<std::string> items = {"Home", "Dashboard", "Settings", "Users", "Reports", "Help"};
    for (size_t i = 0; i < items.size(); ++i)
        ImGui::Selectable(items[i].c_str(), i == 0);  // Selectable: a clickable text item
}

void MainContent()
{
    ImGui::Text("Main Area");
    ImGui::Separator();
    ImGui::TextWrapped("This is the main content area. It fills the remaining space after the sidebar. "
                       "Drag the left border to resize the sidebar.");
    ImGui::Spacing();
    // Some sample widgets
    ImGui::Button("Action 1");
    ImGui::SameLine();
    ImGui::Button("Action 2");
    ImGui::SameLine();
    ImGui::Button("Action 3");
    ImGui::Spacing();
    // A simple table
    if (ImGui::BeginTable("##data", 3, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg))
    {
        ImGui::TableSetupColumn("Name");
        ImGui::TableSetupColumn("Value");
        ImGui::TableSetupColumn("Status");
        ImGui::TableHeadersRow();
        for (int row = 0; row < 5; ++row)
        {
            ImGui::TableNextRow();
            ImGui::TableNextColumn();
            ImGui::Text("Item %d", row + 1);
            ImGui::TableNextColumn();
            ImGui::Text("%d", (row + 1) * 42);
            ImGui::TableNextColumn();
            bool ok = row % 3 != 2;
            ImVec4 color = ok ? ImVec4(0.3f, 0.8f, 0.3f, 1.f) : ImVec4(0.8f, 0.3f, 0.3f, 1.f);
            ImGui::TextColored(color, "%s", ok ? "OK" : "Error");
        }
        ImGui::EndTable();
    }
}

void BottomContent()
{
    ImGui::Text("Bottom Panel");
    ImGui::Separator();
    ImGui::TextDisabled("Drag the top border to resize this panel.");
    // Simulate a log output
    const char* levels[] = {"INFO", "DEBUG", "WARN"};
    for (int i = 0; i < 8; ++i)
        ImGui::TextDisabled("[%s] Log message %d...", levels[i % 3], i + 1);
}

}  // namespace

void gui_layout_child()
{
    RichMd::Render(R"(# Resizable Layouts with BeginChild
`BeginChild` creates scrollable, nestable sub-regions. With `ImGuiChildFlags_ResizeX` or `ResizeY`, the user can
**drag dividers** to resize panels. This demo builds a classic app layout with them: a sidebar, a main area, and a
bottom panel.
)");
    ImGui::Separator();
    float em = ImGui::GetFontSize();

    // Top row: sidebar + main, its bottom border draggable (ResizeY); the bottom panel fills what is left below.
    // The top row starts at 65% of the available height.
    ImVec2 avail = ImGui::GetContentRegionAvail();
    ImGui::BeginChild("##top_row", ImVec2(0, avail.y * 0.65f), ImGuiChildFlags_ResizeY);

    // Sidebar (resizable width)
    ImGui::BeginChild("##sidebar", ImVec2(em * 10, 0), ImGuiChildFlags_Borders | ImGuiChildFlags_ResizeX);
    SidebarContent();
    ImGui::EndChild();

    // Main area (fills the remaining width)
    ImGui::SameLine();
    ImGui::BeginChild("##main", ImVec2(0, 0), ImGuiChildFlags_Borders);
    MainContent();
    ImGui::EndChild();

    ImGui::EndChild();  // top_row

    // Bottom panel (fills the remaining space)
    ImGui::BeginChild("##bottom", ImVec2(0, 0), ImGuiChildFlags_Borders);
    BottomContent();
    ImGui::EndChild();
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = gui_layout_child;
    params.windowTitle = "Resizable Layouts";
    params.windowSize = {1000, 700};
    params.iniDisable = true;
    ImmApp::AddOnsParams addOns;
    addOns.withMarkdown = true;
    ImmApp::Run(params, addOns);
    return 0;
}
#endif
