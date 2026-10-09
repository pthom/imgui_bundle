"""
# Non-Latin text: Chinese, Japanese, Korean, Hebrew, Arabic

The bundled fonts cover Latin, Greek and Cyrillic only: other scripts show up as `???`. The fix: load a font that has
the glyphs you need. This demo shows two ways, with [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC):

* At startup, from your assets, first: it becomes the default font of the whole app (the FontAwesome icons are then
  merged into it).
* After startup: the demo downloads the font (8 MB) when it is not in the assets, loads it, and draws its sample lines
  with it. This works in the browser too.

## Where to get a font

This demo does not ship a CJK font (a full one is about 10 MB). Download one (TTF or OTF):

* [Noto Sans SC (Simplified Chinese)](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
* [Source Han Sans](https://github.com/adobe-fonts/source-han-sans)

The same approach works for Japanese, Korean, Hebrew or Arabic: pick a font that contains those glyphs.

*Tip: CJK fonts have no italic styles. For markdown, merge the regular CJK glyphs into the italic slots too (CJK will
appear upright there).*

*Alternative (zero code): overwrite `assets/fonts/DroidSans.ttf` with your own font, keeping that exact filename. The
default font loader will then pick it up automatically.*
"""

import os
import tempfile
from typing import Optional

from imgui_bundle import hello_imgui, imgui, rich_md, immapp, register_demos_assets_folder, ImVec4

# Make the demos_assets/ folder searchable before we look for the font below.
register_demos_assets_folder()

# Edit this to match the font you downloaded (path relative to an assets folder):
CHINESE_FONT = "fonts/NotoSansSC-Regular.otf"
FONT_FILE_PRESENT = hello_imgui.asset_exists(CHINESE_FONT)
# Where the demo downloads the font when it is not in the assets (a CDN that allows the browser to fetch it)
FONT_URL = "https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@Sans2.004/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf"

download: Optional[immapp.Download] = None  # the font's download, in the background
downloaded_font: Optional[imgui.ImFont] = None  # the font, once downloaded and loaded


def load_fonts() -> None:  # called once by runner_params.callbacks.load_additional_fonts
    if FONT_FILE_PRESENT:
        # Load the CJK font FIRST so it becomes the default font (fonts[0])
        hello_imgui.load_font(CHINESE_FONT, 18.0)
        # Merge FontAwesome icons on top (optional)
        fa = hello_imgui.FontLoadingParams()
        fa.merge_to_last_font = True
        hello_imgui.load_font("fonts/fontawesome-webfont.ttf", 16.0, fa)
    else:  # the default fonts of Hello ImGui (this callback replaces their loading)
        hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()


def sample_lines() -> None:
    imgui.text("    Chinese:  你好，世界")
    imgui.text("    Japanese: こんにちは世界")
    imgui.text("    Korean:   안녕하세요 세계")
    imgui.text_disabled("Each line renders only if the font covers that script")
    imgui.text_disabled("(Noto Sans SC covers Chinese; use e.g. Noto Sans KR for Korean)")


def load_downloaded_font() -> None:
    """Once its download is done: the font goes to a file, then Hello ImGui loads it (fonts can be added at any time)"""
    global download, downloaded_font
    if download is None or not download.done:
        return
    if download.error:
        imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"The download failed: {download.error}")
        return
    path = os.path.join(tempfile.gettempdir(), os.path.basename(CHINESE_FONT))
    with open(path, "wb") as f:
        f.write(download.data)
    params = hello_imgui.FontLoadingParams()
    params.inside_assets = False  # a path anywhere on disk
    downloaded_font = hello_imgui.load_font(path, 18.0, params)
    download = None


def gui() -> None:
    global download
    rich_md.render(__doc__ or "")
    imgui.separator()
    if FONT_FILE_PRESENT:  # the default font of the app
        imgui.text(f"Loaded '{CHINESE_FONT}' at startup. Sample text:")
        sample_lines()
        return

    # Not in the assets: downloaded, then loaded after startup, and used for these lines only
    if downloaded_font is None and download is None:
        download = immapp.start_download(FONT_URL, timeout_s=120.0)
    load_downloaded_font()
    if downloaded_font is None:
        imgui.text("Downloading Noto Sans SC (8 MB)...")
        return
    imgui.text("Downloaded and loaded Noto Sans SC. Sample text:")
    # A quarter bigger than the text around it: a CJK font draws smaller at the same size (its lines are taller)
    imgui.push_font(downloaded_font, imgui.get_style().font_size_base * 1.25)
    sample_lines()
    imgui.pop_font()
    imgui.text_disabled("To make it the default font, place it in one of these folders, then start again:")
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
