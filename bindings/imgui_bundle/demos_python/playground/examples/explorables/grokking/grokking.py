"""Grokking: a network learns by heart, then suddenly understands

A small network learns addition modulo 53 from half of the sums. It first memorizes them (the test half stays wrong),
then, much later, it [groks](https://arxiv.org/abs/2201.02177) the rule and the test half turns right. Scrub through
the training: the table of answers, the accuracies, and the geometry of the 53 numbers inside the network.
"""

from pathlib import Path

import numpy as np
from imgui_bundle import hello_imgui, imgui, immapp, implot, rich_md
from imgui_bundle import ImVec2, ImVec4

import narrator
from grok_train import P

DATA = np.load(Path(__file__).parent / "grokking_data.npz")  # recorded by grok_train.py
STEPS: np.ndarray = DATA["steps"]                                  # the training step of each checkpoint
LAST_STEP = int(STEPS[-1])
CHECKPOINTS_PER_SECOND = 40                                        # the speed of the play button

r"""::md Lesson
---
title: Grokking
voice: en-US-AndrewMultilingualNeural
defaults:
  over: 1
  delay_after_interaction: 8
---
# Grokking

## The end

```cues
set_value("step", 1000)
set_value("clock", 0)
```
This network learned to add. Nobody told it how.

```cues
highlight("step", at="hidden half")
animate("step", 0, over=4, at="Let's go back")
```
For a long time, it only knew the sums by heart. Then, in a few hundred steps, it found the rule, and the hidden
half of the table turned green. Let's go back to the beginning, and watch it happen.

## Learning by heart

```cues
animate("step", 100, over=8, at="Watch the table")
```
The network is shown half of the sums: the blue cells. The other half, in red, stays hidden: that is the test.
Watch the table while it trains. Within a hundred steps, every blue cell is right.

```cues
highlight("step", at="still red")
pause("Drag the step slider between 100 and 250: nothing changes on the hidden half. Then press Continue.")
```
But the hidden half is still red. The network has learned its half by heart, and has no idea about the rest.

### More: overfitting
A model that fits its training data, but not new data, is said to overfit. Usually, training stops here.

### Code
The training step: the loss, its gradient, and AdamW, which also shrinks every weight a little at each step.
![[grok_train.py#Step#code]]

## Grokking

```cues
animate("step", 700, over=12, at="Nothing changes")
```
Nothing changes in the training: the same steps continue, on the same half. And then, slowly at first, the red
cells turn green. By step seven hundred, the network answers every sum it has never seen.

```cues
highlight("clock", at="Look inside")
animate("step", 1000, over=4, at="a circle")
```
Look inside. The 53 numbers, as the network represents them, now sit on a circle: a clock. The network adds by
turning hands. There are several such clocks, one per frequency: pick another one below the plot.

### More: the clock explanation
On the plane of frequency $k$, the number $n$ sits at the angle $2 \pi k n / 53$. Adding $a$ and $b$ is adding
angles: $\cos(a + b) = \cos a \cos b - \sin a \sin b$. The network found this trick by itself, pushed by the weight
decay: a memorized table costs large weights, a clock costs small ones (Nanda et al., 2023).
"""

INTRO = """# Grokking
A network is shown **half** of the 53 x 53 table of sums modulo 53 (the blue cells), and is tested on the other half
(the red ones). Scrub through its training, or press play. First it learns its half by heart: blue, but no green.
Then, long after, it finds the rule, and the hidden half turns green: it **grokked**. Inside, the 53 numbers have
arranged themselves on circles: clocks, one per frequency.
"""


class AppState:
    def __init__(self) -> None:
        self.checkpoint = 0           # the index of the checkpoint shown
        self.playing = False
        self.play_accumulator = 0.0
        self.clock = 0                # which of the recorded clocks is shown

    @property
    def step(self) -> int:
        return int(STEPS[self.checkpoint])

    @step.setter
    def step(self, step: int) -> None:
        self.checkpoint = int(np.clip(np.searchsorted(STEPS, step), 0, len(STEPS) - 1))

    def set_step(self, step: int) -> None:
        self.step = step

    def advance(self) -> None:
        self.play_accumulator += imgui.get_io().delta_time * CHECKPOINTS_PER_SECOND
        while self.play_accumulator >= 1.0:
            self.play_accumulator -= 1.0
            if self.checkpoint < len(STEPS) - 1:
                self.checkpoint += 1
            else:
                self.playing = False


app_state = AppState()
lesson = narrator.Lesson(__file__, section="Lesson")
lesson.param(name="step", owner=app_state, range=(0, LAST_STEP))
lesson.param(name="clock", owner=app_state, range=(0, 3))


def table_colormap() -> int:
    """Four cells: a seen sum wrong (grey), seen and right (blue), hidden and wrong (red), hidden and right (green)"""
    cmap = implot.get_colormap_index("grokking_table")
    if cmap == -1:
        colors = np.array([[0.72, 0.72, 0.78, 1.0], [0.25, 0.45, 0.85, 1.0],
                           [0.85, 0.32, 0.32, 1.0], [0.25, 0.68, 0.38, 1.0]], np.float32)
        cmap = implot.add_colormap("grokking_table", colors, qual=True)
    return cmap


