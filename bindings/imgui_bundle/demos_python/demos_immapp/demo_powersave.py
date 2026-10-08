"""
Power save: the app slows down when you don't use it.

When nothing happens, [Hello ImGui](https://pthom.github.io/hello_imgui/) lowers the frame rate to spare the CPU:
the live plot and the spinner then move by jumps. Move the mouse or touch the screen, and they are smooth again. The
slider sets `fps_idle` (0 means full speed), and the checkbox turns idling off, for example during an animation.
"""

import itertools
import math

import numpy as np
from imgui_bundle import ImVec2, hello_imgui, imgui, immapp, implot, imspinner

SIGNAL_SECONDS = 4.0  # the plot shows the last seconds of the signal
SIGNAL_FREQUENCY = 0.6  # Hz, of the signal's main wave

# A signal of varying data, sampled once per frame: the gaps between the samples are the frame durations
times: list[float] = []
values: list[float] = []


def sample_signal() -> None:
    now = immapp.clock_seconds()
    phase = 2.0 * math.pi * SIGNAL_FREQUENCY * now
    times.append(now)
    values.append(math.sin(phase) + 0.3 * math.sin(3.7 * phase))  # a main wave, and a faster one
    nb_old = 0  # the samples out of the plot, but one (the line enters from its left edge)
    while nb_old + 1 < len(times) and times[nb_old + 1] < now - SIGNAL_SECONDS:
        nb_old += 1
    del times[:nb_old]
    del values[:nb_old]


def show_pace() -> None:
    """The pace of the last second: the number of frames, and their shortest and longest gaps (ms)"""
    now = times[-1]
    gaps = [(t1 - t0) * 1000.0 for t0, t1 in itertools.pairwise(times) if t1 >= now - 1.0]
    if gaps:
        imgui.text(f"Last second: {len(gaps)} frames, {min(gaps):.0f} to {max(gaps):.0f} ms apart")


def show_signal() -> None:
    ages = np.array(times) - times[-1]  # the x axis: seconds before now
    if implot.begin_plot("A live signal", ImVec2(-1, hello_imgui.em_size(12))):
        implot.setup_axes_limits(-SIGNAL_SECONDS, 0.0, -1.5, 1.5, implot.Cond_.always)
        implot.plot_line("signal", ages, np.array(values))
        implot.end_plot()


def gui() -> None:
    sample_signal()
    fps_idling = hello_imgui.get_runner_params().fps_idling

    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}{'  (idling)' if fps_idling.is_idling else ''}")
    show_pace()
    imgui.text_wrapped(
        "In order to reduce the CPU usage, the FPS is reduced automatically when no user interaction is detected. "
        "As a consequence, the plot and the spinner below may move by jumps. Move the mouse or touch the screen, "
        "and they are smooth again."
    )

    show_signal()
    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    radius1 = imgui.get_font_size()
    imspinner.spinner_ang_triple("spinner_arc_fade", radius1, radius1 * 1.5, radius1 * 2.0, 2.5, color, color, color)

    imgui.text_wrapped(
        "You can adjust hello_imgui.get_runner_params().fps_idling.fps_idle if you need smoother animations "
        "when the app is idle. A value of 0 means that the refresh will be as fast as possible."
    )
    imgui.text("fps_idling.fps_idle")  # the label above the slider: the slider gets the whole width
    imgui.set_next_item_width(-1)
    _, fps_idling.fps_idle = imgui.slider_float("##fps_idle", fps_idling.fps_idle, 0.0, 60.0, "%.0f")

    imgui.text_wrapped("You can also set hello_imgui.get_runner_params().fps_idling.enable_idling.")
    _, fps_idling.enable_idling = imgui.checkbox("Enable Idling", fps_idling.enable_idling)


def main() -> None:
    immapp.run(gui, window_title="Power save", window_size=(500, 600), fps_idle=3, with_implot=True)


if __name__ == "__main__":
    main()
