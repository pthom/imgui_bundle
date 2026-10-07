"""Grokking: a network learns by heart, then suddenly understands

A small network learns addition modulo 53 from half of the sums. It first memorizes them (the test half stays wrong),
then, much later, it [groks](https://arxiv.org/abs/2201.02177) the rule and the test half turns right. Scrub through
the training: the table of answers, the accuracies, and the geometry of the 53 numbers inside the network.
"""

import math
import time
from pathlib import Path

import numpy as np
from imgui_bundle import hello_imgui, imgui, immapp, implot, icons_fontawesome_4 as fa
from imgui_bundle import ImVec2, ImVec4

import narrator
import grok_train
from grok_train import P

CHECKPOINTS_PER_SECOND = 40                                        # the speed of the play button
LIVE_TRAINING_BUDGET_S = 0.035                                     # the time spent training per frame, live
ACCENT_BLINK_SECONDS = 4.0                                         # an accented curve blinks that long
ONE_FIGURE_BELOW_EM = 36.0                                         # a narrower stage (a phone) shows one figure
FIGURE_NAMES = {"table": "Table", "accuracy": "Accuracy", "clock": "Clock"}


class TrainingPath:
    """What the figures show at every checkpoint of a training: the recorded run, or a live one"""

    def __init__(self, train_mask: np.ndarray, clock_axes: np.ndarray, clock_frequencies: np.ndarray) -> None:
        self.train_mask = train_mask                  # (P, P): the sums shown during the training
        self.clock_axes = clock_axes                  # (CLOCKS, 2, D_EMBED): the planes of the clock views
        self.clock_frequencies = clock_frequencies
        self.steps = np.zeros(0, np.int64)
        self.train_acc = np.zeros(0, np.float32)
        self.test_acc = np.zeros(0, np.float32)
        self.correct = np.zeros((0, P, P), np.uint8)
        self.clocks = np.zeros((0, len(clock_frequencies), P, 2), np.float32)   # (steps, CLOCKS, P, 2)

    @staticmethod
    def recorded(file: Path) -> "TrainingPath":
        data = np.load(file)
        path = TrainingPath(data["train_mask"], data["clock_axes"], data["clock_frequencies"])
        path.steps, path.train_acc, path.test_acc = data["steps"], data["train_acc"], data["test_acc"]
        path.correct, path.clocks = data["correct"], data["clocks"]
        return path

    @property
    def last_step(self) -> int:
        return int(self.steps[-1]) if len(self.steps) else 0

    @property
    def grok_start(self) -> int:
        """The step where the hidden sums start to be answered (the end of the path if they never are)"""
        above = np.flatnonzero(self.test_acc > 0.1)
        return int(self.steps[above[0]]) if len(above) else self.last_step


class LiveTraining:
    """A network trained here, a few steps per frame, with the learner's hyperparameters"""

    def __init__(self, weight_decay: float, seed: int, clock_axes: np.ndarray, frequencies: np.ndarray) -> None:
        rng = np.random.default_rng(seed)
        self.pairs, train_mask = grok_train.make_data(rng)
        self.train = self.pairs[train_mask]
        self.trainer = grok_train.Trainer(grok_train.init_params(rng), weight_decay=weight_decay)
        self.path = TrainingPath(train_mask.reshape(P, P), clock_axes, frequencies)
        self.embeddings: list[np.ndarray] = []
        self.step = 0
        self.done = False
        self._checkpoint()

    def _checkpoint(self) -> None:
        right = grok_train.forward(self.trainer.params, self.pairs)[3].argmax(1) == self.pairs[:, 2]
        mask = self.path.train_mask.reshape(-1)
        e = self.trainer.params["E"] - self.trainer.params["E"].mean(0)
        self.embeddings.append(e)
        p = self.path
        p.steps = np.append(p.steps, self.step)
        p.train_acc = np.append(p.train_acc, np.float32(right[mask].mean()))
        p.test_acc = np.append(p.test_acc, np.float32(right[~mask].mean()))
        p.correct = np.concatenate([p.correct, right.reshape(1, P, P).astype(np.uint8)])
        clocks = np.array([[e @ a.T for a in p.clock_axes]], np.float32)
        p.clocks = np.concatenate([p.clocks, clocks])

    def run_some(self, budget_s: float) -> None:
        """Trains until the time budget of this frame is spent, or the run is over"""
        t0 = time.perf_counter()
        while not self.done and time.perf_counter() - t0 < budget_s:
            self.trainer.step(self.train)
            self.step += 1
            if self.step % grok_train.CHECKPOINT_EVERY == 0:
                self._checkpoint()
            if self.step >= grok_train.STEPS:
                self.done = True
                self._finish()

    def _finish(self) -> None:
        """The clock views of this run: the planes of its own strongest frequencies, at every checkpoint"""
        p = self.path
        final = self.embeddings[-1]
        p.clock_frequencies = grok_train.clock_frequencies(final, grok_train.CLOCKS)
        p.clock_axes = np.array([grok_train.clock_axes(final, int(k)) for k in p.clock_frequencies])
        p.clocks = np.array([[e @ a.T for a in p.clock_axes] for e in self.embeddings], np.float32)


