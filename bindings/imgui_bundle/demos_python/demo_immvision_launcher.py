from imgui_bundle import imgui, immvision, immapp, imgui_md, imgui_color_text_edit as text_edit

HAS_IMMVISION = "immvision_not_available" not in dir(immvision)
from imgui_bundle.demos_python import demo_utils

HAS_OPENCV = False
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    pass

if HAS_IMMVISION and HAS_OPENCV:
    from imgui_bundle.demos_python import demos_immvision


@immapp.static(opencv_help=None)
def make_gui() -> demo_utils.GuiFunction:
    if HAS_IMMVISION and HAS_OPENCV:
        gui_process = demos_immvision.demo_immvision_process.make_gui()

    def gui():
        if not HAS_IMMVISION:
            imgui.text("ImGui Bundle was compiled without support for ImmVision (this requires OpenCV)")
            return
        elif not HAS_OPENCV:
            if make_gui.opencv_help is None:
                make_gui.opencv_help = text_edit.TextEditor()
                make_gui.opencv_help.set_text("""
# OpenCv standard package
pip install opencv-python

# OpenCv package with contrib modules
pip install opencv-contrib-python

# OpenCv package headless (no cv.imshow, etc.); for server installations
pip install opencv-python-headless
""")
            demo_utils.render_md_unindented(
        """
        ImGui Bundle's ImmVision demos require that one of the [opencv-python pip packages](https://github.com/opencv/opencv-python) is installed and imports successfully.
        
        Please install *one* and _only one_ of the packages below (copy and paste the desired line into a terminal)
        """)
            make_gui.opencv_help.render("Install opencv-python", immapp.em_to_vec2(60, 10))
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
