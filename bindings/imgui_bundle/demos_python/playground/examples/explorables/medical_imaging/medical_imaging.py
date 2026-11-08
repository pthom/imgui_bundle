"""Medical imaging: a chest CT scan, its contrast windows, and a segmentation grown from a click

A real chest CT, explored as a radiologist would: its slices, its windows, and a region grown from a click. Choose
a window preset or drag its bounds on the histogram. Click a structure: the region grows across the slices, and the
app measures it and shows it in 3D. A second tab finds the blood vessels of a retina. For research and teaching, not
for diagnosis.

The original and the processed views zoom and pan together; the original gives the pixels' values in Hounsfield
units (HU). The region takes the pixels within a tolerance of the seed's value, connected to it, slice after slice.
The retina's vessels come from classic image processing, with no learning: the green channel, CLAHE, a black
top-hat, a threshold, and the small blobs dropped. A click on a vessel measures it: its width at half height across
it, its length along its skeleton, its position from the optic disc.

The texts of the app (the intros, the help of each widget) live in `medical_imaging_help.md`, which the tab "How it
works" shows whole, with the code it explains embedded from this file (narrative programming, with RichMd).

The data waits on the site, not in the repository: at its first run, the app downloads it (2 MB) beside itself, and
then runs offline. The scan: LIDC-IDRI-0001, a chest CT of the LIDC-IDRI collection (Armato et al., 2015,
https://doi.org/10.7937/K9/TCIA.2015.LO9QL9SX), from The Cancer Imaging Archive, under the CC BY 3.0 license, made
lighter by `make_ct_data.py`. The fundus photograph: a normal left eye, by Mikael Häggström, Wikimedia Commons, CC0.

Run it:
    pip install imgui-bundle opencv-python
    python medical_imaging.py
"""

import bz2
import contextlib
import io
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, ContextManager, Dict, List, Optional, Tuple, TypeVar

import cv2
import numpy as np
from numpy.typing import NDArray

from imgui_bundle import ImVec2, ImVec4, __bundle_pyodide__, em_size, hello_imgui, imgui, imgui_kit, imgui_knobs, immapp
from imgui_bundle import icons_fontawesome_4 as fa  # the icon font Hello ImGui loads by default
from imgui_bundle import immvision, implot, implot3d, rich_md

T = TypeVar("T")  # a knob's value: a float or an int

HERE = Path(__file__).parent
DATA_URL = "https://imgui-bundle.pages.dev/resources/explorables/medical_imaging/"  # the data, on the site
DATA_FILES = {"ct_chest.npz.bz2": "the CT scan", "fundus_left_eye.jpg": "the retina's photograph"}  # 1.9 MB, 82 KB
HELP_FILE = HERE / "medical_imaging_help.md"  # the intros and the help of each widget
WINDOWS: Dict[str, Tuple[float, float]] = {  # the radiologists' presets: (level, width), in HU
    "Lung": (-600, 1500),
    "Mediastinum": (40, 400),
    "Bone": (400, 1800),
    "Full range": (500, 3000),
}
EXAMPLES: Dict[str, Tuple[Tuple[int, int, int], float]] = {  # seeds to try: (slice, y, x), and the tolerance (HU)
    "Right lung": ((37, 128, 60), 300),
    "Left lung": ((37, 128, 190), 300),
    "Nodule": ((37, 182, 157), 100),
}
START_EXAMPLE = "Right lung"
OVERLAY_RGB = (40, 190, 255)  # the segmented region, and the vessels
OVERLAY_ALPHA = 0.45
SEED_RGB = (255, 200, 40)  # the seed, the window's bounds on the histogram, the slice's plane in 3D
POINTS_3D = 6000  # at most, on the region's surface
NARROW_WIDTH_EM = 52  # under this width (a phone), everything goes in one column
PINNED_MIN_HEIGHT_EM = 24  # a phone at least this tall keeps the viewer at the top, the controls scroll under it
PINNED_VIEW_SHARE = 0.5  # then the view's share of the height
VIEWS = ("Both", "Original", "Segmented", "3D")  # the CT viewer's switch (a phone shows one view at a time)
RETINA_VIEWS = ("Both", "Photograph", "Processed")  # the retina viewer's switch
CONTROLS_WIDTH_EM = 23
HISTOGRAM_HEIGHT_EM = 7.5
HISTOGRAM_BINS = np.arange(-1000, 1510, 10)  # HU
STAGES = ("Green channel", "CLAHE", "Top-hat", "Vessels", "Overlay", "Measure")  # what the retina's second view shows
DISC_CENTER_PX = (137, 372)  # the optic disc on the photograph (800 px), measured by eye
DISC_DIAMETER_PX = 100  # its vertical diameter, measured by eye: the scale of the measures
DISC_DIAMETER_MM = 1.8  # a typical optic disc: it varies from about 1.5 to 2.2 mm between people
NUMBERED_SEGMENTS = 10  # the largest vessel segments carry a number
NUMBERED_RGB = (140, 230, 255)  # their color in the measure's view

Volume = NDArray[np.int16]
Mask = NDArray[np.bool_]
Points = NDArray[np.float64]
Colors = NDArray[np.uint32]


# ======================================================================================================================
# The data: downloaded from the site at the first run, kept beside the program
# ======================================================================================================================
class DataFiles:
    """The data files: read beside the program, else downloaded on request (at once in a browser, whose page already
    downloads everything), and kept there for the next runs (in memory only, when the folder is read-only)"""

    def __init__(self) -> None:
        self.downloads: Dict[str, immapp.Download] = {}
        self.in_memory: Dict[str, bytes] = {}
        self.error = ""

    def missing(self) -> List[str]:
        return [n for n in DATA_FILES if n not in self.in_memory and not (HERE / n).exists()]

    def read(self, name: str) -> bytes:
        return self.in_memory[name] if name in self.in_memory else (HERE / name).read_bytes()

    def start(self) -> None:
        self.error = ""
        for name in self.missing():
            self.downloads[name] = immapp.start_download(DATA_URL + name, timeout_s=120)

    def update(self) -> None:
        for name, download in list(self.downloads.items()):
            if not download.done:
                continue
            del self.downloads[name]
            if download.error:  # the HTTP status alone: the error goes on with the start of the page
                reason = f"HTTP {download.status}" if download.status else download.error.splitlines()[0]
                self.error = f"{name}: {reason}"
                continue
            try:
                (HERE / name).write_bytes(download.data)
            except OSError:
                self.in_memory[name] = download.data


DATA = DataFiles()


def gui_data_ready() -> bool:
    """True when the data is here; else the request to download it, or its progress"""
    DATA.update()
    if not DATA.missing():
        return True
    if __bundle_pyodide__ and not DATA.downloads and not DATA.error:
        DATA.start()
    imgui.dummy(ImVec2(0, em_size(1)))
    if DATA.downloads:
        imgui.text(f"Downloading the data (2 MB) from {DATA_URL}...")
        hello_imgui.set_item_is_live()  # full speed until it arrives
    else:
        imgui.text_wrapped("This demo needs its data: a CT scan and a retina's photograph (2 MB), from the Dear ImGui "
                           "Bundle site. They will be kept beside the program, for the next runs.")
        if imgui.button(f"{fa.ICON_FA_DOWNLOAD} Download the data (2 MB)"):
            DATA.start()
    if DATA.error:
        imgui.text_colored(ImVec4(1, 0.4, 0.4, 1), f"The download failed: {DATA.error}")
    return False


