// Demo: displaying non-Latin text (Chinese, Japanese, Korean, Hebrew, Arabic, ...)
//
// The explanation is rendered in-app as markdown (with clickable download links).
// In short: load a font that contains the glyphs you need, make it the default font,
// and let the on-demand glyph rasterization (ImGui 1.92) do the rest.

#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_utils/api_demos.h"
#include "imgui.h"
#include <string>

// Poor man's fix for C++ late arrival in the unicode party:
//    - C++17: u8"my string" is of type const char*
//    - C++20: u8"my string" is of type const char8_t*
// However, ImGui text functions expect const char*.
#ifdef __cpp_char8_t
#define U8_TO_CHAR(x) reinterpret_cast<const char*>(x)
#else
#define U8_TO_CHAR(x) x
#endif

// Edit this to match the font you downloaded (path relative to an assets folder):
static const std::string CHINESE_FONT = "fonts/NotoSansSC-Regular.otf";

// Documentation shown in the app, as markdown (the download links are clickable).
static const std::string DOC = R"(
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

The same approach works for Japanese / Korean / Hebrew / Arabic / Cyrillic: just pick a font
that contains those glyphs.

*Tip: CJK fonts have no italic styles. For markdown, merge the regular CJK glyphs into the
italic slots too (CJK will appear upright there).*

*Alternative (zero code): overwrite `assets/fonts/DroidSans.ttf` with your own font, keeping that
exact filename. The default font loader will then pick it up automatically.*
)";


// Called once by runnerParams.callbacks.LoadAdditionalFonts
void LoadFonts(bool fontFilePresent)
{
    if (fontFilePresent)
    {
        // Load the CJK font FIRST so it becomes the default font (fonts[0])
        HelloImGui::LoadFont(CHINESE_FONT, 18.f);
        // Merge FontAwesome icons on top (optional)
        HelloImGui::FontLoadingParams fa;
        fa.mergeToLastFont = true;
        HelloImGui::LoadFont("fonts/fontawesome-webfont.ttf", 16.f, fa);
    }
}


void Gui(bool fontFilePresent)
{
    ImGuiMd::RenderUnindented(DOC);
    ImGui::Separator();
    if (fontFilePresent)
    {
        ImGui::Text("Loaded '%s'. Sample text:", CHINESE_FONT.c_str());
        ImGui::TextUnformatted(U8_TO_CHAR(u8"    Chinese:  你好，世界"));
        ImGui::TextUnformatted(U8_TO_CHAR(u8"    Japanese: こんにちは世界"));
        ImGui::TextUnformatted(U8_TO_CHAR(u8"    Korean:   안녕하세요 세계"));
        ImGui::TextDisabled("Each line renders only if your font covers that script");
        ImGui::TextDisabled("(Noto Sans SC covers Chinese; use e.g. Noto Sans KR for Korean)");
    }
    else
    {
        ImGui::TextColored(ImVec4(1.f, 0.4f, 0.4f, 1.f), "Font not found: %s", CHINESE_FONT.c_str());
        ImGui::TextUnformatted("Place the downloaded font into one of these folders:");
        for (const std::string& path : HelloImGui::GetAssetsSearchPaths())
            ImGui::BulletText("%s", path.c_str());
    }
}


int main(int, char**)
{
    ChdirBesideAssetsFolder();  // makes the demos_assets/ folder searchable
    bool fontFilePresent = HelloImGui::AssetExists(CHINESE_FONT);

    HelloImGui::RunnerParams runnerParams;
    runnerParams.appWindowParams.windowTitle = "Chinese / non-Latin fonts demo";
    runnerParams.appWindowParams.windowGeometry.size = {800, 600};
    runnerParams.callbacks.LoadAdditionalFonts = [fontFilePresent]() { LoadFonts(fontFilePresent); };
    runnerParams.callbacks.ShowGui = [fontFilePresent]() { Gui(fontFilePresent); };

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    ImmApp::Run(runnerParams, addons);

    return 0;
}
