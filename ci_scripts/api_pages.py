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
    demos: list[str] = field(default_factory=list)  # the demos to show, by file name: for the core libraries, whose
    # use is not tagged (every demo imports them)
    headers: str = ""  # the folder of the C++ headers, when the stub comes from an amalgamation: the entries are then
    # classified by the header that declares them (the amalgamation's markers only mark the include points)


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
             ("imgui_bundle.immapp (C++ part)", "immapp/immapp_cpp.pyi"), ("imgui_bundle.immapp.nb", "immapp/nb.pyi")],
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


def _clean_comment(line: str) -> str:
    return line.strip().lstrip("#").strip()


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
    return [b for b in kept if not re.match(r"^\s*#+\s*$", b) and not HEADER_MARK.match(b.strip())]


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
    before = [b for b in before if not re.match(r"^#?\s*(if|ifdef|ifndef|elif|else|endif|define|include|pragma)\b", b)
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
        elif (m := re.match(r"^#\s+(\S+\.h) included by \S+\s*//$", line)):  # an amalgamation's marker
            headers.append((i + 1, m.group(1)))
    entries: list[Entry] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        entry = _read_node(lines, node)
        if entry is None:
            continue
        entry.header = next((h for (ln, h) in reversed(headers) if ln < node.lineno), "")
        entries.append(entry)
    entries = _merge_overloads(entries)
    if len({e.part for e in entries if e.part}) < 2 or not any(e.section for e in entries):
        # parts hold sections: a lone banner (hello_imgui's), or banners with no section inside (rich_md's), are sections
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
    module = module.split(" ")[0]  # "imgui_bundle.immapp (C++ part)": the import name
    return re.sub(r"[^a-zA-Z0-9_.-]", "-", f"{module}.{name}")


def _code(language: str, text: str) -> list[str]:
    return [f"```{language}", text, "```", ""]


def _safe_markdown(text: str) -> str:
    """A docstring as markdown, with the hazards of C++ comments neutralized: a line of "=" or "-" (a setext heading
    for the line above), a leading "#" (a heading; ImPlot writes #xs for a parameter), "<Type>" (an HTML tag), an
    unclosed code fence (it would swallow the rest of the page), a NUL (a docstring's \0, as in Combo's)"""
    text = text.replace("\x00", "\\0")
    out = []
    for line in text.splitlines():
        if re.match(r"^\s*(=+|-{3,}|/{4,})\s*$", line):
            continue
        line = re.sub(r"^(\s*)#", r"\1\\#", line)
        line = re.sub(r"(?<![`\\])<(?=[A-Za-z_])", r"\\<", line)
        out.append(line)
    if sum(1 for line in out if line.strip().startswith("```")) % 2:
        out.append("```")
    return "\n".join(out)


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
        for python, cpp in [(entry.signature, entry.cpp), *entry.overloads]:
            out += _code("python", python)
            if cpp:
                out += _code("cpp", cpp)
        out += _doc_lines(entry.doc)
        if entry.note:
            out += [_safe_markdown(entry.note), ""]
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


SPLIT_ABOVE = 300  # top-level entries: a module with more, and parts ([SECTION] marks), gets a page per group of
# parts and an index page (imgui and imgui.internal)
PAGE_ENTRIES = 100  # about, per page of a split module (a part larger than that keeps a page of its own)


@dataclass
class ModulePages:
    module: str
    index: Path  # the module's page: the reference itself, or the index of its pages when split
    pages: list[tuple[str, Path]]  # (title, page) when split
    functions: int
    classes: int
    enums: int


def _intro_sentence(library: Library, stub: Path, functions: int, classes: int, enums: int) -> str:
    return (f"The Python API of [{library.title}](index.md), from "
            f"`bindings/imgui_bundle/{stub.relative_to(STUBS).as_posix()}`: {functions} functions, {classes} classes, "
            f"{enums} enums. Each entry gives the Python signature, then the C++ one, then the doc of the C++ header. "
            "The sections are the header's.")


def _render_entries(entries: list[Entry], module: str, cpp_namespace: Optional[str] = None,
                    header: Optional[str] = None) -> list[str]:
    """The entries as markdown, under the headings of their headers, parts and sections (the levels shift by one
    when the entries have parts). With a C++ namespace: the C++ view of the entries"""
    out: list[str] = []
    shift = 1 if any(e.part for e in entries) else 0
    for entry in entries:
        if entry.header != header:
            header = entry.header
            out += [f"## {header}", ""] if header else []
        if entry.part is not None:
            out += [f"### {entry.part}", ""]
        if entry.section is not None:
            title, text = entry.section
            out += [f"{'#' * (3 + shift)} {title}", ""]
            if text:
                out += [_safe_markdown("\n".join(text)), ""]
        if cpp_namespace is None:
            out += _render_entry(entry, module, 4 + shift)
        else:
            out += _render_cpp_entry(entry, module, cpp_namespace, 4 + shift)
    return out


def _parts(entries: list[Entry]) -> list[tuple[Optional[str], list[Entry]]]:
    """The entries by part (the entries before the first part form a part without a title)"""
    parts: list[tuple[Optional[str], list[Entry]]] = []
    for entry in entries:
        if entry.part is not None or not parts:
            parts.append((entry.part, []))
        parts[-1][1].append(entry)
    return parts


def _pack(parts: list[tuple[Optional[str], list[Entry]]]) -> list[tuple[list[str], list[Entry]]]:
    """The parts packed into pages of about PAGE_ENTRIES entries: (the parts' titles, the entries). A page still
    small (under half of that) takes the next part whatever its size"""
    pages: list[tuple[list[str], list[Entry]]] = []
    for title, entries in parts:
        if pages and (len(pages[-1][1]) + len(entries) <= PAGE_ENTRIES or len(pages[-1][1]) < PAGE_ENTRIES / 2):
            pages[-1][1].extend(entries)
        else:
            pages.append(([], list(entries)))
        if title:
            pages[-1][0].append(title)
    return pages


def write_module_pages(library: Library, module: str, stub: Path, folder: Path, stem: str) -> ModulePages:
    """The reference of one module: one page, or, above SPLIT_ABOVE entries and when the header has parts, a page
    per group of parts and an index page listing them"""
    entries = read_stub(stub, REPO / library.headers if library.headers else None)
    functions = sum(1 for e in entries if e.kind == "function")
    classes = sum(1 for e in entries if e.kind == "class")
    enums = sum(1 for e in entries if e.kind == "enum")
    folder.mkdir(parents=True, exist_ok=True)
    index = folder / f"{stem}.md"
    intro = _intro_sentence(library, stub, functions, classes, enums)
    packed = _pack(_parts(entries)) if len(entries) > SPLIT_ABOVE else []
    if len(packed) <= 1:
        index.write_text("\n".join([GENERATED, "", f"# {module}", "", intro, "", *_render_entries(entries, module)]))
        return ModulePages(module, index, [], functions, classes, enums)
    pages: list[tuple[str, Path]] = []
    for n, (titles, page_entries) in enumerate(packed, 1):
        title = ", ".join(titles[:3]) + (f", ... ({len(titles)} parts)" if len(titles) > 4 else "")
        title = title or page_entries[0].header or module
        page = folder / f"{stem}_{n}.md"
        header = page_entries[0].header
        lines = [GENERATED, "", f"# {title}", "",
                 f"Page {n} of {len(packed)} of [`{module}`]({index.name}). "
                 + intro.split(": ", 1)[1].split(". ", 1)[1], ""]
        if header:
            lines += [f"## {header}", ""]
        lines += _render_entries(page_entries, module, None, header)
        page.write_text("\n".join(lines))
        pages.append((title, page))
    lines = [GENERATED, "", f"# {module}", "", intro, "",
             f"The module is in {len(pages)} pages, by part of the header:", ""]
    for (titles, _), (title, page) in zip(packed, pages):
        lines.append(f"- [{title}]({page.name})" + (f": {', '.join(titles)}" if len(titles) > 4 else ""))
    index.write_text("\n".join(lines) + "\n")
    return ModulePages(module, index, pages, functions, classes, enums)


CPP_PROTOTYPES = {"implot": "ImPlot", "imgui_knobs": "ImGuiKnobs"}  # library key: its C++ namespace. A prototype
# (Q2b, option A): a C++ view of the first module, from the same stubs, for two libraries


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


def _render_cpp_entry(entry: Entry, module: str, namespace: str, level: int, owner: str = "") -> list[str]:
    """An entry as markdown, the C++ way: the C++ name and signature first, the Python name and signature after"""
    name = _cpp_name(entry, namespace, owner)
    short = module.removeprefix("imgui_bundle.")  # the Python names as one writes them: implot.begin_plot
    python = entry.name if owner else f"{short}.{entry.name}"
    hashes = "#" * level
    out = [f"({_label('cpp.' + module, name)})=", f"{hashes} `{name}`", ""]
    if entry.kind in ("function", "method"):
        for py_signature, cpp in [(entry.signature, entry.cpp), *entry.overloads]:
            if cpp:
                out += _code("cpp", cpp)
            out += [f"Python: `{python}`", ""] + _code("python", py_signature)
        out += _doc_lines(entry.doc)
        if entry.note:
            out += [_safe_markdown(entry.note), ""]
    elif entry.kind == "enum":
        out[1] = f"{hashes} `{name}` (enum)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += [f"Python: `{python}`", ""]
        out += _doc_lines(entry.doc)
        out += ["| Member | Value | Python | |", "|---|---|---|---|"]
        for m in entry.children:
            out.append(f"| `{_cell(m.cpp)}` | {_cell(m.value)} | `{m.name}` | {_cell(m.note)} |")
        out.append("")
    elif entry.kind == "class":
        out[1] = f"{hashes} `{name}` (struct)"
        if entry.cpp:
            out += _code("cpp", entry.cpp)
        out += [f"Python: `{python}`", ""]
        out += _doc_lines(entry.doc)
        attributes = [c for c in entry.children if c.kind == "attribute"]
        if attributes:
            out += ["| Member | Python | |", "|---|---|---|"]
            for a in attributes:
                out.append(f"| `{_cell(a.cpp)}` | `{_cell(a.signature)}` | {_cell(a.note)} |")
            out.append("")
        for c in entry.children:
            if c.kind != "attribute":
                out += _render_cpp_entry(c, module, namespace, min(level + 1, 6), name)
    return out


def write_cpp_page(library: Library, module: str, entries: list[Entry], page: Path, python_page: str) -> None:
    """The C++ view of a module (a prototype): the same entries, in the same order, the C++ names first"""
    out = [GENERATED, "", f"# {library.title}: the C++ API", "",
           f"A prototype: the same entries as [`{module}`]({python_page}), in the same order, with the C++ name and "
           "signature first and the Python name beside. It lists what is bound to Python, from the stubs: an overload "
           "or a function excluded from the bindings is absent.", ""]
    out += _render_entries(entries, module, CPP_PROTOTYPES[library.key])
    page.write_text("\n".join(out))


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
    folder = API / library.key
    folder.mkdir(parents=True, exist_ok=True)
    modules: list[ModulePages] = []
    for module, stub in library.modules:
        stub_path = STUBS / stub
        if not stub_path.is_file():
            print(f"warning: {stub_path} not found")
            continue
        stem = re.sub(r"[^a-z0-9_]+", "_", module.removeprefix("imgui_bundle.").lower()).strip("_") or "module"
        modules.append(write_module_pages(library, module, stub_path, folder, stem))
    cpp_page: Optional[Path] = None
    if library.key in CPP_PROTOTYPES:
        module, stub = library.modules[0]
        cpp_page = folder / f"{modules[0].index.stem}_cpp.md"
        write_cpp_page(library, module, read_stub(STUBS / stub), cpp_page, modules[0].index.name)
    index = folder / "index.md"
    out = [GENERATED, "", f"# {library.title}", "", library.tagline, ""]
    links = [f"[Upstream repository]({library.upstream})"]
    if library.book_page:
        links.append(f"[The book's page]({os.path.relpath(BOOK / (library.book_page + '.md'), folder)})")
    out += [" · ".join(links), ""]
    out += ["## Modules", ""]
    for m in modules:
        pages = f" (in {len(m.pages)} pages)" if m.pages else ""
        out.append(f"- [`{m.module}`]({m.index.name}): {m.functions} functions, {m.classes} classes, "
                   f"{m.enums} enums{pages}")
    if cpp_page is not None:
        out.append(f"- [The C++ view of `{library.modules[0][0]}`]({cpp_page.name}) (a prototype)")
    out.append("")
    out += _demo_cards(library, manifest, docs, index)
    index.write_text("\n".join(out))
    toc = [f"      - file: api/{library.key}/index", "        sections:"]
    for m in modules:
        toc.append(f"          - file: api/{library.key}/{m.index.stem}")
        if m.pages:
            toc.append("            sections:")
            toc += [f"              - file: api/{library.key}/{page.stem}" for _, page in m.pages]
    if cpp_page is not None:
        toc.append(f"          - file: api/{library.key}/{cpp_page.stem}")
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
