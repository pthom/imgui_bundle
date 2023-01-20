import os
from imgui_bundle import imgui, hello_imgui, immapp, icons_fontawesome
from imgui_bundle.demos_python import demo_utils


def my_load_fonts_via_hello_imgui() -> imgui.ImFont:
    # hello_imgui can load font and merge them with font awesome automatically.

    # It will load them from the assets/ folder.
    assets_folder = demo_utils.demos_assets_folder()
    hello_imgui.set_assets_folder(assets_folder)

    # First, we load the default fonts (the font that was loaded first is the default font)
    hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()

    # Then we load our custom font
    font_filename = "fonts/Akronim-Regular.ttf"
    acronym_font = hello_imgui.load_font_ttf_with_font_awesome_icons(font_filename, 40.0)
    return acronym_font


def my_load_fonts_manually() -> imgui.ImFont:
    # Load font manually.
    # We need to use font_atlas_add_font_from_file_ttf instead of ImFont.add_font_from_file_ttf

    # first, we load the default font (it will not include icons)
    # Note: on high dpi screen, this font might look very small if you do not take into account
    # the font scaling factor, as shown below.
    # HelloImGui provides hello_imgui::dpi_font_loading_factor() which corresponds to:
    #      `dpi_window_size_factor() * 1.f / imgui.get_io().font_global_scale`
    #          where dpi_window_size_factor() is equal to `current_screen_pixel_per_inch / 96` under windows and linux, 1 under macOS
    default_font_config = imgui.ImFontConfig()
    default_font_config.size_pixels = 14.0 * hello_imgui.dpi_font_loading_factor()
    imgui.get_io().fonts.add_font_default(default_font_config)

    # Load a font and merge icons into it
    # i. load the font...
    this_dir = os.path.dirname(__file__)
    font_atlas = imgui.get_io().fonts
    # We need to take into account the global font scale! This is required for macOS retina screens
    font_size_pixel = 40.0 * hello_imgui.dpi_font_loading_factor()
    font_filename = demo_utils.demos_assets_folder() + "/fonts/Akronim-Regular.ttf"
    glyph_range = imgui.get_io().fonts.get_glyph_ranges_default()
    acronym_font = font_atlas.add_font_from_file_ttf(
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=glyph_range,
    )
    # ii. ... Aad merge icons into the previous font
    from imgui_bundle import icons_fontawesome

    font_filename = demo_utils.demos_assets_folder() + "/fonts/fontawesome-webfont.ttf"
    font_config = imgui.ImFontConfig()
    font_config.merge_mode = True
    icons_range = [icons_fontawesome.ICON_MIN_FA, icons_fontawesome.ICON_MAX_FA, 0]
    acronym_font = font_atlas.add_font_from_file_ttf(
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=icons_range,
        font_cfg=font_config,
    )

    return acronym_font


def main() -> None:
    custom_font: imgui.ImFont

    def gui() -> None:
        imgui.push_font(custom_font)
        imgui.text("Hello " + icons_fontawesome.ICON_FA_SMILE)
        imgui.pop_font()
        imgui.text("Text with standard font")

    def callback_load_font() -> None:
        nonlocal custom_font
        # Choose your own loading method below
        # custom_font = my_load_fonts_manually()
        custom_font = my_load_fonts_via_hello_imgui()

    runner_params = immapp.RunnerParams()
    runner_params.callbacks.load_additional_fonts = callback_load_font
    runner_params.callbacks.show_gui = gui

    immapp.run(runner_params)


if __name__ == "__main__":
    main()
