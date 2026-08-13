"""Boids
=====

Three trivial local rules — **separation**, **alignment**, **cohesion** —
and a flock emerges. No leader, no plan. Turn the knobs to re-weight the
rules and watch order appear or dissolve. Send in **hunters** that chase
the swarm down, or flip on the **cursor predator** and scatter it yourself.
"""

import numpy as np
from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, imgui_knobs, imgui_toggle, icons_fontawesome_4
from imgui_bundle import ImVec2, ImVec4
from typing import List, Optional
import colorsys
import time

# =============================================================================
# Simulation (vectorized — every boid updated in one numpy pass)
# =============================================================================

MIN_SPEED = 45.0      # boids never freeze; keeps the flock alive
ACCEL = 220.0         # how hard the three rules can steer (px/s^2)
FLEE_RADIUS = 95.0    # predator panic distance
FLEE_SCALE = 650.0    # predator avoidance strength
EDGE_SCALE = 420.0    # turn-back force near the walls
MARGIN = 55.0         # soft border where boids begin to turn

PRED_ACCEL = 320.0          # how sharply a hunter can turn toward its prey
PRED_SPEED_FACTOR = 1.08    # hunters are a touch faster than the boids...
PRED_MIN_FACTOR = 0.6       # ...but never slower than this fraction of max
PRED_CATCH = 11.0           # a boid this close to a hunter gets eaten


def _normalize(v, eps=1e-9):
    """Row-wise unit vectors; all-zero rows stay zero."""
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.maximum(n, eps)


def flock_step(pos, vel, dt, W, H, w_sep, w_align, w_coh,
               perception, max_speed, predators: Optional[np.ndarray]):
    """Advance every boid one step. Returns (pos, vel, neighbor_counts)."""
    sep_radius = max(12.0, 0.45 * perception)

    # Pairwise offsets: delta[i, j] = pos[j] - pos[i]
    delta = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]
    dist2 = np.sum(delta * delta, axis=2)
    np.fill_diagonal(dist2, np.inf)          # ignore self
    dist = np.sqrt(dist2)

    neighbor = dist < perception
    counts = neighbor.sum(axis=1)
    safe = np.maximum(counts, 1)[:, None]
    has = (counts > 0)[:, None]

    # Cohesion: steer toward the average position of neighbors
    mean_pos = (neighbor[:, :, None] * pos[None, :, :]).sum(axis=1) / safe
    cohesion = _normalize((mean_pos - pos) * has)

    # Alignment: steer toward the average heading of neighbors
    mean_vel = (neighbor[:, :, None] * vel[None, :, :]).sum(axis=1) / safe
    alignment = _normalize(mean_vel * has)

    # Separation: steer away from boids that are too close (inverse-distance)
    sep_mask = dist < sep_radius
    inv = sep_mask / np.maximum(dist2, 1e-6)
    separation = _normalize(-(inv[:, :, None] * delta).sum(axis=1))

    accel = ACCEL * (w_sep * separation + w_align * alignment + w_coh * cohesion)

    # Predators: flee hard from every hunter within panic range
    if predators is not None and len(predators):
        away = pos[:, None, :] - predators[None, :, :]            # (N, P, 2)
        pdist = np.linalg.norm(away, axis=2)                      # (N, P)
        units = away / np.maximum(pdist[:, :, None], 1e-9)
        flee = _normalize((units * (pdist < FLEE_RADIUS)[:, :, None]).sum(axis=1))
        accel = accel + FLEE_SCALE * flee

    # Soft walls: turn back inside the margin instead of bouncing
    turn = np.zeros_like(pos)
    turn[:, 0] += (pos[:, 0] < MARGIN)
    turn[:, 0] -= (pos[:, 0] > W - MARGIN)
    turn[:, 1] += (pos[:, 1] < MARGIN)
    turn[:, 1] -= (pos[:, 1] > H - MARGIN)
    accel = accel + EDGE_SCALE * turn

    vel = vel + accel * dt
    speed = np.linalg.norm(vel, axis=1, keepdims=True)
    vel = vel / np.maximum(speed, 1e-9) * np.clip(speed, MIN_SPEED, max_speed)
    pos = pos + vel * dt
    pos[:, 0] = np.clip(pos[:, 0], 0, W)
    pos[:, 1] = np.clip(pos[:, 1], 0, H)
    return pos, vel, counts


