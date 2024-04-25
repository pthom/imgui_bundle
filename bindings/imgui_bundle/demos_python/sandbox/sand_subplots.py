# Demo of issue that you can't adjust and get back subplot layout ratios
import numpy as np
from imgui_bundle import imgui, immapp, implot


x = np.log(np.arange(100))
y = np.sin(x)
y2 = y+1
scater_values = np.array([x,y2]).transpose()

ratios = implot.SubplotsRowColRatios()
ratios.row_ratios = [.6, .4]
ratios.col_ratios = [.75, .25]


def gui():
    "Our gui function, which will be invoked by the application loop"

    if implot.begin_subplots("Subplots - try and adjust plot sizes", rows=2, cols=2, size=imgui.ImVec2(-1,-1),
                            row_col_ratios=ratios):
        for i in range(4):
            if implot.begin_plot(f"Play with me {i}"):
                implot.plot_line("line plot", x, y2)

                implot.plot_scatter("scatter plot", x, y)
                implot.end_plot()

        implot.end_subplots()


immapp.run(gui, with_implot=True)
