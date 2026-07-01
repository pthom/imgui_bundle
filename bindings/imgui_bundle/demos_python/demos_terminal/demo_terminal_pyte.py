"""Interactive terminal emulator demo for imgui_bundle.imgui_terminal.

This file is just the *application*: it loads a monospace font, creates a
`TerminalView` widget, attaches a `LocalShellTransport` (a real shell on a
pseudo-terminal), and draws the widget in a child window.

The widget itself lives in the `imgui_bundle.imgui_terminal` module:
  - terminal_view.py : the transport-agnostic widget (pyte model + draw + input)
  - local_shell.py   : the local-shell transport (POSIX pty)

Data path:  keyboard -> ImGui -> pty master -> shell -> pty master -> pyte -> ImGui draws it

Requires:   pip install "imgui-bundle[terminal]"   (i.e. the pyte package)
Platform:   POSIX only (the transport uses a pty). The widget itself is portable;
            a remote transport (SSH / websocket / Zenoh) would replace only
            LocalShellTransport.
"""
from __future__ import annotations

from imgui_bundle import imgui, immapp, hello_imgui, imgui_ctx
from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport

mono_font: imgui.ImFont | None = None
terminal_view: TerminalView | None = None
shell_transport: LocalShellTransport | None = None


def load_fonts() -> None:
    global mono_font
    mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", font_size = 16.0)


def gui() -> None:
    global terminal_view, shell_transport, _focus_next

    if terminal_view is None:
        terminal_view = TerminalView()
        shell_transport = LocalShellTransport()
        shell_transport.start(terminal_view)  # wires view.on_input / on_resize and starts the reader

    imgui.text_disabled("Click to focus | scroll for history | drag to select, "
                        "Cmd/Ctrl-Shift-C to copy, Cmd/Ctrl-Shift-V to paste:")

    if imgui.get_frame_count() == 3:  # Give focus at startup
        imgui.set_next_window_focus()

    with imgui_ctx.push_font(mono_font, 0.0):
        terminal_view.render_in_child("terminal", child_flags=imgui.ChildFlags_.borders.value)

    if shell_transport is not None and not shell_transport.alive:
        hello_imgui.get_runner_params().app_shall_exit = True


def on_exit() -> None:
    if shell_transport is not None:
        shell_transport.stop()


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "pyte + Dear ImGui terminal"
    params.app_window_params.window_geometry.size = (900, 560)
    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window)
    params.callbacks.load_additional_fonts = load_fonts
    params.callbacks.show_gui = gui
    params.callbacks.before_exit = on_exit
    # shell output arrives asynchronously: keep repainting instead of idling
    params.fps_idling.enable_idling = False

    immapp.run(params)


if __name__ == "__main__":
    main()
