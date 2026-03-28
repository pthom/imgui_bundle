# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp
from imgui_bundle.demos_python.demos_imgui_explorer import implot3d_demo
from imgui_bundle.demos_python.demos_imgui_explorer import implot_demo

from imgui_bundle.demos_python.demo_utils.imgui_explorer_setup import get_imgui_explorer, get_package_path
imgui_explorer, _has_imgui_explorer = get_imgui_explorer()


def demo_gui():
    imgui_md.render_unindented(
        """
        [Implot](https://github.com/epezent/implot) and [Implot3D](https://github.com/brenocq/implot3d) are fast and efficient libraries which provide immediate Mode Plotting.
        """
    )

    if imgui.collapsing_header("ImPlot: Full Demo"):
        if _has_imgui_explorer:
            imgui.push_id("ImPlotDemo")
            imgui_explorer.show_imgui_explorer_gui_python(imgui_explorer.ImGuiExplorerLibrary.implot, get_package_path())
            imgui.pop_id()
        else:
            implot_demo.show_all_demos()

    if imgui.collapsing_header("ImPlot3D: Full Demo"):
        if _has_imgui_explorer:
            imgui.push_id("ImPlot3DDemo")
            imgui_explorer.show_imgui_explorer_gui_python(imgui_explorer.ImGuiExplorerLibrary.implot3_d, get_package_path())
            imgui.pop_id()
        else:
            implot3d_demo.show_all_demos()


def main():
    immapp.run(demo_gui, with_implot=True, with_implot3d=True, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
