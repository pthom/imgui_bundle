// This sandbox was used to investigate a clipping issue
// when using imgui-node-editor inside a docked window with popups
// See related commit:
// https://github.com/pthom/imgui-node-editor/commit/e9b0fa8641f33c7b71492d68a160c7781d1e377f
// .
#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "imgui.h"
#include "imgui_internal.h"
#include "imgui-node-editor/imgui_node_editor.h"

namespace ed = ax::NodeEditor;

ImVec4 gColor(0.1, 0.2, 0.8, 1);

static void DebugWidgetInfo(const char* label)
{
    ImVec2 min   = ImGui::GetItemRectMin();
    ImVec2 max   = ImGui::GetItemRectMax();
    ImVec2 mouse = ImGui::GetIO().MousePos;
    if (mouse.x > -151.f && mouse.x < -150.f)
        printf("Break\n");
    bool   hover = ImGui::IsItemHovered();

    ImGui::Text("=== %s ===", label);
    ImGui::Text("  Rect: (%.1f, %.1f) – (%.1f, %.1f)", min.x, min.y, max.x, max.y);
    ImGui::Text("  Mouse: (%.1f, %.1f)", mouse.x, mouse.y);
    ImGui::Text("  Hovered: %s", hover ? "YES" : "NO");
}


void Gui()
{
    ed::Begin("My Node Editor");

    ed::BeginNode(1);

    ImGui::BeginVertical("BV");

    ImGui::Dummy(ImVec2(500, 0));

    if (ImGui::Button("TestButton"))
        ImGui::Text("Button clicked!");
    DebugWidgetInfo("TestButton");
    ImGuiWindow* win = ImGui::GetCurrentWindow();
    ImGui::Text("CurrentWindow: %s", win->Name);
    ImGui::Text("ClipRect: (%.1f, %.1f) – (%.1f, %.1f)",
                win->ClipRect.Min.x, win->ClipRect.Min.y,
                win->ClipRect.Max.x, win->ClipRect.Max.y);

    ImGui::SeparatorText("Test DrawList");

    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 p = ImGui::GetCursorScreenPos();
    dl->AddRectFilled(p + ImVec2(-50, -50), p + ImVec2(-20, -20), IM_COL32(255, 0, 0, 200)); // Red rect

    ImGui::Text("My Node Editor");
    ImGui::SetNextItemWidth(200.f);
    ImGui::ColorEdit4("Color", &gColor.x);

    p = ImGui::GetCursorScreenPos();
    dl->AddRectFilled(p + ImVec2(20, 20), p + ImVec2(50, 50), IM_COL32(0, 255, 0, 200)); // Green rect

    ImGui::EndVertical();

    ed::EndNode();

    ed::End();
}


int main(int, char**)
{
    HelloImGui::RunnerParams runnerParams;
    ImmApp::AddOnsParams addOnsParams;

    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;

    // runnerParams.callbacks.ShowGui = Gui;
    HelloImGui::DockableWindow dockwindow("Node Editor Demo");
    dockwindow.GuiFunction = Gui;
    dockwindow.dockSpaceName = "MainDockSpace";
    runnerParams.dockingParams.dockableWindows = {dockwindow};

    runnerParams.imGuiWindowParams.enableViewports = true;
    addOnsParams.withNodeEditor = true;
    addOnsParams.withNodeEditorConfig = ed::Config();
    addOnsParams.withNodeEditorConfig->ForceWindowContentWidthToNodeWidth = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
