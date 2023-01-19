#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "hello_imgui/icons_font_awesome.h"
#include "demo_utils/api_demos.h"


// Returns the custom font loaded by hello_imgui
ImFont* MyLoadFontsViaHelloImGui()
{
    // hello_imgui can load font and merge them with font awesome automatically.

    // First, we load the default fonts (the font that was loaded first is the default font)
    HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons();

    // Then we load our custom font
    const std::string fontFilename = "fonts/Akronim-Regular.ttf";
    ImFont* acronymFont = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFilename.c_str(), 40.f);
    return acronymFont;
}


ImFont* MyLoadFontsManually()
{
    // Fixme: this version triggers an exception in debug mode under msvc, far later, and deep inside FontAtlas callstack.
    // (although it seems to work fine in release mode. Probable memory overflow somewhere)

    // First, we load the default font
    // Note: 
    // on high dpi screen, this font might look very small if you do not take into account the font scaling factor, such as show below.
    // HelloImGui provides HelloImGui::DpiFontLoadingFactor() which corresponds to:
    //      `DpiWindowFactor() * 1.f / ImGui::GetIO().FontGlobalScale`
    //            where DpiWindowSizeFactor() is equal to `CurrentScreenPixelPerInch / 96` under windows and linux, 1 under macOS
    static ImFontConfig defaultFontConfig;
    defaultFontConfig.SizePixels = 14.f * HelloImGui::DpiFontLoadingFactor();
    ImGui::GetIO().Fonts->AddFontDefault(&defaultFontConfig);

    // Load a font and merge icons into it
    // i. load the font...
    ImFontAtlas* fontAtlas = ImGui::GetIO().Fonts;
    const float fontSizePixel = 40.0f * HelloImGui::DpiFontLoadingFactor();
    const std::string fontFilename = "demos_assets/fonts/Akronim-Regular.ttf";
    auto glyphRange = fontAtlas->GetGlyphRangesDefault();
    ImFont* acronymFont = fontAtlas->AddFontFromFileTTF(fontFilename.c_str(), fontSizePixel, NULL, glyphRange);

    // ii. ... Aad merge icons into the previous font
    ImFontConfig fontConfig;
    fontConfig.MergeMode = true;

    // See warning inside imgui.h:
    //     If you pass a 'glyph_ranges' array to AddFont*** functions, you need to make sure that your array persist up until the
    //     atlas is build (when calling GetTexData*** or Build()). We only copy the pointer, not the data.
    // We need to make sure that iconRanges is not destroyed when exiting this function! In this case, we can make it
    // either static or constexpr.
    constexpr ImWchar iconRanges[] = { ICON_MIN_FA, ICON_MAX_FA, 0 };
    acronymFont = fontAtlas->AddFontFromFileTTF("demos_assets/fonts/fontawesome-webfont.ttf", fontSizePixel, &fontConfig, iconRanges);
    return acronymFont;
}


int main(int, char**)
{
    ChdirBesideAssetsFolder();

    ImFont *customFont;

    auto gui = [&customFont]() {
        ImGui::PushFont(customFont);
        ImGui::Text("Hello " ICON_FA_SMILE);
        ImGui::PopFont();
        ImGui::Text("Text with standard font");
    };

    auto callbackLoadFont = [&customFont] {
        // Choose your own loading method below:
        // customFont = MyLoadFontsManually();
        customFont = MyLoadFontsViaHelloImGui();
    };

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.LoadAdditionalFonts = callbackLoadFont;
    runnerParams.callbacks.ShowGui = gui;

    ImmApp::Run(runnerParams);
    return 0;
}