"""The API pages of the book (docs/book/api/), written from the Python stubs (bindings/imgui_bundle/**/*.pyi).

The stubs are litgen's: for each function, class, method, attribute and enum member, they carry the Python signature,
the docstring (the comment of the C++ header) and, as a comment above, the original C++ signature (the generators
set `original_signature_flag_show`). They also keep the headers' section comments (e.g. "Widgets: Main" and its
bullets, glued to the section's first function) and a marker per source header (`<generated_from:imgui.h>`).

This script reads them with `ast` and their source lines, and writes, for each library of LIBRARIES:
- `api/<lib>/index.md`: what the library does, its upstream, the book's page that presents it, the demos that use
  it (the same cards as the demos page), its modules;
- `api/<lib>/<module>.md`: the reference of a module: per source header, its sections (the headers' comments), and
  per entry the Python signature, the C++ signature, the doc;
and `api/index.md` (all the libraries), and the part of `_toc.yml` between `# <api pages>` and `# </api pages>`.
Run by `just api_pages` and by the doc recipes. The same design in three readers' minds: a Python user looks up a
name, a C++ user reads the C++ signature next to it, an AI assistant reads the whole page.
"""
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playground_examples_docs import EXAMPLES_DIR, demo_card  # noqa: E402  # the demos' cards, as on the demos page

REPO = Path(__file__).resolve().parent.parent
STUBS = REPO / "bindings/imgui_bundle"
BOOK = REPO / "docs/book"
API = BOOK / "api"
CPP_MARK = "/* original C++ signature */"
HEADER_MARK = re.compile(r"^#+\s*<generated_from:(.+?)>\s*#+$")
GENERATED = "% Written by ci_scripts/api_pages.py from the Python stubs: do not edit it by hand"


@dataclass
class Library:
    key: str  # the folder under api/
    title: str
    tagline: str  # one line: what it does
    upstream: str  # its repository
    book_page: str  # the book's page that presents it (relative to docs/book, without .md), or ""
    modules: list[tuple[str, str]]  # (the import name, the stub relative to bindings/imgui_bundle)
    uses: list[str] = field(default_factory=list)  # its names in examples_docs.json's "uses": the demos to show


