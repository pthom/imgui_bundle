#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui.h"
#include "imgui_internal.h"
#include <unordered_map>
#include <functional>

#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"
namespace ed = ax::NodeEditor;


using VoidFunction = std::function<void()>;

struct WidgetResizingState_
{
    bool   Resizing = false;
    bool   MouseInResizingZone = false;
    bool   MouseDown = false;
    ImVec2 MousePosition = ImVec2();
};

static std::unordered_map<ImGuiID, WidgetResizingState_> gWidgetResizingStates;

static WidgetResizingState_* GetWidgetResizingState_(ImGuiID widget_id)
{
    if (gWidgetResizingStates.find(widget_id) == gWidgetResizingStates.end())
        gWidgetResizingStates[widget_id] = WidgetResizingState_();
    return &gWidgetResizingStates.at(widget_id);
}


ImVec2 WidgetWithResizeHandle(VoidFunction widget_function, float handle_size_em = 1.0f)
{
    widget_function();

    ax::NodeEditor::Detail::EditorContext *nodeContext = (ax::NodeEditor::Detail::EditorContext *)ed::GetCurrentEditor();

    if (ImGui::IsMouseHoveringRect(ImGui::GetItemRectMin(), ImGui::GetItemRectMax()))
        nodeContext->DisableUserInputThisFrame();


    ImVec2 widget_size = ImGui::GetItemRectSize();
    ImGuiID widget_id = ImGui::GetItemID();

   float em = ImGui::GetFontSize(), size = em * handle_size_em;
    ImVec2 widget_bottom_right = ImGui::GetItemRectMax();

    ImVec2 br(widget_bottom_right), bl(br.x - size, br.y), tr(br.x, br.y - size), tl(br.x - size, br.y - size);
    ImRect zone = ImRect(tl, br);

    //
    // Get and update resizing state
    //
    WidgetResizingState_* resizingState = GetWidgetResizingState_(widget_id);
    WidgetResizingState_ previousResizingState = *resizingState; // This is a copy

    resizingState->MousePosition = ImGui::GetIO().MousePos;
    resizingState->MouseInResizingZone = ImGui::IsMouseHoveringRect(zone.Min, zone.Max);
    resizingState->MouseDown = ImGui::IsMouseDown(0);

    ImVec2 mouseDelta = resizingState->MousePosition - previousResizingState.MousePosition;

    // Color
    ImU32 color = ImGui::GetColorU32(ImGuiCol_Button);
    if (ImGui::IsMouseHoveringRect(zone.Min, zone.Max))
        color = ImGui::GetColorU32(ImGuiCol_ButtonHovered);
    if (resizingState->Resizing)
        color = ImGui::GetColorU32(ImGuiCol_ButtonActive);

    ImGui::GetWindowDrawList()->AddTriangleFilled(br, bl, tr, color);

    if (!resizingState->Resizing)
    {
        bool wasMouseJustClicked = !previousResizingState.MouseDown && resizingState->MouseDown;
        bool mouseInZoneBeforeAfter = previousResizingState.MouseInResizingZone && resizingState->MouseInResizingZone;
        if (wasMouseJustClicked && mouseInZoneBeforeAfter)
        {
            nodeContext->DisableUserInputThisFrame();
            ImGui::SetMouseCursor(ImGuiMouseCursor_ResizeNWSE);
            resizingState->Resizing = true;
        }
    }
    if (resizingState->Resizing)
    {
        nodeContext->DisableUserInputThisFrame();
        if (ImGui::IsMouseDown(0))
        {
            if (mouseDelta.x != 0.0f || mouseDelta.y != 0.0f)
            {
                widget_size.x += mouseDelta.x;
                widget_size.y += mouseDelta.y;
                ImGui::ResetMouseDragDelta(0);
            }
        }
        else
        {
            ImGui::SetMouseCursor(ImGuiMouseCursor_Arrow);
            resizingState->Resizing = false;
        }
    }

    return widget_size;
}


// --------------  Example usage with ImGui Bundle --------------

#include "implot/implot.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "immapp/runner.h"

namespace ed = ax::NodeEditor;

void gui()
{
    static ImVec2 widget_size(200, 200);
    static double xPos = 5.f;

    auto myWidgetFunction = []()
    {
        if (ImPlot::BeginPlot("My Plot", widget_size)) {
            static std::vector<float> x(1000), y(1000);
            for (int i = 0; i < 1000; ++i) {
                x[i] = i * 0.01f;
                y[i] = std::sin(x[i]);
            }
            ImPlot::PlotLine("My Line", x.data(), y.data(), 1000);
            ImPlot::DragLineX(0, &xPos, ImVec4(1, 1, 0, 1));
            ImPlot::EndPlot();
        }
    };

    ed::Begin("My Node Editor");
    ed::BeginNode(ed::NodeId(1));
    ImGui::Text("Hello");
    ImGui::Text("World");
    widget_size = WidgetWithResizeHandle(myWidgetFunction);
    ed::EndNode();
    ed::End();
}

int main(int, char**) {
    HelloImGui::RunnerParams runner_params; runner_params.callbacks.ShowGui = gui;
    ImmApp::AddOnsParams addons_params; addons_params.withImplot = true; addons_params.withNodeEditor = true;
    ImmApp::Run(runner_params, addons_params);
}
