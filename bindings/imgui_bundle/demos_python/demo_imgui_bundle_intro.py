# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""Dear ImGui Bundle: the welcome page

The first screen of the explorer and of the playground: the tagline, a carousel of live mini demos (plots, a
shader, a neural network, images, a node editor, widgets, markdown, code), a button to the catalog of demos, and
the prose of demos_assets/welcome.md behind "More info & links". The page that shows it (the explorer, the playground)
gives it a Host: what the button and the links do.
"""
import math
import sys
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import numpy as np

import imgui_bundle
from imgui_bundle import imgui, rich_md, hello_imgui, immapp, ImVec2, ImVec4, em_size
from imgui_bundle import imgui_color_text_edit as ed, register_demos_assets_folder
from imgui_bundle import imgui_knobs, imgui_toggle, imgui_node_editor as node_ed
from imgui_bundle import implot, implot3d
from imgui_bundle.immapp import icons_fontawesome_4

register_demos_assets_folder()  # welcome.md and resources.md (in Pyodide: delivered by the playground, see examples.json)

IS_PYODIDE = sys.platform == "emscripten"

try:
    from imgui_bundle import immvision
    HAS_IMMVISION = True
except ImportError:
    HAS_IMMVISION = False

# The GPU slide draws with OpenGL: PyOpenGL on the desktop, WebGL2 in Pyodide (through a PyOpenGL-shaped adapter,
# see the slide). Without either, the slide is left out.
HAS_GL = False
if IS_PYODIDE:
    HAS_GL = imgui_bundle.has_submodule("webgl")
else:
    try:
        # Workaround for PyOpenGL 3.1.6+ on Wayland: GLFW (used by immapp / hello_imgui)
        # creates X11/XWayland windows, but PyOpenGL defaults to Wayland EGL, causing a
        # context mismatch. Force the X11 backend before importing OpenGL.
        # See https://github.com/pthom/imgui_bundle/issues/321
        import os
        if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
            os.environ["PYOPENGL_PLATFORM"] = "x11"

        import OpenGL.GL as GL
        import ctypes
        HAS_GL = True
    except ImportError:
        pass


SITE = "https://imgui-bundle.pages.dev"
# The interactive manuals, by their filename in the catalog (examples.json)
MANUALS = [("Dear ImGui", "manual_imgui.py"), ("ImPlot", "manual_implot.py"), ("ImPlot3D", "manual_implot3d.py"),
           ("ImAnim", "manual_im_anim.py")]
SLIDE_DURATION = 5.0  # s: the carousel moves to the next slide by itself, until the user touches it


def is_small_screen() -> bool:
    """Returns True on phones and small tablets (< ~800px width)."""
    return imgui.get_io().display_size.x < hello_imgui.em_size() * 50


@dataclass
class Host:
    """What the page that shows the welcome provides: the explorer changes its state, the playground opens its
    gallery (see main()). Without a host (the standalone run), the page shows no button."""
    nb_demos: int = 0
    browse: Optional[Callable[[], None]] = None  # opens the catalog of demos
    open_demo: Optional[Callable[[str], None]] = None  # opens one demo of the catalog, by its filename in examples.json


_host = Host()  # the page that shows the welcome (welcome_gui sets it): the slides' own links use it


# ============================================================================
# Test engine automations: "Show me" walks the explorer's demos (the explorer only)
# ============================================================================

def _explorer():
    """The explorer's module and its page (imported here: the explorer imports this module). None standalone."""
    from imgui_bundle.demos_python import demo_imgui_bundle
    return demo_imgui_bundle, demo_imgui_bundle._EXPLORER


def _show_demo_code(ctx, filename: str) -> None:
    """Goes to the demos, selects this one (its category's chip scrolls to it, a click on its card) and shows its
    code"""
    explorer_module, explorer = _explorer()
    launcher = explorer.launcher
    launcher.code_view = None  # as a previous automation may have left it
    if explorer.state != explorer_module.DEMOS:
        ctx.item_click("//**/" + explorer_module.DEMOS_LABEL)
        ctx.sleep(1.5)  # the change of page, then the cards dealt
    category = next(c for c in launcher.categories if any(d.filename == filename for d in c.demos))
    ctx.item_click("//**/" + launcher.chip_label(category))
    ctx.sleep(0.8)  # the scroll
    top_left, bottom_right = launcher.card_rects[filename]
    ctx.mouse_move_to_pos(ImVec2((top_left.x + bottom_right.x) / 2, (top_left.y + bottom_right.y) / 2))
    ctx.mouse_click(0)
    ctx.sleep(0.5)
    ctx.item_click("//**/" + icons_fontawesome_4.ICON_FA_CODE + "  View code")


def _automation_show_me_immediate_apps():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(engine, "Automation", "ShowMeImmediateApps")

    def test_func(ctx):
        explorer_module, _ = _explorer()
        all_the_demos = "//**/" + icons_fontawesome_4.ICON_FA_ARROW_LEFT + "  All the demos"
        _show_demo_code(ctx, "demo_hello_world.py")
        ctx.sleep(2.0)
        ctx.item_click(all_the_demos)
        _show_demo_code(ctx, "demo_assets_addons.py")
        ctx.sleep(2.0)
        ctx.item_click(all_the_demos)
        ctx.mouse_move("//**/" + icons_fontawesome_4.ICON_FA_PLAY + "  Run")
        ctx.sleep(1.0)
        ctx.item_click("//**/" + explorer_module.WELCOME_LABEL)

    automation.test_func = test_func
    return automation


def _automation_show_me_custom_background():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(engine, "Automation", "ShowMeCustomBackgroundExample")

    def test_func(ctx):
        _show_demo_code(ctx, "demo_custom_background.py")
        ctx.mouse_move("//**/" + icons_fontawesome_4.ICON_FA_ARROW_LEFT + "  All the demos")

    automation.test_func = test_func
    return automation


def _automation_show_me_docking():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(engine, "Automation", "ShowMeDockingExample")

    def test_func(ctx):
        _show_demo_code(ctx, "demo_docking.py")
        ctx.mouse_move("//**/" + icons_fontawesome_4.ICON_FA_ARROW_LEFT + "  All the demos")

    automation.test_func = test_func
    return automation


class _IntroAutomations:
    show_immediate_apps = None
    show_custom_background = None
    show_docking = None
    _inited = False

    @staticmethod
    def init():
        if _IntroAutomations._inited:
            return
        if not hello_imgui.get_runner_params().use_imgui_test_engine or _explorer()[1] is None:
            return  # the automations drive the explorer's page: none standalone
        _IntroAutomations._inited = True
        _IntroAutomations.show_immediate_apps = _automation_show_me_immediate_apps()
        _IntroAutomations.show_custom_background = _automation_show_me_custom_background()
        _IntroAutomations.show_docking = _automation_show_me_docking()
        engine_io = imgui.test_engine.get_io(hello_imgui.get_imgui_test_engine())
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.cinematic

    @staticmethod
    def show_link(label, automation):
        if automation is None:
            return
        imgui.spacing()
        imgui.push_style_color(imgui.Col_.text, rich_md.link_color())
        imgui.text(label)
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal):
            imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
            if imgui.is_mouse_clicked(imgui.MouseButton_.left):
                imgui.set_window_focus(None)  # clear focus from overlay
                imgui.test_engine.queue_test(hello_imgui.get_imgui_test_engine(), automation)
        imgui.pop_style_color()


# ============================================================================
# Carousel infrastructure
# ============================================================================

@dataclass
class CarouselSlide:
    title: str
    description: str
    gui_func: Callable[[ImVec2], None]
    demo: str = ""  # the catalog's demo that goes further (its filename in examples.json), linked from the title card


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
    dl.add_rect(panel_pos, ImVec2(panel_pos.x + width, panel_pos.y + height), border, rounding, 1.5, 0)

    imgui.begin_child(panel_id, ImVec2(width, height), False,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
    pad = em * 0.5
    imgui.set_cursor_pos(ImVec2(pad, pad))
    imgui.push_item_width((width - pad * 2.0) * 0.5)
    draw_widgets()
    imgui.pop_item_width()
    imgui.end_child()


def _accent_knob(label: str, value: float, v_min: float, v_max: float, fmt: str, size: float) -> tuple[bool, float]:
    """A knob in the accent color of the style (the sequencer's tempo, Lorenz's parameters)"""
    accent = imgui.get_style_color_vec4(imgui.Col_.slider_grab)
    imgui.push_style_color(imgui.Col_.frame_bg, ImVec4(accent.x, accent.y, accent.z, 0.4))
    imgui.push_style_color(imgui.Col_.frame_bg_hovered, ImVec4(accent.x, accent.y, accent.z, 0.6))
    imgui.push_style_color(imgui.Col_.frame_bg_active, ImVec4(accent.x, accent.y, accent.z, 0.8))
    changed, value = imgui_knobs.knob(label, value, v_min, v_max, 0.0, fmt, imgui_knobs.ImGuiKnobVariant_.wiper_dot,
                                      size, imgui_knobs.ImGuiKnobFlags_.always_clamp)
    imgui.pop_style_color(3)
    return changed, value


def _accent_button(label: str, size: ImVec2) -> bool:
    """A button in the accent color of the style"""
    accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    imgui.push_style_color(imgui.Col_.button, ImVec4(accent.x, accent.y, accent.z, 0.55))
    imgui.push_style_color(imgui.Col_.button_hovered, ImVec4(accent.x, accent.y, accent.z, 0.8))
    imgui.push_style_color(imgui.Col_.button_active, ImVec4(accent.x, accent.y, accent.z, 1.0))
    clicked = imgui.button(label, size)
    imgui.pop_style_color(3)
    return clicked


MANUAL_PICTURE_ASPECT = 640 / 401  # the width / the height of the manuals' pictures (their cards' in the catalog)


def _manual_picture(demo: str, width: float) -> None:
    """The picture of a manual (its card's, from the site), which opens it when the page can open a demo"""
    url = f"{SITE}/resources/playground/{demo.replace('.py', '.jpg')}"
    top_left = imgui.get_cursor_screen_pos()
    rich_md.render(f'<img src="{url}" width="{int(width)}">')
    bottom_right = ImVec2(top_left.x + width, imgui.get_cursor_screen_pos().y)
    if _host.open_demo is None or not imgui.is_mouse_hovering_rect(top_left, bottom_right):
        return
    imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
    imgui.get_window_draw_list().add_rect(top_left, bottom_right, imgui.get_color_u32(imgui.Col_.button_hovered),
                                          hello_imgui.em_size(0.3), 2.0)
    if imgui.is_mouse_clicked(imgui.MouseButton_.left):
        _host.open_demo(demo)


def _manual_teaser(text: str, demo: str) -> None:
    """A line of text, then the manual's picture below it, as large as the space left allows (none if too small)"""
    em = hello_imgui.em_size()
    imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x)
    imgui.text_wrapped(text)
    imgui.pop_text_wrap_pos()
    avail = imgui.get_content_region_avail()
    width = min(avail.x - em * 0.5, (avail.y - em * 0.5) * MANUAL_PICTURE_ASPECT)
    if width < em * 6:
        return
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail.x - width) / 2)
    _manual_picture(demo, width)


def panel_bg(top_left: ImVec2, size: ImVec2, alpha_bg: float = 0.08, alpha_border: float = 0.3) -> None:
    """A rounded rectangle in the accent color, behind a part of a slide"""
    em = hello_imgui.em_size()
    dl = imgui.get_window_draw_list()
    accent = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    bg = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, alpha_bg))
    border = imgui.color_convert_float4_to_u32(ImVec4(accent.x, accent.y, accent.z, alpha_border))
    bottom_right = ImVec2(top_left.x + size.x, top_left.y + size.y)
    dl.add_rect_filled(top_left, bottom_right, bg, em * 0.4)
    dl.add_rect(top_left, bottom_right, border, em * 0.4, 1.5, 0)


# ============================================================================
# Slide: ImPlot, 4 plot types in subplots
# ============================================================================

_implot_inited = False
_implot_xs: np.ndarray = None  # type: ignore

# Filled line plots (static)
_filled_xs: np.ndarray = None  # type: ignore
_filled_ys1: np.ndarray = None  # type: ignore
_filled_ys2: np.ndarray = None  # type: ignore
_filled_ys3: np.ndarray = None  # type: ignore

# Shaded plots (static, like original demo)
_shaded_xs: np.ndarray = None  # type: ignore
_shaded_ys: np.ndarray = None  # type: ignore
_shaded_ys1: np.ndarray = None  # type: ignore
_shaded_ys2: np.ndarray = None  # type: ignore
_shaded_ys3: np.ndarray = None  # type: ignore
_shaded_ys4: np.ndarray = None  # type: ignore


def _random_range(low: float, high: float, n: int) -> np.ndarray:
    return low + (high - low) * np.random.rand(n)


def _implot_init():
    global _implot_inited, _implot_xs
    global _filled_xs, _filled_ys1, _filled_ys2, _filled_ys3
    global _shaded_xs, _shaded_ys, _shaded_ys1, _shaded_ys2, _shaded_ys3, _shaded_ys4
    np.random.seed(0)

    _implot_xs = np.linspace(0, 1, 1001, dtype=np.float64)

    # Filled line plots
    _filled_xs = np.arange(101, dtype=np.float64)
    _filled_ys1 = _random_range(400.0, 450.0, 101)
    _filled_ys2 = _random_range(275.0, 350.0, 101)
    _filled_ys3 = _random_range(150.0, 225.0, 101)

    # Shaded plots (from original demo_shaded_plots)
    _shaded_xs = np.linspace(0, 1, 1001, dtype=np.float64)
    _shaded_ys = 0.25 + 0.25 * np.sin(25 * _shaded_xs) * np.sin(5 * _shaded_xs) + _random_range(-0.01, 0.01, 1001)
    _shaded_ys1 = _shaded_ys + _random_range(0.1, 0.12, 1001)
    _shaded_ys2 = _shaded_ys - _random_range(0.1, 0.12, 1001)
    _shaded_ys3 = 0.75 + 0.2 * np.sin(25 * _shaded_xs)
    _shaded_ys4 = 0.75 + 0.1 * np.cos(25 * _shaded_xs)

    _implot_inited = True


def _implot_subplot1_line_plots():
    """Animated line plots with 3 curves and interactive legend."""
    t = imgui.get_time() * 1.5
    ys1 = 0.5 + 0.5 * np.sin(6.0 * (_implot_xs + t))
    ys2 = 0.5 + 0.3 * np.cos(4.0 * (_implot_xs + t))
    ys3 = 0.5 + 0.2 * np.sin(10.0 * _implot_xs + t) * np.cos(3.0 * _implot_xs + t)
    if implot.begin_plot("Line Plots", flags=_implot_flags()):
        implot.setup_axes("x", "y",
                          implot.AxisFlags_.no_tick_labels,
                          implot.AxisFlags_.no_tick_labels)
        implot.setup_axes_limits(0, 1, -0.1, 1.1)
        implot.plot_line("f(x)", _implot_xs, ys1)
        implot.plot_line("g(x)", _implot_xs, ys2)
        implot.plot_line("h(x)", _implot_xs, ys3)
        implot.end_plot()
        hello_imgui.set_item_is_live()  # the curves move on their own


