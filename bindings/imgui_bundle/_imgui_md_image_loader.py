# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Provides URL image download support for imgui_md.

When enabled, markdown images with http:// or https:// URLs are downloaded
and rendered as textures.

On desktop, downloads are asynchronous (background thread via ThreadPoolExecutor).
The callback returns Downloading on first call, then Ready/Failed once the download completes.
This avoids blocking the UI while images are being fetched.

On Pyodide, synchronous XMLHttpRequest is used (no threads available).
"""
import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Dict

# Enable logging with:
#    logging.getLogger("imgui_md_image_loader").setLevel(logging.DEBUG)
log = logging.getLogger("imgui_md_image_loader")

# Artificial delay for testing async downloads (set to 0 for production)
_DEBUG_DELAY_SECONDS = 0.0

# Background thread pool for async downloads (desktop only)
_executor = ThreadPoolExecutor(max_workers=2)
_pending: Dict[str, "Future[Any]"] = {}


def _do_download_desktop(url: str) -> bytes:
    """Blocking download (runs in background thread).
    Returns bytes on success, empty bytes on failure."""
    import urllib.request
    import time
    if _DEBUG_DELAY_SECONDS > 0:
        log.debug("Artificial delay of %.1fs for %s", _DEBUG_DELAY_SECONDS, url)
        time.sleep(_DEBUG_DELAY_SECONDS)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "imgui_bundle/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data: bytes = resp.read()
            log.debug("Downloaded %d bytes from %s", len(data), url)
            return data
    except Exception as e:
        log.warning("Failed to download %s: %s", url, e)
        return b""


def _download_desktop_async(url: str):
    """Async download callback for desktop (Option B).
    Returns Downloading on first call, Ready/Failed once done.
    Manages pending downloads internally."""
    from imgui_bundle import imgui_md
    result = imgui_md.MarkdownDownloadResult()

    # Already in progress: check if done
    if url in _pending:
        future = _pending[url]
        if not future.done():
            result.status = imgui_md.MarkdownDownloadStatus.downloading
            return result
        # Done - get result
        del _pending[url]
        data = future.result()
        if data:
            result.fill_from_bytes(data)
            result.status = imgui_md.MarkdownDownloadStatus.ready
        else:
            result.status = imgui_md.MarkdownDownloadStatus.failed
            result.error_message = f"Download failed for {url}"
        return result

    # First call: start background download
    log.debug("Starting async download for %s", url)
    _pending[url] = _executor.submit(_do_download_desktop, url)
    result.status = imgui_md.MarkdownDownloadStatus.downloading
    return result


_pyodide_js_initialized = False

def _ensure_pyodide_js():
    """Initialize the JS-side download infrastructure (once)."""
    global _pyodide_js_initialized
    if _pyodide_js_initialized:
        return
    from pyodide.code import run_js  # type: ignore
    run_js("""
    window._imgui_downloads = {};

    window._imgui_download_debug_delay_ms = 0;  // set to e.g. 3000 to simulate slow downloads

    window._imgui_start_download = function(url) {
        if (window._imgui_downloads[url]) return;  // already in progress
        window._imgui_downloads[url] = {status: 'downloading'};
        var doFetch = function() { fetch(url)
            .then(function(response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.arrayBuffer();
            })
            .then(function(buf) {
                window._imgui_downloads[url] = {status: 'ready', data: new Uint8Array(buf)};
            })
            .catch(function(e) {
                window._imgui_downloads[url] = {status: 'failed', error: e.toString()};
            }); };
        if (window._imgui_download_debug_delay_ms > 0)
            setTimeout(doFetch, window._imgui_download_debug_delay_ms);
        else
            doFetch();
    };

    window._imgui_poll_download = function(url) {
        return window._imgui_downloads[url] || {status: 'not_started'};
    };

    window._imgui_clear_download = function(url) {
        delete window._imgui_downloads[url];
    };
    """)
    _pyodide_js_initialized = True


def _download_pyodide_async(url: str):
    """Async download using JS fetch() in Pyodide.
    Returns Downloading on first call, Ready/Failed once done."""
    from imgui_bundle import imgui_md
    from pyodide.code import run_js  # type: ignore
    result = imgui_md.MarkdownDownloadResult()

    try:
        _ensure_pyodide_js()

        # Start download if not already in progress
        run_js(f"window._imgui_start_download({repr(url)})")

        # Poll status
        js_result = run_js(f"window._imgui_poll_download({repr(url)})")
        status = js_result.status

        if status == 'downloading':
            result.status = imgui_md.MarkdownDownloadStatus.downloading
        elif status == 'ready':
            data = bytes(js_result.data)
            log.debug("Downloaded %d bytes from %s (Pyodide)", len(data), url)
            result.fill_from_bytes(data)
            result.status = imgui_md.MarkdownDownloadStatus.ready
            # Clean up JS-side storage
            run_js(f"window._imgui_clear_download({repr(url)})")
        elif status == 'failed':
            error_msg = str(js_result.error) if hasattr(js_result, 'error') else "Unknown error"
            log.warning("Failed to download %s (Pyodide): %s", url, error_msg)
            result.status = imgui_md.MarkdownDownloadStatus.failed
            result.error_message = error_msg
            run_js(f"window._imgui_clear_download({repr(url)})")
        else:
            result.status = imgui_md.MarkdownDownloadStatus.downloading
    except Exception as e:
        log.warning("Failed to download %s (Pyodide): %s", url, e)
        result.status = imgui_md.MarkdownDownloadStatus.failed
        result.error_message = str(e)

    return result


def _get_download_function():
    """Return the appropriate download function for the current platform."""
    from imgui_bundle import __bundle_pyodide__
    if __bundle_pyodide__:
        return _download_pyodide_async
    else:
        return _download_desktop_async


def md_options_with_url_images():
    """Create MarkdownOptions with URL image download support enabled."""
    from imgui_bundle import imgui_md
    opts = imgui_md.MarkdownOptions()
    opts.callbacks.on_download_data = _get_download_function()
    return opts
