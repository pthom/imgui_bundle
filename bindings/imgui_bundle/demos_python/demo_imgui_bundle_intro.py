# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import math
from dataclasses import dataclass, field
from typing import Callable, List

import numpy as np

from imgui_bundle import imgui, imgui_md, hello_imgui, immapp, ImVec2, ImVec4
from imgui_bundle import imgui_color_text_edit as ed
from imgui_bundle import imgui_knobs, imgui_toggle
from imgui_bundle.demos_python import demo_utils
from imgui_bundle import implot3d
from imgui_bundle.immapp import icons_fontawesome_6
import webbrowser

# Optional imports (replacing #ifdef guards)
try:
    from imgui_bundle import implot
    HAS_IMPLOT = True
except ImportError:
    HAS_IMPLOT = False

try:
    from imgui_bundle import immvision
    import cv2
    HAS_IMMVISION = True
except ImportError:
    HAS_IMMVISION = False

try:
    import OpenGL.GL as GL
    import ctypes
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False


# ============================================================================
# Test engine automation (unchanged from old file)
# ============================================================================

def automation_show_me_immediate_apps():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(
        engine, "Automation", "ShowMeImmediateApps"
    )

    def test_func(ctx):
        tab_imm_apps_name = "//**/Demo Apps"
        tab_intro_name = "//**/Intro"
        ctx.mouse_move(tab_imm_apps_name)
        ctx.mouse_click(0)
        ctx.item_click("//**/demo_docking/View code")
        ctx.item_click("//**/demo_assets_addons/View code")
        ctx.item_click("//**/demo_hello_world/View code")
        ctx.mouse_move("//**/demo_hello_world/Run")
        ctx.mouse_move(tab_intro_name)
        ctx.mouse_click(0)

    automation.test_func = test_func
    return automation


# ============================================================================
# Carousel infrastructure
# ============================================================================

@dataclass
class CarouselSlide:
    title: str
    description: str
    gui_func: Callable[[ImVec2], None]


def smooth_damp(current: float, target: float, speed: float, dt: float) -> float:
    """Exponential smoothing: approaches target with a given speed (higher = faster)."""
    return current + (target - current) * (1.0 - math.exp(-speed * dt))


