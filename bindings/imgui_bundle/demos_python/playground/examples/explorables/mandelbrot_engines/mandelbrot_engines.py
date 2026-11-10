"""One Mandelbrot set, four engines: Python, numpy, C++, and a deep zoom

One Mandelbrot picture, computed by the engine you choose: Python, numpy, C++, or a C++ deep zoom down to 10^300.
Dive to famous places, split the view to compare two engines, and read how each one works beside its code.
Python draws the GUI; an engine only fills arrays of numbers, and the C++ is 70 lines loaded with ctypes, on the
desktop and in the browser.

This file is its own narrative (narrative programming, see imgui_rich_md): the ::md sections below are the texts
shown beside the picture, next to the code they explain. The C++ loops are in mandel_kernels.cpp.
"""

r"""::md Intro
# One Mandelbrot set, four engines
Every pixel is a number $c$. Iterate $z \leftarrow z^2 + c$ from $z = 0$, and count the steps until $|z| > 16$:
the count gives the color. Points that never escape are in the set, in black.

Pick a place and an engine on the card at the bottom left, and watch the time. The gauge on the right shows how deep
we are: its white part, down to a zoom of 10^13, is where every engine works. Its orange part is for the
perturbation only.
"""

r"""::md Help
**Moving around**
* **Wheel**: zoom, around the mouse. **Drag**: move the view.
* **Double click**: dive towards the clicked point.
* The arrow, bottom left: back to the previous view.

**The card, bottom left**
* The **place's name** is a menu of places. The **zoom** beside it is a menu of deeper views of that place.
* The **engine's name** is a menu: pick another one, and watch its time.
* **Split**: a second engine draws the right part of the picture. Drag the divider; each side has its own menu.
* The gear: the iterations and the colors. The bookmark: add this view to my places (a file beside the demo).

**Engines**
* Every engine gets the same time for a picture: 0.3 s, and much less while the view moves.
* An engine that cannot afford all the pixels computes one out of 4, 16 or 64.
  **All the pixels** then computes them all, a little at each frame: the picture fills in, with its
  progress and a button to cancel. It starts by itself when it would take less than 2.5 s.

**The gauge** on the right: how deep the view is. White: every engine works. Orange: the perturbation only.
"""

# ruff: noqa: E402  # the story comes first
import ctypes
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np
from imgui_bundle import em_size, hello_imgui, icons_fontawesome_6, imgui, imgui_kit, immapp, immvision, rich_md

THREADS = os.cpu_count() or 4  # the bands of rows computed at once by the C++ engines (in a browser: one)
MOVING_BUDGET = 0.04  # seconds for a picture while the view moves. An engine that cannot afford all the pixels
STILL_BUDGET = 0.3  # in its budget computes one out of 4, 16 or 64. This one: once the view stopped
BAND_ROWS = 4  # the C++ engines compute the picture in bands of this many rows
SLICE_SECONDS = 0.03  # "All the pixels" computes this long at each frame
QUICK_SECONDS = 2.5  # and starts by itself, once the view stopped, when it would take less than this
REPAINT_SECONDS = 0.4  # and its picture fills in at this pace
WHOLE_SET = ("-0.6", "0", 3.4)  # a view: the center (re, im), with as many digits as needed, and the width
ESCAPE2 = 256.0  # |z| > 16, squared
IN_BROWSER = sys.platform == "emscripten"
HERE = Path(__file__).parent

Counts = tuple[np.ndarray, np.ndarray]  # for each pixel: its number of steps, and |z|^2 at the last one
# An engine computes step by step. At each step it gives: how far it is (0 to 1), its arrays so far, and which rows
# of them are ready. So a long picture can be computed a little at each frame: the page stays alive, and fills in.
Step = tuple[float, Counts, np.ndarray]
Steps = Iterator[Step]


def whole(steps: Steps) -> Counts:
    """Runs an engine to its end, at once"""
    *_, (_fraction, counts, _ready) = steps
    return counts


r"""::md View
### What an engine receives, and returns
Every engine is one function. It receives a **view**: the rectangle of the plane to compute, as a center, the
size of a pixel, and a grid of `w` x `h` pixels. It fills two arrays of that shape: for each pixel, its count
of steps, and $|z|^2$ at the last one (which smooths the colors). The page turns them into a picture.

An engine works step by step (a Python generator): at each `yield` it says how far it is, and which rows are
ready. A quick picture runs it to its end at once. **All the pixels** runs it a little at each frame: the page
stays alive, shows the progress, and the picture fills in.
::code
"""
@dataclass
class View:
    """What to compute: a rectangle of the plane, on a grid of pixels. The center is a Decimal: at a zoom of
    1e-100, it needs more than 100 digits."""
    center_re: Decimal
    center_im: Decimal
    pixel: float  # the size of a pixel, in the plane
    w: int
    h: int
    max_iter: int

    def corner(self) -> tuple[float, float]:
        """The top left pixel, in double precision"""
        return float(self.center_re) - self.w / 2 * self.pixel, float(self.center_im) + self.h / 2 * self.pixel
# ::endcode


# ======================================================================================================================
#                                           The four engines
# ======================================================================================================================

r"""::md Python
### Python
The definition, as two loops. It is the slowest by far: in the time given to a picture, it can only afford
one pixel out of 16 or 64.
::code
"""
def python_engine(view: View) -> Steps:
    x0, y0 = view.corner()
    count, size2 = np.zeros((view.h, view.w), np.int32), np.zeros((view.h, view.w), np.float32)
    ready = np.zeros(view.h, bool)
    for row in range(view.h):
        for col in range(view.w):
            c = complex(x0 + col * view.pixel, y0 - row * view.pixel)
            z, n = 0j, 0
            while n < view.max_iter and z.real * z.real + z.imag * z.imag <= ESCAPE2:
                z = z * z + c
                n += 1
            count[row, col], size2[row, col] = n, min(z.real * z.real + z.imag * z.imag, 1e30)
        ready[row] = True
        yield (row + 1) / view.h, (count, size2), ready  # a row is done
# ::endcode


r"""::md numpy
### numpy
All the pixels advance together, one step per line of Python. The pixels that escaped leave the computation.
Its progress is the iterations done: while it computes, the black recedes.
::code
"""
def numpy_engine(view: View) -> Steps:
    x0, y0 = view.corner()
    c = ((x0 + np.arange(view.w) * view.pixel)[None, :] + 1j * (y0 - np.arange(view.h) * view.pixel)[:, None]).ravel()
    z = np.zeros_like(c)
    count, size2 = np.full(c.shape, view.max_iter, np.int32), np.zeros(c.shape, np.float32)
    alive = np.arange(c.size)  # the pixels still iterating
    counts, ready = (count.reshape(view.h, view.w), size2.reshape(view.h, view.w)), np.ones(view.h, bool)
    for n in range(1, view.max_iter + 1):
        z[alive] = z[alive] * z[alive] + c[alive]
        s = z[alive].real ** 2 + z[alive].imag ** 2
        size2[alive] = s
        out = s > ESCAPE2
        count[alive[out]] = n
        alive = alive[~out]
        yield n / view.max_iter, counts, ready  # an iteration is done, for all the pixels
# ::endcode


