// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include <fplus/fplus.hpp>

TextEditor _PrepareTextEditor()
{
    TextEditor editor;
    std::string filename = __FILE__;
#ifndef __EMSCRIPTEN__
    std::string this_file_code = fplus::read_text_file(filename)();
#else
    std::string this_file_code = fplus::read_text_file("/demos_cpp/demo_text_edit.cpp")();
#endif
    editor.SetText(this_file_code);
    editor.SetLanguageDefinition(TextEditor::LanguageDefinitionId::Cpp);
    return editor;
}


void demo_text_edit()
{
    static TextEditor editor = _PrepareTextEditor();

    ImGuiMd::Render(R"(
# ImGuiColorTextEdit
[ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit)  is a colorizing text editor for ImGui, able to colorize C, C++, hlsl, Sql, angel_script and lua code
    )");

    auto ShowPaletteButtons = []()
    {
        if (ImGui::SmallButton("Dark palette"))
            editor.SetPalette(TextEditor::PaletteId::Dark);
        ImGui::SameLine();
        if (ImGui::SmallButton("Light palette"))
            editor.SetPalette(TextEditor::PaletteId::Light);
        ImGui::SameLine();
        if (ImGui::SmallButton("Retro blue palette"))
            editor.SetPalette(TextEditor::PaletteId::RetroBlue);
        ImGui::SameLine();
        if (ImGui::SmallButton("Mariana palette"))
            editor.SetPalette(TextEditor::PaletteId::Mariana);
    };

    ShowPaletteButtons();
    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("Code");
    ImGui::PopFont();
}
