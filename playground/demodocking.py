"""
HelloImGui bindings issues:

* [ ] issue / Logger not found
  # void CommandGui(AppState & state, HelloImGui::Widgets::Logger & logger)

* [ ] Typo in HelloImGui::DockableWindow.GuiFonction !

* [ ] issue / embedded namespace
  HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons();
  ==>
  hello_imgui.load_default_font_with_font_awesome_icons()

* [ ] ImGui transcribed to im_gui

* [ ] structs could be exported as dataclasses, so that we have an equivalent of designated initializers

* [ ] Rewrite parts of cpp code, to avoid mysterious inits of docking elements

* [ ] Pb /pass param ImVec2: should accept tuple?
    Use IM_VEC2_CLASS_EXTRA (cf imconfig.h)?

"""

import os
from enum import Enum
from lg_imgui_bundle import imgui, implot, hello_imgui, icons_fontawesome
from typing import Any


THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Important: HelloImGui uses an assets dir where it can find assets (fonts, images, etc.)
#
# By default an assets folder is installed via pip inside site-packages/lg_imgui_bundle/assets
# and provides two fonts (fonts/DroidSans.ttf and fonts/fontawesome-webfont.ttf)
# If you need to add more assets, make a copy of this assets folder and add your own files, and call set_assets_folder
hello_imgui.set_assets_folder(THIS_DIR + "/assets")


# Struct that holds the application's state
class AppState:
    f: float = 0.
    counter: int = 0
    rocket_progress: float = 0.

    class RocketState(Enum):
        Init = 0
        Preparing = 1
        Launched = 2

    rocket_state: RocketState = RocketState.Init


# MyLoadFonts: demonstrate
# * how to load additional fonts
# * how to use assets from the local assets/ folder
gAkronimFont: imgui.ImFont = None


def my_load_fonts():
    global gAkronimFont
    # First, we load the default fonts (the font that was loaded first is the default font)
    hello_imgui.load_default_font_with_font_awesome_icons()
    # HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons();  # issue / embedded namespace

    # Then we load a second font from
    # Since this font is in a local assets/ folder, it was embedded automatically
    font_filename = "fonts/Akronim-Regular.ttf"
    gAkronimFont = hello_imgui.load_font_ttf_with_font_awesome_icons(font_filename, 40.)


# CommandGui: the widgets on the left panel
# void CommandGui(AppState & state, HelloImGui::Widgets::Logger & logger)
def command_gui(state: AppState, logger: Any):
    imgui.text_wrapped("The font below was loaded from the application assets folder" \
                       "(those files are embedded automatically).")
    imgui.push_font(gAkronimFont)
    imgui.text_wrapped("Hello, Dear ImGui! " + icons_fontawesome.ICON_FA_SMILE)
    imgui.pop_font()
    imgui.separator()

    # Edit 1 float using a slider from 0.0f to 1.0f
    changed, state.f = imgui.slider_float("float", state.f, 0.0, 1.0)
    if changed:
        pass
        # logger.warning("state.f was changed to %f", state.f);

    # Buttons return true when clicked (most widgets return true when edited/activated)
    if imgui.button("Button"):
        state.counter += 1
        # logger.info("Button was pressed", state.f);

    imgui.same_line()
    imgui.text(f"counter = {state.counter}")

    if state.rocket_state == AppState.RocketState.Init:
        if imgui.button(icons_fontawesome.ICON_FA_ROCKET + " Launch rocket"):
            state.rocket_state = AppState.RocketState.Preparing
            # logger.warning("Rocket is being prepared");
            print("Rocket is being prepared")
    elif state.rocket_state == AppState.RocketState.Preparing:
        imgui.text("Please Wait")
        state.rocket_progress += 0.003
        if state.rocket_progress >= 1.:
            state.rocket_state = AppState.RocketState.Launched
            print("Rocket was launched!")
            # logger.warning("Rocket was launched!");
    elif state.rocket_state == AppState.RocketState.Launched:
        imgui.text(icons_fontawesome.ICON_FA_ROCKET + " Rocket Launched")
        if imgui.button("Reset Rocket"):
            state.rocket_state = AppState.RocketState.Init
            state.rocket_progress = 0.


# Our Gui in the status bar
def status_bar_gui(appState: AppState):
    if appState.rocket_state == AppState.RocketState.Preparing:
        imgui.text("Rocket completion: ")
        imgui.same_line()
        imgui.progress_bar(appState.rocket_progress, imgui.ImVec2(100., 15.))


