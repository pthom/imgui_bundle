# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import webbrowser
from imgui_bundle import imgui, imgui_md, immapp
from imgui_bundle.demos_python.demos_implot3d import implot3d_demo
from imgui_bundle.demos_python.demos_implot import implot_demo


def demo_gui():
    imgui_md.render_unindented(
        """
        # ImPlot & ImPlot3D &nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;&nbsp;[Online Demo](https://traineq.org/implot_demo/src/implot_demo.html)
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.
        """
    )

    if imgui.collapsing_header("ImPlot: Full Demo"):
        imgui.text("View on GitHub:")
        imgui.same_line()
        if imgui.button("C++ demo code"):
            webbrowser.open("https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp")
        imgui.same_line()
        if imgui.button("Python demo code"):
            webbrowser.open("https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot/implot_demo.py")
        implot_demo.show_all_demos()

    if imgui.collapsing_header("ImPlot3D: Full Demo"):
        imgui.text("View on GitHub:")
        imgui.same_line()
        if imgui.button("C++ demo code"):
            webbrowser.open("https://github.com/brenocq/implot3d/blob/main/implot3d_demo.cpp")
        imgui.same_line()
        if imgui.button("Python demo code"):
            webbrowser.open("https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_implot3d/implot3d_demo.py")
        implot3d_demo.show_all_demos()


def main():
    immapp.run(demo_gui, with_implot=True, with_implot3d=True, with_markdown=True, window_size=(1000, 800))


if __name__ == "__main__":
    main()
