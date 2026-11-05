"""Gravitational lensing: a galaxy seen through a mass, as a ring, arcs or several images

A mass in the foreground bends the light of a galaxy behind it. The left sky shows the galaxy as it is, the right one
what we see through the lens. Drag the galaxy (yellow) and the lens (blue), turn the knobs, or start from a preset: an
Einstein ring, two images, a giant arc, the Einstein Cross. The thin lines are the critical curve, where the
magnification diverges, and its map in the source plane, the caustic: as the galaxy crosses it, images are born or
merge. Hover a pixel of the observed sky to see where its light comes from.

The model is a thin, static lens in arbitrary angular units: a point mass (a star, a black hole), an isothermal sphere
(a galaxy), or a galaxy with an external shear, which makes the four images of the Einstein Cross. Each pixel of the
observed sky is traced back to the source plane (backward ray mapping, with NumPy), so the same galaxy can answer
several times. The texts live in `gravitational_lensing_help.md` beside the program; the tab "How it works" shows
them whole.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from imgui_bundle import ImVec2, ImVec4, em_size, hello_imgui, imgui, imgui_knobs, imgui_toggle, immapp, implot, rich_md

HERE = Path(__file__).parent
HELP_FILE = HERE / "gravitational_lensing_help.md"  # the intro of the tab, and the text of "How it works"

GRID = 192  # the skies' resolution, in pixels on a side
EXTENT = 2.15  # the skies' half width, in the unit of angle (the Einstein radius is about 0.8)
SOFT = 0.008  # a small core at each mass: no division by zero
TWEEN_SECONDS = 1.2  # a preset's parameters ease in over this time
LABEL_SECONDS = 8.0  # the handles' names stay this long after the start, then fade
NARROW_WIDTH_EM = 50  # under this width (a phone), everything goes in one column
CONTROLS_WIDTH_EM = 21
KNOB_SIZE_EM = 3.4
SOURCE_COLOR = ImVec4(1.0, 0.83, 0.33, 1.0)  # the galaxy's handle
LENS_COLOR = ImVec4(0.29, 0.85, 1.0, 1.0)  # the lens's handle
SECOND_COLOR = ImVec4(1.0, 0.48, 0.54, 1.0)  # the second lens's handle
CURVE_COLOR = ImVec4(0.48, 0.81, 0.97, 0.75)  # the critical curve and the caustic
IMAGE_COLOR = ImVec4(1.0, 0.96, 0.87, 1.0)  # the exact image points
HOVER_COLOR = ImVec4(0.55, 1.0, 0.6, 1.0)  # the hovered pixel's origin, and the cells lit by a hover
GHOST_COLOR = ImVec4(1.0, 0.83, 0.33, 0.45)  # the galaxy's true outline in the observed sky
COLORMAPS = ("Lensing sky", "Greys", "Viridis")  # the sky's colors: a night sky, a telescope's raw image, a false color

Array = NDArray[np.float64]
AXIS = np.linspace(-EXTENT, EXTENT, GRID)
STEP = float(AXIS[1] - AXIS[0])
X, Y = np.meshgrid(AXIS, AXIS[::-1])  # row 0 at the top, as ImPlot draws a heatmap
ANGLE = np.linspace(0.0, 2.0 * np.pi, 181)

POINT_MASS, GALAXY, GALAXY_SHEAR = 0, 1, 2
MODEL_NAMES = ("Point mass", "Galaxy", "Galaxy with shear")


# ======================================================================================================================
# The model: a galaxy, a lens, the mapping from the observed sky to the source plane
# ======================================================================================================================
@dataclass
class Params:
    sx: float = 0.12  # the galaxy's center, in the source plane
    sy: float = 0.03
    size: float = 0.38  # its radius, and its tilt in radians
    tilt: float = 0.40
    lx: float = 0.0  # the lens, in the observed sky
    ly: float = 0.0
    einstein: float = 0.78  # the Einstein radius: the ring's radius when the galaxy sits right behind the lens
    model: int = POINT_MASS
    shear: float = 0.15  # the external shear of GALAXY_SHEAR: the pull of the lens's neighbors
    binary: bool = False  # a second lens, of the same kind
    l2x: float = 0.68
    l2y: float = 0.06
    mass_ratio: float = 0.35  # the second lens's mass, relative to the first


TWEENED = ("sx", "sy", "size", "tilt", "lx", "ly", "einstein", "shear", "l2x", "l2y", "mass_ratio")


@dataclass
class Preset:
    name: str
    caption: str  # one sentence under the skies
    params: Params


PRESETS = (
    Preset("Einstein ring", "The galaxy sits right behind the lens: its light comes from all around it, a ring.",
           Params(sx=0.0, sy=0.0)),
    Preset("Two images", "A little off the axis, the ring breaks into two images: one outside the ring, one inside, "
           "mirrored.", Params(sx=0.48, sy=0.08)),
    Preset("Giant arc", "A galaxy as the lens, a small source near the axis: a long arc on one side, a faint counter "
           "image on the other.", Params(sx=0.14, sy=0.04, size=0.28, model=GALAXY)),
    Preset("Einstein Cross", "A lens pulled by its neighbors (a shear): the caustic becomes a diamond, and a source "
           "inside it shows four times.", Params(sx=0.04, sy=0.025, size=0.10, model=GALAXY_SHEAR, shear=0.15)),
    Preset("Binary lens", "Two masses: the critical curve joins them, the caustic grows cusps, and the images "
           "multiply.", Params(sx=0.15, sy=0.06, binary=True)),
)


def galaxy(x: Array, y: Array, p: Params) -> Array:
    """A synthetic spiral galaxy's surface brightness at the source-plane positions (x, y): a bulge, a disk, two arms
    and a bright knot on one side, which shows the mirror images"""
    dx, dy = x - p.sx, y - p.sy
    ca, sa = np.cos(p.tilt), np.sin(p.tilt)
    u = (ca * dx + sa * dy) / p.size
    v = (-sa * dx + ca * dy) / (p.size * 0.64)
    r = np.sqrt(u * u + v * v + 1e-7)
    phi = np.arctan2(v, u)
    bulge = 1.15 * np.exp(-0.5 * (r / 0.30) ** 2)
    disk = 0.64 * np.exp(-r / 0.90)
    arms = (0.5 + 0.5 * np.cos(2.0 * phi - 3.5 * np.log(r + 0.20))) ** 4
    knot = 0.42 * np.exp(-((u - 0.53) ** 2 + (v - 0.18) ** 2) / 0.018)
    return np.asarray(bulge + disk * (0.27 + 1.05 * arms) + knot, dtype=np.float64)


def ray_map(x: Array, y: Array, p: Params) -> Tuple[Array, Array]:
    """Where the light seen at (x, y) comes from: the source-plane position, by the lens equation. A point mass
    deflects as 1/r, an isothermal sphere by a constant angle; the shear stretches the sky along x and squeezes it
    along y, around the lens."""
    bx, by = x.copy(), y.copy()
    lenses = [(p.lx, p.ly, 1.0)]
    if p.binary:
        lenses.append((p.l2x, p.l2y, p.mass_ratio))
    for lx, ly, mass in lenses:
        dx, dy = x - lx, y - ly
        r2 = dx * dx + dy * dy + SOFT * SOFT
        k = p.einstein * p.einstein * mass / r2 if p.model == POINT_MASS else p.einstein * mass / np.sqrt(r2)
        bx -= k * dx
        by -= k * dy
    if p.model == GALAXY_SHEAR:
        bx -= p.shear * (x - p.lx)
        by += p.shear * (y - p.ly)
    return bx, by


def image_points(p: Params) -> Tuple[Array, Array, float]:
    """The exact images of the galaxy's center and their total magnification, for one point mass or one isothermal
    sphere. On the axis, a ring: no point, an infinite magnification. With a shear or two lenses: nothing (the hover
    shows the images)."""
    none = np.empty(0)
    if p.binary or p.model == GALAXY_SHEAR:
        return none, none, float("nan")
    vx, vy = p.sx - p.lx, p.sy - p.ly
    d = float(np.hypot(vx, vy))
    if d < 1e-6:
        return none, none, float("inf")
    ux, uy = vx / d, vy / d
    if p.model == POINT_MASS:
        root = np.sqrt(d * d + 4.0 * p.einstein ** 2)
        t = np.array([0.5 * (d + root), 0.5 * (d - root)])  # along the source's direction, past and before the lens
        u = d / p.einstein
        mu = float((u * u + 2.0) / (u * np.sqrt(u * u + 4.0)))
    else:
        t = np.array([d + p.einstein] + ([d - p.einstein] if d < p.einstein else []))
        mu = 2.0 * p.einstein / d if d < p.einstein else 1.0 + p.einstein / d
    return p.lx + t * ux, p.ly + t * uy, mu


def critical_curve(bx: Array, by: Array, p: Params) -> Tuple[Array, Array]:
    """The points of the observed sky where the mapping's Jacobian changes sign between neighboring cells: the critical
    curve, where the magnification diverges. The cells around each mass are left out (its singularity)."""
    bx_y, bx_x = np.gradient(bx, STEP)  # along the rows (y, downwards) and the columns (x)
    by_y, by_x = np.gradient(by, STEP)
    det = bx_x * by_y - bx_y * by_x
    near = (X - p.lx) ** 2 + (Y - p.ly) ** 2 < (3 * STEP) ** 2
    if p.binary:
        near |= (X - p.l2x) ** 2 + (Y - p.l2y) ** 2 < (3 * STEP) ** 2
    det = np.where(near, np.nan, det)
    with np.errstate(invalid="ignore", divide="ignore"):
        d0, d1 = det[:, :-1], det[:, 1:]  # between a cell and its right neighbor
        cross = d0 * d1 < 0
        xs = [(X[:, :-1] + STEP * d0 / (d0 - d1))[cross]]
        ys = [Y[:, :-1][cross]]
        d0, d1 = det[:-1, :], det[1:, :]  # between a cell and the one under it
        cross = d0 * d1 < 0
        xs.append(X[:-1, :][cross])
        ys.append((Y[:-1, :] - STEP * d0 / (d0 - d1))[cross])
    return np.concatenate(xs), np.concatenate(ys)


def exposure_stretch(light: Array, exposure: float) -> Array:
    """The display's brightness: an asinh stretch, as astronomers show a sky whose range the eye cannot take"""
    return np.ascontiguousarray(np.clip(np.arcsinh(exposure * light) / np.arcsinh(exposure * 1.8), 0.0, 1.0))


