import os
import imgui_bundle
from imgui_bundle import imgui, hello_imgui, icons_fontawesome


def my_load_fonts_via_hello_imgui():
    # hello_imgui can load font and merge them with font awesome automatically.
    # It will load them from the assets/ folder.

    # First, we load the default fonts (the font that was loaded first is the default font)
    hello_imgui.ImGuiDefaultSettings.load_default_font_with_font_awesome_icons()
    font_filename = "fonts/Akronim-Regular.ttf"
    acronym_font = hello_imgui.load_font_ttf_with_font_awesome_icons(font_filename, 100.0)
    return acronym_font


def my_load_fonts_manually():
    # Load font manually.
    # We need to use font_atlas_add_font_from_file_ttf instead of ImFont.add_font_from_file_ttf
    global gAkronimFont

    # first, we load the default font (it will not include icons)
    imgui.get_io().fonts.add_font_default()

    # Load a font and merge icons into it
    # i. load the font...
    this_dir = os.path.dirname(__file__)
    font_atlas = imgui.get_io().fonts
    # We need to take into account the global font scale!
    font_size_pixel = 100.0 / imgui.get_io().font_global_scale
    font_filename = this_dir + "/assets/fonts/Akronim-Regular.ttf"
    glyph_range = imgui.font_atlas_glyph_ranges_default(font_atlas)
    acronym_font = imgui.font_atlas_add_font_from_file_ttf(
        font_atlas=imgui.get_io().fonts,
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=glyph_range,
    )
    # ii. ... Aad merge icons into the previous font
    from imgui_bundle import icons_fontawesome

    font_filename = this_dir + "/assets/fonts/fontawesome-webfont.ttf"
    font_config = imgui.ImFontConfig()
    font_config.merge_mode = True
    icons_range = [icons_fontawesome.ICON_MIN_FA, icons_fontawesome.ICON_MAX_FA, 0]
    acronym_font = imgui.font_atlas_add_font_from_file_ttf(
        font_atlas,
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=icons_range,
        font_cfg=font_config,
    )

    return acronym_font


def main():
    custom_font: imgui.ImFont

    def gui():
        imgui.push_font(custom_font)
        imgui.text("Hello " + icons_fontawesome.ICON_FA_SMILE)
        imgui.pop_font()

    def callback_load_font():
        nonlocal custom_font
        # Choose your own loading method below
        custom_font = my_load_fonts_manually()
        # custom_font = my_load_fonts_via_hello_imgui()

    runner_params = imgui_bundle.RunnerParams()
    runner_params.callbacks.load_additional_fonts = callback_load_font
    runner_params.callbacks.show_gui = gui

    imgui_bundle.run(runner_params)


if __name__ == "__main__":
    main()
