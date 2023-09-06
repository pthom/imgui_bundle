# A more complex app demo,
#
# It demonstrates:
# - How to use a specific application state (instead of using static variables)
# - How to set up a complex docking layouts (with several possible layouts):
#     - How to use the status bar
# - How to use default menus (App and view menu), and how to customize them
# - How to display a log window
# - How to load additional fonts


from enum import Enum
import time

from imgui_bundle import hello_imgui, icons_fontawesome, imgui, immapp
from imgui_bundle.demos_python import demo_utils
from typing import List


##########################################################################
#    Our Application State
##########################################################################
class MyAppSettings:
    name: str = "Test"
    value: int = 10


class RocketState(Enum):
    Init = 0
    Preparing = 1
    Launched = 2


# Struct that holds the application's state
class AppState:
    f: float
    counter: int
    rocket_progress: float
    my_app_settings: MyAppSettings
    rocket_state: RocketState

    def __init__(self):
        self.f = 0
        self.counter = 0
        self.rocket_progress = 0.0
        self.my_app_settings = MyAppSettings()
        self.rocket_state = RocketState.Init


##########################################################################
#    Additional fonts handling
##########################################################################

TITLE_FONT: imgui.ImFont


def load_fonts():  # This is called by runnerParams.callbacks.LoadAdditionalFonts
    global TITLE_FONT
    # First, load the default font (the default font should be loaded first)
    hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()
    # Then load the title font
    TITLE_FONT = hello_imgui.load_font_ttf("fonts/DroidSans.ttf", 18.0)


##########################################################################
#    Save additional settings in the ini file
##########################################################################
# This demonstrates how to store additional info in the application settings
# Use this sparingly!
# This is provided as a convenience only, and it is not intended to store large quantities of text data.

# Warning, the save/load function below are quite simplistic!
def my_app_settings_to_string(settings: MyAppSettings) -> str:
    r = settings.name + "\n" + str(settings.value)
    return r


def string_to_my_app_settings(s: str) -> MyAppSettings:
    r = MyAppSettings()
    lines = s.splitlines(False)
    if len(lines) >= 2:
        r.name = lines[0]
        r.value = int(lines[1])
    return r


def load_my_app_settings(app_state: AppState):
    """
    Note: load_my_app_settings() and save_my_app_settings() will be called in the callbacks `post_init` & `before_exit`
         runner_params.callbacks.post_init = lambda: load_user_settings(app_state)
         runner_params.callbacks.before_exit = lambda: save_user_settings(app_state)
    """
    app_state.my_app_settings = string_to_my_app_settings(hello_imgui.load_user_pref("MyAppSettings"))


def save_my_app_settings(app_state: AppState):
    hello_imgui.save_user_pref("MyAppSettings", my_app_settings_to_string(app_state.my_app_settings))


##########################################################################
#    Gui functions used in this demo
##########################################################################
@immapp.static(last_hide_time=1)
def demo_hide_window():
    # Display a button that will hide the application window
    imgui.push_font(TITLE_FONT)
    imgui.text("Hide app window")
    imgui.pop_font()
    imgui.text_wrapped("By clicking the button below, you can hide the window for 3 seconds.")

    if imgui.button("Hide"):
        demo_hide_window.last_hide_time = time.time()
        hello_imgui.get_runner_params().app_window_params.hidden = True

    if demo_hide_window.last_hide_time > 0.:
        now = time.time()
        if now - demo_hide_window.last_hide_time > 3.0:
            demo_hide_window.last_hide_time = -1.
            hello_imgui.get_runner_params().app_window_params.hidden = False


