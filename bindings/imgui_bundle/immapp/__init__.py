# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import Any
from imgui_bundle import _imgui_bundle as _native_bundle
from imgui_bundle._imgui_bundle import immapp_cpp as immapp_cpp  # type: ignore
from imgui_bundle._imgui_bundle.immapp_cpp import (  # type: ignore
    clock_seconds,

    default_node_editor_context,
    default_node_editor_config,

    delete_node_editor_settings,
    has_node_editor_settings,
    node_editor_settings_location,

    em_size,
    em_to_vec2,
    pixels_to_em,
    pixel_size_to_em,

    run,
    run_with_markdown,
    AddOnsParams,
    snippets,

    begin_plot_in_node_editor,
    end_plot_in_node_editor,
    show_resizable_plot_in_node_editor,
    show_resizable_plot_in_node_editor_em,
    widget_with_resize_handle_in_node_editor,
    widget_with_resize_handle_in_node_editor_em,
)

# Note: to enable font awesome 6:
#     runner_params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome_4
from imgui_bundle.immapp import icons_fontawesome_6 as icons_fontawesome_6
from imgui_bundle.immapp import icons_fontawesome_4 as icons_fontawesome  # Icons font awesome v4

from imgui_bundle.immapp.immapp_utils import (
    static as static,
    run_anon_block as run_anon_block,
)

from imgui_bundle.immapp import immapp_code_utils

from imgui_bundle._imgui_bundle.hello_imgui import (  # type: ignore
    RunnerParams as RunnerParams,
    SimpleRunnerParams as SimpleRunnerParams,
)

# Import async support
from imgui_bundle.immapp.run_async_overloads import run_async as run_async

# Import notebook convenience API
from imgui_bundle.immapp import nb as nb

manual_render = _native_bundle.immapp_cpp.manual_render
__all__ = [
    "clock_seconds",
    "default_node_editor_context",
    "default_node_editor_config",
    "delete_node_editor_settings",
    "has_node_editor_settings",
    "node_editor_settings_location",
    "em_size",
    "em_to_vec2",
    "pixels_to_em",
    "pixel_size_to_em",
    "run",
    "run_async",
    "run_with_markdown",
    "AddOnsParams",
    "icons_fontawesome",  # v4
    "icons_fontawesome_4",
    "icons_fontawesome_6",
    "static",
    "run_anon_block",
    "RunnerParams",
    "SimpleRunnerParams",
    "snippets",
    "manual_render",
    "begin_plot_in_node_editor",
    "end_plot_in_node_editor",
    "show_resizable_plot_in_node_editor",
    "show_resizable_plot_in_node_editor_em",
    "widget_with_resize_handle_in_node_editor",
    "widget_with_resize_handle_in_node_editor_em",
    "immapp_code_utils",
    "nb",
]


def run_nb(*args: Any, **kwargs: Any) -> Any:
    """run_nb: alias for immapp.run, kept for backward compatibility.
    Was intended to be used in Jupyter notebooks. Now immapp.run is patched to work in notebooks.
    """
    return run(*args, **kwargs)

__all__.append("run_nb")


def render_markdown_doc_panel(doc: str, height_em: float = 20.0) -> None:
    """Render a markdown documentation panel with a light theme, inside a resizable child window.
    Useful for showing docstrings or documentation at the top of a demo.

    Args:
        doc: markdown string to render (will be unindented automatically)
        height_em: height of the panel in em units
    """
    from imgui_bundle import imgui, rich_md, hello_imgui
    tweaked_theme = hello_imgui.ImGuiTweakedTheme()
    tweaked_theme.theme = hello_imgui.ImGuiTheme_.gray_variations
    tweaked_theme.tweaks.rounding = 0.0
    hello_imgui.push_tweaked_theme(tweaked_theme)
    size = hello_imgui.em_to_vec2(0, height_em)
    # Note: with ResizeY, ImGui uses the size only on the very first frame
    # (it saves/restores the resized height in the ini file after that)
    imgui.begin_child("##doc", size,
                      imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_y)
    rich_md.render(doc)
    imgui.end_child()
    imgui.new_line()
    hello_imgui.pop_tweaked_theme()

