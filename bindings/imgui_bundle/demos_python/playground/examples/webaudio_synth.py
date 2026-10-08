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

Browsers require a *user gesture* before an `AudioContext` may produce sound, and it must start inside the gesture's
handler, which the frames of Python come after. A few lines of JavaScript start it at the first touch, click or key
press anywhere on the page: a phone takes a moment to start its audio, better at the first scroll than at the first
note. The tunes wait until it runs.
"""
import sys
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from imgui_bundle import imgui, immapp, imgui_knobs, rich_md, icons_fontawesome_4, em_size, em_to_vec2, hello_imgui
from imgui_bundle import ImVec2, ImVec4, ImVec2Like, ImColor

IN_BROWSER = sys.platform == "emscripten"

HEADER = """
# WebAudio synthesizer
A small synthesizer written in Python, which plays through your browser's
[WebAudio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API).
Play it with the mouse, or with your computer keyboard (the letters are on the keys), or pick a tune.
"""

# The piano: four octaves, from C3 (MIDI note 48) to C7
LOWEST_NOTE = 48
NB_NOTES = 49
PIANO_HEIGHT = 13.0  # em
PIANO_HEIGHT_NARROW = 9.0  # em: on a narrow screen, so that the controls and the keys fit on the screen together
MIN_KEY_WIDTH = 2.4  # em: a white key at least as wide as a finger; else the piano shows part of its keys
STRIP_HEIGHT = 2.0  # em: the strip above the keys, the whole piano in miniature, which moves the view
VIEW_SPEED = 12.0  # 1/s: the view glides to its place (in about a quarter of a second)
# The computer keys that play two octaves, as in a tracker: the bottom letter row plays C4 to B4, the top row C5 to
# C6. The piano shows them on its keys.
KEYS_LOWEST_NOTE = 60  # C4
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

# The layout
NARROW_EM = 46.0  # below this width (in em, a phone): the tunes or the piano, a switch between them; smaller controls
TUNES_VIEW, PIANO_VIEW = 0, 1  # the views on a narrow screen
CARD_HEIGHT = 7.6  # em: the tune cards, in a row
CARD_MIN_HEIGHT_NARROW = 9.5  # em: two by two, the texts take more lines; else the cards fill the screen
VIEW_LABELS = [icons_fontawesome_4.ICON_FA_LIST + " Tunes", icons_fontawesome_4.ICON_FA_MUSIC + " Piano"]

# The scope
SCOPE_SAMPLES = 1024  # about 20 ms
SILENCE = 1e-4  # below this level, the scope's samples are silence
SCOPE_ZOOM = 3.0
SPECTRUM_BINS = 128  # of 1024: up to about 3 kHz
SCOPE_MIN_HEIGHT = 6.0  # em
SCOPE_MIN_HEIGHT_NARROW = 2.0  # em: in the piano view of a narrow screen, which fits the screen: less, no scope

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
STRIP_VEIL = imgui.IM_COL32(0, 0, 0, 150)  # over the keys out of view, in the strip
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


def white_keys_below(note: int) -> int:
    """The white keys of the piano below this note"""
    return sum(not is_black(n) for n in range(LOWEST_NOTE, note))


NB_WHITE_KEYS = sum(not is_black(note) for note in NOTES)
PIANO_KEYS = [imgui.Key[label.lower() if label.isalpha() else "_" + label] for label in KEY_LABELS]


# Creates window.pySynthAudio inside the handler of the first gesture (see the docstring at the top), and resumes it
# at each gesture: a phone may suspend it (a call, another app)
START_AUDIO_JS = """
if (!window.pySynthAudioListening) {
    window.pySynthAudioListening = true;
    const start = () => {
        window.pySynthAudio = window.pySynthAudio || new AudioContext();
        window.pySynthAudio.resume();
    };
    ['pointerdown', 'touchend', 'click', 'keydown'].forEach((e) => document.addEventListener(e, start, true));
}
"""
if IN_BROWSER:  # at once: the first gesture, wherever it lands, starts the audio
    import js  # type: ignore[import-not-found]

    js.eval(START_AUDIO_JS)


def audio_context() -> Any:
    """The page's audio context, once a gesture created it. None before, and on desktop."""
    if not IN_BROWSER:
        return None
    return getattr(js.window, "pySynthAudio", None)


