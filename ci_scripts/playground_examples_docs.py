"""Extracts the title and first paragraph of each playground example's docstring, for the playground's examples menu.

Writes examples_docs.json next to examples.json: {filename: {"title": plain text, "text": markdown}}.
Run by `just playground_examples_docs` and by `just cf_stage` (the deploy).

Convention: an example's module docstring starts with a title (a first line, possibly "# Title", or underlined with
= or -), then a blank line, then a paragraph that tells a visitor what the example shows. The menu renders its markdown,
but not math: write formulas in ASCII, e.g. `x(n+1) = r * x(n) * (1 - x(n))`.
"""
import ast
import json
import re
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


def main() -> None:
    examples = json.loads((EXAMPLES_DIR / "examples.json").read_text())["examples"]
    docs = {}
    for example in examples:
        if example.get("hidden"):
            continue
        filename = example["filename"]
        docstring = ast.get_docstring(ast.parse((EXAMPLES_DIR / filename).read_text()))
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