__all__.append("render_markdown_doc_panel")


def _http_error_text(status: int, body: bytes) -> str:
    """The error of an HTTP status: its phrase, and the start of the body (web APIs explain their errors there).
    The phrase comes from Python, not from the server: browsers give none over HTTP/2."""
    import http
    try:
        phrase = " " + http.HTTPStatus(status).phrase
    except ValueError:
        phrase = ""
    excerpt = body[:200].decode("utf-8", errors="replace").strip()
    return f"HTTP {status}{phrase}" + (f": {excerpt}" if excerpt else "")


def _request_desktop(url: str, method: str, json_body: Any, timeout_s: float,
                     headers: dict[str, str] | None = None) -> tuple[int, bytes, str]:
    """Makes a request with urllib (blocking), and returns (status, data, error)"""
    import json
    import urllib.error
    import urllib.request
    request_headers = {"User-Agent": "imgui_bundle/1.0"}
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode()
        request_headers["Content-Type"] = "application/json"
    request_headers.update(headers or {})
    timeout_text = f"Timeout after {timeout_s:g} s"
    try:
        request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return response.status, response.read(), ""
    except urllib.error.HTTPError as e:  # urllib raises on an error status, with the body
        data = e.read()
        return e.code, data, _http_error_text(e.code, data)
    except TimeoutError:  # while reading the answer
        return 0, b"", timeout_text
    except urllib.error.URLError as e:  # while connecting
        return 0, b"", timeout_text if isinstance(e.reason, TimeoutError) else str(e.reason)
    except Exception as e:  # e.g. an invalid URL
        return 0, b"", str(e) or type(e).__name__


async def _request_browser(url: str, method: str, json_body: Any, timeout_s: float,
                           headers: dict[str, str] | None = None) -> tuple[int, bytes, str]:
    """Makes a request with the browser's fetch, and returns (status, data, error)"""
    import asyncio
    import json
    from pyodide.http import pyfetch  # type: ignore
    options: dict[str, Any] = {"method": method}
    request_headers: dict[str, str] = {}
    if json_body is not None:
        options["body"] = json.dumps(json_body)
        request_headers["Content-Type"] = "application/json"
    request_headers.update(headers or {})
    if request_headers:
        options["headers"] = request_headers
    try:
        # The time limit is for the answer, as on the desktop, not for reading a long body
        response = await asyncio.wait_for(pyfetch(url, **options), timeout_s)
        data: bytes = await response.bytes()
    except asyncio.TimeoutError:
        return 0, b"", f"Timeout after {timeout_s:g} s"
    except Exception as e:  # a network failure, or a refusal by CORS
        return 0, b"", str(e) or type(e).__name__
    return response.status, data, "" if response.ok else _http_error_text(response.status, data)


def download_url_bytes(url: str, timeout_s: float = 10.0) -> bytes:
    """Download data from a URL. Works on both desktop (urllib) and Pyodide (sync XMLHttpRequest).
    Returns the downloaded bytes, or empty bytes on failure (an error status included).
    This blocks the GUI: from a GUI function, prefer start_download().

    Args:
        url: the URL to download from
        timeout_s: how long to wait for the server's answer (on the desktop: Pyodide's sync request has no limit)
    """
    from imgui_bundle import __bundle_pyodide__
    if __bundle_pyodide__:
        try:
            from pyodide.code import run_js  # type: ignore
            # Sync XHR doesn't support responseType='arraybuffer'.
            # Instead, download as base64 text and decode in Python.
            _fetch_fn = run_js("""
            (function(url) {
                var xhr = new XMLHttpRequest();
                xhr.open('GET', url, false);
                xhr.overrideMimeType('text/plain; charset=x-user-defined');
                xhr.send();
                if (xhr.status === 200) {
                    var binary = '';
                    var bytes = xhr.responseText;
                    for (var i = 0; i < bytes.length; i++) {
                        binary += String.fromCharCode(bytes.charCodeAt(i) & 0xff);
                    }
                    return btoa(binary);
                } else {
                    return null;
                }
            })
            """)
            result = _fetch_fn(url)
            if result is not None and len(result) > 0:
                import base64
                return base64.b64decode(result)
        except Exception as e:
            import logging
            logging.getLogger("immapp").warning("Failed to download %s: %s", url, e)
        return b""
    else:
        _status, data, error = _request_desktop(url, "GET", None, timeout_s)
        if error:
            import logging
            logging.getLogger("immapp").warning("Failed to download %s: %s", url, error)
            return b""
        return data