def table_cells(checkpoint: int) -> np.ndarray:
    """0: seen and wrong, 1: seen and right, 2: hidden and wrong, 3: hidden and right"""
    right = DATA["correct"][checkpoint].astype(np.float32)
    hidden = (~DATA["train_mask"]).astype(np.float32)
    return np.asarray(2.0 * hidden + right, dtype=np.float32)


def gui_table() -> None:
    """The 53 x 53 table of sums, each cell colored by what the network answers at this step"""
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text | implot.Flags_.equal
    if implot.begin_plot("##table", hello_imgui.em_to_vec2(24, 24), flags):
        implot.setup_axes("b", "a", implot.AxisFlags_.no_grid_lines, implot.AxisFlags_.no_grid_lines)
        implot.setup_axes_limits(0, P, 0, P, imgui.Cond_.always)
        implot.push_colormap(table_colormap())
        implot.plot_heatmap("##cells", table_cells(app_state.checkpoint), 0.0, 3.0, "",
                            implot.Point(0, 0), implot.Point(P, P))
        implot.pop_colormap()
        implot.end_plot()


def gui_accuracy() -> None:
    """The accuracies on the seen and the hidden sums, with a line at the current step (drag it to scrub)"""
    flags = implot.Flags_.no_menus | implot.Flags_.no_mouse_text
    if implot.begin_plot("Accuracy", hello_imgui.em_to_vec2(28, 11.5), flags):
        implot.setup_axes("training step", "accuracy")
        implot.setup_axes_limits(0, LAST_STEP, -0.02, 1.02, imgui.Cond_.always)
        implot.setup_legend(implot.Location_.east)
        implot.plot_line("seen sums", STEPS.astype(np.float64), DATA["train_acc"].astype(np.float64),
                         spec=implot.Spec(line_color=ImVec4(0.25, 0.45, 0.85, 1.0), line_weight=2.0))
        implot.plot_line("hidden sums", STEPS.astype(np.float64), DATA["test_acc"].astype(np.float64),
                         spec=implot.Spec(line_color=ImVec4(0.25, 0.68, 0.38, 1.0), line_weight=2.0))
        changed, x, *_ = implot.drag_line_x(0, float(app_state.step), ImVec4(1.0, 0.8, 0.3, 1.0), 2.0)
        if changed:
            app_state.set_step(int(x))
        implot.end_plot()


def gui_clocks() -> None:
    """The 53 numbers inside the network: their embeddings on the plane of one frequency (a clock, once it groks)"""
    frequencies = DATA["clock_frequencies"]
    imgui.text("The 53 numbers inside the network, on the clock of frequency")
    for i, k in enumerate(frequencies):
        imgui.same_line()
        if imgui.radio_button(str(int(k)), app_state.clock == i):
            app_state.clock = i
        lesson.widget("clock", changed=imgui.is_item_clicked())
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text | implot.Flags_.equal
    if implot.begin_plot("##clock", hello_imgui.em_to_vec2(28, 11), flags):
        implot.setup_axes("", "", implot.AxisFlags_.no_tick_labels, implot.AxisFlags_.no_tick_labels)
        extent = float(np.abs(DATA["clocks"]).max()) * 1.1
        implot.setup_axes_limits(-extent, extent, -extent, extent, imgui.Cond_.always)
        points = DATA["clocks"][app_state.checkpoint, app_state.clock]
        implot.plot_scatter("##numbers", points[:, 0].astype(np.float64), points[:, 1].astype(np.float64),
                            spec=implot.Spec(marker=implot.Marker_.circle, marker_size=3,
                                             marker_fill_color=ImVec4(0.25, 0.45, 0.85, 1.0)))
        for n in range(P):
            implot.plot_text(str(n), float(points[n, 0]), float(points[n, 1]), ImVec2(9, -7))
        implot.end_plot()


def gui_controls() -> None:
    """Play, pause, and the slider of the training step"""
    if imgui.button("Pause" if app_state.playing else "Play", hello_imgui.em_to_vec2(5, 0)):
        app_state.playing = not app_state.playing
        if app_state.playing and app_state.checkpoint == len(STEPS) - 1:
            app_state.checkpoint = 0
    imgui.same_line()
    imgui.set_next_item_width(hello_imgui.em_size(30))
    changed, step = imgui.slider_int("Training step", app_state.step, 0, LAST_STEP)
    lesson.widget("step", changed=changed)
    if changed:
        app_state.set_step(step)
    imgui.same_line()
    imgui.text(f"seen: {DATA['train_acc'][app_state.checkpoint]:4.0%}   "
               f"hidden: {DATA['test_acc'][app_state.checkpoint]:4.0%}")


def gui() -> None:
    if app_state.playing:
        app_state.advance()
    hello_imgui.get_runner_params().fps_idling.enable_idling = not app_state.playing
    rich_md.render(INTRO)
    gui_controls()
    gui_table()
    imgui.same_line()
    imgui.begin_group()
    gui_accuracy()
    gui_clocks()
    imgui.end_group()
    lesson.gui()


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Grokking"
    params.app_window_params.window_geometry.size = (1000, 1000)
    params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.white_is_white
    params.ini_disable = True
    params.callbacks.show_gui = gui
    immapp.run(params, immapp.AddOnsParams(with_implot=True, with_markdown=True))


if __name__ == "__main__":
    main()
