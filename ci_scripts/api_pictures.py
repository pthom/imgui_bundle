"""Pictures of the ImGui Explorer's demo sections, for the API pages.

An entry of the API pages (imgui, implot, implot3d) links to the demo section that shows it (see `demo_section` in
api_pages.py), and shows its picture when there is one. This script takes these pictures: it opens each section in the
local web build of the explorer (`build_imex_ems`, built by `just imex_ems_build`), in headless Chrome, by its link
(`?lib=implot&demo=Plots/Line Plots`). The explorer scrolls the section into view, and gives its place to the page
(`window.imguiExplorerSection`: its marker's place, the y of the markers after it, its window's edges). The picture is
the section's window from its title (above its marker, when the source shows one there) to its end: a marker after it,
between MIN_HEIGHT and MAX_HEIGHTS, or, before that, a closed header of a sibling or a parent (text left of the
section's indentation). CROPS adjusts a section's crop. The pictures are JPEG, 480 pixels wide at most, in the website
resources: docs/clone_website_resources/imgui-bundle.pages.dev/resources/api/<lib>/<section>.jpg.

Usage (Playwright and Pillow come from a throwaway environment: `just api_pictures ...`):
    python ci_scripts/api_pictures.py                      # all the sections
    python ci_scripts/api_pictures.py "Plots/Line Plots"   # some of them: their paths, or words of their paths
    python ci_scripts/api_pictures.py --stale              # the sections whose code changed since their picture
    python ci_scripts/api_pictures.py --mark-fresh [names] # their pictures are still right (all if no name)
    python ci_scripts/api_pictures.py --sheet DIR          # contact sheets of the pictures, to review them
    python ci_scripts/api_pictures.py --raw DIR [names]    # the whole page as PNG, in DIR (to choose a crop)

When a picture is saved, the hash of its section's code goes to picture_hashes.json, next to the pictures: `--stale`
compares it with the code as it is now. Retake the stale pictures at each release, and after a bump of imgui, implot or
implot3d (their demos change). Then review them (`--sheet`): a section whose crop is wrong gets an entry in CROPS.

Pitfall: the pictures show the build as it is: rebuild the explorer first (`just imex_ems_build`) after a change of
its demos.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from api_pages import (API_PICTURES, DEMO_SOURCES, DemoSection, demo_lines, demo_picture,  # noqa: E402
                       linked_demo_sections)

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "build_imex_ems/bin"
PORT = 7016  # the local server of the web build, started and stopped by this script
VIEWPORT = (1400, 900)  # the page's size, in CSS pixels (the device scale is 1)
MIN_HEIGHT = 140  # a picture's height before its resize, in CSS pixels
MAX_HEIGHTS = {"imgui": 420, "implot": 420, "implot3d": 600}  # (ImPlot3D: a square plot under its controls)
WIDTH = 480  # the width of the pictures, in pixels at most
HASHES = API_PICTURES / "picture_hashes.json"


TITLE_HEIGHT = 24  # a title's row above a marker (a tree node, a SeparatorText), in CSS pixels
TITLE_CALLS = ("TreeNode", "CollapsingHeader", "BeginTabItem", "SeparatorText")  # a call that draws a section's title


@dataclass
class Crop:
    top: Optional[int] = None  # from the section's marker; None: -TITLE_HEIGHT when a title is above it, else -2
    height: int = 0  # 0: to the section's end (see the docstring)


CROPS: dict[tuple[str, str], Crop] = {  # (library, section): its crop, where the default misses
    ("imgui", "Window options"): Crop(height=120),  # (the headers after it are framed: no closed header to find)
    ("imgui", "Widgets/Color/ColorPicker"): Crop(height=505),  # down to the picker's end
    ("imgui", "Examples/Custom rendering/Primitives"): Crop(top=411, height=212),  # the shapes, under their controls
    ("implot3d", "Plots/Surface Plots"): Crop(top=250, height=370),  # the plot, under its controls
}


def _hash(section: DemoSection) -> str:
    code = "\n".join(text for text, path in demo_lines(section.library) if path == section.path)
    return hashlib.sha1(code.encode()).hexdigest()[:12]


def _key(section: DemoSection) -> str:
    return f"{section.library}/{section.path}"


def _selected(sections: list[DemoSection], names: list[str]) -> list[DemoSection]:
    """The sections named by their paths, or by words of their paths (as the explorer's search)"""
    if not names:
        return sections
    chosen = []
    for name in names:
        exact = [s for s in sections if s.path == name or _key(s) == name]
        words = name.lower().split()
        matches = exact or [s for s in sections if all(w in _key(s).lower() for w in words)]
        if not matches:
            sys.exit(f"no section matches {name!r}")
        chosen += [s for s in matches if s not in chosen]
    return chosen


def _title_above(section: DemoSection) -> bool:
    """Whether the section's title is drawn just above its marker: the code line before the marker draws one, or
    starts the function that the demo calls under its title (ImPlot's Demo_LinePlots)"""
    source = next(path for lib, path in DEMO_SOURCES.values() if lib == section.library)
    lines = (REPO / source).read_text().splitlines()
    mark = next(i for i, line in enumerate(lines) if f'IMGUI_DEMO_MARKER("{section.path}")' in line)
    before = next((line.strip() for line in reversed(lines[:mark])
                   if line.strip() and line.strip() != "{" and not line.strip().startswith("//")), "")
    return any(call in before for call in TITLE_CALLS) or bool(re.match(r"(static\s+)?void\s+\w+\(.*\)\s*\{?$", before))


def _closed_header(image: Image.Image, place: dict[str, float], top: float, bottom: float) -> Optional[float]:
    """The y of the first row below the marker with text left of the section's indentation: a closed header of a
    sibling or a parent, after the section's end"""
    x0, x1 = round(place["left"]) + 2, round(place["x"]) - 4
    gray = image.convert("L")
    pixels, width = gray.tobytes(), gray.width
    for y in range(round(max(place["top"], top)) + 4, round(bottom)):
        if any(pixels[y * width + x] > 150 for x in range(x0, x1)):  # the text's light gray, on the dark theme
            return y - 4.0  # the row's top: its text starts a few pixels below
    return None


def _crop(shot: Path, section: DemoSection, place: dict[str, float], output: Path) -> None:
    """The section's part of the page (place: window.imguiExplorerSection), as a JPEG"""
    crop = CROPS.get((section.library, section.path), Crop())
    offset = crop.top if crop.top is not None else (-TITLE_HEIGHT if _title_above(section) else -2)
    top = max(place["top"] + offset, place["windowTop"])
    page = Image.open(shot)
    if crop.height:
        bottom = top + crop.height
    else:  # a marker after it, at MIN_HEIGHT or below, else the last one above MIN_HEIGHT, else the maximum
        limit = top + MAX_HEIGHTS[section.library]
        ends = sorted(n for n in place["next"] if top + 30 < n <= limit)
        bottom = next((n for n in ends if n >= top + MIN_HEIGHT), ends[-1] if ends else limit)
        bottom = min(bottom, place["windowBottom"])
        bottom = _closed_header(page, place, top, bottom) or bottom
    bottom = min(bottom, place["windowBottom"])
    image = page.crop((round(place["left"]), round(top), round(place["right"]), round(bottom)))
    if image.width > WIDTH:
        image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "JPEG", quality=82, optimize=True, progressive=True)