__all__.append("download_url_bytes")


async def download_url_bytes_async(url: str, timeout_s: float = 10.0) -> bytes:
    """Download data from a URL asynchronously.
    Returns the downloaded bytes, or empty bytes on failure (an error status included).

    On Pyodide: uses pyfetch (non-blocking, lets the browser breathe).
    On desktop: uses urllib in a thread (non-blocking for the event loop).

    Usage:
        # In Pyodide (top-level await):
        data = await immapp.download_url_bytes_async("https://example.com/image.png")

        # On desktop:
        data = asyncio.run(immapp.download_url_bytes_async("https://..."))

    Args:
        url: the URL to download from
        timeout_s: how long to wait for the server's answer
    """
    from imgui_bundle import __bundle_pyodide__
    if __bundle_pyodide__:
        _status, data, error = await _request_browser(url, "GET", None, timeout_s)
        if error:
            import logging
            logging.getLogger("immapp").warning("Failed to download %s: %s", url, error)
            return b""
        return data
    else:
        import asyncio
        # Run sync download in a thread to avoid blocking the event loop
        return await asyncio.to_thread(download_url_bytes, url, timeout_s)

__all__.append("download_url_bytes_async")


class Download:
    """A request running in the background, started by start_download(). Look at `done` at each frame, then at
    `error` and `data`."""

    def __init__(self, url: str) -> None:
        self.url = url
        # (status, data, error), set once and in one assignment: the GUI never sees a half-written result
        self._result: tuple[int, bytes, str] | None = None
        self._task: Any = None  # in Pyodide: a reference to the task, which asyncio keeps only weakly

    @property
    def done(self) -> bool:
        """True once the request ended, with a success or a failure"""
        return self._result is not None

    @property
    def status(self) -> int:
        """The HTTP status, once done; 0 for a network failure or a timeout"""
        return self._result[0] if self._result is not None else 0

    @property
    def data(self) -> bytes:
        """The body of the response, once done (also with an error status)"""
        return self._result[1] if self._result is not None else b""

    @property
    def error(self) -> str:
        """Empty on success (a 2xx status). Else the error status with the start of the body, or the network failure"""
        return self._result[2] if self._result is not None else ""

__all__.append("Download")


def start_download(url: str, method: str = "GET", json_body: Any = None, timeout_s: float = 30.0,
                   headers: dict[str, str] | None = None) -> Download:
    """Starts a request that does not block the GUI: a thread on the desktop, a fetch in Pyodide.
    Call it from a GUI function, and look at the result's `done` at each frame.

    Args:
        url: the URL to request
        method: "GET", "POST", ...
        json_body: if given, sent as JSON (with Content-Type: application/json)
        timeout_s: how long to wait for the server's answer
        headers: more HTTP headers, e.g. {"Authorization": "Bearer <key>"}
    """
    from imgui_bundle import __bundle_pyodide__
    download = Download(url)
    if __bundle_pyodide__:
        import asyncio

        async def request_in_browser() -> None:
            download._result = await _request_browser(url, method, json_body, timeout_s, headers)
        download._task = asyncio.ensure_future(request_in_browser())
    else:
        import threading

        def request_in_thread() -> None:
            download._result = _request_desktop(url, method, json_body, timeout_s, headers)
        # A daemon thread: the app can quit while a request runs
        threading.Thread(target=request_in_thread, daemon=True).start()
    return download

__all__.append("start_download")


