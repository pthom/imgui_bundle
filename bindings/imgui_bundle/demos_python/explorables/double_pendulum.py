from urllib.parse import quote

def latex(tex: str, dpi: int = 150, color: str = "white") -> str:
    """Return a markdown image string for a LaTeX equation via codecogs."""
    return f"![](https://latex.codecogs.com/png.latex?{quote(chr(92) + f'dpi{{{dpi}}}' + chr(92) + f'color{{{color}}}{tex}')})"

DOCS = f"""Double Pendulum
=================

A chaotic system where tiny changes in initial conditions
lead to wildly different trajectories. Drag the angles to set
initial positions, then release and watch chaos unfold.

{latex(r"T = \frac{1}{2}(m_1+m_2)\,l_1^2\dot\theta_1^2 + \frac{1}{2}m_2\,l_2^2\dot\theta_2^2")}

{latex(r"\quad + \; m_2\,l_1 l_2\,\dot\theta_1\dot\theta_2\cos(\theta_1-\theta_2)")}

{latex(r"U = -(m_1+m_2)g\,l_1\cos\theta_1 - m_2 g\,l_2\cos\theta_2")}
"""

import numpy as np
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_knobs, imgui_toggle, icons_fontawesome_4
from imgui_bundle import ImVec2, ImVec4
from typing import List, Tuple
import time
import colorsys

# =============================================================================
# Physics
# =============================================================================

def double_pendulum_derivs(state, m1, m2, l1, l2, g):
    """Compute derivatives for double pendulum: [theta1, omega1, theta2, omega2]."""
    th1, w1, th2, w2 = state
    delta = th2 - th1
    den1 = (m1 + m2) * l1 - m2 * l1 * np.cos(delta)**2
    den2 = (l2 / l1) * den1

    dth1 = w1
    dth2 = w2
    dw1 = (m2 * l1 * w1**2 * np.sin(delta) * np.cos(delta) +
           m2 * g * np.sin(th2) * np.cos(delta) +
           m2 * l2 * w2**2 * np.sin(delta) -
           (m1 + m2) * g * np.sin(th1)) / den1
    dw2 = (-m2 * l2 * w2**2 * np.sin(delta) * np.cos(delta) +
           (m1 + m2) * g * np.sin(th1) * np.cos(delta) -
           (m1 + m2) * l1 * w1**2 * np.sin(delta) -
           (m1 + m2) * g * np.sin(th2)) / den2

    return np.array([dth1, dw1, dth2, dw2])


def rk4_step(state, dt, m1, m2, l1, l2, g):
    """4th-order Runge-Kutta integration step."""
    k1 = double_pendulum_derivs(state, m1, m2, l1, l2, g)
    k2 = double_pendulum_derivs(state + 0.5 * dt * k1, m1, m2, l1, l2, g)
    k3 = double_pendulum_derivs(state + 0.5 * dt * k2, m1, m2, l1, l2, g)
    k4 = double_pendulum_derivs(state + dt * k3, m1, m2, l1, l2, g)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def pendulum_positions(th1, th2, l1, l2):
    """Convert angles to (x, y) positions of both bobs."""
    x1 = l1 * np.sin(th1)
    y1 = l1 * np.cos(th1)
    x2 = x1 + l2 * np.sin(th2)
    y2 = y1 + l2 * np.cos(th2)
    return (x1, y1), (x2, y2)


def kinetic_potential_energy(state, m1, m2, l1, l2, g):
    th1, w1, th2, w2 = state
    v1_sq = (l1 * w1)**2
    v2_sq = (l1 * w1)**2 + (l2 * w2)**2 + 2 * l1 * l2 * w1 * w2 * np.cos(th1 - th2)
    T = 0.5 * m1 * v1_sq + 0.5 * m2 * v2_sq
    U = -(m1 + m2) * g * l1 * np.cos(th1) - m2 * g * l2 * np.cos(th2)
    return T, U


# =============================================================================
# Pendulum instance (for running multiple in parallel)
# =============================================================================

class Pendulum:
    def __init__(self, th1: float, th2: float, color: ImVec4):
        self.state = np.array([th1, 0.0, th2, 0.0])
        self.trail: List[Tuple[float, float]] = []
        self.color = color
        self.max_trail = 3000

    def step(self, dt, m1, m2, l1, l2, g, substeps=4):
        sub_dt = dt / substeps
        for _ in range(substeps):
            self.state = rk4_step(self.state, sub_dt, m1, m2, l1, l2, g)
        _, p2 = pendulum_positions(self.state[0], self.state[2], l1, l2)
        self.trail.append(p2)
        if len(self.trail) > self.max_trail:
            self.trail = self.trail[-self.max_trail:]


