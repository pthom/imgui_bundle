import yaml
import json
from pathlib import Path

THIS_DIR = Path(__file__).parent
_TUTORIAL_DIR = THIS_DIR.parent
TUTORIAL_DIR_JBOOK = _TUTORIAL_DIR / "jbook"
TUTORIAL_DIR_SINGLEPAGE = _TUTORIAL_DIR / "single_page_book_app"

input_file = TUTORIAL_DIR_JBOOK / "_toc.yml"
output_file = TUTORIAL_DIR_SINGLEPAGE / "resources_singlepage/generated_toc.json"

def get_md_title(md_path: Path) -> str:
    """
    Extract the first H1 title (# ...) from the given markdown file.
    If none found, returns the filename stem as a fallback.
    """
    assert md_path.exists()

    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):  # First H1 found
                return line[2:].strip()
    return md_path.stem  # Fallback if no H1 found


def enrich_node(node: dict, base_path: Path):
    """
    Recursively enrich nodes in the TOC structure.
    Each node can have keys like 'file', 'sections', etc.
    We add a 'title' key if there's a corresponding file.
    """
    # If node has 'file', extract title
    if 'file' in node:
        md_file = base_path / (node['file'] + ".md")
        title = get_md_title(md_file)
        node['title'] = title

    # If node has sections, process them too
    if 'sections' in node:
        for section in node['sections']:
            enrich_node(section, base_path)

# Load and process the TOC file
with input_file.open("r", encoding="utf-8") as f:
    toc_data = yaml.safe_load(f)

# Enrich the root node
if "root" in toc_data:
    root_node = {"file": toc_data["root"]}
    enrich_node(root_node, TUTORIAL_DIR_JBOOK)
    toc_data["root"] = root_node

# Enrich all chapters
if "chapters" in toc_data:
    for chapter in toc_data["chapters"]:
        enrich_node(chapter, TUTORIAL_DIR_JBOOK)

# Write the enriched TOC to JSON
with output_file.open("w", encoding="utf-8") as f:
    json.dump(toc_data, f, indent=2, ensure_ascii=False)