class Lab:
    """The state: the parameters, the computed skies, the tween toward a preset, the hover"""

    def __init__(self) -> None:
        self.p = Params()
        self.exposure = 4.0
        self.show_curves = True
        self.show_images = True
        self.show_ghost = False
        self.cmap_index = 0
        self.caption = "Drag the yellow galaxy and the blue lens, or start from a preset."
        self.dirty = True
        self.tween_t = -1.0  # the tween's progress, 0 to 1; -1 when none runs
        self.tween_from: Dict[str, float] = {}
        self.tween_to: Dict[str, float] = {}
        self.hover_source: Optional[Tuple[float, float]] = None  # the origin of the hovered pixel of the observed sky
        self.hover_cells: Tuple[Array, Array] = (np.empty(0), np.empty(0))  # the cells lit by a hover of the source
        self.hover_frame = -9  # when the hover was last seen
        self.started = -1.0  # the first frame's time, for the labels (no ImGui context yet at the import)
        self.source = np.zeros((GRID, GRID))
        self.lensed = np.zeros((GRID, GRID))
        self.beta_x, self.beta_y = X.copy(), Y.copy()  # the mapping of the grid
        self.source_display = self.source.copy()
        self.lensed_display = self.lensed.copy()
        self.flux_ratio = 1.0
        self.point_mu = 1.0
        self.image_x, self.image_y = np.empty(0), np.empty(0)
        self.crit_x, self.crit_y = np.empty(0), np.empty(0)
        self.caustic_x, self.caustic_y = np.empty(0), np.empty(0)

    def start_preset(self, preset: Preset) -> None:
        """The preset's parameters ease in: the model switches at once, the numbers tween; a second lens grows in"""
        q = preset.params
        if q.binary and not self.p.binary:
            self.p.mass_ratio = 0.0
        self.p.binary, self.p.model = q.binary, q.model
        self.tween_from = {k: float(getattr(self.p, k)) for k in TWEENED}
        self.tween_to = {k: float(getattr(q, k)) for k in TWEENED}
        self.tween_t = 0.0
        self.caption = preset.caption
        self.dirty = True

    def advance(self, dt: float) -> None:
        if self.tween_t < 0:
            return
        self.tween_t = min(1.0, self.tween_t + dt / TWEEN_SECONDS)
        ease = 1.0 - (1.0 - self.tween_t) ** 3
        for k in TWEENED:
            setattr(self.p, k, self.tween_from[k] + (self.tween_to[k] - self.tween_from[k]) * ease)
        if self.tween_t >= 1.0:
            self.tween_t = -1.0
        self.dirty = True

    def touched(self) -> None:
        """A drag or a knob: the tween, if one runs, stops where it is"""
        self.tween_t = -1.0
        self.dirty = True

    def recompute(self) -> None:
        """The skies, once per parameter change, not at every frame"""
        p = self.p
        self.source = galaxy(X, Y, p)
        self.beta_x, self.beta_y = ray_map(X, Y, p)
        self.lensed = galaxy(self.beta_x, self.beta_y, p)
        self.flux_ratio = float(self.lensed.sum() / max(self.source.sum(), 1e-20))
        self.image_x, self.image_y, self.point_mu = image_points(p)
        if self.show_curves:
            self.crit_x, self.crit_y = critical_curve(self.beta_x, self.beta_y, p)
            self.caustic_x, self.caustic_y = ray_map(self.crit_x, self.crit_y, p)
        self.reexpose()
        self.dirty = False

    def reexpose(self) -> None:
        self.source_display = exposure_stretch(self.source, self.exposure)
        self.lensed_display = exposure_stretch(self.lensed, self.exposure)

    def light_cells(self, sx: float, sy: float) -> Tuple[Array, Array]:
        """The cells of the observed sky whose light comes from near (sx, sy) in the source plane: the hovered
        source point's images"""
        near = (self.beta_x - sx) ** 2 + (self.beta_y - sy) ** 2 < (2.5 * STEP) ** 2
        return X[near], Y[near]


