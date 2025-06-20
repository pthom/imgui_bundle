# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os.path
import subprocess
import sys
from imgui_bundle import imgui, immapp, hello_imgui, imgui_md, ImVec2
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

    imgui.text(
        "Click the button below to launch the demo (below the button is a screenshot of the app that will be launched)"
    )
    if demo_utils.can_run_subprocess():
        if imgui.button("Run gizmo demo"):
            this_dir = os.path.dirname(__file__)
            subprocess.Popen(
                [sys.executable, this_dir + "/demos_imguizmo/demo_gizmo.py"]
            )
    hello_imgui.image_from_asset(
        "images/gizmo_screenshot.jpg", size=ImVec2(0, immapp.em_size(15.0))
    )
    demo_utils.show_python_vs_cpp_file("demos_imguizmo/demo_gizmo", nb_lines=30)


def main():
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
