"""ImmVision: images that pan and zoom together

Image params that share a `zoom_key` follow each other: pan or zoom one image, and the others move with it. Here, a
photo and its three color channels. Pan by dragging, zoom with the mouse wheel. The image is read with OpenCV
(`pip install imgui-bundle[imgproc]`).
"""
import cv2
import numpy as np

from imgui_bundle import immvision, immapp, imgui, rich_md, hello_imgui, register_demos_assets_folder

NARROW_WIDTH_EM = 40  # Under this width (in em), two images per row instead of four

register_demos_assets_folder()
# In RGB: ImmVision's default order (OpenCV reads BGR)
image_bgr = cv2.imread(hello_imgui.asset_file_full_path("images/tennis.jpg"))
image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)  # type: ignore[arg-type]
images = {"RGB": image}
for i, channel_name in enumerate(["Red", "Green", "Blue"]):
    images[channel_name] = np.ascontiguousarray(image[:, :, i])

# One params per image, all with the same zoom key
all_params = {}
for name in images:
    all_params[name] = immvision.ImageParams()
    all_params[name].zoom_key = "tennis"


def gui():
    rich_md.render(
        "Images whose params share a `zoom_key` pan and zoom together: drag one to pan, zoom with the mouse wheel."
    )

    # Four images in a row, or two on a narrow screen (a phone)
    narrow = imgui.get_content_region_avail().x < NARROW_WIDTH_EM * imgui.get_font_size()
    if imgui.begin_table("images", 2 if narrow else 4):
        for name, img in images.items():
            imgui.table_next_column()
            # A negative width: the column's width, less one pixel (ImmVision then stores the size it used)
            all_params[name].image_display_size = (-1, 0)
            immvision.image(name, img, all_params[name])
        imgui.end_table()


if __name__ == "__main__":
    immapp.run(gui, window_size=(1000, 800), with_markdown=True)
