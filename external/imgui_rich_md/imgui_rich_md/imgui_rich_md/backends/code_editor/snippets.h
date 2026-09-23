#pragma once

#include <string>
#include <vector>

// Code snippets with syntax highlighting (ImGuiColorTextEdit), read-only or editable, with a copy
// button. The markdown code blocks use ShowCodeSnippet when built with IMGUI_RICHMD_WITH_CODE_EDITOR.
namespace Snippets
{

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
        Auto,   // Automatic based on bg color
        Dark,
        Light,
    };


    // DefaultSnippetLanguage: Cpp, or Python when the host defines IMGUI_RICHMD_DEFAULT_SNIPPET_LANGUAGE_PYTHON (Python bindings)
    inline SnippetLanguage DefaultSnippetLanguage()
    {
#ifdef IMGUI_RICHMD_DEFAULT_SNIPPET_LANGUAGE_PYTHON
        return SnippetLanguage::Python;
#else
        return SnippetLanguage::Cpp;
#endif
    }


    struct SnippetData
    {
        std::string Code = "";
        SnippetLanguage Language = DefaultSnippetLanguage();
        SnippetTheme Palette = SnippetTheme::Auto;

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
