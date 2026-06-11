# pip install yfinance   (desktop only; in the Pyodide playground the WebSource is used)
import asyncio
import json
import numpy as np
import numpy.typing as npt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from imgui_bundle import implot, ImVec4, ImVec2, imgui, imgui_ctx, IM_COL32, immapp
from typing import Any, Optional, TypeAlias
from functools import cached_property

try:
    import pyodide  # type: ignore[import-not-found]  # noqa: F401
    IN_PYODIDE = True
except ImportError:
    IN_PYODIDE = False


# ArrayFloat: 1D array of float64
ArrayFloat: TypeAlias = npt.NDArray[np.float64]  # shape (N,)

if IN_PYODIDE:
    # Pyodide: matches the JSON whitelist baked into the website-resources repo.
    TICKER_IDS = ["AAPL", "MSFT", "GOOGL", "NVDA",
                  "MC.PA", "OR.PA", "AIR.PA", "DSY.PA",
                  "ASML.AS"]
    PERIOD_RANGES = ["6mo", "1y", "2y", "3y"]
    DEFAULT_PERIOD = "2y"
    DEFAULT_TICKER = "MC.PA"
else:
    TICKER_IDS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "AMD", "INTC"]
    PERIOD_RANGES = ["1mo", "3mo", "6mo", "12mo", "24mo", "60mo"]
    DEFAULT_PERIOD = "24mo"
    DEFAULT_TICKER = "GOOGL"

# Currency display: (tooltip prefix, ImPlot axis-format string).
CURRENCY_FORMATS: dict[str, tuple[str, str]] = {
    "USD": ("$", "$%.0f"),
    "EUR": ("€", "€%.0f"),
    "GBP": ("£", "£%.0f"),
    "CHF": ("CHF", "CHF %.0f"),
}


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
        negative_color: ImVec4 | None = None,
        currency_symbol: str = "$") -> None:
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
                imgui.text(f"Open:  {currency_symbol} {opens[idx]:.2f}")
                imgui.text(f"Close: {currency_symbol} {closes[idx]:.2f}")
                imgui.text(f"Low:   {currency_symbol} {lows[idx]:.2f}")
                imgui.text(f"High:  {currency_symbol} {highs[idx]:.2f}")

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


def _rolling_mean(arr: ArrayFloat, window: int) -> ArrayFloat:
    """Rolling mean with NaN padding for the first window-1 values."""
    n = arr.shape[0]
    result = np.full(n, np.nan)
    if n >= window:
        from numpy.lib.stride_tricks import sliding_window_view
        result[window - 1:] = sliding_window_view(arr, window).mean(axis=1)
    return result


def _rolling_std(arr: ArrayFloat, window: int) -> ArrayFloat:
    """Rolling standard deviation with NaN padding for the first window-1 values."""
    n = arr.shape[0]
    result = np.full(n, np.nan)
    if n >= window:
        from numpy.lib.stride_tricks import sliding_window_view
        result[window - 1:] = sliding_window_view(arr, window).std(axis=1)
    return result


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
    currency: str = "USD"

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
    def sma_20(self) -> ArrayFloat:
        return _rolling_mean(self.closes, 20)

    @cached_property
    def bollinger_std_20(self) -> ArrayFloat:
        return _rolling_std(self.closes, 20)

    @cached_property
    def bollinger_upper(self) -> ArrayFloat:
        return self.sma_20 + 2.0 * self.bollinger_std_20

    @cached_property
    def bollinger_lower(self) -> ArrayFloat:
        return self.sma_20 - 2.0 * self.bollinger_std_20

    @cached_property
    def drawdown_pct(self) -> ArrayFloat:
        """Running drawdown from rolling max, as a percentage (always ≤ 0)."""
        running_max = np.maximum.accumulate(self.closes)
        return (self.closes / running_max - 1.0) * 100.0

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


class DataSource(ABC):
    """Abstracts where stock OHLCV data comes from.

    `request` kicks off a fetch (sync on desktop, async on Pyodide).
    Each frame the viewer calls `take_result` to pick up a finished fetch.
    `is_loading` tells the GUI to show a "Loading…" state instead of the chart.
    """

    @abstractmethod
    def request(self, ticker: str, period: str) -> None: ...

    @abstractmethod
    def is_loading(self) -> bool: ...

    @abstractmethod
    def take_result(self) -> tuple[Optional["StockData"], Optional[str]]:
        """Return (data, error_msg). At most one is non-None. (None, None) means nothing new."""
        ...


