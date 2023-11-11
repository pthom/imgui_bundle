# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import immapp, hello_imgui, imgui, imgui_md


ALL_THEMES = [
    hello_imgui.ImGuiTheme_.darcula_darker,
    hello_imgui.ImGuiTheme_.darcula,
    hello_imgui.ImGuiTheme_.imgui_colors_classic,
    hello_imgui.ImGuiTheme_.imgui_colors_dark,
    hello_imgui.ImGuiTheme_.imgui_colors_light,
    hello_imgui.ImGuiTheme_.material_flat,
    hello_imgui.ImGuiTheme_.photoshop_style,
    hello_imgui.ImGuiTheme_.gray_variations,
    hello_imgui.ImGuiTheme_.gray_variations_darker,
    hello_imgui.ImGuiTheme_.microsoft_style,
    hello_imgui.ImGuiTheme_.cherry,
    hello_imgui.ImGuiTheme_.light_rounded,
    hello_imgui.ImGuiTheme_.so_dark_accent_blue,
    hello_imgui.ImGuiTheme_.so_dark_accent_yellow,
    hello_imgui.ImGuiTheme_.so_dark_accent_red,
    hello_imgui.ImGuiTheme_.black_is_black,
    hello_imgui.ImGuiTheme_.white_is_white,
]

ALL_THEMES_NAMES = [theme.name for theme in ALL_THEMES]


@immapp.static(current_theme_idx=0)
def demo_gui():
    static = demo_gui
    imgui_md.render_unindented(
        """
        # Theming
        HelloImGui adds support for advanced theming to ImGui.

        Select the menu View/Theme/Theme tweak window to explore all the themes and their customization.
    """
    )

    imgui.text("Theme")
    changed, static.current_theme_idx = imgui.list_box(
        "##Theme", static.current_theme_idx, ALL_THEMES_NAMES, len(ALL_THEMES_NAMES)
    )
    if changed:
        hello_imgui.apply_theme(ALL_THEMES[static.current_theme_idx])


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)
