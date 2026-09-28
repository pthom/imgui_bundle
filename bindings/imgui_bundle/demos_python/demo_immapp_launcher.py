# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""
The demos of Dear ImGui Bundle, with their pictures, descriptions and code.

The playground's examples, the immapp demos and the explorer's demos, by category. Pick one to see its picture and
description, then run it, read its code, or open it online: in the Python playground, or in the C++ explorer.

The catalog is the playground's (`playground/examples/examples.json`, and the descriptions extracted from the
docstrings in `examples_docs.json`). The pictures come from the website (see `ci_scripts/playground_screenshots.py`).
"""
import json
import math
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from imgui_bundle import imgui, immapp, hello_imgui, rich_md, im_anim, icons_fontawesome_4 as fa
from imgui_bundle import ImVec2, ImVec4, IM_COL32, em_size
from imgui_bundle.demos_python.demo_utils.api_demos import (
    main_python_package_folder, demos_python_folder, demos_cpp_folder, read_code, can_run_subprocess, spawn_demo_file)

SITE = "https://imgui-bundle.pages.dev"
PICTURES_URL = SITE + "/resources/playground/"
GITHUB = "https://github.com/pthom/imgui_bundle/blob/main/"
# In a clone of the repository, the pictures are also here, before they reach the website
REPO = Path(main_python_package_folder()).parent.parent
LOCAL_PICTURES = REPO / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground"
DEMOS_PYTHON_DIR = Path(demos_python_folder()).resolve()
DEMOS_CPP_DIR = Path(demos_cpp_folder()).resolve()  # its folders mirror those of demos_python
EXAMPLES_DIR = DEMOS_PYTHON_DIR / "playground/examples"

CARD_WIDTH = 15.0  # em: the minimum width of a card
DETAIL_WIDTH = 28.0  # em
PICTURE_ASPECT = 1.6  # of the pictures on the cards (cropped to it, or fitted when their shape is too different)
MAX_CROP = 1.5  # a picture more than 1.5 times wider or taller than the card's shape is fitted, not cropped
EASE = im_anim.ease_preset(im_anim.ease_type.ease_out_cubic)
DEAL_DELAY = 0.05  # s: between two cards dealt, when the gallery arrives on screen
DEAL_DURATION = 0.5  # s: the flight of one card, from the deck to its place
DEAL_SPIN = 18.0  # degrees: a card is dealt with a spin of at most this, settling as it lands (0: no spin)

# Colors
ACCENT = ImVec4(0.45, 0.65, 1.0, 1.0)  # the selected card, the chip of the category in view
CARD_BG = ImVec4(0.16, 0.18, 0.24, 1.0)  # under the card's text (the picture covers the rest)
CARD_BG_HOVERED = ImVec4(0.2, 0.23, 0.31, 1.0)
CARD_BORDER = ImVec4(0.25, 0.25, 0.3, 1.0)
CARD_BORDER_HOVERED = ImVec4(0.6, 0.62, 0.72, 1.0)
CATEGORY_TITLE = ImVec4(0.61, 0.86, 1.0, 1.0)
TAG_COLORS = {"Python": IM_COL32(48, 105, 152, 235), "C++": IM_COL32(96, 72, 160, 235),
              "Browser only": IM_COL32(190, 105, 30, 235), "Desktop only": IM_COL32(40, 125, 85, 235)}


def tween(key: str, target: float, duration: float, start: Optional[float] = None) -> float:
    """A value that eases toward its target (ImAnim), from `start` the first time (default: the target itself),
    identified by this key in the current ID stack"""
    return im_anim.tween_float(imgui.get_id(key), 0, target, duration, EASE, im_anim.policy.crossfade,
                               imgui.get_io().delta_time, target if start is None else start)


# ---------------------------------------------------------------------------------------------------------------------
# The catalog
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class Demo:
    label: str
    filename: str  # as in examples.json (e.g. explorables/julia_map.py): the playground knows it by this name
    where: str  # both, desktop or browser
    text: str  # a paragraph for visitors (markdown)
    summary: str  # its first sentences, for the card (markdown)
    uses: list[str]  # the libraries it uses (from its imports, named by the generator)
    path: Path  # its Python file
    cpp_path: Optional[Path]  # its C++ version, if any
    cpp_url: str  # where its C++ version runs online (the explorer's page by default)
    variants: list[tuple[str, Path]] = field(default_factory=list)  # the same demo in other files (label, file)

    @property
    def stem(self) -> str:
        return Path(self.filename).stem

    def tags(self) -> list[str]:
        tags = ["Python"]
        if self.cpp_path is not None:
            tags.append("C++")
        if self.where == "browser":
            tags.append("Browser only")
        if self.where == "desktop":
            tags.append("Desktop only")
        return tags


@dataclass
class Category:
    name: str
    about: str
    tip: str  # a second line, when the category has one to give (empty otherwise)
    demos: list[Demo] = field(default_factory=list)


def load_catalog() -> list[Category]:
    manifest = json.loads((EXAMPLES_DIR / "examples.json").read_text())
    docs = json.loads((EXAMPLES_DIR / "examples_docs.json").read_text())
    categories = {c["name"]: Category(c["name"], c["about"], c.get("tip", "")) for c in manifest["categories"]}
    for e in manifest["examples"]:
        if e.get("hidden") or not e.get("launcher", True):  # "launcher": false, e.g. Fiatlight until its studio is ready
            continue
        folder = EXAMPLES_DIR / manifest["sources"][e.get("source", "examples")]
        path = (folder / e["filename"]).resolve()
        cpp_path = None
        if "cpp" in e:  # a C++ version that is not the mirror of the Python file (e.g. in a submodule)
            cpp_path = REPO / e["cpp"]
        elif path.is_relative_to(DEMOS_PYTHON_DIR):  # not the Python backends
            cpp_path = DEMOS_CPP_DIR / path.relative_to(DEMOS_PYTHON_DIR).with_suffix(".cpp")
        categories[e["category"]].demos.append(Demo(
            label=e["label"],
            filename=e["filename"],
            where=e.get("where", "both"),
            text=docs.get(e["filename"], {}).get("text", ""),
            summary=docs.get(e["filename"], {}).get("summary", ""),
            uses=docs.get(e["filename"], {}).get("uses", []),
            path=path,
            cpp_path=cpp_path if cpp_path is not None and cpp_path.exists() else None,
            cpp_url=e.get("cpp_url", f"{SITE}/explorer/{Path(e['filename']).stem}.html"),
            variants=[(v["label"], (folder / v["filename"]).resolve()) for v in e.get("variants", [])],
        ))
    return [c for c in categories.values() if c.demos]


def plain_text(markdown: str) -> str:
    """Markdown as plain text: links keep their text, emphasis and code marks go"""
    import re
    plain = re.sub(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)", r"\1", markdown)  # a URL may hold (...)
    return " ".join(plain.replace("**", "").replace("`", "").replace("*", "").split())


# ---------------------------------------------------------------------------------------------------------------------
# The pictures: downloaded in the background, made into textures on the GUI thread
# ---------------------------------------------------------------------------------------------------------------------
class Pictures:
    TEXTURES_PER_FRAME = 3  # decoding all the pictures in one frame would freeze the app for a moment

    def __init__(self, stems: list[str]) -> None:
        self._data: dict[str, bytes] = {}  # downloaded, b"" when missing (e.g. offline)
        self._images: dict[str, Optional[hello_imgui.ImageAndSize]] = {}
        self._nb_stems = len(stems)
        self._last_texture_time = 0.0
        self._budget = 0
        if can_run_subprocess():  # i.e. not in Pyodide
            threading.Thread(target=self._download_all, args=(stems,), daemon=True).start()
        else:
            import asyncio
            asyncio.ensure_future(self._download_all_async(stems))

    @staticmethod
    def _local(stem: str) -> Optional[bytes]:
        path = LOCAL_PICTURES / f"{stem}.jpg"
        return path.read_bytes() if path.is_file() else None

    @staticmethod
    def _jpeg(data: bytes) -> bytes:
        """The data if it is a JPEG (the site answers a missing file with a web page), else b"""""
        return data if data.startswith(b"\xff\xd8") else b""

    def _download_all(self, stems: list[str]) -> None:
        for stem in stems:
            local = self._local(stem)
            data = local if local is not None else immapp.download_url_bytes(PICTURES_URL + stem + ".jpg")
            self._data[stem] = self._jpeg(data)

    async def _download_all_async(self, stems: list[str]) -> None:
        for stem in stems:
            self._data[stem] = self._jpeg(await immapp.download_url_bytes_async(PICTURES_URL + stem + ".jpg"))

    def new_frame(self) -> None:
        self._budget = self.TEXTURES_PER_FRAME

    def still_loading(self) -> bool:
        """Some pictures are still being downloaded, or fading in"""
        return len(self._data) < self._nb_stems or time.time() - self._last_texture_time < 1.0

    def image(self, stem: str) -> Optional[hello_imgui.ImageAndSize]:
        if stem in self._images:
            return self._images[stem]
        data = self._data.get(stem)
        if data is None or self._budget <= 0:
            return None  # not yet
        self._budget -= 1
        self._last_texture_time = time.time()
        image = hello_imgui.image_and_size_from_encoded_data(data, stem) if data else None
        self._images[stem] = image if image is not None and image.size.x > 0 else None
        return self._images[stem]

    def draw(self, stem: str, width: float, aspect: Optional[float] = None, rounding: float = 0.0,
             corners: int = 0) -> None:
        """The picture as an item (cropped to the aspect ratio, if given), fading in over a placeholder once it is
        loaded; its corners (an ImDrawFlags_ choice) rounded, e.g. the top ones in a rounded card"""
        image = self.image(stem)
        aspect = aspect or (image.size.x / image.size.y if image is not None else PICTURE_ASPECT)
        top_left = imgui.get_cursor_screen_pos()
        imgui.dummy(ImVec2(width, width / aspect))
        self.draw_at(imgui.get_window_draw_list(), stem, top_left, width, aspect, rounding, corners)

    def draw_at(self, draw_list: imgui.ImDrawList, stem: str, top_left: ImVec2, width: float, aspect: float,
                rounding: float = 0.0, corners: int = 0) -> None:
        """The picture on this draw list, from this corner, cropped to the aspect ratio (or fitted, when its shape is
        too different)"""
        image = self.image(stem)
        image_aspect = image.size.x / image.size.y if image is not None else PICTURE_ASPECT
        bottom_right = ImVec2(top_left.x + width, top_left.y + width / aspect)
        draw_list.add_rect_filled(top_left, bottom_right, IM_COL32(44, 46, 68, 255), rounding, corners)
        if image is None:
            icon_size = imgui.calc_text_size(fa.ICON_FA_CODE)
            draw_list.add_text(ImVec2((top_left.x + bottom_right.x - icon_size.x) / 2,
                                      (top_left.y + bottom_right.y - icon_size.y) / 2),
                               IM_COL32(200, 200, 220, 160), fa.ICON_FA_CODE)
            return
        alpha = tween(f"picture {stem}", 1.0, 0.5, start=0.0)
        uv0, uv1 = ImVec2(0, 0), ImVec2(1, 1)
        if max(image_aspect / aspect, aspect / image_aspect) > MAX_CROP:  # fit it, centered, on a dark background
            draw_list.add_rect_filled(top_left, bottom_right, IM_COL32(20, 22, 26, 255), rounding, corners)
            rounding = 0.0  # the picture floats inside the background: square
            if image_aspect > aspect:
                height = width / image_aspect
                top_left = ImVec2(top_left.x, (top_left.y + bottom_right.y - height) / 2)
                bottom_right = ImVec2(bottom_right.x, top_left.y + height)
            else:
                picture_width = (bottom_right.y - top_left.y) * image_aspect
                top_left = ImVec2((top_left.x + bottom_right.x - picture_width) / 2, top_left.y)
                bottom_right = ImVec2(top_left.x + picture_width, bottom_right.y)
        elif image_aspect > aspect:  # crop the sides
            margin = (1 - aspect / image_aspect) / 2
            uv0, uv1 = ImVec2(margin, 0), ImVec2(1 - margin, 1)
        elif image_aspect < aspect:  # crop the top and the bottom
            margin = (1 - image_aspect / aspect) / 2
            uv0, uv1 = ImVec2(0, margin), ImVec2(1, 1 - margin)
        draw_list.add_image_rounded(imgui.ImTextureRef(image.texture_id), top_left, bottom_right, uv0, uv1,
                                    IM_COL32(255, 255, 255, int(255 * alpha)), rounding, corners)


# ---------------------------------------------------------------------------------------------------------------------
# The actions
# ---------------------------------------------------------------------------------------------------------------------
def open_url(url: str) -> None:
    if can_run_subprocess():  # i.e. not in Pyodide
        import webbrowser
        webbrowser.open(url)
    else:
        import js  # type: ignore[import-not-found]
        js.window.open(url, "_blank")


def playground_url(demo: Demo) -> str:
    return f"{SITE}/playground/?demo={demo.filename}"


@dataclass
class CodeFile:
    """A source file of a demo, shown by the code view"""
    language: str  # "Python" or "C++"
    path: Path
    snippet: immapp.snippets.SnippetData

    @property
    def in_repository(self) -> Path:
        return self.path.relative_to(REPO)

    @property
    def github_url(self) -> Optional[str]:
        """Its page on GitHub, for the bundle's own files (a submodule's file has another repository)"""
        relative = self.in_repository.as_posix()
        return GITHUB + relative if relative.startswith("bindings/") else None


def code_file(path: Path, language: str) -> CodeFile:
    snippet = immapp.snippets.SnippetData()
    snippet.code = read_code(str(path))
    snippet.language = (immapp.snippets.SnippetLanguage.python if language == "Python"
                        else immapp.snippets.SnippetLanguage.cpp)
    snippet.displayed_filename = path.name
    return CodeFile(language, path, snippet)


# ---------------------------------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------------------------------
def lerp(a: ImVec4, b: ImVec4, t: float) -> ImVec4:
    return ImVec4(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t)


def small_screen() -> bool:
    """A phone or a small tablet (under about 800 px): the detail becomes a page of its own, the header wraps"""
    return imgui.get_io().display_size.x < em_size(50)


def curtain(alpha: float) -> int:
    """The color of a veil that hides what is under it: the window's background, at this opacity (the theme's
    background is translucent over black: composited here, so that the veil at alpha 1 hides everything)"""
    bg = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    return IM_COL32(int(255 * bg.x * bg.w), int(255 * bg.y * bg.w), int(255 * bg.z * bg.w), int(255 * alpha))


def big_text(text: str, scale: float, color: Optional[ImVec4] = None) -> None:
    imgui.push_font(None, imgui.get_style().font_size_base * scale)
    if color is not None:
        imgui.text_colored(color, text)
    else:
        imgui.text(text)
    imgui.pop_font()


def fit(text: str, width: float, lines: int) -> str:
    """The text, cut at a word and ended with an ellipsis, so that it takes at most these lines once wrapped"""
    max_height = lines * imgui.get_text_line_height() + 1
    if imgui.calc_text_size(text, wrap_width=width).y <= max_height:
        return text
    words = text.split()
    while words and imgui.calc_text_size(" ".join(words) + "…", wrap_width=width).y > max_height:
        words.pop()
    return " ".join(words) + "…"


def draw_tags(tags: list[str], bottom_right: ImVec2, draw_list: Optional[imgui.ImDrawList] = None) -> None:
    """Small pills, right-aligned from this corner (a picture's bottom right: usually its emptiest part)"""
    if draw_list is None:
        draw_list = imgui.get_window_draw_list()
    imgui.push_font(None, imgui.get_style().font_size_base * 0.85)
    pad = ImVec2(em_size(0.4), em_size(0.1))
    x = bottom_right.x
    for tag in reversed(tags):
        size = imgui.calc_text_size(tag)
        top = bottom_right.y - size.y - 2 * pad.y
        x -= size.x + 2 * pad.x
        draw_list.add_rect_filled(ImVec2(x, top), ImVec2(x + size.x + 2 * pad.x, bottom_right.y), TAG_COLORS[tag],
                                  em_size(0.6))
        draw_list.add_text(ImVec2(x + pad.x, top + pad.y), IM_COL32(240, 245, 255, 255), tag)
        x -= em_size(0.25)
    imgui.pop_font()


class Launcher:
    def __init__(self) -> None:
        self.categories = load_catalog()
        self.selected = self.categories[0].demos[0]
        self.pictures = Pictures(list(dict.fromkeys(d.stem for c in self.categories for d in c.demos)))
        self.category_y: dict[str, float] = {}  # the position of each category in the gallery (scroll coordinates)
        self.category_in_view = ""
        self.scroll_target: Optional[float] = None  # a click on a category chip scrolls smoothly to it
        self.nb_scrolls = 0
        self.code_view: Optional[tuple[Demo, list[CodeFile]]] = None
        self.code_language = "Side by side"  # or "Python", "C++": what the code view shows of a demo in two languages
        self.variant: dict[str, int] = {}  # per demo with variants: the one picked in the detail pane
        self.library = ""  # the library in use: the gallery shows the demos that use it (all when empty)
        self.search = ""  # the words typed in the search box: the gallery shows the demos that have them all
        self.idling_before: Optional[bool] = None  # the app's idling setting, while the launcher animates
        self.dealt_at: Optional[float] = None  # when the gallery last arrived on screen: its cards are dealt one by one
        self.deal_order: Optional[dict[str, int]] = None  # the cards dealt, in their order: the ones in view when it began
        self.gallery_rect = (ImVec2(0, 0), ImVec2(0, 0))  # on screen, this frame: the cards are dealt from below it
        self.detail_open = False  # on a small screen, the detail is a page of its own (a card opens it) not a pane
        self.card_rects: dict[str, tuple[ImVec2, ImVec2]] = {}  # on screen, this frame (the intro's automations click)

    def libraries(self) -> list[tuple[str, int]]:
        """The libraries the demos use, with how many use each, the most used first"""
        counts: dict[str, int] = {}
        for category in self.categories:
            for demo in category.demos:
                for library in demo.uses:
                    counts[library] = counts.get(library, 0) + 1
        return sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))

    def shown(self, category: Category) -> list[Demo]:
        """The demos of the category that the gallery shows: those that use the library in use, and that have every
        word of the search in their title, their description, their category or their libraries"""
        words = self.search.lower().split()
        return [d for d in category.demos if (not self.library or self.library in d.uses) and (not words or all(
            w in f"{d.label} {plain_text(d.text)} {category.name} {' '.join(d.uses)}".lower() for w in words))]

    def chip_label(self, category: Category) -> str:
        return f"{category.name} ({len(self.shown(category))})"

    def chip(self, label: str, highlight: float) -> bool:
        """A small button, colored with the accent when highlighted (in view, or in use); a row of chips wraps"""
        width = imgui.calc_text_size(label).x + 2 * imgui.get_style().frame_padding.x
        if width > imgui.get_content_region_avail().x:
            imgui.new_line()
        button = imgui.get_style_color_vec4(imgui.Col_.button)
        imgui.push_style_color(imgui.Col_.button, lerp(button, ImVec4(ACCENT.x, ACCENT.y, ACCENT.z, 0.55), highlight))
        clicked = imgui.small_button(label)
        imgui.pop_style_color()
        imgui.same_line()
        return clicked

    # The header: the name, what the bundle is, a chip per category that scrolls to it, and the library filter
    def title(self) -> None:
        big_text("Dear ImGui Bundle", 2.0)
        imgui.same_line()
        y = imgui.get_cursor_pos_y() + em_size(0.75)  # the tagline sits on the title's baseline
        imgui.set_cursor_pos_y(y)
        imgui.text_disabled("   Interactive apps in Python and C++, for desktop, web and mobile.")
        imgui.same_line()
        imgui.set_cursor_pos_y(y)
        imgui.text("Pick a demo: see it, run it, and read its code: each demo is a documented quickstart.")

    def filters(self) -> None:
        """The category chips, the library filter and the search box, then a separator"""
        for category in self.categories:
            highlight = tween(f"chip {category.name}", 1.0 if category.name == self.category_in_view else 0.0, 0.25)
            if self.chip(self.chip_label(category), highlight) and self.code_view is None:
                self.scroll_target = self.category_y.get(category.name)
                self.nb_scrolls += 1
        imgui.dummy(ImVec2(em_size(1.0), 0))
        imgui.same_line()
        self.library_filter()
        self.search_box()
        imgui.new_line()
        imgui.separator()

    def search_box(self) -> None:
        """The words to find in the demos (Escape clears them)"""
        width = em_size(14)
        if width > imgui.get_content_region_avail().x:
            imgui.new_line()
        imgui.set_next_item_width(width)
        padding = imgui.get_style().frame_padding
        imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(padding.x, 0))  # as high as the chips
        _, self.search = imgui.input_text_with_hint("##search", fa.ICON_FA_SEARCH + "  Search the demos", self.search)
        imgui.pop_style_var()
        if imgui.is_item_active() and imgui.is_key_pressed(imgui.Key.escape):
            self.search = ""
        imgui.set_item_tooltip("Words to find in the title, the description, the category or the libraries of a demo")
        imgui.same_line()

    def library_filter(self) -> None:
        """A button that says which library the gallery is filtered on, and a popup to pick one"""
        label = f"Library: {self.library} " + fa.ICON_FA_TIMES if self.library else "Library " + fa.ICON_FA_CARET_DOWN
        if self.chip(label, 1.0 if self.library else 0.0):
            imgui.open_popup("library")
        imgui.set_item_tooltip("Keep only the demos that use a library")
        if imgui.begin_popup("library"):
            if imgui.menu_item_simple("All the demos", "", not self.library):
                self.library = ""
            imgui.separator()
            for library, count in self.libraries():
                if imgui.menu_item_simple(f"{library} ({count})", "", library == self.library):
                    self.library = library
            imgui.end_popup()

    def card(self, demo: Demo, width: float) -> None:
        """The demo's picture, its label and the first sentences of its description; a click selects it"""
        padding = em_size(0.6)
        title_scale = 1.1
        height = width / PICTURE_ASPECT + imgui.get_text_line_height() * (title_scale + 2) + em_size(1.6)
        top_left = imgui.get_cursor_screen_pos()
        bottom_right = ImVec2(top_left.x + width, top_left.y + height)
        self.card_rects[demo.filename] = (top_left, bottom_right)
        hovered = imgui.is_mouse_hovering_rect(top_left, bottom_right) and imgui.is_window_hovered(
            imgui.HoveredFlags_.child_windows.value)
        hover = tween(f"hover {demo.filename}", 1.0 if hovered else 0.0, 0.15)
        is_selected = demo is self.selected

        # A shadow, as if the card lifted under the mouse: offset downward only (offset sideways, its rounded corner
        # showed as a notch outside the frame's rounded corner)
        shadow = em_size(0.5) * hover
        imgui.get_window_draw_list().add_rect_filled(ImVec2(top_left.x, top_left.y + shadow),
                                                     ImVec2(bottom_right.x, bottom_right.y + shadow),
                                                     IM_COL32(0, 0, 0, int(110 * hover)), em_size(0.5))
        border = ACCENT if is_selected else lerp(CARD_BORDER, CARD_BORDER_HOVERED, hover)
        imgui.push_style_color(imgui.Col_.border, border)
        imgui.push_style_color(imgui.Col_.child_bg, lerp(CARD_BG, CARD_BG_HOVERED, hover))
        imgui.push_style_var(imgui.StyleVar_.child_rounding, em_size(0.5))
        imgui.push_style_var(imgui.StyleVar_.child_border_size, 2.0 if is_selected else 1.0)
        imgui.push_style_var(imgui.StyleVar_.window_padding, ImVec2(0, 0))
        imgui.begin_child(f"##card {demo.filename}", ImVec2(width, height), imgui.ChildFlags_.borders.value,
                          imgui.WindowFlags_.no_scrollbar.value | imgui.WindowFlags_.no_scroll_with_mouse.value)
        # Rounded more than the card: the border is stroked inside the card's rect with the card's radius, so a
        # picture with that radius pokes out of the border's curve at the corner (visible on a high-DPI screen)
        self.pictures.draw(demo.stem, width, PICTURE_ASPECT, em_size(0.8), imgui.ImDrawFlags_.round_corners_top.value)
        picture_bottom_right = imgui.get_item_rect_max()
        draw_tags(demo.tags(), ImVec2(picture_bottom_right.x - em_size(0.4), picture_bottom_right.y - em_size(0.4)))
        imgui.set_cursor_pos(ImVec2(padding, imgui.get_cursor_pos_y() + em_size(0.4)))
        imgui.push_font(None, imgui.get_style().font_size_base * title_scale)
        imgui.text(fit(demo.label, width - 2 * padding, 1))
        imgui.pop_font()
        imgui.set_cursor_pos_x(padding)
        imgui.push_text_wrap_pos(width - padding)
        shown = fit(plain_text(demo.summary), width - 2 * padding, 2)
        imgui.text_disabled(shown)
        summary_hovered = imgui.is_item_hovered(imgui.HoveredFlags_.for_tooltip.value)
        imgui.pop_text_wrap_pos()
        if self.deal_order is not None and demo.filename not in self.deal_order and self.dealing():
            gallery_top, gallery_bottom = self.gallery_rect[0].y, self.gallery_rect[1].y
            if bottom_right.y > gallery_top and top_left.y < gallery_bottom:  # in view when the deal begins
                self.deal_order[demo.filename] = len(self.deal_order)
        flight = self.flight(demo.filename)
        if flight is not None and flight < 1.0 and self.deal_order is not None:  # hidden under a veil while its
            # double flies from the deck to here
            draw_list = imgui.get_window_draw_list()
            draw_list.push_clip_rect_full_screen()  # over the border too
            draw_list.add_rect_filled(ImVec2(top_left.x - 1, top_left.y - 1), ImVec2(bottom_right.x + 1, bottom_right.y + 1),
                                      curtain(1.0))  # a pixel more: the border's stroke
            draw_list.pop_clip_rect()
            if flight > 0.0:
                self.flying_card(demo, top_left, width, height, flight, self.deal_order[demo.filename])
        imgui.end_child()
        imgui.pop_style_var(3)
        imgui.pop_style_color(2)
        # The whole description, on the summary, when the card cuts it or shows its first sentences only
        if summary_hovered and shown != plain_text(demo.text):  # after the pops: the card's styles stay out of it
            imgui.set_next_window_size(ImVec2(em_size(25), 0))  # the markdown wraps at this width
            if imgui.begin_tooltip():
                rich_md.render(demo.text)
                imgui.end_tooltip()
        if hovered and imgui.is_mouse_released(imgui.MouseButton_.left.value):
            self.selected = demo
            if small_screen():
                self.detail_open = True

    def smooth_scroll(self) -> None:
        """Eases the gallery's scroll toward the chip's category (a new ImAnim channel per click, starting here)"""
        if self.scroll_target is None:
            return
        target = min(self.scroll_target, imgui.get_scroll_max_y())
        y = im_anim.tween_float(imgui.get_id(f"scroll {self.nb_scrolls}"), 0, target, 0.5, EASE,
                                im_anim.policy.crossfade, imgui.get_io().delta_time, imgui.get_scroll_y())
        imgui.set_scroll_y(y)
        if abs(y - target) < 1.0 or imgui.get_io().mouse_wheel != 0.0:
            self.scroll_target = None

    def deal(self) -> None:
        """Called when the gallery arrives on screen: the cards in view are dealt one after another, from the top
        left (the others, scrolled away, are simply there)"""
        self.dealt_at = imgui.get_time()
        self.deal_order = {}  # filled by the first frame's cards

    def dealing(self) -> bool:
        return self.dealt_at is not None and imgui.get_time() < self.dealt_at + 24 * DEAL_DELAY + DEAL_DURATION

    def flight(self, filename: str) -> Optional[float]:
        """Where this card is in its flight, from 0 (leaving the deck) to 1 (in place), while the gallery is being
        dealt: None when it is not, or when the card is not dealt; below 0 when it waits in the deck"""
        if self.deal_order is None or not self.dealing() or filename not in self.deal_order:
            return None
        assert self.dealt_at is not None
        return (imgui.get_time() - self.dealt_at - min(self.deal_order[filename], 24) * DEAL_DELAY) / DEAL_DURATION

    def flying_card(self, demo: Demo, top_left: ImVec2, width: float, height: float, flight: float,
                    index: int) -> None:
        """The card's double on the foreground, sliding from the deck (below the gallery, at its center) to the
        card's place; with DEAL_SPIN, it spins on the way (the vertices are rotated after the fact)"""
        eased = 1.0 - (1.0 - flight) ** 3
        gallery_min, gallery_max = self.gallery_rect
        deck = ImVec2((gallery_min.x + gallery_max.x - width) / 2, gallery_max.y + height * 0.3)
        pos = ImVec2(deck.x + (top_left.x - deck.x) * eased, deck.y + (top_left.y - deck.y) * eased)
        draw_list = imgui.get_foreground_draw_list()
        draw_list.push_clip_rect(gallery_min, gallery_max, True)
        first_vertex = draw_list.vtx_buffer.size()
        self.card_face(draw_list, demo, pos, width, height)
        if DEAL_SPIN:
            angle = math.radians(DEAL_SPIN * (((index * 7) % 5) - 2) / 2) * (1.0 - eased)  # this card's own
            center = ImVec2(pos.x + width / 2, pos.y + height / 2)
            imgui.internal.shade_verts_transform_pos(draw_list, first_vertex, draw_list.vtx_buffer.size(), center,
                                                     math.cos(angle), math.sin(angle), center)
        draw_list.pop_clip_rect()

    def card_face(self, draw_list: imgui.ImDrawList, demo: Demo, top_left: ImVec2, width: float,
                  height: float) -> None:
        """The card as primitives on a draw list (the flying double of `card`, which lays it out as widgets)"""
        bottom_right = ImVec2(top_left.x + width, top_left.y + height)
        padding, title_scale, rounding = em_size(0.6), 1.1, em_size(0.5)
        draw_list.add_rect_filled(top_left, bottom_right, imgui.color_convert_float4_to_u32(CARD_BG), rounding)
        self.pictures.draw_at(draw_list, demo.stem, top_left, width, PICTURE_ASPECT, em_size(0.8),
                              imgui.ImDrawFlags_.round_corners_top.value)
        picture_bottom = top_left.y + width / PICTURE_ASPECT
        draw_tags(demo.tags(), ImVec2(bottom_right.x - em_size(0.4), picture_bottom - em_size(0.4)), draw_list)
        font, font_size = imgui.get_font(), imgui.get_font_size()
        imgui.push_font(None, imgui.get_style().font_size_base * title_scale)
        title = fit(demo.label, width - 2 * padding, 1)
        imgui.pop_font()
        y = picture_bottom + em_size(0.4)
        draw_list.add_text(font, font_size * title_scale, ImVec2(top_left.x + padding, y),
                           imgui.get_color_u32(imgui.Col_.text), title)
        y += font_size * title_scale + imgui.get_style().item_spacing.y
        draw_list.add_text(font, font_size, ImVec2(top_left.x + padding, y),
                           imgui.get_color_u32(imgui.Col_.text_disabled),
                           fit(plain_text(demo.summary), width - 2 * padding, 2), wrap_width=width - 2 * padding)
        draw_list.add_rect(top_left, bottom_right, imgui.color_convert_float4_to_u32(CARD_BORDER), rounding)

    def gallery(self) -> None:
        self.smooth_scroll()
        pos, size = imgui.get_window_pos(), imgui.get_window_size()
        self.gallery_rect = (pos, ImVec2(pos.x + size.x, pos.y + size.y))
        spacing = em_size(1.0)
        avail = imgui.get_content_region_avail().x
        columns = max(1, int((avail + spacing) // (em_size(CARD_WIDTH) + spacing)))
        card_width = (avail - (columns - 1) * spacing) / columns  # the cards fill the width
        categories = [c for c in self.categories if self.shown(c)]
        if not categories:
            imgui.text_disabled("No demo matches.")
            return
        self.category_in_view = categories[0].name
        for i, category in enumerate(categories):
            if i:
                imgui.dummy(ImVec2(0, em_size(0.6)))
            self.category_y[category.name] = imgui.get_cursor_pos_y()
            at_the_end = imgui.get_scroll_y() >= imgui.get_scroll_max_y() - 1  # the last categories can't reach the top
            if self.category_y[category.name] <= imgui.get_scroll_y() + em_size(3) or at_the_end:
                self.category_in_view = category.name
            big_text(category.name, 1.45, CATEGORY_TITLE)
            imgui.text_disabled(category.about)
            if category.tip:
                imgui.text_disabled(category.tip)
            imgui.dummy(ImVec2(0, em_size(0.3)))
            for i, demo in enumerate(self.shown(category)):
                if i % columns:
                    imgui.same_line(0, spacing)
                elif i:
                    imgui.dummy(ImVec2(0, em_size(0.3)))  # a little space between the rows
                self.card(demo, card_width)
            imgui.dummy(ImVec2(0, em_size(0.8)))

    def action(self, label: str, tooltip: str) -> bool:
        clicked = imgui.button(label, ImVec2(-1, 0))
        imgui.set_item_tooltip(tooltip)
        return clicked

    def detail(self) -> None:
        """The selected demo: its picture, its description, and what to do with it"""
        demo = self.selected
        appear = tween(f"appear {demo.filename}", 1.0, 0.35, start=0.0)  # a new selection fades in
        imgui.push_style_var(imgui.StyleVar_.alpha, appear)
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + (1.0 - appear) * em_size(1.0))  # it slides in a little
        width = imgui.get_content_region_avail().x
        self.pictures.draw(demo.stem, width, rounding=em_size(0.5), corners=imgui.ImDrawFlags_.round_corners_all.value)
        picture_bottom_right = imgui.get_item_rect_max()
        draw_tags(demo.tags(), ImVec2(picture_bottom_right.x - em_size(0.4), picture_bottom_right.y - em_size(0.4)))
        imgui.dummy(ImVec2(0, em_size(0.4)))
        rich_md.render(f"## {demo.label}\n\n{demo.text}")
        if demo.uses:
            imgui.text_disabled("Uses: " + ", ".join(demo.uses))
        imgui.dummy(ImVec2(0, em_size(0.6)))

        path = demo.path
        if demo.variants:  # e.g. the Python backends: one card, a combo picks the file to run and to show
            index = self.variant.get(demo.filename, 0)
            imgui.set_next_item_width(-1)
            _, index = imgui.combo("##variant", index, [label for label, _ in demo.variants])
            self.variant[demo.filename] = index
            path = demo.variants[index][1]
        if demo.where != "browser" and can_run_subprocess():
            if self.action(fa.ICON_FA_PLAY + "  Run", "Runs the demo on your machine, in a new window"):
                spawn_demo_file(str(path))
        if self.action(fa.ICON_FA_CODE + "  View code",
                       "Shows its code: Python, and C++ side by side when there is a C++ version"):
            files = [code_file(path, "Python")]
            if demo.cpp_path is not None:
                files.append(code_file(demo.cpp_path, "C++"))
            self.code_view = (demo, files)
        if demo.where != "desktop":
            if self.action(fa.ICON_FA_GLOBE + "  Open in the Python playground",
                           "Opens it in your browser, in the Python playground: edit its code, and run it again"):
                open_url(playground_url(demo))
        if demo.cpp_path is not None:
            if self.action(fa.ICON_FA_GLOBE + "  Run the C++ version online",
                           "Opens its C++ version in your browser, compiled to WebAssembly"):
                open_url(demo.cpp_url)
        imgui.pop_style_var()

    def show_code(self) -> None:
        """The demo's code: its files (where they are, a way to open each), then the code, one language or both"""
        assert self.code_view is not None
        demo, files = self.code_view
        if imgui.button(fa.ICON_FA_ARROW_LEFT + "  All the demos"):
            self.code_view = None
            return
        imgui.same_line()
        big_text(demo.label, 1.3)
        for file in files:  # where the file is, and how to open it
            imgui.push_id(file.language)
            imgui.text_disabled(f"{file.language}:")
            imgui.same_line()
            imgui.text(file.in_repository.as_posix())
            if can_run_subprocess():  # i.e. not in Pyodide
                imgui.same_line()
                if imgui.small_button(fa.ICON_FA_FOLDER_OPEN + "  Open"):
                    open_url(file.path.as_uri())
                imgui.set_item_tooltip("Opens the file with the application your system uses for it")
            if file.github_url is not None:
                imgui.same_line()
                if imgui.small_button(fa.ICON_FA_GLOBE + "  GitHub"):
                    open_url(file.github_url)
            imgui.pop_id()
        shown = files
        if len(files) == 2:  # one language, or both side by side
            for choice in ("Side by side", "Python", "C++"):
                if self.chip(choice, 1.0 if choice == self.code_language else 0.0):
                    self.code_language = choice
            imgui.new_line()
            shown = [f for f in files if self.code_language in ("Side by side", f.language)]
        lines = int(imgui.get_content_region_avail().y / imgui.get_text_line_height()) - 4
        for file in shown:
            file.snippet.height_in_lines = lines
            file.snippet.max_height_in_lines = lines
        if len(shown) == 2:
            immapp.snippets.show_side_by_side_snippets(shown[0].snippet, shown[1].snippet)
        else:
            immapp.snippets.show_code_snippet(shown[0].snippet)

    @property
    def depth(self) -> int:
        """How many levels Escape can go back: the code view, then the detail page of a small screen"""
        return (self.code_view is not None) + self.detail_open

    def back(self) -> None:
        """One level back: closes the code view, else the detail page of a small screen"""
        if self.code_view is not None:
            self.code_view = None
        elif self.detail_open:
            self.detail_open = False

    def detail_page(self) -> None:
        """On a small screen: the detail alone, full width, with the way back to the gallery"""
        if imgui.button(fa.ICON_FA_ARROW_LEFT + "  All the demos"):
            self.detail_open = False
            return
        avail = imgui.get_content_region_avail()
        imgui.begin_child("detail", avail)
        imgui.begin_child("detail content", ImVec2(avail.x - imgui.get_style().scrollbar_size, 0),
                          imgui.ChildFlags_.auto_resize_y.value)
        self.detail()
        imgui.end_child()
        imgui.end_child()

    def gui(self, with_title: bool = True) -> None:
        """The launcher; without its title when the explorer draws its own header above"""
        self.pictures.new_frame()
        self.keep_smooth(self.pictures.still_loading() or self.scroll_target is not None or self.dealing())
        if imgui.is_key_pressed(imgui.Key.escape) and not imgui.is_any_item_active():  # active: the search box
            self.back()
        if self.code_view is not None:  # no header: the demo's title and the way back are the only row
            self.show_code()
            return
        if small_screen() and self.detail_open:
            self.detail_page()
            return
        if with_title:
            self.title()
        self.filters()
        avail = imgui.get_content_region_avail()
        if small_screen():  # the gallery alone: a card opens the detail as a page
            imgui.begin_child("gallery", avail)
            self.gallery()
            imgui.end_child()
            return
        detail_width = em_size(DETAIL_WIDTH)
        imgui.begin_child("gallery", ImVec2(avail.x - detail_width - em_size(1.0), avail.y))
        self.gallery()
        imgui.end_child()
        imgui.same_line(0, em_size(1.0))
        imgui.begin_child("detail", ImVec2(detail_width, avail.y))
        # The content in a child of fixed width (a scrollbar's width less than the pane), sized to its height: its
        # picture and markdown take the child's width, so the pane's scrollbar, which comes and goes with that height,
        # never changes their width (it did: narrower, then shorter, then wider again, every frame)
        imgui.begin_child("detail content", ImVec2(detail_width - imgui.get_style().scrollbar_size, 0),
                          imgui.ChildFlags_.auto_resize_y.value)
        self.detail()
        imgui.end_child()
        imgui.end_child()

    def keep_smooth(self, animating: bool) -> None:
        """No idling while something moves (smooth animations), then the app's idling setting is back"""
        fps_idling = hello_imgui.get_runner_params().fps_idling
        if animating and self.idling_before is None:
            self.idling_before = fps_idling.enable_idling
            fps_idling.enable_idling = False
        elif not animating and self.idling_before is not None:
            fps_idling.enable_idling = self.idling_before
            self.idling_before = None


_LAUNCHER: Optional[Launcher] = None


def demo_gui() -> None:
    global _LAUNCHER
    if _LAUNCHER is None:
        _LAUNCHER = Launcher()
    _LAUNCHER.gui()


def main() -> None:
    immapp.run(demo_gui, window_title="Dear ImGui Bundle: the demos", window_size=(1500, 950), with_markdown=True,
               with_im_anim=True)


if __name__ == "__main__":
    main()
