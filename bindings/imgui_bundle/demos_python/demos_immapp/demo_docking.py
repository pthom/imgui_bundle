# A more complex app demo
#
# It demonstrates how to:
# - set up a complex docking layouts (with several possible layouts):
# - load additional fonts, possibly colored, and with emojis
# - display a log window
# - use the status bar
# - use default menus (App and view menu), and how to customize them
# - use a specific application state (instead of using static variables)
# - save some additional user settings within imgui ini file
# - use borderless windows, that are movable and resizable
import json
from enum import Enum
import time

from imgui_bundle import hello_imgui, icons_fontawesome_6, imgui, immapp, imgui_ctx, ImVec4, ImVec2
from imgui_bundle.demos_python import demo_utils
from typing import List


##########################################################################
#    Our Application State
##########################################################################
class MyAppSettings:
    motto: hello_imgui.InputTextData
    value: int = 10

    def __init__(self):
        self.motto = hello_imgui.InputTextData(
            "Hello, Dear ImGui\n"
            "Unleash your creativity!\n",
            True, # multiline
            ImVec2(14.0, 3.0) # initial size (in em)
        )

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
    rocket_launch_time: float

    title_font: imgui.ImFont
    color_font: imgui.ImFont
    emoji_font: imgui.ImFont
    large_icon_font: imgui.ImFont

    def __init__(self):
        self.f = 0
        self.counter = 0
        self.rocket_progress = 0.0
        self.rocket_launch_time = 0.0
        self.my_app_settings = MyAppSettings()
        self.rocket_state = RocketState.Init


##########################################################################
#    Additional fonts handling
##########################################################################
def load_fonts(app_state: AppState):  # This is called by runnerParams.callbacks.LoadAdditionalFonts
    # First, load the default font (the default font should be loaded first)
    # In this example, we instruct HelloImGui to use FontAwesome6 instead of FontAwesome4
    hello_imgui.get_runner_params().callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
    hello_imgui.imgui_default_settings.load_default_font_with_font_awesome_icons()

    # Load the title font
    app_state.title_font = hello_imgui.load_font("fonts/DroidSans.ttf", 18.0)
    font_loading_params_title_icons = hello_imgui.FontLoadingParams()
    font_loading_params_title_icons.merge_to_last_font = True
    font_loading_params_title_icons.use_full_glyph_range = True
    app_state.title_font = hello_imgui.load_font("fonts/Font_Awesome_6_Free-Solid-900.otf",
                                                 18.0, font_loading_params_title_icons)

    # Load the emoji font
    font_loading_params_emoji = hello_imgui.FontLoadingParams()
    font_loading_params_emoji.use_full_glyph_range = True
    app_state.emoji_font = hello_imgui.load_font("fonts/NotoEmoji-Regular.ttf", 24., font_loading_params_emoji)

    # Load a large icon font
    font_loading_params_large_icon = hello_imgui.FontLoadingParams()
    font_loading_params_large_icon.use_full_glyph_range = True
    app_state.large_icon_font = hello_imgui.load_font("fonts/fontawesome-webfont.ttf", 24., font_loading_params_large_icon)

    # Load a colored font
    font_loading_params_color = hello_imgui.FontLoadingParams()
    font_loading_params_color.load_color = True
    app_state.color_font = hello_imgui.load_font("fonts/Playbox/Playbox-FREE.otf", 24., font_loading_params_color)



##########################################################################
#    Save additional settings in the ini file
##########################################################################
# This demonstrates how to store additional info in the application settings
# Use this sparingly!
# This is provided as a convenience only, and it is not intended to store large quantities of text data.

# Warning, the save/load function below are quite simplistic!
def my_app_settings_to_string(settings: MyAppSettings) -> str:
    as_dict = {}
    as_dict["motto"] = hello_imgui.input_text_data_to_dict(settings.motto)
    as_dict["value"] = settings.value
    return json.dumps(as_dict)


def string_to_my_app_settings(s: str) -> MyAppSettings:
    r = MyAppSettings()
    try:
        as_dict = json.loads(s)
        r.motto = hello_imgui.input_text_data_from_dict(as_dict["motto"])
        r.value = as_dict["value"]
    except Exception as e:
        hello_imgui.log(hello_imgui.LogLevel.error, f"Error while loading user settings: {e}")
    return r


