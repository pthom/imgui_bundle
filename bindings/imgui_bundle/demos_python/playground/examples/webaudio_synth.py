"""
WebAudio synthesizer: a piano, four tunes, and a scope.

A small synthesizer written in Python: play the piano with the mouse or the computer keyboard, or let it play a
tune. Pick a waveform, add some echo, and watch the scope. **Pyodide only**: it plays through the browser's
[WebAudio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API), via [Pyodide](https://pyodide.org)'s
`js` interop.

## How it works

The audio graph is built once, at the first sound:

```
voices -> brightness (a low-pass filter) -> volume -> speakers
volume -> delay -> feedback -> delay        (the echo loop)
delay -> echo -> speakers
volume + echo -> analyser                   (read by the scope)
```

- A key you hold starts a voice: an oscillator, and a gain for its envelope. Releasing the key fades it out.
- A tune schedules all its notes at once, on the audio clock (`ctx.currentTime`), so that the rhythm stays exact
  whatever the frame rate. The GUI only reads this clock, to light the keys.
- No JavaScript callback calls Python: there is no proxy to keep alive, or to destroy.

## Gotcha

Browsers require a *user gesture* before an `AudioContext` may produce sound. We create it at the first sound: the
click or the key press that asks for it is the gesture.
"""
import sys
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from imgui_bundle import imgui, immapp, imgui_knobs, rich_md, icons_fontawesome_4, em_size, em_to_vec2
from imgui_bundle import ImVec2, ImVec4, ImVec2Like, ImColor

IN_BROWSER = sys.platform == "emscripten"

HEADER = """
# WebAudio synthesizer
A small synthesizer written in Python, which plays through your browser's
[WebAudio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API).
Play it with the mouse, or with your computer keyboard (the letters are on the keys), or pick a tune.
"""

# The piano: two octaves, from C4 (MIDI note 60) to C6
LOWEST_NOTE = 60
NB_NOTES = 25
PIANO_HEIGHT = 13.0  # em
# The computer keys that play them, as in a tracker: the bottom letter row plays C4 to B4, the top row C5 to C6.
# The piano shows them on its keys.
KEY_LABELS = "Z S X D C V G B H N J M Q 2 W 3 E R 5 T 6 Y 7 U I".split()


@dataclass
class Tune:
    name: str
    origin: str
    fact: str
    notes: str  # a note, and its length in beats after a colon (1 by default). R is a rest.


TUNES = [
    Tune("Ode to Joy", "Beethoven, 1824", "The finale of his 9th symphony, now the anthem of Europe.", """
        E5 E5 F5 G5 G5 F5 E5 D5 C5 C5 D5 E5 E5:1.5 D5:0.5 D5:2
        E5 E5 F5 G5 G5 F5 E5 D5 C5 C5 D5 E5 D5:1.5 C5:0.5 C5:2
        D5 D5 E5 C5 D5 E5:0.5 F5:0.5 E5 C5 D5 E5:0.5 F5:0.5 E5 D5 C5 D5 G4:2
        E5 E5 F5 G5 G5 F5 E5 D5 C5 C5 D5 E5 D5:1.5 C5:0.5 C5:2
    """),
    Tune("Frère Jacques", "French round, 18th century", "Mahler turned it into a funeral march, in minor.", """
        C5 D5 E5 C5 C5 D5 E5 C5 E5 F5 G5:2 E5 F5 G5:2
        G5:0.5 A5:0.5 G5:0.5 F5:0.5 E5 C5 G5:0.5 A5:0.5 G5:0.5 F5:0.5 E5 C5
        C5 G4 C5:2 C5 G4 C5:2
    """),
    Tune("Twinkle, Twinkle", "French melody, 1761", "Mozart wrote twelve variations on it.", """
        C4 C4 G4 G4 A4 A4 G4:2 F4 F4 E4 E4 D4 D4 C4:2
        G4 G4 F4 F4 E4 E4 D4:2 G4 G4 F4 F4 E4 E4 D4:2
        C4 C4 G4 G4 A4 A4 G4:2 F4 F4 E4 E4 D4 D4 C4:2
    """),
    Tune("Für Elise", "Beethoven, 1810", "Published in 1867, forty years after his death.", """
        E5:0.5 D#5:0.5
        E5:0.5 D#5:0.5 E5:0.5 B4:0.5 D5:0.5 C5:0.5 A4 R:0.5 C4:0.5 E4:0.5 A4:0.5 B4 R:0.5 E4:0.5 G#4:0.5 B4:0.5
        C5 R:0.5 E4:0.5 E5:0.5 D#5:0.5
        E5:0.5 D#5:0.5 E5:0.5 B4:0.5 D5:0.5 C5:0.5 A4 R:0.5 C4:0.5 E4:0.5 A4:0.5 B4 R:0.5 E4:0.5 C5:0.5 B4:0.5 A4:2
    """),
]