# Display a button that will show an additional window
def demo_show_additional_window():
    # Notes:
    #     - it is *not* possible to modify the content of the vector runnerParams.dockingParams.dockableWindows
    #       from the code inside a window's `GuiFunction` (since this GuiFunction will be called while iterating
    #       on this vector!)
    #     - there are two ways to dynamically add windows:
    #           * either make them initially invisible, and exclude them from the view menu (such as shown here)
    #           * or modify runnerParams.dockingParams.dockableWindows inside the callback RunnerCallbacks.PreNewFrame
    window_name = "Additional Window"

    imgui.push_font(TITLE_FONT)
    imgui.text("Dynamically add window")
    imgui.pop_font()

    if imgui.button("Show additional window"):
        runner_params = hello_imgui.get_runner_params()
        additional_window_ptr = runner_params.docking_params.dockable_window_of_name(window_name)
        if additional_window_ptr:
            # additional_window_ptr.include_in_view_menu = True
            additional_window_ptr.is_visible = True


def demo_basic_widgets(app_state: AppState):
    imgui.push_font(TITLE_FONT)
    imgui.text("Basic widgets demo")
    imgui.pop_font()
    imgui.text_wrapped("The widgets below will interact with the log window")

    # Edit a float using a slider from 0.0 to 1.0
    changed, app_state.f = imgui.slider_float("float", app_state.f, 0.0, 1.0)
    if changed:
        hello_imgui.log(hello_imgui.LogLevel.warning, f"state.f was changed to {app_state.f}")

    # Buttons return true when clicked (most widgets return true when edited/activated)
    if imgui.button("Button"):
        app_state.counter += 1
        hello_imgui.log(hello_imgui.LogLevel.info, "Button was pressed")
    imgui.same_line()
    imgui.text(f"counter = {app_state.counter}")


def demo_user_settings(app_state: AppState):
    imgui.push_font(TITLE_FONT)
    imgui.text("User settings")
    imgui.pop_font()
    imgui.text_wrapped("The values below are stored in the application settings ini file and restored at startup")
    imgui.set_next_item_width(hello_imgui.em_size(7.0))
    _, app_state.my_app_settings.name = imgui.input_text("Name", app_state.my_app_settings.name)
    imgui.set_next_item_width(hello_imgui.em_size(7.0))
    _, app_state.my_app_settings.value = imgui.slider_int("Value", app_state.my_app_settings.value, 0, 100)


def demo_rocket(app_state: AppState):
    imgui.push_font(TITLE_FONT)
    imgui.text("Rocket demo")
    imgui.pop_font()
    imgui.text_wrapped("How to show a progress bar in the status bar")
    if app_state.rocket_state == RocketState.Init:
        if imgui.button(f"{icons_fontawesome.ICON_FA_ROCKET} Launch rocket"):
            app_state.rocket_launch_time = time.time()
            app_state.rocket_state = RocketState.Preparing
            hello_imgui.log(hello_imgui.LogLevel.warning, "Rocket is being prepared")
    elif app_state.rocket_state == RocketState.Preparing:
        imgui.text("Please Wait")
        app_state.rocket_progress = (time.time() - app_state.rocket_launch_time) / 3.0
        if app_state.rocket_progress >= 1.0:
            app_state.rocket_state = RocketState.Launched
            hello_imgui.log(hello_imgui.LogLevel.warning, "Rocket was launched")
    elif app_state.rocket_state == RocketState.Launched:
        imgui.text(f"{icons_fontawesome.ICON_FA_ROCKET} Rocket launched")
        if imgui.button("Reset Rocket"):
            app_state.rocket_state = RocketState.Init
            app_state.rocket_progress = 0.0


