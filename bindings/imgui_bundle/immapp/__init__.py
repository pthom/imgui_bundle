# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
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


def run_nb(*args, **kwargs):
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
    from imgui_bundle import imgui, imgui_md, hello_imgui
    tweaked_theme = hello_imgui.ImGuiTweakedTheme()
    tweaked_theme.theme = hello_imgui.ImGuiTheme_.gray_variations
    tweaked_theme.tweaks.rounding = 0.0
    hello_imgui.push_tweaked_theme(tweaked_theme)
    size = hello_imgui.em_to_vec2(0, height_em)
    # Note: with ResizeY, ImGui uses the size only on the very first frame
    # (it saves/restores the resized height in the ini file after that)
    imgui.begin_child("##doc", size,
                      imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_y)
    imgui_md.render_unindented(doc)
    imgui.end_child()
    imgui.new_line()
    hello_imgui.pop_tweaked_theme()

__all__.append("render_markdown_doc_panel")


def download_url_bytes(url: str) -> bytes:
    """Download data from a URL. Works on both desktop (urllib) and Pyodide (sync XMLHttpRequest).
    Returns the downloaded bytes, or empty bytes on failure.

    Args:
        url: the URL to download from
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
        import urllib.request
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "imgui_bundle/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read()
        except Exception as e:
            import logging
            logging.getLogger("immapp").warning("Failed to download %s: %s", url, e)
            return b""

__all__.append("download_url_bytes")