class YFinanceSource(DataSource):
    """Synchronous data source backed by the `yfinance` package (desktop)."""

    def __init__(self):
        self._pending: tuple[Optional["StockData"], Optional[str]] = (None, None)

    def request(self, ticker: str, period: str) -> None:
        import yfinance as yf  # type: ignore  # lazy: not available in Pyodide
        try:
            df = yf.download(ticker, period=period, interval="1d")
            df = df.dropna()
            timestamps = df.index.map(lambda ts: ts.timestamp()).to_numpy(np.float64)
            data = StockData(
                timestamps,
                df["Open"].to_numpy().flatten(),
                df["Close"].to_numpy().flatten(),
                df["Low"].to_numpy().flatten(),
                df["High"].to_numpy().flatten(),
                df["Volume"].to_numpy().astype(np.float64).flatten(),
            )
            self._pending = (data, None)
        except Exception as e:
            self._pending = (None, str(e))

    def is_loading(self) -> bool:
        return False

    def take_result(self) -> tuple[Optional["StockData"], Optional[str]]:
        result = self._pending
        self._pending = (None, None)
        return result


_PERIOD_DAYS: dict[str, int] = {
    "1mo":  21,  "3mo":  63,  "6mo":  126,
    "12mo": 252, "1y":   252,
    "24mo": 504, "2y":   504,
    "3y":   756, "60mo": 1260,
}


class WebSource(DataSource):
    """Async data source for the Pyodide playground.

    Fetches `/stock_data/<slug>.json` (served by the same Pages site as the
    playground) using `pyodide.http.pyfetch`. Each `request()` cancels any
    in-flight task and starts a new one. `take_result()` polls the task's
    state without blocking the GUI.
    """

    BASE_URL = "/stock_data"

    def __init__(self):
        self._task: Optional[asyncio.Task[None]] = None
        self._pending: tuple[Optional["StockData"], Optional[str]] = (None, None)

    def request(self, ticker: str, period: str) -> None:
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._pending = (None, None)
        self._task = asyncio.create_task(self._fetch_async(ticker, period))

    def is_loading(self) -> bool:
        return self._task is not None and not self._task.done()

    def take_result(self) -> tuple[Optional["StockData"], Optional[str]]:
        if self._task is None or not self._task.done():
            return (None, None)
        result = self._pending
        self._pending = (None, None)
        self._task = None
        return result

    async def _fetch_async(self, ticker: str, period: str) -> None:
        from pyodide.http import pyfetch  # type: ignore[import-not-found]
        slug = ticker.replace(".", "_")
        url = f"{self.BASE_URL}/{slug}.json"
        try:
            resp = await pyfetch(url)
            if resp.status != 200:
                self._pending = (None, f"HTTP {resp.status} for {url}")
                return
            text = await resp.string()
            doc = json.loads(text)
            self._pending = (self._parse(doc, period), None)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self._pending = (None, str(e))

    @staticmethod
    def _parse(doc: dict[str, Any], period: str) -> "StockData":
        ts      = np.asarray(doc["ts"],     dtype=np.float64)
        opens   = np.asarray(doc["open"],   dtype=np.float64)
        highs   = np.asarray(doc["high"],   dtype=np.float64)
        lows    = np.asarray(doc["low"],    dtype=np.float64)
        closes  = np.asarray(doc["close"],  dtype=np.float64)
        volumes = np.asarray(doc["volume"], dtype=np.float64)
        days = _PERIOD_DAYS.get(period)
        if days is not None and ts.size > days:
            ts, opens, highs = ts[-days:], opens[-days:], highs[-days:]
            lows, closes, volumes = lows[-days:], closes[-days:], volumes[-days:]
        return StockData(ts, opens, closes, lows, highs, volumes,
                         currency=doc.get("currency", "USD"))


def _make_default_data_source() -> DataSource:
    return WebSource() if IN_PYODIDE else YFinanceSource()