LAB = Lab()


# ======================================================================================================================
# The texts: the sections of gravitational_lensing_help.md
# ======================================================================================================================
def read_help() -> Dict[str, str]:
    """The help file's sections, by their heading: the text under each heading, up to the next one"""
    sections: Dict[str, str] = {}
    heading = ""
    for line in HELP_FILE.read_text(encoding="utf-8").splitlines():
        found = re.match(r"^#+ (.*)", line)
        if found:
            heading = found.group(1).strip()
            sections[heading] = ""
        else:
            sections[heading] = sections.get(heading, "") + line + "\n"
    return sections


HELP = read_help()
HELP_TEXT = HELP_FILE.read_text(encoding="utf-8")


def gui_intro() -> None:
    """The tab's intro, folded to its first sentence: "More..." opens it"""
    options = rich_md.FoldingTextOptions()
    options.start_folded = True
    rich_md.render_folding("intro", HELP["Explore"], options)


# ======================================================================================================================
# The skies
# ======================================================================================================================
SKY_FLAGS = implot.Flags_.equal | implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text


def sky_colormap() -> int:
    """A night sky's false colors: midnight to cream, added to ImPlot once"""
    cmap = implot.get_colormap_index(COLORMAPS[0])
    if cmap == -1:
        colors = np.array([[0.012, 0.020, 0.058, 1.0], [0.070, 0.065, 0.200, 1.0], [0.190, 0.155, 0.390, 1.0],
                           [0.360, 0.230, 0.520, 1.0], [0.740, 0.345, 0.510, 1.0], [0.980, 0.625, 0.360, 1.0],
                           [1.000, 0.950, 0.765, 1.0]], dtype=np.float32)
        cmap = implot.add_colormap(COLORMAPS[0], colors, qual=False)
    return cmap


