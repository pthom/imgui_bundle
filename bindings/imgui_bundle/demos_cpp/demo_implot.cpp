// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#if defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)

#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "immapp/immapp.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB
#include "imgui_manual.h"
#endif


void demo_implot()
{
    ImGuiMd::RenderUnindented(R"(
        # ImPlot & ImPlot3D &nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;[Online Demo](https://traineq.org/implot_demo/src/implot_demo.html)
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.
    )");
    if (ImGui::CollapsingHeader("ImPlot: Full Demo"))
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB
        ImGui::PushID("ImPlotDemo");
        ShowImGuiManualGui(ImGuiManualLibrary::ImPlot);
        ImGui::PopID();
#else
        ImPlot::ShowDemoWindow_MaybeDocked(false);
#endif
    }

    if (ImGui::CollapsingHeader("ImPlot3D: Full Demo"))
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB
        ImGui::PushID("ImPlot3DDemo");
        ShowImGuiManualGui(ImGuiManualLibrary::ImPlot3D);
        ImGui::PopID();
#else
        ImPlot3D::ShowAllDemos();
#endif
    }
}

#else // defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)
#include "imgui.h"
void demo_implot() { ImGui::Text("Dear ImGui Bundle was compiled without support for both ImPlot and ImPlot3D"); }
#endif
