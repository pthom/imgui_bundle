from imgui_bundle import immapp, imgui_node_editor as ed, ImVec4

def gui():
    ed.begin("Nodes")
    ed.push_style_var(ed.StyleVar.node_padding, ImVec4(1, 1, 1, 1))
    ed.pop_style_var()


    style = ed.get_style()
    style.node_padding = ImVec4(8, 8, 8, 8)

    ed.push_style_color(ed.StyleColor.node_bg, ImVec4(0.2, 0.2, 0.2, 1.0))

    ed.get_style().set_color_(ed.StyleColor.node_bg, ImVec4(0.2, 0.2, 0.2, 1.0))
    # ed.get_style().col

    ed.end()


def main():
    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    main()
