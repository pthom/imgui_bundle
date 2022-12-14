import os.path

from imgui_bundle import immvision, immapp, imgui
import cv2


def fill_inspector():
    this_dir = os.path.dirname(__file__)
    image_files = ["dmla.jpg", "house.jpg", "tennis.jpg", "world.jpg"]
    for image_file in image_files:
        img = cv2.imread(f"{this_dir}/../assets/images/{image_file}")
        immvision.inspector_add_image(img, legend=image_file)


@immapp.static(inited=False)
def gui():
    if not gui.inited:
        fill_inspector()
        gui.inited = True

    immvision.inspector_show()


def main():
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
