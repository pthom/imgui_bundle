"""The Mandelbrot set as a map of Julia sets: click on the left picture to choose c, the right one follows.

This file is its own narrative (narrative programming, see imgui_rich_md): its ::md sections are markdown, next to
the code they explain. It also shows a specific use of it: the markdown places the widgets.

The "::md Story" section below draws the **whole** GUI, except the full code at the bottom:
- Its markdown will be rendered by a call to `rich_md.render_this_file("Story")`
- It includes widgets via fenced blocks of the language "widget", such as
    ```widget
    maps
    ```
which the program draws with maps_widget() (see WIDGETS, and register_fenced_block_renderer() in gui()).

Edit the story while the program runs: on the desktop, it will automatically display the updated story upon saving!
"""


from typing import Callable

import numpy as np
from imgui_bundle import imgui, immapp, immvision, rich_md

r"""::md Story
# The Mandelbrot set is a map of Julia sets
Both pictures iterate the same rule, $z \leftarrow z^2 + c$, and color each pixel by how fast $z$ escapes.
On the left, $c$ is the pixel and $z$ starts at $0$. On the right, $c$ is fixed and $z$ starts at the pixel.
**Click anywhere on the left picture to choose $c$**: the Julia set on the right is the one for that $c$.

<!-- A widget: the program draws it with maps_widget() (the two pictures, and the value of c) -->
```widget
maps
```

## Navigate in the sets
Zoom into either picture with the mouse wheel, and drag it to move around: it is computed again for the part you
see, so new details keep appearing, until a zoom of about 10 000 (the limit of single precision). **Full view**
brings back the whole picture.

## Iterations
Set the maximum number of iterations (see `max_iter` in `escape_time` below), and watch the fine details of the
boundary appear:
```widget
budget
```

## Why the boundary matters
A Julia set is connected exactly when its $c$ belongs to the Mandelbrot set.

**Try this**
* Click just inside the big cardioid, then just outside: the set shatters into dust.
* Click along the boundary: each Julia set looks like the region of the map around its $c$, spirals for spirals,
  antennae for antennae (that is the sense in which the Mandelbrot set is a map).
* Tick **zoom with the map**: the Julia set is then shown around the point $c$, at the scale of the map.
  Zoom into the map at the tip of an antenna, or where branches meet, and click there: the two pictures look alike.


## How the pictures are computed

![[#Escape]]
![[#Escape#code]]
![[#Mandelbrot]]
![[#Mandelbrot#code]]
![[#Julia]]
![[#Julia#code]]
"""


# Below is an example of a documented function via narrative programming:
# - First we define "::md Escape", a markdown string that can be included somewhere else
# - Then we define an associated code part with "::code"
# - We end both with "::endcode" (which automatically closes its parent markdown section)
# Then, our story can include both with
#     ![[#Escape]]
#     ![[#Escape#code]]
r"""::md Escape
### Escape time
Iterate $z \leftarrow z^2 + c$ and count the steps until $|z| > 2$, after which $z$ flies to infinity.
A point that survives all `max_iter` iterations is considered in the set. The normalized count is the color.
::code
"""
def escape_time(z: np.ndarray, c: np.ndarray, max_iter: int) -> np.ndarray:
    count = np.full(z.shape, max_iter, dtype=np.float32)
    for i in range(max_iter):
        z = z * z + c
        escaped = np.abs(z) > 2.0
        count[escaped & (count == max_iter)] = i
        z[escaped] = 2.0  # keep the escaped values small
    return count / max_iter
# ::endcode

Window = tuple[float, float]  # a range on an axis of the complex plane
MANDEL_RE, MANDEL_IM = (-2.2, 0.8), (-1.5, 1.5)  # the window of the whole Mandelbrot set
JULIA_RE, JULIA_IM = (-1.7, 1.7), (-1.7, 1.7)  # the window of a whole Julia set

r"""::md Mandelbrot
### The map: $c$ varies, $z_0 = 0$
::code
"""
def mandelbrot_image(size: int, max_iter: int, window_re: Window, window_im: Window) -> np.ndarray:
    re = np.linspace(*window_re, size, dtype=np.float32)
    im = np.linspace(*window_im, size, dtype=np.float32)
    c = (re[None, :] + 1j * im[:, None]).astype(np.complex64)
    return escape_time(np.zeros_like(c), c, max_iter)
