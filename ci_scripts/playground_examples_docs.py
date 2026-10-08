"""Prepares the playground's examples: their descriptions for the examples menu, and the manifests of their folders.

Writes examples_docs.json next to examples.json:
{filename: {"title": plain text, "text": markdown, "summary": markdown}}, extracted from the title and first paragraph
of each example's docstring; the summary is the paragraph's first sentences, which the cards of the launcher and of the
book show. Also writes the manifest.json of each bundle folder of examples.json: the files the playground downloads
with the example (e.g. Fiatlight's saved state in fiat_settings).
Also writes the book's page of the demos (docs/book/intro/demos.md): what the demo launcher shows, as a page that people
and AIs can read. The PDF export drops its grids of cards: the PDF gets a copy without them (intro/demos_pdf.md),
listed by a copy of the table of contents (_toc_pdf.yml). Also writes the catalog of the C++ launcher, an asset of
the explorer (demos_assets/demos_catalog.json): the categories and their demos, with what the Python launcher derives
at load time (the files, relative to the repository; whether a C++ version exists). Also writes the demos in plain
text for AI assistants (docs/book/intro/demos.txt, published as llms/demos.txt next to llms.txt): the categories,
what each demo shows, and the links to its code. Run by `just playground_examples_docs`, by the doc recipes, and
by `just cf_stage` (the deploy).

The "sources" of examples.json are the folders the playground serves (playground/<name>), with their place in the
repository (relative to the examples folder). An example's file is in the folder of its "source" (examples by default,
or e.g. demos_immapp), and its bundle folders are paths from there, as served (e.g. ../demos_assets). File names are
unique across sources: examples_docs.json is keyed by them.

The categories answer a reader's question, and an example goes where its kind says: a tutorial or an explanation to
"Start here" (the haikus too: a few lines that do a lot); a how-to to "Build an app", or to the category of its
platform when it is bound to one ("Python specifics", "In the browser"); a reference (a library, all of it) to
"Library tours", or to "Interactive manuals" when it is a library's demo wrapped by the imgui_explorer tooling (the
code of each section beside it); a showcase to "Interactive science" when it teaches science, else to the category of
what it shows off. Within a category, the entries are in the reader's order: simple first.

A page entry (its "page": a URL, and an optional "video") is a page to read, not a demo to run: e.g. the notebooks,
which run in Jupyter. Its "filename" is a markdown file, whose title and first paragraph play the docstring's role;
the cards link to the page and the video instead of the code.

Convention: an example's module docstring starts with a title (a first line, possibly "# Title", or underlined with
= or -), then a blank line, then a paragraph that tells a visitor what the example shows. Its first sentence, the
summary that the cards show, stands alone: it says what the example is about, in at most 120 characters. The menu
renders the markdown, but not math: write formulas in ASCII, e.g. `x(n+1) = r * x(n) * (1 - x(n))`.
"""
import ast
import json
import os
import re
import subprocess
from typing import Any, Optional
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO / "bindings/imgui_bundle/demos_python/playground/examples"
DEMOS_PYTHON_DIR = REPO / "bindings/imgui_bundle/demos_python"
DEMOS_CPP_DIR = REPO / "bindings/imgui_bundle/demos_cpp"  # its folders mirror those of demos_python
BOOK = REPO / "docs/book"
BOOK_PAGE = BOOK / "intro/demos.md"
BOOK_PAGE_PDF = BOOK / "intro/demos_pdf.md"
LLMS_DEMOS = BOOK / "intro/demos.txt"  # the demos in plain text, for AI assistants (published as llms/demos.txt)
CPP_CATALOG = REPO / "bindings/imgui_bundle/demos_assets/demos_catalog.json"
PICTURES = REPO / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground"
SITE = "https://imgui-bundle.pages.dev"
GITHUB = "https://github.com/pthom/imgui_bundle/blob/main/"
MAX_PARAGRAPH = 400  # characters: a longer first paragraph does not fit the menu's pane
MIN_SUMMARY = 40  # characters: a first "Pyodide only." says too little
MAX_SUMMARY = 120  # characters: a longer summary pushes the card's "More" far down, and the launcher's card cuts it
PICTURE_ASPECT, MAX_CROP = 1.6, 1.5  # as in the launcher: cropped to 16:10, or fitted when the shape is too different
# What an example uses, from its imports: the module, and the name shown (the launcher's library filter, the cards'
# "Uses" line). A module not listed here is not shown: the core (imgui, hello_imgui, immapp), the markdown and the
# icons (in nearly every example), and the utilities (numpy, ctypes...). When the imports mislead (a library imported
# for a utility, e.g. ImmVision for a texture in the ImPlot demo), the entry sets its own "uses" in examples.json.
USES = {
    "implot": "ImPlot", "implot_ctx": "ImPlot", "implot3d": "ImPlot3D", "immvision": "ImmVision",
    "imgui_knobs": "knobs", "imgui_toggle": "toggles", "imspinner": "spinners", "im_cool_bar": "cool bar",
    "imgui_command_palette": "command palette", "portable_file_dialogs": "file dialogs",
    "im_file_dialog": "file dialogs",
    "imgui_color_text_edit": "code editor", "imgui_node_editor": "node editor", "imguizmo": "ImGuizmo",
    "nanovg": "NanoVG", "im_anim": "ImAnim", "imgui_tex_inspect": "Tex Inspect", "imgui_terminal": "terminal",
    "imgui_fig": "Matplotlib", "matplotlib": "Matplotlib", "pydantic": "Pydantic", "fiatlight": "Fiatlight",
    "cv2": "OpenCV", "pandas": "pandas", "OpenGL": "OpenGL", "glfw": "GLFW", "glfw_utils": "GLFW",
    "sdl2": "SDL", "sdl3": "SDL", "pyglet": "pyglet", "pygame": "pygame", "wgpu": "wgpu", "js": "browser APIs",
}
RUN_ICON = "\u25b6\ufe0e"  # ▶, as text (not as an emoji): the links that run a demo in the browser, in the cards


