"""Health and wealth of nations, 1800 to 2100: an animated bubble chart fed by live open data.

Each bubble is a country: income per person across, life expectancy up, population as the
size, world region as the color. Press Play and two centuries go by. Click a bubble to pin
it and draw its path through time; pick other indicators for the axes.

The data are not bundled: at start, the app fetches them from Gapminder's Fast Track
dataset on GitHub, and the panel "Where the data comes from" shows each request as it
happens. Indicators you pick for an axis are fetched when you pick them. The same code
runs on the desktop (urllib in a thread) and in the browser (fetch), through
immapp.download_url_bytes_async, with the GUI and the downloads sharing one event loop.

With "Events" on, a small card fades in while the years pass through moments the data
show (the drought famines of 1876-1879, the Ethiopian famine of 1888-1892, the First
World War, the 1918 influenza pandemic, the Second World War, the famine in China, the eradication of
smallpox, COVID-19): a sourced one-line fact and, where a fitting public domain image
exists, a picture fetched live from Wikimedia Commons and credited there.

Data: based on free material from GAPMINDER.ORG, CC-BY LICENSE. Values after the current
year are projections; the app interpolates between yearly values to animate smoothly.

Run it:
    pip install imgui-bundle numpy
    python health_and_wealth.py

This chart comes from Hans Rosling (1948-2017) and Gapminder. His demonstration "200 Countries, 200 Years,
4 Minutes" (The Joy of Stats, BBC Four, 2010: https://www.youtube.com/watch?v=jbkSRLYSojo) made it famous.
Thank you, Hans.

Written by Claude (Anthropic) in a plain chat, from the bundle's guide for AI assistants alone
(https://imgui-bundle.pages.dev/llms.txt).
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import math
import time
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from imgui_bundle import (
    __bundle_pyodide__,
    em_size,
    em_to_vec2,
    hello_imgui,
    icons_fontawesome_4 as fa,  # the icon font Hello ImGui loads by default
    imgui,
    immapp,
    implot,
    imspinner,
    rich_md,
)

# ---------------------------------------------------------------------------
# Where the data come from
# ---------------------------------------------------------------------------
REPO = "open-numbers/ddf--gapminder--fasttrack"
BASE_URL = f"https://raw.githubusercontent.com/{REPO}/refs/heads/master/"
ATTRIBUTION = "Based on free material from GAPMINDER.ORG, CC-BY LICENSE"
ATTRIBUTION_URL = "https://www.gapminder.org/data/"
ROSLING_URL = "https://www.youtube.com/watch?v=jbkSRLYSojo"  # "200 Countries, 200 Years, 4 Minutes"

FIRST_YEAR, LAST_YEAR = 1800, 2100
N_YEARS = LAST_YEAR - FIRST_YEAR + 1
THIS_YEAR = time.gmtime().tm_year  # after it, the dataset's values are projections


@dataclass(frozen=True)
class Indicator:
    key: str  # the dataset's name for it
    title: str  # short, for the axis menus
    axis: str  # axis label, with the unit
    log: bool  # shown on a log scale
    fmt: str  # how one value reads in a tooltip
    default_range: Tuple[float, float] = (0.0, 1.0)  # the axis while its data are on their way

    @property
    def path(self) -> str:
        return f"countries_etc_datapoints/ddf--datapoints--{self.key}--by--country--time.csv"

    def format(self, v: float) -> str:
        return self.fmt.format(v) if math.isfinite(v) else "no data"


INCOME = Indicator("gdp_pcap", "Income per person", "Income per person (GDP per capita, PPP$, inflation-adjusted)",
                   True, "${:,.0f}", (300.0, 200000.0))
LIFE = Indicator("lex", "Life expectancy", "Life expectancy (years)", False, "{:.1f} years", (10.0, 95.0))
POPULATION = Indicator("pop", "Population", "Population", False, "{:,.0f}")
CHILD_MORTALITY = Indicator("child_mortality_0_5_year_olds_dying_per_1000_born", "Child mortality",
                            "Child mortality (deaths before age 5, per 1,000 born)", False, "{:.0f} per 1,000",
                            (0.0, 600.0))
BABIES = Indicator("children_per_woman_total_fertility", "Babies per woman", "Babies per woman", False, "{:.2f}",
                   (0.0, 9.0))
CO2 = Indicator("co2_pcap_cons", "CO2 per person", "CO2 emissions per person (tonnes, consumption-based)",
                True, "{:.2f} t", (0.01, 100.0))
AXIS_CHOICES = [INCOME, LIFE, CHILD_MORTALITY, BABIES, CO2]
COUNTRIES_PATH = "ddf--entities--geo--country.csv"

# Regions and their colors: the Okabe-Ito palette, distinct for color-blind readers too.
REGIONS = ["africa", "americas", "asia", "europe"]
REGION_NAMES = ["Africa", "Americas", "Asia", "Europe"]
REGION_COLORS = ["#E69F00", "#009E73", "#CC79A7", "#56B4E9"]


# ---------------------------------------------------------------------------
# Events: context cards for moments the data show. Each caption is a short, sourced
# fact; images are public domain files on Wikimedia Commons, chosen to be non-graphic.
# Where no freely licensed image fits the event fairly, the card is text only.
# ---------------------------------------------------------------------------
def commons_thumb_url(file_name: str, width: int = 330) -> str:
    """The address of a Commons thumbnail: the path comes from the MD5 of the file name.
    330 px is one of Wikimedia's standard thumbnail widths."""
    name = file_name.replace(" ", "_")
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name)
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


def commons_page_url(file_name: str) -> str:
    return "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(file_name.replace(" ", "_"))


@dataclass(frozen=True)
class Event:
    start: int
    end: int
    title: str
    caption: str
    source: str  # where the caption's figures come from
    source_url: str = ""  # a link to it, when there is a good one
    image_file: str = ""  # a file on Wikimedia Commons, or "" for a text-only card
    credit: str = ""  # who made the image, and its license (a Markdown link to it is added)
    more_sources: Tuple[Tuple[str, str, str], ...] = ()  # (what it supports, source, link)

    @property
    def key(self) -> str:
        return f"img:{self.start}"

    def markdown(self, image_width: int) -> str:
        """The card, as a small Markdown document. Its image is fetched through the app's
        download callback, so the request shows in the data panel like the others."""
        parts = []
        if self.image_file and image_width > 0:
            parts.append(f'<img src="{commons_thumb_url(self.image_file)}" width="{image_width}">')
        parts.append(f"**{self.title}**")
        parts.append(self.caption)
        # One credit per line, each ending with its link: in imgui-bundle 1.92.900 the renderer
        # can break a word in the middle when text follows a link on the same line.
        if self.image_file and image_width > 0:
            parts.append(f"<small>[{self.credit}]({commons_page_url(self.image_file)})</small>")
        figures = f"[{self.source}]({self.source_url})" if self.source_url else self.source
        parts.append(f"<small>Figures: {figures}</small>")
        for what, name, url in self.more_sources:
            parts.append(f"<small>{what}: [{name}]({url})</small>")
        return "\n\n".join(parts)


