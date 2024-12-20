# scripts/convert_toc.py (just a rough sketch)
import yaml
import json
from pathlib import Path
import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
tutorial_dir = Path(THIS_DIR).parent

input_file = tutorial_dir / "_toc.yml"
output_file = tutorial_dir / "toc.json"

with input_file.open() as f:
    toc_data = yaml.safe_load(f)

# No special processing at first, just dump as JSON
with output_file.open("w") as f:
    json.dump(toc_data, f, indent=2)