def load_my_app_settings(app_state: AppState):
    """
    Note: load_my_app_settings() and save_my_app_settings() will be called in the callbacks `post_init` & `before_exit`
         runner_params.callbacks.post_init = lambda: load_user_settings(app_state)
         runner_params.callbacks.before_exit = lambda: save_user_settings(app_state)
    """
    app_state.my_app_settings = string_to_my_app_settings(
        hello_imgui.load_user_pref("MyAppSettings")
    )


def save_my_app_settings(app_state: AppState):
    hello_imgui.save_user_pref(
        "MyAppSettings", my_app_settings_to_string(app_state.my_app_settings)
    )


##########################################################################
#    Gui functions used in this demo
##########################################################################
@immapp.static(last_hide_time=1)
def demo_hide_window(app_state: AppState):
    # Display a button that will hide the application window
    imgui.push_font(app_state.title_font)
    imgui.text("Hide app window")
    imgui.pop_font()

    if imgui.button("Hide"):
        demo_hide_window.last_hide_time = time.time()
        hello_imgui.get_runner_params().app_window_params.hidden = True
    if imgui.is_item_hovered():
        imgui.set_tooltip("By clicking this button, you can hide the window for 3 seconds.")
    if demo_hide_window.last_hide_time > 0.0:
        now = time.time()
        if now - demo_hide_window.last_hide_time > 3.0:
            demo_hide_window.last_hide_time = -1.0
            hello_imgui.get_runner_params().app_window_params.hidden = False


# Display a button that will show an additional window
def demo_show_additional_window(app_state: AppState):
    # Notes:
    #     - it is *not* possible to modify the content of the vector runnerParams.dockingParams.dockableWindows
    #       from the code inside a window's `GuiFunction` (since this GuiFunction will be called while iterating
    #       on this vector!)
    #     - there are two ways to dynamically add windows:
    #           * either make them initially invisible, and exclude them from the view menu (such as shown here)
    #           * or modify runnerParams.dockingParams.dockableWindows inside the callback RunnerCallbacks.PreNewFrame
    window_name = "Additional Window"

    imgui.push_font(app_state.title_font)
    imgui.text("Dynamically add window")
    imgui.pop_font()

    if imgui.button("Show additional window"):
        runner_params = hello_imgui.get_runner_params()
        additional_window_ptr = runner_params.docking_params.dockable_window_of_name(
            window_name
        )
        if additional_window_ptr:
            # additional_window_ptr.include_in_view_menu = True
            additional_window_ptr.is_visible = True
    if imgui.is_item_hovered():
        imgui.set_tooltip("By clicking this button, you can show an additional window")


