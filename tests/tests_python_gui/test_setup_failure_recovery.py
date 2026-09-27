"""A new app must start after an app whose setup failed.

When a user callback fails during the setup (here: a font that is not in the assets), the setup must not leave the
ImGui context and the backends behind. Otherwise, in a Python REPL, a notebook or the Pyodide playground, every
following app fails with "Already initialized a platform backend!".
"""
import pytest


def _load_missing_font() -> None:
    from imgui_bundle import hello_imgui
    hello_imgui.load_font("fonts/this_font_does_not_exist.ttf", 16.0)


@pytest.mark.parametrize("use_manual_render", [False, True])
def test_new_app_after_failed_setup(use_manual_render: bool) -> None:
    from imgui_bundle import hello_imgui, imgui

    failing_params = hello_imgui.RunnerParams()
    failing_params.callbacks.load_additional_fonts = _load_missing_font
    failing_params.callbacks.show_gui = lambda: None
    with pytest.raises(Exception):
        if use_manual_render:
            hello_imgui.manual_render.setup_from_runner_params(failing_params)
        else:
            hello_imgui.run(failing_params)

    nb_frames = [0]

    def gui() -> None:
        imgui.text("A new app, after a failed setup")
        nb_frames[0] += 1
        if nb_frames[0] >= 3:
            hello_imgui.get_runner_params().app_shall_exit = True

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    if use_manual_render:
        hello_imgui.manual_render.setup_from_runner_params(params)
        while not params.app_shall_exit:
            hello_imgui.manual_render.render()
        hello_imgui.manual_render.tear_down()
    else:
        hello_imgui.run(params)
    assert nb_frames[0] >= 3
