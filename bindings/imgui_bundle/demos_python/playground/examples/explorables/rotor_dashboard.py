"""Rotor run-up monitor: a live vibration-analysis dashboard built with Dear ImGui Bundle.

A simulated three-axis accelerometer sits on the bearing housing of a rotor whose
speed sweeps up and down. The dashboard shows what a vibration analyst would watch:

- the raw acceleration of the last two seconds,
- the spectrum, with the shaft orders and the structural resonance marked,
- the amplitude distribution, against a Gaussian of the same variance,
- a spectrogram, where harmonics sweep with the shaft speed and light up as they
  cross the resonance.

Toggle "Bearing defect" to add periodic impacts: watch the kurtosis leave 3 and the
histogram grow heavy tails, long before the spectrum makes it obvious.

The "Signal chain" page is a node editor for the processing: sensors, filters, envelope,
integration and spectra, wired into plots. Pins are typed (signal or spectrum), and the
editor refuses links of the wrong type or that would make a loop. Its default graph runs
the classic bearing check: band-pass around the mode the impacts ring, take the envelope,
and the defect frequency (3.58 shaft orders) stands out in the envelope's spectrum.

Run it:
    pip install imgui-bundle numpy
    python rotor_dashboard.py

No dependency besides numpy, so it also runs in the browser playground
(https://imgui-bundle.pages.dev/playground/).

Written by Claude (Anthropic) in a plain chat, from the bundle's guide for AI assistants alone
(https://imgui-bundle.pages.dev/llms.txt).
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from imgui_bundle import (
    em_size,
    em_to_vec2,
    hello_imgui,
    icons_fontawesome_4,  # the icon font Hello ImGui loads by default
    imgui,
    imgui_knobs,
    imgui_node_editor as ed,
    imgui_toggle,
    immapp,
    implot,
)

# ---------------------------------------------------------------------------
# Acquisition and analysis settings
# ---------------------------------------------------------------------------
FS = 2000.0  # sampling rate, Hz
HISTORY_S = 2.0  # length of the time-series view, s
SPECTRUM_NFFT = 1024  # FFT size of the spectrum (1.95 Hz resolution)
SPECTRO_NFFT = 512  # FFT size of each spectrogram column
SPECTRO_HOP = 100  # samples between spectrogram columns (20 columns per second)
SPECTRO_COLS = 240  # 12 s of spectrogram
F_VIEW = 400.0  # highest frequency shown, Hz
DB_MIN, DB_MAX = -64.0, -5.0  # spectrogram color range, dB re 1 g

# ---------------------------------------------------------------------------
# Palettes. Dark: a deep slate ground, so the viridis spectrogram carries the color.
# Light: a cool grey ground with white plots. Channel colors come from the Okabe-Ito
# palette, which stays distinct for readers with color-vision deficiencies.
# ---------------------------------------------------------------------------


def hex_color(h: str, alpha: float = 1.0) -> imgui.ImVec4:
    h = h.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return imgui.ImVec4(r, g, b, alpha)


@dataclass(frozen=True)
class Palette:
    window: str  # window background
    panel: str  # panels and plot frames
    plot: str  # inside the plots
    frame: str  # widget frames
    frame_hi: str  # hovered frames
    text: str
    muted: str
    grid: str
    accent: str  # interactive state
    warn: str  # resonance and alerts
    channels: Tuple[str, str, str]
    dark: bool


DARK = Palette(
    window="#0F1A24", panel="#162432", plot="#0F1A24", frame="#213547", frame_hi="#2C4760",
    text="#DCE4EC", muted="#8597A9", grid="#24384B", accent="#56B4E9", warn="#F0E442",
    channels=("#E69F00", "#56B4E9", "#009E73"),  # Okabe-Ito orange, sky blue, bluish green
    dark=True,
)
# On white, sky blue and yellow wash out: the light palette takes the darker Okabe-Ito
# hues (vermillion, blue, bluish green) and a deep amber for the resonance and alerts.
LIGHT = Palette(
    window="#E3E9EF", panel="#F3F6F9", plot="#FFFFFF", frame="#E0E7EE", frame_hi="#CCD8E3",
    text="#17222D", muted="#5A6B7C", grid="#DCE3EA", accent="#0072B2", warn="#A87B00",
    channels=("#D55E00", "#0072B2", "#009E73"),
    dark=False,
)
PAL = DARK  # the active palette; every color is read from it at draw time

CHANNEL_NAMES = ("Axial", "Radial X", "Radial Y")


def channels() -> List[Tuple[str, str]]:
    """(name, color) of each channel, in the active palette."""
    return list(zip(CHANNEL_NAMES, PAL.channels, strict=True))


def set_palette(dark: bool) -> None:
    global PAL
    PAL = DARK if dark else LIGHT


BPFO_ORDER = 3.58  # ball-pass frequency of the outer race, in shaft orders
PAGE_SLIDE_S = 0.28  # duration of the slide between pages; 0 turns the animation off
PAGES = [
    (icons_fontawesome_4.ICON_FA_CHART_LINE, "Monitor"),
    (icons_fontawesome_4.ICON_FA_SITEMAP, "Signal chain"),
]
NARROW_PAGES = [  # on a phone, the plots fill a page, and the controls get a page of their own
    (icons_fontawesome_4.ICON_FA_CHART_LINE, "Plots"),
    (icons_fontawesome_4.ICON_FA_SLIDERS_H, "Controls"),
    (icons_fontawesome_4.ICON_FA_SITEMAP, "Chain"),
]
NARROW_EM = 45.0  # below this width, in em, the narrow layout (a phone): pages above, header on two lines
SIDEBAR_EM = (19.0, 15.0, 34.0)  # initial, min and max width of the sidebar, in em

WINDOWS: Dict[str, Callable[[int], np.ndarray]] = {
    "Hann": np.hanning,
    "Hamming": np.hamming,
    "Blackman": np.blackman,
    "Rectangular": np.ones,
}


# ---------------------------------------------------------------------------
# The simulated machine
# ---------------------------------------------------------------------------
class Rotor:
    """A rotor with imbalance harmonics, a structural resonance and an optional
    outer-race bearing defect, seen by a three-axis accelerometer."""

    # amplitude (g) of shaft orders 1..4 on each channel, before the resonance gain
    ORDER_AMPS = np.array(
        [
            [0.020, 0.030, 0.012, 0.010],  # axial: misalignment shows at 2x
            [0.060, 0.018, 0.010, 0.006],  # radial X: imbalance dominates at 1x
            [0.055, 0.015, 0.012, 0.008],  # radial Y
        ]
    )
    ORDER_PHASES = np.random.default_rng(3).uniform(0, 2 * np.pi, (3, 4))

    def __init__(self) -> None:
        self.rng = np.random.default_rng(7)
        self.t = 0.0
        self.shaft_cycles = 0.0  # integrated shaft rotation, in turns
        self.sweep = True
        self.manual_speed = 25.0
        self.speed_lo, self.speed_hi = 8.0, 60.0
        self.sweep_period = 24.0
        self.res_freq = 118.0
        self.damping = 0.035
        self.noise = 0.012
        self.bearing_defect = False
        self.ring_freq = 650.0  # a high-frequency housing mode, excited by the bearing impacts
        self.ring_decay = 0.004  # s, decay time of that ringing
        self.last_impact_t = -1.0  # carried across chunks, so the ringing continues
        self.last_impact_amp = 0.0

    def speed_at(self, t: np.ndarray) -> np.ndarray:
        if not self.sweep:
            return np.full_like(t, self.manual_speed)
        u = (t % self.sweep_period) / self.sweep_period  # 0..1
        tri = 1.0 - np.abs(2.0 * u - 1.0)  # up then down
        return self.speed_lo + (self.speed_hi - self.speed_lo) * tri

    def resonance_gain(self, f: np.ndarray) -> np.ndarray:
        r = f / self.res_freq
        return 1.0 / np.sqrt((1.0 - r * r) ** 2 + (2.0 * self.damping * r) ** 2)

    def generate(self, n: int) -> np.ndarray:
        """Return n new samples for the three channels, shape (3, n)."""
        t = self.t + np.arange(n) / FS
        f_shaft = self.speed_at(t)
        cycles = self.shaft_cycles + np.cumsum(f_shaft) / FS
        out = np.zeros((3, n))
        for k in range(1, 5):
            gain = self.resonance_gain(k * f_shaft)
            arg = 2.0 * np.pi * k * cycles
            for c in range(3):
                out[c] += self.ORDER_AMPS[c, k - 1] * gain * np.sin(arg + self.ORDER_PHASES[c, k - 1])
        if self.bearing_defect:
            out += np.array([[0.35], [0.9], [0.7]]) * self.bearing_impacts(t, cycles)
        out += self.noise * self.rng.standard_normal((3, n))
        self.t = float(t[-1] + 1.0 / FS)
        self.shaft_cycles = float(cycles[-1])
        return out

    def bearing_impacts(self, t: np.ndarray, cycles: np.ndarray) -> np.ndarray:
        """Each ball passing the outer-race defect strikes it and rings a high-frequency
        housing mode that decays within a few ms. The strike is stronger when the defect
        is in the load zone, once per shaft turn: that adds sidebands at the shaft speed."""
        passes = np.floor(BPFO_ORDER * cycles)
        prev = np.floor(BPFO_ORDER * (cycles[0] - (cycles[1] - cycles[0]) if len(cycles) > 1 else cycles[0]))
        is_impact = np.diff(np.concatenate([[prev], passes])) > 0
        amp_here = np.where(is_impact, 0.75 + 0.25 * np.cos(2.0 * np.pi * cycles), 0.0)
        # time and strength of the latest impact, at each sample
        idx = np.where(is_impact, np.arange(len(t)), -1)
        idx = np.maximum.accumulate(idx)
        since = np.where(idx >= 0, t - t[np.maximum(idx, 0)], t - self.last_impact_t)
        amp = np.where(idx >= 0, amp_here[np.maximum(idx, 0)], self.last_impact_amp)
        if is_impact.any():
            last = int(np.nonzero(is_impact)[0][-1])
            self.last_impact_t, self.last_impact_amp = float(t[last]), float(amp_here[last])
        return amp * np.exp(-since / self.ring_decay) * np.sin(2.0 * np.pi * self.ring_freq * since)

    @property
    def speed_now(self) -> float:
        return float(self.speed_at(np.array([self.t]))[0])


# ---------------------------------------------------------------------------
# Signal processing helpers
# ---------------------------------------------------------------------------
def amplitude_db(x: np.ndarray, window: np.ndarray) -> np.ndarray:
    """Single-sided amplitude spectrum in dB re 1 g, corrected for the window gain."""
    spectrum = np.fft.rfft(x * window)
    amp = 2.0 * np.abs(spectrum) / window.sum()
    db: np.ndarray = 20.0 * np.log10(amp + 1e-9)
    return db


def ease_in_out_cubic(t: float) -> float:
    return 4.0 * t * t * t if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0


def eased_page_position(pos: float) -> float:
    """The pages' position (0 for the first page, 1 for the second...), eased between two neighbor pages"""
    whole = int(pos)
    return whole + ease_in_out_cubic(pos - whole)


