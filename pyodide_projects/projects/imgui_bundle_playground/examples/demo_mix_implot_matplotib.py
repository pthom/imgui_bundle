"""Demonstrates plots generated using ImPlot and Matplotlib in the same application.
"""
import matplotlib
matplotlib.use("Agg")

from fiatlight import fiat_implot
import fiatlight as fl
import numpy as np
import math
import time
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from enum import Enum


_start_time = time.time()


def time_seconds() -> float:
    """Returns the time in seconds since the start of the application."""
    return time.time() - _start_time


def phase_from_time_seconds(time_: float) -> float:
    """Converts time in seconds to a phase value."""
    return time_ * 15.0


time_seconds.invoke_always_dirty = True  # type: ignore


@fl.with_fiat_attributes(
    label="Sine Wave (ImPlot)",
    phase__range=(0.0, 2 * math.pi),
    amplitude__range=(0.0, 4.0),
)
def sin_wave(phase: float, amplitude: float = 1.0) -> fiat_implot.FloatMatrix_Dim2:
    """A sine wave with adjustable phase and amplitude."""
    x = np.arange(0, 10, 0.1)
    y = np.sin(x + phase) * amplitude
    r = np.stack((x, y))
    return r  # type: ignore


@fl.with_fiat_attributes(
    label="Spirograph (ImPlot)",
    radius_fixed_circle__range=(0.0, 100.0),
    radius_moving_circle__range=(0.0, 100.0),
    pen_offset__range=(0.0, 100.0),
    nb_turns__range=(0.0, 100.0),
    nb_turns__edit_type="knob",
)
def make_spirograph_curve(
    radius_fixed_circle: float = 10.84,
    radius_moving_circle: float = 3.48,
    pen_offset: float = 6.0,
    nb_turns: float = 23.0,
) -> fiat_implot.FloatMatrix_Dim2:
    """a spirograph-like curve"""
    t = np.linspace(0, 2 * np.pi * nb_turns, int(500 * nb_turns))
    x = (radius_fixed_circle + radius_moving_circle) * np.cos(t) - pen_offset * np.cos(
        (radius_fixed_circle + radius_moving_circle) / radius_moving_circle * t
    )
    y = (radius_fixed_circle + radius_moving_circle) * np.sin(t) - pen_offset * np.sin(
        (radius_fixed_circle + radius_moving_circle) / radius_moving_circle * t
    )
    return np.array([x, y])  # type: ignore


class ColorMap(Enum):
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"


@fl.with_fiat_attributes(
    label="Gaussian Heatmap (Matplotlib)",
    mean__range=(-5, 5),
    variance__range=(0.1, 5),
    levels__range=(1, 20),
)
def gaussian_heatmap(
    mean: float = 0, variance: float = 1, colormap: ColorMap = ColorMap.VIRIDIS, levels: int = 10
) -> Figure:
    """Generates a Gaussian heatmap with adjustable mean, variance, colormap, and number of contour levels."""
    x = y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((X - mean) ** 2 + (Y - mean) ** 2) / (2 * variance))
    fig, ax = plt.subplots()
    contour = ax.contourf(X, Y, Z, levels, cmap=colormap.value)
    fig.colorbar(contour, ax=ax)
    return fig


@fl.with_fiat_attributes(
    label="Interactive Histogram (Matplotlib)",
    n_bars__range=(1, 50),
    mu__range=(-5, 5),
    sigma__range=(0.1, 5),
    average__range=(0, 1000),
    nb_data__range=(100, 1_000_000),
    nb_data__slider_logarithmic=True,
)
def interactive_histogram(
    n_bars: int = 10,
    mu: float = 0,
    sigma: float = 1,
    average: float = 500,
    nb_data: int = 1000,
) -> Figure:
    """Generates an interactive histogram with adjustable number of bars, mean, and standard deviation."""
    data = np.random.normal(mu, sigma, int(nb_data)) + average
    bins = np.linspace(np.min(data), np.max(data), n_bars)
    fig, ax = plt.subplots()
    ax.hist(data, bins=bins, color="blue", alpha=0.7)
    return fig


def main() -> None:
    graph = fl.FunctionsGraph()

    # ImPlot functions
    graph.add_function(make_spirograph_curve)

    graph.add_function(time_seconds)
    graph.add_function(phase_from_time_seconds)
    graph.add_function(sin_wave)
    graph.add_link("time_seconds", "phase_from_time_seconds")
    graph.add_link("phase_from_time_seconds", "sin_wave")

    # Matplotlib functions
    graph.add_function(gaussian_heatmap)
    graph.add_function(interactive_histogram)

    fl.run(graph, params=fl.FiatRunParams(app_name="Mix ImPlot - Matplotlib", theme=fl.ImGuiTheme_.white_is_white))


if __name__ == "__main__":
    main()
