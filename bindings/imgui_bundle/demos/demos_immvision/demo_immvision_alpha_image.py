import os.path

import numpy as np
import cv2


from imgui_bundle import immvision, immapp


def make_demo_closure():
    this_dir = os.path.dirname(__file__)
    image = cv2.imread(this_dir + "/../assets/images/bear_transparent.png", cv2.IMREAD_UNCHANGED)

    params = immvision.ImageParams()

    def gui():
        nonlocal image, params
        immvision.image("Bear", image, params)

    return gui


def main():
    gui = make_demo_closure()
    immapp.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()