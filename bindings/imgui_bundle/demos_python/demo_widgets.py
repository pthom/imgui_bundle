# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List
from imgui_bundle import (
    imgui,
    hello_imgui,
    imgui_md,
    imgui_toggle,
    ImVec2,
    immapp,
    ImVec4,
    im_cool_bar,
)
from imgui_bundle import imgui_command_palette as imcmd
from imgui_bundle import portable_file_dialogs as pfd


@immapp.static(knob_float_value=0, knob_int_value=0)
def demo_knobs():
    static = demo_knobs
    from imgui_bundle import imgui_knobs

    imgui_md.render(
        """
# Knobs
  [imgui-knobs](https://github.com/altschuler/imgui-knobs) provides knobs for ImGui."""
    )
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
            changed, static.knob_float_value = imgui_knobs.knob(
                knob_typename,
                p_value=static.knob_float_value,
                v_min=0.0,
                v_max=1.0,
                speed=0,
                format="%.2f",
                variant=knob_type,
                size=knob_size,
                flags=0,
                steps=100,
            )
            imgui.same_line()
        imgui.new_line()
        imgui.pop_id()

    def show_int_knobs(knob_size: float):
        imgui.push_id(f"{knob_size}_int")
        for knob_typename, knob_type in knob_types.items():
            changed, static.knob_int_value = imgui_knobs.knob_int(
                knob_typename,
                p_value=static.knob_int_value,
                v_min=0,
                v_max=15,
                speed=0,
                format="%02i",
                variant=knob_type,
                steps=10,
                size=knob_size,
            )
            imgui.same_line()
        imgui.new_line()
        imgui.pop_id()

    knobs_size_small = immapp.em_size() * 2.5
    knobs_size_big = knobs_size_small * 1.3

    imgui.begin_group()
    imgui.text("Some small knobs")
    show_float_knobs(knobs_size_small)
    imgui.end_group()

    imgui.same_line()

    imgui.begin_group()
    imgui.text("Some big knobs (int values)")
    show_int_knobs(knobs_size_big)
    imgui.end_group()


def demo_spinner():
    from imgui_bundle import imspinner

    imgui_md.render(
        """
# Spinners
  [imspinner](https://github.com/dalerank/imspinner) provides spinners for ImGui."""
    )

    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    imgui.text("spinner_moving_dots")
    imgui.same_line()
    imspinner.spinner_moving_dots("spinner_moving_dots", 20.0, 4.0, color, 20)
    imgui.same_line()

    radius = imgui.get_font_size() / 1.8
    imgui.text("spinner_arc_rotation")
    imgui.same_line()
    imspinner.spinner_arc_rotation("spinner_arc_rotation", radius, 4.0, color)
    imgui.same_line()

    radius1 = imgui.get_font_size() / 2.5
    imgui.text("spinner_ang_triple")
    imgui.same_line()
    imspinner.spinner_ang_triple(
        "spinner_ang_triple",
        radius1,
        radius1 * 1.5,
        radius1 * 2.0,
        2.5,
        color,
        color,
        color,
    )


@immapp.static(flag=True)
def demo_toggle():
    static = demo_toggle
    imgui_md.render_unindented(
        """
        # Toggle Switch
          [imgui_toggle](https://github.com/cmdwtf/imgui_toggle) provides toggle switches for ImGui."""
    )

    _changed, static.flag = imgui_toggle.toggle("Default Toggle", static.flag)
    imgui.same_line()

    _changed, static.flag = imgui_toggle.toggle(
        "Animated Toggle", static.flag, imgui_toggle.ToggleFlags_.animated
    )
    imgui.same_line()

    toggle_config = imgui_toggle.material_style()
    toggle_config.animation_duration = 0.4
    _changed, static.flag = imgui_toggle.toggle(
        "Material Style (with slowed anim)", static.flag, config=toggle_config
    )

    imgui.same_line()
    _changed, static.flag = imgui_toggle.toggle(
        "iOS style", static.flag, config=imgui_toggle.ios_style(size_scale=0.2)
    )

    imgui.same_line()
    _changed, static.flag = imgui_toggle.toggle(
        "iOS style (light)",
        static.flag,
        config=imgui_toggle.ios_style(size_scale=0.2, light_mode=True),
    )


