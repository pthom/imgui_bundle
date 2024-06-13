#pragma once

#include <string>
#include <vector>

namespace Snippets
{
    //
    // TextEditorBundle: addition to ImGuiColorTextEdit, specific to ImGuiBundle
    //

    enum class SnippetLanguage
    {
        Cpp,
        Hlsl,
        Glsl,
        C,
        Sql,
        AngelScript,
        Lua,
        Python
    };

    enum class SnippetTheme
    {
        Dark,
        Light,
        RetroBlue,
        Mariana
    };


    // DefaultSnippetLanguage will be Cpp or Python if using python bindings.
    inline SnippetLanguage DefaultSnippetLanguage()
    {
#ifdef IMGUI_BUNDLE_BUILD_PYTHON
        return SnippetLanguage::Python;
#else
        return SnippetLanguage::Cpp;
#endif
    }


    struct SnippetData
    {
        std::string Code = "";
        SnippetLanguage Language = DefaultSnippetLanguage();
        SnippetTheme Palette = SnippetTheme::Light;

        bool ShowCopyButton = true;         // Displayed on top of the editor (Top Right corner)
        bool ShowCursorPosition = true;     // Show line and column number
        std::string DisplayedFilename = {}; // Displayed on top of the editor

        int HeightInLines = 0;              // Number of visible lines in the editor
        int MaxHeightInLines = 40;          // If the number of lines in the code exceeds this, the editor will scroll. Set to 0 to disable.

        bool ReadOnly = false;               // Snippets are read-only by default

        bool Border = false;                // Draw a border around the editor

        bool DeIndentCode = true;           // Keep the code indentation, but remove main indentation,
                                            // so that the displayed code start at column 1

        bool AddFinalEmptyLine = false;     // Add an empty line at the end of the code if missing
    };


    bool ShowEditableCodeSnippet(const std::string& label_id, SnippetData* snippetData, float width = 0.f, int overrideHeightInLines = 0);
    void ShowCodeSnippet(const SnippetData& snippetData, float width = 0.f, int overrideHeightInLines = 0);
    void ShowSideBySideSnippets(const SnippetData& snippet1, const SnippetData& snippet2,
                                bool hideIfEmpty = true, bool equalVisibleLines = true);
    void ShowSideBySideSnippets(const std::vector<SnippetData>& snippets ,
                                bool hideIfEmpty = true, bool equalVisibleLines = true);
};