class Synth:
    """The audio graph (see the docstring at the top). Needs the browser."""

    def __init__(self, ctx: Any) -> None:
        from js import Float32Array, Uint8Array  # type: ignore[import-not-found]

        self.ctx = ctx
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

    def starting(self) -> bool:
        """The browser is still starting the audio (a phone takes a moment)"""
        return bool(self.ctx.state != "running")

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
        # The first white key in view, when the piano shows part of its keys: C4, where the computer keys start
        self.first_key = white_keys_below(KEYS_LOWEST_NOTE)
        self.view: float | None = None  # the first white key drawn: it glides to first_key
        self.strip_pressed = False  # the press on the piano started on its strip: it moves the view
        self.narrow_view = TUNES_VIEW
        self.tune_to_show: Tune | None = None  # a tune that starts: the piano shows its keys

    def ensure_synth(self) -> None:
        """Each frame: creates the synth once a gesture created the page's audio (see audio_context)"""
        if self.synth is None:
            ctx = audio_context()
            if ctx is not None:
                self.synth = Synth(ctx)
                self.synth.apply(self)

    def sound_ready(self) -> bool:
        return self.synth is not None and not self.synth.starting()


def header() -> None:
    rich_md.render(HEADER)
    if not IN_BROWSER:
        imgui.text_colored(imgui.color_convert_u32_to_float4(PLAYED_KEY),
                           "No sound on desktop: this demo uses the browser's WebAudio API. Run it in the playground.")


def is_narrow() -> bool:
    return imgui.get_content_region_avail().x < em_size(NARROW_EM)


def tune_card(state: State, tune: Tune, size: ImVec2) -> None:
    """The tune's name, origin and a fact, then Play, or Stop and the progress while it plays"""
    synth = state.synth
    playing = synth is not None and synth.tune is tune
    tune_color = imgui.color_convert_u32_to_float4(TUNE_KEY)
    imgui.push_style_color(imgui.Col_.border, tune_color if playing else imgui.get_style_color_vec4(imgui.Col_.border))
    imgui.push_style_color(imgui.Col_.child_bg, ImVec4(tune_color.x, tune_color.y, tune_color.z, 0.12 if playing else 0))
    imgui.push_style_var(imgui.StyleVar_.child_rounding, em_size(0.5))
    imgui.begin_child(tune.name, size, imgui.ChildFlags_.borders.value)

    imgui.push_font(None, imgui.get_style().font_size_base * 1.3)
    imgui.text(tune.name)
    imgui.pop_font()
    imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
    imgui.text_wrapped(tune.origin)
    imgui.pop_style_color()
    imgui.text_wrapped(tune.fact)

    imgui.set_cursor_pos_y(imgui.get_window_height() - imgui.get_frame_height() - imgui.get_style().window_padding.y)
    if synth is not None and playing:
        stop_and_progress(synth)
    else:
        imgui.begin_disabled(not state.sound_ready())  # sound_status() says why
        if imgui.button(icons_fontawesome_4.ICON_FA_PLAY + " Play") and synth is not None:
            synth.play_tune(tune, state.tempo, WAVEFORMS[state.waveform])
            state.tune_to_show = tune
            state.narrow_view = PIANO_VIEW  # on a narrow screen: watch the keys play
        imgui.end_disabled()

    imgui.end_child()
    imgui.pop_style_var()
    imgui.pop_style_color(2)


