from imgui_bundle import implot, immapp
import numpy as np

x = np.linspace(0, 2 * np.pi, 1000)
y = np.sin(x)


def gui():
    implot.begin_plot("Plot")
    implot.plot_line("Line", x, y)
    implot.end_plot()


def main():
    immapp.run(gui, with_implot=True)


if __name__ == "__main__":
    main()
