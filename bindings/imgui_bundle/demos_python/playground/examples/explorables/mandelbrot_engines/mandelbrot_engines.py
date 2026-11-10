"""One Mandelbrot set, four engines: Python, numpy, C++, and C++ with perturbation (deep zoom)

The same picture, computed in four ways. Python draws the GUI; the engine only fills an array of numbers.
Zoom with the wheel, drag to move, and switch engines to compare their speed and how deep they can go.

This file is its own narrative (narrative programming, see imgui_rich_md): the ::md sections below are the texts
shown beside the picture, next to the code they explain. The C++ loops are in mandel_kernels.cpp.
"""

r"""::md Intro
# One Mandelbrot set, four engines
Every pixel is a number $c$. Iterate $z \leftarrow z^2 + c$ from $z = 0$, and count the steps until $|z| > 16$:
the count gives the color. Points that never escape are in the set, in black.

Pick a place, change the engine, and watch the time under the picture. The gauge on the right shows how deep
we are: its white part, down to a zoom of 10^13, is where every engine works. Its orange part is for the
perturbation only.
"""

r"""::md Help
**Moving around**
* **Wheel**: zoom, around the mouse.
* **Drag**: move the view.
* **Double click**: dive towards the clicked point.
* **Back**: return to the previous view. Places and double clicks are remembered.

**Places**
* A click on a name goes to its first zoom.
* The arrow beside it lists its deeper zooms.

**Engines**
* Every engine gets the same time for a picture: 1.5 s, and much less while the view moves.
* An engine that cannot afford all the pixels computes one out of 4, 16 or 64.
  **All the pixels**, at the bottom right, then computes them all in the background.

**Iterations**
* *Automatic*: while you move by hand, the page raises them when the picture needs them.
* The slider sets them by hand, and turns *automatic* off.

**Colors**: click a gradient. The picture is recolored at once, not computed again.

**The gauge** on the right: how deep the view is. White: every engine works. Orange: the perturbation only.
"""

# ruff: noqa: E402  # the story comes first
import ctypes
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Callable

import numpy as np
from imgui_bundle import em_size, hello_imgui, icons_fontawesome_6, imgui, imgui_kit, immapp, immvision, rich_md

THREADS = os.cpu_count() or 4  # the bands of rows computed at once by the C++ engines (in a browser: one)
MOVING_BUDGET = 0.04  # seconds for a picture while the view moves. An engine that cannot afford all the pixels
STILL_BUDGET = 1.5  # in its budget computes one out of 4, 16 or 64. This one: once the view stopped
WHOLE_SET = ("-0.6", "0", 3.4)  # a view: the center (re, im), with as many digits as needed, and the width
ESCAPE2 = 256.0  # |z| > 16, squared
IN_BROWSER = sys.platform == "emscripten"
HERE = Path(__file__).parent

Counts = tuple[np.ndarray, np.ndarray]  # for each pixel: its number of steps, and |z|^2 at the last one
PROGRESS = [0.0]  # of the picture computed in the background ("All the pixels"): 0 to 1


def report(fraction: float) -> None:
    """An engine says how far it is. Only the background picture has a progress bar."""
    if threading.current_thread() is not threading.main_thread():
        PROGRESS[0] = fraction


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


# ======================================================================================================================
#                                           The four engines
# ======================================================================================================================

r"""::md Python
### Python
The definition, as two loops. It is the slowest by far: in the time given to a picture, it can only afford
one pixel out of 16 or 64.
::code
"""
def python_engine(view: View) -> Counts:
    x0, y0 = view.corner()
    count, size2 = np.empty((view.h, view.w), np.int32), np.empty((view.h, view.w), np.float32)
    for row in range(view.h):
        report(row / view.h)
        for col in range(view.w):
            c = complex(x0 + col * view.pixel, y0 - row * view.pixel)
            z, n = 0j, 0
            while n < view.max_iter and z.real * z.real + z.imag * z.imag <= ESCAPE2:
                z = z * z + c
                n += 1
            count[row, col], size2[row, col] = n, min(z.real * z.real + z.imag * z.imag, 1e30)
    return count, size2
# ::endcode