r"""::md Cpp
### C++
The same two loops as the Python engine, in C++ (`mandel_double`, below). Python gives it two numpy arrays to
fill, through `ctypes`: no copy, no wrapper to generate.

*On the desktop*, `ctypes` releases Python's lock during the call, so a pool of threads computes several bands
of rows at once. *In a browser*, Python has one thread: the same C++, compiled to WebAssembly, computes the bands
one after the other, about ten times slower than a desktop with ten cores. (The threaded version is for the
desktop only.)

It is fast, but a `double` holds 16 digits. Below a pixel size of about 1e-13, pixels start to be wrong; at
1e-16, neighbours get the same $c$ and the picture turns into blocks.
::code
"""
def cpp_engine(view: View) -> Steps:
    x0, y0 = view.corner()
    return run_in_bands(view, lambda count, size2, row0, row1: KERNELS.mandel_double(
        D(x0), D(y0), D(view.pixel), view.w, view.h, row0, row1, view.max_iter, count, size2))
# ::endcode


r"""::md Perturbation
### C++ with perturbation: the deep zoom
Neighbouring pixels have almost the same orbit. So compute **one** orbit with many digits, the reference
$Z_n$ of the center $C$, and for each pixel only its small difference $d_n$ from it. For a pixel at $C + dc$:

$$d_{n+1} = 2 Z_n d_n + d_n^2 + dc$$

The differences are tiny, but a `double` stores tiny numbers very well (down to 1e-308): it is the sum
$C + dc$ that needs many digits, and it is never computed.

* The reference orbit takes `max_iter` steps in total. Python computes it with `decimal`, from its standard
  library: no big number library on the C++ side.
* The loop over the pixels (`mandel_perturbation`, below) is plain `double` arithmetic.
* The trap: when $z_n$ comes close to 0, $d_n$ has lost its digits. The fix is one line, *rebasing*: restart
  the reference at $Z_0 = 0$, with $d = z$.

It zooms down to a pixel size of 1e-300. Checked against a computation with 300 digits per pixel: the same
counts, where the C++ engine in `double` already has 20% of wrong pixels at 1e-12.
::code
"""
def reference_orbit(view: View) -> np.ndarray:
    getcontext().prec = digits_for(view.pixel)
    x = y = Decimal(0)
    orbit = [(0.0, 0.0)]
    for _ in range(view.max_iter):
        x, y = x * x - y * y + view.center_re, 2 * x * y + view.center_im
        orbit.append((float(x), float(y)))
        if x * x + y * y > ESCAPE2:
            break
    return np.array(orbit)


def perturbation_engine(view: View) -> Steps:
    ref = reference_orbit(view)
    dx0, dy0 = -view.w / 2 * view.pixel, view.h / 2 * view.pixel  # the top left pixel, from the center
    return run_in_bands(view, lambda count, size2, row0, row1: KERNELS.mandel_perturbation(
        ref.ctypes.data_as(PTR), len(ref), D(dx0), D(dy0), D(view.pixel),
        view.w, view.h, row0, row1, view.max_iter, count, size2))
# ::endcode


r"""::md Pattern
### The pattern
The C++ part knows nothing about the GUI: it fills arrays. Python turns them into a picture and shows it with
one call. A C++ library that draws with Dear ImGui by itself would need the very same Dear ImGui as the Python
package (version, options, compiler). An array has no such needs.

The C++ file is compiled once, into a small library: on the desktop by your compiler at the first run, and
for the browser into a WebAssembly module of 1.3 KB (`mandel_kernels.wasm`, beside this file), loaded the same
way by `ctypes`.
"""


def digits_for(pixel: float) -> int:
    """The decimal digits that a coordinate needs at this zoom"""
    return int(-math.log10(pixel)) + 25


# ======================================================================================================================
#                                  Loading the C++ loops, and calling them in bands
# ======================================================================================================================
D, PTR = ctypes.c_double, ctypes.c_void_p


def load_kernels() -> ctypes.CDLL | None:
    """The library compiled from mandel_kernels.cpp. In the browser: a WebAssembly module of this folder.
    On the desktop: compiled at the first run into the temporary folder (it needs a C++ compiler)."""
    source = HERE / "mandel_kernels.cpp"
    if IN_BROWSER:
        try:
            return ctypes.CDLL(str(HERE / "mandel_kernels.wasm"))
        except OSError:
            return None
    library = Path(tempfile.gettempdir()) / f"mandel_kernels_{int(source.stat().st_mtime)}.lib"
    try:
        if not library.exists():
            if sys.platform == "win32":
                command = ["cl", "/O2", "/LD", "/nologo", "/std:c++20", str(source),
                           f"/Fe{library}", f"/Fo{library}.obj"]
            else:
                command = ["c++", "-O3", "-std=c++20", "-shared", "-fPIC", "-o", str(library), str(source)]
            subprocess.run(command, check=True, capture_output=True)
        return ctypes.CDLL(str(library))
    except (OSError, subprocess.CalledProcessError):
        return None


KERNELS: Any = load_kernels()  # None without a C++ compiler
POOL = None if IN_BROWSER else ThreadPoolExecutor(THREADS)


r"""::md Bands
`run_in_bands` is what both C++ engines call. It creates the two arrays, cuts the picture into bands of a few
rows, and calls the C++ loop on each band, with pointers to the arrays: no copy.
* *On the desktop*, all the bands go to a pool of threads, and a step waits for some of them to finish.
  `ctypes` releases Python's lock during a call, so the bands truly run at once.
* *In a browser* there are no threads (`POOL` is `None`): a step computes one band.
* The C++ has no thread of its own: on the desktop, the parallelism is these few lines of Python.
::code
"""
def run_in_bands(view: View, kernel: Callable[[ctypes.c_void_p, ctypes.c_void_p, int, int], None]) -> Steps:
    """Calls kernel(count, size2, row0, row1) for each band of rows: a step is some bands done"""
    count, size2 = np.zeros((view.h, view.w), np.int32), np.zeros((view.h, view.w), np.float32)
    ready = np.zeros(view.h, bool)
    pointers = count.ctypes.data_as(PTR), size2.ctypes.data_as(PTR)
    bands = [(row0, min(row0 + BAND_ROWS, view.h)) for row0 in range(0, view.h, BAND_ROWS)]
    if POOL is None:  # in a browser: one band after the other
        for i, (row0, row1) in enumerate(bands):
            kernel(*pointers, row0, row1)
            ready[row0:row1] = True
            yield (i + 1) / len(bands), (count, size2), ready
        return
    waiting = {POOL.submit(kernel, *pointers, row0, row1): (row0, row1) for row0, row1 in bands}

    def keep_arrays(_future: Any, _arrays: Counts = (count, size2)) -> None:
        """The arrays live as long as a band may write into them, even after a cancel"""

    for future in waiting:
        future.add_done_callback(keep_arrays)
    try:
        while waiting:
            for future in wait(waiting, timeout=0.005, return_when=FIRST_COMPLETED).done:
                row0, row1 = waiting.pop(future)
                future.result()
                ready[row0:row1] = True
            yield 1 - len(waiting) / len(bands), (count, size2), ready
    finally:  # left before the end (a cancelled picture): the bands not started yet are dropped
        for future in waiting:
            future.cancel()
# ::endcode


@dataclass
class Engine:
    name: str
    section: str  # its ::md section in this file
    compute: Callable[[View], Steps]
    cpp_region: str = ""  # its function in mandel_kernels.cpp (empty: an engine in Python only)


ENGINES = [
    Engine("Python", "Python", python_engine),
    Engine("numpy", "numpy", numpy_engine),
    Engine("C++", "Cpp", cpp_engine, cpp_region="Double"),
    Engine("C++ with perturbation", "Perturbation", perturbation_engine, cpp_region="Perturbation"),
]

# Places to visit: a name, a point (re, im), and its zooms: the width of the view, the iterations, a short name,
# and what to see there. The digits of a point limit its zooms: 110 digits for a zoom of 10^100.
SEAHORSE = ("-0.743916538692433356599334896378352022720811393898656056544159"
            "34462016366377146254866440653871761911999857422",
            "0.131688791359494617577789121421345189627001256552777831155761"
            "33333081667103570998513450421077334266471040041")