def _implot_subplot2_filled():
    """Static filled line plots (stock prices)."""
    if implot.begin_plot("Stock Prices", flags=_implot_flags()):
        implot.setup_axes("Days", "Price")
        implot.setup_axes_limits(0, 100, 0, 500)
        spec = implot.Spec(fill_alpha=0.25)
        implot.plot_shaded("Stock 1", _filled_xs, _filled_ys1, 0.0, spec)
        implot.plot_line("Stock 1", _filled_xs, _filled_ys1)
        implot.plot_shaded("Stock 2", _filled_xs, _filled_ys2, 0.0, spec)
        implot.plot_line("Stock 2", _filled_xs, _filled_ys2)
        implot.plot_shaded("Stock 3", _filled_xs, _filled_ys3, 0.0, spec)
        implot.plot_line("Stock 3", _filled_xs, _filled_ys3)
        implot.end_plot()


def _implot_subplot3_shaded():
    """Shaded plots (from original demo)."""
    spec = implot.Spec(fill_alpha=0.25)
    if implot.begin_plot("Shaded Plots", flags=_implot_flags()):
        implot.setup_legend(implot.Location_.north_west, implot.LegendFlags_.reverse)
        implot.plot_shaded("Uncertain Data", _shaded_xs, _shaded_ys1, _shaded_ys2, spec)
        implot.plot_line("Uncertain Data", _shaded_xs, _shaded_ys, spec)
        implot.plot_shaded("Overlapping", _shaded_xs, _shaded_ys3, _shaded_ys4, spec)
        implot.plot_line("Overlapping", _shaded_xs, _shaded_ys3, spec)
        implot.plot_line("Overlapping", _shaded_xs, _shaded_ys4, spec)
        implot.end_plot()


def _implot_flags() -> int:
    """No legends on a phone: they would cover the small plots"""
    return implot.Flags_.no_legend.value if is_small_screen() else 0


def _implot_slide_gui(content_size: ImVec2):
    """Three plots, and in the place of the fourth the picture of the ImPlot manual"""
    if not _implot_inited:
        _implot_init()
    sub_flags = implot.SubplotFlags_.no_resize
    if not implot.begin_subplots("##ImPlotShowcase", 2, 2, content_size, sub_flags):
        return
    _implot_subplot1_line_plots()
    _implot_subplot2_filled()
    _implot_subplot3_shaded()
    implot.end_subplots()
    after = imgui.get_cursor_screen_pos()
    top_left, bottom_right = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    em = hello_imgui.em_size()
    cell_min = ImVec2((top_left.x + bottom_right.x) / 2 + em, (top_left.y + bottom_right.y) / 2 + em * 0.5)
    imgui.set_cursor_screen_pos(cell_min)
    imgui.begin_child("##implot_manual", bottom_right - cell_min - ImVec2(em * 0.5, em * 0.5), False,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
    _manual_teaser("Every plot type, with its code: the ImPlot manual", "manual_implot.py")
    imgui.end_child()
    imgui.set_cursor_screen_pos(after)
    imgui.dummy(ImVec2(0, 0))  # ImGui wants an item where the cursor was moved


# ============================================================================
# Slide: the seascape shader, rendered to a texture (OpenGL on the desktop, WebGL2 in Pyodide)
# ============================================================================

if HAS_GL:
    if IS_PYODIDE:
        from js import document, Float32Array  # type: ignore
        from imgui_bundle import webgl

        class _GLCompat:
            """A PyOpenGL-shaped adapter over the WebGL2 context that hello_imgui renders into, for the subset of calls
            the slide makes (as demos_python/playground/examples/webgl_background_shader.py). Renames are forwarded
            (glCreateShader -> createShader, GL_FLOAT -> gl.FLOAT); the calls whose shape differs are written out."""

            def __init__(self):
                self._gl = document.getElementById("canvas").getContext("webgl2")
                if self._gl is None:
                    raise RuntimeError("Could not acquire WebGL2 context on #canvas")

            _CONSTANT_FALLBACKS = {"FALSE": 0, "TRUE": 1}

            def __getattr__(self, name):
                if name.startswith("GL_"):
                    suffix = name[3:]
                    if hasattr(self._gl, suffix):
                        return getattr(self._gl, suffix)
                    if suffix in self._CONSTANT_FALLBACKS:
                        return self._CONSTANT_FALLBACKS[suffix]
                    raise AttributeError(name)
                if name.startswith("gl") and len(name) > 2 and name[2].isupper():
                    return getattr(self._gl, name[2].lower() + name[3:])
                raise AttributeError(name)

            # WebGL creates and deletes one object at a time
            def glGenVertexArrays(self, n):
                return self._gl.createVertexArray()

            def glDeleteVertexArrays(self, n, vaos):
                for vao in vaos:
                    self._gl.deleteVertexArray(vao)

            def glGenBuffers(self, n):
                return self._gl.createBuffer()

            def glGenFramebuffers(self, n):
                return self._gl.createFramebuffer()

            def glDeleteFramebuffers(self, n, fbos):
                for fbo in fbos:
                    self._gl.deleteFramebuffer(fbo)

            def glGenTextures(self, n):
                return self._gl.createTexture()

            def glDeleteTextures(self, n, textures):
                for tex in textures:
                    self._gl.deleteTexture(tex)

            # PyOpenGL unbinds with 0, WebGL with null
            def glBindBuffer(self, target, buffer):
                self._gl.bindBuffer(target, buffer or None)

            def glBindVertexArray(self, vao):
                self._gl.bindVertexArray(vao or None)

            def glUseProgram(self, program):
                self._gl.useProgram(program or None)

            def glBindFramebuffer(self, target, fbo):
                self._gl.bindFramebuffer(target, fbo or None)

            def glBindTexture(self, target, texture):
                self._gl.bindTexture(target, texture or None)

            def glGetShaderiv(self, shader, pname):
                return self._gl.getShaderParameter(shader, pname)

            def glBufferData(self, target, data, usage):
                self._gl.bufferData(target, Float32Array.new(data.tolist()), usage)

            def glVertexAttribPointer(self, index, size, type_, normalized, stride, offset):
                self._gl.vertexAttribPointer(index, size, type_, bool(normalized), stride, offset)

        GL = _GLCompat()
        _GLSL_HEADER = "#version 300 es\nprecision highp float;\n"
    else:
        _GLSL_HEADER = "#version 330 core\n"

    _VERT_SRC = _GLSL_HEADER + """
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;
out vec2 TexCoord;
void main() { gl_Position = vec4(aPos, 0.0, 1.0); TexCoord = aTexCoord; }
"""

    # Seascape by Alexander Alekseev aka TDM - 2014, https://www.shadertoy.com/view/Ms2SD1
    # License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported
    _FRAG_SRC = _GLSL_HEADER + """
in vec2 TexCoord;
out vec4 FragColor;
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
    FragColor=vec4(pow(color,vec3(0.65)),1.0);
}
"""

    class _ShaderState:
        def __init__(self, fbo_size: int):
            self.shader_program = 0
            self.quad_vao = 0
            self.fbo = 0
            self.texture = 0
            self.texture_id = 0  # what imgui.image() shows (in Pyodide, the texture registered with the renderer)
            self.fbo_width = fbo_size
            self.fbo_height = fbo_size
            self.loc_resolution = -1
            self.loc_time = -1
            self.loc_sea_height = -1
            self.loc_sea_choppy = -1
            self.loc_sea_base = -1

            self.sea_height = 0.6
            self.sea_choppy = 4.0
            self.sea_base = ImVec4(0.0, 0.09, 0.18, 1.0)

        def init(self):
            vs = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            GL.glShaderSource(vs, _VERT_SRC)
            GL.glCompileShader(vs)
            fs = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
            GL.glShaderSource(fs, _FRAG_SRC)
            GL.glCompileShader(fs)
            if not GL.glGetShaderiv(fs, GL.GL_COMPILE_STATUS):
                raise RuntimeError("Seascape shader: " + str(GL.glGetShaderInfoLog(fs)))
            self.shader_program = GL.glCreateProgram()
            GL.glAttachShader(self.shader_program, vs)
            GL.glAttachShader(self.shader_program, fs)
            GL.glLinkProgram(self.shader_program)
            GL.glDeleteShader(vs)
            GL.glDeleteShader(fs)

            # A quad over the whole texture: x, y, u, v
            vertices = np.array([-1, -1, 0, 0, 1, -1, 1, 0, -1, 1, 0, 1, 1, 1, 1, 1], dtype="float32")
            self.quad_vao = GL.glGenVertexArrays(1)
            vbo = GL.glGenBuffers(1)
            GL.glBindVertexArray(self.quad_vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_STATIC_DRAW)
            offset0, offset8 = (0, 8) if IS_PYODIDE else (ctypes.c_void_p(0), ctypes.c_void_p(8))
            GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 16, offset0)
            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 16, offset8)
            GL.glEnableVertexAttribArray(1)
            GL.glBindVertexArray(0)

            self.loc_resolution = GL.glGetUniformLocation(self.shader_program, "iResolution")
            self.loc_time = GL.glGetUniformLocation(self.shader_program, "iTime")
            self.loc_sea_height = GL.glGetUniformLocation(self.shader_program, "SEA_HEIGHT")
            self.loc_sea_choppy = GL.glGetUniformLocation(self.shader_program, "SEA_CHOPPY")
            self.loc_sea_base = GL.glGetUniformLocation(self.shader_program, "SEA_BASE")

            # The texture the shader draws into
            self.fbo = GL.glGenFramebuffers(1)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
            self.texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, self.fbo_width, self.fbo_height, 0,
                            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.texture, 0)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            self.texture_id = webgl.register_texture(self.texture) if IS_PYODIDE else self.texture

        def destroy(self):
            try:
                if IS_PYODIDE and self.texture_id:
                    webgl.unregister_texture(self.texture_id)
                if self.texture:
                    GL.glDeleteTextures(1, [self.texture])
                if self.fbo:
                    GL.glDeleteFramebuffers(1, [self.fbo])
                if self.shader_program:
                    GL.glDeleteProgram(self.shader_program)
                if self.quad_vao:
                    GL.glDeleteVertexArrays(1, [self.quad_vao])
            except Exception:
                pass  # GL context may already be partially torn down at exit
            self.texture = self.fbo = self.shader_program = self.quad_vao = self.texture_id = 0

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
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    _shader_state: Optional[_ShaderState] = None
    _shader_inited = False

    def _shader_lazy_init():
        global _shader_state, _shader_inited
        if _shader_inited:
            return
        _shader_inited = True
        try:
            # A phone's GPU ray-marches the sea at a quarter of the pixels
            _shader_state = _ShaderState(300 if is_small_screen() else 600)
            _shader_state.init()
            hello_imgui.get_runner_params().callbacks.enqueue_before_exit(
                lambda: _shader_state.destroy() if _shader_state else None
            )
        except Exception as e:
            print(f"Shader init failed: {e}")
            _shader_state = None

    def _shader_gui_side(narrow: bool):
        imgui.text('"Seascape" by TDM' if narrow else '"Seascape" by Alexander Alekseev aka TDM')
        imgui.set_item_tooltip(
            "Alexander Alekseev aka TDM, https://www.shadertoy.com/view/Ms2SD1\n"
            "License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported\n"
            "Contact: tdmaav@gmail.com")
        if _shader_state is None:
            return
        imgui.set_next_item_width(hello_imgui.em_size(7))
        _, _shader_state.sea_height = imgui.slider_float("Wave height", _shader_state.sea_height, 0.1, 2.0)
        if narrow:
            return
        imgui.set_next_item_width(hello_imgui.em_size(7))
        _, _shader_state.sea_choppy = imgui.slider_float("Choppiness", _shader_state.sea_choppy, 0.5, 8.0)
        imgui.set_next_item_width(hello_imgui.em_size(7))
        _, _shader_state.sea_base = imgui.color_edit3("Sea base color", _shader_state.sea_base)
        _IntroAutomations.show_link("More info & code", _IntroAutomations.show_custom_background)

    def _shader_slide_gui(content_size: ImVec2):
        em = hello_imgui.em_size()
        _shader_lazy_init()
        if _shader_state is None:
            imgui.dummy(content_size)
            return
        _shader_state.render_to_fbo()
        imgui.image(imgui.ImTextureRef(_shader_state.texture_id), content_size, ImVec2(0, 1), ImVec2(1, 0))
        hello_imgui.set_item_is_live()  # the sea moves on its own

        # The controls, in a translucent window over the sea
        narrow = is_small_screen()
        pad = em * 0.8
        overlay_w = em * 13.0 if narrow else em * 18.0
        overlay_x = imgui.get_item_rect_max().x - overlay_w - pad
        overlay_y = imgui.get_item_rect_min().y + pad
        imgui.set_next_window_pos(ImVec2(overlay_x, overlay_y), imgui.Cond_.always.value)
        imgui.set_next_window_bg_alpha(0.45)
        imgui.push_style_var(imgui.StyleVar_.window_rounding, em * 0.5)
        # No focus when it appears: the slide comes into view during a swipe, and a focused window would end the swipe
        if imgui.begin("##seascape_overlay", None,
                       imgui.WindowFlags_.always_auto_resize | imgui.WindowFlags_.no_title_bar
                       | imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_saved_settings
                       | imgui.WindowFlags_.no_focus_on_appearing)[0]:
            imgui.push_item_width(overlay_w - em * 2.0)
            _shader_gui_side(narrow)
            imgui.pop_item_width()
        imgui.end()
        imgui.pop_style_var()


# ============================================================================
# Slide: Lorenz, an ImPlot3D attractor with two trajectories
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
        hello_imgui.set_item_is_live()  # the trajectories move on their own
    _lorenz_traj1.step(_lorenz_params)
    _lorenz_traj2.step(_lorenz_params)


def _lorenz_knobs(size: float, all_five: bool) -> None:
    """The parameters as knobs, on one row: sigma, rho and beta (then dt and the initial gap, when all_five)"""
    global _lorenz_initial_delta
    p = _lorenz_params
    _, p.sigma = _accent_knob("Sigma", p.sigma, 0.0, 30.0, "%.1f", size)
    imgui.set_item_tooltip("Rate of divergence (chaos level)")
    imgui.same_line()
    _, p.rho = _accent_knob("Rho", p.rho, 0.0, 60.0, "%.1f", size)
    imgui.set_item_tooltip("Size and shape of the attractor")
    imgui.same_line()
    _, p.beta = _accent_knob("Beta", p.beta, 0.0, 8.0, "%.2f", size)
    imgui.set_item_tooltip("Damping on vertical movement")
    if not all_five:
        return
    _, p.dt = _accent_knob("dt", p.dt, 0.001, 0.03, "%.3f", size)
    imgui.set_item_tooltip("Time step (smaller = smoother)")
    imgui.same_line()
    _, _lorenz_initial_delta = _accent_knob("Gap", _lorenz_initial_delta, 0.0, 0.2, "%.2f", size)
    imgui.set_item_tooltip("The initial gap between the two trajectories (Restart applies it)")


