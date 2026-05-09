# type: ignore
"""
Double pendulum, streamed via Shiny for Python (Posit) + Plotly FigureWidget.

Run with:
    pip install shiny shinywidgets plotly
    shiny run --reload pendulum_shiny.py

Shiny's reactive model + WebSocket transport drives the loop:
  - reactive.invalidate_later(dt) re-fires the effect every `dt` seconds
  - the Plotly FigureWidget is mutated in place inside batch_update();
    only the diff is shipped to the browser.
"""
import numpy as np
import plotly.graph_objects as go
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget


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

app_ui = ui.page_fluid(
    ui.row(
        ui.column(3,
            ui.input_slider("speed", "Speed", 0.1, 3.0, 1.0, step=0.1),
            ui.input_checkbox("paused", "Pause", False),
            ui.input_checkbox("trails", "Trails", True),
            ui.input_action_button("reset", "Reset"),
        ),
        ui.column(9,
            output_widget("pendulum"),
            output_widget("energy"),
        ),
    ),
)


def server(input, output, session):
    bag = {"s": INIT.copy(), "frame": 0,
           "tx": [], "ty": [],
           "et": [], "ke": [], "pe": []}

    pend_fig = go.FigureWidget()
    pend_fig.add_scatter(x=[], y=[], mode="lines",
                         line=dict(color="orange", width=1), name="trail")
    pend_fig.add_scatter(x=[0, 0, 0], y=[0, 0, 0], mode="lines",
                         line=dict(color="lightgray", width=3), name="rod")
    pend_fig.add_scatter(x=[0, 0], y=[0, 0], mode="markers",
                         marker=dict(size=[14, 20], color="orange",
                                     line=dict(color="white", width=1)),
                         name="bobs")
    pend_fig.update_layout(xaxis=dict(range=[-2.5, 2.5]),
                           yaxis=dict(range=[-2.5, 1.5], scaleanchor="x"),
                           showlegend=False, uirevision="locked",
                           width=600, height=480,
                           margin=dict(l=10, r=10, t=10, b=10))

    en_fig = go.FigureWidget()
    en_fig.add_scatter(x=[], y=[], mode="lines",
                       line=dict(color="royalblue"), name="KE")
    en_fig.add_scatter(x=[], y=[], mode="lines",
                       line=dict(color="crimson"), name="PE")
    en_fig.update_layout(uirevision="locked",
                         width=600, height=200,
                         margin=dict(l=10, r=10, t=10, b=10))

    @render_widget
    def pendulum():
        return pend_fig

    @render_widget
    def energy():
        return en_fig

    @reactive.effect
    @reactive.event(input.reset)
    def _reset():
        bag["s"] = INIT.copy()
        bag["frame"] = 0
        bag["tx"].clear(); bag["ty"].clear()
        bag["et"].clear(); bag["ke"].clear(); bag["pe"].clear()
        with pend_fig.batch_update():
            pend_fig.data[0].x = []
            pend_fig.data[0].y = []
        with en_fig.batch_update():
            en_fig.data[0].x = []
            en_fig.data[0].y = []
            en_fig.data[1].x = []
            en_fig.data[1].y = []

    @reactive.effect
    def _tick():
        reactive.invalidate_later(0.033)  # ~30 Hz
        if input.paused():
            return
        s = bag["s"]
        dt = 0.02 * input.speed()
        for _ in range(2):
            s = rk4(s, dt, M1, M2, L1, L2, G)
        bag["s"] = s
        th1, w1, th2, w2 = s
        x1, y1 = L1 * np.sin(th1), L1 * np.cos(th1)
        x2, y2 = x1 + L2 * np.sin(th2), y1 + L2 * np.cos(th2)

        if input.trails():
            bag["tx"].append(x2); bag["ty"].append(y2)
            if len(bag["tx"]) > 300:
                del bag["tx"][:-300]; del bag["ty"][:-300]

        v1_sq = (L1 * w1) ** 2
        v2_sq = v1_sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2)
        ke = 0.5 * M1 * v1_sq + 0.5 * M2 * v2_sq
        pe = -(M1 + M2) * G * L1 * np.cos(th1) - M2 * G * L2 * np.cos(th2)
        bag["et"].append(bag["frame"])
        bag["ke"].append(ke); bag["pe"].append(pe)
        if len(bag["et"]) > 500:
            del bag["et"][:-500]; del bag["ke"][:-500]; del bag["pe"][:-500]
        bag["frame"] += 1

        with pend_fig.batch_update():
            pend_fig.data[1].x = (0, x1, x2)
            pend_fig.data[1].y = (0, y1, y2)
            pend_fig.data[2].x = (x1, x2)
            pend_fig.data[2].y = (y1, y2)
            if input.trails():
                pend_fig.data[0].x = bag["tx"]
                pend_fig.data[0].y = bag["ty"]
        with en_fig.batch_update():
            en_fig.data[0].x = bag["et"]
            en_fig.data[0].y = bag["ke"]
            en_fig.data[1].x = bag["et"]
            en_fig.data[1].y = bag["pe"]


app = App(app_ui, server)
