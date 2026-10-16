"""The book in plain text, for AI assistants (published as llms/book.txt): its pages for users, one after the other.

The pages are those of the PDF (docs/book/_toc_pdf.yml) before the developer docs, but for the guide for AI assistants
(published as llms.txt) and the demos (llms/demos.txt has them, with their links). Each page starts with its URL.
The MyST markup becomes plain markdown:
- the pictures are dropped (a figure keeps its caption, a link to a picture keeps its text);
- a tab gets its label ("Python:", "C++:"), a note its kind ("Tip:"), a card its link;
- an include is inlined, and a link to another page of the book becomes its URL.
A notebook gives its markdown cells, and its code cells as Python blocks.
Run by `just cf_stage`: `python ci_scripts/llms_book.py <output file>`.
"""
import json
import posixpath
import re
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent.parent / "docs/book"
DOC_URL = "https://imgui-bundle.pages.dev/doc/"
ROOT_PAGE = "intro/intro"  # served at the root of the book
SKIPPED_PAGES = ["intro/ai_guide", "intro/demos_pdf"]

HEADER = (
    "# Dear ImGui Bundle: the book, in plain text\n\n"
    f"The pages of the book for users ({DOC_URL}), one after the other: what the bundle is, how to install it, the "
    "core libraries, the add-ons, the notes for Python and for C++. Each page starts with its URL. The pictures are "
    "left out, and so are the developer docs (how to build the bundle and its bindings).\n\n"
    "The guide for AI assistants: https://imgui-bundle.pages.dev/llms.txt\n"
    "The API, in plain text: https://imgui-bundle.pages.dev/llms/api/index.txt\n"
    "The demos, with their code: https://imgui-bundle.pages.dev/llms/demos.txt\n"
)

OPEN_DIRECTIVE = re.compile(r"^(\s*)(`{3,}|:{3,})\{([\w-]+)\}\s*(.*?)\s*$")
OPEN_CODE = re.compile(r"^(\s*)(`{3,}|~{3,})")
OPTION = re.compile(r"^\s*:([\w-]+):\s*(.*?)\s*$")
ADMONITIONS = {"note", "tip", "important", "warning", "hint", "seealso", "attention", "caution", "danger", "error"}
CODE_DIRECTIVES = {"code", "code-block", "code-cell"}
LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")


def page_url(page: str) -> str:
    """The URL of a page, from its path in the book without extension (intro/key_features -> .../intro/key-features/)"""
    if page == ROOT_PAGE:
        return DOC_URL
    slug = page.lower().replace("_", "-")
    if slug == "index" or slug.endswith("/index"):
        return DOC_URL + slug[: -len("index")]
    return DOC_URL + slug + "/"


def convert_link(match: re.Match[str], page_dir: str) -> str:
    text, target = match.group(1), match.group(2)
    if re.match(r"(https?:|mailto:|#)", target):
        return match.group(0)
    path, _, anchor = target.partition("#")
    stem, ext = posixpath.splitext(path)
    if ext not in (".md", ".ipynb"):
        return text  # a picture, or a file of the book: no URL for it
    url = page_url(posixpath.normpath(posixpath.join(page_dir, stem)))
    return f"[{text}]({url}{'#' + anchor if anchor else ''})"


def convert_line(line: str, page_dir: str) -> str | None:
    """A line of text: None when it is markup only (a comment, a label, a picture)"""
    if line.startswith("%") or re.match(r"^\s*\([\w-]+\)=\s*$", line) or line.strip() == "+++":
        return None
    line = re.sub(r"<img\b[^>]*>", "", line)
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
    if not line.strip() and line:
        return None  # a line that held a picture only
    return LINK.sub(lambda m: convert_link(m, page_dir), line)


def is_closing(line: str, fence: str) -> bool:
    s = line.strip()
    return len(s) >= len(fence) and set(s) == {fence[0]}


def verbatim_until(lines: list[str], i: int, fence: str) -> tuple[list[str], int]:
    """The lines of a code block, up to its closing fence; and the index after it"""
    body = []
    while i < len(lines) and not is_closing(lines[i], fence):
        body.append(lines[i])
        i += 1
    return body, i + 1


def render_directive(name: str, arg: str, options: dict[str, str], body: list[str], indent: str,
                     page_dir: str) -> list[str]:
    if name == "image":
        return []
    if name == "include":
        included = (BOOK_DIR / page_dir / arg).resolve()
        return convert_text(included.read_text(), page_dir)
    out = []
    if name == "tab-item":
        out.append(f"{indent}{arg}:")
    elif name in ADMONITIONS:
        kind = name.capitalize()
        out.append(f"{indent}{kind}: {arg}" if arg and arg.lower() != name else f"{indent}{kind}:")
    elif name != "figure" and arg:
        out.append(f"{indent}{arg}")  # the title of a card, a dropdown...
    if "link" in options:
        out.append(f"{indent}Link: {options['link']}")
    return out + body


def convert_block(lines: list[str], i: int, closing_fence: str | None, page_dir: str) -> tuple[list[str], int]:
    """Converts lines from i up to the closing fence of the current directive (or to the end); and the index after it"""
    out: list[str] = []
    while i < len(lines):
        line = lines[i]
        if closing_fence and is_closing(line, closing_fence):
            return out, i + 1
        directive = OPEN_DIRECTIVE.match(line)
        code = OPEN_CODE.match(line)
        if directive:
            indent, fence, name, arg = directive.groups()
            i += 1
            options = {}
            while i < len(lines) and (option := OPTION.match(lines[i])):
                options[option.group(1)] = option.group(2)
                i += 1
            if name in CODE_DIRECTIVES:
                body, i = verbatim_until(lines, i, fence)
                out += [f"{indent}```{arg}"] + body + [f"{indent}```"]
            else:
                body, i = convert_block(lines, i, fence, page_dir)
                out += render_directive(name, arg, options, body, indent, page_dir)
        elif code:
            body, i = verbatim_until(lines, i + 1, code.group(2))
            out += [line] + body + [code.group(1) + code.group(2)]
        else:
            converted = convert_line(line, page_dir)
            if converted is not None:
                out.append(converted)
            i += 1
    return out, i


def convert_text(text: str, page_dir: str) -> list[str]:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # the front matter
    return convert_block(text.splitlines(), 0, None, page_dir)[0]


def convert_notebook(path: Path, page_dir: str) -> list[str]:
    out = []
    for cell in json.loads(path.read_text())["cells"]:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            out += convert_text(source, page_dir) + [""]
        elif cell["cell_type"] == "code":
            out += ["```python", *source.splitlines(), "```", ""]
    return out


def user_pages() -> list[str]:
    toc = (BOOK_DIR / "_toc_pdf.yml").read_text().split("  - caption: Developer docs")[0]
    return [p for p in re.findall(r"file: (\S+)", toc) if p not in SKIPPED_PAGES]


def main() -> None:
    parts = [HEADER]
    for page in user_pages():
        stem = page.removesuffix(".ipynb")
        page_dir = posixpath.dirname(stem)
        if page.endswith(".ipynb"):
            lines = convert_notebook(BOOK_DIR / page, page_dir)
        else:
            lines = convert_text((BOOK_DIR / f"{page}.md").read_text(), page_dir)
        parts.append(f"\n{'-' * 80}\nPage: {page_url(stem)}\n\n" + "\n".join(lines))
    text = "\n".join(parts)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    Path(sys.argv[1]).write_text(text)
    print(f"{sys.argv[1]}: {len(user_pages())} pages, {len(text.split())} words")


if __name__ == "__main__":
    main()
