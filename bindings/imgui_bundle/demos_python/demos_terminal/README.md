# Terminal emulator demo (pyte + Dear ImGui)

A small **interactive terminal emulator** widget for Dear ImGui: a real shell
running behind a pseudo-terminal, rendered with ImGui and embeddable in any
window or child window.

It is not part of the built-in demo suite, because it needs an extra dependency
(`pyte`) and the local-shell transport is POSIX-only. It is a copy-paste starting
point for "can imgui_bundle host a VT100 / terminal?".

## Run it

```bash
uv pip install pyte      # or: pip install pyte
python demo_terminal_pyte.py
```

Click the terminal to focus it, then type as in any terminal (colors, `vim`,
`htop`, `tmux`, job control with Ctrl-C / Ctrl-Z all work). Scroll through
history with the mouse wheel or the native scrollbar (the widget declares the
full history height to the host window, so ImGui scrolling just works; the view
follows live output until you scroll up, and typing snaps back to the bottom).
Drag with the left mouse button to select text;
to select across more than one screen, either drag past the top/bottom edge
(auto-scrolls) or click a start, scroll, then **shift-click** the end. Copy with
**Cmd-C** (macOS) or **Ctrl-Shift-C** (Linux/Windows), paste with **Cmd-V** /
**Ctrl-Shift-V**.

## Files

| file                   | role                                                            | portable? |
|------------------------|-----------------------------------------------------------------|-----------|
| `terminal_view.py`     | `TerminalView` widget + `TerminalTheme` + `TerminalTransport` protocol. pyte model, drawing, input, scrollback. Transport-agnostic. | yes (pyte + imgui) |
| `local_shell.py`       | `LocalShellTransport`: a real shell on a pty (the desktop transport) | no (POSIX pty) |
| `demo_terminal_pyte.py`| the immapp app: loads a font, wires view + transport, draws it in a child window | - |

## Architecture

Three decoupled pieces:

```
keyboard -> ImGui -> transport.write -> shell -> transport.feed -> pyte -> ImGui draws it
```

- **`TerminalView`** owns a pyte `HistoryScreen` and knows how to draw it and
  translate keyboard input. It knows nothing about where bytes come from: you push
  output in with `view.feed(bytes)`, and receive keystrokes via `view.on_input`.
- A **transport** produces/consumes those bytes. `LocalShellTransport` runs a local
  shell; a remote transport (SSH, Zenoh, websocket) implements the same
  `start()` / `stop()` contract (`TerminalTransport`).

## Embedding in your own app

```python
from imgui_bundle import imgui_ctx, hello_imgui, em_to_vec2
from terminal_view import TerminalView
from local_shell import LocalShellTransport

mono = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", 16)  # in load_additional_fonts

view = TerminalView(mono)
LocalShellTransport().start(view)          # desktop: local shell

def gui():                                 # inside any window, child, or dock node
    with imgui_ctx.begin_child("terminal", em_to_vec2(0, 0)):
        view.render()                      # fills the region; input only when focused
```

### Remote shell (SSH / robot companion computer / Zenoh)

Reuse the *same widget*; supply your own transport:

```python
view = TerminalView(mono)
view.on_input  = lambda data: channel.send(data)        # keystrokes -> remote pty
view.on_resize = lambda cols, rows: channel.resize(cols, rows)
# background reader:  for chunk in channel: view.feed(chunk)
```

This is also the only variant that can work under Emscripten/Pyodide, where there
is no local PTY or shell.

## Notes / adapting further

- **Windows:** swap the `pty` stdlib module in `local_shell.py` for `pywinpty`
  (ConPTY). The widget half is unchanged.
- **Job control:** the child must claim the pty as its controlling terminal
  (`TIOCSCTTY`), otherwise Ctrl-C / Ctrl-Z produce no signals. `local_shell.py`
  does this in `_become_session_leader`.
- **macOS Ctrl:** ImGui swaps Cmd<>Ctrl on macOS, so physical Ctrl arrives as
  `key_super`. `TerminalView` reads `io.config_mac_osx_behaviors` to keep physical
  Ctrl as the terminal control key.
- **TUIs (tmux, vim) and pyte's limits:** pyte is a solid VT100 emulator, not a
  complete xterm. `TerminalView` subclasses its screen (`_VTScreen`) to answer
  device-status / cursor-position queries (which tmux and vim need) and to survive
  pyte 0.8.2's private-DSR bug; `feed()` also swallows unsupported escapes so one
  bad sequence never kills the session. Most interactive apps work, but some
  advanced terminal features may still render imperfectly.