def take(sections: list[DemoSection], raw_dir: Path | None) -> None:
    """Opens each section in headless Chrome, and saves its picture (or, with raw_dir, the whole page)"""
    from playwright.sync_api import sync_playwright

    if not (BUILD / "index.html").is_file():
        sys.exit(f"{BUILD} has no web build of the explorer: run `just imex_ems_build`")
    hashes = json.loads(HASHES.read_text()) if HASHES.is_file() else {}
    server = subprocess.Popen([sys.executable, str(REPO / "ci_scripts/webserver_multithread_policy.py"), "-p",
                               str(PORT)], cwd=BUILD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_context(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]}).new_page()
            shots = raw_dir or Path(tempfile.mkdtemp())
            shots.mkdir(parents=True, exist_ok=True)
            for i, section in enumerate(sections):
                # "&shot": the explorer rewrites the address once its reveal is done (without it): wait for that
                url = f"http://localhost:{PORT}/?lib={section.library}&demo={quote(section.path, safe='')}&shot=1"
                page.goto(url)
                try:
                    page.wait_for_function("!location.search.includes('shot=1')", timeout=30_000)
                except Exception:
                    print(f"  {_key(section)}: the reveal did not finish, picture taken anyway")
                time.sleep(1.5)  # the reveal's scroll, and the demo's first frames (an animated plot)
                stem = demo_picture(section).stem
                shot = shots / f"{section.library}_{stem}.png"
                page.screenshot(path=str(shot))
                place = page.evaluate("window.imguiExplorerSection")
                if raw_dir is not None:
                    print(f"[{i + 1}/{len(sections)}] {_key(section)}: {place}")
                    continue
                print(f"[{i + 1}/{len(sections)}] {_key(section)}")
                if not place or place["section"] != section.path:
                    print(f"  not revealed: no picture (the explorer gives {place and place['section']!r})")
                    continue
                _crop(shot, section, place, demo_picture(section))
                shot.unlink()
                hashes[_key(section)] = _hash(section)
            browser.close()
        if raw_dir is None:
            shutil.rmtree(shots)
    finally:
        server.terminate()
        server.wait()
    if raw_dir is None:
        HASHES.write_text(json.dumps(dict(sorted(hashes.items())), indent=1) + "\n")
        pictures = [demo_picture(s) for s in linked_demo_sections() if demo_picture(s).is_file()]
        total = sum(p.stat().st_size for p in pictures)
        print(f"{len(pictures)} pictures in {API_PICTURES}, {total // 1024} KB in all")


