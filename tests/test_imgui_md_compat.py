# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle

"""imgui_md, the former name of the markdown module, keeps working for the code written before rich_md.

The names below are the public API of imgui_md.pyi in v1.92.900, the last release before the rename to rich_md
(`git show v1.92.900:bindings/imgui_bundle/imgui_md.pyi`). No GUI context is needed.
Run with: pytest tests/test_imgui_md_compat.py
"""

import ast
from pathlib import Path

import pytest
import imgui_bundle

pytestmark = pytest.mark.skipif(
    not imgui_bundle.has_submodule("rich_md"),
    reason="rich_md submodule not available in this build",
)

# The module's functions and classes in v1.92.900, with the members of each class
V1_92_900_API: dict[str, list[str]] = {
    "MarkdownFontOptions": ["font_base_path", "header_size_factors", "regular_size"],
    "MarkdownImage": ["col_border", "col_tint", "size", "texture_id", "uv0", "uv1"],
    "SizedFont": ["font", "size"],
    "MarkdownDownloadStatus": ["downloading", "failed", "not_started", "ready"],
    "MarkdownDownloadResult": ["error_message", "fill_from_bytes", "status"],
    "MarkdownCallbacks": ["on_download_data", "on_html_div", "on_html_span", "on_image", "on_open_link"],
    "MarkdownOptions": ["autolinks", "callbacks", "font_options", "with_latex"],
    "MarkdownFontSpec": ["bold", "header_level", "italic"],
    "on_image_default": [],
    "on_open_link_default": [],
    "initialize_markdown": [],
    "de_initialize_markdown": [],
    "get_font_loader_function": [],
    "render": [],
    "render_unindented": [],
    "get_code_font": [],
    "get_font": [],
    "link_color": [],
    "render_text_as_link": [],
}

# Type aliases of the v1.92.900 stub: they exist only for type checkers, in the stub
V1_92_900_STUB_ALIASES = [
    "VoidFunction",
    "StringFunction",
    "HtmlDivFunction",
    "HtmlSpanFunction",
    "MarkdownImageFunction",
    "MarkdownDownloadFunction",
]


def test_imgui_md_is_rich_md() -> None:
    from imgui_bundle import imgui_md, rich_md
    import imgui_bundle.imgui_md as imgui_md_module

    assert imgui_md is rich_md
    assert imgui_md_module is rich_md


def test_v1_92_900_api_still_exists() -> None:
    from imgui_bundle import imgui_md

    missing = []
    for name, members in V1_92_900_API.items():
        if not hasattr(imgui_md, name):
            missing.append(name)
            continue
        missing += [f"{name}.{m}" for m in members if not hasattr(getattr(imgui_md, name), m)]
    assert not missing, f"names of imgui_md (v1.92.900) missing now: {missing}"


def test_v1_92_900_stub_aliases_still_exist() -> None:
    """imgui_md.pyi re-exports rich_md.pyi (`from imgui_bundle.rich_md import *`): the aliases must be there"""
    stubs = Path(imgui_bundle.__file__).parent
    assert "from imgui_bundle.rich_md import *" in (stubs / "imgui_md.pyi").read_text()
    tree = ast.parse((stubs / "rich_md.pyi").read_text())
    defined = {t.id for node in tree.body if isinstance(node, ast.Assign) for t in node.targets if isinstance(t, ast.Name)}
    missing = [a for a in V1_92_900_STUB_ALIASES if a not in defined]
    assert not missing, f"type aliases of imgui_md.pyi (v1.92.900) missing now: {missing}"
