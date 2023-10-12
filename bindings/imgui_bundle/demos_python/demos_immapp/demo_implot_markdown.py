import numpy as np
from imgui_bundle import implot, imgui_md, immapp
from imgui_bundle.demos_python import demo_utils


def main():
    # This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    #         hello_imgui.set_assets_folder("my_assets"); # (By default, HelloImGui will search inside "assets")
    demo_utils.set_hello_imgui_demo_assets_folder()

    x = np.arange(0, np.pi * 4, 0.01)
    y1 = np.cos(x)
    y2 = np.sin(x)

    def gui():
        imgui_md.render("# This is the plot of _cosinus_ and *sinus*")  # Markdown
        if implot.begin_plot("Plot"):
            implot.plot_line("y1", x, y1)
            implot.plot_line("y2", x, y2)
            implot.end_plot()

    immapp.run(gui, with_implot=True, with_markdown=True, window_size=(600, 400))


if __name__ == "__main__":
    main()
