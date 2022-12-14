from imgui_bundle import immapp, hello_imgui, imgui
from imgui_bundle.demos import demo_utils


def make_gui():

    def gui():
        demo_utils.render_md_unindented("""
        HelloImGui adds support for advanced theming to ImGui.
        
        Select the menu View/Theme/Theme tweak window to explore all the themes and their customization.
        """)

        themes = [
            hello_imgui.ImGuiTheme_.imgui_colors_classic,
            hello_imgui.ImGuiTheme_.imgui_colors_dark,
            hello_imgui.ImGuiTheme_.imgui_colors_light,
            hello_imgui.ImGuiTheme_.material_flat,
            hello_imgui.ImGuiTheme_.photoshop_style,
            hello_imgui.ImGuiTheme_.gray_variations,
            hello_imgui.ImGuiTheme_.gray_variations_darker,
            hello_imgui.ImGuiTheme_.microsoft_style,
            hello_imgui.ImGuiTheme_.cherry,
            hello_imgui.ImGuiTheme_.darcula,
            hello_imgui.ImGuiTheme_.darcula_darker,
            hello_imgui.ImGuiTheme_.light_rounded,
            hello_imgui.ImGuiTheme_.so_dark_accent_blue,
            hello_imgui.ImGuiTheme_.so_dark_accent_yellow,
            hello_imgui.ImGuiTheme_.so_dark_accent_red,
            hello_imgui.ImGuiTheme_.black_is_black,
            hello_imgui.ImGuiTheme_.white_is_white
        ]
        for theme in themes:
            if imgui.button(theme.name):
                hello_imgui.apply_theme(theme)
    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()


if __name__ == "__main__":
    immapp.run(demo_launch, window_size=(1000, 800), with_markdown=True)
