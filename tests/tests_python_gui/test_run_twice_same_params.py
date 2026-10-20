"""Test that the same RunnerParams can run twice: with hello_imgui.run, immapp.run and immapp.manual_render.
A run leaves the params as it found them: appShallExit, LoadAdditionalFonts, the DPI factor, and the user's callbacks.
"""

import gc
import weakref

from imgui_bundle import hello_imgui, immapp, imgui

NB_RUNS = 2


def _user_setup_style() -> None:
    imgui.style_colors_dark()


def _runner_params(nb_runs_seen: list[int]) -> hello_imgui.RunnerParams:
    def gui() -> None:
        if imgui.get_frame_count() == 3:
            nb_runs_seen[0] += 1
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui
    runner_params.callbacks.setup_imgui_style = _user_setup_style  # a Python function: it comes back as itself
    runner_params.app_window_params.window_geometry.size = (300, 200)
    runner_params.ini_disable = True
    return runner_params


def test_hello_imgui_run_twice() -> None:
    nb_runs_seen = [0]
    runner_params = _runner_params(nb_runs_seen)
    for _ in range(NB_RUNS):
        hello_imgui.run(runner_params)
    assert nb_runs_seen[0] == NB_RUNS


def test_dpi_factor_after_run() -> None:
    """A factor that the run measured is measured again at the next run (on another screen, it may differ);
    a factor set by the app stays"""
    runner_params = _runner_params([0])
    factor_during_run = [0.0]

    def post_init() -> None:
        factor_during_run[0] = hello_imgui.get_runner_params().dpi_aware_params.dpi_window_size_factor

    runner_params.callbacks.post_init = post_init
    for factor_set_by_app in (0.0, 1.5):  # 0: measured
        runner_params.dpi_aware_params.dpi_window_size_factor = factor_set_by_app
        hello_imgui.run(runner_params)
        assert factor_during_run[0] > 0.0
        assert runner_params.dpi_aware_params.dpi_window_size_factor == factor_set_by_app


def test_immapp_run_twice() -> None:
    nb_runs_seen = [0]
    runner_params = _runner_params(nb_runs_seen)
    add_ons = immapp.AddOnsParams(with_implot=True, with_markdown=True, with_node_editor=True)
    for _ in range(NB_RUNS):
        immapp.run(runner_params, add_ons)
        # ImmApp chains its own callbacks into the params during the run: the user's come back
        assert runner_params.callbacks.setup_imgui_style is _user_setup_style
    assert nb_runs_seen[0] == NB_RUNS


def test_immapp_manual_render_keeps_no_callback() -> None:
    """After tear_down, ImmApp keeps no copy of the app's callbacks: freed after Python's exit, they could crash it"""
    runner_params = _runner_params([0])
    gui = weakref.ref(runner_params.callbacks.show_gui)
    immapp.manual_render.setup_from_runner_params(runner_params, immapp.AddOnsParams())
    while not runner_params.app_shall_exit:
        immapp.manual_render.render()
    immapp.manual_render.tear_down()
    del runner_params
    gc.collect()
    assert gui() is None


def test_immapp_manual_render_twice() -> None:
    nb_runs_seen = [0]
    runner_params = _runner_params(nb_runs_seen)
    for _ in range(NB_RUNS):
        immapp.manual_render.setup_from_runner_params(runner_params, immapp.AddOnsParams(with_implot=True))
        while not runner_params.app_shall_exit:
            immapp.manual_render.render()
        immapp.manual_render.tear_down()
        assert runner_params.callbacks.setup_imgui_style is _user_setup_style
    assert nb_runs_seen[0] == NB_RUNS
