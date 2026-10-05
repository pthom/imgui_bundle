# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Tests of immapp's downloads (start_download, download_url_bytes), against a local HTTP server.

The desktop path only (urllib): the Pyodide path (fetch) is checked by running the demos in the playground.
"""
import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterator

import pytest

from imgui_bundle import immapp

IMAGE = b"\xff\xd8 not quite a jpeg"
SLOW_ANSWER_S = 1.0  # the delay of /slow, longer than the time limit of the tests that use it


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/image":
            self.answer(200, IMAGE)
        elif self.path == "/slow":
            time.sleep(SLOW_ANSWER_S)
            self.answer(200, IMAGE)
        else:
            self.answer(404, b"  no such point\n")

    def do_POST(self) -> None:
        """Echoes the JSON it received, with its Content-Type"""
        body = self.rfile.read(int(self.headers["Content-Length"]))
        echo = {"content_type": self.headers["Content-Type"], "received": json.loads(body)}
        self.answer(201, json.dumps(echo).encode())

    def answer(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002  # silences the server's log
        pass


@pytest.fixture(scope="module")
def server_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def wait(download: immapp.Download, max_wait_s: float = 5.0) -> immapp.Download:
    """Waits until the download is done, as a GUI would by looking at it at each frame"""
    deadline = time.time() + max_wait_s
    while not download.done and time.time() < deadline:
        time.sleep(0.01)
    assert download.done
    return download


def test_get(server_url: str) -> None:
    download = wait(immapp.start_download(server_url + "/image"))
    assert (download.status, download.data, download.error) == (200, IMAGE, "")


def test_error_status(server_url: str) -> None:
    download = wait(immapp.start_download(server_url + "/missing"))
    assert download.status == 404
    assert download.data == b"  no such point\n"  # the body, kept with an error status
    assert download.error == "HTTP 404 Not Found: no such point"


def test_timeout(server_url: str) -> None:
    download = immapp.start_download(server_url + "/slow", timeout_s=0.2)
    assert not download.done and (download.status, download.data, download.error) == (0, b"", "")
    wait(download)
    assert (download.status, download.data, download.error) == (0, b"", "Timeout after 0.2 s")


def test_network_failure() -> None:
    download = wait(immapp.start_download("http://127.0.0.1:9/"))  # port 9 (discard): nobody listens
    assert download.status == 0 and download.data == b"" and download.error != ""


def test_post_json(server_url: str) -> None:
    point = {"name": "Oscilloscope", "re": -1.806, "im": -0.024}
    download = wait(immapp.start_download(server_url + "/points", method="POST", json_body=point))
    assert (download.status, download.error) == (201, "")
    assert json.loads(download.data) == {"content_type": "application/json", "received": point}


def test_download_url_bytes(server_url: str) -> None:
    assert immapp.download_url_bytes(server_url + "/image") == IMAGE
    assert immapp.download_url_bytes(server_url + "/missing") == b""  # an error status gives no data
    assert immapp.download_url_bytes(server_url + "/slow", timeout_s=0.2) == b""
    assert asyncio.run(immapp.download_url_bytes_async(server_url + "/image")) == IMAGE
