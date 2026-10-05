from . import immapp_cpp as immapp_cpp
from .immapp_cpp import (
    clock_seconds as clock_seconds,
    default_node_editor_context as default_node_editor_context,
    em_size as em_size,
    em_to_vec2 as em_to_vec2,
    pixels_to_em as pixels_to_em,
    pixel_size_to_em as pixel_size_to_em,
    run as run,
    run_with_markdown as run_with_markdown,
    AddOnsParams as AddOnsParams,
    snippets as snippets,
    manual_render as manual_render,
    begin_plot_in_node_editor as begin_plot_in_node_editor,
    end_plot_in_node_editor as end_plot_in_node_editor,
    show_resizable_plot_in_node_editor as show_resizable_plot_in_node_editor,
    show_resizable_plot_in_node_editor_em as show_resizable_plot_in_node_editor_em,
)
from .immapp_utils import (
    static as static,
    run_anon_block as run_anon_block,
    add_static as add_static,
    add_static_values as add_static_values,
)
from .immapp_notebook import run_nb as run_nb

from imgui_bundle.hello_imgui import (
    RunnerParams as RunnerParams,
    SimpleRunnerParams as SimpleRunnerParams,
)

# Re-export run_async with all its overloads from the implementation module
# (Full type hints and docs are in run_async_overloads.py)
from .run_async_overloads import run_async as run_async
# Re-export nb module for notebook convenience API
from . import nb as nb


def render_markdown_doc_panel(doc: str, height_em: float = 20.0) -> None:
    """Render a markdown documentation panel with a light theme, inside a resizable child window.
    Useful for showing docstrings or documentation at the top of a demo.

    Args:
        doc: markdown string to render (will be unindented automatically)
        height_em: height of the panel in em units
    """
    ...


def download_url_bytes(url: str, timeout_s: float = 10.0) -> bytes:
    """Download data from a URL synchronously. Works on both desktop (urllib) and Pyodide (sync XMLHttpRequest).
    Returns the downloaded bytes, or empty bytes on failure (an error status included).
    This blocks the GUI: from a GUI function, prefer start_download().

    Args:
        url: the URL to download from
        timeout_s: how long to wait for the server's answer (on the desktop: Pyodide's sync request has no limit)
    """
    ...


async def download_url_bytes_async(url: str, timeout_s: float = 10.0) -> bytes:
    """Download data from a URL asynchronously.
    On Pyodide: uses pyfetch (non-blocking). On desktop: uses urllib in a thread.
    Returns the downloaded bytes, or empty bytes on failure (an error status included).

    Usage:
        # In Pyodide (top-level await supported by runPythonAsync):
        data = await immapp.download_url_bytes_async(url)

        # On desktop:
        data = asyncio.run(immapp.download_url_bytes_async(url))

    Args:
        url: the URL to download from
        timeout_s: how long to wait for the server's answer
    """
    ...


class Download:
    """A request running in the background, started by start_download(). Look at `done` at each frame, then at
    `error` and `data`."""
    url: str

    @property
    def done(self) -> bool:
        """True once the request ended, with a success or a failure"""
        ...

    @property
    def status(self) -> int:
        """The HTTP status, once done; 0 for a network failure or a timeout"""
        ...

    @property
    def data(self) -> bytes:
        """The body of the response, once done (also with an error status)"""
        ...

    @property
    def error(self) -> str:
        """Empty on success (a 2xx status). Else the error status with the start of the body, or the network failure"""
        ...


def start_download(url: str, method: str = "GET", json_body: object = None, timeout_s: float = 30.0) -> Download:
    """Starts a request that does not block the GUI: a thread on the desktop, a fetch in Pyodide.
    Call it from a GUI function, and look at the result's `done` at each frame:

        if imgui.button("Download"):
            state.download = immapp.start_download(url)
        if state.download is not None and state.download.done:
            if state.download.error:
                state.message = state.download.error  # e.g. "HTTP 404 Not Found: ..." (the start of the body)
            else:
                state.data = state.download.data
            state.download = None

    Args:
        url: the URL to request
        method: "GET", "POST", ...
        json_body: if given, sent as JSON (with Content-Type: application/json)
        timeout_s: how long to wait for the server's answer
    """
    ...