def demo_docking_flags():
    imgui.push_font(TITLE_FONT)
    imgui.text("Main dock space node flags")
    imgui.pop_font()
    imgui.text_wrapped(
        """
This will edit the ImGuiDockNodeFlags for "MainDockSpace".
Most flags are inherited by children dock spaces.
        """
    )

    class DockFlagWithInfo:
        def __init__(self, flag, label, tip):
            self.flag = flag
            self.label = label
            self.tip = tip

    all_flags = [
        DockFlagWithInfo(imgui.DockNodeFlags_.no_split, "NoSplit", "prevent Dock Nodes from being split"),
        DockFlagWithInfo(imgui.DockNodeFlags_.no_resize, "NoResize", "prevent Dock Nodes from being resized"),
        DockFlagWithInfo(imgui.DockNodeFlags_.auto_hide_tab_bar, "AutoHideTabBar",
                         "show tab bar only if multiple windows\n" +
                         "You will need to restore the layout after changing (Menu \"View/Restore Layout\")"),
        DockFlagWithInfo(imgui.DockNodeFlags_.no_docking_in_central_node, "NoDockingInCentralNode",
                         "prevent docking in central node\n(only works with the main dock space)"),
        # DockFlagWithInfo(imgui.DockNodeFlags_.passthru_central_node, "PassthruCentralNode", "advanced"),
    ]

    main_dock_space_node_flags = hello_imgui.get_runner_params().docking_params.main_dock_space_node_flags
    for flag_with_info in all_flags:
        _, main_dock_space_node_flags = imgui.checkbox_flags(
            flag_with_info.label, main_dock_space_node_flags, flag_with_info.flag)
        if imgui.is_item_hovered():
            imgui.set_tooltip("%s" % flag_with_info.tip)

    hello_imgui.get_runner_params().docking_params.main_dock_space_node_flags = main_dock_space_node_flags


def gui_window_layout_customization():
    imgui.push_font(TITLE_FONT)
    imgui.text("Switch between layouts")
    imgui.pop_font()
    imgui.text("with the menu \"View/Layouts\"")
    if imgui.is_item_hovered():
        imgui.set_tooltip("Each layout remembers separately the modifications applied by the user, \n" +
                          "and the selected layout is restored at startup")

    imgui.separator()

    imgui.push_font(TITLE_FONT)
    imgui.text("Change the theme")
    imgui.pop_font()
    imgui.text("with the menu \"View/Theme\"")
    if imgui.is_item_hovered():
        imgui.set_tooltip("The selected theme is remembered and restored at startup")
    imgui.separator()

    demo_docking_flags()
    imgui.separator()


def gui_window_demo_features(app_state: AppState):
    demo_basic_widgets(app_state)
    imgui.separator()
    demo_rocket(app_state)
    imgui.separator()
    demo_user_settings(app_state)
    imgui.separator()
    demo_hide_window()
    imgui.separator()
    demo_show_additional_window()
    imgui.separator()


def status_bar_gui(app_state: AppState):
    if app_state.rocket_state == RocketState.Preparing:
        imgui.text("Rocket completion: ")
        imgui.same_line()
        imgui.progress_bar(app_state.rocket_progress, hello_imgui.em_to_vec2(7.0, 1.0))  # type: ignore


def show_menu_gui():
    if imgui.begin_menu("My Menu"):
        clicked, _ = imgui.menu_item("Test me", "", False)
        if clicked:
            hello_imgui.log(hello_imgui.LogLevel.warning, "It works")
        imgui.end_menu()


def show_app_menu_items():
    clicked, _ = imgui.menu_item("A Custom app menu item", "", False)
    if clicked:
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on A Custom app menu item")


##########################################################################
#    Docking Layouts and Docking windows
##########################################################################

#
# 1. Define the Docking splits (two versions are available)
#
def create_default_docking_splits() -> List[hello_imgui.DockingSplit]:
    # Define the default docking splits,
    # i.e. the way the screen space is split in different target zones for the dockable windows
    # We want to split "MainDockSpace" (which is provided automatically) into three zones, like this:
    #
    #    ___________________________________________
    #    |        |                                |
    #    | Command|                                |
    #    | Space  |    MainDockSpace               |
    #    |        |                                |
    #    |        |                                |
    #    |        |                                |
    #    -------------------------------------------
    #    |     MiscSpace                           |
    #    -------------------------------------------
    #

    # Uncomment the next line if you want to always start with this layout.
    # Otherwise, modifications to the layout applied by the user layout will be remembered.
    # runner_params.docking_params.layout_condition = hello_imgui.DockingLayoutCondition.ApplicationStart

    # Then, add a space named "MiscSpace" whose height is 25% of the app height.
    # This will split the preexisting default dockspace "MainDockSpace" in two parts.
    split_main_misc = hello_imgui.DockingSplit()
    split_main_misc.initial_dock = "MainDockSpace"
    split_main_misc.new_dock = "MiscSpace"
    split_main_misc.direction = imgui.Dir_.down
    split_main_misc.ratio = 0.25

    # Then, add a space to the left which occupies a column whose width is 25% of the app width
    split_main_command = hello_imgui.DockingSplit()
    split_main_command.initial_dock = "MainDockSpace"
    split_main_command.new_dock = "CommandSpace"
    split_main_command.direction = imgui.Dir_.left
    split_main_command.ratio = 0.25

    splits = [split_main_misc, split_main_command]
    return splits


