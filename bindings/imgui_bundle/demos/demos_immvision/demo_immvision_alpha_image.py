import os.path
import cv2

from imgui_bundle import immvision, immapp


this_dir = os.path.dirname(__file__)
image = cv2.imread(this_dir + "/../assets/images/bear_transparent.png", cv2.IMREAD_UNCHANGED)
params = immvision.ImageParams()


def gui():
    immvision.image("Bear", image, params)


def main():
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()