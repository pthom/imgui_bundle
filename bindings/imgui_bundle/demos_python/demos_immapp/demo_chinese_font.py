"""
# Displaying non-Latin text (Chinese, Japanese, Korean, Hebrew, Arabic, ...)

The default bundled fonts (DroidSans, Roboto) only contain Latin / Greek / Cyrillic glyphs.
Any CJK / Hebrew / Arabic text therefore shows up as `???`.

> **Solution:** load a font that contains the glyphs you need, and make it the default font.
>
> This demo loads a CJK font *first* (so it becomes the default font), then merges FontAwesome icons.

## Where to get a font

This demo does not ship a CJK font (a full one is ~10 MB). Download one (TTF or OTF):

* [Noto Sans SC (Simplified Chinese)](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
* [Source Han Sans](https://github.com/adobe-fonts/source-han-sans)

The same approach works for Japanese / Korean / Hebrew / Arabic / Cyrillic: just pick a font that contains those glyphs.

*Tip: CJK fonts have no italic styles. For markdown, merge the regular CJK glyphs into the
italic slots too (CJK will appear upright there).*

*Alternative (zero code): overwrite `assets/fonts/DroidSans.ttf` with your own font, keeping that
exact filename. The default font loader will then pick it up automatically.*
"""
from imgui_bundle import hello_imgui, imgui, imgui_md, immapp, register_demos_assets_folder, ImVec4

# Make the demos_assets/ folder searchable before we look for the font below.
register_demos_assets_folder()

# Edit this to match the font you downloaded (path relative to an assets folder):
CHINESE_FONT = "fonts/NotoSansSC-Regular.otf"
FONT_FILE_PRESENT = hello_imgui.asset_exists(CHINESE_FONT)


def load_fonts() -> None:  # called once by runner_params.callbacks.load_additional_fonts
    if FONT_FILE_PRESENT:
        # Load the CJK font FIRST so it becomes the default font (fonts[0])
        hello_imgui.load_font(CHINESE_FONT, 18.0)
        # Merge FontAwesome icons on top (optional)
        fa = hello_imgui.FontLoadingParams()
        fa.merge_to_last_font = True
        hello_imgui.load_font("fonts/fontawesome-webfont.ttf", 16.0, fa)


def gui() -> None:
    imgui_md.render_unindented(__doc__ or "")
    imgui.separator()
    if FONT_FILE_PRESENT:
        imgui.text(f"Loaded '{CHINESE_FONT}'. Sample text:")
        imgui.text("    Chinese:  你好，世界")
        imgui.text("    Japanese: こんにちは世界")
        imgui.text("    Korean:   안녕하세요 세계")
        imgui.text_disabled("Each line renders only if your font covers that script")
        imgui.text_disabled("(Noto Sans SC covers Chinese; use e.g. Noto Sans KR for Korean)")
    else:
        imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"Font not found: {CHINESE_FONT}")
        imgui.text("Place the downloaded font into one of these folders:")
        for path in hello_imgui.get_assets_search_paths():
            imgui.bullet_text(f"{path}")


def main() -> None:
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Chinese / non-Latin fonts demo"
    runner_params.app_window_params.window_geometry.size = (800, 600)
    runner_params.callbacks.load_additional_fonts = load_fonts
    runner_params.callbacks.show_gui = gui
    immapp.run(runner_params, immapp.AddOnsParams(with_markdown=True))


if __name__ == "__main__":
    main()
