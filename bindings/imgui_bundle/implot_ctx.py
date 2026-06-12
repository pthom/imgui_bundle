"""
implot_ctx provide context managers to simplify the use of functions pairs like:

- `implot.begin...()` and `imgui.end...()`
  can be replaced by:
  >>> with implot_ctx.begin...() as plot:
  ...     if plot: ...
  Do note that the context manager returns a boolean indicating whether the plot is or not,
  and thus you should check if the plot evaluates to True, just like the `if plot:` in the example above.
  See the `imgui_ctx.begin_plot()` function doc for more details & examples if required.

- `implot.push...()` and `implot.pop...()`
  can be replaced by: `with implot_ctx.push...():`
  Unlike `implot.begin...()`, there is no need to check the return value of the context manager.
  See the `imgui_ctx.push_style_color()` function doc for more details & examples if required.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from imgui_bundle import implot

if TYPE_CHECKING:
    from types import TracebackType
    from imgui_bundle import imgui


class _ImplotContext:
    """Internal, do not call this directly."""

    def __enter__(self) -> _ImplotContext:
        implot.create_context()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        implot.destroy_context()

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}()'


def create_context() -> _ImplotContext:
    """Creates a new ImPlot context.
    Automatically destroys the implot context at end.

    Examples:
        >>> with implot_ctx.create_context():
        ...     hello_imgui.run(...)
    """
    return _ImplotContext()


class _BeginPlot:
    """Internal, do not call this directly."""

    def __init__(self, title_id: str, size: imgui.ImVec2Like | None = None, flags: implot.Flags = 0) -> None:
        self.title = title_id
        self.size = size
        self.flags = flags
        self.visible = False

    def __enter__(self) -> _BeginPlot:
        self.visible = implot.begin_plot(self.title, self.size, self.flags)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        if self.visible:
            implot.end_plot()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(title='{self.title}')"


def begin_plot(title_id: str, size: imgui.ImVec2Like | None = None, flags: implot.Flags = 0) -> _BeginPlot:
    """Starts a new ImPlot 2D plotting context.
    Automatically ends the plot at end.

    Args:
        title_id: **unique** identifier for the plot. If you need to avoid ID
            collisions or don't want to display a title in the plot, use double hashes
            (e.g. "MyPlot##HiddenIdText" or "##NoTitle").
        size: **frame** size of the plot widget, not the plot area.
        flags: flags to customize the plot behavior.

    Examples:
        >>> graph_values = np.array([1, 2, 3], dtype=np.int8)
        >>> with implot_ctx.begin_plot("My Plot") as plot:
        ...     if plot:
        ...         implot.plot_bars(
        ...             label_id="Graph Values Name",
        ...             values=graph_values,
        ...         )
    """
    return _BeginPlot(title_id, size, flags)


class _BeginSubPlots:
    """Internal, do not call this directly."""

    def __init__(
        self,
        title_id: str,
        rows: int,
        cols: int,
        size: imgui.ImVec2Like,
        flags: implot.SubplotFlags = 0,
        row_col_ratios: implot.SubplotsRowColRatios | None = None
    ) -> None:
        self.title = title_id
        self.rows = rows
        self.cols = cols
        self.size = size
        self.flags = flags
        self.row_col_ratios = row_col_ratios
        self.visible = False

    def __enter__(self) -> _BeginSubPlots:
        self.visible = implot.begin_subplots(
            self.title,
            self.rows,
            self.cols,
            self.size,
            self.flags,
            self.row_col_ratios,
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        if self.visible:
            implot.end_subplots()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(title='{self.title}')"


def begin_subplots(
    title_id: str,
    rows: int,
    cols: int,
    size: imgui.ImVec2Like,
    flags: implot.SubplotFlags = 0,
    row_col_ratios: implot.SubplotsRowColRatios | None = None
) -> _BeginSubPlots:
    """Starts a subdivided plotting context. Plots are added in row major order.
    Automatically ends the subplots at end.

    Args:
        title_id: **unique** identifier for the subplots context. If you need to avoid ID
            collisions or don't want to display a title in the plot, use double hashes
            (e.g. "MyPlot##HiddenIdText" or "##NoTitle").
        rows: number of rows in the subplots grid, must be greater than 0.
        cols: number of columns in the subplots grid, must be greater than 0.
        size: size of the entire grid of subplots, not the individual plots.
        flags: flags to customize the subplots behavior.
        row_col_ratios: ratios of the height of each row and width of each column.
            ``row_ratios`` and ``col_ratios`` must have AT LEAST ``rows`` and ``cols`` elements,
            respectively. These are the sizes of the rows and columns expressed in ratios.
            If the user adjusts the dimensions, the arrays are updated with new ratios.

    Notes:
        Number of plots in a subplots context must not go over [rows*cols].

        The ``title_id`` parameter of _BeginPlot_ (see above) does NOT have to be
        unique when called inside of a subplot context. Subplot IDs are hashed
        for your convenience, so you don't have to call PushID or generate unique title
        strings. Simply pass an empty string to BeginPlot unless you want to title
        each subplot.

        The ``size`` parameter of _BeginPlot_ (see above) is ignored when inside of a
        subplot context. The actual size of the subplot will be based on the
        ``size`` value you pass to _BeginSubplots_ and ``row``/``col_ratios`` if provided

    Examples:
        >>> graph_values = np.array([1, 2, 3], dtype=np.int8)
        >>> rows, cols = 2, 3
        >>> with implot_ctx.begin_subplots("My Sub-Plots", rows, cols, imgui.ImVec2(800,400)) as sub_plots:
        ...     if sub_plots:
        ...         for _ in range(rows * cols):
        ...             with implot_ctx.begin_subplot("My plot") as plot:
        ...                 if plot:
        ...                     implot.plot_bars(
        ...                         label_id="Graph Values Name",
        ...                         values=graph_values,
        ...                     )
    """
    return _BeginSubPlots(title_id, rows, cols, size, flags, row_col_ratios)


class _PushStyleColor:
    """Internal, do not call this directly."""

    def __init__(self, idx: implot.Col, col: imgui.ImU32 | imgui.ImVec4Like) -> None:
        self.idx = idx
        self.col = col

    def __enter__(self) -> _PushStyleColor:
        implot.push_style_color(self.idx, self.col)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        implot.pop_style_color()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"


def push_style_color(idx: implot.Col, col: imgui.ImU32 | imgui.ImVec4Like) -> _PushStyleColor:
    """Pushes a style color to the ImPlot context.
    Automatically pops the style color at end.

    Examples:
        >>> with implot_ctx.push_style_color(implot.Col_.inlay_text, [1, 0, 1, 1]):
        ...     # plot as usual
    """
    return _PushStyleColor(idx, col)


class _PushStyleVar:
    """Internal, do not call this directly."""

    def __init__(self, idx: implot.StyleVar, val: int | float | imgui.ImVec2Like) -> None:
        self.idx = idx
        self.val = val

    def __enter__(self) -> _PushStyleVar:
        implot.push_style_var(self.idx, self.val)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        implot.pop_style_var()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"


def push_style_var(idx: implot.StyleVar, val: int | float | imgui.ImVec2Like) -> _PushStyleVar:
    """Pushes a style var to the ImPlot context.
    Automatically pops the style var at end.

    Examples:
        >>> with implot_ctx.push_style_var(implot.StyleVar_.plot_padding, ImVec2(0, 0)):
        ...     # plot as usual
    """
    return _PushStyleVar(idx, val)


class _PushColormap:
    """Internal, do not call this directly."""

    def __init__(self, cmap_or_name: implot.Colormap | str) -> None:
        self.cmap_or_name = cmap_or_name

    def __enter__(self) -> _PushColormap:
        implot.push_colormap(self.cmap_or_name)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        implot.pop_colormap()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"


def push_colormap(cmap_or_name: implot.Colormap | str) -> _PushColormap:
    """Pushes a colormap onto the ImPlot stack, by enum (implot.Colormap_) or by name.
    Automatically pops it at end.

    Examples:
        >>> with implot_ctx.push_colormap(implot.Colormap_.deep):
        ...     ...
    """
    return _PushColormap(cmap_or_name)


class _PushPlotClipRect:
    """Internal, do not call this directly."""

    def __init__(self, expand: float = 0) -> None:
        self._expand = expand

    def __enter__(self) -> _PushPlotClipRect:
        implot.push_plot_clip_rect(self._expand)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[TracebackType] | None,
    ) -> None:
        implot.pop_plot_clip_rect()


def push_plot_clip_rect(expand: float = 0) -> _PushPlotClipRect:
    """Pushes a plot clip rect to the ImPlot context.
    Automatically pops the plot clip rect at end.

    Examples:
        >>> with implot_ctx.push_plot_clip_rect():
        ...     draw_list = implot.get_plot_draw_list()
        ...     cntr = implot.plot_to_pixels(implot.Point(0.5, 0.5))
        ...     draw_list.add_circle_filled(cntr, 20, imgui.IM_COL32(255, 255, 0, 255), 20)
    """
    return _PushPlotClipRect(expand)