def _lorenz_gui_side():
    em = hello_imgui.em_size()
    pad = em * 0.5
    imgui.text("Butterfly effect")
    imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
    imgui.push_text_wrap_pos(imgui.get_window_width() - pad)
    imgui.text_wrapped(f"Two trajectories start {_lorenz_initial_delta:.2f} apart, then part ways: "
                       "deterministic chaos.")
    imgui.pop_text_wrap_pos()
    imgui.pop_style_color()
    imgui.spacing()
    avail = imgui.get_window_width() - 2 * pad
    spacing = imgui.get_style().item_spacing.x
    _lorenz_knobs(min(em * 3.6, (avail - 2 * spacing) / 3), all_five=True)
    imgui.spacing()
    if _accent_button(icons_fontawesome_4.ICON_FA_SYNC + "  Restart", ImVec2(avail, em * 1.8)):
        _lorenz_init_trajectories()
    imgui.spacing()
    imgui.separator()
    imgui.spacing()
    _manual_teaser("Every 3D plot type, with its code: the ImPlot3D manual", "manual_implot3d.py")


def _lorenz_gui_side_narrow():
    """Sigma, rho and beta, and the Restart button, on one row"""
    em = hello_imgui.em_size()
    pad = em * 0.5
    button_w = em * 5.5
    spacing = imgui.get_style().item_spacing.x
    size = min(em * 3.0, (imgui.get_window_width() - 2 * pad - button_w - 3 * spacing) / 3)
    top = imgui.get_cursor_pos_y()
    _lorenz_knobs(size, all_five=False)
    imgui.same_line()
    imgui.set_cursor_pos_y(top + em * 1.4)  # level with the knobs, below their titles
    if _accent_button(icons_fontawesome_4.ICON_FA_SYNC + " Restart", ImVec2(button_w, em * 1.8)):
        _lorenz_init_trajectories()


def _lorenz_slide_gui(content_size: ImVec2):
    em = hello_imgui.em_size()
    gap = em * 0.5
    if is_small_screen():  # the plot, then the parameters under it
        panel_h = em * 6.5
        _lorenz_gui_main(ImVec2(content_size.x, content_size.y - panel_h - gap))
        draw_side_panel("##lorenz_side", content_size.x, panel_h, _lorenz_gui_side_narrow)
        return
    main_side = content_size.y
    side_panel_w = content_size.x - main_side - gap
    _lorenz_gui_main(ImVec2(main_side, main_side))
    if side_panel_w > em * 4.0:
        imgui.same_line(0.0, gap)
        draw_side_panel("##lorenz_side", side_panel_w, main_side, _lorenz_gui_side)


# ============================================================================
# Slide: a tiny neural network learns two spirals (the explorable's widget, see explorables/neural_spiral)
# ============================================================================

@dataclass
class Network:
    """Two inputs, one hidden layer of H units (tanh), one output (a sigmoid: the probability of class 1)"""
    w1: np.ndarray  # (2, H)
    b1: np.ndarray  # (H,)
    w2: np.ndarray  # (H,)
    b2: float


def _nn_random(hidden: int, rng: np.random.Generator) -> Network:
    return Network(rng.normal(0, 1, (2, hidden)), rng.normal(0, 0.5, hidden),
                   rng.normal(0, 1 / np.sqrt(hidden), hidden), 0.0)


