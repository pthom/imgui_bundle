# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_color_text_edit as ed, imgui_md
from imgui_bundle.immapp import static

TextEditor = ed.TextEditor


def _prepare_text_editor():
    with open(__file__, encoding="utf8") as f:
        this_file_code = f.read()
    editor = TextEditor()
    editor.set_text(this_file_code)
    editor.set_language_definition(TextEditor.LanguageDefinition.python())
    return editor


@static(editor=_prepare_text_editor())
def demo_gui():
    static = demo_gui
    editor = static.editor

    imgui_md.render(
        """
# ImGuiColorTextEdit:
[ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit)  is a colorizing text editor for ImGui, able to colorize C, C++, hlsl, Sql, angel_script and lua code
    """
    )

    def show_palette_buttons():
        if imgui.small_button("Dark palette"):
            editor.set_palette(ed.TextEditor.get_dark_palette())
        imgui.same_line()
        if imgui.small_button("Light palette"):
            editor.set_palette(TextEditor.get_light_palette())
        imgui.same_line()
        if imgui.small_button("Retro blue palette"):
            editor.set_palette(TextEditor.get_retro_blue_palette())
        imgui.same_line()
        if imgui.small_button("Mariana palette"):
            editor.set_palette(TextEditor.get_mariana_palette())

    show_palette_buttons()
    imgui.push_font(imgui_md.get_code_font())
    editor.render("Code")
    imgui.pop_font()


def main():
    from imgui_bundle import immapp

    immapp.run(demo_gui, with_markdown=True)


if __name__ == "__main__":
    main()