RECORDED = TrainingPath.recorded(Path(__file__).parent / "grokking_data.npz")   # recorded by grok_train.py
LAST_STEP = RECORDED.last_step


class AppState:
    def __init__(self) -> None:
        self.path = RECORDED          # the training shown: the recorded one, or the live one
        self.live: LiveTraining | None = None
        self.training_live = False
        self.weight_decay = 1.0       # the hyperparameters of the next live training
        self.seed = 42
        self.checkpoint = 0           # the index of the checkpoint shown
        self.playing = False
        self.play_accumulator = 0.0
        self.clock = 0                # which of the recorded clocks is shown
        self.table_view = "answers"   # "answers": right or wrong at this step; "split": seen or hidden only
        self.view = "full"            # "full", "curves" (accuracy and clock), "accuracy" (that plot alone), "none"
        self.focus = "accuracy"       # the figure the narration talks about: a narrow stage shows it alone
        self.accent_line = "none"     # the accuracy curve drawn thick: "seen", "hidden" or "none"
        self.accent_since = 0.0       # when the accent last changed: the accented curve blinks for a moment
        self._last_accent = "none"
        self.zone = "none"            # a shaded span of the accuracy plot: "memorizing", "grokking" or "none"

    @property
    def step(self) -> int:
        return int(self.path.steps[self.checkpoint]) if len(self.path.steps) else 0

    @step.setter
    def step(self, step: int) -> None:
        self.checkpoint = int(np.clip(np.searchsorted(self.path.steps, step), 0, max(0, len(self.path.steps) - 1)))

    def set_step(self, step: int) -> None:
        self.step = step

    def toggle_training(self) -> None:
        self.playing = not self.playing
        if self.playing and self.checkpoint == len(self.path.steps) - 1:
            self.checkpoint = 0

    def advance(self) -> None:
        lesson.touched("step")                       # the learner plays the training: the lesson lets the step be
        self.play_accumulator += imgui.get_io().delta_time * CHECKPOINTS_PER_SECOND
        while self.play_accumulator >= 1.0:
            self.play_accumulator -= 1.0
            if self.checkpoint < len(self.path.steps) - 1:
                self.checkpoint += 1
            else:
                self.playing = False

    def start_training(self) -> None:
        """A live training with the current hyperparameters; the figures follow it"""
        self.playing = False                      # while it trains, a live run is seen on the recorded run's planes
        self.live = LiveTraining(self.weight_decay, int(self.seed), RECORDED.clock_axes, RECORDED.clock_frequencies)
        self.path, self.training_live, self.checkpoint = self.live.path, True, 0

    def use_recorded(self) -> None:
        """Back to the recorded training (the lesson's chapters are written on it)"""
        self.live, self.training_live = None, False
        self.path = RECORDED
        self.checkpoint = min(self.checkpoint, len(RECORDED.steps) - 1)

    def train_live(self) -> None:
        """Called every frame while a live training runs: the shown checkpoint follows it"""
        assert self.live is not None
        lesson.touched("step")
        self.live.run_some(LIVE_TRAINING_BUDGET_S)
        self.checkpoint = len(self.path.steps) - 1
        if self.live.done:
            self.training_live = False


