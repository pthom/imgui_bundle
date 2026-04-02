"""A lesson on Simple Harmonic Motion, built with Dear ImGui Bundle."""

from urllib.parse import quote
import numpy as np
import time
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_knobs, imgui_toggle
from imgui_bundle import ImVec2, ImVec4


# =============================================================================
# LaTeX helper
# =============================================================================

# Experimentation on whether we could display math in the renderer.
# Currently uses https://latex.codecogs.com/
# A more robust solution would be to bundle a math renderer
# KateX come to mind, but actually the most astute would be
#    https://github.com/NanoMichael/MicroTeX
# (would work in C++ and Python)

def _detect_latex_color() -> str:
    """Detect whether the current ImGui theme is light or dark."""
    try:
        bg = imgui.get_style_color_vec4(imgui.Col_.window_bg)
        luminance = 0.299 * bg.x + 0.587 * bg.y + 0.114 * bg.z
        return "black" if luminance > 0.5 else "white"
    except Exception:
        return "white"

def _latex_to_img(tex: str, display: bool, color: str) -> str:
    """Convert a LaTeX string to an <img> tag via codecogs."""
    dpi = 150 if display else 100
    encoded = quote(f"\\dpi{{{dpi}}}\\color{{{color}}}{tex}")
    url = f"https://latex.codecogs.com/png.latex?{encoded}"
    return f'<img src="{url}">'

def render_md_with_math(md: str):
    """Render markdown with LaTeX math support.

    Uses LaTeX/KaTeX flavor:
      $...$   for inline math
      $$...$$ for display math (on its own line)
      \\$      for a literal dollar sign

    Calls imgui_md.render_unindented() with math replaced by <img> tags.
    """
    import re
    color = _detect_latex_color()

    # Protect escaped dollars
    md = md.replace(r"\$", "%%ESCAPED_DOLLAR%%")

    # Replace $$...$$ (display math) first - greedy on content, not on delimiters
    md = re.sub(
        r"\$\$(.*?)\$\$",
        lambda m: _latex_to_img(m.group(1).strip(), display=True, color=color),
        md, flags=re.DOTALL)

    # Replace $...$ (inline math) - single line only, no nested $
    md = re.sub(
        r"\$([^\$\n]+?)\$",
        lambda m: _latex_to_img(m.group(1).strip(), display=False, color=color),
        md)

    # Restore escaped dollars
    md = md.replace("%%ESCAPED_DOLLAR%%", "$")

    imgui_md.render_unindented(md)


# =============================================================================
# Lesson content (markdown + LaTeX)
# =============================================================================

INTRO = r"""# Simple Harmonic Motion

**Simple harmonic motion** (SHM) is the most fundamental type of oscillation in physics.
A mass on a spring, a pendulum at small angles, a vibrating string - they all follow
the same elegant mathematics.

## The setup

Imagine a mass *m* attached to a spring with stiffness *k*. When displaced from
equilibrium, the spring pulls it back with a force proportional to the displacement:

$$F = -kx$$

Newton's second law gives us:

$$m\ddot{x} = -kx \quad\Rightarrow\quad \ddot{x} + \omega^2 x = 0$$

where the **natural frequency** is:

$$\omega_0 = \sqrt{k/m}$$

The solution is a pure sinusoid:

$$x(t) = A\cos(\omega_0 t + \phi)$$

**Try it below:** adjust the mass and spring stiffness, and watch how the motion changes.
"""

DAMPING_INTRO = r"""### What is damping?

In the real world, friction slows things down. We model this with a damping force
proportional to velocity:

$$m\ddot{x} + b\dot{x} + kx = 0$$

The **damping ratio** controls the behavior:

$$\zeta = \frac{b}{2\sqrt{mk}}$$

- $\zeta < 1$: **underdamped** - oscillates with decaying amplitude
- $\zeta = 1$: **critically damped** - fastest return without oscillation
- $\zeta > 1$: **overdamped** - slow exponential return
"""

