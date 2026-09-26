"""The Mandelbrot set as a map of Julia sets

This file is its own narrative (narrative programming, see imgui_rich_md): its ::md sections are markdown, next to
the code they explain. It also shows a specific use of it: the markdown places the widgets.

The "::md Story" section below draws the **whole** GUI:
- Its markdown will be rendered by a call to `rich_md.render_this_file("Story")`
- It includes widgets via fenced blocks of the language "widget", such as...
    ```widget
    maps
    ```
  ...which the program draws with maps_widget() (see WIDGETS, and register_fenced_block_renderer() in gui()).

Edit the story while the program runs: on the desktop, it will automatically display the updated story upon saving!
"""


r"""::md Story
# The Mandelbrot set is a map of Julia sets
Both pictures iterate the same rule, $z \leftarrow z^2 + c$, and color each pixel by how fast $z$ escapes.
On the left, $c$ is the pixel and $z$ starts at $0$. On the right, $c$ is fixed and $z$ starts at the pixel.
**Click anywhere on the left picture to choose $c$**: the Julia set on the right is the one for that $c$.
Or pick a famous value in the list on the right: the map flies there, and the Julia set changes on the way. Hover
a name to read its story.

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


# ruff: noqa: E402  # Allow imports to come after the story
from dataclasses import dataclass
from typing import Callable
import numpy as np
from imgui_bundle import imgui, immapp, immvision, rich_md, em_size, hello_imgui, IM_COL32


# Below is an example of a documented function via narrative programming:
# - First we define "::md Escape", a markdown string that can be included somewhere else
# - Then we define an associated code part with "::code"
# - We end both with "::endcode" (which automatically closes its parent markdown section)
# Then, our story can include both with
#     ![[#Escape]]
#     ![[#Escape#code]]
r"""::md Escape
### Escape time
Iterate $z \leftarrow z^2 + c$ and count the steps until $|z| > 16$ (beyond 2, $z$ already flies to infinity).
A point that survives all `max_iter` iterations is considered in the set, and drawn in black. Elsewhere, the count
minus $\log_2 \log_2 |z|$ gives the color: this fraction of a step smooths the bands between two counts, and the
bound of 16 makes it accurate.
::code
"""
def escape_time(z: np.ndarray, c: np.ndarray, max_iter: int) -> np.ndarray:
    count = np.full(z.shape, max_iter, dtype=np.float32)
    for i in range(max_iter):
        z = z * z + c
        size = np.abs(z)
        escaped = (size > 16.0) & (count == max_iter)
        count[escaped] = i + 1 - np.log2(np.log2(size[escaped]))
        z[size > 16.0] = 16.0  # keep the escaped values small
    return np.clip(count, 0, max_iter) / max_iter
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
JOURNEY_SECONDS = 2.5  # the way to a famous value of c
GLIDE_SECONDS = 1.0  # the way to a clicked value of c


# The colors of the pictures: the "Ultra Fractal" palette (navy, blue, white, orange, black), repeated 4 times from
# "escapes at once" (0) to "never escapes" (1), and black inside the set
PALETTE_STOPS = [(0.0, 0, 7, 100), (0.16, 32, 107, 203), (0.42, 237, 255, 255), (0.6425, 255, 170, 0),
                 (0.8575, 0, 2, 0), (1.0, 0, 7, 100)]  # position, red, green, blue
PALETTE = np.stack([np.interp(np.linspace(0, 1, 256), np.array(PALETTE_STOPS)[:, 0], np.array(PALETTE_STOPS)[:, k])
                    for k in (1, 2, 3)], axis=1).astype(np.uint8)  # 256 RGB colors
PALETTE_CYCLES = 4


def colorize(values: np.ndarray) -> np.ndarray:
    """Normalized counts -> an RGB image: the palette outside the set, black inside"""
    rgb = PALETTE[(values * PALETTE_CYCLES % 1.0 * 255).astype(np.uint8)]
    rgb[values >= 1.0] = 0
    return rgb


class PlaneView:
    """A picture of a window of the complex plane, computed by compute(window_re, window_im, size). The mouse wheel
    zooms around the mouse, a drag pans: the picture is computed again for the part it shows."""

    def __init__(self, label: str, window_re: Window, window_im: Window,
                 compute: Callable[[Window, Window, int], np.ndarray]) -> None:
        self.label, self.compute, self.full_window = label, compute, (window_re, window_im)
        self.window_re, self.window_im = window_re, window_im
        self.drag_start = self.window_re, self.window_im  # the window when a drag started
        self.coarse = False  # computed at half the resolution, then enlarged: 3 times faster (while moving)
        self.sharp_at: float | None = None  # when to compute it at full resolution again, after a zoom or a pan
        self.refresh()

    def set_view(self, center: complex, width: float) -> None:
        """Shows the square of the plane of this width around center"""
        self.window_re = (center.real - width / 2, center.real + width / 2)
        self.window_im = (center.imag - width / 2, center.imag + width / 2)
        self.refresh()

    def refresh(self) -> None:
        if self.coarse:
            values = self.compute(self.window_re, self.window_im, SIZE // 2).repeat(2, axis=0).repeat(2, axis=1)
        else:
            values = self.compute(self.window_re, self.window_im, SIZE)
        self.image = colorize(values)
        self.changed = True  # the texture is updated by the next show()

    def to_plane(self, x: float, y: float) -> complex:
        (re0, re1), (im0, im1) = self.window_re, self.window_im
        return complex(re0 + x / SIZE * (re1 - re0), im0 + y / SIZE * (im1 - im0))

    def to_pixel(self, z: complex) -> tuple[int, int]:
        (re0, re1), (im0, im1) = self.window_re, self.window_im
        return int((z.real - re0) / (re1 - re0) * SIZE), int((z.imag - im0) / (im1 - im0) * SIZE)

    def move(self, window_re: Window, window_im: Window) -> None:
        """After a zoom or a pan: computed fast while the mouse moves, then sharp"""
        if window_re[1] - window_re[0] < 1e-12:  # deeper, float64 could not tell the pixels apart
            return
        self.window_re, self.window_im = window_re, window_im
        self.coarse, self.sharp_at = True, imgui.get_time() + 0.2
        self.refresh()

    def handle_mouse(self, x: float, y: float) -> complex | None:
        """On the last item: the wheel zooms around the mouse (at x, y), a drag pans. Returns the point of a click"""
        imgui.set_item_key_owner(imgui.Key.mouse_wheel_y)  # the wheel zooms the picture, and does not scroll
        (re0, re1), (im0, im1) = self.window_re, self.window_im
        wheel = imgui.get_io().mouse_wheel
        if imgui.is_item_hovered() and wheel != 0:
            z, f = self.to_plane(x, y), 0.8 ** wheel
            self.move((z.real + (re0 - z.real) * f, z.real + (re1 - z.real) * f),
                      (z.imag + (im0 - z.imag) * f, z.imag + (im1 - z.imag) * f))
        if imgui.is_item_activated():
            self.drag_start = self.window_re, self.window_im
        drag = imgui.get_mouse_drag_delta(0)  # stays (0, 0) until the mouse moves past the drag threshold
        if imgui.is_item_active() and (drag.x, drag.y) != (0, 0):
            (re0, re1), (im0, im1) = self.drag_start
            d_re, d_im = -drag.x / SIZE * (re1 - re0), -drag.y / SIZE * (im1 - im0)
            window = (re0 + d_re, re1 + d_re), (im0 + d_im, im1 + d_im)
            if window != (self.window_re, self.window_im):
                self.move(*window)
        if imgui.is_item_deactivated() and (drag.x, drag.y) == (0, 0):
            return self.to_plane(x, y)
        return None

    def draw_cross(self, top_left: imgui.ImVec2, z: complex) -> None:
        """A cross at z, when in view"""
        x, y = self.to_pixel(z)
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            return
        cx, cy, r = top_left.x + x, top_left.y + y, em_size(0.4)
        draw_list = imgui.get_window_draw_list()
        for color, thickness in ((IM_COL32(0, 0, 0, 255), 3.0), (IM_COL32(255, 255, 255, 255), 1.5)):
            draw_list.add_line(imgui.ImVec2(cx - r, cy - r), imgui.ImVec2(cx + r, cy + r), color, thickness)
            draw_list.add_line(imgui.ImVec2(cx - r, cy + r), imgui.ImVec2(cx + r, cy - r), color, thickness)

    def show(self, marker: complex | None = None) -> complex | None:
        """The picture, with a cross at marker. Returns the point of a click on it"""
        imgui.align_text_to_frame_padding()  # the titles of the three columns, on one line
        imgui.text(self.label)
        top_left = imgui.get_cursor_screen_pos()
        imgui.invisible_button(f"##{self.label} mouse", imgui.ImVec2(SIZE, SIZE))  # takes the mouse, under the picture
        mouse = imgui.get_mouse_pos()
        clicked = self.handle_mouse(mouse.x - top_left.x, mouse.y - top_left.y)
        if self.sharp_at is not None and imgui.get_time() > self.sharp_at:
            self.coarse, self.sharp_at = False, None
            self.refresh()
        imgui.set_cursor_screen_pos(top_left)
        immvision.image_display(f"##{self.label}", self.image, (SIZE, SIZE), refresh_image=self.changed)
        self.changed = False
        if marker is not None:
            self.draw_cross(top_left, marker)
        if imgui.button(f"Full view##{self.label}"):
            self.window_re, self.window_im = self.full_window
            self.refresh()
        return clicked


def ease(x: float) -> float:
    """0 -> 0, 1 -> 1, slow at both ends"""
    return x * x * (3 - 2 * x)


@dataclass
class Journey:
    """The way to a famous value of c: c moves there in a straight line, and the map flies there (it zooms out until
    both places are in view, then zooms in)"""
    start_c: complex
    target_c: complex
    start_center: complex
    start_width: float
    target_center: complex
    target_width: float
    start_time: float


class State:
    def __init__(self) -> None:
        self.max_iter = 80
        self.c = complex(-0.8, 0.156)
        self.julia_follows_map = False
        self.journey: Journey | None = None
        self.glide: tuple[complex, complex, float] | None = None  # after a click: c from, c to, start time
        self.animation_speed = 1.0  # divides JOURNEY_SECONDS and GLIDE_SECONDS
        self.map = PlaneView("Mandelbrot", MANDEL_RE, MANDEL_IM,
                             lambda re, im, size: mandelbrot_image(size, self.max_iter, re, im))
        self.julia = PlaneView("Julia", JULIA_RE, JULIA_IM,
                               lambda re, im, size: julia_image(self.c, size, self.max_iter, re, im))

    def choose_c(self, c: complex) -> None:
        self.c = c
        if not self.julia_follows_map:
            self.julia.refresh()  # else follow_map() will

    def go_to(self, c: complex, width: float | None) -> None:
        """A journey to c, where the map arrives with a view of this width (None: the whole set)"""
        self.glide = None
        (re0, re1), (im0, im1) = self.map.window_re, self.map.window_im
        target_center = c if width is not None else complex(sum(MANDEL_RE) / 2, sum(MANDEL_IM) / 2)
        target_width = width if width is not None else MANDEL_RE[1] - MANDEL_RE[0]
        self.journey = Journey(self.c, c, complex((re0 + re1) / 2, (im0 + im1) / 2), re1 - re0,
                               target_center, target_width, imgui.get_time())

    def glide_to(self, c: complex) -> None:
        """After a click: c glides there, and the map stays"""
        self.journey = None
        self.glide = (self.c, c, imgui.get_time())

    def travel(self) -> None:
        """Each frame: the next step of the journey, or of the glide"""
        j = self.journey
        if j is not None:
            t = min((imgui.get_time() - j.start_time) * self.animation_speed / JOURNEY_SECONDS, 1.0)
            self.map.coarse = self.julia.coarse = t < 1.0  # fast on the way, sharp on arrival
            # The map zooms out until both places are in view, then in (the time is shared in proportion to the two
            # zoom factors). It pans, and c moves, around the widest moment: the view is never lost
            top = max(j.start_width, j.target_width, 2 * abs(j.target_center - j.start_center))
            rise, fall = np.log(top / j.start_width), np.log(top / j.target_width)
            split = rise / (rise + fall) if rise + fall > 0 else 0.5
            if t < split or split >= 1.0:
                u, width_from, width_to = min(t / split, 1.0), j.start_width, top
            else:
                u, width_from, width_to = (t - split) / (1 - split), top, j.target_width
            p = ease(min(max(2 * t - split, 0.0), 1.0))
            self.choose_c(j.target_c if t == 1.0 else j.start_c + (j.target_c - j.start_c) * p)
            center = j.start_center + (j.target_center - j.start_center) * p
            self.map.set_view(center, width_from * (width_to / width_from) ** ease(u))
            if t == 1.0:
                self.journey = None
        if self.glide is not None:
            start_c, target_c, start_time = self.glide
            t = min((imgui.get_time() - start_time) * self.animation_speed / GLIDE_SECONDS, 1.0)
            self.julia.coarse = t < 1.0
            self.choose_c(target_c if t == 1.0 else start_c + (target_c - start_c) * ease(t))
            if t == 1.0:
                self.glide = None
        moving = self.journey is not None or self.glide is not None
        hello_imgui.get_runner_params().fps_idling.enable_idling = not moving  # a smooth journey

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


# Well-known values of c: their names, and what they are known for (shown in a tooltip)
FAMOUS_C: dict[str, tuple[complex, str]] = {
    "Circle": (0j, "The simplest case: z is squared. The Julia set is the unit circle: inside it, points fall to 0; "
                   "outside, they escape to infinity."),
    "Siegel disk": (-0.3905408702 - 0.5867879073j,
                    "On the edge of the cardioid, at the golden mean angle. Around a fixed point, the map turns the "
                    "plane by an irrational angle: Carl Ludwig Siegel proved in 1942 that such a turning disk exists. "
                    "The Julia set is its wrinkled border."),
    "Douady rabbit": (-0.122561 + 0.744862j,
                      "The center of the period 3 bulb, at the top of the cardioid: the inside of the Julia set turns "
                      "in three steps, ear after ear. Named after Adrien Douady, who explored the Mandelbrot set with "
                      "John Hubbard in the 1980s."),
    "Basilica": (-1 + 0j, "The center of the period 2 bulb: 0 goes to -1, and back. Its bulbs, stacked like domes, "
                          "gave the Julia set its name."),
    "San Marco": (-0.75 + 0j, "Where the cardioid meets the period 2 bulb. Benoit Mandelbrot called its Julia set the "
                              "San Marco dragon: its outline recalls the Basilica of San Marco in Venice, reflected "
                              "in the flooded square."),
    "Cauliflower": (0.25 + 0j, "The cusp of the cardioid. A step further right on the real axis, the Julia set "
                               "bursts into dust: the parabolic implosion, studied by Douady and Pierre Lavaurs."),
    "Airplane": (-1.754877666 + 0j, "The center of the period 3 window of the real axis: the case of Li and Yorke's "
                                    "\"period three implies chaos\" (1975), for the logistic map."),
    "Feigenbaum point": (-1.401155189 + 0j,
                         "Where the period doublings of the real axis (2, 4, 8...) pile up. Mitchell Feigenbaum found "
                         "in 1975 that their spacing shrinks by a universal factor, 4.669..., the same for many maps."),
    "Seahorse valley": (-0.75 + 0.11j, "The crack between the cardioid and the period 2 bulb: zoom into the map, "
                                       "seahorse tails curl everywhere. Just outside the set, the Julia set is dust, "
                                       "in double spirals."),
    "Elephant valley": (0.285 + 0.01j, "Near the cusp of the cardioid: the map shows rows of elephant trunks. Just "
                                       "outside the set, the Julia set is dust, in the same shapes."),
    "Triple spiral valley": (-0.088 + 0.654j, "Between the cardioid and the period 3 bulb: spirals with three arms. "
                                              "Just outside the set, the Julia set is dust, in triple spirals."),
    "Dendrite": (1j, "0 goes to i, then -1+i, -i, -1+i, -i...: it lands on a cycle, so c is a Misiurewicz point. The "
                     "Julia set has no inside: a tree of branches, a dendrite."),
    "Misiurewicz point": (-0.10109636384562 + 0.95628651080914j,
                          "0 lands on a fixed point after three steps (after Michal Misiurewicz, 1981). Tan Lei proved "
                          "in 1990 that near such a point, the map and the Julia set look alike: tick \"zoom with the "
                          "map\" and zoom in here."),
    "Segment": (-2 + 0j, "The tip of the antenna. The Julia set is the interval [-2, 2]: with z = 2 cos t, the map "
                         "z*z - 2 is 2 cos 2t, a Chebyshev polynomial."),
    "Cantor dust": (0.5 + 0j, "Outside the Mandelbrot set: the orbit of 0 escapes. Fatou and Julia proved around 1919 "
                              "that the Julia set is then a dust of points (a Cantor set), and otherwise connected."),
}


# How close the map arrives at each famous value: the width of its view (None: the whole set)
ARRIVAL_WIDTH: dict[str, float | None] = {
    "Circle": None, "Siegel disk": 0.1, "Douady rabbit": 0.3, "Basilica": 1.0, "San Marco": 0.4, "Cauliflower": 0.3,
    "Airplane": 0.03, "Feigenbaum point": 0.1, "Seahorse valley": 0.03, "Elephant valley": 0.01,
    "Triple spiral valley": 0.02, "Dendrite": 0.1, "Misiurewicz point": 0.03, "Segment": 0.6, "Cantor dust": 1.0,
}


def maps_widget() -> None:
    """The two pictures side by side, and the famous values: a click on the map chooses c (a drag pans it)"""
    state.travel()
    if not imgui.begin_table("##maps", 3, imgui.TableFlags_.sizing_fixed_fit):  # three columns, aligned at the top
        return
    imgui.table_next_column()
    column_x = imgui.get_cursor_pos_x()
    clicked = state.map.show(marker=state.c)
    if clicked is not None:
        state.glide_to(clicked)
    pixel = (state.map.window_re[1] - state.map.window_re[0]) / SIZE
    digits = max(3, int(np.ceil(-np.log10(pixel))))  # enough to tell two pixels of the map apart
    imgui.same_line()
    imgui.push_text_wrap_pos(column_x + SIZE)  # deep in the map, c needs many digits: two lines
    imgui.text(f"c = {state.c.real:.{digits}f} {state.c.imag:+.{digits}f} i")
    imgui.pop_text_wrap_pos()

    imgui.table_next_column()
    if state.julia_follows_map:
        state.follow_map()
    state.julia.show()
    imgui.same_line()
    _, state.julia_follows_map = imgui.checkbox("zoom with the map", state.julia_follows_map)

    imgui.table_next_column()
    imgui.align_text_to_frame_padding()
    imgui.text("Famous values of c")
    height = (len(FAMOUS_C) + 0.5) * imgui.get_text_line_height_with_spacing()  # every name, no scrolling
    if imgui.begin_list_box("##famous c", imgui.ImVec2(em_size(11), height)):
        for name, (c, story) in FAMOUS_C.items():
            if imgui.selectable(name, state.c == c)[0]:
                state.go_to(c, ARRIVAL_WIDTH[name])
            if imgui.begin_item_tooltip():
                imgui.push_text_wrap_pos(em_size(24))
                imgui.text_unformatted(f"c = {c.real:g} {c.imag:+g} i\n\n{story}")
                imgui.pop_text_wrap_pos()
                imgui.end_tooltip()
        imgui.end_list_box()
    imgui.set_next_item_width(em_size(11))
    _, state.animation_speed = imgui.slider_float("##animation speed", state.animation_speed, 0.2, 5.0,
                                                  "animation speed x%.1f", imgui.SliderFlags_.logarithmic)
    imgui.end_table()


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


immapp.run(gui, window_title="Julia map", window_size=(900, 1000), with_markdown=True, with_latex=True)
