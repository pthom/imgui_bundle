"""ImGuiMd::ResolveImports: sections of a source file imported into a markdown document."""
from imgui_bundle import imgui_md

HEART_CPP = '''// Part of a demo - license header
#include "imgui.h"

// @@md#Intro
// # A beating heart
// The curve first:
// @import {md_id=HeartPoints}
// Then the drawing:
// @import {md_id=Drawing, part=code}
// @@/md

// @@md#HeartPoints
// The heart is a parametric curve: $r(t) = 1 + a \\sin(\\omega t)$.
// @@/md
std::vector<ImVec2> HeartPoints(int n)
{
    return {};
}

// @@md#Drawing
// ImPlot draws the polygon.
//
//     indented code in the prose stays indented
// @@/md
void Gui()
{
    Draw();
}
'''

NOTES_MD = "A note.\n\n@import \"heart.cpp\" {md_id=Drawing, part=prose}\n"

INDENTED_PY = "class A:\n    # @@md#Method\n    # A method.\n    # @@/md\n    def m(self):\n        pass\n"

FILES = {"heart.cpp": HEART_CPP, "indented.py": INDENTED_PY, "notes.md": NOTES_MD, "lessons/heart.cpp": HEART_CPP, "lessons/index.md": "@import \"heart.cpp\" {md_id=HeartPoints, part=prose}\n"}


def read(path: str) -> str | None:
    return FILES.get(path)


def resolve(text: str, current_file: str = "") -> str:
    return imgui_md.resolve_imports(text, read, current_file)


def test_no_directive_is_identity() -> None:
    assert resolve("# Title\n\nplain text") == "# Title\n\nplain text"


def test_section_prose_then_code() -> None:
    out = resolve('@import "heart.cpp" {md_id=HeartPoints}\n')
    assert out == (
        "The heart is a parametric curve: $r(t) = 1 + a \\sin(\\omega t)$.\n\n"
        "```cpp\nstd::vector<ImVec2> HeartPoints(int n)\n{\n    return {};\n}\n```\n\n"
    )


def test_part_and_dedent() -> None:
    prose = resolve('@import "heart.cpp" {md_id=Drawing, part=prose}\n')
    assert prose == "ImPlot draws the polygon.\n\n    indented code in the prose stays indented\n\n"
    code = resolve('@import "heart.cpp" {md_id=Drawing, part=code}\n')
    assert code == "```cpp\nvoid Gui()\n{\n    Draw();\n}\n```\n\n"
    method = resolve('@import "indented.py" {md_id=Method, part=code}\n')
    assert method == "```python\ndef m(self):\n    pass\n```\n\n"
    kept = resolve('@import "indented.py" {md_id=Method, part=code, dedent=false}\n')
    assert kept.startswith("```python\n    def m(self):\n")


def test_whole_file_in_order_skips_the_header() -> None:
    out = resolve('@import "heart.cpp"\n')
    assert "license header" not in out and "#include" not in out
    assert out.index("A beating heart") < out.index("parametric curve") < out.index("ImPlot draws")


def test_self_narrating_file() -> None:
    out = resolve('@import "heart.cpp" {md_id=Intro}\n')
    assert out.startswith("# A beating heart\nThe curve first:\n\nThe heart is a parametric curve")
    assert "```cpp\nstd::vector<ImVec2> HeartPoints" in out
    assert "Then the drawing:\n\n```cpp\nvoid Gui()" in out
    assert "@import" not in out


def test_markdown_file_and_relative_paths() -> None:
    out = resolve('@import "notes.md"\n')
    assert out == "A note.\n\nImPlot draws the polygon.\n\n    indented code in the prose stays indented\n\n"
    nested = resolve('@import "lessons/index.md"\n')
    assert nested.startswith("The heart is a parametric curve")


def test_errors_are_spans_with_a_reason() -> None:
    def err(text: str) -> str:
        out = resolve(text)
        assert out.startswith("<md-error title=\"") and out.endswith("</md-error>\n"), out
        return out
    assert "file not found: nope.cpp" in err('@import "nope.cpp"\n')
    assert "no block 'Zzz' in heart.cpp" in err('@import "heart.cpp" {md_id=Zzz}\n')
    assert "unknown attribute: foo" in err('@import "heart.cpp" {foo=1}\n')
    assert "no file given" in err('@import {md_id=Intro}\n')
    FILES["open.cpp"] = "// @@md#A\n// never closed\nint x;\n"
    assert "not closed" in err('@import "open.cpp" {md_id=A}\n')
    FILES["cycle.cpp"] = "// @@md#A\n// @import {md_id=B}\n// @@/md\n// @@md#B\n// @import {md_id=A}\n// @@/md\n"
    assert "import cycle" in resolve('@import "cycle.cpp" {md_id=A}\n')
