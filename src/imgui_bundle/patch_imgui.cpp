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


    ImFont* font_atlas_add_font_from_file_ttf(
        ImFontAtlas* self,
        const char* filename,
        float size_pixels,
        const ImFontConfig* font_cfg,
        std::optional<std::vector<int>> glyph_ranges_as_int_list)
    {
        static std::vector<std::vector<ImWchar>> all_glyph_ranges;

        ImFont *font = nullptr;

        if (glyph_ranges_as_int_list.has_value())
        {
            // from imgui.h doc:
            // - If you pass a 'glyph_ranges' array to AddFont*** functions, you need to make sure that your array persist up until the
            //   atlas is build (when calling GetTexData*** or Build()). We only copy the pointer, not the data.
            std::vector<ImWchar> glyph_range_this_call;
            for (int x : *glyph_ranges_as_int_list)
                glyph_range_this_call.push_back((ImWchar) x);
            glyph_range_this_call.push_back(0); // Add a final zero, in case the user forgot
            all_glyph_ranges.push_back(glyph_range_this_call); // "make sure that your array persist up until the atlas is build"

            // glyph_range_this_call will soon die, let's use a static one...
            const ImWchar* glyph_range_static = all_glyph_ranges.back().data();

            font = self->AddFontFromFileTTF(filename, size_pixels, font_cfg, glyph_range_static);
        }
        else
        {
            font = self->AddFontFromFileTTF(filename, size_pixels, font_cfg);
        }

        return font;
    };


    namespace
    {
        std::vector<int> ImWcharRangeToVecInt(const ImWchar* range)
        {
            std::vector<int> r;
            const ImWchar* v = range;
            while(*v != 0){
                r.push_back((int)*v);
                ++v;
            }
            r.push_back(0);
            return r;
        }
    }

    std::vector<int>    font_atlas_glyph_ranges_default(ImFontAtlas* self)                // Basic Latin, Extended Latin
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesDefault());
    }

    std::vector<int>    font_atlas_glyph_ranges_greek(ImFontAtlas* self)                  // Default + Greek and Coptic
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesGreek());
    }

    std::vector<int>    font_atlas_glyph_ranges_korean(ImFontAtlas* self)                 // Default + Korean characters
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesKorean());
    }

    std::vector<int>    font_atlas_glyph_ranges_japanese(ImFontAtlas* self)               // Default + Hiragana, Katakana, Half-Width, Selection of 2999 Ideographs
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesJapanese());
    }

    std::vector<int>    font_atlas_glyph_ranges_chinese_full(ImFontAtlas* self)            // Default + Half-Width + Japanese Hiragana/Katakana + full set of about 21000 CJK Unified Ideographs
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesChineseFull());
    }

    std::vector<int>    font_atlas_glyph_ranges_chinese_simplified_common(ImFontAtlas* self)// Default + Half-Width + Japanese Hiragana/Katakana + set of 2500 CJK Unified Ideographs for common simplified Chinese
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesChineseSimplifiedCommon());
    }

    std::vector<int>    font_atlas_glyph_ranges_cyrillic(ImFontAtlas* self)               // Default + about 400 Cyrillic characters
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesCyrillic());
    }

    std::vector<int>    font_atlas_glyph_ranges_thai(ImFontAtlas* self)                    // Default + Thai characters
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesThai());
    }

    std::vector<int>    font_atlas_glyph_ranges_vietnamese(ImFontAtlas* self)              // Default + Vietnamese characters
    {
        return ImWcharRangeToVecInt(self->GetGlyphRangesVietnamese());
    }


} // namespace PatchImGui
