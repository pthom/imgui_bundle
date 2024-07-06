"""Demonstrates how to load a font with Chinese characters and display them in the GUI,
using the common glyph ranges defined in by ImGui.
"""

from imgui_bundle import imgui, hello_imgui


def load_default_font_with_fa_icon():
    # Note: this font is not provided with the ImGui bundle (too large).
    # You will need to provide it yourself, or use another font.
    font_filename = "NotoSerifSC-VariableFont_wght.ttf"

    # The range of Chinese characters is defined by ImGui as a single list of characters (List[ImWchar]), with a terminating 0.
    # (each range is a pair of successive characters in this list, with the second character being the last one in the range)
    cn_glyph_ranges_imgui = imgui.get_io().fonts.get_glyph_ranges_chinese_simplified_common()
    # We need to convert this list into a list of pairs (List[ImWcharPair]), where each pair is a range of characters.
    cn_glyph_ranges_pair = hello_imgui.translate_common_glyph_ranges(cn_glyph_ranges_imgui)

    font_loading_params = hello_imgui.FontLoadingParams()
    # font_loading_params.inside_assets = False
    font_loading_params.glyph_ranges = cn_glyph_ranges_pair
    hello_imgui.load_font(font_filename, 40.0, font_loading_params)


def gui():
    imgui.text("Hello world")
    imgui.text("你好，世界")


runner_params = hello_imgui.RunnerParams()
runner_params.callbacks.load_additional_fonts = load_default_font_with_fa_icon
runner_params.callbacks.show_gui = gui
hello_imgui.run(runner_params)