def draw_side_panel(panel_id: str, width: float, height: float, draw_widgets: Callable[[], None]):
    """Draw a colored rounded-rect background, then run draw_widgets inside a child window."""
    em = hello_imgui.em_size()
    panel_pos = imgui.get_cursor_screen_pos()
    dl = imgui.get_window_draw_list()

    accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    bg = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.08))
    border = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.3))
    rounding = em * 0.4

    dl.add_rect_filled(panel_pos, ImVec2(panel_pos.x + width, panel_pos.y + height), bg, rounding)
    dl.add_rect(panel_pos, ImVec2(panel_pos.x + width, panel_pos.y + height), border, rounding, 0, 1.5)

    imgui.begin_child(panel_id, ImVec2(width, height), False,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
    pad = em * 0.5
    imgui.set_cursor_pos(ImVec2(pad, pad))
    imgui.push_item_width((width - pad * 2.0) * 0.5)
    draw_widgets()
    imgui.pop_item_width()
    imgui.end_child()


# ============================================================================
# Slide 1: Lorenz — ImPlot3D attractor with dual trajectories
# ============================================================================

@dataclass
class LorenzParams:
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0
    dt: float = 0.01
    max_size: int = 2000


class AnimatedLorenzTrajectory:
    def __init__(self, x: float, y: float, z: float):
        self.xs = [x]
        self.ys = [y]
        self.zs = [z]

    def step(self, params: LorenzParams):
        x, y, z = self.xs[-1], self.ys[-1], self.zs[-1]
        dx = params.sigma * (y - x)
        dy = x * (params.rho - z) - y
        dz = x * y - params.beta * z
        x += dx * params.dt
        y += dy * params.dt
        z += dz * params.dt
        self.xs.append(x)
        self.ys.append(y)
        self.zs.append(z)
        if len(self.xs) > params.max_size:
            self.xs.pop(0)
            self.ys.pop(0)
            self.zs.pop(0)


# Module-level state for Lorenz
_lorenz_params = LorenzParams()
_lorenz_traj1: AnimatedLorenzTrajectory = None  # type: ignore
_lorenz_traj2: AnimatedLorenzTrajectory = None  # type: ignore
_lorenz_inited = False
_lorenz_initial_delta = 0.1


def _lorenz_init_trajectories():
    global _lorenz_traj1, _lorenz_traj2, _lorenz_inited
    _lorenz_traj1 = AnimatedLorenzTrajectory(0.0, 1.0, 1.05)
    _lorenz_traj2 = AnimatedLorenzTrajectory(0.0 + _lorenz_initial_delta, 1.0, 1.05)
    _lorenz_inited = True


def _lorenz_gui_main(plot_size: ImVec2):
    global _lorenz_inited
    if not _lorenz_inited:
        _lorenz_init_trajectories()

    if implot3d.begin_plot("Lorenz##intro", plot_size):
        implot3d.setup_axes("X", "Y", "Z",
                            implot3d.AxisFlags_.auto_fit,
                            implot3d.AxisFlags_.auto_fit,
                            implot3d.AxisFlags_.auto_fit)
        xs1 = np.array(_lorenz_traj1.xs, dtype=np.float64)
        ys1 = np.array(_lorenz_traj1.ys, dtype=np.float64)
        zs1 = np.array(_lorenz_traj1.zs, dtype=np.float64)
        implot3d.plot_line("Trajectory", xs1, ys1, zs1)
        xs2 = np.array(_lorenz_traj2.xs, dtype=np.float64)
        ys2 = np.array(_lorenz_traj2.ys, dtype=np.float64)
        zs2 = np.array(_lorenz_traj2.zs, dtype=np.float64)
        implot3d.plot_line("Trajectory2", xs2, ys2, zs2)
        implot3d.end_plot()
    _lorenz_traj1.step(_lorenz_params)
    _lorenz_traj2.step(_lorenz_params)


def _lorenz_gui_side():
    global _lorenz_initial_delta
    imgui.text_disabled("Butterfly Effect")
    imgui.set_item_tooltip(
        "Tiny changes in initial conditions lead to\n"
        "completely different trajectories \u2014\n"
        "the hallmark of deterministic chaos.")
    imgui.spacing()
    _, _lorenz_params.sigma = imgui.slider_float("Sigma", _lorenz_params.sigma, 0.0, 100.0)
    imgui.set_item_tooltip("Rate of divergence (chaos level)")
    _, _lorenz_params.rho = imgui.slider_float("Rho", _lorenz_params.rho, 0.0, 100.0)
    imgui.set_item_tooltip("Size and shape of the attractor")
    _, _lorenz_params.beta = imgui.slider_float("Beta", _lorenz_params.beta, 0.0, 10.0)
    imgui.set_item_tooltip("Damping on vertical movement")
    _, _lorenz_params.dt = imgui.slider_float("dt", _lorenz_params.dt, 0.0, 0.05)
    imgui.set_item_tooltip("Time step (smaller = smoother)")
    _, _lorenz_initial_delta = imgui.slider_float("Delta", _lorenz_initial_delta, 0.0, 0.2)
    imgui.set_item_tooltip("Initial difference between trajectories")
    if imgui.button("Reset"):
        _lorenz_init_trajectories()


def _lorenz_slide_gui(content_size: ImVec2):
    em = hello_imgui.em_size()
    main_side = content_size.y
    gap = em * 0.5
    side_panel_w = content_size.x - main_side - gap

    _lorenz_gui_main(ImVec2(main_side, main_side))

    if side_panel_w > em * 4.0:
        imgui.same_line(0.0, gap)
        draw_side_panel("##lorenz_side", side_panel_w, main_side, _lorenz_gui_side)


# ============================================================================
# Slide 2: Telemetry — ImPlot subplots with scrolling signals
# ============================================================================

if HAS_IMPLOT:
    class _TelemetryChannel:
        def __init__(self, max_size: int = 2000):
            self.times: List[float] = []
            self.values: List[float] = []
            self.max_size = max_size

        def add_point(self, t: float, v: float):
            self.times.append(t)
            self.values.append(v)
            if len(self.times) > self.max_size:
                self.times.pop(0)
                self.values.pop(0)

    _telemetry_channels = [_TelemetryChannel() for _ in range(4)]
    _telemetry_time = 0.0
    _telemetry_speed = 20.0
    _telemetry_paused = False
    _telemetry_history = 10.0

    def _pseudo_noise(t: float) -> float:
        return math.sin(t * 37.1) * math.sin(t * 53.7)

    def _telemetry_update():
        global _telemetry_time
        if _telemetry_paused:
            return
        dt = imgui.get_io().delta_time * _telemetry_speed
        _telemetry_time += dt
        pi = math.pi
        t = _telemetry_time
        _telemetry_channels[0].add_point(t, math.sin(2.0 * pi * 0.5 * t))
        _telemetry_channels[1].add_point(t, 0.5 * math.sin(2.0 * pi * 0.3 * t) + 0.3 * _pseudo_noise(t))
        _telemetry_channels[2].add_point(t, 1.0 if math.sin(2.0 * pi * 0.4 * t) > 0.0 else -1.0)
        _telemetry_channels[3].add_point(t, 0.6 * math.sin(2.0 * pi * 0.7 * t) + 0.3 * math.sin(2.0 * pi * 2.3 * t))

    def _telemetry_gui_main(plot_size: ImVec2):
        _telemetry_update()

        labels = ["Voltage", "Pressure", "Digital", "Vibration"]
        colors = [
            ImVec4(0.2, 0.9, 0.4, 1.0),
            ImVec4(0.3, 0.6, 1.0, 1.0),
            ImVec4(1.0, 0.6, 0.1, 1.0),
            ImVec4(0.9, 0.3, 0.6, 1.0),
        ]

        sub_flags = implot.SubplotFlags_.link_all_x | implot.SubplotFlags_.no_resize
        if implot.begin_subplots("##Telemetry", 2, 2, plot_size, sub_flags):
            for i in range(4):
                if implot.begin_plot(labels[i], ImVec2(), implot.Flags_.no_legend):
                    implot.setup_axes("", "",
                                      implot.AxisFlags_.no_tick_labels,
                                      implot.AxisFlags_.auto_fit)
                    implot.setup_axis_limits(implot.ImAxis_.x1,
                                             _telemetry_time - _telemetry_history,
                                             _telemetry_time,
                                             implot.Cond_.always)
                    ch = _telemetry_channels[i]
                    if len(ch.times) > 0:
                        times_arr = np.array(ch.times, dtype=np.float64)
                        values_arr = np.array(ch.values, dtype=np.float64)
                        spec = implot.Spec()
                        spec.line_color = colors[i]
                        implot.plot_line(labels[i], times_arr, values_arr, spec)
                    implot.end_plot()
            implot.end_subplots()

    def _telemetry_gui_side():
        global _telemetry_paused, _telemetry_speed, _telemetry_history
        _, _telemetry_paused = imgui.checkbox("Pause", _telemetry_paused)
        _, _telemetry_speed = imgui.slider_float("Speed", _telemetry_speed, 0.5, 40.0)
        _, _telemetry_history = imgui.slider_float("History", _telemetry_history, 2.0, 20.0, "%.0f s")

    def _telemetry_slide_gui(content_size: ImVec2):
        em = hello_imgui.em_size()
        main_side = content_size.y
        gap = em * 0.5
        side_panel_w = content_size.x - main_side - gap

        _telemetry_gui_main(ImVec2(main_side, main_side))

        if side_panel_w > em * 4.0:
            imgui.same_line(0.0, gap)
            draw_side_panel("##telemetry_side", side_panel_w, main_side, _telemetry_gui_side)


# ============================================================================
# Slide 3: Angled Headers Table — drum sequencer
# ============================================================================

_table_instruments = ["kick", "snare", "hihat", "open-hh", "tom", "clap", "rim", "crash"]
_table_num_instr = 8
_table_num_beats = 8
_table_pattern: List[List[bool]] = []
_table_inited = False
_table_playhead = 0
_table_bpm = 140.0
_table_playing = True
_table_accum = 0.0
_table_hl_color = ImVec4(0.3, 0.5, 1.0, 0.25)


def _table_init():
    global _table_pattern, _table_inited
    _table_pattern = [[False] * _table_num_instr for _ in range(_table_num_beats)]
    _table_pattern[0][0] = _table_pattern[4][0] = True   # kick
    _table_pattern[2][1] = _table_pattern[6][1] = True   # snare
    for i in range(0, _table_num_beats, 2):
        _table_pattern[i][2] = True                        # hihat
    _table_pattern[1][3] = _table_pattern[5][3] = True    # open-hh
    _table_pattern[3][4] = True                            # tom
    _table_pattern[6][5] = True                            # clap
    _table_pattern[4][6] = _table_pattern[7][6] = True    # rim
    _table_pattern[0][7] = True                            # crash
    _table_inited = True


def _table_update():
    global _table_playhead, _table_accum
    if not _table_playing:
        return
    _table_accum += imgui.get_io().delta_time
    beat_interval = 60.0 / _table_bpm
    if _table_accum >= beat_interval:
        _table_accum -= beat_interval
        _table_playhead = (_table_playhead + 1) % _table_num_beats


def _table_gui_main(size: ImVec2):
    global _table_inited
    if not _table_inited:
        _table_init()
    _table_update()

    total_cols = _table_num_instr + 1
    flags = (imgui.TableFlags_.sizing_fixed_fit
             | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y
             | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_inner_h
             | imgui.TableFlags_.highlight_hovered_column)

    if imgui.begin_table("##drum_seq", total_cols, flags, size):
        imgui.table_setup_column("Beat", imgui.TableColumnFlags_.no_hide)
        for n in range(_table_num_instr):
            imgui.table_setup_column(
                _table_instruments[n],
                imgui.TableColumnFlags_.angled_header | imgui.TableColumnFlags_.width_fixed)
        imgui.table_setup_scroll_freeze(1, 2)

        imgui.table_angled_headers_row()
        imgui.table_headers_row()

        hl_col = imgui.color_convert_float4_to_u32(_table_hl_color)

        for row in range(_table_num_beats):
            imgui.push_id(row)
            imgui.table_next_row()

            is_playhead = (row == _table_playhead) and _table_playing

            imgui.table_set_column_index(0)
            if is_playhead:
                imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, hl_col)
            imgui.align_text_to_frame_padding()
            imgui.text(str(row + 1))

            for col in range(_table_num_instr):
                if imgui.table_set_column_index(col + 1):
                    if is_playhead:
                        imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, hl_col)
                    imgui.push_id(col)
                    _, _table_pattern[row][col] = imgui.checkbox("", _table_pattern[row][col])
                    imgui.pop_id()
            imgui.pop_id()
        imgui.end_table()


