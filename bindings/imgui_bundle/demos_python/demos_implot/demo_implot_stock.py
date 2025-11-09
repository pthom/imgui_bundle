# pip install yfinance
import yfinance as yf  # type: ignore
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from imgui_bundle import implot, ImVec4, ImVec2, imgui, imgui_ctx, IM_COL32, immapp
from typing import Optional, TypeAlias
from functools import cached_property


# ArrayFloat: 1D array of float64
ArrayFloat: TypeAlias = npt.NDArray[np.float64]  # shape (N,)

TICKER_IDS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "AMD", "INTC"]
PERIOD_RANGES = ["1mo", "3mo", "6mo", "12mo", "24mo", "60mo"]


def plot_candlestick(
        label_id: str,
        xs: ArrayFloat,  # x-axis values (timestamps as float)
        opens: ArrayFloat,
        closes: ArrayFloat,
        lows: ArrayFloat,
        highs: ArrayFloat,
        tooltip: bool = True,
        width_percent: float = 0.38,
        positive_color: ImVec4 | None = None,
        negative_color: ImVec4 | None = None) -> None:
    """Custom plotter for candlestick charts."""
    from datetime import datetime

    if positive_color is None:
        positive_color = ImVec4(0.0, 1.0, 0.441, 1.0)
    if negative_color is None:
        negative_color = ImVec4(0.853, 0.050, 0.310, 1.0)

    assert opens.shape == closes.shape == lows.shape == highs.shape == xs.shape, "All input arrays must have the same shape."
    assert xs.ndim == 1, "Input arrays must be 1D."

    # get ImGui window DrawList
    draw_list = implot.get_plot_draw_list()
    # calc real value width
    count = xs.shape[0]
    half_width = (xs[1] - xs[0]) * width_percent if count > 1 else width_percent

    # custom tool
    if implot.is_plot_hovered() and tooltip:
        mouse = implot.get_plot_mouse_pos()  # mouse position in plot coordinates, i.e. x is a timestamp
        # round mouse.x to day
        mouse_dt = datetime.fromtimestamp(mouse.x)
        rounded_dt = datetime(mouse_dt.year, mouse_dt.month, mouse_dt.day)
        mouse.x = rounded_dt.timestamp()
        # Draw a transparent gray vertical rect around the hovered day
        tool_l = implot.plot_to_pixels(mouse.x - half_width * 1.5, mouse.y).x
        tool_r = implot.plot_to_pixels(mouse.x + half_width * 1.5, mouse.y).x
        tool_t = implot.get_plot_pos().y
        tool_b = tool_t + implot.get_plot_size().y
        implot.push_plot_clip_rect()
        draw_list.add_rect_filled(ImVec2(tool_l, tool_t), ImVec2(tool_r, tool_b), IM_COL32(128, 128, 128, 64))
        implot.pop_plot_clip_rect()

        # render tool tip (won't be affected by plot clip rect)
        idx = np.searchsorted(xs, mouse.x)
        if 0 < idx < count:
            with imgui_ctx.begin_tooltip():
                dt = datetime.fromtimestamp(xs[idx])
                date_str = dt.strftime("%Y-%m-%d")
                imgui.text(f"Day:   {date_str}")
                imgui.text(f"Open:  $ {opens[idx]:.2f}")
                imgui.text(f"Close: $ {closes[idx]:.2f}")
                imgui.text(f"Low:   $ {lows[idx]:.2f}")
                imgui.text(f"High:  $ {highs[idx]:.2f}")

    # begin plot item
    if implot.internal.begin_item(label_id):
        # override legend icon color
        current_item = implot.internal.get_current_item()
        current_item.color = IM_COL32(64, 64, 64, 255)
        # fit data if requested
        if implot.internal.fit_this_frame():
            for i in range(count):
                implot.internal.fit_point(implot.Point(xs[i], lows[i]))
                implot.internal.fit_point(implot.Point(xs[i], highs[i]))
        # render data
        for i in range(count):
            open_pos = implot.plot_to_pixels(xs[i] - half_width, opens[i])
            close_pos = implot.plot_to_pixels(xs[i] + half_width, closes[i])
            low_pos = implot.plot_to_pixels(xs[i], lows[i])
            high_pos = implot.plot_to_pixels(xs[i], highs[i])
            color = positive_color if opens[i] < closes[i] else negative_color
            color_u32 = imgui.get_color_u32(color)
            draw_list.add_line(low_pos, high_pos, color_u32)
            draw_list.add_rect_filled(open_pos, close_pos, color_u32)

        # end plot item
        implot.internal.end_item()


def exponential_moving_average(arr: ArrayFloat, window: int) -> ArrayFloat:
    """Calculate the Exponential Moving Average (EMA) of a 1D array.
    A moving average with a faster response to recent price changes.
    """
    assert window > 0, "Window size must be positive."
    count = arr.shape[0]
    if count == 0:
        return arr
    ema_values = np.empty_like(arr)
    alpha = 2 / (window + 1)
    ema_values[0] = arr[0]
    for i in range(1, len(arr)):
        ema_values[i] = alpha * arr[i] + (1 - alpha) * ema_values[i - 1]
    return ema_values


