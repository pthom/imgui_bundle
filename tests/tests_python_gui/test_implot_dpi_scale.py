"""Test that ImmApp scales the ImPlot and ImPlot3D styles by the DPI factor, as Hello ImGui scales ImGui's style.
Exactly once: the test also fails if a later ImPlot or ImPlot3D scales its sizes by itself (2 * 2 = 4 times larger).
"""

from imgui_bundle import hello_imgui, immapp, imgui, implot, implot3d


def test_implot_dpi_scale() -> None:
    sizes: list[tuple[float, float, float, float]] = []  # per run: a size of imgui, implot, implot3d, and a 3D marker

    def gui() -> None:
        if imgui.get_frame_count() == 3:
            sizes.append(
                (
                    imgui.get_style().item_spacing.x,
                    implot.get_style().plot_default_size.x,
                    implot3d.get_style().plot_default_size.x,
                    implot3d.get_style().marker_size,
                )
            )
            hello_imgui.get_runner_params().app_shall_exit = True

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui
    runner_params.app_window_params.window_geometry.size = (300, 200)
    runner_params.ini_disable = True
    add_ons = immapp.AddOnsParams(with_implot=True, with_implot3d=True)

    # 1, then 2 as on a screen at 200%, twice with the same params: ImmApp's callbacks must not pile up
    for dpi_factor in (1.0, 2.0, 2.0):
        runner_params.dpi_aware_params.dpi_window_size_factor = dpi_factor
        immapp.run(runner_params, add_ons)

    unscaled = sizes[0]
    scaled = tuple(2.0 * v for v in unscaled)
    assert sizes == [unscaled, scaled, scaled], sizes
    print("OK test_implot_dpi_scale", sizes)