def plain(markdown: str) -> str:
    """Markdown -> plain text: images go, links keep their text, emphasis marks go; code keeps its text as is"""
    parts = re.split(r"(`[^`]*`)", markdown)  # the odd parts are code: `x * y` keeps its "*"
    for i, part in enumerate(parts):
        if i % 2:
            parts[i] = part.strip("`")
        else:
            part = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", part)
            part = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", part)
            parts[i] = re.sub(r"\*|__", "", part)
    return "".join(parts).strip()


def title_and_paragraph(docstring: str) -> tuple[str, str]:
    lines = docstring.strip().splitlines()
    title = lines[0].lstrip("#").strip()
    rest = lines[1:]
    if rest and re.fullmatch(r"[=-]{3,}", rest[0].strip()):
        rest = rest[1:]
    blocks = [block.strip() for block in "\n".join(rest).split("\n\n")]
    return plain(title), next((b for b in blocks if plain(b)), "")  # the first one with text (not only an image)


def uses(paths: list[Path]) -> list[str]:
    """The names of USES for the modules these files import (`from imgui_bundle import implot`, `import cv2`...),
    in the order of USES"""
    modules: set[str] = set()
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                modules |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == "imgui_bundle":  # from imgui_bundle import implot, or from imgui_bundle.implot import x
                    modules |= {alias.name for alias in node.names} if len(parts) == 1 else {parts[1]}
                else:
                    modules.add(parts[0])
    return list(dict.fromkeys(name for module, name in USES.items() if module in modules))


def summary_and_rest(markdown: str) -> tuple[str, str]:
    """A paragraph's first sentences, at least MIN_SUMMARY characters of text, and the rest"""
    text = " ".join(markdown.split())
    end = text.find(". ")
    while end >= 0 and len(plain(text[:end + 1])) < MIN_SUMMARY:
        end = text.find(". ", end + 1)
    return (text, "") if end < 0 else (text[:end + 1], text[end + 2:])


def _ignored_by_git(paths: list[Path]) -> set[str]:
    """The files git ignores and does not track (e.g. the .ini of a local run): the repository does not ship them"""
    try:
        result = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(str(p) for p in paths),
                                capture_output=True, text=True, cwd=EXAMPLES_DIR)
    except FileNotFoundError:  # no git
        return set()
    return set(result.stdout.splitlines())


def disk_path(sources: dict[str, str], served: str) -> Path:
    """The file or folder of the repository that the playground serves at `served` (e.g. demos_immapp/../demos_assets,
    i.e. demos_assets): its first component is one of the served folders, which "sources" maps to the repository"""
    first, *rest = os.path.normpath(served).split(os.sep)
    return (EXAMPLES_DIR / sources[first]).joinpath(*rest).resolve()


