# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, immvision, immapp, imgui_md
import importlib.util

HAS_IMMVISION = "immvision_not_available" not in dir(immvision)
from imgui_bundle.demos_python import demo_utils  # noqa: E402


HAS_OPENCV = importlib.util.find_spec("cv2") is not None


if HAS_IMMVISION and HAS_OPENCV:
    from imgui_bundle.demos_python import demos_immvision


def demo_gui():
    if not HAS_IMMVISION:
        imgui.text(
            "Dear ImGui Bundle was compiled without support for ImmVision (this requires OpenCV)"
        )
        return
    elif not HAS_OPENCV:
        imgui_md.render_unindented(
            """
            ImGui Bundle's ImmVision demos require that one of the [opencv-python pip packages](https://github.com/opencv/opencv-python) is installed and imports successfully.

            Please install *one* and _only one_ of the packages below (copy and paste the desired line into a terminal).

            * To install OpenCv standard package:
            ```bash
            pip install opencv-python
            ```

            * To install OpenCv package with contrib modules
            ```bash
            pip install opencv-contrib-python
            ```

            To install OpenCv package headless (no cv.imshow, etc., for server installations)
            ```bash
            pip install opencv-python-headless
            ```
        """
        )
        return

    imgui_md.render_unindented(
        """
        # ImmVision
        [ImmVision](https://github.com/pthom/immvision) is an immediate image debugger.
        It is based on OpenCv and can analyse RGB & float, images with 1 to 4 channels.

        Whereas *imgui_tex_inspect* is dedicated to texture analysis, *immvision* is more dedicated to image processing and computer vision.

        Open the demos below by clicking on their title.
    """
    )

    if imgui.collapsing_header("Display images"):
        demos_immvision.demo_immvision_display.demo_gui()
        demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_display")
    if imgui.collapsing_header("Link images zoom"):
        demos_immvision.demo_immvision_link.demo_gui()
        demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_link")
    if imgui.collapsing_header("Image inspector"):
        demos_immvision.demo_immvision_inspector.demo_gui()
        demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_inspector")
    if imgui.collapsing_header("Example with image processing"):
        demos_immvision.demo_immvision_process.demo_gui()
        demo_utils.show_python_vs_cpp_file(
            "demos_immvision/demo_immvision_process", nb_lines=40
        )


def main():
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    demo_utils.set_hello_imgui_demo_assets_folder()
    main()
