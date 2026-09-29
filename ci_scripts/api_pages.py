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
AMALGAMATION_MARK = re.compile(r"^#\s+(\S+\.h) included by \S+\s*//$")  # hello_imgui's amalgamation
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
    demos: list[str] = field(default_factory=list)  # the demos to show, by file name: for the core libraries, whose
    # use is not tagged (every demo imports them)
    headers: str = ""  # the folder of the C++ headers, when the stub comes from an amalgamation: the entries are then
    # classified by the header that declares them (the amalgamation's markers only mark the include points)
    comments: str = "markdown"  # how the comments render: "markdown", or "pre" for a header laid out in ASCII (imgui.h:
    # aligned columns, one idea per line): a multi-line comment is then a preformatted block, a one-liner a paragraph


LIBRARIES = [
    Library("imgui", "Dear ImGui",
            "The immediate mode GUI: windows, widgets, layouts, tables, the draw list, styles, IO.",
            "https://github.com/ocornut/imgui", "core_libs/imgui",
            [("imgui_bundle.imgui", "imgui/__init__.pyi"), ("imgui_bundle.imgui.internal", "imgui/internal.pyi"),
             ("imgui_bundle.imgui.test_engine", "imgui/test_engine.pyi"),
             ("imgui_bundle.imgui.backends", "imgui/backends.pyi")],
            demos=["demo_widgets.py", "layout_child.py", "demo_drag_and_drop.py", "manual_imgui.py",
                   "demo_hello_world.py"]),
    Library("hello_imgui", "Hello ImGui",
            "The app runner: the window and its backends, docking layouts, fonts, assets, DPI, idling.",
            "https://github.com/pthom/hello_imgui", "core_libs/hello_imgui_immapp",
            [("imgui_bundle.hello_imgui", "hello_imgui.pyi"), ("imgui_bundle.hello_imgui_nb", "hello_imgui_nb.pyi")],
            headers="external/hello_imgui/hello_imgui/src/hello_imgui",
            demos=["demo_docking.py", "layout_docking.py", "demo_powersave.py", "demo_chinese_font.py",
                   "demo_assets_addons.py", "demo_custom_background.py", "themes.py", "demo_logger.py",
                   "demo_testengine.py", "demo_command_palette.py", "demo_run_async.py"]),
    Library("immapp", "ImmApp",
            "Runs an app in one call, with the add-ons set up (ImPlot, markdown, the node editor...); helpers for "
            "demos, tests and notebooks.",
            "https://github.com/pthom/imgui_bundle/tree/main/external/immapp", "core_libs/hello_imgui_immapp",
            [("imgui_bundle.immapp", "immapp/__init__.pyi"),
             ("imgui_bundle.immapp.immapp_cpp", "immapp/immapp_cpp.pyi"), ("imgui_bundle.immapp.nb", "immapp/nb.pyi")],
            demos=["demo_hello_world.py", "welcome_imm_mode.py", "demo_parametric_curve.py", "demo_assets_addons.py",
                   "demo_python_context_manager.py", "demo_run_async.py", "demo_widgets.py", "demo_testapp.py"]),
    Library("implot", "ImPlot",
            "2D plots: lines, scatter, bars, heatmaps, histograms, pies, real-time data.",
            "https://github.com/epezent/implot", "addons/plotting",
            [("imgui_bundle.implot", "implot/__init__.pyi"), ("imgui_bundle.implot.internal", "implot/internal.pyi")],
            uses=["ImPlot"]),
    Library("implot3d", "ImPlot3D",
            "3D plots: lines, scatter, surfaces, meshes, with rotation and zoom.",
            "https://github.com/brenocq/implot3d", "addons/plotting",
            [("imgui_bundle.implot3d", "implot3d/__init__.pyi"),
             ("imgui_bundle.implot3d.internal", "implot3d/internal.pyi")],
            uses=["ImPlot3D"]),
    Library("immvision", "ImmVision",
            "Image display and inspection: zoom, pan, pixel values, colormaps, linked views (OpenCV images, numpy "
            "arrays).",
            "https://github.com/pthom/immvision", "addons/visualization",
            [("imgui_bundle.immvision", "immvision.pyi")],
            uses=["ImmVision"]),
    Library("imgui_node_editor", "ImGui Node Editor",
            "Node graphs: nodes, pins and links on a zoomable canvas.",
            "https://github.com/thedmd/imgui-node-editor", "addons/visualization",
            [("imgui_bundle.imgui_node_editor", "imgui_node_editor.pyi")],
            uses=["node editor"]),
    Library("imguizmo", "ImGuizmo",
            "3D gizmos to move, rotate and scale, and a view manipulator.",
            "https://github.com/CedricGuillemet/ImGuizmo", "addons/visualization",
            [("imgui_bundle.imguizmo", "imguizmo.pyi")],
            uses=["ImGuizmo"]),
    Library("nanovg", "NanoVG",
            "Antialiased 2D vector drawing: paths, gradients, text, images; in an ImGui window or a framebuffer.",
            "https://github.com/memononen/nanovg", "addons/visualization",
            [("imgui_bundle.nanovg", "nanovg.pyi")],
            uses=["NanoVG"]),
    Library("im_anim", "ImAnim",
            "Animation for Dear ImGui: tweens, easings, springs, timelines.",
            "https://github.com/soufianekhiat/ImAnim", "addons/tools",
            [("imgui_bundle.im_anim", "im_anim.pyi")],
            uses=["ImAnim"]),
    Library("imgui_color_text_edit", "ImGuiColorTextEdit",
            "A code editor widget: syntax highlighting, multiple cursors, a diff view, filters.",
            "https://github.com/goossens/ImGuiColorTextEdit", "addons/text_markdown",
            [("imgui_bundle.imgui_color_text_edit", "imgui_color_text_edit.pyi")],
            uses=["code editor"]),
    Library("rich_md", "Rich Markdown",
            "Markdown rendered in ImGui: text, tables, code, images, math, admonitions, transclusions.",
            "https://github.com/pthom/imgui_rich_md", "addons/text_markdown",
            [("imgui_bundle.rich_md", "rich_md.pyi")],
            demos=["demo_imgui_md.py", "demo_implot_markdown.py", "demo_assets_addons.py", "demo_widgets.py"]),
    Library("imgui_microtex", "MicroTeX",
            "LaTeX formulas rendered in ImGui (the markdown's math uses it).",
            "https://github.com/NanoMichael/MicroTeX", "addons/text_markdown",
            [("imgui_bundle.imgui_microtex", "imgui_microtex.pyi")]),
    Library("imgui_knobs", "ImGui Knobs",
            "Rotary knobs, in several styles.",
            "https://github.com/altschuler/imgui-knobs", "addons/widgets",
            [("imgui_bundle.imgui_knobs", "imgui_knobs.pyi")],
            uses=["knobs"]),
    Library("imgui_toggle", "ImGui Toggle",
            "Toggle switches, with styles and animation.",
            "https://github.com/cmdwtf/imgui_toggle", "addons/widgets",
            [("imgui_bundle.imgui_toggle", "imgui_toggle.pyi")],
            uses=["toggles"]),
    Library("imspinner", "ImSpinner",
            "Loading spinners, dozens of them.",
            "https://github.com/dalerank/imspinner", "addons/widgets",
            [("imgui_bundle.imspinner", "imspinner.pyi")],
            uses=["spinners"]),
    Library("im_cool_bar", "ImCoolBar",
            "A dock-like bar whose icons magnify under the mouse.",
            "https://github.com/aiekick/ImCoolBar", "addons/widgets",
            [("imgui_bundle.im_cool_bar", "im_cool_bar.pyi")],
            uses=["cool bar"]),
    Library("imgui_command_palette", "ImGui Command Palette",
            "A command palette, as in Sublime Text or VS Code.",
            "https://github.com/hnOsmium0001/imgui-command-palette", "addons/widgets",
            [("imgui_bundle.imgui_command_palette", "imgui_command_palette.pyi")],
            uses=["command palette"]),
    Library("im_file_dialog", "ImFileDialog",
            "A file dialog drawn with ImGui.",
            "https://github.com/dfranx/ImFileDialog", "addons/widgets",
            [("imgui_bundle.im_file_dialog", "im_file_dialog.pyi")],
            uses=["file dialogs"]),
    Library("portable_file_dialogs", "Portable File Dialogs",
            "The native file dialogs, message boxes and notifications of each platform.",
            "https://github.com/samhocevar/portable-file-dialogs", "addons/widgets",
            [("imgui_bundle.portable_file_dialogs", "portable_file_dialogs.pyi")],
            uses=["file dialogs"]),
    Library("imgui_tex_inspect", "ImGui Tex Inspect",
            "A texture inspector: zoom into a texture, read its texels.",
            "https://github.com/andyborrell/imgui_tex_inspect", "addons/tools",
            [("imgui_bundle.imgui_tex_inspect", "imgui_tex_inspect.pyi")],
            uses=["Tex Inspect"]),
    Library("imgui_explorer", "Dear ImGui Explorer",
            "The interactive manuals of Dear ImGui, ImPlot, ImPlot3D and ImAnim, as a widget.",
            "https://github.com/pthom/imgui_explorer", "intro/interactive_manuals",
            [("imgui_bundle.imgui_explorer", "imgui_explorer.pyi")],
            demos=["manual_imgui.py", "manual_implot.py", "manual_implot3d.py", "manual_im_anim.py"]),
    Library("webgl", "WebGL helpers",
            "WebGL from Python, in Pyodide.",
            "https://github.com/pthom/imgui_bundle", "python/python_pyodide",
            [("imgui_bundle.webgl", "webgl.pyi")],
            uses=["browser APIs"]),
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
    part: Optional[str] = None  # a part of the header that starts here: a [SECTION] mark (imgui, implot); the parts
    # hold the sections
    header: str = ""  # the C++ header it comes from
    children: list["Entry"] = field(default_factory=list)
    overloads: list[tuple[str, str]] = field(default_factory=list)  # the other signatures (Python, C++) of an overload
    generated: bool = True  # written by litgen (between its markers), as opposed to the stub's hand-written parts


def _clean_comment(line: str) -> str:
    """The text of a stub's comment line, keeping its indentation (a code example in a comment)"""
    return re.sub(r"^\s*#\s?", "", line).rstrip()


def _is_stop_block(block: list[str]) -> bool:
    """A comment block that belongs to no entry: a table of contents (several [SECTION] lines), a license, the
    stub's own header"""
    text = "\n".join(block)
    return (len(re.findall(r"^#\s*(//\s*)?\[SECTION\]", text, re.M)) > 1 or "Permission is hereby granted" in text
            or "<litgen_stub>" in text or "AUTOGENERATED" in text or "<generated_from:" in text)


def _leading_comments(lines: list[str], first_line: int) -> list[str]:
    """The comment lines above a line (1-based), in their order: the block glued to it, and the blocks above
    separated by one blank line (a header's section comment, and the prose before its first bound entry), up to a
    block that belongs to no entry"""
    blocks: list[list[str]] = [[]]
    i = first_line - 2
    while i >= 0:
        if lines[i].strip().startswith("#"):
            blocks[-1].append(lines[i])
        elif not lines[i].strip() and i >= 1 and lines[i - 1].strip().startswith("#"):
            blocks.append([])  # a blank line, and a comment block above it
        else:
            break
        i -= 1
    kept: list[str] = []
    for block in blocks:
        block.reverse()
        if _is_stop_block(block):
            break
        kept = block + kept
    return [b for b in kept if not re.match(r"^\s*#+\s*$", b) and not HEADER_MARK.match(b.strip())
            and not AMALGAMATION_MARK.match(b)]


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


def _part_title(line: str) -> str:
    """The title of a part: without its [SECTION] mark, and without the list of its structs in parentheses"""
    return re.sub(r"\s*\([^)]*\)$", "", line.strip().removeprefix("[SECTION]").strip())


def _section_or_note(before: list[str]) -> tuple[Optional[str], Optional[tuple[str, list[str]]], str]:
    """The lines above a C++ signature: a part of the header (a [SECTION] mark), a section (a title, then its lines),
    or a mere note. Not a section: a sentence, a bullet, a marker of the bundle's patches ([ADAPT_IMGUI_BUNDLE]),
    a preprocessor line"""
    is_rule = [bool(re.match(r"^[/=-]{4,}$", b)) for b in before]
    before = [b for i, b in enumerate(before) if not (is_rule[i] and i > 0 and is_rule[i - 1])]  # one rule per run
    is_rule = [bool(re.match(r"^[/=-]{4,}$", b)) for b in before]
    if len(before) >= 3 and is_rule[0] and is_rule[2] and _is_title(before[1]):  # a banner: a part (the node editor's)
        nearer, section, note = _section_or_note(before[3:])
        return nearer or _part_title(before[1]), section, note
    preprocessor = r"^(#\s*(if|else)|#?\s*(ifdef|ifndef|elif|endif|define|include|pragma))\b"
    before = [b for b in before if not re.match(preprocessor, b)
              and not re.match(r"^[/=-]{4,}$", b) and not b.startswith("[ADAPT_") and not b.startswith("</")]
    if not before:
        return None, None, ""
    title = before[0]
    if (m := re.match(r"^-{3,}\s*(.+?)\s*-{3,}$", title)):  # `--- Title ---`: the node editor's sections
        title = m.group(1)
    if title.startswith("[SECTION]"):  # imgui's and implot's marks: a part
        nearer, section, note = _section_or_note(before[1:])  # a part without bound entries: the next one counts
        return nearer or _part_title(title), section, note
    if (m := re.match(r"^<submodule (\w+)>$", title)):  # litgen's marker of a nested namespace
        title = f"Submodule {m.group(1)}"
    if not _is_title(title):
        return None, None, "\n".join(before)
    return None, (title, before[1:]), ""


def _is_title(title: str) -> bool:
    """A comment line that can title a section: not a sentence, a marker, a line of code"""
    title = title.strip()
    return not (title.startswith(("-", "<", "[/")) or len(title) > 60 or title.endswith((".", ",", ";", ":"))
                or re.search(r'[;"]', title) or ("," in title and ":" not in title and len(title.split()) > 3))


def _trailing_comment(lines: list[str], node: ast.AST) -> str:
    """The comment at the end of a statement's lines (an attribute's or a member's)"""
    text = "\n".join(lines[node.lineno - 1:node.end_lineno])  # type: ignore[attr-defined]
    comments = re.findall(r"(?<!['\"])#(?!#)\s*(.+)$", text, re.M)
    return " ".join(c.strip() for c in comments if CPP_MARK not in c)


def _parameter(arg: ast.arg, default: Optional[ast.expr]) -> str:
    text = arg.arg + (f": {ast.unparse(arg.annotation)}" if arg.annotation else "")
    if default is not None:
        text += (" = " if arg.annotation else "=") + ast.unparse(default)
    return text


def _parameters(a: ast.arguments) -> str:
    """As ast.unparse, with black's spaces around the `=` of an annotated parameter's default"""
    positional = a.posonlyargs + a.args
    defaults: list[Optional[ast.expr]] = [None] * (len(positional) - len(a.defaults)) + list(a.defaults)
    parts = [_parameter(arg, default) for arg, default in zip(positional, defaults)]
    if a.posonlyargs:
        parts.insert(len(a.posonlyargs), "/")
    if a.vararg:
        parts.append("*" + _parameter(a.vararg, None))
    elif a.kwonlyargs:
        parts.append("*")
    parts += [_parameter(arg, default) for arg, default in zip(a.kwonlyargs, a.kw_defaults)]
    if a.kwarg:
        parts.append("**" + _parameter(a.kwarg, None))
    return ", ".join(parts)


def _signature(node: ast.FunctionDef) -> str:
    args = _parameters(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    decorators = "".join(f"@{ast.unparse(d)}\n" for d in node.decorator_list)
    return f"{decorators}def {node.name}({args}){ret}"


def _first_line(node: ast.AST) -> int:
    decorators = getattr(node, "decorator_list", [])
    return int(decorators[0].lineno if decorators else node.lineno)  # type: ignore[attr-defined]


def _is_enum(node: ast.ClassDef) -> bool:
    return any("enum" in ast.unparse(b) for b in node.bases)


def _declaring_header(entry: Entry, headers: dict[str, str]) -> str:
    """The header (of `headers`: name to text) that declares the entry, found by its C++ signature (a function) or
    its C++ name (a class, an enum); "" when none does"""
    if entry.kind == "function" and entry.cpp:
        prefix = entry.cpp.split("(")[0]  # `ImFont* LoadFont`, without its parameters
        pattern = r"\s*".join(re.escape(w) for w in prefix.split()) + r"\s*\("
    elif entry.kind in ("class", "enum"):
        name = re.sub(r"^(struct|class|enum class|enum)\s+", "", entry.cpp.split(":")[0].split("{")[0].strip())
        pattern = r"\b(struct|class|enum class|enum)\s+" + re.escape(name or entry.name) + r"\b"
    else:
        return ""
    for header, text in headers.items():
        if re.search(pattern, text):
            return header
    return ""


def read_stub(path: Path, headers_dir: Optional[Path] = None) -> list[Entry]:
    source = path.read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    headers: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if (m := HEADER_MARK.match(line.strip())):
            headers.append((i + 1, m.group(1)))
        elif (m := AMALGAMATION_MARK.match(line)):
            headers.append((i + 1, m.group(1)))
    generated_start = next((i + 1 for i, line in enumerate(lines) if "<litgen_stub>" in line), 0)
    generated_end = next((i + 1 for i, line in enumerate(lines) if "</litgen_stub>" in line), len(lines) + 1)
    entries: list[Entry] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        entry = _read_node(lines, node)
        if entry is None:
            continue
        entry.header = next((h for (ln, h) in reversed(headers) if ln < node.lineno), "")
        entry.generated = generated_start < node.lineno < generated_end
        entries.append(entry)
    entries = _merge_overloads(entries)
    if len({e.part for e in entries if e.part}) < 2 or not any(e.section for e in entries):
        # parts hold sections: a lone banner (hello_imgui's), or banners with no section inside (rich_md's), are
        # sections
        for entry in entries:
            if entry.part is not None:
                entry.section = entry.section or (entry.part, [])
                entry.part = None
    if headers_dir is not None:
        texts = {f"{headers_dir.name}/{h.name}": h.read_text() for h in sorted(headers_dir.glob("*.h"))}
        for entry in entries:
            entry.header = _declaring_header(entry, texts) or entry.header
        order = {h: i + 1 for i, (_, h) in enumerate(headers)}  # the amalgamation's order; the others after
        order[f"{headers_dir.name}/{headers_dir.name}.h"] = 0  # the umbrella header (Run, GetRunnerParams...) first
        entries.sort(key=lambda e: order.get(e.header, len(order) + 1))  # stable: the stub's order within a header
    return entries


def _merge_overloads(entries: list[Entry]) -> list[Entry]:
    """Consecutive functions of one name (Python overloads) become one entry with several signatures"""
    merged: list[Entry] = []
    for entry in entries:
        previous = merged[-1] if merged else None
        if (previous is not None and entry.kind in ("function", "method") and entry.kind == previous.kind
                and entry.name == previous.name):
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
        part, section, note = _section_or_note(before)
        entry = Entry("method" if in_class else "function", node.name, _signature(node), cpp,
                      ast.get_docstring(node) or "", "\n".join(x for x in [note, *after] if x), section=section)
        entry.part = part
        return entry
    if isinstance(node, ast.ClassDef):
        cpp, before, after = _split_comments(_leading_comments(lines, _first_line(node)))
        part, section, note = _section_or_note(before)
        entry = Entry("enum" if _is_enum(node) else "class", node.name, "", cpp, ast.get_docstring(node) or "",
                      "\n".join(x for x in [note, *after] if x), section=section)
        entry.part = part
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                sub = _read_node(lines, child, in_class=True)
                if sub is not None:
                    entry.children.append(sub)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                c_cpp, _, _ = _split_comments(_leading_comments(lines, child.lineno))
                signature = f"{child.target.id}: {ast.unparse(child.annotation)}"
                entry.children.append(Entry("attribute", child.target.id, signature, c_cpp, "",
                                            _trailing_comment(lines, child)))
            elif isinstance(child, ast.Assign) and entry.kind == "enum" and isinstance(child.targets[0], ast.Name):
                c_cpp, _, _ = _split_comments(_leading_comments(lines, child.lineno))
                trailing = _trailing_comment(lines, child)
                value = ""
                if (m := re.match(r"\(=\s*(.+?)\)\s*(.*)", trailing)):
                    value, trailing = m.group(1), m.group(2).lstrip("# ")
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


OUTLINE_WITHOUT_ENTRIES = {"imgui_bundle.imgui", "imgui_bundle.imgui.internal"}  # the modules whose outline (the
# contents panel) stops at the sections: hundreds of entries would make it heavy; the others list their entries

COMMENT_STYLE = "markdown"  # the current library's Library.comments, while its pages are written


def _is_code_line(line: str) -> bool:
    """A comment line laid out as code or as a table: a statement's end, a comment column, aligned columns"""
    text = line.rstrip()
    return bool(re.search(r"[;{}]\s*(//.*)?$", text) or re.search(r"\S\s{2,}//", text)
                or re.search(r"\S\s{3,}\S", text))


def _runs(lines: list[str]) -> list[tuple[str, list[str]]]:
    """The lines of a comment by run: "fence" (a markdown code fence, verbatim), "code" (lines laid out as code or
    tables, and the short lines between them, such as "..."), "prose" (the rest)"""
    runs: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            if not in_fence:
                runs.append(("fence", []))
            in_fence = not in_fence
            runs[-1][1].append(line)
            continue
        if in_fence:
            runs[-1][1].append(line)
            continue
        kind = "code" if _is_code_line(line) else "prose"
        if kind == "prose" and runs and runs[-1][0] == "code" and len(line.strip()) < 8:
            kind = "code"  # a short line between code lines ("...", "}")
        if not runs or runs[-1][0] != kind:
            runs.append((kind, []))
        runs[-1][1].append(line)
    for i in range(len(runs) - 1):  # a code run must hold two lines, unless it stands between prose and the end
        if runs[i][0] == "code" and len([x for x in runs[i][1] if x.strip()]) < 2 and runs[i + 1][0] == "prose":
            runs[i] = ("prose", runs[i][1])
    return runs


def _pre_block(lines: list[str]) -> str:
    """A text block; custom.css wraps its long lines (pre-wrap)"""
    return "::::::{code-block} text\n:class: header-comment\n" + "\n".join(lines).rstrip() + "\n::::::"


def _prose_lines(lines: list[str]) -> list[str]:
    """Prose lines as markdown: the hazards neutralized, the breaks kept, a [SECTION] mark as a bold line"""
    out = []
    for line in lines:
        if re.match(r"^\s*(=+|-{3,}|/{4,})\s*$", line):
            continue
        if line.strip().startswith("[SECTION]"):
            line = f"**{_part_title(line)}**"
        line = re.sub(r"^(\s*)#", r"\1\\#", line)
        line = re.sub(r"(?<![`\\])<(?=[A-Za-z_])", r"\\<", line)
        out.append(line)
    for i in range(len(out) - 1):  # a hard break between two lines of text (not around blank lines or list items)
        if (out[i].strip() and out[i + 1].strip() and not out[i].endswith("\\")
                and not re.match(r"^\s*([-*+]|\d+[.)])\s", out[i + 1])):
            out[i] += "\\"
    return out


def _safe_markdown(text: str) -> str:
    """A comment as markdown, with the hazards of C++ comments neutralized: a line of "=" or "-" (a setext heading
    for the line above), a leading "#" (a heading; ImPlot writes #xs for a parameter), "<Type>" (an HTML tag), an
    unclosed code fence (it would swallow the rest of the page), a NUL (a docstring's \0, as in Combo's). The lines
    laid out as code or as tables (imgui.h's examples and option lists) are text blocks, the prose keeps its breaks.
    A library with comments="pre" gets every multi-line comment as one text block"""
    text = text.replace("\x00", "\\0")
    if COMMENT_STYLE == "pre" and "\n" in text.strip():
        return _pre_block(text.splitlines())
    out: list[str] = []
    for kind, lines in _runs(text.splitlines()):
        if kind == "code":
            out += ["", _pre_block(lines), ""]
        elif kind == "fence":
            out += lines + ([] if len([x for x in lines if x.strip().startswith("```")]) % 2 == 0 else ["```"])
        else:
            out += _prose_lines(lines)
    return "\n".join(out).strip("\n")


def _split_bindings_notes(doc: str) -> tuple[str, str]:
    """A docstring, and litgen's notes for Python users apart (the "Python bindings defaults" paragraphs)"""
    paragraphs = doc.split("\n\n")
    notes = [p for p in paragraphs if p.lstrip().startswith("Python bindings defaults:")]
    return "\n\n".join(p for p in paragraphs if p not in notes), "\n\n".join(notes)


def _doc_lines(text: str) -> list[str]:
    return [_safe_markdown(text), ""] if text else []


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\x00", "\\0")


def _render_entry(entry: Entry, module: str, level: int, owner: str = "") -> list[str]:
    """An entry as markdown: a heading with a label, the signatures, the doc"""
    qualified = f"{owner}.{entry.name}" if owner else entry.name
    hashes = "#" * level
    out = [f"({_label(module, qualified)})=", f"{hashes} `{qualified}`", ""]  # a code span: __init__ is not emphasis
    if entry.kind in ("function", "method"):
        signatures = [(entry.signature, entry.cpp), *entry.overloads]
        out += _code("python", "\n\n".join(python for python, _ in signatures))
        if any(cpp for _, cpp in signatures):  # the C++ signatures, muted (custom.css: .cpp-signature)
            out += ["::::::{code-block} cpp", ":class: cpp-signature", *[cpp for _, cpp in signatures if cpp],
                    "::::::", ""]
        doc, notes = _split_bindings_notes(entry.doc)
        out += _doc_lines(doc)
        if entry.note:
            out += [_safe_markdown(entry.note), ""]
        if notes:  # litgen's "Python bindings defaults", which restates the signature: last, small
            out += ["::::::{div}", ":class: bindings-note", _safe_markdown(notes), "::::::", ""]
    elif entry.kind == "enum":
        out[1] = f"{hashes} `{qualified}` (enum)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += _doc_lines(entry.doc)
        out += ["| Member | Value | C++ | |", "|---|---|---|---|"]
        for m in entry.children:
            out.append(f"| `{m.name}` | {_cell(m.value)} | `{_cell(m.cpp)}` | {_cell(m.note)} |")
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
                out.append(f"| `{_cell(a.signature)}` | `{_cell(a.cpp)}` | {_cell(a.note)} |")
            out.append("")
        for c in entry.children:
            if c.kind != "attribute":
                out += _render_entry(c, module, min(level + 1, 6), qualified)
    return out


@dataclass
class ModulePages:
    module: str
    index: Path  # the module's page
    functions: int
    classes: int
    enums: int


def _intro_sentence(library: Library, module: str, stub: Path, functions: int, classes: int, enums: int) -> str:
    return (f"The module `{module}`, the Python API of [{library.title}](index.md), from "
            f"`bindings/imgui_bundle/{stub.relative_to(STUBS).as_posix()}`: {functions} functions, {classes} classes, "
            f"{enums} enums. Each entry gives the Python signature, then the C++ one, then the doc of the C++ header. "
            "The sections are the header's.")


def _bound_entries(entries: list[Entry]) -> list[Entry]:
    """The entries written by litgen from a library's headers, for the C++ pages: the stubs' hand-written parts
    (Python helpers, IM_COL32...) bind nothing, and the bundle's `*_pywrappers.h` headers exist for Python only.
    A dropped entry's part or section passes to the next kept entry"""
    kept: list[Entry] = []
    part: Optional[str] = None
    section: Optional[tuple[str, list[str]]] = None
    for entry in entries:
        part = entry.part or part
        section = entry.section or section
        if not entry.generated or "pywrappers" in entry.header:
            continue
        if part is not None and entry.part is None:
            entry.part = part
        if section is not None and entry.section is None:
            entry.section = section
        part, section = None, None
        kept.append(entry)
    return kept


def _render_entries(entries: list[Entry], module: str, cpp_namespace: Optional[str] = None) -> list[str]:
    """The entries as markdown, under the headings of their headers and parts (both H2), their sections (H3); the
    entries are H4. With a C++ namespace: the C++ view of the entries"""
    if cpp_namespace is not None:
        entries = _bound_entries(entries)
    out: list[str] = []
    header: Optional[str] = None
    for entry in entries:
        if entry.header != header:
            header = entry.header
            out += [f"## {header}", ""] if header else []
        if entry.part is not None:
            out += [f"## {entry.part}", ""]
        if entry.section is not None:
            title, text = entry.section
            out += [f"### {title}", ""]
            if text:
                out += [_safe_markdown("\n".join(text)), ""]
        if cpp_namespace is None:
            out += _render_entry(entry, module, 4)
        else:
            out += _render_cpp_entry(entry, module, cpp_namespace, 4)
    return out


def _cpp_intro(library: Library, module: str, python_index: str) -> str:
    return (f"The C++ API of [{library.title}](index.md) as it is bound to Python: the entries of the module "
            f"[`{module}`]({python_index}), in the same order, with their C++ signatures and the headers' comments. "
            "From the stubs: the functions excluded from the bindings, the typedefs and the macros are absent.")


def write_module_pages(library: Library, module: str, stub: Path, folder: Path, stem: str,
                       cpp: bool = False) -> ModulePages:
    """The reference of one module, one page (Ctrl-F finds everything; the outline stops at the sections). With
    `cpp`: the C++ view of the module, the same page with a `_cpp` suffix"""
    entries = read_stub(stub, REPO / library.headers if library.headers else None)
    functions = sum(1 for e in entries if e.kind == "function")
    classes = sum(1 for e in entries if e.kind == "class")
    enums = sum(1 for e in entries if e.kind == "enum")
    folder.mkdir(parents=True, exist_ok=True)
    index = folder / (f"{stem}_cpp.md" if cpp else f"{stem}.md")
    namespace = CPP_NAMESPACES.get(module) if cpp else None
    short = module.removeprefix("imgui_bundle.")  # the titles, in the navigation: the intro names the module
    title = f"{short} (C++)" if cpp else short
    intro = (_cpp_intro(library, module, f"{stem}.md") if cpp
             else _intro_sentence(library, module, stub, functions, classes, enums))
    # the theme reads outline_maxdepth from the page's frontmatter (site:) over the site's option (myst.yml, 2)
    frontmatter = ["---", "site:", "  outline_maxdepth: 3", "---"] if module not in OUTLINE_WITHOUT_ENTRIES else []
    index.write_text("\n".join([*frontmatter, GENERATED, "", f"# {title}", "", intro, "",
                                *_render_entries(entries, module, namespace)]))
    return ModulePages(module, index, functions, classes, enums)


CPP_NAMESPACES = {  # the C++ namespace of each module's functions, for the C++ pages ("" when the C++ names carry
    # their own prefix, as nvgBeginPath, or when the module is Python-only: no C++ page)
    "imgui_bundle.imgui": "ImGui", "imgui_bundle.imgui.internal": "ImGui", "imgui_bundle.imgui.test_engine": "",
    "imgui_bundle.imgui.backends": "", "imgui_bundle.hello_imgui": "HelloImGui",
    "imgui_bundle.immapp.immapp_cpp": "ImmApp", "imgui_bundle.implot": "ImPlot",
    "imgui_bundle.implot.internal": "ImPlot", "imgui_bundle.implot3d": "ImPlot3D",
    "imgui_bundle.implot3d.internal": "ImPlot3D", "imgui_bundle.immvision": "ImmVision",
    "imgui_bundle.imgui_node_editor": "ax::NodeEditor", "imgui_bundle.imguizmo": "ImGuizmo",
    "imgui_bundle.nanovg": "", "imgui_bundle.im_anim": "", "imgui_bundle.imgui_color_text_edit": "",
    "imgui_bundle.rich_md": "RichMd", "imgui_bundle.imgui_microtex": "ImGuiMicroTeX",
    "imgui_bundle.imgui_knobs": "ImGuiKnobs", "imgui_bundle.imgui_toggle": "ImGui",
    "imgui_bundle.imspinner": "ImSpinner", "imgui_bundle.im_cool_bar": "ImGui",
    "imgui_bundle.imgui_command_palette": "ImCmd", "imgui_bundle.im_file_dialog": "ifd",
    "imgui_bundle.portable_file_dialogs": "pfd", "imgui_bundle.imgui_tex_inspect": "ImGuiTexInspect",
    "imgui_bundle.imgui_explorer": "",
}


def _cpp_name(entry: Entry, namespace: str, owner: str = "") -> str:
    """The C++ name of an entry: from its signature (a function), its declaration (a class, an enum), or its name"""
    if entry.kind in ("function", "method"):
        m = re.search(r"([A-Za-z_]\w*)\s*\(", entry.cpp)
        name = m.group(1) if m else entry.name
    else:
        m = re.match(r"^(?:struct|class|enum class|enum)\s+([A-Za-z_]\w*)", entry.cpp)
        name = m.group(1) if m else entry.name
    if owner:
        return f"{owner}::{name}"
    return f"{namespace}::{name}" if namespace and entry.kind == "function" else name


def _cpp_doc(doc: str) -> str:
    """A docstring without litgen's notes for Python users (the "Python bindings defaults" paragraph)"""
    paragraphs = doc.split("\n\n")
    return "\n\n".join(p for p in paragraphs if not p.lstrip().startswith("Python bindings defaults:"))


def _render_cpp_entry(entry: Entry, module: str, namespace: str, level: int, owner: str = "") -> list[str]:
    """An entry as markdown, the C++ way: the C++ name, the C++ signature(s), the header's doc; nothing of Python"""
    name = _cpp_name(entry, namespace, owner)
    hashes = "#" * level
    out = [f"({_label('cpp.' + module, name)})=", f"{hashes} `{name}`", ""]
    if entry.kind in ("function", "method"):
        for _, cpp in [(entry.signature, entry.cpp), *entry.overloads]:
            if cpp:
                out += _code("cpp", cpp)
        out += _doc_lines(_cpp_doc(entry.doc))
        if entry.note:
            out += [_safe_markdown(entry.note), ""]
    elif entry.kind == "enum":
        out[1] = f"{hashes} `{name}` (enum)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += _doc_lines(_cpp_doc(entry.doc))
        out += ["| Member | Value | |", "|---|---|---|"]
        for m in entry.children:
            out.append(f"| `{_cell(m.cpp)}` | {_cell(m.value)} | {_cell(m.note)} |")
        out.append("")
    elif entry.kind == "class":
        out[1] = f"{hashes} `{name}` (struct)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += _doc_lines(_cpp_doc(entry.doc))
        attributes = [c for c in entry.children if c.kind == "attribute"]
        if attributes:
            out += ["| Member | |", "|---|---|"]
            for a in attributes:
                out.append(f"| `{_cell(a.cpp)}` | {_cell(a.note)} |")
            out.append("")
        for c in entry.children:
            if c.kind != "attribute":
                out += _render_cpp_entry(c, module, namespace, min(level + 1, 6), name)
    return out


def _demo_cards(library: Library, manifest: dict[str, Any], docs: dict[str, dict[str, Any]], page: Path) -> list[str]:
    """The cards of the demos that use the library, as on the demos page (the pictures' paths made relative to here)"""
    if not library.uses and not library.demos:
        return []
    out: list[str] = []
    for e in manifest["examples"]:
        if e.get("hidden") or not e.get("launcher", True):
            continue
        tagged = set(docs.get(e["filename"], {}).get("uses", [])) & set(library.uses)
        if not tagged and Path(e["filename"]).name not in library.demos:
            continue
        card = demo_card(manifest, docs, e, in_grid=True)
        for i, line in enumerate(card):  # demo_card writes the pictures' paths relative to the demos page
            if line.startswith(":::{image} "):
                picture = (BOOK / "intro" / line[len(":::{image} "):]).resolve()
                card[i] = ":::{image} " + os.path.relpath(picture, page.parent)
        out += ["::::{card}", *card, "::::", ""]
    if not out:
        return []
    return ["## Demos using it", "",
            "The demos of the catalog that use the library (the pictures link to their code and to the playground).",
            "",
            ":::::{grid} 1 2 3 3", "", *out, ":::::", ""]


def write_library_pages(library: Library, manifest: dict[str, Any], docs: dict[str, dict[str, Any]]) -> list[str]:
    """The intro page and the module pages of a library; returns the TOC lines"""
    global COMMENT_STYLE
    COMMENT_STYLE = library.comments
    folder = API / library.key
    folder.mkdir(parents=True, exist_ok=True)
    modules: list[ModulePages] = []
    cpp_pages: list[ModulePages] = []  # the C++ view of each module, when it has one
    for module, stub in library.modules:
        stub_path = STUBS / stub
        if not stub_path.is_file():
            print(f"warning: {stub_path} not found")
            continue
        stem = re.sub(r"[^a-z0-9_]+", "_", module.removeprefix("imgui_bundle.").lower()).strip("_") or "module"
        modules.append(write_module_pages(library, module, stub_path, folder, stem))
        if module in CPP_NAMESPACES:
            cpp_pages.append(write_module_pages(library, module, stub_path, folder, stem, cpp=True))
    index = folder / "index.md"
    out = [GENERATED, "", f"# {library.title}", "", library.tagline, ""]
    links = [f"[Upstream repository]({library.upstream})"]
    if library.book_page:
        links.append(f"[The book's page]({os.path.relpath(BOOK / (library.book_page + '.md'), folder)})")
    out += [" · ".join(links), ""]
    out += ["## Modules", "", "In `imgui_bundle` (`from imgui_bundle import imgui`):", ""]
    for m in modules:
        cpp = next((c for c in cpp_pages if c.module == m.module), None)
        view = f" · [the C++ view]({cpp.index.name})" if cpp else ""
        out.append(f"- [`{m.module.removeprefix('imgui_bundle.')}`]({m.index.name}): {m.functions} functions, "
                   f"{m.classes} classes, {m.enums} enums{view}")
    out.append("")
    out += _demo_cards(library, manifest, docs, index)
    index.write_text("\n".join(out))
    toc = [f"      - file: api/{library.key}/index", "        sections:"]
    for m in modules:
        cpp = next((c for c in cpp_pages if c.module == m.module), None)
        for mp in ([m, cpp] if cpp else [m]):
            toc.append(f"          - file: api/{library.key}/{mp.index.stem}")
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