def current_colormap() -> int:
    sky_colormap()
    return implot.get_colormap_index(COLORMAPS[LAB.cmap_index])


def faded(color: ImVec4) -> ImVec4:
    """The handles' labels: full for a while after the start, then gone"""
    alpha = max(0.0, min(1.0, LAB.started + LABEL_SECONDS - imgui.get_time()))
    return ImVec4(color.x, color.y, color.z, color.w * alpha)


def draw_handle(id: int, x: float, y: float, color: ImVec4, label: str) -> Optional[Tuple[float, float]]:
    """A draggable dot, named for a while; its new position when dragged"""
    changed, nx, ny = implot.drag_point(id, x, y, color, 9.0)[:3]
    if faded(color).w > 0:
        implot.annotation(x, y, faded(color), ImVec2(em_size(0.8), -em_size(0.8)), True, label)
    if changed:
        return float(np.clip(nx, -EXTENT * 0.9, EXTENT * 0.9)), float(np.clip(ny, -EXTENT * 0.9, EXTENT * 0.9))
    return None


def plot_dots(label: str, xs: Array, ys: Array, color: ImVec4, size: float) -> None:
    implot.plot_scatter(label, xs, ys, implot.Spec(marker=implot.Marker_.circle, marker_size=size,
                                                   marker_fill_color=color, marker_line_color=color))


