import os
from enum import Enum

from imgui_bundle import hello_imgui, icons_fontawesome, imgui
from imgui_bundle import imgui_color_text_edit

TextEditor = imgui_color_text_edit.TextEditor

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Important: HelloImGui uses an assets dir where it can find assets (fonts, images, etc.)
#
# By default an assets folder is installed via pip inside site-packages/imgui_bundle/assets
# and provides two fonts (fonts/DroidSans.ttf and fonts/fontawesome-webfont.ttf)
# If you need to add more assets, make a copy of this assets folder and add your own files, and call set_assets_folder
hello_imgui.set_assets_folder(THIS_DIR + "/assets")


# Struct that holds the application's state
class AppState:
    f: float = 0.0
    counter: int = 0
    rocket_progress: float = 0.0
    text_editor: TextEditor
    knob_int_value: int = 0
    knob_value: float = 0.0
    file_dialog_selection: str = ""

    def __init__(self):
        with open(__file__) as f:
            this_file_code = f.read()
        self.text_editor = TextEditor()
        self.text_editor.set_text(this_file_code)
        self.text_editor.set_language_definition(TextEditor.LanguageDefinition.c())

    class RocketState(Enum):
        Init = 0
        Preparing = 1
        Launched = 2

    rocket_state: RocketState = RocketState.Init


def demo_editor_gui(app_state: AppState):
    imgui.text("This editor is provided by ImGuiColorTextEdit (https://github.com/BalazsJako/ImGuiColorTextEdit)")
    imgui.text("It is able to colorize C, C++, hlsl, Sql, angel_script and lua code")

    editor = app_state.text_editor

    def show_palette_buttons():
        if imgui.small_button("Dark palette"):
            editor.set_palette(TextEditor.get_dark_palette())
        imgui.same_line()
        if imgui.small_button("Light palette"):
            editor.set_palette(TextEditor.get_light_palette())
        imgui.same_line()
        if imgui.small_button("Retro blue palette"):
            editor.set_palette(TextEditor.get_retro_blue_palette())

    show_palette_buttons()
    editor.render("Code")


def demo_knobs(app_state: AppState):
    from imgui_bundle import imgui_knobs

    knob_types = {
        "tick": imgui_knobs.ImGuiKnobVariant_.tick,
        "dot": imgui_knobs.ImGuiKnobVariant_.dot,
        "space": imgui_knobs.ImGuiKnobVariant_.space,
        "stepped": imgui_knobs.ImGuiKnobVariant_.stepped,
        "wiper": imgui_knobs.ImGuiKnobVariant_.wiper,
        "wiper_dot": imgui_knobs.ImGuiKnobVariant_.wiper_dot,
        "wiper_only": imgui_knobs.ImGuiKnobVariant_.wiper_only,
    }

    def show_float_knobs(knob_size: float):
        imgui.push_id(f"{knob_size}_float")
        for knob_typename, knob_type in knob_types.items():
            changed, app_state.knob_value = imgui_knobs.knob(
                knob_typename,
                p_value=app_state.knob_value,
                v_min=0.0,
                v_max=1.0,
                speed=0,
                variant=knob_type,
                steps=10,
                size=knob_size,
            )
            imgui.same_line()
        imgui.new_line()
        imgui.pop_id()

    def show_int_knobs(knob_size: float):
        imgui.push_id(f"{knob_size}_int")
        for knob_typename, knob_type in knob_types.items():
            changed, app_state.knob_int_value = imgui_knobs.knob_int(
                knob_typename,
                p_value=app_state.knob_int_value,
                v_min=0,
                v_max=10,
                speed=0,
                variant=knob_type,
                steps=10,
                size=knob_size,
            )
            imgui.same_line()
        imgui.new_line()
        imgui.pop_id()

    imgui.text("Some small knobs")
    show_float_knobs(40.0)
    imgui.separator()
    imgui.text("Some knobs on integer value")
    show_int_knobs(60.0)
    imgui.separator()
    imgui.text("Some big knobs")
    show_float_knobs(70.0)