def mix(a: imgui.ImVec4, b: imgui.ImVec4, t: float) -> imgui.ImVec4:
    return imgui.ImVec4(*(a[i] + (b[i] - a[i]) * t for i in range(4)))


def kurtosis(x: np.ndarray) -> float:
    d = x - x.mean()
    var = np.mean(d * d)
    return float(np.mean(d**4) / (var * var + 1e-18))


# ---------------------------------------------------------------------------
# Signal chain: a free-form graph of processing nodes with typed pins
#
# Two kinds of data flow through the links: a Signal (samples in time) and a
# Spectrum (amplitude against frequency). A pin accepts only its own kind, so the
# editor refuses, for example, a spectrum going into a filter.
#
# The filters work in the frequency domain on the whole two-second block: simple and
# numpy-only, but zero-phase and non-causal, unlike a real-time filter.
# ---------------------------------------------------------------------------
SIGNAL, SPECTRUM = "signal", "spectrum"
SPECTRUM_PIN_COLOR = "#CC79A7"  # Okabe-Ito reddish purple, readable in both themes


@dataclass
class Signal:
    x: np.ndarray
    fs: float
    unit: str
    path: str  # what produced it, for plot legends, e.g. "Radial X > band-pass > envelope"


@dataclass
class Spectrum:
    f: np.ndarray
    amp: np.ndarray  # single-sided amplitude, linear
    unit: str
    path: str


_next_id = itertools.count(1)  # node, pin and link ids share one counter: the editor needs them unique


@dataclass
class Pin:
    node: "Node"
    name: str
    type: str  # SIGNAL or SPECTRUM
    is_input: bool
    multi: bool = False  # a multi input accepts several links (the plots do)
    id: int = field(default_factory=lambda: next(_next_id))

    def color(self) -> str:
        return PAL.accent if self.type == SIGNAL else SPECTRUM_PIN_COLOR


@dataclass
class Link:
    out_pin: Pin
    in_pin: Pin
    id: int = field(default_factory=lambda: next(_next_id))


class Node:
    """Base class of the graph's nodes. A subclass declares its pins in __init__,
    computes its outputs in evaluate(), and draws its settings in draw_settings()."""

    title = "Node"
    kind = "process"  # "source", "process" or "sink"; sets the color of the title bar
    width_em = 11.0  # nodes share one width, so their pins line up in columns

    def __init__(self) -> None:
        self.id = next(_next_id)
        self.inputs: List[Pin] = []
        self.outputs: List[Pin] = []
        self.values: Dict[str, object] = {}  # output pin name -> Signal / Spectrum / None
        self.message = ""  # shown in the node when it cannot compute
        # placed by the editor next frame; in em, like the node widths, so layouts scale with the font
        self.pending_pos: Optional[Tuple[float, float]] = None

    def add_input(self, name: str, type_: str, multi: bool = False) -> None:
        self.inputs.append(Pin(self, name, type_, True, multi))

    def add_output(self, name: str, type_: str) -> None:
        self.outputs.append(Pin(self, name, type_, False))

    def evaluate(self, ins: Dict[str, List[Any]], ctx: "Dashboard") -> Dict[str, object]:
        return {}

    def draw_settings(self, width: float) -> bool:
        """Draw the node's widgets; return True if a setting changed."""
        return False


def node_color(kind: str) -> str:
    return {"source": PAL.channels[2], "process": PAL.accent, "sink": SPECTRUM_PIN_COLOR}[kind]


def labeled_combo(label: str, current: int, items: List[str], width: float) -> Tuple[bool, int]:
    imgui.set_next_item_width(width * 0.62)
    return imgui.combo(label, current, items)


class SensorNode(Node):
    title, kind = "Sensor", "source"

    def __init__(self, channel: int = 1) -> None:
        super().__init__()
        self.channel = channel
        self.add_output("signal", SIGNAL)

    def evaluate(self, ins, ctx):
        return {"signal": Signal(ctx.buffer[self.channel].copy(), FS, "g", CHANNEL_NAMES[self.channel])}

    def draw_settings(self, width):
        changed, self.channel = labeled_combo("Channel", self.channel, list(CHANNEL_NAMES), width)
        return changed


def raised_cosine_step(f: np.ndarray, edge: float, width: float) -> np.ndarray:
    """0 below edge - width/2, 1 above edge + width/2, smooth in between."""
    u = np.clip((f - edge) / width + 0.5, 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * u)


class FilterNode(Node):
    title = "Filter"
    MODES = ["Low-pass", "High-pass", "Band-pass", "Band-stop"]

    def __init__(self, mode: int = 2, f_lo: float = 70.0, f_hi: float = 170.0) -> None:
        super().__init__()
        self.mode, self.f_lo, self.f_hi = mode, f_lo, f_hi
        self.add_input("in", SIGNAL)
        self.add_output("out", SIGNAL)

    def gain(self, f: np.ndarray) -> np.ndarray:
        def tw(edge: float) -> float:  # transition width: 10 % of the edge, at least 4 Hz
            return max(4.0, 0.1 * edge)

        low_pass = 1.0 - raised_cosine_step(f, self.f_hi, tw(self.f_hi))
        high_pass = raised_cosine_step(f, self.f_lo, tw(self.f_lo))
        if self.mode == 0:
            return low_pass
        if self.mode == 1:
            return high_pass
        band = high_pass * low_pass
        return band if self.mode == 2 else 1.0 - band

    def evaluate(self, ins, ctx):
        s: Signal = ins["in"][0]
        spectrum = np.fft.rfft(s.x)
        f = np.fft.rfftfreq(len(s.x), 1.0 / s.fs)
        y = np.fft.irfft(spectrum * self.gain(f), n=len(s.x))
        return {"out": Signal(y, s.fs, s.unit, f"{s.path} > {self.MODES[self.mode].lower()}")}

    def draw_settings(self, width):
        changed, self.mode = labeled_combo("Mode", self.mode, self.MODES, width)
        imgui.set_next_item_width(width * 0.62)
        if self.mode == 0:
            c, self.f_hi = imgui.drag_float("Cutoff", self.f_hi, 1.0, 1.0, FS / 2, "%.0f Hz")
        elif self.mode == 1:
            c, self.f_lo = imgui.drag_float("Cutoff", self.f_lo, 1.0, 1.0, FS / 2, "%.0f Hz")
        else:
            c, self.f_lo, self.f_hi = imgui.drag_float_range2(
                "Band", self.f_lo, self.f_hi, 1.0, 1.0, FS / 2, "%.0f", "%.0f Hz", imgui.SliderFlags_.always_clamp
            )
        self.draw_response(width)
        return changed or c

    def draw_response(self, width: float) -> None:
        """A small picture of the filter's gain from 0 to fs/2."""
        h = em_size(2.2)
        p0 = imgui.get_cursor_screen_pos()
        imgui.dummy(imgui.ImVec2(width, h))
        dl = imgui.get_window_draw_list()
        dl.add_rect_filled(p0, imgui.ImVec2(p0.x + width, p0.y + h), imgui.get_color_u32(hex_color(PAL.plot)), 3.0)
        f = np.linspace(0.0, FS / 2, 160)
        g = self.gain(f)
        points: List[imgui.ImVec2Like] = [
            imgui.ImVec2(p0.x + width * i / (len(f) - 1), p0.y + h - 2 - (h - 4) * gi) for i, gi in enumerate(g)]
        dl.add_polyline(points, imgui.get_color_u32(hex_color(PAL.accent)), 1.5, 0)
        imgui.text_colored(hex_color(PAL.muted), f"gain, 0 to {FS / 2:.0f} Hz")


