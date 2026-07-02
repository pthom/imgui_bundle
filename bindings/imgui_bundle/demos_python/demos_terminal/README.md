# Terminal emulator demo (imgui_bundle.imgui_terminal)

Demo for the **`imgui_bundle.imgui_terminal`** module: an interactive terminal
emulator widget for Dear ImGui — a real shell running behind a pseudo-terminal,
rendered with ImGui and embeddable in any window or child window.

The reusable widget lives in `bindings/imgui_bundle/imgui_terminal/`
(`TerminalView`, `TerminalTheme`, `TerminalTransport`, `LocalShellTransport`);
this folder only holds the runnable demo.

## Demos in this folder

| file | what it shows | extra deps |
|------|---------------|------------|
| `demo_terminal_pyte.py` | local shell (the common case) | - |
| `demo_terminal_ssh.py` | same widget over an **SSH** channel (paramiko) | `paramiko` |
| `demo_terminal_websocket.py` | same widget over a **websocket** to `pty_bridge_server.py` | `websockets` |
| `pty_bridge_server.py` | host-side script: exposes a local shell over a websocket | `websockets` |

The remote demos (SSH, websocket) prove the transport abstraction: the widget is
byte-for-byte the same, only the byte source changes. The websocket path is also
what a Pyodide/browser build would use, since browsers have no local pty.

## Run it

```bash
pip install "imgui-bundle[terminal]"   # installs the pyte dependency
python demo_terminal_pyte.py           # local shell

# remote variants:
pip install websockets && python demo_terminal_websocket.py   # spawns its own bridge
pip install paramiko   && python demo_terminal_ssh.py         # edit host/user first
```

Click the terminal to focus it, then type as in any terminal (colors, `vim`,
`htop`, `tmux`, job control with Ctrl-C / Ctrl-Z all work). Scroll through
history with the mouse wheel or the native scrollbar (the view follows live
output until you scroll up; typing snaps back to the bottom). Drag with the
left mouse button to select text; double-click a word or triple-click a line.
To select across more than one screen, either drag past the top/bottom edge
(auto-scrolls) or click a start, scroll, then **shift-click** the end. Copy with
**Cmd-C** (macOS) or **Ctrl-Shift-C** (Linux/Windows), paste with **Cmd-V** /
**Ctrl-Shift-V** or a **right-click**.

## Architecture

Three decoupled pieces:

```
keyboard -> ImGui -> transport.write -> shell -> view.feed -> pyte -> ImGui draws it
```

- **`TerminalView`** owns a pyte `HistoryScreen` and knows how to draw it and
  translate keyboard input. It knows nothing about where bytes come from: you push
  output in with `view.feed(bytes)`, and receive keystrokes via `view.on_input`.
- A **transport** produces/consumes those bytes. `LocalShellTransport` runs a local
  shell (POSIX pty); a remote transport (SSH, Zenoh, websocket) implements the same
  `start()` / `stop()` contract (`TerminalTransport`). Note that `start()` takes
  ownership of `view.on_input` / `view.on_resize`.

## Embedding in your own app

```python
from imgui_bundle import hello_imgui, imgui_ctx
from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport

mono = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", 16)  # in load_additional_fonts

terminal_view = TerminalView()
LocalShellTransport().start(terminal_view)  # desktop: local shell


def gui():  # inside any window, child, or dock node
    with imgui_ctx.push_font(mono, 0.0):  # the widget renders with the active font
        terminal_view.render_in_child("terminal")  # child + scrollbar + focus handling
```

### Remote shell (SSH / robot companion computer / Zenoh)

Reuse the *same widget*; supply your own transport:

```python
terminal_view = TerminalView()
terminal_view.on_input = lambda data: channel.send(data)  # keystrokes -> remote pty
terminal_view.on_resize = lambda cols, rows: channel.resize(cols, rows)
# background reader:  for chunk in channel: terminal_view.feed(chunk)
```

This is also the only variant that can work under Emscripten/Pyodide, where there
is no local PTY or shell (the widget itself is pure Python and browser-safe).

## Notes / adapting further

- **Windows:** swap the `pty` stdlib module in `local_shell.py` for `pywinpty`
  (ConPTY). The widget half is unchanged.
- **Job control:** the child must claim the pty as its controlling terminal
  (`TIOCSCTTY`), otherwise Ctrl-C / Ctrl-Z produce no signals. `local_shell.py`
  does this in `_become_session_leader`.
- **macOS Ctrl:** ImGui swaps Cmd<>Ctrl on macOS, so physical Ctrl arrives as
  `key_super`. `TerminalView` reads `io.config_mac_osx_behaviors` to keep physical
  Ctrl as the terminal control key (and Cmd free for copy/paste).
- **TUIs (tmux, vim) and pyte's limits:** pyte is a solid VT100 emulator, not a
  complete xterm. `TerminalView` subclasses its screen (`_VTScreen`) to answer
  device-status / cursor-position queries (which tmux and vim need) and to survive
  pyte 0.8.2's private-DSR bug; `feed()` also swallows unsupported escapes so one
  bad sequence never kills the session. Known gaps inherited from pyte: no
  alternate screen buffer (vim/htop frames land in scrollback), no application
  cursor keys, no bracketed paste, and double-width (CJK/emoji) glyphs may
  overlap. The program-set window title is available as `view.title`.
