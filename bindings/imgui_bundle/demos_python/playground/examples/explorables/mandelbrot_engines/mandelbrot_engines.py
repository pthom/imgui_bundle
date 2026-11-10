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

**Wheel** to zoom, **drag** to move. Then change the engine, and watch the time.
Black where there should be detail? Raise the iterations.
"""

# ruff: noqa: E402  # the story comes first
import ctypes
import math
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Callable

import numpy as np
from imgui_bundle import em_size, imgui, immapp, immvision, rich_md

THREADS = os.cpu_count() or 4  # the bands of rows computed at once by the C++ engines (in a browser: one)
PREVIEW_SHRINK = 4  # while the view moves, a slow engine computes one pixel out of 4 x 4
SLOW_SECONDS = 0.05  # an engine is slow when a full picture takes longer
WHOLE_SET = ("-0.6", "0", 3.4)  # a view: the center (re, im), with as many digits as needed, and the width
ESCAPE2 = 256.0  # |z| > 16, squared
IN_BROWSER = sys.platform == "emscripten"
HERE = Path(__file__).parent

Counts = tuple[np.ndarray, np.ndarray]  # for each pixel: its number of steps, and |z|^2 at the last one


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
The definition, as two loops. It is the slowest by far, so it computes one pixel out of 64.
::code
"""
def python_engine(view: View) -> Counts:
    x0, y0 = view.corner()
    count, size2 = np.empty((view.h, view.w), np.int32), np.empty((view.h, view.w), np.float32)
    for row in range(view.h):
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
It computes one pixel out of 4.
::code
"""
def numpy_engine(view: View) -> Counts:
    x0, y0 = view.corner()
    c = ((x0 + np.arange(view.w) * view.pixel)[None, :] + 1j * (y0 - np.arange(view.h) * view.pixel)[:, None]).ravel()
    z = np.zeros_like(c)
    count, size2 = np.full(c.shape, view.max_iter, np.int32), np.zeros(c.shape, np.float32)
    alive = np.arange(c.size)  # the pixels still iterating
    for n in range(1, view.max_iter + 1):
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
    if POOL:
        list(POOL.map(lambda band: kernel(*pointers, *band), bands))
    else:
        for band in bands:
            kernel(*pointers, *band)
    return count, size2


@dataclass
class Engine:
    name: str
    section: str  # its ::md section in this file
    compute: Callable[[View], Counts]
    shrink: int  # computes one pixel out of shrink x shrink
    needs_cpp: bool = False


ENGINES = [
    Engine("Python", "Python", python_engine, shrink=8),
    Engine("numpy", "numpy", numpy_engine, shrink=2),
    Engine("C++", "Cpp", cpp_engine, shrink=1, needs_cpp=True),
    Engine("C++ with perturbation", "Perturbation", perturbation_engine, shrink=1, needs_cpp=True),
]

# Places to visit: a name, a view (center, width), a number of iterations, and what to see there
SEAHORSE = ("-0.743916538692433356599334896378352022720811396866", "0.131688791359494617577789121421345189627001255958")
PLACES = [
    ("The whole set", WHOLE_SET, 300, "The starting point."),
    ("Seahorse valley", (*SEAHORSE, 3e-9), 3000,
     "Spirals within spirals. The C++ engine starts to drift here: compare it with the perturbation."),
    ("The end of double", (*SEAHORSE, 2e-14), 4500,
     "With the C++ engine: blocks. With the perturbation: the picture."),
    ("Seahorse, at 1e-40", (*SEAHORSE, 1e-37), 9000,
     "Only the perturbation gets here. Its reference orbit has 60 digits."),
    ("i, at 1e-290", ("0", "1", 1e-287), 2000,
     "The point c = i is on the boundary: there is detail at every scale. A proton next to the observable universe "
     "is a ratio of 1e-41: this is far beyond."),
]


# ======================================================================================================================
#                                           From counts to colors
# ======================================================================================================================
PALETTE = np.array([(0, 7, 100), (32, 107, 203), (237, 255, 255), (255, 170, 0), (0, 2, 0), (0, 7, 100)])
PALETTE_AT = [0.0, 0.16, 0.42, 0.6425, 0.8575, 1.0]  # a cyclic gradient: night blue, white, orange, black


def colors(counts: Counts, max_iter: int) -> np.ndarray:
    """An RGB picture. The count, minus log2(log2|z|), varies smoothly from a pixel to the next: no bands.
    The palette starts at the lowest count of the picture: a deep zoom, where all counts are high, keeps its
    contrast."""
    count, size2 = counts
    smooth = count + 1 - np.log2(np.log2(np.maximum(size2, 4.0)) / 2)
    t = 0.45 * np.log2(1 + (smooth - smooth.min()) / 6) % 1.0
    rgb = np.stack([np.interp(t, PALETTE_AT, PALETTE[:, k]) for k in range(3)], axis=-1)
    rgb[count >= max_iter] = 0
    return rgb.astype(np.uint8)


# ======================================================================================================================
#                                           The GUI
# ======================================================================================================================
class State:
    def __init__(self) -> None:
        self.engine = ENGINES[2 if KERNELS else 1]
        self.max_iter = 300
        self.image = np.zeros((2, 2, 3), np.uint8)
        self.computed: tuple[str, View] | None = None  # what the image shows
        self.where: tuple[Decimal, Decimal, float, int, int] | None = None  # the view at the last frame
        self.seconds = 0.0  # the time of the last full picture
        self.timed: View | None = None  # its view
        self.moved_at = 0.0  # when the view last changed
        self.dive: tuple[float, float, float] | None = None  # a zoom animation: from width, to width, start time
        self.go_to(WHOLE_SET, 300, animate=False)

    def go_to(self, place: tuple[str, str, float], max_iter: int, animate: bool = True) -> None:
        getcontext().prec = digits_for(place[2] / 2000)
        self.center_re, self.center_im, self.width = Decimal(place[0]), Decimal(place[1]), place[2]
        self.max_iter = max_iter
        if animate:
            self.dive, self.width = (float(WHOLE_SET[2]), place[2], imgui.get_time()), float(WHOLE_SET[2])

    def move(self, d_re: float, d_im: float) -> None:
        getcontext().prec = digits_for(self.width / 2000)
        self.center_re += Decimal(d_re)
        self.center_im += Decimal(d_im)


STATE: State | None = None
DIVE_SECONDS_PER_DECADE = 0.12  # the speed of the zoom animation


def picture(size: imgui.ImVec2) -> None:
    """The picture, its mouse handling, and its computation when something changed"""
    state = STATE
    assert state is not None
    w, h = max(int(size.x), 16), max(int(size.y), 16)
    pixel = state.width / w

    # The mouse: an invisible button under the picture takes the wheel and the drags
    top_left = imgui.get_cursor_screen_pos()
    imgui.invisible_button("##picture", imgui.ImVec2(w, h))
    imgui.set_item_key_owner(imgui.Key.mouse_wheel_y)
    io = imgui.get_io()
    if imgui.is_item_active() and (io.mouse_delta.x or io.mouse_delta.y):
        state.move(-io.mouse_delta.x * pixel, io.mouse_delta.y * pixel)
    if imgui.is_item_hovered() and io.mouse_wheel and state.dive is None:
        factor = 0.8 ** io.mouse_wheel
        if 1e-300 < state.width * factor < 8:  # zoom around the mouse: the point under it stays there
            mx, my = io.mouse_pos.x - top_left.x - w / 2, io.mouse_pos.y - top_left.y - h / 2
            state.move(mx * pixel * (1 - factor), -my * pixel * (1 - factor))
            state.width *= factor

    # A dive to a place: the width shrinks at a constant number of decades per second
    if state.dive is not None:
        start, end, t0 = state.dive
        decades = math.log10(start / end)
        progress = min(1.0, (imgui.get_time() - t0) / max(0.5, decades * DIVE_SECONDS_PER_DECADE))
        state.width = start * (end / start) ** progress
        if progress >= 1.0:
            state.dive = None

    # Compute, when the view or the engine changed. While the view moves, a slow engine gives a coarse preview.
    where = (state.center_re, state.center_im, state.width, w, h)
    if where != state.where:
        state.where, state.moved_at = where, imgui.get_time()
    moving = imgui.get_time() - state.moved_at < 0.15
    shrink = state.engine.shrink * (PREVIEW_SHRINK if moving and state.seconds > SLOW_SECONDS else 1)
    view = View(state.center_re, state.center_im, state.width / w * shrink, w // shrink, h // shrink, state.max_iter)
    wanted = (state.engine.name, view)
    refresh = wanted != state.computed
    if refresh:
        start_time = time.perf_counter()
        state.image = colors(state.engine.compute(view), view.max_iter)
        if shrink > 1:
            state.image = np.ascontiguousarray(state.image.repeat(shrink, axis=0).repeat(shrink, axis=1))
        if shrink == state.engine.shrink:  # a full picture
            state.seconds, state.timed = time.perf_counter() - start_time, view
        state.computed = wanted
    imgui.set_cursor_screen_pos(top_left)
    immvision.image_display("##mandelbrot", state.image, (w, h), refresh_image=refresh)


# To picture a zoom: if the whole set were as wide as the observable universe, what would the picture be as wide as?
UNIVERSE = 8.8e26  # meters
SIZES = [(8.8e26, "the observable universe"), (1e21, "a galaxy"), (9e12, "the solar system"), (1.3e7, "the Earth"),
         (4e4, "a city"), (1.7, "a person"), (1e-4, "a hair's width"), (1e-6, "a bacterium"), (1e-10, "an atom"),
         (1.7e-15, "a proton"), (1.6e-35, "the Planck length, the smallest length that physics describes")]


def zoom_in_words(width: float) -> str:
    zoom = WHOLE_SET[2] / width
    if zoom < 10:
        return f"Zoom: {zoom:.1f}."
    exponent = math.floor(math.log10(zoom))
    number = f"{zoom:,.0f}" if zoom < 1e6 else f"{zoom / 10 ** exponent:.1f} x 10^{exponent}"
    size = UNIVERSE / zoom
    if size < SIZES[-1][0] / 100:
        thing = f"10^{round(math.log10(SIZES[-1][0] / size))} times smaller than the Planck length, the smallest " \
                "length that physics describes"
    else:
        thing = "as wide as " + min(SIZES, key=lambda entry: abs(math.log10(entry[0] / size)))[1]
    return f"Zoom: {number}. If the whole set were as wide as the observable universe, this picture would be {thing}."


def same_line_if_room(next_label: str) -> None:
    """Puts the next widget on the same line, when it fits"""
    imgui.same_line()
    if imgui.get_cursor_pos_x() + imgui.calc_text_size(next_label).x + em_size(2.5) > imgui.get_window_width():
        imgui.new_line()


def controls() -> None:
    state = STATE
    assert state is not None
    rich_md.render_this_file("Intro")

    imgui.separator_text("Engine")
    for i, engine in enumerate(ENGINES):
        if i > 0:
            same_line_if_room(engine.name)
        imgui.begin_disabled(engine.needs_cpp and KERNELS is None)
        if imgui.radio_button(engine.name, state.engine is engine):
            state.engine, state.seconds = engine, 0.0
        imgui.end_disabled()
    if KERNELS is None:
        imgui.text_wrapped("The C++ engines need a C++ compiler (c++ or cl) at the first run: none was found.")
    if state.timed is not None:
        megapixels = state.timed.w * state.timed.h / 1e6
        imgui.text(f"{state.seconds * 1000:.0f} ms for {megapixels:.2f} million pixels")
        imgui.same_line()
        imgui.text_disabled(f"  {megapixels / max(state.seconds, 1e-6):.1f} million pixels per second")
        if state.seconds > SLOW_SECONDS:
            imgui.text_disabled("A coarse preview while the view moves, the full picture when it stops.")

    imgui.separator_text("Where we are")
    imgui.text_wrapped(zoom_in_words(state.width))
    digits = max(3, int(-math.log10(state.width)) + 4)
    shown = [f"{value:+.{digits}f}" for value in (state.center_re, state.center_im)]
    if digits > 40:  # the first digits only
        shown = [f"{text[:22]}..." for text in shown]
    imgui.text_disabled(f"center  {shown[0]}  {shown[1]} i" + (f"  ({digits} digits)" if digits > 40 else ""))
    for i, (name, place, max_iter, story) in enumerate(PLACES):
        if i > 0:
            same_line_if_room(name)
        if imgui.button(name):
            state.go_to(place, max_iter)
        imgui.set_item_tooltip(story)
    imgui.set_next_item_width(em_size(10))
    _, state.max_iter = imgui.slider_int("iterations", state.max_iter, 50, 50000, flags=imgui.SliderFlags_.logarithmic)
    imgui.set_item_tooltip("Black where there should be detail? Raise the iterations.")

    imgui.separator_text("How this engine works")
    rich_md.render_this_file(state.engine.section)
    if imgui.collapsing_header("Its code"):
        rich_md.render_this_file(state.engine.section + "#code")
        if state.engine.needs_cpp:
            rich_md.render_file(str(HERE / "mandel_kernels.cpp"))
            rich_md.render_this_file("Pattern")


def gui() -> None:
    global STATE
    if STATE is None:
        STATE = State()
    available = imgui.get_content_region_avail()
    wide_window = available.x > em_size(60)  # else (a phone): the picture above the texts
    picture_size = imgui.ImVec2(available.x * 0.58, available.y) if wide_window else \
        imgui.ImVec2(available.x, available.x * 0.75)
    picture(picture_size)
    if wide_window:
        imgui.same_line()
        imgui.begin_child("##controls", imgui.ImVec2(0, available.y))
    controls()
    if wide_window:
        imgui.end_child()


def main() -> None:
    immapp.run(gui, window_title="Mandelbrot engines", window_size=(1500, 900), with_markdown=True, with_latex=True)


if __name__ == "__main__":
    main()
