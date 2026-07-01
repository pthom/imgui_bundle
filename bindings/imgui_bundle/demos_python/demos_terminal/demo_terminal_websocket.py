"""Remote-shell demo: TerminalView driven over a websocket.

Shows the *transport* half of imgui_bundle.imgui_terminal: the widget is exactly
the same one the local-shell demo uses, but the bytes now travel over a
websocket to `pty_bridge_server.py`. Replace the pty bridge with a shell on a
robot / server / container and the GUI is unchanged.

For convenience this demo starts a local `pty_bridge_server.py` subprocess and
connects to it. Point BRIDGE_URL at an already-running bridge to skip that.

    pip install "imgui-bundle[terminal]" websockets
    python demo_terminal_websocket.py

The same `WebSocketTransport` is what a Pyodide/browser build would use (there
is no local pty in the browser), talking to a bridge on some host.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import threading
from pathlib import Path

from imgui_bundle import imgui, imgui_ctx, immapp, hello_imgui
from imgui_bundle.imgui_terminal import TerminalView

from websockets.asyncio.client import connect

BRIDGE_URL = "ws://127.0.0.1:8765"
SPAWN_LOCAL_BRIDGE = True      # set False to connect to a remote bridge instead
FONT_SIZE = 16.0


class WebSocketTransport:
    """A TerminalTransport that tunnels the terminal over a websocket.

    Runs an asyncio event loop in a background thread; GUI-thread callbacks hand
    work to it via `call_soon_threadsafe`.
    """
    def __init__(self, url: str):
        self.url = url
        self.alive = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._out: asyncio.Queue[bytes | str] | None = None
        self._stop_evt: asyncio.Event | None = None
        self._view: TerminalView | None = None

    def start(self, view: TerminalView) -> None:
        self._view = view
        view.on_input = self._on_input
        view.on_resize = self._on_resize
        self.alive = True
        threading.Thread(target=lambda: asyncio.run(self._main()), daemon=True).start()

    async def _main(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._out = asyncio.Queue()
        self._stop_evt = asyncio.Event()
        view, out = self._view, self._out
        assert view is not None
        try:
            async with connect(self.url, max_size=None) as ws:
                await ws.send(json.dumps({"resize": [view.cols, view.rows]}))

                async def recv() -> None:
                    async for msg in ws:
                        if isinstance(msg, bytes):
                            view.feed(msg)

                async def send() -> None:
                    while True:
                        await ws.send(await out.get())

                # exit cleanly when recv/send finish OR stop() is requested
                tasks = [asyncio.create_task(recv()), asyncio.create_task(send()),
                         asyncio.create_task(self._stop_evt.wait())]
                _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in pending:
                    task.cancel()
        except Exception as e:
            print(f"[websocket transport] {type(e).__name__}: {e}", file=sys.stderr)
        self.alive = False

    def _enqueue(self, item: bytes | str) -> None:
        if self._loop is not None and self._out is not None:
            self._loop.call_soon_threadsafe(self._out.put_nowait, item)

    def _on_input(self, data: bytes) -> None:
        self._enqueue(data)

    def _on_resize(self, cols: int, rows: int) -> None:
        self._enqueue(json.dumps({"resize": [cols, rows]}))

    def stop(self) -> None:
        self.alive = False
        if self._loop is not None and self._stop_evt is not None:
            self._loop.call_soon_threadsafe(self._stop_evt.set)


mono_font: imgui.ImFont | None = None
view: TerminalView | None = None
transport: WebSocketTransport | None = None
bridge_proc: subprocess.Popen[bytes] | None = None


def load_fonts() -> None:
    global mono_font
    mono_font = hello_imgui.load_font("fonts/Inconsolata-Medium.ttf", FONT_SIZE)


def gui() -> None:
    global view, transport
    if view is None:
        view = TerminalView()
        transport = WebSocketTransport(BRIDGE_URL)
        transport.start(view)

    imgui.text_disabled(f"Terminal over a websocket -> {BRIDGE_URL} "
                        "(same widget, remote bytes)")
    with imgui_ctx.push_font(mono_font, 0.0):
        view.render_in_child("terminal", child_flags=imgui.ChildFlags_.borders.value)


def on_exit() -> None:
    if transport is not None:
        transport.stop()
    if bridge_proc is not None:
        bridge_proc.terminate()


def main() -> None:
    global bridge_proc
    if SPAWN_LOCAL_BRIDGE:
        server = Path(__file__).with_name("pty_bridge_server.py")
        bridge_proc = subprocess.Popen([sys.executable, str(server)])

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "imgui_terminal over websocket"
    params.app_window_params.window_geometry.size = (900, 560)
    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window)
    params.callbacks.load_additional_fonts = load_fonts
    params.callbacks.show_gui = gui
    params.callbacks.before_exit = on_exit
    params.fps_idling.enable_idling = False
    immapp.run(params)


if __name__ == "__main__":
    main()