def write_manifests(examples: list[dict[str, Any]], sources: dict[str, str]) -> None:
    """The manifest of each bundle folder: its files, in its subfolders too, except the manifest, the examples
    themselves, dot files, and what git ignores"""
    example_paths = {disk_path(sources, f"{e.get('source', 'examples')}/{e['filename']}") for e in examples}
    folders = {disk_path(sources, f"{e.get('source', 'examples')}/{f}")
               for e in examples for f in e.get("bundle_folders", [])}
    for folder_path in sorted(folders):
        candidates = [p for p in folder_path.rglob("*")
                      if p.is_file() and p.name not in ("manifest.json", CPP_CATALOG.name)
                      and p.resolve() not in example_paths
                      and not any(part.startswith(".") for part in p.relative_to(folder_path).parts)]
        ignored = _ignored_by_git(candidates)
        files = sorted(p.relative_to(folder_path).as_posix() for p in candidates if str(p) not in ignored)
        (folder_path / "manifest.json").write_text(json.dumps(files, indent=2) + "\n")
        print(f"wrote {folder_path / 'manifest.json'} ({len(files)} files)")


def cpp_file(e: dict[str, Any], python_path: Path) -> Optional[Path]:
    """The C++ version of an example, when it exists: the mirror of the Python file in demos_cpp, or the file that
    "cpp" names (e.g. in a submodule)"""
    if "cpp" in e:
        path = REPO / e["cpp"]
    elif python_path.is_relative_to(DEMOS_PYTHON_DIR):  # not the Python backends
        path = DEMOS_CPP_DIR / python_path.relative_to(DEMOS_PYTHON_DIR).with_suffix(".cpp")
    else:
        return None
    return path if path.exists() else None


def write_cpp_catalog(manifest: dict[str, Any], docs: dict[str, dict[str, Any]]) -> None:
    """The catalog of the C++ launcher: the categories, and per demo what the Python launcher derives at load time
    (see `load_catalog` in demo_immapp_launcher.py). The files are relative to the repository: the C++ maps them to
    its folders (preloaded under /demos_cpp and /demos_python in the browser)"""
    categories = {c["name"]: {"name": c["name"], "about": c["about"], "tip": c.get("tip", ""), "demos": []}
                  for c in manifest["categories"]}
    for e in manifest["examples"]:
        if e.get("hidden") or not e.get("launcher", True):
            continue
        folder = disk_path(manifest["sources"], e.get("source", "examples"))
        path = folder / e["filename"]
        cpp_path = cpp_file(e, path)
        doc = docs.get(e["filename"], {})
        categories[e["category"]]["demos"].append({
            "label": e["label"],
            "filename": e["filename"],
            "stem": Path(e["filename"]).stem,  # the picture's name on the site, the demo's page in the explorer
            "where": e.get("where", "both"),
            "text": doc.get("text", ""),
            "summary": doc.get("summary", ""),
            "uses": doc.get("uses", []),
            "python_file": path.relative_to(REPO).as_posix(),
            "cpp_file": cpp_path.relative_to(REPO).as_posix() if cpp_path is not None else None,
            "cpp_url": e.get("cpp_url", f"{SITE}/explorer/{Path(e['filename']).stem}.html"),  # "": none online
            "in_place": bool(e.get("in_place")),  # its function may be linked in the explorer
            "page": e.get("page", ""),  # a page entry: its URL (it has no code to run)
            "video": e.get("video", ""),
            "variants": [{"label": v["label"], "python_file": (folder / v["filename"]).resolve().relative_to(REPO).as_posix()}
                         for v in e.get("variants", [])],
        })
    catalog = {"categories": [c for c in categories.values() if c["demos"]]}
    CPP_CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {CPP_CATALOG} ({sum(len(c['demos']) for c in catalog['categories'])} demos)")