def polarization(vel) -> float:
    """Order parameter: 0 = chaos, 1 = everyone aligned."""
    speed = np.linalg.norm(vel, axis=1, keepdims=True)
    return float(np.linalg.norm((vel / np.maximum(speed, 1e-9)).mean(axis=0)))


def edge_spawn(k: int, W: float, H: float):
    """k spawns just inside a random wall, each moving inward. Used for
    initial hunter placement and for re-spawning boids that get eaten."""
    pos = np.empty((k, 2))
    vel = np.empty((k, 2))
    side = np.random.randint(0, 4, k)
    for i in range(k):
        if side[i] == 0:      # left
            pos[i] = [4.0, np.random.uniform(0, H)]
            vel[i] = [1.0, np.random.uniform(-1, 1)]
        elif side[i] == 1:    # right
            pos[i] = [W - 4.0, np.random.uniform(0, H)]
            vel[i] = [-1.0, np.random.uniform(-1, 1)]
        elif side[i] == 2:    # top
            pos[i] = [np.random.uniform(0, W), 4.0]
            vel[i] = [np.random.uniform(-1, 1), 1.0]
        else:                 # bottom
            pos[i] = [np.random.uniform(0, W), H - 4.0]
            vel[i] = [np.random.uniform(-1, 1), -1.0]
    return pos, _normalize(vel) * 100.0


def predator_step(pred_pos, pred_vel, boids, dt, W, H, max_speed):
    """Each hunter accelerates toward its nearest boid. Returns (pos, vel)."""
    if len(pred_pos) == 0 or len(boids) == 0:
        return pred_pos, pred_vel
    d = boids[None, :, :] - pred_pos[:, None, :]          # (P, N, 2)
    nearest = np.argmin(np.sum(d * d, axis=2), axis=1)    # (P,)
    steer = _normalize(boids[nearest] - pred_pos)

    turn = np.zeros_like(pred_pos)
    turn[:, 0] += (pred_pos[:, 0] < MARGIN)
    turn[:, 0] -= (pred_pos[:, 0] > W - MARGIN)
    turn[:, 1] += (pred_pos[:, 1] < MARGIN)
    turn[:, 1] -= (pred_pos[:, 1] > H - MARGIN)

    pred_vel = pred_vel + (PRED_ACCEL * steer + EDGE_SCALE * turn) * dt
    sp = np.linalg.norm(pred_vel, axis=1, keepdims=True)
    pred_vel = pred_vel / np.maximum(sp, 1e-9) * np.clip(
        sp, max_speed * PRED_MIN_FACTOR, max_speed * PRED_SPEED_FACTOR)
    pred_pos = pred_pos + pred_vel * dt
    pred_pos[:, 0] = np.clip(pred_pos[:, 0], 0, W)
    pred_pos[:, 1] = np.clip(pred_pos[:, 1], 0, H)
    return pred_pos, pred_vel


# =============================================================================
# Flock instance
# =============================================================================

class Flock:
    def __init__(self, n: int, W: float, H: float):
        self.max_trail = 18
        self.reseed(n, W, H)

    def reseed(self, n: int, W: float, H: float):
        self.n = n
        self.pos = np.random.uniform(0, 1, (n, 2)) * np.array([W, H])
        ang = np.random.uniform(0, 2 * np.pi, n)
        self.vel = np.stack([np.cos(ang), np.sin(ang)], axis=1) * 100.0
        self.trail: List[np.ndarray] = []

    def rescale(self, sx: float, sy: float):
        self.pos[:, 0] *= sx
        self.pos[:, 1] *= sy
        self.trail.clear()

    def step(self, dt, W, H, w_sep, w_align, w_coh, perception, max_speed,
             predators, keep_trail):
        self.pos, self.vel, counts = flock_step(
            self.pos, self.vel, dt, W, H, w_sep, w_align, w_coh,
            perception, max_speed, predators)
        if keep_trail:
            self.trail.append(self.pos.copy())
            if len(self.trail) > self.max_trail:
                self.trail = self.trail[-self.max_trail:]
        elif self.trail:
            self.trail.clear()
        return counts