def contact_sheets(sections: list[DemoSection], folder: Path, per_sheet: int = 12, columns: int = 3) -> None:
    """The pictures in grids, with their sections' names: sheet_01.png, ... in folder"""
    folder.mkdir(parents=True, exist_ok=True)
    pictures = [(s, demo_picture(s)) for s in sections if demo_picture(s).is_file()]
    cell_w, cell_h, label = WIDTH + 10, 340, 18
    for n in range(0, len(pictures), per_sheet):
        batch = pictures[n:n + per_sheet]
        rows = (len(batch) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cell_w, rows * (cell_h + label)), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        for i, (section, path) in enumerate(batch):
            x, y = (i % columns) * cell_w, (i // columns) * (cell_h + label)
            draw.text((x + 4, y + 3), f"{n + i + 1}. {_key(section)}", fill=(0, 0, 0))
            image = Image.open(path)
            image.thumbnail((WIDTH, cell_h))
            sheet.paste(image, (x + 5, y + label))
        sheet.save(folder / f"sheet_{n // per_sheet + 1:02d}.png")
    print(f"{(len(pictures) + per_sheet - 1) // per_sheet} sheets in {folder}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", help="sections: their paths, or words of their paths")
    parser.add_argument("--stale", action="store_true", help="the sections whose code changed since their picture")
    parser.add_argument("--mark-fresh", action="store_true", help="their pictures are still right")
    parser.add_argument("--sheet", type=Path, help="contact sheets of the pictures, in this folder")
    parser.add_argument("--raw", type=Path, help="the whole pages as PNG, in this folder (no picture saved)")
    args = parser.parse_args()
    sections = _selected(linked_demo_sections(), args.names)
    if args.sheet:
        contact_sheets(sections, args.sheet)
        return
    hashes = json.loads(HASHES.read_text()) if HASHES.is_file() else {}
    if args.mark_fresh:
        hashes.update({_key(s): _hash(s) for s in sections if demo_picture(s).is_file()})
        HASHES.write_text(json.dumps(dict(sorted(hashes.items())), indent=1) + "\n")
        return
    if args.stale:
        sections = [s for s in sections if hashes.get(_key(s)) != _hash(s) or not demo_picture(s).is_file()]
        print(f"{len(sections)} stale sections")
    take(sections, args.raw)


if __name__ == "__main__":
    main()
