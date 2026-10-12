"""wordcloud: what the demos talk about
=====================================

[wordcloud](https://github.com/amueller/word_cloud) packs the words of a text into an image, each sized by how often it
appears. Here, the words of this bundle's demos: the descriptions of all of them. Pick a shape and colors, or type
your own text.

<!--more-->

`WordCloud(...).generate(text)` counts the words, leaves out the most common ones of English (its `STOPWORDS`), and
places the most frequent first, as large as they fit. A mask gives the cloud its shape: here a circle or a heart, made
with numpy. The image comes out with a transparent background, so it follows the theme, and ImmVision shows it. A cloud
takes a fraction of a second: it is drawn again when a choice changes (once a slider is released).

Needs wordcloud: `pip install wordcloud`.
"""
import json
import re
from dataclasses import dataclass

import numpy as np
from wordcloud import STOPWORDS, WordCloud
from imgui_bundle import imgui, immvision, immapp, hello_imgui, rich_md
from imgui_bundle.demos_python.demo_utils import api_demos

CLOUD_MAX_WIDTH = 760.0  # the cloud's width at most, in points
SHAPES = ["Rectangle", "Circle", "Heart"]
COLORMAPS = ["viridis", "plasma", "cividis", "cool", "Set2", "tab10"]
MORE_STOPWORDS = {"see", "two", "one", "show", "shows", "e", "g", "etc", "use", "uses", "also", "will"}
YOUR_TEXT = "Type or paste a text here, then press Draw. The words that come back often are drawn larger."


def demos_text() -> str:
    """The descriptions of the bundle's demos, without the targets of their links"""
    with open(api_demos.demos_assets_folder() + "/demos_catalog.json", encoding="utf-8") as f:
        catalog = json.load(f)
    text = " ".join(demo["text"] for category in catalog["categories"] for demo in category["demos"])
    text = re.sub(r"\]\([^)]*\)", "]", text)  # [label](url) -> [label]
    return re.sub(r"https?://\S+", "", text)  # bare links


def mask(shape: str, width: int, height: int) -> np.ndarray | None:
    """Where the words may go: 0 inside the shape, 255 outside (as wordcloud wants it). None: the whole rectangle"""
    if shape == "Rectangle":
        return None
    y, x = np.mgrid[-1.0:1.0:height * 1j, -1.0:1.0:width * 1j]
    if shape == "Circle":
        inside = x**2 + y**2 < 0.95
    else:  # a heart: (x² + y² - 1)³ - x² y³ < 0, with y upward
        x, y = 1.25 * x, -1.25 * y + 0.2
        inside = (x**2 + y**2 - 1.0) ** 3 - x**2 * y**3 < 0.0
    return np.where(inside, 0, 255).astype(np.uint8)


def word_cloud(text: str, shape: str, colormap: str, max_words: int, seed: int, width: int, height: int) -> np.ndarray:
    """The cloud as an RGBA image, with a transparent background. width, height: in points"""
    scale = min(imgui.get_io().display_framebuffer_scale.x, 2.0)  # more pixels on a high density screen: sharp
    cloud = WordCloud(width=width, height=height, scale=scale, mask=mask(shape, width, height), mode="RGBA",
                      background_color=None, colormap=colormap, max_words=max_words, random_state=seed,
                      stopwords=STOPWORDS | MORE_STOPWORDS)
    image: np.ndarray = cloud.generate(text).to_array()
    return image


@dataclass
class AppState:
    source: int = 0  # 0: the demos' descriptions, 1: your text
    your_text: str = YOUR_TEXT
    shape: int = 0  # in SHAPES
    colormap: int = 0  # in COLORMAPS
    max_words: int = 150
    seed: int = 0  # "New layout" changes it
    image: np.ndarray | None = None
    drawn: tuple[object, ...] = ()  # what the image was drawn with
    drawn_size: tuple[int, int] = (0, 0)
    demos_text: str = ""


state = AppState()


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    if not state.demos_text:
        state.demos_text = demos_text()
    width = hello_imgui.em_size(12)
    imgui.set_next_item_width(width)
    _, state.source = imgui.combo("text", state.source, ["The demos' descriptions", "Your text"])
    imgui.set_next_item_width(width)
    _, state.shape = imgui.combo("shape", state.shape, SHAPES)
    imgui.set_next_item_width(width)
    _, state.colormap = imgui.combo("colors", state.colormap, COLORMAPS)
    imgui.set_next_item_width(width)
    _, state.max_words = imgui.slider_int("words", state.max_words, 20, 300)
    sliding = imgui.is_item_active()
    imgui.same_line()
    if imgui.button("New layout"):
        state.seed += 1
    text = state.demos_text
    if state.source == 1:
        _, state.your_text = imgui.input_text_multiline("##your_text", state.your_text,
                                                        imgui.ImVec2(-1, hello_imgui.em_size(5)))
        draw_clicked = imgui.button("Draw")
        text = state.your_text if (draw_clicked or not state.drawn) else str(state.drawn[0])

    # The cloud: as wide as the window, at most CLOUD_MAX_WIDTH; square for a shape. Drawn again when a choice changes
    # (once the slider is released), or when the window's width changes much
    avail_width = min(CLOUD_MAX_WIDTH, imgui.get_content_region_avail().x)
    w = int(avail_width if state.shape == 0 else min(avail_width, hello_imgui.em_size(30)))
    h = int(w * 0.55) if state.shape == 0 else w
    wanted = (text, state.shape, state.colormap, state.max_words, state.seed)
    resized = abs(w - state.drawn_size[0]) > hello_imgui.em_size(2)
    redraw = state.image is None or resized or (wanted != state.drawn and not sliding)
    if redraw:
        try:
            state.image = word_cloud(text, SHAPES[state.shape], COLORMAPS[state.colormap], state.max_words,
                                     state.seed, w, h)
        except ValueError:  # a text with no word left once the common ones are out
            state.image = np.zeros((h, w, 4), np.uint8)
        state.drawn, state.drawn_size = wanted, (w, h)
    assert state.image is not None

    immvision.push_color_order_rgb()
    immvision.image_display("##cloud", state.image, state.drawn_size, refresh_image=redraw)
    immvision.pop_color_order()


def main() -> None:
    immapp.run(gui, window_title="wordcloud: what the demos talk about", window_size=(800, 760), with_markdown=True)


if __name__ == "__main__":
    main()