RESONANCE_INTRO = r"""### Resonance

Now add an external periodic force:

$$m\ddot{x} + b\dot{x} + kx = F_0\cos(\omega_d t)$$

When the driving frequency $\omega_d$ matches the natural frequency
$\omega_0$, the amplitude grows dramatically. This is **resonance**.

The steady-state amplitude is:

$$A(\omega_d) = \frac{F_0/m}{\sqrt{(\omega_0^2-\omega_d^2)^2 + (2\zeta\omega_0\omega_d)^2}}$$

**Try it:** sweep the driving frequency and watch the resonance peak emerge.
"""


# =============================================================================
# Physics simulation
# =============================================================================

class Oscillator:
    def __init__(self):
        self.x = 1.0       # displacement
        self.v = 0.0       # velocity
        self.t = 0.0

    def step(self, dt: float, k: float, m: float, b: float, f0: float, wd: float):
        # RK4 integration of: m*x'' + b*x' + k*x = F0*cos(wd*t)
        def derivs(x, v, t):
            a = (-k * x - b * v + f0 * np.cos(wd * t)) / m
            return v, a

        v1, a1 = derivs(self.x, self.v, self.t)
        v2, a2 = derivs(self.x + 0.5*dt*v1, self.v + 0.5*dt*a1, self.t + 0.5*dt)
        v3, a3 = derivs(self.x + 0.5*dt*v2, self.v + 0.5*dt*a2, self.t + 0.5*dt)
        v4, a4 = derivs(self.x + dt*v3, self.v + dt*a3, self.t + dt)

        self.x += (dt/6) * (v1 + 2*v2 + 2*v3 + v4)
        self.v += (dt/6) * (a1 + 2*a2 + 2*a3 + a4)
        self.t += dt

    def reset(self, x0=1.0):
        self.x = x0
        self.v = 0.0
        self.t = 0.0


# =============================================================================
# Application state
# =============================================================================

class AppState:
    def __init__(self):
        # Spring parameters
        self.k = 4.0       # stiffness
        self.m = 1.0       # mass
        self.speed = 1.0

        # Damping
        self.damping_enabled = False
        self.b = 0.3       # damping coefficient

        # Driving force
        self.driving_enabled = False
        self.f0 = 1.0      # driving amplitude
        self.wd = 2.0      # driving frequency

        self.osc = Oscillator()
        self.last_time = time.time()
        self.paused = False

        # History for plotting
        self.t_history = []
        self.x_history = []
        self.max_history = 800

    def reset(self):
        self.osc.reset()
        self.t_history.clear()
        self.x_history.clear()

    def update(self):
        now = time.time()
        dt = min(now - self.last_time, 0.1)
        self.last_time = now
        if self.paused:
            return

        b = self.b if self.damping_enabled else 0.0
        f0 = self.f0 if self.driving_enabled else 0.0
        wd = self.wd if self.driving_enabled else 0.0

        # Fixed timestep accumulator: consistent simulation regardless of frame rate
        fixed_dt = 1.0 / 240.0
        accumulated = dt * self.speed
        while accumulated >= fixed_dt:
            self.osc.step(fixed_dt, self.k, self.m, b, f0, wd)
            accumulated -= fixed_dt

        self.t_history.append(self.osc.t)
        self.x_history.append(self.osc.x)
        if len(self.t_history) > self.max_history:
            self.t_history = self.t_history[-self.max_history:]
            self.x_history = self.x_history[-self.max_history:]


# =============================================================================
# Drawing: animated spring + mass
# =============================================================================