EVENTS = [
    Event(1876, 1879, "1876-1879: drought famines",
          "A record El Niño brought drought to India, China, Brazil and parts of Africa; "
          "the famines that followed killed tens of millions of people.",
          "Singh et al., 2018", "https://repository.library.noaa.gov/view/noaa/48315/noaa_48315_DS1.pdf"),
    Event(1888, 1892, "1888-1892: famine in Ethiopia",
          "Rinderpest, a cattle plague that arrived in 1887, killed most of the herds; with drought, "
          "it caused a famine in which an estimated one in three Ethiopians died.",
          "UN / FAO", "https://news.un.org/en/story/2010/10/355812"),
    # Shown until 1917: 1918 belongs to the pandemic, which the contrast below is about.
    Event(1914, 1917, "1914-1918: First World War",
          "About 15 million or more soldiers and civilians died. In the data, life expectancy falls "
          "in Europe while the other regions keep rising; in 1918, the pandemic strikes them all. "
          "The deepest fall is in the Ottoman Empire, where the Armenian genocide of 1915-1916 "
          "killed between 664,000 and 1.2 million people.",
          "Statista", "https://www.statista.com/statistics/1208625/first-world-war-fatalities-per-country/",
          more_sources=(("Armenian genocide", "USHMM",
                         "https://www.ushmm.org/information/press/press-releases/"
                         "museum-statement-on-the-100th-anniversary-of-the-armenian-genocide"),)),
    Event(1918, 1920, "1918: influenza pandemic",
          "About a third of the world's population was infected; at least 50 million people died.",
          "CDC", "https://archive.cdc.gov/www_cdc_gov/flu/pandemic-resources/1918-commemoration/1918-pandemic-history.htm",
          "Emergency hospital during Influenza epidemic, Camp Funston, Kansas - NCP 1603.jpg",
          "Photo: National Museum of Health and Medicine, public domain"),
    Event(1939, 1945, "1939-1945: Second World War",
          "An estimated 70 to 85 million deaths, with the heaviest losses in the Soviet Union and China.",
          "Statista"),
    Event(1959, 1961, "1959-1961: famine in China",
          "Estimates of excess deaths during the Great Leap Forward range from about 15 to 45 million; "
          "many demographic studies put them near 30 million.",
          "Population, 2012", "https://shs.cairn.info/article/E_POPU_1202_0329?lang=en"),
    Event(1967, 1980, "1967-1980: smallpox eradicated",
          "WHO intensified its campaign in 1967; in 1980 it declared smallpox eradicated, "
          "the first human disease ever eliminated.",
          "WHO", "https://www.who.int/news-room/spotlight/history-of-vaccination/history-of-smallpox-vaccination",
          "Directors of Global Smallpox Eradication Program.jpg", "Photo: CDC, public domain"),
    Event(2020, 2021, "2020-2021: COVID-19 pandemic",
          "WHO estimates 14.9 million excess deaths over these two years, directly or indirectly "
          "linked to the pandemic.",
          "WHO", "https://www.who.int/news/item/05-05-2022-14.9-million-excess-deaths-were-associated-with-the-COVID-19-pandemic-in-2020-and-2021",
          "SARS-CoV-2-CDC-23312.png", "Illustration: CDC, A. Eckert and D. Higgins, public domain"),
]


def hex_color(h: str, alpha: float = 1.0) -> imgui.ImVec4:
    h = h.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return imgui.ImVec4(r, g, b, alpha)


def scaled(c: imgui.ImVec4, k: float, alpha: float = 1.0) -> imgui.ImVec4:
    return imgui.ImVec4(c.x * k, c.y * k, c.z * k, alpha)


def human_bytes(n: int) -> str:
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{n / 1e3:.0f} kB"


def elided(text: str, width: float) -> str:
    """The text, shortened with an ellipsis to fit the width."""
    if imgui.calc_text_size(text).x <= width:
        return text
    while text and imgui.calc_text_size(text + "...").x > width:
        text = text[:-1]
    return text + "..."


def human_population(p: float) -> str:
    if not math.isfinite(p):
        return "no data"
    for limit, word in ((1e9, "billion"), (1e6, "million"), (1e3, "thousand")):
        if p >= limit:
            return f"{p / limit:.3g} {word}"
    return f"{p:.0f}"


# ---------------------------------------------------------------------------
# Fetching and parsing, with every request on display
# ---------------------------------------------------------------------------
@dataclass
class Source:
    """One file of the dataset, and what happened to it."""

    key: str
    title: str
    path: str
    state: str = "waiting"  # waiting, fetching, ready, failed
    size: int = 0
    rows: int = 0
    seconds: float = 0.0
    started: float = 0.0
    error: str = ""
    full_url: str = ""  # for files outside the dataset (the event images)
    page_url: str = ""  # where to credit them
    credit: str = ""

    @property
    def url(self) -> str:
        return self.full_url or BASE_URL + self.path

    @property
    def is_image(self) -> bool:
        return self.key.startswith("img:")