def demo_card(manifest: dict[str, Any], docs: dict[str, dict[str, Any]], e: dict[str, Any], in_grid: bool) -> list[str]:
    """A demo's heading, picture, description, tags and links. In a grid's card, the picture comes first (the pictures
    of a row align), the description is its summary, with the rest in a "More" dropdown, and the links are short, a row
    per language"""
    source, stem, where = e.get("source", "examples"), Path(e["filename"]).stem, e.get("where", "both")
    if e.get("page"):
        return page_card(e, docs, in_grid)
    path = disk_path(manifest["sources"], f"{source}/{e['filename']}")
    if "cpp" in e:  # a C++ version that is not the mirror of the Python file (e.g. in a submodule)
        cpp: Optional[Path] = REPO / e["cpp"]
    else:
        cpp = (DEMOS_CPP_DIR / path.relative_to(DEMOS_PYTHON_DIR).with_suffix(".cpp")
               if path.is_relative_to(DEMOS_PYTHON_DIR) else None)  # None: the Python backends
    cpp_code = f"{GITHUB}{cpp.relative_to(REPO).as_posix()}" if cpp is not None and cpp.exists() else None
    has_cpp = cpp_code is not None
    where_tags = {"browser": ["Browser only"], "desktop": ["Desktop only"]}.get(where, [])
    playground = f"{SITE}/playground/?demo={e['filename']}"
    # Where the C++ version runs online; an empty "cpp_url" says it cannot (e.g. it writes screenshots and exits)
    explorer = e.get("cpp_url", f"{SITE}/explorer/{stem}.html")
    code = f"{GITHUB}{path.relative_to(REPO).as_posix()}"
    # A demo in several files (e.g. the Python backends): a code link per variant, instead of the one code link
    code_links = [f"[Code {v['label']}]({GITHUB}{(path.parent / v['filename']).relative_to(REPO).as_posix()})"
                  for v in e.get("variants", [])] or [f"[Code]({code})"]
    picture = PICTURES / f"{stem}.jpg"
    lines = []
    if picture.is_file():  # a local path: the book's builds copy it (the PDF too), with no network
        lines += [f":::{{image}} {os.path.relpath(picture, BOOK_PAGE.parent)}", f":alt: {e['label']}"]
        if in_grid:
            width, height = Image.open(picture).size
            if max(width / height / PICTURE_ASPECT, PICTURE_ASPECT * height / width) > MAX_CROP:
                lines += [":class: demo-fit"]  # custom.css fits it, instead of cropping it
        else:
            lines += [":width: 400px"]
        lines += [":::", ""]
    heading = [f"### {e['label']}", ""]
    lines = lines + heading if in_grid else heading + lines
    text = docs.get(e["filename"], {}).get("text", "")
    used = docs.get(e["filename"], {}).get("uses", [])
    uses_line = [f"*Uses: {', '.join(used)}*", ""] if used else []
    if in_grid:
        summary, rest = summary_and_rest(text)
        lines += [summary, ""] + ([":::{dropdown} More", rest, ":::", ""] if rest else [])
        python_links = ([f"[{RUN_ICON} Run]({playground})"] if where != "desktop" else []) + code_links
        rows = ["{span .demo-lang}`Python:` " + " · ".join(python_links)]
        if has_cpp:
            cpp_links = ([f"[{RUN_ICON} Run]({explorer})"] if explorer else []) + [f"[Code]({cpp_code})"]
            rows.append("{span .demo-lang}`C++:` " + " · ".join(cpp_links))
        return lines + ([f"*{where_tags[0]}*", ""] if where_tags else []) + uses_line + ["\\\n".join(rows), ""]
    links = [f"[Run it in the playground]({playground})"] if where != "desktop" else []
    links += [f"[C++ version, in the explorer]({explorer})"] if has_cpp and explorer else []
    links += [link.replace("[Code", "[Python code") for link in code_links]
    links += [f"[C++ code]({cpp_code})"] if has_cpp else []
    tags = ["Python"] + (["C++"] if has_cpp else []) + where_tags
    return lines + [text, "", f"*{', '.join(tags)}*", ""] + uses_line + [" · ".join(links), ""]


def page_links(e: dict[str, Any]) -> list[tuple[str, str]]:
    """A page entry's links: (label, url), the page then the video"""
    return [("Page", e["page"])] + ([("Video", e["video"])] if e.get("video") else [])


