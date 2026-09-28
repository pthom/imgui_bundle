# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle

"""The lists of links written by hand use the addresses of the resources list.

The resources list is bindings/imgui_bundle/demos_assets/resources.md: the book's Resources page includes it, and the
explorer's intro transcludes its "Start here" section. A few short lists stay written by hand (the intro's row of
links, the playground's landing page, the Readme): each of their links must be in the list, with the same address.
Run with: pytest tests/test_resources_links.py
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RESOURCES = REPO / "bindings/imgui_bundle/demos_assets/resources.md"
URL = re.compile(r"https?://[^\s)\"'<>\]]+")
IMAGE = (".png", ".gif", ".svg", ".jpg")

# The hand-written lists: (file, the text that starts the list, the text that ends it)
HAND_WRITTEN = [
    ("bindings/imgui_bundle/demos_python/demo_imgui_bundle_intro.py", "def _render_links_row", "for i, (label"),
    ("bindings/imgui_bundle/demos_cpp/demo_imgui_bundle_intro.cpp", "void RenderLinksRow()", "for (int i = 0"),
    ("bindings/imgui_bundle/demos_python/playground/examples/landing_page.py", "## See also", '"""'),
    ("Readme.md", "", "### Build status"),  # tracked as Readme.md: the exact case matters on Linux
]


def addresses(text: str) -> set[str]:
    return {u.rstrip("/.,") for u in URL.findall(text) if not u.lower().endswith(IMAGE)}


def test_resources_list_has_the_transcluded_section() -> None:
    assert "\n## Start here\n" in "\n" + RESOURCES.read_text(), "the explorer's intro transcludes this section"


@pytest.mark.parametrize("path, start, end", HAND_WRITTEN, ids=[h[0].split("/")[-1] for h in HAND_WRITTEN])
def test_hand_written_links_are_in_the_resources_list(path: str, start: str, end: str) -> None:
    text = (REPO / path).read_text()
    begin = text.index(start)  # a ValueError here: the list moved; update HAND_WRITTEN
    links = text[begin:text.index(end, begin + len(start))]
    known = addresses(RESOURCES.read_text())
    unknown = sorted(addresses(links) - known)
    assert addresses(links), f"no link found in the list of {path}"
    assert not unknown, f"{path}: addresses missing from {RESOURCES.name} (or different there): {unknown}"
