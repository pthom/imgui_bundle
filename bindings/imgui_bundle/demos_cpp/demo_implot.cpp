// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#if defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)

#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "immapp/immapp.h"
#include "immapp/browse_to_url.h"


void demo_implot()
{
    ImGuiMd::RenderUnindented(R"(
        # ImPlot & ImPlot3D &nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;[Online Demo](https://traineq.org/implot_demo/src/implot_demo.html)
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.
    )");
    if (ImGui::CollapsingHeader("ImPlot: Full Demo"))
    {
        ImGui::Text("View on GitHub:");
        ImGui::SameLine();
        if (ImGui::Button("C++ demo code"))
            ImmApp::BrowseToUrl("https://github.com/epezent/implot/blob/master/implot_demo.cpp");
        ImGui::SameLine();
        if (ImGui::Button("Python demo code"))
            ImmApp::BrowseToUrl("https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot/implot_demo.py");
        ImPlot::ShowAllDemos();
    }

    if (ImGui::CollapsingHeader("ImPlot3D: Full Demo"))
    {
        ImGui::Text("View on GitHub:");
        ImGui::SameLine();
        if (ImGui::Button("C++ demo code"))
            ImmApp::BrowseToUrl("https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp");
        ImGui::SameLine();
        if (ImGui::Button("Python demo code"))
            ImmApp::BrowseToUrl("https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot3d/implot3d_demo.py");
        ImPlot3D::ShowAllDemos();
    }
}

#else // defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)
#include "imgui.h"
void demo_implot() { ImGui::Text("Dear ImGui Bundle was compiled without support for both ImPlot and ImPlot3D"); }
#endif
