"""
A beating heart, in a few lines of ImPlot.

A heart curve drawn with [ImPlot](https://github.com/epezent/implot) beats at the rate set by a knob from
[imgui-knobs](https://github.com/altschuler/imgui-knobs). A few lines of Python: a parametric curve, scaled by a pulse
at each frame. Turn the knobs to change the heart rate, or its thickness.
"""

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
heart_pulse_rate = 80.0
heart_thickness = 0.15
LARGEST_SCALE = 0.9 * 1.3  # of the heart: the pulse scales it up to 0.9, the thickness knob up to 1.3

def gui():
    global heart_pulse_rate, phase, t0, x, y, heart_thickness

    t = time.time()
    phase += (t - t0) * heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(phase)
    t0 = t

    if implot.begin_plot("Heart", immapp.em_to_vec2(21, 21)):  # False when the plot is not visible (clipped)
        # Axes sized for the largest heart (fitted to the first frame's heart, a small one, they would clip the next)
        implot.setup_axes_limits(x.min() * LARGEST_SCALE, x.max() * LARGEST_SCALE,
                                 y.min() * LARGEST_SCALE, y.max() * LARGEST_SCALE)
        for k2 in np.arange(1 - heart_thickness, 1 + heart_thickness, 0.01):  # Give some thickness to the heart
            implot.plot_line("", x * k * k2, y * k * k2)
        implot.end_plot()
        hello_imgui.set_item_is_live()  # the heart beats on its own: the app keeps its full speed while visible

    _, heart_pulse_rate = imgui_knobs.knob("Pulse", heart_pulse_rate, 30, 180,
                                           variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=hello_imgui.em_size(4.0))
    imgui.same_line()
    _, heart_thickness = imgui_knobs.knob("Line Thickness", heart_thickness, 0.01, 0.3,
                                         variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=hello_imgui.em_size(4.0))


if __name__ == "__main__":
    immapp.run(gui, window_size=(380, 470), with_implot=True)