LIBRARIES = [
    Library("imgui", "Dear ImGui", "The immediate mode GUI: windows, widgets, layouts, tables, the draw list, styles, IO.",
            "https://github.com/ocornut/imgui", "core_libs/imgui",
            [("imgui_bundle.imgui", "imgui/__init__.pyi"), ("imgui_bundle.imgui.internal", "imgui/internal.pyi"),
             ("imgui_bundle.imgui.test_engine", "imgui/test_engine.pyi"), ("imgui_bundle.imgui.backends", "imgui/backends.pyi")]),
    Library("hello_imgui", "Hello ImGui", "The app runner: the window and its backends, docking layouts, fonts, assets, DPI, idling.",
            "https://github.com/pthom/hello_imgui", "core_libs/hello_imgui_immapp",
            [("imgui_bundle.hello_imgui", "hello_imgui.pyi"), ("imgui_bundle.hello_imgui_nb", "hello_imgui_nb.pyi")]),
    Library("immapp", "ImmApp", "Runs an app in one call, with the add-ons set up (ImPlot, markdown, the node editor...); helpers for demos, tests and notebooks.",
            "https://github.com/pthom/imgui_bundle/tree/main/external/immapp", "core_libs/hello_imgui_immapp",
            [("imgui_bundle.immapp", "immapp/__init__.pyi"), ("imgui_bundle.immapp (C++ part)", "immapp/immapp_cpp.pyi"),
             ("imgui_bundle.immapp.nb", "immapp/nb.pyi")]),
    Library("implot", "ImPlot", "2D plots: lines, scatter, bars, heatmaps, histograms, pies, real-time data.",
            "https://github.com/epezent/implot", "addons/plotting",
            [("imgui_bundle.implot", "implot/__init__.pyi"), ("imgui_bundle.implot.internal", "implot/internal.pyi")], ["ImPlot"]),
    Library("implot3d", "ImPlot3D", "3D plots: lines, scatter, surfaces, meshes, with rotation and zoom.",
            "https://github.com/brenocq/implot3d", "addons/plotting",
            [("imgui_bundle.implot3d", "implot3d/__init__.pyi"), ("imgui_bundle.implot3d.internal", "implot3d/internal.pyi")], ["ImPlot3D"]),
    Library("immvision", "ImmVision", "Image display and inspection: zoom, pan, pixel values, colormaps, linked views (OpenCV images, numpy arrays).",
            "https://github.com/pthom/immvision", "addons/visualization", [("imgui_bundle.immvision", "immvision.pyi")], ["ImmVision"]),
    Library("imgui_node_editor", "ImGui Node Editor", "Node graphs: nodes, pins and links on a zoomable canvas.",
            "https://github.com/thedmd/imgui-node-editor", "addons/visualization",
            [("imgui_bundle.imgui_node_editor", "imgui_node_editor.pyi")], ["node editor"]),
    Library("imguizmo", "ImGuizmo", "3D gizmos to move, rotate and scale, and a view manipulator.",
            "https://github.com/CedricGuillemet/ImGuizmo", "addons/visualization", [("imgui_bundle.imguizmo", "imguizmo.pyi")], ["ImGuizmo"]),
    Library("nanovg", "NanoVG", "Antialiased 2D vector drawing: paths, gradients, text, images; in an ImGui window or a framebuffer.",
            "https://github.com/memononen/nanovg", "addons/visualization", [("imgui_bundle.nanovg", "nanovg.pyi")], ["NanoVG"]),
    Library("im_anim", "ImAnim", "Animation for Dear ImGui: tweens, easings, springs, timelines.",
            "https://github.com/soufianekhiat/ImAnim", "addons/tools", [("imgui_bundle.im_anim", "im_anim.pyi")], ["ImAnim"]),
    Library("imgui_color_text_edit", "ImGuiColorTextEdit", "A code editor widget: syntax highlighting, multiple cursors, a diff view, filters.",
            "https://github.com/goossens/ImGuiColorTextEdit", "addons/text_markdown",
            [("imgui_bundle.imgui_color_text_edit", "imgui_color_text_edit.pyi")], ["code editor"]),
    Library("rich_md", "Rich Markdown", "Markdown rendered in ImGui: text, tables, code, images, math, admonitions, transclusions.",
            "https://github.com/pthom/imgui_rich_md", "addons/text_markdown", [("imgui_bundle.rich_md", "rich_md.pyi")]),
    Library("imgui_microtex", "MicroTeX", "LaTeX formulas rendered in ImGui (the markdown's math uses it).",
            "https://github.com/NanoMichael/MicroTeX", "addons/text_markdown", [("imgui_bundle.imgui_microtex", "imgui_microtex.pyi")]),
    Library("imgui_knobs", "ImGui Knobs", "Rotary knobs, in several styles.",
            "https://github.com/altschuler/imgui-knobs", "addons/widgets", [("imgui_bundle.imgui_knobs", "imgui_knobs.pyi")], ["knobs"]),
    Library("imgui_toggle", "ImGui Toggle", "Toggle switches, with styles and animation.",
            "https://github.com/cmdwtf/imgui_toggle", "addons/widgets", [("imgui_bundle.imgui_toggle", "imgui_toggle.pyi")], ["toggles"]),
    Library("imspinner", "ImSpinner", "Loading spinners, dozens of them.",
            "https://github.com/dalerank/imspinner", "addons/widgets", [("imgui_bundle.imspinner", "imspinner.pyi")], ["spinners"]),
    Library("im_cool_bar", "ImCoolBar", "A dock-like bar whose icons magnify under the mouse.",
            "https://github.com/aiekick/ImCoolBar", "addons/widgets", [("imgui_bundle.im_cool_bar", "im_cool_bar.pyi")], ["cool bar"]),
    Library("imgui_command_palette", "ImGui Command Palette", "A command palette, as in Sublime Text or VS Code.",
            "https://github.com/hnOsmium0001/imgui-command-palette", "addons/widgets",
            [("imgui_bundle.imgui_command_palette", "imgui_command_palette.pyi")], ["command palette"]),
    Library("im_file_dialog", "ImFileDialog", "A file dialog drawn with ImGui.",
            "https://github.com/dfranx/ImFileDialog", "addons/widgets", [("imgui_bundle.im_file_dialog", "im_file_dialog.pyi")], ["file dialogs"]),
    Library("portable_file_dialogs", "Portable File Dialogs", "The native file dialogs, message boxes and notifications of each platform.",
            "https://github.com/samhocevar/portable-file-dialogs", "addons/widgets",
            [("imgui_bundle.portable_file_dialogs", "portable_file_dialogs.pyi")], ["file dialogs"]),
    Library("imgui_tex_inspect", "ImGui Tex Inspect", "A texture inspector: zoom into a texture, read its texels.",
            "https://github.com/andyborrell/imgui_tex_inspect", "addons/tools", [("imgui_bundle.imgui_tex_inspect", "imgui_tex_inspect.pyi")], ["Tex Inspect"]),
    Library("imgui_explorer", "Dear ImGui Explorer", "The interactive manuals of Dear ImGui, ImPlot, ImPlot3D and ImAnim, as a widget.",
            "https://github.com/pthom/imgui_explorer", "intro/interactive_manuals", [("imgui_bundle.imgui_explorer", "imgui_explorer.pyi")]),
    Library("webgl", "WebGL helpers", "WebGL from Python, in Pyodide.",
            "https://github.com/pthom/imgui_bundle", "python/python_pyodide", [("imgui_bundle.webgl", "webgl.pyi")], ["browser APIs"]),
]


