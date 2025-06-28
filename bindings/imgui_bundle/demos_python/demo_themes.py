"""Demo for ImGui theming using ImGui Bundle.

In order to apply a theme, you can use:
=======================================
  hello_imgui.apply_theme(hello_imgui.ImGuiTheme_.cherry)

"""
# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import immapp, hello_imgui, imgui, imgui_md


def demo_gui():
    imgui_md.render_unindented(
        """
        # Theming
        HelloImGui adds support for advanced theming to ImGui.

        Select the menu View/Theme/Theme tweak window to explore all the themes and their customization.
        """
    )
    imgui.new_line()
    tweaked_theme = hello_imgui.get_runner_params().imgui_window_params.tweaked_theme
    theme_changed = hello_imgui.show_theme_tweak_gui(tweaked_theme)
    if theme_changed:
        hello_imgui.apply_tweaked_theme(tweaked_theme)

    imgui.show_demo_window()


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)
