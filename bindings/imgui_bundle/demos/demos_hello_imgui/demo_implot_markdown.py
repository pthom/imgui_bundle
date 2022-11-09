import numpy as np
from imgui_bundle import implot, imgui_md, ImVec2
import imgui_bundle


def main():
    x = np.arange(0, np.pi * 4, 0.01)
    y1 = np.cos(x)
    y2 = np.sin(x)

    def gui():
        imgui_md.render("# This is the plot of _cosinus_ and *sinus*")  # Markdown
        implot.begin_plot("Plot")
        implot.plot_line("y1", x, y1)
        implot.plot_line("y2", x, y2)
        implot.end_plot()

    imgui_bundle.run(gui, with_implot=True, with_markdown=True, window_size=(600, 400))


if __name__ == "__main__":
    main()
