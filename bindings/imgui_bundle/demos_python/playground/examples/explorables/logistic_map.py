r"""Logistic Map
============

One line — $x_{n+1} = r\,x_n\,(1-x_n)$ — and an entire universe of behaviour.
As **r** climbs, a steady population doubles into a 2-cycle, a 4-cycle, an
8-cycle… then shatters into **chaos**, threaded with sudden windows of order.

Drag **r** or click the diagram to jump there. **Scroll to zoom** the
bifurcation diagram — the same branching returns at every scale.
"""

import numpy as np
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_toggle, icons_fontawesome_4
from imgui_bundle import ImVec2, ImVec4
from typing import Tuple, Optional
import time

# =============================================================================
# The map
# =============================================================================

R_MIN, R_MAX = 0.0, 4.0          # the full parameter range
DEF_VIEW = (2.5, 4.0, 0.0, 1.0)  # default (r0, r1, x0, x1) window
GRID_COLS, GRID_ROWS = 500, 340  # heatmap resolution
TRANSIENT = 300                  # iterations discarded before sampling

# Period-doubling cascade landmarks (r values)
LANDMARKS = [
    (3.0,      "1 → 2"),
    (3.449,    "2 → 4"),
    (3.544,    "4 → 8"),
    (3.56995,  "chaos onset"),
    (3.82843,  "period-3 window"),
]


def compute_bifurcation(r0, r1, x0v, x1v, samples,
                        cols=GRID_COLS, rows=GRID_ROWS, transient=TRANSIENT):
    """Density heatmap of the attractor plus the Lyapunov exponent per column.

    Returns (density[rows, cols] in 0..1, lyapunov[cols], r_axis[cols]).
    """
    r = np.linspace(r0, r1, cols)
    x = np.full(cols, 0.5)
    for _ in range(transient):
        x = r * x * (1.0 - x)

    xs = np.empty((samples, cols))
    lyap = np.zeros(cols)
    for k in range(samples):
        x = r * x * (1.0 - x)
        lyap += np.log(np.abs(r * (1.0 - 2.0 * x)) + 1e-12)
        xs[k] = x
    lyap /= samples

    # Accumulate visited (x, r) cells into a 2-D histogram in one pass.
    inv = rows / (x1v - x0v)
    row = ((x1v - xs) * inv).astype(np.int64)      # row 0 = top = x1v
    col = np.broadcast_to(np.arange(cols), (samples, cols))
    m = (row >= 0) & (row < rows)
    flat = (row * cols + col)[m]
    hist = np.bincount(flat, minlength=rows * cols).reshape(rows, cols).astype(float)

    dens = np.log1p(hist)            # log so faint chaotic bands stay visible
    mx = dens.max()
    if mx > 0:
        dens /= mx
    return dens, lyap, r


def analyze(r, transient=1000, n=400, tol=1e-4) -> Tuple[int, float]:
    """Return (period, lyapunov) for a single r. period 0 means chaotic."""
    x = 0.5
    for _ in range(transient):
        x = r * x * (1 - x)
    seq = np.empty(n)
    lam = 0.0
    for k in range(n):
        x = r * x * (1 - x)
        lam += np.log(abs(r * (1 - 2 * x)) + 1e-12)
        seq[k] = x
    lam /= n
    for p in range(1, 17):
        if np.all(np.abs(seq[p:] - seq[:-p]) < tol):
            return p, lam
    return 0, lam


def cobweb_points(r, x0, steps):
    """The staircase path of the iteration, for the cobweb plot."""
    px, py = [x0], [0.0]
    x = x0
    for _ in range(steps):
        fx = r * x * (1 - x)
        px += [x, fx]
        py += [fx, fx]
        x = fx
    return np.array(px), np.array(py)


# =============================================================================
# Application state
# =============================================================================

COLORMAPS = [
    ("Plasma", implot.Colormap_.plasma),
    ("Viridis", implot.Colormap_.viridis),
    ("Hot", implot.Colormap_.hot),
    ("Twilight", implot.Colormap_.twilight),
    ("Greys", implot.Colormap_.greys),
]