app_state = AppState()
lesson = narrator.Lesson(Path(__file__).parent / "scenario.md", program=__file__)   # the script, watched: edit it live
lesson.param(name="step", owner=app_state, range=(0, LAST_STEP))
lesson.param(name="weight_decay", owner=app_state, range=(0.0, 1.0))
lesson.param(name="seed", owner=app_state, range=(0, 9999))
lesson.action(name="train", function=app_state.start_training)
lesson.action(name="use_recorded", function=app_state.use_recorded)
lesson.param(name="clock", owner=app_state, range=(0, 3))
lesson.param(name="table_view", owner=app_state)
lesson.param(name="view", owner=app_state)
lesson.param(name="focus", owner=app_state)
lesson.param(name="accent_line", owner=app_state)
lesson.param(name="zone", owner=app_state)


def button_height() -> float:
    """Taller on a phone, for a finger"""
    return narrator.TOUCH_BUTTON_EM * hello_imgui.em_size() if lesson.compact else imgui.get_frame_height()


def chip(label: str, selected: bool) -> bool:
    """A button that reads as selected or not (the figure shown, the clock's frequency)"""
    if selected:
        imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
    clicked = imgui.button(label, ImVec2(0, button_height()))
    if selected:
        imgui.pop_style_color()
    return clicked


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
    hidden = (~app_state.path.train_mask).astype(np.float32)
    if app_state.table_view == "split":
        return np.asarray(1.0 + hidden, dtype=np.float32)            # seen in blue, hidden in red
    right = app_state.path.correct[checkpoint].astype(np.float32)
    return np.asarray(2.0 * hidden + right, dtype=np.float32)


def gui_table(size: ImVec2) -> None:
    """The 53 x 53 table of sums, each cell colored by what the network answers at this step (a square, centered)"""
    side = max(1.0, min(size.x, size.y))
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (size.x - side) / 2)
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text | implot.Flags_.equal
    if implot.begin_plot("##table", ImVec2(side, side), flags):
        implot.setup_axes("b", "a", implot.AxisFlags_.no_grid_lines, implot.AxisFlags_.no_grid_lines)
        implot.setup_axes_limits(0, P, 0, P, imgui.Cond_.always)
        implot.push_colormap(table_colormap())
        implot.plot_heatmap("##cells", table_cells(app_state.checkpoint), 0.0, 3.0, "",
                            implot.Point(0, 0), implot.Point(P, P))
        implot.pop_colormap()
        implot.end_plot()
    lesson.widget("table_view")


def gui_accuracy(size: ImVec2) -> None:
    """The accuracies on the seen and the hidden sums, with a line at the current step (a tap or a drag scrubs)"""
    flags = implot.Flags_.no_menus | implot.Flags_.no_mouse_text
    if implot.begin_plot("Accuracy", ImVec2(max(1.0, size.x), max(1.0, size.y)), flags):
        implot.setup_axes("training step", "accuracy")
        implot.setup_axes_limits(0, LAST_STEP, -0.02, 1.02, imgui.Cond_.always)
        implot.setup_legend(implot.Location_.south_east, implot.LegendFlags_.no_buttons)
        path = app_state.path
        if app_state.zone != "none":
            lo, hi = (0, path.grok_start) if app_state.zone == "memorizing" else (path.grok_start, LAST_STEP)
            implot.plot_shaded("##zone", np.array([lo, hi], np.float64), np.array([1.02, 1.02]), np.array([-0.02, -0.02]),
                               spec=implot.Spec(fill_color=ImVec4(1.0, 0.8, 0.3, 0.18)))
        if app_state.accent_line != app_state._last_accent:
            app_state._last_accent, app_state.accent_since = app_state.accent_line, time.time()
        blink = max(0.0, 1.0 - (time.time() - app_state.accent_since) / ACCENT_BLINK_SECONDS)   # 1 at the change, then 0
        for label, key, color in (("Training set", "train_acc", ImVec4(0.25, 0.45, 0.85, 1.0)),
                                  ("Hidden set", "test_acc", ImVec4(0.25, 0.68, 0.38, 1.0))):
            accented = app_state.accent_line == key.split("_")[0].replace("train", "seen").replace("test", "hidden")
            dimmed = app_state.accent_line != "none" and not accented
            line_color = ImVec4(color.x, color.y, color.z, 0.25 if dimmed else 1.0)
            weight = 3.5 if accented else 2.0
            if accented and blink > 0:                 # the blink: the curve flashes white and thick, twice a second
                k = (0.5 + 0.5 * math.sin(time.time() * 2 * math.pi * 2.0)) * blink
                line_color = ImVec4(color.x + (1 - color.x) * k, color.y + (1 - color.y) * k,
                                    color.z + (1 - color.z) * k, 1.0)
                weight = 3.5 + 3.0 * k
            implot.plot_line(label, path.steps.astype(np.float64), getattr(path, key).astype(np.float64),
                             spec=implot.Spec(line_color=line_color, line_weight=weight))
        changed, x, *_ = implot.drag_line_x(0, float(app_state.step), ImVec4(1.0, 0.8, 0.3, 1.0), 2.0)
        if not changed and implot.is_plot_hovered() and imgui.is_mouse_down(imgui.MouseButton_.left):
            changed, x = True, implot.get_plot_mouse_pos().x       # a finger cannot grab a thin line: the plot scrubs
        if changed:
            app_state.set_step(int(x))
            lesson.touched("step")
        implot.end_plot()
    lesson.widget("accent_line")