# ::endcode

r"""::md Julia
### One Julia set: $c$ fixed, $z_0$ varies
::code
"""
def julia_image(c: complex, size: int, max_iter: int, window_re: Window, window_im: Window) -> np.ndarray:
    re = np.linspace(*window_re, size, dtype=np.float32)
    im = np.linspace(*window_im, size, dtype=np.float32)
    z0 = (re[None, :] + 1j * im[:, None]).astype(np.complex64)
    return escape_time(z0, np.full_like(z0, c), max_iter)
# ::endcode

# The widgets that the story places in its ```widget blocks
SIZE = 300  # the pictures, in pixels


class PlaneView:
    """A picture of a window of the complex plane, computed by compute(window_re, window_im). Zoomed or panned
    with immvision (mouse wheel, drag), it is computed again for the part it shows."""

    def __init__(self, label: str, window_re: Window, window_im: Window,
                 compute: Callable[[Window, Window], np.ndarray]) -> None:
        self.label, self.compute, self.full_window = label, compute, (window_re, window_im)
        self.window_re, self.window_im = window_re, window_im
        self.params = immvision.ImageParams()
        self.params.image_display_size = (SIZE, SIZE)
        self.params.colormap_settings.colormap = "Magma"
        self.params.add_watched_pixel_on_double_click = False
        self.params.show_image_info = False
        self.params.show_zoom_buttons = False  # zoom with the wheel, and "Full view" below
        self.refresh()

    def refresh(self) -> None:
        self.image = self.compute(self.window_re, self.window_im)
        self.params.refresh_image = True

    def to_plane(self, x: float, y: float) -> complex:
        (re0, re1), (im0, im1) = self.window_re, self.window_im
        return complex(re0 + x / SIZE * (re1 - re0), im0 + y / SIZE * (im1 - im0))

    def to_pixel(self, z: complex) -> tuple[int, int]:
        (re0, re1), (im0, im1) = self.window_re, self.window_im
        return int((z.real - re0) / (re1 - re0) * SIZE), int((z.imag - im0) / (im1 - im0) * SIZE)

    def follow_zoom(self) -> None:
        """Once zoomed or panned (mouse released): the window becomes the part of the plane shown"""
        (scale, _, tx), (_, _, ty), _ = self.params.zoom_pan_matrix
        width = self.params.image_display_size[0]
        full_scale = width / SIZE  # the whole image fills the display
        if (scale, tx, ty) == (full_scale, 0.0, 0.0) or imgui.is_mouse_down(0):
            return

        def visible(window: Window, t: float) -> Window:  # display [0, width] -> plane
            lo, hi = window
            return lo + (hi - lo) * -t / scale / SIZE, lo + (hi - lo) * (width - t) / scale / SIZE

        self.window_re, self.window_im = visible(self.window_re, tx), visible(self.window_im, ty)
        self.params.zoom_pan_matrix = [[full_scale, 0.0, 0.0], [0.0, full_scale, 0.0], [0.0, 0.0, 1.0]]
        self.refresh()

    def show(self) -> None:
        immvision.image(self.label, self.image, self.params)
        self.params.refresh_image = False  # immvision leaves it set (for live video)
        self.follow_zoom()
        if imgui.small_button(f"Full view##{self.label}"):
            self.window_re, self.window_im = self.full_window
            self.refresh()


