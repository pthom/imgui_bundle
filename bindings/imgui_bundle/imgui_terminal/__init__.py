"""imgui_terminal: a terminal emulator widget for Dear ImGui (pyte-based).

- `TerminalView` is the widget: it renders a VT100 screen and translates
  keyboard/mouse input, but knows nothing about where the bytes come from.
- A *transport* produces/consumes those bytes: `LocalShellTransport` runs a
  local shell behind a pty (POSIX); remote transports (SSH, websocket, Zenoh)
  implement the same two-method `TerminalTransport` protocol.

Requires the `pyte` package: pip install "imgui-bundle[terminal]"

Quick start (see bindings/imgui_bundle/demos_python/demos_terminal/ for a
complete demo):

    from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport

    view = TerminalView(mono_font)      # a monospace ImFont
    transport = LocalShellTransport()
    transport.start(view)

    def gui():                          # each frame
        view.render_in_child("terminal")
"""
from typing import Any

from imgui_bundle.imgui_terminal.terminal_view import (
    TerminalView,
    TerminalTheme,
    TerminalTransport,
)

__all__ = ["TerminalView", "TerminalTheme", "TerminalTransport", "LocalShellTransport"]


def __getattr__(name: str) -> Any:
    # LocalShellTransport is imported lazily: it needs the POSIX pty/termios
    # modules, and must not break `import imgui_bundle.imgui_terminal` on
    # platforms without them (Windows, Pyodide) where only the widget +
    # a remote transport are usable.
    if name == "LocalShellTransport":
        from imgui_bundle.imgui_terminal.local_shell import LocalShellTransport
        return LocalShellTransport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
