# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List, Callable
from types import ModuleType
from dataclasses import dataclass, field

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
from imgui_bundle.demos_python import demo_im_anim
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


_show_code_states: dict[str, bool] = {}

def show_module_demo(demo_filename: str, demo_function: Callable[[], None], show_code: bool = False) -> None:
    if imgui.get_frame_count() < 2:  # cf https://github.com/pthom/imgui_bundle/issues/293
        return
    if show_code:
        current = _show_code_states.get(demo_filename, False)
        _, current = imgui.checkbox("Show code##" + demo_filename, current)
        _show_code_states[demo_filename] = current
        if current:
            demo_utils.show_python_vs_cpp_file(demo_filename, 40)
    demo_function()


@dataclass
class DemoDetails:
    label: str
    demo_module: ModuleType
    show_code: bool = False


@dataclass
class DemoGroup:
    """A group of demos shown as collapsing headers inside a single tab."""
    label: str
    demos: List[DemoDetails] = field(default_factory=list)


def _show_group_gui(group: DemoGroup) -> None:
    """Gui function for a grouped tab: each sub-demo is a collapsing header."""
    if imgui.get_frame_count() < 2:
        return
    for demo in group.demos:
        demo_module_name = demo.demo_module.__name__.split(".")[-1]
        if imgui.collapsing_header(demo.label):
            imgui.indent()
            show_module_demo(demo_module_name, demo.demo_module.demo_gui, demo.show_code)
            imgui.unindent()


def make_params() -> tuple[hello_imgui.RunnerParams, immapp.AddOnsParams]:
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

    runner_params.ini_clear_previous_settings = True

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

    # --- Standalone tabs (no grouping) ---
    standalone_demos = [
        DemoDetails("Intro",       demo_imgui_bundle_intro),
        DemoDetails("Dear ImGui",  demo_imgui_show_demo_window),
        DemoDetails("Demo Apps",   demo_immapp_launcher),
    ]

    for demo in standalone_demos:
        window = hello_imgui.DockableWindow()
        window.label = demo.label
        window.dock_space_name = "MainDockSpace"
        demo_module_name = demo.demo_module.__name__.split(".")[-1]

        def make_win_fn(mod_name: str, mod: ModuleType, sc: bool) -> Callable[[], None]:
            def win_fn() -> None:
                show_module_demo(mod_name, mod.demo_gui, sc)
            return win_fn

        window.gui_function = make_win_fn(demo_module_name, demo.demo_module, demo.show_code)
        dockable_windows.append(window)

    # --- Grouped tabs (sub-demos shown as collapsing headers) ---
    groups = [
        DemoGroup("Visualization", [
            DemoDetails("Plots with ImPlot and ImPlot3D", demo_implot),
            DemoDetails("ImmVision - Image analyzer", demo_immvision_launcher),
            DemoDetails("ImGuizmo - Immediate Mode 3D Gizmo",  demo_imguizmo_launcher),
            DemoDetails("NanoVG - 2D Vector Drawing", demo_nanovg_launcher),
        ]),
        DemoGroup("Widgets", [
            DemoDetails("Markdown - Rich Text Rendering",     demo_imgui_md,    show_code=True),
            DemoDetails("Text Editor - Code Editing Widget",  demo_text_edit,   show_code=True),
            DemoDetails("Misc Widgets - Knobs, Toggles, ...", demo_widgets,     show_code=True),
            DemoDetails("Logger - Log Window Widget",         demo_logger,      show_code=True),
            DemoDetails("Tex Inspect - Texture Inspector",    demo_tex_inspect_launcher),
        ]),
        DemoGroup("Tools", [
            DemoDetails("Node Editor - Visual Node Graphs", demo_node_editor_launcher),
            DemoDetails("Themes - Style & Color Customization", demo_themes,   show_code=True),
            DemoDetails("ImAnim - Animation Library",       demo_im_anim),
        ]),
    ]

    for group in groups:
        window = hello_imgui.DockableWindow()
        window.label = group.label
        window.dock_space_name = "MainDockSpace"

        def make_group_fn(g: DemoGroup) -> Callable[[], None]:
            def win_fn() -> None:
                _show_group_gui(g)
            return win_fn

        window.gui_function = make_group_fn(group)
        dockable_windows.append(window)

    runner_params.docking_params.dockable_windows = dockable_windows

    # the main gui is only responsible to give focus to ImGui Bundle dockable window
    @static(nb_frames=0)
    def show_gui():
        if show_gui.nb_frames == 1:
            # Focus cannot be given at frame 0, since some additional windows will
            # be created after (and will steal the focus)
            runner_params.docking_params.focus_dockable_window("Dear ImGui Bundle")
        show_gui.nb_frames += 1

    def show_edit_font_scale_in_status_bar():
        imgui.set_next_item_width(imgui.get_content_region_avail().x / 10)
        _, imgui.get_style().font_scale_main = imgui.slider_float(
            "Font scale", imgui.get_style().font_scale_main, 0.5, 5)

    runner_params.callbacks.show_status = show_edit_font_scale_in_status_bar

    runner_params.callbacks.show_gui = show_gui

    if "test_engine" in dir(imgui):  # only enable test engine if available (i.e. if imgui bundle was compiled with it)
        runner_params.use_imgui_test_engine = True

    def setup_imgui_config() -> None:
        imgui.get_io().config_flags |= imgui.ConfigFlags_.nav_enable_keyboard.value

    runner_params.callbacks.setup_imgui_config = setup_imgui_config


    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    addons.with_node_editor = True
    addons.with_implot = True
    addons.with_implot3d = True
    addons.with_im_anim = True

    return runner_params, addons


def main():
    runner_params, addons = make_params()
    immapp.run(runner_params=runner_params, add_ons_params=addons)


if __name__ == "__main__":
    main()
