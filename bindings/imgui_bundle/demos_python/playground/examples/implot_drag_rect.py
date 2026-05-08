"""# ImPlot: Interactive Drag Rect

[ImPlot](https://github.com/epezent/implot) is a plotting library for Dear ImGui, focused on **fast** rendering and ease of use.

This demo shows two linked plots: drag the pink rectangle in the top plot to zoom the bottom plot.

The key function is `implot.drag_rect()`, which creates an interactive, draggable rectangle on a plot:
```python
_, rect.x.min, rect.y.min, rect.x.max, rect.y.max, \
    clicked, hovered, held = implot.drag_rect(
        0, rect.x.min, rect.y.min, rect.x.max, rect.y.max,
        ImVec4(1, 0, 1, 1), flags)
```

**Links:**
- [ImPlot repository](https://github.com/epezent/implot)
- [ImPlot in Dear ImGui Explorer](https://pthom.github.io/imgui_explorer/?lib=implot) (after opening, select "Python" in the top right corner)
"""
import math
import numpy as np
from imgui_bundle import imgui, implot, immapp, ImVec4


class AppState:
    """State for the drag rect demo."""
    def __init__(self):
        # Generate 3 sine signals at different frequencies
        nb_data = 512
        sampling_freq = 44100
        freq = 500.0
        i = np.arange(-nb_data, 2 * nb_data, 1)
        t = i / sampling_freq
        arg = 2 * math.pi * freq * t
        self.x_data = t
        self.y_data1 = np.sin(arg)
        self.y_data2 = (self.y_data1 - 0.6
                        + np.sin(arg * 2) * 0.4)
        self.y_data3 = (self.y_data2 - 0.6
                        + np.sin(arg * 3) * 0.4)
        # Initial drag rect position
        self.rect = implot.Rect(
            0.0025, 0.0075, -2.7, 1.1)
        self.flags: int = implot.DragToolFlags_.none.value


def gui(state: AppState) -> None:
    s = state

    # Render the docstring as a documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=20)

    # Options for the drag tool
    _, s.flags = imgui.checkbox_flags(
        "NoCursors", s.flags,
        implot.DragToolFlags_.no_cursors)
    imgui.same_line()
    _, s.flags = imgui.checkbox_flags(
        "NoFit", s.flags,
        implot.DragToolFlags_.no_fit)
    imgui.same_line()
    _, s.flags = imgui.checkbox_flags(
        "NoInput", s.flags,
        implot.DragToolFlags_.no_inputs)

    # em = one font height (like the CSS em unit)
    plot_h = immapp.em_size() * 12

    # Top plot: full view with draggable rectangle
    if implot.begin_plot("##Main", (-1, plot_h)):
        implot.plot_line("Signal 1", s.x_data, s.y_data1)
        implot.plot_line("Signal 2", s.x_data, s.y_data2)
        implot.plot_line("Signal 3", s.x_data, s.y_data3)
        # drag_rect: creates a draggable rectangle
        # returns the updated rect coordinates
        (_, s.rect.x.min, s.rect.y.min,
            s.rect.x.max, s.rect.y.max,
            _clicked, _hovered, _held,
        ) = implot.drag_rect(
            0,
            s.rect.x.min, s.rect.y.min,
            s.rect.x.max, s.rect.y.max,
            ImVec4(1, 0, 1, 1),  # pink color
            s.flags)
        # Ensure Y range fits all signals
        implot.internal.fit_point(implot.Point(0, -3.5))
        implot.internal.fit_point(implot.Point(0, 1.5))
        implot.end_plot()

    # Bottom plot: zoomed view (locked to the drag rect)
    canvas_only = implot.Flags_.canvas_only
    if implot.begin_plot("##Zoom", (-1, plot_h), canvas_only):
        implot.setup_axes_limits(
            s.rect.x.min, s.rect.x.max,
            s.rect.y.min, s.rect.y.max,
            imgui.Cond_.always)
        implot.plot_line("Signal 1", s.x_data, s.y_data1)
        implot.plot_line("Signal 2", s.x_data, s.y_data2)
        implot.plot_line("Signal 3", s.x_data, s.y_data3)
        implot.end_plot()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="ImPlot: Drag Rect",
        with_implot=True,
        with_markdown=True)


if __name__ == "__main__":
    main()