# ======================================================================================================================
# The texts: the sections of medical_imaging_help.md, and the (i) that shows them
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


def help_text(topic: str) -> str:
    """The topic's help, as Markdown, under its title"""
    return f"**{topic}**\n\n{HELP[topic]}"


def help_marker(topic: str) -> None:
    """An (i) after the last widget, with the topic's help: imgui_kit's help marker (a tooltip on hover, a popup on a
    click or a tap), its text rendered as Markdown"""
    imgui.same_line()
    imgui_kit.help_marker(help_text(topic))


def text_with_help(text: str, topic: str) -> None:
    """A wrapped text, and its (i) at the end of its last line"""
    imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
                             - imgui_kit.help_marker_width())
    imgui.text_wrapped(text)
    imgui.pop_text_wrap_pos()
    help_marker(topic)


def gui_intro(tab: str) -> None:
    """The tab's intro, folded to its first paragraph: "More..." opens it. It does not fold by itself on a click
    elsewhere: that folds at the press, and the layout, moved up under the mouse, would lose the click's release."""
    options = rich_md.FoldingTextOptions()
    options.start_folded = True
    rich_md.render_folding(f"intro_{tab}", HELP[tab], options)


# ======================================================================================================================
# The CT: the algorithms
# ======================================================================================================================
# ::code Window
def window_to_gray(hu: NDArray[np.int16], level: float, width: float) -> NDArray[np.uint8]:
    """The slice as the window shows it: level - width / 2 is black, level + width / 2 is white"""
    lo = level - width / 2
    gray: NDArray[np.uint8] = np.clip((hu.astype(np.float32) - lo) * (255.0 / width), 0, 255).astype(np.uint8)
    return gray
# ::endcode


# ::code Region growing
def grow_region(hu: Volume, seed: Tuple[int, int, int], tolerance: float) -> Tuple[Mask, float]:
    """The region of the pixels within `tolerance` HU of the seed's value, connected to the seed: on the seed's slice,
    then slice after slice, where a region of the next slice touches the region of the slice before.
    Returns the region and the seed's value."""
    z0, y0, x0 = seed
    value = float(np.median(hu[z0, max(y0 - 1, 0) : y0 + 2, max(x0 - 1, 0) : x0 + 2]))
    lo, hi = value - tolerance, value + tolerance
    region = np.zeros(hu.shape, bool)

    def components(z: int) -> NDArray[np.int32]:
        inside = ((hu[z] >= lo) & (hu[z] <= hi)).astype(np.uint8)
        return cv2.connectedComponents(inside, connectivity=4)[1]  # type: ignore[no-any-return]

    labels = components(z0)
    if labels[y0, x0] == 0:
        return region, value
    region[z0] = labels == labels[y0, x0]
    for step in (1, -1):
        z = z0 + step
        while 0 <= z < hu.shape[0]:
            labels = components(z)
            touched = np.unique(labels[region[z - step] & (labels > 0)])
            if touched.size == 0:
                break
            region[z] = np.isin(labels, touched)
            z += step
    return region, value
# ::endcode