def _nn_forward(net: Network, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """n points x (n, 2) -> the answers of the hidden units h (n, H), the probabilities p (n,)"""
    h = np.tanh(x @ net.w1 + net.b1)
    p = 1 / (1 + np.exp(-(h @ net.w2 + net.b2)))
    return h, p


def _nn_loss(p: np.ndarray, y: np.ndarray) -> float:
    """The cross-entropy"""
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def _nn_step(net: Network, x: np.ndarray, y: np.ndarray, rate: float) -> None:
    """One step of gradient descent on all the points (backpropagation, by hand)"""
    h, p = _nn_forward(net, x)
    ds = (p - y) / len(y)
    da = np.outer(ds, net.w2) * (1 - h * h)
    net.w1 -= rate * (x.T @ da)
    net.b1 -= rate * da.sum(axis=0)
    net.w2 -= rate * (h.T @ ds)
    net.b2 -= rate * float(ds.sum())


def _make_spirals(n: int, turns: float, noise: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """n points (n, 2), and their classes (n,): 0 on the first spiral, 1 on the second"""
    radius = np.tile(np.linspace(0.08, 1.0, n // 2), 2)
    y = np.repeat([0.0, 1.0], n // 2)
    angle = 2 * np.pi * turns * radius + np.pi * y
    x = np.stack([radius * np.cos(angle), radius * np.sin(angle)], axis=1)
    return x + rng.normal(0, noise, x.shape), y


_NN_STEPS_PER_FRAME = 20
_NN_EXTENT = 1.2  # the plane shown: [-EXTENT, EXTENT] on both axes
_NN_GRID = 80  # the network's answer is drawn on a GRID x GRID heatmap
_nn_coords = np.linspace(-_NN_EXTENT, _NN_EXTENT, _NN_GRID)
_NN_GRID_POINTS = np.stack(np.meshgrid(_nn_coords, _nn_coords[::-1]), axis=-1).reshape(-1, 2)  # row 0 on top


class _SpiralState:
    def __init__(self) -> None:
        self.rng = np.random.default_rng(0)
        self.x, self.y = _make_spirals(200, 2.0, 0.02, self.rng)
        self.rate = 1.0
        self.training = True  # the slide trains as soon as it shows
        self.reset()

    def reset(self) -> None:
        self.net = _nn_random(16, self.rng)
        self.steps = 0
        self.losses: list[float] = []
        self.record()

    def record(self) -> None:
        _, p = _nn_forward(self.net, self.x)
        self.losses.append(_nn_loss(p, self.y))
        self.accuracy = float(np.mean((p > 0.5) == (self.y > 0.5)))

    def train(self) -> None:
        for _ in range(_NN_STEPS_PER_FRAME):
            _nn_step(self.net, self.x, self.y, self.rate)
        self.steps += _NN_STEPS_PER_FRAME
        self.record()


_spiral: Optional[_SpiralState] = None


def _spiral_colormap() -> int:
    """Muted red (class 0), dark grey where the network hesitates, muted blue (class 1): the points stay visible"""
    cmap = implot.get_colormap_index("answer")
    if cmap == -1:
        colors = np.array([[0.5, 0.15, 0.15, 1.0], [0.15, 0.15, 0.15, 1.0], [0.15, 0.25, 0.55, 1.0]], np.float32)
        cmap = implot.add_colormap("answer", colors, qual=False)
    return cmap


def _spiral_plane(state: _SpiralState, size: ImVec2) -> None:
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text | implot.Flags_.equal
    if implot.begin_plot("##plane", size, flags):
        implot.setup_axes_limits(-_NN_EXTENT, _NN_EXTENT, -_NN_EXTENT, _NN_EXTENT, imgui.Cond_.always)
        _, p = _nn_forward(state.net, _NN_GRID_POINTS)
        implot.push_colormap(_spiral_colormap())
        implot.plot_heatmap("##answer", p.reshape(_NN_GRID, _NN_GRID), 0.0, 1.0, "",
                            implot.Point(-_NN_EXTENT, -_NN_EXTENT), implot.Point(_NN_EXTENT, _NN_EXTENT))
        implot.pop_colormap()
        for label, cls, color in (("class 0", 0.0, ImVec4(1.0, 0.35, 0.35, 1.0)),
                                  ("class 1", 1.0, ImVec4(0.35, 0.6, 1.0, 1.0))):
            points = state.x[state.y == cls]
            implot.plot_scatter(label, points[:, 0].copy(), points[:, 1].copy(), spec=implot.Spec(
                marker=implot.Marker_.circle, marker_size=3, marker_fill_color=color,
                marker_line_color=ImVec4(1, 1, 1, 1)))
        implot.end_plot()
        hello_imgui.set_item_is_live(state.training)  # the network learns on its own while it trains


def _spiral_loss(state: _SpiralState, size: ImVec2) -> None:
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text
    if implot.begin_plot("Loss", size, flags):
        implot.setup_axes("step", "", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
        implot.plot_line("loss", np.array(state.losses), xscale=_NN_STEPS_PER_FRAME)
        implot.end_plot()


def _spiral_controls(state: _SpiralState, width: float) -> None:
    em = hello_imgui.em_size()
    if imgui.button("Pause" if state.training else "Train", ImVec2(em * 5, 0)):
        state.training = not state.training
    imgui.same_line()
    if imgui.button("Reset"):
        state.reset()
    imgui.same_line()
    imgui.text(f"step {state.steps}  |  loss {state.losses[-1]:.3f}  |  {state.accuracy:.0%} right")
    imgui.set_next_item_width(width - em * 9)
    _, state.rate = imgui.slider_float("learning rate", state.rate, 0.01, 10.0, "%.2f", imgui.SliderFlags_.logarithmic)


def _spiral_slide_gui(content_size: ImVec2):
    global _spiral
    if _spiral is None:
        _spiral = _SpiralState()
    state = _spiral
    if state.training:
        state.train()
    em = hello_imgui.em_size()
    gap = em * 0.5
    controls_h = em * 3.6
    plots_h = content_size.y - controls_h
    if is_small_screen():  # the plane, then the loss under it (when there is room for it)
        side = min(content_size.x, plots_h * 0.65)
        _spiral_plane(state, ImVec2(side, side))
        if plots_h - side - gap >= em * 5:
            _spiral_loss(state, ImVec2(content_size.x, plots_h - side - gap))
    else:
        side = min(plots_h, content_size.x * 0.55)
        _spiral_plane(state, ImVec2(side, side))
        imgui.same_line(0.0, gap)
        _spiral_loss(state, ImVec2(content_size.x - side - gap, side))
    _spiral_controls(state, content_size.x)


# ============================================================================
# Slide: ImmVision, an image and its edges, inspected (a Julia set computed with numpy)
# ============================================================================

def _julia_image(w: int, h: int, c: complex = -0.8 + 0.156j, max_iter: int = 100) -> np.ndarray:
    """A Julia set, colored by its smooth escape time: an RGB uint8 image (h, w, 3)"""
    xs = np.linspace(-1.6, 1.6, w)
    ys = np.linspace(-1.2, 1.2, h)
    z = (xs[None, :] + 1j * ys[:, None]).astype(np.complex128)
    count = np.full(z.shape, float(max_iter), np.float64)
    alive = np.ones(z.shape, bool)
    for i in range(max_iter):
        z[alive] = z[alive] ** 2 + c
        escaped = alive & (np.abs(z) > 4.0)
        count[escaped] = i + 1 - np.log2(np.log(np.abs(z[escaped])))
        alive &= ~escaped
    t = np.clip(count / max_iter, 0.0, 1.0)
    r = 9 * (1 - t) * t ** 3
    g = 15 * (1 - t) ** 2 * t ** 2
    b = 8.5 * (1 - t) ** 3 * t
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


if HAS_IMMVISION:
    _immvision_image: Optional[np.ndarray] = None
    _immvision_edges: Optional[np.ndarray] = None
    _immvision_params = immvision.ImageParams()
    _immvision_params_edges = immvision.ImageParams()
    _immvision_inited = False
    _immvision_animating = True
    _immvision_start_time = 0.0

    _ZOOM_IN_DURATION = 1.5
    _HOLD_DURATION = 1.5
    _ZOOM_OUT_DURATION = 1.5
    _PAUSE_DURATION = 3.0
    _TOTAL_CYCLE = _ZOOM_IN_DURATION + _HOLD_DURATION + _ZOOM_OUT_DURATION + _PAUSE_DURATION
    # Display pixels per image pixel at the end of the zoom: ImmVision draws the pixels' values from 36 (uint8
    # images) or 48 (float images), whatever the size of the image on screen
    _PIXEL_VALUES_ZOOM = 60.0
    _immvision_zoom_center = (0.0, 0.0)

    def _immvision_init():
        global _immvision_image, _immvision_edges, _immvision_inited, _immvision_zoom_center, _immvision_start_time
        _immvision_image = _julia_image(320, 240)
        gray = _immvision_image.astype(np.float32).mean(axis=2) / 255.0
        dy, dx = np.gradient(gray)
        _immvision_edges = np.hypot(dx, dy).astype(np.float32)  # a float image: ImmVision applies a colormap to it

        for params in (_immvision_params, _immvision_params_edges):
            params.show_options_panel = False
            params.show_image_info = False
            params.show_pixel_info = True
            params.show_zoom_buttons = True  # below the image: zoom in, out, to fit, at 1:1
            params.zoom_key = "intro_immvision"  # the two images zoom and pan together
        _immvision_params_edges.colormap_settings.colormap = "Viridis"

        h, w = _immvision_image.shape[:2]
        _immvision_zoom_center = (w * 0.56, h * 0.42)
        _immvision_start_time = immapp.clock_seconds()
        _immvision_inited = True

    def _immvision_zoom_progress() -> float:
        """From 0 (the whole image) to 1 (its pixels and their values): the whole image first, then the zoom in, a
        hold, and the zoom out"""
        elapsed = math.fmod(immapp.clock_seconds() - _immvision_start_time, _TOTAL_CYCLE)
        if elapsed < _PAUSE_DURATION:
            return 0.0
        elapsed -= _PAUSE_DURATION
        if elapsed < _ZOOM_IN_DURATION:
            t = elapsed / _ZOOM_IN_DURATION
            return 1.0 - (1.0 - t) * (1.0 - t)
        elapsed -= _ZOOM_IN_DURATION
        if elapsed < _HOLD_DURATION:
            return 1.0
        elapsed -= _HOLD_DURATION
        if elapsed < _ZOOM_OUT_DURATION:
            t = elapsed / _ZOOM_OUT_DURATION
            return 1.0 - t * t
        return 0.0

    def _immvision_check_user_interaction() -> bool:
        hovering = (_immvision_params.mouse_info.is_mouse_hovering
                    or _immvision_params_edges.mouse_info.is_mouse_hovering)
        return hovering and (imgui.is_mouse_dragging(0) or imgui.get_io().mouse_wheel != 0.0)

    def _immvision_gui_main(size: ImVec2, both: bool):
        global _immvision_animating
        if not _immvision_inited:
            _immvision_init()
        assert _immvision_image is not None and _immvision_edges is not None

        if _immvision_animating and _immvision_check_user_interaction():
            _immvision_animating = False

        em = hello_imgui.em_size()
        img_h, img_w = _immvision_image.shape[:2]
        display_w = int(size.x * 0.5 - em) if both else int(size.x)
        display_h = int(min(display_w * img_h / img_w, size.y))
        display_w = int(display_h * img_w / img_h)
        _immvision_params.image_display_size = (display_w, display_h)
        _immvision_params_edges.image_display_size = (display_w, display_h)

        if _immvision_animating:
            # From the whole image (the zoom that fits it, centered) to the pixels around the zoom target
            fit_zoom = display_w / img_w
            t = _immvision_zoom_progress()
            zoom = fit_zoom + (max(_PIXEL_VALUES_ZOOM, fit_zoom) - fit_zoom) * t
            center = (img_w * 0.5 + (_immvision_zoom_center[0] - img_w * 0.5) * t,
                      img_h * 0.5 + (_immvision_zoom_center[1] - img_h * 0.5) * t)
            _immvision_params.zoom_pan_matrix = immvision.make_zoom_pan_matrix(
                center, zoom, _immvision_params.image_display_size)
            _immvision_params_edges.zoom_pan_matrix = _immvision_params.zoom_pan_matrix

        immvision.image("Julia set##intro", _immvision_image, _immvision_params)
        if both:
            imgui.same_line()
            immvision.image("Its edges##intro", _immvision_edges, _immvision_params_edges)
        hello_imgui.set_item_is_live(_immvision_animating)  # the zoom moves on its own

    def _immvision_gui_side():
        global _immvision_animating, _immvision_start_time
        imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
        imgui.text_wrapped("Drag to pan, scroll to zoom: at a high zoom, the pixels show their values")
        imgui.pop_style_color()
        if not _immvision_animating:
            imgui.same_line()
            if imgui.small_button("Restart the animation"):
                _immvision_animating = True
                _immvision_start_time = immapp.clock_seconds()

    def _immvision_slide_gui(content_size: ImVec2):
        em = hello_imgui.em_size()
        narrow = is_small_screen()
        # The zoom buttons under the images, then the hint (on two lines on a phone)
        side_h = em * (5.0 if narrow else 3.8)
        _immvision_gui_main(ImVec2(content_size.x, content_size.y - side_h), both=not narrow)
        _immvision_gui_side()


# ============================================================================
# Slide: a node editor, an image through a pipeline of filters (a mini version of
# demos_node_editor/demo_node_editor_image_pipeline.py, with numpy filters)
# ============================================================================

PIPE_IMAGE_SIZE = (200, 150)  # the image that enters the pipeline: width, height (a half of the pictures)
PIPE_PICTURE = "images/golden_gate.jpg"  # an asset; from picsum.photos (Chris Brignola, Unsplash), copied
PIPE_RANDOM_URL = "https://picsum.photos/400/300?random={}"  # a random picture (the number defeats the cache)
PIPE_IMAGE_WIDTH_EM = 7.0  # the width of the images in the nodes (it gives the nodes their width)
PIPE_LINK_COLOR = ImVec4(0.4, 0.75, 1.0, 1.0)
PIPE_UNLINKED = ImVec4(0.3, 0.3, 0.3, 1.0)


def _pipe_blur(image: np.ndarray, sigma: float) -> np.ndarray:
    """A gaussian blur, in two passes (one per axis), the borders repeated"""
    if sigma < 0.3:
        return image
    radius = int(math.ceil(3.0 * sigma))
    kernel = np.exp(-0.5 * (np.arange(-radius, radius + 1) / sigma) ** 2)
    kernel /= kernel.sum()
    out = image.astype(np.float32)
    for axis in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[axis] = (radius, radius)
        padded = np.pad(out, pad, mode="edge")
        n = out.shape[axis]
        acc = np.zeros_like(out)
        for k, weight in enumerate(kernel):
            acc += weight * np.take(padded, np.arange(k, k + n), axis=axis)
        out = acc
    return out.clip(0, 255).astype(np.uint8)


def _pipe_edges(image: np.ndarray) -> np.ndarray:
    """The magnitude of the gradient of the gray image, scaled to 0..255: a gray image"""
    gray = image.astype(np.float32).mean(axis=2) if image.ndim == 3 else image.astype(np.float32)
    gy, gx = np.gradient(gray)
    magnitude = np.hypot(gx, gy)
    edges: np.ndarray = (255.0 * magnitude / max(float(magnitude.max()), 1e-6)).astype(np.uint8)
    return edges


def _pipe_overlay(image: np.ndarray, edges: np.ndarray, strength: float) -> np.ndarray:
    """The edges painted in yellow over the image"""
    rgb = image if image.ndim == 3 else np.repeat(image[..., None], 3, axis=2)
    gray_edges = edges if edges.ndim == 2 else edges.mean(axis=2)
    if rgb.shape[:2] != gray_edges.shape:
        return rgb
    mask = (gray_edges.astype(np.float32) / 255.0 * strength * 2.0).clip(0.0, 1.0)[..., None]
    out = rgb.astype(np.float32) * (1.0 - mask) + np.array([255.0, 220.0, 60.0], np.float32) * mask
    overlaid: np.ndarray = out.astype(np.uint8)
    return overlaid


def _half_size(image: np.ndarray) -> np.ndarray:
    """The image at half its size (each pixel the mean of 2 x 2): the filters run four times faster"""
    h, w = image.shape[0] // 2 * 2, image.shape[1] // 2 * 2
    quads = image[:h, :w].astype(np.float32).reshape(h // 2, 2, w // 2, 2, -1)
    half: np.ndarray = quads.mean(axis=(1, 3)).astype(np.uint8)
    return half


def _pipe_picture_from_bytes(file_bytes: bytes) -> Optional[np.ndarray]:
    """A picture file's bytes decoded, at half size; None when they are not a picture, or when this build of the bundle
    has no decoder (a Pyodide wheel older than immapp.decode_image)"""
    if not hasattr(immapp, "decode_image"):
        return None
    try:
        return _half_size(immapp.decode_image(file_bytes))
    except ValueError:
        return None


def _pipe_default_picture() -> np.ndarray:
    """The asset's picture, or a Julia set when it cannot be read"""
    path = hello_imgui.asset_file_full_path(PIPE_PICTURE, assert_if_not_found=False)
    picture = None
    if path:
        with open(path, "rb") as f:
            picture = _pipe_picture_from_bytes(f.read())
    if picture is None:
        picture = _julia_image(PIPE_IMAGE_SIZE[0], PIPE_IMAGE_SIZE[1], -0.8 + 0.156j, 60)
    return picture


class _PipeNode:
    """A node of the pipeline: its pins, its parameter, and its result (computed again when an input or the
    parameter changes)"""

    def __init__(self, kind: str, inputs: list[str], param: Optional[float]) -> None:
        self.kind = kind
        self.id = node_ed.NodeId.create()
        self.inputs = [(node_ed.PinId.create(), name) for name in inputs]
        self.output = node_ed.PinId.create()
        self.param = param  # the blur's sigma, the overlay's strength (None: no parameter)
        self.result: Optional[np.ndarray] = None
        self.key: Any = None  # what the result was computed from
        self.version = 0  # one more at each new result: its image is sent again to the GPU
        self.shown_version = -1
        # The Image node: its picture, and the download of a random one
        self.picture: Optional[np.ndarray] = None
        self.picture_version = 0
        self.download: Optional[immapp.Download] = None
        self.download_count = 0
        self.download_error = ""

    def compute(self, inputs: list[np.ndarray]) -> np.ndarray:
        if self.kind == "Image":
            if self.picture is None:
                self.picture = _pipe_default_picture()
            return self.picture
        if self.kind == "Blur":
            assert self.param is not None
            return _pipe_blur(inputs[0], self.param)
        if self.kind == "Edges":
            return _pipe_edges(inputs[0])
        assert self.param is not None
        return _pipe_overlay(inputs[0], inputs[1], self.param)  # Overlay


class _PipeGraph:
    def __init__(self) -> None:
        julia = _PipeNode("Image", [], None)
        blur = _PipeNode("Blur", ["in"], 1.5)
        edges = _PipeNode("Edges", ["in"], None)
        overlay = _PipeNode("Overlay", ["image", "edges"], 0.8)
        self.nodes = [julia, blur, edges, overlay]
        # Two levels, so that the link from the image to the overlay passes under the blur and the edges
        for node, position in ((julia, ImVec2(0, 6)), (blur, ImVec2(11, 0)), (edges, ImVec2(22, 0)),
                               (overlay, ImVec2(33, 11))):
            node_ed.set_node_position(node.id, position * em_size())  # in the editor's coordinates
        self.links: list[tuple[node_ed.LinkId, node_ed.PinId, node_ed.PinId]] = []  # (id, an output, an input)
        self.connect(julia.output, blur.inputs[0][0])
        self.connect(blur.output, edges.inputs[0][0])
        self.connect(julia.output, overlay.inputs[0][0])
        self.connect(edges.output, overlay.inputs[1][0])

    def connect(self, output: node_ed.PinId, input: node_ed.PinId) -> None:
        self.links = [link for link in self.links if link[2] != input]  # an input receives one link at most
        self.links.append((node_ed.LinkId.create(), output, input))

    def node_of_pin(self, pin: node_ed.PinId) -> Optional[_PipeNode]:
        for node in self.nodes:
            if pin == node.output or any(pin == p for p, _ in node.inputs):
                return node
        return None

    def is_output(self, pin: node_ed.PinId) -> bool:
        return any(pin == node.output for node in self.nodes)

    def source(self, input: node_ed.PinId) -> Optional[_PipeNode]:
        """The node whose output reaches this input"""
        for _, output, linked_input in self.links:
            if linked_input == input:
                return self.node_of_pin(output)
        return None

    def feeds(self, node: _PipeNode, other: _PipeNode) -> bool:
        """True if `node` is `other`, or feeds it through links"""
        if node is other:
            return True
        sources = [self.source(pin) for pin, _ in other.inputs]
        return any(s is not None and self.feeds(node, s) for s in sources)

    def evaluate(self, node: _PipeNode) -> Optional[np.ndarray]:
        """The node's result, computed again only when its parameter or one of its sources changed"""
        sources = [self.source(pin) for pin, _ in node.inputs]
        inputs = [self.evaluate(s) if s is not None else None for s in sources]
        if any(i is None for i in inputs):
            if node.result is not None:
                node.result, node.key = None, None
            return None
        key = (node.param, node.picture_version, tuple((id(s), s.version) for s in sources if s is not None))
        if key != node.key:
            node.result = node.compute([i for i in inputs if i is not None])
            node.key = key
            node.version += 1
        return node.result


_pipe_editor: Optional[node_ed.EditorContext] = None
_pipe_graph: Optional[_PipeGraph] = None
_pipe_frames = 0
_pipe_size = ImVec2(0, 0)


def _pipe_pin(pin: node_ed.PinId, kind: node_ed.PinKind, linked: bool) -> None:
    node_ed.begin_pin(pin, kind)
    node_ed.pin_pivot_alignment(ImVec2(0.5, 0.5))  # the links reach the center of the circle
    node_ed.pin_pivot_size(ImVec2(0, 0))
    radius = em_size(0.4)
    top_left = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(2 * radius, 2 * radius))
    center = top_left + ImVec2(radius, radius)
    draw_list = imgui.get_window_draw_list()
    draw_list.add_circle_filled(center, radius, imgui.get_color_u32(PIPE_LINK_COLOR if linked else PIPE_UNLINKED))
    draw_list.add_circle(center, radius, imgui.get_color_u32(imgui.Col_.text), thickness=1.5)
    node_ed.end_pin()


def _pipe_node(graph: _PipeGraph, node: _PipeNode) -> None:
    width = em_size(PIPE_IMAGE_WIDTH_EM)
    node_ed.begin_node(node.id)
    imgui.push_id(node.id.id())
    imgui.text(node.kind)
    for pin, name in node.inputs:  # the inputs, on the left
        _pipe_pin(pin, node_ed.PinKind.input, graph.source(pin) is not None)
        imgui.same_line()
        imgui.text(name)
    if node.kind == "Image":
        _pipe_random_picture(node, width)
    if node.param is not None:
        imgui.set_next_item_width(width)
        if node.kind == "Blur":
            _, node.param = imgui.slider_float("##param", node.param, 0.0, 4.0, "sigma %.1f")
        else:
            _, node.param = imgui.slider_float("##param", node.param, 0.0, 1.0, "strength %.2f")
    height = width * PIPE_IMAGE_SIZE[1] / PIPE_IMAGE_SIZE[0]
    if node.result is not None:
        immvision.image_display("##image", node.result, (int(width), int(height)),
                                refresh_image=node.version != node.shown_version)
        node.shown_version = node.version
    else:
        imgui.dummy(ImVec2(width, height * 0.5))
        imgui.text_disabled("(no input)")
    imgui.begin_horizontal("output", ImVec2(width, 0))  # the output, on the right
    imgui.spring()
    imgui.text("out")
    _pipe_pin(node.output, node_ed.PinKind.output, any(link[1] == node.output for link in graph.links))
    imgui.end_horizontal()
    imgui.pop_id()
    node_ed.end_node()


def _pipe_random_picture(node: _PipeNode, width: float) -> None:
    """The Image node's button: a random picture from picsum.photos, downloaded without blocking the GUI"""
    if not hasattr(immapp, "decode_image"):
        return  # this build cannot decode a download (a Pyodide wheel older than immapp.decode_image)
    if node.download is not None:
        if not node.download.done:
            imgui.text_disabled("Downloading...")
            hello_imgui.set_item_is_live()  # the download ends on its own
            return
        picture = _pipe_picture_from_bytes(node.download.data) if not node.download.error else None
        node.download_error = "" if picture is not None else "No picture: offline?"
        if picture is not None:
            node.picture = picture
            node.picture_version += 1
        node.download = None
    if imgui.button(icons_fontawesome_4.ICON_FA_RANDOM + " Random", ImVec2(width, 0)):
        node.download_count += 1
        node.download = immapp.start_download(PIPE_RANDOM_URL.format(node.download_count))
    if node.download_error:
        imgui.text_disabled(node.download_error)


def _pipe_push_theme_colors() -> int:
    """The editor's colors from the ImGui theme: its own are dark, and its text unreadable under a light theme.
    Returns how many colors were pushed"""
    window = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    text = imgui.get_style_color_vec4(imgui.Col_.text)

    def towards_text(t: float, alpha: float = 1.0) -> ImVec4:
        return ImVec4(window.x + (text.x - window.x) * t, window.y + (text.y - window.y) * t,
                      window.z + (text.z - window.z) * t, alpha)

    colors = [(node_ed.StyleColor.bg, towards_text(0.04)), (node_ed.StyleColor.grid, towards_text(0.5, 0.12)),
              (node_ed.StyleColor.node_bg, towards_text(0.10)), (node_ed.StyleColor.node_border, towards_text(0.5))]
    for index, color in colors:
        node_ed.push_style_color(index, color)
    return len(colors)


def _pipe_new_links(graph: _PipeGraph) -> None:
    """A link dragged from a pin to another: accepted from an output to an input, unless it makes a loop"""
    if node_ed.begin_create(PIPE_LINK_COLOR, 2.0):
        start_id, end_id = node_ed.PinId(), node_ed.PinId()
        if node_ed.query_new_link(start_id, end_id):
            output, input = (end_id, start_id) if graph.is_output(end_id) else (start_id, end_id)
            output_node, input_node = graph.node_of_pin(output), graph.node_of_pin(input)
            if output_node is not None and input_node is not None:
                if graph.is_output(output) and not graph.is_output(input) \
                        and not graph.feeds(input_node, output_node):
                    if node_ed.accept_new_item():
                        graph.connect(output, input)
                else:
                    node_ed.reject_new_item(ImVec4(1.0, 0.3, 0.3, 1.0), 2.0)
        node_ed.end_create()


def _pipe_deletions(graph: _PipeGraph) -> None:
    if node_ed.begin_delete():
        link_id = node_ed.LinkId()
        while node_ed.query_deleted_link(link_id):
            if node_ed.accept_deleted_item():
                graph.links = [link for link in graph.links if link[0] != link_id]
        node_id = node_ed.NodeId()
        while node_ed.query_deleted_node(node_id):
            node_ed.reject_deleted_item()  # the four nodes stay
        node_ed.end_delete()


def _pipeline_slide_gui(content_size: ImVec2):
    global _pipe_editor, _pipe_graph, _pipe_frames, _pipe_size
    em = hello_imgui.em_size()
    if _pipe_editor is None:
        config = node_ed.Config()
        config.settings_file = None  # the slide places its nodes: nothing to save
        _pipe_editor = node_ed.create_editor(config)
    previous_editor = node_ed.get_current_editor()
    node_ed.set_current_editor(_pipe_editor)
    hint_h = em * (2.8 if is_small_screen() else 1.5)
    editor_size = ImVec2(content_size.x, content_size.y - hint_h)
    nb_colors = _pipe_push_theme_colors()
    node_ed.begin("##pipeline", editor_size)
    if _pipe_graph is None:
        _pipe_graph = _PipeGraph()
    for node in _pipe_graph.nodes:
        _pipe_graph.evaluate(node)
    for node in _pipe_graph.nodes:
        _pipe_node(_pipe_graph, node)
    for link_id, output, input in _pipe_graph.links:
        node_ed.link(link_id, output, input, PIPE_LINK_COLOR, 3.0)
    _pipe_new_links(_pipe_graph)
    _pipe_deletions(_pipe_graph)
    node_ed.end()
    node_ed.pop_style_color(nb_colors)
    # Fit the graph in the view once the editor knows the size of the nodes (the third frame), and when the slide's
    # size changes (a phone turned). The navigation functions work after end().
    size_changed = abs(_pipe_size.x - editor_size.x) > 1.0 or abs(_pipe_size.y - editor_size.y) > 1.0
    if _pipe_frames == 2 or (size_changed and _pipe_frames > 2):
        node_ed.navigate_to_content(0.0)
    _pipe_size = editor_size
    _pipe_frames += 1
    if previous_editor is not None:  # the app's own editor, if it has one
        node_ed.set_current_editor(previous_editor)
    imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
    imgui.text_wrapped("Move a slider: the nodes downstream follow. Drag from a pin to another to link them; "
                       "right-drag to pan, the wheel to zoom.")
    imgui.pop_style_color()


# ============================================================================
# Slide: the drum sequencer (a table with angled headers, checkboxes, a toggle, a knob, a color wheel)
# ============================================================================

_table_instruments = ["kick", "snare", "hihat", "open-hh", "tom", "clap", "rim", "crash"]
_table_num_instr = 8
_table_num_beats = 16
_table_pattern: List[List[bool]] = []
_table_volume = [8.0, 7.0, 5.0, 4.0, 6.0, 7.0, 5.0, 3.0]  # per instrument, 0 to 10
_table_inited = False
_table_playhead = 0
_table_bpm = 140.0
_table_playing = True
_table_accum = 0.0
_table_hl_color = ImVec4(0.3, 0.5, 1.0, 0.25)


def _table_init():
    """A pattern of 8 steps, played twice"""
    global _table_pattern, _table_inited
    bar = [[False] * _table_num_instr for _ in range(8)]
    bar[0][0] = bar[4][0] = True   # kick
    bar[2][1] = bar[6][1] = True   # snare
    for i in range(0, 8, 2):
        bar[i][2] = True           # hihat
    bar[1][3] = bar[5][3] = True   # open-hh
    bar[3][4] = True               # tom
    bar[6][5] = True               # clap
    bar[4][6] = bar[7][6] = True   # rim
    bar[0][7] = True               # crash
    _table_pattern = [list(bar[row % 8]) for row in range(_table_num_beats)]
    _table_pattern[15][4] = _table_pattern[14][4] = True  # a tom fill at the end
    _table_inited = True


def _table_update():
    global _table_playhead, _table_accum
    if not _table_playing:
        return
    dt = min(imgui.get_io().delta_time, 0.1)  # clamp to prevent drift when tab is in background
    _table_accum += dt
    beat_interval = 60.0 / _table_bpm
    if _table_accum >= beat_interval:
        _table_accum = 0.0  # reset instead of subtract to prevent accumulated drift
        _table_playhead = (_table_playhead + 1) % _table_num_beats


def _table_gui_main(size: ImVec2, num_instr: int):
    if not _table_inited:
        _table_init()
    _table_update()

    total_cols = num_instr + 1
    flags = (imgui.TableFlags_.sizing_fixed_fit
             | imgui.TableFlags_.scroll_x | imgui.TableFlags_.scroll_y
             | imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_inner_h
             | imgui.TableFlags_.highlight_hovered_column)

    if imgui.begin_table("##drum_seq", total_cols, flags, size):
        imgui.table_setup_column("Beat", imgui.TableColumnFlags_.no_hide)
        for n in range(num_instr):
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

            for col in range(num_instr):
                if imgui.table_set_column_index(col + 1):
                    if is_playhead:
                        imgui.table_set_bg_color(imgui.TableBgTarget_.cell_bg, hl_col)
                    imgui.push_id(col)
                    _, _table_pattern[row][col] = imgui.checkbox("", _table_pattern[row][col])
                    imgui.pop_id()
            imgui.pop_id()

        # The last row: a volume knob per instrument
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        imgui.align_text_to_frame_padding()
        imgui.text_disabled("Vol")
        knob_flags = imgui_knobs.ImGuiKnobFlags_.no_title | imgui_knobs.ImGuiKnobFlags_.no_input
        for col in range(num_instr):
            if imgui.table_set_column_index(col + 1):
                _, _table_volume[col] = imgui_knobs.knob(
                    f"##vol{col}", _table_volume[col], 0.0, 10.0, 0.0, "%.0f",
                    imgui_knobs.ImGuiKnobVariant_.wiper_dot, imgui.get_frame_height(), knob_flags)
        imgui.end_table()
        hello_imgui.set_item_is_live(_table_playing)  # the playhead moves on its own


def _table_play_toggle():
    global _table_playing
    em = hello_imgui.em_size()
    toggle_config = imgui_toggle.material_style()
    toggle_config.size = ImVec2(em * 2.5, em * 1.2)
    _, _table_playing = imgui_toggle.toggle("##play", _table_playing, toggle_config)


def _table_bpm_knob(size_em: float):
    global _table_bpm
    _, _table_bpm = _accent_knob("##bpm", _table_bpm, 60.0, 300.0, "%.0f", hello_imgui.em_size(size_em))


def _table_gui_side():
    """Play, the tempo and the highlight's color on one row; below, the picture of the manual"""
    global _table_hl_color
    em = hello_imgui.em_size()
    imgui.begin_group()
    imgui.text("Play")
    _table_play_toggle()
    imgui.end_group()
    imgui.same_line(0.0, em * 1.5)
    imgui.begin_group()
    imgui.text("Tempo")
    _table_bpm_knob(3.5)
    imgui.end_group()
    imgui.same_line(0.0, em * 1.5)
    imgui.begin_group()
    imgui.text("Highlight")
    picker_flags = (imgui.ColorEditFlags_.no_side_preview
                    | imgui.ColorEditFlags_.no_inputs
                    | imgui.ColorEditFlags_.no_label
                    | imgui.ColorEditFlags_.alpha_bar
                    | imgui.ColorEditFlags_.picker_hue_wheel)
    imgui.set_next_item_width(em * 7.0)
    _, _table_hl_color = imgui.color_picker4("##hl_wheel", _table_hl_color, picker_flags)
    imgui.end_group()
    _IntroAutomations.show_link("More info: complex app layout", _IntroAutomations.show_docking)

    # The manual of all the widgets, below: as wide as the panel, or as tall as the space left
    imgui.spacing()
    imgui.separator()
    imgui.spacing()
    _manual_teaser("All of Dear ImGui's widgets, with their code: the interactive manual", "manual_imgui.py")


def _table_gui_side_narrow():
    """Play and the tempo, on one line"""
    imgui.text("Play")
    imgui.same_line()
    _table_play_toggle()
    imgui.same_line(0.0, hello_imgui.em_size(1.5))
    imgui.text("Tempo")
    imgui.same_line()
    _table_bpm_knob(2.5)


def _table_slide_gui(content_size: ImVec2):
    em = hello_imgui.em_size()
    gap = em * 0.5
    if is_small_screen():  # six instruments fit the width; the controls under the table
        panel_h = em * 4.6  # the tempo knob and its value under it
        _table_gui_main(ImVec2(content_size.x, content_size.y - panel_h - gap), 6)
        draw_side_panel("##table_side", content_size.x, panel_h, _table_gui_side_narrow)
        return
    table_w = min(em * 21.0, content_size.x * 0.5)  # the width of its columns and their angled headers
    _table_gui_main(ImVec2(table_w, content_size.y), _table_num_instr)
    imgui.same_line(0.0, gap)
    draw_side_panel("##table_side", content_size.x - table_w - gap, content_size.y, _table_gui_side)


# ============================================================================
# Slide: markdown, the source and its live render
# ============================================================================

_MARKDOWN_SAMPLE = r"""
## Dear ImGui Bundle — live markdown
> *Edit the panel on the left and watch the right update in real time.*
### What you can write
- **Bold**, *italic*, ~~strike~~, <u>underline</u>, <mark>highlight</mark>, `code`
- Keyboard shortcuts: <kbd>Ctrl</kbd>+<kbd>S</kbd>, <kbd>Cmd</kbd>+<kbd>K</kbd>
- Chemistry & exponents: H<sub>2</sub>O, x<sup>2</sup>+y<sup>2</sup>=r<sup>2</sup>
- [Clickable links](https://github.com/pthom/imgui_bundle) and bare URLs: https://dearimgui.org
### A little code
```python
from imgui_bundle import imgui, immapp
immapp.run(lambda: imgui.text("Hello, World!"))
```
### A little math
Euler's identity $e^{i\pi} + 1 = 0$ generalizes to:
$$
e^{i\theta} = \cos\theta + i\sin\theta
$$
### A diagram
```mermaid
flowchart LR
    A[Markdown] --> B{rich_md}
    B --> C[Text and math]
    B --> D[Diagrams]
```
## Tables with *resizable* columns and *alignment*
|Id| Library    | What it does        |
|-:|:----------:|---------------------|
|1| ImGui      | Core widgets        |
|2| ImPlot     | 2D plots            |
|3| ImPlot3D   | 3D plots            |
|4| ImmVision  | Image analysis      |
|5| rich_md   | This renderer       |
> [!TIP]
> Click the triangle below to unfold. Try adding your own collapsible section.
<details>
<summary>Images, including from the web</summary>
<img src="https://picsum.photos/id/1019/200/130" height="100" />
</details>
"""

_markdown_text_editor: ed.TextEditor = None  # type: ignore
_markdown_editor_initialized = False
_markdown_show_source = False  # on a phone: the source or the render, one at a time


def _init_markdown_editor():
    global _markdown_text_editor, _markdown_editor_initialized
    _markdown_text_editor = ed.TextEditor()
    _markdown_text_editor.set_text(_MARKDOWN_SAMPLE)
    _markdown_text_editor.set_language(ed.TextEditor.Language.markdown())
    _markdown_text_editor.set_palette(ed.TextEditor.get_dark_palette())
    _markdown_editor_initialized = True


def _markdown_source(size: ImVec2):
    em = hello_imgui.em_size()
    panel_bg(imgui.get_cursor_screen_pos(), size)
    imgui.begin_child("##md_source", size, False, imgui.WindowFlags_.no_background)
    code_font = rich_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size * 0.9)
    _markdown_text_editor.render("##md_editor", ImVec2(size.x - em * 0.2, size.y))
    imgui.pop_font()
    imgui.end_child()


def _markdown_rendered(size: ImVec2):
    """The render, as a document: its table of contents beside it (or above it, when narrow)"""
    rich_md.render_document("##md_rendered", _markdown_text_editor.get_text(), size)


def _markdown_slide_gui(content_size: ImVec2):
    global _markdown_show_source
    if not _markdown_editor_initialized:
        _init_markdown_editor()
    em = hello_imgui.em_size()
    gap = em * 0.5
    if is_small_screen():  # one panel at a time
        if imgui.radio_button("Rendered", not _markdown_show_source):
            _markdown_show_source = False
        imgui.same_line()
        if imgui.radio_button("Source", _markdown_show_source):
            _markdown_show_source = True
        size = ImVec2(content_size.x, content_size.y - imgui.get_frame_height_with_spacing())
        if _markdown_show_source:
            _markdown_source(size)
        else:
            _markdown_rendered(size)
        return
    half_w = (content_size.x - gap) * 0.5
    _markdown_source(ImVec2(half_w, content_size.y))
    imgui.same_line(0, gap)
    _markdown_rendered(ImVec2(half_w, content_size.y))


# ============================================================================
# Slide: a whole app, the heart haiku (demos_immapp/haiku_implot_heart.py): its complete code, and beside it the
# app that this code runs
# ============================================================================

_HAIKU_PYTHON = r'''import time
import numpy as np
from imgui_bundle import implot, imgui_knobs, imgui, immapp, hello_imgui

# Fill x and y whose plot is a heart
vals = np.arange(0, np.pi * 2, 0.01)
x = np.power(np.sin(vals), 3) * 16
y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)
# Heart pulse rate and time tracking
phase = 0.0
t0 = time.time() + 0.2
heart_pulse_rate = 80.0
heart_thickness = 0.15
LARGEST_SCALE = 0.9 * 1.3  # of the heart: the pulse scales it up to 0.9, the thickness up to 1.3

def gui():
    global heart_pulse_rate, phase, t0, heart_thickness
    t = time.time()
    phase += (t - t0) * heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(phase)
    t0 = t

    if implot.begin_plot("Heart", immapp.em_to_vec2(21, 21)):
        implot.setup_axes_limits(x.min() * LARGEST_SCALE, x.max() * LARGEST_SCALE,
                                 y.min() * LARGEST_SCALE, y.max() * LARGEST_SCALE)
        for k2 in np.arange(1 - heart_thickness, 1 + heart_thickness, 0.01):
            implot.plot_line("", x * k * k2, y * k * k2)  # some thickness
        implot.end_plot()
        hello_imgui.set_item_is_live()  # the heart beats on its own

    _, heart_pulse_rate = imgui_knobs.knob("Pulse", heart_pulse_rate, 30, 180,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=immapp.em_size(4.0))
    imgui.same_line()
    _, heart_thickness = imgui_knobs.knob("Line Thickness", heart_thickness, 0.01, 0.3,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=immapp.em_size(4.0))

if __name__ == "__main__":
    immapp.run(gui, window_size=(380, 470), with_implot=True)
'''

_HAIKU_CPP = r'''#include "imgui.h"
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include "immapp/immapp.h"
#include <algorithm>
#include <cmath>

const double LARGEST_SCALE = 0.9 * 1.3;  // of the heart: the pulse scales it up to 0.9, the thickness up to 1.3

std::vector<double> VectorTimesK(const std::vector<double>& values, double k) {
    std::vector<double> r(values.size(), 0.);
    for (size_t i = 0; i < values.size(); ++i)
        r[i] = k * values[i];
    return r;
}

void Gui() {
    // Fill x and y whose plot is a heart
    const double pi = 3.1415926535;
    static std::vector<double> x, y;
    if (x.empty()) {
        for (double t = 0.; t < pi * 2.; t += 0.01) {
            x.push_back(pow(sin(t), 3.) * 16.);
            y.push_back(13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t));
        }
    }
    // Heart pulse rate and time tracking
    static double phase = 0., t0 = ImmApp::ClockSeconds() + 0.2;
    static float heart_pulse_rate = 80., heart_thickness = 0.15;
    double t = ImmApp::ClockSeconds();
    phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.);
    double k = 0.8 + 0.1 * cos(phase);
    t0 = t;

    if (ImPlot::BeginPlot("Heart", ImmApp::EmToVec2(21, 21))) {
        auto [xMin, xMax] = std::minmax_element(x.begin(), x.end());
        auto [yMin, yMax] = std::minmax_element(y.begin(), y.end());
        ImPlot::SetupAxesLimits(*xMin * LARGEST_SCALE, *xMax * LARGEST_SCALE,
                                *yMin * LARGEST_SCALE, *yMax * LARGEST_SCALE);
        for (double k2 = 1 - heart_thickness; k2 <= 1. + heart_thickness; k2 += 0.01) {
            auto xk = VectorTimesK(x, k * k2), yk = VectorTimesK(y, k * k2);
            ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size());  // some thickness
        }
        ImPlot::EndPlot();
        HelloImGui::SetItemIsLive();  // the heart beats on its own
    }

    ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
    ImGui::SameLine();
    ImGuiKnobs::Knob("Line Thickness", &heart_thickness, 0.01, 0.3);
}

int main() {
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = Gui;
    runnerParams.windowTitle = "Hello!";
    runnerParams.windowSize = {380, 470};
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    ImmApp::Run(runnerParams, addOnsParams);
}
'''

_haiku_app: Optional[dict[str, Any]] = None  # the globals of the Python code above, run once (its gui() is the app)
_haiku_editors: list[Any] = []  # the code, in a read-only editor: [Python, C++]
_haiku_view = -1  # 0: Python, 1: C++ (on a phone, 2: the app); -1 until the first frame: the app on a phone


def _haiku_init() -> None:
    global _haiku_app
    _haiku_app = {"__name__": "haiku_implot_heart"}  # not "__main__": the code defines gui(), and does not run it
    exec(_HAIKU_PYTHON, _haiku_app)
    for code, language in ((_HAIKU_PYTHON, ed.TextEditor.Language.python()),
                           (_HAIKU_CPP, ed.TextEditor.Language.cpp())):
        editor = ed.TextEditor()
        editor.set_text(code)
        editor.set_language(language)
        editor.set_palette(ed.TextEditor.get_dark_palette())
        editor.set_read_only_enabled(True)
        editor.set_show_whitespaces_enabled(False)  # a page of code, to be read
        _haiku_editors.append(editor)


def _haiku_code(index: int, size: ImVec2) -> None:
    panel_bg(imgui.get_cursor_screen_pos(), size)
    imgui.begin_child("##haiku_code", size, False, imgui.WindowFlags_.no_background)
    code_font = rich_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size * 0.85)
    _haiku_editors[index].render("##haiku_editor", size)
    imgui.pop_font()
    imgui.end_child()


def _haiku_running_app(size: ImVec2) -> None:
    """The app that the Python code runs: its gui(), in a frame"""
    assert _haiku_app is not None
    panel_bg(imgui.get_cursor_screen_pos(), size, 0.04, 0.3)
    imgui.begin_child("##haiku_app", size, False, imgui.WindowFlags_.no_background)
    imgui.set_cursor_pos(ImVec2(hello_imgui.em_size(0.5), hello_imgui.em_size(0.5)))
    imgui.begin_group()
    _haiku_app["gui"]()
    imgui.end_group()
    imgui.end_child()


def _haiku_slide_gui(content_size: ImVec2):
    global _haiku_view
    if _haiku_app is None:
        _haiku_init()
    em = hello_imgui.em_size()
    gap = em * 0.5
    narrow = is_small_screen()
    labels = ["Python", "C++"] + (["The app"] if narrow else [])
    if _haiku_view < 0:
        _haiku_view = 2 if narrow else 0
    for i, label in enumerate(labels):
        if i > 0:
            imgui.same_line()
        if imgui.radio_button(label, _haiku_view == i):
            _haiku_view = i
    if not narrow and _haiku_view == 2:
        _haiku_view = 0
    size = ImVec2(content_size.x, content_size.y - imgui.get_frame_height_with_spacing())
    if narrow:  # one at a time: the code, or the app
        if _haiku_view == 2:
            _haiku_running_app(size)
        else:
            _haiku_code(_haiku_view, size)
        return
    app_w = min(em * 23.0, size.x * 0.45)  # the heart is 21 em wide
    _haiku_code(_haiku_view, ImVec2(size.x - app_w - gap, size.y))
    imgui.same_line(0, gap)
    _haiku_running_app(ImVec2(app_w, size.y))


# ============================================================================
# Slide: "Code that reads like a book": four snippets, each beside the widget it draws
# ============================================================================

# Each snippet: (title, Python code, C++ code). The code shown is the code that draws the widget beside it.
_GALLERY_SNIPPETS = [
    ("Animated Plot",
     # Python
     """\
t = imgui.get_time()
x = np.linspace(0, 4 * np.pi, 200)
if implot.begin_plot("##wave", ImVec2(-1, -1)):
    implot.plot_line("sin", x, np.sin(x + t))
    implot.plot_line("cos", x, np.cos(x + t * 0.7))
    implot.end_plot()""",
     # C++
     """\
float t = ImGui::GetTime();
std::vector<float> x(200), s(200), c(200);
for (int i = 0; i < 200; i++) {
    x[i] = i * 4.f * IM_PI / 199.f;
    s[i] = sinf(x[i] + t);
    c[i] = cosf(x[i] + t * 0.7f);
}
if (ImPlot::BeginPlot("##wave", ImVec2(-1, -1))) {
    ImPlot::PlotLine("sin", x.data(), s.data(), 200);
    ImPlot::PlotLine("cos", x.data(), c.data(), 200);
    ImPlot::EndPlot();
}"""),
    ("Knob",
     # Python
     """\
_, value = imgui_knobs.knob(
    "Volume", value, 0, 100, 1,
    "%.0f%%", imgui_knobs.ImGuiKnobVariant_.wiper_dot)
imgui.same_line()
imgui.v_slider_float("##vslider",
    ImVec2(em * 1.5, em * 5), value, 0, 100, "%.0f")""",
     # C++
     """\
ImGuiKnobs::Knob(
    "Volume", &value, 0, 100, 1,
    "%.0f%%", ImGuiKnobVariant_WiperDot);
ImGui::SameLine();
ImGui::VSliderFloat("##vslider",
    ImVec2(em * 1.5f, em * 5.f), &value, 0, 100, "%.0f");"""),
    ("Color Picker",
     # Python
     """\
# c is an ImVec4
imgui.text(f"({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
_, c = imgui.color_picker4("##color", c)
""",
     # C++
     """\
// c is an ImVec4
ImGui::Text("(%.2f, %.2f, %.2f)", c.x, c.y, c.z);
ImGui::ColorPicker4("##color", &c.x);
"""),
    ("Mini Form",
     # Python
     """\
_changed, name = imgui.input_text("Name", name)
if imgui.button("Greet") and name:
    greeting = f"Hello, {name}!"
imgui.text_colored(ImVec4(0.4, 1, 0.4, 1), greeting)
_, agreed = imgui.checkbox("I agree", agreed)
_, choice = imgui.combo("Fruit", choice,
                        ["Apple", "Banana", "Cherry"])""",
     # C++
     """\
ImGui::InputText("Name", name, sizeof(name));
if (ImGui::Button("Greet") && name[0])
    snprintf(greeting, sizeof(greeting), "Hello, %s!", name);
ImGui::TextColored(ImVec4(0.4f,1,0.4f,1), "%s", greeting);
ImGui::Checkbox("I agree", &agreed);
ImGui::Combo("Fruit", &choice, "Apple\\0Banana\\0Cherry\\0");"""),
]

# _gallery_editors[lang_idx][snippet_idx], lang_idx: 0=Python, 1=C++
_gallery_editors: list[list[Any]] = [[], []]
_gallery_initialized = False
_gallery_lang = 0  # 0 = Python, 1 = C++
_gallery_snippet = 0  # on a phone: the one snippet shown


def _init_gallery():
    global _gallery_initialized
    for lang_idx, lang_def in enumerate([
        ed.TextEditor.Language.python(),
        ed.TextEditor.Language.cpp(),
    ]):
        for _, py_code, cpp_code in _GALLERY_SNIPPETS:
            code = py_code if lang_idx == 0 else cpp_code
            editor = ed.TextEditor()
            editor.set_text(code)
            editor.set_language(lang_def)
            editor.set_palette(ed.TextEditor.get_dark_palette())
            _gallery_editors[lang_idx].append(editor)
    _gallery_initialized = True


def _gallery_slide_gui(content_size: ImVec2):
    global _gallery_initialized, _gallery_lang, _gallery_snippet
    s = _gallery_slide_gui  # static-like state on the function object
    if not _gallery_initialized:
        _init_gallery()

    if not hasattr(s, "_knob_val"):
        s._knob_val = 42.0
        s._color = [0.4, 0.6, 1.0, 1.0]
        s._name = "World"
        s._greeting = "Hello, World!"
        s._agreed = True
        s._choice = 0

    em = hello_imgui.em_size()
    narrow = is_small_screen()

    # Language radio buttons (and on a phone, the snippet shown)
    _, _gallery_lang = imgui.radio_button("Python", _gallery_lang, 0)
    imgui.same_line()
    _, _gallery_lang = imgui.radio_button("C++", _gallery_lang, 1)
    if narrow:
        imgui.same_line(0.0, em)
        imgui.set_next_item_width(-1)
        _, _gallery_snippet = imgui.combo("##snippet", _gallery_snippet, [title for title, _, _ in _GALLERY_SNIPPETS])

    snippets_gui = [
        lambda: _gallery_gui_plot(em),
        lambda: _gallery_gui_knob(em, s),
        lambda: _gallery_gui_color(em, s),
        lambda: _gallery_gui_form(em, s),
    ]
    cursor_offset_y = imgui.get_cursor_screen_pos().y - imgui.get_window_pos().y
    remaining_h = content_size.y - cursor_offset_y
    if narrow:  # one snippet, its code above its widget
        _gallery_render_cell(_gallery_snippet, content_size.x, remaining_h, em, snippets_gui[_gallery_snippet],
                             stacked=True)
        return
    cols, rows = 2, 2
    gap = em * 0.4
    cell_w = (content_size.x - gap * (cols - 1)) / cols
    cell_h = (remaining_h - gap * (rows - 1)) / rows
    origin = imgui.get_cursor_screen_pos()
    for idx in range(4):
        row, col = divmod(idx, cols)
        imgui.set_cursor_screen_pos(ImVec2(origin.x + col * (cell_w + gap), origin.y + row * (cell_h + gap)))
        _gallery_render_cell(idx, cell_w, cell_h, em, snippets_gui[idx], stacked=False)


def _gallery_render_cell(idx: int, w: float, h: float, em: float, gui_func, stacked: bool):
    """A snippet's code and its widget, side by side (the code at the left, resizable) or stacked (the code above)"""
    if not hasattr(_gallery_render_cell, "_copy_times"):
        _gallery_render_cell._copy_times = {}
    title = _GALLERY_SNIPPETS[idx][0]
    editor = _gallery_editors[_gallery_lang][idx]

    panel_bg(imgui.get_cursor_screen_pos(), ImVec2(w, h), 0.06, 0.25)
    imgui.begin_child(f"##gallery_{idx}", ImVec2(w, h), False,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)
    pad = em * 0.4
    avail_h = h - imgui.get_cursor_pos_y() - pad
    if stacked:
        code_size, code_flags = ImVec2(w - pad, avail_h * 0.5), imgui.ChildFlags_.resize_y | imgui.ChildFlags_.borders
    else:
        code_size, code_flags = ImVec2((w - pad * 2) * 0.5, avail_h), imgui.ChildFlags_.resize_x | imgui.ChildFlags_.borders

    imgui.begin_child(f"##code_{idx}", code_size, code_flags)
    # Title + Copy button
    imgui.text_disabled(title)
    imgui.same_line(imgui.get_content_region_avail().x - imgui.get_frame_height())
    if imgui.small_button(icons_fontawesome_4.ICON_FA_COPY + f"##copy_{idx}"):
        code = _GALLERY_SNIPPETS[idx][1] if _gallery_lang == 0 else _GALLERY_SNIPPETS[idx][2]
        imgui.set_clipboard_text(code)
        _gallery_render_cell._copy_times[idx] = imgui.get_time()
    copied_recently = (imgui.get_time() - _gallery_render_cell._copy_times.get(idx, -1.0)) < 0.7
    imgui.set_item_tooltip("Copied!" if copied_recently else "Copy")
    code_font = rich_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size * 0.8)
    editor.render(f"##ed_gallery_{idx}", ImVec2(-1, -1))
    imgui.pop_font()
    imgui.end_child()

    if not stacked:
        imgui.same_line()
    # The widget, in the remaining space
    imgui.begin_child(f"##live_{idx}", ImVec2(0, 0 if stacked else avail_h), False, imgui.WindowFlags_.no_scrollbar)
    gui_func()
    imgui.end_child()
    imgui.end_child()


def _gallery_gui_plot(em: float):
    t = imgui.get_time()
    x = np.linspace(0, 4 * np.pi, 200)
    if implot.begin_plot("##wave", ImVec2(-1, -1)):
        implot.plot_line("sin", x, np.sin(x + t))
        implot.plot_line("cos", x, np.cos(x + t * 0.7))
        implot.end_plot()
        hello_imgui.set_item_is_live()  # the waves move on their own


def _gallery_gui_knob(em: float, s):
    _, s._knob_val = imgui_knobs.knob(
        "Volume", s._knob_val, 0, 100, 1,
        "%.0f%%", imgui_knobs.ImGuiKnobVariant_.wiper_dot)
    imgui.same_line()
    _, s._knob_val = imgui.v_slider_float(
        "##vslider", ImVec2(em * 1.5, em * 5), s._knob_val, 0, 100, "%.0f")


def _gallery_gui_color(em: float, s):
    imgui.text(f"({s._color[0]:.2f}, {s._color[1]:.2f}, {s._color[2]:.2f})")
    _, s._color = imgui.color_picker4("##color", s._color)


def _gallery_gui_form(em: float, s):
    imgui.set_next_item_width(-1)
    _changed, s._name = imgui.input_text("Name", s._name)
    if imgui.button("Greet") and s._name:
        s._greeting = f"Hello, {s._name}!"
    imgui.text_colored(ImVec4(0.4, 1.0, 0.4, 1.0), s._greeting)
    _, s._agreed = imgui.checkbox("I agree", s._agreed)
    imgui.set_next_item_width(-1)
    _, s._choice = imgui.combo("Fruit", s._choice, ["Apple", "Banana", "Cherry"])


# ============================================================================
# Top section: the links row, the prose
# ============================================================================

def links_row():
    """The main links row: the site | Repository | Documentation | Playground | Discord. Not on a phone: three lines
    there, and the fold has them all (the "Start here" of resources.md)"""
    if is_small_screen():
        return
    links = [
        ("imgui-bundle.pages.dev", "https://imgui-bundle.pages.dev", "Main project site"),
        ("Repository", "https://github.com/pthom/imgui_bundle", "Source code, issues, discussions"),
        ("Documentation", "https://imgui-bundle.pages.dev/doc/", "Full documentation for Dear ImGui Bundle"),
        ("Python Playground", "https://imgui-bundle.pages.dev/playground/", "Live Python sandbox with demos - edit and run in your browser"),
        ("Discord", "https://discord.gg/xkzpKMeYN3", "Join the community for questions, showcase, and discussion (new!)"),
        ("All the resources", "https://imgui-bundle.pages.dev/doc/intro/resources/", "Every documentation, manual, video and community link, in one page"),
    ]
    for i, (label, url, tooltip) in enumerate(links):
        if i > 0:
            imgui.same_line()
            needed = imgui.calc_text_size("| " + label).x + 2 * imgui.get_style().item_spacing.x
            if needed > imgui.get_content_region_avail().x:  # the row wraps on a narrow screen
                imgui.new_line()
            else:
                imgui.text_disabled("|")
                imgui.same_line()
        rich_md.render_text_as_link(label, url)
        if imgui.is_item_hovered():
            imgui.set_tooltip(tooltip)


ABOUT_TITLE = "About Dear ImGui Bundle"  # the window of the prose
ABOUT_ANIMATION = 0.3  # s: the window of the prose slides up and fades in
HEAD_SCALE_SMALL_SCREEN = 0.75  # the tagline's size on a phone, where it would take a third of the screen

_welcome_head: list[str] = []  # the tagline and the subtitle: the paragraphs of welcome.md before its first section
_welcome_rest = ""  # its sections, in the window of the prose
_welcome_loaded = False
_about_opened_at: Optional[float] = None  # when the window of the prose opened (None: closed)
_cta_height = 0.0  # the height of the button and the manuals' line, measured at the last frame
HEAD_EXPANDED_DURATION = 8.0  # s: on a phone, a tap on the short tagline shows all of it for that long
_head_expanded_until = 0.0  # the time until which the whole head shows, on a phone


def _load_welcome_text() -> None:
    """welcome.md, an asset (demos_assets): its paragraphs before the first "## " heading are the head (one line of
    text each, `*italic*` for the whole paragraph), the rest is the prose"""
    global _welcome_head, _welcome_rest, _welcome_loaded
    _welcome_loaded = True
    path = hello_imgui.asset_file_full_path("welcome.md", assert_if_not_found=False)
    if not path:
        _welcome_head = ["*Interactive Python & C++ apps for desktop, mobile, and the web.*"]
        return
    with open(path, encoding="utf-8") as f:
        text = f.read()
    cut = text.find("\n## ")
    head, _welcome_rest = (text, "") if cut < 0 else (text[:cut], text[cut + 1:])
    _welcome_head = [p.strip() for p in head.split("\n\n") if p.strip()]


def _short_head() -> list[str]:
    """On a phone: the tagline's first sentence only (it ends at its first ". ")"""
    if not _welcome_head:
        return []
    first = _welcome_head[0]
    italic = first.startswith("*") and first.endswith("*")
    text = first.strip("*") if italic else first
    cut = text.find(". ")
    if cut < 0:
        return [first]
    return [f"*{text[:cut + 1]}*" if italic else text[:cut + 1]]


def _render_head() -> None:
    """The tagline and the subtitle, and at the right of their last line the button that opens the prose. Drawn with
    the markdown fonts, not rendered as markdown: a phone shows them smaller, and only the tagline's first sentence,
    until a tap shows the rest for a while"""
    global _about_opened_at, _head_expanded_until
    if not _welcome_loaded:
        _load_welcome_text()
    em = hello_imgui.em_size()
    small = is_small_screen()
    expanded = not small or imgui.get_time() < _head_expanded_until
    paragraphs = _welcome_head if expanded else _short_head()
    if small and expanded:
        hello_imgui.request_refresh()  # the head folds back on its own
    label = icons_fontawesome_4.ICON_FA_INFO_CIRCLE if small else f"More info & links {icons_fontawesome_4.ICON_FA_EXPAND}"
    button_w = imgui.calc_text_size(label).x + imgui.get_style().frame_padding.x * 2.0
    top_left = imgui.get_cursor_screen_pos()
    avail_x = imgui.get_content_region_avail().x
    imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + avail_x - (button_w + em if _welcome_rest else 0.0))
    last_line_end = 0.0  # where the last paragraph ends, when it takes one line (else the button goes at the right)
    for i, paragraph in enumerate(paragraphs):
        italic = len(paragraph) > 2 and paragraph.startswith("*") and paragraph.endswith("*")
        text = paragraph.strip("*") if italic else paragraph
        font = rich_md.get_font(rich_md.MarkdownFontSpec(italic_=italic))
        imgui.push_font(font.font, font.size * (HEAD_SCALE_SMALL_SCREEN if small else 1.0))
        if i > 0:
            imgui.dummy(ImVec2(0, em * 0.2))
        width = imgui.calc_text_size(text).x
        last_line_end = width if width + button_w + em <= avail_x else 0.0
        imgui.text_wrapped(text)
        imgui.pop_font()
    imgui.pop_text_wrap_pos()
    if small:  # a tap on the text shows all of it, or folds it back
        head_bottom = imgui.get_cursor_screen_pos().y
        if imgui.is_mouse_hovering_rect(top_left, ImVec2(top_left.x + avail_x - button_w - em, head_bottom)) \
                and imgui.is_mouse_released(imgui.MouseButton_.left) and imgui.get_mouse_drag_delta(0).y == 0:
            _head_expanded_until = 0.0 if expanded else imgui.get_time() + HEAD_EXPANDED_DURATION
    if not _welcome_rest:
        return
    below = imgui.get_cursor_screen_pos()
    button_x = top_left.x + (last_line_end + em if last_line_end > 0.0 else avail_x - button_w)
    imgui.set_cursor_screen_pos(ImVec2(button_x, below.y - imgui.get_text_line_height_with_spacing()))
    if imgui.small_button(label):
        _about_opened_at = imgui.get_time()
    imgui.set_cursor_screen_pos(below)


def _about_window() -> None:
    """The prose of welcome.md, in a modal window that slides up as it fades in; a click outside, Escape or its close
    button closes it"""
    global _about_opened_at
    if _about_opened_at is None:
        return
    if not imgui.is_popup_open(ABOUT_TITLE):
        imgui.open_popup(ABOUT_TITLE)
    em = hello_imgui.em_size()
    t = min((imgui.get_time() - _about_opened_at) / ABOUT_ANIMATION, 1.0)
    eased = 1.0 - (1.0 - t) ** 3
    if t < 1.0:
        hello_imgui.request_refresh()  # the window arrives on its own
    viewport = imgui.get_main_viewport()
    center = viewport.get_center()
    imgui.set_next_window_pos(ImVec2(center.x, center.y + em * 3.0 * (1.0 - eased)), imgui.Cond_.always,
                              ImVec2(0.5, 0.5))
    imgui.set_next_window_size(ImVec2(min(em * 56.0, viewport.size.x * 0.94), viewport.size.y * 0.82),
                               imgui.Cond_.always)
    imgui.push_style_var(imgui.StyleVar_.alpha, max(eased, 0.01))
    imgui.push_style_var(imgui.StyleVar_.window_rounding, em * 0.6)
    imgui.push_style_var(imgui.StyleVar_.window_padding, ImVec2(em * 1.2, em * 0.8))
    background = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    imgui.push_style_color(imgui.Col_.popup_bg, ImVec4(background.x, background.y, background.z, 1.0))  # opaque
    opened, keep_open = imgui.begin_popup_modal(ABOUT_TITLE, True,
                                                imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_saved_settings)
    if not opened:  # its close button
        _about_opened_at = None
    else:
        rich_md.render(_welcome_rest)
        clicked_outside = (imgui.is_mouse_clicked(imgui.MouseButton_.left)
                           and not imgui.is_window_hovered(imgui.HoveredFlags_.root_and_child_windows))
        if not keep_open or clicked_outside or imgui.is_key_pressed(imgui.Key.escape):
            imgui.close_current_popup()
            _about_opened_at = None
        imgui.end_popup()
    imgui.pop_style_color()
    imgui.pop_style_var(3)


# ============================================================================
# The carousel
# ============================================================================

def _draw_slide_motto_card(slide: CarouselSlide, slide_width: float, host: Host) -> float:
    """The title card of a slide: its title, its description and, when the host can open it, a link to its full
    demo. Returns the height taken."""
    em = hello_imgui.em_size()
    dl = imgui.get_window_draw_list()
    font_size = imgui.get_font_size()
    narrow = is_small_screen()  # a phone: the title and the link, smaller, no description
    title_font_size = font_size * (1.0 if narrow else 1.2)
    font = imgui.get_font()

    link = "Open the full demo " + icons_fontawesome_4.ICON_FA_CHEVRON_RIGHT if slide.demo and host.open_demo else ""
    link_size = imgui.calc_text_size(link) if link else ImVec2(0, 0)
    title_size = imgui.calc_text_size(slide.title)
    title_h = title_size.y * (title_font_size / font_size)
    desc_size = ImVec2(0, 0) if narrow else imgui.calc_text_size(slide.description, None, False, slide_width - em * 2.0)

    card_pad_x = em * (0.6 if narrow else 1.0)
    card_pad_y = em * (0.25 if narrow else 0.4)
    card_w = slide_width - em * 1.0
    # The link at the right of the title when both fit on the line, else on a line of its own under the text
    link_on_title = link_size.x + title_size.x * (title_font_size / font_size) + em * 1.0 <= card_w - 2 * card_pad_x
    inner_h = title_h + desc_size.y + (em * 0.3 if not narrow else 0.0)
    if link and not link_on_title:
        inner_h += link_size.y + em * 0.3
    card_h = inner_h + card_pad_y * 2.0
    card_x = imgui.get_cursor_screen_pos().x + (slide_width - card_w) * 0.5
    card_y = imgui.get_cursor_screen_pos().y

    accent_col = imgui.get_style_color_vec4(imgui.Col_.button_hovered)
    card_bg = imgui.color_convert_float4_to_u32(ImVec4(accent_col.x, accent_col.y, accent_col.z, 0.12))
    card_border = imgui.color_convert_float4_to_u32(ImVec4(accent_col.x, accent_col.y, accent_col.z, 0.4))
    title_col = imgui.get_color_u32(imgui.Col_.text)
    desc_col = imgui.get_color_u32(imgui.Col_.text_disabled)

    dl.add_rect_filled(ImVec2(card_x, card_y), ImVec2(card_x + card_w, card_y + card_h), card_bg, em * 0.4)
    dl.add_rect(ImVec2(card_x, card_y), ImVec2(card_x + card_w, card_y + card_h), card_border, em * 0.4, 1.5, 0)
    dl.add_text(font, title_font_size, ImVec2(card_x + card_pad_x, card_y + card_pad_y), title_col, slide.title)
    if not narrow:
        dl.add_text(font, font_size, ImVec2(card_x + card_pad_x, card_y + card_pad_y + title_h + em * 0.3),
                    desc_col, slide.description, None, slide_width - em * 2.0)

    total_h = card_h + em * 0.4
    cursor = imgui.get_cursor_screen_pos()
    if link:  # at the right of the card: on the title's line, or on its own line under the text
        if link_on_title:
            link_y = card_y + card_pad_y + (title_h - link_size.y) / 2
        else:
            link_y = card_y + card_h - card_pad_y - link_size.y
        link_pos = ImVec2(card_x + card_w - card_pad_x - link_size.x, link_y)
        imgui.set_cursor_screen_pos(link_pos)
        if imgui.invisible_button(f"##open_{slide.demo}", link_size):
            assert host.open_demo is not None
            host.open_demo(slide.demo)
        hovered = imgui.is_item_hovered()
        if hovered:
            imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
        color = imgui.color_convert_float4_to_u32(rich_md.link_color())
        dl.add_text(link_pos, color, link)
        if hovered:
            dl.add_line(ImVec2(link_pos.x, link_pos.y + link_size.y), ImVec2(link_pos.x + link_size.x, link_pos.y + link_size.y), color)
    # After the link: ImGui gives the hover to the first item submitted, so the link keeps its click
    _card_swipe(ImVec2(card_x, card_y), ImVec2(card_w, card_h), slide_width)
    imgui.set_cursor_screen_pos(cursor)
    imgui.dummy(ImVec2(slide_width, total_h))
    return total_h


def _card_swipe(top_left: ImVec2, size: ImVec2, slide_width: float) -> None:
    """A drag on a slide's title card (a swipe, on a touch screen) moves the carousel with it; released past 3 em, the
    next or the previous slide comes"""
    global _current_slide, _drag_offset, _auto_stopped
    imgui.set_cursor_screen_pos(top_left)
    imgui.invisible_button("##swipe", size)
    hello_imgui.set_item_takes_touch_drags(False)  # on a touch screen, the finger's drag is this button's at once
    if not (imgui.is_item_active() or imgui.is_item_deactivated()):
        return
    dx = imgui.get_mouse_drag_delta(imgui.MouseButton_.left).x
    if imgui.is_item_active():
        _drag_offset = _current_slide - dx / slide_width
        _auto_stopped = True
        return
    _drag_offset = None
    em = hello_imgui.em_size()
    if dx < -em * 3:
        _current_slide = (_current_slide + 1) % len(slides())
    elif dx > em * 3:
        _current_slide = (_current_slide - 1) % len(slides())


# Module-level carousel state
_current_slide = 0
_animated_offset = 0.0
_auto_timer = 0.0
_auto_stopped = False
_drag_offset: Optional[float] = None  # while a swipe drags the slides: where they are (in slides)
_slides: Optional[list[CarouselSlide]] = None


def slides() -> list[CarouselSlide]:
    """The slides, in their order; the ones whose library is missing are left out"""
    global _slides
    if _slides is not None:
        return _slides
    _slides = [CarouselSlide(
        "Rich Interactive Plots",
        "ImPlot delivers animated, interactive 2D charts with minimal code. It is extremely fast, and ideal for real-time data monitoring, diagnostics, and dashboards.",
        _implot_slide_gui, "manual_implot.py")]
    if HAS_GL:
        _slides.append(CarouselSlide(
            "GPU-Accelerated Rendering",
            "Dear ImGui renders directly on the GPU, fast enough to blend custom shaders and 3D content into your UI.",
            _shader_slide_gui, "webgl_background_shader.py" if IS_PYODIDE else "demo_custom_background.py"))
    _slides.append(CarouselSlide(
        "3D Data Exploration",
        "ImPlot3D adds rotatable, zoomable 3D plots. Navigate complex datasets with intuitive controls.",
        _lorenz_slide_gui, "manual_implot3d.py"))
    _slides.append(CarouselSlide(
        "Interactive Science",
        "A tiny neural network learns two spirals, live: a model with its knobs, in a few lines of numpy. The explorable tells how it works, formula by formula.",
        _spiral_slide_gui, "explorables/neural_spiral/neural_spiral.py"))
    if HAS_IMMVISION:
        _slides.append(CarouselSlide(
            "Image Analysis",
            "ImmVision lets you zoom, pan, and inspect pixel values in real time, with linked views and colormaps.",
            _immvision_slide_gui, "demo_immvision_inspector.py"))
        _slides.append(CarouselSlide(  # its nodes show their images with ImmVision
            "Visual Node Editors",
            "Explore ideas in graph form with imgui-node-editor: an image flows through filters written in numpy, "
            "and each node shows its result.",
            _pipeline_slide_gui, "demo_node_editor_image_pipeline.py"))
    _slides.append(CarouselSlide(
        "Feature-Rich Widgets",
        "Dear ImGui ships with advanced tables featuring angled headers, column reordering, sorting, and much more.",
        _table_slide_gui, "demo_widgets.py"))
    _slides.append(CarouselSlide(
        "Rich Documentation, Built In",
        "Render markdown directly in your UI - headers, code blocks, tables, links, math and images, all from a simple string.",
        _markdown_slide_gui, "demo_imgui_md.py"))
    _slides.append(CarouselSlide(
        "A Whole App in a Few Lines",
        "The complete program of a beating heart, imports and window included, and beside it the app it runs. "
        "No boilerplate: the GUI is a function that draws each frame.",
        _haiku_slide_gui, "haiku_implot_heart.py"))
    _slides.append(CarouselSlide(
        "Code That Reads Like a Book",
        "No widget trees, no callbacks, no state sync. Each snippet below is the complete code for the live demo beside it. The interactive manuals read the same way: every section with its code.",
        _gallery_slide_gui, "manual_imgui.py"))
    return _slides


def _slides_bg_color() -> int:
    """The slides' background: the page's, a little darker (more so in a dark theme), so that they stand out"""
    bg = imgui.get_style_color_vec4(imgui.Col_.window_bg)
    k = 0.75 if 0.299 * bg.x + 0.587 * bg.y + 0.114 * bg.z < 0.5 else 0.93
    return imgui.color_convert_float4_to_u32(ImVec4(bg.x * k, bg.y * k, bg.z * k, 1.0))


def _intro_mini_demos(host: Host, bottom_margin: float):
    """The carousel, 4:3 and centered, as tall as the space left above bottom_margin"""
    static = _intro_mini_demos
    global _current_slide, _animated_offset, _auto_timer, _auto_stopped

    the_slides = slides()
    slide_count = len(the_slides)

    dt = imgui.get_io().delta_time
    if dt <= 0.0:
        dt = 1.0 / 60.0
    if dt > 0.1:
        dt = 0.1

    em = hello_imgui.em_size()
    dl = imgui.get_window_draw_list()

    # --- Carousel zone: use available height, maintain 4:3 aspect ratio ---
    # On a phone the welcome fits the screen, even with a large text setting: the arrows, the dots and the button stay
    # in view, and nothing needs a vertical swipe (most of the page takes the finger: plots, editors, the cards)
    min_height = em * 12.0 if is_small_screen() else em * 15.0
    carousel_height = max(imgui.get_content_region_avail().y - bottom_margin, min_height)
    carousel_width = carousel_height * (4.0 / 3.0)
    avail_width = imgui.get_content_region_avail().x
    if carousel_width > avail_width:
        carousel_width = avail_width

    carousel_offset_x = (avail_width - carousel_width) * 0.5
    if carousel_offset_x < 0.0:
        carousel_offset_x = 0.0

    if carousel_offset_x > 0.0:  # indent(0) indents by the style's default: the carousel would overflow
        imgui.indent(carousel_offset_x)

    # --- Auto-advance, until the user touches something (a slide's widget, an arrow): then the slide stays ---
    if imgui.is_any_item_active():
        _auto_stopped = True
    if not _auto_stopped:
        _auto_timer += dt
        if _auto_timer > SLIDE_DURATION:
            _current_slide = (_current_slide + 1) % slide_count
            _auto_timer = 0.0

    # --- Smooth slide animation (none while a swipe holds the slides: they follow the finger) ---
    target = float(_current_slide)
    _animated_offset = _drag_offset if _drag_offset is not None else smooth_damp(_animated_offset, target, 8.0, dt)
    if abs(_animated_offset - target) < 0.001:
        _animated_offset = target
    if _animated_offset != target:
        hello_imgui.request_refresh()  # the slides slide on their own

    # --- Slide area: a child that clips the slides (each one is a child of its own, which the draw list's clip
    # rect would not clip) ---
    nav_bar_height = em * 2.0
    slide_height = carousel_height - nav_bar_height
    if slide_height < em * 10.0:
        slide_height = em * 10.0
    slide_width = carousel_width

    slide_area_pos = imgui.get_cursor_screen_pos()
    imgui.get_window_draw_list().add_rect_filled(  # behind the slides, which have no background of their own
        slide_area_pos, slide_area_pos + ImVec2(carousel_width, slide_height), _slides_bg_color(), em * 0.5)
    imgui.begin_child("##carousel_zone", ImVec2(carousel_width, slide_height), False,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
                      | imgui.WindowFlags_.no_background)
    for i in range(slide_count):
        slide_x = slide_area_pos.x + (float(i) - _animated_offset) * slide_width
        if slide_x >= slide_area_pos.x + carousel_width or slide_x + slide_width <= slide_area_pos.x:
            continue

        imgui.set_cursor_screen_pos(ImVec2(slide_x, slide_area_pos.y))
        child_id = f"##slide_{i}"
        imgui.begin_child(child_id, ImVec2(slide_width, slide_height), False,
                          imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_background)

        motto_h = _draw_slide_motto_card(the_slides[i], slide_width, host)

        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + em * 0.5)
        demo_size = ImVec2(slide_width - em * 1.0, slide_height - motto_h - em * 0.5)
        the_slides[i].gui_func(demo_size)

        imgui.end_child()
    imgui.end_child()

    # --- Navigation: arrows + dots ---
    dot_radius = em * 0.3
    dot_spacing = em * 1.5
    dots_width = slide_count * dot_spacing
    arrow_btn_w = em * 2.0
    total_nav_width = arrow_btn_w * 2.0 + dots_width + em * 1.0
    nav_start_x = slide_area_pos.x + (carousel_width - total_nav_width) * 0.5
    nav_y = slide_area_pos.y + slide_height + em * 0.3

    # Left arrow
    imgui.set_cursor_screen_pos(ImVec2(nav_start_x, nav_y + hello_imgui.em_size(0.15)))
    if imgui.button(icons_fontawesome_4.ICON_FA_CHEVRON_LEFT + "##carousel_prev",
                    ImVec2(arrow_btn_w, em * 1.2)):
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
    imgui.set_cursor_screen_pos(ImVec2(right_arrow_x, nav_y + hello_imgui.em_size(0.15)))
    if imgui.button(icons_fontawesome_4.ICON_FA_CHEVRON_RIGHT + "##carousel_next",
                    ImVec2(arrow_btn_w, em * 1.2)):
        _current_slide = (_current_slide + 1) % slide_count
        _auto_stopped = True

    # Advance cursor to the end of the nav bar: exactly the height claimed above, so that no scrollbar appears
    imgui.set_cursor_screen_pos(ImVec2(slide_area_pos.x, nav_y + em * 1.7))
    imgui.dummy(ImVec2(1, 0))

    # Navigation via mouse wheel
    if imgui.shortcut(imgui.Key.mod_shift | imgui.Key.mouse_wheel_x, imgui.InputFlags_.route_global.value):
        now = imgui.get_time()
        if not hasattr(static, "_time_last_trigger"):
            static._time_last_trigger = -1.0
        if now - static._time_last_trigger > 1.0:
            _auto_stopped = True
            if imgui.get_io().mouse_wheel_h > 0:
                if _current_slide > 0:
                    _current_slide = (_current_slide - 1) % slide_count
            else:
                _current_slide = (_current_slide + 1) % slide_count
            if _current_slide < 0:
                _current_slide = 0
            static._time_last_trigger = now

    if carousel_offset_x > 0.0:
        imgui.unindent(carousel_offset_x)


# ============================================================================
# The page
# ============================================================================

def _call_to_action(host: Host) -> None:
    """Centered: the big "Browse the N demos" button, then the line of the interactive manuals"""
    if host.browse is None:
        return
    global _cta_height
    em = hello_imgui.em_size()
    small = is_small_screen()
    top = imgui.get_cursor_screen_pos().y
    avail_x = imgui.get_content_region_avail().x
    label = f"{icons_fontawesome_4.ICON_FA_TH_LARGE}  Browse the {host.nb_demos} demos"
    imgui.push_font(None, imgui.get_style().font_size_base * (1.15 if small else 1.3))
    imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(em * 1.2, em * (0.3 if small else 0.4)))
    width = imgui.calc_text_size(label).x + em * 2.4
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_x - width) / 2)
    if imgui.button(label):
        host.browse()
    imgui.pop_style_var()
    imgui.pop_font()
    if host.open_demo is not None:
        _manuals_line(host.open_demo, avail_x, small)
    _cta_height = imgui.get_cursor_screen_pos().y - top


