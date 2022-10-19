import os
from typing import List, Callable

from imgui_bundle import hello_imgui, icons_fontawesome, imgui, ImguiNodeEditorContextHolder, ImplotContextHolder
from imgui_bundle import imgui_color_text_edit, imgui_node_editor

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


def demo_implot():
    from demo_implot import demo_drag_rects

    demo_drag_rects()


def demo_node_editor():
    from demo_node_editor import DemoNodeEditor

    if not hasattr(demo_node_editor, "demo_class"):
        demo_node_editor.demo = DemoNodeEditor()
    demo_node_editor.demo.on_frame()


def demo_spinner():
    from imgui_bundle import imspinner

    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    imspinner.spinner_moving_dots("spinner_moving_dots", 3.0, color, 28.0)
    imgui.same_line()
    imspinner.spinner_arc_rotation("spinner_arc_rotation", 10.0, 4.0, color)
    imgui.same_line()
    imspinner.spinner_ang_triple("spinner_arc_fade", 5.0, 8.0, 11.0, 2.5, color, color, color)



def main():
    ################################################################################################
    # Part 1: Define the application state, fill the status and menu bars, and load additional font
    ################################################################################################

    # Our application state
    app_state = AppState()
    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Docking demo"
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

    # Then, add a space named "BottomSpace" whose height is 25% of the app height.
    # This will split the preexisting default dockspace "MainDockSpace" in two parts.
    split_main_bottom = hello_imgui.DockingSplit()
    split_main_bottom.initial_dock = "MainDockSpace"
    split_main_bottom.new_dock = "BottomSpace"
    split_main_bottom.direction = imgui.ImGuiDir_.down
    split_main_bottom.ratio = 0.25

    runner_params.docking_params.docking_splits = [split_main_bottom]

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
        print("a")

    add_dockable_window("Logs", hello_imgui.log_gui, "BottomSpace")
    add_dockable_window("Dear ImGui Demo", imgui.show_demo_window)
    add_dockable_window("Editor demo", lambda: demo_editor_gui(app_state))
    add_dockable_window("Knobs", lambda: demo_knobs)
    add_dockable_window("File dialog", lambda: demo_file_dialog)
    add_dockable_window("Implot", demo_implot)
    add_dockable_window("Node Editor", demo_node_editor)
    add_dockable_window("Spinner", demo_spinner)

    runner_params.docking_params.dockable_windows = dockable_windows


    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    hello_imgui.run(runner_params)


if __name__ == "__main__":

    config = imgui_node_editor.Config()
    config.settings_file = "BasicInteraction.json"
    ImguiNodeEditorContextHolder.start(config)

    ImplotContextHolder.start()

    main()
