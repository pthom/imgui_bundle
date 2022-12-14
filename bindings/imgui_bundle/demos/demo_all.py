import os
import sys
from typing import List, Callable
from types import ModuleType

from imgui_bundle import imgui, hello_imgui, immapp, imgui_color_text_edit as ed, imgui_md
from imgui_bundle.immapp import static
from imgui_bundle.demos.demos_immapp import demo_apps
from imgui_bundle.demos import demo_imgui_color_text_edit, demo_imgui_bundle, demo_imgui_show_demo_window
from imgui_bundle.demos import demo_widgets
from imgui_bundle.demos import demo_implot
from imgui_bundle.demos import demo_node_editor
from imgui_bundle.demos import demo_imgui_md
from imgui_bundle.demos import demo_immvision_launcher
from imgui_bundle.demos import demo_imguizmo_launcher
from imgui_bundle.demos import demo_tex_inspect_launcher
from imgui_bundle.demos import demo_themes


@static(was_initialized=None)
def show_module_demo(demo_module: ModuleType, demo_function: Callable[[], None]) -> None:
    static = show_module_demo

    if not static.was_initialized:
        static.editor = ed.TextEditor()
        static.last_module = None
        static.was_initialized = True

    if demo_module != static.last_module:
        import inspect

        code = inspect.getsource(demo_module)
        static.editor.set_text(code)
        static.last_module = demo_module

    if imgui.collapsing_header("Code for this demo"):
        static.editor.render("Code")

    demo_function()


def demo_node_editor_separate_app():
    from imgui_bundle.demos.demo_node_editor import demo_node_editor

    imgui_md.render(
        """
# imgui-node-editor
[imgui-node-editor](https://github.com/thedmd/imgui-node-editor) is a zoomable and node Editor built using Dear ImGui.
    """
    )
    if imgui.collapsing_header("Screenshot - BluePrint", imgui.TreeNodeFlags_.default_open):
        hello_imgui.image_from_asset("images/node_editor_screenshot.jpg", immapp.em_vec2(40, 0))
    if imgui.collapsing_header("Demo"):
        imgui.text("Use the mouse wheel to zoom-unzoom. Right-click and drag to pan the view.")
        demo_node_editor()

    # if imgui.button("Run demo"):
    #     import subprocess
    #
    #     this_dir = os.path.dirname(__file__)
    #     subprocess.Popen([sys.executable, this_dir + "/demo_node_editor.py"])


def main() -> None:
    ################################################################################################
    # Part 1: Define the runner params
    ################################################################################################

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    # Window size and title
    runner_params.app_window_params.window_title = "ImGui Bundle"
    runner_params.app_window_params.window_geometry.size = (1200, 900)

    # Menu bar
    runner_params.imgui_window_params.show_menu_bar = True

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
    # 2.1 Define our dockable windows : each window provide a Gui callback, and will be displayed
    #     in a docking split.
    #
    dockable_windows: List[hello_imgui.DockableWindow] = []

    def add_dockable_window(
        label: str,
        demo_module: ModuleType,
        demo_function: Callable[[], None],
        dock_space_name: str = "MainDockSpace",
    ):
        window = hello_imgui.DockableWindow()
        window.label = label
        window.dock_space_name = dock_space_name

        def win_fn() -> None:
            show_module_demo(demo_module, demo_function)

        window.gui_function = win_fn
        dockable_windows.append(window)

    add_dockable_window("ImGui Bundle", demo_imgui_bundle, demo_imgui_bundle.demo_imgui_bundle)
    add_dockable_window("Dear ImGui Demo", demo_imgui_show_demo_window, demo_imgui_show_demo_window.show_demo_window)
    add_dockable_window("Immediate Apps", demo_apps, demo_apps.make_closure_demo_apps())
    add_dockable_window("Implot", demo_implot, demo_implot.demo_implot)
    add_dockable_window("Node Editor", demo_node_editor, demo_node_editor_separate_app)
    add_dockable_window("Markdown", demo_imgui_md, demo_imgui_md.demo_imgui_md)
    add_dockable_window("Text Editor", demo_imgui_color_text_edit, demo_imgui_color_text_edit.demo_imgui_color_text_edit)
    add_dockable_window("Widgets", demo_widgets, demo_widgets.demo_widgets)
    add_dockable_window("ImmVision", demo_immvision_launcher, demo_immvision_launcher.demo_launch)
    add_dockable_window("imgui_tex_inspect", demo_tex_inspect_launcher, demo_tex_inspect_launcher.demo_launch)
    add_dockable_window("ImGuizmo", demo_imguizmo_launcher, demo_imguizmo_launcher.demo_launch)
    add_dockable_window("Themes", demo_themes, demo_themes.demo_launch)

    runner_params.docking_params.dockable_windows = dockable_windows

    # Main gui only responsibility is to give focus to ImGui Bundle dockable window
    @static(nb_frames=0)
    def show_gui():
        if show_gui.nb_frames == 1:
            # Focus cannot be given at frame 0, since some additional windows will
            # be created after (and will steal the focus)
            runner_params.docking_params.focus_dockable_window("ImGui Bundle")
        show_gui.nb_frames += 1

    runner_params.callbacks.show_gui = show_gui

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