# The waveforms, and their shapes over t (in periods), drawn on their buttons
WAVE_SHAPES: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "sine": lambda t: np.sin(2 * np.pi * t),
    "triangle": lambda t: 2 / np.pi * np.arcsin(np.sin(2 * np.pi * t)),
    "square": lambda t: np.sign(np.sin(2 * np.pi * t)),
    "sawtooth": lambda t: 2 * (t % 1) - 1,
}
WAVEFORMS = list(WAVE_SHAPES)

# The sound
VOICE_GAIN = 0.2  # per note, so that chords don't saturate
ATTACK = 0.01  # seconds
DECAY = 0.3  # seconds (a time constant), towards the sustain level
SUSTAIN = 0.5  # of VOICE_GAIN
RELEASE = 0.08  # seconds (a time constant)
NOTE_LENGTH = 0.9  # of the note's duration in a tune: a short gap separates repeated notes
ECHO_DELAY = 0.3  # seconds

# The scope
SCOPE_SAMPLES = 1024  # about 20 ms
SCOPE_ZOOM = 3.0
SPECTRUM_BINS = 128  # of 1024: up to about 3 kHz

# Colors
PLAYED_KEY = imgui.IM_COL32(255, 150, 60, 255)  # the keys you play
TUNE_KEY = imgui.IM_COL32(90, 180, 255, 255)  # the keys the tune plays
WHITE_KEY = imgui.IM_COL32(248, 245, 236, 255)
BLACK_KEY = imgui.IM_COL32(28, 28, 34, 255)
KEY_OUTLINE = imgui.IM_COL32(60, 60, 60, 255)
KEY_SHADOW = imgui.IM_COL32(0, 0, 0, 90)  # cast by the felt, at the top of the keys
NO_SHADOW = imgui.IM_COL32(0, 0, 0, 0)
WHITE_KEY_FRONT = imgui.IM_COL32(0, 0, 0, 22)  # the front face of the keys, seen from above
BLACK_KEY_FRONT = imgui.IM_COL32(255, 255, 255, 45)
FELT = imgui.IM_COL32(130, 24, 38, 255)
PANEL = ImVec4(0.16, 0.16, 0.19, 1.0)
KNOB_COLORS = imgui_knobs.KnobColors(
    primary=imgui_knobs.color_set(ImColor(1.0, 0.59, 0.24, 1.0), ImColor(1.0, 0.7, 0.4, 1.0), ImColor(1.0, 0.7, 0.4, 1.0)),
    secondary=imgui_knobs.color_set(ImColor(0.4, 0.4, 0.45, 1.0), ImColor(0.47, 0.47, 0.52, 1.0),
                                    ImColor(0.47, 0.47, 0.52, 1.0)),
    track=imgui_knobs.color_set(ImColor(0.27, 0.27, 0.31, 1.0)),
)
SCOPE_BACKGROUND = imgui.IM_COL32(15, 22, 28, 255)
SCOPE_LINE = imgui.IM_COL32(120, 255, 170, 255)
SCOPE_GLOW = imgui.IM_COL32(120, 255, 170, 50)
# The spectrum goes from blue (low frequencies) to orange (high ones)
SPECTRUM_COLORS = [imgui.IM_COL32(int(90 + 165 * f), int(180 - 30 * f), int(255 - 195 * f), 255)
                   for f in np.linspace(0.0, 1.0, SPECTRUM_BINS)]


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def note_number(name: str) -> int:
    """The MIDI number of a note named like C4 or D#5 (C4 is 60)"""
    return 12 * (int(name[-1]) + 1) + NOTE_NAMES.index(name[:-1])


