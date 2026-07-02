"""Interactive terminal emulator demo for imgui_bundle.imgui_terminal.

This file is just the *application*: it loads a monospace font and shows one or
more `TerminalView` widgets in a tab bar, each backed by a `LocalShellTransport`
(a real shell on a pseudo-terminal). Use the '+' tab to open more terminals.

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

HELP = (
    "Click a terminal to focus it, then type as in any terminal.\n"
    "Scroll (wheel or scrollbar) for history; typing snaps back to the bottom.\n"
    "Select: drag, double-click a word, triple-click a line, or click then "
    "shift-click across scrollback.\n"
    "Copy: Cmd-C (macOS) / Ctrl-Shift-C.  Paste: Cmd-V / Ctrl-Shift-V / right-click.\n"
    "Ctrl-C / Ctrl-Z send signals; Ctrl/Alt-Left/Right jump word by word.\n"
    "'+' opens another terminal; the X on a tab closes it."
)

mono_font: imgui.ImFont | None = None


class Session:
    """One terminal tab: a widget + a local shell behind a pty."""
    _next_id = 1

    def __init__(self) -> None:
        self.id = Session._next_id
        Session._next_id += 1
        self.view = TerminalView()
        self.transport = LocalShellTransport()
        self.transport.start(self.view)  # wires on_input / on_resize, starts the reader


class AppState:
    def __init__(self) -> None:
        self.sessions = [Session()]
        self.focused_id: int | None = None  # session whose child holds keyboard focus


def load_fonts() -> None:
    global mono_font
    mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", font_size=16.0)


def help_marker(text: str) -> None:
    imgui.same_line()
    imgui.text_disabled("(?)")
    if imgui.begin_item_tooltip():
        imgui.push_text_wrap_pos(imgui.get_font_size() * 40.0)
        imgui.text_unformatted(text)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()


def gui(app_state: AppState) -> None:
    imgui.text("Terminals")
    help_marker(HELP)

    tab_bar_flags = (imgui.TabBarFlags_.auto_select_new_tabs.value
                     | imgui.TabBarFlags_.reorderable.value)
    if imgui.begin_tab_bar("terminals", tab_bar_flags):
        # '+' button on the right opens a new terminal
        if imgui.tab_item_button("+", imgui.TabItemFlags_.trailing.value
                                 | imgui.TabItemFlags_.no_tooltip.value):
            app_state.sessions.append(Session())

        survivors: list[Session] = []
        for s in app_state.sessions:
            selected, keep = imgui.begin_tab_item(f"Terminal {s.id}###{s.id}", True)
            if selected:
                with imgui_ctx.push_font(mono_font, 0.0):
                    if s.id != app_state.focused_id:  # tab just became active -> focus it for typing
                        imgui.set_next_window_focus()
                        app_state.focused_id = s.id
                    s.view.render_in_child("terminal",
                                           child_flags=imgui.ChildFlags_.borders.value)
                imgui.end_tab_item()
            # drop a tab when its X is clicked or its shell exits (e.g. `exit`)
            if keep and s.transport.alive:
                survivors.append(s)
            else:
                s.transport.stop()
        app_state.sessions[:] = survivors
        imgui.end_tab_bar()

    if not app_state.sessions:  # last terminal closed -> quit the app
        hello_imgui.get_runner_params().app_shall_exit = True


def on_exit(app_state: AppState) -> None:
    for s in app_state.sessions:
        s.transport.stop()


def main() -> None:
    app_state = AppState()

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "pyte + Dear ImGui terminal"
    params.app_window_params.window_geometry.size = (900, 560)
    params.callbacks.load_additional_fonts = load_fonts
    params.callbacks.show_gui = lambda: gui(app_state)
    params.callbacks.before_exit = lambda: on_exit(app_state)
    params.fps_idling.fps_idle = 20  # idling speed than the default (9), since shell output arrives asynchronously

    immapp.run(params)


if __name__ == "__main__":
    main()