def draw_sky(observed: bool, side: float) -> None:
    """One of the two skies: the galaxy as it is (the source plane), or what we see (the observed sky)"""
    p, frame = LAB.p, imgui.get_frame_count()
    if side < em_size(16):  # a phone: short titles
        title = "What we see" if observed else "As it is"
    else:
        title = "What we see, through the lens" if observed else "The galaxy as it is"
    if not implot.begin_plot(f"{title}##{observed}", ImVec2(side, side), SKY_FLAGS):
        return
    implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
    implot.setup_axes_limits(-EXTENT, EXTENT, -EXTENT, EXTENT, imgui.Cond_.always)
    implot.push_colormap(current_colormap())
    implot.plot_heatmap("##sky", LAB.lensed_display if observed else LAB.source_display, 0.0, 1.0, "",
                        implot.Point(-EXTENT, -EXTENT), implot.Point(EXTENT, EXTENT))
    implot.pop_colormap()
    hovered = implot.is_plot_hovered()
    mouse = implot.get_plot_mouse_pos() if hovered else None
    fresh = frame - LAB.hover_frame <= 2  # the other sky's hover, seen a frame ago

    if observed:
        if LAB.show_curves:
            plot_dots("##critical", LAB.crit_x, LAB.crit_y, CURVE_COLOR, 1.5)
        if LAB.show_ghost:  # the galaxy's outline, where it would be without the lens
            ca, sa = np.cos(p.tilt), np.sin(p.tilt)
            u, v = 1.2 * p.size * np.cos(ANGLE), 1.2 * p.size * 0.64 * np.sin(ANGLE)
            implot.plot_line("##ghost", p.sx + ca * u - sa * v, p.sy + sa * u + ca * v,
                             implot.Spec(line_color=GHOST_COLOR, line_weight=1.0))
        if LAB.show_images and LAB.image_x.size:
            plot_dots("##images", LAB.image_x, LAB.image_y, IMAGE_COLOR, 5.0)
        if fresh and LAB.hover_cells[0].size:
            plot_dots("##lit", LAB.hover_cells[0], LAB.hover_cells[1], HOVER_COLOR, 2.0)
        moved = draw_handle(1, p.lx, p.ly, LENS_COLOR, "lens")
        if moved:
            p.lx, p.ly = moved
            LAB.touched()
        if p.binary:
            moved = draw_handle(2, p.l2x, p.l2y, SECOND_COLOR, "second lens")
            if moved:
                p.l2x, p.l2y = moved
                LAB.touched()
        if mouse is not None:
            bx, by = ray_map(np.array([mouse.x]), np.array([mouse.y]), p)
            LAB.hover_source, LAB.hover_frame = (float(bx[0]), float(by[0])), frame
            LAB.hover_cells = (np.empty(0), np.empty(0))
    else:
        if LAB.show_curves:
            plot_dots("##caustic", LAB.caustic_x, LAB.caustic_y, CURVE_COLOR, 1.5)
        if fresh and LAB.hover_source is not None:
            hx, hy = LAB.hover_source
            implot.plot_scatter("##origin", np.array([hx]), np.array([hy]),
                                implot.Spec(marker=implot.Marker_.cross, marker_size=7, marker_line_color=HOVER_COLOR))
        moved = draw_handle(0, p.sx, p.sy, SOURCE_COLOR, "galaxy")
        if moved:
            p.sx, p.sy = moved
            LAB.touched()
        if mouse is not None:
            LAB.hover_source, LAB.hover_cells, LAB.hover_frame = None, LAB.light_cells(mouse.x, mouse.y), frame
    implot.end_plot()
    hello_imgui.set_item_takes_touch_drags()  # on a touch screen, a drag on the sky moves a handle, not the page