def parse_notes(notes: str) -> list[tuple[int | None, float]]:
    """The notes of a tune (None for a rest), with their length in beats"""
    result: list[tuple[int | None, float]] = []
    for token in notes.split():
        name, _, beats = token.partition(":")
        result.append((None if name == "R" else note_number(name), float(beats or 1)))
    return result


def is_black(note: int) -> bool:
    return note % 12 in (1, 3, 6, 8, 10)


NOTES = range(LOWEST_NOTE, LOWEST_NOTE + NB_NOTES)
NB_WHITE_KEYS = sum(not is_black(note) for note in NOTES)
PIANO_KEYS = [imgui.Key[label.lower() if label.isalpha() else "_" + label] for label in KEY_LABELS]


class Synth:
    """The audio graph (see the docstring at the top). Needs the browser."""

    def __init__(self) -> None:
        from js import AudioContext, Float32Array, Uint8Array  # type: ignore[import-not-found]

        self.ctx = ctx = AudioContext.new()
        self.filter = ctx.createBiquadFilter()
        self.filter.type = "lowpass"
        self.volume = ctx.createGain()
        self.delay = ctx.createDelay(1.0)
        self.delay.delayTime.value = ECHO_DELAY
        self.feedback = ctx.createGain()
        self.echo = ctx.createGain()
        self.analyser = ctx.createAnalyser()
        self.analyser.fftSize = 2048

        self.filter.connect(self.volume)
        self.volume.connect(ctx.destination)
        self.volume.connect(self.delay)
        self.delay.connect(self.feedback)
        self.feedback.connect(self.delay)
        self.delay.connect(self.echo)
        self.echo.connect(ctx.destination)
        self.volume.connect(self.analyser)
        self.echo.connect(self.analyser)

        self.waveform_buffer = Float32Array.new(self.analyser.fftSize)
        self.spectrum_buffer = Uint8Array.new(self.analyser.frequencyBinCount)
        self.voices: dict[int, tuple[Any, Any, float]] = {}  # the notes held: oscillator, envelope, attack end
        self.tune: Tune | None = None  # the tune playing
        self.tune_bus: Any = None  # the tune's notes go through it, so that Stop can cut them
        self.tune_notes: list[tuple[int, float, float]] = []  # note, start, end
        self.tune_start = self.tune_end = 0.0

    def apply(self, state: "State") -> None:
        self.filter.frequency.value = state.brightness
        self.volume.gain.value = state.volume
        self.feedback.gain.value = 0.5 * state.echo
        self.echo.gain.value = state.echo

    def _start_voice(self, note: int, start: float, destination: Any, waveform: str) -> tuple[Any, Any]:
        oscillator = self.ctx.createOscillator()
        oscillator.type = waveform
        oscillator.frequency.value = 440.0 * 2 ** ((note - 69) / 12)
        envelope = self.ctx.createGain()
        envelope.gain.setValueAtTime(0.0, start)
        envelope.gain.linearRampToValueAtTime(VOICE_GAIN, start + ATTACK)
        envelope.gain.setTargetAtTime(SUSTAIN * VOICE_GAIN, start + ATTACK, DECAY)
        oscillator.connect(envelope)
        envelope.connect(destination)
        oscillator.start(start)
        return oscillator, envelope

    @staticmethod
    def _release(oscillator: Any, envelope: Any, end: float) -> None:
        envelope.gain.setTargetAtTime(0.0, end, RELEASE)
        oscillator.stop(end + 5 * RELEASE)

    def update(self, held: set[int], waveform: str) -> None:
        """Each frame: starts the notes newly held, releases the ones no longer held, and notices the tune's end"""
        now = self.ctx.currentTime
        for note in held - set(self.voices):
            oscillator, envelope = self._start_voice(note, now, self.filter, waveform)
            self.voices[note] = (oscillator, envelope, now + ATTACK)
        for note in set(self.voices) - held:
            oscillator, envelope, attack_end = self.voices.pop(note)
            self._release(oscillator, envelope, max(now, attack_end))
        if self.tune is not None and now > self.tune_end:
            self.tune = None  # its last note fades out on its own
            self.tune_notes = []

    def play_tune(self, tune: Tune, tempo: float, waveform: str) -> None:
        """Schedules all the notes of the tune on the audio clock"""
        self.stop_tune()
        self.tune = tune
        self.tune_bus = self.ctx.createGain()
        self.tune_bus.connect(self.filter)
        t = self.tune_start = self.ctx.currentTime + 0.1
        for note, beats in parse_notes(tune.notes):
            duration = beats * 60.0 / tempo
            if note is not None:
                end = t + NOTE_LENGTH * duration
                oscillator, envelope = self._start_voice(note, t, self.tune_bus, waveform)
                self._release(oscillator, envelope, end)
                self.tune_notes.append((note, t, end))
            t += duration
        self.tune_end = t

    def stop_tune(self) -> None:
        if self.tune_bus is not None:
            self.tune_bus.disconnect()  # the scheduled notes play on, unheard, until their end
        self.tune = self.tune_bus = None
        self.tune_notes = []

    def tune_progress(self) -> float:
        return float(self.ctx.currentTime - self.tune_start) / (self.tune_end - self.tune_start)

    def tune_notes_sounding(self) -> set[int]:
        now = self.ctx.currentTime
        return {note for note, start, end in self.tune_notes if start <= now < end}

    def waveform(self) -> np.ndarray:
        self.analyser.getFloatTimeDomainData(self.waveform_buffer)
        return np.frombuffer(self.waveform_buffer.to_bytes(), dtype=np.float32)

    def spectrum(self) -> np.ndarray:
        self.analyser.getByteFrequencyData(self.spectrum_buffer)
        return np.frombuffer(self.spectrum_buffer.to_bytes(), dtype=np.uint8)


