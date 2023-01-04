#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include <fplus/fplus.hpp>

TextEditor _PrepareTextEditor()
{
    TextEditor editor;
    std::string filename = __FILE__;
    std::string this_file_code = fplus::read_text_file(filename)();
    editor.SetText(this_file_code);
    editor.SetLanguageDefinition(TextEditor::LanguageDefinition::CPlusPlus());
    return editor;
}


void DemoGui()
{
    static TextEditor editor = _PrepareTextEditor();

    ImGuiMd::Render(R"(
# ImGuiColorTextEdit:
[ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit)  is a colorizing text editor for ImGui, able to colorize C, C++, hlsl, Sql, angel_script and lua code
    )");

    auto ShowPaletteButtons = []()
    {
        if (ImGui::SmallButton("Dark palette"))
            editor.SetPalette(TextEditor::GetDarkPalette());
        ImGui::SameLine();
        if (ImGui::SmallButton("Light palette"))
            editor.SetPalette(TextEditor::GetLightPalette());
        ImGui::SameLine();
        if (ImGui::SmallButton("Retro blue palette"))
            editor.SetPalette(TextEditor::GetRetroBluePalette());
    };

    ShowPaletteButtons();
    ImGui::PushFont(ImGuiMd::GetCodeFont());
    editor.Render("Code");
    ImGui::PopFont();
}