def demo_file_dialog(app_state: AppState):
    from imgui_bundle import im_file_dialog as ifd

    if imgui.button("Open file"):
        ifd.FileDialog.instance().open(
            "ShaderOpenDialog",
            "Open a shader",
            "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
            True,
        )
    if imgui.button("Open directory"):
        ifd.FileDialog.instance().open("DirectoryOpenDialog", "Open a directory", "")
    if imgui.button("Save file"):
        ifd.FileDialog.instance().save("ShaderSaveDialog", "Save a shader", "*.sprj .sprj")
    if len(app_state.file_dialog_selection) > 0:
        imgui.text(f"Last file selection:\n  {app_state.file_dialog_selection}")

    # file dialogs
    if ifd.FileDialog.instance().is_done("ShaderOpenDialog"):
        if ifd.FileDialog.instance().has_result():
            # get_results: plural form - ShaderOpenDialog supports multi-selection
            res = ifd.FileDialog.instance().get_results()
            filenames = [f.path() for f in res]
            app_state.file_dialog_selection = "\n  ".join(filenames)

        ifd.FileDialog.instance().close()

    if ifd.FileDialog.instance().is_done("DirectoryOpenDialog"):
        if ifd.FileDialog.instance().has_result():
            app_state.file_dialog_selection = ifd.FileDialog.instance().get_result().path()

        ifd.FileDialog.instance().close()

    if ifd.FileDialog.instance().is_done("ShaderSaveDialog"):
        if ifd.FileDialog.instance().has_result():
            app_state.file_dialog_selection = ifd.FileDialog.instance().get_result().path()

        ifd.FileDialog.instance().close()


# MyLoadFonts: demonstrate
# * how to load additional fonts
# * how to use assets from the local assets/ folder
gAkronimFont: imgui.ImFont = None


def my_load_fonts():
    global gAkronimFont
    # First, we load the default fonts (the font that was loaded first is the default font)
    hello_imgui.ImGuiDefaultSettings.load_default_font_with_font_awesome_icons()
    # HelloImGui::ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons();  # issue / embedded namespace

    # Then we load a second font from
    # Since this font is in a local assets/ folder, it was embedded automatically
    font_filename = "fonts/Akronim-Regular.ttf"
    gAkronimFont = hello_imgui.load_font_ttf_with_font_awesome_icons(font_filename, 40.0)


# CommandGui: the widgets on the left panel
def command_gui(state: AppState):
    imgui.push_font(gAkronimFont)
    imgui.text("Hello  " + icons_fontawesome.ICON_FA_SMILE)
    hello_imgui.image_from_asset("world.jpg")
    imgui.pop_font()
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            """
        The custom font and the globe image below were loaded
        from the application assets folder
        (those files are embedded automatically).
        """
        )

    imgui.separator()

    # Edit 1 float using a slider from 0.0f to 1.0f
    changed, state.f = imgui.slider_float("float", state.f, 0.0, 1.0)
    if changed:
        hello_imgui.log(hello_imgui.LogLevel.warning, f"state.f was changed to {state.f}")

    # Buttons return true when clicked (most widgets return true when edited/activated)
    if imgui.button("Button"):
        state.counter += 1
        hello_imgui.log(hello_imgui.LogLevel.info, "Button was pressed")

    imgui.same_line()
    imgui.text(f"counter = {state.counter}")

    if state.rocket_state == AppState.RocketState.Init:
        if imgui.button(icons_fontawesome.ICON_FA_ROCKET + " Launch rocket"):
            state.rocket_state = AppState.RocketState.Preparing
            hello_imgui.log(hello_imgui.LogLevel.warning, "Rocket is being prepared")
    elif state.rocket_state == AppState.RocketState.Preparing:
        imgui.text("Please Wait")
        state.rocket_progress += 0.003
        if state.rocket_progress >= 1.0:
            state.rocket_state = AppState.RocketState.Launched
            print("Rocket was launched!")
            hello_imgui.log(hello_imgui.LogLevel.warning, "Rocker was launched")
    elif state.rocket_state == AppState.RocketState.Launched:
        imgui.text(icons_fontawesome.ICON_FA_ROCKET + " Rocket Launched")
        if imgui.button("Reset Rocket"):
            state.rocket_state = AppState.RocketState.Init
            state.rocket_progress = 0.0


# Our Gui in the status bar
def status_bar_gui(app_state: AppState):
    if app_state.rocket_state == AppState.RocketState.Preparing:
        imgui.text("Rocket completion: ")
        imgui.same_line()
        imgui.progress_bar(app_state.rocket_progress, imgui.ImVec2(100.0, 15.0))


