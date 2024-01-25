#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
// Demo zoom slider with ImGuizmo
// See equivalent python program: demos/litgen/imgui_bundle/bindings/imgui_bundle/demos/demos_imguizmo/demo_guizmo_zoom_slider.py

// ###############################################################################
// # Warning! This component does not render well on high DPI
// # (especially under windows) => this demo is hidden by default
// ###############################################################################
#define IMGUI_DEFINE_MATH_OPERATORS

#include "demo_utils/api_demos.h"

#include "immapp/immapp.h"
#include "imgui_internal.h"
#include "ImGuizmoPure/ImZoomSliderPure.h"


std::vector<float> range_float(float min, float max, float dx)
{
    std::vector<float> r;
    float v = min;
    while (v < max)
    {
        r.push_back(v);
        v += dx;
    }
    return r;
}


// The zoomable grid on the background
void DrawZoomableGrid(
    ImVec2 rectMin, ImVec2 rectMax, // Those are pixels
    ImVec2 viewMin, ImVec2 viewMax  // Those are values between 0 and 1
    )
{
    auto to_x_window_coord = [&](float x) {
        float kx = (x - viewMin.x) / (viewMax.x - viewMin.x);
        return ImLerp(rectMin.x, rectMax.x, kx);
    };
    auto to_y_window_coord = [&](float y) {
        float ky = (y - viewMin.y) / (viewMax.y - viewMin.y);
        return ImLerp(rectMin.y, rectMax.y, ky);
    };

    auto color = ImGui::GetColorU32(ImVec4(1.f, 1.f, 1.f, 0.2f));
    for (float x: range_float(0.f, 1.f, 0.05))
    {
        float x_win = to_x_window_coord(x);
        if ((x_win >= rectMin.x) && (x_win < rectMax.x))
            ImGui::GetForegroundDrawList()->AddLine(
                ImVec2(x_win, rectMin.y),
                ImVec2(x_win, rectMax.y),
                color);
    }
    for (float y: range_float(0.f, 1.f, 0.05))
    {
        float y_win = to_y_window_coord(y);
        if ((y_win >= rectMin.y) && (y_win < rectMax.y))
            ImGui::GetForegroundDrawList()->AddLine(ImVec2(rectMin.x, y_win), ImVec2(rectMax.x, y_win), color);
    }
}


void demo_guizmo_zoom_slider()
{
    // Values between 0. and 1. that represent the current viewed portion
    static ImZoomSlider::Range viewHorizontal{0.1f, 0.6f}, viewVertical{0.3f, 0.8f};
    static bool linkZooms = true;

    ImGui::Checkbox("Link zooms", &linkZooms);

    ImGui::BeginChild("SliderChild", ImVec2(400.f, 400.f));

    // Draw anything in the zoomable part,
    // or reserve some space (for example with ImGui::Dummy)
    {
        float zoneWidth = 380.f;
        ImGui::BeginGroup();
        // If needed, just use ImGui::Dummy to reserve some space
        ImGui::Dummy(ImVec2(zoneWidth, 80.f));
        ImGui::Text(R"(
            You are looking at a zoomable part:
            use the mouse wheel on the sliders,
            or drag their extremities.

            Current zoom values:
                viewHorizontal.Min=%.2f viewHorizontal.Max=%.2f
                viewVertical.Min=%.2f viewVertical.Max=%.2f

            ...now do whatever you want with those values!
        )",
                    viewHorizontal.Min, viewHorizontal.Max,
                    viewVertical.Min, viewVertical.Max);
         ImGui::Dummy(ImVec2(zoneWidth, 80.f));
        ImGui::EndGroup();
    }

    // Get the zoomable part size (which may have been reserved by ImGui:Dummy)
    ImVec2 zoomZoneMin = ImGui::GetItemRectMin();
    ImVec2 zoomZoneMax = ImGui::GetItemRectMax();

    // And do some drawing depending on the zoom
    DrawZoomableGrid(zoomZoneMin, zoomZoneMax, {viewHorizontal.Min, viewVertical.Min}, {viewHorizontal.Max, viewVertical.Max});

    // Draw the vertical slider
    {
        ImGui::SameLine();
        ImGui::PushID(18);
        auto sliderResult = ImZoomSlider::ImZoomSliderPure(
            {0.f, 1.f}, {viewVertical.Min, viewVertical.Max}, 0.1f, ImZoomSlider::ImGuiZoomSliderFlags_Vertical);
        if (sliderResult)
            viewVertical = sliderResult.Value;

        // Handle link zoom
        if (sliderResult && linkZooms)
        {
            float avgH = viewHorizontal.Center();
            float lengthV = viewVertical.Length();
            viewHorizontal = {avgH - lengthV / 2.f, avgH + lengthV / 2.f };
        }
        ImGui::PopID();
    }
    // Draw the horizontal slider
    {
        ImGui::PushID(19);
        auto sliderResult = ImZoomSlider::ImZoomSliderPure({0.f, 1.f}, viewHorizontal, 0.1f);
        if (sliderResult)
            viewHorizontal = sliderResult.Value;

        // Handle link zoom
        if (sliderResult && linkZooms)
        {
            float avgV = viewVertical.Center();
            float lengthH = viewHorizontal.Length();
            viewVertical = {avgV - lengthH / 2.f, avgV + lengthH / 2.f };
        }
        ImGui::PopID();
    }

    ImGui::EndChild();
}

#else // IMGUI_BUNDLE_WITH_IMGUIZMO
#include "imgui.h"
void demo_guizmo_zoom_slider() { ImGui::Text("Dear ImGui Bundle was compiled without support for ImGuizmo"); }
#endif // IMGUI_BUNDLE_WITH_IMGUIZMO
