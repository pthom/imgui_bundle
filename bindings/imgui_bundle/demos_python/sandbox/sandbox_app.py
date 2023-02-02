from __future__ import annotations
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction
from imgui_bundle import imgui, immapp, ImVec4


def make_gui_closure() -> GuiFunction:
    color_text = None
    vec = ImVec4(0.1, 0.2, 0.3, 0.4)

    def gui():
        nonlocal color_text, vec
        if color_text is None:
            color_text = imgui.get_style().color_(imgui.Col_.text)

        changed, color_text = imgui.color_edit4("Text color", color_text)
        if changed:
            imgui.get_style().set_color_(imgui.Col_.text, color_text)

        _, vec = imgui.input_float4("Vec", vec)

    return gui


def main():
    gui = make_gui_closure()
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
