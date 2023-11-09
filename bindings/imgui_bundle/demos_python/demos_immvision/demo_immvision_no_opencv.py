from imgui_bundle import imgui, immvision
import numpy as np
import math

ImVec2 = imgui.ImVec2
ImVec4 = imgui.ImVec4


def main() -> None:
    from imgui_bundle import immapp

    image = np.zeros((1000, 800, 3), np.uint8)
    h = image.shape[0]
    w = image.shape[1]
    for row in range(h):
        for col in range(w):
            x = col / w * math.pi
            y = row / h * math.pi
            image[row, col, 0] = np.uint8((math.cos(x * 2) + math.sin(y)) * 128)
            image[row, col, 1] = np.uint8((math.cos(x) + math.sin(y * 2)) * 128)
            image[row, col, 2] = np.uint8((math.cos(x * 5) + math.sin(y * 3)) * 128)

    image_params = immvision.ImageParams()
    image_params.image_display_size = (1000, 800)

    def gui() -> None:
        imgui.text(f"FPS:{imgui.get_io().framerate:.1f}")
        immvision.image("House", image, image_params)

    immapp.run(gui, with_implot=True, with_markdown=True, fps_idle=0)


if __name__ == "__main__":
    main()
