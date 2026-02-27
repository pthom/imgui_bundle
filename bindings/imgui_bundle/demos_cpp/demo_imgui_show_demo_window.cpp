// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/animate_logo.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif

void demo_imgui_show_demo_window()
{
    ImGuiMd::RenderUnindented(R"(
        # Dear ImGui demo
        Browse the demos below, and look at their code in the right panel! You may switch between C++ and Python code with the toggle at the top right of this window.
    )");

    ImGui::NewLine();
    ImGui::Separator();

#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiExplorerGui(ImGuiExplorerLibrary::ImGui, ImGuiExplorerCppOrPython::Cpp, false);
#else
    ImGui::ShowDemoWindow_MaybeDocked(false);
#endif

    AnimateLogo("images/logo_imgui_600.jpg", 2.f, ImVec2(1.f * 0.64f, 4.8f * 0.64f), 0.45f, "https://github.com/ocornut/imgui");
}
