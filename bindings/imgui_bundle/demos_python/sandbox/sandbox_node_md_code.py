from imgui_bundle import immapp, imgui, imgui_md, imgui_node_editor as ed, ImVec2


def gui():
    imgui_md.render_unindented("""
        Below is a code block rendered in markdown outside of a node editor: it should use ImGuiColorTextEdit
        ```cpp
        // This is a code block
        int main() {
            return 0;
        }
        """)

    ed.begin("My Node Editor")
    ed.begin_node(ed.NodeId(1))
    imgui.dummy(ImVec2(500, 0))
    imgui_md.render_unindented("""
        Below is a code block rendered in markdown inside a node editor:
        it should not use ImGuiColorTextEdit, but instead render as a simple code block,
        with no syntax highlighting (but using a code font).
        ```cpp
        // This is a code block
        int main() {
            return 0;
        }
        """)
    ed.end_node()
    ed.end()


def main():
    runner_params = immapp.RunnerParams()
    runner_params.callbacks.show_gui = gui
    add_ons_params = immapp.AddOnsParams()
    add_ons_params.with_markdown = True

    # important: force the window content width to be the same as the node width
    add_ons_params.with_node_editor = True
    add_ons_params.with_node_editor_config = ed.Config()
    add_ons_params.with_node_editor_config.force_window_content_width_to_node_width = True

    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