def page_card(e: dict[str, Any], docs: dict[str, dict[str, Any]], in_grid: bool) -> list[str]:
    """The card of a page entry: as a demo's, with the links to the page and its video instead of the code"""
    stem = Path(e["filename"]).stem
    picture = PICTURES / f"{stem}.jpg"
    lines = []
    if picture.is_file():
        lines += [f":::{{image}} {os.path.relpath(picture, BOOK_PAGE.parent)}", f":alt: {e['label']}"]
        lines += [":::", ""] if in_grid else [":width: 400px", ":::", ""]
    heading = [f"### {e['label']}", ""]
    lines = lines + heading if in_grid else heading + lines
    text = docs.get(e["filename"], {}).get("text", "")
    links = " · ".join(f"[{label}]({url})" for label, url in page_links(e))
    if in_grid:
        summary, rest = summary_and_rest(text)
        return lines + [summary, ""] + ([":::{dropdown} More", rest, ":::", ""] if rest else []) + [links, ""]
    return lines + [text, "", links, ""]


def demo_code_links(manifest: dict[str, Any], e: dict[str, Any]) -> list[tuple[str, str]]:
    """The code of a demo on GitHub: (language, url), Python first (one per variant when it has some), then C++; for a
    page entry, its page and its video"""
    if e.get("page"):
        return page_links(e)
    path = disk_path(manifest["sources"], f"{e.get('source', 'examples')}/{e['filename']}")
    links = [(f"Python ({v['label']})", f"{GITHUB}{(path.parent / v['filename']).relative_to(REPO).as_posix()}")
             for v in e.get("variants", [])] or [("Python", f"{GITHUB}{path.relative_to(REPO).as_posix()}")]
    cpp = cpp_file(e, path)
    if cpp is not None:
        links.append(("C++", f"{GITHUB}{cpp.relative_to(REPO).as_posix()}"))
    return links


def write_llms_demos(manifest: dict[str, Any], docs: dict[str, dict[str, Any]]) -> None:
    """The demos in plain text, for AI assistants: by category, what each demo shows (its first paragraph), the
    libraries it uses, and the links to its code. An assistant reads it to find a demo close to what it writes."""
    out = ["# Dear ImGui Bundle: the demos", "",
           "The demos of the catalog, by category: what each one shows, the libraries it uses, and its code on GitHub "
           "(Python, and C++ when it exists). Read the code of a demo close to what you write. Most demos run in the "
           f"browser: {SITE}/playground/?demo=<file name> (not those marked desktop only). "
           f"The guide for AI assistants: {SITE}/llms.txt; the API in plain text: {SITE}/llms/api/index.txt.", ""]
    count = 0
    for category in manifest["categories"]:
        demos = [e for e in manifest["examples"] if e["category"] == category["name"]
                 and not e.get("hidden") and e.get("launcher", True)]
        if not demos:
            continue
        out += ["", f"## {category['name']}", "", plain(category["about"])]
        if category.get("tip"):
            out.append(plain(category["tip"]))
        out.append("")
        for e in demos:
            doc = docs.get(e["filename"], {})
            where = {"desktop": " (desktop only)", "browser": " (browser only)"}.get(e.get("where", "both"), "")
            out.append(f"- {e['label']}{where}: {' '.join(plain(doc.get('text', '')).split())}")  # one line
            if doc.get("uses"):
                out.append(f"  Uses: {', '.join(doc['uses'])}")
            out += [f"  {language}: {url}" for language, url in demo_code_links(manifest, e)]
            count += 1
    LLMS_DEMOS.write_text("\n".join(out) + "\n")
    print(f"wrote {LLMS_DEMOS} ({count} demos)")