# ---------------------------------------------------------------------------------------------------------------------
# Reading a stub
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Entry:
    kind: str  # function, method, class, enum, attribute, member
    name: str
    signature: str = ""  # Python: "def name(args) -> ret"
    cpp: str = ""  # the original C++ signature
    doc: str = ""  # the docstring
    note: str = ""  # a comment about it: trailing (attributes, members) or leading (functions without a section)
    value: str = ""  # an enum member's value
    section: Optional[tuple[str, list[str]]] = None  # a section of the header that starts here: its title, its lines
    header: str = ""  # the C++ header it comes from
    children: list["Entry"] = field(default_factory=list)
    overloads: list[tuple[str, str]] = field(default_factory=list)  # the other signatures (Python, C++) of an overload


def _clean_comment(line: str) -> str:
    return line.strip().lstrip("#").strip()


def _leading_comments(lines: list[str], first_line: int) -> list[str]:
    """The comment lines right above a line (1-based), in their order, without the stub's own markers"""
    block: list[str] = []
    i = first_line - 2
    while i >= 0 and lines[i].strip().startswith("#"):
        block.append(lines[i])
        i -= 1
    block.reverse()
    return [b for b in block if not re.match(r"^\s*#+\s*$", b) and "<litgen_stub>" not in b and "AUTOGENERATED" not in b
            and not HEADER_MARK.match(b.strip())]


def _split_comments(block: list[str]) -> tuple[str, list[str], list[str]]:
    """A leading block: the C++ signature (the last marked line), the lines before it, the lines after it"""
    cpp, before, after = "", [], []
    marked = [i for i, b in enumerate(block) if CPP_MARK in b]
    if marked:
        k = marked[-1]
        cpp = re.sub(r"\s+", " ", _clean_comment(block[k]).replace(CPP_MARK, "")).strip()
        before = [_clean_comment(b) for b in block[:k]]
        after = [_clean_comment(b) for b in block[k + 1:]]
    else:
        before = [_clean_comment(b) for b in block]
    return cpp, before, after