class AppState:
    def __init__(self):
        self.r = 3.7
        self.x0 = 0.2

        self.detail = 450            # samples per column (heatmap detail slider)
        self.cmap_idx = 0
        self.show_landmarks = True
        self.show_about = False
        self.show_tips = False

        # Cobweb animation
        self.paused = False
        self.cobweb_step = 0.0
        self.cobweb_max = 220
        self.cobweb_rate = 110.0     # steps drawn per second

        # Bifurcation view + debounced recompute
        self.computed_view = DEF_VIEW
        self.target_view = DEF_VIEW
        self.view_change_t = -1.0
        self.dirty = False
        self.force_view: Optional[Tuple[float, float, float, float]] = None

        # Cached single-r analysis
        self.period = 0
        self.lam = 0.0
        self._last_r = None

        self.last_time = time.time()
        self.grid, self.lyap, self.r_axis = compute_bifurcation(*DEF_VIEW, self.detail)

    # -- single r readout --------------------------------------------------
    def refresh_analysis(self):
        if self._last_r != self.r:
            self.period, self.lam = analyze(self.r)
            self._last_r = self.r

    def set_r(self, r):
        r = float(np.clip(r, R_MIN, R_MAX))
        if r != self.r:
            self.r = r
            self.cobweb_step = 0.0

    def set_x0(self, x0):
        self.x0 = float(np.clip(x0, 0.0, 1.0))
        self.cobweb_step = 0.0

    # -- debounced heatmap recompute --------------------------------------
    def note_view(self, view):
        if self._view_diff(view, self.target_view) > 1e-9:
            self.target_view = view
            self.view_change_t = time.time()
            self.dirty = True

    def mark_detail_changed(self):
        self.dirty = True
        self.view_change_t = -1.0    # recompute immediately on next tick

    @staticmethod
    def _view_diff(a, b):
        return sum(abs(x - y) for x, y in zip(a, b, strict=True))

    def maybe_recompute(self):
        if self.dirty and time.time() - self.view_change_t > 0.10:
            self.grid, self.lyap, self.r_axis = compute_bifurcation(
                *self.target_view, self.detail)
            self.computed_view = self.target_view
            self.dirty = False

    # -- cobweb animation --------------------------------------------------
    def tick(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now
        if not self.paused:
            self.cobweb_step += dt * self.cobweb_rate
            if self.cobweb_step > self.cobweb_max:
                self.cobweb_step = 0.0


# =============================================================================
# GUI
# =============================================================================

FA_PLAY = icons_fontawesome_4.ICON_FA_PLAY
FA_PAUSE = icons_fontawesome_4.ICON_FA_PAUSE
FA_UNDO = icons_fontawesome_4.ICON_FA_UNDO
FA_INFO = icons_fontawesome_4.ICON_FA_INFO_CIRCLE

ACCENT = ImVec4(1.0, 0.85, 0.25, 1.0)
MARKER = ImVec4(1.0, 1.0, 1.0, 0.85)
FAINT = ImVec4(0.7, 0.75, 0.9, 0.30)


ABOUT_MD = r"""# The Logistic Map

A deceptively simple recurrence:

$x_{n+1} = r\,x_n\,(1 - x_n)$

Each $x_n$ is a number between 0 and 1, and $r$ is a growth parameter
between 0 and 4. Feed a value back into the formula over and over — the
long-term fate of the sequence depends entirely on $r$.

## What it models

Read $x_n$ as a **population**, measured as a fraction of the most the
environment can sustain. The formula balances two opposing forces:

- $r\,x_n$ — **growth**: more individuals now means more next season.
- $(1 - x_n)$ — **crowding**: as the habitat fills, competition for food
  and space throttles further growth.

It is the discrete-time cousin of Verhulst's **logistic equation**,
$\frac{dN}{dt} = r\,N\,(1 - N/K)$, written down by the Belgian
mathematician Pierre-François Verhulst in **1838** to temper Malthus's
notion of unbounded exponential growth.

## Where the chaos came from

For over a century this was a quiet ecological model. Then in **1976** the
physicist-ecologist **Robert May**, in a celebrated *Nature* paper, showed
that the one-line equation hides staggering complexity: as $r$ rises it
**period-doubles** — 1, then 2, 4, 8 cycles — and then tips into **chaos**.

Soon after, **Mitchell Feigenbaum** found that the doublings shrink by a
fixed ratio, the universal constant $\delta \approx 4.6692$, which appears
in *any* system taking this route to chaos — from dripping taps to driven
circuits. A toy population model turned out to obey a universal law.

## Reading the diagram

- $r < 1$ — the population dies out.
- $1 < r < 3$ — it settles to a single steady value.
- $r = 3$ — the first split: a stable 2-cycle.
- $r \approx 3.5699$ — the doublings accumulate: the **onset of chaos**.
- beyond — chaos, shot through with sudden **windows of order**, most
  vividly the period-3 window near $r \approx 3.8284$. *(A 1975 theorem of
  Li and Yorke proved that period three implies chaos.)*

The **Lyapunov exponent** $\lambda$ beneath the diagram measures this:
$\lambda < 0$ where orbits settle, $\lambda > 0$ where nearby trajectories
separate exponentially — the fingerprint of chaos.

## Why it endures

The logistic map is the textbook first example of **deterministic chaos**:
a perfectly definite rule whose output is, in practice, unpredictable,
because the slightest change in the starting point can eventually lead
anywhere. It reshaped how scientists think about ecosystems, weather, and
the limits of prediction itself.

## Further reading

- Robert May (1976), [*Simple mathematical models with very complicated dynamics*](https://doi.org/10.1038/261459a0) — the *Nature* review that revealed the chaos hiding in this one-line equation.
- Li & Yorke (1975), [*Period Three Implies Chaos*](https://doi.org/10.2307/2318254) — the paper that gave the field its name.
- [Feigenbaum constants](https://en.wikipedia.org/wiki/Feigenbaum_constants) — the universality that ties this cascade to dripping taps, circuits, and beyond.
- [The logistic map](https://en.wikipedia.org/wiki/Logistic_map) — a fuller tour of the map and its bifurcations.
- Veritasium (2020), [This equation will change how you see the world (the logistic map)](https://www.youtube.com/watch?v=ovJcsL7vyrk) (YouTube Video)
"""


TIPS_MD = r"""Click a button to jump there, then watch the **cobweb** redraw
and the **Lyapunov** strip respond. The zoom presets recompute fresh detail —
use **Reset view** to pull back out."""


def draw_cobweb(state: AppState, size: ImVec2):
    r, x0 = state.r, state.x0
    if implot.begin_plot("##cobweb", size, implot.Flags_.no_legend):
        implot.setup_axes("x", "f(x)")
        implot.setup_axes_limits(0, 1, 0, 1, imgui.Cond_.always)

        xs = np.linspace(0, 1, 256)
        para = r * xs * (1 - xs)
        implot.plot_line("f(x) = r x (1-x)", xs, para, spec=implot.Spec(line_color=ImVec4(0.45, 0.7, 1.0, 1.0)))
        implot.plot_line("y = x", np.array([0.0, 1.0]), np.array([0.0, 1.0]), spec=implot.Spec(line_color=ImVec4(0.5, 0.5, 0.55, 0.8)))

        steps = int(state.cobweb_step)
        if steps >= 1:
            cx, cy = cobweb_points(r, x0, steps)
            implot.plot_line("orbit", cx, cy, spec=implot.Spec(line_weight=2.0, line_color=ACCENT))
            implot.plot_scatter("##now", np.array([cx[-1]]), np.array([cy[-1]]), spec=implot.Spec(line_color=ImVec4(1, 1, 1, 1)))
        implot.end_plot()


def draw_bifurcation(state: AppState, size: ImVec2):
    if implot.begin_plot("##bif", size, implot.Flags_.no_legend | implot.Flags_.no_mouse_text):
        implot.setup_axes("r", "x", implot.AxisFlags_.none, implot.AxisFlags_.none)
        fv = state.force_view
        if fv is not None:
            state.force_view = None
            implot.setup_axes_limits(fv[0], fv[1], fv[2], fv[3], cond=imgui.Cond_.always)
        else:
            implot.setup_axes_limits(*DEF_VIEW[:2], *DEF_VIEW[2:], cond=imgui.Cond_.once)

        # Track the view so detail re-renders once it settles
        if fv is not None:
            state.note_view(fv)
        else:
            lim = implot.get_plot_limits()
            state.note_view((lim.x.min, lim.x.max, lim.y.min, lim.y.max))

        # Heatmap drawn at the resolution it was computed for (anchored in data)
        cr0, cr1, cx0, cx1 = state.computed_view
        implot.push_colormap(COLORMAPS[state.cmap_idx][1])
        implot.plot_heatmap("##density", state.grid, 0.0, 1.0, "",
                            implot.Point(cr0, cx0), implot.Point(cr1, cx1))
        implot.pop_colormap()

        # Cascade landmarks
        if state.show_landmarks:
            implot.plot_inf_lines("##marks", np.array([m[0] for m in LANDMARKS]), spec=implot.Spec(line_color=FAINT))

        # Current-r marker
        implot.plot_inf_lines("##r", np.array([state.r]), spec=implot.Spec(line_color=MARKER, line_weight=2.0))

        # Click (not drag) to set r
        if implot.is_plot_hovered() and imgui.is_mouse_released(imgui.MouseButton_.left):
            d = imgui.get_mouse_drag_delta(imgui.MouseButton_.left)
            if abs(d.x) + abs(d.y) < 4:
                state.set_r(implot.get_plot_mouse_pos().x)

        implot.end_plot()


def draw_lyapunov(state: AppState, size: ImVec2):
    cr0, cr1 = state.computed_view[0], state.computed_view[1]
    if implot.begin_plot("##lyap", size, implot.Flags_.no_legend | implot.Flags_.no_mouse_text):
        implot.setup_axes("r", "Lyapunov  λ")
        implot.setup_axes_limits(cr0, cr1, -6.0, 1.2, imgui.Cond_.always)

        # zero baseline
        implot.plot_line("##zero", np.array([cr0, cr1]), np.array([0.0, 0.0]), spec=implot.Spec(line_color=ImVec4(0.5, 0.5, 0.55, 0.7)))

        # shade the chaotic (λ > 0) bands
        implot.plot_shaded("##chaos", state.r_axis, np.clip(state.lyap, 0.0, None), 0.0, spec=implot.Spec(fill_color=ImVec4(0.95, 0.35, 0.25, 0.5)))

        implot.plot_line("lambda", state.r_axis, np.clip(state.lyap, -6.0, 1.2), spec=implot.Spec(line_color=ImVec4(0.55, 0.8, 1.0, 1.0)))
        implot.end_plot()


def gui(state: AppState):
    state.maybe_recompute()
    state.tick()
    state.refresh_analysis()

    em = hello_imgui.em_size()
    btn = ImVec2(em * 2.5, em * 2.0)
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, em * 0.5)

    # ---- Controls + cobweb (left column) ---------------------------------
    imgui.begin_child("controls", ImVec2(em * 24, 0))

    imgui_md.render(__doc__)
    imgui.separator()

    if imgui.button(FA_PAUSE if not state.paused else FA_PLAY, btn):
        state.paused = not state.paused
    imgui.same_line()
    if imgui.button(FA_UNDO, btn):
        state.cobweb_step = 0.0
    imgui.same_line()
    if imgui.button(FA_INFO, btn):
        state.show_about = not state.show_about
    if imgui.is_item_hovered():
        imgui.set_tooltip("Background & history")

    if imgui.button("Things to try", ImVec2(-1, 0)):
        state.show_tips = not state.show_tips

    imgui.separator_text("Parameter")
    imgui.set_next_item_width(em * 22)
    ch_r, r = imgui.slider_float("r", state.r, R_MIN, R_MAX, "%.5f")
    if ch_r:
        state.set_r(r)
    imgui.set_next_item_width(em * 22)
    ch_x, x0 = imgui.slider_float("x0", state.x0, 0.0, 1.0, "%.3f")
    if ch_x:
        state.set_x0(x0)

    regime = f"period {state.period}" if state.period else "chaos"
    imgui.text(f"r = {state.r:.5f}")
    color = ImVec4(0.95, 0.45, 0.3, 1) if state.period == 0 else ImVec4(0.5, 0.85, 1, 1)
    imgui.text_colored(color, f"  {regime}   (λ = {state.lam:+.3f})")

    imgui.separator_text("Cobweb")
    draw_cobweb(state, ImVec2(-1, em * 15))

    imgui.separator_text("Bifurcation")
    imgui.set_next_item_width(em * 10)
    ch_d, state.detail = imgui.slider_int("Detail", state.detail, 150, 1200)
    if ch_d:
        state.mark_detail_changed()
    imgui.set_next_item_width(em * 10)
    _, state.cmap_idx = imgui.combo("Colors", state.cmap_idx, [c[0] for c in COLORMAPS])
    _, state.show_landmarks = imgui_toggle.toggle("Cascade landmarks", state.show_landmarks)
    imgui.same_line()
    if imgui.button("Reset view"):
        state.force_view = DEF_VIEW
    imgui.text_disabled("scroll = zoom · drag = pan · click = pick r")

    imgui.pop_style_var()
    imgui.end_child()

    imgui.same_line()

    # ---- Bifurcation + Lyapunov (right column) ---------------------------
    imgui.begin_child("viz", ImVec2(0, 0))
    avail = imgui.get_content_region_avail()
    draw_bifurcation(state, ImVec2(-1, avail.y * 0.68))
    draw_lyapunov(state, ImVec2(-1, 0))
    imgui.end_child()

    # ---- Hideable background panel ---------------------------------------
    if state.show_about:
        imgui.set_next_window_size(ImVec2(em * 34, em * 40), imgui.Cond_.appearing)
        expanded, opened = imgui.begin("About — the Logistic Map", True)
        state.show_about = bool(opened)
        if expanded:
            imgui_md.render(ABOUT_MD)
        imgui.end()

    # ---- Hideable "things to try" panel ----------------------------------
    if state.show_tips:
        imgui.set_next_window_size(ImVec2(em * 25, em * 30), imgui.Cond_.appearing)
        expanded, opened = imgui.begin("Things to try", True)
        state.show_tips = bool(opened)
        if expanded:
            imgui_md.render(TIPS_MD)

            imgui.separator_text("Pick a value of r")
            if imgui.button("Stable fixed point  ·  r = 2.8", ImVec2(-1, 0)):
                state.set_r(2.8)
            if imgui.button("Period 2  ·  r = 3.20", ImVec2(-1, 0)):
                state.set_r(3.20)
            if imgui.button("Period 4  ·  r = 3.50", ImVec2(-1, 0)):
                state.set_r(3.50)
            if imgui.button("Edge of chaos  ·  r = 3.5699", ImVec2(-1, 0)):
                state.set_r(3.56995)
            if imgui.button("Period-3 window  ·  r = 3.83", ImVec2(-1, 0)):
                state.set_r(3.83)
            if imgui.button("Deep chaos  ·  r = 3.99", ImVec2(-1, 0)):
                state.set_r(3.99)

            imgui.separator_text("Zoom the diagram")
            if imgui.button("The period-doubling cascade", ImVec2(-1, 0)):
                state.force_view = (3.40, 3.60, 0.0, 1.0)
            if imgui.button("Into the period-3 window", ImVec2(-1, 0)):
                state.force_view = (3.82, 3.86, 0.0, 1.0)
            if imgui.button("A diagram inside the diagram", ImVec2(-1, 0)):
                state.set_r(3.852)
                state.force_view = (3.847, 3.857, 0.43, 0.56)

            imgui.separator()
            if imgui.button("Reset view", ImVec2(-1, 0)):
                state.force_view = DEF_VIEW
        imgui.end()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_title="Logistic Map",
        window_size=(1320, 840),
        with_implot=True,
        with_markdown=True,
        with_latex=True,
        fps_idle=0,
        ini_disable=True,
    )


if __name__ == "__main__":
    main()