# The center of a small copy of the set, hidden in the spirals of the valley (found with Newton's method)
HIDDEN_COPY = ("-0.74391653869243335659933489638638694153569553630943849046081220664810341437",
               "0.13168879135949461757778912139905999762536756237320873041503736241957753062")
BUILT_IN_PLACES = [
    ("The whole set", WHOLE_SET[:2], [(WHOLE_SET[2], 300, "", "")]),
    ("Elephant valley", ("0.275", "0.0068"), [
        (0.005, 3000, "trunks", "A parade of elephants, trunks up, along the right side of the set.")]),
    ("Double spiral", ("-0.7453", "0.1127"), [
        (6.5e-4, 2000, "a spiral", "A spiral made of spirals, at the entrance of Seahorse valley.")]),
    ("The needle", ("-1.7548776662466927", "0"), [
        (0.07, 600, "a small copy", "A small copy of the whole set, on the needle that points to the left. "
                                    "There are infinitely many copies: see also the hidden one.")]),
    ("Feigenbaum point", ("-1.401155189092050593", "0"), [
        (0.06, 2000, "bulbs", "Each bulb carries a smaller one, about 4.669 times smaller: Feigenbaum's constant."),
        (6e-5, 6000, "the same, 1000 times smaller", "A thousand times closer: the cascade of bulbs goes on.")]),
    ("Seahorse valley", SEAHORSE, [
        (3e-9, 3000, "spirals",
         "Spirals within spirals. The C++ engine starts to drift here: compare it with the perturbation."),
        (2e-14, 4500, "the end of double",
         "The end of double: the C++ engine draws blocks, the perturbation draws the picture."),
        (1e-37, 9000, "perturbation only",
         "Only the perturbation gets here. Its reference orbit is computed with 60 digits."),
        (3e-100, 14000, "deeper still",
         "Still spirals, 63 zooms of ten further. Each picture needs about 12 000 iterations per pixel.")]),
    ("A hidden copy", HIDDEN_COPY, [
        (1e-44, 30000, "rings", "Something is in the middle of the spirals: rings around a center."),
        (1e-46, 30000, "closer", "Closer: the rings announce a copy of the set, 100 times smaller still."),
        (4.5e-49, 60000, "the copy",
         "A copy of the whole set, tilted, nearly 10^49 times smaller. Each pixel needs 20 000 to 60 000 "
         "iterations.")]),
    ("The point i", ("0", "1"), [
        (1e-8, 600, "a tree",
         "The point c = i is on the boundary: a branching tree, with detail at every scale."),
        (1e-57, 1200, "the same tree",
         "The same tree. A proton next to the observable universe is only a zoom of 10^41."),
        (1e-287, 2000, "the limit",
         "The same tree again, near the smallest number that a double can hold: the limit of this page.")]),
]


# My places: the views added with the card's bookmark button, kept in a file beside this one (git ignores it)
MY_PLACES_FILE = HERE / "my_places.json"
MY_VIEWS: list[dict[str, Any]] = []  # the file's content: a name, a point, a width, iterations, two texts
Zoom = tuple[float, int, str, str, tuple[str, str]]  # a width, iterations, a short name, what to see, its point
PLACES: list[tuple[str, tuple[str, str], list[Zoom]]] = []  # the built-in places and mine, see load_places()


def load_places() -> None:
    """Fills PLACES: the built-in places, then my views. A view named as a place is one more zoom of that place
    (with its own point); another name is a new place."""
    places = {name: (point, [(*zoom, point) for zoom in zooms]) for name, point, zooms in BUILT_IN_PLACES}
    MY_VIEWS[:] = json.loads(MY_PLACES_FILE.read_text()) if MY_PLACES_FILE.exists() else []
    for view in MY_VIEWS:
        point = (view["re"], view["im"])
        zooms = places.setdefault(view["name"], (point, []))[1]
        zooms.append((view["width"], view["iterations"], view["short"], view["sentence"], point))
        zooms.sort(key=lambda zoom: -zoom[0])  # the widest view first
    PLACES[:] = [(name, point, zooms) for name, (point, zooms) in places.items()]


load_places()


# ======================================================================================================================
#                                           From counts to colors
# ======================================================================================================================
# The palettes: cyclic gradients (the last color is the first), as (position, color) stops
PALETTES: dict[str, list[tuple[float, tuple[int, int, int]]]] = {
    "Night and gold": [(0.0, (0, 7, 100)), (0.16, (32, 107, 203)), (0.42, (237, 255, 255)), (0.64, (255, 170, 0)),
                       (0.86, (0, 2, 0)), (1.0, (0, 7, 100))],
    "Fire": [(0.0, (10, 0, 0)), (0.25, (150, 10, 0)), (0.5, (255, 110, 0)), (0.7, (255, 225, 90)),
             (0.82, (255, 255, 240)), (1.0, (10, 0, 0))],
    "Lagoon": [(0.0, (68, 1, 84)), (0.25, (59, 82, 139)), (0.5, (33, 145, 140)), (0.72, (94, 201, 98)),
               (0.88, (253, 231, 37)), (1.0, (68, 1, 84))],
    "Twilight": [(0.0, (226, 217, 226)), (0.25, (104, 132, 196)), (0.5, (48, 20, 56)), (0.75, (186, 92, 98)),
                 (1.0, (226, 217, 226))],
    "Ink": [(0.0, (250, 248, 240)), (0.5, (20, 22, 30)), (1.0, (250, 248, 240))],
}


def palette_colors(name: str, t: np.ndarray) -> np.ndarray:
    """The colors of the palette at t (0 to 1), as an array of RGB values"""
    stops = PALETTES[name]
    return np.stack([np.interp(t, [at for at, _ in stops], [color[k] for _, color in stops]) for k in range(3)],
                    axis=-1)


def smooth_counts(counts: Counts) -> np.ndarray:
    """The count, minus log2(log2|z|): it varies smoothly from a pixel to the next, with no bands"""
    count, size2 = counts
    return count + 1 - np.log2(np.log2(np.maximum(size2, 4.0)) / 2)


def colors(counts: Counts, max_iter: int, palette: str, lowest: float | None = None) -> np.ndarray:
    """An RGB picture. The palette starts at the lowest count of the picture (or at `lowest`, for a picture
    that is not complete yet): a deep zoom, where all counts are high, keeps its contrast."""
    count = counts[0]
    smooth = smooth_counts(counts)
    lowest = smooth.min() if lowest is None else lowest
    rgb = palette_colors(palette, 0.45 * np.log2(1 + np.maximum(smooth - lowest, 0) / 6) % 1.0)
    rgb[count >= max_iter] = 0
    return rgb.astype(np.uint8)


# ======================================================================================================================
#                                           The GUI
# ======================================================================================================================
@dataclass
class AllPixels:
    """All the pixels of one engine's picture, computed a little at each frame: the page stays alive, shows the
    progress, fills the picture in, and can cancel"""
    side: int  # 0, or 1 for the right side of a split view
    steps: Steps
    wanted: tuple[Any, ...]  # the view and the engines it was asked for
    start_time: float
    last: Step | None = None  # its latest step
    fraction: float = 0.0
    painted_at: float = 0.0


