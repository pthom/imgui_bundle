# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""
The demos of Dear ImGui Bundle, with their pictures, descriptions and code.

The playground's examples and the immapp demos, by category. Pick one to see its picture and description, then run
it, read its code, or open it online: in the Python playground, or in the C++ explorer.

The catalog is the playground's (`playground/examples/examples.json`, and the descriptions extracted from the
docstrings in `examples_docs.json`). The pictures come from the website (see `ci_scripts/playground_screenshots.py`).
"""
import json
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
# In a clone of the repository, the pictures are also here, before they reach the website
LOCAL_PICTURES = (Path(main_python_package_folder()).parent.parent
                  / "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground")
EXAMPLES_DIR = Path(demos_python_folder()) / "playground/examples"
CPP_IMMAPP_DIR = Path(demos_cpp_folder()) / "demos_immapp"

CARD_WIDTH = 15.0  # em: the minimum width of a card
DETAIL_WIDTH = 28.0  # em
PICTURE_ASPECT = 1.6  # of the pictures on the cards (cropped to it, or fitted when their shape is too different)
MAX_CROP = 1.5  # a picture more than 1.5 times wider or taller than the card's shape is fitted, not cropped
EASE = im_anim.ease_preset(im_anim.ease_type.ease_out_cubic)

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
    path: Path  # its Python file
    cpp_path: Optional[Path]  # its C++ version, if any

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
    demos: list[Demo] = field(default_factory=list)


def load_catalog() -> list[Category]:
    manifest = json.loads((EXAMPLES_DIR / "examples.json").read_text())
    docs = json.loads((EXAMPLES_DIR / "examples_docs.json").read_text())
    categories = {c["name"]: Category(c["name"], c["about"]) for c in manifest["categories"]}
    for e in manifest["examples"]:
        if e.get("hidden") or not e.get("launcher", True):  # "launcher": false, e.g. Fiatlight until its studio is ready
            continue
        source = e.get("source", "examples")
        cpp_path = CPP_IMMAPP_DIR / (Path(e["filename"]).stem + ".cpp")
        categories[e["category"]].demos.append(Demo(
            label=e["label"],
            filename=e["filename"],
            where=e.get("where", "both"),
            text=docs.get(e["filename"], {}).get("text", ""),
            summary=docs.get(e["filename"], {}).get("summary", ""),
            path=(EXAMPLES_DIR / manifest["sources"][source] / e["filename"]).resolve(),
            cpp_path=cpp_path if source == "demos_immapp" and cpp_path.exists() else None,
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

    def draw(self, stem: str, width: float, aspect: Optional[float] = None) -> None:
        """The picture (cropped to the aspect ratio, if given), fading in over a placeholder once it is loaded"""
        image = self.image(stem)
        image_aspect = image.size.x / image.size.y if image is not None else PICTURE_ASPECT
        aspect = aspect or image_aspect
        top_left = imgui.get_cursor_screen_pos()
        bottom_right = ImVec2(top_left.x + width, top_left.y + width / aspect)
        imgui.dummy(ImVec2(width, width / aspect))
        draw_list = imgui.get_window_draw_list()
        draw_list.add_rect_filled_multi_color(top_left, bottom_right, IM_COL32(40, 52, 80, 255),
                                              IM_COL32(60, 40, 90, 255), IM_COL32(30, 30, 40, 255),
                                              IM_COL32(30, 36, 50, 255))
        if image is None:
            icon_size = imgui.calc_text_size(fa.ICON_FA_CODE)
            draw_list.add_text(ImVec2((top_left.x + bottom_right.x - icon_size.x) / 2,
                                      (top_left.y + bottom_right.y - icon_size.y) / 2),
                               IM_COL32(200, 200, 220, 160), fa.ICON_FA_CODE)
            return
        alpha = tween(f"picture {stem}", 1.0, 0.5, start=0.0)
        uv0, uv1 = ImVec2(0, 0), ImVec2(1, 1)
        if max(image_aspect / aspect, aspect / image_aspect) > MAX_CROP:  # fit it, centered, on a dark background
            draw_list.add_rect_filled(top_left, bottom_right, IM_COL32(20, 22, 26, 255))
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
        draw_list.add_image(imgui.ImTextureRef(image.texture_id), top_left, bottom_right, uv0, uv1,
                            IM_COL32(255, 255, 255, int(255 * alpha)))


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


def explorer_url(demo: Demo) -> str:
    return f"{SITE}/explorer/{demo.stem}.html"


def code_snippet(path: Path, language: immapp.snippets.SnippetLanguage, name: str) -> immapp.snippets.SnippetData:
    snippet = immapp.snippets.SnippetData()
    snippet.code = read_code(str(path))
    snippet.language = language
    snippet.displayed_filename = name
    return snippet


# ---------------------------------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------------------------------
def lerp(a: ImVec4, b: ImVec4, t: float) -> ImVec4:
    return ImVec4(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t)


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


def draw_tags(tags: list[str], bottom_right: ImVec2) -> None:
    """Small pills, right-aligned from this corner (a picture's bottom right: usually its emptiest part)"""
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
        self.code_view: Optional[tuple[Demo, list[immapp.snippets.SnippetData]]] = None
        self.idling_before: Optional[bool] = None  # the app's idling setting, while the launcher animates

    # The header: the name, what the bundle is, and a chip per category that scrolls to it
    def header(self) -> None:
        big_text("Dear ImGui Bundle", 2.0)
        imgui.same_line()
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + em_size(0.75))
        imgui.text_disabled("   Interactive apps in Python and C++, for desktop, web and mobile. "
                            "Pick a demo: see it, run it, read its code.")
        for category in self.categories:
            highlight = tween(f"chip {category.name}", 1.0 if category.name == self.category_in_view else 0.0, 0.25)
            button = imgui.get_style_color_vec4(imgui.Col_.button)
            chip_color = lerp(button, ImVec4(ACCENT.x, ACCENT.y, ACCENT.z, 0.55), highlight)
            imgui.push_style_color(imgui.Col_.button, chip_color)
            if imgui.small_button(f"{category.name} ({len(category.demos)})") and self.code_view is None:
                self.scroll_target = self.category_y.get(category.name)
                self.nb_scrolls += 1
            imgui.pop_style_color()
            imgui.same_line()
        imgui.new_line()
        imgui.separator()

    def card(self, demo: Demo, width: float) -> None:
        """The demo's picture, its label and the first sentences of its description; a click selects it"""
        padding = em_size(0.6)
        title_scale = 1.1
        height = width / PICTURE_ASPECT + imgui.get_text_line_height() * (title_scale + 2) + em_size(1.6)
        top_left = imgui.get_cursor_screen_pos()
        bottom_right = ImVec2(top_left.x + width, top_left.y + height)
        hovered = imgui.is_mouse_hovering_rect(top_left, bottom_right) and imgui.is_window_hovered(
            imgui.HoveredFlags_.child_windows.value)
        hover = tween(f"hover {demo.filename}", 1.0 if hovered else 0.0, 0.15)
        is_selected = demo is self.selected

        # A shadow, as if the card lifted under the mouse
        shadow = em_size(0.25) * hover
        imgui.get_window_draw_list().add_rect_filled(ImVec2(top_left.x + shadow, top_left.y + 2 * shadow),
                                                     ImVec2(bottom_right.x + shadow, bottom_right.y + 2 * shadow),
                                                     IM_COL32(0, 0, 0, int(110 * hover)), em_size(0.5))
        border = ACCENT if is_selected else lerp(CARD_BORDER, CARD_BORDER_HOVERED, hover)
        imgui.push_style_color(imgui.Col_.border, border)
        imgui.push_style_color(imgui.Col_.child_bg, lerp(CARD_BG, CARD_BG_HOVERED, hover))
        imgui.push_style_var(imgui.StyleVar_.child_rounding, em_size(0.5))
        imgui.push_style_var(imgui.StyleVar_.child_border_size, 2.0 if is_selected else 1.0)
        imgui.push_style_var(imgui.StyleVar_.window_padding, ImVec2(0, 0))
        imgui.begin_child(f"##card {demo.filename}", ImVec2(width, height), imgui.ChildFlags_.borders.value,
                          imgui.WindowFlags_.no_scrollbar.value | imgui.WindowFlags_.no_scroll_with_mouse.value)
        self.pictures.draw(demo.stem, width, PICTURE_ASPECT)
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

    def gallery(self) -> None:
        self.smooth_scroll()
        spacing = em_size(1.0)
        avail = imgui.get_content_region_avail().x
        columns = max(1, int((avail + spacing) // (em_size(CARD_WIDTH) + spacing)))
        card_width = (avail - (columns - 1) * spacing) / columns  # the cards fill the width
        self.category_in_view = self.categories[0].name
        for i, category in enumerate(self.categories):
            if i:
                imgui.dummy(ImVec2(0, em_size(0.6)))
            self.category_y[category.name] = imgui.get_cursor_pos_y()
            at_the_end = imgui.get_scroll_y() >= imgui.get_scroll_max_y() - 1  # the last categories can't reach the top
            if self.category_y[category.name] <= imgui.get_scroll_y() + em_size(3) or at_the_end:
                self.category_in_view = category.name
            big_text(category.name, 1.45, CATEGORY_TITLE)
            imgui.text_disabled(category.about)
            imgui.dummy(ImVec2(0, em_size(0.3)))
            for i, demo in enumerate(category.demos):
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
        self.pictures.draw(demo.stem, width)
        picture_bottom_right = imgui.get_item_rect_max()
        draw_tags(demo.tags(), ImVec2(picture_bottom_right.x - em_size(0.4), picture_bottom_right.y - em_size(0.4)))
        imgui.dummy(ImVec2(0, em_size(0.4)))
        rich_md.render(f"## {demo.label}\n\n{demo.text}")
        imgui.dummy(ImVec2(0, em_size(0.6)))

        if demo.where != "browser" and can_run_subprocess():
            if self.action(fa.ICON_FA_PLAY + "  Run", "Runs the demo on your machine, in a new window"):
                spawn_demo_file(str(demo.path))
        if self.action(fa.ICON_FA_CODE + "  View code",
                       "Shows its code: Python, and C++ side by side when there is a C++ version"):
            snippets = [code_snippet(demo.path, immapp.snippets.SnippetLanguage.python, "Python")]
            if demo.cpp_path is not None:
                snippets.append(code_snippet(demo.cpp_path, immapp.snippets.SnippetLanguage.cpp, "C++"))
            self.code_view = (demo, snippets)
        if demo.where != "desktop":
            if self.action(fa.ICON_FA_GLOBE + "  Open in the Python playground",
                           "Opens it in your browser, in the Python playground: edit its code, and run it again"):
                open_url(playground_url(demo))
        if demo.cpp_path is not None:
            if self.action(fa.ICON_FA_EXTERNAL_LINK_ALT + "  Open in the C++ explorer",
                           "Opens its C++ version in your browser (compiled to WebAssembly)"):
                open_url(explorer_url(demo))
        imgui.pop_style_var()

    def show_code(self) -> None:
        assert self.code_view is not None
        demo, snippets = self.code_view
        if imgui.button(fa.ICON_FA_ARROW_LEFT + "  All the demos"):
            self.code_view = None
            return
        imgui.same_line()
        big_text(demo.label, 1.3)
        lines = int(imgui.get_content_region_avail().y / imgui.get_text_line_height()) - 4
        for snippet in snippets:
            snippet.height_in_lines = lines
            snippet.max_height_in_lines = lines
        if len(snippets) == 2:
            immapp.snippets.show_side_by_side_snippets(snippets[0], snippets[1])
        else:
            immapp.snippets.show_code_snippet(snippets[0])

    def gui(self) -> None:
        self.pictures.new_frame()
        self.keep_smooth(self.pictures.still_loading() or self.scroll_target is not None)
        self.header()
        if self.code_view is not None:
            self.show_code()
            return
        avail = imgui.get_content_region_avail()
        detail_width = em_size(DETAIL_WIDTH)
        imgui.begin_child("gallery", ImVec2(avail.x - detail_width - em_size(1.0), avail.y))
        self.gallery()
        imgui.end_child()
        imgui.same_line(0, em_size(1.0))
        imgui.begin_child("detail", ImVec2(detail_width, avail.y))
        self.detail()
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
