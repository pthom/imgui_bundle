"""ImmVision: the inspector collects images along a pipeline

Call `immvision.inspector_add_image()` anywhere, for example at each step of an image processing algorithm. Then
`immvision.inspector_show()` shows all the collected images, with the zoom, the pan and the pixel inspection of
`immvision.image()`. Here, two photos at startup; on the desktop, a button adds images of every depth and channel
count.
"""
import importlib.util

import cv2
from imgui_bundle import imgui, immvision, immapp, rich_md, hello_imgui, register_demos_assets_folder

register_demos_assets_folder()
# The test suite lives in the demos' utilities, which the Pyodide wheel leaves out (with the whole demos_python)
HAS_TEST_SUITE = importlib.util.find_spec("imgui_bundle.demos_python") is not None


def fill_inspector() -> None:
    """Two images in the inspector at startup, in RGB (ImmVision's default order; OpenCV reads BGR)"""
    for image_file in ["house.jpg", "tennis.jpg"]:
        img_bgr = cv2.imread(hello_imgui.asset_file_full_path("images/" + image_file))
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  # type: ignore[arg-type]
        immvision.inspector_add_image(img, legend=image_file)


@immapp.static(inited=False)
def gui():
    if not gui.inited:
        fill_inspector()
        gui.inited = True

    rich_md.render(
        """Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images."""
    )

    if HAS_TEST_SUITE and imgui.button("Add Test Images"):
        from imgui_bundle.demos_python.demo_utils.immvision_make_test_suite import immvision_make_test_suite
        immvision_make_test_suite()

    immvision.inspector_show()


def main():
    immapp.run(gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