# =============================================================================
# Application state
# =============================================================================

def make_rainbow_color(index: int, total: int, alpha: float = 1.0) -> ImVec4:
    h = index / max(total, 1)
    r, g, b = colorsys.hsv_to_rgb(h, 0.8, 1.0)
    return ImVec4(r, g, b, alpha)


class AppState:
    def __init__(self):
        self.m1 = 1.0
        self.m2 = 1.0
        self.l1 = 1.0
        self.l2 = 1.0
        self.g = 9.81
        self.speed = 1.0

        self.init_th1 = np.pi * 0.75
        self.init_th2 = np.pi * 0.75

        self.paused = False
        self.show_trails = True
        self.show_ghost = True
        self.n_ghosts = 5
        self.ghost_spread = 0.05

        self.last_time = time.time()
        self.ke_history: List[float] = []
        self.pe_history: List[float] = []
        self.max_energy_history = 500

        self.pendulums: List[Pendulum] = []
        self.reset()

    def reset(self):
        self.pendulums.clear()
        self.ke_history.clear()
        self.pe_history.clear()
        # Main pendulum
        self.pendulums.append(Pendulum(self.init_th1, self.init_th2,
                                       ImVec4(1.0, 1.0, 1.0, 1.0)))
        # Ghost pendulums with tiny perturbations
        if self.show_ghost:
            for i in range(self.n_ghosts):
                offset = self.ghost_spread * (i + 1) / self.n_ghosts
                color = make_rainbow_color(i, self.n_ghosts, 0.7)
                self.pendulums.append(Pendulum(
                    self.init_th1 + offset, self.init_th2, color))

    def update(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)  # cap to avoid spiral of death
        self.last_time = now
        if self.paused:
            return
        sim_dt = dt * self.speed
        for p in self.pendulums:
            p.step(sim_dt, self.m1, self.m2, self.l1, self.l2, self.g)
        # Track kinetic and potential energy of main pendulum
        ke, pe = kinetic_potential_energy(self.pendulums[0].state, self.m1, self.m2,
                                          self.l1, self.l2, self.g)
        self.ke_history.append(ke)
        self.pe_history.append(pe)
        if len(self.ke_history) > self.max_energy_history:
            self.ke_history = self.ke_history[-self.max_energy_history:]
            self.pe_history = self.pe_history[-self.max_energy_history:]


# =============================================================================
# Drawing
# =============================================================================