def draw_spring_mass(state: AppState, origin: ImVec2, width: float, height: float):
    """Draw an animated spring-mass system."""
    draw_list = imgui.get_window_draw_list()
    em = hello_imgui.em_size()

    x = state.osc.x
    # Map displacement to screen (equilibrium at center)
    max_disp = 2.0
    cx = origin.x + width * 0.5
    cy = origin.y + height * 0.5
    mass_x = cx + (x / max_disp) * width * 0.3

    # Wall
    wall_x = origin.x + em * 2
    wall_col = imgui.get_color_u32(ImVec4(0.6, 0.6, 0.6, 1.0))
    draw_list.add_line(ImVec2(wall_x, cy - height * 0.3),
                      ImVec2(wall_x, cy + height * 0.3), wall_col, 3.0)
    # Hatching
    for i in range(6):
        y = cy - height * 0.3 + i * height * 0.1
        draw_list.add_line(ImVec2(wall_x - em * 0.5, y + height * 0.05),
                          ImVec2(wall_x, y), wall_col, 1.5)

    # Spring (zigzag)
    spring_start = wall_x
    spring_end = mass_x - em * 1.5
    n_coils = 12
    coil_h = height * 0.08
    spring_col = imgui.get_color_u32(ImVec4(0.3, 0.7, 1.0, 0.9))
    prev = ImVec2(spring_start, cy)
    for i in range(1, n_coils + 1):
        frac = i / (n_coils + 1)
        sx = spring_start + frac * (spring_end - spring_start)
        sy = cy + coil_h * (1 if i % 2 == 0 else -1)
        draw_list.add_line(prev, ImVec2(sx, sy), spring_col, 2.0)
        prev = ImVec2(sx, sy)
    draw_list.add_line(prev, ImVec2(spring_end, cy), spring_col, 2.0)

    # Mass (filled rectangle with rounded corners)
    mass_w = em * 3
    mass_h = em * 3
    mass_col = imgui.get_color_u32(ImVec4(0.9, 0.4, 0.2, 1.0))
    draw_list.add_rect_filled(
        ImVec2(mass_x - mass_w * 0.5, cy - mass_h * 0.5),
        ImVec2(mass_x + mass_w * 0.5, cy + mass_h * 0.5),
        mass_col, em * 0.3)

    # "m" label on mass
    draw_list.add_text(ImVec2(mass_x - em * 0.3, cy - em * 0.4),
                      imgui.get_color_u32(ImVec4(1, 1, 1, 1)), "m")

    # Equilibrium line
    eq_col = imgui.get_color_u32(ImVec4(1, 1, 1, 0.15))
    draw_list.add_line(ImVec2(cx, cy - height * 0.35),
                      ImVec2(cx, cy + height * 0.35), eq_col, 1.0)

    # Displacement arrow
    if abs(x) > 0.05:
        arrow_y = cy + mass_h * 0.5 + em * 0.8
        arrow_col = imgui.get_color_u32(ImVec4(0.3, 0.7, 0.3, 0.8))
        draw_list.add_line(ImVec2(cx, arrow_y), ImVec2(mass_x, arrow_y),
                          arrow_col, 2.0)
        # Arrowhead
        direction = 1 if x > 0 else -1
        draw_list.add_triangle_filled(
            ImVec2(mass_x, arrow_y),
            ImVec2(mass_x - direction * em * 0.5, arrow_y - em * 0.3),
            ImVec2(mass_x - direction * em * 0.5, arrow_y + em * 0.3),
            arrow_col)
        draw_list.add_text(ImVec2(cx - em * 0.2, arrow_y + em * 0.3),
                          arrow_col, "x")

    # Driving force indicator
    if state.driving_enabled:
        force_x = mass_x + mass_w * 0.5
        force_val = state.f0 * np.cos(state.wd * state.osc.t)
        force_screen = force_val * width * 0.05
        f_col = imgui.get_color_u32(ImVec4(0.3, 1.0, 0.3, 0.8))
        draw_list.add_line(ImVec2(force_x, cy),
                          ImVec2(force_x + force_screen, cy),
                          f_col, 3.0)
        if abs(force_val) > 0.1:
            fd = 1 if force_val > 0 else -1
            draw_list.add_triangle_filled(
                ImVec2(force_x + force_screen, cy),
                ImVec2(force_x + force_screen - fd * em * 0.4, cy - em * 0.3),
                ImVec2(force_x + force_screen - fd * em * 0.4, cy + em * 0.3),
                f_col)


