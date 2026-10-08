"""
Power save: the app slows down when you don't use it.

When nothing happens, [Hello ImGui](https://pthom.github.io/hello_imgui/) lowers the frame rate to spare the CPU:
after 3 seconds, the live plot and the spinner become choppy. Content that changes on its own says so with
`hello_imgui.set_item_is_live()`, and keeps the full speed while it is visible. The idling settings are global.
"""

import itertools
import math

import numpy as np
from imgui_bundle import ImVec2, ImVec4, hello_imgui, imgui, imgui_toggle, immapp, implot, imspinner, rich_md

SIGNAL_SECONDS = 4.0  # the plot shows the last seconds of the signal
SIGNAL_FREQUENCY = 0.6  # Hz, of the signal's main wave
IDLING_COLOR = ImVec4(0.85, 0.45, 0.1, 1.0)  # the status's pill while the app idles
FULL_SPEED_COLOR = ImVec4(0.2, 0.55, 0.3, 1.0)  # and at full speed

# A signal of varying data, sampled once per frame: the gaps between the samples are the frame durations
times: list[float] = []
values: list[float] = []
live = False  # the plot and the spinner say that they are live (hello_imgui.set_item_is_live)


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


def switch(label: str, v: bool) -> bool:
    """An animated on/off switch (imgui_toggle), in the colors of the theme"""
    config = imgui_toggle.default_style()
    config.flags |= imgui_toggle.ToggleFlags_.animated.value
    config.size = hello_imgui.em_to_vec2(2.2, 1.2)
    _, v = imgui_toggle.toggle(label, v, config)
    return v


def pill(label: str, color: ImVec4) -> None:
    """A word on a colored pill"""
    padding = imgui.get_font_size() * 0.5
    text_size = imgui.calc_text_size(label)
    size = ImVec2(text_size.x + padding * 2, text_size.y)
    pos = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()
    draw_list.add_rect_filled(pos, ImVec2(pos.x + size.x, pos.y + size.y), imgui.get_color_u32(color), size.y * 0.5)
    draw_list.add_text(ImVec2(pos.x + padding, pos.y), imgui.get_color_u32(ImVec4(1, 1, 1, 1)), label)
    imgui.dummy(size)


def show_status() -> None:
    """The frames of the last second, whether the app idles, and the shortest and longest gaps between frames"""
    now = times[-1]
    gaps = [(t1 - t0) * 1000.0 for t0, t1 in itertools.pairwise(times) if t1 >= now - 1.0] or [0.0]
    idling = hello_imgui.get_runner_params().fps_idling.is_idling
    imgui.text(f"{len(gaps)} FPS")
    imgui.same_line()
    pill("idling" if idling else "full speed", IDLING_COLOR if idling else FULL_SPEED_COLOR)
    imgui.same_line()
    imgui.text_disabled(f"frames {min(gaps):.0f} to {max(gaps):.0f} ms apart")


def show_live_content() -> None:
    """The plot, and the spinner at its right"""
    spinner_radius = imgui.get_font_size() * 2.0
    plot_width = imgui.get_content_region_avail().x - spinner_radius * 2.0 - hello_imgui.em_size(1.5)
    ages = np.array(times) - times[-1]  # the x axis: seconds before now
    if implot.begin_plot("A live signal", ImVec2(plot_width, hello_imgui.em_size(10))):
        implot.setup_axes_limits(-SIGNAL_SECONDS, 0.0, -1.5, 1.5, implot.Cond_.always)
        implot.plot_line("signal", ages, np.array(values))
        implot.end_plot()
    hello_imgui.set_item_is_live(live)  # the plot changes on its own: the app does not idle while it is visible

    imgui.same_line()
    imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + hello_imgui.em_size(3))
    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    imspinner.spinner_ang_triple(
        "spinner", spinner_radius * 0.5, spinner_radius * 0.75, spinner_radius, 2.5, color, color, color
    )
    hello_imgui.set_item_is_live(live)


def gui() -> None:
    global live
    sample_signal()
    show_status()
    imgui.spacing()
    rich_md.render("""
        Hello ImGui tries hard to save the CPU (and the battery) by lowering the frame rate when it is not needed.
        After 3 seconds without user interaction, animations may become choppy: watch the plot and the spinner,
        without moving the mouse or touching the screen.
    """)
    live = switch("The plot and the spinner are live", live)
    imgui.spacing()
    show_live_content()

    imgui.dummy(hello_imgui.em_to_vec2(0, 0.5))
    if imgui.collapsing_header("Keep the full speed while content changes", imgui.TreeNodeFlags_.default_open):
        rich_md.render("""
            Call `SetItemIsLive()` right after a widget that changes on its own (an animation, a live image, a plot
            of varying data): the app keeps its full speed while the widget is visible.

            ```cpp
            ImPlot::EndPlot();
            HelloImGui::SetItemIsLive();
            ```

            ```python
            implot.end_plot()
            hello_imgui.set_item_is_live()
            ```

            Data that arrives in another thread (a camera, a socket): call `HelloImGui::RequestRefresh()` in C++,
            `hello_imgui.request_refresh()` in Python, when it arrives.
        """)

    imgui.dummy(hello_imgui.em_to_vec2(0, 0.5))
    if imgui.collapsing_header("Idling settings"):
        fps_idling = hello_imgui.get_runner_params().fps_idling
        rich_md.render("""
            These settings are global: they act on the whole application. To keep some content moving, prefer
            `SetItemIsLive()` on its widget: the app idles again as soon as the widget leaves the view, or stops
            changing.

            They are in the runner params; while the app runs, `HelloImGui::GetRunnerParams()` gives them
            (`hello_imgui.get_runner_params()` in Python).

            ```cpp
            // Idle frame rate (0: full speed)
            runnerParams.fpsIdling.fpsIdle = 3.f;
            // No idling at all
            runnerParams.fpsIdling.enableIdling = false;
            ```

            ```python
            # Idle frame rate (0: full speed)
            runner_params.fps_idling.fps_idle = 3
            # No idling at all
            runner_params.fps_idling.enable_idling = False
            ```
        """)
        imgui.set_next_item_width(-imgui.FLT_MIN)  # the whole width: a slider is easier to drag with a finger
        _, fps_idling.fps_idle = imgui.slider_float("##fps_idle", fps_idling.fps_idle, 0.0, 60.0, "fps_idle: %.0f")
        fps_idling.enable_idling = switch("Enable idling", fps_idling.enable_idling)


def main() -> None:
    immapp.run(gui, window_title="Power save", window_size=(520, 720), fps_idle=3, with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