def _table_gui_side():
    global _table_playing, _table_bpm, _table_hl_color
    em = hello_imgui.em_size()

    # Play/Pause
    imgui.text("Play")
    toggle_config = imgui_toggle.material_style()
    toggle_config.size = ImVec2(em * 2.5, em * 1.2)
    _, _table_playing = imgui_toggle.toggle("##play", _table_playing, toggle_config)

    # BPM
    imgui.spacing()
    imgui.text("Tempo")
    accent = imgui.get_style_color_vec4(imgui.Col_.slider_grab)
    imgui.push_style_color(imgui.Col_.frame_bg, ImVec4(accent.x, accent.y, accent.z, 0.4))
    imgui.push_style_color(imgui.Col_.frame_bg_hovered, ImVec4(accent.x, accent.y, accent.z, 0.6))
    imgui.push_style_color(imgui.Col_.frame_bg_active, ImVec4(accent.x, accent.y, accent.z, 0.8))
    _, _table_bpm = imgui_knobs.knob(
        "##bpm", _table_bpm, 60.0, 300.0, 0.0, "%.0f",
        imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        em * 3.5, imgui_knobs.ImGuiKnobFlags_.always_clamp)
    imgui.pop_style_color(3)

    # Highlight color
    imgui.spacing()
    imgui.text("Highlight")
    picker_flags = (imgui.ColorEditFlags_.no_side_preview
                    | imgui.ColorEditFlags_.no_inputs
                    | imgui.ColorEditFlags_.no_label
                    | imgui.ColorEditFlags_.alpha_bar
                    | imgui.ColorEditFlags_.picker_hue_wheel)
    _, _table_hl_color = imgui.color_picker4("##hl_wheel", _table_hl_color, picker_flags)


def _table_slide_gui(content_size: ImVec2):
    em = hello_imgui.em_size()
    main_side = content_size.y
    gap = em * 0.5
    side_panel_w = content_size.x - main_side - gap

    _table_gui_main(ImVec2(main_side, main_side))

    if side_panel_w > em * 4.0:
        imgui.same_line(0.0, gap)
        draw_side_panel("##table_side", side_panel_w, main_side, _table_gui_side)


# ============================================================================
# Slide 4: ImmVision — Image debugging with animated zoom
# ============================================================================

if HAS_IMMVISION:
    _immvision_image = None
    _immvision_image_sobel = None
    _immvision_params = immvision.ImageParams()
    _immvision_params_sobel = immvision.ImageParams()
    _immvision_inited = False
    _immvision_animating = True
    _immvision_start_time = 0.0

    _immvision_blur_size = 1.25
    _immvision_deriv_order = 1
    _immvision_k_size = 7

    _ZOOM_IN_DURATION = 1.5
    _HOLD_DURATION = 1.5
    _ZOOM_OUT_DURATION = 1.5
    _PAUSE_DURATION = 1.5
    _TOTAL_CYCLE = _ZOOM_IN_DURATION + _HOLD_DURATION + _ZOOM_OUT_DURATION + _PAUSE_DURATION
    _MIN_ZOOM = 1.0
    _MAX_ZOOM = 70.0

    _immvision_zoom_center = None

    def _immvision_compute_sobel():
        gray = cv2.cvtColor(_immvision_image, cv2.COLOR_BGR2GRAY)
        img_float = gray.astype(np.float32) / 255.0
        blurred = cv2.GaussianBlur(img_float, (0, 0), _immvision_blur_size, _immvision_blur_size)
        good_scale = 1.0 / (2.0 ** (_immvision_k_size - 2 * _immvision_deriv_order - 2))
        r = cv2.Sobel(blurred, cv2.CV_64F, _immvision_deriv_order, 0, ksize=_immvision_k_size, scale=good_scale)
        return r

    def _immvision_init():
        global _immvision_image, _immvision_image_sobel, _immvision_inited
        global _immvision_zoom_center, _immvision_start_time

        immvision.use_bgr_color_order()
        _immvision_image = cv2.imread(demo_utils.demos_assets_folder() + "/images/house.jpg")
        _immvision_image_sobel = _immvision_compute_sobel()

        disp_w = int(hello_imgui.em_size(20.0))
        _immvision_params.image_display_size = (disp_w, 0)
        _immvision_params.show_options_panel = False
        _immvision_params.show_image_info = False
        _immvision_params.show_pixel_info = True
        _immvision_params.show_zoom_buttons = False
        _immvision_params.zoom_key = "intro_immvision"

        _immvision_params_sobel.image_display_size = (disp_w, 0)
        _immvision_params_sobel.show_options_panel = False
        _immvision_params_sobel.show_image_info = False
        _immvision_params_sobel.show_pixel_info = True
        _immvision_params_sobel.show_zoom_buttons = False
        _immvision_params_sobel.zoom_key = "intro_immvision"

        h, w = _immvision_image.shape[:2]
        _immvision_zoom_center = (w * 0.35, h * 0.45)
        _immvision_start_time = immapp.clock_seconds()
        _immvision_inited = True

    def _immvision_current_zoom_ratio() -> float:
        elapsed = math.fmod(immapp.clock_seconds() - _immvision_start_time, _TOTAL_CYCLE)

        if elapsed < _ZOOM_IN_DURATION:
            t = elapsed / _ZOOM_IN_DURATION
            eased = 1.0 - (1.0 - t) * (1.0 - t)
            return _MIN_ZOOM + (_MAX_ZOOM - _MIN_ZOOM) * eased
        elapsed -= _ZOOM_IN_DURATION
        if elapsed < _HOLD_DURATION:
            return _MAX_ZOOM
        elapsed -= _HOLD_DURATION
        if elapsed < _ZOOM_OUT_DURATION:
            t = elapsed / _ZOOM_OUT_DURATION
            eased = t * t
            return _MAX_ZOOM - (_MAX_ZOOM - _MIN_ZOOM) * eased
        return _MIN_ZOOM

    def _immvision_check_user_interaction() -> bool:
        hovering = (_immvision_params.mouse_info.is_mouse_hovering
                    or _immvision_params_sobel.mouse_info.is_mouse_hovering)
        if hovering and (imgui.is_mouse_dragging(0) or imgui.get_io().mouse_wheel != 0.0):
            return True
        return False

    def _immvision_gui_main(size: ImVec2):
        global _immvision_animating

        if not _immvision_inited:
            _immvision_init()

        if _immvision_animating and _immvision_check_user_interaction():
            _immvision_animating = False

        if _immvision_animating:
            zoom = _immvision_current_zoom_ratio()
            _immvision_params.zoom_pan_matrix = immvision.make_zoom_pan_matrix(
                _immvision_zoom_center, zoom, _immvision_params.image_display_size)
            _immvision_params_sobel.zoom_pan_matrix = _immvision_params.zoom_pan_matrix

        half_w = int(size.x * 0.5 - hello_imgui.em_size(1.5))
        _immvision_params.image_display_size = (half_w, 0)
        _immvision_params_sobel.image_display_size = (half_w, 0)

        immvision.image("Original##intro", _immvision_image, _immvision_params)
        imgui.same_line()
        immvision.image("Sobel##intro", _immvision_image_sobel, _immvision_params_sobel)

    def _immvision_gui_side():
        global _immvision_animating, _immvision_start_time
        global _immvision_blur_size, _immvision_deriv_order
        global _immvision_image_sobel

        imgui.text_disabled("Drag to pan, scroll to zoom")
        if not _immvision_animating:
            if imgui.button("Restart animation"):
                _immvision_animating = True
                _immvision_start_time = immapp.clock_seconds()
        imgui.separator()

        changed = False
        c, _immvision_blur_size = imgui.slider_float("Blur", _immvision_blur_size, 0.5, 10.0)
        if c:
            changed = True

        imgui.text("Deriv order:")
        for order in range(1, 5):
            imgui.same_line()
            if imgui.radio_button(str(order), _immvision_deriv_order == order):
                _immvision_deriv_order = order
                changed = True

        if changed:
            _immvision_image_sobel = _immvision_compute_sobel()
            _immvision_params_sobel.refresh_image = True

    def _immvision_slide_gui(content_size: ImVec2):
        em = hello_imgui.em_size()
        main_w = content_size.x
        main_h = content_size.y * 0.7
        gap = em * 0.5
        side_panel_h = content_size.y - main_h - gap

        _immvision_gui_main(ImVec2(main_w, main_h))

        if side_panel_h > em * 3.0:
            imgui.spacing()
            draw_side_panel("##immvision_side", main_w, side_panel_h, _immvision_gui_side)


