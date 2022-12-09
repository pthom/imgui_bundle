#pragma once

#include "imgui.h"
#include <optional>
#include <vector>
#include <string>


// Specific patches for python bindings, where ImWChar* cannot be bound to python

namespace PatchImGui
{
    
    std::vector<ImWchar>    font_atlas_glyph_ranges_default(ImFontAtlas* self);                // Basic Latin, Extended Latin
    std::vector<ImWchar>    font_atlas_glyph_ranges_greek(ImFontAtlas* self);                  // Default + Greek and Coptic
    std::vector<ImWchar>    font_atlas_glyph_ranges_korean(ImFontAtlas* self);                 // Default + Korean characters
    std::vector<ImWchar>    font_atlas_glyph_ranges_japanese(ImFontAtlas* self);               // Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs
    std::vector<ImWchar>    font_atlas_glyph_ranges_chinese_full(ImFontAtlas* self);            // Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs
    std::vector<ImWchar>    font_atlas_glyph_ranges_chinese_simplified_common(ImFontAtlas* self);// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese
    std::vector<ImWchar>    font_atlas_glyph_ranges_cyrillic(ImFontAtlas* self);               // Default + about 400 Cyrillic characters
    std::vector<ImWchar>    font_atlas_glyph_ranges_thai(ImFontAtlas* self);                   // Default + Thai characters
    std::vector<ImWchar>    font_atlas_glyph_ranges_vietnamese(ImFontAtlas* self);             // Default + Vietnamese characters


    void set_imgui_io_filename(const std::string& filename);
    void set_imgui_log_filename(const std::string& filename);

}