r"""::md numpy
### numpy
All the pixels advance together, one step per line of Python. The pixels that escaped leave the computation.
::code
"""
def numpy_engine(view: View) -> Counts:
    x0, y0 = view.corner()
    c = ((x0 + np.arange(view.w) * view.pixel)[None, :] + 1j * (y0 - np.arange(view.h) * view.pixel)[:, None]).ravel()
    z = np.zeros_like(c)
    count, size2 = np.full(c.shape, view.max_iter, np.int32), np.zeros(c.shape, np.float32)
    alive = np.arange(c.size)  # the pixels still iterating
    for n in range(1, view.max_iter + 1):
        report(n / view.max_iter)
        z[alive] = z[alive] * z[alive] + c[alive]
        s = z[alive].real ** 2 + z[alive].imag ** 2
        size2[alive] = s
        out = s > ESCAPE2
        count[alive[out]] = n
        alive = alive[~out]
    return count.reshape(view.h, view.w), size2.reshape(view.h, view.w)
# ::endcode


r"""::md Cpp
### C++
The same two loops as the Python engine, in C++ (`mandel_double`, below). Python gives it two numpy arrays to
fill, through `ctypes`: no copy, no wrapper to generate. `ctypes` releases Python's lock during the call, so a
pool of threads computes several bands of rows at once.

It is fast, but a `double` holds 16 digits. Below a pixel size of about 1e-13, pixels start to be wrong; at
1e-16, neighbours get the same $c$ and the picture turns into blocks.
::code
"""
def cpp_engine(view: View) -> Counts:
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


def perturbation_engine(view: View) -> Counts:
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
for the browser into a WebAssembly module of a few hundred bytes.
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
        return ctypes.CDLL(str(HERE / "mandel_kernels.wasm.so"))
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


def run_in_bands(view: View, kernel: Callable[[ctypes.c_void_p, ctypes.c_void_p, int, int], None]) -> Counts:
    """Calls kernel(count, size2, row0, row1) for each band of rows, in the pool of threads"""
    count, size2 = np.empty((view.h, view.w), np.int32), np.empty((view.h, view.w), np.float32)
    pointers = count.ctypes.data_as(PTR), size2.ctypes.data_as(PTR)
    rows = np.linspace(0, view.h, (THREADS if POOL else 1) * 4 + 1).astype(int)  # small bands: an even load
    bands = [(int(row0), int(row1)) for row0, row1 in zip(rows[:-1], rows[1:], strict=True)]
    run_all = POOL.map if POOL else map  # in a browser: one band after the other
    for i, _ in enumerate(run_all(lambda band: kernel(*pointers, *band), bands)):
        report((i + 1) / len(bands))
    return count, size2


