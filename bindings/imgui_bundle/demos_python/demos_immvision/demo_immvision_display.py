"""ImmVision: display an image, and inspect it

Two ways to show an image (a NumPy array in Python, a cv::Mat in C++). `immvision.image_display_resizable()` draws
it, and you drag its corner to resize it. `immvision.image()` adds the inspection tools: zoom with the mouse wheel until the pixel values
show, pan by dragging, and a button at the bottom right corner opens the settings (colormaps, channels, values).
"""
import cv2
from imgui_bundle import immvision, immapp, rich_md, ImVec2, imgui, hello_imgui, register_demos_assets_folder

register_demos_assets_folder()


def read_image(asset: str, with_alpha: bool = False):
    """An image of the demos' assets, in RGB (ImmVision's default order; OpenCV reads BGR)"""
    path = hello_imgui.asset_file_full_path(asset)
    if with_alpha:
        return cv2.cvtColor(cv2.imread(path, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)  # type: ignore[arg-type]
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)  # type: ignore[arg-type]


@immapp.static(inited=False)
def gui() -> None:
    statics = gui
    if not statics.inited:
        statics.image_display_size = ImVec2(0, immapp.em_size(15))
        statics.bear = read_image("images/bear_transparent.png", with_alpha=True)
        statics.tennis = read_image("images/tennis.jpg")

        statics.params = immvision.ImageParams()
        bear_display_size = int(hello_imgui.em_size(15))
        statics.params.image_display_size = (bear_display_size, bear_display_size)
        statics.inited = True

    imgui.begin_group()
    rich_md.render("# immvision.image_display()")
    rich_md.render("Displays an image (possibly resizable)")
    immvision.image_display_resizable(
        "Tennis", statics.tennis, size=statics.image_display_size
    )
    imgui.end_group()

    imgui.same_line()

    imgui.begin_group()
    rich_md.render("# immvision.image()")
    rich_md.render("Displays an image, while providing lots of visualization options.")
    immvision.image("Bear", statics.bear, statics.params)
    rich_md.render("""
        * Zoom in/out using the mouse wheel.
        * Pixel values are displayed at high zoom levels.
        * Pan the image by dragging it with the left mouse button
        * Open settings via button (bottom right corner of the image)
        """)
    imgui.end_group()


def main():
    immapp.run(gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
