import os.path

from imgui_bundle import imgui, immvision, immapp, imgui_md
from imgui_bundle.demos_python import demo_utils

# Adds many other images to the inspector (test suite with various depth & types)
from imgui_bundle.demos_python.demo_utils.immvision_make_test_suite import immvision_make_test_suite


# Add two images to the inspector at startup
def fill_inspector():
    image_files = ["house.jpg", "tennis.jpg"]
    for image_file in image_files:
        img = demo_utils.imread_demo(f"{demo_utils.demos_assets_folder()}/images/{image_file}")
        immvision.inspector_add_image(img, legend=image_file)


@immapp.static(inited=False)
def demo_gui():
    if not demo_gui.inited:
        fill_inspector()
        demo_gui.inited = True

    imgui_md.render_unindented(
        """Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images."""
    )

    if imgui.button("Add Test Images"):
        immvision_make_test_suite()

    immvision.inspector_show()


def main():
    immvision.use_rgb_color_order()
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
