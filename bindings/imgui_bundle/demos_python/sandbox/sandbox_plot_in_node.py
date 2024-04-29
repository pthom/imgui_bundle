from imgui_bundle import imgui, implot, immapp, ImVec2, ImVec4, imgui_node_editor as ed

x_pos = 5.0
plot_size = ImVec2(20, 10)


def gui():
    global plot_size
    import numpy as np
    x = np.arange(0, 10, 0.01)
    y = np.sin(x)

    def my_plot_function():
        global x_pos
        implot.plot_line("My Line", x, y)
        _, x_pos, _, _, _ = implot.drag_line_x(0, x_pos, ImVec4(1, 1, 0, 1))

    ed.begin("My Node Editor")
    ed.begin_node(ed.NodeId(1))
    imgui.text("Hello")
    imgui.text("World")
    plot_size = immapp.show_resizable_plot_in_node_editor_em("My Plot", plot_size, my_plot_function)
    ed.end_node()
    ed.end()


def main():
    immapp.run(gui, with_implot=True, with_node_editor=True)


if __name__ == "__main__":
    main()