def _section_or_note(before: list[str]) -> tuple[Optional[tuple[str, list[str]]], str]:
    """The lines above a C++ signature: a section of the header (a title, then its lines) or a mere note"""
    if not before:
        return None, ""
    title = before[0]
    if title.startswith("-") or len(title) > 90 or title.endswith((".", ":")) and len(before) == 1 and len(title) > 50:
        return None, "\n".join(before)
    return (title, before[1:]), ""


def _trailing_comment(lines: list[str], node: ast.AST) -> str:
    """The comment at the end of a statement's lines (an attribute's or a member's)"""
    text = "\n".join(lines[node.lineno - 1:node.end_lineno])  # type: ignore[attr-defined]
    comments = re.findall(r"(?<!['\"])#(?!#)\s*(.+)$", text, re.M)
    return " ".join(c.strip() for c in comments if CPP_MARK not in c)


def _signature(node: ast.FunctionDef) -> str:
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    decorators = "".join(f"@{ast.unparse(d)}\n" for d in node.decorator_list)
    return f"{decorators}def {node.name}({args}){ret}"


def _first_line(node: ast.AST) -> int:
    decorators = getattr(node, "decorator_list", [])
    return int(decorators[0].lineno if decorators else node.lineno)  # type: ignore[attr-defined]


def _is_enum(node: ast.ClassDef) -> bool:
    return any("enum" in ast.unparse(b) for b in node.bases)


def read_stub(path: Path) -> list[Entry]:
    source = path.read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    headers: list[tuple[int, str]] = [(i + 1, m.group(1)) for i, line in enumerate(lines) if (m := HEADER_MARK.match(line.strip()))]
    entries: list[Entry] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        entry = _read_node(lines, node)
        if entry is None:
            continue
        entry.header = next((h for (ln, h) in reversed(headers) if ln < node.lineno), "")
        entries.append(entry)
    return _merge_overloads(entries)


def _merge_overloads(entries: list[Entry]) -> list[Entry]:
    """Consecutive functions of one name (Python overloads) become one entry with several signatures"""
    merged: list[Entry] = []
    for entry in entries:
        previous = merged[-1] if merged else None
        if previous is not None and entry.kind in ("function", "method") and entry.kind == previous.kind and entry.name == previous.name:
            previous.overloads.append((entry.signature, entry.cpp))
            if not previous.doc:
                previous.doc = entry.doc
            continue
        entry.children = _merge_overloads(entry.children) if entry.children else entry.children
        merged.append(entry)
    return merged


def _read_node(lines: list[str], node: ast.AST, in_class: bool = False) -> Optional[Entry]:
    if isinstance(node, ast.FunctionDef):
        if node.name.startswith("_") and node.name != "__init__":
            return None
        cpp, before, after = _split_comments(_leading_comments(lines, _first_line(node)))
        section, note = _section_or_note(before)
        entry = Entry("method" if in_class else "function", node.name, _signature(node), cpp, ast.get_docstring(node) or "",
                      "\n".join(x for x in [note, *after] if x), section=section)
        return entry
    if isinstance(node, ast.ClassDef):
        cpp, before, after = _split_comments(_leading_comments(lines, _first_line(node)))
        section, note = _section_or_note(before)
        entry = Entry("enum" if _is_enum(node) else "class", node.name, "", cpp, ast.get_docstring(node) or "",
                      "\n".join(x for x in [note, *after] if x), section=section)
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                sub = _read_node(lines, child, in_class=True)
                if sub is not None:
                    entry.children.append(sub)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                c_cpp, _, _ = _split_comments(_leading_comments(lines, child.lineno))
                entry.children.append(Entry("attribute", child.target.id, f"{child.target.id}: {ast.unparse(child.annotation)}",
                                            c_cpp, "", _trailing_comment(lines, child)))
            elif isinstance(child, ast.Assign) and entry.kind == "enum" and isinstance(child.targets[0], ast.Name):
                c_cpp, _, _ = _split_comments(_leading_comments(lines, child.lineno))
                trailing = _trailing_comment(lines, child)
                value = ""
                if (m := re.match(r"\(=\s*(.+?)\)\s*(.*)", trailing)):
                    value, trailing = m.group(1), m.group(2)
                entry.children.append(Entry("member", child.targets[0].id, "", c_cpp.rstrip(","), "", trailing, value))
        return entry
    return None