class State:
    def __init__(self) -> None:
        self.max_iter = 80
        self.c = complex(-0.8, 0.156)
        self.julia_follows_map = False
        self.map = PlaneView("Mandelbrot", MANDEL_RE, MANDEL_IM,
                             lambda re, im: mandelbrot_image(SIZE, self.max_iter, re, im))
        self.julia = PlaneView("Julia", JULIA_RE, JULIA_IM,
                               lambda re, im: julia_image(self.c, SIZE, self.max_iter, re, im))

    def choose_c(self, c: complex) -> None:
        self.c = c
        if not self.julia_follows_map:
            self.julia.refresh()  # else follow_map() will

    def follow_map(self) -> None:
        """The Julia set around z = c, at the scale of the map: where the two sets look alike"""
        (re0, re1), (im0, im1) = self.map.window_re, self.map.window_im
        window_re = (self.c.real - (re1 - re0) / 2, self.c.real + (re1 - re0) / 2)
        window_im = (self.c.imag - (im1 - im0) / 2, self.c.imag + (im1 - im0) / 2)
        if (window_re, window_im) != (self.julia.window_re, self.julia.window_im):
            self.julia.window_re, self.julia.window_im = window_re, window_im
            self.julia.refresh()

    def set_budget(self, max_iter: int) -> None:
        self.max_iter = max_iter
        self.map.refresh()
        self.julia.refresh()


state = State()


def maps_widget() -> None:
    """The two pictures side by side: a click on the map chooses c (a drag pans it)"""
    imgui.begin_group()
    state.map.params.watched_pixels = [state.map.to_pixel(state.c)]  # c, shown on the map
    state.map.show()
    mouse = state.map.params.mouse_info
    drag = imgui.get_mouse_drag_delta(0)  # stays (0, 0) until the mouse moves past the drag threshold
    if mouse.is_mouse_hovering and imgui.is_mouse_released(0) and drag.x == 0 and drag.y == 0:
        state.choose_c(state.map.to_plane(*mouse.mouse_position))
    pixel = (state.map.window_re[1] - state.map.window_re[0]) / SIZE
    digits = max(3, int(np.ceil(-np.log10(pixel))))  # enough to tell two pixels of the map apart
    imgui.text(f"c = {state.c.real:.{digits}f} {state.c.imag:+.{digits}f} i")
    imgui.end_group()
    imgui.same_line()
    imgui.begin_group()
    if state.julia_follows_map:
        state.follow_map()
    state.julia.show()
    _, state.julia_follows_map = imgui.checkbox("zoom with the map", state.julia_follows_map)
    imgui.end_group()


def budget_widget() -> None:
    """The iteration budget of both pictures"""
    changed, max_iter = imgui.slider_int("iterations", state.max_iter, 10, 250)
    if changed:
        state.set_budget(max_iter)


WIDGETS = {"maps": maps_widget, "budget": budget_widget}


def widget_block(name: str) -> None:
    widget = WIDGETS.get(name.strip())
    if widget:
        widget()
    else:
        imgui.text_colored(imgui.ImVec4(1.0, 0.4, 0.4, 1.0), f"unknown widget: {name.strip()}")


def gui() -> None:
    rich_md.register_fenced_block_renderer("widget", widget_block)  # the story's ```widget blocks

    # The line below renders the whole GUI of the app!
    rich_md.render_this_file("Story")

    # Additional, for interested readers: the full code, with some comments
    if imgui.collapsing_header("Full code - Commented"):
        # We can of course render markdown directly from a string, such as below:
        rich_md.render(r"""
        ## Narrative programming
        This program is its own narrative: an example of
        [narrative programming](https://github.com/pthom/imgui_rich_md/blob/main/docs/narrative_programming/narrative_programming.md).
        Its prose lives in its source, in named sections (`::md Story`, `::md Escape`, ...), next to the code it
        explains. The story transcludes them in its own order (`![[#Escape]]` for the prose of a section,
        `![[#Escape#code]]` for its code): the file keeps the order of a program, the story the order of an explanation.

        Edit the file while the program runs: the story follows. The code does not: restart the program to run it.

        ## Widgets in the story
        The pictures and the slider are placed by the story, not by the program's layout. A code block of the language
        `widget` in the prose is drawn by a function of the program (`maps_widget`, `budget_widget`), which
        `rich_md.register_fenced_block_renderer` connects to it. The story decides where the reader plays.

        ## The full code
        """)
        # Render the whole file, as code
        rich_md.render_this_file("")


immvision.use_rgb_color_order()
immapp.run(gui, window_title="Julia map", window_size=(900, 1000), with_markdown=True, with_latex=True)
