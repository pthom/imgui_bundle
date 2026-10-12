"""Seaborn: a joint plot of two correlated variables
===================================================

[Seaborn](https://seaborn.pydata.org) draws statistics figures on top of Matplotlib, so `imgui_fig.fig()` shows them
as they are. Here, a joint plot of two correlated variables: their scatter plot in the middle, the distribution of each
on its side. Move the correlation: the cloud stretches along a line.

<!--more-->

Three kinds of joint plot: a regression (the scatter, its line, and the confidence band of the line), the density
(the contours of a kernel density estimate), and hexagonal bins. A seaborn figure takes a while to draw: the demo
redraws it when a slider is released. The data come from numpy: seaborn's `load_dataset()` downloads its datasets,
which a browser may refuse.

Needs seaborn: `pip install seaborn`.
"""
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from imgui_bundle import imgui, imgui_fig, immapp, hello_imgui, rich_md, ImVec2

FIGURE_MAX_SIDE = 560.0  # the figure's side at most, in points (it is square)
KINDS = ["reg", "kde", "hex"]  # the kinds of joint plot, by their names in seaborn
KIND_LABELS = ["Regression", "Density", "Hexagons"]


def sample(correlation: float, count: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Two normal variables with this correlation"""
    rng = np.random.default_rng(seed)
    covariance = [[1.0, correlation], [correlation, 1.0]]
    x, y = rng.multivariate_normal([0.0, 0.0], covariance, count).T
    return x, y


def joint_plot(x: np.ndarray, y: np.ndarray, kind: str, side: float) -> sns.JointGrid:
    """Seaborn's joint plot, in a square figure. side: in points"""
    # A style for this figure only: Matplotlib's global settings stay. No grid behind the hexagons: they cut its lines
    with sns.axes_style("ticks" if kind == "hex" else "whitegrid"):
        grid = sns.jointplot(x=x, y=y, kind=kind, height=side / 100.0)
    grid.set_axis_labels("x", "y")  # arrays have no names (a pandas DataFrame's columns would give them)
    grid.figure.tight_layout()  # room for the labels
    # More pixels than points on a high density screen (a Retina display, a phone): the figure stays sharp
    grid.figure.set_dpi(100.0 * min(imgui.get_io().display_framebuffer_scale.x, 2.0))
    return grid


@dataclass
class AppState:
    correlation: float = 0.7
    count: int = 300  # the number of points
    kind: int = 0  # in KINDS
    seed: int = 0  # "New sample" changes it
    grid: sns.JointGrid | None = None  # the figure, as seaborn made it
    drawn: tuple[float, int, int, int] = (0.0, 0, 0, 0)  # the parameters it was drawn with
    drawn_side: float = 0.0
    sample_correlation: float = 0.0  # the correlation measured on the sample


state = AppState()


def gui() -> None:
    about = rich_md.FoldingTextOptions()
    about.start_folded = True  # its first paragraph; "More..." shows the rest
    rich_md.render_folding("about", __doc__ or "", about)

    imgui.set_next_item_width(hello_imgui.em_size(12))
    _, state.correlation = imgui.slider_float("correlation", state.correlation, -0.95, 0.95)
    sliding = imgui.is_item_active()
    imgui.set_next_item_width(hello_imgui.em_size(12))
    _, state.count = imgui.slider_int("points", state.count, 50, 2000)
    sliding = sliding or imgui.is_item_active()
    imgui.set_next_item_width(hello_imgui.em_size(12))
    _, state.kind = imgui.combo("kind", state.kind, KIND_LABELS)
    imgui.same_line()
    if imgui.button("New sample"):
        state.seed += 1

    # The figure: as wide as the window, at most FIGURE_MAX_SIDE. Seaborn redraws it when a parameter changes (once
    # the slider is released), or when the window's width changes much.
    side = min(FIGURE_MAX_SIDE, imgui.get_content_region_avail().x)
    params = (state.correlation, state.count, state.kind, state.seed)
    redraw = state.grid is None or abs(side - state.drawn_side) > hello_imgui.em_size(2)
    redraw = redraw or (params != state.drawn and not sliding)
    if redraw:
        if state.grid is not None:
            plt.close(state.grid.figure)  # seaborn made it with pyplot, which keeps it until it is closed
        x, y = sample(state.correlation, state.count, state.seed)
        state.grid = joint_plot(x, y, KINDS[state.kind], side)
        state.drawn, state.drawn_side = params, side
        state.sample_correlation = float(np.corrcoef(x, y)[0, 1])
    assert state.grid is not None

    imgui_fig.fig("joint plot", state.grid.figure, size=ImVec2(state.drawn_side, state.drawn_side),
                  refresh_image=redraw, resizable=False)
    imgui.text_disabled(f"The correlation measured on this sample: {state.sample_correlation:.2f}")


def main() -> None:
    immapp.run(gui, window_title="Seaborn: a joint plot", window_size=(760, 900), with_markdown=True)


if __name__ == "__main__":
    main()