def stop_and_progress(synth: Synth) -> None:
    """Stop, and the tune's progress, on one line"""
    if imgui.button(icons_fontawesome_4.ICON_FA_STOP + " Stop"):
        synth.stop_tune()
    imgui.same_line()
    imgui.push_style_color(imgui.Col_.plot_histogram, imgui.color_convert_u32_to_float4(TUNE_KEY))
    imgui.progress_bar(synth.tune_progress(), ImVec2(-1, 0), "")
    imgui.pop_style_color()


def tune_cards(state: State, height: float) -> None:
    """The tunes in a row, or two by two on a narrow screen"""
    per_row = 2 if is_narrow() else len(TUNES)
    spacing = imgui.get_style().item_spacing.x
    width = (imgui.get_content_region_avail().x - (per_row - 1) * spacing) / per_row
    for i, tune in enumerate(TUNES):
        if i % per_row > 0:
            imgui.same_line()
        tune_card(state, tune, ImVec2(width, height))


def waveform_button(state: State, i: int, size: ImVec2) -> None:
    """A button that draws its waveform"""
    name = WAVEFORMS[i]
    selected = state.waveform == i
    if imgui.invisible_button(name, size):
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


def knob(label: str, value: float, v_min: float, v_max: float, format: str, size: float,
         flags: int = 0) -> tuple[bool, float]:
    """A knob, its label above and its value below"""
    imgui.begin_vertical(label, ImVec2(0, 0), 0.5)
    r = imgui_knobs.knob(label, value, v_min, v_max, format=format, flags=flags, size=size,
                         variant=imgui_knobs.ImGuiKnobVariant_.wiper)
    imgui.end_vertical()
    # On a touch screen, a drag on the knob turns it at once (it does not scroll the page), even after a pause
    hello_imgui.set_item_takes_touch_drags(long_press_is_right_click=False)
    return r


def synth_name(subtitle: bool) -> None:
    imgui.begin_vertical("name")
    imgui.push_font(None, imgui.get_style().font_size_base * 1.8)
    imgui.text_colored(imgui.color_convert_u32_to_float4(PLAYED_KEY), f"PY-{NB_NOTES}")
    imgui.pop_font()
    if subtitle:
        imgui.text_disabled("Python synthesizer")
    imgui.end_vertical()


def waveforms(state: State, button_size: ImVec2) -> None:
    imgui.begin_vertical("waveforms")
    imgui.text_disabled("Waveform")
    imgui.begin_horizontal("waveform buttons")
    for i in range(len(WAVEFORMS)):
        waveform_button(state, i, button_size)
    imgui.end_horizontal()
    imgui.end_vertical()


def knobs(state: State, size: float, spread: bool) -> bool:
    """The knobs, side by side: 1 em apart, or spread over the row; True when one that the synth reads changed"""
    gap = (1.0, -1.0) if spread else (0.0, em_size(1))  # the weight and the spacing of the springs between them
    imgui_knobs.set_knob_colors(KNOB_COLORS)
    changed1, state.echo = knob("Echo", state.echo, 0.0, 1.0, "%.2f", size)
    imgui.spring(*gap)
    changed2, state.brightness = knob("Brightness", state.brightness, 200.0, 12000.0, "%.0f Hz", size,
                                      imgui_knobs.ImGuiKnobFlags_.logarithmic.value)
    imgui.spring(*gap)
    changed3, state.volume = knob("Volume", state.volume, 0.0, 1.0, "%.2f", size)
    imgui.spring(*gap)
    _, state.tempo = knob("Tempo", state.tempo, 60.0, 240.0, "%.0f bpm", size)
    imgui_knobs.unset_knob_colors()
    return changed1 or changed2 or changed3