# =============================================================================
# Application state
# =============================================================================

class AppState:
    def __init__(self):
        # Rule weights (the three knobs)
        self.w_sep = 1.6
        self.w_align = 1.0
        self.w_coh = 1.0

        # Parameters
        self.n_boids = 200
        self.perception = 55.0
        self.max_speed = 160.0
        self.speed = 1.0

        # Predators
        self.n_hunters = 1          # autonomous chasers
        self.cursor_on = True       # extra predator that follows the mouse
        self.catches = 0
        self.pred_pos = np.empty((0, 2))
        self.pred_vel = np.empty((0, 2))
        self.cursor_pred: Optional[np.ndarray] = None

        # Display
        self.paused = False
        self.show_trails = False
        self.color_heading = True

        # Canvas (refined once the animation pane reports its real size)
        self.W = 820.0
        self.H = 680.0
        self.anim_origin = None
        self.anim_size = None

        # History for the order plot
        self.order_history: List[float] = []
        self.density_history: List[float] = []
        self.max_history = 500

        self.last_time = time.time()
        self.flock = Flock(self.n_boids, self.W, self.H)
        self.spawn_hunters()

    def spawn_hunters(self):
        self.pred_pos, self.pred_vel = edge_spawn(self.n_hunters, self.W, self.H)

    def reset(self):
        self.flock.reseed(self.n_boids, self.W, self.H)
        self.spawn_hunters()
        self.catches = 0
        self.order_history.clear()
        self.density_history.clear()

    def resize_canvas(self, w: float, h: float):
        if w <= 0 or h <= 0:
            return
        if abs(w - self.W) > 1 or abs(h - self.H) > 1:
            sx, sy = w / self.W, h / self.H
            self.flock.rescale(sx, sy)
            if len(self.pred_pos):
                self.pred_pos[:, 0] *= sx
                self.pred_pos[:, 1] *= sy
            self.W, self.H = w, h

    def compute_cursor_predator(self):
        self.cursor_pred = None
        if self.cursor_on and self.anim_origin is not None:
            mp = imgui.get_mouse_pos()
            ox, oy = self.anim_origin
            w, h = self.anim_size
            if ox <= mp.x <= ox + w and oy <= mp.y <= oy + h:
                self.cursor_pred = np.array([mp.x - ox, mp.y - oy], dtype=float)

    def _threats(self) -> Optional[np.ndarray]:
        parts = []
        if len(self.pred_pos):
            parts.append(self.pred_pos)
        if self.cursor_pred is not None:
            parts.append(self.cursor_pred[None, :])
        return np.vstack(parts) if parts else None

    def update(self):
        now = time.time()
        dt = min(now - self.last_time, 0.05)   # cap to avoid a spiral of death
        self.last_time = now
        if self.paused:
            return
        sdt = dt * self.speed

        # Hunters chase the nearest boid first
        self.pred_pos, self.pred_vel = predator_step(
            self.pred_pos, self.pred_vel, self.flock.pos,
            sdt, self.W, self.H, self.max_speed)

        # The flock flees from every threat (hunters + cursor)
        counts = self.flock.step(
            sdt, self.W, self.H,
            self.w_sep, self.w_align, self.w_coh,
            self.perception, self.max_speed,
            self._threats(), self.show_trails)

        # Catches: boids within reach of any hunter re-spawn at an edge
        if len(self.pred_pos):
            dd = np.linalg.norm(
                self.flock.pos[None, :, :] - self.pred_pos[:, None, :], axis=2)
            caught = (dd < PRED_CATCH).any(axis=0)
            k = int(caught.sum())
            if k:
                self.catches += k
                npos, nvel = edge_spawn(k, self.W, self.H)
                idx = np.where(caught)[0]
                self.flock.pos[idx] = npos
                self.flock.vel[idx] = nvel

        self.order_history.append(polarization(self.flock.vel))
        density = float(counts.mean()) / max(self.n_boids - 1, 1)
        self.density_history.append(min(density, 1.0))
        if len(self.order_history) > self.max_history:
            self.order_history = self.order_history[-self.max_history:]
            self.density_history = self.density_history[-self.max_history:]