class DataStore:
    """Fetches the dataset's files, parses them into (country, year) matrices, and keeps
    a log of what it did, so the app can show it."""

    def __init__(self) -> None:
        self.sources: Dict[str, Source] = {"countries": Source("countries", "Countries and regions", COUNTRIES_PATH)}
        for ind in [POPULATION] + AXIS_CHOICES:
            self.sources[ind.key] = Source(ind.key, ind.title, ind.path)
        for ev in EVENTS:
            if ev.image_file:
                self.sources[ev.key] = Source(
                    ev.key, f"Image: {ev.title.split(': ')[1]}", ev.image_file,
                    full_url=commons_thumb_url(ev.image_file), page_url=commons_page_url(ev.image_file),
                    credit=ev.credit)
        self.images: Dict[str, bytes] = {}  # event image key -> encoded bytes (PNG or JPEG)
        self.log: List[Tuple[float, str]] = []
        self.t0 = time.perf_counter()
        self.ids: List[str] = []
        self.names: List[str] = []
        self.region: np.ndarray = np.zeros(0, dtype=np.int32)
        self.index: Dict[str, int] = {}
        self.values: Dict[str, np.ndarray] = {}  # indicator key -> (n_countries, N_YEARS), NaN = no data
        self.limits: Dict[str, Tuple[float, float]] = {}
        self.countries_ready: Optional[asyncio.Event] = None

    # ----- requests -------------------------------------------------------------
    def say(self, text: str) -> None:
        self.log.append((time.perf_counter() - self.t0, text))

    def start(self) -> None:
        """Begin fetching what the first view needs. Must be called inside the event loop."""
        self.countries_ready = asyncio.Event()
        self.say(f"Dataset: github.com/{REPO}")
        for key in ("countries", POPULATION.key, INCOME.key, LIFE.key):
            self.request(key)

    def request(self, key: str) -> None:
        """Fetch a file in the background, unless it's already here or on its way."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:  # no event loop (a test harness, say): nothing can be fetched now
            return
        if self.sources[key].state in ("waiting", "failed") and self.countries_ready is not None:
            self.sources[key].state = "fetching"
            asyncio.ensure_future(self.fetch(key))

    def request_images(self) -> None:
        for s in self.sources.values():
            if s.is_image:
                self.request(s.key)

    def refetch_all(self) -> None:
        loaded = [k for k, s in self.sources.items() if s.state in ("ready", "failed")]
        self.say("Fetching everything again")
        self.values.clear()
        self.limits.clear()
        self.images.clear()
        self.countries_ready = asyncio.Event()
        for k in loaded:
            old = self.sources[k]
            self.sources[k] = Source(k, old.title, old.path, full_url=old.full_url, page_url=old.page_url,
                                     credit=old.credit)
            self.request(k)

    def markdown_download(self, url: str) -> rich_md.MarkdownDownloadResult:
        """The Markdown renderer's download callback, called each frame for an image until
        it is ready or failed. It answers from this store, so images go through the same
        visible, logged path as the data."""
        result = rich_md.MarkdownDownloadResult()
        src = next((s for s in self.sources.values() if s.full_url == url), None)
        if src is None:
            result.status, result.error_message = rich_md.MarkdownDownloadStatus.failed, "Not a known source"
            return result
        if src.state == "waiting":  # never a retry: the renderer asks every frame, and a failure
            self.request(src.key)    # must be reported, not downloaded again (Retry is in the panel)
        if src.state == "ready" and src.key in self.images:
            result.fill_from_bytes(self.images[src.key])
            result.status = rich_md.MarkdownDownloadStatus.ready
        elif src.state == "failed":
            result.status, result.error_message = rich_md.MarkdownDownloadStatus.failed, src.error
        else:
            result.status = rich_md.MarkdownDownloadStatus.downloading
        return result

    def ready(self, *keys: str) -> bool:
        return all(self.sources[k].state == "ready" for k in keys)

    @property
    def busy(self) -> bool:
        return any(s.state == "fetching" for s in self.sources.values())

    async def fetch(self, key: str) -> None:
        src = self.sources[key]
        src.state, src.started, src.error = "fetching", time.perf_counter(), ""
        self.say(f"GET {src.url.split('/')[2] + ': ' if src.is_image else ''}{src.path.split('/')[-1]}")
        data = await immapp.download_url_bytes_async(src.url)
        src.seconds = time.perf_counter() - src.started
        if not data:
            src.state, src.error = "failed", "No answer from the server (offline?)"
            self.say(f"FAILED {src.title}: no data received")
            return
        src.size = len(data)
        if src.is_image:  # kept encoded: the GUI turns it into a texture on its own thread
            self.images[key] = data
            src.state = "ready"
            self.say(f"{src.title}: {human_bytes(src.size)}, in {src.seconds:.2f} s")
            return
        try:
            if key == "countries":
                src.rows = self.parse_countries(data.decode("utf-8"))
                assert self.countries_ready is not None
                self.countries_ready.set()
            else:
                assert self.countries_ready is not None
                await self.countries_ready.wait()  # rows are filed by country: the list comes first
                await asyncio.sleep(0)  # let a frame show the state before parsing
                src.rows = self.parse_datapoints(key, data.decode("utf-8"))
        except Exception as e:  # a malformed file shows why, the app keeps working
            src.state, src.error = "failed", f"Could not read it: {e}"
            self.say(f"FAILED {src.title}: {e}")
            return
        src.state = "ready"
        self.say(f"{src.title}: {human_bytes(src.size)}, {src.rows:,} rows, in {src.seconds:.2f} s")

    # ----- parsing ----------------------------------------------------------------
    def parse_countries(self, text: str) -> int:
        rows = list(csv.DictReader(io.StringIO(text)))  # names can hold quoted commas
        kept = [r for r in rows if r.get("world_4region") in REGIONS]
        self.ids = [r["country"] for r in kept]
        self.names = [r["name"] for r in kept]
        self.region = np.array([REGIONS.index(r["world_4region"]) for r in kept], dtype=np.int32)
        self.index = {c: i for i, c in enumerate(self.ids)}
        return len(rows)

    def parse_datapoints(self, key: str, text: str) -> int:
        """Rows are "country,year,value". Unknown countries and empty values are skipped."""
        m = np.full((len(self.ids), N_YEARS), np.nan)
        lines = text.splitlines()
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 3 or not parts[2]:
                continue
            i = self.index.get(parts[0])
            y = int(parts[1]) - FIRST_YEAR
            if i is not None and 0 <= y < N_YEARS:
                m[i, y] = float(parts[2])
        self.values[key] = m
        return len(lines) - 1

    # ----- queries ----------------------------------------------------------------
    def at(self, ind: Indicator, year: float) -> np.ndarray:
        """Every country's value at a fractional year, interpolated between yearly values
        (geometrically for indicators that grow by factors, like income and population)."""
        m = self.values[ind.key]
        y = min(max(year - FIRST_YEAR, 0.0), N_YEARS - 1.0)
        i = int(y)
        j, f = min(i + 1, N_YEARS - 1), y - i
        a, b = m[:, i], m[:, j]
        if ind.log or ind is POPULATION:
            with np.errstate(invalid="ignore", divide="ignore"):
                geometric: np.ndarray = np.exp(np.log(a) * (1.0 - f) + np.log(b) * f)
            return geometric
        return a * (1.0 - f) + b * f

    def axis_limits(self, ind: Indicator) -> Tuple[float, float]:
        """Fixed limits for an indicator, from robust percentiles of all its values: fixed,
        so that motion on the chart means change in the world."""
        if ind.key not in self.limits:
            v = self.values[ind.key]
            v = v[np.isfinite(v) & (v > 0)] if ind.log else v[np.isfinite(v)]
            lo, hi = np.percentile(v, [0.3, 99.9])
            if ind.log:
                self.limits[ind.key] = (lo / 1.5, hi * 1.5)
            else:
                # A quantity that can't be negative starts at zero: its extremes can be the story
                # (Ethiopia's life expectancy fell to about 5 years in the 1890 famine).
                pad = 0.05 * (hi - lo)
                self.limits[ind.key] = (0.0 if v.min() >= 0 else lo - pad, hi + pad)
        return self.limits[ind.key]


# ---------------------------------------------------------------------------
# The app
# ---------------------------------------------------------------------------
class App:
    SPEEDS = [2.0, 5.0, 10.0, 20.0]  # years per second

    def __init__(self) -> None:
        self.data = DataStore()
        self.year = float(FIRST_YEAR)
        self.playing = False
        self.autoplay_done = False  # play once by itself, when the data first arrive
        self.speed_index = 2
        self.with_projections = False
        self.x_ind, self.y_ind = INCOME, LIFE
        self.relimit = True  # set the axes' limits on the next frame
        self.hidden_regions: Set[int] = set()
        self.pinned: List[int] = []
        self.hovered: Optional[int] = None
        self.press_pos: Optional[imgui.ImVec2] = None
        self.search = ""
        self.controls_two_lines = False
        self.show_events = True
        self.card_event: Optional[Event] = None  # the card on screen, fading in or out
        self.card_alpha = 0.0
        self.card_corner = 0  # 0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right
        self.images_requested = False
        self.card_size = imgui.ImVec2(0.0, 0.0)  # measured last frame (the card sizes itself)
        self.card_rect: Optional[Tuple[imgui.ImVec2, imgui.ImVec2]] = None  # to keep the plot's hover off it
        self.plot_rect: Optional[Tuple[imgui.ImVec2, imgui.ImVec2]] = None

    # ----- time -------------------------------------------------------------------
    @property
    def end_year(self) -> int:
        return LAST_YEAR if self.with_projections else THIS_YEAR

    def advance(self) -> None:
        if self.playing:
            dt = min(imgui.get_io().delta_time, 0.1)
            self.year = min(self.year + dt * self.SPEEDS[self.speed_index], float(self.end_year))
            if self.year >= self.end_year:
                self.playing = False
        self.year = min(self.year, float(self.end_year))

    # ----- frame ------------------------------------------------------------------
    def gui(self) -> None:
        d = self.data
        if not self.autoplay_done and d.ready("countries", POPULATION.key, self.x_ind.key, self.y_ind.key):
            self.playing, self.autoplay_done = True, True
        if self.show_events and not self.images_requested and d.ready("countries", POPULATION.key):
            d.request_images()  # once the data are in: the images come second
            self.images_requested = True
        self.advance()
        # The chart moves while playing or loading: let the app idle only when it's still.
        fading = 0.0 < self.card_alpha < 1.0
        hello_imgui.get_runner_params().fps_idling.enable_idling = not (self.playing or d.busy or fading)

        self.handle_keys()
        self.gui_header()
        avail = imgui.get_content_region_avail()
        narrow = avail.x < em_size(60.0)  # on a phone, the side panel goes below the chart
        if narrow:
            self.gui_chart_area(imgui.ImVec2(avail.x, max(em_size(24.0), avail.y * 0.62)))
            imgui.begin_child("side", imgui.ImVec2(0.0, 0.0), imgui.ChildFlags_.always_use_window_padding)
            self.gui_side_panel()
            imgui.end_child()
        else:
            side_w = min(em_size(25.0), avail.x * 0.34)
            spacing = imgui.get_style().item_spacing.x
            self.gui_chart_area(imgui.ImVec2(avail.x - side_w - spacing, avail.y))
            imgui.same_line()
            imgui.begin_child("side", imgui.ImVec2(0.0, avail.y), imgui.ChildFlags_.always_use_window_padding)
            self.gui_side_panel()
            imgui.end_child()

    def gui_header(self) -> None:
        imgui.push_font(None, em_size(1.4))
        imgui.text("Health and wealth of nations")
        imgui.pop_font()
        # On the right, the state of the data, always in view.
        d = self.data
        n_ready = sum(s.state == "ready" for s in d.sources.values())
        n_asked = sum(s.state != "waiting" for s in d.sources.values())
        failed = any(s.state == "failed" for s in d.sources.values())
        if d.busy:
            text = f"Fetching live data, {n_ready} of {n_asked} files"
        elif failed:
            text = "Some data could not be fetched: see the panel"
        else:
            total = sum(s.size for s in d.sources.values())
            hosts = "GitHub and Wikimedia Commons" if any(s.is_image and s.state == "ready"
                                                           for s in d.sources.values()) else "GitHub"
            text = f"Live data from {hosts}: {n_ready} files, {human_bytes(total)}"
        w = imgui.calc_text_size(text).x + em_size(2.0)
        title_end = imgui.get_item_rect_max().x - imgui.get_window_pos().x
        if title_end + em_size(1.5) + w < imgui.get_window_width() - em_size(1.0):
            imgui.same_line(imgui.get_window_width() - w - em_size(1.0))
            imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + em_size(0.25))
        # (otherwise it goes on its own line, under the title)
        if d.busy:
            imspinner.spinner_ang("##loading", em_size(0.45), em_size(0.12),
                                  imgui.ImColor(imgui.get_style().color_(imgui.Col_.text)), imgui.ImColor(imgui.ImVec4(0, 0, 0, 0)))
        elif failed:
            imgui.text_colored(hex_color("#D55E00"), fa.ICON_FA_EXCLAMATION_TRIANGLE)
        else:
            imgui.text_colored(hex_color("#009E73"), fa.ICON_FA_CHECK)
        imgui.same_line()
        imgui.text_wrapped(text)  # on a phone, it wraps under the title

    # ----- the chart --------------------------------------------------------------
    def gui_chart_area(self, size: imgui.ImVec2) -> None:
        imgui.begin_child("chart_area", size)
        self.gui_chart_top_row()
        # one decision, used both here (the plot's height) and by the controls (their layout)
        check_w = (imgui.calc_text_size("Projections to 2100").x + imgui.calc_text_size("Events").x
                   + 2 * imgui.get_frame_height() + em_size(2.0))
        self.controls_two_lines = imgui.get_content_region_avail().x < em_size(29.0) + check_w
        lines = 2 if self.controls_two_lines else 1
        controls_h = lines * (imgui.get_frame_height() + imgui.get_style().item_spacing.y)
        plot_h = imgui.get_content_region_avail().y - controls_h
        self.gui_chart(imgui.ImVec2(-1.0, plot_h))
        self.gui_controls()
        imgui.end_child()

    def gui_chart_top_row(self) -> None:
        """Regions, clickable to hide or show them; then the axis menus."""
        dl = imgui.get_window_draw_list()
        for r, name in enumerate(REGION_NAMES):
            if r:
                imgui.same_line()
            hidden = r in self.hidden_regions
            p = imgui.get_cursor_screen_pos()
            label_w = imgui.calc_text_size(name).x
            if imgui.invisible_button(f"##region{r}", imgui.ImVec2(label_w + em_size(1.4), imgui.get_frame_height())):
                self.hidden_regions ^= {r}
            if imgui.is_item_hovered():
                imgui.set_tooltip(f"Click to {'show' if hidden else 'hide'} {name}")
            center = imgui.ImVec2(p.x + em_size(0.45), p.y + 0.5 * imgui.get_frame_height())
            col = hex_color(REGION_COLORS[r], 0.25 if hidden else 1.0)
            dl.add_circle_filled(center, em_size(0.38), imgui.get_color_u32(col))
            text_col = imgui.get_style().color_(imgui.Col_.text_disabled if hidden else imgui.Col_.text)
            dl.add_text(imgui.ImVec2(p.x + em_size(1.1), p.y + imgui.get_style().frame_padding.y),
                        imgui.get_color_u32(text_col), name)

        names = [ind.title for ind in AXIS_CHOICES]
        labels_w = imgui.calc_text_size("Across").x + imgui.calc_text_size("Up").x + em_size(2.5)
        menu_w = em_size(10.5)
        regions_end = imgui.get_item_rect_max().x - imgui.get_window_pos().x
        if regions_end + em_size(1.5) + 2 * menu_w + labels_w <= imgui.get_window_width():
            imgui.same_line(imgui.get_window_width() - 2 * menu_w - labels_w)
        else:  # narrow: a line of their own, split evenly
            menu_w = max(em_size(6.0), 0.5 * (imgui.get_content_region_avail().x - labels_w))
        for label, attr in (("Across", "x_ind"), ("Up", "y_ind")):
            imgui.set_next_item_width(menu_w)
            current = getattr(self, attr)
            changed, i = imgui.combo(label, AXIS_CHOICES.index(current), names)
            if changed:
                setattr(self, attr, AXIS_CHOICES[i])
                self.data.request(AXIS_CHOICES[i].key)  # fetched now if it isn't here yet
                self.relimit = True
            if label == "Across":
                imgui.same_line()

    def gui_chart(self, size: imgui.ImVec2) -> None:
        d = self.data
        xi, yi = self.x_ind, self.y_ind
        needed = ("countries", POPULATION.key, xi.key, yi.key)
        ready = d.ready(*needed)
        flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text
        space = imgui.get_content_region_avail()  # the chart's size (`size` may be 0: fill)
        if not implot.begin_plot("##bubbles", size, flags):
            return
        # On a narrow chart (a phone), a long label would run off its edges: the indicator's short title instead
        x_label = xi.axis if imgui.calc_text_size(xi.axis).x < space.x - em_size(4.0) else xi.title
        y_label = yi.axis if imgui.calc_text_size(yi.axis).x < space.y - em_size(4.0) else yi.title
        implot.setup_axes(x_label, y_label)
        if xi.log:
            implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.log10)
        if yi.log:
            implot.setup_axis_scale(implot.ImAxis_.y1, implot.Scale_.log10)
        if ready:
            cond = imgui.Cond_.always if self.relimit else imgui.Cond_.once
            implot.setup_axis_limits(implot.ImAxis_.x1, *d.axis_limits(xi), cond)
            implot.setup_axis_limits(implot.ImAxis_.y1, *d.axis_limits(yi), cond)
            self.relimit = False
        else:  # sensible axes while waiting; the data's own limits apply when they arrive
            implot.setup_axis_limits(implot.ImAxis_.x1, *xi.default_range, imgui.Cond_.always)
            implot.setup_axis_limits(implot.ImAxis_.y1, *yi.default_range, imgui.Cond_.always)
            self.relimit = True
        implot.setup_finish()
        # Double-click restores the chart's fixed axes, rather than fitting to this year's
        # bubbles: fixed axes are what make motion on the chart mean change in the world.
        if implot.is_plot_hovered() and imgui.is_mouse_double_clicked(0):
            self.relimit = True

        self.draw_year_watermark()
        if ready:
            self.draw_bubbles()
        else:
            self.draw_waiting_message([d.sources[k] for k in needed])
        implot.end_plot()
        self.gui_event_card()

    def draw_year_watermark(self) -> None:
        """The year, huge and faint behind the bubbles."""
        pos, size = implot.get_plot_pos(), implot.get_plot_size()
        text = f"{int(self.year)}"
        big = size.y * 0.42
        scale = big / imgui.get_font_size()
        w = imgui.calc_text_size(text).x * scale
        dl = implot.get_plot_draw_list()
        implot.push_plot_clip_rect()
        col = imgui.get_style().color_(imgui.Col_.text)
        corner = imgui.ImVec2(pos.x + 0.5 * (size.x - w), pos.y + 0.5 * (size.y - big))
        dl.add_text(imgui.get_font(), big, corner, imgui.get_color_u32(imgui.ImVec4(col.x, col.y, col.z, 0.07)), text)
        if self.year > THIS_YEAR:
            note = "projection"
            note_size = big * 0.22
            nw = imgui.calc_text_size(note).x * note_size / imgui.get_font_size()
            dl.add_text(imgui.get_font(), note_size, imgui.ImVec2(pos.x + 0.5 * (size.x - nw), corner.y + big * 1.02),
                        imgui.get_color_u32(imgui.ImVec4(col.x, col.y, col.z, 0.12)), note)
        implot.pop_plot_clip_rect()

    def draw_waiting_message(self, sources: List[Source]) -> None:
        pos, size = implot.get_plot_pos(), implot.get_plot_size()
        failed = [s for s in sources if s.state == "failed"]
        if failed:
            lines = [f"Could not fetch {', '.join(s.title for s in failed)}.", "Retry from the panel on the right."]
        else:
            lines = ["Fetching the data from GitHub:"] + [
                f"{fa.ICON_FA_CHECK if s.state == 'ready' else fa.ICON_FA_CLOCK}  {s.title}" for s in sources
            ]
        dl = implot.get_plot_draw_list()
        line_h = imgui.get_text_line_height_with_spacing()
        y = pos.y + 0.5 * size.y - 0.5 * line_h * len(lines)
        col = imgui.get_color_u32(imgui.Col_.text)
        for line in lines:
            w = imgui.calc_text_size(line).x
            dl.add_text(imgui.ImVec2(pos.x + 0.5 * (size.x - w), y), col, line)
            y += line_h

    def draw_bubbles(self) -> None:
        d = self.data
        xi, yi = self.x_ind, self.y_ind
        x, y, pop = d.at(xi, self.year), d.at(yi, self.year), d.at(POPULATION, self.year)
        visible = np.isfinite(x) & np.isfinite(y) & np.isfinite(pop) & (pop > 0)
        if xi.log:
            visible &= x > 0
        if yi.log:
            visible &= y > 0
        for hidden in self.hidden_regions:
            visible &= d.region != hidden
        idx = np.nonzero(visible)[0]
        idx = idx[np.argsort(-pop[idx])]  # the largest first, so the small ones stay visible on top

        plot_size = implot.get_plot_size()
        pop_max = np.nanmax(d.values[POPULATION.key])
        r_max = 0.085 * min(plot_size.x, plot_size.y)
        radius = np.maximum(r_max * np.sqrt(pop[idx] / pop_max), 2.0).astype(np.float32)

        region_fill = [imgui.color_convert_float4_to_u32(hex_color(c, 0.85)) for c in REGION_COLORS]
        region_line = [imgui.color_convert_float4_to_u32(scaled(hex_color(c), 0.6)) for c in REGION_COLORS]

        # trails of the pinned countries, under the bubbles
        last = int(min(max(self.year - FIRST_YEAR, 0), N_YEARS - 1))
        for c in self.pinned:
            tx = np.append(d.values[xi.key][c, : last + 1], x[c])
            ty = np.append(d.values[yi.key][c, : last + 1], y[c])
            ok = np.isfinite(tx) & np.isfinite(ty)
            if xi.log:
                ok &= tx > 0
            if yi.log:
                ok &= ty > 0
            if ok.sum() > 1:
                spec = implot.Spec(line_color=hex_color(REGION_COLORS[d.region[c]], 0.7), line_weight=1.5)
                implot.plot_line(f"##trail{c}", tx[ok], ty[ok], spec)

        # The bubbles themselves, drawn as circles. ImPlot's circle markers are a fixed 10-point
        # polygon, round enough for small markers but visibly faceted at bubble sizes; the draw
        # list's circles take their number of segments from the radius.
        centers = [implot.plot_to_pixels(float(x[c]), float(y[c])) for c in idx]
        dl = implot.get_plot_draw_list()
        implot.push_plot_clip_rect()
        for k, c in enumerate(idx.tolist()):
            r, region = float(radius[k]), int(d.region[c])
            dl.add_circle_filled(centers[k], r, region_fill[region])
            dl.add_circle(centers[k], r, region_line[region], 0, 1.0)
        implot.pop_plot_clip_rect()

        self.handle_pointer(idx, centers, x, y, pop, radius)
        self.draw_labels(idx, centers, radius)
        self.update_event_card(centers)

    def handle_pointer(self, idx: np.ndarray, centers: List[imgui.ImVec2], x: np.ndarray, y: np.ndarray,
                       pop: np.ndarray, radius: np.ndarray) -> None:
        """Hover shows a country; a click (not a drag, which pans) pins or unpins it."""
        self.hovered = None
        mouse_on_card = self.card_rect is not None and (
            self.card_rect[0].x <= imgui.get_mouse_pos().x <= self.card_rect[1].x
            and self.card_rect[0].y <= imgui.get_mouse_pos().y <= self.card_rect[1].y)
        if not implot.is_plot_hovered() or mouse_on_card:
            self.press_pos = None
            return
        mouse = imgui.get_mouse_pos()
        best, best_r = None, 1e9
        for k, c in enumerate(idx):
            p = centers[k]
            r = float(radius[k])
            if (p.x - mouse.x) ** 2 + (p.y - mouse.y) ** 2 <= (r + 2) ** 2 and r < best_r:
                best, best_r = int(c), r  # the smallest bubble under the mouse is the one on top
        self.hovered = best
        if imgui.is_mouse_clicked(0):
            self.press_pos = mouse
        if imgui.is_mouse_released(0) and self.press_pos is not None:
            moved = (mouse.x - self.press_pos.x) ** 2 + (mouse.y - self.press_pos.y) ** 2
            if moved < 16 and best is not None:
                self.toggle_pin(best)
            self.press_pos = None
        if best is not None:
            self.country_tooltip(best, x, y, pop)

    def country_tooltip(self, c: int, x: np.ndarray, y: np.ndarray, pop: np.ndarray) -> None:
        d = self.data
        imgui.begin_tooltip()
        imgui.push_font(None, em_size(1.2))
        imgui.text(d.names[c])
        imgui.pop_font()
        imgui.text_colored(hex_color(REGION_COLORS[d.region[c]]), REGION_NAMES[d.region[c]])
        imgui.text(f"{self.x_ind.title}: {self.x_ind.format(float(x[c]))}")
        imgui.text(f"{self.y_ind.title}: {self.y_ind.format(float(y[c]))}")
        imgui.text(f"Population: {human_population(float(pop[c]))}")
        imgui.text_disabled("Click to " + ("unpin" if c in self.pinned else "pin and draw its path"))
        imgui.end_tooltip()

    def draw_labels(self, idx: np.ndarray, centers: List[imgui.ImVec2], radius: np.ndarray) -> None:
        dl = implot.get_plot_draw_list()
        implot.push_plot_clip_rect()
        text_col = imgui.get_color_u32(imgui.Col_.text)
        where = {int(c): (centers[k], float(radius[k])) for k, c in enumerate(idx)}
        for c in set(self.pinned) | ({self.hovered} if self.hovered is not None else set()):
            if c not in where:
                continue
            p, r = where[c]
            dl.add_circle(p, r + 1.5, text_col, 0, 2.0)
            if c in self.pinned:
                dl.add_text(imgui.ImVec2(p.x + r + 4, p.y - 0.5 * imgui.get_text_line_height()), text_col,
                            self.data.names[c])
        implot.pop_plot_clip_rect()

    # ----- event cards ----------------------------------------------------------
    def current_event(self) -> Optional[Event]:
        for ev in EVENTS:
            if ev.start - 0.2 <= self.year <= ev.end + 1.0:
                return ev
        return None

    def card_width(self, plot_size: imgui.ImVec2) -> Tuple[float, bool]:
        compact = plot_size.x < em_size(32.0)  # on a phone: text only, so the card hides fewer bubbles
        return min(em_size(16.0), plot_size.x * (0.5 if compact else 0.4)), compact

    def update_event_card(self, centers: List[imgui.ImVec2]) -> None:
        """Inside the plot: which card shows, how faded, and in which corner. A new card goes
        where it hides the fewest bubbles, and stays there."""
        ev = self.current_event() if self.show_events else None
        dt = min(imgui.get_io().delta_time, 0.1)
        if ev is not None and ev is not self.card_event and self.card_alpha <= 0.0:
            self.card_event, self.card_corner = ev, -1
        target = 1.0 if (ev is not None and ev is self.card_event) else 0.0
        self.card_alpha += (dt / 0.35) * (1.0 if target > self.card_alpha else -1.0)
        self.card_alpha = min(max(self.card_alpha, 0.0), 1.0)
        pos, size = implot.get_plot_pos(), implot.get_plot_size()
        self.plot_rect = (pos, imgui.ImVec2(pos.x + size.x, pos.y + size.y))
        if self.card_corner < 0 and self.card_alpha > 0.0:
            w = self.card_width(size)[0]
            h = self.card_size.y if self.card_size.y > 0 else em_size(14.0)
            corners = self.card_corners(w, h)
            def covered(c: imgui.ImVec2) -> int:
                return sum(c.x <= p.x <= c.x + w and c.y <= p.y <= c.y + h for p in centers)

            self.card_corner = min(range(4), key=lambda i: (covered(corners[i]), i))

    def card_corners(self, w: float, h: float) -> List[imgui.ImVec2]:
        assert self.plot_rect is not None  # set by the chart, which places the card
        (x0, y0), (x1, y1) = (self.plot_rect[0].x, self.plot_rect[0].y), (self.plot_rect[1].x, self.plot_rect[1].y)
        m = em_size(0.8)
        return [imgui.ImVec2(x0 + m, y0 + m), imgui.ImVec2(x1 - m - w, y0 + m),
                imgui.ImVec2(x0 + m, y1 - m - h), imgui.ImVec2(x1 - m - w, y1 - m - h)]

    def gui_event_card(self) -> None:
        """After the plot: the card as a small Markdown document, over the chosen corner."""
        self.card_rect = None
        if self.card_alpha <= 0.0 or self.card_event is None or self.plot_rect is None or self.card_corner < 0:
            return
        size = imgui.ImVec2(self.plot_rect[1].x - self.plot_rect[0].x, self.plot_rect[1].y - self.plot_rect[0].y)
        w, compact = self.card_width(size)
        h = self.card_size.y if self.card_size.y > 0 else em_size(14.0)
        p0 = self.card_corners(w, h)[self.card_corner]
        pad = imgui.get_style().window_padding.x
        # The image goes in once it's here: while it downloads, or if it failed, the card is
        # text only, rather than showing the renderer's placeholder at full width.
        ev = self.card_event
        image_here = ev.image_file != "" and self.data.sources[ev.key].state == "ready"
        image_width = int(w - 2 * pad) if image_here and not compact else 0

        back = imgui.get_cursor_screen_pos()  # the card floats: the layout continues where it was
        imgui.set_cursor_screen_pos(p0)
        imgui.push_style_var(imgui.StyleVar_.alpha, self.card_alpha)
        bg = imgui.get_style().color_(imgui.Col_.popup_bg)
        imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(bg.x, bg.y, bg.z, 0.92))
        flags = imgui.ChildFlags_.borders | imgui.ChildFlags_.auto_resize_y | imgui.ChildFlags_.always_use_window_padding
        imgui.begin_child("event_card", imgui.ImVec2(w, 0.0), flags, imgui.WindowFlags_.no_scrollbar)
        rich_md.render_unindented(self.card_event.markdown(image_width))
        self.card_size = imgui.get_window_size()
        imgui.end_child()
        imgui.pop_style_color()
        imgui.pop_style_var()
        self.card_rect = (p0, imgui.ImVec2(p0.x + w, p0.y + self.card_size.y))
        imgui.set_cursor_screen_pos(back)

    def toggle_pin(self, c: int) -> None:
        if c in self.pinned:
            self.pinned.remove(c)
        else:
            self.pinned.append(c)

    # ----- the timeline -------------------------------------------------------------
    def toggle_play(self) -> None:
        if not self.playing and self.year >= self.end_year:
            self.year = float(FIRST_YEAR)  # at the end, Play starts over
        self.playing = not self.playing

    def handle_keys(self) -> None:
        """Space plays or pauses, except while typing (in the search box, say)."""
        io = imgui.get_io()
        if not io.want_text_input and imgui.is_key_pressed(imgui.Key.space, False):
            self.toggle_play()

    def gui_controls(self) -> None:
        icon = fa.ICON_FA_PAUSE if self.playing else fa.ICON_FA_PLAY
        # The button doesn't take keyboard focus: Space would otherwise both "click" it and
        # toggle play through the shortcut, and cancel itself out.
        imgui.push_item_flag(imgui.ItemFlags_.no_nav, True)
        if imgui.button(f"{icon}###play", em_to_vec2(2.6, 0)):
            self.toggle_play()
        imgui.pop_item_flag()
        if imgui.is_item_hovered():
            imgui.set_tooltip("Play or pause (Space)")
        imgui.same_line()
        check_w = (imgui.calc_text_size("Projections to 2100").x + imgui.calc_text_size("Events").x
                   + 2 * imgui.get_frame_height() + em_size(2.0))
        two_lines = self.controls_two_lines
        right_w = em_size(9.0) + (0.0 if two_lines else check_w)
        imgui.set_next_item_width(max(em_size(6.0), imgui.get_content_region_avail().x - right_w))
        imgui.push_style_var(imgui.StyleVar_.grab_min_size, em_size(0.35))  # a thin grab: the year stays readable
        changed, self.year = imgui.slider_float("##year", self.year, FIRST_YEAR, self.end_year, "%.0f")
        if changed:
            self.playing = False
        self.draw_timeline_marks()
        imgui.pop_style_var()
        imgui.same_line()
        imgui.set_next_item_width(em_size(8.0))
        speeds = [f"{s:.0f} years/s" for s in self.SPEEDS]
        _, self.speed_index = imgui.combo("##speed", self.speed_index, speeds)
        if not two_lines:
            imgui.same_line()
        _, self.with_projections = imgui.checkbox("Projections to 2100", self.with_projections)
        if imgui.is_item_hovered():
            imgui.set_tooltip(f"After {THIS_YEAR}, the dataset's values are projections.")
        imgui.same_line()
        _, self.show_events = imgui.checkbox("Events", self.show_events)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Context cards for events the data show: pandemics, wars, famines, eradications.")

    def draw_timeline_marks(self) -> None:
        """On the year slider: a faint band for each event, a tick where it starts, and its name
        on hover; a shade over the projected years. Uses the slider's own geometry: the grab's
        center moves over the frame minus the grab's width and a 2-pixel padding on each side."""
        p0, p1 = imgui.get_item_rect_min(), imgui.get_item_rect_max()
        grab = imgui.get_style().grab_min_size
        x0, x1 = p0.x + 2.0 + 0.5 * grab, p1.x - 2.0 - 0.5 * grab
        span = float(self.end_year - FIRST_YEAR)
        def x_of(year: float) -> float:
            return x0 + (min(max(year, FIRST_YEAR), self.end_year) - FIRST_YEAR) / span * (x1 - x0)

        dl = imgui.get_window_draw_list()
        text = imgui.get_style().color_(imgui.Col_.text)
        if self.end_year > THIS_YEAR:
            dl.add_rect_filled(imgui.ImVec2(x_of(THIS_YEAR), p0.y + 1), imgui.ImVec2(p1.x - 1, p1.y - 1),
                               imgui.get_color_u32(imgui.ImVec4(text.x, text.y, text.z, 0.06)))
        if not self.show_events:
            return
        mark = hex_color("#E69F00")
        hovered_event = None
        mouse = imgui.get_mouse_pos()
        for ev in EVENTS:
            if ev.start > self.end_year:
                continue
            a, b = x_of(ev.start), max(x_of(ev.end + 1), x_of(ev.start) + 3.0)
            dl.add_rect_filled(imgui.ImVec2(a, p0.y + 2), imgui.ImVec2(b, p1.y - 2),
                               imgui.get_color_u32(imgui.ImVec4(mark.x, mark.y, mark.z, 0.22)))
            dl.add_line(imgui.ImVec2(a, p0.y + 2), imgui.ImVec2(a, p1.y - 2),
                        imgui.get_color_u32(imgui.ImVec4(mark.x, mark.y, mark.z, 0.9)), 2.0)
            if imgui.is_item_hovered() and a - 3 <= mouse.x <= b + 3:
                hovered_event = ev
        if hovered_event is not None and not imgui.is_item_active():
            imgui.set_tooltip(hovered_event.title)

    # ----- the side panel -----------------------------------------------------------
    def gui_side_panel(self) -> None:
        self.gui_data_sources()
        imgui.spacing()
        imgui.separator()
        self.gui_countries()

    def gui_data_sources(self) -> None:
        d = self.data
        imgui.text(f"{fa.ICON_FA_DATABASE}  Where the data comes from")
        imgui.push_text_wrap_pos(0.0)  # a narrow panel (a phone, or beside the code) wraps them
        imgui.text_disabled(f"Data: {REPO} on GitHub")
        imgui.text_disabled("Images: commons.wikimedia.org")
        imgui.pop_text_wrap_pos()
        imgui.spacing()
        for s in d.sources.values():
            if s.state == "waiting":
                continue  # files nobody asked for yet
            imgui.push_id(s.key)
            if s.state == "fetching":
                imspinner.spinner_ang("##sp", em_size(0.35), em_size(0.1),
                                      imgui.ImColor(imgui.get_style().color_(imgui.Col_.text)),
                                      imgui.ImColor(imgui.ImVec4(0, 0, 0, 0)))
            elif s.state == "ready":
                imgui.text_colored(hex_color("#009E73"), fa.ICON_FA_CHECK)
            else:
                imgui.text_colored(hex_color("#D55E00"), fa.ICON_FA_TIMES)
            imgui.same_line()
            imgui.text(s.title)
            if s.state == "ready":
                rows = "" if s.is_image else f", {s.rows:,} rows"
                info = f"{human_bytes(s.size)}{rows}, {s.seconds:.2f} s"
            elif s.state == "fetching":
                info = f"downloading, {time.perf_counter() - s.started:.1f} s"
            else:
                info = s.error
            imgui.same_line(imgui.get_window_width() - imgui.calc_text_size(info).x - em_size(1.0))
            imgui.text_disabled(info)
            imgui.text_disabled("    " + elided(s.path.split("/")[-1], imgui.get_content_region_avail().x - em_size(2.0)))
            if imgui.is_item_hovered():
                imgui.set_tooltip(s.url)
            if s.is_image:
                imgui.text_disabled("    ")
                imgui.same_line(0.0, 0.0)
                imgui.text_link_open_url(elided(f"{s.credit} (Wikimedia Commons)",
                                                imgui.get_content_region_avail().x - em_size(1.0)), s.page_url)
            if s.state == "failed" and imgui.small_button("Retry"):
                d.request(s.key)
            imgui.pop_id()
        imgui.spacing()
        if imgui.button(f"{fa.ICON_FA_SYNC}  Fetch it all again"):
            d.refetch_all()
            self.autoplay_done = True  # stay at the current year

        # the log of requests, newest at the bottom
        imgui.spacing()
        imgui.text_disabled("Requests")
        log_h = em_size(7.0)
        if imgui.begin_child("log", imgui.ImVec2(0.0, log_h), imgui.ChildFlags_.borders):
            for t, line in d.log[-60:]:
                imgui.text_disabled(f"{t:6.2f} s")
                imgui.same_line()
                imgui.text_wrapped(line)
            if imgui.get_scroll_y() >= imgui.get_scroll_max_y() - 1:
                imgui.set_scroll_here_y(1.0)  # follow new lines, unless the user scrolled up
        imgui.end_child()
        # The credits, in markdown: its links wrap on a narrow panel
        imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
        rich_md.render_unindented(f"""
            [{ATTRIBUTION}]({ATTRIBUTION_URL})

            The chart is Hans Rosling's: [200 countries, 200 years, 4 minutes]({ROSLING_URL}). Thank you, Hans.
            """)
        imgui.pop_style_color()

    def gui_countries(self) -> None:
        d = self.data
        imgui.text(f"{fa.ICON_FA_THUMBTACK}  Pinned countries")
        if not d.ids:
            imgui.text_disabled("Available once the data arrive.")
            return
        imgui.set_next_item_width(-1.0)
        _, self.search = imgui.input_text_with_hint("##search", f"{fa.ICON_FA_SEARCH}  Find a country to pin",
                                                    self.search)
        if self.search:
            matches = [i for i, n in enumerate(d.names) if self.search.lower() in n.lower()][:8]
            for i in matches:
                if imgui.selectable(f"{d.names[i]}##find{i}", i in self.pinned)[0]:
                    self.toggle_pin(i)
                    self.search = ""
        for c in list(self.pinned):
            imgui.push_id(c)
            if imgui.small_button(fa.ICON_FA_TIMES):
                self.pinned.remove(c)
            imgui.same_line()
            imgui.color_button("##swatch", hex_color(REGION_COLORS[d.region[c]]),
                               imgui.ColorEditFlags_.no_tooltip | imgui.ColorEditFlags_.no_border,
                               em_to_vec2(0.7, 0.7))
            imgui.same_line()
            imgui.text(d.names[c])
            imgui.pop_id()
        if not self.pinned:
            imgui.text_disabled("Click a bubble, or search above.")