class State:
    def __init__(self) -> None:
        self.engine = ENGINES[2 if KERNELS else 1]
        self.max_iter = 300
        self.image = np.zeros((2, 2, 3), np.uint8)
        self.counts: list[Any] = []  # the counts behind the image, per engine: a new palette only recolors them
        self.each_seconds: list[float] = []  # the time of each engine
        self.sides: list[np.ndarray] = []  # the picture of each engine
        self.composed: tuple[Any, ...] | None = None  # what the image is made of
        self.other: Engine | None = None  # the split view: a second engine, on the right of a divider
        self.split = 0.5  # the place of the divider, 0 to 1
        self.dragging_split = False
        self.palette = next(iter(PALETTES))
        self.painted: tuple[Any, ...] | None = None  # what the image shows: the computation, and its palette
        self.computed: tuple[str, Decimal, Decimal, float, int, int, int] | None = None  # what the image shows
        self.where: tuple[Decimal, Decimal, float, int, int] | None = None  # the view at the last frame
        self.shrinks: list[int] = []  # what each engine's picture holds: 1 after "All the pixels"
        self.all_pixels: AllPixels | None = None  # the picture being computed frame after frame, see the button
        self.lowest: list[float] = []  # the lowest count of each engine's picture: the start of its palette
        self.cancelled: tuple[Any, int] | None = None  # the picture and the side of the last cancel
        self.new_view = ["", "", ""]  # the texts typed for a view to add: its place, its short name, a sentence
        self.costs: dict[str, dict[int, float]] = {}  # for each engine, at this view: the seconds its pictures took,
        # by their number of pixels. Two sizes tell the fixed part of a picture's time from the part per pixel.
        self.moved_at = 0.0  # when the view last changed
        self.dive: tuple[float, float, float] | None = None  # a zoom animation: from width, to width, start time
        self.center_re, self.center_im, self.width = Decimal(0), Decimal(0), float(WHOLE_SET[2])
        self.place = ""
        self.history: list[tuple[Decimal, Decimal, float, int]] = []  # the views to come back to
        self.auto_iterations = True  # the page adapts the iterations when the view is moved by hand
        self.by_hand = False  # the view was moved by hand since the last place
        self.late: float | None = None  # in the last picture: the count below which 90% of the escaped pixels are
        self.notes_open = False  # the explanations beside the picture
        self.card_height = em_size(5.0)  # the sizes of the panels over the picture, measured at the last frame
        self.side_widths = [em_size(20), em_size(20)]
        self.explained = self.engine  # the engine that the explanations are about: it follows the engine chosen
        self.shown_tab: Engine | None = None  # the tab open at the last frame
        self.go_to(WHOLE_SET, 300, animate=False)

    def seconds_for(self, engine: "Engine", pixels: int) -> float | None:
        """The time a picture of this many pixels should take, from the pictures already computed here"""
        taken = sorted(self.costs.get(engine.name, {}).items())
        if not taken:
            return None
        (small, t_small), (large, t_large) = taken[0], taken[-1]
        per_pixel = (t_large - t_small) / (large - small) if large > small else t_large / large
        return max(t_large + per_pixel * (pixels - large), 0.0)

    def start_all_pixels(self, side: int, engine: "Engine") -> None:
        """All the pixels of an engine's picture, from now on computed a little at each frame"""
        if self.where is not None and self.computed is not None:
            center_re, center_im, width, w, h = self.where
            full = View(center_re, center_im, width / w, w, h, self.max_iter)
            self.all_pixels = AllPixels(side, engine.compute(full), self.computed, time.perf_counter())

    def add_view(self, name: str, short: str, sentence: str) -> None:
        """The current view joins my places, and their file"""
        digits = max(6, int(-math.log10(self.width)) + 8)  # enough to find the view again
        MY_VIEWS.append({"name": name, "re": f"{self.center_re:.{digits}f}", "im": f"{self.center_im:.{digits}f}",
                         "width": self.width, "iterations": self.max_iter, "short": short, "sentence": sentence})
        MY_PLACES_FILE.write_text(json.dumps(MY_VIEWS, indent=1) + "\n")
        load_places()
        self.place = name

    def remove_view(self, name: str, width: float) -> None:
        kept = [view for view in MY_VIEWS if (view["name"], view["width"]) != (name, width)]
        MY_PLACES_FILE.write_text(json.dumps(kept, indent=1) + "\n")
        load_places()

    def remember(self) -> None:
        self.history.append((self.center_re, self.center_im, self.width, self.max_iter))

    def back(self) -> None:
        self.center_re, self.center_im, self.width, self.max_iter = self.history.pop()
        self.dive = None
        self.costs.clear()

    def go_to(self, place: tuple[str, str, float], max_iter: int, name: str = "", animate: bool = True) -> None:
        getcontext().prec = digits_for(place[2] / 2000)
        target_re, target_im = Decimal(place[0]), Decimal(place[1])
        # The dive starts from the current view when the target is inside it (another zoom of the same place),
        # else from the whole set
        start = float(WHOLE_SET[2])
        if animate:
            self.remember()
        if animate and max(abs(target_re - self.center_re), abs(target_im - self.center_im)) < self.width / 2:
            start = self.width
        self.center_re, self.center_im, self.width = target_re, target_im, place[2]
        self.max_iter = max_iter
        self.costs.clear()  # a new place: new costs
        self.place = name  # the place we went to: its name shows while its point is in view
        self.by_hand = False
        if animate:
            self.dive, self.width = (start, place[2], imgui.get_time()), start

    def move(self, d_re: float, d_im: float) -> None:
        getcontext().prec = digits_for(self.width / 2000)
        self.center_re += Decimal(d_re)
        self.center_im += Decimal(d_im)


STATE: State | None = None
DIVE_SECONDS_PER_DECADE = 0.12  # the speed of the zoom animation


ALL_BLACK_LIMIT = 50000  # the automatic iterations stop here when no pixel escapes
HANDLE_EM = 1.8  # the split view's handle and its two panels: this far from the top of the picture, in em
DOUBLE_CLICK_ZOOM = 6.0  # a double click zooms in by this factor, around the clicked point
DEEPEST = 300  # the gauge's last decade: a double holds numbers down to 1e-308
DOUBLE_ENDS = 13  # the decade where the engines in double precision start to be wrong


