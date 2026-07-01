"""Interactive terminal emulator demo: pyte (VT100 parsing) + Dear ImGui.

This file is just the *application*: it loads a monospace font, creates a
`TerminalView` widget, attaches a `LocalShellTransport` (a real shell on a
pseudo-terminal), and draws the widget inside a child window to show that it
embeds anywhere. The reusable parts live in:

  - terminal_view.py : the transport-agnostic widget (pyte model + draw + input)
  - local_shell.py   : the local-shell transport (POSIX pty)

Data path:  keyboard -> ImGui -> pty master -> shell -> pty master -> pyte -> ImGui draws it

Requires:   uv pip install pyte   (or: pip install pyte)
Platform:   POSIX only (the transport uses a pty). The widget itself is portable;
            a remote transport (SSH / Zenoh) would replace only local_shell.py.
"""
from __future__ import annotations

from imgui_bundle import imgui, imgui_ctx, immapp, hello_imgui, em_to_vec2

from imgui_bundle.demos_python.demos_terminal.terminal_view import TerminalView
from imgui_bundle.demos_python.demos_terminal.local_shell import LocalShellTransport

FONT_SIZE = 16.0

mono_font: imgui.ImFont | None = None
view: TerminalView | None = None
transport: LocalShellTransport | None = None
_focus_next = True


def load_fonts() -> None:
    global mono_font
    mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", FONT_SIZE)


def gui() -> None:
    global view, transport, _focus_next
    assert mono_font is not None

    if view is None:
        view = TerminalView(mono_font)
        transport = LocalShellTransport()
        transport.start(view)  # wires view.on_input / on_resize and starts the reader
    assert view is not None  # narrows for the render() call below

    imgui.text_disabled("Click to focus | scroll for history | drag to select, "
                        "Cmd/Ctrl-Shift-C to copy, Cmd/Ctrl-Shift-V to paste:")

    if _focus_next:  # focus the child on the first frame so typing works immediately
        imgui.set_next_window_focus()
        _focus_next = False
    with imgui_ctx.begin_child("terminal", em_to_vec2(0, 0),
                               imgui.ChildFlags_.borders.value):
        view.render()

    if transport is not None and not transport.alive:
        hello_imgui.get_runner_params().app_shall_exit = True


def on_exit() -> None:
    if transport is not None:
        transport.stop()


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
