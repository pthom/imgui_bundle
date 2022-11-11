from imgui_bundle import imgui, ImVec2, run, hello_imgui


def gui():
    from imgui_bundle import imspinner, imgui_md

    imgui_md.render(
        f"""
### Current FPS:  {imgui.get_io().framerate:.1f}

In order to reduce the CPU usage, the FPS is reduced automatically when no user interaction is detected.

As a consequence, the animation may below not be fluid. However, if you move the mouse over this window,
the FPS will rise and the animation will be smooth again.
"""
    )

    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    radius1 = imgui.get_font_size()
    imspinner.spinner_ang_triple("spinner_arc_fade", radius1, radius1 * 1.5, radius1 * 2.0, 2.5, color, color, color)

    imgui_md.render(
        f"""You can adjust hello_imgui.get_runner_params().fps_idle if you need smoother animations 
    when the app is idle. A value of 0 means that the refresh will be as fast as possible"""
    )

    imgui.new_line()
    runner_params = hello_imgui.get_runner_params()
    _, runner_params.fps_idle = imgui.slider_float("runner_params.fpsIdle", runner_params.fps_idle, 0, 60)


def main():
    run(gui_function=gui, window_title="Power save", window_size=(400, 500), with_markdown=True, fps_idle=4)


if __name__ == "__main__":
    main()