def picture(size: imgui.ImVec2) -> tuple[imgui.ImVec2, int, int]:
    """The picture, its mouse handling, and its computation when something changed. Returns its place."""
    state = STATE
    assert state is not None
    w, h = max(int(size.x), 16), max(int(size.y), 16)
    pixel = state.width / w

    # The mouse: an invisible button under the picture takes the wheel, the drags and the double clicks
    top_left = imgui.get_cursor_screen_pos()
    imgui.invisible_button("##picture", imgui.ImVec2(w, h))
    imgui.set_item_key_owner(imgui.Key.mouse_wheel_y)
    io = imgui.get_io()
    mx, my = io.mouse_pos.x - top_left.x - w / 2, io.mouse_pos.y - top_left.y - h / 2  # the mouse, from the center
    on_divider = state.other is not None and imgui.is_item_hovered() and \
        abs(io.mouse_pos.x - (top_left.x + state.split * w)) < em_size(0.8)
    if imgui.is_item_activated() and on_divider:
        state.dragging_split = True
    if not imgui.is_item_active():
        state.dragging_split = False
    if on_divider or state.dragging_split:
        imgui.set_mouse_cursor(imgui.MouseCursor_.resize_ew)
    if state.dragging_split:  # the split view's divider follows the mouse
        state.split = min(max((io.mouse_pos.x - top_left.x) / w, 0.03), 0.97)
    elif imgui.is_item_active() and (io.mouse_delta.x or io.mouse_delta.y):
        state.move(-io.mouse_delta.x * pixel, io.mouse_delta.y * pixel)
    if imgui.is_item_hovered() and io.mouse_wheel and state.dive is None:
        factor = 0.8 ** io.mouse_wheel
        if 10.0 ** -DEEPEST < state.width * factor < 8:  # zoom around the mouse: the point under it stays there
            state.move(mx * pixel * (1 - factor), -my * pixel * (1 - factor))
            state.width *= factor
            state.by_hand = True
    if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(0) and state.width > 10.0 ** (3 - DEEPEST) \
            and not on_divider:
        state.remember()  # the clicked point comes to the center, and the view dives towards it
        state.move(mx * pixel, -my * pixel)
        state.dive = (state.width, state.width / DOUBLE_CLICK_ZOOM, imgui.get_time())
        state.by_hand = True

    # A dive to a place: the width shrinks at a constant number of decades per second
    if state.dive is not None:
        start, end, t0 = state.dive
        decades = abs(math.log10(start / end))  # a dive goes in, or out
        progress = min(1.0, (imgui.get_time() - t0) / max(0.5, decades * DIVE_SECONDS_PER_DECADE))
        state.width = start * (end / start) ** progress
        if progress >= 1.0:
            state.dive = None

    # Compute, when the view or the engine changed, and again once the view stopped, with a larger budget
    where = (state.center_re, state.center_im, state.width, w, h)
    if where != state.where:
        state.where, state.moved_at = where, imgui.get_time()
    moving = imgui.get_time() - state.moved_at < 0.15
    if not moving and state.auto_iterations and state.by_hand and state.late is not None:
        # Many pixels escape late: the boundary needs more iterations. Nearly all escape early: fewer will do.
        # No pixel escapes (a black picture): more too, up to a point, since the inside of the set stays black.
        if state.late > 0.4 * state.max_iter and (state.late < math.inf or state.max_iter < ALL_BLACK_LIMIT):
            state.max_iter, state.late = min(int(state.max_iter * 1.5), 500000), None
        elif state.late < 0.05 * state.max_iter and state.max_iter > 300:
            state.max_iter, state.late = max(int(state.max_iter / 1.5), 300), None
    engines = [state.engine] + ([state.other] if state.other is not None else [])  # two: a split view
    budget = (MOVING_BUDGET if moving else STILL_BUDGET) / len(engines)  # each engine has its own

    def affordable_shrink(engine: Engine) -> int:
        """One pixel out of shrink x shrink: what the engine can compute in its budget"""
        if engine.name not in state.costs:
            return 8  # a first, coarse picture measures the cost
        return next((k for k in (1, 2, 4) if (state.seconds_for(engine, (w // k) * (h // k)) or 0) <= budget), 8)

    shrinks = [affordable_shrink(engine) for engine in engines]
    wanted = ("/".join(engine.name for engine in engines), *where, state.max_iter)
    same_view = wanted == state.computed and len(state.shrinks) == len(engines)
    job = state.all_pixels
    if job is not None and job.wanted != wanted:  # the view moved, or an engine changed: its picture is dropped
        job.steps.close()
        state.all_pixels = job = None
    if job is None and same_view and not moving and state.dive is None:
        # Once the view stopped: all the pixels by themselves, for the first engine that can have them quickly
        for side, engine in enumerate(engines):
            if state.shrinks[side] > 1 and (state.seconds_for(engine, w * h) or math.inf) < QUICK_SECONDS \
                    and state.cancelled != (wanted, side):
                state.start_all_pixels(side, engine)
                break
        job = state.all_pixels
    if job is not None:  # "All the pixels": a slice of its computation, at each frame
        all_pixels_slice(job, w, h)
    elif not same_view or any(new < old for new, old in zip(shrinks, state.shrinks, strict=True)):
        if not same_view:
            state.counts, state.each_seconds, state.shrinks = [None] * len(engines), [0.0] * len(engines), []
        for i, (engine, shrink) in enumerate(zip(engines, shrinks, strict=True)):
            if same_view and state.shrinks[i] <= shrink:
                continue  # this side is already as fine: only the other one is computed again
            view = View(state.center_re, state.center_im, state.width / w * shrink, w // shrink, h // shrink,
                        state.max_iter)
            start_time = time.perf_counter()
            state.counts[i] = whole(engine.compute(view))
            state.each_seconds[i] = time.perf_counter() - start_time
            state.costs.setdefault(engine.name, {})[view.w * view.h] = state.each_seconds[i]
            if same_view:
                state.shrinks[i] = shrink
        if not same_view:
            state.shrinks = shrinks
        state.computed = wanted
        escaped = state.counts[0][0][state.counts[0][0] < state.max_iter]
        state.late = float(np.percentile(escaped, 90)) if escaped.size else math.inf

    # Color the counts, when they or the palette changed: one picture per engine
    painted = (state.computed, tuple(state.shrinks), state.palette)
    if painted != state.painted and state.counts and state.computed is not None:
        state.sides, state.lowest = [], []
        for counts in state.counts:  # each with its own colors: an engine that is wrong does not spoil the other
            image = colors(counts, state.computed[-1], state.palette)
            rows, columns = np.arange(h) * image.shape[0] // h, np.arange(w) * image.shape[1] // w
            state.sides.append(image[rows][:, columns])  # stretched to the size of the picture
            state.lowest.append(float(smooth_counts(counts).min()))
        state.painted = painted
    # The image: one picture, or the left of the first and the right of the second
    composed = (state.painted, state.split if len(state.sides) > 1 else None)
    recompose = composed != state.composed and bool(state.sides)
    if recompose:
        column = int(state.split * w)
        state.image = np.ascontiguousarray(
            state.sides[0] if len(state.sides) == 1 else
            np.hstack([state.sides[0][:, :column], state.sides[1][:, column:]]))
        state.composed = composed
    imgui.set_cursor_screen_pos(top_left)
    immvision.image_display("##mandelbrot", state.image, (w, h), refresh_image=recompose)
    if state.other is not None and len(state.each_seconds) > 1 and len(state.shrinks) > 1:
        divider(top_left, w, h)
    return top_left, w, h


def all_pixels_slice(job: AllPixels, w: int, h: int) -> None:
    """Computes "All the pixels" for a moment, and from time to time paints the rows that are ready over the
    coarse picture. At the end, its arrays become the picture's."""
    state = STATE
    assert state is not None and state.computed is not None
    stop_at, complete = time.perf_counter() + SLICE_SECONDS, False
    while time.perf_counter() < stop_at and not complete:
        step = next(job.steps, None)
        if step is None:  # the end: the last step holds the complete arrays
            complete = True
        else:
            job.last = step
    if job.last is None:
        return
    job.fraction, counts, ready = job.last
    if complete:  # the usual painting takes over
        state.counts[job.side], state.shrinks[job.side] = counts, 1
        state.each_seconds[job.side] = time.perf_counter() - job.start_time
        state.all_pixels = None
    elif time.perf_counter() - job.painted_at > REPAINT_SECONDS and job.side < len(state.sides):
        image = colors(counts, state.computed[-1], state.palette, state.lowest[job.side])
        rows, columns = np.arange(h) * image.shape[0] // h, np.arange(w) * image.shape[1] // w
        filled = ready[rows]  # the rows of the picture whose pixels are ready
        state.sides[job.side][filled] = image[rows[filled]][:, columns]
        job.painted_at, state.composed = time.perf_counter(), None


def divider(top_left: imgui.ImVec2, w: int, h: int) -> None:
    """The split view's divider: a line with a handle"""
    state = STATE
    assert state is not None and state.other is not None
    draw_list = imgui.get_window_draw_list()
    white, black = imgui.IM_COL32(255, 255, 255, 255), imgui.IM_COL32(0, 0, 0, 255)
    x, y, r = top_left.x + state.split * w, top_left.y + HANDLE_EM * em_size(1), em_size(0.75)  # near the top
    draw_list.add_line((x, top_left.y), (x, top_left.y + h), black, 4)
    draw_list.add_line((x, top_left.y), (x, top_left.y + h), white, 2)
    draw_list.add_circle_filled((x, y), r + 2, black)
    draw_list.add_circle_filled((x, y), r, white)
    for sign in (-1, 1):  # two small arrows in the handle: it moves left and right
        tip = x + sign * r * 0.72
        back = tip - sign * r * 0.45
        draw_list.add_triangle_filled((tip, y), (back, y - r * 0.4), (back, y + r * 0.4), black)

# To picture a zoom: if the whole set were as wide as the observable universe, what would the picture be as wide as?
UNIVERSE = 8.8e26  # meters
SIZES = [(8.8e26, "the observable universe"), (1e21, "a galaxy"), (9e12, "the solar system"), (1.3e7, "the Earth"),
         (4e4, "a city"), (1.7, "a person"), (1e-4, "a hair's width"), (1e-6, "a bacterium"), (1e-10, "an atom"),
         (1.7e-15, "a proton"), (1.6e-35, "the Planck length, the smallest length that physics describes")]


def zoom_number(width: float) -> str:
    zoom = WHOLE_SET[2] / width
    exponent = math.floor(math.log10(zoom))
    return f"{zoom:,.0f}" if zoom < 1e6 else f"{zoom / 10 ** exponent:.1f} x 10^{exponent}"


def zoom_in_words(width: float) -> str:
    """A zoom, as a comparison of sizes"""
    size = UNIVERSE * width / WHOLE_SET[2]
    reference, name = min((entry for entry in SIZES if entry[0] >= size / 3), key=lambda entry: entry[0])
    ratio = reference / size  # the smallest thing that is not smaller than the picture
    if ratio < 30:
        thing = f"about as wide as {name}"
    elif ratio < 1e6:
        thing = f"{round(ratio, -int(math.log10(ratio))):,.0f} times smaller than {name}"
    else:
        thing = f"10^{round(math.log10(ratio))} times smaller than {name}"
    return f"If the whole set were as wide as the observable universe, this picture would be {thing}."


def same_line_if_room(next_label: str) -> None:
    """Puts the next widget on the same line, when it fits"""
    imgui.same_line()
    if imgui.get_cursor_pos_x() + imgui.calc_text_size(next_label).x + em_size(2.5) > imgui.get_window_width():
        imgui.new_line()


# ======================================================================================================================
#                             The panels over the picture, and the explanations beside it
# ======================================================================================================================
def begin_over_picture(name: str, pos: imgui.ImVec2, size: imgui.ImVec2 | None = None) -> None:
    """A semi-transparent panel at a fixed place over the picture (no size: as large as its content).
    To be closed with end_over_picture(), which returns its size."""
    background = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    imgui.set_cursor_screen_pos(pos)
    imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(background.x, background.y, background.z, 0.82))
    fit = imgui.ChildFlags_.auto_resize_x | imgui.ChildFlags_.auto_resize_y | imgui.ChildFlags_.always_auto_resize
    imgui.begin_child(name, size or (0, 0), imgui.ChildFlags_.borders | (0 if size else fit))
    imgui.pop_style_color()


def end_over_picture() -> imgui.ImVec2:
    imgui.end_child()
    return imgui.get_item_rect_size()


def menu_button(label: str, popup: str, title: bool = False, upwards: bool = True) -> None:
    """A text with a small arrow, which opens a menu above it (the card is at the bottom of the picture) or under
    it: `if imgui.begin_popup(popup): ...` follows"""
    imgui.push_style_color(imgui.Col_.button, imgui.ImVec4(0, 0, 0, 0))
    if title:
        imgui.push_font(None, imgui.get_style().font_size_base * 1.45)
    if imgui.button(f"{label}  {icons_fontawesome_6.ICON_FA_CARET_DOWN}###{popup}"):
        imgui.open_popup(popup)
    if title:
        imgui.pop_font()
    imgui.pop_style_color()
    low, high = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    imgui.set_next_window_pos((low.x, low.y if upwards else high.y), imgui.Cond_.always, (0, 1 if upwards else 0))


def engine_menu(popup: str, current: Engine, other: Engine | None) -> Engine:
    """The menu of the engines, opened by a menu_button: returns the chosen one"""
    chosen = current
    if imgui.begin_popup(popup):
        for engine in ENGINES:
            imgui.begin_disabled(engine is other or (bool(engine.cpp_region) and KERNELS is None))
            if imgui.selectable(engine.name, engine is current)[0]:
                chosen = engine
            imgui.end_disabled()
        if KERNELS is None:
            imgui.text_disabled("The C++ engines need a C++ compiler (c++ or cl) at the first run.")
        imgui.end_popup()
    return chosen


def cost_text(side: int) -> str:
    state = STATE
    assert state is not None
    text = f"{state.each_seconds[side] * 1000:.0f} ms for {state.counts[side][0].size / 1e6:.2f} million pixels"
    return text + (f" (1 out of {state.shrinks[side] ** 2})" if state.shrinks[side] > 1 else "")


def palette_swatches() -> None:
    """A row of gradients: a click picks the palette. The picture is recolored at once, not computed again."""
    state = STATE
    assert state is not None
    draw_list, size, steps = imgui.get_window_draw_list(), imgui.ImVec2(em_size(5.3), em_size(1.3)), 48
    for name in PALETTES:
        if imgui.invisible_button(f"##palette {name}", size):
            state.palette = name
        imgui.set_item_tooltip(name)
        low, high = imgui.get_item_rect_min(), imgui.get_item_rect_max()
        for i, (r, g, b) in enumerate(palette_colors(name, (np.arange(steps) + 0.5) / steps)):
            x0, x1 = low.x + size.x * i / steps, low.x + size.x * (i + 1) / steps
            draw_list.add_rect_filled((x0, low.y), (x1 + 1, high.y), imgui.IM_COL32(int(r), int(g), int(b), 255))
        if name == state.palette:  # the chosen one: a frame
            draw_list.add_rect((low.x - 1, low.y - 1), (high.x + 1, high.y + 1), imgui.get_color_u32(imgui.Col_.text),
                               thickness=2.5)
        elif imgui.is_item_hovered():
            draw_list.add_rect(low, high, imgui.get_color_u32(imgui.Col_.text_disabled))
        imgui.same_line(0, em_size(0.35))
    imgui.new_line()


def where_we_are() -> str:
    """The name of the place in view: the first place with a point in the picture"""
    state = STATE
    assert state is not None
    if state.where is None or state.width > WHOLE_SET[2] / 10:
        return PLACES[0][0]
    center_re, center_im, width, w, h = state.where
    half_w, half_h = width / 2, width / 2 * h / w

    def inside(point: tuple[str, str]) -> bool:
        return abs(Decimal(point[0]) - center_re) < half_w and abs(Decimal(point[1]) - center_im) < half_h

    in_view = [name for name, _point, zooms in PLACES[1:] if any(inside(zoom[4]) for zoom in zooms)]
    if state.place in in_view:  # the place we went to, while its point is in view (the hidden copy is in the valley)
        return state.place
    return in_view[0] if in_view else "Uncharted waters"


def add_view_popup() -> None:
    """Three texts, and the current view joins my places"""
    state = STATE
    assert state is not None
    imgui.set_next_window_pos(imgui.get_item_rect_min(), imgui.Cond_.always, (0, 1))  # above its button
    if not imgui.begin_popup("add view"):
        return
    imgui.text(f"Add this view to my places (zoom {zoom_number(state.width)})")
    labels = ["Place", "Name of this view", "What to see there"]
    hints = ["An existing place: one more of its zooms. A new name: a new place.", "A few words, for the menu.", ""]
    for i, (label, hint) in enumerate(zip(labels, hints, strict=True)):
        imgui.set_next_item_width(em_size(22 if i == 2 else 14))
        _, state.new_view[i] = imgui.input_text(label, state.new_view[i])
        if hint:
            imgui.same_line()
            imgui_kit.help_marker(hint)
    name, short, sentence = (text.strip() for text in state.new_view)
    imgui.begin_disabled(not name or not short)
    if imgui.button("Add"):
        state.add_view(name, short, sentence)
        imgui.close_current_popup()
    imgui.end_disabled()
    imgui.same_line()
    imgui.text_disabled(f"Saved in {MY_PLACES_FILE.name}, beside this demo")
    imgui.end_popup()


def title_card(top_left: imgui.ImVec2, h: int) -> None:
    """Bottom left: where we are, and the controls. First line: back, the place and its zoom (two menus), the
    help. Second line: the engine (a menu) and its cost, the split view, the settings."""
    state = STATE
    assert state is not None
    margin = em_size(0.6)
    begin_over_picture("##card", imgui.ImVec2(top_left.x + margin, top_left.y + h - margin - state.card_height))
    place = where_we_are()

    # Back, in the height of the place's name
    imgui.push_font(None, imgui.get_style().font_size_base * 1.45)
    tall = imgui.get_frame_height()
    imgui.pop_font()
    imgui.begin_disabled(not state.history)
    if imgui.button(icons_fontawesome_6.ICON_FA_ARROW_LEFT, (tall, tall)):
        state.back()
    imgui.end_disabled()
    imgui.set_item_tooltip("Back to the previous view")

    imgui.same_line()
    menu_button(place, "places", title=True)  # the place: a menu of the places
    if imgui.begin_popup("places"):
        for name, _point, zooms in PLACES:
            if imgui.selectable(name, name == place)[0]:
                state.go_to((*zooms[0][4], zooms[0][0]), zooms[0][1], name)
        imgui.end_popup()

    deeper = [its_zooms for name, _point, its_zooms in PLACES[1:] if name == place]  # the zooms of this place
    imgui.same_line()
    imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + tall - imgui.get_frame_height())  # on the name's baseline
    if not deeper:
        imgui.align_text_to_frame_padding()
        imgui.text(f"zoom {zoom_number(state.width)}")
    else:  # the zoom: a menu of the place's zooms, each with an (i) that says what to see there
        menu_button(f"zoom {zoom_number(state.width)}", "zooms")
        imgui.set_next_window_size_constraints((em_size(23), 0), (imgui.FLT_MAX, imgui.FLT_MAX))  # room for the (i)
        if imgui.begin_popup("zooms"):
            for width, max_iter, short, story, point in list(deeper[0]):
                zoom = math.floor(math.log10(WHOLE_SET[2] / width))
                label = f"Zoom 10^{zoom}: {short}" if zoom >= 6 else f"Zoom {WHOLE_SET[2] / width:,.0f}: {short}"
                if imgui.selectable(f"{label}##{width}", False, size=(em_size(17), 0))[0]:
                    state.go_to((*point, width), max_iter, place)
                if story:
                    imgui.same_line()
                    imgui_kit.help_marker(story)
                if any((view["name"], view["width"]) == (place, width) for view in MY_VIEWS):  # one of mine
                    imgui.same_line(em_size(20.5))
                    if imgui.small_button(f"{icons_fontawesome_6.ICON_FA_TRASH}##{width}"):
                        state.remove_view(place, width)
                    imgui.set_item_tooltip("Remove this view from my places")
            imgui.end_popup()
    imgui.same_line(0, em_size(1.0))
    imgui.dummy((imgui_kit.help_marker_width() + em_size(0.5), 1))  # room for the (i), drawn last in this corner

    # Second line: the engine and its cost, the split view, the settings
    if state.other is None:
        menu_button(state.engine.name, "engine")
        chosen = engine_menu("engine", state.engine, None)
        if chosen is not state.engine:
            state.engine = state.explained = chosen  # the explanations follow the engine, when it changes
        if state.counts and state.shrinks:
            imgui.same_line()
            imgui.text_disabled(cost_text(0))
    else:
        imgui.align_text_to_frame_padding()
        imgui.text_disabled("Two engines: pick each one beside the divider")
    imgui.same_line(0, em_size(1.5))
    split = state.other is not None
    if imgui.checkbox("Split", split)[0]:  # a second engine draws the right part of the picture
        fallback = ENGINES[3] if state.engine is not ENGINES[3] else ENGINES[2]
        state.other = None if split else (fallback if KERNELS is not None else ENGINES[1 - ENGINES.index(state.engine)])
    imgui.same_line()
    if imgui.button(icons_fontawesome_6.ICON_FA_GEAR):
        imgui.open_popup("settings")
    imgui.set_item_tooltip("Iterations and colors")
    imgui.same_line()
    if imgui.button(icons_fontawesome_6.ICON_FA_BOOKMARK):  # add this view to my places
        known = place not in (PLACES[0][0], "Uncharted waters")
        state.new_view = [place if known else "", "", ""]
        imgui.open_popup("add view")
    imgui.set_item_tooltip("Add this view to my places")
    add_view_popup()
    imgui.set_next_window_pos(imgui.get_item_rect_min(), imgui.Cond_.always, (0, 1))  # above the gear
    if imgui.begin_popup("settings"):
        imgui.set_next_item_width(em_size(9))
        changed, state.max_iter = imgui.slider_int("iterations", state.max_iter, 50, 500000,
                                                   flags=imgui.SliderFlags_.logarithmic)
        if changed:
            state.auto_iterations = False  # set by hand: the page stops adapting them
            state.costs.clear()
        imgui.same_line()
        _, state.auto_iterations = imgui.checkbox("automatic", state.auto_iterations)
        imgui.same_line()
        imgui_kit.help_marker("Automatic: while you move the view by hand, the page raises the iterations when the "
                              "boundary needs them (black where there should be detail), and lowers them when it can.")
        palette_swatches()
        imgui.end_popup()
    padding = imgui.get_style().window_padding
    imgui.set_cursor_pos((imgui.get_window_width() - imgui_kit.help_marker_width() - padding.x, padding.y))
    with imgui_kit.help_marker_ctx("##help", width_em=28) as shown:  # an (i): the zoom in words, then the guide
        if shown:
            imgui.text_wrapped(zoom_in_words(state.width))
            imgui.separator()
            rich_md.render_this_file("Help")
    state.card_height = end_over_picture().y


def all_pixels_control(side: int, width: float) -> None:
    """For one engine's picture, when the budget did not afford all its pixels: a button to compute them, then
    their progress and a button to cancel"""
    state = STATE
    assert state is not None
    job = state.all_pixels
    if job is not None and job.side == side:
        seconds_left = (time.perf_counter() - job.start_time) * (1 - job.fraction) / max(job.fraction, 0.02)
        imgui.progress_bar(job.fraction, (width - em_size(5), 0), f"{job.fraction:.0%}, {seconds_left:.0f} s left")
        hello_imgui.set_item_is_live()  # the computation goes on at each frame: no idling meanwhile
        imgui.same_line()
        if imgui.button("Cancel", (em_size(4.4), 0)):
            job.steps.close()  # the engine stops there
            state.all_pixels, state.painted = None, None  # and the coarse picture comes back
            state.cancelled = (job.wanted, side)  # it will not start again by itself
    elif side < len(state.shrinks) and state.shrinks[side] > 1 and state.where is not None:
        imgui.begin_disabled(job is not None)  # one at a time
        engine = state.engine if side == 0 else state.other
        assert engine is not None
        seconds = state.seconds_for(engine, state.where[3] * state.where[4]) or 0.0
        if imgui.button(f"All the pixels (about {seconds:.0f} s)", (width, 0)):
            state.start_all_pixels(side, engine)
        imgui.end_disabled()


def side_panel(side: int, x: float, y: float) -> None:
    """In a split view, beside the divider: the engine of this side (a menu), its cost, and "All the pixels".
    The left one ends at x, the right one starts there."""
    state = STATE
    assert state is not None and state.other is not None
    left = x - state.side_widths[side] if side == 0 else x
    begin_over_picture(f"##side {side}", imgui.ImVec2(left, y))
    engines = [state.engine, state.other]
    menu_button(engines[side].name, f"engine {side}", upwards=False)
    chosen = engine_menu(f"engine {side}", engines[side], engines[1 - side])
    if chosen is not engines[side]:
        state.explained = chosen  # the explanations follow the engine, when it changes
        if side == 0:
            state.engine = chosen
        else:
            state.other = chosen
    if side < len(state.shrinks) and side < len(state.counts):
        imgui.same_line()
        imgui.text_disabled(cost_text(side))
    all_pixels_control(side, em_size(17))
    state.side_widths[side] = end_over_picture().x


def depth_gauge(right: float, top: float, bottom: float) -> None:
    """Along the right edge: how deep we are, from a zoom of 1 to 10^300, and where double precision ends"""
    state = STATE
    assert state is not None
    draw_list = imgui.get_window_draw_list()
    white, dim, orange = imgui.IM_COL32(255, 255, 255, 255), imgui.IM_COL32(255, 255, 255, 190), \
        imgui.IM_COL32(255, 170, 0, 255)
    x, line_height = right - em_size(0.9), imgui.get_text_line_height()

    def y_of(decade: float) -> float:
        return top + (bottom - top) * min(max(decade, 0), DEEPEST) / DEEPEST

    draw_list.add_rect_filled((right - em_size(4.6), top - em_size(0.8)), (right, bottom + em_size(0.8)),
                              imgui.IM_COL32(0, 0, 0, 170), em_size(0.4))
    draw_list.add_line((x, top), (x, y_of(DOUBLE_ENDS)), white, 3)  # where every engine works
    draw_list.add_line((x, y_of(DOUBLE_ENDS)), (x, bottom), orange, 3)  # the perturbation only
    for decade in (DOUBLE_ENDS, *range(50, DEEPEST + 1, 50)):  # the end of double, then every 50 decades
        label, color = f"10^{decade}", white if decade == DOUBLE_ENDS else dim
        draw_list.add_line((x - em_size(0.3), y_of(decade)), (x, y_of(decade)), color, 1)
        draw_list.add_text((x - em_size(0.6) - imgui.calc_text_size(label).x, y_of(decade) - line_height / 2), color,
                           label)
    here = y_of(math.log10(WHOLE_SET[2] / state.width))
    draw_list.add_circle_filled((x, here), em_size(0.45), white)
    draw_list.add_circle_filled((x, here), em_size(0.28), orange if here > y_of(DOUBLE_ENDS) else imgui.IM_COL32(
        32, 107, 203, 255))


def explanations() -> None:
    """The side panel: the equation, then a tab per engine: how it works, and its code"""
    state = STATE
    assert state is not None
    if imgui.button(icons_fontawesome_6.ICON_FA_ANGLES_RIGHT):
        state.notes_open = False
    imgui.set_item_tooltip("Hide the explanations: the picture takes the whole window")
    imgui.same_line()
    imgui.text_disabled("Explanations")
    rich_md.render_this_file("Intro")
    rich_md.render_this_file("View")
    if imgui.collapsing_header("The view's code"):
        rich_md.render_this_file("View#code")
    if imgui.begin_tab_bar("##engines"):
        follow = state.explained is not state.shown_tab  # the engine changed: its tab comes forward
        for engine in ENGINES:
            flags = imgui.TabItemFlags_.set_selected if follow and engine is state.explained else 0
            if imgui.begin_tab_item(engine.name, None, flags)[0]:
                if not follow:
                    state.explained = state.shown_tab = engine  # the tab open, or just clicked by the reader
                elif engine is state.explained:
                    state.shown_tab = engine
                rich_md.render_this_file(engine.section)
                if imgui.collapsing_header("Its code"):
                    rich_md.render_this_file(engine.section + "#code")
                    if engine.cpp_region:
                        if imgui.collapsing_header("run_in_bands: in bands, from several threads"):
                            rich_md.render_this_file("Bands")
                            rich_md.render_this_file("Bands#code")
                        rich_md.render("### The C++ loop")
                        rich_md.render_file(str(HERE / "mandel_kernels.cpp"), engine.cpp_region)
                        rich_md.render_this_file("Pattern")
                imgui.end_tab_item()
        imgui.end_tab_bar()


def gui() -> None:
    global STATE
    if STATE is None:
        STATE = State()
    state = STATE
    available = imgui.get_content_region_avail()
    spacing = imgui.get_style().item_spacing.x
    notes_width = min(em_size(34), available.x * 0.45) if state.notes_open else 0.0
    top_left, w, h = picture(imgui.ImVec2(available.x - notes_width - (spacing if state.notes_open else 0),
                                          available.y))
    right, bottom = top_left.x + w, top_left.y + h

    # Over the picture: the gauge, the title card with the controls, and "All the pixels"
    gauge = em_size(5.2)  # the width kept for the gauge, along the right edge
    depth_gauge(right - em_size(0.6), top_left.y + em_size(4.2), bottom - em_size(4.2))
    title_card(top_left, h)
    if state.other is None:  # bottom right
        job = state.all_pixels
        if job is not None or (state.shrinks and state.shrinks[0] > 1):
            width = em_size(18)
            frame = imgui.get_frame_height() + 2 * imgui.get_style().window_padding.y
            begin_over_picture("##all pixels", imgui.ImVec2(right - gauge - em_size(1.8) - width,
                                                            bottom - em_size(0.6) - frame))
            all_pixels_control(0, width)
            end_over_picture()
    elif len(state.shrinks) > 1:  # beside the divider: each side has its engine, its cost and its button
        x, y = top_left.x + state.split * w, top_left.y + (HANDLE_EM - 1.1) * em_size(1)
        side_panel(0, x - em_size(1.4), y)
        side_panel(1, x + em_size(1.4), y)
    if not state.notes_open:  # an arrow to bring the explanations back
        padding, side = imgui.get_style().window_padding, imgui.get_frame_height()
        begin_over_picture("##notes button", imgui.ImVec2(right - em_size(0.6) - side - 2 * padding.x,
                                                          top_left.y + em_size(0.6)),
                           imgui.ImVec2(side + 2 * padding.x, side + 2 * padding.y))
        if imgui.button(icons_fontawesome_6.ICON_FA_ANGLES_LEFT, (side, side)):
            state.notes_open = True
        imgui.set_item_tooltip("Show the explanations: the equation, how the engine works, its code")
        imgui.end_child()

    if state.notes_open:
        imgui.set_cursor_screen_pos(imgui.ImVec2(right + spacing, top_left.y))
        imgui.begin_child("##explanations", imgui.ImVec2(notes_width, available.y))
        explanations()
        imgui.end_child()


def main() -> None:
    immapp.run(gui, window_title="Mandelbrot engines", window_size=(1500, 900), with_markdown=True, with_latex=True)


if __name__ == "__main__":
    main()
