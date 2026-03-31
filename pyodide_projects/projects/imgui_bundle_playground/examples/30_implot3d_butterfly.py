"""# Lorenz Attractor & Butterfly Effect

[ImPlot3D](https://github.com/brenocq/implot3d) adds rotatable, zoomable 3D plots to Dear ImGui.

This demo shows two trajectories that diverge from a tiny initial difference, illustrating **chaos theory**. The term *butterfly effect* comes from the Lorenz attractor: tiny changes in initial conditions lead to completely different outcomes.

**Try it:** drag the plot to rotate, scroll to zoom. Tweak the knobs to change the attractor's shape.

**Links:**
- [ImPlot3D repository](https://github.com/brenocq/implot3d)
- [ImPlot3D in Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/?lib=implot3d) (select "Python" in the top right corner)
"""
import numpy as np
from dataclasses import dataclass
from imgui_bundle import (
    imgui, implot3d, immapp, hello_imgui, imgui_knobs,
)


@dataclass
class LorenzParams:
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0
    dt: float = 0.01
    max_size: int = 2000


class Trajectory:
    """A single Lorenz trajectory."""
    def __init__(self, x: float, y: float, z: float):
        self.xs = np.array([x])
        self.ys = np.array([y])
        self.zs = np.array([z])

    def step(self, p: LorenzParams):
        x, y, z = self.xs[-1], self.ys[-1], self.zs[-1]
        dx = p.sigma * (y - x)
        dy = x * (p.rho - z) - y
        dz = x * y - p.beta * z
        x += dx * p.dt
        y += dy * p.dt
        z += dz * p.dt
        self.xs = np.append(self.xs, x)
        self.ys = np.append(self.ys, y)
        self.zs = np.append(self.zs, z)
        if len(self.xs) > p.max_size:
            self.xs = self.xs[-p.max_size:]
            self.ys = self.ys[-p.max_size:]
            self.zs = self.zs[-p.max_size:]


class AppState:
    params: LorenzParams
    traj1: Trajectory
    traj2: Trajectory
    initial_delta: float = 0.1

    def __init__(self):
        self.params = LorenzParams()
        self.reset()

    def reset(self):
        x, y, z = 0.0, 1.0, 1.05
        self.traj1 = Trajectory(x, y, z)
        self.traj2 = Trajectory(
            x + self.initial_delta, y, z)


def gui(state: AppState) -> None:
    s = state
    p = s.params
    em = imgui.get_font_size()

    # Documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=16)

    # Parameters as knobs (more visual than sliders)
    knob = imgui_knobs.ImGuiKnobVariant_
    knob_size = em * 2.2
    _, p.sigma = imgui_knobs.knob(
        "Sigma", p.sigma, 0, 100,
        variant=knob.wiper_dot, size=knob_size)
    imgui.set_item_tooltip("Rate of divergence (chaos)")
    imgui.same_line()
    _, p.rho = imgui_knobs.knob(
        "Rho", p.rho, 0, 100,
        variant=knob.wiper_dot, size=knob_size)
    imgui.set_item_tooltip("Size/shape of attractor")
    imgui.same_line()
    _, p.beta = imgui_knobs.knob(
        "Beta", p.beta, 0, 10,
        variant=knob.tick, size=knob_size)
    imgui.set_item_tooltip("Damping on vertical movement")
    imgui.same_line()
    _, p.dt = imgui_knobs.knob(
        "dt", p.dt, 0, 0.05,
        variant=knob.stepped, size=knob_size)
    imgui.set_item_tooltip("Time step (smaller=smoother)")
    imgui.same_line()
    _, s.initial_delta = imgui_knobs.knob(
        "Delta", s.initial_delta, 0, 0.2,
        variant=knob.wiper, size=knob_size)
    imgui.set_item_tooltip("Initial difference between trajectories")
    imgui.same_line()
    # Reset button (vertically centered with knobs)
    imgui.set_cursor_pos_y(
        imgui.get_cursor_pos_y() + knob_size * 0.5)
    if imgui.button("Reset"):
        s.reset()

    # 3D plot (fills remaining space)
    avail = imgui.get_content_region_avail()
    auto_fit = implot3d.AxisFlags_.auto_fit
    if implot3d.begin_plot("##lorenz", avail):
        implot3d.setup_axes(
            "X", "Y", "Z",
            auto_fit, auto_fit, auto_fit)
        implot3d.plot_line(
            "Traj 1", s.traj1.xs, s.traj1.ys, s.traj1.zs)
        implot3d.plot_line(
            "Traj 2", s.traj2.xs, s.traj2.ys, s.traj2.zs)
        implot3d.end_plot()

    # Advance simulation
    s.traj1.step(p)
    s.traj2.step(p)


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="ImPlot3D: Butterfly Effect",
        with_implot3d=True,
        with_markdown=True,
        fps_idle=0)


if __name__ == "__main__":
    main()
