#include "snippets.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui_md_wrapper/imgui_md_internal.h"

#include <algorithm>
#include <map>


namespace Snippets
{
    void _SetTheme(TextEditor& editor, SnippetTheme palette)
    {
        if (palette == SnippetTheme::Auto)
        {
            auto& bg = ImGui::GetStyle().Colors[ImGuiCol_WindowBg];
            float luminance = 0.299f * bg.x + 0.587f * bg.y + 0.114f * bg.z;
            if (luminance > 0.5f)
                editor.SetPalette(TextEditor::GetLightPalette());
            else
                editor.SetPalette(TextEditor::GetDarkPalette());
        }
        else if (palette == SnippetTheme::Dark)
            editor.SetPalette(TextEditor::GetDarkPalette());
        else if (palette == SnippetTheme::Light)
            editor.SetPalette(TextEditor::GetLightPalette());
    }

    void _SetLanguage(TextEditor& editor, SnippetLanguage lang)
    {
        if (lang == SnippetLanguage::Cpp)
            editor.SetLanguage(TextEditor::Language::Cpp());
        else if (lang == SnippetLanguage::Hlsl)
            editor.SetLanguage(TextEditor::Language::Hlsl());
        else if (lang == SnippetLanguage::Glsl)
            editor.SetLanguage(TextEditor::Language::Glsl());
        else if (lang == SnippetLanguage::C)
            editor.SetLanguage(TextEditor::Language::C());
        else if (lang == SnippetLanguage::Sql)
            editor.SetLanguage(TextEditor::Language::Sql());
        else if (lang == SnippetLanguage::AngelScript)
            editor.SetLanguage(TextEditor::Language::AngelScript());
        else if (lang == SnippetLanguage::Lua)
            editor.SetLanguage(TextEditor::Language::Lua());
        else if (lang == SnippetLanguage::Python)
            editor.SetLanguage(TextEditor::Language::Python());
    }

#if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)
    void _ProcessClipboard_Emscripten(TextEditor& editor)
    {
      if (!ImGui::IsItemHovered())
          return;

      ImGuiIO& io = ImGui::GetIO();
      auto shift = io.KeyShift;
      //auto ctrl = io.ConfigMacOSXBehaviors ? io.KeySuper : io.KeyCtrl;
      // auto alt = io.ConfigMacOSXBehaviors ? io.KeyCtrl : io.KeyAlt;

      auto ctrl = io.KeySuper || io.KeyCtrl;

      bool shallFillBrowserClipboard = false;
      if (ctrl && !shift && ImGui::IsKeyPressed(ImGuiKey_Insert))
          shallFillBrowserClipboard = true;
      else if (ctrl && !shift && ImGui::IsKeyPressed(ImGuiKey_C))
          shallFillBrowserClipboard = true;
      else if (ctrl && !shift && ImGui::IsKeyPressed(ImGuiKey_X))
          shallFillBrowserClipboard = true;
      else if (!ctrl && shift && ImGui::IsKeyPressed(ImGuiKey_Delete))
          shallFillBrowserClipboard = true;

      // ImmApp routes the clipboard to the browser (see js_clipboard_tricks in immapp)
      if (shallFillBrowserClipboard)
          ImGui::SetClipboardText(editor.GetCursorText(0).c_str());
    }
#endif // #if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)

    // The copy button: the FontAwesome "copy" glyph when the current font has it (ImGui Bundle merges
    // FontAwesome into its fonts), else two overlapping squares drawn with the draw list
    static bool CopyButton(float lineHeight)
    {
        const ImWchar copyGlyph = 0xF0C5;  // ICON_FA_COPY, FontAwesome 4 and 6
        if (ImGui::GetFont()->IsGlyphInFont(copyGlyph))
            return ImGui::Button("\xef\x83\x85");
        bool clicked = ImGui::Button("##copy", ImVec2(lineHeight * 1.2f, 0.f));
        ImVec2 mi = ImGui::GetItemRectMin(), ma = ImGui::GetItemRectMax();
        float s = (ma.y - mi.y) * 0.45f, cx = (mi.x + ma.x) * 0.5f, cy = (mi.y + ma.y) * 0.5f;
        ImU32 col = ImGui::GetColorU32(ImGuiCol_Text);
        ImDrawList* dl = ImGui::GetWindowDrawList();
        dl->AddRect(ImVec2(cx - s * 0.7f, cy - s * 0.3f), ImVec2(cx + s * 0.3f, cy + s * 0.7f), col, 1.f);
        dl->AddRect(ImVec2(cx - s * 0.3f, cy - s * 0.7f), ImVec2(cx + s * 0.7f, cy + s * 0.3f), col, 1.f);
        return clicked;
    }

