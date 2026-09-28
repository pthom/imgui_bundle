"""ImmVision: images that pan and zoom together

Image params that share a `zoom_key` follow each other: pan or zoom one image, and the others move with it. Here, a
photo and its three color channels. Pan by dragging, zoom with the mouse wheel. The image is read with OpenCV
(`pip install imgui-bundle[imgproc]`).
"""
import cv2
import numpy as np

from imgui_bundle import immvision, immapp, imgui, rich_md, hello_imgui, register_demos_assets_folder

register_demos_assets_folder()
# In RGB: ImmVision's default order (OpenCV reads BGR)
image_bgr = cv2.imread(hello_imgui.asset_file_full_path("images/tennis.jpg"))
image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)  # type: ignore[arg-type]
channels = [np.ascontiguousarray(image[:, :, i]) for i in range(image.shape[2])]

params_rgb = immvision.ImageParams()
params_rgb.image_display_size = (300, 0)
params_rgb.zoom_key = "some_common_zoom_key"

params_channels = immvision.ImageParams()
params_channels.image_display_size = (300, 0)
params_channels.zoom_key = "some_common_zoom_key"


def demo_gui():
    rich_md.render(
        "If two images params share the same ZoomKey, then the images will pan in sync. Pan and zoom the image with the mouse and the mouse wheel"
    )

    immvision.image("RGB", image, params_rgb)
    for i, channel in enumerate(channels):
        immvision.image(f"channel {i}", channel, params_channels)
        imgui.same_line()
    imgui.new_line()


if __name__ == "__main__":
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)