# ======================================================================================================================
# The controls
# ======================================================================================================================
def knob(label: str, value: float, lo: float, hi: float, speed: float, fmt: str,
         variant: imgui_knobs.ImGuiKnobVariant_ = imgui_knobs.ImGuiKnobVariant_.wiper_dot) -> Tuple[bool, float]:
    changed, value = imgui_knobs.knob(label, value, lo, hi, speed, fmt, variant, em_size(KNOB_SIZE_EM))
    hello_imgui.set_item_takes_touch_drags()  # on a touch screen, a drag on a knob turns it at once
    return changed, value


def param_knob(label: str, name: str, lo: float, hi: float, speed: float, fmt: str = "%.2f",
               variant: imgui_knobs.ImGuiKnobVariant_ = imgui_knobs.ImGuiKnobVariant_.wiper_dot) -> None:
    changed, value = knob(label, float(getattr(LAB.p, name)), lo, hi, speed, fmt, variant)
    if changed:
        setattr(LAB.p, name, value)
        LAB.touched()


def gui_presets() -> None:
    width = (imgui.get_content_region_avail().x - imgui.get_style().item_spacing.x) / 2
    for i, preset in enumerate(PRESETS):
        if i % 2:
            imgui.same_line()
        if imgui.button(preset.name, ImVec2(width, 0)):
            LAB.start_preset(preset)