    static std::string AddFinalEmptyLineIfMissing(const std::string &s)
    {
        if (s.empty())
            return s;
        bool hasEmptyLine = (s.back() == '\n');
        if (hasEmptyLine)
            return s;
        else
        {
            printf("Adding final empty line last=%c\n", s.back());
            return s + "\n";
        }
    }

    bool ShowEditableCodeSnippet(const std::string& label_id, SnippetData* snippetDataPtr, float width, int overrideHeightInLines)
    {
        SnippetData& snippetData = *snippetDataPtr;

        if (width == 0.f)
            width = (ImGui::GetContentRegionAvail().x - ImGui::GetStyle().ItemSpacing.x);

        auto id = ImGui::GetID(label_id.c_str());
        ImGui::PushID(label_id.c_str());
        static std::map<ImGuiID, TextEditor> gEditors;
        static std::map<ImGuiID, double> timeClickCopyButton;
        static std::map<ImGuiID, bool> gEditorChanged;

        if (gEditors.find(id) == gEditors.end())
        {
            gEditors.insert({id, TextEditor()});
            gEditorChanged[id] = false;
            auto& editor = gEditors.at(id);
            _SetLanguage(editor, snippetData.Language);
            editor.SetChangeCallback([id]() { gEditorChanged[id] = true; });
        }

        auto& editor = gEditors.at(id);
        editor.SetReadOnlyEnabled(snippetData.ReadOnly);
        editor.SetCaretsVisible(!snippetData.ReadOnly);
        editor.SetShowWhitespacesEnabled(false);
        _SetTheme(editor, snippetData.Palette);
        if (editor.GetText().empty() || snippetData.ReadOnly)
        {
            std::string displayedCode = snippetData.DeIndentCode ? ImGuiMd::Internal::Unindent(snippetData.Code, true) : snippetData.Code;
            if (snippetData.AddFinalEmptyLine)
                displayedCode = AddFinalEmptyLineIfMissing(displayedCode);

            if (editor.GetText() != displayedCode)
                editor.SetText(displayedCode);
        }

        ImGui::BeginGroup();

        // Title Line
        bool hasTitleLine = ! snippetData.DisplayedFilename.empty() || snippetData.ShowCopyButton || snippetData.ShowCursorPosition;

        float lineHeight;
        {
            auto codeFont = ImGuiMd::GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size);
            lineHeight = ImGui::GetTextLineHeightWithSpacing();
            ImGui::PopFont();
        }

        ImVec2 editorSize;
        {
            editorSize.x = width;

            int nbVisibleLines = 0;
            if ((snippetData.HeightInLines == 0) && (overrideHeightInLines==0))
                nbVisibleLines = (int)std::count(snippetData.Code.begin(), snippetData.Code.end(), '\n') + 1;
            else if (overrideHeightInLines != 0)
                nbVisibleLines = overrideHeightInLines;
            else
                nbVisibleLines = snippetData.HeightInLines;

            if ((snippetData.MaxHeightInLines > 0) && (nbVisibleLines > snippetData.MaxHeightInLines))
                nbVisibleLines = snippetData.MaxHeightInLines;

            // + ImGui::GetStyle().ScrollbarSize: account for a possible horizontal scrollbar
            editorSize.y = lineHeight * (float)nbVisibleLines + ImGui::GetStyle().ScrollbarSize;
        }

