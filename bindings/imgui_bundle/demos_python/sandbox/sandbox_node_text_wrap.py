from imgui_bundle import imgui_node_editor as ed, imgui, immapp, hello_imgui, ImVec2, imgui_md


g_node_width = 400.0
g_value = 5.0
g_reset_node_layout = False


def gui():
    global g_node_width, g_value, g_reset_node_layout

    ed.begin("My Editor")
    ed.begin_node(ed.NodeId(1))

    if g_reset_node_layout:
        g_reset_node_layout = False
    else:
        # Test ImGui::Separator: it should use the actual node width.
        imgui.text_wrapped("Below is a separator and a separator text. They should use the actual node width.")
        imgui.separator()
        imgui.separator_text("Hello")

        #
        # A dummy button, to artificially set the node width
        #

        imgui.separator_text("Dummy Button")
        imgui_md.render_unindented("""
            This is a _dummy button_, to artificially set the node width.
            Below it is a fixed width slider, which enables to set this button's width.
        """)
        dummy_button_size = ImVec2(g_node_width, 20)
        imgui.button("Dummy", dummy_button_size)
        # With a fixed width slider, so that we can set the node width.
        imgui.set_next_item_width(200)
        _, g_node_width = imgui.slider_float("width", g_node_width, 0, 700)

        #
        # Test ImGui::TextWrapped: it should use the actual node width.
        #
        # Notes:
        # * If using the slider to make the node wider, the wrapped text with will adapt.
        # * After that if you try to reduce the node width, The wrapped text with will not reduce
        #   (This is because the node caches its previous size, and the wrapped text will use it.
        #   This is okay.)
        imgui.separator_text("Test TextWrapped")
        imgui.text_wrapped("""
Note:
    * If using the slider to make the node wider, the wrapped text with will adapt.
    * After that if you try to reduce the node width, The wrapped text with will not reduce (This is because the node caches its previous size, and the wrapped text will use it. This is okay.)
    """)

        #
        # Test ImGui::SliderFloat: it should use the actual node width.
        #
        imgui.separator_text("Slider with default width")
        imgui.text_wrapped("Below is a slider using the default width. It should be the same width as the node (There is a hard code max label size, which corresponds to 4 wide characters)." )
        _, g_value = imgui.slider_float("value##2", g_value, 0, 700)

        #
        # Reset Node Layout
        #
        imgui.separator_text("Reset Layout")
        imgui_md.render_unindented("""
            Click the button below to reset the node layout. Its content will disappear for one frame,
            allowing it to be re-laid out with the new width.
        """)
        if imgui.button("Reset Layout"):
            g_reset_node_layout = True

    ed.end_node()

    ed.end()


def main() -> None:
    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui

    addons_params = immapp.AddOnsParams()
    addons_params.with_node_editor = True

    # Change the node editor config to force ImGui to use the node width.
    addons_params.with_node_editor_config = ed.Config()
    addons_params.with_node_editor_config.force_window_content_width_to_node_width = True

    addons_params.with_markdown = True

    immapp.run(runner_params, addons_params)


if __name__ == "__main__":
    main()
