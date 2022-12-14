import os.path
import subprocess
import sys
from imgui_bundle import imgui, immvision, immapp
from imgui_bundle.demos import demo_utils, demos_imguizmo


def make_gui() -> demo_utils.GuiFunction:
    def gui():
        demo_utils.render_md_unindented("""
        [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) provides an immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui 

        What started with the gizmo is now a collection of dear imgui widgets and more advanced controls. 

        Open the demos below by clicking on their title.
        """)

        if imgui.collapsing_header("Gizmo"):
            imgui.text("Click the button below to launch the demo")
            if imgui.button("Run gizmo demo"):
                this_dir = os.path.dirname(__file__)
                subprocess.Popen([sys.executable, this_dir + "/demos_imguizmo/demo_gizmo.py"])
            demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_gizmo", nb_lines=30)
        if imgui.collapsing_header("Curve Edit"):
            demos_imguizmo.demo_guizmo_curve_edit.demo_launch()
            demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_guizmo_curve_edit", nb_lines=30)
        if imgui.collapsing_header("Zoom Slider"):
            imgui.text("Click the button below to launch the demo")
            if imgui.button("Run demo"):
                this_dir = os.path.dirname(__file__)
                subprocess.Popen([sys.executable, this_dir + "/demos_imguizmo/demo_guizmo_zoom_slider.py"])
            demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_guizmo_zoom_slider", nb_lines=30)
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
