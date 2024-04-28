#include "imgui.h"
#include "imgui_internal.h"
#include <unordered_map>
#include <functional>

using VoidFunction = std::function<void()>;

static std::unordered_map<ImGuiID, bool> gResizingState;

static bool _isResizing(ImGuiID widget_id)
{
    if (gResizingState.find(widget_id) == gResizingState.end())
        gResizingState[widget_id] = false;
    return gResizingState.at(widget_id);
}

static void _setResizing(ImGuiID widget_id, bool value) { gResizingState[widget_id] = value; }

ImVec2 WidgetWithResizeHandle(VoidFunction widget_function, float handle_size_em = 1.0f)
{
    widget_function();
    ImVec2 widget_size = ImGui::GetItemRectSize();
    ImGuiID widget_id = ImGui::GetItemID();

    float em = ImGui::GetFontSize(), size = em * handle_size_em;
    ImVec2 widget_bottom_right = ImGui::GetItemRectMax();

    ImVec2 br(widget_bottom_right), bl(br.x - size, br.y), tr(br.x, br.y - size), tl(br.x - size, br.y - size);
    ImRect zone(tl, br);

    ImU32 color = ImGui::GetColorU32(ImGuiCol_Button);
    if (ImGui::IsMouseHoveringRect(zone.Min, zone.Max))
        color = ImGui::GetColorU32(ImGuiCol_ButtonHovered);
    if (_isResizing(widget_id))
        color = ImGui::GetColorU32(ImGuiCol_ButtonActive);

    ImGui::GetWindowDrawList()->AddTriangleFilled(br, bl, tr, color);

    if (!_isResizing(widget_id))
    {
        if (ImGui::IsMouseHoveringRect(zone.Min, zone.Max) && ImGui::IsMouseDown(0))
        {
            ImGui::SetMouseCursor(ImGuiMouseCursor_ResizeNWSE);
            _setResizing(widget_id, true);
        }
    }
    if (_isResizing(widget_id))
    {
        if (ImGui::IsMouseDown(0))
        {
            ImVec2 mouse_delta = ImGui::GetMouseDragDelta(0);
            if (mouse_delta.x != 0.0f || mouse_delta.y != 0.0f)
            {
                widget_size.x += mouse_delta.x;
                widget_size.y += mouse_delta.y;
                ImGui::ResetMouseDragDelta(0);
            }
        }
        else
        {
            ImGui::SetMouseCursor(ImGuiMouseCursor_Arrow);
            _setResizing(widget_id, false);
        }
    }

    return widget_size;
}


// --------------  Example usage with ImGui Bundle --------------

#include "implot/implot.h"
#include "immapp/runner.h"


void gui()
{
    static ImVec2 widget_size(200, 200);

    auto myWidgetFunction = []()
    {
        if (ImPlot::BeginPlot("My Plot", widget_size)) {
            static std::vector<float> x(1000), y(1000);
            for (int i = 0; i < 1000; ++i) {
                x[i] = i * 0.01f;
                y[i] = std::sin(x[i]);
            }
            ImPlot::PlotLine("My Line", x.data(), y.data(), 1000);
            ImPlot::EndPlot();
        }
    };

    widget_size = WidgetWithResizeHandle(myWidgetFunction);
}

int main(int, char**) {
    HelloImGui::RunnerParams runner_params; runner_params.callbacks.ShowGui = gui;
    ImmApp::AddOnsParams addons_params; addons_params.withImplot = true;
    ImmApp::Run(runner_params, addons_params);
}
