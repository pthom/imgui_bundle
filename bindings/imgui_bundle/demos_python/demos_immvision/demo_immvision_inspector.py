import os.path

from imgui_bundle import immvision, immapp, imgui_md
from imgui_bundle.demos_python import demo_utils
import cv2  # type: ignore


def fill_inspector():
    os.path.dirname(__file__)
    image_files = ["dmla.jpg", "house.jpg", "tennis.jpg", "world.png"]
    for image_file in image_files:
        img = cv2.imread(f"{demo_utils.demos_assets_folder()}/images/{image_file}")
        immvision.inspector_add_image(img, legend=image_file)


@immapp.static(inited=False)
def demo_gui():
    if not demo_gui.inited:
        fill_inspector()
        demo_gui.inited = True

    imgui_md.render_unindented(
        """Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images."""
    )
    immvision.inspector_show()


def main():
    demo_utils.set_hello_imgui_demo_assets_folder()
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