def gui_clocks(size: ImVec2) -> None:
    """The 53 numbers inside the network: their embeddings on the plane of one frequency (a clock, once it groks)"""
    em = hello_imgui.em_size()
    path = app_state.path
    frequencies = path.clock_frequencies
    h = button_height()
    imgui.push_style_var(imgui.StyleVar_.frame_padding,                # the label centered on the chips' height
                         ImVec2(imgui.get_style().frame_padding.x, (h - imgui.get_font_size()) / 2))
    imgui.align_text_to_frame_padding()
    label = "The 53 numbers inside the network, on the clock of frequency"
    if imgui.calc_text_size(label).x + len(frequencies) * 3 * em > size.x:
        label = "Frequency"
    imgui.text(label)
    for i, k in enumerate(frequencies):
        imgui.same_line()
        if chip(f"{int(k)}##frequency", app_state.clock == i):
            app_state.clock = i
        lesson.widget("clock", changed=imgui.is_item_clicked())
    imgui.pop_style_var()
    height = size.y - h - imgui.get_style().item_spacing.y
    flags = implot.Flags_.no_legend | implot.Flags_.no_menus | implot.Flags_.no_mouse_text | implot.Flags_.equal
    if implot.begin_plot("##clock", ImVec2(max(1.0, size.x), max(1.0, height)), flags):
        implot.setup_axes("", "", implot.AxisFlags_.no_tick_labels, implot.AxisFlags_.no_tick_labels)
        extent = float(np.abs(RECORDED.clocks).max()) * 1.1
        implot.setup_axes_limits(-extent, extent, -extent, extent, imgui.Cond_.always)
        points = path.clocks[app_state.checkpoint, app_state.clock]
        small = min(size.x, height) < 30 * em                       # a small clock: smaller labels, larger dots
        implot.plot_scatter("##numbers", points[:, 0].astype(np.float64), points[:, 1].astype(np.float64),
                            spec=implot.Spec(marker=implot.Marker_.circle, marker_size=4 if small else 3,
                                             marker_fill_color=ImVec4(0.25, 0.45, 0.85, 1.0)))
        label_scale = max(0.6, min(1.0, min(size.x, height) / (30 * em)))
        imgui.push_font(None, imgui.get_style().font_size_base * label_scale)
        offset = ImVec2(9 * label_scale, -7 * label_scale)
        for n in range(P):
            implot.plot_text(str(n), float(points[n, 0]), float(points[n, 1]), offset)
        imgui.pop_font()
        implot.end_plot()


def gui_controls() -> None:
    """Play, pause, and the slider of the training step; on a phone, the accuracies go into the slider"""
    path = app_state.path
    seen, hidden = path.train_acc[app_state.checkpoint], path.test_acc[app_state.checkpoint]
    if lesson.compact:
        h = button_height()
        icon = fa.ICON_FA_PAUSE if app_state.playing else fa.ICON_FA_PLAY
        if imgui.button(icon + "###training", ImVec2(1.25 * h, h)):
            app_state.toggle_training()
        imgui.same_line()
        imgui.set_next_item_width(-1)
        imgui.push_style_var(imgui.StyleVar_.frame_padding,
                             ImVec2(imgui.get_style().frame_padding.x, (h - imgui.get_font_size()) / 2))
        changed, step = imgui.slider_int("##step", app_state.step, 0, LAST_STEP,
                                         f"step %d   seen {seen * 100:.0f}%%   hidden {hidden * 100:.0f}%%")
        imgui.pop_style_var()
    else:
        if imgui.button("Pause" if app_state.playing else "Play the training", hello_imgui.em_to_vec2(9, 0)):
            app_state.toggle_training()
        imgui.same_line()
        imgui.set_next_item_width(hello_imgui.em_size(30))
        changed, step = imgui.slider_int("Training step", app_state.step, 0, LAST_STEP)
    lesson.widget("step", changed=changed)
    if changed:
        app_state.set_step(step)
    if not lesson.compact:
        imgui.same_line()
        imgui.text(f"seen: {seen:4.0%}   hidden: {hidden:4.0%}")
    gui_hyperparameters()


