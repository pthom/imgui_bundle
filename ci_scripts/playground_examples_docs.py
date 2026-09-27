"""Prepares the playground's examples: their descriptions for the examples menu, and the manifests of their folders.

Writes examples_docs.json next to examples.json: {filename: {"title": plain text, "text": markdown}}, extracted from
the title and first paragraph of each example's docstring. Also writes the manifest.json of each bundle folder of
examples.json: the files the playground downloads with the example (e.g. Fiatlight's saved state in fiat_settings).
Run by `just playground_examples_docs` and by `just cf_stage` (the deploy).

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

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "bindings/imgui_bundle/demos_python/playground/examples"
MAX_PARAGRAPH = 400  # characters: a longer first paragraph does not fit the menu's pane


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
        docs[filename] = {"title": title, "text": text}
    (EXAMPLES_DIR / "examples_docs.json").write_text(json.dumps(docs, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {EXAMPLES_DIR / 'examples_docs.json'} ({len(docs)} examples)")


if __name__ == "__main__":
    main()