# =============================================================================
# Drawing
# =============================================================================

def heading_color(vx: float, vy: float, alpha: float = 1.0) -> ImVec4:
    h = (np.arctan2(vy, vx) / (2 * np.pi)) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.65, 1.0)
    return ImVec4(r, g, b, alpha)


FLAT_COLOR = ImVec4(0.55, 0.78, 1.0, 1.0)


def draw_flock(draw_list, state: AppState, origin: ImVec2):
    pos = state.flock.pos
    vel = state.flock.vel
    ox, oy = origin.x, origin.y

    # Trails (drawn under the boids)
    if state.show_trails and len(state.flock.trail) >= 2:
        trail = state.flock.trail
        steps = len(trail)
        for j in range(state.flock.n):
            base = heading_color(vel[j, 0], vel[j, 1]) if state.color_heading else FLAT_COLOR
            for i in range(steps - 1):
                a = (i + 1) / steps * 0.5
                col = imgui.get_color_u32(ImVec4(base.x, base.y, base.z, a))
                x1, y1 = trail[i][j]
                x2, y2 = trail[i + 1][j]
                draw_list.add_line(ImVec2(ox + x1, oy + y1),
                                   ImVec2(ox + x2, oy + y2), col, 1.2)

    # Boids as little arrowheads pointing along their velocity
    speed = np.linalg.norm(vel, axis=1, keepdims=True)
    heading = vel / np.maximum(speed, 1e-9)
    size = 7.0
    for j in range(state.flock.n):
        px, py = ox + pos[j, 0], oy + pos[j, 1]
        ux, uy = heading[j]
        col = imgui.get_color_u32(
            heading_color(ux, uy) if state.color_heading else FLAT_COLOR)
        tip = ImVec2(px + ux * size, py + uy * size)
        left = ImVec2(px - ux * size * 0.6 - uy * size * 0.5,
                      py - uy * size * 0.6 + ux * size * 0.5)
        right = ImVec2(px - ux * size * 0.6 + uy * size * 0.5,
                       py - uy * size * 0.6 - ux * size * 0.5)
        draw_list.add_triangle_filled(tip, left, right, col)

    # Autonomous hunters: red arrowheads with a faint panic ring
    if len(state.pred_pos):
        psp = np.linalg.norm(state.pred_vel, axis=1, keepdims=True)
        phead = state.pred_vel / np.maximum(psp, 1e-9)
        red = imgui.get_color_u32(ImVec4(0.95, 0.22, 0.22, 1.0))
        ring = imgui.get_color_u32(ImVec4(0.95, 0.25, 0.25, 0.16))
        hs = 11.0
        for i in range(len(state.pred_pos)):
            cx, cy = ox + state.pred_pos[i, 0], oy + state.pred_pos[i, 1]
            ux, uy = phead[i]
            draw_list.add_circle(ImVec2(cx, cy), FLEE_RADIUS, ring, 0, 1.5)
            tip = ImVec2(cx + ux * hs, cy + uy * hs)
            left = ImVec2(cx - ux * hs * 0.6 - uy * hs * 0.55,
                          cy - uy * hs * 0.6 + ux * hs * 0.55)
            right = ImVec2(cx - ux * hs * 0.6 + uy * hs * 0.55,
                           cy - uy * hs * 0.6 - ux * hs * 0.55)
            draw_list.add_triangle_filled(tip, left, right, red)

    # Cursor predator
    if state.cursor_pred is not None:
        cx, cy = ox + state.cursor_pred[0], oy + state.cursor_pred[1]
        draw_list.add_circle_filled(ImVec2(cx, cy), 7.0,
                                    imgui.get_color_u32(ImVec4(0.95, 0.45, 0.15, 1.0)))
        draw_list.add_circle(ImVec2(cx, cy), FLEE_RADIUS,
                             imgui.get_color_u32(ImVec4(0.95, 0.45, 0.15, 0.22)), 0, 1.5)


# =============================================================================
# GUI
# =============================================================================

