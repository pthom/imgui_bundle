import imgui_bundle
from imgui_bundle import imgui, immvision
import numpy as np


def make_gui_closure():
    font_texture: np.ndarray = None
    params = immvision.ImageParams()

    def gui():
        nonlocal font_texture, params
        imgui.text("Hello")
        if imgui.button("text"):
            font_texture = imgui.font_atlas_get_tex_data_as_rgba32(imgui.get_io().fonts)

        if font_texture is not None:
            immvision.image("font texture", font_texture, params)

    return gui


def main():
    gui = make_gui_closure()
    imgui_bundle.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
