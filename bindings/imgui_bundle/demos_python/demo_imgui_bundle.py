# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List, Callable
from types import ModuleType
from dataclasses import dataclass

from imgui_bundle import imgui, hello_imgui, immapp
from imgui_bundle.immapp import static
from imgui_bundle.demos_python import demo_text_edit
from imgui_bundle.demos_python import demo_imgui_bundle_intro
from imgui_bundle.demos_python import demo_imgui_show_demo_window
from imgui_bundle.demos_python import demo_widgets
from imgui_bundle.demos_python import demo_implot
from imgui_bundle.demos_python import demo_imgui_md
from imgui_bundle.demos_python import demo_immvision_launcher
from imgui_bundle.demos_python import demo_imguizmo_launcher
from imgui_bundle.demos_python import demo_tex_inspect_launcher
from imgui_bundle.demos_python import demo_node_editor_launcher
from imgui_bundle.demos_python import demo_immapp_launcher
from imgui_bundle.demos_python import demo_nanovg_launcher
from imgui_bundle.demos_python import demo_themes
from imgui_bundle.demos_python import demo_logger
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def show_module_demo(demo_filename: str, demo_function: Callable[[], None]) -> None:
    if imgui.collapsing_header("Code for this demo"):
        demo_utils.show_python_vs_cpp_file(demo_filename)
    demo_function()


def main() -> None:
    print(
        f"For information, demos sources are available in {demo_utils.api_demos.demos_python_folder()}"
    )

    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())
    ################################################################################################
    # Part 1: Define the runner params
    ################################################################################################

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    # Window size and title
    runner_params.app_window_params.window_title = (
        "Dear ImGui Bundle interactive manual"
    )
    runner_params.app_window_params.window_geometry.size = (1400, 950)

    # Menu bar
    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.imgui_window_params.show_status_bar = True

    ################################################################################################
    # Part 2: Define the application layout and windows
    ################################################################################################

    # First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    # In this demo, we also demonstrate multiple viewports.
    # you can drag windows outside out the main window in order to put their content into new native windows
    runner_params.imgui_window_params.enable_viewports = True

    #
    # Define our dockable windows : each window provide a Gui callback, and will be displayed
    # in a docking split.
    #
    dockable_windows: List[hello_imgui.DockableWindow] = []

    def add_demo_dockable_window(label: str, demo_module: ModuleType):
        window = hello_imgui.DockableWindow()
        window.label = label
        window.dock_space_name = "MainDockSpace"
        demo_module_name = demo_module.__name__.split(".")[-1]

        def win_fn() -> None:
            show_module_demo(demo_module_name, demo_module.demo_gui)

        window.gui_function = win_fn
        dockable_windows.append(window)

    @dataclass
    class DemoDetails:
        label: str
        demo_module: ModuleType

    demos = [
        DemoDetails("Dear ImGui Bundle", demo_imgui_bundle_intro),
        DemoDetails("Dear ImGui", demo_imgui_show_demo_window),
        DemoDetails("Immediate Apps", demo_immapp_launcher),
        DemoDetails("Implot", demo_implot),
        DemoDetails("Node Editor", demo_node_editor_launcher),
        DemoDetails("Markdown", demo_imgui_md),
        DemoDetails("Text Editor", demo_text_edit),
        DemoDetails("Widgets", demo_widgets),
        DemoDetails("ImmVision", demo_immvision_launcher),
        DemoDetails("NanoVG", demo_nanovg_launcher),
        DemoDetails("ImGuizmo", demo_imguizmo_launcher),
        DemoDetails("Themes", demo_themes),
        DemoDetails("Logger", demo_logger),
        DemoDetails("tex_inspect", demo_tex_inspect_launcher),
    ]

    for demo in demos:
        add_demo_dockable_window(demo.label, demo.demo_module)

    runner_params.docking_params.dockable_windows = dockable_windows

    # the main gui is only responsible to give focus to ImGui Bundle dockable window
    @static(nb_frames=0)
    def show_gui():
        if show_gui.nb_frames == 1:
            # Focus cannot be given at frame 0, since some additional windows will
            # be created after (and will steal the focus)
            runner_params.docking_params.focus_dockable_window("Dear ImGui Bundle")
        show_gui.nb_frames += 1

    runner_params.callbacks.show_gui = show_gui
    runner_params.use_imgui_test_engine = True

    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    addons.with_node_editor = True
    addons.with_markdown = True
    addons.with_implot = True
    addons.with_tex_inspect = True
    immapp.run(runner_params=runner_params, add_ons_params=addons)


if __name__ == "__main__":
    main()