def controls(state: State) -> None:
    """The synth's name, the waveforms, and the knobs: in a row; on a narrow screen, on two rows and smaller"""
    width = imgui.get_content_region_avail().x
    if is_narrow():
        imgui.begin_horizontal("name and waveforms", ImVec2(width, 0), 0.5)
        synth_name(subtitle=False)
        imgui.spring()
        waveforms(state, em_to_vec2(2.8, 2.0))
        imgui.end_horizontal()
        imgui.begin_horizontal("knobs", ImVec2(width, 0), 0.5)
        imgui.spring()
        changed = knobs(state, em_size(3.6), spread=True)  # wide enough for "4000 Hz" and "120 bpm"
        imgui.spring()
        imgui.end_horizontal()
    else:
        imgui.begin_horizontal("controls", ImVec2(width, 0), 0.5)
        synth_name(subtitle=True)
        imgui.spring()
        waveforms(state, em_to_vec2(3.4, 2.4))
        imgui.spring()
        changed = knobs(state, em_size(4.0), spread=False)
        imgui.end_horizontal()
    if changed and state.synth is not None:
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
    return {KEYS_LOWEST_NOTE + i for i, key in enumerate(PIANO_KEYS) if imgui.is_key_down(key)}


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

    i = note - KEYS_LOWEST_NOTE
    labels = [KEY_LABELS[i]] if 0 <= i < len(KEY_LABELS) else []  # the computer key that plays it
    if note % 12 == 0:
        labels.insert(0, f"C{note // 12 - 1}")  # the octave, above the key's letter
    label_color = imgui.IM_COL32(200, 200, 200, 255) if black else imgui.IM_COL32(70, 70, 70, 255)
    y = p_max.y - front - em_size(0.3)
    for label in reversed(labels):
        label_size = imgui.calc_text_size(label)
        y -= label_size.y
        draw_list.add_text(ImVec2((p_min.x + p_max.x - label_size.x) / 2, y), label_color, label)


def draw_strip(p0: ImVec2, size: ImVec2, first_key: float, nb_shown: int, key_color: Callable[[int, int], int]) -> None:
    """The whole piano in miniature: the keys out of view veiled, a frame around the ones in view"""
    draw_list = imgui.get_window_draw_list()
    whites, blacks = piano_key_rects(p0, size)
    for note, p_min, p_max in whites:
        draw_list.add_rect_filled(p_min, p_max, key_color(note, WHITE_KEY))
        draw_list.add_rect(p_min, p_max, KEY_OUTLINE)
    for note, p_min, p_max in blacks:
        draw_list.add_rect_filled(p_min, p_max, key_color(note, BLACK_KEY))
    x0 = p0.x + size.x * first_key / NB_WHITE_KEYS
    x1 = p0.x + size.x * (first_key + nb_shown) / NB_WHITE_KEYS
    draw_list.add_rect_filled(p0, ImVec2(x0, p0.y + size.y), STRIP_VEIL)
    draw_list.add_rect_filled(ImVec2(x1, p0.y), ImVec2(p0.x + size.x, p0.y + size.y), STRIP_VEIL)
    draw_list.add_rect(ImVec2(x0, p0.y), ImVec2(x1, p0.y + size.y), PLAYED_KEY, em_size(0.2), thickness=em_size(0.15))


