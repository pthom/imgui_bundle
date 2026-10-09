"""
Matplotlib figures inside an ImGui window.

`imgui_fig.fig()` shows a [Matplotlib](https://matplotlib.org) figure as an image in the GUI. On the left, an animated
sine wave, redrawn at each frame, with a slider for its amplitude. On the right, a static figure, drawn once. Handy to
reuse existing Matplotlib code; for fast interactive plots, prefer [ImPlot](https://github.com/epezent/implot).

Needs Matplotlib: `pip install "imgui-bundle[matplotlib]"`.
"""

import matplotlib
import matplotlib.pyplot as plt
from imgui_bundle import immapp, imgui, imgui_fig, imgui_ctx, hello_imgui
import numpy as np
from numpy.typing import NDArray

FIGURE_WIDTH = 640  # The figures' width, in pixels: Matplotlib's default (6.4 inches at 100 dpi)


class AnimatedFigure:
    """A class that encapsulates a Matplotlib figure, and provides a method to animate it."""
    x: NDArray[np.float64]
    y: NDArray[np.float64]
    amplitude: float = 1.0
    plotted_curve: matplotlib.lines.Line2D
    phase: float
    fig: matplotlib.figure.Figure
    ax: matplotlib.axes.Axes

    def __init__(self):
        # Data for plotting
        self.phase = 0.0
        self.x = np.arange(0.0, 2.0, 0.01)
        self.y = 1 + np.sin(2 * np.pi * self.x + self.phase) * self.amplitude

        # Create a figure and a set of subplots
        self.fig, self.ax = plt.subplots()

        # Plot the data
        self.plotted_curve, = self.ax.plot(self.x, self.y)

        # Add labels and title
        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='Simple Plot: Voltage vs. Time')

        # Add a grid
        self.ax.grid()

    def animate(self):
        self.phase += 0.1
        self.y = 1 + np.sin(2 * np.pi * self.x + self.phase) * self.amplitude
        self.plotted_curve.set_ydata(self.y)


def main():
    # Create an animated figure
    animated_figure = AnimatedFigure()

    # Create a static figure
    x = np.linspace(-2 * np.pi, 2 * np.pi, 100)
    y = np.sin(x) * np.exp(-x ** 2 / 20)
    static_fig, static_ax = plt.subplots()
    static_ax.plot(x, y)

    def gui():
        # The figures side by side when they fit, else one under the other. In a window narrower than a figure
        # (a phone), they take its width (a negative width).
        avail_width = imgui.get_content_region_avail().x
        fig_size = imgui.ImVec2(-1, 0) if avail_width < FIGURE_WIDTH else None

        # Show an animated figure
        with imgui_ctx.begin_group():
            animated_figure.animate()
            imgui_fig.fig("Animated figure", animated_figure.fig, size=fig_size, refresh_image=True,
                          show_options_button=False)
            hello_imgui.set_item_is_live()  # the figure moves on its own: no idling while it is visible
            imgui.set_next_item_width(immapp.em_size(20))
            _, animated_figure.amplitude = imgui.slider_float("amplitude", animated_figure.amplitude, 0.1, 2.0)

        if avail_width >= 2 * FIGURE_WIDTH:
            imgui.same_line()

        # Show a static figure
        imgui_fig.fig("Static figure", static_fig, size=fig_size)


    runner_params = immapp.RunnerParams()
    runner_params.app_window_params.window_geometry.size = (1400, 600)
    runner_params.app_window_params.window_title = "imgui_fig demo"
    runner_params.callbacks.show_gui = gui
    immapp.run(runner_params)


if __name__ == '__main__':
    main()
