"""Fourier Epicycles
==================

Any closed curve can be approximated by a sum of rotating circles (Fourier series).
Adjust the number of circles to see how the approximation improves.
"""

import numpy as np
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_knobs, imgui_toggle, icons_fontawesome_4
from imgui_bundle import ImVec2, ImVec4
from typing import Callable, List, Tuple
import time


# =============================================================================
# Shape definitions
# =============================================================================

def sample_parametric(fn: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]], n: int = 500) -> np.ndarray:
    """Sample a parametric function f(t) -> (x, y) for t in [0, 2*pi), return complex array."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = fn(t)
    return x + 1j * y


def points_to_complex(pts: List[Tuple[float, float]], n: int = 500) -> np.ndarray:
    """Resample a polygon (list of (x,y) points) to n evenly spaced complex samples."""
    pts = pts + [pts[0]]  # close the loop
    segs = np.array(pts)
    diffs = np.diff(segs, axis=0)
    lengths = np.sqrt(diffs[:, 0]**2 + diffs[:, 1]**2)
    cum = np.concatenate([[0], np.cumsum(lengths)])
    total = cum[-1]
    targets = np.linspace(0, total, n, endpoint=False)
    x = np.interp(targets, cum, segs[:, 0])
    y = np.interp(targets, cum, segs[:, 1])
    return x + 1j * y  # type: ignore


def parse_svg_path(d: str) -> List[Tuple[float, float]]:
    """Minimal SVG path parser. Supports M, L, C, Z (absolute only)."""
    import re
    tokens = re.findall(r'[MLCZmlcz]|[-+]?\d*\.?\d+', d)
    points: List[Tuple[float, float]] = []
    i = 0
    cx, cy = 0.0, 0.0
    while i < len(tokens):
        cmd = tokens[i] if tokens[i].isalpha() else None
        if cmd:
            i += 1
        if cmd == 'M' or cmd is None:
            cx, cy = float(tokens[i]), float(tokens[i + 1])
            points.append((cx, cy))
            i += 2
        elif cmd == 'L':
            while i < len(tokens) and not tokens[i].isalpha():
                cx, cy = float(tokens[i]), float(tokens[i + 1])
                points.append((cx, cy))
                i += 2
        elif cmd == 'C':
            while i < len(tokens) and not tokens[i].isalpha():
                x1, y1 = float(tokens[i]), float(tokens[i + 1])
                x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
                x3, y3 = float(tokens[i + 4]), float(tokens[i + 5])
                for s in np.linspace(0, 1, 12, endpoint=False)[1:]:
                    a = (1 - s)
                    bx = a**3 * cx + 3 * a**2 * s * x1 + 3 * a * s**2 * x2 + s**3 * x3
                    by = a**3 * cy + 3 * a**2 * s * y1 + 3 * a * s**2 * y2 + s**3 * y3
                    points.append((bx, by))
                cx, cy = x3, y3
                points.append((cx, cy))
                i += 6
        elif cmd == 'Z' or cmd == 'z':
            pass
        else:
            i += 1
    return points


def shape_from_svg(d: str, n: int = 500) -> np.ndarray:
    pts = parse_svg_path(d)
    # Flip Y: SVG has Y-down, our rendering has Y-up
    pts = [(x, -y) for x, y in pts]
    return points_to_complex(pts, n)


# --- Parametric shapes ---

def heart(t):
    x = 16 * np.sin(t)**3
    y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    return x, y

def star(t, n_points=5, inner_ratio=0.4):
    r = np.where(np.floor(t / (np.pi / n_points)) % 2 == 0, 1.0, inner_ratio)
    return r * np.cos(t), r * np.sin(t)

def trefoil(t):
    return np.sin(t) + 2 * np.sin(2*t), np.cos(t) - 2 * np.cos(2*t)

def butterfly(t):
    r = np.exp(np.sin(t)) - 2 * np.cos(4*t) + np.sin((2*t - np.pi) / 24)**5
    return r * np.sin(t), r * np.cos(t)

def hypotrochoid(t):
    # Need full period: t in [0, 2*pi*r/gcd(R,r)] = [0, 6*pi] for R=10, r=3
    # Remap t from [0, 2*pi) to [0, 6*pi)
    R, r, d = 10, 3, 5
    t = t * 3  # 3 full inner rotations to close the curve
    x = (R - r) * np.cos(t) + d * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - d * np.sin((R - r) / r * t)
    return x, y


# --- SVG shapes ---

# Cat: sitting cat silhouette with pointy ears and curved tail
SVG_CAT = (
    "M 0 0 L -2 -3 L -4 -8 L -3 -10 L -1 -9 L 0 -10 L 1 -9 L 3 -10 L 4 -8 L 2 -3 "
    "C 4 -2 5 0 5 3 C 5 6 4 8 2 9 L 3 10 C 5 11 7 10 8 8 C 9 6 9 5 8 4 "
    "L 7 5 C 7 6 6 7 5 7 L 3 10 L 2 9 C 1 10 -1 10 -2 9 "
    "C -4 8 -5 6 -5 3 C -5 0 -4 -2 -2 -3 Z"
)

SVG_FISH = (
    "M 10 0 C 7 4 3 6 -2 6 C -5 6 -8 4 -10 2 L -14 5 L -13 0 L -14 -5 "
    "L -10 -2 C -8 -4 -5 -6 -2 -6 C 3 -6 7 -4 10 0"
)

# Eighth note (Material Design)
SVG_MUSIC_NOTE = "M 12 3 L 12 13.55 C 11.41 13.21 10.73 13 10 13 C 7.79 13 6 14.79 6 17 C 6 19.21 7.79 21 10 21 C 12.21 21 14 19.21 14 17 L 14 7 L 18 7 L 18 3 Z"

SVG_LIGHTNING = "M 2 -12 L -4 1 L 0 1 L -2 12 L 6 -1 L 2 -1 Z"


# --- Shape catalog ---

SHAPES = {
    "Heart": lambda: sample_parametric(heart),
    "Star": lambda: sample_parametric(lambda t: star(t, 5)),
    "Trefoil": lambda: sample_parametric(trefoil),
    "Butterfly": lambda: sample_parametric(butterfly, 1000),
    "Spirograph": lambda: sample_parametric(hypotrochoid),
    "Cat": lambda: shape_from_svg(SVG_CAT),
    "Fish": lambda: shape_from_svg(SVG_FISH),
    "Lightning": lambda: shape_from_svg(SVG_LIGHTNING),
    "Music Note": lambda: shape_from_svg(SVG_MUSIC_NOTE),
    "Square": lambda: points_to_complex([(1, 1), (1, -1), (-1, -1), (-1, 1)]),
}

SHAPE_NAMES = list(SHAPES.keys())


# =============================================================================
# Fourier computation
# =============================================================================

def compute_fourier_coefficients(z: np.ndarray) -> np.ndarray:
    """Compute DFT coefficients, ordered by magnitude (largest first)."""
    coeffs = np.fft.fft(z) / len(z)
    freqs = np.fft.fftfreq(len(z)) * len(z)
    order = np.argsort(-np.abs(coeffs))
    return np.array(list(zip(freqs[order], coeffs[order])),  # noqa
                    dtype=[('freq', float), ('coeff', complex)])


def evaluate_epicycles(coeffs, t, n_terms: int):
    """Evaluate the first n_terms epicycles at time t."""
    circles = []
    x, y = 0.0, 0.0
    for i in range(min(n_terms, len(coeffs))):
        freq = coeffs[i]['freq']
        c = coeffs[i]['coeff']
        radius = abs(c)
        angle = 2 * np.pi * freq * t + np.angle(c)
        circles.append((x, y, radius, angle))
        x += radius * np.cos(angle)
        y += radius * np.sin(angle)
    return circles, (x, y)


# =============================================================================
# Application state
# =============================================================================

class AppState:
    def __init__(self):
        self.shape_idx = 0
        self.n_terms = 20
        self.speed = 1.0
        self.show_circles = True
        self.show_radii = True
        self.paused = False

        self.t = 0.0
        self.last_time = time.time()
        self.trail: List[Tuple[float, float]] = []
        self.max_trail = 2000

        self.coeffs = None
        self.shape_points = None
        self._load_shape(0)

    def _load_shape(self, idx: int):
        self.shape_idx = idx
        z = SHAPES[SHAPE_NAMES[idx]]()
        self.coeffs = compute_fourier_coefficients(z)
        self.shape_points = z
        self.trail.clear()
        self.t = 0.0

    def update(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if not self.paused:
            self.t += dt * self.speed * 0.15


# =============================================================================
# Drawing
# =============================================================================

def draw_epicycles(state: AppState, center: ImVec2, scale: float):
    draw_list = imgui.get_window_draw_list()
    circles, tip = evaluate_epicycles(state.coeffs, state.t, state.n_terms)

    # Add tip to trail
    state.trail.append(tip)
    if len(state.trail) > state.max_trail:
        state.trail = state.trail[-state.max_trail:]

    # Draw circles and radii
    if state.show_circles or state.show_radii:
        for cx, cy, radius, angle in circles:
            sx = center.x + cx * scale
            sy = center.y - cy * scale
            sr = radius * scale
            if state.show_circles and sr > 1:
                draw_list.add_circle(
                    ImVec2(sx, sy), sr,
                    imgui.get_color_u32(ImVec4(0.4, 0.4, 0.7, 0.5)),
                    0, 1.5)
            if state.show_radii:
                ex = center.x + (cx + radius * np.cos(angle)) * scale
                ey = center.y - (cy + radius * np.sin(angle)) * scale
                draw_list.add_line(
                    ImVec2(sx, sy), ImVec2(ex, ey),
                    imgui.get_color_u32(ImVec4(0.6, 0.6, 0.8, 0.7)),
                    1.5)

    # Draw trail with fade
    if len(state.trail) >= 2:
        for i in range(len(state.trail) - 1):
            alpha = (i + 1) / len(state.trail)
            c = imgui.get_color_u32(ImVec4(0.2, 0.8, 1.0, alpha * 0.95))
            p1 = state.trail[i]
            p2 = state.trail[i + 1]
            draw_list.add_line(
                ImVec2(center.x + p1[0] * scale, center.y - p1[1] * scale),
                ImVec2(center.x + p2[0] * scale, center.y - p2[1] * scale),
                c, 2.5)

    # Draw tip dot
    tx = center.x + tip[0] * scale
    ty = center.y - tip[1] * scale
    draw_list.add_circle_filled(
        ImVec2(tx, ty), 5.0,
        imgui.get_color_u32(ImVec4(1.0, 0.3, 0.3, 1.0)))


# =============================================================================
# GUI
# =============================================================================

FA_PLAY = icons_fontawesome_4.ICON_FA_PLAY
FA_PAUSE = icons_fontawesome_4.ICON_FA_PAUSE
FA_UNDO = icons_fontawesome_4.ICON_FA_UNDO

def gui(state: AppState):
    state.update()
    em = hello_imgui.em_size()

    # Controls (left column)
    imgui.begin_child("controls", ImVec2(em * 18, 0))

    imgui_md.render(__doc__)
    imgui.spacing()

    # Shape selector
    imgui.text("Shape")
    changed, state.shape_idx = imgui.combo("##shape", state.shape_idx, SHAPE_NAMES)
    if changed:
        state._load_shape(state.shape_idx)

    imgui.spacing()

    # Circles knob
    max_terms = min(len(state.coeffs), 200) if state.coeffs is not None else 200
    changed_n, state.n_terms = imgui_knobs.knob_int(
        "Circles", state.n_terms, 1, max_terms,
        speed=0.5,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot)

    imgui.same_line()

    # Speed knob
    _, state.speed = imgui_knobs.knob(
        "Speed", state.speed, 0.1, 5.0,
        speed=0.01,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.1f")

    imgui.spacing()

    # Play/Pause + Reset buttons (round style)
    rounding = em * 0.5
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, rounding)
    btn_size = ImVec2(em * 2.5, em * 2.0)

    if imgui.button(FA_PAUSE if not state.paused else FA_PLAY, btn_size):
        state.paused = not state.paused
    imgui.same_line()
    if imgui.button(FA_UNDO, btn_size):
        state.trail.clear()
        state.t = 0.0

    imgui.pop_style_var()

    imgui.spacing()

    # Toggles for display options
    _, state.show_circles = imgui_toggle.toggle("Circles##tog", state.show_circles)
    imgui.same_line()
    imgui.text("Circles")
    _, state.show_radii = imgui_toggle.toggle("Radii##tog", state.show_radii)
    imgui.same_line()
    imgui.text("Radii")

    imgui.spacing()
    imgui.separator()
    imgui.spacing()

    # Spectrum plot: magnitude sorted by harmonic index, auto-fit
    imgui.text("Frequency spectrum")
    if state.coeffs is not None:
        n = min(state.n_terms, 60)
        magnitudes = np.array([abs(state.coeffs[i]['coeff']) for i in range(n)])
        freq_order = np.argsort([abs(state.coeffs[i]['freq']) for i in range(n)])
        sorted_mags = magnitudes[freq_order]
        bar_positions = np.arange(n, dtype=float)
        if implot.begin_plot("##spectrum", ImVec2(-1, em * 10)):
            implot.setup_axes("Harmonic #", "Magnitude")
            implot.setup_axes_limits(
                -0.5, float(n) - 0.5,
                0, float(np.max(sorted_mags)) * 1.1 + 0.01,
                imgui.Cond_.always)
            implot.plot_bars("##mag", bar_positions, sorted_mags, 0.7)
            implot.end_plot()

    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")

    imgui.end_child()

    imgui.same_line()

    # Animation (right area)
    imgui.begin_child("animation", ImVec2(0, 0))
    avail = imgui.get_content_region_avail()
    center = imgui.get_cursor_screen_pos()
    center = ImVec2(center.x + avail.x * 0.5, center.y + avail.y * 0.5)

    # Compute scale to fit the shape
    if state.shape_points is not None:
        max_extent = max(np.max(np.abs(state.shape_points.real)),
                        np.max(np.abs(state.shape_points.imag)))
        scale = min(avail.x, avail.y) * 0.35 / max(max_extent, 1e-6)
    else:
        scale = 20.0

    draw_epicycles(state, center, scale)

    # Draw original shape faintly
    if state.shape_points is not None:
        draw_list = imgui.get_window_draw_list()
        z = state.shape_points
        col = imgui.get_color_u32(ImVec4(1.0, 1.0, 1.0, 0.12))
        for i in range(len(z)):
            j = (i + 1) % len(z)
            draw_list.add_line(
                ImVec2(center.x + z[i].real * scale, center.y - z[i].imag * scale),
                ImVec2(center.x + z[j].real * scale, center.y - z[j].imag * scale),
                col, 1.0)

    imgui.end_child()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_title="Fourier Epicycles",
        window_size=(1200, 700),
        with_implot=True,
        with_markdown=True,
        fps_idle=0,
        ini_disable=True
    )


if __name__ == "__main__":
    main()
