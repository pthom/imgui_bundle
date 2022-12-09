import imgui_bundle
from imgui_bundle import imgui, immapp


def make_gui_closure():
    color_text = None

    def gui():

        imgui.text("Hello world")

        nonlocal color_text
        if color_text is None:
            color_text = imgui.get_style().get_color(imgui.Col_.text)

        def edit_text_color():
            nonlocal color_text
            color_as_list = [color_text.x, color_text.y, color_text.z, color_text.w]
            changed, new_color_list = imgui.color_edit4("Text color", color_as_list)
            if changed:
                # color_text = ImVec4(new_color_list[0], new_color_list[1], new_color_list[2], new_color_list[3])
                # imgui.get_style().set_color(imgui.Col_.text, color_text)
                color_text.x = new_color_list[0]
                color_text.y = new_color_list[1]
                color_text.z = new_color_list[2]
                color_text.w = new_color_list[3]

        edit_text_color()

        # Show that get_io().mouse_clicked : bool[5] is bound
        click = imgui.get_io().mouse_clicked
        if click[0]:
            print("click")

    return gui


def main():
    gui = make_gui_closure()
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
