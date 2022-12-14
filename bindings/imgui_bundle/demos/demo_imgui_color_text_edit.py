from imgui_bundle import imgui, imgui_color_text_edit as ed, imgui_md
from imgui_bundle.immapp import static

TextEditor = ed.TextEditor


def _prepare_text_editor():
    with open(__file__) as f:
        this_file_code = f.read()
    editor = TextEditor()
    editor.set_text(this_file_code)
    editor.set_language_definition(TextEditor.LanguageDefinition.python())
    return editor


@static(editor=_prepare_text_editor())
def demo_imgui_color_text_edit():
    static = demo_imgui_color_text_edit
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

    show_palette_buttons()
    editor.render("Code")


def main():
    from imgui_bundle import immapp

    immapp.run(demo_imgui_color_text_edit, with_markdown=True)


if __name__ == "__main__":
    main()
