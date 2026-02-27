// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_manual.h"
#endif

void demo_im_anim()
{
    ImGuiMd::RenderUnindented(R"(
        # ImAnim
        ImAnim is an Animation Engine for Dear ImGui. Browse the demos below, and look at their code in the right panel! You may switch between C++ and Python code with the toggle at the top right of this window.
    )");

    ImGui::NewLine();
    ImGui::Separator();

#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
    ShowImGuiManualGui(ImGuiManualLibrary::ImAnim, ImGuiManualCppOrPython::Cpp, false);
#else
    ImGui::Text("Demo unavailable, because Dear ImGui Manual library is not included in this build.");
#endif
}