def create_alternative_docking_splits() -> List[hello_imgui.DockingSplit]:
    # Define alternative docking splits for the "Alternative Layout"
    #    ___________________________________________
    #    |                |                        |
    #    | Misc           |                        |
    #    | Space          |    MainDockSpace       |
    #    |                |                        |
    #    -------------------------------------------
    #    |                                         |
    #    |                                         |
    #    |     CommandSpace                        |
    #    |                                         |
    #    -------------------------------------------

    split_main_command = hello_imgui.DockingSplit()
    split_main_command.initial_dock = "MainDockSpace"
    split_main_command.new_dock = "CommandSpace"
    split_main_command.direction = imgui.Dir_.down
    split_main_command.ratio = 0.5

    split_main_misc = hello_imgui.DockingSplit()
    split_main_misc.initial_dock = "MainDockSpace"
    split_main_misc.new_dock = "MiscSpace"
    split_main_misc.direction = imgui.Dir_.left
    split_main_misc.ratio = 0.5

    splits = [split_main_command, split_main_misc]
    return splits


#
# 2. Define the Dockable windows
#
def create_dockable_windows(app_state: AppState) -> List[hello_imgui.DockableWindow]:
    # A features demo window named "FeaturesDemo" will be placed in "CommandSpace".
    # Its Gui is provided by "gui_window_demo_features"
    features_demo_window = hello_imgui.DockableWindow()
    features_demo_window.label = "Features Demo"
    features_demo_window.dock_space_name = "CommandSpace"
    features_demo_window.gui_function = lambda: gui_window_demo_features(app_state)

    # A layout customization window will be placed in "MainDockSpace".
    # Its Gui is provided by "gui_window_layout_customization"
    layout_customization_window = hello_imgui.DockableWindow()
    layout_customization_window.label = "Layout customization"
    layout_customization_window.dock_space_name = "MainDockSpace"
    layout_customization_window.gui_function = gui_window_layout_customization

    # A Log window named "Logs" will be placed in "MiscSpace". It uses the HelloImGui logger gui
    logs_window = hello_imgui.DockableWindow()
    logs_window.label = "Logs"
    logs_window.dock_space_name = "MiscSpace"
    logs_window.gui_function = hello_imgui.log_gui

    # A Window named "Dear ImGui Demo" will be placed in "MainDockSpace"
    dear_imgui_demo_window = hello_imgui.DockableWindow()
    dear_imgui_demo_window.label = "Dear ImGui Demo"
    dear_imgui_demo_window.dock_space_name = "MainDockSpace"
    dear_imgui_demo_window.gui_function = imgui.show_demo_window

    # additional_window is initially not visible (and not mentioned in the view menu).
    # it will be opened only if the user chooses to display it
    additional_window = hello_imgui.DockableWindow()
    additional_window.label = "Additional Window"
    additional_window.is_visible = False  # this window is initially hidden,
    additional_window.include_in_view_menu = False  # it is not shown in the view menu,
    additional_window.remember_is_visible = False  # its visibility is not saved in the settings file,
    additional_window.dock_space_name = "MiscSpace"  # when shown, it will appear in MiscSpace.
    additional_window.gui_function = lambda: imgui.text("This is the additional window")

    dockable_windows = [
        features_demo_window,
        layout_customization_window,
        logs_window,
        dear_imgui_demo_window,
        additional_window,
    ]
    return dockable_windows


