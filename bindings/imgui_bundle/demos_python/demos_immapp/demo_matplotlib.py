"""Matplotlib: a pendulum's phase portrait
========================================

`imgui_fig.fig()` shows a [Matplotlib](https://matplotlib.org) figure in the GUI. Here, the phase portrait of a damped
pendulum: the flow of its motion (a stream plot) over its energy (filled contours). Click in the portrait: the pendulum
starts from there, and swings beside it.

<!--more-->

Matplotlib draws what [ImPlot](https://github.com/epezent/implot) cannot: the stream plot and the contours. A figure
takes a while to draw, so the demo redraws it only when the damping changes. What moves is drawn at every frame with
ImGui's draw list, over the figure and beside it: the trajectory, its moving point, the pendulum. `ax.transData`
converts the axes' coordinates into the figure's pixels.

The motion: `θ'' = -sin(θ) - b θ'`, with b the damping. With little damping, a fast start sends the pendulum over the
top a few times, before it spirals to rest.

Needs Matplotlib: `pip install "imgui-bundle[matplotlib]"`.
"""
import math
from dataclasses import dataclass

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from imgui_bundle import imgui, imgui_fig, immapp, hello_imgui, rich_md, ImVec2

FIGURE_MAX_WIDTH = 640.0  # the figure's width at most, in points (Matplotlib's default: 6.4 inches at 100 dpi)
THETA_MAX = 2 * math.pi  # the portrait shows the angles in [-THETA_MAX, THETA_MAX]
OMEGA_MAX = 3.0  # and the velocities in [-OMEGA_MAX, OMEGA_MAX]
DURATION = 30.0  # the simulated time of a trajectory, in seconds
DT = 0.02  # the time step of the simulation
TIME_SCALE = 2.0  # the simulated seconds shown per second
TRAJECTORY_COLOR = imgui.IM_COL32(255, 120, 60, 255)


def trajectory(theta: float, omega: float, damping: float) -> np.ndarray:
    """The angle and the velocity every DT, over DURATION (Runge-Kutta, order 4): an array of shape (n, 2)"""

    def accel(th: float, om: float) -> float:
        return -math.sin(th) - damping * om

    points = [(theta, omega)]
    for _ in range(int(DURATION / DT)):
        k1t, k1o = omega, accel(theta, omega)
        k2t, k2o = omega + DT / 2 * k1o, accel(theta + DT / 2 * k1t, omega + DT / 2 * k1o)
        k3t, k3o = omega + DT / 2 * k2o, accel(theta + DT / 2 * k2t, omega + DT / 2 * k2o)
        k4t, k4o = omega + DT * k3o, accel(theta + DT * k3t, omega + DT * k3o)
        theta += DT / 6 * (k1t + 2 * k2t + 2 * k3t + k4t)
        omega += DT / 6 * (k1o + 2 * k2o + 2 * k3o + k4o)
        points.append((theta, omega))
    return np.array(points)


def portrait_figure(damping: float, width: float) -> tuple[Figure, Axes]:
    """The phase portrait: the flow of the motion over the energy. width: in points"""
    # More pixels than points on a high density screen (a Retina display, a phone): the figure stays sharp
    dpi = 100.0 * min(imgui.get_io().display_framebuffer_scale.x, 2.0)
    fig = Figure(figsize=(width / 100.0, width * 0.7 / 100.0), dpi=dpi, layout="constrained")
    ax = fig.add_subplot()
    theta, omega = np.meshgrid(np.linspace(-THETA_MAX, THETA_MAX, 160), np.linspace(-OMEGA_MAX, OMEGA_MAX, 120))
    energy = omega**2 / 2 + 1 - np.cos(theta)
    ax.contourf(theta, omega, energy, levels=20, cmap="viridis")
    ax.streamplot(theta, omega, omega, -np.sin(theta) - damping * omega,
                  color="white", linewidth=0.6, density=1.1, arrowsize=0.7)
    ax.set(xlim=(-THETA_MAX, THETA_MAX), ylim=(-OMEGA_MAX, OMEGA_MAX), xlabel=r"angle $\theta$",
           ylabel=r"velocity $\dot\theta$", title=f"Phase portrait, damping b = {damping:.2f}")
    return fig, ax


@dataclass
class AppState:
    damping: float = 0.25
    start: tuple[float, float] = (-6.0, 2.6)  # the angle and the velocity at the start
    points: np.ndarray | None = None  # the trajectory: see trajectory()
    time: float = 0.0  # the time shown, in the trajectory
    fig: Figure | None = None
    ax: Axes | None = None
    fig_damping: float = -1.0  # the damping and the width the figure was drawn with
    fig_width: float = 0.0


state = AppState()


def figure_to_screen(pixels: np.ndarray, image_min: ImVec2, image_max: ImVec2) -> np.ndarray:
    """Points in the figure's pixels (y up) to the screen, where the figure shows as an image (y down)"""
    assert state.fig is not None
    w, h = state.fig.bbox.width, state.fig.bbox.height
    x = image_min.x + pixels[:, 0] / w * (image_max.x - image_min.x)
    y = image_min.y + (1.0 - pixels[:, 1] / h) * (image_max.y - image_min.y)
    return np.stack([x, y], axis=1)


