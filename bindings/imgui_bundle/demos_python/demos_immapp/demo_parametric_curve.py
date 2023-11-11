import random

import numpy as np
from imgui_bundle import imgui, immapp, implot, imgui_knobs


class Curve:
    "Just a parametric curve to demonstrate how to edit its parameters a, b, & c"
    a = 2.0
    b = 60.0
    c = 2.0

    def get_xy(self):
        """Return x and y arrays that we will draw"""
        t = np.arange(0, np.pi * 2, 0.001)
        x = 2 * np.cos(t) + np.sin(self.a * t) * np.cos(self.b * t)
        y = np.sin(self.c * t) + np.sin(60 * t)
        return x, y


curve = Curve()


def gui():
    "Our gui function, which will be invoked by the application loop"
    x, y = curve.get_xy()

    # Draw the x/y curve
    implot.begin_plot("Play with me")
    implot.plot_line("curve", x, y)
    implot.end_plot()

    # Edit the curve parameters: no callback is needed
    _, curve.a = imgui_knobs.knob("a", curve.a, 0.5, 5.0)
    imgui.same_line()
    _, curve.b = imgui_knobs.knob("b", curve.b, 55, 65)
    imgui.same_line()
    _, curve.c = imgui_knobs.knob("c", curve.c, 0.5, 5.0)

    #                             # As an illustration of the Immediate Gui paradigm,
    if imgui.button("Random"):  # this draws a button
        #                         # and you handle its action immediately!
        curve.a = random.uniform(0.5, 5)
        curve.b = random.uniform(55, 65)
        curve.c = random.uniform(0.5, 5)


# Start your application in one line
immapp.run(gui, with_implot=True)
