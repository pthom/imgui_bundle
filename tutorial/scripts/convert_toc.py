import yaml
import json
from pathlib import Path

THIS_DIR = Path(__file__).parent
TUTORIAL_DIR = THIS_DIR.parent

input_file = TUTORIAL_DIR / "jbook/_toc.yml"
output_file = TUTORIAL_DIR / "single_page_book_app/resources_singlepage/generated_toc.json"

def get_md_title(md_path: Path) -> str:
    """
    Extract the first H1 title (# ...) from the given markdown file.
    If none found, returns the filename stem as a fallback.
    """
    if not md_path.exists():
        # If the file doesn't exist, return a fallback title
        return md_path.stem

    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):  # first H1 found
                return line[2:].strip()
    # fallback if no H1 found
    return md_path.stem

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

with input_file.open("r", encoding="utf-8") as f:
    toc_data = yaml.safe_load(f)

# The toc_data structure:
# {
#   "format": "jb-book",
#   "root": "discover_immediate",
#   "chapters": [
#       {
#           "file": "discover/hello_world",
#           "sections": [
#               {"file": "discover/widget_edit"}
#           ]
#       },
#       {
#          "file": "imgui/intro"
#       }
#   ]
# }

# Process root
root_file = toc_data.get("root")
if root_file:
    # Convert to a dict node for uniform treatment
    # (If root is just a string, we wrap it)
    # We'll store root in a dict: {"file": root_file}
    root_node = {"file": root_file}
    enrich_node(root_node, TUTORIAL_DIR)
    # Now copy back the title and keep root as a dict
    toc_data["root"] = root_node

# Process chapters
if "chapters" in toc_data:
    for chapter in toc_data["chapters"]:
        enrich_node(chapter, TUTORIAL_DIR)

with output_file.open("w", encoding="utf-8") as f:
    json.dump(toc_data, f, indent=2, ensure_ascii=False)
