"""Prepares the playground's examples: their descriptions for the examples menu, and the manifests of their folders.

Writes examples_docs.json next to examples.json:
{filename: {"title": plain text, "text": markdown, "summary": markdown}}, extracted from the title and first paragraph
of each example's docstring; the summary is the paragraph's first sentences, which the cards of the launcher and of the
book show. Also writes the manifest.json of each bundle folder of examples.json: the files the playground downloads
with the example (e.g. Fiatlight's saved state in fiat_settings).
Also writes the book's page of the demos (docs/book/intro/demos.md): what the demo launcher shows, as a page that people
and AIs can read. The PDF export drops its grids of cards: the PDF gets a copy without them (intro/demos_pdf.md),
listed by a copy of the table of contents (_toc_pdf.yml). Run by `just playground_examples_docs`, by the doc recipes,
and by `just cf_stage` (the deploy).

The "sources" of examples.json are the folders the playground serves (playground/<name>), with their place in the
repository (relative to the examples folder). An example's file is in the folder of its "source" (examples by default,
or e.g. demos_immapp), and its bundle folders are paths from there, as served (e.g. ../demos_assets). File names are
unique across sources: examples_docs.json is keyed by them.

Convention: an example's module docstring starts with a title (a first line, possibly "# Title", or underlined with
= or -), then a blank line, then a paragraph that tells a visitor what the example shows. The menu renders its markdown,
but not math: write formulas in ASCII, e.g. `x(n+1) = r * x(n) * (1 - x(n))`.
"""
import ast
import json
import os
import re
import subprocess
from typing import Any
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO / "bindings/imgui_bundle/demos_python/playground/examples"
CPP_IMMAPP_DIR = REPO / "bindings/imgui_bundle/demos_cpp/demos_immapp"
BOOK = REPO / "docs/book"
BOOK_PAGE = BOOK / "intro/demos.md"
BOOK_PAGE_PDF = BOOK / "intro/demos_pdf.md"
PICTURES = REPO / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground"
SITE = "https://imgui-bundle.pages.dev"
GITHUB = "https://github.com/pthom/imgui_bundle/blob/main/"
MAX_PARAGRAPH = 400  # characters: a longer first paragraph does not fit the menu's pane
MIN_SUMMARY = 40  # characters: a first "Pyodide only." says too little
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
                      if p.is_file() and p.name != "manifest.json" and p.resolve() not in example_paths
                      and not any(part.startswith(".") for part in p.relative_to(folder_path).parts)]
        ignored = _ignored_by_git(candidates)
        files = sorted(p.relative_to(folder_path).as_posix() for p in candidates if str(p) not in ignored)
        (folder_path / "manifest.json").write_text(json.dumps(files, indent=2) + "\n")
        print(f"wrote {folder_path / 'manifest.json'} ({len(files)} files)")


def demo_card(manifest: dict[str, Any], docs: dict[str, dict[str, str]], e: dict[str, Any], in_grid: bool) -> list[str]:
    """A demo's heading, picture, description, tags and links. In a grid's card, the description is its summary, and
    the rest is in a "More" dropdown; the links are short, a row per language"""
    source, stem, where = e.get("source", "examples"), Path(e["filename"]).stem, e.get("where", "both")
    path = disk_path(manifest["sources"], f"{source}/{e['filename']}")
    cpp = CPP_IMMAPP_DIR / f"{stem}.cpp"
    has_cpp = source == "demos_immapp" and cpp.exists()
    where_tags = {"browser": ["Browser only"], "desktop": ["Desktop only"]}.get(where, [])
    playground = f"{SITE}/playground/?demo={e['filename']}"
    explorer = f"{SITE}/explorer/{stem}.html"
    code, cpp_code = f"{GITHUB}{path.relative_to(REPO).as_posix()}", f"{GITHUB}{cpp.relative_to(REPO).as_posix()}"
    picture = PICTURES / f"{stem}.jpg"
    lines = [f"### {e['label']}", ""]
    if picture.is_file():  # a local path: the book's builds copy it (the PDF too), with no network
        lines += [f":::{{image}} {os.path.relpath(picture, BOOK_PAGE.parent)}", f":alt: {e['label']}"]
        lines += [] if in_grid else [":width: 400px"]
        lines += [":::", ""]
    text = docs.get(e["filename"], {}).get("text", "")
    if in_grid:
        summary, rest = summary_and_rest(text)
        lines += [summary, ""] + ([":::{dropdown} More", rest, ":::", ""] if rest else [])
        python_links = ([f"[{RUN_ICON} Run]({playground})"] if where != "desktop" else []) + [f"[Code]({code})"]
        rows = ["{span .demo-lang}`Python:` " + " · ".join(python_links)]
        if has_cpp:
            rows.append(f"{{span .demo-lang}}`C++:` [{RUN_ICON} Run]({explorer}) · [Code]({cpp_code})")
        return lines + ([f"*{where_tags[0]}*", ""] if where_tags else []) + ["\\\n".join(rows), ""]  # a line break
    links = [f"[Run it in the playground]({playground})"] if where != "desktop" else []
    links += [f"[C++ version, in the explorer]({explorer})"] if has_cpp else []
    links += [f"[Python code]({code})"] + ([f"[C++ code]({cpp_code})"] if has_cpp else [])
    tags = ["Python"] + (["C++"] if has_cpp else []) + where_tags
    return lines + [text, "", f"*{', '.join(tags)}*", "", " · ".join(links), ""]


def write_book_pages(manifest: dict[str, Any], docs: dict[str, dict[str, str]]) -> None:
    """The book's page of the demos: the demo launcher's content (the same demos, categories and descriptions), in
    grids of cards. The PDF export drops the grids (mystmd's typst exporter does not handle them): the PDF gets a copy
    of the page without them, listed by a copy of the table of contents."""
    intro = [
        "",
        "The demos of Dear ImGui Bundle, by category, as in its demo launcher (the \"Demo Apps\" tab of "
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
    docs: dict[str, dict[str, str]] = {}
    for example in examples:
        if example.get("hidden"):
            continue
        filename = example["filename"]
        if filename in docs:
            raise ValueError(f"{filename} is listed twice: examples_docs.json is keyed by file names")
        folder = EXAMPLES_DIR / manifest["sources"][example.get("source", "examples")]
        docstring = ast.get_docstring(ast.parse((folder / filename).read_text()))
        if docstring is None:
            print(f"warning: {filename} has no docstring")
            continue
        title, text = title_and_paragraph(docstring)
        if not text:
            print(f"warning: {filename} has no first paragraph after its title")
        elif len(plain(text)) > MAX_PARAGRAPH:
            print(f"warning: {filename}: its first paragraph has {len(plain(text))} characters (more than {MAX_PARAGRAPH})")
        docs[filename] = {"title": title, "text": text, "summary": summary_and_rest(text)[0]}
    (EXAMPLES_DIR / "examples_docs.json").write_text(json.dumps(docs, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {EXAMPLES_DIR / 'examples_docs.json'} ({len(docs)} examples)")
    write_book_pages(manifest, docs)


if __name__ == "__main__":
    main()
