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
from typing import Dict

# Enable logging with:
#    logging.getLogger("imgui_md_image_loader").setLevel(logging.DEBUG)
log = logging.getLogger("imgui_md_image_loader")

# Artificial delay for testing async downloads (set to 0 for production)
_DEBUG_DELAY_SECONDS = 0.0

# Background thread pool for async downloads (desktop only)
_executor = ThreadPoolExecutor(max_workers=2)
_pending: Dict[str, Future] = {}


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
            data = resp.read()
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


def _download_pyodide(url: str):
    """Synchronous download using XMLHttpRequest in Pyodide.
    Returns a MarkdownDownloadResult with status Ready or Failed."""
    from imgui_bundle import imgui_md
    log.debug("Downloading %s (Pyodide)", url)
    result = imgui_md.MarkdownDownloadResult()
    try:
        from pyodide.code import run_js  # type: ignore
        js_code = """
        (function(url) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, false);
            xhr.responseType = 'arraybuffer';
            xhr.send();
            if (xhr.status === 200) {
                return new Uint8Array(xhr.response);
            } else {
                return null;
            }
        })
        """
        fetch_fn = run_js(js_code)
        js_result = fetch_fn(url)
        if js_result is not None and len(js_result) > 0:
            log.debug("Downloaded %d bytes from %s", len(js_result), url)
            result.fill_from_bytes(bytes(js_result))
            result.status = imgui_md.MarkdownDownloadStatus.ready
        else:
            log.warning("Failed to download %s (HTTP error or CORS blocked)", url)
            result.status = imgui_md.MarkdownDownloadStatus.failed
            result.error_message = "Download failed (HTTP error or CORS blocked)"
    except Exception as e:
        log.warning("Failed to download %s: %s", url, e)
        result.status = imgui_md.MarkdownDownloadStatus.failed
        result.error_message = str(e)
    return result


def _get_download_function():
    """Return the appropriate download function for the current platform."""
    from imgui_bundle import __bundle_pyodide__
    if __bundle_pyodide__:
        return _download_pyodide
    else:
        return _download_desktop_async


def md_options_with_url_images():
    """Create MarkdownOptions with URL image download support enabled."""
    from imgui_bundle import imgui_md
    opts = imgui_md.MarkdownOptions()
    opts.callbacks.on_download_data = _get_download_function()
    return opts
