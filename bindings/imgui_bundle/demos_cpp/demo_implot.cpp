// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#if defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)

#include "implot/implot.h"
#include "implot3d/implot3d.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif


// The ImPlot manual alone, and the ImPlot3D manual alone (the explorer's "interactive manuals", as in Python)
void manual_implot()
{
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImPlot);
#else
    ImPlot::ShowDemoWindow_MaybeDocked(false);
#endif
}

void manual_implot3d()
{
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImPlot3D);
#else
    ImPlot3D::ShowAllDemos();
#endif
}

#else // defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMPLOT3D)
#include "imgui.h"
void manual_implot() { ImGui::Text("Dear ImGui Bundle was compiled without support for both ImPlot and ImPlot3D"); }
void manual_implot3d() { manual_implot(); }
#endif