def piano(state: State) -> None:
    """Draws the piano, and plays the keys held with the mouse, a finger or the computer keyboard. When the keys would
    be thinner than a finger, it shows part of them: a strip above them, the whole piano in miniature, moves the view"""
    p0 = imgui.get_cursor_screen_pos()
    width = imgui.get_content_region_avail().x
    nb_shown = max(1, min(NB_WHITE_KEYS, int(width / em_size(MIN_KEY_WIDTH))))  # the white keys in view
    has_strip = nb_shown < NB_WHITE_KEYS
    top = em_size(STRIP_HEIGHT if has_strip else 0.45)  # the strip, or the felt
    keys_p0 = ImVec2(p0.x, p0.y + top)
    keys_size = ImVec2(width, em_size(PIANO_HEIGHT_NARROW if is_narrow() else PIANO_HEIGHT))
    imgui.invisible_button("piano", ImVec2(width, top + keys_size.y))
    # On a touch screen, a key plays at once, a drag is a glissando, and a still finger holds the note
    hello_imgui.set_item_takes_touch_drags(long_press_is_right_click=False)

    mouse = imgui.get_mouse_pos()
    if imgui.is_item_activated():
        state.strip_pressed = has_strip and mouse.y < keys_p0.y
    if imgui.is_item_active() and state.strip_pressed:  # the view follows the finger on the strip
        state.first_key = round((mouse.x - p0.x) / width * NB_WHITE_KEYS - nb_shown / 2)
    if state.tune_to_show is not None:  # the view centers on the tune's notes
        notes = [note for note, _ in parse_notes(state.tune_to_show.notes) if note is not None]
        state.first_key = round((white_keys_below(min(notes)) + white_keys_below(max(notes)) + 1 - nb_shown) / 2)
        state.tune_to_show = None
    state.first_key = max(0, min(state.first_key, NB_WHITE_KEYS - nb_shown))
    if state.view is None:
        state.view = float(state.first_key)
    state.view += (state.first_key - state.view) * min(1.0, imgui.get_io().delta_time * VIEW_SPEED)
    if abs(state.first_key - state.view) < 0.01:
        state.view = float(state.first_key)
    else:
        hello_imgui.request_refresh()  # the view glides on its own

    # The keys: the whole piano at their size, shifted so that the first key in view is at the left
    white_width = width / nb_shown
    whites, blacks = piano_key_rects(ImVec2(p0.x - state.view * white_width, keys_p0.y),
                                     ImVec2(white_width * NB_WHITE_KEYS, keys_size.y))
    held = computer_keys_held()
    if imgui.is_item_active() and not state.strip_pressed and p0.x <= mouse.x < p0.x + width:
        for note, p_min, p_max in blacks + whites:  # the black keys first, since they lie on top
            if p_min.x <= mouse.x < p_max.x and p_min.y <= mouse.y < p_max.y:
                held.add(note)
                break

    tune_notes: set[int] = set()
    if state.synth is not None:
        state.synth.update(held, WAVEFORMS[state.waveform])
        tune_notes = state.synth.tune_notes_sounding()

    def key_color(note: int, normal: int) -> int:
        return PLAYED_KEY if note in held else TUNE_KEY if note in tune_notes else normal

    draw_list = imgui.get_window_draw_list()
    draw_list.push_clip_rect(keys_p0, ImVec2(keys_p0.x + width, keys_p0.y + keys_size.y), True)
    for keys, normal in ((whites, WHITE_KEY), (blacks, BLACK_KEY)):
        for note, p_min, p_max in keys:
            draw_key(note, p_min, p_max, key_color(note, normal))
    draw_list.pop_clip_rect()
    if has_strip:
        draw_strip(p0, ImVec2(width, top - em_size(0.2)), state.view, nb_shown, key_color)
    else:
        draw_list.add_rect_filled(p0, ImVec2(p0.x + width, p0.y + top), FELT)


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


def scope(state: State, height: float) -> None:
    """The waveform and the spectrum of what the speakers play"""
    size = ImVec2((imgui.get_content_region_avail().x - imgui.get_style().item_spacing.x) / 2, height)
    draw_list = imgui.get_window_draw_list()
    rounding = em_size(0.5)
    caption_color = imgui.get_color_u32(imgui.Col_.text_disabled)

    # The waveform, from a rising zero crossing, so that a steady note stands still
    p0 = imgui.get_cursor_screen_pos()
    imgui.dummy(size)
    draw_list.add_rect_filled(p0, ImVec2(p0.x + size.x, p0.y + size.y), SCOPE_BACKGROUND, rounding)
    draw_list.add_text(ImVec2(p0.x + em_size(0.6), p0.y + em_size(0.4)), caption_color, "Waveform")
    samples = state.synth.waveform() if state.synth is not None else np.zeros(SCOPE_SAMPLES, np.float32)
    sounding = state.synth is not None and (state.synth.tune is not None or bool(np.abs(samples).max() > SILENCE))
    hello_imgui.set_item_is_live(sounding)  # the scope moves on its own while it shows sound (notes, their echo)
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


