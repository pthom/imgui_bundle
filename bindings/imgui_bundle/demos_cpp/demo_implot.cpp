// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#if defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)

#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "immapp/immapp.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif


void demo_implot()
{
    ImGuiMd::RenderUnindented(R"(
        [Implot](https://github.com/epezent/implot) and [Implot3D](https://github.com/brenocq/implot3d) are fast and efficient libraries which provide immediate Mode Plotting.
    )");
    if (ImGui::CollapsingHeader("ImPlot: Full Demo"))
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
        ImGui::PushID("ImPlotDemo");
        ShowImGuiExplorerGui(ImGuiExplorerLibrary::ImPlot);
        ImGui::PopID();
#else
        ImPlot::ShowDemoWindow_MaybeDocked(false);
#endif
    }

    if (ImGui::CollapsingHeader("ImPlot3D: Full Demo"))
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
        ImGui::PushID("ImPlot3DDemo");
        ShowImGuiExplorerGui(ImGuiExplorerLibrary::ImPlot3D);
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
