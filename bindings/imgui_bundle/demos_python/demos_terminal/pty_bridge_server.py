"""pty_bridge_server: expose a local shell over a websocket.

Run this on the machine whose shell you want to reach (a server, a robot's
companion computer, ...). A GUI client -- desktop `demo_terminal_websocket.py`
or a Pyodide/browser app -- connects and gets an interactive terminal.

This is deliberately tiny (~1 screen) so it is easy to audit and drop onto a
host. It is the remote counterpart of LocalShellTransport: same pty handling,
but the bytes travel over a websocket instead of staying in-process.

    pip install websockets
    python pty_bridge_server.py --host 127.0.0.1 --port 8765

Protocol (one shell per connection):
    client -> server:  binary frame           = bytes to write to the pty (keystrokes)
                       text frame '{"resize":[cols,rows]}' = window resize
    server -> client:  binary frame            = pty output

SECURITY: this hands out a raw shell to whoever connects. It has NO auth and is
a *demo*. Bind to 127.0.0.1, or put it behind an authenticated wss:// proxy /
SSH tunnel before exposing it. Not for production as-is.
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
import pty
import shutil
import signal
import struct
import termios

from websockets.asyncio.server import serve, ServerConnection


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


async def handle(ws: ServerConnection) -> None:
    shell = os.environ.get("SHELL", "/bin/bash")
    pid, master_fd = pty.fork()
    if pid == 0:  # child: pty.fork already made the pty our controlling terminal
        os.environ["TERM"] = "xterm-256color"
        os.execvp(shell, [shell])  # noqa: S606  (demo: intentional shell)
        os._exit(1)

    loop = asyncio.get_running_loop()
    output: asyncio.Queue[bytes | None] = asyncio.Queue()

    def on_readable() -> None:
        try:
            data = os.read(master_fd, 65536)
        except OSError:
            data = b""
        output.put_nowait(data or None)  # None == EOF (shell exited)
        if not data:
            loop.remove_reader(master_fd)

    loop.add_reader(master_fd, on_readable)

    async def pump_output() -> None:
        while (data := await output.get()) is not None:
            await ws.send(data)
        await ws.close()

    pump = asyncio.create_task(pump_output())
    try:
        async for message in ws:  # client -> pty
            if isinstance(message, bytes):
                os.write(master_fd, message)
            else:
                resize = json.loads(message).get("resize")
                if resize:
                    cols, rows = resize
                    _set_winsize(master_fd, rows, cols)
    finally:
        pump.cancel()
        loop.remove_reader(master_fd)
        try:
            os.close(master_fd)
            os.kill(pid, signal.SIGHUP)
        except OSError:
            pass


async def main(host: str, port: int) -> None:
    async with serve(handle, host, port):
        print(f"pty bridge listening on ws://{host}:{port}  (shell: "
              f"{os.environ.get('SHELL', '/bin/bash')})")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    if shutil.which("bash") is None and not os.environ.get("SHELL"):
        raise SystemExit("no shell found (set $SHELL)")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        pass