#
# 3. Define the layouts:
# A layout is stored inside DockingParams, and stores the splits + the dockable windows.
# Here, we provide the default layout, and two alternative layouts.
def create_default_layout(app_state: AppState) -> hello_imgui.DockingParams:
    docking_params = hello_imgui.DockingParams()
    # By default, the layout name is already "Default"
    # docking_params.layout_name = "Default"
    docking_params.docking_splits = create_default_docking_splits()
    docking_params.dockable_windows = create_dockable_windows(app_state)
    return docking_params


def create_alternative_layouts(app_state: AppState) -> List[hello_imgui.DockingParams]:
    alternative_layout = hello_imgui.DockingParams()
    alternative_layout.layout_name = "Alternative Layout"
    alternative_layout.docking_splits = create_alternative_docking_splits()
    alternative_layout.dockable_windows = create_dockable_windows(app_state)

    tabs_layout = hello_imgui.DockingParams()
    tabs_layout.layout_name = "Tabs Layout"
    tabs_layout.dockable_windows = create_dockable_windows(app_state)
    # Force all windows to be presented in the MainDockSpace
    for window in tabs_layout.dockable_windows:
        window.dock_space_name = "MainDockSpace"
    # In "Tabs Layout", no split is created
    tabs_layout.docking_splits = []

    return [alternative_layout, tabs_layout]


##########################################################################
#    main(): here, we simply fill RunnerParams, then run the application
##########################################################################
def main():
    # By default, an assets folder is installed via pip inside site-packages/lg_imgui_bundle/assets
    # and provides two fonts (fonts/DroidSans.ttf and fonts/fontawesome-webfont.ttf)
    # If you need to add more assets, make a copy of this assets folder and add your own files,
    # and call set_assets_folder
    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())

    #
    # Part 1: Define the application state, fill the status and menu bars, and load additional font
    #

    # Our application state
    app_state = AppState()

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()

    # Note: by setting the window title, we also set the name of the ini files in which the settings for the user
    # layout will be stored: Docking_demo.ini
    runner_params.app_window_params.window_title = "Docking demo"

    runner_params.imgui_window_params.menu_app_title = "Docking App"
    runner_params.app_window_params.window_geometry.size = (1000, 900)
    runner_params.app_window_params.restore_previous_geometry = True

    # Set LoadAdditionalFonts callback
    runner_params.callbacks.load_additional_fonts = load_fonts

    #
    # Status bar
    #
    # We use the default status bar of Hello ImGui
    runner_params.imgui_window_params.show_status_bar = True
    # Add custom widgets in the status bar
    runner_params.callbacks.show_status = lambda: status_bar_gui(app_state)
    # uncomment next line in order to hide the FPS in the status bar
    # runner_params.im_gui_window_params.show_status_fps = False

    #
    # Menu bar
    #
    runner_params.imgui_window_params.show_menu_bar = True  # We use the default menu of Hello ImGui
    # fill callbacks ShowMenuGui and ShowAppMenuItems, to add items to the default menu and to the App menu
    runner_params.callbacks.show_menus = show_menu_gui
    runner_params.callbacks.show_app_menu_items = show_app_menu_items

    #
    # Load user settings at callbacks `post_init` and save them at `before_exit`
    #
    runner_params.callbacks.post_init = lambda: load_my_app_settings(app_state)
    runner_params.callbacks.before_exit = lambda: save_my_app_settings(app_state)

    #
    # Part 2: Define the application layout and windows
    #

    # First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runner_params.imgui_window_params.default_imgui_window_type = \
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    # In this demo, we also demonstrate multiple viewports: you can drag windows outside out the main window
    # in order to put their content into new native windows
    runner_params.imgui_window_params.enable_viewports = True
    # Set the default layout (this contains the default DockingSplits and DockableWindows)
    runner_params.docking_params = create_default_layout(app_state)
    # Add alternative layouts
    runner_params.alternative_docking_layouts = create_alternative_layouts(app_state)

    #
    # Part 3: Run the app
    #
    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