# ::code Surface points
def surface_points(region: Mask, spacing_mm: Tuple[float, float, float]) -> Tuple[Points, Colors]:
    """Points of the region's surface (its voxels with a neighbor outside), in mm, and their colors, lit from the front
    and above. Returns (x, y, z) columns, the head up and the patient's front toward +y; at most POINTS_3D points."""
    padded = np.pad(region, 1)
    inner = padded[1:-1, 1:-1, 1:-1].copy()
    for axis in range(3):
        for shift in (-1, 1):
            inner &= np.roll(padded, shift, axis)[1:-1, 1:-1, 1:-1]
    z, y, x = np.nonzero(region & ~inner)
    step = max(1, len(z) // POINTS_3D)
    z, y, x = z[::step], y[::step], x[::step]
    dz, dy, dx = spacing_mm
    points = np.stack([x * dx, -y * dy, z * dz], axis=1).astype(np.float64)

    # The normals: the gradient of the region, blurred (it points inward); the shade: how much they face the light
    blurred = np.stack([cv2.blur(s.astype(np.float32), (5, 5)) for s in region])
    blurred[1:-1] = (blurred[:-2] + blurred[1:-1] + blurred[2:]) / 3
    nz, ny, nx = region.shape

    def at(zs: NDArray[np.intp], ys: NDArray[np.intp], xs: NDArray[np.intp]) -> NDArray[np.float32]:
        return blurred[np.clip(zs, 0, nz - 1), np.clip(ys, 0, ny - 1), np.clip(xs, 0, nx - 1)]

    gx = (at(z, y, x + 1) - at(z, y, x - 1)) / dx
    gy = -(at(z, y + 1, x) - at(z, y - 1, x)) / dy  # y goes toward the back in the image, toward the front in 3D
    gz = (at(z + 1, y, x) - at(z - 1, y, x)) / dz
    normals = -np.stack([gx, gy, gz], axis=1)
    normals /= np.linalg.norm(normals, axis=1, keepdims=True) + 1e-9
    light = np.array([-0.3, 0.6, 0.75]) / np.linalg.norm([-0.3, 0.6, 0.75])
    shade = 0.45 + 0.55 * np.clip(normals @ light, 0, 1)
    r, g, b = (np.clip(c * shade, 0, 255).astype(np.uint32) for c in OVERLAY_RGB)
    colors = (r | (g << 8) | (b << 16) | (255 << 24)).astype(np.uint32)  # ImGui's ABGR order
    return points, colors
# ::endcode


def rgb_to_vec4(rgb: Tuple[int, int, int], alpha: float = 1.0) -> ImVec4:
    return ImVec4(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)


def image_params(zoom_key: str, colormap: str, show_pixel_info: bool) -> immvision.ImageParams:
    """The two views of a tab share their zoom (zoom_key), and a double click does not add a watched pixel"""
    params = immvision.ImageParams()
    params.zoom_key = zoom_key
    params.can_resize = False
    params.show_image_info = False
    params.show_pixel_info = show_pixel_info
    params.add_watched_pixel_on_double_click = False
    params.colormap_settings.colormap = colormap
    return params


class ViewClick:
    """A click (or a tap) on a view, told apart from a drag (which pans the views): its pixel, in the image"""

    def __init__(self) -> None:
        self.press: Optional[Tuple[str, float, float, Tuple[float, float]]] = None  # the view, the mouse, the pixel

    def take(self, view: str, params: immvision.ImageParams) -> Optional[Tuple[int, int]]:
        """Call after the view's immvision.image(): (x, y) when a click on it ends, else None"""
        mouse = imgui.get_io().mouse_pos
        if params.mouse_info.is_mouse_hovering and imgui.is_mouse_clicked(imgui.MouseButton_.left):
            self.press = (view, mouse.x, mouse.y, params.mouse_info.mouse_position)
        if self.press is None or self.press[0] != view or not imgui.is_mouse_released(imgui.MouseButton_.left):
            return None
        _, x0, y0, (px, py) = self.press
        self.press = None
        if params.mouse_info.is_mouse_hovering and (mouse.x - x0) ** 2 + (mouse.y - y0) ** 2 < em_size(0.4) ** 2:
            return int(px), int(py)
        return None


def set_views_size(params: Tuple[immvision.ImageParams, ...], size: float) -> None:
    """The views' side (at least 8 em), set when it changes only; their zoom follows it, to show the same part of the
    image"""
    side = max(int(size), int(em_size(8)))
    for p in params:
        old = p.image_display_size[0]
        if old == side:
            continue
        if old > 0:  # the zoom's first two rows map the image to the view: scaled with the view
            m = p.zoom_pan_matrix
            p.zoom_pan_matrix = [[c * side / old for c in m[0]], [c * side / old for c in m[1]], m[2]]
        p.image_display_size = (side, side)


def fit_views(params: Tuple[immvision.ImageParams, ...], width: float, max_height: float) -> None:
    """Two square views side by side, as large as the width and the height allow"""
    spacing = imgui.get_style().item_spacing.x
    set_views_size(params, min((width - spacing) / 2 - imgui.get_frame_height(), max_height))


def centered_on_phone(str_id: str, narrow: bool) -> ContextManager[object]:
    """On a phone, centers what it encloses (a view narrower than the screen); elsewhere, changes nothing"""
    return imgui_kit.aligned_group(str_id, 0.5) if narrow else contextlib.nullcontext()


# ======================================================================================================================
# The CT: its state
# ======================================================================================================================
class CtViewer:
    """The scan, the view (slice, window), the segmentation, and what the GUI draws from them"""

    def __init__(self) -> None:
        data = np.load(io.BytesIO(bz2.decompress(DATA.read("ct_chest.npz.bz2"))))
        self.hu: Volume = data["hu"]  # (slices, rows, columns), from the feet to the head
        dz, dy, dx = (float(v) for v in data["spacing_mm"])
        self.spacing_mm = (dz, dy, dx)
        self.level, self.width = WINDOWS["Lung"]
        self.seed: Optional[Tuple[int, int, int]] = None  # (slice, y, x)
        self.tolerance = 0.0
        self.seed_value = 0.0
        self.region: Mask = np.zeros(self.hu.shape, bool)
        self.points = np.zeros((0, 3))  # the region's surface, in 3D, and the colors of its points
        self.point_colors = np.zeros(0, np.uint32)
        self.original_params = image_params("ct", "Gray", show_pixel_info=True)  # its pixels: the HU
        self.processed_params = image_params("ct", "None", show_pixel_info=False)
        self.processed: NDArray[np.uint8] = np.zeros((*self.hu.shape[1:], 3), np.uint8)
        self.click = ViewClick()  # a click on a view seeds the region
        self.view = "Both"  # the viewer's switch
        self.histogram = (np.zeros(0), np.zeros(0))  # the slice's, then the region's
        self.slice_changed = self.view_changed = True
        self.z = 0
        self.try_example(START_EXAMPLE)

    # The data
    def grow(self) -> None:
        if self.seed is None:
            self.region[:] = False
        else:
            self.region, self.seed_value = grow_region(self.hu, self.seed, self.tolerance)
        self.points, self.point_colors = surface_points(self.region, self.spacing_mm)
        self.view_changed = True

    def try_example(self, name: str) -> None:
        self.seed, self.tolerance = EXAMPLES[name]
        self.set_slice(self.seed[0])
        self.grow()

    def window_bounds(self) -> Tuple[float, float]:
        return self.level - self.width / 2, self.level + self.width / 2

    def update(self) -> None:
        """The processed view and the histograms, made again when the slice, the window or the region changed"""
        self.original_params.refresh_image = self.slice_changed
        self.processed_params.refresh_image = self.slice_changed or self.view_changed
        if self.slice_changed or self.view_changed:
            hu, mask = self.hu[self.z], self.region[self.z]
            rgb = np.repeat(window_to_gray(hu, self.level, self.width)[:, :, None], 3, axis=2).astype(np.float32)
            rgb[mask] = rgb[mask] * (1 - OVERLAY_ALPHA) + np.array(OVERLAY_RGB, np.float32) * OVERLAY_ALPHA
            self.processed = rgb.astype(np.uint8)
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(self.processed, contours, -1, OVERLAY_RGB, 1)
            if self.seed is not None and self.seed[0] == self.z:
                cv2.drawMarker(self.processed, (self.seed[2], self.seed[1]), SEED_RGB, cv2.MARKER_CROSS, 9, 1)
            body = hu > -1024  # the air around the body was blanked to -1024: not counted
            self.histogram = (
                np.histogram(hu[body], HISTOGRAM_BINS)[0].astype(np.float64),
                np.histogram(hu[mask], HISTOGRAM_BINS)[0].astype(np.float64),
            )
        self.slice_changed = self.view_changed = False
        # The original view shows the HU themselves, through a gray colormap over the window. ImmVision sets this range
        # from the image's stats when the image changes: it is set again at each frame. Its "Gray" colormap goes from
        # white to black: the range is given from the window's top to its bottom.
        lo, hi = self.window_bounds()
        self.original_params.colormap_settings.colormap_scale_min = hi
        self.original_params.colormap_settings.colormap_scale_max = lo

    def set_slice(self, z: int) -> None:
        z = int(np.clip(z, 0, self.hu.shape[0] - 1))
        if z != self.z:
            self.z, self.slice_changed = z, True

    def set_window(self, level: float, width: float) -> None:
        if (level, width) != (self.level, self.width):
            self.level, self.width, self.view_changed = level, max(width, 1.0), True

    # The measures
    def area_cm2(self) -> float:
        return float(self.region[self.z].sum()) * self.spacing_mm[1] * self.spacing_mm[2] / 100

    def volume_ml(self) -> float:
        return float(self.region.sum()) * float(np.prod(self.spacing_mm)) / 1000

    def slices_spanned(self) -> Tuple[int, int]:
        zs = np.flatnonzero(self.region.any(axis=(1, 2)))
        return (int(zs[0]), int(zs[-1])) if zs.size else (0, -1)


VIEWER: Optional[CtViewer] = None


def ct_viewer() -> CtViewer:
    global VIEWER
    if VIEWER is None:
        VIEWER = CtViewer()
    return VIEWER


# ======================================================================================================================
# The CT: its GUI
# ======================================================================================================================
def take_click(v: CtViewer, view: str, params: immvision.ImageParams) -> None:
    """A click (or a tap) on a view seeds the region; a drag pans the views, as usual"""
    clicked = v.click.take(view, params)
    if clicked is not None:
        v.seed = (v.z, clicked[1], clicked[0])
        v.grow()


def gui_views(v: CtViewer, width: float, max_height: float, narrow: bool) -> None:
    """The original and the processed views, side by side; they pan and zoom together. The original gives the HU of
    the pixel under the mouse (not on a phone: a finger does not hover)."""
    v.original_params.show_pixel_info = not narrow
    fit_views((v.original_params, v.processed_params), width, max_height)
    v.update()
    immvision.image("Original, in HU##ct", v.hu[v.z], v.original_params)
    take_click(v, "original", v.original_params)
    imgui.same_line()
    immvision.image("Window and segmentation##ct", v.processed, v.processed_params)
    take_click(v, "processed", v.processed_params)


def gui_view_switch(views: Tuple[str, ...], current: str, narrow: bool) -> Tuple[bool, str]:
    """Both views, or one alone, larger (a phone shows one at a time: the processed one, at first).
    Returns (changed, the view)."""
    names = list(views[1:] if narrow else views)
    if current not in names:
        current = names[1]
    with centered_on_phone("switch_" + views[-1], narrow):
        changed, i = imgui_kit.segmented_switch("##view", names.index(current), names)
    return changed, names[i]


def gui_ct_switch(v: CtViewer, narrow: bool) -> None:
    changed, v.view = gui_view_switch(VIEWS, v.view, narrow)
    if changed:  # refreshed: a view hidden while the slice changed would show the old one
        v.slice_changed = True


def gui_one_view(v: CtViewer, width: float, max_size: float, narrow: bool) -> None:
    """The view chosen in the switch, alone: a square as large as the width and max_size allow"""
    if v.view == "3D":
        v.update()  # the histogram
        gui_3d(v, max_size + 2 * imgui.get_frame_height_with_spacing() + em_size(1))  # the images' size, and chrome
        return
    params = v.original_params if v.view == "Original" else v.processed_params
    v.original_params.show_pixel_info = not narrow
    set_views_size((v.original_params, v.processed_params), min(width - imgui.get_frame_height(), max_size))
    v.update()
    with centered_on_phone("ct_view", narrow):
        if v.view == "Original":
            immvision.image("Original, in HU##ct", v.hu[v.z], params)
        else:
            immvision.image("Window and segmentation##ct", v.processed, params)
    take_click(v, v.view, params)


def gui_slice(v: CtViewer) -> None:
    """The slider through the slices, with a step button on each side (a finger moves a slider by one with pain)"""
    if imgui.arrow_button("##previous", imgui.Dir.left):
        v.set_slice(v.z - 1)
    imgui.same_line()
    with imgui_kit.fill_row("slice") as row:  # the slider fills the line, up to the items after row.tail()
        z_mm = v.z * v.spacing_mm[0]
        _, z = imgui.slider_int("##slice", v.z, 0, v.hu.shape[0] - 1, f"Slice %d of {v.hu.shape[0]}  ({z_mm:.0f} mm)")
        v.set_slice(z)
        row.tail()
        if imgui.arrow_button("##next", imgui.Dir.right):
            v.set_slice(v.z + 1)
        help_marker("Slices and views")


def gui_buttons(names: Tuple[str, ...], selected: Optional[str]) -> Optional[str]:
    """A row of buttons that wraps on a narrow screen (an imgui_kit flow), the selected one highlighted. Returns the one
    clicked."""
    clicked = None
    with imgui_kit.flow(names[0]):
        for name in names:
            imgui_kit.flow_next()
            if name == selected:
                imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
            if imgui.button(name):
                clicked = name
            if name == selected:
                imgui.pop_style_color()
    return clicked


def gui_window(v: CtViewer) -> None:
    """The window: its presets, its level and width (beside them when there is room), and the histogram, where its
    bounds can be dragged"""
    current = next((n for n, w in WINDOWS.items() if w == (v.level, v.width)), None)
    clicked = gui_buttons(tuple(WINDOWS), current)
    if clicked is not None:
        v.set_window(*WINDOWS[clicked])
    help_marker("Window")
    slider_width, label_width = em_size(10), em_size(3.5)
    beside = imgui.get_content_region_avail().x - imgui.get_item_rect_max().x + imgui.get_cursor_screen_pos().x
    beside = beside > 2 * (slider_width + label_width) + em_size(4)
    level, width = v.level, v.width
    for name, v_min, v_max in (("Level", -1000, 1000), ("Width", 1, 3000)):
        if beside:
            imgui.same_line(spacing=em_size(1))
        imgui.set_next_item_width(slider_width if beside else -label_width - em_size(1.5))
        if name == "Level":
            _, level = imgui.slider_float(name, level, v_min, v_max, "%.0f HU")
        else:
            _, width = imgui.slider_float(name, width, v_min, v_max, "%.0f HU")
            help_marker("Level and width")
    v.set_window(level, width)
    gui_histogram(v)


def gui_histogram(v: CtViewer) -> None:
    """The slice's histogram (the region's in its color), the window as a gray ramp between two draggable lines"""
    counts, region_counts = v.histogram
    if counts.size == 0:
        return
    centers = (HISTOGRAM_BINS[:-1] + 5).astype(np.float64)
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_box_select | implot.Flags_.no_mouse_text
    if implot.begin_plot("##histogram", ImVec2(-imgui_kit.help_marker_width(), em_size(HISTOGRAM_HEIGHT_EM)), flags):
        implot.setup_axes("HU", "", 0, implot.AxisFlags_.no_tick_labels)
        implot.setup_axis_scale(implot.ImAxis_.y1, implot.Scale_.log10)
        implot.setup_axis_limits(implot.ImAxis_.x1, -1400, 2100, implot.Cond_.always)  # the presets' bounds
        y_max = float(max(counts.max(), 10)) * 2
        implot.setup_axis_limits(implot.ImAxis_.y1, 1, y_max, implot.Cond_.always)

        lo, hi = v.window_bounds()
        implot.push_plot_clip_rect()
        black, white = imgui.get_color_u32(ImVec4(0, 0, 0, 0.45)), imgui.get_color_u32(ImVec4(1, 1, 1, 0.45))
        p_min, p_max = implot.plot_to_pixels(lo, y_max), implot.plot_to_pixels(hi, 1)
        implot.get_plot_draw_list().add_rect_filled_multi_color(p_min, p_max, black, white, white, black)
        implot.pop_plot_clip_rect()

        text = imgui.get_style_color_vec4(imgui.Col_.text)
        implot.plot_shaded("slice", centers, np.maximum(counts, 1), 1, implot.Spec(fill_color=text, fill_alpha=0.25))
        implot.plot_line("slice", centers, np.maximum(counts, 1), implot.Spec(line_color=text))
        if region_counts.any():
            spec = implot.Spec(fill_color=rgb_to_vec4(OVERLAY_RGB), fill_alpha=0.6)
            implot.plot_shaded("region", centers, np.maximum(region_counts, 1), 1, spec)

        accent = rgb_to_vec4(SEED_RGB)
        changed_lo, lo, *_ = implot.drag_line_x(0, lo, accent, 2)
        changed_hi, hi, *_ = implot.drag_line_x(1, hi, accent, 2)
        for x in (lo, hi):
            implot.annotation(x, y_max, accent, ImVec2(0, em_size(0.6)), True, f"{x:.0f}")
        if changed_lo or changed_hi:
            lo, hi = min(lo, hi - 1), max(hi, lo + 1)
            v.set_window((lo + hi) / 2, hi - lo)
        implot.end_plot()
    help_marker("Histogram")


def gui_segmentation(v: CtViewer) -> None:
    """The examples, the tolerance, and the region's measures: its area on this slice, its volume across the slices"""
    text_with_help("Click a structure in either view: a region grows from that point.", "Segmentation")
    imgui.text("Or try:")
    imgui.same_line()
    current = next((n for n, (seed, tol) in EXAMPLES.items() if (seed, tol) == (v.seed, v.tolerance)), None)
    clicked = gui_buttons(tuple(EXAMPLES), current)
    if clicked is not None:
        v.try_example(clicked)
    help_marker("Examples")
    imgui.set_next_item_width(-em_size(7))
    changed, v.tolerance = imgui.slider_float("Tolerance", v.tolerance, 10, 600, "+/- %.0f HU")
    if changed and v.seed is not None:
        v.grow()
    help_marker("Tolerance")
    if v.seed is None or not v.region.any():
        imgui.text_disabled("No region.")
        return
    z, y, x = v.seed
    first, last = v.slices_spanned()
    volume = v.volume_ml()
    volume_text = f"{volume / 1000:.2f} L" if volume >= 1000 else f"{volume:.1f} mL"
    imgui.text(f"Seed: slice {z}, ({x}, {y}), {v.seed_value:.0f} HU")
    imgui.text(f"Area on this slice: {v.area_cm2():.1f} cm²")
    imgui.text(f"Volume: {volume_text}, slices {first} to {last}")
    help_marker("Measures")
    if imgui.button("Clear"):
        v.seed = None
        v.grow()


def gui_3d(v: CtViewer, height: float) -> None:
    """The region in 3D (points of its surface), and the current slice as a plane through it"""
    imgui.text_disabled("Right-drag to rotate (two fingers on a phone)")
    help_marker("In 3D")
    if v.points.shape[0] == 0:
        return
    flags = implot3d.Flags_.no_legend | implot3d.Flags_.no_mouse_text
    transparent = ImVec4(0, 0, 0, 0)  # no strip along the axes to drag: the box's limits are fixed
    implot3d.push_style_color(implot3d.Col_.axis_bg_hovered, transparent)
    implot3d.push_style_color(implot3d.Col_.axis_bg_active, transparent)
    if not implot3d.begin_plot("##region_3d", ImVec2(-1, height - imgui.get_text_line_height_with_spacing()), flags):
        implot3d.pop_style_color(2)
        return
    no_ticks = implot3d.AxisFlags_.no_tick_labels | implot3d.AxisFlags_.no_label
    implot3d.setup_axes("", "", "", no_ticks, no_ticks, no_ticks)
    lo, hi = v.points.min(axis=0), v.points.max(axis=0)  # the box: the region, and a margin
    margin = 0.08 * (hi - lo).max()
    lo, hi = lo - margin, hi + margin
    implot3d.setup_axes_limits(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], implot3d.Cond_.always)
    implot3d.setup_box_scale(*((hi - lo) / (hi - lo).max()))  # the box keeps the region's proportions
    implot3d.setup_box_initial_rotation(15, -60)
    spec = implot3d.Spec(marker=implot3d.Marker_.circle, marker_size=2)
    spec.marker_fill_colors = spec.marker_line_colors = v.point_colors
    xs, ys, zs = (np.ascontiguousarray(v.points[:, i]) for i in range(3))
    implot3d.plot_scatter("region", xs, ys, zs, spec)
    z_mm = v.z * v.spacing_mm[0]
    if lo[2] <= z_mm <= hi[2]:  # the current slice, as a plane through the box
        quad = np.array([[lo[0], lo[1], z_mm], [hi[0], lo[1], z_mm], [hi[0], hi[1], z_mm], [lo[0], hi[1], z_mm]])
        plane = implot3d.Spec(fill_color=rgb_to_vec4(SEED_RGB), fill_alpha=0.25, line_color=rgb_to_vec4(SEED_RGB))
        qx, qy, qz = (np.ascontiguousarray(quad[:, i]) for i in range(3))
        implot3d.plot_quad("slice", qx, qy, qz, plane)
    implot3d.end_plot()
    implot3d.pop_style_color(2)


