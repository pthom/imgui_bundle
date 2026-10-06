"""Grokking: a network learns by heart, then suddenly understands

A small network learns addition modulo 53 from half of the sums. It first memorizes them (the test half stays wrong),
then, much later, it [groks](https://arxiv.org/abs/2201.02177) the rule and the test half turns right. Scrub through
the training: the table of answers, the accuracies, and the geometry of the 53 numbers inside the network.
"""

import math
import time
from pathlib import Path

import numpy as np
from imgui_bundle import hello_imgui, imgui, immapp, implot, rich_md
from imgui_bundle import ImVec2, ImVec4

import narrator
from grok_train import P

DATA = np.load(Path(__file__).parent / "grokking_data.npz")  # recorded by grok_train.py
STEPS: np.ndarray = DATA["steps"]                                  # the training step of each checkpoint
LAST_STEP = int(STEPS[-1])
GROK_START = int(STEPS[np.argmax(DATA["test_acc"] > 0.1)])          # where the hidden sums start to be answered
CHECKPOINTS_PER_SECOND = 40                                        # the speed of the play button
ACCENT_BLINK_SECONDS = 1.5                                         # an accented curve blinks that long

INTRO = """
# Grokking
A network is shown **half** of the 53 x 53 table of sums modulo 53 (the blue cells), and is tested on the other half
(the red ones).
Scrub through its training, or press play. First it learns its half by heart: blue, but no green.
Then, long after, it finds the rule, and the hidden half turns green: it **grokked**. Inside, the 53 numbers have
arranged themselves on circles: clocks, one per frequency.
"""


class AppState:
    def __init__(self) -> None:
        self.checkpoint = 0           # the index of the checkpoint shown
        self.playing = False
        self.play_accumulator = 0.0
        self.clock = 0                # which of the recorded clocks is shown
        self.table_view = "answers"   # "answers": right or wrong at this step; "split": seen or hidden only
        self.view = "full"            # "full", "curves" (accuracy and clock), "accuracy" (that plot alone), "none"
        self.accent_line = "none"     # the accuracy curve drawn thick: "seen", "hidden" or "none"
        self.accent_since = 0.0       # when the accent last changed: the accented curve blinks for a moment
        self._last_accent = "none"
        self.zone = "none"            # a shaded span of the accuracy plot: "memorizing", "grokking" or "none"

    @property
    def step(self) -> int:
        return int(STEPS[self.checkpoint])

    @step.setter
    def step(self, step: int) -> None:
        self.checkpoint = int(np.clip(np.searchsorted(STEPS, step), 0, len(STEPS) - 1))

    def set_step(self, step: int) -> None:
        self.step = step

    def advance(self) -> None:
        lesson.touched("step")                       # the learner plays the training: the lesson lets the step be
        self.play_accumulator += imgui.get_io().delta_time * CHECKPOINTS_PER_SECOND
        while self.play_accumulator >= 1.0:
            self.play_accumulator -= 1.0
            if self.checkpoint < len(STEPS) - 1:
                self.checkpoint += 1
            else:
                self.playing = False


app_state = AppState()
lesson = narrator.Lesson(Path(__file__).parent / "scenario.md")   # the script, watched: edit it while this runs
lesson.param(name="step", owner=app_state, range=(0, LAST_STEP))
lesson.param(name="clock", owner=app_state, range=(0, 3))
lesson.param(name="table_view", owner=app_state)
lesson.param(name="view", owner=app_state)
lesson.param(name="accent_line", owner=app_state)
lesson.param(name="zone", owner=app_state)


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
    hidden = (~DATA["train_mask"]).astype(np.float32)
    if app_state.table_view == "split":
        return np.asarray(1.0 + hidden, dtype=np.float32)            # seen in blue, hidden in red
    right = DATA["correct"][checkpoint].astype(np.float32)
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
    lesson.widget("table_view")


def gui_accuracy(size: ImVec2) -> None:
    """The accuracies on the seen and the hidden sums, with a line at the current step (drag it to scrub)"""
    flags = implot.Flags_.no_menus | implot.Flags_.no_mouse_text
    if implot.begin_plot("Accuracy", size, flags):
        implot.setup_axes("training step", "accuracy")
        implot.setup_axes_limits(0, LAST_STEP, -0.02, 1.02, imgui.Cond_.always)
        implot.setup_legend(implot.Location_.east)
        if app_state.zone != "none":
            lo, hi = (0, GROK_START) if app_state.zone == "memorizing" else (GROK_START, LAST_STEP)
            implot.plot_shaded("##zone", np.array([lo, hi], np.float64), np.array([1.02, 1.02]), np.array([-0.02, -0.02]),
                               spec=implot.Spec(fill_color=ImVec4(1.0, 0.8, 0.3, 0.18)))
        if app_state.accent_line != app_state._last_accent:
            app_state._last_accent, app_state.accent_since = app_state.accent_line, time.time()
        blink = max(0.0, 1.0 - (time.time() - app_state.accent_since) / ACCENT_BLINK_SECONDS)   # 1 at the change, then 0
        for label, key, color in (("seen sums", "train_acc", ImVec4(0.25, 0.45, 0.85, 1.0)),
                                  ("hidden sums", "test_acc", ImVec4(0.25, 0.68, 0.38, 1.0))):
            accented = app_state.accent_line == key.split("_")[0].replace("train", "seen").replace("test", "hidden")
            dimmed = app_state.accent_line != "none" and not accented
            alpha = 0.35 if dimmed else 1.0
            if accented and blink > 0:
                alpha = 0.55 + 0.45 * abs(math.sin(time.time() * 9.0)) * blink + (1 - blink) * 0.45
            line_color = ImVec4(color.x, color.y, color.z, alpha)
            implot.plot_line(label, STEPS.astype(np.float64), DATA[key].astype(np.float64),
                             spec=implot.Spec(line_color=line_color, line_weight=3.5 if accented else 2.0))
        changed, x, *_ = implot.drag_line_x(0, float(app_state.step), ImVec4(1.0, 0.8, 0.3, 1.0), 2.0)
        if changed:
            app_state.set_step(int(x))
        implot.end_plot()
    lesson.widget("accent_line")


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
    if imgui.button("Pause" if app_state.playing else "Play the training", hello_imgui.em_to_vec2(9, 0)):
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
    hello_imgui.get_runner_params().fps_idling.enable_idling = not (app_state.playing or lesson.playing)
    if not lesson.started:                        # the explorable's own intro; the lesson has its teaser
        rich_md.render(INTRO)
    if app_state.view == "none":                  # an empty stage: the narration alone
        pass
    elif app_state.view == "accuracy":            # the first figure alone, as large as the stage
        gui_accuracy(ImVec2(-1, hello_imgui.em_size(28)))
    else:
        if app_state.view == "full":
            gui_controls()
            gui_table()
            imgui.same_line()
        imgui.begin_group()
        gui_accuracy(hello_imgui.em_to_vec2(28, 11.5))
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
    immapp.run(params, immapp.AddOnsParams(with_implot=True, with_markdown=True, with_latex=True))


if __name__ == "__main__":
    main()