def _manuals_line(open_demo: Callable[[str], None], avail_x: float, small: bool) -> None:
    """The manuals: "or open an interactive manual: Dear ImGui | ImPlot | ImPlot3D | ImAnim" (shorter on a phone;
    centered when it fits on one line, else wrapped as the links row)"""
    em = hello_imgui.em_size()
    intro = "Interactive manuals: " if small else "or open an interactive manual: "
    parts_w = imgui.calc_text_size(intro).x + sum(imgui.calc_text_size(name).x for name, _ in MANUALS)
    parts_w += imgui.calc_text_size(" | ").x * (len(MANUALS) - 1)
    if parts_w <= avail_x:
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_x - parts_w) / 2)
    imgui.text_disabled(intro)
    for i, (name, filename) in enumerate(MANUALS):
        imgui.same_line(0, 0)
        if i > 0:
            if imgui.calc_text_size(" | " + name).x > imgui.get_content_region_avail().x:
                imgui.new_line()
            else:
                imgui.text_disabled(" | ")
                imgui.same_line(0, 0)
        imgui.push_style_color(imgui.Col_.text, rich_md.link_color())
        imgui.text(name)
        imgui.pop_style_color()
        if imgui.is_item_hovered():
            imgui.set_mouse_cursor(imgui.MouseCursor_.hand)
            if imgui.is_mouse_clicked(imgui.MouseButton_.left):
                open_demo(filename)
    _IntroAutomations.init()
    if _IntroAutomations.show_immediate_apps is not None:  # the explorer with the test engine: a guided tour
        imgui.same_line(0, em)
        if imgui.small_button("Show me " + icons_fontawesome_4.ICON_FA_EYE):
            imgui.test_engine.queue_test(hello_imgui.get_imgui_test_engine(), _IntroAutomations.show_immediate_apps)


