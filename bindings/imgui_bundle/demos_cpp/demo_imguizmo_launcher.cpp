// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"

void demo_guizmo_curve_edit();


void demo_imguizmo_launcher()
{
    ImGuiMd::RenderUnindented(R"(
        # ImGuizmo
        [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) provides an immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui

        What started with the gizmo is now a collection of dear imgui widgets and more advanced controls.

        Open the demos below by clicking on their title.
    )");

    if (ImGui::CollapsingHeader("Gizmo"))
    {
        ImGui::Text(
            "Click the button below to launch the demo (below the button is a screenshot of the app that will be launched)"
        );
        if (ImGui::Button("Run gizmo demo"))
            SpawnDemo("demo_gizmo");
        HelloImGui::ImageFromAsset("images/gizmo_screenshot.jpg", ImVec2(0, HelloImGui::EmSize(15.0f)));
        ShowPythonVsCppFile("demos_imguizmo/demo_gizmo", 30);
    }
    if (ImGui::CollapsingHeader("Curve Edit"))
    {
        demo_guizmo_curve_edit();
        ShowPythonVsCppFile("demos_imguizmo/demo_guizmo_curve_edit", 30);
    }
    //if (ImGui::CollapsingHeader("Zoom Slider")) // Disabled, because of missing high DPI support
    //{
    //    ImGui::Text("Click the button below to launch the demo");
    //    if (ImGui::Button("Run demo"))
    //    {
    //        SpawnDemo("demo_guizmo_zoom_slider");
    //    }
    //    ShowPythonVsCppFile("demos_imguizmo/demo_guizmo_zoom_slider", 30);
    //}


}
