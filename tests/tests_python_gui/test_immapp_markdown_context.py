"""ImmApp's markdown context: its own, current during run and destroyed at exit. The context that the application had
made current before run is current again afterwards, and still alive."""

from imgui_bundle import hello_imgui, imgui, immapp, rich_md


def test_immapp_markdown_context() -> None:
    mine = rich_md.create_context()
    seen: dict[str, object] = {}

    def gui() -> None:
        rich_md.render("Some *markdown* in ImmApp")
        if imgui.get_frame_count() == 3:
            seen["during_run"] = rich_md.get_current_context()
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Test ImmApp markdown context"
    runner_params.callbacks.show_gui = gui
    runner_params.ini_disable = True
    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    immapp.run(runner_params, addons)

    assert seen["during_run"] is not None
    assert seen["during_run"] is not mine  # ImmApp's own context
    assert rich_md.get_current_context() is mine  # the application's context, current again
    rich_md.destroy_context(mine)
    assert rich_md.get_current_context() is None
    print("OK test_immapp_markdown_context")