def gui_ct_credit() -> None:
    imgui.push_text_wrap_pos(0)
    imgui.text_disabled("Scan: LIDC-IDRI-0001, LIDC-IDRI collection (Armato et al., 2015), The Cancer Imaging Archive, "
                        "CC BY 3.0; one slice in two, from the kidneys up, at half resolution.")
    imgui.pop_text_wrap_pos()
    imgui.text_link_open_url("doi.org/10.7937/K9/TCIA.2015.LO9QL9SX", "https://doi.org/10.7937/K9/TCIA.2015.LO9QL9SX")


def gui_ct(v: CtViewer) -> None:
    gui_intro("Chest CT")
    avail = imgui.get_content_region_avail()
    line = imgui.get_frame_height_with_spacing()
    views_chrome = 2 * line + em_size(1)  # the legend and the zoom buttons
    if avail.x < em_size(NARROW_WIDTH_EM):  # a phone: one view at a time, then the controls
        pinned = avail.y >= em_size(PINNED_MIN_HEIGHT_EM)  # the viewer stays, the controls scroll under it
        size = min(avail.x, avail.y * PINNED_VIEW_SHARE if pinned else em_size(40))
        if pinned:
            imgui.begin_child("viewer", ImVec2(0, 2 * line + size + views_chrome))
        gui_ct_switch(v, narrow=True)
        gui_one_view(v, avail.x, size, narrow=True)
        if pinned:  # the slider at the viewer's bottom, whatever the view: it stays under the finger
            imgui.set_cursor_pos_y(imgui.get_window_height() - imgui.get_frame_height())
        gui_slice(v)
        if pinned:
            imgui.end_child()
            imgui.begin_child("controls")
        imgui.separator_text("Window")
        gui_window(v)
        imgui.separator_text("Segmentation")
        gui_segmentation(v)
        gui_ct_credit()
        if pinned:
            imgui.end_child()
        return

    # The controls at the left: the segmentation and the region in 3D (unless the viewer shows it, larger)
    imgui.begin_child("controls", ImVec2(em_size(CONTROLS_WIDTH_EM), 0))
    imgui.separator_text("Segmentation")
    gui_segmentation(v)
    if v.view != "3D":
        imgui.separator_text("In 3D")
        gui_3d(v, max(imgui.get_content_region_avail().y, em_size(14)))
    imgui.end_child()
    imgui.same_line()

    # The views, the slider under them (it moves the views and the plane in 3D at once), the window, and the credit
    imgui.begin_group()
    gui_ct_switch(v, narrow=False)
    below_views = 4 * line + em_size(HISTOGRAM_HEIGHT_EM) + 2 * imgui.get_text_line_height_with_spacing()
    max_height = imgui.get_content_region_avail().y - below_views - views_chrome
    if v.view == "Both":
        gui_views(v, imgui.get_content_region_avail().x, max_height, narrow=False)
    else:
        gui_one_view(v, imgui.get_content_region_avail().x, max_height, narrow=False)
    gui_slice(v)
    imgui.separator_text("Window")
    gui_window(v)
    gui_ct_credit()
    imgui.end_group()