class EnvelopeNode(Node):
    title = "Envelope"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("in", SIGNAL)
        self.add_output("out", SIGNAL)

    def evaluate(self, ins, ctx):
        s: Signal = ins["in"][0]
        n = len(s.x)
        spectrum = np.fft.fft(s.x)
        h = np.zeros(n)  # analytic signal: keep DC and Nyquist, double the positive frequencies
        h[0] = 1.0
        h[1 : (n + 1) // 2] = 2.0
        if n % 2 == 0:
            h[n // 2] = 1.0
        env = np.abs(np.fft.ifft(spectrum * h))
        return {"out": Signal(env - env.mean(), s.fs, s.unit, f"{s.path} > envelope")}

    def draw_settings(self, width):
        imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
        imgui.text_colored(hex_color(PAL.muted), "Amplitude envelope (Hilbert), mean removed.")
        imgui.pop_text_wrap_pos()
        return False


class IntegrateNode(Node):
    title = "Integrate"

    def __init__(self, f_min: float = 5.0) -> None:
        super().__init__()
        self.f_min = f_min
        self.add_input("in", SIGNAL)
        self.add_output("out", SIGNAL)

    def evaluate(self, ins, ctx):
        s: Signal = ins["in"][0]
        n = len(s.x)
        f = np.fft.rfftfreq(n, 1.0 / s.fs)
        spectrum = np.fft.rfft(s.x)
        with np.errstate(divide="ignore", invalid="ignore"):
            integrator = np.where(f > 0, 1.0 / (2j * np.pi * f), 0.0)
        y = np.fft.irfft(spectrum * integrator * raised_cosine_step(f, self.f_min, 2.0), n=n)
        if s.unit == "g":  # acceleration in g -> velocity in mm/s
            return {"out": Signal(y * 9.80665 * 1000.0, s.fs, "mm/s", f"{s.path} > velocity")}
        return {"out": Signal(y, s.fs, f"{s.unit}·s", f"{s.path} > integral")}

    def draw_settings(self, width):
        imgui.set_next_item_width(width * 0.62)
        changed, self.f_min = imgui.drag_float("From", self.f_min, 0.2, 0.5, 100.0, "%.1f Hz")
        if imgui.is_item_hovered():
            imgui.set_tooltip("Content below this frequency is removed, so the integral doesn't drift.")
        return changed


class SpectrumNode(Node):
    title = "Spectrum"
    SIZES = [512, 1024, 2048, 4096]

    def __init__(self, size_index: int = 2) -> None:
        super().__init__()
        self.size_index = size_index
        self.window_name = "Hann"
        self.add_input("in", SIGNAL)
        self.add_output("spectrum", SPECTRUM)

    def evaluate(self, ins, ctx):
        s: Signal = ins["in"][0]
        n = min(self.SIZES[self.size_index], len(s.x))
        window = WINDOWS[self.window_name](n)
        amp = 2.0 * np.abs(np.fft.rfft(s.x[-n:] * window)) / window.sum()
        return {"spectrum": Spectrum(np.fft.rfftfreq(n, 1.0 / s.fs), amp, s.unit, s.path)}

    def draw_settings(self, width):
        names = list(WINDOWS)
        c1, i = labeled_combo("Window", names.index(self.window_name), names, width)
        self.window_name = names[i]
        c2, self.size_index = labeled_combo("Size", self.size_index, [str(n) for n in self.SIZES], width)
        resolution = FS / self.SIZES[self.size_index]
        imgui.text_colored(hex_color(PAL.muted), f"resolution {resolution:.2f} Hz")
        return c1 or c2


class TimePlotNode(Node):
    title, kind = "Time plot", "sink"

    def __init__(self, name: str = "Time plot", seconds: float = 0.5) -> None:
        super().__init__()
        self.name, self.seconds = name, seconds
        self.traces: List[Signal] = []
        self.add_input("signals", SIGNAL, multi=True)

    def evaluate(self, ins, ctx):
        self.traces = ins["signals"]
        return {}

    def draw_settings(self, width):
        imgui.text(self.name)
        imgui.set_next_item_width(width * 0.62)
        changed, self.seconds = imgui.drag_float("Shown", self.seconds, 0.01, 0.05, HISTORY_S, "%.2f s")
        return changed

    def plot(self, size: imgui.ImVec2, ctx: "Dashboard") -> None:
        if implot.begin_plot(f"{self.name}##{self.id}", size):
            unit = self.traces[0].unit if self.traces else ""
            implot.setup_axes("time (s)", unit, 0, implot.AxisFlags_.auto_fit)
            implot.setup_axis_limits(implot.ImAxis_.x1, -self.seconds, 0.0, imgui.Cond_.always)
            implot.setup_legend(implot.Location_.north_west)
            for k, s in enumerate(self.traces):
                n = min(len(s.x), int(self.seconds * s.fs) + 1)
                t = (np.arange(n) - n + 1) / s.fs
                spec = implot.Spec(line_color=hex_color(trace_color(k)), line_weight=1.2)
                implot.plot_line(f"{s.path}##{k}", t, s.x[-n:].astype(np.float64), spec)
            implot.end_plot()


class SpectrumPlotNode(Node):
    title, kind = "Spectrum plot", "sink"
    MARKS = ["No markers", "Shaft orders", "Bearing defect orders"]

    def __init__(self, name: str = "Spectrum plot", db: bool = True, marks: int = 1, f_max: float = 400.0) -> None:
        super().__init__()
        self.name, self.db, self.marks, self.f_max = name, db, marks, f_max
        self.traces: List[Spectrum] = []
        self.add_input("spectra", SPECTRUM, multi=True)

    def evaluate(self, ins, ctx):
        self.traces = ins["spectra"]
        return {}

    def draw_settings(self, width):
        imgui.text(self.name)
        c1, self.db = imgui.checkbox("Decibels", self.db)
        c2, self.marks = labeled_combo("Mark", self.marks, self.MARKS, width)
        imgui.set_next_item_width(width * 0.62)
        c3, self.f_max = imgui.drag_float("Up to", self.f_max, 2.0, 20.0, FS / 2, "%.0f Hz")
        return c1 or c2 or c3

    def plot(self, size: imgui.ImVec2, ctx: "Dashboard") -> None:
        if implot.begin_plot(f"{self.name}##{self.id}", size):
            unit = self.traces[0].unit if self.traces else ""
            implot.setup_axes("frequency (Hz)", f"dB re 1 {unit}" if self.db else unit)
            implot.setup_axis_limits(implot.ImAxis_.x1, 0.0, self.f_max, imgui.Cond_.always)
            y_flags = implot.AxisFlags_.auto_fit
            implot.setup_axis(implot.ImAxis_.y1, None, y_flags)
            implot.setup_legend(implot.Location_.north_east)
            if self.marks:
                order = 1.0 if self.marks == 1 else BPFO_ORDER
                lines = ctx.rotor.speed_now * order * np.arange(1.0, 6.0)
                label = "Shaft orders" if self.marks == 1 else "Bearing defect orders"
                implot.plot_inf_lines(label, lines, implot.Spec(line_color=hex_color(PAL.warn, 0.45)))
            for k, sp in enumerate(self.traces):
                view = sp.f <= self.f_max
                y = 20.0 * np.log10(sp.amp[view] + 1e-9) if self.db else sp.amp[view]
                spec = implot.Spec(line_color=hex_color(trace_color(k)), line_weight=1.3)
                implot.plot_line(f"{sp.path}##{k}", sp.f[view], y, spec)
            implot.end_plot()


NODE_TYPES = [SensorNode, FilterNode, EnvelopeNode, IntegrateNode, SpectrumNode, TimePlotNode, SpectrumPlotNode]


def trace_color(k: int) -> str:
    extra = ("#CC79A7", PAL.warn)
    colors = PAL.channels + extra
    return colors[k % len(colors)]


class Graph:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.links: List[Link] = []
        self.dirty = True  # set when the structure or a setting changes: evaluate again

    # ----- structure ----------------------------------------------------------
    def add(self, node: Node, pos: Tuple[float, float]) -> Node:
        node.pending_pos = pos
        self.nodes.append(node)
        self.dirty = True
        return node

    def pin(self, pin_id: int) -> Optional[Pin]:
        for node in self.nodes:
            for p in node.inputs + node.outputs:
                if p.id == pin_id:
                    return p
        return None

    def check_link(self, a: Pin, b: Pin) -> Tuple[Optional[Link], str]:
        """Return (link, "") if a and b can be connected, else (None, reason)."""
        if a.is_input == b.is_input:
            return None, "Connect an output to an input"
        out_pin, in_pin = (b, a) if a.is_input else (a, b)
        if out_pin.node is in_pin.node:
            return None, "A node can't feed itself"
        if out_pin.type != in_pin.type:
            return None, f"A {out_pin.type} can't go into a {in_pin.type} input"
        if any(lnk.out_pin is out_pin and lnk.in_pin is in_pin for lnk in self.links):
            return None, "Already connected"
        if self.reaches(in_pin.node, out_pin.node):
            return None, "This link would make a loop"
        return Link(out_pin, in_pin), ""

    def reaches(self, start: Node, target: Node) -> bool:
        """True if target can be reached from start by following links downstream."""
        stack, seen = [start], set()
        while stack:
            node = stack.pop()
            if node is target:
                return True
            if node.id in seen:
                continue
            seen.add(node.id)
            stack.extend(lnk.in_pin.node for lnk in self.links if lnk.out_pin.node is node)
        return False

    def connect(self, link: Link) -> None:
        if not link.in_pin.multi:  # a single input takes the newest link
            self.links = [lnk for lnk in self.links if lnk.in_pin is not link.in_pin]
        self.links.append(link)
        self.dirty = True

    def remove_link(self, link_id: int) -> None:
        self.links = [lnk for lnk in self.links if lnk.id != link_id]
        self.dirty = True

    def remove_node(self, node_id: int) -> None:
        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.links = [lnk for lnk in self.links if lnk.out_pin.node.id != node_id and lnk.in_pin.node.id != node_id]
        self.dirty = True

    def connected(self, pin: Pin) -> bool:
        return any(lnk.in_pin is pin or lnk.out_pin is pin for lnk in self.links)

    # ----- evaluation -----------------------------------------------------------
    def topological_order(self) -> List[Node]:
        indegree = {n.id: 0 for n in self.nodes}
        for lnk in self.links:
            indegree[lnk.in_pin.node.id] += 1
        ready = [n for n in self.nodes if indegree[n.id] == 0]
        order = []
        while ready:
            node = ready.pop(0)
            order.append(node)
            for lnk in self.links:
                if lnk.out_pin.node is node:
                    indegree[lnk.in_pin.node.id] -= 1
                    if indegree[lnk.in_pin.node.id] == 0:
                        ready.append(lnk.in_pin.node)
        return order  # links are checked for loops when created, so every node is here

    def evaluate(self, ctx: "Dashboard") -> None:
        for node in self.topological_order():
            ins = {
                p.name: [
                    lnk.out_pin.node.values.get(lnk.out_pin.name)
                    for lnk in self.links
                    if lnk.in_pin is p and lnk.out_pin.node.values.get(lnk.out_pin.name) is not None
                ]
                for p in node.inputs
            }
            missing = [p.name for p in node.inputs if not p.multi and not ins[p.name]]
            if missing:
                node.values, node.message = {}, "Connect its input"
                continue
            try:
                node.values, node.message = node.evaluate(ins, ctx), ""
            except Exception as e:  # a node that fails shows why, the others keep working
                node.values, node.message = {}, f"Error: {e}"
        self.dirty = False


def default_graph() -> Graph:
    """The raw spectrum; the classic bearing check (band-pass around the high-frequency
    mode the impacts ring, take the envelope, look at its spectrum); and the velocity,
    which ISO vibration standards use."""
    g = Graph()
    col = 15.0  # column step, in em: one node width (11 em) plus a gap
    row1, row2 = 14.0, 31.0  # rows, in em
    sensor = g.add(SensorNode(channel=1), (0, row1))
    raw_spec = g.add(SpectrumNode(size_index=2), (col, 0))
    raw_plot = g.add(SpectrumPlotNode("Raw spectrum", db=True, marks=1, f_max=1000.0), (2 * col, 0))
    # The band must reach beyond the 650 Hz carrier by the highest envelope frequency we want
    # to see: here three defect harmonics, about 3 x 107 Hz on each side.
    band = g.add(FilterNode(mode=2, f_lo=320.0, f_hi=960.0), (col, row1))
    env = g.add(EnvelopeNode(), (2 * col, row1))
    env_spec = g.add(SpectrumNode(size_index=3), (3 * col, row1))
    env_plot = g.add(SpectrumPlotNode("Envelope spectrum", db=False, marks=2, f_max=400.0), (4 * col, row1))
    integ = g.add(IntegrateNode(f_min=5.0), (col, row2))
    vel_plot = g.add(TimePlotNode("Velocity", seconds=0.5), (2 * col, row2))
    for a, b in [
        (sensor, raw_spec), (raw_spec, raw_plot), (sensor, band), (band, env),
        (env, env_spec), (env_spec, env_plot), (sensor, integ), (integ, vel_plot),
    ]:
        link, reason = g.check_link(a.outputs[0], b.inputs[0])
        assert link is not None, reason
        g.connect(link)
    return g


class GraphEditor:
    """Draws the graph in imgui-node-editor and turns the user's gestures into graph edits."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.frame = 0
        self.fit = "readable"  # the view to set once node sizes are known: "readable", "all" or ""
        self.popup_pos = imgui.ImVec2(0, 0)
        self.context_node = 0

    def draw(self, size: imgui.ImVec2) -> None:
        g = self.graph
        ed.begin("signal_chain", size)
        for node in list(g.nodes):
            self.draw_node(node)
        for link in g.links:
            ed.link(ed.LinkId(link.id), ed.PinId(link.out_pin.id), ed.PinId(link.in_pin.id),
                    hex_color(link.out_pin.color(), 0.85), 2.0)
        self.handle_create()
        self.handle_delete()
        self.handle_context_menus()
        if self.fit and self.frame >= 2:  # node sizes are known after the first frames
            self.apply_fit(size)
        ed.end()
        self.frame += 1

    MIN_READABLE_SCALE = 0.8  # below this, node text gets hard to read

    def apply_fit(self, size: imgui.ImVec2) -> None:
        """Fit the whole graph, unless that would shrink it below a readable size: then fit
        the start of the chain (the nodes on the left), and the rest is a pan away."""
        mode, self.fit = self.fit, ""
        nodes = self.graph.nodes
        if not nodes:
            return
        boxes = []
        for n in nodes:
            p, sz = ed.get_node_position(ed.NodeId(n.id)), ed.get_node_size(ed.NodeId(n.id))
            boxes.append((n, p.x, p.y, p.x + sz.x, p.y + sz.y))
        margin = em_size(3.0)
        left, top = min(b[1] for b in boxes), min(b[2] for b in boxes)
        right, bottom = max(b[3] for b in boxes), max(b[4] for b in boxes)
        scale = min(size.x / (right - left + margin), size.y / (bottom - top + margin))
        if mode == "all" or scale >= self.MIN_READABLE_SCALE:
            ed.navigate_to_content(0.0)
            return
        reach = left + size.x / self.MIN_READABLE_SCALE - margin  # what fits at a readable scale
        ed.clear_selection()
        for n, _x0, _, x1, _ in boxes:
            if x1 <= reach:
                ed.select_node(ed.NodeId(n.id), True)
        ed.navigate_to_selection(True, 0.0)
        ed.clear_selection()

    def draw_node(self, node: Node) -> None:
        nid = ed.NodeId(node.id)
        if node.pending_pos is not None:
            x, y = node.pending_pos
            ed.set_node_position(nid, imgui.ImVec2(em_size(x), em_size(y)))
            node.pending_pos = None
        width = em_size(node.width_em)
        ed.begin_node(nid)
        imgui.push_id(node.id)
        top_left = imgui.get_cursor_screen_pos()

        # title, with a colored bar telling sources, processing and plots apart
        dl = imgui.get_window_draw_list()
        bar = imgui.ImVec2(top_left.x, top_left.y + em_size(0.15))
        dl.add_rect_filled(bar, imgui.ImVec2(bar.x + em_size(0.3), bar.y + em_size(1.0)),
                           imgui.get_color_u32(hex_color(node_color(node.kind))), 2.0)
        imgui.set_cursor_screen_pos(imgui.ImVec2(top_left.x + em_size(0.6), top_left.y))
        imgui.text(node.title)
        imgui.set_cursor_screen_pos(imgui.ImVec2(top_left.x, imgui.get_cursor_screen_pos().y))
        imgui.dummy(imgui.ImVec2(width, em_size(0.1)))

        # pins: inputs on the left, outputs on the right, on shared rows
        rows = max(len(node.inputs), len(node.outputs))
        for r in range(rows):
            y = imgui.get_cursor_screen_pos().y
            if r < len(node.inputs):
                self.draw_pin(node.inputs[r])
            if r < len(node.outputs):
                pin = node.outputs[r]
                label_w = imgui.calc_text_size(pin.name).x + em_size(1.2)
                imgui.set_cursor_screen_pos(imgui.ImVec2(top_left.x + width - label_w, y))
                self.draw_pin(pin)
            imgui.set_cursor_screen_pos(imgui.ImVec2(top_left.x, max(imgui.get_cursor_screen_pos().y, y + imgui.get_frame_height())))

        imgui.spacing()
        if node.draw_settings(width):
            self.graph.dirty = True
        if node.message:
            imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
            imgui.text_colored(hex_color(PAL.warn), node.message)
            imgui.pop_text_wrap_pos()
        imgui.pop_id()
        ed.end_node()

    def draw_pin(self, pin: Pin) -> None:
        r = em_size(0.32)
        ed.begin_pin(ed.PinId(pin.id), ed.PinKind.input if pin.is_input else ed.PinKind.output)
        if not pin.is_input:
            imgui.text_colored(hex_color(PAL.muted), pin.name)
            imgui.same_line()
        p = imgui.get_cursor_screen_pos()
        imgui.dummy(imgui.ImVec2(2 * r + 2, imgui.get_text_line_height()))
        center = imgui.ImVec2(p.x + r + 1, p.y + 0.5 * imgui.get_text_line_height())
        ed.pin_pivot_rect(imgui.ImVec2(center.x, center.y), imgui.ImVec2(center.x, center.y))
        col = imgui.get_color_u32(hex_color(pin.color()))
        dl = imgui.get_window_draw_list()
        if pin.type == SIGNAL:  # circle for signals, diamond for spectra: shape tells the type too
            if self.graph.connected(pin):
                dl.add_circle_filled(center, r, col)
            else:
                dl.add_circle(center, r, col, 0, 1.5)
        else:
            pts: List[imgui.ImVec2Like] = [imgui.ImVec2(center.x, center.y - r * 1.2), imgui.ImVec2(center.x + r * 1.2, center.y),
                   imgui.ImVec2(center.x, center.y + r * 1.2), imgui.ImVec2(center.x - r * 1.2, center.y)]
            if self.graph.connected(pin):
                dl.add_convex_poly_filled(pts, col)
            else:
                dl.add_polyline(pts, col, 1.5, imgui.ImDrawFlags_.closed)
        if pin.is_input:
            imgui.same_line()
            label = pin.name + (" (several)" if pin.multi else "")
            imgui.text_colored(hex_color(PAL.muted), label)
        ed.end_pin()

    def handle_create(self) -> None:
        g = self.graph
        if ed.begin_create(hex_color(PAL.accent), 2.0):
            start, end = ed.PinId(), ed.PinId()
            if ed.query_new_link(start, end) and start.id() and end.id():
                a, b = g.pin(start.id()), g.pin(end.id())
                link, reason = g.check_link(a, b) if a and b else (None, "Unknown pin")
                if link is None:
                    ed.reject_new_item(hex_color(PAL.warn), 2.0)
                    ed.suspend()
                    imgui.set_tooltip(reason)
                    ed.resume()
                elif ed.accept_new_item(hex_color(link.out_pin.color()), 2.5):
                    g.connect(link)
            ed.end_create()  # only when begin_create() returned True

    def handle_delete(self) -> None:
        g = self.graph
        if ed.begin_delete():
            link_id = ed.LinkId()
            while ed.query_deleted_link(link_id):
                if ed.accept_deleted_item():
                    g.remove_link(link_id.id())
            node_id = ed.NodeId()
            while ed.query_deleted_node(node_id):
                if ed.accept_deleted_item():
                    g.remove_node(node_id.id())
            ed.end_delete()  # only when begin_delete() returned True

    def handle_context_menus(self) -> None:
        mouse_canvas = imgui.get_mouse_pos()  # inside the editor, this is in canvas coordinates
        ed.suspend()
        node_id = ed.NodeId()
        if ed.show_node_context_menu(node_id):
            self.context_node = node_id.id()
            imgui.open_popup("node_menu")
        elif ed.show_background_context_menu():
            self.popup_pos = mouse_canvas
            imgui.open_popup("add_node")
        if imgui.begin_popup("add_node"):
            imgui.text_colored(hex_color(PAL.muted), "Add a node")
            imgui.separator()
            for cls in NODE_TYPES:
                if imgui.menu_item_simple(cls.title):
                    em = em_size()
                    self.graph.add(cls(), (self.popup_pos.x / em, self.popup_pos.y / em))
            imgui.end_popup()
        if imgui.begin_popup("node_menu"):
            if imgui.menu_item_simple("Delete"):
                ed.delete_node(ed.NodeId(self.context_node))
            imgui.end_popup()
        ed.resume()


# ---------------------------------------------------------------------------
# The dashboard
# ---------------------------------------------------------------------------
class Dashboard:
    def __init__(self) -> None:
        self.rotor = Rotor()
        self.styled = False
        self.paused = False
        self.window_name = "Hann"
        self.spectro_channel = 1
        self.hist_channel = 1
        self.show_orders = True

        self.hist_n = int(FS * HISTORY_S)
        self.buffer = np.zeros((3, self.hist_n))
        self.t_axis = np.linspace(-HISTORY_S, 0.0, self.hist_n)
        self.sample_debt = 0.0
        self.since_column = 0

        self.spectro_freqs = np.fft.rfftfreq(SPECTRO_NFFT, 1.0 / FS)
        self.spectro_rows = int(np.searchsorted(self.spectro_freqs, F_VIEW)) + 1
        self.spectro = np.full((self.spectro_rows, SPECTRO_COLS), DB_MIN)
        self.speed_track = np.full(SPECTRO_COLS, np.nan)
        self.spectro_t = (np.arange(SPECTRO_COLS) - SPECTRO_COLS + 1) * SPECTRO_HOP / FS

        self.spectrum_freqs = np.fft.rfftfreq(SPECTRUM_NFFT, 1.0 / FS)
        self.spectrum_view = int(np.searchsorted(self.spectrum_freqs, F_VIEW)) + 1

        self.narrow = False  # the phone layout (see NARROW_EM)
        self.page = 0  # its index in PAGES, or in NARROW_PAGES on a phone
        self.page_pos = 0.0  # animated position between pages: 0 shows the monitor, 1 the chain
        self.graph = default_graph()
        self.graph_editor = GraphEditor(self.graph)
        self.new_data = True
        self.last_graph_eval = 0.0

        # Start with a full history, so the first frame already tells the story.
        self.acquire(int(SPECTRO_COLS * SPECTRO_HOP))

    # ----- acquisition --------------------------------------------------
    def acquire(self, n: int) -> None:
        while n > 0:
            chunk = min(n, SPECTRO_HOP - self.since_column)
            new = self.rotor.generate(chunk)
            self.buffer = np.concatenate([self.buffer[:, chunk:], new], axis=1)
            self.since_column += chunk
            n -= chunk
            if self.since_column == SPECTRO_HOP:
                self.since_column = 0
                self.push_spectro_column()

    def push_spectro_column(self) -> None:
        x = self.buffer[self.spectro_channel, -SPECTRO_NFFT:]
        db = amplitude_db(x, WINDOWS[self.window_name](SPECTRO_NFFT))[: self.spectro_rows]
        self.spectro = np.roll(self.spectro, -1, axis=1)
        self.spectro[:, -1] = db
        self.speed_track = np.roll(self.speed_track, -1)
        # the column describes its FFT window: track the speed at the window's centre
        t_center = self.rotor.t - 0.5 * SPECTRO_NFFT / FS
        self.speed_track[-1] = float(self.rotor.speed_at(np.array([t_center]))[0])

    def update(self) -> None:
        if self.paused:
            return
        dt = min(imgui.get_io().delta_time, 0.1)  # don't flood after a stall
        self.sample_debt += dt * FS
        n = int(self.sample_debt)
        self.sample_debt -= n
        if n > 0:
            self.acquire(n)
            self.new_data = True

    # ----- style ----------------------------------------------------------
    def set_theme(self, dark: bool) -> None:
        set_palette(dark)
        self.apply_style()

    def apply_style(self) -> None:
        style = imgui.get_style()
        style.window_rounding = 0.0
        style.child_rounding = 6.0
        style.frame_rounding = 4.0
        style.grab_rounding = 4.0
        style.grab_min_size = em_size(0.35)  # a thin grab leaves the value text readable
        style.window_border_size = 0.0
        style.child_border_size = 0.0
        style.window_padding = em_to_vec2(0.9, 0.8)
        style.frame_padding = em_to_vec2(0.55, 0.3)
        style.item_spacing = em_to_vec2(0.6, 0.55)
        style.cell_padding = em_to_vec2(0.4, 0.25)

        if PAL.dark:
            imgui.style_colors_dark()
            implot.style_colors_dark()
        else:
            imgui.style_colors_light()
            implot.style_colors_light()

        C = imgui.Col_
        colors = {
            C.window_bg: hex_color(PAL.window),
            C.child_bg: hex_color(PAL.panel),
            C.popup_bg: hex_color(PAL.panel),
            C.text: hex_color(PAL.text),
            C.text_disabled: hex_color(PAL.muted),
            C.frame_bg: hex_color(PAL.frame),
            C.frame_bg_hovered: hex_color(PAL.frame_hi),
            C.frame_bg_active: hex_color(PAL.frame_hi),
            C.slider_grab: hex_color(PAL.accent, 0.85),
            C.slider_grab_active: hex_color(PAL.accent),
            C.check_mark: hex_color(PAL.accent),
            C.button: hex_color(PAL.frame),
            C.button_hovered: hex_color(PAL.frame_hi),
            C.button_active: hex_color(PAL.accent, 0.6),
            C.header: hex_color(PAL.frame),
            C.header_hovered: hex_color(PAL.frame_hi),
            C.header_active: hex_color(PAL.frame_hi),
            C.separator: hex_color(PAL.grid),
            C.separator_hovered: hex_color(PAL.accent, 0.7),  # the sidebar's resizable edge
            C.separator_active: hex_color(PAL.accent),
            C.border: hex_color(PAL.grid),
            C.table_header_bg: hex_color(PAL.frame),
            C.table_border_light: hex_color(PAL.grid),
            C.table_border_strong: hex_color(PAL.grid),
            C.table_row_bg: hex_color(PAL.panel, 0.0),
            C.table_row_bg_alt: hex_color(PAL.frame, 0.35),
        }
        for idx, col in colors.items():
            style.set_color_(idx, col)

        ps = implot.get_style()
        P = implot.Col_
        ps.set_color_(P.frame_bg, hex_color(PAL.panel))
        ps.set_color_(P.plot_bg, hex_color(PAL.plot))
        ps.set_color_(P.plot_border, hex_color(PAL.grid))
        ps.set_color_(P.legend_bg, hex_color(PAL.panel, 0.85))
        ps.set_color_(P.legend_border, hex_color(PAL.grid))
        ps.set_color_(P.axis_grid, hex_color(PAL.grid))
        ps.set_color_(P.axis_text, hex_color(PAL.muted))
        ps.set_color_(P.title_text, hex_color(PAL.text))
        ps.set_color_(P.axis_bg_hovered, hex_color(PAL.frame_hi, 0.35))
        ps.set_color_(P.axis_bg_active, hex_color(PAL.frame_hi, 0.55))
        ps.plot_padding = em_to_vec2(0.6, 0.6)

        def knob_colors(h: str, hover: str, active: str) -> imgui_knobs.color_set:
            return imgui_knobs.color_set(
                imgui.ImColor(hex_color(h)), imgui.ImColor(hex_color(hover)), imgui.ImColor(hex_color(active))
            )

        if ed.get_current_editor() is not None:  # the node editor derives its colors from ImGui's
            ed.update_node_editor_colors_from_imgui_colors()

        imgui_knobs.set_knob_colors(
            imgui_knobs.KnobColors(
                primary=knob_colors(PAL.accent, PAL.accent, PAL.text),  # the indicator
                secondary=knob_colors(PAL.frame, PAL.frame_hi, PAL.frame_hi),  # the knob body
                track=knob_colors(PAL.grid, PAL.grid, PAL.grid),  # the arc behind it
            )
        )

    # ----- pages ------------------------------------------------------------
    def page_labels(self) -> List[Tuple[str, str]]:
        return NARROW_PAGES if self.narrow else PAGES

    def page_functions(self) -> List[Callable[[], None]]:
        if self.narrow:
            return [self.gui_plots, self.gui_controls_page, self.gui_signal_chain]
        return [self.gui_monitor, self.gui_signal_chain]

    def segment_width(self) -> float:
        return em_size(6.2 if self.narrow else 9.0)

    def page_switch_width(self) -> float:
        return len(self.page_labels()) * self.segment_width() + 2 * em_size(0.2)

    def gui_page_switch(self) -> None:
        """A segmented control. Its highlight slides with the pages, on the same easing."""
        pad, seg_w, h = em_size(0.2), self.segment_width(), imgui.get_frame_height()
        n = len(self.page_labels())
        p0 = imgui.get_cursor_screen_pos()
        dl = imgui.get_window_draw_list()
        rounding = 0.5 * h + pad
        dl.add_rect_filled(p0, imgui.ImVec2(p0.x + n * seg_w + 2 * pad, p0.y + h + 2 * pad),
                           imgui.get_color_u32(hex_color(PAL.frame)), rounding)
        e = eased_page_position(self.page_pos)
        pill = imgui.ImVec2(p0.x + pad + e * seg_w, p0.y + pad)
        dl.add_rect_filled(pill, imgui.ImVec2(pill.x + seg_w, pill.y + h),
                           imgui.get_color_u32(hex_color(PAL.frame_hi)), 0.5 * h)

        for i, (icon, label) in enumerate(self.page_labels()):
            seg = imgui.ImVec2(p0.x + pad + i * seg_w, p0.y + pad)
            imgui.set_cursor_screen_pos(seg)
            if imgui.invisible_button(f"###page{i}", imgui.ImVec2(seg_w, h)):
                self.page = i
            if imgui.is_item_hovered() and i != self.page:
                dl.add_rect_filled(seg, imgui.ImVec2(seg.x + seg_w, seg.y + h),
                                   imgui.get_color_u32(hex_color(PAL.frame_hi, 0.45)), 0.5 * h)
            # how selected this segment looks, following the slide: 1 when the pill is on it
            weight = max(0.0, 1.0 - abs(i - e))
            icon_col = mix(hex_color(PAL.muted), hex_color(PAL.accent), weight)
            text_col = mix(hex_color(PAL.muted), hex_color(PAL.text), weight)
            icon_w, text_w = imgui.calc_text_size(icon).x, imgui.calc_text_size(label).x
            gap = em_size(0.45)
            x = seg.x + 0.5 * (seg_w - icon_w - gap - text_w)
            y = seg.y + 0.5 * (h - imgui.get_text_line_height())
            dl.add_text(imgui.ImVec2(x, y), imgui.get_color_u32(icon_col), icon)
            dl.add_text(imgui.ImVec2(x + icon_w + gap, y), imgui.get_color_u32(text_col), label)

        imgui.set_cursor_screen_pos(p0)
        imgui.dummy(imgui.ImVec2(n * seg_w + 2 * pad, h + 2 * pad))

    def gui_pages(self) -> None:
        """Both pages sit side by side; during a switch both are drawn, shifted by the eased
        position, and the container clips whatever is outside it."""
        target = float(self.page)
        # Cap the time step: after an idle frame (up to 0.1 s when paused) the slide would
        # otherwise start by jumping a third of the way.
        dt = min(imgui.get_io().delta_time, 1.0 / 30.0)
        step = dt / PAGE_SLIDE_S if PAGE_SLIDE_S > 0 else 1.0
        if self.page_pos < target:
            self.page_pos = min(target, self.page_pos + step)
        else:
            self.page_pos = max(target, self.page_pos - step)
        e = eased_page_position(self.page_pos)

        size = imgui.get_content_region_avail()
        transparent = hex_color(PAL.window, 0.0)
        no_scroll = imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
        imgui.push_style_color(imgui.Col_.child_bg, transparent)
        imgui.begin_child("pages", size, 0, no_scroll)
        imgui.pop_style_color()
        origin = imgui.get_cursor_pos()
        gap = em_size(2.0)
        for i, draw_page in enumerate(self.page_functions()):
            offset = (i - e) * (size.x + gap)
            if abs(offset) >= size.x + gap:  # fully outside: skip it
                continue
            imgui.set_cursor_pos(imgui.ImVec2(origin.x + offset, origin.y))
            imgui.push_style_color(imgui.Col_.child_bg, transparent)
            imgui.begin_child(f"page{i}", size, 0, no_scroll)
            imgui.pop_style_color()
            draw_page()
            imgui.end_child()
        imgui.end_child()

    @property
    def animating(self) -> bool:
        return self.page_pos != float(self.page)

    # ----- panels -----------------------------------------------------------
    def theme_button(self) -> None:
        icon = icons_fontawesome_4.ICON_FA_SUN if PAL.dark else icons_fontawesome_4.ICON_FA_MOON
        if imgui.button(f"{icon}###theme", em_to_vec2(2.2, 0)):  # ### keeps one ID while the icon changes
            self.set_theme(dark=not PAL.dark)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Switch to the light theme" if PAL.dark else "Switch to the dark theme")

    def gui_header_narrow(self) -> None:
        """On a phone, two lines: the title, the theme and pause buttons; then the page switch, and the speed
        if it fits"""
        win_w, pad_r = imgui.get_window_width(), imgui.get_style().window_padding.x
        button_w, spacing = em_size(2.2), imgui.get_style().item_spacing.x
        y0 = imgui.get_cursor_pos_y()
        imgui.push_font(None, em_size(1.25))
        imgui.text("Rotor run-up monitor")
        imgui.pop_font()
        imgui.same_line(win_w - pad_r - 2 * button_w - spacing)
        imgui.set_cursor_pos_y(y0)
        self.theme_button()
        imgui.same_line()
        icon = icons_fontawesome_4.ICON_FA_PLAY if self.paused else icons_fontawesome_4.ICON_FA_PAUSE
        if imgui.button(f"{icon}###run", em_to_vec2(2.2, 0)):
            self.paused = not self.paused

        y1 = imgui.get_cursor_pos_y()
        self.gui_page_switch()
        speed = f"{self.rotor.speed_now:5.1f} Hz"
        speed_w = imgui.calc_text_size(speed).x
        if self.page_switch_width() + em_size(0.8) + speed_w < win_w - 2 * pad_r:
            imgui.same_line(win_w - pad_r - speed_w)
            imgui.set_cursor_pos_y(y1 + em_size(0.2) + imgui.get_style().frame_padding.y)
            imgui.text(speed)

    def gui_header(self) -> None:
        if self.narrow:
            self.gui_header_narrow()
            return
        speed = self.rotor.speed_now
        y0 = imgui.get_cursor_pos_y()
        baseline_shift = em_size(0.45) * 0.78  # large text is 1.45 em: drop small text to its baseline

        def small_text(text: str) -> None:
            imgui.same_line()
            imgui.set_cursor_pos_y(y0 + baseline_shift)
            imgui.text_colored(hex_color(PAL.muted), text)

        imgui.push_font(None, em_size(1.45))
        imgui.text("Rotor run-up monitor")
        imgui.pop_font()
        title_end = imgui.get_item_rect_max().x - imgui.get_window_pos().x

        # Right group (speed, rpm, theme, pause) is anchored to the right edge; the page switch
        # centers in what remains; the subtitle and the rpm show only when they fit.
        win_w = imgui.get_window_width()
        pad_r = imgui.get_style().window_padding.x
        buttons_w = em_size(2.2) + em_size(7.5) + imgui.get_style().item_spacing.x
        imgui.push_font(None, em_size(1.45))
        speed_w = imgui.calc_text_size(f"{speed:5.1f} Hz").x
        imgui.pop_font()
        rpm_w = imgui.calc_text_size("0000 rpm").x + em_size(0.6)
        switch_w = self.page_switch_width()
        gap = em_size(1.2)
        show_rpm = title_end + 2 * gap + switch_w + speed_w + rpm_w + buttons_w + gap + pad_r < win_w
        right_w = speed_w + (rpm_w if show_rpm else 0.0) + gap + buttons_w
        right_x = win_w - pad_r - right_w
        switch_x = min(max(0.5 * (win_w - switch_w), title_end + gap), right_x - gap - switch_w)
        switch_x = max(switch_x, title_end + em_size(0.5))
        subtitle = "simulated three-axis accelerometer, bearing housing"
        if title_end + em_size(0.6) + imgui.calc_text_size(subtitle).x + gap < switch_x:
            small_text(subtitle)
        imgui.same_line(switch_x)
        imgui.set_cursor_pos_y(y0 + 0.5 * (em_size(1.45) - imgui.get_frame_height()) - em_size(0.2))
        self.gui_page_switch()

        imgui.same_line(max(right_x, switch_x + switch_w + gap))
        imgui.set_cursor_pos_y(y0)
        imgui.push_font(None, em_size(1.45))
        imgui.text(f"{speed:5.1f} Hz")
        imgui.pop_font()
        if show_rpm:
            small_text(f"{speed * 60:5.0f} rpm")
        imgui.same_line(win_w - pad_r - buttons_w)
        imgui.set_cursor_pos_y(y0 + em_size(0.1))
        self.theme_button()
        imgui.same_line()
        label = "Resume" if self.paused else "Pause"
        if imgui.button(f"{label}##run", em_to_vec2(7.5, 0)):
            self.paused = not self.paused

    def gui_controls(self) -> None:
        r = self.rotor

        imgui.text("Shaft")
        r.sweep = self.toggle("Sweep the speed", r.sweep)
        if r.sweep:
            # a range widget keeps min <= max by construction, and shows both values in full
            _, r.speed_lo, r.speed_hi = imgui.drag_float_range2(
                "Range", r.speed_lo, r.speed_hi, 0.2, 2.0, 90.0, "%.0f Hz", "%.0f Hz",
                imgui.SliderFlags_.always_clamp,
            )
            _, r.sweep_period = imgui.slider_float("Period", r.sweep_period, 6.0, 60.0, "%.0f s")
        else:
            _, r.manual_speed = imgui.slider_float("Speed", r.manual_speed, 2.0, 90.0, "%.1f Hz")

        imgui.spacing()
        imgui.separator()
        imgui.text("Structure")
        self.gui_structure_knobs()
        r.bearing_defect = self.toggle("Bearing defect", r.bearing_defect)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Adds outer-race impacts at 3.58 shaft orders, ringing a housing mode near 650 Hz.")

        imgui.spacing()
        imgui.separator()
        imgui.text("Analysis")
        names = list(WINDOWS)
        _, i = imgui.combo("Window", names.index(self.window_name), names)
        self.window_name = names[i]
        channel_names = [c[0] for c in channels()]
        _, self.spectro_channel = imgui.combo("Spectrogram", self.spectro_channel, channel_names)
        _, self.hist_channel = imgui.combo("Histogram", self.hist_channel, channel_names)
        self.show_orders = self.toggle("Mark shaft orders", self.show_orders)

        imgui.spacing()
        imgui.separator()
        imgui.text("Last two seconds")
        self.gui_readouts()

        # usage hint, pinned to the bottom of the panel
        hint_h = em_size(3.0)
        imgui.set_cursor_pos_y(max(imgui.get_cursor_pos_y(), imgui.get_window_height() - hint_h - em_size(0.8)))
        imgui.separator()
        imgui.push_text_wrap_pos(0.0)
        imgui.text_colored(
            hex_color(PAL.muted),
            "In the plots: drag to pan, scroll to zoom, double-click to fit, right-click for options.",
        )
        imgui.pop_text_wrap_pos()

    @staticmethod
    def toggle(label: str, value: bool) -> bool:
        """An animated switch. The toggle draws its track with Button (on) or FrameBg (off)
        and its knob with Text, so the label is drawn apart: the knob can stay light in both
        themes while the label keeps the theme's text color."""
        imgui.push_style_color(imgui.Col_.button, hex_color(PAL.accent, 0.85))
        imgui.push_style_color(imgui.Col_.button_hovered, hex_color(PAL.accent))
        imgui.push_style_color(imgui.Col_.frame_bg, hex_color(PAL.frame_hi))
        imgui.push_style_color(imgui.Col_.frame_bg_hovered, hex_color(PAL.frame_hi, 0.8))
        imgui.push_style_color(imgui.Col_.text, hex_color("#F7F9FB"))
        _, value = imgui_toggle.toggle(f"##{label}", value, imgui_toggle.ToggleFlags_.animated)
        imgui.pop_style_color(5)
        imgui.same_line()
        imgui.text(label)
        if imgui.is_item_clicked():  # the label toggles too, like a checkbox's
            value = not value
        return value

    def gui_structure_knobs(self) -> None:
        """Three knobs in a row, sized to the sidebar's current width."""
        r = self.rotor
        spacing = imgui.get_style().item_spacing.x
        size = min(em_size(4.2), (imgui.get_content_region_avail().x - 2 * spacing) / 3.0 - em_size(0.4))
        variant = imgui_knobs.ImGuiKnobVariant_.wiper  # the filled arc reads at a glance
        drag = imgui_knobs.ImGuiKnobFlags_.drag_vertical

        _, r.res_freq = imgui_knobs.knob(
            "Resonance", r.res_freq, 40.0, 350.0, 0.0, "%.0f Hz", variant, size, drag
        )
        imgui.same_line()
        _, r.damping = imgui_knobs.knob(
            "Damping", r.damping, 0.005, 0.3, 0.0, "%.3f", variant, size,
            drag | imgui_knobs.ImGuiKnobFlags_.logarithmic,
        )
        imgui.same_line()
        _, r.noise = imgui_knobs.knob("Noise", r.noise, 0.0, 0.1, 0.0, "%.3f g", variant, size, drag)
        r.res_freq = min(max(r.res_freq, 40.0), 350.0)

    def gui_readouts(self) -> None:
        flags = imgui.TableFlags_.row_bg | imgui.TableFlags_.sizing_stretch_prop
        if imgui.begin_table("readouts", 4, flags):
            imgui.table_setup_column("Channel", imgui.TableColumnFlags_.width_stretch, 1.6)
            imgui.table_setup_column("RMS", imgui.TableColumnFlags_.width_stretch, 1.0)
            imgui.table_setup_column("Crest", imgui.TableColumnFlags_.width_stretch, 1.0)
            imgui.table_setup_column("Kurt.", imgui.TableColumnFlags_.width_stretch, 1.0)
            imgui.table_headers_row()
            for c, (name, col) in enumerate(channels()):
                x = self.buffer[c]
                rms = float(np.sqrt(np.mean(x * x)))
                crest = float(np.max(np.abs(x)) / (rms + 1e-12))
                kurt = kurtosis(x)
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.color_button(
                    f"##sw{c}",
                    hex_color(col),
                    imgui.ColorEditFlags_.no_tooltip | imgui.ColorEditFlags_.no_border,
                    em_to_vec2(0.7, 0.7),
                )
                imgui.same_line()
                imgui.text(name)
                imgui.table_next_column()
                imgui.text(f"{rms:.3f}")
                imgui.table_next_column()
                imgui.text(f"{crest:.1f}")
                imgui.table_next_column()
                # kurtosis of a Gaussian is 3: well above means impulsive content
                if kurt > 4.0:
                    imgui.text_colored(hex_color(PAL.warn), f"{kurt:.1f}")
                else:
                    imgui.text(f"{kurt:.1f}")
            imgui.end_table()
        imgui.text_colored(hex_color(PAL.muted), "RMS in g. Kurtosis is 3 for Gaussian noise.")

    def phone_plot_flags(self) -> int:
        """On a phone, the plots are narrow: their legends would cover the data (the channels' colors are in the
        acceleration's legend)"""
        return implot.Flags_.no_legend if self.narrow else 0

    def gui_time_series(self, size: imgui.ImVec2) -> None:
        if implot.begin_plot("Acceleration", size):
            implot.setup_axes("time (s)", "g", 0, implot.AxisFlags_.auto_fit)
            implot.setup_axis_limits(implot.ImAxis_.x1, -HISTORY_S, 0.0, imgui.Cond_.always)
            outside = implot.LegendFlags_.outside if self.narrow else 0  # on a phone, off the data
            implot.setup_legend(implot.Location_.north_west, implot.LegendFlags_.horizontal | outside)
            for c, (name, col) in enumerate(channels()):
                spec = implot.Spec(line_color=hex_color(col, 0.9), line_weight=1.0)
                implot.plot_line(name, self.t_axis, self.buffer[c], spec)
            implot.end_plot()

    def gui_spectrum(self, size: imgui.ImVec2) -> None:
        window = WINDOWS[self.window_name](SPECTRUM_NFFT)
        f = self.spectrum_freqs[: self.spectrum_view]
        if implot.begin_plot("Spectrum", size, self.phone_plot_flags()):
            implot.setup_axes("frequency (Hz)", "dB re 1 g")
            implot.setup_axis_limits(implot.ImAxis_.x1, 0.0, F_VIEW, imgui.Cond_.once)
            implot.setup_axis_limits(implot.ImAxis_.y1, -80.0, 5.0, imgui.Cond_.once)
            implot.setup_legend(implot.Location_.north_east)

            if self.show_orders:
                orders = self.rotor.speed_now * np.arange(1.0, 5.0)
                implot.plot_inf_lines(
                    "Shaft orders", orders, implot.Spec(line_color=hex_color(PAL.text, 0.25))
                )
            self.resonance_drag_line(vertical=True)

            peak_f, peak_db = 0.0, -999.0
            for c, (name, col) in enumerate(channels()):
                db = amplitude_db(self.buffer[c, -SPECTRUM_NFFT:], window)[: self.spectrum_view]
                implot.plot_line(name, f, db, implot.Spec(line_color=hex_color(col), line_weight=1.3))
                i = int(np.argmax(db[2:])) + 2  # skip the DC bins
                if db[i] > peak_db:
                    peak_f, peak_db = float(f[i]), float(db[i])
            implot.annotation(
                peak_f, peak_db, hex_color(PAL.panel, 0.9), em_to_vec2(0.6, -0.6), True,
                f"peak {peak_f:.0f} Hz, {peak_db:.0f} dB",
            )
            implot.end_plot()

    def resonance_drag_line(self, vertical: bool) -> None:
        """The resonance, drawn as a line the user can drag, inside the current plot."""
        r = self.rotor
        col = hex_color(PAL.warn, 0.6)
        # an inf line with the same position gives the drag line a legend entry
        inf_flags = 0 if vertical else implot.InfLinesFlags_.horizontal
        implot.plot_inf_lines(
            "Resonance (drag it)", np.array([r.res_freq]), implot.Spec(line_color=col, flags=inf_flags)
        )
        drag_line = implot.drag_line_x if vertical else implot.drag_line_y
        changed, value, _, hovered, _ = drag_line(
            0, r.res_freq, col, 1.5, implot.DragToolFlags_.none, False, False, False
        )
        if changed:
            r.res_freq = min(max(value, 40.0), 350.0)
        if hovered:
            imgui.set_tooltip(f"Resonance {r.res_freq:.0f} Hz: drag to move it")

    def gui_histogram(self, size: imgui.ImVec2) -> None:
        name, col = channels()[self.hist_channel]
        x = self.buffer[self.hist_channel]
        mu, sigma = float(x.mean()), float(x.std()) + 1e-12
        lim = max(4.5 * sigma, float(np.max(np.abs(x - mu))))
        counts, edges = np.histogram(x, bins=41, range=(mu - lim, mu + lim), density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        xs = np.linspace(mu - lim, mu + lim, 200)
        gauss = np.exp(-0.5 * ((xs - mu) / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))

        if implot.begin_plot(f"Distribution, {name}", size, self.phone_plot_flags()):
            implot.setup_axes("g", "density", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
            implot.setup_legend(implot.Location_.north_east)
            implot.plot_bars(
                "Measured", centers, counts, float(edges[1] - edges[0]) * 0.92,
                implot.Spec(fill_color=hex_color(col, 0.55), line_color=hex_color(col, 0.0)),
            )
            implot.plot_line("Gaussian", xs, gauss, implot.Spec(line_color=hex_color(PAL.text, 0.8), line_weight=1.5))
            implot.end_plot()

    def gui_spectrogram(self, size: imgui.ImVec2) -> None:
        scale_w = em_size(4.2)
        plot_size = imgui.ImVec2(size.x - scale_w - imgui.get_style().item_spacing.x, size.y)
        name = channels()[self.spectro_channel][0]
        t0, t1 = float(self.spectro_t[0]), float(self.spectro_t[-1])

        implot.push_colormap(implot.Colormap_.viridis)
        if implot.begin_plot(f"Spectrogram, {name}", plot_size, self.phone_plot_flags()):
            implot.setup_axes("time (s)", "frequency (Hz)")
            implot.setup_axis_limits(implot.ImAxis_.x1, t0, t1, imgui.Cond_.always)
            implot.setup_axis_limits(implot.ImAxis_.y1, 0.0, F_VIEW, imgui.Cond_.always)
            implot.setup_legend(implot.Location_.north_west)
            # Row 0 of a heatmap is drawn at the top: put the highest frequency first.
            image = np.ascontiguousarray(np.flipud(self.spectro))
            top = float(self.spectro_freqs[self.spectro_rows - 1])
            implot.plot_heatmap(
                "##spectrogram", image, DB_MIN, DB_MAX, "",
                implot.Point(t0, 0.0), implot.Point(t1, top),
            )
            if self.show_orders:
                for k in range(1, 5):
                    implot.plot_line(
                        "Shaft orders" if k == 1 else f"##order{k}",
                        self.spectro_t, k * self.speed_track,
                        implot.Spec(line_color=hex_color(PAL.text, 0.22), line_weight=1.0),
                    )
            self.resonance_drag_line(vertical=False)
            implot.end_plot()
        imgui.same_line()
        implot.colormap_scale("dB re 1 g", DB_MIN, DB_MAX, imgui.ImVec2(scale_w, size.y))
        implot.pop_colormap()

    # ----- frame --------------------------------------------------------------
    def gui(self) -> None:
        if not self.styled:
            self.apply_style()
            self.styled = True
        self.update()
        # The whole window moves while acquiring or sliding pages; idle only when neither happens.
        hello_imgui.get_runner_params().fps_idling.enable_idling = self.paused and not self.animating

        narrow = imgui.get_content_region_avail().x < em_size(NARROW_EM)
        if narrow != self.narrow:  # the layout changes: the chain stays the chain, any other page shows the plots
            on_chain = self.page == len(self.page_labels()) - 1
            self.narrow = narrow
            self.page = len(self.page_labels()) - 1 if on_chain else 0
            self.page_pos = float(self.page)

        self.gui_header()
        imgui.dummy(em_to_vec2(0.0, 0.1))
        self.gui_pages()

    def gui_monitor(self) -> None:
        # The sidebar is resizable: drag its right edge. Its width is remembered in the ini file.
        initial_w, min_w, max_w = (em_size(w) for w in SIDEBAR_EM)
        imgui.set_next_window_size_constraints(imgui.ImVec2(min_w, 0.0), imgui.ImVec2(max_w, 1e6))
        imgui.begin_child(
            "controls",
            imgui.ImVec2(initial_w, 0.0),
            imgui.ChildFlags_.always_use_window_padding | imgui.ChildFlags_.resize_x,
        )
        imgui.push_item_width(-em_size(6.0))  # widgets stretch with the sidebar, labels keep 6 em
        self.gui_controls()
        imgui.pop_item_width()
        imgui.end_child()

        imgui.same_line()
        imgui.begin_child("plots", imgui.ImVec2(0.0, 0.0))
        avail = imgui.get_content_region_avail()
        gap = imgui.get_style().item_spacing.y
        h_time = (avail.y - 2 * gap) * 0.27
        h_mid = (avail.y - 2 * gap) * 0.33
        h_spectro = avail.y - 2 * gap - h_time - h_mid

        self.gui_time_series(imgui.ImVec2(avail.x, h_time))
        w_hist = avail.x * 0.3
        self.gui_spectrum(imgui.ImVec2(avail.x - w_hist - imgui.get_style().item_spacing.x, h_mid))
        imgui.same_line()
        self.gui_histogram(imgui.ImVec2(w_hist, h_mid))
        self.gui_spectrogram(imgui.ImVec2(avail.x, h_spectro))
        imgui.end_child()


    def gui_plots(self) -> None:
        """On a phone: the four plots stacked, in a column that scrolls (a swipe scrolls it, even from a plot; a short
        hold, then a drag, pans the plot)"""
        imgui.begin_child("plots_column", imgui.ImVec2(0.0, 0.0))
        w = imgui.get_content_region_avail().x
        self.gui_time_series(imgui.ImVec2(w, em_size(13.0)))
        self.gui_spectrum(imgui.ImVec2(w, em_size(16.0)))
        self.gui_histogram(imgui.ImVec2(w, em_size(13.0)))
        self.gui_spectrogram(imgui.ImVec2(w, em_size(17.0)))
        imgui.end_child()

    def gui_controls_page(self) -> None:
        """On a phone: the sidebar's controls, on a page of their own"""
        imgui.begin_child("controls", imgui.ImVec2(0.0, 0.0), imgui.ChildFlags_.always_use_window_padding)
        imgui.push_item_width(-em_size(6.0))
        self.gui_controls()
        imgui.pop_item_width()
        imgui.end_child()

    def gui_signal_chain(self) -> None:
        # Evaluate when something changed, and at most 30 times a second for new data.
        now = time.perf_counter()
        if self.graph.dirty or (self.new_data and now - self.last_graph_eval > 1.0 / 30.0):
            self.graph.evaluate(self)
            self.last_graph_eval, self.new_data = now, False

        if imgui.button("Reset the graph"):
            self.graph = default_graph()
            self.graph_editor = GraphEditor(self.graph)
        imgui.same_line()
        if imgui.button("Fit the view"):
            self.graph_editor.fit = "all"
        imgui.same_line()
        imgui.push_text_wrap_pos(0.0)  # wraps at the window's edge when narrow
        imgui.text_colored(
            hex_color(PAL.muted),
            "Drag from a pin to link. Right-click to add a node, right-drag to pan, scroll to zoom. "
            "Delete removes the selection.",
        )
        imgui.pop_text_wrap_pos()

        # The editor on the left takes 60 % of the width at first; drag its right edge to change
        # that. The plots of the graph's plot nodes fill the rest.
        # On a phone, the editor takes the upper 55 % of the page, and its plots the rest.
        avail = imgui.get_content_region_avail()
        if not self.narrow:
            imgui.set_next_window_size_constraints(
                imgui.ImVec2(min(em_size(20.0), avail.x * 0.5), 0.0), imgui.ImVec2(avail.x - em_size(16.0), 1e6)
            )
        imgui.push_style_color(imgui.Col_.child_bg, hex_color(PAL.window, 0.0))
        if self.narrow:
            imgui.begin_child("editor_area", imgui.ImVec2(avail.x, avail.y * 0.55))
        else:
            imgui.begin_child("editor_area", imgui.ImVec2(avail.x * 0.6, avail.y), imgui.ChildFlags_.resize_x)
        imgui.pop_style_color()
        self.graph_editor.draw(imgui.get_content_region_avail())
        imgui.end_child()
        if not self.narrow:
            imgui.same_line()
        imgui.begin_child("results", imgui.ImVec2(0.0, 0.0), imgui.ChildFlags_.always_use_window_padding)
        sinks = [n for n in self.graph.nodes if n.kind == "sink"]
        if not sinks:
            imgui.text_colored(hex_color(PAL.muted), "Add a Time plot or a Spectrum plot node to see results here.")
        else:
            space = imgui.get_content_region_avail()
            gap = imgui.get_style().item_spacing.y
            h = max(em_size(9.0), (space.y - gap * (len(sinks) - 1)) / len(sinks))
            for node in sinks:
                node.plot(imgui.ImVec2(space.x, h), self)
        imgui.end_child()

_dashboard: Optional[Dashboard] = None


def gui() -> None:
    """The dashboard, created at its first frame"""
    global _dashboard
    if _dashboard is None:
        _dashboard = Dashboard()
    _dashboard.gui()


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Rotor run-up monitor"
    params.app_window_params.window_geometry.size = (1500, 920)
    params.callbacks.show_gui = gui
    params.fps_idling.enable_idling = False
    addons = immapp.AddOnsParams()
    addons.with_implot = True
    addons.with_node_editor = True
    immapp.run(params, addons)


if __name__ == "__main__":
    main()
