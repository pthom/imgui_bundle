"""# Lorenz Attractor & Butterfly Effect
This is a simple example of the Lorenz Attractor. It shows two trajectories that diverge
because of a small initial difference, illustrating chaos theory in action.

The term **butterfly effect** in popular media may stem from the real-world implications
of the Lorenz attractor, namely that tiny changes in initial conditions evolve to
completely different trajectories.
"""

import numpy as np
from imgui_bundle import implot3d, immapp, imgui, imgui_md, hello_imgui
from dataclasses import dataclass


@dataclass
class LorenzParams:
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0
    dt: float = 0.01
    max_size: int = 2000

PARAMS = LorenzParams()


class AnimatedLorenzTrajectory:
    def __init__(self, x, y, z):
        self.xs = np.array([x])
        self.ys = np.array([y])
        self.zs = np.array([z])

    def step(self):
        x, y, z = self.xs[-1], self.ys[-1], self.zs[-1]
        dx = PARAMS.sigma * (y - x)
        dy = x * (PARAMS.rho - z) - y
        dz = x * y - PARAMS.beta * z
        x += dx * PARAMS.dt
        y += dy * PARAMS.dt
        z += dz * PARAMS.dt

        self.xs = np.concatenate([self.xs, [x]])
        self.ys = np.concatenate([self.ys, [y]])
        self.zs = np.concatenate([self.zs, [z]])
        if len(self.xs) > PARAMS.max_size:
            self.xs = self.xs[-PARAMS.max_size:]
            self.ys = self.ys[-PARAMS.max_size:]
            self.zs = self.zs[-PARAMS.max_size:]


class CompareLorenzTrajectories:
    initial_delta = 0.1
    def __init__(self):
        self.init_trajectories()

    def init_trajectories(self):
        x, y, z = 0.0, 1.0, 1.05
        self.traj1 = AnimatedLorenzTrajectory(x, y, z)
        self.traj2 = AnimatedLorenzTrajectory(x + self.initial_delta, y, z)

    def gui_params(self):
        _, PARAMS.sigma = imgui.slider_float("Sigma", PARAMS.sigma, 0.0, 100.0)
        imgui.set_item_tooltip("Controls the rate of divergence between nearby points (chaos level).")

        _, PARAMS.rho = imgui.slider_float("Rho", PARAMS.rho, 0.0, 100.0)
        imgui.set_item_tooltip("Determines the size and shape of the attractor.")

        _, PARAMS.beta = imgui.slider_float("Beta", PARAMS.beta, 0.0, 10.0)
        imgui.set_item_tooltip("A damping parameter affecting vertical movement.")

        _, PARAMS.dt = imgui.slider_float("dt", PARAMS.dt, 0.0, 0.05)
        imgui.set_item_tooltip("Time step size for numerical integration (smaller is smoother).")

        _, self.initial_delta = imgui.slider_float("Initial Delta", self.initial_delta, 0.0, 0.2)
        imgui.set_item_tooltip("Initial difference between trajectories to demonstrate divergence.")

        if imgui.button("Reset"):
            self.init_trajectories()

    def gui_plot(self):
        if implot3d.begin_plot("Lorenz Attractor", hello_imgui.em_to_vec2(40, 40)):
            implot3d.setup_axes("X", "Y", "Z",
                                implot3d.AxisFlags_.auto_fit, implot3d.AxisFlags_.auto_fit, implot3d.AxisFlags_.auto_fit)
            implot3d.plot_line("Trajectory", self.traj1.xs, self.traj1.ys, self.traj1.zs)
            implot3d.plot_line("Trajectory2", self.traj2.xs, self.traj2.ys, self.traj2.zs)
            implot3d.end_plot()
        self.traj1.step()
        self.traj2.step()

    def gui(self):
        imgui_md.render_unindented(__doc__)
        imgui.separator_text("Parameters")
        self.gui_params()
        imgui.separator_text("Plot")
        self.gui_plot()


lorenz_comparer = CompareLorenzTrajectories()

immapp.run(lambda: lorenz_comparer.gui(),
           with_implot3d=True,
           with_markdown=True,
           window_size_auto=True,
           window_title="Butterfly Effect",
           fps_idle=0)