def main():
    ################################################################################################
    # Part 1: Define the application state, fill the status and menu bars, and load additional font
    ################################################################################################

    # Our application state
    app_state = AppState()

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()

    runner_params.app_window_params.window_title = "Docking demo"

    #
    # Status bar
    #
    # We use the default status bar of Hello ImGui
    runner_params.imgui_window_params.show_status_bar = True
    # uncomment next line in order to hide the FPS in the status bar
    # runner_params.im_gui_window_params.show_status_fps = False
    runner_params.callbacks.show_status = lambda: status_bar_gui(app_state)

    #
    # Menu bar
    #
    # We use the default menu of Hello ImGui, to which we add some more items
    runner_params.imgui_window_params.show_menu_bar = True

    def show_menu_gui():
        if imgui.begin_menu("My Menu"):
            if imgui.menu_item("Test me"):
                print("It works")
                # logger.warning("It works")
            imgui.end_menu()

    runner_params.callbacks.show_menus = show_menu_gui

    # Custom load fonts
    runner_params.callbacks.load_additional_fonts = my_load_fonts

    # optional native events handling
    # runner_params.callbacks.any_backend_event_callback = ...

    ################################################################################################
    # Part 2: Define the application layout and windows
    ################################################################################################

    #
    #    2.1 Define the docking splits,
    #    i.e. the way the screen space is split in different target zones for the dockable windows
    #     We want to split "MainDockSpace" (which is provided automatically) into three zones, like this:
    #
    #    ___________________________________________
    #    |        |                                |
    #    | Left   |                                |
    #    | Space  |    MainDockSpace               |
    #    |        |                                |
    #    |        |                                |
    #    |        |                                |
    #    -------------------------------------------
    #    |     BottomSpace                         |
    #    -------------------------------------------
    #

    # First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    # In this demo, we also demonstrate multiple viewports.
    # you can drag windows outside out the main window in order to put their content into new native windows
    runner_params.imgui_window_params.enable_viewports = True

    # Then, add a space named "BottomSpace" whose height is 25% of the app height.
    # This will split the preexisting default dockspace "MainDockSpace" in two parts.
    split_main_bottom = hello_imgui.DockingSplit()
    split_main_bottom.initial_dock = "MainDockSpace"
    split_main_bottom.new_dock = "BottomSpace"
    split_main_bottom.direction = imgui.ImGuiDir_.down
    split_main_bottom.ratio = 0.25

    # Then, add a space to the left which occupies a column whose width is 25% of the app width
    split_main_left = hello_imgui.DockingSplit()
    split_main_left.initial_dock = "MainDockSpace"
    split_main_left.new_dock = "LeftSpace"
    split_main_left.direction = imgui.ImGuiDir_.left
    split_main_left.ratio = 0.25

    # Finally, transmit these splits to HelloImGui
    runner_params.docking_params.docking_splits = [split_main_bottom, split_main_left]

    #
    # 2.1 Define our dockable windows : each window provide a Gui callback, and will be displayed
    #     in a docking split.
    #

    # A Command panel named "Commands" will be placed in "LeftSpace". Its Gui is provided calls "CommandGui"
    commands_window = hello_imgui.DockableWindow()
    commands_window.label = "Commands"
    commands_window.dock_space_name = "LeftSpace"
    commands_window.gui_function = lambda: command_gui(app_state)
    # A Log  window named "Logs" will be placed in "BottomSpace". It uses the HelloImGui logger gui
    logs_window = hello_imgui.DockableWindow()
    logs_window.label = "Logs"
    logs_window.dock_space_name = "BottomSpace"
    logs_window.gui_function = hello_imgui.log_gui
    # A Window named "Dear ImGui Demo" will be placed in "MainDockSpace"
    dear_imgui_demo_window = hello_imgui.DockableWindow()
    dear_imgui_demo_window.label = "Dear ImGui Demo"
    dear_imgui_demo_window.dock_space_name = "MainDockSpace"
    dear_imgui_demo_window.gui_function = imgui.show_demo_window
    # A window that demonstrate the colored text editor (ImGuiColorTextEdit)
    # (https://github.com/BalazsJako/ImGuiColorTextEdit)
    editor_window = hello_imgui.DockableWindow()
    editor_window.label = "Code for this demo"
    editor_window.dock_space_name = "MainDockSpace"
    editor_window.gui_function = lambda: demo_editor_gui(app_state)
    # A window that demonstrate knobs
    # (https://github.com/altschuler/imgui-knobs)
    knobs_window = hello_imgui.DockableWindow()
    knobs_window.label = "Knobs"
    knobs_window.dock_space_name = "MainDockSpace"
    knobs_window.gui_function = lambda: demo_knobs(app_state)
    # A window that demonstrate ImFileDialog
    # (https://github.com/dfranx/ImFileDialog)
    file_dialog_window = hello_imgui.DockableWindow()
    file_dialog_window.label = "File Dialog"
    file_dialog_window.dock_space_name = "MainDockSpace"
    file_dialog_window.gui_function = lambda: demo_file_dialog(app_state)

    # Finally, transmit these windows to HelloImGui
    runner_params.docking_params.dockable_windows = [
        commands_window,
        logs_window,
        dear_imgui_demo_window,
        editor_window,
        knobs_window,
        file_dialog_window,
    ]

    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