# ---------------------------------------------------------------------------
# Running: the GUI and the downloads share one event loop
# ---------------------------------------------------------------------------
def markdown_options(data: DataStore) -> rich_md.MarkdownOptions:
    """Markdown with URL images served by the data store, and a <small> tag for credits."""
    options = rich_md.MarkdownOptions()
    options.callbacks.on_download_data = data.markdown_download

    def on_html_span(tag: str, opening: bool) -> bool:
        if tag != "small":
            return False  # the renderer handles its own tags (sub, sup, kbd, mark)
        if opening:
            imgui.push_font(None, em_size(0.82))
            imgui.push_style_color(imgui.Col_.text, imgui.get_style().color_(imgui.Col_.text_disabled))
        else:
            imgui.pop_style_color()
            imgui.pop_font()
        return True

    options.callbacks.on_html_span = on_html_span
    return options


def addons_for(app: "App") -> immapp.AddOnsParams:
    addons = immapp.AddOnsParams()
    addons.with_implot = True
    addons.with_markdown_options = markdown_options(app.data)
    return addons


_app: Optional[App] = None  # created by run_app()


def gui() -> None:
    """The app's frame (run_app() creates the app)"""
    assert _app is not None
    _app.gui()


async def run_app() -> None:
    global _app
    _app = App()
    _app.data.start()  # the requests start now, while the window opens
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Health and wealth of nations"
    params.app_window_params.window_geometry.size = (1400, 860)
    params.callbacks.show_gui = gui
    await immapp.run_async(params, addons_for(_app))


def main() -> None:
    if __bundle_pyodide__:
        asyncio.ensure_future(run_app())  # the browser's event loop is already running
    else:
        asyncio.run(run_app())


if __name__ == "__main__":
    main()
