from imgui_bundle import imgui, hello_imgui, immapp


def gui():
    from imgui_bundle import imspinner

    imgui.text_wrapped(
        f"""
Current FPS:  {hello_imgui.frame_rate():.1f}

In order to reduce the CPU usage, the FPS is reduced automatically when no user interaction is detected.

As a consequence, the animation may below not be fluid. However, if you move the mouse over this window,
the FPS will rise and the animation will be smooth again.
"""
    )

    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    radius1 = imgui.get_font_size()
    imspinner.spinner_ang_triple(
        "spinner_arc_fade",
        radius1,
        radius1 * 1.5,
        radius1 * 2.0,
        2.5,
        color,
        color,
        color,
    )

    imgui.text_wrapped(
        """You can adjust hello_imgui.get_runner_params().fps_idle if you need smoother animations
    when the app is idle. A value of 0 means that the refresh will be as fast as possible"""
    )

    imgui.new_line()
    runner_params = hello_imgui.get_runner_params()
    _, runner_params.fps_idling.fps_idle = imgui.slider_float(
        "runner_params.fpsIdle", runner_params.fps_idling.fps_idle, 0, 60
    )

    imgui.text(
        "You can also set HelloImGui::GetRunnerParams()->fpdIdling.enableIdling."
    )
    _, runner_params.fps_idling.enable_idling = imgui.checkbox(
        "Enable Idling", runner_params.fps_idling.enable_idling
    )


def main():
    immapp.run(
        gui_function=gui, window_title="Power save", window_size=(400, 500), fps_idle=3
    )


if __name__ == "__main__":
    main()
