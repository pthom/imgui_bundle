#include "patch_imgui.h"
#include "imgui.h"

#include <string>
#include <vector>


namespace PatchImGui
{
    // ImGuiIO::IniFilename & LogFilename
    // Those are bare pointers with no storage for a string.
    //
    // Let's hack a storage
    static std::string gIniFilename, gLogFilename;

    void set_imgui_io_filename(const std::string& filename)
    {
        gIniFilename = filename;
        ImGui::GetIO().IniFilename = gIniFilename.c_str();
    }

    void set_imgui_log_filename(const std::string& filename)
    {
        gLogFilename = filename;
        ImGui::GetIO().LogFilename = gLogFilename.c_str();
    }


    namespace
    {
        std::vector<ImWchar> ImWcharRangeToVec(const ImWchar* range)
        {
            std::vector<ImWchar> r;
            const ImWchar* v = range;
            while(*v != 0){
                r.push_back((int)*v);
                ++v;
            }

            r.push_back(0);
            return r;
        }
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_default(ImFontAtlas* self)                // Basic Latin, Extended Latin
    {
        return ImWcharRangeToVec(self->GetGlyphRangesDefault());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_greek(ImFontAtlas* self)                  // Default + Greek and Coptic
    {
        return ImWcharRangeToVec(self->GetGlyphRangesGreek());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_korean(ImFontAtlas* self)                 // Default + Korean characters
    {
        return ImWcharRangeToVec(self->GetGlyphRangesKorean());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_japanese(ImFontAtlas* self)               // Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs
    {
        return ImWcharRangeToVec(self->GetGlyphRangesJapanese());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_chinese_full(ImFontAtlas* self)            // Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs
    {
        return ImWcharRangeToVec(self->GetGlyphRangesChineseFull());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_chinese_simplified_common(ImFontAtlas* self)// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese
    {
        return ImWcharRangeToVec(self->GetGlyphRangesChineseSimplifiedCommon());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_cyrillic(ImFontAtlas* self)               // Default + about 400 Cyrillic characters
    {
        return ImWcharRangeToVec(self->GetGlyphRangesCyrillic());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_thai(ImFontAtlas* self)                    // Default + Thai characters
    {
        return ImWcharRangeToVec(self->GetGlyphRangesThai());
    }

    std::vector<ImWchar>    font_atlas_glyph_ranges_vietnamese(ImFontAtlas* self)              // Default + Vietnamese characters
    {
        return ImWcharRangeToVec(self->GetGlyphRangesVietnamese());
    }


} // namespace PatchImGui
