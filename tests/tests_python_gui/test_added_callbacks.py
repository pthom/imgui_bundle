"""Test the added callbacks (add_callback, call_soon, call_later): they run in their order around the app's function,
a plain assignment of the slot keeps them, and immapp.run leaves the params' callbacks as they were."""

from imgui_bundle import hello_imgui, imgui, immapp


def test_added_callbacks() -> None:
    log: list[str] = []
    frames: dict[str, int] = {}

    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Test added callbacks"
    params.app_window_params.window_geometry.size = (300, 200)
    cb = params.callbacks
    Slot = hello_imgui.CallbackSlot

    cb.add_callback(Slot.post_init, lambda: log.append("addon_init"), owner="test")
    cb.add_callback(Slot.before_exit, lambda: log.append("addon_exit"), owner="test")
    cb.post_init = lambda: log.append("app_init")  # assigned after the add-on: it keeps the add-on's
    cb.before_exit = lambda: log.append("app_exit")

    def gui() -> None:
        n = imgui.get_frame_count()
        if n == 2:
            frames["asked"] = n

            def note_soon() -> None:
                frames["soon"] = imgui.get_frame_count()

            def note_later() -> None:
                frames["later"] = imgui.get_frame_count()

            hello_imgui.get_runner_params().callbacks.call_soon(note_soon)
            hello_imgui.get_runner_params().callbacks.call_later(note_later, 0.2)
        if "later" in frames:
            hello_imgui.get_runner_params().app_shall_exit = True
        if n > 600:  # a safety net: the test fails below
            hello_imgui.get_runner_params().app_shall_exit = True

    cb.show_gui = gui
    params.fps_idling.enable_idling = True  # call_later must wake the idling app
    immapp.run(params)

    assert log == ["addon_init", "app_init", "app_exit", "addon_exit"], log
    assert frames["soon"] == frames["asked"] + 1, frames  # the next frame
    assert "later" in frames, frames
    # Synonyms (compared as ints: the stub declares them as members of their own)
    assert int(Slot.before_gui) == int(Slot.post_new_frame) and int(Slot.after_gui) == int(Slot.before_imgui_render)

    # The same params run again: the added callbacks are still there, once (immapp chains nothing into them)
    log.clear()
    frames.clear()
    cb.show_gui = lambda: setattr(hello_imgui.get_runner_params(), "app_shall_exit", True)
    immapp.run(params)
    assert log == ["addon_init", "app_init", "app_exit", "addon_exit"], log

    cb.remove_callbacks("test")
    log.clear()
    immapp.run(params)
    assert log == ["app_init", "app_exit"], log
    print("OK test_added_callbacks")


if __name__ == "__main__":
    test_added_callbacks()