def gui_controls(with_presets: bool) -> None:
    p = LAB.p
    if with_presets:
        imgui.separator_text("Presets")
        gui_presets()
    imgui.separator_text("Galaxy")
    param_knob("Size", "size", 0.12, 0.70, 0.003)
    imgui.same_line()
    param_knob("Tilt", "tilt", -3.14, 3.14, 0.02, "%.2f", imgui_knobs.ImGuiKnobVariant_.dot)
    imgui.separator_text("Lens")
    imgui.set_next_item_width(-1)
    changed, p.model = imgui.combo("##model", p.model, list(MODEL_NAMES))
    if changed:
        LAB.touched()
    param_knob("Radius", "einstein", 0.25, 1.20, 0.004)
    if p.model == GALAXY_SHEAR:
        imgui.same_line()
        param_knob("Shear", "shear", 0.0, 0.30, 0.002)
    if p.binary:
        imgui.same_line()
        param_knob("2nd mass", "mass_ratio", 0.02, 1.0, 0.004)
    changed, p.binary = imgui_toggle.toggle("Second lens", p.binary)
    if changed:
        LAB.touched()
    imgui.separator_text("Display")
    changed, LAB.exposure = knob("Exposure", LAB.exposure, 0.5, 15.0, 0.05, "%.1f",
                                 imgui_knobs.ImGuiKnobVariant_.wiper_only)
    if changed:
        LAB.reexpose()  # a display change: no new mapping
    imgui.same_line()
    imgui.begin_group()
    imgui.text("Colors")
    if implot.colormap_button("##colors", ImVec2(em_size(5), 0), current_colormap()):
        LAB.cmap_index = (LAB.cmap_index + 1) % len(COLORMAPS)
    imgui.end_group()
    changed, LAB.show_curves = imgui_toggle.toggle("Critical curve, caustic", LAB.show_curves)
    if changed:
        LAB.dirty = True
    _, LAB.show_images = imgui_toggle.toggle("Exact images", LAB.show_images)
    _, LAB.show_ghost = imgui_toggle.toggle("True outline", LAB.show_ghost)
    imgui.separator_text("Light")
    most = max(1.0, LAB.flux_ratio)
    imgui.progress_bar(1.0 / most, ImVec2(-1, 0), "as it is: x1.00")
    imgui.progress_bar(LAB.flux_ratio / most, ImVec2(-1, 0), f"through the lens: x{LAB.flux_ratio:.2f}")
    if np.isnan(LAB.point_mu):
        imgui.text_disabled("Exact magnification: one lens, no shear")
    elif np.isinf(LAB.point_mu):
        imgui.text("Its center: a ring, magnified without limit")
    else:
        imgui.text(f"Its center, exactly: x{LAB.point_mu:.2f}")
    imgui.text_wrapped("The lens spreads the same light over a larger area: more light reaches us, not brighter "
                       "pixels.")


# ======================================================================================================================
# The layout
# ======================================================================================================================
def gui_skies(side: float, stacked: bool) -> None:
    draw_sky(False, side)
    if not stacked:
        imgui.same_line()
    draw_sky(True, side)
    imgui.text_wrapped(LAB.caption)


def gui_explore() -> None:
    avail = imgui.get_content_region_avail()
    line = imgui.get_text_line_height_with_spacing()
    if avail.x < em_size(NARROW_WIDTH_EM):  # a phone: one column, the presets first, the skies small but both in view
        gui_presets()
        stacked = avail.x < em_size(22)
        gui_skies(avail.x - em_size(0.5) if stacked else (avail.x - imgui.get_style().item_spacing.x) / 2, stacked)
        if imgui.collapsing_header("Controls", imgui.TreeNodeFlags_.default_open):
            gui_controls(with_presets=False)
        return
    imgui.begin_child("controls", ImVec2(em_size(CONTROLS_WIDTH_EM), 0))
    gui_controls(with_presets=True)
    imgui.end_child()
    imgui.same_line()
    imgui.begin_group()
    room = imgui.get_content_region_avail()
    side = max(em_size(10), min((room.x - imgui.get_style().item_spacing.x) / 2, room.y - 2.5 * line))
    gui_skies(side, stacked=False)
    imgui.end_group()


def gui() -> None:
    if LAB.started < 0:
        LAB.started = imgui.get_time()
    LAB.advance(imgui.get_io().delta_time)
    if LAB.dirty:
        LAB.recompute()
    if imgui.begin_tab_bar("##tabs"):
        if imgui.begin_tab_item_simple("Explore"):
            gui_intro()
            gui_explore()
            imgui.end_tab_item()
        if imgui.begin_tab_item_simple("How it works"):
            imgui.begin_child("help")
            rich_md.render(HELP_TEXT)
            imgui.end_child()
            imgui.end_tab_item()
        imgui.end_tab_bar()


def main() -> None:
    immapp.run(gui, window_title="Gravitational lensing", window_size=(1240, 820), with_implot=True,
               with_markdown=True)


if __name__ == "__main__":
    main()