# ---------------------------------------------------------------------------------------------------------------------
# Writing the pages
# ---------------------------------------------------------------------------------------------------------------------
def _label(module: str, name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "-", f"{module}.{name}")


def _code(language: str, text: str) -> list[str]:
    return [f"```{language}", text, "```", ""]


def _doc_lines(text: str) -> list[str]:
    return [text, ""] if text else []


def _render_entry(entry: Entry, module: str, level: int, owner: str = "") -> list[str]:
    """An entry as markdown: a heading with a label, the signatures, the doc"""
    qualified = f"{owner}.{entry.name}" if owner else entry.name
    hashes = "#" * level
    out = [f"({_label(module, qualified)})=", f"{hashes} `{qualified}`", ""]  # a code span: __init__ is not emphasis
    if entry.kind in ("function", "method"):
        for python, cpp in [(entry.signature, entry.cpp), *entry.overloads]:
            out += _code("python", python)
            if cpp:
                out += _code("cpp", cpp)
        out += _doc_lines(entry.doc)
        if entry.note:
            out += [entry.note, ""]
    elif entry.kind == "enum":
        out[1] = f"{hashes} `{qualified}` (enum)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += _doc_lines(entry.doc)
        out += ["| Member | Value | C++ | |", "|---|---|---|---|"]
        for m in entry.children:
            out.append(f"| `{m.name}` | {m.value} | `{m.cpp}` | {m.note} |")
        out.append("")
    elif entry.kind == "class":
        out[1] = f"{hashes} `{qualified}` (class)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += _doc_lines(entry.doc)
        attributes = [c for c in entry.children if c.kind == "attribute"]
        if attributes:
            out += ["| Attribute | C++ | |", "|---|---|---|"]
            for a in attributes:
                out.append(f"| `{a.signature}` | `{a.cpp}` | {a.note} |")
            out.append("")
        for c in entry.children:
            if c.kind != "attribute":
                out += _render_entry(c, module, min(level + 1, 6), qualified)
    return out


def write_module_page(library: Library, module: str, stub: Path, page: Path) -> tuple[int, int]:
    """The reference of one module; returns its counts of functions and classes (enums included)"""
    entries = read_stub(stub)
    functions = sum(1 for e in entries if e.kind == "function")
    classes = sum(1 for e in entries if e.kind in ("class", "enum"))
    out = [GENERATED, "", f"# {module}", "",
           f"The Python API of [{library.title}](index.md), from `bindings/imgui_bundle/{stub.relative_to(STUBS).as_posix()}`: "
           f"{functions} functions, {classes} classes and enums. Each entry gives the Python signature, then the C++ one, "
           "then the doc of the C++ header. The sections are the header's.", ""]
    header = None
    for entry in entries:
        if entry.header != header:
            header = entry.header
            out += [f"## {header}", ""] if header else []
        if entry.section is not None:
            title, text = entry.section
            out += [f"### {title}", ""]
            if text:
                out += ["\n".join(text), ""]
        out += _render_entry(entry, module, 4)
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text("\n".join(out))
    return functions, classes


def _demo_cards(library: Library, manifest: dict[str, Any], docs: dict[str, dict[str, Any]], page: Path) -> list[str]:
    """The cards of the demos that use the library, as on the demos page (the pictures' paths made relative to here)"""
    if not library.uses:
        return []
    out: list[str] = []
    for e in manifest["examples"]:
        if e.get("hidden") or not e.get("launcher", True):
            continue
        if not set(docs.get(e["filename"], {}).get("uses", [])) & set(library.uses):
            continue
        card = demo_card(manifest, docs, e, in_grid=True)
        for i, line in enumerate(card):  # demo_card writes the pictures' paths relative to the demos page
            if line.startswith(":::{image} "):
                picture = (BOOK / "intro" / line[len(":::{image} "):]).resolve()
                card[i] = ":::{image} " + os.path.relpath(picture, page.parent)
        out += ["::::{card}", *card, "::::", ""]
    if not out:
        return []
    return ["## Demos using it", "", "The demos of the catalog that use the library (the pictures link to their code and to the playground).", "",
            ":::::{grid} 1 2 3 3", "", *out, ":::::", ""]


