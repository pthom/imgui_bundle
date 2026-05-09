# type: ignore
"""
Double pendulum, streamed via Panel (HoloViz).

Run with:
    pip install panel bokeh
    panel serve pendulum_panel.py --show

Panel sits on top of the Bokeh server, so the transport is the same
WebSocket-based ColumnDataSource patching as the raw-Bokeh demo;
only the layout/widget API differs.
"""
import numpy as np
import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

pn.extension()


def derivs(s, m1, m2, l1, l2, g):
    th1, w1, th2, w2 = s
    d = th2 - th1
    den1 = (m1 + m2) * l1 - m2 * l1 * np.cos(d) ** 2
    den2 = (l2 / l1) * den1
    dw1 = (m2 * l1 * w1 ** 2 * np.sin(d) * np.cos(d) +
           m2 * g * np.sin(th2) * np.cos(d) +
           m2 * l2 * w2 ** 2 * np.sin(d) -
           (m1 + m2) * g * np.sin(th1)) / den1
    dw2 = (-m2 * l2 * w2 ** 2 * np.sin(d) * np.cos(d) +
           (m1 + m2) * g * np.sin(th1) * np.cos(d) -
           (m1 + m2) * l1 * w1 ** 2 * np.sin(d) -
           (m1 + m2) * g * np.sin(th2)) / den2
    return np.array([w1, dw1, w2, dw2])


def rk4(s, dt, *a):
    k1 = derivs(s, *a)
    k2 = derivs(s + 0.5 * dt * k1, *a)
    k3 = derivs(s + 0.5 * dt * k2, *a)
    k4 = derivs(s + dt * k3, *a)
    return s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


M1, M2, L1, L2, G = 1.0, 1.0, 1.0, 1.0, 9.81
INIT = np.array([np.pi * 0.75, 0.0, np.pi * 0.75, 0.0])

state = INIT.copy()
frame = 0

rod_src = ColumnDataSource(data=dict(x=[0, 0, 0], y=[0, 0, 0]))
bob_src = ColumnDataSource(data=dict(x=[0, 0], y=[0, 0], size=[14, 20]))
trail_src = ColumnDataSource(data=dict(x=[], y=[]))
energy_src = ColumnDataSource(data=dict(t=[], ke=[], pe=[]))

p_pend = figure(width=600, height=480, x_range=(-2.5, 2.5), y_range=(-2.5, 1.5),
                output_backend="webgl", tools="", toolbar_location=None,
                title="Double pendulum")
p_pend.line("x", "y", source=trail_src, line_color="orange", line_alpha=0.5)
p_pend.line("x", "y", source=rod_src, line_color="#cccccc", line_width=3)
p_pend.scatter("x", "y", size="size", source=bob_src,
               fill_color="orange", line_color="white")

p_en = figure(width=600, height=200, output_backend="webgl",
              tools="", toolbar_location=None, title="Energy")
p_en.line("t", "ke", source=energy_src, line_color="royalblue", legend_label="KE")
p_en.line("t", "pe", source=energy_src, line_color="crimson", legend_label="PE")
p_en.legend.location = "top_left"

speed = pn.widgets.FloatSlider(name="Speed", start=0.1, end=3.0, step=0.1, value=1.0)
paused = pn.widgets.Checkbox(name="Pause", value=False)
trails_on = pn.widgets.Checkbox(name="Trails", value=True)
reset_btn = pn.widgets.Button(name="Reset")


def do_reset(event):
    global state, frame
    state = INIT.copy()
    frame = 0
    trail_src.data = dict(x=[], y=[])
    energy_src.data = dict(t=[], ke=[], pe=[])


reset_btn.on_click(do_reset)


def tick():
    global state, frame
    if paused.value:
        return
    dt = 0.02 * speed.value
    for _ in range(2):
        state = rk4(state, dt, M1, M2, L1, L2, G)
    th1, w1, th2, w2 = state
    x1, y1 = L1 * np.sin(th1), L1 * np.cos(th1)
    x2, y2 = x1 + L2 * np.sin(th2), y1 + L2 * np.cos(th2)

    rod_src.data = dict(x=[0, x1, x2], y=[0, y1, y2])
    bob_src.data = dict(x=[x1, x2], y=[y1, y2], size=[14, 20])
    if trails_on.value:
        trail_src.stream(dict(x=[x2], y=[y2]), rollover=300)

    v1_sq = (L1 * w1) ** 2
    v2_sq = v1_sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2)
    ke = 0.5 * M1 * v1_sq + 0.5 * M2 * v2_sq
    pe = -(M1 + M2) * G * L1 * np.cos(th1) - M2 * G * L2 * np.cos(th2)
    energy_src.stream(dict(t=[frame], ke=[ke], pe=[pe]), rollover=500)
    frame += 1


pn.state.add_periodic_callback(tick, 33)  # ~30 Hz

app = pn.Row(
    pn.Column(speed, paused, trails_on, reset_btn, width=220),
    pn.Column(p_pend, p_en),
)
app.servable(title="Double pendulum (Panel)")