class State:
    def __init__(self) -> None:
        self.waveform = 0  # in WAVEFORMS
        self.echo = 0.3
        self.brightness = 4000.0  # Hz: the cutoff of the low-pass filter
        self.volume = 0.8
        self.tempo = 120.0  # beats per minute
        self.synth: Synth | None = None

    def ensure_synth(self) -> Synth | None:
        """The synth, created at the first sound, since browsers require a user gesture first. None on desktop."""
        if self.synth is None and IN_BROWSER:
            self.synth = Synth()
            self.synth.apply(self)
        return self.synth


def header() -> None:
    rich_md.render(HEADER)
    if not IN_BROWSER:
        imgui.text_colored(imgui.color_convert_u32_to_float4(PLAYED_KEY),
                           "No sound on desktop: this demo uses the browser's WebAudio API. Run it in the playground.")


def tune_card(state: State, tune: Tune, width: float) -> None:
    """The tune's name, origin and a fact, then Play, or Stop and the progress while it plays"""
    synth = state.synth
    playing = synth is not None and synth.tune is tune
    tune_color = imgui.color_convert_u32_to_float4(TUNE_KEY)
    imgui.push_style_color(imgui.Col_.border, tune_color if playing else imgui.get_style_color_vec4(imgui.Col_.border))
    imgui.push_style_color(imgui.Col_.child_bg, ImVec4(tune_color.x, tune_color.y, tune_color.z, 0.12 if playing else 0))
    imgui.push_style_var(imgui.StyleVar_.child_rounding, em_size(0.5))
    imgui.begin_child(tune.name, ImVec2(width, em_size(7.6)), imgui.ChildFlags_.borders.value)

    imgui.push_font(None, imgui.get_style().font_size_base * 1.3)
    imgui.text(tune.name)
    imgui.pop_font()
    imgui.text_disabled(tune.origin)
    imgui.text_wrapped(tune.fact)

    imgui.set_cursor_pos_y(imgui.get_window_height() - imgui.get_frame_height() - imgui.get_style().window_padding.y)
    if synth is not None and playing:
        if imgui.button(icons_fontawesome_4.ICON_FA_STOP + " Stop"):
            synth.stop_tune()
        imgui.same_line()
        imgui.push_style_color(imgui.Col_.plot_histogram, tune_color)
        imgui.progress_bar(synth.tune_progress(), ImVec2(-1, 0), "")
        imgui.pop_style_color()
    elif imgui.button(icons_fontawesome_4.ICON_FA_PLAY + " Play"):
        new_synth = state.ensure_synth()
        if new_synth is not None:
            new_synth.play_tune(tune, state.tempo, WAVEFORMS[state.waveform])

    imgui.end_child()
    imgui.pop_style_var()
    imgui.pop_style_color(2)


