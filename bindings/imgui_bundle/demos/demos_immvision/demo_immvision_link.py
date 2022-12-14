import os.path
import cv2
from imgui_bundle import immvision, immapp, imgui


this_dir = os.path.dirname(__file__)
image = cv2.imread(this_dir + "/../assets/images/tennis.jpg")
channels = cv2.split(image)

params_rgb = immvision.ImageParams()
params_rgb.image_display_size = (200, 0)
params_rgb.zoom_key = "some_common_zoom_key"

params_channels = immvision.ImageParams()
params_channels.image_display_size = (200, 0)
params_channels.zoom_key = "some_common_zoom_key"


def gui():
    immvision.image("RGB", image, params_rgb)
    for i, channel in enumerate(channels):
        immvision.image(f"channel {i}", channel, params_channels)
        imgui.same_line()


if __name__ == "__main__":
    immapp.run(gui, window_size=(1000, 800))