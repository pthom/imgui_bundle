import imgui_bundle
from imgui_bundle import imgui, immapp, ImVec4


def make_gui_closure():
    color_text = None

    def gui():
        imgui.text("Hello world")
        size = [300, 300]
        imgui.button("Hello", size)

        nonlocal color_text
        if color_text is None:
            color_text = imgui.get_style().get_color(imgui.Col_.text)

        _ = imgui.color_edit4("Text color", color_text)

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
