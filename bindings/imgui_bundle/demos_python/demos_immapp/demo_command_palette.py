"""
A command palette, as in VS Code or Sublime Text.

Press **Ctrl+Shift+P** (**Cmd+Shift+P** on macOS): a searchable list of commands pops up, as in VS Code, powered by
[imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette). Type a few letters to filter it. One
command changes the theme in two steps, another writes to the log below. Learn how to register commands and their
callbacks.
"""

from imgui_bundle import immapp, hello_imgui, imgui
from imgui_bundle import imgui_command_palette as imcmd
from imgui_bundle import icons_fontawesome, ImVec4


class AppState:
    show_command_palette: bool = False
    command_palette_context: imcmd.ContextWrapper

    def __init__(self):
        self.command_palette_context = imcmd.ContextWrapper()


def init_command_palette():
    highlight_font_color = ImVec4(1.0, 0.0, 0.0, 1.0)
    imcmd.set_style_color(
        imcmd.ImCmdTextType.highlight,
        imgui.color_convert_float4_to_u32(highlight_font_color),
    )

    # Add theme command: a two steps command, with initial callback + SubsequentCallback
    select_theme_cmd = imcmd.Command()
    select_theme_cmd.name = "Select theme"

    def select_theme_cmd_initial_cb():
        imcmd.prompt(["Classic", "Dark", "Light"])

    def select_theme_cmd_subsequent_cb(selected_option: int):
        if selected_option == 0:
            imgui.style_colors_classic()
        elif selected_option == 1:
            imgui.style_colors_dark()
        elif selected_option == 2:
            imgui.style_colors_light()

    select_theme_cmd.initial_callback = select_theme_cmd_initial_cb
    select_theme_cmd.subsequent_callback = select_theme_cmd_subsequent_cb
    imcmd.add_command(select_theme_cmd)

    # Simple command that logs messages
    log_cmd = imcmd.Command()
    log_cmd.name = "You say goodbye"
    log_cmd.initial_callback = lambda: hello_imgui.log(
        hello_imgui.LogLevel.info,
        "... and I say hello..." + icons_fontawesome.ICON_FA_MUSIC,
    )
    imcmd.add_command(log_cmd)


def main():
    app_state = AppState()

    def gui():
        io = imgui.get_io()

        if io.key_ctrl and io.key_shift and imgui.is_key_pressed(imgui.Key.p):
            app_state.show_command_palette = not app_state.show_command_palette

        if app_state.show_command_palette:
            app_state.show_command_palette = imcmd.command_palette_window(
                "CommandPalette", True
            )

        imgui.text("Press Ctrl+Shift+P to bring up the command palette")

        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + 100)
        imgui.separator()
        hello_imgui.log_gui()

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params.callbacks.post_init = init_command_palette

    immapp.run(params)


if __name__ == "__main__":
    main()