def draw_pendulum(draw_list, p: Pendulum, pivot: ImVec2, scale: float,
                  l1: float, l2: float, is_main: bool, show_trail: bool):
    th1, _, th2, _ = p.state
    (x1, y1), (x2, y2) = pendulum_positions(th1, th2, l1, l2)

    # Convert to screen coords (y is down)
    sx1 = pivot.x + x1 * scale
    sy1 = pivot.y + y1 * scale
    sx2 = pivot.x + x2 * scale
    sy2 = pivot.y + y2 * scale

    col = imgui.get_color_u32(p.color)
    trail_col_base = p.color

    # Trail
    if show_trail and len(p.trail) >= 2:
        for i in range(len(p.trail) - 1):
            alpha = (i + 1) / len(p.trail)
            tc = imgui.get_color_u32(ImVec4(
                trail_col_base.x, trail_col_base.y, trail_col_base.z,
                alpha * trail_col_base.w * 0.6))
            px1 = pivot.x + p.trail[i][0] * scale
            py1 = pivot.y + p.trail[i][1] * scale
            px2 = pivot.x + p.trail[i + 1][0] * scale
            py2 = pivot.y + p.trail[i + 1][1] * scale
            draw_list.add_line(ImVec2(px1, py1), ImVec2(px2, py2),
                             tc, 2.0 if is_main else 1.5)

    # Rods
    rod_alpha = 0.9 if is_main else 0.4
    rod_col = imgui.get_color_u32(ImVec4(0.8, 0.8, 0.8, rod_alpha))
    rod_thickness = 3.0 if is_main else 1.5
    draw_list.add_line(pivot, ImVec2(sx1, sy1), rod_col, rod_thickness)
    draw_list.add_line(ImVec2(sx1, sy1), ImVec2(sx2, sy2), rod_col, rod_thickness)

    # Bobs
    if is_main:
        bob_radius1 = 8.0
        bob_radius2 = 10.0
        draw_list.add_circle_filled(ImVec2(sx1, sy1), bob_radius1,
                                    imgui.get_color_u32(ImVec4(0.9, 0.5, 0.2, 1.0)))
        draw_list.add_circle_filled(ImVec2(sx2, sy2), bob_radius2, col)
    else:
        draw_list.add_circle_filled(ImVec2(sx2, sy2), 4.0, col)

    # Pivot
    if is_main:
        draw_list.add_circle_filled(pivot, 5.0,
                                    imgui.get_color_u32(ImVec4(0.6, 0.6, 0.6, 1.0)))


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
    imgui.begin_child("controls", ImVec2(em * 20, 0))

    imgui_md.render(DOCS)
    imgui.spacing()

    # Initial angles
    changed_th1, state.init_th1 = imgui_knobs.knob(
        "Angle 1", state.init_th1, 0, 2 * np.pi,
        speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.2f")
    imgui.same_line()
    changed_th2, state.init_th2 = imgui_knobs.knob(
        "Angle 2", state.init_th2, 0, 2 * np.pi,
        speed=0.02, variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        format="%.2f")

    if changed_th1 or changed_th2:
        state.reset()

    imgui.same_line()

    # Speed knob
    _, state.speed = imgui_knobs.knob(
        "Speed", state.speed, 0.1, 3.0,
        speed=0.01, variant=imgui_knobs.ImGuiKnobVariant_.stepped,
        format="%.1fx")

    imgui.spacing()

    # Play/Pause + Reset
    rounding = em * 0.5
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, rounding)
    btn_size = ImVec2(em * 2.5, em * 2.0)
    if imgui.button(FA_PAUSE if not state.paused else FA_PLAY, btn_size):
        state.paused = not state.paused
    imgui.same_line()
    if imgui.button(FA_UNDO, btn_size):
        state.reset()
    imgui.pop_style_var()

    imgui.spacing()

    # Display options
    _, state.show_trails = imgui_toggle.toggle("Trails##tog", state.show_trails)
    imgui.same_line()
    imgui.text("Trails")

    changed_ghost, state.show_ghost = imgui_toggle.toggle("Ghost##tog", state.show_ghost)
    imgui.same_line()
    imgui.text("Chaos comparison")

    if state.show_ghost:
        changed_n, state.n_ghosts = imgui.slider_int("##nghosts", state.n_ghosts, 1, 12)
        imgui.same_line()
        imgui.text("Ghosts")
        changed_s, state.ghost_spread = imgui.slider_float(
            "##spread", state.ghost_spread, 0.001, 0.2, "%.3f")
        imgui.same_line()
        imgui.text("Spread")
        if changed_ghost or changed_n or changed_s:
            state.reset()
    elif changed_ghost:
        state.reset()

    imgui.spacing()
    imgui.separator()
    imgui.spacing()

    # Energy plot: kinetic vs potential
    imgui.text("Energy exchange")
    if len(state.ke_history) > 1:
        ke = np.array(state.ke_history)
        pe = np.array(state.pe_history)
        xs = np.arange(len(ke), dtype=float)
        all_e = np.concatenate([ke, pe])
        e_min, e_max = float(np.min(all_e)), float(np.max(all_e))
        e_range = max(e_max - e_min, 0.1)
        if implot.begin_plot("##energy", ImVec2(-1, em * 14)):
            implot.setup_axes("Frame", "Energy")
            implot.setup_axes_limits(
                0, float(len(ke)),
                e_min - e_range * 0.1, e_max * 1.3 + e_range * 0.1,
                imgui.Cond_.always)
            implot.plot_line("Kinetic", xs, ke)
            implot.plot_line("Potential", xs, pe)
            implot.end_plot()
    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")

    imgui.end_child()

    imgui.same_line()

    # Animation (right area)
    imgui.begin_child("animation", ImVec2(0, 0))
    avail = imgui.get_content_region_avail()
    # Pivot at top-center
    pivot = imgui.get_cursor_screen_pos()
    pivot = ImVec2(pivot.x + avail.x * 0.5, pivot.y + avail.y * 0.3)

    total_length = state.l1 + state.l2
    scale = min(avail.x, avail.y) * 0.3 / total_length

    draw_list = imgui.get_window_draw_list()

    # Draw ghosts first (behind main)
    for p in reversed(state.pendulums[1:]):
        draw_pendulum(draw_list, p, pivot, scale, state.l1, state.l2,
                     is_main=False, show_trail=state.show_trails)
    # Draw main pendulum on top
    if state.pendulums:
        draw_pendulum(draw_list, state.pendulums[0], pivot, scale,
                     state.l1, state.l2, is_main=True,
                     show_trail=state.show_trails)

    imgui.end_child()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_title="Double Pendulum",
        window_size=(1200, 750),
        with_implot=True,
        with_markdown=True,
        fps_idle=0,
    )


if __name__ == "__main__":
    main()
