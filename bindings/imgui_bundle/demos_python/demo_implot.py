# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import imgui, imgui_md, immapp
from imgui_bundle.demos_python.demos_imgui_manual import implot3d_demo
from imgui_bundle.demos_python.demos_imgui_manual import implot_demo

try:
    from imgui_bundle import imgui_manual
    _has_imgui_manual = True
except ImportError:
    _has_imgui_manual = False


def demo_gui():
    imgui_md.render_unindented(
        """
        # ImPlot & ImPlot3D &nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;[Online Demo](https://traineq.org/implot_demo/src/implot_demo.html)
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.
        """
    )

    if imgui.collapsing_header("ImPlot: Full Demo"):
        if _has_imgui_manual:
            imgui.push_id("ImPlotDemo")
            imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.implot)
            imgui.pop_id()
        else:
            implot_demo.show_all_demos()

    if imgui.collapsing_header("ImPlot3D: Full Demo"):
        if _has_imgui_manual:
            imgui.push_id("ImPlot3DDemo")
            imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.implot3_d)
            imgui.pop_id()
        else:
            implot3d_demo.show_all_demos()


def main():
    immapp.run(demo_gui, with_implot=True, with_implot3d=True, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
