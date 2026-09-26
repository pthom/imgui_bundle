"""rich_md.resolve_transclusions: the narrative programming cases of imgui_rich_md, run through the Python binding.
Each case folder holds source files, a doc.md with transclusions, and expected.md (see the library's tests/narrative)."""
from pathlib import Path

import pytest
import imgui_bundle

# Skip the whole module if imgui_bundle was built without rich_md (e.g. the minimal wheels)
pytestmark = pytest.mark.skipif(
    not imgui_bundle.has_submodule("rich_md"),
    reason="rich_md submodule not available in this build",
)
if imgui_bundle.has_submodule("rich_md"):
    from imgui_bundle import rich_md

CASES_DIR = Path(__file__).parent.parent / "external/imgui_rich_md/imgui_rich_md/tests/narrative/cases"
CASES = sorted(p for p in CASES_DIR.iterdir() if p.is_dir())


@pytest.mark.parametrize("case", CASES, ids=[c.name for c in CASES])
def test_case(case: Path) -> None:
    def read(path: str) -> str | None:
        file = case / path
        return file.read_text() if file.is_file() else None

    actual = rich_md.resolve_transclusions((case / "doc.md").read_text(), read, "doc.md")
    assert actual == (case / "expected.md").read_text()


def test_text_without_transclusion_is_unchanged() -> None:
    assert rich_md.resolve_transclusions("# Title\n\nplain text", lambda path: None) == "# Title\n\nplain text"
