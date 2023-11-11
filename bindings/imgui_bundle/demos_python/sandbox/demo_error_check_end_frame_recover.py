# This demo show how we can call ImGui::ErrorCheckEndFrameRecover()
# to recover from errors originating when ImGui::End() is not called (for example when an exception is raised)

from imgui_bundle import hello_imgui, imgui


def sub_window_gui() -> None:
    imgui.set_next_window_size((600, 200))
    imgui.begin("Sub window")
    imgui.text_wrapped(
        "The button below will raise an exception which lead to imgui.end() not being called"
    )

    if imgui.button(
        "Raise exception"
    ):  # This button raises an exception that bypasses `ìmgui.end()`
        raise RuntimeError("Argh")
    imgui.end()


def gui() -> None:
    try:
        imgui.text("Hello")
        sub_window_gui()
    except RuntimeError as e:
        print(f"Ouch, caught an exception: {e}")


# ImGui Bundle provides a fork of ImGui
# where imgui.internal.error_check_end_frame_recover() can use a simple callback, such a below:
def my_end_frame_error_callback(message: str) -> None:
    print("my_end_frame_error_callback ==> " + message)


def main() -> None:

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui

    runner_params.callbacks.before_imgui_render = (
        lambda: imgui.internal.error_check_end_frame_recover(
            my_end_frame_error_callback
        )
    )

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