def tune_cards(state: State) -> None:
    spacing = imgui.get_style().item_spacing.x
    width = (imgui.get_content_region_avail().x - (len(TUNES) - 1) * spacing) / len(TUNES)
    for i, tune in enumerate(TUNES):
        if i > 0:
            imgui.same_line()
        tune_card(state, tune, width)


def waveform_button(state: State, i: int) -> None:
    """A button that draws its waveform"""
    name = WAVEFORMS[i]
    selected = state.waveform == i
    if imgui.invisible_button(name, em_to_vec2(3.4, 2.4)):
        state.waveform = i
    imgui.set_item_tooltip(name)
    p_min, p_max = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    draw_list = imgui.get_window_draw_list()
    background = imgui.Col_.button_hovered if imgui.is_item_hovered() else imgui.Col_.frame_bg
    draw_list.add_rect_filled(p_min, p_max, imgui.get_color_u32(background), em_size(0.3))
    if selected:
        draw_list.add_rect(p_min, p_max, PLAYED_KEY, em_size(0.3), thickness=em_size(0.1))

    t = np.linspace(0.0, 2.0, 257)  # two periods
    margin = em_size(0.5)
    xs = p_min.x + margin + t / 2 * (p_max.x - p_min.x - 2 * margin)
    ys = (p_min.y + p_max.y) / 2 - WAVE_SHAPES[name](t) * ((p_max.y - p_min.y) / 2 - margin)
    color = PLAYED_KEY if selected else imgui.get_color_u32(imgui.Col_.text)
    draw_list.add_polyline(list(zip(xs.tolist(), ys.tolist(), strict=True)), color, em_size(0.1), 0)


def knob(label: str, value: float, v_min: float, v_max: float, format: str, flags: int = 0) -> tuple[bool, float]:
    """A knob, its label above and its value below"""
    imgui.begin_vertical(label, ImVec2(0, 0), 0.5)
    r = imgui_knobs.knob(label, value, v_min, v_max, format=format, flags=flags, size=em_size(4.0),
                         variant=imgui_knobs.ImGuiKnobVariant_.wiper)
    imgui.end_vertical()
    return r


def controls(state: State) -> None:
    """A row: the synth's name, the waveforms, and the knobs"""
    imgui.begin_horizontal("controls", ImVec2(imgui.get_content_region_avail().x, 0), 0.5)

    imgui.begin_vertical("name")
    imgui.push_font(None, imgui.get_style().font_size_base * 1.8)
    imgui.text_colored(imgui.color_convert_u32_to_float4(PLAYED_KEY), "PY-25")
    imgui.pop_font()
    imgui.text_disabled("Python synthesizer")
    imgui.end_vertical()
    imgui.spring()

    imgui.begin_vertical("waveforms")
    imgui.text_disabled("Waveform")
    imgui.begin_horizontal("waveform buttons")
    for i in range(len(WAVEFORMS)):
        waveform_button(state, i)
    imgui.end_horizontal()
    imgui.end_vertical()
    imgui.spring()

    imgui_knobs.set_knob_colors(KNOB_COLORS)
    changed1, state.echo = knob("Echo", state.echo, 0.0, 1.0, "%.2f")
    imgui.spring(0, em_size(1))
    changed2, state.brightness = knob("Brightness", state.brightness, 200.0, 12000.0, "%.0f Hz",
                                      imgui_knobs.ImGuiKnobFlags_.logarithmic.value)
    imgui.spring(0, em_size(1))
    changed3, state.volume = knob("Volume", state.volume, 0.0, 1.0, "%.2f")
    imgui.spring(0, em_size(1))
    _, state.tempo = knob("Tempo", state.tempo, 60.0, 240.0, "%.0f bpm")
    imgui_knobs.unset_knob_colors()
    imgui.end_horizontal()
    if (changed1 or changed2 or changed3) and state.synth is not None:
        state.synth.apply(state)


