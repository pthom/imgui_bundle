from imgui_bundle import imgui, immvision, immapp, imgui_md

HAS_IMMVISION = "immvision_not_available" not in dir(immvision)
from imgui_bundle.demos_python import demo_utils

has_opencv = False
try:
    import cv2
    has_opencv = True
except ImportError:
    pass

if HAS_IMMVISION and has_opencv:
    from imgui_bundle.demos_python import demos_immvision


def make_gui() -> demo_utils.GuiFunction:
    if HAS_IMMVISION and has_opencv:
        gui_process = demos_immvision.demo_immvision_process.make_gui()

    def gui():
        if not HAS_IMMVISION:
            imgui.text("ImGui Bundle was compiled without support for ImmVision (this requires OpenCV)")
            return
        elif not has_opencv:
            imgui_md.render(
        """
ImGui Bundle's ImmVision demos require that one of the [opencv-python pip packages](https://github.com/opencv/opencv-python) is installed and imports successfully.
`cv2` was not found or could not be imported, so no demos are available here."""
    )
    
            return

        nonlocal gui_process

        demo_utils.render_md_unindented(
            """
        [ImmVision](https://github.com/pthom/immvision) is an immediate image debugger. 
        It is based on OpenCv and can analyse RGB & float, images with 1 to 4 channels. 

        Whereas *imgui_tex_inspect* is dedicated to texture analysis, *immvision* is more dedicated to image processing and computer vision. 

        Open the demos below by clicking on their title.
        """
        )

        if imgui.collapsing_header("Display images"):
            demos_immvision.demo_immvision_display.gui()
            demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_display")
        if imgui.collapsing_header("Link images zoom"):
            demos_immvision.demo_immvision_link.gui()
            demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_link")
        if imgui.collapsing_header("Image inspector"):
            demos_immvision.demo_immvision_inspector.gui()
            demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_inspector")
        if imgui.collapsing_header("Example with image processing"):
            gui_process()
            demo_utils.show_python_vs_cpp_file("demos_immvision/demo_immvision_process", nb_lines=40)

    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()


def main():
    gui = make_gui()
    immapp.run(gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
