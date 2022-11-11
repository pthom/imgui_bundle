import time
import numpy as np
from imgui_bundle import implot, imgui_knobs, imgui, run


vals = np.arange(0, np.pi * 2, 0.01)
x = np.power(np.sin(vals), 3) * 16
y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)

phase = 0
t0 = time.time() + 0.2
heart_pulse_rate = 80


def gui():
    global heart_pulse_rate, phase, t0
    t = time.time()
    phase += (t - t0) * heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(phase)
    t0 = t
    imgui.text("Bloat free code")
    implot.begin_plot("Heart")
    implot.plot_line("", x * k, y * k)
    implot.end_plot()
    _, heart_pulse_rate = imgui_knobs.knob("Pulse", heart_pulse_rate, 30, 180)


if __name__ == "__main__":
    run(gui, window_size=(300, 450), window_title="Hello!", with_implot=True, fps_idle=0)
