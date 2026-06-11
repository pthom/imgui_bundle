# type: ignore
"""
Double pendulum, streamed via NiceGUI (FastAPI + socket.io).

Run with:
    pip install nicegui plotly
    python pendulum_nicegui.py
    # then open http://127.0.0.1:8080

NiceGUI pushes updates over a persistent WebSocket. We mutate the
Plotly figure in place and call .update() per tick — NiceGUI ships
the resulting diff to the browser.
"""
import numpy as np
import plotly.graph_objects as go
from nicegui import ui


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
trail_x: list[float] = []
trail_y: list[float] = []
energy_t: list[int] = []
energy_ke: list[float] = []
energy_pe: list[float] = []

pend_fig = go.Figure()
pend_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                                line=dict(color="orange", width=1)))
pend_fig.add_trace(go.Scattergl(x=[0, 0, 0], y=[0, 0, 0], mode="lines",
                                line=dict(color="lightgray", width=3)))
pend_fig.add_trace(go.Scattergl(x=[0, 0], y=[0, 0], mode="markers",
                                marker=dict(size=[14, 20], color="orange",
                                            line=dict(color="white", width=1))))
pend_fig.update_layout(xaxis=dict(range=[-2.5, 2.5]),
                       yaxis=dict(range=[-2.5, 1.5], scaleanchor="x"),
                       showlegend=False, uirevision="locked",
                       margin=dict(l=10, r=10, t=10, b=10))

en_fig = go.Figure()
en_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                              line=dict(color="royalblue"), name="KE"))
en_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                              line=dict(color="crimson"), name="PE"))
en_fig.update_layout(uirevision="locked",
                     margin=dict(l=10, r=10, t=10, b=10))

with ui.row():
    with ui.column().classes("w-56"):
        ui.label("Speed")
        speed = ui.slider(min=0.1, max=3.0, step=0.1, value=1.0)
        paused = ui.checkbox("Pause", value=False)
        trails_on = ui.checkbox("Trails", value=True)
        reset_btn = ui.button("Reset")
    with ui.column():
        pend_plot = ui.plotly(pend_fig).classes("w-[600px] h-[480px]")
        en_plot = ui.plotly(en_fig).classes("w-[600px] h-[200px]")


def do_reset():
    global state, frame
    state = INIT.copy()
    frame = 0
    trail_x.clear(); trail_y.clear()
    energy_t.clear(); energy_ke.clear(); energy_pe.clear()


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

    pend_fig.data[1].x = (0, x1, x2)
    pend_fig.data[1].y = (0, y1, y2)
    pend_fig.data[2].x = (x1, x2)
    pend_fig.data[2].y = (y1, y2)
    if trails_on.value:
        trail_x.append(x2); trail_y.append(y2)
        if len(trail_x) > 300:
            del trail_x[:-300]; del trail_y[:-300]
        pend_fig.data[0].x = trail_x
        pend_fig.data[0].y = trail_y
    pend_plot.update()

    v1_sq = (L1 * w1) ** 2
    v2_sq = v1_sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2)
    ke = 0.5 * M1 * v1_sq + 0.5 * M2 * v2_sq
    pe = -(M1 + M2) * G * L1 * np.cos(th1) - M2 * G * L2 * np.cos(th2)
    energy_t.append(frame); energy_ke.append(ke); energy_pe.append(pe)
    if len(energy_t) > 500:
        del energy_t[:-500]; del energy_ke[:-500]; del energy_pe[:-500]
    en_fig.data[0].x = energy_t
    en_fig.data[0].y = energy_ke
    en_fig.data[1].x = energy_t
    en_fig.data[1].y = energy_pe
    en_plot.update()
    frame += 1


ui.timer(0.033, tick)
ui.run(reload=False, title="Double pendulum (NiceGUI)")