# ============================================================================
# Slide 5: Notebook — static screenshot
# ============================================================================

def _notebook_slide_gui(content_size: ImVec2):
    img_aspect = 1680.0 / 1050.0
    w = content_size.x
    h = w / img_aspect
    if h > content_size.y:
        h = content_size.y
        w = h * img_aspect
    hello_imgui.image_from_asset("images/imgui_notebook.jpg", ImVec2(w, h))


# ============================================================================
# Slide 6: Node Editor — static screenshot
# ============================================================================

def _node_editor_slide_gui(content_size: ImVec2):
    img_aspect = 800.0 / 516.0
    link_h = imgui.get_frame_height()
    w = content_size.x
    h = w / img_aspect
    if h > content_size.y - link_h:
        h = content_size.y - link_h
        w = h * img_aspect
    hello_imgui.image_from_asset("images/node_editor_fiat.jpg", ImVec2(w, h))

    imgui_md.render_unindented("Built with [fiatlight](https://pthom.github.io/fiatlight_doc/)")


# ============================================================================
# Slide 7: Markdown — side-by-side source and rendered
# ============================================================================

_MARKDOWN_SAMPLE = """\
## Quick Start Guide

**ImGui Bundle** makes it easy to build
_beautiful_ apps with rich documentation.

Features:
- Headers, **bold**, *italic*, ~~strikethrough~~
- [Clickable links](https://github.com/pthom/imgui_bundle)
- Syntax-highlighted code blocks

```python
import imgui_bundle
imgui_md.render("# Hello!")
```

Tip: *You can resize the columns on the table below!*

| Library   | Domain          |
|-----------|-----------------|
| ImPlot    | 2D plots        |
| ImPlot3D  | 3D plots        |
| ImmVision | Image analysis  |
"""

# Markdown editor with syntax highlighting
_markdown_text_editor: ed.TextEditor = None  # type: ignore
_markdown_editor_initialized = False


def _init_markdown_editor():
    global _markdown_text_editor, _markdown_editor_initialized
    _markdown_text_editor = ed.TextEditor()
    _markdown_text_editor.set_text(_MARKDOWN_SAMPLE)
    # Use C++ language definition as a reasonable approximation for markdown
    # (it will highlight code blocks and some syntax)
    _markdown_text_editor.set_language_definition(ed.TextEditor.LanguageDefinitionId.cpp)
    _markdown_text_editor.set_palette(ed.TextEditor.PaletteId.dark)
    _markdown_editor_initialized = True


def _markdown_slide_gui(content_size: ImVec2):
    global _markdown_editor_initialized
    if not _markdown_editor_initialized:
        _init_markdown_editor()

    em = hello_imgui.em_size()
    gap = em * 0.5
    half_w = (content_size.x - gap) * 0.5
    h = content_size.y

    # Left panel: editable source with syntax highlighting
    accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    bg = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.08))
    border = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.3))
    rounding = em * 0.4

    panel_pos = imgui.get_cursor_screen_pos()
    dl = imgui.get_window_draw_list()
    dl.add_rect_filled(panel_pos, ImVec2(panel_pos.x + half_w, panel_pos.y + h), bg, rounding)
    dl.add_rect(panel_pos, ImVec2(panel_pos.x + half_w, panel_pos.y + h), border, rounding, 0, 1.5)

    imgui.begin_child("##md_source", ImVec2(half_w, h), False,
                      imgui.WindowFlags_.no_background)

    # Use code font for better readability
    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size * 0.9)

    # Render the text editor
    _markdown_text_editor.render("##md_editor", False, ImVec2(half_w, h))

    imgui.pop_font()
    imgui.end_child()

    imgui.same_line(0, gap)

    # Right panel: rendered markdown
    imgui.begin_child("##md_rendered", ImVec2(half_w, h), False, imgui.WindowFlags_.no_scrollbar)
    # Get the current text from the editor
    current_markdown = _markdown_text_editor.get_text()
    imgui_md.render_unindented(current_markdown)
    imgui.end_child()


# ============================================================================
# Slide 8: Source Code Viewer — Self-documenting demo
# ============================================================================

def _source_code_slide_gui(content_size: ImVec2):
    imgui.begin_child("##source_code", content_size, False)
    demo_utils.show_python_vs_cpp_file("demo_imgui_bundle_intro", 25)
    imgui.end_child()


# ============================================================================
# Slide 9: Web Deployment — static screenshot
# ============================================================================

def _web_deploy_slide_gui(content_size: ImVec2):
    img_aspect = 1024.0 / 768.0
    w = content_size.x
    h = w / img_aspect
    if h > content_size.y:
        h = content_size.y
        w = h * img_aspect
    hello_imgui.image_from_asset("images/bundle_playground.jpg", ImVec2(w, h))


