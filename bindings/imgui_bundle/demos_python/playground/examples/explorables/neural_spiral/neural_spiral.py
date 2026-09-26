"""A tiny neural network learns two spirals

Can 16 neurons tell two spirals apart? Watch a tiny [neural
network](https://en.wikipedia.org/wiki/Neural_network_(machine_learning)) learn, live, as in the [TensorFlow
Playground](https://playground.tensorflow.org). Then read how it works, formula by formula, next to its numpy
code.

This explorable is written in two files (narrative programming, see imgui_rich_md):
- tiny_nn.py: the network, in numpy, with its explanation in ::md sections next to its code
- this file: the story, the data and the widgets. The story transcludes the sections of tiny_nn.py
  (![[tiny_nn.py#Network]] for the prose, ![[tiny_nn.py#Network#code]] for the code), and places the widgets
  with fenced blocks of the language "widget", as julia_map.py does.

Edit the prose of either file while the program runs: on the desktop, the story follows upon saving.
"""


r"""::md Story
# Can 16 neurons tell two spirals apart?
The points below come in two colors, on two spirals that wind into each other: no straight line separates them.
A tiny neural network learns to tell them apart. The background shows its answer at every point of the plane, red
for class 0 and blue for class 1, and changes while it learns. **Press Train.**

```widget
playground
```

The network is written in numpy, in its own file, `tiny_nn.py`. The sections below come from there, prose and code:
the program imports the file, the story tells it.

![[tiny_nn.py#Network]]
![[tiny_nn.py#Network#code]]

Change the number of hidden units, then train again: with 8, the network gets stuck around 80% of the points
right; with 4, it barely does better than a guess.
```widget
hidden_units
```

![[tiny_nn.py#Loss]]
![[tiny_nn.py#Loss#code]]
![[tiny_nn.py#Gradients]]
![[tiny_nn.py#Gradients#code]]
![[tiny_nn.py#Step]]
![[tiny_nn.py#Step#code]]

Too small a learning rate, and learning crawls (try 0.1). Too large, and the steps overshoot: from 3 up, the loss
jumps around and the network learns nothing.
```widget
learning_rate
```

![[#Data]]
![[#Data#code]]
"""


# ruff: noqa: E402  # Allow imports to come after the story
import numpy as np
from imgui_bundle import imgui, immapp, implot, rich_md, em_to_vec2, hello_imgui
from tiny_nn import Network, random_network, forward, loss, step


