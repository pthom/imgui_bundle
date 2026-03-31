"""Animated plot using ImPlot
=============================

> A minimal animated plot using ImPlot (available in imgui_bundle).

This example draws a parametric heart curve and animates it with a pulse.

**Try this:**
- Modify the heart shape by editing `state.x` / `state.y`
- Reduce the number of curves: `range(10)` → `range(5)`
- Change the animation: tweak `k = 0.8 + ...`

**Key idea:**
State is stored as function attributes (`show_heart.state` pattern), avoiding globals.

*Click **Run** after each change*
"""

import time
import numpy as np
from imgui_bundle import implot, imgui, immapp, hello_imgui, imgui_toggle, imgui_knobs, imgui_md


def show_heart():
    # Store mutable state as function attributes (avoids globals)
    state = show_heart
    if not hasattr(state, "initialized"):
        # Fill state.x and state.y whose plot is a heart
        vals = np.arange(0, np.pi * 2, 0.01)
        state.x = np.power(np.sin(vals), 3) * 16
        state.y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)
        # Heart pulse rate and time tracking
        state.phase = 0.0
        state.t0 = time.time()
        state.heart_pulse_rate = 80
        state.initialized = True

    t = time.time()
    state.phase += (t - state.t0) * state.heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(state.phase)
    state.t0 = t

    imgui_md.render(__doc__)

    implot.begin_plot("Heart", immapp.em_to_vec2(21, 21))
    for i in range(10):
        implot.plot_line("", state.x * k, state.y * k * (1 - 0.02 * i))
    implot.end_plot()

    imgui.set_next_item_width(hello_imgui.em_size(10))
    _, state.heart_pulse_rate = imgui_knobs.knob(
        "Pulse", state.heart_pulse_rate, 30, 180,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot)


if __name__ == "__main__":
    immapp.run_with_markdown(show_heart,
               window_size=(800, 700),
               window_title="Hello!",
               with_implot=True,
               fps_idle=0)
