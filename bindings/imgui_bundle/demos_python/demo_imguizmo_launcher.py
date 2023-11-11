# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os.path
import subprocess
import sys
from imgui_bundle import imgui, immapp, hello_imgui, imgui_md
from imgui_bundle.demos_python import demos_imguizmo
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def demo_gui():
    imgui_md.render_unindented(
        """
        # ImGuizmo
        [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo) provides an immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui

        What started with the gizmo is now a collection of dear imgui widgets and more advanced controls.

        Open the demos below by clicking on their title.
        """
    )

    if imgui.collapsing_header("Gizmo"):
        imgui.text(
            "Click the button below to launch the demo (below the button is a screenshot of the app that will be launched)"
        )
        if imgui.button("Run gizmo demo"):
            this_dir = os.path.dirname(__file__)
            subprocess.Popen(
                [sys.executable, this_dir + "/demos_imguizmo/demo_gizmo.py"]
            )
        hello_imgui.image_from_asset(
            "images/gizmo_screenshot.jpg", size=(0, immapp.em_size(15.0))
        )
        demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_gizmo", nb_lines=30)
    if imgui.collapsing_header("Curve Edit"):
        demos_imguizmo.demo_guizmo_curve_edit.demo_launch()
        demo_utils.show_python_vs_cpp_file(
            "demos_imguizmo/demo_guizmo_curve_edit", nb_lines=30
        )
    # if imgui.collapsing_header("Zoom Slider"):   # Disabled, because of missing high DPI support
    #     imgui.text("Click the button below to launch the demo")
    #     if imgui.button("Run demo"):
    #         this_dir = os.path.dirname(__file__)
    #         subprocess.Popen([sys.executable, this_dir + "/demos_imguizmo/demo_guizmo_zoom_slider.py"])
    #     demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_guizmo_zoom_slider", nb_lines=30)


def main():
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