@immapp.static(
    open_file_dialog=None,
    open_file_multiselect=None,
    save_file_dialog=None,
    select_folder_dialog=None,
    last_file_selection="",
    # Messages and Notifications
    icon_type=pfd.icon.info,
    message_dialog=None,
    message_choice_type=pfd.choice.ok,
)
def demo_portable_file_dialogs():
    # from imgui_bundle import portable_file_dialogs as pfd
    static = demo_portable_file_dialogs


    imgui.push_id("pfd")
    imgui_md.render_unindented(
        """
        # Portable File Dialogs
         [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) provides file dialogs
         as well as notifications and messages. They will use the native dialogs and notifications on each platform.
    """
    )

    def log_result(what: str):
        static.last_file_selection = what

    def log_result_list(whats: List[str]):
        static.last_file_selection = "\n".join(whats)

    imgui.text("      ---   File dialogs   ---")
    if imgui.button("Open file"):
        static.open_file_dialog = pfd.open_file("Select file")
    if static.open_file_dialog is not None and static.open_file_dialog.ready():
        log_result_list(static.open_file_dialog.result())
        static.open_file_dialog = None

    imgui.same_line()

    if imgui.button("Open file (multiselect)"):
        static.open_file_multiselect = pfd.open_file(
            "Select file", options=pfd.opt.multiselect
        )
    if (
        static.open_file_multiselect is not None
        and static.open_file_multiselect.ready()
    ):
        log_result_list(static.open_file_multiselect.result())
        static.open_file_multiselect = None

    imgui.same_line()

    if imgui.button("Save file"):
        static.save_file_dialog = pfd.save_file("Save file")
    if static.save_file_dialog is not None and static.save_file_dialog.ready():
        log_result(static.save_file_dialog.result())
        static.save_file_dialog = None

    imgui.same_line()

    if imgui.button("Select folder"):
        static.select_folder_dialog = pfd.select_folder("Select folder")
    if static.select_folder_dialog is not None and static.select_folder_dialog.ready():
        log_result(static.select_folder_dialog.result())
        static.select_folder_dialog = None

    if len(static.last_file_selection) > 0:
        imgui.text(static.last_file_selection)

    imgui.text("      ---   Notifications and messages   ---")

    # icon type
    imgui.text("Icon type")
    imgui.same_line()
    for notification_icon in (pfd.icon.info, pfd.icon.warning, pfd.icon.error):
        if imgui.radio_button(notification_icon.name, static.icon_type == notification_icon):
            static.icon_type = notification_icon
        imgui.same_line()
    imgui.new_line()

    if imgui.button("Add Notif"):
        pfd.notify("Notification title", "This is an example notification", static.icon_type)

    # messages
    imgui.same_line()
    # 1. Display the message
    if imgui.button("Add message"):
        static.message_dialog = pfd.message("Message title", "This is an example message", static.message_choice_type, static.icon_type)
    # 2. Handle the message result
    if static.message_dialog is not None and static.message_dialog.ready():
        print("msg ready: " + str(static.message_dialog.result()))
        static.message_dialog = None
    # Optional: Select the message type
    imgui.same_line()
    for choice_type in (pfd.choice.ok, pfd.choice.yes_no, pfd.choice.yes_no_cancel, pfd.choice.retry_cancel, pfd.choice.abort_retry_ignore):
        if imgui.radio_button(choice_type.name, static.message_choice_type == choice_type):
            static.message_choice_type = choice_type
        imgui.same_line()
    imgui.new_line()

    imgui.pop_id()


@immapp.static(selected_filename="")
def demo_imfile_dialog():
    static = demo_imfile_dialog  # Access to static variable via static
    from imgui_bundle import im_file_dialog as ifd

    imgui_md.render_unindented(
        """
        # ImFileDialog
         [ImFileDialog](https://github.com/pthom/ImFileDialog.git) provides file dialogs for ImGui, with images preview.
         *Not (yet) adapted for High DPI resolution under windows*
        """
    )

    if imgui.button("Open file"):
        ifd.FileDialog.instance().open(
            "ShaderOpenDialog",
            "Open a shader",
            "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
            True,
        )
    imgui.same_line()
    if imgui.button("Open directory"):
        ifd.FileDialog.instance().open("DirectoryOpenDialog", "Open a directory", "")
    imgui.same_line()
    if imgui.button("Save file"):
        ifd.FileDialog.instance().save(
            "ShaderSaveDialog", "Save a shader", "*.sprj .sprj"
        )

    if len(static.selected_filename) > 0:
        imgui.text(f"Last file selection:\n  {static.selected_filename}")

    # file dialogs
    if ifd.FileDialog.instance().is_done("ShaderOpenDialog"):
        if ifd.FileDialog.instance().has_result():
            # get_results: plural form - ShaderOpenDialog supports multi-selection
            res = ifd.FileDialog.instance().get_results()
            filenames = [f.path() for f in res]
            static.selected_filename = "\n  ".join(filenames)

        ifd.FileDialog.instance().close()

    if ifd.FileDialog.instance().is_done("DirectoryOpenDialog"):
        if ifd.FileDialog.instance().has_result():
            static.selected_filename = ifd.FileDialog.instance().get_result().path()

        ifd.FileDialog.instance().close()

    if ifd.FileDialog.instance().is_done("ShaderSaveDialog"):
        if ifd.FileDialog.instance().has_result():
            static.selected_filename = ifd.FileDialog.instance().get_result().path()

        ifd.FileDialog.instance().close()


