# type: ignore
"""
Double pendulum, streamed via Dash + Plotly.

Run with:
    pip install dash plotly
    python sandbox_tmp_plotly.py
    # then open http://127.0.0.1:8050

Streaming primitives used:
  - dcc.Interval               : server-side periodic tick
  - Output("graph","extendData"): append-only, with maxPoints auto-trim
  - Patch()                    : partial figure diff (only changed fields shipped)
"""
import numpy as np
import plotly.graph_objects as go  # type: ignore
from dash import Dash, Input, Output, Patch, State, callback, dcc, html, no_update


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
INIT = {"th1": np.pi * 0.75, "w1": 0.0, "th2": np.pi * 0.75, "w2": 0.0, "frame": 0}

# Trace order is fixed and referenced by index in extendData / Patch:
#   pendulum graph: 0=trail, 1=rod, 2=bobs
#   energy   graph: 0=KE, 1=PE
pend_fig = go.Figure()
pend_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                                line=dict(color="orange", width=1), name="trail"))
pend_fig.add_trace(go.Scattergl(x=[0, 0, 0], y=[0, 0, 0], mode="lines",
                                line=dict(color="lightgray", width=3), name="rod"))
pend_fig.add_trace(go.Scattergl(x=[0, 0], y=[0, 0], mode="markers",
                                marker=dict(size=[14, 20], color="orange",
                                            line=dict(color="white", width=1)),
                                name="bobs"))
pend_fig.update_layout(xaxis=dict(range=[-2.5, 2.5]),
                       yaxis=dict(range=[-2.5, 1.5], scaleanchor="x"),
                       showlegend=False, uirevision="locked",
                       margin=dict(l=10, r=10, t=30, b=10), title="Double pendulum")

en_fig = go.Figure()
en_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                              line=dict(color="royalblue"), name="KE"))
en_fig.add_trace(go.Scattergl(x=[], y=[], mode="lines",
                              line=dict(color="crimson"), name="PE"))
en_fig.update_layout(uirevision="locked",
                     margin=dict(l=10, r=10, t=30, b=10), title="Energy")

app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Label("Speed"),
        dcc.Slider(0.1, 3.0, 0.1, value=1.0, id="speed"),
        dcc.Checklist([{"label": "Pause", "value": "p"},
                       {"label": "Trails", "value": "t"}],
                      value=["t"], id="flags"),
        html.Button("Reset", id="reset"),
    ], style={"width": "220px", "display": "inline-block",
              "verticalAlign": "top", "padding": "10px"}),
    html.Div([
        dcc.Graph(id="pendulum", figure=pend_fig),
        dcc.Graph(id="energy", figure=en_fig),
    ], style={"display": "inline-block"}),
    dcc.Store(id="state", data=INIT),
    dcc.Interval(id="tick", interval=33),  # ~30 Hz
])


@callback(
    Output("pendulum", "extendData"),
    Output("pendulum", "figure"),
    Output("energy", "extendData"),
    Output("state", "data"),
    Input("tick", "n_intervals"),
    State("state", "data"),
    State("speed", "value"),
    State("flags", "value"),
    prevent_initial_call=True,
)
def step(_, st, speed, flags):
    if "p" in flags:
        return no_update, no_update, no_update, no_update
    s = np.array([st["th1"], st["w1"], st["th2"], st["w2"]])
    dt = 0.02 * speed
    for _ in range(2):
        s = rk4(s, dt, M1, M2, L1, L2, G)
    th1, w1, th2, w2 = s
    x1, y1 = L1 * np.sin(th1), L1 * np.cos(th1)
    x2, y2 = x1 + L2 * np.sin(th2), y1 + L2 * np.cos(th2)

    # Rod (trace 1) and bobs (trace 2): small full-array updates via Patch
    patch = Patch()
    patch["data"][1]["x"] = [0, x1, x2]
    patch["data"][1]["y"] = [0, y1, y2]
    patch["data"][2]["x"] = [x1, x2]
    patch["data"][2]["y"] = [y1, y2]

    # Trail (trace 0): append a single point, browser trims to last 300
    trail_ext = ((dict(x=[[x2]], y=[[y2]]), [0], 300)
                 if "t" in flags else no_update)

    v1_sq = (L1 * w1) ** 2
    v2_sq = v1_sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2)
    ke = 0.5 * M1 * v1_sq + 0.5 * M2 * v2_sq
    pe = -(M1 + M2) * G * L1 * np.cos(th1) - M2 * G * L2 * np.cos(th2)

    frame = st["frame"] + 1
    energy_ext = (dict(x=[[frame], [frame]], y=[[ke], [pe]]), [0, 1], 500)
    new_state = {"th1": float(th1), "w1": float(w1),
                 "th2": float(th2), "w2": float(w2), "frame": frame}
    return trail_ext, patch, energy_ext, new_state


@callback(Output("state", "data", allow_duplicate=True),
          Output("pendulum", "figure", allow_duplicate=True),
          Output("energy", "figure", allow_duplicate=True),
          Input("reset", "n_clicks"),
          prevent_initial_call=True)
def reset(_):
    clear = Patch()
    clear["data"][0]["x"] = []
    clear["data"][0]["y"] = []
    clear_en = Patch()
    clear_en["data"][0]["x"] = []
    clear_en["data"][0]["y"] = []
    clear_en["data"][1]["x"] = []
    clear_en["data"][1]["y"] = []
    return INIT, clear, clear_en


if __name__ == "__main__":
    app.run(debug=False)
