"""LocalShellTransport: run a local shell behind a pseudo-terminal and stream it
into a TerminalView.

This is the desktop implementation of the TerminalTransport protocol. It is
POSIX only (macOS / Linux) -- Windows would swap the `pty` stdlib module for
pywinpty (ConPTY), and a remote transport (SSH / Zenoh) would replace the pty
entirely while keeping the same `start()` / `stop()` surface.
"""
from __future__ import annotations

import fcntl
import os
import pty
import select
import struct
import subprocess
import termios
import threading

from imgui_bundle.imgui_terminal.terminal_view import TerminalView


def _become_session_leader() -> None:
    # Runs in the child before exec. setsid() starts a new session but leaves it
    # with NO controlling terminal; we must claim the pty explicitly. Without a
    # controlling terminal there is no foreground process group, so the line
    # discipline never turns ^C / ^Z into SIGINT / SIGTSTP -- i.e. job control
    # (Ctrl-C interrupt, Ctrl-Z suspend) silently does nothing.
    os.setsid()
    fcntl.ioctl(0, termios.TIOCSCTTY, 0)  # fd 0 is the pty slave (subprocess dup2'd it)


class LocalShellTransport:
    def __init__(self, shell: str | None = None):
        self.shell = shell or os.environ.get("SHELL", "/bin/bash")
        self.master_fd = -1
        self.proc: subprocess.Popen[bytes] | None = None
        self.alive = False

    def start(self, view: TerminalView) -> None:
        """Spawn the shell and connect it to `view`.

        Takes ownership of `view.on_input` and `view.on_resize` (both are
        overwritten to point at the pty); to observe keystrokes, wrap
        `view.on_input` AFTER calling start(). Output is fed to `view.feed()`
        from a background reader thread.
        """
        self.master_fd, slave_fd = pty.openpty()
        self._set_winsize(view.rows, view.cols)
        self.proc = subprocess.Popen(
            [self.shell],
            stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
            preexec_fn=_become_session_leader,  # new session + controlling tty (job control)
            env={**os.environ, "TERM": "xterm-256color"},
        )
        os.close(slave_fd)  # child holds it now

        view.on_input = self.write
        view.on_resize = lambda cols, rows: self._set_winsize(rows, cols)

        self.alive = True
        threading.Thread(target=self._reader, args=(view,), daemon=True).start()

    def _reader(self, view: TerminalView) -> None:
        while self.alive:
            try:
                r, _, _ = select.select([self.master_fd], [], [], 0.1)
                if self.master_fd in r:
                    data = os.read(self.master_fd, 65536)
                    if not data:
                        break
                    view.feed(data)
            except OSError:
                break
        self.alive = False

    def write(self, data: bytes) -> None:
        try:
            os.write(self.master_fd, data)
        except OSError:
            pass

    def _set_winsize(self, rows: int, cols: int) -> None:
        # tell the kernel the tty size; the shell receives SIGWINCH automatically
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ,
                    struct.pack("HHHH", rows, cols, 0, 0))

    def stop(self) -> None:
        self.alive = False
        if self.proc is not None:
            try:
                self.proc.terminate()
            except Exception:
                pass
        try:
            os.close(self.master_fd)
        except OSError:
            pass