# =============================================================================
# Resonance curve computation
# =============================================================================

def resonance_curve(w0: float, zeta: float, f0_over_m: float, n_points: int = 200):
    """Compute steady-state amplitude vs driving frequency."""
    wd = np.linspace(0.01, w0 * 3, n_points)
    denom = np.sqrt((w0**2 - wd**2)**2 + (2 * zeta * w0 * wd)**2)
    amp = f0_over_m / denom
    return wd, amp


# =============================================================================
# GUI
# =============================================================================

def gui(state: AppState):
    state.update()
    em = hello_imgui.em_size()

    # Full-width scrollable lesson
    imgui.begin_child("lesson", ImVec2(0, 0), imgui.ChildFlags_.none)

    # ---- INTRODUCTION ----
    render_md_with_math(INTRO)
    imgui.spacing()

    # ---- INTERACTIVE: Free oscillation ----
    imgui.separator()
    imgui.spacing()

    # Controls row
    imgui.begin_horizontal("shm_controls", ImVec2(imgui.get_content_region_avail().x, 0))
    _, state.k = imgui_knobs.knob("Stiffness k", state.k, 0.5, 20.0,
                                   speed=0.05, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
                                   format="%.1f")
    imgui.spring(0, em)
    _, state.m = imgui_knobs.knob("Mass m", state.m, 0.1, 5.0,
                                   speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
                                   format="%.1f")
    imgui.spring(0, em)
    _, state.speed = imgui_knobs.knob("Speed", state.speed, 0.1, 3.0,
                                       speed=0.01, variant=imgui_knobs.ImGuiKnobVariant_.stepped,
                                       format="%.1fx")
    imgui.spring(0, em)

    # Natural frequency display
    w0 = np.sqrt(state.k / state.m)
    period = 2 * np.pi / w0

    imgui.begin_vertical("info", ImVec2(0, 0))
    imgui.spring()
    imgui.text(f"Natural freq: {w0:.2f} rad/s")
    imgui.text(f"Period: {period:.2f} s")
    imgui.spacing()
    if imgui.button("Reset"):
        state.reset()
    imgui.spring()
    imgui.end_vertical()

    imgui.spring()
    imgui.end_horizontal()

    imgui.spacing()

    # Spring-mass animation
    anim_height = em * 8
    cursor = imgui.get_cursor_screen_pos()
    avail_w = imgui.get_content_region_avail().x
    imgui.dummy(ImVec2(avail_w, anim_height))
    draw_spring_mass(state, cursor, avail_w, anim_height)

    imgui.spacing()

    # Displacement plot (always render to avoid layout height change on reset)
    plot_w = imgui.get_content_region_avail().x
    if implot.begin_plot("##displacement", ImVec2(plot_w, em * 10)):
        implot.setup_axes("Time (s)", "Displacement x")
        if len(state.t_history) > 1:
            ts = np.array(state.t_history)
            xs = np.array(state.x_history)
            implot.setup_axes_limits(ts[0], ts[-1] + 0.5, -2.5, 2.5,
                                    imgui.Cond_.always)
            implot.plot_line("x(t)", ts, xs)
        else:
            implot.setup_axes_limits(0, 10, -2.5, 2.5, imgui.Cond_.always)
        implot.end_plot()

    imgui.spacing()
    imgui.spacing()

    # ---- DAMPING SECTION ----
    if imgui.collapsing_header("Damping", imgui.TreeNodeFlags_.default_open):
        render_md_with_math(DAMPING_INTRO)
        imgui.spacing()

        if imgui.button("Disable damping" if state.damping_enabled else "Enable damping"):
            state.damping_enabled = not state.damping_enabled
            state.reset()

        if not state.damping_enabled:
            imgui.begin_disabled()
        imgui.set_next_item_width(em * 15)
        _, state.b = imgui.slider_float("Damping b", state.b, 0.0, 5.0, "%.2f")
        zeta = state.b / (2 * np.sqrt(state.m * state.k))
        if zeta < 1:
            regime = "Underdamped"
        elif abs(zeta - 1) < 0.01:
            regime = "Critically damped"
        else:
            regime = "Overdamped"
        imgui.text(f"Damping ratio: zeta = {zeta:.3f} ({regime})")
        if not state.damping_enabled:
            imgui.end_disabled()

    imgui.spacing()
    imgui.spacing()

    # ---- RESONANCE SECTION ----
    if imgui.collapsing_header("Driven Oscillation & Resonance"):
        render_md_with_math(RESONANCE_INTRO)
        imgui.spacing()

        if imgui.button("Disable driving force" if state.driving_enabled else "Enable driving force"):
            state.driving_enabled = not state.driving_enabled
            if state.driving_enabled and not state.damping_enabled:
                state.damping_enabled = True
                state.b = 0.3
            state.reset()

        if not state.driving_enabled:
            imgui.begin_disabled()

        imgui.begin_horizontal("drive_controls", ImVec2(imgui.get_content_region_avail().x, 0))
        _, state.f0 = imgui_knobs.knob("Force F0", state.f0, 0.1, 5.0,
                                        speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
                                        format="%.1f")
        imgui.spring(0, em)
        _, state.wd = imgui_knobs.knob("Drive freq", state.wd, 0.1, 8.0,
                                        speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
                                        format="%.1f")
        imgui.spring(0, em)

        w0 = np.sqrt(state.k / state.m)
        imgui.begin_vertical("ratio_info", ImVec2(0, 0))
        imgui.spring()
        ratio = state.wd / w0
        imgui.text(f"w_d / w_0 = {ratio:.2f}")
        if 0.9 < ratio < 1.1:
            imgui.text_colored(ImVec4(1, 0.3, 0.3, 1), "Near resonance!")
        imgui.spring()
        imgui.end_vertical()
        imgui.spring()
        imgui.end_horizontal()

        # Resonance curve
        imgui.spacing()
        imgui.text("Resonance curve (amplitude vs driving frequency)")
        zeta = state.b / (2 * np.sqrt(state.m * state.k))
        f0_over_m = state.f0 / state.m
        wd_arr, amp_arr = resonance_curve(w0, zeta, f0_over_m)
        plot_w = imgui.get_content_region_avail().x
        if implot.begin_plot("##resonance", ImVec2(plot_w, em * 12)):
            implot.setup_axes("Driving freq (rad/s)", "Amplitude")
            implot.setup_axes_limits(0, float(w0 * 3), 0,
                                    float(np.max(amp_arr) * 1.2) + 0.1,
                                    imgui.Cond_.always)
            implot.plot_line("A(w_d)", wd_arr, amp_arr)
            implot.plot_inf_lines("w_d", np.array([state.wd]))
            implot.end_plot()

        if not state.driving_enabled:
            imgui.end_disabled()

    imgui.spacing()
    imgui.spacing()
    imgui.end_child()


def main():
    state = AppState()
    params = hello_imgui.RunnerParams()
    params.ini_disable = True
    params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.white_is_white
    params.callbacks.show_gui = lambda: gui(state)
    params.app_window_params.window_geometry.size = (1000, 800)
    params.app_window_params.window_title = "Lesson: Simple Harmonic Motion"
    params.fps_idling.fps_idle = 25
    addons = immapp.AddOnsParams(with_markdown=True, with_implot= True)
    immapp.run(params, addons)


if __name__ == "__main__":
    main()