def welcome_gui(host: Host):
    """The welcome without its title and links row (the explorer draws its own header above it): the tagline and the
    button to the prose, the carousel of mini demos, the button to the demos and the manuals"""
    global _host
    _host = host
    _render_head()
    imgui.separator()
    em = hello_imgui.em_size()
    # The button and the manuals' line: their height at the last frame (an estimate at the first)
    bottom = 0.0 if host.browse is None else (_cta_height + em * 0.3 if _cta_height > 0.0 else em * 4.6)
    _intro_mini_demos(host, bottom)
    _call_to_action(host)
    _about_window()


def gui(host: Optional[Host] = None):
    """The whole page: the title, the links row, the welcome"""
    if is_small_screen():  # the title smaller, in the font of a markdown title
        font = rich_md.get_font(rich_md.MarkdownFontSpec(header_level_=1))
        imgui.push_font(font.font, font.size * 0.7)
        imgui.text("Dear ImGui Bundle")
        imgui.pop_font()
        imgui.separator()
    else:
        rich_md.render("# Dear ImGui Bundle")
    links_row()
    welcome_gui(host or Host())


def main():
    host = Host()
    if IS_PYODIDE:  # the playground: its gallery of demos (js/examples.js)
        import js  # type: ignore
        host.nb_demos = int(js.document.querySelectorAll(".gallery-card").length)
        host.browse = js.openGallery
        host.open_demo = js.loadDemoByFilename
    immapp.run(
        lambda: gui(host),
        window_title="Dear ImGui Bundle - Welcome",
        window_size=(1200, 900),
        with_implot=True,
        with_implot3d=True,
        with_markdown=True,
        with_latex=True,
    )


if __name__ == "__main__":
    main()
