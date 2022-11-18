from imgui_bundle import static, imgui, imgui_color_text_edit as ed, imgui_md


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

    if imgui.button("Test glfw link"):
        import imgui_bundle
        import glfw
        window = imgui_bundle.glfw_window_hello_imgui()
        glfw.set_window_pos(window, 10, 10)

        # from imgui_bundle import hello_imgui
        #
        # import glfw
        # import ctypes
        # window_address = hello_imgui.get_glfw_window_address()
        # window_pointer = ctypes.cast(window_address, ctypes.POINTER(glfw._GLFWwindow))
        # glfw.set_window_pos(window_pointer, 10, 10)


    show_palette_buttons()
    editor.render("Code")


def main():
    from imgui_bundle import run

    run(demo_imgui_color_text_edit, with_markdown=True)


if __name__ == "__main__":
    main()