        if (hasTitleLine)
        {
            ImVec2 topLeft = ImGui::GetCursorPos();
            ImVec2 topRight { topLeft.x + editorSize.x, topLeft.y};
            float textY = topRight.y + (float)lineHeight * 0.2f;

            if (! snippetData.DisplayedFilename.empty())
            {
                ImGui::SetCursorPos({topLeft.x, textY});
                ImGui::Text("%s", snippetData.DisplayedFilename.c_str());
            }

            if (snippetData.ShowCursorPosition)
            {
                float textX = snippetData.ShowCopyButton ? topRight.x - lineHeight * 6.f : topRight.x - lineHeight * 4.5f;
                ImGui::SetCursorPos({textX, textY});
                auto pos = editor.GetMainCursorPosition();
                ImGui::Text("L:%02zu C:%02zu", pos.line + 1, pos.index + 1);
            }

            if (snippetData.ShowCopyButton)
            {
                ImGui::SetCursorPos({topRight.x - lineHeight * 1.5f, topRight.y});
                if (CopyButton(lineHeight))
                {
                    timeClickCopyButton[id] = ImGui::GetTime();
                    ImGui::SetClipboardText(snippetData.Code.c_str());
                }

                bool wasCopiedRecently = false;
                if (timeClickCopyButton.find(id) != timeClickCopyButton.end())
                {
                    double now = ImGui::GetTime();
                    double deltaTime = now - timeClickCopyButton.at(id);
                    if (deltaTime < 0.7)
                        wasCopiedRecently = true;
                }
                if (wasCopiedRecently)
                    ImGui::SetTooltip("Copied!");
                else if (ImGui::IsItemHovered())
                    ImGui::SetTooltip("Copy");
            }
            ImGui::SetCursorPos(topRight);
            ImGui::NewLine();
        }

        auto codeFont = ImGuiMd::GetCodeFont();
        ImGui::PushFont(codeFont.font, codeFont.size);

        editor.Render(std::to_string(id).c_str(), editorSize, snippetData.Border);
        bool changed = gEditorChanged[id];
        gEditorChanged[id] = false;
        if (changed && !snippetData.ReadOnly)
            snippetData.Code = editor.GetText();

#if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)
        _ProcessClipboard_Emscripten(editor);
#endif

        ImGui::PopFont();
        ImGui::EndGroup();
        ImGui::PopID();

        return changed;
    }

    void ShowCodeSnippet(const SnippetData& snippetData, float width, int overrideHeightInLines)
    {
        auto code = snippetData.Code;
        auto nonConstSnippedData = const_cast<SnippetData&>(snippetData);  // I know...
        std::string labelId = nonConstSnippedData.Code;
        ShowEditableCodeSnippet(labelId, &nonConstSnippedData, width, overrideHeightInLines);
        nonConstSnippedData.Code = code;
    }



    float _EditorWidth(int nbSideBySideEditors)
    {
        float margins_x = (nbSideBySideEditors + 1) * ImGui::GetStyle().ItemSpacing.x;
        float windowContentWidth = ImGui::GetContentRegionAvail().x;
        float editorWidth= (windowContentWidth - margins_x) / nbSideBySideEditors;
        return editorWidth;
    }

    void ShowSideBySideSnippets(const std::vector<SnippetData>& snippets , bool hideIfEmpty, bool equalVisibleLines)
    {
        int nbSideBySideEditors = (int)snippets.size();

        if (hideIfEmpty)
        {
            for (const auto& snippet: snippets)
                if (snippet.Code.empty())
                    nbSideBySideEditors -= 1;
            if (nbSideBySideEditors == 0)
                return;
        }

        int overrideHeightInLines = 0;
        if (equalVisibleLines)
        {
            size_t maxLines = 0;
            for (const auto& s : snippets)
                maxLines = std::max(maxLines, (size_t)std::count(s.Code.begin(), s.Code.end(), '\n'));
            overrideHeightInLines = (int)maxLines + 1;
        }

        float editorWidth = _EditorWidth(nbSideBySideEditors);

        for (const auto& snippet: snippets)
        {
            bool show = !hideIfEmpty || !snippet.Code.empty();
            if (show)
            {
                ShowCodeSnippet(snippet, editorWidth, overrideHeightInLines);
                ImGui::SameLine();
            }
        }
        ImGui::NewLine();
    }


    void ShowSideBySideSnippets(const SnippetData& snippet1, const SnippetData& snippet2, bool hideIfEmpty, bool equalVisibleLines)
    {
        ShowSideBySideSnippets({snippet1, snippet2}, hideIfEmpty, equalVisibleLines);
    }
}
