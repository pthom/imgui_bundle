// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif

void gui_demo_imgui_show_demo_window()
{
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImGui, false);
#else
    ImGui::ShowDemoWindow_MaybeDocked(false);
#endif
}