r"""::md Data
### The data
Two spirals of 100 points each: the distance to the center grows with the angle, and the second spiral is the
first one turned by half a turn. A little noise keeps the points off the exact curves.
::code
"""
def make_spirals(n: int, turns: float, noise: float,
                 rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """n points (n, 2), and their classes (n,): 0 on the first spiral, 1 on the second"""
    radius = np.tile(np.linspace(0.08, 1.0, n // 2), 2)
    y = np.repeat([0.0, 1.0], n // 2)
    angle = 2 * np.pi * turns * radius + np.pi * y
    x = np.stack([radius * np.cos(angle), radius * np.sin(angle)], axis=1)
    return x + rng.normal(0, noise, x.shape), y
# ::endcode


N_POINTS, TURNS, NOISE = 200, 2.0, 0.02
STEPS_PER_FRAME = 20
EXTENT = 1.2  # the plane shown: [-EXTENT, EXTENT] on both axes
GRID = 100  # the network's answer is drawn on a GRID x GRID heatmap
_coords = np.linspace(-EXTENT, EXTENT, GRID)
GRID_POINTS = np.stack(np.meshgrid(_coords, _coords[::-1]), axis=-1).reshape(-1, 2)  # row 0 on top, as heatmaps draw


class State:
    def __init__(self) -> None:
        self.rng = np.random.default_rng()
        self.x, self.y = make_spirals(N_POINTS, TURNS, NOISE, self.rng)
        self.hidden = 16
        self.rate = 1.0
        self.training = False
        self.reset()

    def reset(self) -> None:
        self.net: Network = random_network(self.hidden, self.rng)
        self.steps = 0
        self.losses: list[float] = []
        self.record()

    def record(self) -> None:
        """The loss, and the share of the points the network gets right"""
        _, p = forward(self.net, self.x)
        self.losses.append(loss(p, self.y))
        self.accuracy = float(np.mean((p > 0.5) == (self.y > 0.5)))

    def train(self) -> None:
        for _ in range(STEPS_PER_FRAME):
            step(self.net, self.x, self.y, self.rate)
        self.steps += STEPS_PER_FRAME
        self.record()


state = State()


def answer_colormap() -> int:
    """Muted red (class 0), dark grey where the network hesitates, muted blue (class 1): the points stay visible"""
    cmap = implot.get_colormap_index("answer")
    if cmap == -1:
        colors = np.array([[0.5, 0.15, 0.15, 1.0], [0.15, 0.15, 0.15, 1.0], [0.15, 0.25, 0.55, 1.0]], np.float32)
        cmap = implot.add_colormap("answer", colors, qual=False)
    return cmap


# The widgets that the story places in its ```widget blocks
def playground_widget() -> None:
    """The points over the network's answer, the loss beside them, and the buttons"""
    if state.training:
        state.train()
    hello_imgui.get_runner_params().fps_idling.enable_idling = not state.training

    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text
    if implot.begin_plot("##plane", em_to_vec2(22, 22), flags | implot.Flags_.equal):
        implot.setup_axes_limits(-EXTENT, EXTENT, -EXTENT, EXTENT, imgui.Cond_.always)
        _, p = forward(state.net, GRID_POINTS)
        implot.push_colormap(answer_colormap())
        implot.plot_heatmap("##answer", p.reshape(GRID, GRID), 0.0, 1.0, "",
                            implot.Point(-EXTENT, -EXTENT), implot.Point(EXTENT, EXTENT))
        implot.pop_colormap()
        for label, cls, color in (("class 0", 0.0, imgui.ImVec4(1.0, 0.35, 0.35, 1.0)),
                                  ("class 1", 1.0, imgui.ImVec4(0.35, 0.6, 1.0, 1.0))):
            points = state.x[state.y == cls]
            implot.plot_scatter(label, points[:, 0].copy(), points[:, 1].copy(), spec=implot.Spec(
                marker=implot.Marker_.circle, marker_size=4, marker_fill_color=color,
                marker_line_color=imgui.ImVec4(1, 1, 1, 1)))
        implot.end_plot()
    imgui.same_line()
    if implot.begin_plot("Loss", em_to_vec2(20, 22), flags):
        implot.setup_axes("step", "", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
        implot.plot_line("loss", np.array(state.losses), xscale=STEPS_PER_FRAME)
        implot.end_plot()

    if imgui.button("Pause" if state.training else "Train", em_to_vec2(5, 0)):
        state.training = not state.training
    imgui.same_line()
    if imgui.button("Reset"):
        state.reset()
    imgui.same_line()
    imgui.text(f"step {state.steps}  |  loss {state.losses[-1]:.3f}  |  {state.accuracy:.0%} of the points right  |  FPS:{hello_imgui.frame_rate():.1f}")


def hidden_units_widget() -> None:
    changed, state.hidden = imgui.slider_int("hidden units (starts again)", state.hidden, 1, 32)
    if changed:
        state.reset()


def learning_rate_widget() -> None:
    _, state.rate = imgui.slider_float("learning rate", state.rate, 0.01, 10.0, "%.2f",
                                       imgui.SliderFlags_.logarithmic)


WIDGETS = {"playground": playground_widget, "hidden_units": hidden_units_widget,
           "learning_rate": learning_rate_widget}


def widget_block(name: str) -> None:
    widget = WIDGETS.get(name.strip())
    if widget:
        widget()
    else:
        imgui.text_colored(imgui.ImVec4(1.0, 0.4, 0.4, 1.0), f"unknown widget: {name.strip()}")


r"""::md Files
## The network: tiny_nn.py
![[tiny_nn.py]]
## The story, the data and the widgets: neural_spiral.py
![[neural_spiral.py]]
"""


def gui() -> None:
    rich_md.register_fenced_block_renderer("widget", widget_block)  # the story's ```widget blocks
    rich_md.render_this_file("Story")
    if imgui.collapsing_header("Full code: the two files"):
        rich_md.render_this_file("Files")


immapp.run(gui, window_title="Neural spiral", window_size=(900, 1000),
           with_implot=True, with_markdown=True, with_latex=True)