@immapp.static(
    was_inited=False,
    show_command_palette=False,
    counter=0,
    command_palette_context=None,
)
def demo_command_palette():
    static = demo_command_palette

    def init_command_palette():
        static.command_palette_context = imcmd.ContextWrapper()
        highlight_font_color = ImVec4(1.0, 0.0, 0.0, 1.0)
        imcmd.set_style_color(
            imcmd.ImCmdTextType.highlight,
            imgui.color_convert_float4_to_u32(highlight_font_color),
        )
        # Add theme command: a two steps command, with initial callback + SubsequentCallback
        select_theme_cmd = imcmd.Command()
        select_theme_cmd.name = "Select theme"

        def select_theme_cmd_initial_cb():
            imcmd.prompt(["Classic", "Dark", "Light"])

        def select_theme_cmd_subsequent_cb(selected_option: int):
            if selected_option == 0:
                imgui.style_colors_classic()
            elif selected_option == 1:
                imgui.style_colors_dark()
            elif selected_option == 2:
                imgui.style_colors_light()

        select_theme_cmd.initial_callback = select_theme_cmd_initial_cb
        select_theme_cmd.subsequent_callback = select_theme_cmd_subsequent_cb
        imcmd.add_command(select_theme_cmd)

        # Simple command that increments a counter
        inc_cmd = imcmd.Command()
        inc_cmd.name = "increment counter"

        def inc_counter():
            static.counter += 1

        inc_cmd.initial_callback = inc_counter
        imcmd.add_command(inc_cmd)

    if not static.was_inited:
        init_command_palette()
        static.was_inited = True

    imgui_md.render_unindented(
        """
        # Command Palette
        [imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette.git) provides a Sublime Text or VSCode style command palette in ImGui
        """
    )

    io = imgui.get_io()
    if io.key_ctrl and io.key_shift and imgui.is_key_pressed(imgui.Key.p):
        static.show_command_palette = not static.show_command_palette

    if static.show_command_palette:
        static.show_command_palette = imcmd.command_palette_window(
            "CommandPalette", True
        )

    imgui.new_line()
    imgui.text("Press Ctrl+Shift+P to bring up the command palette")
    imgui.new_line()
    imgui.text(f"{static.counter=}")


def demo_cool_bar():
    # Function to show a CoolBar button
    def show_cool_bar_button(label):
        w = im_cool_bar.get_cool_bar_item_width()

        # Display transparent image and check if clicked
        hello_imgui.image_from_asset("images/bear_transparent.png", (w, w))
        clicked = imgui.is_item_hovered() and imgui.is_mouse_clicked(0)

        # Optional: add a label on the image
        top_left_corner = imgui.get_item_rect_min()
        text_pos = (
            top_left_corner.x + immapp.em_size(1.0),
            top_left_corner.y + immapp.em_size(1.0),
        )
        imgui.get_window_draw_list().add_text(text_pos, 0xFFFFFFFF, label)

        return clicked

    button_labels = ["A", "B", "C", "D", "E", "F"]
    imgui_md.render_unindented(
        """
        # ImCoolBar:
        ImCoolBar provides a dock-like Cool bar for Dear ImGui
        """
    )

    cool_bar_config = im_cool_bar.ImCoolBarConfig()
    cool_bar_config.anchor = ImVec2(
        0.5, 0.07
    )  #  position in the window (ratio of window size)
    if im_cool_bar.begin_cool_bar(
        "##CoolBarMain", im_cool_bar.ImCoolBarFlags_.horizontal, cool_bar_config
    ):
        for label in button_labels:
            if im_cool_bar.cool_bar_item():
                if show_cool_bar_button(label):
                    print(f"Clicked {label}")
        im_cool_bar.end_cool_bar()

    imgui.new_line()
    imgui.new_line()


def demo_gui():
    demo_cool_bar()
    demo_portable_file_dialogs()
    imgui.new_line()
    demo_imfile_dialog()
    imgui.new_line()
    demo_knobs()
    demo_toggle()
    imgui.new_line()
    demo_spinner()
    demo_command_palette()


if __name__ == "__main__":
    from imgui_bundle.demos_python import demo_utils
    demo_utils.set_hello_imgui_demo_assets_folder()

    from imgui_bundle import immapp
    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 1000))  # type: ignore