def view_switch(state: State) -> None:
    """On a narrow screen: the tunes, or the piano"""
    width = (imgui.get_content_region_avail().x - imgui.get_style().item_spacing.x) / 2
    for view, label in enumerate(VIEW_LABELS):
        if view > 0:
            imgui.same_line()
        selected = state.narrow_view == view
        if selected:
            imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
        if imgui.button(label, ImVec2(width, em_size(2.2))):
            state.narrow_view = view
        if selected:
            imgui.pop_style_color()


def sound_status(state: State) -> None:
    """In the browser, until the sound runs: a line that says why the tunes wait"""
    if not IN_BROWSER or state.sound_ready():
        return
    color = imgui.color_convert_u32_to_float4(TUNE_KEY)
    if state.synth is None:  # browsers wait for a gesture
        touch = imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen.value
        text = ("Tap" if touch else "Click") + " anywhere to start the sound"
    else:  # a phone takes a moment: the text pulses meanwhile
        text = "Starting the sound..."
        color = ImVec4(color.x, color.y, color.z, 0.65 + 0.35 * float(np.sin(5.0 * imgui.get_time())))
        hello_imgui.request_refresh()
    imgui.align_text_to_frame_padding()
    imgui.text_colored(color, icons_fontawesome_4.ICON_FA_VOLUME_UP + "  " + text)


def now_playing(state: State) -> None:
    """On a narrow screen, below the piano: the tune that plays and Stop, or why the sound waits"""
    synth = state.synth
    if synth is None or synth.tune is None:
        sound_status(state)
        return
    imgui.align_text_to_frame_padding()
    imgui.text_colored(imgui.color_convert_u32_to_float4(TUNE_KEY), synth.tune.name)
    imgui.same_line()
    stop_and_progress(synth)


def gui() -> None:
    STATE.ensure_synth()
    if not is_narrow():
        header()
        sound_status(STATE)
        tune_cards(STATE, em_size(CARD_HEIGHT))
        imgui.dummy(em_to_vec2(0, 0.3))
        synth_panel(STATE)
        imgui.dummy(em_to_vec2(0, 0.3))
        scope(STATE, max(imgui.get_content_region_avail().y, em_size(SCOPE_MIN_HEIGHT)))
        return

    # On a narrow screen (a phone): the tunes, or the piano, each down to the bottom of the screen without a scroll
    bottom = imgui.get_window_height() - imgui.get_style().window_padding.y  # in the window's content
    if STATE.narrow_view == TUNES_VIEW:
        header()
        view_switch(STATE)
        sound_status(STATE)
        two_rows = bottom - imgui.get_cursor_pos_y() - imgui.get_style().item_spacing.y
        tune_cards(STATE, max(two_rows / 2, em_size(CARD_MIN_HEIGHT_NARROW)))
        if STATE.synth is not None:  # the piano is not drawn: the computer keys still play, and a tune still ends
            STATE.synth.update(computer_keys_held(), WAVEFORMS[STATE.waveform])
    else:  # the line below the piano comes and goes: the scope takes the rest, so that the keys stay in place
        view_switch(STATE)
        synth_panel(STATE)
        imgui.dummy(em_to_vec2(0, 0.3))
        now_playing(STATE)
        scope_height = bottom - imgui.get_cursor_pos_y()
        if scope_height >= em_size(SCOPE_MIN_HEIGHT_NARROW):
            scope(STATE, scope_height)


immapp.run(gui, window_title="WebAudio synthesizer", window_size=(1100, 860), with_markdown=True)