KeyRect = tuple[int, ImVec2, ImVec2]  # note, top left, bottom right


def piano_key_rects(p0: ImVec2, size: ImVec2) -> tuple[list[KeyRect], list[KeyRect]]:
    """The white keys, and the black ones (they lie on top)"""
    white_width = size.x / NB_WHITE_KEYS
    whites: list[KeyRect] = []
    blacks: list[KeyRect] = []
    x = p0.x
    for note in NOTES:
        if is_black(note):  # centered on the border of two white keys
            blacks.append((note, ImVec2(x - 0.3 * white_width, p0.y), ImVec2(x + 0.3 * white_width, p0.y + 0.62 * size.y)))
        else:
            whites.append((note, ImVec2(x, p0.y), ImVec2(x + white_width, p0.y + size.y)))
            x += white_width
    return whites, blacks


def computer_keys_held() -> set[int]:
    if imgui.get_io().want_text_input:  # typing a value in a knob
        return set()
    return {LOWEST_NOTE + i for i, key in enumerate(PIANO_KEYS) if imgui.is_key_down(key)}


def draw_key(note: int, p_min: ImVec2, p_max: ImVec2, color: int) -> None:
    """A key, with the shadow of the felt at its top, its front face, and its labels"""
    draw_list = imgui.get_window_draw_list()
    rounding = em_size(0.25)
    bottom_corners = imgui.ImDrawFlags_.round_corners_bottom.value
    black = is_black(note)
    front = em_size(0.9 if black else 0.5)
    draw_list.add_rect_filled(p_min, p_max, color, rounding, bottom_corners)
    draw_list.add_rect_filled_multi_color(p_min, ImVec2(p_max.x, p_min.y + em_size(1.0)),
                                          KEY_SHADOW, KEY_SHADOW, NO_SHADOW, NO_SHADOW)
    inset = em_size(0.12) if black else 0.0
    draw_list.add_rect_filled(ImVec2(p_min.x + inset, p_max.y - front), ImVec2(p_max.x - inset, p_max.y - inset),
                              BLACK_KEY_FRONT if black else WHITE_KEY_FRONT, rounding, bottom_corners)
    draw_list.add_rect(p_min, p_max, KEY_OUTLINE, rounding, flags=bottom_corners)

    labels = [KEY_LABELS[note - LOWEST_NOTE]]
    if note % 12 == 0:
        labels.insert(0, f"C{note // 12 - 1}")  # the octave, above the key's letter
    label_color = imgui.IM_COL32(200, 200, 200, 255) if black else imgui.IM_COL32(70, 70, 70, 255)
    y = p_max.y - front - em_size(0.3)
    for label in reversed(labels):
        label_size = imgui.calc_text_size(label)
        y -= label_size.y
        draw_list.add_text(ImVec2((p_min.x + p_max.x - label_size.x) / 2, y), label_color, label)


def piano(state: State) -> None:
    """Draws the keyboard, and plays the keys held with the mouse or the computer keyboard"""
    p0 = imgui.get_cursor_screen_pos()
    width = imgui.get_content_region_avail().x
    felt = em_size(0.45)
    imgui.invisible_button("piano", ImVec2(width, felt + em_size(PIANO_HEIGHT)))
    whites, blacks = piano_key_rects(ImVec2(p0.x, p0.y + felt), ImVec2(width, em_size(PIANO_HEIGHT)))

    held = computer_keys_held()
    if imgui.is_item_active():  # the mouse is pressed on the piano: dragging it makes a glissando
        mouse = imgui.get_mouse_pos()
        for note, p_min, p_max in blacks + whites:  # the black keys first, since they lie on top
            if p_min.x <= mouse.x < p_max.x and p_min.y <= mouse.y < p_max.y:
                held.add(note)
                break

    if held:
        state.ensure_synth()
    tune_notes: set[int] = set()
    if state.synth is not None:
        state.synth.update(held, WAVEFORMS[state.waveform])
        tune_notes = state.synth.tune_notes_sounding()

    imgui.get_window_draw_list().add_rect_filled(p0, ImVec2(p0.x + width, p0.y + felt), FELT)
    for keys, key_color in ((whites, WHITE_KEY), (blacks, BLACK_KEY)):
        for note, p_min, p_max in keys:
            draw_key(note, p_min, p_max,
                     PLAYED_KEY if note in held else TUNE_KEY if note in tune_notes else key_color)