def demo_basic_widgets(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Basic widgets demo")
    imgui.pop_font()

    imgui.begin_group()
    # Edit a float using a slider from 0.0 to 1.0
    changed, app_state.f = imgui.slider_float("float", app_state.f, 0.0, 1.0)
    if changed:
        hello_imgui.log(
            hello_imgui.LogLevel.warning, f"state.f was changed to {app_state.f}"
        )

    # Buttons return true when clicked (most widgets return true when edited/activated)
    if imgui.button("Button"):
        app_state.counter += 1
        hello_imgui.log(hello_imgui.LogLevel.info, "Button was pressed")
    imgui.same_line()
    imgui.text(f"counter = {app_state.counter}")
    imgui.end_group()

    if imgui.is_item_hovered():
        imgui.set_tooltip("These widgets will interact with the log window")


def demo_user_settings(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("User settings")
    imgui.pop_font()

    imgui.begin_group()

    imgui.set_next_item_width(hello_imgui.em_size(7.0))
    _, app_state.my_app_settings.value = imgui.slider_int(
        "Value", app_state.my_app_settings.value, 0, 100
    )

    _ = hello_imgui.input_text_resizable("Motto", app_state.my_app_settings.motto)
    imgui.text("(this text widget is resizable)")

    imgui.end_group()
    if imgui.is_item_hovered():
        imgui.set_tooltip("The values below are stored in the application settings ini file and restored at startup")


def demo_rocket(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Rocket demo")
    imgui.pop_font()

    imgui.begin_group()
    if app_state.rocket_state == RocketState.Init:
        if imgui.button(f"{icons_fontawesome_6.ICON_FA_ROCKET} Launch rocket"):
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
        imgui.text(f"{icons_fontawesome_6.ICON_FA_ROCKET} Rocket launched")
        if imgui.button("Reset Rocket"):
            app_state.rocket_state = RocketState.Init
            app_state.rocket_progress = 0.0
    imgui.end_group()
    if imgui.is_item_hovered():
        imgui.set_tooltip("Look at the status bar after clicking")


def demo_docking_flags(app_state: AppState):
    imgui.push_font(app_state.title_font)
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
        DockFlagWithInfo(
            imgui.DockNodeFlags_.no_docking_split,
            "NoSplit",
            "prevent Dock Nodes from being split",
        ),
        DockFlagWithInfo(
            imgui.DockNodeFlags_.no_resize,
            "NoResize",
            "prevent Dock Nodes from being resized",
        ),
        DockFlagWithInfo(
            imgui.DockNodeFlags_.auto_hide_tab_bar,
            "AutoHideTabBar",
            "show tab bar only if multiple windows\n"
            + 'You will need to restore the layout after changing (Menu "View/Restore Layout")',
        ),
        DockFlagWithInfo(
            imgui.DockNodeFlags_.no_docking_over_central_node,
            "NoDockingInCentralNode",
            "prevent docking in central node\n(only works with the main dock space)",
        ),
        # DockFlagWithInfo(imgui.DockNodeFlags_.passthru_central_node, "PassthruCentralNode", "advanced"),
    ]

    main_dock_space_node_flags = (
        hello_imgui.get_runner_params().docking_params.main_dock_space_node_flags
    )
    for flag_with_info in all_flags:
        _, main_dock_space_node_flags = imgui.checkbox_flags(
            flag_with_info.label, main_dock_space_node_flags, flag_with_info.flag
        )
        if imgui.is_item_hovered():
            imgui.set_tooltip("%s" % flag_with_info.tip)

    hello_imgui.get_runner_params().docking_params.main_dock_space_node_flags = (
        main_dock_space_node_flags
    )


def gui_window_layout_customization(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Switch between layouts")
    imgui.pop_font()
    imgui.text('with the menu "View/Layouts"')
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            "Each layout remembers separately the modifications applied by the user, \n"
            + "and the selected layout is restored at startup"
        )

    imgui.separator()

    imgui.push_font(app_state.title_font)
    imgui.text("Change the theme")
    imgui.pop_font()
    imgui.text('with the menu "View/Theme"')
    if imgui.is_item_hovered():
        imgui.set_tooltip("The selected theme is remembered and restored at startup")
    imgui.separator()

    demo_docking_flags(app_state)
    imgui.separator()


def gui_window_alternative_theme(app_state: AppState):
    # Since this window applies a theme, We need to call "imgui.begin" ourselves so
    # that we can apply the theme before opening the window.
    #
    # In order to obtain this, we applied the following option to the window
    # that displays this Gui:
    #     alternative_theme_window.call_begin_end = False

    # emulate C/C++ static variable: we will store some static variables
    # as attributes of the function
    statics = gui_window_alternative_theme

    # Apply the theme before opening the window
    tweaked_theme = hello_imgui.ImGuiTweakedTheme()
    tweaked_theme.theme = hello_imgui.ImGuiTheme_.white_is_white
    tweaked_theme.tweaks.rounding = 0.0
    hello_imgui.push_tweaked_theme(tweaked_theme)

    # Open the window
    window_opened = imgui.begin("Alternative Theme")
    if window_opened:
        # Display some widgets
        imgui.push_font(app_state.title_font)
        imgui.text("Alternative Theme")
        imgui.pop_font()
        imgui.text("This window uses a different theme")
        imgui.set_item_tooltip("""
            tweaked_theme = hello_imgui.ImGuiTheme.ImGuiTweakedTheme()
            tweaked_theme.theme = hello_imgui.ImGuiTheme_.white_is_white.value
            tweaked_theme.tweaks.rounding = 0.0
            hello_imgui.apply_tweaked_theme(tweaked_theme)
        """
        )

        if imgui.collapsing_header("Basic Widgets", imgui.TreeNodeFlags_.default_open.value):
            if not hasattr(statics, "checked"):
                statics.checked = True
            _, statics.checked = imgui.checkbox("Checkbox", statics.checked)

            if imgui.button("Button"):
                hello_imgui.log(hello_imgui.LogLevel.info, "Button was pressed")
            imgui.set_item_tooltip("This is a button")

            if not hasattr(statics, "radio"):
                statics.radio = 0
            if imgui.radio_button("Radio 1", statics.radio == 0):
                statics.radio = 0
            imgui.same_line()
            if imgui.radio_button("Radio 2", statics.radio == 1):
                statics.radio = 1
            imgui.same_line()
            if imgui.radio_button("Radio 3", statics.radio == 2):
                statics.radio = 2

            # Haiku
            # Display a image of the haiku below with Japanese characters
            # with an informative tooltip
            haiku_image_height = hello_imgui.em_size(5.0)
            hello_imgui.image_from_asset("images/haiku.png", ImVec2(0.0, haiku_image_height))
            imgui.set_item_tooltip("""
Extract from Wikipedia
-------------------------------------------------------------------------------

In early 1686, Bashō composed one of his best-remembered haiku:

        furu ike ya / kawazu tobikomu / mizu no oto

   an ancient pond / a frog jumps in / the splash of water

This poem became instantly famous.

-------------------------------------------------------------------------------

This haiku is here rendered as an image, mainly to preserve space,
because adding a Japanese font to the project would enlarge its size.
Handling Japanese font is of course possible within ImGui / Hello ImGui!
            """)

            # Display the haiku text as an InputTextMultiline
            if not hasattr(statics, "poem"):
                statics.poem = (
                    "   Old Pond\n"
                    "  Frog Leaps In\n"
                    " Water's Sound\n"
                    "\n"
                    "      Matsuo Bashō - 1686"
                )

            _, statics.poem = imgui.input_text_multiline("##Poem", statics.poem, hello_imgui.em_to_vec2(15.0, 5.5))

            # a popup with a modal window
            if imgui.button("Open Modal"):
                imgui.open_popup("MyModal")
            popup_opened, _ = imgui.begin_popup_modal("MyModal", None, imgui.WindowFlags_.always_auto_resize.value)
            if popup_opened:
                imgui.text("This is a modal window")
                if imgui.button("Close"):
                    imgui.close_current_popup()
                imgui.end_popup()

            if not hasattr(statics, "text"):
                statics.text = "Hello, world!"
            _, statics.text = imgui.input_text("Input text", statics.text)

            if imgui.tree_node("Text Display"):
                imgui.text("Hello, world!")
                imgui.text_colored(ImVec4(1.0, 0.5, 0.5, 1.0), "Some text")
                imgui.text_disabled("Disabled text")
                imgui.text_wrapped("This is a long text that will be wrapped in the window")
                imgui.tree_pop()

    # Close the window
    imgui.end()

    # Restore the theme
    hello_imgui.pop_tweaked_theme()


def demo_assets(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Image From Assets")
    imgui.pop_font()
    hello_imgui.begin_group_column()
    imgui.dummy(hello_imgui.em_to_vec2(0.0, 0.45))
    imgui.text("Hello")
    hello_imgui.end_group_column()
    hello_imgui.image_from_asset("images/world.png", hello_imgui.em_to_vec2(2.5, 2.5))


def demo_fonts(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Fonts - " + icons_fontawesome_6.ICON_FA_PEN_NIB)
    imgui.pop_font()

    imgui.text_wrapped("Mix icons " + icons_fontawesome_6.ICON_FA_FACE_SMILE + " and text " + icons_fontawesome_6.ICON_FA_ROCKET)
    if imgui.is_item_hovered():
        imgui.set_tooltip("Example with Font Awesome Icons")

    imgui.text("Emojis")

    with imgui_ctx.begin_group():
        imgui.push_font(app_state.emoji_font)
        # ✌️ (Victory Hand Emoji)
        imgui.text("\U0000270C\U0000FE0F")
        imgui.same_line()

        # ❤️ (Red Heart Emoji)
        imgui.text("\U00002764\U0000FE0F")
        imgui.same_line()

        # 🌴 (Palm Tree Emoji)
        imgui.text("\U0001F334")
        imgui.same_line()

        # 🚀 (Rocket Emoji)
        imgui.text("\U0001F680")
        imgui.pop_font()

    if imgui.is_item_hovered():
        imgui.set_tooltip("Example with NotoEmoji font")

    imgui.text("Colored Fonts")
    imgui.push_font(app_state.color_font)
    imgui.text("C O L O R !")
    imgui.pop_font()
    if imgui.is_item_hovered():
        imgui.set_tooltip("Example with Playbox-FREE.otf font")


def demo_themes(app_state: AppState):
    imgui.push_font(app_state.title_font)
    imgui.text("Themes")
    imgui.pop_font()

    tweaked_theme = hello_imgui.get_runner_params().imgui_window_params.tweaked_theme

    imgui.begin_group()
    button_size = hello_imgui.em_to_vec2(7.0, 0.0)
    if imgui.button("Cherry", button_size):
        tweaked_theme.theme = hello_imgui.ImGuiTheme_.cherry
        hello_imgui.apply_tweaked_theme(tweaked_theme)
    if imgui.button("DarculaDarker", button_size):
        tweaked_theme.theme = hello_imgui.ImGuiTheme_.darcula_darker
        hello_imgui.apply_tweaked_theme(tweaked_theme)
    imgui.end_group()
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            "There are lots of other themes: look at the menu View/Theme\n"
            "The selected theme is remembered and restored at startup"
        )


def gui_window_demo_features(app_state: AppState):
    demo_fonts(app_state)
    imgui.separator()
    demo_assets(app_state)
    imgui.separator()
    demo_basic_widgets(app_state)
    imgui.separator()
    demo_rocket(app_state)
    imgui.separator()
    demo_user_settings(app_state)
    imgui.separator()
    demo_hide_window(app_state)
    imgui.separator()
    demo_show_additional_window(app_state)
    imgui.separator()
    demo_themes(app_state)
    imgui.separator()


def status_bar_gui(app_state: AppState):
    if app_state.rocket_state == RocketState.Preparing:
        imgui.text("Rocket completion: ")
        imgui.same_line()
        imgui.progress_bar(app_state.rocket_progress, hello_imgui.em_to_vec2(7.0, 1.0))  # type: ignore


def show_menu_gui(runner_params: hello_imgui.RunnerParams):
    hello_imgui.show_app_menu(runner_params)
    hello_imgui.show_view_menu(runner_params)
    if imgui.begin_menu("My Menu"):
        clicked, _ = imgui.menu_item("Test me", "", False)
        if clicked:
            hello_imgui.log(hello_imgui.LogLevel.warning, "It works")
        imgui.end_menu()


def show_app_menu_items():
    clicked, _ = imgui.menu_item("A Custom app menu item", "", False)
    if clicked:
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on A Custom app menu item")


def show_top_toolbar(app_state: AppState):
    imgui.push_font(app_state.large_icon_font)
    if imgui.button(icons_fontawesome_6.ICON_FA_POWER_OFF):
        hello_imgui.get_runner_params().app_shall_exit = True

    imgui.same_line(imgui.get_window_width() - hello_imgui.em_size(7.0))
    if imgui.button(icons_fontawesome_6.ICON_FA_HOUSE):
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on Home in the top toolbar")
    imgui.same_line()
    if imgui.button(icons_fontawesome_6.ICON_FA_FLOPPY_DISK):
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on Save in the top toolbar")
    imgui.same_line()
    if imgui.button(icons_fontawesome_6.ICON_FA_ADDRESS_BOOK):
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on Address Book in the top toolbar")

    imgui.same_line(imgui.get_window_width() - hello_imgui.em_size(2.0))
    imgui.text(icons_fontawesome_6.ICON_FA_BATTERY_THREE_QUARTERS)
    imgui.pop_font()


def show_right_toolbar(app_state: AppState):
    imgui.push_font(app_state.large_icon_font)
    if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_ARROW_LEFT):
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on Circle left in the right toolbar")
    if imgui.button(icons_fontawesome_6.ICON_FA_CIRCLE_ARROW_RIGHT):
        hello_imgui.log(hello_imgui.LogLevel.info, "Clicked on Circle right in the right toolbar")
    imgui.pop_font()


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
    #    |------- |                                |
    #    |        |--------------------------------|
    #    |        |       CommandSpace2            |
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
    split_main_misc.direction = imgui.Dir.down
    split_main_misc.ratio = 0.25

    # Then, add a space to the left which occupies a column whose width is 25% of the app width
    split_main_command = hello_imgui.DockingSplit()
    split_main_command.initial_dock = "MainDockSpace"
    split_main_command.new_dock = "CommandSpace"
    split_main_command.direction = imgui.Dir.left
    split_main_command.ratio = 0.25

    # Then, add CommandSpace2 below MainDockSpace
    split_main_command2 = hello_imgui.DockingSplit()
    split_main_command2.initial_dock = "MainDockSpace"
    split_main_command2.new_dock = "CommandSpace2"
    split_main_command2.direction = imgui.Dir.down
    split_main_command2.ratio = 0.5

    splits = [split_main_misc, split_main_command, split_main_command2]
    return splits


def create_alternative_docking_splits() -> List[hello_imgui.DockingSplit]:
    # Define alternative docking splits for the "Alternative Layout"
    #    ___________________________________________
    #    |                |                        |
    #    | Misc           |                        |
    #    | Space          |    MainDockSpace       |
    #    |                |                        |
    #    -------------------------------------------
    #    |                       |                 |
    #    |                       | Command         |
    #    |     CommandSpace      | Space2          |
    #    -------------------------------------------

    split_main_command = hello_imgui.DockingSplit()
    split_main_command.initial_dock = "MainDockSpace"
    split_main_command.new_dock = "CommandSpace"
    split_main_command.direction = imgui.Dir.down
    split_main_command.ratio = 0.5

    split_main_command2 = hello_imgui.DockingSplit()
    split_main_command2.initial_dock = "CommandSpace"
    split_main_command2.new_dock = "CommandSpace2"
    split_main_command2.direction = imgui.Dir.right
    split_main_command2.ratio = 0.4

    split_main_misc = hello_imgui.DockingSplit()
    split_main_misc.initial_dock = "MainDockSpace"
    split_main_misc.new_dock = "MiscSpace"
    split_main_misc.direction = imgui.Dir.left
    split_main_misc.ratio = 0.5

    splits = [split_main_command, split_main_command2, split_main_misc]
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
    layout_customization_window.gui_function = lambda: gui_window_layout_customization(app_state)

    # A Log window named "Logs" will be placed in "MiscSpace". It uses the HelloImGui logger gui
    logs_window = hello_imgui.DockableWindow()
    logs_window.label = "Logs"
    logs_window.dock_space_name = "MiscSpace"
    logs_window.gui_function = hello_imgui.log_gui

    # A Window named "Dear ImGui Demo" will be placed in "MainDockSpace"
    dear_imgui_demo_window = hello_imgui.DockableWindow()
    dear_imgui_demo_window.label = "Dear ImGui Demo"
    dear_imgui_demo_window.dock_space_name = "MainDockSpace"
    dear_imgui_demo_window.imgui_window_flags = imgui.WindowFlags_.menu_bar
    dear_imgui_demo_window.gui_function = imgui.show_demo_window  # type: ignore

    # additional_window is initially not visible (and not mentioned in the view menu).
    # it will be opened only if the user chooses to display it
    additional_window = hello_imgui.DockableWindow()
    additional_window.label = "Additional Window"
    additional_window.is_visible = False  # this window is initially hidden,
    additional_window.include_in_view_menu = False  # it is not shown in the view menu,
    additional_window.remember_is_visible = (
        False  # its visibility is not saved in the settings file,
    )
    additional_window.dock_space_name = (
        "MiscSpace"  # when shown, it will appear in MiscSpace.
    )
    additional_window.gui_function = lambda: imgui.text("This is the additional window")

    # alternativeThemeWindow
    alternative_theme_window = hello_imgui.DockableWindow()
    # Since this window applies a theme, We need to call "imgui.begin" ourselves so
    # that we can apply the theme before opening the window.
    alternative_theme_window.call_begin_end = False
    alternative_theme_window.label = "Alternative Theme"
    alternative_theme_window.dock_space_name = "CommandSpace2"
    alternative_theme_window.gui_function = lambda: gui_window_alternative_theme(app_state)

    dockable_windows = [
        features_demo_window,
        layout_customization_window,
        logs_window,
        dear_imgui_demo_window,
        additional_window,
        alternative_theme_window,
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
    runner_params.app_window_params.window_title = "Docking Demo"
    runner_params.imgui_window_params.menu_app_title = "Docking Demo"
    runner_params.app_window_params.window_geometry.size = (1000, 900)
    runner_params.app_window_params.restore_previous_geometry = True
    runner_params.app_window_params.borderless = True
    runner_params.app_window_params.borderless_movable = True
    runner_params.app_window_params.borderless_resizable = True
    runner_params.app_window_params.borderless_closable = True

    # Set LoadAdditionalFonts callback
    runner_params.callbacks.load_additional_fonts = lambda: load_fonts(app_state)

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
    # Here, we fully customize the menu bar:
    # by setting `show_menu_bar` to True, and `show_menu_app` and `show_menu_view` to False,
    # HelloImGui will display an empty menu bar, which we can fill with our own menu items via the callback `show_menus`
    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.imgui_window_params.show_menu_app = False
    runner_params.imgui_window_params.show_menu_view = False
    # Inside `show_menus`, we can call `hello_imgui.show_view_menu` and `hello_imgui.show_app_menu` if desired
    runner_params.callbacks.show_menus = lambda: show_menu_gui(runner_params)
    # Optional: add items to Hello ImGui default App menu
    runner_params.callbacks.show_app_menu_items = show_app_menu_items

    #
    # Top and bottom toolbars
    #
    # toolbar options
    edge_toolbar_options = hello_imgui.EdgeToolbarOptions()
    edge_toolbar_options.size_em = 2.5
    edge_toolbar_options.window_bg = ImVec4(0.8, 0.8, 0.8, 0.35)
    # top toolbar
    runner_params.callbacks.add_edge_toolbar(
        hello_imgui.EdgeToolbarType.top,
        lambda: show_top_toolbar(app_state),
        edge_toolbar_options,
    )
    # right toolbar
    edge_toolbar_options.window_bg.w = 0.4
    runner_params.callbacks.add_edge_toolbar(
        hello_imgui.EdgeToolbarType.right,
        lambda: show_right_toolbar(app_state),
        edge_toolbar_options,
    )

    #
    # Load user settings at callbacks `post_init` and save them at `before_exit`
    #
    runner_params.callbacks.post_init = lambda: load_my_app_settings(app_state)
    runner_params.callbacks.before_exit = lambda: save_my_app_settings(app_state)

    #
    # Change style
    #
    # 1. Change theme
    tweaked_theme = runner_params.imgui_window_params.tweaked_theme
    tweaked_theme.theme = hello_imgui.ImGuiTheme_.material_flat
    tweaked_theme.tweaks.rounding = 10.0
    # 2. Customize ImGui style at startup
    def setup_imgui_style():
        # Reduce spacing between items ((8, 4) by default)
        imgui.get_style().item_spacing = (6, 4)
    runner_params.callbacks.setup_imgui_style = setup_imgui_style

    #
    # Part 2: Define the application layout and windows
    #

    # First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    # In this demo, we also demonstrate multiple viewports: you can drag windows outside
    # out the main window in order to put their content into new native windows
    runner_params.imgui_window_params.enable_viewports = True
    # Set the default layout (this contains the default DockingSplits and DockableWindows)
    runner_params.docking_params = create_default_layout(app_state)
    # Add alternative layouts
    runner_params.alternative_docking_layouts = create_alternative_layouts(app_state)

    #
    # Part 3: Where to save the app settings
    #
    # tag::app_settings[]
    # By default, HelloImGui will save the settings in the current folder.
    # This is convenient when developing, but not so much when deploying the app.
    # You can tell HelloImGui to save the settings in a specific folder: choose between
    #         current_folder
    #         app_user_config_folder
    #         app_executable_folder
    #         home_folder
    #         temp_folder
    #         documents_folder
    #
    # Note: app_user_config_folder is:
    #         AppData under Windows (Example: C:\Users\[Username]\AppData\Roaming)
    #         ~/.config under Linux
    #         "~/Library/Application Support" under macOS or iOS
    runner_params.ini_folder_type = hello_imgui.IniFolderType.app_user_config_folder

    # runnerParams.ini_filename: this will be the name of the ini file in which the settings
    # will be stored.
    # In this example, the subdirectory Docking_Demo will be created under the folder defined
    # by runnerParams.ini_folder_type.
    #
    # Note: if ini_filename is left empty, the name of the ini file will be derived
    # from app_window_params.window_title
    runner_params.ini_filename = "Docking_Demo/Docking_demo.ini"
    # end::app_settings[]

    #
    # Part 4: Run the app
    #
    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
