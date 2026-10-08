// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_rich_md/rich_md.h"
#include "demo_utils/animate_logo.h"
#include "demo_utils/api_demos.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif

void gui_demo_imgui_show_demo_window()
{
    // The logo lands at the top right of the page, beside the title
    AnimateLogo("images/logo_imgui_600.jpg", 2.f, 0.45f, "https://github.com/ocornut/imgui");
    ShowManualIntro("Dear ImGui");

#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImGui, false);
#else
    ImGui::ShowDemoWindow_MaybeDocked(false);
#endif
}
