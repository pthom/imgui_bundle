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


def download_url_bytes(url: str) -> bytes:
    """Download data from a URL synchronously. Works on both desktop (urllib) and Pyodide (sync XMLHttpRequest).
    Returns the downloaded bytes, or empty bytes on failure.

    Args:
        url: the URL to download from
    """
    ...


async def download_url_bytes_async(url: str) -> bytes:
    """Download data from a URL asynchronously.
    On Pyodide: uses pyfetch (non-blocking). On desktop: uses urllib in a thread.
    Returns the downloaded bytes, or empty bytes on failure.

    Usage:
        # In Pyodide (top-level await supported by runPythonAsync):
        data = await immapp.download_url_bytes_async(url)

        # On desktop:
        data = asyncio.run(immapp.download_url_bytes_async(url))

    Args:
        url: the URL to download from
    """
    ...