@dataclass
class Engine:
    name: str
    section: str  # its ::md section in this file
    compute: Callable[[View], Counts]
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
PLACES = [
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


def colors(counts: Counts, max_iter: int, palette: str) -> np.ndarray:
    """An RGB picture. The count, minus log2(log2|z|), varies smoothly from a pixel to the next: no bands.
    The palette starts at the lowest count of the picture: a deep zoom, where all counts are high, keeps its
    contrast."""
    count, size2 = counts
    smooth = count + 1 - np.log2(np.log2(np.maximum(size2, 4.0)) / 2)
    rgb = palette_colors(palette, 0.45 * np.log2(1 + (smooth - smooth.min()) / 6) % 1.0)
    rgb[count >= max_iter] = 0
    return rgb.astype(np.uint8)


# ======================================================================================================================
#                                           The GUI
# ======================================================================================================================
class AllPixels(threading.Thread):
    """A picture with all its pixels, computed in the background: the page stays alive, and shows a progress bar.
    (In a browser, without threads: computed at once, the page waits.)"""
    def __init__(self, engine: "Engine", view: View, wanted: tuple[Any, ...]) -> None:
        super().__init__(daemon=True)
        self.engine, self.view, self.wanted = engine, view, wanted
        self.counts: Counts | None = None
        self.start_time = time.perf_counter()
        self.seconds = 0.0
        PROGRESS[0] = 0.0
        if POOL:
            self.start()
        else:
            self.run()

    def run(self) -> None:
        counts = self.engine.compute(self.view)
        self.seconds = time.perf_counter() - self.start_time
        self.counts = counts  # last: the page takes the picture as soon as it is there


class State:
    def __init__(self) -> None:
        self.engine = ENGINES[2 if KERNELS else 1]
        self.max_iter = 300
        self.image = np.zeros((2, 2, 3), np.uint8)
        self.counts: Counts | None = None  # the counts behind the image: a change of palette only recolors them
        self.palette = next(iter(PALETTES))
        self.painted: tuple[Any, ...] | None = None  # what the image shows: the computation, and its palette
        self.computed: tuple[str, Decimal, Decimal, float, int, int, int] | None = None  # what the image shows
        self.where: tuple[Decimal, Decimal, float, int, int] | None = None  # the view at the last frame
        self.seconds = 0.0  # the time of the last picture
        self.timed: View | None = None  # its view
        self.shrink = 8  # it holds one pixel out of shrink x shrink
        self.all_pixels: AllPixels | None = None  # the picture computed in the background, see the button
        self.pixel_seconds: float | None = None  # the cost of a pixel, measured on the last picture
        self.moved_at = 0.0  # when the view last changed
        self.dive: tuple[float, float, float] | None = None  # a zoom animation: from width, to width, start time
        self.center_re, self.center_im, self.width = Decimal(0), Decimal(0), float(WHOLE_SET[2])
        self.history: list[tuple[Decimal, Decimal, float, int]] = []  # the views to come back to
        self.auto_iterations = True  # the page adapts the iterations when the view is moved by hand
        self.by_hand = False  # the view was moved by hand since the last place
        self.late: float | None = None  # in the last picture: the count below which 90% of the escaped pixels are
        self.places_open, self.notes_open = True, True  # the panel over the picture, the explanations beside it
        self.go_to(WHOLE_SET, 300, animate=False)

    def remember(self) -> None:
        self.history.append((self.center_re, self.center_im, self.width, self.max_iter))

    def back(self) -> None:
        self.center_re, self.center_im, self.width, self.max_iter = self.history.pop()
        self.dive, self.pixel_seconds = None, None

    def go_to(self, place: tuple[str, str, float], max_iter: int, animate: bool = True) -> None:
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
        self.pixel_seconds = None  # a new place: a new cost
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
    if imgui.is_item_active() and (io.mouse_delta.x or io.mouse_delta.y):
        state.move(-io.mouse_delta.x * pixel, io.mouse_delta.y * pixel)
    if imgui.is_item_hovered() and io.mouse_wheel and state.dive is None:
        factor = 0.8 ** io.mouse_wheel
        if 10.0 ** -DEEPEST < state.width * factor < 8:  # zoom around the mouse: the point under it stays there
            state.move(mx * pixel * (1 - factor), -my * pixel * (1 - factor))
            state.width *= factor
            state.by_hand = True
    if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(0) and state.width > 10.0 ** (3 - DEEPEST):
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
    shrink = 8  # for a first picture: it measures the cost of a pixel. Then: what the budget affords
    if state.pixel_seconds is not None:
        affordable = (MOVING_BUDGET if moving else STILL_BUDGET) / state.pixel_seconds
        shrink = next((k for k in (1, 2, 4) if (w // k) * (h // k) <= affordable), 8)
    wanted = (state.engine.name, *where, state.max_iter)
    refresh = wanted != state.computed or shrink < state.shrink
    job = state.all_pixels
    if job is not None and job.counts is not None:  # the background picture is ready: show it, if we are still there
        if job.wanted == wanted:
            state.counts, state.seconds, state.timed = job.counts, job.seconds, job.view
            state.computed, state.shrink = wanted, 1
        state.all_pixels = None
    elif refresh:
        view = View(state.center_re, state.center_im, state.width / w * shrink, w // shrink, h // shrink,
                    state.max_iter)
        start_time = time.perf_counter()
        state.counts = counts = state.engine.compute(view)
        state.seconds, state.timed = time.perf_counter() - start_time, view
        state.pixel_seconds = state.seconds / (view.w * view.h)
        state.computed, state.shrink = wanted, shrink
        escaped = counts[0][counts[0] < view.max_iter]
        state.late = float(np.percentile(escaped, 90)) if escaped.size else math.inf

    # Color the counts, when they or the palette changed
    painted = (state.computed, state.shrink, state.palette)
    repaint = painted != state.painted
    if repaint and state.counts is not None and state.timed is not None:
        image = colors(state.counts, state.timed.max_iter, state.palette)
        state.image = np.ascontiguousarray(image.repeat(state.shrink, axis=0).repeat(state.shrink, axis=1))
        state.painted = painted
    imgui.set_cursor_screen_pos(top_left)
    immvision.image_display("##mandelbrot", state.image, (w, h), refresh_image=repaint)
    return top_left, w, h


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
def begin_over_picture(name: str, pos: imgui.ImVec2, size: imgui.ImVec2, inputs: bool = True) -> None:
    """A semi-transparent panel at a fixed place over the picture (a height of 0: as tall as its content).
    To be closed with imgui.end_child()."""
    background = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    imgui.set_cursor_screen_pos(pos)
    imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(background.x, background.y, background.z, 0.82))
    child_flags = imgui.ChildFlags_.borders | (imgui.ChildFlags_.auto_resize_y if size.y == 0 else 0)
    imgui.begin_child(name, size, child_flags, 0 if inputs else imgui.WindowFlags_.no_inputs)
    imgui.pop_style_color()


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


def places_and_engine(top_left: imgui.ImVec2) -> None:
    """Top left: where to go, then how to compute"""
    state = STATE
    assert state is not None
    margin = em_size(0.6)
    begin_over_picture("##places", imgui.ImVec2(top_left.x + margin, top_left.y + margin),
                       imgui.ImVec2(em_size(31) if state.places_open else em_size(9), 0))
    if imgui.arrow_button("##fold", imgui.Dir.down if state.places_open else imgui.Dir.right):
        state.places_open = not state.places_open
    imgui.same_line()
    imgui.text("Go to" if state.places_open else "Places")
    imgui.same_line()
    with imgui_kit.help_marker_ctx("##help", width_em=28) as shown:  # an (i): how to move around, and the rest
        if shown:
            rich_md.render_this_file("Help")
    if not state.places_open:
        imgui.end_child()
        return
    back = icons_fontawesome_6.ICON_FA_ARROW_LEFT + "  Back"
    imgui.same_line(imgui.get_window_width() - imgui.calc_text_size(back).x - em_size(1.6))
    imgui.begin_disabled(not state.history)
    if imgui.button(back):
        state.back()
    imgui.end_disabled()
    imgui.set_item_tooltip("To the previous view")

    for i, (name, point, zooms) in enumerate(PLACES):
        if i > 0:
            same_line_if_room(name + "    ")
        if imgui.button(name):  # a click on the name: its first zoom
            state.go_to((*point, zooms[0][0]), zooms[0][1])
        below = imgui.ImVec2(imgui.get_item_rect_min().x, imgui.get_item_rect_max().y)
        if zooms[0][3]:  # an arrow beside it: the menu of its zooms, which opens under the button
            imgui.same_line(0, 1)
            if imgui.arrow_button(f"##zooms of {name}", imgui.Dir.down):
                imgui.open_popup(f"zooms of {name}")
            imgui.set_next_window_pos(below)
            imgui.set_next_window_size_constraints((em_size(21), 0), (imgui.FLT_MAX, imgui.FLT_MAX))  # room for (i)
            if imgui.begin_popup(f"zooms of {name}"):
                for width, max_iter, short, story in zooms:
                    zoom = math.floor(math.log10(WHOLE_SET[2] / width))
                    label = f"Zoom 10^{zoom}: {short}" if zoom >= 6 else f"Zoom {WHOLE_SET[2] / width:,.0f}: {short}"
                    if imgui.selectable(label, False, size=(em_size(17), 0))[0]:
                        state.go_to((*point, width), max_iter)
                    imgui.same_line()
                    imgui_kit.help_marker(story)  # an (i): what to see there
                imgui.end_popup()

    imgui.separator_text("Computed by")
    for i, engine in enumerate(ENGINES):
        if i > 0:
            same_line_if_room(engine.name)
        imgui.begin_disabled(bool(engine.cpp_region) and KERNELS is None)
        if imgui.radio_button(engine.name, state.engine is engine):
            state.engine, state.pixel_seconds, state.computed = engine, None, None
        imgui.end_disabled()
    if KERNELS is None:
        imgui.text_wrapped("The C++ engines need a C++ compiler (c++ or cl) at the first run: none was found.")
    imgui.set_next_item_width(em_size(9))
    changed, state.max_iter = imgui.slider_int("iterations", state.max_iter, 50, 500000,
                                               flags=imgui.SliderFlags_.logarithmic)
    if changed:
        state.pixel_seconds, state.auto_iterations = None, False  # set by hand: the page stops adapting them
    imgui.same_line()
    _, state.auto_iterations = imgui.checkbox("automatic", state.auto_iterations)
    imgui.set_item_tooltip("While you move the view by hand, the page raises the iterations when the boundary\n"
                           "needs them (black where there should be detail), and lowers them when it can.")
    palette_swatches()
    imgui.end_child()


def status(top_left: imgui.ImVec2, h: int) -> None:
    """Bottom left: what the picture cost, and where it is"""
    state = STATE
    assert state is not None
    if state.timed is None:
        return
    megapixels = state.timed.w * state.timed.h / 1e6
    cost = f"{state.engine.name}: {state.seconds * 1000:.0f} ms for {megapixels:.2f} million pixels"
    if state.shrink > 1:
        cost += f" (1 pixel out of {state.shrink ** 2})"
    margin, padding = em_size(0.6), imgui.get_style().window_padding
    width = imgui.calc_text_size(cost).x + 2 * padding.x + em_size(1)
    height = imgui.get_text_line_height() + imgui.get_frame_height_with_spacing() + 2 * padding.y
    begin_over_picture("##status", imgui.ImVec2(top_left.x + margin, top_left.y + h - margin - height),
                       imgui.ImVec2(width, height))
    imgui.text(cost)
    imgui.align_text_to_frame_padding()
    imgui.text(f"Zoom: {zoom_number(state.width)}")
    imgui.same_line()
    imgui_kit.help_marker(zoom_in_words(state.width))  # an (i): the zoom as a comparison of sizes
    imgui.end_child()


def all_pixels_button(right: float, bottom: float) -> None:
    """Bottom right, when the budget did not afford all the pixels: a button to compute them in the background,
    then their progress"""
    state = STATE
    assert state is not None
    job = state.all_pixels
    if job is None and (state.shrink == 1 or state.computed is None or state.timed is None):
        return
    margin, padding = em_size(0.6), imgui.get_style().window_padding
    width, height = em_size(19), imgui.get_frame_height() + 2 * padding.y
    begin_over_picture("##all pixels", imgui.ImVec2(right - margin - width, bottom - margin - height),
                       imgui.ImVec2(width, height))
    if job is not None:
        left = (time.perf_counter() - job.start_time) * (1 - PROGRESS[0]) / max(PROGRESS[0], 0.02)
        imgui.progress_bar(PROGRESS[0], (-1, 0), f"All the pixels: {PROGRESS[0]:.0%}, {left:.0f} s left")
        hello_imgui.set_item_is_live()  # the bar moves on its own: no idling while it is visible
    elif imgui.button(f"All the pixels (about {state.seconds * state.shrink ** 2:.0f} s)", (-1, 0)):
        view = state.timed
        assert view is not None
        full = View(view.center_re, view.center_im, view.pixel / state.shrink, view.w * state.shrink,
                    view.h * state.shrink, view.max_iter)
        state.all_pixels = AllPixels(state.engine, full, state.computed or ())
    imgui.end_child()


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
    """The side panel: the equation, how the selected engine works, and its code"""
    state = STATE
    assert state is not None
    if imgui.button(icons_fontawesome_6.ICON_FA_ANGLES_RIGHT):
        state.notes_open = False
    imgui.set_item_tooltip("Hide the explanations: the picture takes the whole window")
    imgui.same_line()
    imgui.text_disabled("Explanations")
    rich_md.render_this_file("Intro")
    rich_md.render_this_file(state.engine.section)
    if imgui.collapsing_header("Its code"):
        rich_md.render_this_file(state.engine.section + "#code")
        if state.engine.cpp_region:
            rich_md.render_file(str(HERE / "mandel_kernels.cpp"), state.engine.cpp_region)
            rich_md.render_this_file("Pattern")


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

    # Over the picture: the places and the engine, the status, the gauge, and two buttons on the right
    gauge = em_size(5.2)  # the width kept for the gauge, along the right edge
    depth_gauge(right - em_size(0.6), top_left.y + em_size(4.2), bottom - em_size(4.2))
    places_and_engine(top_left)
    status(top_left, h)
    all_pixels_button(right - gauge, bottom)
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
