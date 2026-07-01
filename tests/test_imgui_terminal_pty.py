"""LocalShellTransport tests: real shell on a pty, job control (POSIX only).

These encode the TIOCSCTTY lesson: without a controlling terminal there is no
foreground process group and ^C / ^Z never become SIGINT / SIGTSTP.
"""
import shutil
import sys
import time
from typing import Callable

import pytest

pytest.importorskip("pyte")

posix_with_bash = pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="needs a POSIX pty and bash",
)


def wait_for(predicate: Callable[[], bool],
             timeout: float = 5.0, step: float = 0.05) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return True
        time.sleep(step)
    return False


@posix_with_bash
def test_job_control() -> None:
    import fcntl
    import struct
    import termios

    from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport

    view = TerminalView(cols=80, rows=24)
    transport = LocalShellTransport(shell=shutil.which("bash"))
    transport.start(view)
    try:
        def display() -> str:
            return "\n".join(view.screen.display)

        # the pty must be the shell's controlling terminal (real foreground pgrp)
        assert wait_for(lambda: struct.unpack(
            "i", fcntl.ioctl(transport.master_fd, termios.TIOCGPGRP, b"\0\0\0\0"))[0] > 0)

        # Ctrl-C interrupts a foreground sleep -> prompt is live again
        view.on_input(b"sleep 20\n")
        time.sleep(0.5)
        view.on_input(b"\x03")
        time.sleep(0.3)
        view.on_input(b"echo ALIVE_$?\n")
        assert wait_for(lambda: "ALIVE_" in display()), display()

        # Ctrl-Z suspends a foreground sleep -> job-control message
        view.on_input(b"sleep 20\n")
        time.sleep(0.5)
        view.on_input(b"\x1a")
        assert wait_for(lambda: "topped" in display() or "uspended" in display()), display()
    finally:
        transport.stop()


@posix_with_bash
def test_shell_roundtrip_and_resize() -> None:
    from imgui_bundle.imgui_terminal import TerminalView, LocalShellTransport

    view = TerminalView(cols=40, rows=10)
    transport = LocalShellTransport(shell=shutil.which("bash"))
    transport.start(view)
    try:
        view.on_input(b"echo roundtrip_$((6*7))\n")
        assert wait_for(lambda: "roundtrip_42" in "\n".join(view.screen.display))

        # on_resize must propagate to the tty (checked via stty inside the shell)
        view.screen.resize(15, 60)
        view.on_resize(60, 15)
        view.on_input(b"echo size_$(stty size | tr ' ' 'x')\n")
        assert wait_for(lambda: "size_15x60" in "\n".join(view.screen.display))
    finally:
        transport.stop()
