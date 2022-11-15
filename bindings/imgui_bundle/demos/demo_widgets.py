from imgui_bundle import static, imgui, hello_imgui, imgui_md, ImVec2


@static(knob_value=0, knob_int_value=0)
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
            changed, static.knob_value = imgui_knobs.knob(
                knob_typename,
                p_value=static.knob_value,
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
            changed, static.knob_int_value = imgui_knobs.knob_int(
                knob_typename,
                p_value=static.knob_int_value,
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
    knobs_size_small = imgui.get_font_size() / imgui.get_io().font_global_scale * 2.5
    knobs_size_big = knobs_size_small * 1.5
    show_float_knobs(knobs_size_small)
    imgui.text("Some big knobs (int values)")
    show_int_knobs(knobs_size_big)


def demo_spinner():
    from imgui_bundle import imspinner

    imgui_md.render(
        """
# Spinners
  [imspinner](https://github.com/dalerank/imspinner) provides spinners for ImGui."""
    )

    color = imgui.ImColor(0.3, 0.5, 0.9, 1.0)
    imspinner.spinner_moving_dots("spinner_moving_dots", 3.0, color, 28.0)
    imgui.same_line()

    radius = imgui.get_font_size() / 2.0
    imspinner.spinner_arc_rotation("spinner_arc_rotation", radius, 4.0, color)
    imgui.same_line()

    radius1 = imgui.get_font_size() / 2.5
    imspinner.spinner_ang_triple("spinner_arc_fade", radius1, radius1 * 1.5, radius1 * 2.0, 2.5, color, color, color)


@static(toggle_a=True, toggle_b=True)
def demo_toggle():
    static = demo_toggle
    imgui_md.render(
        """
# Toggle Switch
  [imgui_toggle](https://github.com/cmdwtf/imgui_toggle) provides toggle switches for ImGui."""
    )

    changed, static.toggle_a = imgui.toggle("Default Toggle", static.toggle_a)
    changed, static.toggle_b = imgui.toggle("Animated Toggle", static.toggle_b, imgui.ImGuiToggleFlags_.animated)


@static(selected_filename="")
def demo_file_dialog():
    static = demo_file_dialog  # Acces to static variable via static
    from imgui_bundle import im_file_dialog as ifd

    imgui_md.render(
        """
# ImFileDialog
 [ImFileDialog](https://github.com/pthom/ImFileDialog.git) provides file dialogs for ImGui, with images preview.    
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
        ifd.FileDialog.instance().save("ShaderSaveDialog", "Save a shader", "*.sprj .sprj")

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


def _fake_log_provider() -> str:
    try:
        from fortune import fortune

        message_provider = fortune
    except ImportError:

        def message_provider() -> str:
            import random

            return random.choice(
                [
                    """pip install fortune-python if you want real fortunes""",
                    """There's such a thing as too much point on a pencil.
               -- H. Allen Smith, "Let the Crabgrass Grow" """,
                    """Santa Claus is watching!""",
                    """I'll meet you... on the dark side of the moon...
                    -- Pink Floyd""",
                    """Money can't buy love, but it improves your bargaining position.
                                    -- Christopher Marlowe""",
                    """Those who in quarrels interpose, must often wipe a bloody nose.""",
                    """Everybody is somebody else's weirdo.
                                    -- Dykstra""",
                ]
            )

    return message_provider()


def demo_logger():
    imgui_md.render(
        """# Log Viewer
A simple Log viewer from [ImGuiAl](https://github.com/leiradel/ImGuiAl)
        """
    )
    if imgui.button("Log some messages"):
        hello_imgui.log(hello_imgui.LogLevel.debug, _fake_log_provider())
        hello_imgui.log(hello_imgui.LogLevel.info, _fake_log_provider())
        hello_imgui.log(hello_imgui.LogLevel.warning, _fake_log_provider())
        hello_imgui.log(hello_imgui.LogLevel.error, _fake_log_provider())

    # hello_imgui.log_gui will display the logs
    imgui.begin_child("Logs", ImVec2(0, 150))
    hello_imgui.log_gui()
    imgui.end_child()


def demo_widgets():
    demo_file_dialog()
    imgui.separator()
    demo_knobs()
    demo_toggle()
    imgui.separator()
    demo_spinner()
    imgui.separator()
    demo_logger()


if __name__ == "__main__":
    from imgui_bundle import run

    run(demo_widgets, with_markdown=True)
