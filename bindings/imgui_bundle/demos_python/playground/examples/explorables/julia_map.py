"""The Mandelbrot set as a map of Julia sets: click on the left picture to choose c, the right one follows.
This file is its own narrative: the comment blocks (@@md#Name ... @@/md) are markdown, and the two
@import directives below render them in the order of the story, with the code that follows each block."""

import os
import numpy as np
from imgui_bundle import imgui, immapp, immvision, hello_imgui, imgui_md

# @@md#Intro
# # The Mandelbrot set is a map of Julia sets
# Both pictures iterate the same rule, $z \leftarrow z^2 + c$, and color each pixel by how fast $z$ escapes.
# On the left, $c$ is the pixel and $z$ starts at $0$. On the right, $c$ is fixed and $z$ starts at the pixel.
# **Click anywhere on the left picture to choose $c$**: the Julia set on the right is the one for that $c$.
# @@/md

# @@md#Story
# ## What you are looking at
# @import {md_id=Escape}
# @import {md_id=Mandelbrot}
# @import {md_id=Julia}
# ## Why the boundary matters
# A Julia set is connected exactly when its $c$ belongs to the Mandelbrot set. Click just inside the big
# cardioid, then just outside: the set shatters into dust. Click along the boundary: each Julia set looks
# like the region of the map around its $c$, spirals for spirals, antennae for antennae. That is the
# sense in which the Mandelbrot set is a map.
# @@/md

# @@md#Escape
# ### Escape time
# Iterate $z \leftarrow z^2 + c$ and count the steps until $|z| > 2$, after which $z$ flies to infinity.
# A point that survives the whole budget is considered in the set. The normalized count is the color.
# @@/md
def escape_time(z: np.ndarray, c: np.ndarray, max_iter: int = 80) -> np.ndarray:
    count = np.full(z.shape, max_iter, dtype=np.float32)
    for i in range(max_iter):
        z = z * z + c
        escaped = np.abs(z) > 2.0
        count[escaped & (count == max_iter)] = i
        z[escaped] = 2.0  # keep the escaped values small
    return count / max_iter

MANDEL_RE, MANDEL_IM = (-2.2, 0.8), (-1.5, 1.5)  # the window of the map

# @@md#Mandelbrot
# ### The map: $c$ varies, $z_0 = 0$
# @@/md
def mandelbrot_image(size: int = 300) -> np.ndarray:
    re = np.linspace(*MANDEL_RE, size, dtype=np.float32)
    im = np.linspace(*MANDEL_IM, size, dtype=np.float32)
    c = (re[None, :] + 1j * im[:, None]).astype(np.complex64)
    return escape_time(np.zeros_like(c), c)

# @@md#Julia
# ### One Julia set: $c$ fixed, $z_0$ varies
# @@/md
def julia_image(c: complex, size: int = 300) -> np.ndarray:
    re = np.linspace(-1.7, 1.7, size, dtype=np.float32)
    im = np.linspace(-1.7, 1.7, size, dtype=np.float32)
    z0 = (re[None, :] + 1j * im[:, None]).astype(np.complex64)
    return escape_time(z0, np.full_like(z0, c))


# The GUI: two images side by side, the narrative around them
class State:
    def __init__(self) -> None:
        self.size = 300
        self.c = complex(-0.8, 0.156)
        self.mandel = mandelbrot_image(self.size)
        self.julia = julia_image(self.c, self.size)
        self.params_mandel = self._params()
        self.params_julia = self._params()

    def _params(self) -> immvision.ImageParams:
        p = immvision.ImageParams()
        p.image_display_size = (self.size, self.size)
        p.colormap_settings.colormap = "Magma"
        p.show_options_button = False
        p.show_zoom_buttons = False
        p.show_image_info = False
        p.show_pixel_info = False
        p.zoom_with_mouse_wheel = False
        p.pan_with_mouse = False
        p.add_watched_pixel_on_double_click = False
        return p


THIS_FILE = os.path.basename(__file__)  # the lesson imports its own blocks (see the module docstring)
hello_imgui.add_assets_search_path(os.path.dirname(__file__))
state = State()


def gui() -> None:
    imgui_md.render(f'@import "{THIS_FILE}" {{md_id=Intro}}')
    immvision.image("Mandelbrot", state.mandel, state.params_mandel)
    mouse = state.params_mandel.mouse_info
    if mouse.is_mouse_hovering and imgui.is_mouse_clicked(0):
        x, y = mouse.mouse_position
        re = MANDEL_RE[0] + x / state.size * (MANDEL_RE[1] - MANDEL_RE[0])
        im = MANDEL_IM[0] + y / state.size * (MANDEL_IM[1] - MANDEL_IM[0])
        state.c = complex(re, im)
        state.julia = julia_image(state.c, state.size)
        state.params_julia.refresh_image = True
    imgui.same_line()
    immvision.image("Julia", state.julia, state.params_julia)
    imgui.text(f"c = {state.c.real:.3f} {state.c.imag:+.3f} i")
    imgui_md.render(f'@import "{THIS_FILE}" {{md_id=Story}}')


immvision.use_rgb_color_order()
immapp.run(gui, window_title="Julia map", window_size=(900, 1000), with_markdown=True, with_latex=True)