def write_book_pages(manifest: dict[str, Any], docs: dict[str, dict[str, Any]]) -> None:
    """The book's page of the demos: the demo launcher's content (the same demos, categories and descriptions), in
    grids of cards. The PDF export drops the grids (mystmd's typst exporter does not handle them): the PDF gets a copy
    of the page without them, listed by a copy of the table of contents."""
    intro = [
        "",
        "The demos of Dear ImGui Bundle, by category, as in its demo launcher (the \"Demos\" page of the explorer, "
        "`demo_imgui_bundle`, or `python -m imgui_bundle.demos_python.demo_immapp_launcher`). Most of them run in your "
        f"browser, in the [Python playground]({SITE}/playground/); some also exist in C++, in the "
        f"[interactive explorer]({SITE}/explorer/).",
        "",
    ]
    generated = "% Generated by ci_scripts/playground_examples_docs.py from examples.json: do not edit it by hand"
    # The H1 comes first: mystmd takes it as the page's title
    legend = f"In each card, {RUN_ICON} Run opens the demo in your browser, and Code shows its source, on GitHub."
    site = ["# Demos & Tutorials", "", generated, *intro, legend, ""]
    pdf = ["# Demos & Tutorials", "", generated + " (the PDF's copy of demos.md, without its grids)", *intro]
    for category in manifest["categories"]:
        examples = [e for e in manifest["examples"] if e["category"] == category["name"]
                    and not e.get("hidden") and e.get("launcher", True)]
        if not examples:
            continue
        header = [f"## {category['name']}", "", category["about"], ""]
        if category.get("tip"):
            header += [f"*{category['tip']}*", ""]
        site += header + [":::::{grid} 1 2 3 3", ""]  # the outer fences are longer than the inner ones
        pdf += header
        for e in examples:
            site += ["::::{card}", *demo_card(manifest, docs, e, in_grid=True), "::::", ""]
            pdf += demo_card(manifest, docs, e, in_grid=False)
        site += [":::::", ""]
    for page, lines in ((BOOK_PAGE, site), (BOOK_PAGE_PDF, pdf)):
        page.write_text("\n".join(lines))
        print(f"wrote {page}")

    toc = (BOOK / "_toc.yml").read_text()
    # The API pages (written by api_pages.py) stay out of the PDF: too long, and made to be looked up
    toc = re.sub(r"  - caption: API reference\n(?:(?!  - caption:).*\n)*", "", toc)
    entry, entry_pdf = (f"- file: {p.relative_to(BOOK).with_suffix('').as_posix()}\n"
                        for p in (BOOK_PAGE, BOOK_PAGE_PDF))
    if toc.count(entry) != 1:
        raise ValueError(f"_toc.yml must list {entry.strip()} once")
    toc_pdf = "# Generated by ci_scripts/playground_examples_docs.py from _toc.yml: do not edit it by hand\n"
    (BOOK / "_toc_pdf.yml").write_text(toc_pdf + toc.replace(entry, entry_pdf))
    print(f"wrote {BOOK / '_toc_pdf.yml'}")


def main() -> None:
    manifest = json.loads((EXAMPLES_DIR / "examples.json").read_text())
    examples = manifest["examples"]
    write_manifests(examples, manifest["sources"])
    docs: dict[str, dict[str, Any]] = {}
    for example in examples:
        if example.get("hidden"):
            continue
        filename = example["filename"]
        if filename in docs:
            raise ValueError(f"{filename} is listed twice: examples_docs.json is keyed by file names")
        folder = EXAMPLES_DIR / manifest["sources"][example.get("source", "examples")]
        source_text = (folder / filename).read_text()
        docstring = source_text if example.get("page") else ast.get_docstring(ast.parse(source_text))
        if docstring is None:
            print(f"warning: {filename} has no docstring")
            continue
        title, text = title_and_paragraph(docstring)
        if not text:
            print(f"warning: {filename} has no first paragraph after its title")
        elif len(plain(text)) > MAX_PARAGRAPH:
            print(f"warning: {filename}: its first paragraph has {len(plain(text))} characters (more than {MAX_PARAGRAPH})")
        summary = summary_and_rest(text)[0]
        if len(plain(summary)) > MAX_SUMMARY and example.get("launcher", True):  # "launcher": false has no card
            print(f"warning: {filename}: its summary (first sentence) has {len(plain(summary))} characters "
                  f"(more than {MAX_SUMMARY})")
        files = [] if example.get("page") else ([folder / v["filename"] for v in example.get("variants", [])]
                                                or [folder / filename])
        docs[filename] = {"title": title, "text": text, "summary": summary,
                          "uses": example.get("uses", uses(files)),  # "uses" in examples.json: the imports mislead
                          "cpp": cpp_file(example, (folder / filename).resolve()) is not None}  # the gallery's C++ tag
    (EXAMPLES_DIR / "examples_docs.json").write_text(json.dumps(docs, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {EXAMPLES_DIR / 'examples_docs.json'} ({len(docs)} examples)")
    write_book_pages(manifest, docs)
    write_cpp_catalog(manifest, docs)
    write_llms_demos(manifest, docs)


if __name__ == "__main__":
    main()
