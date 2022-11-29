#pragma once

#include "imgui.h"
#include <optional>
#include <vector>

// Specific patches for python bindings, where ImWChar* cannot be bound to python

namespace PatchImGui
{
    ImFont* font_atlas_add_font_from_file_ttf(
        ImFontAtlas* self,
        const char* filename,
        float size_pixels,
        const ImFontConfig* font_cfg = NULL,
        std::optional<std::vector<int>> glyph_ranges_as_int_list = std::nullopt);


    std::vector<int>    font_atlas_glyph_ranges_default(ImFontAtlas* self);                // Basic Latin, Extended Latin
    std::vector<int>    font_atlas_glyph_ranges_greek(ImFontAtlas* self);                  // Default + Greek and Coptic
    std::vector<int>    font_atlas_glyph_ranges_korean(ImFontAtlas* self);                 // Default + Korean characters
    std::vector<int>    font_atlas_glyph_ranges_japanese(ImFontAtlas* self);               // Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs
    std::vector<int>    font_atlas_glyph_ranges_chinese_full(ImFontAtlas* self);            // Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs
    std::vector<int>    font_atlas_glyph_ranges_chinese_simplified_common(ImFontAtlas* self);// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese
    std::vector<int>    font_atlas_glyph_ranges_cyrillic(ImFontAtlas* self);               // Default + about 400 Cyrillic characters
    std::vector<int>    font_atlas_glyph_ranges_thai(ImFontAtlas* self);                   // Default + Thai characters
    std::vector<int>    font_atlas_glyph_ranges_vietnamese(ImFontAtlas* self);             // Default + Vietnamese characters


    void set_imgui_io_filename(const std::string& filename);
    void set_imgui_log_filename(const std::string& filename);

}
