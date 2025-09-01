// Demo for ImGui theming using ImGui Bundle.
//
// In order to apply a theme, you can use:
// =======================================

//     ImGuiTheme::ApplyTheme(ImGuiTheme::ImGuiTheme_Cherry)

// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"


void demo_themes()
{
    static int current_theme_idx = 0;
    ImGuiMd::RenderUnindented(R"(
        # Theming
        HelloImGui adds support for advanced theming to ImGui.

        Select the menu View/Theme/Theme tweak window to explore all the themes and their customization.
    )");
    ImGui::NewLine();
    auto & tweakedTheme = HelloImGui::GetRunnerParams()->imGuiWindowParams.tweakedTheme;
    bool themeChanged = ImGuiTheme::ShowThemeTweakGui(&tweakedTheme);
    if (themeChanged)
        ImGuiTheme::ApplyTweakedTheme(tweakedTheme);

    ImGui::ShowDemoWindow();
}