def draw_trajectory_over_figure(image_min: ImVec2, image_max: ImVec2) -> None:
    """The trajectory and its moving point, drawn over the figure's axes"""
    assert state.ax is not None and state.points is not None
    draw_list = imgui.get_window_draw_list()
    axes_corners = figure_to_screen(np.array(state.ax.bbox.get_points()), image_min, image_max)
    clip_min, clip_max = axes_corners.min(axis=0), axes_corners.max(axis=0)  # y flips: min and max swap
    draw_list.push_clip_rect(ImVec2(*clip_min), ImVec2(*clip_max), True)

    # The angle wrapped into the portrait (two turns wide): the line breaks where it jumps across
    wrapped = state.points.copy()
    wrapped[:, 0] = (wrapped[:, 0] + THETA_MAX) % (2 * THETA_MAX) - THETA_MAX
    screen = figure_to_screen(state.ax.transData.transform(wrapped), image_min, image_max)
    jumps = np.nonzero(np.abs(np.diff(wrapped[:, 0])) > THETA_MAX)[0] + 1
    for segment in np.split(screen, jumps):
        draw_list.add_polyline([ImVec2(*p) for p in segment], TRAJECTORY_COLOR, 2.0, imgui.ImDrawFlags_.none)

    i = min(int(state.time / DT), len(screen) - 1)
    draw_list.add_circle_filled(ImVec2(*screen[i]), hello_imgui.em_size(0.4), imgui.IM_COL32(255, 255, 255, 255))
    draw_list.add_circle(ImVec2(*screen[i]), hello_imgui.em_size(0.4), TRAJECTORY_COLOR, 0, 2.0)
    draw_list.pop_clip_rect()


def draw_pendulum(theta: float, side: float) -> None:
    """The pendulum at this angle, drawn with the draw list in a square"""
    top_left = imgui.get_cursor_screen_pos()
    imgui.dummy(ImVec2(side, side))
    draw_list = imgui.get_window_draw_list()
    text_color = imgui.get_color_u32(imgui.Col_.text)
    pivot = ImVec2(top_left.x + side / 2, top_left.y + side / 2)  # in the middle: the pendulum can go over the top
    length = side * 0.4
    bob = ImVec2(pivot.x + length * math.sin(theta), pivot.y + length * math.cos(theta))
    draw_list.add_circle(pivot, length, imgui.get_color_u32(imgui.Col_.text_disabled), 0, 1.0)  # the bob's path
    draw_list.add_line(pivot, bob, text_color, 3.0)
    draw_list.add_circle_filled(bob, side * 0.06, TRAJECTORY_COLOR)
    draw_list.add_circle_filled(pivot, side * 0.02, text_color)


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    imgui.set_next_item_width(hello_imgui.em_size(12))
    changed, state.damping = imgui.slider_float("damping b", state.damping, 0.0, 1.0)
    damping_dragged = imgui.is_item_active()
    if changed or state.points is None:
        state.points = trajectory(state.start[0], state.start[1], state.damping)

    # The figure: as wide as the window, at most FIGURE_MAX_WIDTH. Matplotlib redraws it only when the damping
    # changes (once the slider is released), or when the window's width changes much.
    avail_width = imgui.get_content_region_avail().x
    width = min(FIGURE_MAX_WIDTH, avail_width)
    redraw = state.fig is None or abs(width - state.fig_width) > hello_imgui.em_size(2)
    redraw = redraw or (state.fig_damping != state.damping and not damping_dragged)
    if redraw:
        state.fig, state.ax = portrait_figure(state.damping, width)
        state.fig_damping, state.fig_width = state.damping, width
    assert state.fig is not None and state.ax is not None

    imgui.begin_group()
    imgui_fig.fig("portrait", state.fig, size=ImVec2(state.fig_width, state.fig_width * 0.7), refresh_image=redraw,
                  resizable=False)
    image_min, image_max = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    if imgui.is_item_hovered() and imgui.is_mouse_clicked(imgui.MouseButton_.left):
        # A click: the mouse, from the screen to the figure's pixels (y up), then to the axes' coordinates
        mouse = imgui.get_mouse_pos()
        px = (mouse.x - image_min.x) / (image_max.x - image_min.x) * state.fig.bbox.width
        py = (1.0 - (mouse.y - image_min.y) / (image_max.y - image_min.y)) * state.fig.bbox.height
        theta, omega = state.ax.transData.inverted().transform((px, py))
        if abs(theta) <= THETA_MAX and abs(omega) <= OMEGA_MAX:
            state.start = (float(theta), float(omega))
            state.points = trajectory(state.start[0], state.start[1], state.damping)
            state.time = 0.0
    draw_trajectory_over_figure(image_min, image_max)
    touch = imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen
    imgui.text_disabled(("Tap" if touch else "Click") + " in the portrait: the pendulum starts there.")
    imgui.end_group()

    # The pendulum: beside the figure when there is room, else below it, smaller and centered (a phone)
    side = hello_imgui.em_size(14.0)
    if avail_width >= state.fig_width + side + imgui.get_style().item_spacing.x:
        imgui.same_line()
    else:
        side = hello_imgui.em_size(8.0)
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_width - side) / 2)
    assert state.points is not None
    theta, omega = state.points[min(int(state.time / DT), len(state.points) - 1)]
    imgui.begin_group()
    draw_pendulum(theta, side)
    hello_imgui.set_item_is_live()  # the pendulum moves on its own: no idling while it is visible
    imgui.text_disabled(f"angle {theta:.1f}, velocity {omega:.1f}")
    imgui.end_group()

    state.time += imgui.get_io().delta_time * TIME_SCALE
    if state.time > DURATION:  # at rest by then: the motion starts over
        state.time = 0.0


def main() -> None:
    immapp.run(gui, window_title="Matplotlib: a pendulum's phase portrait", window_size=(1000, 760),
               with_markdown=True)


if __name__ == "__main__":
    main()
