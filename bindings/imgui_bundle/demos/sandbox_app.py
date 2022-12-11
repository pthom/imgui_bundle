import imgui_bundle
from imgui_bundle import imgui, immapp, ImVec4, ImVec2


def make_gui_closure():
    color_text = None
    vec = ImVec4(0.1, 0.2, 0.3, 0.4)

    def gui():
        imgui.text("Hello world")
        imgui.button("Hello", (100, 100))

        nonlocal color_text
        if color_text is None:
            color_text = imgui.get_style().colors[imgui.Col_.text]

        _ = imgui.color_edit4("Text color", color_text)

        imgui.input_float4("Vec", vec)

    return gui


def main():
    gui = make_gui_closure()
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
