import matplotlib
# Important: before importing pyplot, set the renderer to Tk,
# so that the figure is not displayed on the screen before we can capture it.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from imgui_bundle import immapp, imgui, imgui_fig, imgui_ctx
import numpy as np


class AnimatedFigure:
    """A class that encapsulates a Matplotlib figure, and provides a method to animate it."""
    x: np.ndarray
    y: np.ndarray
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
        # Show an animated figure
        with imgui_ctx.begin_group():
            animated_figure.animate()
            imgui_fig.fig("Animated figure", animated_figure.fig, refresh_image=True, show_options_button=False)
            imgui.set_next_item_width(immapp.em_size(20))
            _, animated_figure.amplitude = imgui.slider_float("amplitude", animated_figure.amplitude, 0.1, 2.0)

        imgui.same_line()

        # Show a static figure
        imgui_fig.fig("Static figure", static_fig)


    runner_params = immapp.RunnerParams()
    runner_params.fps_idling.fps_idle = 0  # disable idling, so that the animation is fast
    runner_params.app_window_params.window_geometry.size = (1400, 600)
    runner_params.app_window_params.window_title = "imgui_fig demo"
    runner_params.callbacks.show_gui = gui
    immapp.run(runner_params)


if __name__ == '__main__':
    main()