@dataclass
class StockData:
    timestamps: ArrayFloat
    opens: ArrayFloat
    closes: ArrayFloat
    lows: ArrayFloat
    highs: ArrayFloat
    volumes: ArrayFloat

    @cached_property
    def ema_20(self) -> ArrayFloat:
        return exponential_moving_average(self.closes, 20)

    @cached_property
    def ema_50(self) -> ArrayFloat:
        return exponential_moving_average(self.closes, 50)

    @cached_property
    def volume_ema_20(self) -> ArrayFloat:
        return exponential_moving_average(self.volumes, 20)

    @cached_property
    def volume_ema_50(self) -> ArrayFloat:
        return exponential_moving_average(self.volumes, 50)

    @cached_property
    def rsi_14(self) -> ArrayFloat:
        prices = self.closes
        delta = np.diff(prices, prepend=prices[0])
        gain = np.where(delta > 0, delta, 0.0)
        loss = np.where(delta < 0, -delta, 0.0)

        window = 14
        avg_gain = np.empty_like(prices)
        avg_loss = np.empty_like(prices)

        avg_gain[:window] = np.nan
        avg_loss[:window] = np.nan

        avg_gain[window - 1] = gain[:window].mean()
        avg_loss[window - 1] = loss[:window].mean()

        for i in range(window, len(prices)):
            avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gain[i]) / window
            avg_loss[i] = (avg_loss[i - 1] * (window - 1) + loss[i]) / window

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi[:window] = np.nan  # First values are undefined

        return rsi


class StockViewer:
    def __init__(self):
        self.ticker_input = "GOOGL"
        self.stock_data: Optional[StockData] = None
        self.fetch_error = None
        self.loaded_ticker = ""
        self.needs_refresh_x_extent = True
        self.period = "24mo"  # default
        self.fetch_data()

    def fetch_data(self):
        try:
            df = yf.download(self.ticker_input, period=self.period, interval="1d")
            df = df.dropna()
            timestamps = df.index.map(lambda ts: ts.timestamp()).to_numpy(np.float64)
            self.stock_data = StockData(
                timestamps,
                df["Open"].to_numpy().flatten(),
                df["Close"].to_numpy().flatten(),
                df["Low"].to_numpy().flatten(),
                df["High"].to_numpy().flatten(),
                df["Volume"].to_numpy().astype(np.float64).flatten(),
            )
            self.loaded_ticker = self.ticker_input
            self.fetch_error = None
            self.needs_refresh_x_extent = True
        except Exception as e:
            self.fetch_error = str(e)
            self.stock_data = None

    def _gui_fetch(self):
        imgui.set_next_item_width(immapp.em_size(10))
        if imgui.begin_combo("Ticker", self.ticker_input):
            changed, self.ticker_input = imgui.input_text("Manual entry", self.ticker_input, 16)
            for stock_id in TICKER_IDS:
                changed, selected = imgui.selectable(stock_id, self.ticker_input == stock_id)
                if selected:
                    self.ticker_input = stock_id
            imgui.end_combo()

        imgui.same_line()

        imgui.set_next_item_width(immapp.em_size(10))
        _, current_idx = imgui.combo("Period", PERIOD_RANGES.index(self.period), PERIOD_RANGES)
        self.period = PERIOD_RANGES[current_idx]

        imgui.same_line()

        if imgui.button("Get Data"):
            self.fetch_data()

    def gui(self):
        self._gui_fetch()

        if self.fetch_error:
            imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"Error: {self.fetch_error}")

        if self.stock_data:
            implot.get_style().use_local_time = False
            if implot.begin_subplots("##Candlestick + Volume", 3, 1, ImVec2(-1, -1),
                                    implot.SubplotFlags_.link_all_x):

                # === Candlestick plot ===
                if implot.begin_plot("Price", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "$%.0f")
                    x_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.x1, "##Date", x_axis_flags)
                    y_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.y1, "Price", y_axis_flags)
                    plot_candlestick(
                        self.loaded_ticker,
                        self.stock_data.timestamps,
                        self.stock_data.opens,
                        self.stock_data.closes,
                        self.stock_data.lows,
                        self.stock_data.highs,
                    )
                    implot.plot_line(f"{self.loaded_ticker}-EMA 20", self.stock_data.timestamps, self.stock_data.ema_20)
                    implot.plot_line(f"{self.loaded_ticker}-EMA 50", self.stock_data.timestamps, self.stock_data.ema_50)

                    implot.end_plot()

                # === Volume subplot ===
                if implot.begin_plot("Volume", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "%.0f")
                    y_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.y1, "Volume", y_axis_flags)
                    implot.plot_bars(f"{self.loaded_ticker} Vol", self.stock_data.timestamps, self.stock_data.volumes, 60 * 60 * 24 * 0.8)

                    implot.plot_line(f"{self.loaded_ticker}-Vol EMA 20", self.stock_data.timestamps, self.stock_data.volume_ema_20)
                    implot.plot_line(f"{self.loaded_ticker}-Vol EMA 50", self.stock_data.timestamps, self.stock_data.volume_ema_50)
                    implot.end_plot()

                # === RSI subplot ===
                if implot.begin_plot("RSI", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "%.0f")
                    implot.setup_axis_limits(implot.ImAxis_.y1, 0, 100)  # RSI range
                    implot.setup_axis(implot.ImAxis_.y1, "RSI")

                    implot.plot_line(f"{self.loaded_ticker} RSI 14", self.stock_data.timestamps, self.stock_data.rsi_14)

                    # Overbought/oversold reference lines
                    implot.tag_y(70.0, ImVec4(1.0, 0.0, 0.0, 1.0), "Overbought")
                    implot.drag_line_y(1, 70.0, ImVec4(1.0, 0.0, 0.0, 1.0), 1.0)
                    implot.tag_y(30.0, ImVec4(0.0, 1.0, 0.0, 1.0), "Oversold")
                    implot.drag_line_y(2, 30.0, ImVec4(0.0, 1.0, 0.0, 1.0), 1.0)

                    implot.end_plot()

                self.needs_refresh_x_extent = False
                implot.end_subplots()


viewer = StockViewer()
immapp.run(viewer.gui, with_implot=True, window_title="Demo Implot Stock Viewer", window_size=(1200, 800))
