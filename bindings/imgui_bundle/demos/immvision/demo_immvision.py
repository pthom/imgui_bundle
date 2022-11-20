from imgui_bundle import imgui, immvision
import os

ImVec2 = imgui.ImVec2
ImVec4 = imgui.ImVec4


def main():
    from imgui_bundle import run
    import cv2

    this_dir = os.path.dirname(__file__)
    image = cv2.imread(this_dir + "/resources/house.jpg")
    image_params = immvision.ImageParams()
    image_params.image_display_size = (600, 400)

    def gui():
        immvision.image("House", image, image_params)

    run(gui, with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