class StockViewer:
    def __init__(self, data_source: Optional[DataSource] = None):
        self.data_source: DataSource = data_source or _make_default_data_source()
        self.ticker_input = DEFAULT_TICKER
        self.stock_data: Optional[StockData] = None
        self.fetch_error: Optional[str] = None
        self.loaded_ticker = ""
        self.needs_refresh_x_extent = True
        self.period = DEFAULT_PERIOD
        # Drag-rect range selector x-bounds (unix-seconds). y is anchored to axis limits each frame.
        self.range_x1 = 0.0
        self.range_x2 = 0.0
        # Playback (progressive day-by-day reveal). visible_count_f is a float for sub-day accumulation.
        self.playback_active = False
        self.playback_days_per_sec = 30.0
        self.visible_count_f = 0.0
        self.fetch_data()

    def fetch_data(self):
        """Kick off a fetch. For sync sources the result is ready immediately;
        for async sources it lands on a later `_poll_data_source` call."""
        self.data_source.request(self.ticker_input, self.period)
        self._poll_data_source()

    def _poll_data_source(self):
        """Pick up a result from the data source if one is ready."""
        data, err = self.data_source.take_result()
        if data is None and err is None:
            return
        if err is not None:
            self.fetch_error = err
            self.stock_data = None
            return
        assert data is not None  # narrows for type-checkers (both early returns above handle None)
        self.stock_data = data
        self.loaded_ticker = self.ticker_input
        self.fetch_error = None
        self.needs_refresh_x_extent = True
        # Reset the drag-rect x-range to the last ~90 days of the new series.
        sd = data
        ts = sd.timestamps
        i0 = max(0, len(ts) - 90)
        self.range_x1 = float(ts[i0])
        self.range_x2 = float(ts[-1])
        # New data: start fully visible, playback paused.
        self.visible_count_f = float(len(ts))
        self.playback_active = False
        # Cache full-data axis bounds — used to pin axes during partial reveal.
        bb_lo = np.nanmin(sd.bollinger_lower) if np.isfinite(sd.bollinger_lower).any() else sd.lows.min()
        bb_hi = np.nanmax(sd.bollinger_upper) if np.isfinite(sd.bollinger_upper).any() else sd.highs.max()
        self._bounds_x = (float(ts[0]), float(ts[-1]))
        self._bounds_price = (float(min(sd.lows.min(), bb_lo)), float(max(sd.highs.max(), bb_hi)))
        self._bounds_volume = (0.0, float(max(sd.volumes.max(), sd.volume_ema_50.max())))
        self._bounds_drawdown = (float(sd.drawdown_pct.min()), 0.0)

    def _gui_fetch(self):
        imgui.set_next_item_width(immapp.em_size(10))
        if imgui.begin_combo("Ticker", self.ticker_input):
            if not IN_PYODIDE:
                # Desktop: free-form ticker entry (any symbol yfinance accepts).
                # Pyodide: locked to the prebaked whitelist.
                _, self.ticker_input = imgui.input_text("Manual entry", self.ticker_input, 16)
            for stock_id in TICKER_IDS:
                _, selected = imgui.selectable(stock_id, self.ticker_input == stock_id)
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

    def _gui_playback(self):
        if self.stock_data is None:
            return
        n_full = len(self.stock_data.timestamps)
        at_end = self.visible_count_f >= n_full
        label = "Pause" if self.playback_active else ("Replay" if at_end else "Play")
        if imgui.button(label):
            if self.playback_active:
                self.playback_active = False
            else:
                if at_end:
                    self.visible_count_f = float(min(50, n_full))
                self.playback_active = True
        imgui.same_line()
        if imgui.button("Reset"):
            self.visible_count_f = float(n_full)
            self.playback_active = False
            self.needs_refresh_x_extent = True
        imgui.same_line()
        imgui.set_next_item_width(immapp.em_size(12))
        _, self.playback_days_per_sec = imgui.slider_float(
            "Speed (days/sec)", self.playback_days_per_sec, 5.0, 200.0)

    def _advance_playback(self):
        if not self.playback_active or self.stock_data is None:
            return
        n_full = len(self.stock_data.timestamps)
        dt = imgui.get_io().delta_time
        self.visible_count_f = min(self.visible_count_f + dt * self.playback_days_per_sec, float(n_full))
        if self.visible_count_f >= n_full:
            self.playback_active = False

    def _compute_range_stats(self) -> Optional[dict[str, str]]:
        """Return formatted stats for the current drag-rect x-range, or None if degenerate."""
        from datetime import datetime
        sd = self.stock_data
        if sd is None:
            return None
        lo, hi = sorted([self.range_x1, self.range_x2])
        i0 = int(np.searchsorted(sd.timestamps, lo, side="left"))
        i1 = int(np.searchsorted(sd.timestamps, hi, side="right"))
        # Clip the upper bound to the playback window so stats reflect only what's drawn.
        i1 = min(i1, int(self.visible_count_f))
        if i1 - i0 < 2:
            return None
        closes = sd.closes[i0:i1]
        ts = sd.timestamps[i0:i1]
        log_ret = np.diff(np.log(closes))
        if log_ret.size == 0 or not np.isfinite(log_ret).all():
            return None
        std = float(log_ret.std(ddof=1)) if log_ret.size > 1 else 0.0
        ret_pct = (closes[-1] / closes[0] - 1.0) * 100.0
        vol_pct = std * np.sqrt(252) * 100.0
        max_dd_pct = float((closes / np.maximum.accumulate(closes) - 1.0).min()) * 100.0
        sharpe = (float(log_ret.mean()) / std) * np.sqrt(252) if std > 0 else 0.0
        return {
            "from":   datetime.fromtimestamp(ts[0]).strftime("%Y-%m-%d"),
            "to":     datetime.fromtimestamp(ts[-1]).strftime("%Y-%m-%d"),
            "return": f"{ret_pct:+.2f}%",
            "vol":    f"{vol_pct:.2f}%",
            "max_dd": f"{max_dd_pct:.2f}%",
            "sharpe": f"{sharpe:+.2f}",
        }

    def _gui_stats_panel(self):
        stats = self._compute_range_stats()
        if stats is None:
            return
        imgui.separator()
        imgui.text(f"Range: {stats['from']}  →  {stats['to']}")
        imgui.same_line()
        imgui.text_colored(ImVec4(0.7, 0.7, 0.7, 1.0),
                           f"  |  Return: {stats['return']}    "
                           f"Vol (ann.): {stats['vol']}    "
                           f"Max DD: {stats['max_dd']}    "
                           f"Sharpe: {stats['sharpe']}")
        imgui.separator()

    def gui(self):
        self._poll_data_source()
        self._gui_fetch()
        self._advance_playback()

        if self.data_source.is_loading():
            imgui.text_colored(ImVec4(0.7, 0.7, 0.7, 1.0), f"Loading {self.ticker_input}…")

        if self.fetch_error:
            imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"Error: {self.fetch_error}")

        if self.stock_data and not self.data_source.is_loading():
            self._gui_playback()
            self._gui_stats_panel()

            sd = self.stock_data
            n_full = len(sd.timestamps)
            n = max(2, min(int(self.visible_count_f), n_full))
            showing_partial = n < n_full
            ts = sd.timestamps[:n]

            implot.get_style().use_local_time = False
            if implot.begin_subplots("##Candlestick + Volume", 4, 1, ImVec2(-1, -1),
                                    implot.SubplotFlags_.link_all_x):

                # === Candlestick plot ===
                currency_symbol, axis_fmt = CURRENCY_FORMATS.get(sd.currency, ("", "%.2f"))
                if implot.begin_plot("Price", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, axis_fmt)
                    x_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.x1, "##Date", x_axis_flags)
                    y_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.y1, "Price", y_axis_flags)
                    if showing_partial:
                        # During playback: pin axes to the full-data range so candles
                        # appear within a fixed window instead of growing the axes.
                        implot.setup_axis_limits(implot.ImAxis_.x1, *self._bounds_x, implot.Cond_.always)
                        implot.setup_axis_limits(implot.ImAxis_.y1, *self._bounds_price, implot.Cond_.always)
                    # Bollinger bands (±2σ around SMA20): drawn first so candles render on top
                    upper = sd.bollinger_upper[:n]
                    lower = sd.bollinger_lower[:n]
                    valid = ~np.isnan(upper)
                    if valid.any():
                        xs_b = ts[valid]
                        implot.plot_shaded("Bollinger ±2σ", xs_b, lower[valid], upper[valid],
                                           spec=implot.Spec(fill_alpha=0.6))
                        implot.plot_line("SMA 20", ts, sd.sma_20[:n])

                    plot_candlestick(
                        self.loaded_ticker,
                        ts,
                        sd.opens[:n],
                        sd.closes[:n],
                        sd.lows[:n],
                        sd.highs[:n],
                        currency_symbol=currency_symbol,
                    )
                    implot.plot_line(f"{self.loaded_ticker}-EMA 20", ts, sd.ema_20[:n])
                    implot.plot_line(f"{self.loaded_ticker}-EMA 50", ts, sd.ema_50[:n])

                    # Draggable range selector — drives the stats panel above.
                    # Anchor the rect's vertical span to the current y-axis limits so the
                    # top/bottom edges always sit at the plot edges and only the x edges
                    # are reachable by the user.
                    y_limits = implot.get_plot_limits().y
                    y_pad = (y_limits.max - y_limits.min) * 0.5
                    rect_y1 = y_limits.min - y_pad
                    rect_y2 = y_limits.max + y_pad
                    _, new_x1, _, new_x2, _, *_ = implot.drag_rect(
                        100, self.range_x1, rect_y1, self.range_x2, rect_y2,
                        ImVec4(1.0, 0.9, 0.2, 1.0),
                        implot.DragToolFlags_.no_fit)
                    self.range_x1 = new_x1
                    self.range_x2 = new_x2

                    implot.end_plot()

                # === Volume subplot ===
                if implot.begin_plot("Volume", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "%.0f")
                    y_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.y1, "Volume", y_axis_flags)
                    if showing_partial:
                        implot.setup_axis_limits(implot.ImAxis_.y1, *self._bounds_volume, implot.Cond_.always)
                    implot.plot_bars(f"{self.loaded_ticker} Vol", ts, sd.volumes[:n], 60 * 60 * 24 * 0.8)
                    implot.plot_line(f"{self.loaded_ticker}-Vol EMA 20", ts, sd.volume_ema_20[:n])
                    implot.plot_line(f"{self.loaded_ticker}-Vol EMA 50", ts, sd.volume_ema_50[:n])
                    implot.end_plot()

                # === RSI subplot ===
                if implot.begin_plot("RSI", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "%.0f")
                    implot.setup_axis_limits(implot.ImAxis_.y1, 0, 100)  # RSI range
                    implot.setup_axis(implot.ImAxis_.y1, "RSI")

                    implot.plot_line(f"{self.loaded_ticker} RSI 14", ts, sd.rsi_14[:n])

                    # Overbought/oversold reference lines
                    implot.tag_y(70.0, ImVec4(1.0, 0.0, 0.0, 1.0), "Overbought")
                    implot.drag_line_y(1, 70.0, ImVec4(1.0, 0.0, 0.0, 1.0), 1.0)
                    implot.tag_y(30.0, ImVec4(0.0, 1.0, 0.0, 1.0), "Oversold")
                    implot.drag_line_y(2, 30.0, ImVec4(0.0, 1.0, 0.0, 1.0), 1.0)

                    implot.end_plot()

                # === Drawdown subplot ===
                if implot.begin_plot("Drawdown", ImVec2(-1, 0)):
                    implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
                    implot.setup_axis_format(implot.ImAxis_.y1, "%.1f%%")
                    y_axis_flags = implot.AxisFlags_.auto_fit if self.needs_refresh_x_extent else 0
                    implot.setup_axis(implot.ImAxis_.y1, "Drawdown", y_axis_flags)
                    if showing_partial:
                        implot.setup_axis_limits(implot.ImAxis_.y1, *self._bounds_drawdown, implot.Cond_.always)

                    dd = sd.drawdown_pct[:n]
                    implot.plot_shaded(f"{self.loaded_ticker} Drawdown",
                                       ts, dd, 0.0,
                                       spec=implot.Spec(fill_alpha=0.5))
                    implot.plot_line(f"{self.loaded_ticker} DD", ts, dd)

                    implot.end_plot()

                self.needs_refresh_x_extent = False
                implot.end_subplots()


viewer = StockViewer()
immapp.run(viewer.gui, with_implot=True, window_title="Demo Implot Stock Viewer", window_size=(1200, 800))
