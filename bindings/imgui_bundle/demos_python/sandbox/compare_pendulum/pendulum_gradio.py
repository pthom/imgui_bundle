# type: ignore
import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time

# =============================================================================
# Physics (same as original)
# =============================================================================
def double_pendulum_derivs(state, m1, m2, l1, l2, g):
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
    k1 = double_pendulum_derivs(state, m1, m2, l1, l2, g)
    k2 = double_pendulum_derivs(state + 0.5 * dt * k1, m1, m2, l1, l2, g)
    k3 = double_pendulum_derivs(state + 0.5 * dt * k2, m1, m2, l1, l2, g)
    k4 = double_pendulum_derivs(state + dt * k3, m1, m2, l1, l2, g)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

def pendulum_positions(th1, th2, l1, l2):
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
# Gradio App
# =============================================================================
class Pendulum:
    def __init__(self, th1, th2, color):
        self.state = np.array([th1, 0.0, th2, 0.0])
        self.trail = []
        self.color = color
        self.max_trail = 150

def reset_pendulums(angle1, angle2, show_ghost, n_ghosts, ghost_spread):
    pendulums = []
    pendulums.append(Pendulum(angle1, angle2, (1.0, 1.0, 1.0, 1.0)))
    if show_ghost:
        for i in range(n_ghosts):
            offset = ghost_spread * (i + 1) / n_ghosts
            h = i / max(n_ghosts, 1)
            r, g, b = plt.get_cmap("hsv")(h)[:3]
            pendulums.append(Pendulum(angle1 + offset, angle2, (r, g, b, 0.7)))
    return pendulums

def update_pendulum(angle1, angle2, speed, show_trails, show_ghost, n_ghosts, ghost_spread, paused, pendulums, ke_history, pe_history):
    if paused:
        return pendulums, ke_history, pe_history

    m1, m2, l1, l2, g = 1.0, 1.0, 1.0, 1.0, 9.81
    dt = 0.05 * speed

    new_pendulums = []
    for p in pendulums:
        new_state = rk4_step(p.state, dt, m1, m2, l1, l2, g)
        _, p2 = pendulum_positions(new_state[0], new_state[2], l1, l2)
        new_trail = p.trail + [p2]
        if len(new_trail) > p.max_trail:
            new_trail = new_trail[-p.max_trail:]
        new_pendulums.append(Pendulum(new_state[0], new_state[2], p.color))
        new_pendulums[-1].trail = new_trail

    # Update energy history
    if new_pendulums:
        ke, pe = kinetic_potential_energy(new_pendulums[0].state, m1, m2, l1, l2, g)
        new_ke_history = ke_history + [ke]
        new_pe_history = pe_history + [pe]
        if len(new_ke_history) > 500:
            new_ke_history = new_ke_history[-500:]
            new_pe_history = new_pe_history[-500:]
    else:
        new_ke_history, new_pe_history = ke_history, pe_history

    return new_pendulums, new_ke_history, new_pe_history

_pendulum_fig, _pendulum_ax = plt.subplots(figsize=(8, 6))
_energy_fig, _energy_ax = plt.subplots(figsize=(8, 3))

def draw_pendulum(pendulums, show_trails):
    ax = _pendulum_ax
    ax.clear()
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")

    for i, p in enumerate(pendulums):
        (x1, y1), (x2, y2) = pendulum_positions(p.state[0], p.state[2], 1.0, 1.0)
        is_main = (i == 0)
        color = p.color

        # Trail
        if show_trails and len(p.trail) >= 2:
            trail_x = [t[0] for t in p.trail]
            trail_y = [t[1] for t in p.trail]
            ax.plot(trail_x, trail_y, color=(*color[:3], 0.3), linewidth=1.0 if is_main else 0.5)

        # Rods
        ax.plot([0, x1], [0, y1], color=(0.8, 0.8, 0.8, 0.9 if is_main else 0.4), linewidth=3.0 if is_main else 1.5)
        ax.plot([x1, x2], [y1, y2], color=(0.8, 0.8, 0.8, 0.9 if is_main else 0.4), linewidth=3.0 if is_main else 1.5)

        # Bobs
        if is_main:
            ax.add_patch(Circle((x1, y1), 0.08, color=(0.9, 0.5, 0.2)))
            ax.add_patch(Circle((x2, y2), 0.1, color=color))
        else:
            ax.add_patch(Circle((x2, y2), 0.04, color=color))

    return _pendulum_fig

def draw_energy(ke_history, pe_history):
    ax = _energy_ax
    ax.clear()
    if len(ke_history) >= 2:
        ax.plot(ke_history, label="Kinetic", color="blue")
        ax.plot(pe_history, label="Potential", color="orange")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Energy")
        ax.legend()
    return _energy_fig

def update_plot(angle1, angle2, speed, show_trails, show_ghost, n_ghosts, ghost_spread, paused, pendulums, ke_history, pe_history):
    pendulums, ke_history, pe_history = update_pendulum(angle1, angle2, speed, show_trails, show_ghost, n_ghosts, ghost_spread, paused, pendulums, ke_history, pe_history)
    pendulum_fig = draw_pendulum(pendulums, show_trails)
    energy_fig = draw_energy(ke_history, pe_history)
    return pendulum_fig, energy_fig, pendulums, ke_history, pe_history

with gr.Blocks(title="Double Pendulum (Gradio)") as demo:
    gr.Markdown("# Double Pendulum (Gradio)")
    gr.Markdown("A chaotic system where tiny changes in initial conditions lead to wildly different trajectories.")

    with gr.Row():
        with gr.Column(scale=1):
            angle1 = gr.Slider(0, 2 * np.pi, value=np.pi * 0.75, label="Angle 1")
            angle2 = gr.Slider(0, 2 * np.pi, value=np.pi * 0.75, label="Angle 2")
            speed = gr.Slider(0.1, 3.0, value=1.0, step=0.1, label="Speed")
            show_trails = gr.Checkbox(value=True, label="Show Trails")
            show_ghost = gr.Checkbox(value=True, label="Show Ghosts")
            n_ghosts = gr.Slider(1, 12, value=5, step=1, label="Nb Ghosts")
            ghost_spread = gr.Slider(1e-6, 0.1, value=0.00001, step=1e-6, label="Spread")
            paused = gr.Checkbox(value=False, label="Pause")
            reset_btn = gr.Button("Reset")

        with gr.Column(scale=3):
            pendulum_plot = gr.Plot(label="Double Pendulum")
            energy_plot = gr.Plot(label="Energy Exchange")

    # Initialize state
    pendulums = gr.State(reset_pendulums(np.pi * 0.75, np.pi * 0.75, True, 5, 0.00001))
    ke_history = gr.State([])
    pe_history = gr.State([])

    # Reset function
    def reset():
        return (reset_pendulums(angle1.value, angle2.value, show_ghost.value, n_ghosts.value, ghost_spread.value),
                [], [])

    reset_btn.click(
        fn=reset,
        outputs=[pendulums, ke_history, pe_history]
    )

    # Animation loop
    demo.load(
        fn=lambda: (draw_pendulum(pendulums.value, show_trails.value),
                    draw_energy(ke_history.value, pe_history.value)),
        outputs=[pendulum_plot, energy_plot]
    )

    timer = gr.Timer(0.1)
    timer.tick(
        fn=update_plot,
        inputs=[angle1, angle2, speed, show_trails, show_ghost, n_ghosts, ghost_spread, paused, pendulums, ke_history, pe_history],
        outputs=[pendulum_plot, energy_plot, pendulums, ke_history, pe_history],
    )

demo.queue(default_concurrency_limit=1).launch()