# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Terminal: a shell inside an ImGui window

A real shell in an ImGui widget: type commands, scroll back through the history, select and copy. The shell runs
behind a pseudo-terminal (macOS and Linux), [pyte](https://github.com/selectel/pyte) parses its VT100 output, and
`imgui_bundle.imgui_terminal.TerminalView` draws it. A standalone version, with more comments:
`demos_terminal/demo_terminal_pyte.py`.
"""
from __future__ import annotations

import atexit
import sys

from imgui_bundle import imgui, imgui_ctx, hello_imgui

try:
    from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport
    _PYTE_AVAILABLE = True
except ImportError:
    _PYTE_AVAILABLE = False

FONT_SIZE = 16.0
TERMINAL_HEIGHT_EM = 25.0

_mono_font: imgui.ImFont | None = None
_view: "TerminalView | None" = None
_transport: "LocalShellTransport | None" = None


def _lazy_init() -> None:
    global _mono_font, _view, _transport
    if _view is not None:
        return
    _mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", FONT_SIZE)
    _view = TerminalView()
    _transport = LocalShellTransport()
    _transport.start(_view)
    atexit.register(_transport.stop)


def gui() -> None:
    if not _PYTE_AVAILABLE:
        imgui.text_wrapped(
            "This demo needs the pyte package (VT100 emulator). Install it with:")
        install_cmd = 'pip install "imgui-bundle[terminal]"'
        imgui.text_colored(imgui.ImVec4(0.5, 0.8, 1.0, 1.0), "    " + install_cmd)
        imgui.same_line()
        if imgui.small_button("Copy"):
            imgui.set_clipboard_text(install_cmd)
        return
    if sys.platform == "win32":
        imgui.text_wrapped(
            "The local-shell demo needs a POSIX pty (macOS / Linux). The widget itself "
            "works everywhere with a remote transport (SSH, websocket), or pywinpty on "
            "Windows.")
        return

    _lazy_init()
    assert _view is not None and _transport is not None

    imgui.text_disabled(
        "A real shell in an ImGui widget. Click to focus | scroll for history | "
        "drag or shift-click to select | Cmd-C / Ctrl-Shift-C to copy")
    if not _transport.alive:
        imgui.text("[shell exited]")
        imgui.same_line()
        if imgui.small_button("Restart"):
            _transport.start(_view)
        return
    with imgui_ctx.push_font(_mono_font, 0.0):
        _view.render_in_child("terminal", hello_imgui.em_to_vec2(0, TERMINAL_HEIGHT_EM),
                              imgui.ChildFlags_.borders.value)


def main() -> None:
    from imgui_bundle import immapp
    immapp.run(gui, window_title="imgui_terminal demo", window_size=(900, 600))


if __name__ == "__main__":
    main()