# ======================================================================================================================
# The retina
# ======================================================================================================================
# ::code Skeleton
def thin(mask: Mask) -> Mask:
    """The mask's skeleton, one pixel wide (Zhang and Suen's thinning): its border pixels are peeled, in two
    alternating passes, as long as removing one neither cuts a line nor shortens its end"""
    img = mask.astype(np.uint8)
    changed = True
    while changed:
        changed = False
        for first_pass in (True, False):
            p = np.pad(img, 1)
            # The 8 neighbors, clockwise from the top: P2, P3, ... P9
            n = [p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:], p[2:, 2:], p[2:, 1:-1], p[2:, :-2], p[1:-1, :-2], p[:-2, :-2]]
            count = sum(q.astype(np.int32) for q in n)
            transitions = sum(((n[i] == 0) & (n[(i + 1) % 8] == 1)).astype(np.int32) for i in range(8))
            p2, p4, p6, p8 = n[0], n[2], n[4], n[6]
            if first_pass:
                keeps_shape = (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                keeps_shape = (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            remove = (img == 1) & (count >= 2) & (count <= 6) & (transitions == 1) & keeps_shape
            if remove.any():
                img[remove] = 0
                changed = True
    return img.astype(bool)
# ::endcode


def skeleton_neighbors(skeleton: Mask) -> NDArray[np.int32]:
    """For each pixel of the skeleton, how many of its 8 neighbors are in it (1: an end, 3 or more: a branching)"""
    kernel = np.ones((3, 3), np.float32)
    kernel[1, 1] = 0
    count = cv2.filter2D(skeleton.astype(np.float32), -1, kernel, borderType=cv2.BORDER_CONSTANT)
    return (count * skeleton).astype(np.int32)


@dataclass
class Segment:
    """A vessel's stretch between two branchings: its skeleton's pixels, and its measures (in pixels)"""
    ys: NDArray[np.intp]
    xs: NDArray[np.intp]
    length: float
    width: float = -1.0  # at half height, measured when needed (-1: not yet)


def vessel_segments(vessels: Mask, spur_px: int = 12) -> Tuple[NDArray[np.int32], List[Segment]]:
    """The vessels' skeleton, cut at its branchings into segments; the short spurs (a segment with a free end, under
    spur_px) are dropped first. Returns the segments, and an image of their numbers (0: none, i + 1: segments[i])."""
    skeleton = thin(vessels)
    for _ in range(2):
        neighbors = skeleton_neighbors(skeleton)
        cut = skeleton & ~cv2.dilate((neighbors >= 3).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(cut.astype(np.uint8), connectivity=8)
        spurs = [i for i in np.unique(labels[(neighbors == 1) & cut]) if i and stats[i, cv2.CC_STAT_AREA] < spur_px]
        if not spurs:
            break
        skeleton &= ~np.isin(labels, spurs)
    # The segments' pixels, in one pass; their lengths from the links between neighbors: 1 for a step to a side,
    # 1.41 for a diagonal one
    ys, xs = np.nonzero(labels)
    order = np.argsort(labels[ys, xs], kind="stable")
    ys, xs = ys[order], xs[order]
    starts = np.searchsorted(labels[ys, xs], np.arange(1, count + 1))
    length = np.zeros(count)
    for a, b, step in ((labels[:, 1:], labels[:, :-1], 1.0), (labels[1:, :], labels[:-1, :], 1.0),
                       (labels[1:, 1:], labels[:-1, :-1], 1.41), (labels[1:, :-1], labels[:-1, 1:], 1.41)):
        same = (a == b) & (a > 0)
        length += step * np.bincount(a[same], minlength=count)[:count]
    segments = [Segment(ys[starts[i - 1] : starts[i]], xs[starts[i - 1] : starts[i]], float(length[i]))
                for i in range(1, count)]
    return labels.astype(np.int32), segments


# ::code Width
def half_height_width(tophat: NDArray[np.float32], seg: Segment) -> float:
    """The vessel's width at half height: at each pixel of its skeleton, the top-hat's profile across the vessel
    (the vessels are bright there), and the span where it stays above half of its peak. Their median."""
    points = np.stack([seg.xs, seg.ys], 1).astype(np.float32)
    offsets = np.arange(-15, 15.01, 0.5, dtype=np.float32)  # along the profile, in pixels
    middle = len(offsets) // 2
    widths = []
    for p in points:
        near = points[np.sum((points - p) ** 2, 1) <= 16] - p  # the skeleton around p: its direction
        if len(near) < 3:
            continue
        tangent = np.linalg.eigh(near.T @ near)[1][:, -1]
        across = np.array([-tangent[1], tangent[0]], np.float32)
        xs, ys = p[0] + offsets * across[0], p[1] + offsets * across[1]
        profile = cv2.remap(tophat, xs[None, :], ys[None, :], cv2.INTER_LINEAR)[0]
        peak = middle - 4 + int(np.argmax(profile[middle - 4 : middle + 5]))
        half = profile[peak] / 2
        lo, hi = peak, peak
        while lo > 0 and profile[lo] > half:
            lo -= 1
        while hi < len(offsets) - 1 and profile[hi] > half:
            hi += 1
        if profile[peak] <= 0 or lo == 0 or hi == len(offsets) - 1:
            continue  # no vessel there, or wider than the profile
        left = offsets[lo] + 0.5 * (half - profile[lo]) / (profile[lo + 1] - profile[lo])  # the crossings, interpolated
        right = offsets[hi - 1] + 0.5 * (profile[hi - 1] - half) / (profile[hi - 1] - profile[hi])
        widths.append(right - left)
    return float(np.median(widths)) if widths else float("nan")
# ::endcode


class RetinaViewer:
    """The fundus photograph, the vessel pipeline's parameters, its stages, and the view of one of them"""

    def __init__(self) -> None:
        bgr = cv2.imdecode(np.frombuffer(DATA.read("fundus_left_eye.jpg"), np.uint8), cv2.IMREAD_COLOR)
        self.rgb: NDArray[np.uint8] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)  # type: ignore
        # The field of view: the lit disc (its red channel), its rim eroded (the edge would read as a vessel)
        self.fov = cv2.erode((self.rgb[:, :, 0] > 30).astype(np.uint8), np.ones((15, 15), np.uint8))
        self.clahe_clip = 2.5  # how much the local contrast may grow
        self.tophat_size = 17  # pixels: the widest vessel the top-hat keeps
        self.threshold = 20  # on the top-hat
        self.min_area = 100  # pixels: the smaller blobs are dropped
        self.stage = "Vessels"
        self.original_params = image_params("retina", "None", show_pixel_info=False)
        self.processed_params = image_params("retina", "None", show_pixel_info=False)
        self.processed = self.rgb
        self.vessel_fraction = 0.0
        self.vessels: Mask = np.zeros(self.rgb.shape[:2], bool)
        self.tophat_raw: NDArray[np.float32] = np.zeros(self.rgb.shape[:2], np.float32)  # for the widths
        # The measure: the segments, their numbers' image, the numbered ones (the largest), the one selected
        self.segment_labels: NDArray[np.int32] = np.zeros(self.rgb.shape[:2], np.int32)
        self.segments: List[Segment] = []
        self.numbered: List[int] = []
        self.selected: Optional[int] = None
        self.measure_pending = False  # the segments wait until the knob is released (the skeleton takes a while)
        self.click = ViewClick()
        self.view = "Both"  # the viewer's switch
        self.stages_height = 0.0  # the stage buttons under the views, as last drawn
        self.run()

    def run(self, with_measure: bool = True) -> None:
        """The pipeline, then the view of the chosen stage (the measure's segments: if with_measure)"""
        # ::code Vessels
        green = self.rgb[:, :, 1]  # where the vessels contrast most
        clahe = cv2.createCLAHE(clipLimit=self.clahe_clip, tileGridSize=(8, 8)).apply(green)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.tophat_size, self.tophat_size))
        raw = cv2.morphologyEx(clahe, cv2.MORPH_BLACKHAT, kernel)  # the dark details, thinner than the kernel
        tophat = cv2.GaussianBlur(raw, (3, 3), 0) * self.fov
        count, labels, stats, _ = cv2.connectedComponentsWithStats((tophat > self.threshold).astype(np.uint8))
        keep = stats[:, cv2.CC_STAT_AREA] >= self.min_area
        keep[0] = False  # the background
        vessels = keep[labels]
        # ::endcode
        self.vessel_fraction = float(vessels.sum()) / float(self.fov.sum())
        self.vessels, self.tophat_raw = vessels, (raw * self.fov).astype(np.float32)
        self.segments, self.numbered, self.selected = [], [], None
        self.measure_pending = self.stage == "Measure" and not with_measure
        if self.stage == "Measure" and with_measure:
            self.measure()

        if self.stage == "Measure":
            view = self.measure_view()
        elif self.stage == "Overlay":
            view = (self.rgb * 0.55).astype(np.uint8)
            view[vessels] = OVERLAY_RGB
        else:
            gray = {
                "Green channel": green,
                "CLAHE": clahe,
                "Top-hat": (tophat * (255.0 / max(int(tophat.max()), 1))).astype(np.uint8),  # the dark lines, bright
                "Vessels": vessels.astype(np.uint8) * 255,
            }[self.stage]
            view = np.repeat(gray[:, :, None], 3, axis=2)
        self.processed = np.ascontiguousarray(view)
        self.processed_params.refresh_image = True

    # The measure
    def measure(self) -> None:
        """The segments, and the widths of the largest ones, which get a number"""
        self.segment_labels, self.segments = vessel_segments(self.vessels)
        dist = cv2.distanceTransform(self.vessels.astype(np.uint8), cv2.DIST_L2, 5)
        size = [s.length * float(np.median(dist[s.ys, s.xs])) for s in self.segments]
        self.numbered = [int(i) for i in np.argsort(size)[::-1][:NUMBERED_SEGMENTS]]
        for i in self.numbered:
            self.segments[i].width = half_height_width(self.tophat_raw, self.segments[i])

    def select(self, x: int, y: int) -> None:
        """The segment nearest to a click (within 12 pixels), measured"""
        y0, y1, x0, x1 = max(y - 12, 0), y + 13, max(x - 12, 0), x + 13
        window = self.segment_labels[y0:y1, x0:x1]
        ys, xs = np.nonzero(window)
        if len(ys) == 0:
            self.selected = None
        else:
            nearest = int(np.argmin((ys + y0 - y) ** 2 + (xs + x0 - x) ** 2))
            self.selected = int(window[ys[nearest], xs[nearest]]) - 1
            if self.segments[self.selected].width < 0:
                self.segments[self.selected].width = half_height_width(self.tophat_raw, self.segments[self.selected])
        self.processed = np.ascontiguousarray(self.measure_view())
        self.processed_params.refresh_image = True

    def measure_view(self) -> NDArray[np.uint8]:
        """The photograph, dimmed; the vessels, faint; the skeleton; the numbered segments, the selected one in
        yellow; the optic disc, the measures' scale, as a circle"""
        view = (self.rgb * 0.4).astype(np.uint8)
        view[self.vessels] = (30, 70, 95)
        view[self.segment_labels > 0] = (90, 140, 170)
        for rank, i in enumerate(self.numbered):
            s = self.segments[i]
            for y, x in zip(s.ys, s.xs, strict=True):  # thicker than the skeleton, to be seen at a glance
                cv2.circle(view, (int(x), int(y)), 2 if i == self.selected else 1, NUMBERED_RGB, -1)
            mid = len(s.ys) // 2
            at = (int(s.xs[mid]) + 6, int(s.ys[mid]) - 6)
            for thickness, text_color in ((4, (0, 0, 0)), (1, (255, 255, 255))):  # the number, outlined
                cv2.putText(view, str(rank + 1), at, cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, thickness, cv2.LINE_AA)
        if self.selected is not None:
            s = self.segments[self.selected]
            for y, x in zip(s.ys, s.xs, strict=True):
                cv2.circle(view, (int(x), int(y)), 2, SEED_RGB, -1)
        cv2.circle(view, DISC_CENTER_PX, DISC_DIAMETER_PX // 2, SEED_RGB, 1, cv2.LINE_AA)
        return view

    def describe(self, i: int) -> str:
        """The measures of a segment, as markdown"""
        s = self.segments[i]
        um_per_px = DISC_DIAMETER_MM * 1000 / DISC_DIAMETER_PX
        cx, cy = float(np.mean(s.xs)), float(np.mean(s.ys))
        distance = np.hypot(cx - DISC_CENTER_PX[0], cy - DISC_CENTER_PX[1]) / DISC_DIAMETER_PX
        # On this photograph of a left eye, the temporal side (toward the macula) is at the right, the superior up
        vertical, horizontal = ("supero" if cy < DISC_CENTER_PX[1] else "infero"), cx > DISC_CENTER_PX[0]
        quadrant = vertical + ("temporal" if horizontal else "nasal")
        number = f"Segment {self.numbered.index(i) + 1}" if i in self.numbered else "This segment"
        return (f"**{number}**\n\n"
                f"- Width at half height: {s.width:.1f} px, about {s.width * um_per_px:.0f} µm\n"
                f"- Length: {s.length:.0f} px, about {s.length * um_per_px / 1000:.1f} mm\n"
                f"- Position: {distance:.1f} disc diameters from the disc's center, {quadrant}")


RETINA: Optional[RetinaViewer] = None


def retina_viewer() -> RetinaViewer:
    global RETINA
    if RETINA is None:
        RETINA = RetinaViewer()
    return RETINA


def gui_retina_controls(r: RetinaViewer) -> None:
    text_with_help("Classic image processing, no learning: the green channel, then:", "Green channel")
    size, knob = em_size(3.4), imgui_knobs.ImGuiKnobVariant_.wiper_dot
    takes_drags = hello_imgui.set_item_takes_touch_drags  # on a touch screen, a drag on a knob turns it at once

    def knob_column(topic: str, draw_knob: Callable[[], Tuple[bool, T]]) -> Tuple[bool, T]:
        """A knob, and its (i) centered under it (an imgui_kit column)"""
        with imgui_kit.column(topic):
            result = draw_knob()
            takes_drags(long_press_is_right_click=False)
            with imgui_kit.aligned_group("help", 0.5):
                imgui_kit.help_marker(help_text(topic))
        imgui.same_line()
        return result

    changed, r.clahe_clip = knob_column(
        "CLAHE", lambda: imgui_knobs.knob("CLAHE", r.clahe_clip, 1.0, 6.0, 0.02, "%.1f", knob, size))
    c, size_px = knob_column(
        "Top-hat", lambda: imgui_knobs.knob_int("Top-hat", r.tophat_size, 5, 41, 0.15, "%d px", knob, size))
    if size_px % 2 == 0:  # odd: the kernel has a center; rounded the way the knob turns
        size_px += 1 if size_px > r.tophat_size else -1
    r.tophat_size, changed = size_px, changed or c
    c, r.threshold = knob_column(
        "Threshold", lambda: imgui_knobs.knob_int("Threshold", r.threshold, 1, 60, 0.2, "%d", knob, size))
    changed |= c
    c, r.min_area = knob_column(
        "Min. area", lambda: imgui_knobs.knob_int("Min. area", r.min_area, 0, 400, 1.0, "%d px", knob, size))
    changed |= c
    imgui.new_line()
    dragging = imgui.is_any_item_active()  # a knob held: the measure's segments wait for its release
    if changed or (r.measure_pending and not dragging):
        r.run(with_measure=not dragging)
    imgui.text(f"Vessels: {100 * r.vessel_fraction:.1f} % of the field of view")
    help_marker("Vessels' share")
    if r.stage == "Measure":
        gui_measure(r)


def gui_measure(r: RetinaViewer) -> None:
    imgui.separator_text("Measure")
    text_with_help("Click a vessel in either view, or a number below.", "Measure")
    if r.measure_pending:
        imgui.text_disabled("Measuring...")
        return
    for rank, i in enumerate(r.numbered):
        if rank > 0:
            imgui.same_line()
        if imgui.small_button(f"{rank + 1}") and r.segments:
            s = r.segments[i]
            r.select(int(s.xs[len(s.xs) // 2]), int(s.ys[len(s.ys) // 2]))
    if r.selected is not None:
        rich_md.render(r.describe(r.selected))


def gui_retina_credit() -> None:
    imgui.push_text_wrap_pos(0)
    imgui.text_disabled("Fundus photograph of a normal left eye: Mikael Häggström, Wikimedia Commons, CC0.")
    imgui.pop_text_wrap_pos()
    url = "https://commons.wikimedia.org/wiki/File:Fundus_photograph_of_normal_left_eye.jpg"
    imgui.text_link_open_url("commons.wikimedia.org: the photograph", url)


def gui_stages(r: RetinaViewer) -> None:
    """The stage the processed view shows: a row of buttons, which wraps on a phone"""
    y = imgui.get_cursor_pos_y()
    clicked = gui_buttons(STAGES, r.stage)
    help_marker("Stages")
    r.stages_height = imgui.get_cursor_pos_y() - y  # the views leave it room at the next frame
    if clicked is not None:
        r.stage = clicked
        r.run()


def gui_retina_views(r: RetinaViewer, width: float, max_size: float, narrow: bool) -> None:
    """The photograph and the processed view, side by side, or the one chosen in the switch, alone (centered on a
    phone); under the processed view, the stage buttons. max_size includes the buttons."""
    with_stages = r.view != "Photograph"
    if with_stages:
        max_size -= r.stages_height
    params = (r.original_params, r.processed_params)
    if r.view == "Both":
        fit_views(params, width, max_size)
    else:
        set_views_size(params, min(width - imgui.get_frame_height(), max_size))
    clicks = []
    if r.view != "Processed":
        with centered_on_phone("retina_photograph", narrow):
            immvision.image("Fundus photograph##retina", r.rgb, r.original_params)
        clicks.append(r.click.take("original", r.original_params))
    if r.view == "Both":
        imgui.same_line()
    if r.view != "Photograph":
        stages_x = imgui.get_cursor_pos_x()  # the stage buttons start here (on a phone, at the left: they wrap)
        with centered_on_phone("retina_processed", narrow):
            immvision.image(f"{r.stage}##retina_processed", r.processed, r.processed_params)
        clicks.append(r.click.take("processed", r.processed_params))
        r.processed_params.refresh_image = False
    for clicked in clicks:
        if clicked is not None and r.stage == "Measure" and r.segments:
            r.select(*clicked)
    if with_stages:
        imgui.set_cursor_pos_x(stages_x)
        gui_stages(r)


def gui_retina(r: RetinaViewer) -> None:
    gui_intro("Retina")
    avail = imgui.get_content_region_avail()
    views_chrome = 2 * imgui.get_frame_height_with_spacing() + em_size(1)  # the legend and the zoom buttons
    switch_height = imgui.get_frame_height_with_spacing()
    if avail.x < em_size(NARROW_WIDTH_EM):  # a phone: one view at a time, then the controls
        pinned = avail.y >= em_size(PINNED_MIN_HEIGHT_EM)  # the viewer stays, the controls scroll under it
        size = min(avail.x, avail.y * PINNED_VIEW_SHARE if pinned else em_size(40))
        if pinned:
            imgui.begin_child("retina_viewer", ImVec2(0, switch_height + size + views_chrome))
        _, r.view = gui_view_switch(RETINA_VIEWS, r.view, narrow=True)
        gui_retina_views(r, avail.x, size, narrow=True)
        if pinned:
            imgui.end_child()
            imgui.begin_child("retina_controls")
        imgui.separator_text("Vessels")
        gui_retina_controls(r)
        gui_retina_credit()
        if pinned:
            imgui.end_child()
        return

    imgui.begin_child("retina_controls", ImVec2(em_size(CONTROLS_WIDTH_EM), 0))
    imgui.separator_text("Vessels")
    gui_retina_controls(r)
    imgui.dummy(ImVec2(0, em_size(1)))
    gui_retina_credit()
    imgui.end_child()
    imgui.same_line()
    imgui.begin_group()
    _, r.view = gui_view_switch(RETINA_VIEWS, r.view, narrow=False)
    gui_retina_views(r, imgui.get_content_region_avail().x, imgui.get_content_region_avail().y - views_chrome,
                     narrow=False)
    imgui.end_group()


# ======================================================================================================================
# How it works: the help file, as a document, beside its source
# ======================================================================================================================
SHOW_SOURCE = [False]  # the markdown source beside the document


def gui_how_it_works() -> None:
    _, SHOW_SOURCE[0] = imgui.checkbox("Show the source of this page, medical_imaging_help.md", SHOW_SOURCE[0])
    avail = imgui.get_content_region_avail()
    beside = SHOW_SOURCE[0] and avail.x >= em_size(NARROW_WIDTH_EM)
    if SHOW_SOURCE[0]:
        size = ImVec2(avail.x / 2 - imgui.get_style().item_spacing.x, 0) if beside else ImVec2(0, avail.y / 2)
        imgui.begin_child("source", size, imgui.ChildFlags_.borders)
        rich_md.render_raw("```markdown\n" + HELP_FILE.read_text(encoding="utf-8") + "\n```")  # raw: no transclusion
        imgui.end_child()
        if beside:
            imgui.same_line()
    rich_md.begin_document("how_it_works")
    rich_md.render_file(str(HELP_FILE))  # it embeds code from this file: ![[medical_imaging.py#Window]]...
    rich_md.end_document()


def gui_header() -> None:
    imgui.push_font(None, em_size(1.35))
    imgui.text("Medical imaging")
    imgui.pop_font()
    imgui.same_line()
    disclaimer = "For research and teaching, not for diagnosis."
    if imgui.get_content_region_avail().x < imgui.calc_text_size(disclaimer).x + em_size(1):
        imgui.new_line()
    else:
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
                               - imgui.calc_text_size(disclaimer).x)
    imgui.align_text_to_frame_padding()
    imgui.text_disabled(disclaimer)


def gui() -> None:
    gui_header()
    if imgui.begin_tab_bar("##modality"):
        if imgui.begin_tab_item_simple("Chest CT"):
            if gui_data_ready():
                gui_ct(ct_viewer())
            imgui.end_tab_item()
        if imgui.begin_tab_item_simple("Retina"):
            if gui_data_ready():
                gui_retina(retina_viewer())
            imgui.end_tab_item()
        if imgui.begin_tab_item_simple("How it works"):
            gui_how_it_works()
            imgui.end_tab_item()
        imgui.end_tab_bar()


def main() -> None:
    immapp.run(gui, window_title="Medical imaging", window_size=(1300, 900), with_implot=True, with_implot3d=True,
               with_markdown=True)


if __name__ == "__main__":
    main()
