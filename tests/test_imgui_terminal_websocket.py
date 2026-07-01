"""End-to-end websocket remote-shell test: pty_bridge_server + WebSocketTransport.

Spawns the bridge server as a subprocess, connects a TerminalView through the
demo's WebSocketTransport, and checks a command round-trips (POSIX only).
"""
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import pytest

pytest.importorskip("pyte")
pytest.importorskip("websockets")

posix = pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="needs a POSIX pty and bash",
)

_DEMOS = Path(__file__).resolve().parents[1] / (
    "bindings/imgui_bundle/demos_python/demos_terminal")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port: int = s.getsockname()[1]
        return port


def _wait_for(predicate: Callable[[], bool], timeout: float = 8.0, step: float = 0.05) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return True
        time.sleep(step)
    return False


@posix
def test_websocket_roundtrip() -> None:
    # import the demo module for its WebSocketTransport (adds demos dir to path)
    sys.path.insert(0, str(_DEMOS))
    import importlib
    ws_demo = importlib.import_module("demo_terminal_websocket")
    from imgui_bundle.imgui_terminal import TerminalView

    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, str(_DEMOS / "pty_bridge_server.py"),
         "--host", "127.0.0.1", "--port", str(port)])
    try:
        view = TerminalView(cols=80, rows=24)
        transport = ws_demo.WebSocketTransport(f"ws://127.0.0.1:{port}")
        # the transport makes one connection attempt; retry until the server is up
        deadline = time.time() + 8.0
        while not transport.alive and time.time() < deadline:
            transport.start(view)
            time.sleep(0.3)
        assert transport.alive, "did not connect to the bridge server"
        try:
            def display() -> str:
                return "\n".join(view.screen.display)

            # wait for the shell prompt before sending (zsh init must finish)
            assert _wait_for(lambda: display().strip() != ""), "no prompt"
            view.on_input(b"echo ws_roundtrip_$((6*7))\n")
            assert _wait_for(lambda: "ws_roundtrip_42" in display()), display()
        finally:
            transport.stop()
    finally:
        server.terminate()
        server.wait(timeout=5)
