//Demonstrates how to load a font with Chinese characters and display them in the GUI,
//using the common glyph ranges defined in by ImGui.

#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"


ImFont* font_cn = nullptr;


void LoadFont()
{
    // Note: this font is not provided with the ImGui bundle (too large).
    // You will need to provide it yourself, or use another font.
    const char *font_filename = "fonts/NotoSerifSC-VariableFont_wght.ttf";
    if (! HelloImGui::AssetExists(font_filename))
        return;

    // The range of Chinese characters is defined by ImGui as a single list of characters (List[ImWchar]), with a terminating 0.
    // (each range is a pair of successive characters in this list, with the second character being the last one in the range)
    const ImWchar * cn_glyph_ranges_imgui = ImGui::GetIO().Fonts->GetGlyphRangesChineseSimplifiedCommon();
    // We need to convert this list into a list of pairs (List[ImWcharPair]), where each pair is a range of characters.
    auto cn_glyph_ranges_pair = HelloImGui::TranslateCommonGlyphRanges(cn_glyph_ranges_imgui);

    HelloImGui::FontLoadingParams font_loading_params;
    font_loading_params.glyphRanges = cn_glyph_ranges_pair;
    font_cn = HelloImGui::LoadFont(font_filename, 40.0f, font_loading_params);
}


void Gui()
{
    if (font_cn != nullptr)
    {
        ImGui::PushFont(font_cn);
        ImGui::Text("Hello world");
        ImGui::Text("你好，世界");
        ImGui::PopFont();
    }
    else
    {
        ImGui::Text("Font file not found");
        ImGui::TextWrapped(R"(
        This font is not provided with the ImGui bundle (too large).
        You will need to provide it yourself, or use another font.
        )");
    }
}



int main(int, char **)
{
    ChdirBesideAssetsFolder();

    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.LoadAdditionalFonts = LoadFont;
    runner_params.callbacks.ShowGui = Gui;
    HelloImGui::Run(runner_params);
}
