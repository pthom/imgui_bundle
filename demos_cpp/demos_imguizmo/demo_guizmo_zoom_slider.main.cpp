// Demo zoom slider with ImGuizmo
// See equivalent python program: demos/litgen/imgui_bundle/bindings/imgui_bundle/demos/demos_imguizmo/demo_guizmo_zoom_slider.py

#include "demos_interface.h"

#include "imgui.h"
#include "imgui_bundle/imgui_bundle.h"
#include "ImGuizmoStl/ImZoomSliderStl.h"


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


// This returns a closure function that will later be invoked to run the app
VoidFunction make_closure_demo_guizmo_zoom_slider()
{
    // Values between 0. and 1. that represent the current viewed portion
    ImVec2 viewMin(0.1f, 0.3f), viewMax(0.6f, 0.8f);
    bool linkZooms = true;

    auto gui = [=]() mutable // mutable => this is a closure
    {
        ImGui::Checkbox("Link zooms", &linkZooms);

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
                    viewMin.x=%.2f viewMax.x=%.2f
                    viewMin.y=%.2f viewMax.y=%.2f

                ...now do whatever you want with those values!
            )", viewMin.x, viewMax.x, viewMin.y, viewMax.y);
             ImGui::Dummy(ImVec2(zoneWidth, 80.f));
            ImGui::EndGroup();
        }

        // Get the zoomable part size (which may have been reserved by ImGui:Dummy)
        ImVec2 zoomZoneMin = ImGui::GetItemRectMin();
        ImVec2 zoomZoneMax = ImGui::GetItemRectMax();

        // And do some drawing depending on the zoom
        DrawZoomableGrid(zoomZoneMin, zoomZoneMax, viewMin, viewMax);

        // Draw the vertical slider
        {
            ImGui::SameLine();
            ImGui::PushID(18);
            bool changed = ImZoomSlider::ImZoomSlider(0.f, 1.f, viewMin.y, viewMax.y, 0.01f, ImZoomSlider::ImGuiZoomSliderFlags_Vertical);

            // Handle link zoom
            if (changed && linkZooms)
            {
                float avg = (viewMin.x + viewMax.x) / 2.f;
                float length = (viewMax.y - viewMin.y);
                viewMin.x = avg - length / 2.f;
                viewMax.x = avg + length / 2.f;
            }
            ImGui::PopID();
        }
        // Draw the horizontal slider
        {
            ImGui::PushID(19);
            bool changed = ImZoomSlider::ImZoomSlider(0.f, 1.f, viewMin.x, viewMax.x);

            // Handle link zoom
            if (changed && linkZooms)
            {
                float avg = (viewMin.y + viewMax.y) / 2.f;
                float length = (viewMax.x - viewMin.x);
                viewMin.y = avg - length / 2.f;
                viewMax.y = avg + length / 2.f;
            }
            ImGui::PopID();
        }
    };
    return gui;
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    auto gui = make_closure_demo_guizmo_zoom_slider();

    HelloImGui::SimpleRunnerParams runnerParams{.guiFunction = gui, .windowSizeAuto=true};
    ImGuiBundle::Run(runnerParams);
}
#endif
