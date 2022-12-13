from imgui_bundle.demos.utils.api_demos import *
from imgui_bundle import imgui, immvision

ImVec2 = imgui.ImVec2
ImVec4 = imgui.ImVec4


def main():
    from imgui_bundle import immapp
    import cv2

    image = cv2.imread(demos_assets_folder() + "/images/house.jpg")
    image_params = immvision.ImageParams()
    image_params.image_display_size = (600, 400)

    def gui():
        immvision.image("House", image, image_params)

    immapp.run(gui, with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
