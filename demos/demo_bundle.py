import os
from typing import List, Callable

from imgui_bundle import hello_imgui, ImVec2, static

from demo_imgui import demo_imgui
from demo_hello_imgui import demo_hello_imgui
from demo_imgui_color_text_edit import demo_imgui_color_text_edit
from demo_widgets import demo_widgets
from demo_implot import demo_implot
from demo_node_editor import demo_node_editor


@static(first_frame=True)
def main():
    ################################################################################################
    # Part 1: Define the runner params
    ################################################################################################

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Docking demo"
    runner_params.app_window_params.window_size = ImVec2(1000, 900)
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

    # # Then, add a space named "BottomSpace" whose height is 25% of the app height.
    # # This will split the preexisting default dockspace "MainDockSpace" in two parts.
    # split_main_bottom = hello_imgui.DockingSplit()
    # split_main_bottom.initial_dock = "MainDockSpace"
    # split_main_bottom.new_dock = "BottomSpace"
    # split_main_bottom.direction = imgui.ImGuiDir_.down
    # split_main_bottom.ratio = 0.25
    #
    # runner_params.docking_params.docking_splits = [split_main_bottom]

    #
    # 2.1 Define our dockable windows : each window provide a Gui callback, and will be displayed
    #     in a docking split.
    #
    dockable_windows: List[hello_imgui.DockableWindow] = []

    def add_dockable_window(label: str, gui_function: Callable[[None], None], dock_space_name: str = "MainDockSpace"):
        window = hello_imgui.DockableWindow()
        window.label = label
        window.dock_space_name = dock_space_name
        window.gui_function = gui_function
        dockable_windows.append(window)

    add_dockable_window("Dear ImGui Demo", demo_imgui)
    add_dockable_window("Hello ImGui", demo_hello_imgui)
    add_dockable_window("Implot", demo_implot)
    add_dockable_window("Node Editor", demo_node_editor)
    add_dockable_window("Editor demo", demo_imgui_color_text_edit)
    add_dockable_window("Widgets", demo_widgets)
    runner_params.docking_params.dockable_windows = dockable_windows

    def fake_gui():
        if main.first_frame:
            # fixme: this fails
            runner_params.docking_params.focus_dockable_window("Dear ImGui Demo")
            main.first_frame = False

    runner_params.callbacks.show_gui = fake_gui


    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