def write_library_pages(library: Library, manifest: dict[str, Any], docs: dict[str, dict[str, Any]]) -> list[str]:
    """The intro page and the module pages of a library; returns the TOC lines"""
    folder = API / library.key
    folder.mkdir(parents=True, exist_ok=True)
    modules = []
    for module, stub in library.modules:
        stub_path = STUBS / stub
        if not stub_path.is_file():
            print(f"warning: {stub_path} not found")
            continue
        stem = re.sub(r"[^a-z0-9_]+", "_", module.removeprefix("imgui_bundle.").lower()).strip("_") or "module"
        page = folder / f"{stem}.md"
        functions, classes = write_module_page(library, module, stub_path, page)
        modules.append((module, page, functions, classes))
    index = folder / "index.md"
    out = [GENERATED, "", f"# {library.title}", "", library.tagline, ""]
    links = [f"[Upstream repository]({library.upstream})"]
    if library.book_page:
        links.append(f"[The book's page]({os.path.relpath(BOOK / (library.book_page + '.md'), folder)})")
    out += [" · ".join(links), ""]
    out += ["## Modules", ""]
    for module, page, functions, classes in modules:
        out.append(f"- [`{module}`]({page.name}): {functions} functions, {classes} classes and enums")
    out.append("")
    out += _demo_cards(library, manifest, docs, index)
    index.write_text("\n".join(out))
    toc = [f"      - file: api/{library.key}/index", "        sections:"]
    toc += [f"          - file: api/{library.key}/{page.stem}" for _, page, _, _ in modules]
    return toc


def write_index() -> None:
    out = [GENERATED, "", "# API reference", "",
           "The libraries of Dear ImGui Bundle, as Python modules, with the C++ signature next to each Python one: "
           "the bindings are generated from the C++ headers, and their names follow them (`ImGui::Button` is "
           "`imgui.button`, `ImPlotFlags_` is `implot.Flags_`). These pages come from the Python stubs (`.pyi`), "
           "which keep the headers' comments. To learn, start with the [demos](../intro/demos.md); to look up a name, "
           "use these pages, or the stubs in your editor.", "",
           "| Library | What it does | Modules |", "|---|---|---|"]
    for library in LIBRARIES:
        modules = ", ".join(f"`{m}`" for m, _ in library.modules)
        out.append(f"| [{library.title}]({library.key}/index.md) | {library.tagline} | {modules} |")
    out.append("")
    (API / "index.md").write_text("\n".join(out))


def write_toc(toc_lines: list[str]) -> None:
    path = BOOK / "_toc.yml"
    text = path.read_text()
    start, end = "      # <api pages>", "      # </api pages>"
    i, j = text.index(start), text.index(end)
    i = text.index("\n", i) + 1
    new = "\n".join(["      - file: api/index", *toc_lines]) + "\n"
    path.write_text(text[:i] + new + text[j:])


def main() -> None:
    manifest = json.loads((EXAMPLES_DIR / "examples.json").read_text())
    docs = json.loads((EXAMPLES_DIR / "examples_docs.json").read_text())
    API.mkdir(exist_ok=True)
    toc: list[str] = []
    for library in LIBRARIES:
        toc += write_library_pages(library, manifest, docs)
    write_index()
    write_toc(toc)
    pages = sorted(API.rglob("*.md"))
    print(f"wrote {len(pages)} pages in {API} ({sum(p.stat().st_size for p in pages) // 1024} KB)")


if __name__ == "__main__":
    main()
