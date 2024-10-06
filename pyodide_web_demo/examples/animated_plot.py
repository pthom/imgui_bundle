import time
import numpy as np

from imgui_bundle import implot, imgui_knobs, imgui, immapp, hello_imgui

# Fill x and y whose plot is a heart
vals = np.arange(0, np.pi * 2, 0.01)
x = np.power(np.sin(vals), 3) * 16
y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)
# Heart pulse rate and time tracking
phase = 0.0
t0 = time.time() + 0.2
heart_pulse_rate = 80


def gui():
    global heart_pulse_rate, phase, t0, x, y
    # Make sure that the animation is smooth
    hello_imgui.get_runner_params().fps_idling.enable_idling = False

    t = time.time()
    phase += (t - t0) * heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(phase)
    t0 = t

    imgui.text("Bloat free code")
    implot.begin_plot("Heart", immapp.em_to_vec2(21, 21))
    implot.plot_line("", x * k, y * k)
    implot.end_plot()

    _, heart_pulse_rate = imgui_knobs.knob("Pulse", heart_pulse_rate, 30, 180)


if __name__ == "__main__":
    immapp.run(gui, window_size=(300, 450), window_title="Hello!", with_implot=True, fps_idle=0)  # type: ignore