def synth_panel(state: State) -> None:
    """The synthesizer: its controls, above the piano"""
    imgui.push_style_color(imgui.Col_.child_bg, PANEL)
    imgui.push_style_var(imgui.StyleVar_.child_rounding, em_size(0.6))
    imgui.push_style_var(imgui.StyleVar_.window_padding, em_to_vec2(1.0, 0.8))
    imgui.begin_child("synth", ImVec2(0, 0),
                      imgui.ChildFlags_.auto_resize_y.value | imgui.ChildFlags_.always_use_window_padding.value)
    controls(state)
    imgui.dummy(em_to_vec2(0, 0.3))
    piano(state)
    imgui.end_child()
    imgui.pop_style_var(2)
    imgui.pop_style_color()


def scope(state: State) -> None:
    """The waveform and the spectrum of what the speakers play, in the remaining height"""
    avail = imgui.get_content_region_avail()
    size = ImVec2((avail.x - imgui.get_style().item_spacing.x) / 2, max(avail.y, em_size(6)))
    draw_list = imgui.get_window_draw_list()
    rounding = em_size(0.5)
    caption_color = imgui.get_color_u32(imgui.Col_.text_disabled)

    # The waveform, from a rising zero crossing, so that a steady note stands still
    p0 = imgui.get_cursor_screen_pos()
    imgui.dummy(size)
    draw_list.add_rect_filled(p0, ImVec2(p0.x + size.x, p0.y + size.y), SCOPE_BACKGROUND, rounding)
    draw_list.add_text(ImVec2(p0.x + em_size(0.6), p0.y + em_size(0.4)), caption_color, "Waveform")
    samples = state.synth.waveform() if state.synth is not None else np.zeros(SCOPE_SAMPLES, np.float32)
    rising = np.flatnonzero((samples[:-1] < 0) & (samples[1:] >= 0))
    start = rising[0] if len(rising) > 0 else 0
    shown = np.clip(samples[start:start + SCOPE_SAMPLES] * SCOPE_ZOOM, -1.0, 1.0)
    xs = p0.x + np.linspace(0.0, size.x, len(shown))
    ys = p0.y + size.y / 2 * (1.0 - 0.9 * shown)
    points: list[ImVec2Like] = list(zip(xs.tolist(), ys.tolist(), strict=True))
    draw_list.add_polyline(points, SCOPE_GLOW, em_size(0.4), 0)
    draw_list.add_polyline(points, SCOPE_LINE, em_size(0.12), 0)

    # The spectrum
    imgui.same_line()
    p0 = imgui.get_cursor_screen_pos()
    imgui.dummy(size)
    draw_list.add_rect_filled(p0, ImVec2(p0.x + size.x, p0.y + size.y), SCOPE_BACKGROUND, rounding)
    draw_list.add_text(ImVec2(p0.x + em_size(0.6), p0.y + em_size(0.4)), caption_color, "Spectrum, up to 3 kHz")
    if state.synth is not None:
        levels = state.synth.spectrum()[:SPECTRUM_BINS] / 255.0
        bar_width = size.x / SPECTRUM_BINS
        bottom = p0.y + size.y - rounding
        for i, level in enumerate(levels.tolist()):
            x = p0.x + i * bar_width
            draw_list.add_rect_filled(ImVec2(x, bottom - 0.85 * size.y * level), ImVec2(x + 0.7 * bar_width, bottom),
                                      SPECTRUM_COLORS[i])


STATE = State()


def gui() -> None:
    header()
    tune_cards(STATE)
    imgui.dummy(em_to_vec2(0, 0.3))
    synth_panel(STATE)
    imgui.dummy(em_to_vec2(0, 0.3))
    scope(STATE)


immapp.run(gui, window_title="WebAudio synthesizer", window_size=(1100, 860), fps_idle=0, with_markdown=True)