FA_PLAY = icons_fontawesome_4.ICON_FA_PLAY
FA_PAUSE = icons_fontawesome_4.ICON_FA_PAUSE
FA_UNDO = icons_fontawesome_4.ICON_FA_UNDO


def gui(state: AppState):
    state.compute_cursor_predator()
    state.update()

    em = hello_imgui.em_size()
    btn_size = ImVec2(em * 2.5, em * 2.0)
    imgui.push_style_var(imgui.StyleVar_.frame_rounding, em * 0.5)

    # ---- Controls (left column) ------------------------------------------
    imgui.begin_child("controls", ImVec2(em * 20, 0))

    imgui_md.render(__doc__)
    imgui.separator()

    if imgui.button(FA_PAUSE if not state.paused else FA_PLAY, btn_size):
        state.paused = not state.paused
    imgui.same_line()
    if imgui.button(FA_UNDO, btn_size):
        state.reset()

    # The headline: three rules, three knobs
    imgui.separator_text("Flocking rules")
    _, state.w_sep = imgui_knobs.knob(
        "Separation", state.w_sep, 0.0, 3.0, speed=0.01,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper, format="%.1f")
    imgui.same_line()
    _, state.w_align = imgui_knobs.knob(
        "Alignment", state.w_align, 0.0, 3.0, speed=0.01,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper, format="%.1f")
    imgui.same_line()
    _, state.w_coh = imgui_knobs.knob(
        "Cohesion", state.w_coh, 0.0, 3.0, speed=0.01,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper, format="%.1f")

    imgui.separator_text("Parameters")
    changed_n, state.n_boids = imgui.slider_int("Boids", state.n_boids, 8, 600)
    if changed_n:
        state.reset()
    _, state.perception = imgui.slider_float("Perception", state.perception, 15.0, 150.0, "%.0f px")
    _, state.max_speed = imgui.slider_float("Max speed", state.max_speed, 80.0, 300.0, "%.0f")
    _, state.speed = imgui_knobs.knob(
        "Sim speed", state.speed, 0.25, 3.0, speed=0.01,
        variant=imgui_knobs.ImGuiKnobVariant_.stepped, format="%.1fx")

    imgui.separator_text("Display options")
    _, state.color_heading = imgui_toggle.toggle("Color by heading", state.color_heading)
    _, state.show_trails = imgui_toggle.toggle("Trails", state.show_trails)

    imgui.separator_text("Predators")
    changed_h, state.n_hunters = imgui.slider_int("Hunters", state.n_hunters, 0, 5)
    if changed_h:
        state.spawn_hunters()
    _, state.cursor_on = imgui_toggle.toggle("Cursor predator", state.cursor_on)
    imgui.text(f"Caught: {state.catches}")

    # The insight, as a plot: order emerging from local rules
    imgui.separator_text("Emergent order")
    if len(state.order_history) >= 2:
        order = np.array(state.order_history)
        density = np.array(state.density_history)
        xs = np.arange(len(order), dtype=float)
        if implot.begin_plot("##order", ImVec2(-1, imgui.get_font_size() * 12)):
            implot.setup_axes("Frame", "")
            implot.setup_axes_limits(0, float(len(order)), 0.0, 1.05, imgui.Cond_.always)
            implot.plot_line("Alignment", xs, order)
            implot.plot_line("Grouping", xs, density)
            implot.end_plot()

    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")

    imgui.pop_style_var()
    imgui.end_child()

    imgui.same_line()

    # ---- Animation (right area) ------------------------------------------
    imgui.begin_child("animation", ImVec2(0, 0))
    avail = imgui.get_content_region_avail()
    origin = imgui.get_cursor_screen_pos()

    state.anim_origin = (origin.x, origin.y)
    state.anim_size = (avail.x, avail.y)
    state.resize_canvas(avail.x, avail.y)

    draw_list = imgui.get_window_draw_list()
    draw_flock(draw_list, state, origin)

    imgui.end_child()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_title="Boids",
        window_size=(1200, 750),
        with_implot=True,
        with_markdown=True,
        fps_idle=0,
        ini_disable=True,
    )


if __name__ == "__main__":
    main()
