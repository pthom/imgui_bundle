#include "snippets.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "immapp/code_utils.h"
#include "immapp/clock.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#ifdef __EMSCRIPTEN__
#include "immapp/js_clipboard_tricks.h"
#endif

#include <map>
#include "fplus/fplus.hpp"


namespace Snippets
{
    void _SetTheme(TextEditor& editor, SnippetTheme palette)
    {
        if (palette == SnippetTheme::Dark)
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

#ifdef __EMSCRIPTEN__
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

      if (shallFillBrowserClipboard)
          JsClipboard_SetClipboardText(editor.GetCursorText(0).c_str());
    }
#endif // #ifdef __EMSCRIPTEN__

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

        if (! fplus::map_contains(gEditors, id))
        {
            gEditors.insert({id, TextEditor()});
            gEditorChanged[id] = false;
            auto& editor = gEditors.at(id);
            _SetLanguage(editor, snippetData.Language);
            _SetTheme(editor, snippetData.Palette);
            editor.SetChangeCallback([id]() { gEditorChanged[id] = true; });
        }

        auto& editor = gEditors.at(id);
        editor.SetReadOnlyEnabled(snippetData.ReadOnly);
        editor.SetShowWhitespacesEnabled(false);
        if (editor.GetText().empty() || snippetData.ReadOnly)
        {
            std::string displayedCode = snippetData.DeIndentCode ? CodeUtils::UnindentCode(snippetData.Code) : snippetData.Code;
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
            lineHeight = ImGui::GetFontSize();
            ImGui::PopFont();
        }

        ImVec2 editorSize;
        {
            editorSize.x = width;

            int nbVisibleLines = 0;
            if ((snippetData.HeightInLines == 0) && (overrideHeightInLines==0))
                nbVisibleLines = (int)fplus::count('\n', snippetData.Code) + 1;
            else if (overrideHeightInLines != 0)
                nbVisibleLines = overrideHeightInLines;
            else
                nbVisibleLines = snippetData.HeightInLines;

            if ((snippetData.MaxHeightInLines > 0) && (nbVisibleLines > snippetData.MaxHeightInLines))
                nbVisibleLines = snippetData.MaxHeightInLines;
            editorSize.y = lineHeight * (float) nbVisibleLines + ImGui::GetStyle().ScrollbarSize;
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
                ImGui::Text("L:%02i C:%02i", pos.line + 1, pos.column + 1);
            }

            if (snippetData.ShowCopyButton)
            {
                ImGui::SetCursorPos({topRight.x - lineHeight * 1.5f, topRight.y});
                if (ImGui::Button(ICON_FA_COPY))
                {
                    timeClickCopyButton[id] = ImmApp::ClockSeconds();
                    ImGui::SetClipboardText(snippetData.Code.c_str());
                }

                bool wasCopiedRecently = false;
                if (fplus::map_contains(timeClickCopyButton, id))
                {
                    double now = ImmApp::ClockSeconds();
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

#ifdef __EMSCRIPTEN__
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
            auto linesPerSnippets = fplus::transform([](const SnippetData& s) {return fplus::count('\n', s.Code);}, snippets);
            overrideHeightInLines = (int)fplus::maximum(linesPerSnippets) + 1;
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
