"""Remote-shell demo: TerminalView driven over SSH (paramiko).

Same widget as the local-shell demo; the transport is an SSH channel instead of
a local pty. This is the shape you'd use to open a shell on a server or a
robot's companion computer from a desktop GUI.

    pip install "imgui-bundle[terminal]" paramiko
    # edit the connection constants below, then:
    python demo_terminal_ssh.py

By default it connects to localhost as the current user via the SSH agent /
default keys -- which works if you have `sshd` enabled and key-based login to
yourself ("Remote Login" on macOS). Edit HOST / USERNAME / PASSWORD otherwise.
"""
from __future__ import annotations

import getpass
import threading

from imgui_bundle import imgui, imgui_ctx, immapp, hello_imgui
from imgui_bundle.imgui_terminal import TerminalView

import paramiko

HOST = "127.0.0.1"
PORT = 22
USERNAME = getpass.getuser()
PASSWORD: str | None = None      # None -> use SSH agent / default keys
FONT_SIZE = 16.0


class SSHTransport:
    """A TerminalTransport backed by a paramiko interactive shell channel."""
    def __init__(self, host: str, port: int, username: str, password: str | None):
        self.host, self.port = host, port
        self.username, self.password = username, password
        self.alive = False
        self.error: str | None = None
        self._client: paramiko.SSHClient | None = None
        self._chan: paramiko.Channel | None = None

    def start(self, view: TerminalView) -> None:
        view.on_input = self._write
        view.on_resize = self._resize
        threading.Thread(target=self._connect, args=(view,), daemon=True).start()

    def _connect(self, view: TerminalView) -> None:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # demo only
            client.connect(self.host, self.port, self.username, self.password,
                           look_for_keys=True, allow_agent=True, timeout=10)
            chan = client.invoke_shell(term="xterm-256color",
                                       width=view.cols, height=view.rows)
            self._client, self._chan = client, chan
            self.alive = True
            while self.alive:
                data = chan.recv(65536)
                if not data:
                    break
                view.feed(data)
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
        self.alive = False

    def _write(self, data: bytes) -> None:
        if self._chan is not None:
            self._chan.sendall(data)

    def _resize(self, cols: int, rows: int) -> None:
        if self._chan is not None:
            self._chan.resize_pty(width=cols, height=rows)

    def stop(self) -> None:
        self.alive = False
        if self._chan is not None:
            self._chan.close()
        if self._client is not None:
            self._client.close()


mono_font: imgui.ImFont | None = None
view: TerminalView | None = None
transport: SSHTransport | None = None


def load_fonts() -> None:
    global mono_font
    mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", FONT_SIZE)


def gui() -> None:
    global view, transport
    if view is None:
        view = TerminalView()
        transport = SSHTransport(HOST, PORT, USERNAME, PASSWORD)
        transport.start(view)

    imgui.text_disabled(f"Terminal over SSH -> {USERNAME}@{HOST}:{PORT}")
    if transport is not None and transport.error is not None:
        imgui.text_colored(imgui.ImVec4(1.0, 0.5, 0.5, 1.0),
                           f"SSH connection failed: {transport.error}")
        imgui.text_wrapped("Edit HOST / USERNAME / PASSWORD at the top of this file "
                           "(needs an SSH server you can log into).")
        return
    with imgui_ctx.push_font(mono_font, 0.0):
        view.render_in_child("terminal", child_flags=imgui.ChildFlags_.borders.value)


def on_exit() -> None:
    if transport is not None:
        transport.stop()


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "imgui_terminal over SSH"
    params.app_window_params.window_geometry.size = (900, 560)
    params.callbacks.load_additional_fonts = load_fonts
    params.callbacks.show_gui = gui
    params.callbacks.before_exit = on_exit
    params.fps_idling.fps_idle = 20  # idling speed than the default (9), since shell output arrives asynchronously
    immapp.run(params)


if __name__ == "__main__":
    main()