def main():
    # Our application state
    app_state = AppState()

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()

    runner_params.app_window_params.window_title = "HelloImGui docking demo"

    # Provide a full screen dock space
    runner_params.im_gui_window_params.default_im_gui_window_type = \
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space

    #
    # Define the docking splits, i.e. the way the screen space is split in different
    # target zones for the dockable windows
    #
    """
    ___________________________________________
    |        |                                |
    | Left   |                                |
    | Space  |    MainDockSpace               |
    |        |                                |
    |        |                                |
    |        |                                |
    -------------------------------------------
    |     BottomSpace                         |
    -------------------------------------------
    """

    # First, add a space named "BottomSpace" whose height is 25% of the app height
    # This will split the preexisting default dockspace "MainDockSpace"
    # (which is provided by "Hello ImGui") in two parts.
    split_main_bottom = hello_imgui.DockingSplit()
    split_main_bottom.initial_dock = "MainDockSpace"
    split_main_bottom.new_dock = "BottomSpace"
    split_main_bottom.direction = imgui.ImGuiDir_.down
    split_main_bottom.ratio = 0.25

    # Then, add a space to the left which occupies a column
    # whose width is 25% of the app width
    split_main_left = hello_imgui.DockingSplit()
    split_main_left.initial_dock = "MainDockSpace"
    split_main_left.new_dock = "LeftSpace"
    split_main_left.direction = imgui.ImGuiDir_.left
    split_main_left.ratio = 0.25

    runner_params.docking_params.docking_splits = \
    [
        split_main_bottom,
        split_main_left,
        # We now have three spaces: "MainDockSpace", "BottomSpace", and "LeftSpace"
    ]


    #
    # Define our dockable windows : each window provide a Gui callback
    #

    # A Command panel named "Commands" will be placed in "LeftSpace".
    # Its Gui is provided by a lambda that calls "CommandGui"
    commands_window = hello_imgui.DockableWindow()
    commands_window.label = "Commands"
    commands_window.dock_space_name = "LeftSpace"
    commands_window.gui_fonction = lambda: command_gui(app_state, logger)

    # HelloImGui::Widgets::Logger is a Dockable Window, with the title "Logs"
    # and placed in the dockspace "BottomSpace"
    # (see src/hello_imgui/widgets/logger.h)
    # HelloImGui::Widgets::Logger logger("Logs", "BottomSpace");
    logger = None

    dear_imgui_demo_window = hello_imgui.DockableWindow()
    dear_imgui_demo_window.label = "Dear ImGui Demo"
    dear_imgui_demo_window.dock_space_name = "MainDockSpace"
    dear_imgui_demo_window.gui_fonction = lambda: True

    runner_params.docking_params.dockable_windows = [
        commands_window,

        # A Log  window named "Logs" will be placed in "BottomSpace"
        # It uses HelloImGui::Widgets::Logger
        # logger,

        # A Window named "Dear ImGui Demo" will be placed in "MainDockSpace".
        # Its Gui function is *not* provided here.
        # This way, we can define the Gui of this window elsewhere: as long
        # as we create a window named "Dear ImGui Demo", it will be placed
        # in "MainDockSpace".
        dear_imgui_demo_window,
    ]

    # We use the default Menu and status bar of Hello ImGui
    runner_params.im_gui_window_params.show_status_bar = True

    # runnerParams.callbacks.ShowGui is the default Gui callback
    # We call ImGui::ShowDemoWindow, which will create a window named "Dear ImGui Demo".
    # It will automatically be placed in "MainDockSpace"
    runner_params.callbacks.show_gui = lambda: imgui.show_demo_window()

    # Custom load fonts
    runner_params.callbacks.load_additional_fonts = my_load_fonts

    # Menu bar: we use the default menu of Hello ImGui,
    # to which we add some more items
    def show_menu_gui():
        if imgui.begin_menu("My Menu"):
            if imgui.menu_item("Test me"):
                print("It works")
                # logger.warning("It works")
            imgui.end_menu()
    runner_params.im_gui_window_params.show_menu_bar = True
    runner_params.callbacks.show_menus = show_menu_gui

    # Status bar:
    runner_params.im_gui_window_params.show_status_bar = True
    # uncomment next line in order to hide the FPS in the status bar
    # runner_params.im_gui_window_params.show_status_fps = False
    runner_params.callbacks.show_status = lambda: status_bar_gui(app_state)

    # In this demo, we also demonstrate multiple viewports (i.e multiple native windows)
    # you can drag the inner windows outside out the main window in order to create another native window
    def setup_im_gui_config():
        io = imgui.get_io()
        io.config_flags |= imgui.ImGuiConfigFlags_.docking_enable
        io.config_flags |= imgui.ImGuiConfigFlags_.viewports_enable
    runner_params.callbacks.setup_im_gui_config = setup_im_gui_config

    # Then, we run the app
    hello_imgui.run(runner_params)
    return 0


if __name__ == "__main__":
    main()
