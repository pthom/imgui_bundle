// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include <vector>


const std::vector<ImGuiTheme::ImGuiTheme_> ALL_THEMES = {
    ImGuiTheme::ImGuiTheme_ImGuiColorsClassic,
    ImGuiTheme::ImGuiTheme_ImGuiColorsDark,
    ImGuiTheme::ImGuiTheme_ImGuiColorsLight,
    ImGuiTheme::ImGuiTheme_MaterialFlat,
    ImGuiTheme::ImGuiTheme_PhotoshopStyle,
    ImGuiTheme::ImGuiTheme_GrayVariations,
    ImGuiTheme::ImGuiTheme_GrayVariations_Darker,
    ImGuiTheme::ImGuiTheme_MicrosoftStyle,
    ImGuiTheme::ImGuiTheme_Cherry,
    ImGuiTheme::ImGuiTheme_Darcula,
    ImGuiTheme::ImGuiTheme_DarculaDarker,
    ImGuiTheme::ImGuiTheme_LightRounded,
    ImGuiTheme::ImGuiTheme_SoDark_AccentBlue,
    ImGuiTheme::ImGuiTheme_SoDark_AccentYellow,
    ImGuiTheme::ImGuiTheme_SoDark_AccentRed,
    ImGuiTheme::ImGuiTheme_BlackIsBlack,
    ImGuiTheme::ImGuiTheme_WhiteIsWhite,
};

const std::vector<std::string> ALL_THEMES_NAMES = {
    "ImGuiColorsClassic",
    "ImGuiColorsDark",
    "ImGuiColorsLight",
    "MaterialFlat",
    "PhotoshopStyle",
    "GrayVariations",
    "GrayVariations_Darker",
    "MicrosoftStyle",
    "Cherry",
    "Darcula",
    "DarculaDarker",
    "LightRounded",
    "SoDark_AccentBlue",
    "SoDark_AccentYellow",
    "SoDark_AccentRed",
    "BlackIsBlack",
    "WhiteIsWhite"
};


void demo_themes()
{
    static int current_theme_idx = 0;
    ImGuiMd::RenderUnindented(R"(
        # Theming
        HelloImGui adds support for advanced theming to ImGui.

        Select the menu View/Theme/Theme tweak window to explore all the themes and their customization.
    )");

    ImGui::Text("Theme");

    std::vector<const char*> all_themes_names_antic;
    for (const auto &v: ALL_THEMES_NAMES)
        all_themes_names_antic.push_back(v.c_str());

    bool changed = ImGui::ListBox(
        "##Theme", &current_theme_idx, all_themes_names_antic.data(), all_themes_names_antic.size(), all_themes_names_antic.size());
    if (changed)
        ImGuiTheme::ApplyTheme(ALL_THEMES[current_theme_idx]);
}