# ============================================================================
# Slide 10: Seascape shader — FBO + OpenGL
# ============================================================================

if HAS_OPENGL:
    _VERT_SRC = """#version 100
precision mediump float;
attribute vec3 aPos;
attribute vec2 aTexCoord;
varying vec2 TexCoord;
void main() {
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
"""

    # Seascape by Alexander Alekseev aka TDM - 2014
    # https://www.shadertoy.com/view/Ms2SD1
    _FRAG_SRC = """#version 100
precision mediump float;
varying vec2 TexCoord;

uniform vec2 iResolution;
uniform float iTime;
uniform float SEA_HEIGHT;
uniform float SEA_CHOPPY;
uniform vec3 SEA_BASE;

const int NUM_STEPS = 8;
const float PI = 3.141592;
const float EPSILON = 1e-3;
#define EPSILON_NRM (0.1 / iResolution.x)

const int ITER_GEOMETRY = 3;
const int ITER_FRAGMENT = 5;
const float SEA_SPEED = 0.8;
const float SEA_FREQ = 0.16;
const vec3 SEA_WATER_COLOR = vec3(0.48, 0.54, 0.36);

#define SEA_TIME (1.0 + iTime * SEA_SPEED)
const mat2 octave_m = mat2(1.6,1.2,-1.2,1.6);

mat3 fromEuler(vec3 ang) {
    vec2 a1=vec2(sin(ang.x),cos(ang.x));
    vec2 a2=vec2(sin(ang.y),cos(ang.y));
    vec2 a3=vec2(sin(ang.z),cos(ang.z));
    mat3 m;
    m[0]=vec3(a1.y*a3.y+a1.x*a2.x*a3.x,a1.y*a2.x*a3.x+a3.y*a1.x,-a2.y*a3.x);
    m[1]=vec3(-a2.y*a1.x,a1.y*a2.y,a2.x);
    m[2]=vec3(a3.y*a1.x*a2.x+a1.y*a3.x,a1.x*a3.x-a1.y*a3.y*a2.x,a2.y*a3.y);
    return m;
}
float hash(vec2 p){float h=dot(p,vec2(127.1,311.7));return fract(sin(h)*43758.5453123);}
float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);vec2 u=f*f*(3.0-2.0*f);return -1.0+2.0*mix(mix(hash(i+vec2(0,0)),hash(i+vec2(1,0)),u.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),u.x),u.y);}
float diffuse(vec3 n,vec3 l,float p){return pow(dot(n,l)*0.4+0.6,p);}
float specular(vec3 n,vec3 l,vec3 e,float s){float nrm=(s+8.0)/(PI*8.0);return pow(max(dot(reflect(e,n),l),0.0),s)*nrm;}
vec3 getSkyColor(vec3 e){e.y=(max(e.y,0.0)*0.8+0.2)*0.8;return vec3(pow(1.0-e.y,2.0),1.0-e.y,0.6+(1.0-e.y)*0.4)*1.1;}
float sea_octave(vec2 uv,float choppy){uv+=noise(uv);vec2 wv=1.0-abs(sin(uv));vec2 swv=abs(cos(uv));wv=mix(wv,swv,wv);return pow(1.0-pow(wv.x*wv.y,0.65),choppy);}

float map(vec3 p){float freq=SEA_FREQ;float amp=SEA_HEIGHT;float choppy=SEA_CHOPPY;vec2 uv=p.xz;uv.x*=0.75;float d,h=0.0;for(int i=0;i<ITER_GEOMETRY;i++){d=sea_octave((uv+SEA_TIME)*freq,choppy);d+=sea_octave((uv-SEA_TIME)*freq,choppy);h+=d*amp;uv*=octave_m;freq*=1.9;amp*=0.22;choppy=mix(choppy,1.0,0.2);}return p.y-h;}
float map_detailed(vec3 p){float freq=SEA_FREQ;float amp=SEA_HEIGHT;float choppy=SEA_CHOPPY;vec2 uv=p.xz;uv.x*=0.75;float d,h=0.0;for(int i=0;i<ITER_FRAGMENT;i++){d=sea_octave((uv+SEA_TIME)*freq,choppy);d+=sea_octave((uv-SEA_TIME)*freq,choppy);h+=d*amp;uv*=octave_m;freq*=1.9;amp*=0.22;choppy=mix(choppy,1.0,0.2);}return p.y-h;}

vec3 getSeaColor(vec3 p,vec3 n,vec3 l,vec3 eye,vec3 dist){float fresnel=clamp(1.0-dot(n,-eye),0.0,1.0);fresnel=min(pow(fresnel,3.0),0.5);vec3 reflected=getSkyColor(reflect(eye,n));vec3 refracted=SEA_BASE+diffuse(n,l,80.0)*SEA_WATER_COLOR*0.12;vec3 color=mix(refracted,reflected,fresnel);float atten=max(1.0-dot(dist,dist)*0.001,0.0);color+=SEA_WATER_COLOR*(p.y-SEA_HEIGHT)*0.18*atten;color+=vec3(specular(n,l,eye,60.0));return color;}
vec3 getNormal(vec3 p,float eps){vec3 n;n.y=map_detailed(p);n.x=map_detailed(vec3(p.x+eps,p.y,p.z))-n.y;n.z=map_detailed(vec3(p.x,p.y,p.z+eps))-n.y;n.y=eps;return normalize(n);}
float heightMapTracing(vec3 ori,vec3 dir,out vec3 p){float tm=0.0;float tx=1000.0;float hx=map(ori+dir*tx);if(hx>0.0){p=ori+dir*tx;return tx;}float hm=map(ori+dir*tm);float tmid=0.0;for(int i=0;i<NUM_STEPS;i++){tmid=mix(tm,tx,hm/(hm-hx));p=ori+dir*tmid;float hmid=map(p);if(hmid<0.0){tx=tmid;hx=hmid;}else{tm=tmid;hm=hmid;}}return tmid;}
vec3 getPixel(vec2 coord,float time){vec2 uv=coord/iResolution.xy;uv=uv*2.0-1.0;uv.x*=iResolution.x/iResolution.y;vec3 ang=vec3(sin(time*3.0)*0.1,sin(time)*0.2+0.3,time);vec3 ori=vec3(0.0,3.5,time*5.0);vec3 dir=normalize(vec3(uv.xy,-2.0));dir.z+=length(uv)*0.14;dir=normalize(dir)*fromEuler(ang);vec3 p;heightMapTracing(ori,dir,p);vec3 dist=p-ori;vec3 n=getNormal(p,dot(dist,dist)*EPSILON_NRM);vec3 light=normalize(vec3(0.0,1.0,0.8));return mix(getSkyColor(dir),getSeaColor(p,n,light,dir,dist),pow(smoothstep(0.0,-0.02,dir.y),0.2));}

void main(){
    vec2 fragCoord=TexCoord*iResolution;
    float time=iTime*0.3;
    vec3 color=getPixel(fragCoord,time);
    gl_FragColor=vec4(pow(color,vec3(0.65)),1.0);
}
"""

    class _ShaderState:
        def __init__(self):
            self.shader_program = 0
            self.quad_vao = 0
            self.fbo = 0
            self.texture = 0
            self.fbo_width = 600
            self.fbo_height = 600
            self.loc_resolution = -1
            self.loc_time = -1
            self.loc_sea_height = -1
            self.loc_sea_choppy = -1
            self.loc_sea_base = -1

            self.sea_height = 0.6
            self.sea_choppy = 4.0
            self.sea_base = ImVec4(0.0, 0.09, 0.18, 1.0)

        def init(self):
            # Compile shaders
            vs = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            GL.glShaderSource(vs, _VERT_SRC)
            GL.glCompileShader(vs)

            fs = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
            GL.glShaderSource(fs, _FRAG_SRC)
            GL.glCompileShader(fs)

            self.shader_program = GL.glCreateProgram()
            GL.glAttachShader(self.shader_program, vs)
            GL.glAttachShader(self.shader_program, fs)
            GL.glLinkProgram(self.shader_program)
            GL.glDeleteShader(vs)
            GL.glDeleteShader(fs)

            # Create quad VAO
            vertices = np.array([
                -1, -1, 0, 0,
                 1, -1, 1, 0,
                -1,  1, 0, 1,
                 1,  1, 1, 1,
            ], dtype='float32')

            self.quad_vao = GL.glGenVertexArrays(1)
            vbo = GL.glGenBuffers(1)
            GL.glBindVertexArray(self.quad_vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_STATIC_DRAW)
            GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 16, ctypes.c_void_p(0))
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 16, ctypes.c_void_p(8))
            GL.glEnableVertexAttribArray(1)
            GL.glBindVertexArray(0)

            # Uniform locations
            self.loc_resolution = GL.glGetUniformLocation(self.shader_program, "iResolution")
            self.loc_time = GL.glGetUniformLocation(self.shader_program, "iTime")
            self.loc_sea_height = GL.glGetUniformLocation(self.shader_program, "SEA_HEIGHT")
            self.loc_sea_choppy = GL.glGetUniformLocation(self.shader_program, "SEA_CHOPPY")
            self.loc_sea_base = GL.glGetUniformLocation(self.shader_program, "SEA_BASE")

            # Create FBO
            self.fbo = GL.glGenFramebuffers(1)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
            self.texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8,
                            self.fbo_width, self.fbo_height, 0,
                            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
                                      GL.GL_TEXTURE_2D, self.texture, 0)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        def destroy(self):
            if self.texture:
                GL.glDeleteTextures(1, [self.texture])
            if self.fbo:
                GL.glDeleteFramebuffers(1, [self.fbo])
            if self.shader_program:
                GL.glDeleteProgram(self.shader_program)
            if self.quad_vao:
                GL.glDeleteVertexArrays(1, [self.quad_vao])
            self.texture = self.fbo = self.shader_program = self.quad_vao = 0

        def render_to_fbo(self):
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
            GL.glViewport(0, 0, self.fbo_width, self.fbo_height)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            GL.glUseProgram(self.shader_program)
            GL.glUniform2f(self.loc_resolution, float(self.fbo_width), float(self.fbo_height))
            GL.glUniform1f(self.loc_time, float(imgui.get_time()))
            GL.glUniform1f(self.loc_sea_height, self.sea_height)
            GL.glUniform1f(self.loc_sea_choppy, self.sea_choppy)
            GL.glUniform3f(self.loc_sea_base, self.sea_base.x, self.sea_base.y, self.sea_base.z)
            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBindVertexArray(self.quad_vao)
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
            GL.glBindVertexArray(0)
            GL.glUseProgram(0)
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    _shader_state: _ShaderState = None  # type: ignore
    _shader_inited = False

    def _shader_lazy_init():
        global _shader_state, _shader_inited
        if _shader_inited:
            return
        _shader_inited = True
        _shader_state = _ShaderState()
        _shader_state.init()
        hello_imgui.get_runner_params().callbacks.enqueue_before_exit(
            lambda: _shader_state.destroy() if _shader_state else None
        )

    def _shader_gui_main(width: float, height: float):
        _shader_lazy_init()
        if _shader_state:
            _shader_state.render_to_fbo()
            tex_ref = imgui.ImTextureRef(_shader_state.texture)
            imgui.image(tex_ref, ImVec2(width, height),
                        ImVec2(0, 1), ImVec2(1, 0))  # flip Y for FBO

    def _shader_gui_side():
        imgui.text('"Seascape" by Alexander Alekseev aka TDM')
        imgui.set_item_tooltip(
            "License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported\n"
            "Contact: tdmaav@gmail.com")
        imgui.spacing()
        if _shader_state:
            imgui.set_next_item_width(hello_imgui.em_size(7))
            _, _shader_state.sea_height = imgui.slider_float("Wave height", _shader_state.sea_height, 0.1, 2.0)
            imgui.set_next_item_width(hello_imgui.em_size(7))
            _, _shader_state.sea_choppy = imgui.slider_float("Choppiness", _shader_state.sea_choppy, 0.5, 8.0)
            imgui.set_next_item_width(hello_imgui.em_size(7))
            _, _shader_state.sea_base = imgui.color_edit3("Sea base color", _shader_state.sea_base)

    def _shader_slide_gui(content_size: ImVec2):
        em = hello_imgui.em_size()

        # Render shader filling the full content area
        _shader_gui_main(content_size.x, content_size.y)

        # Overlay controls on top of the shader
        overlay_w = em * 18.0
        overlay_h = em * 6.5
        pad = em * 0.8
        overlay_x = imgui.get_item_rect_min().x + content_size.x - overlay_w - pad
        overlay_y = imgui.get_item_rect_min().y + pad

        dl = imgui.get_window_draw_list()
        rounding = em * 0.5
        bg_margin = em * 0.3
        bg = imgui.color_convert_float4_to_u32(ImVec4(0.0, 0.0, 0.0, 0.35))
        border = imgui.color_convert_float4_to_u32(ImVec4(1.0, 1.0, 1.0, 0.15))
        dl.add_rect_filled(
            ImVec2(overlay_x - bg_margin, overlay_y),
            ImVec2(overlay_x + overlay_w, overlay_y + overlay_h + bg_margin),
            bg, rounding)
        dl.add_rect(
            ImVec2(overlay_x - bg_margin, overlay_y),
            ImVec2(overlay_x + overlay_w, overlay_y + overlay_h + bg_margin),
            border, rounding, 0, 1.0)

        imgui.set_cursor_screen_pos(ImVec2(overlay_x, overlay_y))
        imgui.begin_child("##shader_overlay", ImVec2(overlay_w, overlay_h), False,
                          imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
        inner_pad = em * 0.5
        imgui.set_cursor_pos(ImVec2(inner_pad, inner_pad))
        imgui.push_item_width(overlay_w - inner_pad * 2.0)
        _shader_gui_side()
        imgui.pop_item_width()
        imgui.end_child()


# ============================================================================
# Slide wrappers with fallbacks
# ============================================================================

def _telemetry_slide_wrapper(cs: ImVec2):
    if HAS_IMPLOT:
        _telemetry_slide_gui(cs)
    else:
        imgui.text_wrapped("ImPlot not available.")


def _immvision_slide_wrapper(cs: ImVec2):
    if HAS_IMMVISION:
        _immvision_slide_gui(cs)
    else:
        imgui.text_wrapped("ImmVision not available (requires OpenCV).")


def _shader_slide_wrapper(cs: ImVec2):
    if HAS_OPENGL:
        _shader_slide_gui(cs)
    else:
        imgui.text_wrapped("Shader demo requires OpenGL backend.")


# ============================================================================
# Top section
# ============================================================================

def _show_badges():
    btn_size = hello_imgui.em_to_vec2(0.0, 1.5)
    badges_height = btn_size.y + imgui.get_style().item_spacing.y * 2.0
    available_y = imgui.get_content_region_avail().y
    if available_y > badges_height:
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + available_y - badges_height)

    if hello_imgui.image_button_from_asset("images/badge_view_sources.png", btn_size):
        webbrowser.open("https://github.com/pthom/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset("images/badge_view_docs.png", btn_size):
        webbrowser.open("https://pthom.github.io/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset("images/badge_interactive_manual.png", btn_size):
        webbrowser.open("https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html")


_automation_inited = False
_automation_show_me = None


def _intro_top_section():
    global _automation_inited, _automation_show_me

    imgui_md.render_unindented("""
# Dear ImGui Bundle

*From expressive code to powerful GUIs in no time*
""")

    imgui_md.render_unindented("""
        A batteries-included framework built on Dear ImGui, bundling 20+ libraries - plotting, markdown, node editors, 3D gizmos, and more. Works in C++ and Python, on desktop, mobile, and web.
        Dear ImGui Bundle's immediate mode paradigm naturally leads to code that is concise, and [easy to understand](https://pthom.github.io/imgui_bundle/#code-that-reads-like-a-book), both for humans and for AI tools.
        """
    )
    imgui.same_line()
    imgui.text_disabled("Start your first app in 2 or 3 lines of code.")

    if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal):
        imgui.begin_tooltip()
        imgui.dummy(hello_imgui.em_to_vec2(80.0, 0.0))
        demo_utils.show_python_vs_cpp_code(
            """
from imgui_bundle import imgui, immapp
immapp.run(lambda: imgui.text("Hello!"))
""",
            """
#include "immapp/immapp.h"
#include "imgui.h"
int main() { ImmApp::Run([] { ImGui::Text("Hello"); }); }
""",
            5,
        )
        imgui.end_tooltip()

    if hello_imgui.get_runner_params().use_imgui_test_engine:
        if not _automation_inited:
            _automation_inited = True
            _automation_show_me = automation_show_me_immediate_apps()
        engine_io = imgui.test_engine.get_io(hello_imgui.get_imgui_test_engine())
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.cinematic

    imgui.new_line()
    imgui_md.render_unindented("""
The "Demo Apps" tab provide sample starter apps from which you can take inspiration. Click on the "View Code" button to view the apps code, and click on "Run" to run them
""")

    if hello_imgui.get_runner_params().use_imgui_test_engine:
        imgui.same_line()
        # imgui.text_disabled("Demo")
        # if imgui.is_item_clicked(0):
        if imgui.small_button("?"):
            imgui.test_engine.queue_test(
                hello_imgui.get_imgui_test_engine(),
                _automation_show_me,
            )

    demo_utils.animate_logo(
        "images/logo_imgui_bundle_512.png", 1.0, ImVec2(0.5, 3.0), 0.30,
        "https://github.com/pthom/imgui_bundle",
    )


# ============================================================================
# Carousel rendering
# ============================================================================

def _draw_slide_motto_card(slide: CarouselSlide, slide_width: float) -> float:
    em = hello_imgui.em_size()
    dl = imgui.get_window_draw_list()
    font_size = imgui.get_font_size()

    title_font_size = font_size * 1.2
    font = imgui.get_font()

    # Estimate text sizes: title is single line scaled, description wraps
    title_size = imgui.calc_text_size(slide.title)
    title_h = title_size.y * (title_font_size / font_size)
    desc_size = imgui.calc_text_size(slide.description, None, False, slide_width - em * 2.0)

    card_pad_x = em * 1.0
    card_pad_y = em * 0.4
    inner_h = title_h + desc_size.y + em * 0.3
    card_w = slide_width - em * 1.0
    card_h = inner_h + card_pad_y * 2.0
    card_x = imgui.get_cursor_screen_pos().x + (slide_width - card_w) * 0.5
    card_y = imgui.get_cursor_screen_pos().y

    accent_col = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    card_bg = imgui.color_convert_float4_to_u32(ImVec4(accent_col.x, accent_col.y, accent_col.z, 0.12))
    card_border = imgui.color_convert_float4_to_u32(ImVec4(accent_col.x, accent_col.y, accent_col.z, 0.4))
    title_col = imgui.get_color_u32(imgui.Col_.text)
    desc_col = imgui.get_color_u32(imgui.Col_.text_disabled)

    dl.add_rect_filled(ImVec2(card_x, card_y), ImVec2(card_x + card_w, card_y + card_h), card_bg, em * 0.4)
    dl.add_rect(ImVec2(card_x, card_y), ImVec2(card_x + card_w, card_y + card_h), card_border, em * 0.4, 0, 1.5)

    dl.add_text(font, title_font_size,
                ImVec2(card_x + card_pad_x, card_y + card_pad_y), title_col, slide.title)
    dl.add_text(font, font_size,
                ImVec2(card_x + card_pad_x, card_y + card_pad_y + title_h + em * 0.3),
                desc_col, slide.description, None, slide_width - em * 2.0)

    total_h = card_h + em * 0.4
    imgui.dummy(ImVec2(slide_width, total_h))
    return total_h


# Module-level carousel state
_current_slide = 0
_animated_offset = 0.0
_auto_timer = 0.0
_auto_stopped = False


def _intro_mini_demos():
    global _current_slide, _animated_offset, _auto_timer, _auto_stopped

    slides = [
        CarouselSlide(
            "Rich Interactive Plots",
            "ImPlot delivers animated, interactive 2D charts with minimal code. It is extremely fast, and ideal for real-time data monitoring, diagnostics, and dashboards.",
            _telemetry_slide_wrapper),
        CarouselSlide(
            "GPU-Accelerated Rendering",
            "Dear ImGui renders directly on the GPU \u2014 fast enough to blend custom shaders and 3D content into your UI.",
            _shader_slide_wrapper),
        CarouselSlide(
            "3D Data Exploration",
            "ImPlot3D adds rotatable, zoomable 3D plots \u2014 navigate complex datasets with intuitive controls.",
            _lorenz_slide_gui),
        CarouselSlide(
            "Image Analysis",
            "ImmVision lets you zoom, pan, and inspect pixel values in real time \u2014 with linked views and colormaps.",
            _immvision_slide_wrapper),
        CarouselSlide(
            "Feature-Rich Widgets",
            "Dear ImGui ships with advanced tables featuring angled headers, column reordering, sorting, and much more.",
            _table_slide_gui),
        CarouselSlide(
            "Explore Ideas in a Node Editor",
            "With imgui-node-editor, you can build complex applications such as blueprint editors. Here is an example of an image editing pipeline.",
            _node_editor_slide_gui),
        CarouselSlide(
            "Rich Documentation, Built In",
            "Render markdown directly in your UI \u2014 headers, code blocks, tables, links, and images, all from a simple string.",
            _markdown_slide_gui),
        CarouselSlide(
            "Integrated Text & Code Editor",
            "The built-in text editor supports syntax highlighting, line numbers, and search. Below is the source of this very demo \u2014 side by side in Python and C++.",
            _source_code_slide_gui),
        CarouselSlide(
            "Deploy to the Web",
            "Python applications can be effortlessly deployed to the web using Pyodide, and C++ apps using Emscripten.",
            _web_deploy_slide_gui),
        CarouselSlide(
            "Usage in Notebooks",
            "Dear ImGui Bundle can also be used from a notebook \u2014 here, it displays a real-time dashboard during an ML training session.",
            _notebook_slide_gui),
    ]
    slide_count = len(slides)

    dt = imgui.get_io().delta_time
    if dt <= 0.0:
        dt = 1.0 / 60.0
    if dt > 0.1:
        dt = 0.1

    em = hello_imgui.em_size()
    dl = imgui.get_window_draw_list()
    window_size = imgui.get_window_size()

    # --- Carousel zone: 4:3 aspect ratio, centered, 65% of window height ---
    carousel_height = window_size.y * 0.65
    if carousel_height < em * 15.0:
        carousel_height = em * 15.0
    carousel_width = carousel_height * (4.0 / 3.0)
    avail_width = imgui.get_content_region_avail().x
    if carousel_width > avail_width:
        carousel_width = avail_width

    carousel_offset_x = (avail_width - carousel_width) * 0.5
    if carousel_offset_x < 0.0:
        carousel_offset_x = 0.0

    imgui.indent(carousel_offset_x)

    # --- Auto-advance ---
    if not _auto_stopped:
        user_interacting = imgui.is_any_item_active()
        if not user_interacting:
            _auto_timer += dt
            if _auto_timer > 5.0:
                _current_slide = (_current_slide + 1) % slide_count
                _auto_timer = 0.0

    # --- Smooth slide animation ---
    target = float(_current_slide)
    _animated_offset = smooth_damp(_animated_offset, target, 8.0, dt)
    if abs(_animated_offset - target) < 0.001:
        _animated_offset = target

    # --- Slide area ---
    nav_bar_height = em * 2.0
    slide_height = carousel_height - nav_bar_height
    if slide_height < em * 10.0:
        slide_height = em * 10.0
    slide_width = carousel_width

    slide_area_pos = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(carousel_width, slide_height))

    # Clip to carousel bounds
    dl.push_clip_rect(slide_area_pos,
                      ImVec2(slide_area_pos.x + carousel_width, slide_area_pos.y + slide_height), True)

    for i in range(slide_count):
        slide_x = slide_area_pos.x + (float(i) - _animated_offset) * slide_width
        if slide_x > slide_area_pos.x + carousel_width or slide_x + slide_width < slide_area_pos.x:
            continue

        imgui.set_cursor_screen_pos(ImVec2(slide_x, slide_area_pos.y))
        child_id = f"##slide_{i}"
        imgui.begin_child(child_id, ImVec2(slide_width, slide_height), False,
                          imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)

        motto_h = _draw_slide_motto_card(slides[i], slide_width)

        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + em * 0.5)
        demo_size = ImVec2(slide_width - em * 1.0, slide_height - motto_h - em * 0.5)
        slides[i].gui_func(demo_size)

        imgui.end_child()

    dl.pop_clip_rect()

    # --- Navigation: arrows + dots ---
    dot_radius = em * 0.3
    dot_spacing = em * 1.5
    dots_width = slide_count * dot_spacing
    arrow_btn_w = em * 2.0
    total_nav_width = arrow_btn_w * 2.0 + dots_width + em * 1.0
    nav_start_x = slide_area_pos.x + (carousel_width - total_nav_width) * 0.5
    nav_y = slide_area_pos.y + slide_height + em * 0.3

    # Left arrow
    imgui.set_cursor_screen_pos(ImVec2(nav_start_x, nav_y))
    if imgui.button(icons_fontawesome_6.ICON_FA_CHEVRON_LEFT + "##carousel_prev",
                    ImVec2(arrow_btn_w, em * 1.5)):
        _current_slide = (_current_slide - 1 + slide_count) % slide_count
        _auto_stopped = True

    # Dots
    dots_start_x = nav_start_x + arrow_btn_w + em * 0.5
    dots_center_y = nav_y + em * 0.75

    for i in range(slide_count):
        center = ImVec2(dots_start_x + i * dot_spacing + dot_spacing * 0.5, dots_center_y)

        imgui.set_cursor_screen_pos(ImVec2(center.x - dot_radius * 2.0, center.y - dot_radius * 2.0))
        dot_id = f"##dot{i}"
        if imgui.invisible_button(dot_id, ImVec2(dot_radius * 4.0, dot_radius * 4.0)):
            _current_slide = i
            _auto_stopped = True

        hovered = imgui.is_item_hovered()
        r = dot_radius * 1.3 if i == _current_slide else dot_radius
        accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
        if i == _current_slide:
            dot_col = imgui.color_convert_float4_to_u32(accent)
        elif hovered:
            dot_col = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, 0.6))
        else:
            dot_col = imgui.get_color_u32(imgui.Col_.text_disabled)
        dl.add_circle_filled(center, r, dot_col)

    # Right arrow
    right_arrow_x = dots_start_x + dots_width + em * 0.5
    imgui.set_cursor_screen_pos(ImVec2(right_arrow_x, nav_y))
    if imgui.button(icons_fontawesome_6.ICON_FA_CHEVRON_RIGHT + "##carousel_next",
                    ImVec2(arrow_btn_w, em * 1.5)):
        _current_slide = (_current_slide + 1) % slide_count
        _auto_stopped = True

    # Advance cursor past nav bar
    imgui.set_cursor_screen_pos(ImVec2(slide_area_pos.x, nav_y + em * 1.8))
    imgui.dummy(ImVec2(1, 1))

    imgui.unindent(carousel_offset_x)


# ============================================================================
# Main entry point
# ============================================================================

def demo_gui():
    # Disable idling so animations run smoothly
    hello_imgui.get_runner_params().fps_idling.enable_idling = False

    _intro_top_section()
    imgui.separator()
    imgui_md.render("*Below are some examples showing what can be achieved with Dear ImGui Bundle*")
    _intro_mini_demos()

    imgui.new_line()
    imgui.separator()
    _show_badges()


if __name__ == "__main__":
    from imgui_bundle import immapp
    immapp.run(
        demo_gui,
        window_title="Dear ImGui Bundle - Intro",
        window_size=(1200, 900),
        with_implot=True,
        with_implot3d=True,
        with_markdown=True,
        fps_idle=0,
    )