def gui_hyperparameters() -> None:
    """The weight decay, the seed, and Train: a live training replaces the recorded one in the figures"""
    em = hello_imgui.em_size()
    h = button_height()
    imgui.set_next_item_width(12 * em)
    changed, app_state.weight_decay = imgui.slider_float("Weight decay", app_state.weight_decay, 0.0, 1.0, "%.2f")
    lesson.widget("weight_decay", changed=changed)
    imgui.same_line()
    imgui.set_next_item_width(6 * em)
    changed, app_state.seed = imgui.input_int("Seed", app_state.seed, 0)
    lesson.widget("seed", changed=changed)
    imgui.same_line()
    if app_state.training_live:
        imgui.button(f"Training... {app_state.path.last_step}", ImVec2(0, h))
    elif imgui.button("Train", ImVec2(0, h)):
        app_state.start_training()
        lesson.touched("step")
    if app_state.live is not None:
        imgui.same_line()
        if imgui.button("Recorded run", ImVec2(0, h)):
            app_state.use_recorded()


def gui_figure_chips(figures: list[str], shown: str) -> None:
    """On a narrow stage: which figure to look at (the narration chooses one, the learner may choose another)"""
    for i, figure in enumerate(figures):
        if i > 0:
            imgui.same_line()
        if chip(FIGURE_NAMES[figure], figure == shown):
            app_state.focus = figure
        lesson.widget("focus", changed=imgui.is_item_clicked())


def gui_figure(figure: str, size: ImVec2) -> None:
    if figure == "table":
        gui_table(size)
    elif figure == "accuracy":
        gui_accuracy(size)
    else:
        gui_clocks(size)


def gui_stage() -> None:
    """The figures, sized from the stage's region: side by side on a wide stage, one at a time on a narrow one"""
    if app_state.view == "none":                  # an empty stage: the narration alone
        return
    if app_state.view == "accuracy":              # the first figure alone, as large as the stage
        gui_accuracy(imgui.get_content_region_avail())
        return
    em = hello_imgui.em_size()
    spacing = imgui.get_style().item_spacing
    figures = ["table", "accuracy", "clock"] if app_state.view == "full" else ["accuracy", "clock"]
    if app_state.view == "full":
        gui_controls()
    avail = imgui.get_content_region_avail()
    if avail.x < ONE_FIGURE_BELOW_EM * em:
        shown = app_state.focus if app_state.focus in figures else figures[0]
        gui_figure_chips(figures, shown)
        gui_figure(shown, imgui.get_content_region_avail())
    elif app_state.view == "full":                # the table on the left; the accuracy and the clock on its right
        side = min(avail.y, max((avail.x - spacing.x) * 0.5, avail.x - spacing.x - 26 * em))
        gui_table(ImVec2(side, side))
        imgui.same_line()
        imgui.begin_group()
        width = avail.x - side - spacing.x
        gui_accuracy(ImVec2(width, side * 0.48))
        gui_clocks(ImVec2(width, side * 0.52 - spacing.y))
        imgui.end_group()
    else:                                         # the accuracy above the clock
        width = min(avail.x, 50 * em)
        gui_accuracy(ImVec2(width, avail.y * 0.45))
        gui_clocks(ImVec2(width, avail.y * 0.55 - spacing.y))


def gui() -> None:
    if app_state.training_live:
        app_state.train_live()
    elif app_state.playing:
        app_state.advance()
    hello_imgui.get_runner_params().fps_idling.enable_idling = \
        not (app_state.playing or app_state.training_live or lesson.playing)
    lesson.gui(stage=gui_stage)


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Grokking"
    params.app_window_params.window_geometry.size = (1000, 1000)
    params.ini_disable = True
    params.callbacks.show_gui = gui
    immapp.run(params, immapp.AddOnsParams(with_implot=True, with_markdown=True, with_latex=True))


if __name__ == "__main__":
    main()
