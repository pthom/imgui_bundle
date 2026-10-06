"""narrator: the player of narrated explorables.

A lesson is the `::md Lesson` section of a program (see the format in _plans/narrated_explorables/nex_dsl__format.md):
chapters are `##` headings, the narration is its paragraphs, and `cues` fenced blocks before a paragraph say what
happens on the stage while it is read. The program declares what the cues may touch (parameters, actions), tags the
widgets that show the parameters, and calls `lesson.gui()` for the strip (the captions, the controls, the chapters).

The voice: `python narrator.py build scenario.md` synthesizes one clip per sentence (edge-tts, the voice of the front
matter) into `scenario_audio/` beside the script, with the words' timings; only new sentences are synthesized. With
the clips, the audio is the clock: a sentence lasts what its clip lasts, and a cue anchored to words fires on them.
Without them (or with the voice off), the clock is estimated from the text.
"""
import hashlib
import inspect
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from imgui_bundle import hello_imgui, imgui, rich_md
from imgui_bundle import ImVec2, ImVec4

SECONDS_PER_CHAR = 0.06          # the silent clock: Tangible's estimate of a voice's pace
SENTENCE_GAP = 0.4               # the silence after a sentence
CHAPTER_GAP = 0.8                # the silence before a chapter
HIGHLIGHT_DURATION = 3.0
RESERVED_SECTIONS = ("More", "Code", "References")
IN_BROWSER = sys.platform == "emscripten"
DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class LessonError(Exception):
    pass


# =============================================================================
# The script, parsed
# =============================================================================

@dataclass
class Sentence:
    text: str
    char_start: int              # in the paragraph's text
    start: float = 0.0           # lesson time
    duration: float = 0.0
    clip: str = ""               # the audio file of the sentence, if synthesized
    words: list[tuple[float, str]] = field(default_factory=list)   # (offset in the clip, word), from the synthesis


@dataclass
class Paragraph:
    chapter: int
    text: str                    # the markdown of the paragraph, as spoken and shown
    line: int
    sentences: list[Sentence] = field(default_factory=list)
    start: float = 0.0
    end: float = 0.0


@dataclass
class Section:
    kind: str                    # More, Code, References
    title: str
    markdown: str


@dataclass
class Chapter:
    title: str
    line: int
    paragraphs: list[Paragraph] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    start: float = 0.0
    end: float = 0.0


@dataclass
class Event:
    time: float
    kind: str                    # set, animate, highlight, pause, challenge, call
    param: str = ""
    value: Any = None
    over: float = 0.0
    prompt: str = ""
    until: str = ""
    hint: str = ""
    hint_after: float = 30.0
    action: str = ""
    args: tuple[Any, ...] = ()
    chapter: int = 0
    line: int = 0
    anchor: tuple[Optional["Paragraph"], Optional[str]] = (None, None)   # the paragraph and the words it waits for


@dataclass
class Script:
    front_matter: dict[str, Any]
    chapters: list[Chapter]
    events: list[Event]
    markdown: str                # the whole lesson, for the full text view
    duration: float


class _CuesBlock:
    def __init__(self, source: str, line: int) -> None:
        self.source, self.line = source, line


def audio_folder(script_file: str) -> Path:
    return Path(script_file).with_name(Path(script_file).stem + "_audio")


def clip_key(voice: str, text: str) -> str:
    return hashlib.sha1(f"{voice}|{text}".encode("utf-8")).hexdigest()[:16]


def load_audio_index(script_file: str) -> dict[str, Any]:
    """{key: {"file", "duration", "words": [[offset, word], ...]}}, written by the build step"""
    index = audio_folder(script_file) / "index.json"
    if index.is_file():
        try:
            return dict(json.loads(index.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return {}
    return {}


def _read_script(file: str, section: str, resolve: bool = True) -> str:
    """The script's text, its transclusions resolved: a markdown file as it is, or a ::md section of a program"""
    base = Path(file).parent

    def read_file(path: str) -> Optional[str]:
        p = Path(path) if os.path.isabs(path) else base / path
        return p.read_text(encoding="utf-8") if p.is_file() else None

    if file.endswith(".md"):
        text = read_file(file)
        if text is None:
            raise LessonError(f"{file} not found")
        return rich_md.resolve_transclusions(text, read_file, file) if resolve else text
    return rich_md.resolve_transclusions(f"![[{Path(file).name}#{section}]]", read_file, file)


def _parse_front_matter(lines: list[str]) -> tuple[dict[str, Any], int]:
    """A small YAML: `key: value`, and one level of nesting under `key:`"""
    result: dict[str, Any] = {}
    if not lines or lines[0].strip() != "---":
        return result, 0
    current = result
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return result, i + 1
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if line.startswith(" "):
            current[key.strip()] = _parse_scalar(value)
        elif value:
            current = result
            result[key.strip()] = _parse_scalar(value)
        else:
            current = result[key.strip()] = {}
    raise LessonError("the front matter has no closing ---")


def _parse_scalar(value: str) -> Any:
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value.strip("'\"")


def _is_prose(line: str) -> bool:
    """A line that the voice reads (not a heading, a fence, a picture, a formula, a table, an html tag)"""
    stripped = line.lstrip()
    return bool(stripped) and not stripped.startswith(("#", "```", "![", "$$", "|", "<", "---", "[["))


def _spoken_text(markdown: str) -> str:
    """What is spoken: the hints for the agent removed, the list bullets removed"""
    text = re.sub(r"\[\[[^\]]*\]\]", "", markdown)
    text = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", text, flags=re.MULTILINE)
    return " ".join(text.split())


def _split_sentences(paragraph: Paragraph) -> None:
    text = _spoken_text(paragraph.text)
    pos = 0
    for piece in _SENTENCE_END.split(text):
        if piece.strip():
            paragraph.sentences.append(Sentence(piece.strip(), text.find(piece, pos)))
            pos = text.find(piece, pos) + len(piece)


class Parser:
    def __init__(self, lesson: "Lesson", text: str) -> None:
        self.lesson = lesson
        self.lines = text.splitlines()
        self.chapters: list[Chapter] = []
        self.events: list[Event] = []
        self.pending_cues: list[_CuesBlock] = []
        self.paragraph_lines: list[str] = []
        self.paragraph_line = 0
        self.section: Optional[Section] = None

    def parse(self) -> Script:
        front_matter, start = _parse_front_matter(self.lines)
        i = start
        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()
            if stripped.startswith("```"):
                language = stripped[3:].strip().split()
                j = i + 1
                while j < len(self.lines) and not self.lines[j].strip().startswith("```"):
                    j += 1
                if language and language[-1] == "cues":
                    self._close_paragraph()
                    self.pending_cues.append(_CuesBlock("\n".join(self.lines[i + 1:j]), i + 2))
                elif self.section is not None:
                    self.section.markdown += "\n".join(self.lines[i:j + 1]) + "\n"
                i = j + 1
                continue
            if stripped.startswith("## ") or stripped.startswith("# "):
                self._close_paragraph()
                self._close_section()
                if stripped.startswith("## "):
                    self._attach_pending_to_chapter_start()
                    self.chapters.append(Chapter(stripped[3:].strip(), i + 1))
            elif stripped.startswith("### "):
                self._close_paragraph()
                self._close_section()
                title = stripped[4:].strip()
                kind, _, subtitle = title.partition(":")
                if kind.strip() in RESERVED_SECTIONS:
                    self.section = Section(kind.strip(), subtitle.strip() or kind.strip(), "")
            elif self.section is not None:
                self.section.markdown += line + "\n"
            elif _is_prose(line):
                if not self.paragraph_lines:
                    self.paragraph_line = i + 1
                self.paragraph_lines.append(line)
            else:
                self._close_paragraph()
            i += 1
        self._close_paragraph()
        self._close_section()
        self._attach_pending_to_chapter_start()
        self._time_everything()
        duration = self.chapters[-1].end if self.chapters else 0.0
        return Script(front_matter, self.chapters, sorted(self.events, key=lambda e: e.time), "\n".join(self.lines),
                      duration)

    def _close_section(self) -> None:
        if self.section is not None and self.chapters:
            self.chapters[-1].sections.append(self.section)
        self.section = None

    def _close_paragraph(self) -> None:
        if not self.paragraph_lines:
            return
        if not self.chapters:
            self.chapters.append(Chapter("", self.paragraph_line))
        paragraph = Paragraph(len(self.chapters) - 1, "\n".join(self.paragraph_lines), self.paragraph_line)
        _split_sentences(paragraph)
        self.chapters[-1].paragraphs.append(paragraph)
        self.paragraph_lines = []
        for block in self.pending_cues:
            self._run_cues(block, paragraph)
        self.pending_cues = []

    def _attach_pending_to_chapter_start(self) -> None:
        """A cues block with no paragraph after it fires when the chapter starts"""
        if self.pending_cues and self.chapters:
            for block in self.pending_cues:
                self._run_cues(block, None)
        self.pending_cues = []

    def _run_cues(self, block: _CuesBlock, paragraph: Optional[Paragraph]) -> None:
        """Runs a cues block once, in a namespace of recorders: each call records an event"""
        chapter = len(self.chapters) - 1
        events = self.events
        lesson = self.lesson

        def record(kind: str, **kw: Any) -> None:
            at = kw.pop("at", None)
            events.append(Event(0.0, kind, chapter=chapter, line=block.line, anchor=(paragraph, at), **kw))

        def check_param(name: str) -> None:
            if lesson.strict and name not in lesson.params:
                raise LessonError(f"line {block.line}: unknown parameter {name!r} (declared: {list(lesson.params)})")

        def check_value(name: str, value: Any) -> None:
            if name in lesson.params:
                lesson.params[name].check(value, block.line)

        def set_value(name: str, value: Any, at: Optional[str] = None) -> None:
            check_param(name)
            check_value(name, value)
            record("set", param=name, value=value, at=at)

        def animate(name: str, value: Any, over: Optional[float] = None, at: Optional[str] = None) -> None:
            check_param(name)
            check_value(name, value)
            record("animate", param=name, value=value, over=lesson.default_over if over is None else over, at=at)

        def highlight(name: str, at: Optional[str] = None) -> None:
            check_param(name)
            record("highlight", param=name, at=at)

        def pause(prompt: str, at: Optional[str] = None) -> None:
            record("pause", prompt=prompt, at=at)

        def challenge(prompt: str, until: str, hint: str = "", hint_after: float = 30.0,
                      at: Optional[str] = None) -> None:
            record("challenge", prompt=prompt, until=until, hint=hint, hint_after=hint_after, at=at)

        namespace: dict[str, Any] = {"set_value": set_value, "animate": animate, "highlight": highlight,
                                     "pause": pause, "challenge": challenge, **lesson.constants}
        for action_name in lesson.actions:
            def make_call(name: str) -> Callable[..., None]:
                def call(*args: Any, at: Optional[str] = None) -> None:
                    record("call", action=name, args=args, at=at)
                return call
            namespace[action_name] = make_call(action_name)
        try:
            exec(compile(block.source, f"{lesson.file}:cues at line {block.line}", "exec"), namespace)
        except LessonError:
            raise
        except Exception as e:
            raise LessonError(f"line {block.line}: {e}") from e

    def _time_everything(self) -> None:
        """The clock: a sentence lasts what its clip lasts, or an estimate from its length"""
        audio = self.lesson.audio_index
        folder = audio_folder(self.lesson.file)
        t = 0.0
        for i, chapter in enumerate(self.chapters):
            t += CHAPTER_GAP if i > 0 else 0.0     # the first chapter starts at 0: its cues set the opening state
            chapter.start = t
            for paragraph in chapter.paragraphs:
                paragraph.start = t
                for sentence in paragraph.sentences:
                    sentence.start = t
                    entry = audio.get(clip_key(self.lesson.voice, sentence.text))
                    if entry:
                        sentence.clip = str(folder / entry["file"])
                        sentence.duration = float(entry["duration"])
                        sentence.words = [(float(o), str(w)) for o, w in entry.get("words", [])]
                    else:
                        sentence.duration = max(0.8, len(sentence.text) * SECONDS_PER_CHAR)
                    t += sentence.duration + SENTENCE_GAP
                paragraph.end = t
            chapter.end = t
        for event in self.events:
            target, at = event.anchor
            if target is None:
                event.time = self.chapters[event.chapter].start
            elif at is None:
                event.time = target.start
            else:
                event.time = self._anchor_time(target, at, event.line)

    def _anchor_time(self, paragraph: Paragraph, words: str, line: int) -> float:
        text = _spoken_text(paragraph.text)
        pos = text.find(words)
        if pos < 0:
            raise LessonError(f"line {line}: the words {words!r} are not in the paragraph that follows")
        for sentence in paragraph.sentences:
            if sentence.char_start <= pos < sentence.char_start + len(sentence.text):
                if sentence.words:                 # the clip knows when each word is spoken
                    index = len(sentence.text[:pos - sentence.char_start].split())
                    if index < len(sentence.words):
                        return sentence.start + sentence.words[index][0]
                return sentence.start + sentence.duration * (pos - sentence.char_start) / max(1, len(sentence.text))
        return paragraph.start


# =============================================================================
# What the program declares
# =============================================================================

class Param:
    def __init__(self, name: str, owner: Any, attr_name: str, range_: Optional[tuple[float, float]]) -> None:
        self.name, self.owner, self.attr_name, self.range = name, owner, attr_name, range_
        self.kind = type(getattr(owner, attr_name))
        self.hold_until = -1.0           # the owner rule: the learner's value holds until then
        self.rect: Optional[tuple[ImVec2, ImVec2]] = None
        self.highlight_until = -1.0

    def get(self) -> Any:
        return getattr(self.owner, self.attr_name)

    def set(self, value: Any) -> None:
        setattr(self.owner, self.attr_name, self.kind(value) if self.kind in (int, float) else value)

    def check(self, value: Any, line: int) -> None:
        if self.range is not None and isinstance(value, (int, float)):
            lo, hi = self.range
            if not lo <= value <= hi:
                raise LessonError(f"line {line}: {self.name} = {value} is out of its range [{lo}, {hi}]")
        elif self.kind in (int, float) and not isinstance(value, (int, float)):
            raise LessonError(f"line {line}: {self.name} takes a number, not {value!r}")


# =============================================================================
# The audio: a clip played at a time, its position read each frame
# =============================================================================

class _MiniaudioBackend:
    """The desktop: miniaudio decodes the clip and plays it; the position is counted in frames"""
    RATE, CHANNELS = 44100, 2

    def __init__(self) -> None:
        import miniaudio  # type: ignore[import-untyped]
        self.miniaudio = miniaudio
        self.device: Any = None
        self.samples: Any = None
        self.frame = 0
        self.total = 0
        self.decoded: dict[str, Any] = {}

    def play(self, path: str, offset: float) -> None:
        self.stop()
        if path not in self.decoded:
            self.decoded[path] = self.miniaudio.decode_file(path, nchannels=self.CHANNELS, sample_rate=self.RATE)
        self.samples = self.decoded[path].samples
        self.total = len(self.samples) // self.CHANNELS
        self.frame = min(self.total, int(offset * self.RATE))
        self._start()

    def _start(self) -> None:
        def feed() -> Any:
            needed = yield b""
            while self.frame < self.total:
                chunk = self.samples[self.frame * self.CHANNELS:(self.frame + needed) * self.CHANNELS]
                self.frame += needed
                needed = yield chunk
        generator = feed()
        next(generator)
        self.device = self.miniaudio.PlaybackDevice(nchannels=self.CHANNELS, sample_rate=self.RATE)
        self.device.start(generator)

    def pause(self) -> None:
        if self.device is not None:
            self.device.close()
            self.device = None

    def resume(self) -> None:
        if self.device is None and self.samples is not None and self.frame < self.total:
            self._start()

    def stop(self) -> None:
        self.pause()
        self.samples, self.frame, self.total = None, 0, 0

    def position(self) -> float:
        return self.frame / self.RATE

    def done(self) -> bool:
        return self.samples is None or self.frame >= self.total


class _WebBackend:
    """The browser: an <audio> element plays the clip from a blob URL (the clip came with the lesson's files)"""

    def __init__(self) -> None:
        import js  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]
        self.js, self.to_js = js, to_js
        self.audio = js.Audio.new()
        self.urls: dict[str, str] = {}
        self.active = False

    def play(self, path: str, offset: float) -> None:
        if path not in self.urls:
            data = Path(path).read_bytes()
            blob = self.js.Blob.new(self.to_js([self.js.Uint8Array.new(data)]), self.to_js({"type": "audio/mpeg"}))
            self.urls[path] = self.js.URL.createObjectURL(blob)
        self.audio.src = self.urls[path]
        self.audio.currentTime = offset
        self.audio.play()
        self.active = True

    def pause(self) -> None:
        self.audio.pause()

    def resume(self) -> None:
        if self.active and not self.audio.ended:
            self.audio.play()

    def stop(self) -> None:
        self.audio.pause()
        self.active = False

    def position(self) -> float:
        return float(self.audio.currentTime)

    def done(self) -> bool:
        return not self.active or bool(self.audio.ended)


def make_audio_backend() -> Any:
    """The backend of this platform, or None when no audio can be played"""
    try:
        return _WebBackend() if IN_BROWSER else _MiniaudioBackend()
    except Exception:
        return None


# =============================================================================
# The player
# =============================================================================

class Lesson:
    """The player. `file` is the script: a markdown file, or a program whose ::md section `section` is the script."""

    def __init__(self, file: str, section: str = "Lesson", program: str = "") -> None:
        self.file, self.section = str(file), section
        self.program = str(program)                # the program's file, shown on demand (empty: the script's file)
        self.params: dict[str, Param] = {}
        self.derived: dict[str, Callable[[], Any]] = {}
        self.actions: dict[str, Callable[..., Any]] = {}
        self.constants: dict[str, Any] = {}
        self.script: Optional[Script] = None
        self.error: str = ""
        self.t = 0.0
        self.playing = False
        self.started = False                       # True once a script is loaded: the lesson drives the parameters
        self.waiting: Optional[Event] = None       # the pause or challenge the lesson waits on
        self.waiting_since = 0.0
        self.passed: set[int] = set()              # the pauses passed (by id)
        self.fired: set[int] = set()               # the actions fired (by id)
        self.initial: dict[str, Any] = {}
        self.default_over = 1.0
        self.delay_after_interaction = 8.0
        self.open_section: Optional[Section] = None
        self.show_full_text = False
        self.show_source = ""                      # "", "scenario" or "program": the source shown under the strip
        self.strict = True                         # False for the build step: the parameters are not declared there
        self.voice = DEFAULT_VOICE
        self.voice_on = True
        self.audio_index: dict[str, Any] = {}
        self.audio = make_audio_backend()
        self._speaking: Optional[Sentence] = None  # the sentence whose clip plays
        self._mtime = 0.0
        self._last_check = 0.0
        self._loaded = False

    @staticmethod
    def from_this_file(section: str = "Lesson") -> "Lesson":
        caller = inspect.stack()[1].frame.f_globals.get("__file__", "")
        return Lesson(caller, section)

    # ---- declarations --------------------------------------------------------------------------------------------
    def param(self, name: str, owner: Any, attr_name: Optional[str] = None,
              range: Optional[tuple[float, float]] = None) -> None:
        self.params[name] = Param(name, owner, attr_name or name, range)

    def derive(self, name: str, getter: Callable[[], Any]) -> None:
        self.derived[name] = getter

    def action(self, name: str, function: Callable[..., Any]) -> None:
        self.actions[name] = function

    def constant(self, name: str, value: Any) -> None:
        self.constants[name] = value

    # ---- loading -------------------------------------------------------------------------------------------------
    def load(self) -> None:
        self.initial = {name: p.get() for name, p in self.params.items()}
        self.audio_index = load_audio_index(self.file)
        self._stop_audio()
        try:
            text = _read_script(self.file, self.section)
            lines = text.splitlines()
            fm0, _ = _parse_front_matter(lines)
            self.voice = str(fm0.get("voice", DEFAULT_VOICE))
            self.script = Parser(self, text).parse()
            fm = self.script.front_matter
            defaults = fm.get("defaults", {}) if isinstance(fm.get("defaults"), dict) else {}
            self.default_over = float(defaults.get("over", 1.0))
            self.delay_after_interaction = float(defaults.get("delay_after_interaction", 8.0))
            self.error = ""
            self.started = True                    # the opening state applies at once, before the first play
        except LessonError as e:
            self.error = str(e)
        self._mtime = os.path.getmtime(self.file) if os.path.isfile(self.file) else 0.0
        self._loaded = True

    def _reload_if_changed(self) -> None:
        now = time.time()
        if now - self._last_check < 0.5:
            return
        self._last_check = now
        mtime = os.path.getmtime(self.file) if os.path.isfile(self.file) else 0.0
        if mtime != self._mtime:
            self.load()

    # ---- time ----------------------------------------------------------------------------------------------------
    def value_at(self, name: str, t: float) -> Any:
        """The value of a parameter at a lesson time: the keyframes of its cues, evaluated"""
        assert self.script is not None
        value = self.initial[name]
        for event in self.script.events:
            if event.param != name or event.kind not in ("set", "animate") or event.time > t:
                continue
            if event.kind == "animate" and event.over > 0 and t < event.time + event.over:
                k = (t - event.time) / event.over
                k = 0.5 - 0.5 * math.cos(math.pi * k)     # ease in and out
                value = value + (event.value - value) * k
            else:
                value = event.value
        return value

    def next_keyframe_time(self, name: str, t: float) -> float:
        assert self.script is not None
        return next((e.time for e in self.script.events if e.param == name and e.kind in ("set", "animate")
                     and e.time > t), float("inf"))

    def current_chapter(self) -> int:
        assert self.script is not None
        return max((i for i, c in enumerate(self.script.chapters) if c.start <= self.t + 1e-6), default=0)

    def current_paragraph(self) -> Optional[Paragraph]:
        assert self.script is not None
        chapter = self.script.chapters[self.current_chapter()]
        return next((p for p in reversed(chapter.paragraphs) if p.start <= self.t + 1e-6), None)

    def current_sentence(self) -> Optional[Sentence]:
        paragraph = self.current_paragraph()
        if paragraph is None:
            return None
        return next((s for s in reversed(paragraph.sentences) if s.start <= self.t + 1e-6), None)

    def seek(self, t: float) -> None:
        """Lands on a sentence start; the parameters are evaluated there, the chapter's actions replayed"""
        assert self.script is not None
        self.started = True
        t = max(0.0, min(t, self.script.duration))
        starts = [s.start for c in self.script.chapters for p in c.paragraphs for s in p.sentences]
        self.t = max((s for s in starts if s <= t + 1e-6), default=0.0)
        self._stop_audio()
        self.waiting = None
        self.passed = {id(e) for e in self.script.events if e.kind in ("pause", "challenge") and e.time < self.t}
        chapter_start = self.script.chapters[self.current_chapter()].start
        self.fired = {id(e) for e in self.script.events if e.kind == "call" and e.time < chapter_start}
        for p in self.params.values():
            p.hold_until = -1.0
        self._apply()

    def sentence_offset(self, delta: int) -> None:
        assert self.script is not None
        starts = [s.start for c in self.script.chapters for p in c.paragraphs for s in p.sentences]
        current = max((i for i, s in enumerate(starts) if s <= self.t + 1e-6), default=0)
        self.seek(starts[max(0, min(len(starts) - 1, current + delta))])

    def _apply(self) -> None:
        """Writes the parameters for the current time, fires what the clock passed"""
        assert self.script is not None
        if not self.started:
            return
        for name, p in self.params.items():
            if p.hold_until >= 0 and self.t >= p.hold_until:
                p.hold_until = -1.0
            if p.hold_until < 0:
                p.set(self.value_at(name, self.t))
        for event in self.script.events:
            if event.time > self.t + 1e-6:
                continue
            if event.kind == "call" and id(event) not in self.fired:
                self.fired.add(id(event))
                self.actions[event.action](*event.args)
            elif event.kind == "highlight" and self.t - event.time < HIGHLIGHT_DURATION:
                self.params[event.param].highlight_until = event.time + HIGHLIGHT_DURATION

    def update(self) -> None:
        """Advances the clock (call it every frame, or let gui() do it)"""
        if not self._loaded:
            self.load()
        self._reload_if_changed()
        if self.script is None or self.error:
            return
        if self.playing:
            self.started = True
        if self.playing and self.waiting is None:
            t_next = self._clock_next()
            stop = next((e for e in self.script.events if e.kind in ("pause", "challenge")
                         and id(e) not in self.passed and self.t - 1e-6 <= e.time <= t_next), None)
            if stop is not None:
                self.t, self.waiting, self.waiting_since = stop.time, stop, time.time()
                self._stop_audio()
            else:
                self.t = min(t_next, self.script.duration)
                if self.t >= self.script.duration:
                    self.playing = False
                    self._stop_audio()
        else:
            self._stop_audio()
        if self.waiting is not None and self.waiting.kind == "challenge" and self._condition(self.waiting.until):
            self._resume()
        self._apply()

    def _clock_next(self) -> float:
        """The lesson time after this frame: the clip's position while a sentence is spoken, else the frame's time"""
        delta = imgui.get_io().delta_time
        sentence = self.current_sentence()
        if self.audio is None or not self.voice_on or sentence is None or not sentence.clip \
                or self.t >= sentence.start + sentence.duration:
            self._stop_audio()
            return self.t + delta
        if self._speaking is not sentence:
            self.audio.play(sentence.clip, max(0.0, self.t - sentence.start))
            self._speaking = sentence
        if self.audio.done():
            return max(self.t, sentence.start + sentence.duration) + delta
        return float(sentence.start + self.audio.position())

    def _stop_audio(self) -> None:
        if self.audio is not None and self._speaking is not None:
            self.audio.stop()
        self._speaking = None

    def _condition(self, expression: str) -> bool:
        names: dict[str, Any] = {"abs": abs, "min": min, "max": max}
        names.update({n: p.get() for n, p in self.params.items()})
        names.update({n: g() for n, g in self.derived.items()})
        try:
            return bool(eval(expression, {"__builtins__": {}}, names))
        except Exception:
            return False

    def _resume(self) -> None:
        if self.waiting is not None:
            self.passed.add(id(self.waiting))
        self.waiting = None

    # ---- the widgets ---------------------------------------------------------------------------------------------
    def touched(self, name: str) -> None:
        """The learner changed a parameter by other means than its widget: its value holds, as after a drag"""
        p = self.params.get(name)
        if p is not None and self.script is not None:
            p.hold_until = max(self.next_keyframe_time(name, self.t), self.t + self.delay_after_interaction)

    def widget(self, name: str, changed: bool = False) -> None:
        """Call it right after the widget that shows a parameter: its rectangle, and the learner's edit"""
        p = self.params.get(name)
        if p is None:
            return
        p.rect = (imgui.get_item_rect_min(), imgui.get_item_rect_max())
        if changed and imgui.is_item_active():
            self.touched(name)
        if self.t < p.highlight_until:
            k = 0.5 + 0.5 * math.sin(time.time() * 12.0)
            color = imgui.get_color_u32(ImVec4(1.0, 0.6, 0.1, 0.35 + 0.6 * k))
            imgui.get_foreground_draw_list().add_rect(p.rect[0] - ImVec2(4, 4), p.rect[1] + ImVec2(4, 4), color,
                                                      rounding=4.0, thickness=3.0)

    # ---- the strip -----------------------------------------------------------------------------------------------
    def gui(self) -> None:
        """The strip: the chapters, the current paragraph, the controls"""
        self.update()
        if self.error:
            imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"Lesson error: {self.error}")
            return
        assert self.script is not None
        em = hello_imgui.em_size()
        imgui.separator()
        chapter_now = self.current_chapter()
        follow = chapter_now if chapter_now != self._last_chapter else None   # the tab follows the clock
        self._last_chapter = chapter_now
        if imgui.begin_tab_bar("##chapters"):
            for i, chapter in enumerate(self.script.chapters):
                flags = imgui.TabItemFlags_.set_selected if follow == i else 0
                if imgui.begin_tab_item_simple(chapter.title or f"Chapter {i + 1}", flags):
                    if i != chapter_now and follow is None:                   # the learner clicked another tab
                        self.seek(chapter.start)
                    imgui.end_tab_item()
            imgui.end_tab_bar()
        self._gui_paragraph()
        self._gui_controls(em)
        if self.open_section is not None:
            imgui.begin_child("##section", ImVec2(0, em * 10), imgui.ChildFlags_.borders)
            rich_md.render(self.open_section.markdown)
            imgui.end_child()
        if self.show_full_text:
            self._gui_full_text(em)
        if self.show_source:
            self._gui_source(em)

    _last_chapter = -1

    def _gui_paragraph(self) -> None:
        paragraph = self.current_paragraph()
        sentence = self.current_sentence()
        if paragraph is None or sentence is None:
            return
        parts = []
        for s in paragraph.sentences:
            if s is sentence:
                parts.append(f"**{s.text}**")
            else:
                parts.append(s.text)
        rich_md.render(" ".join(parts))

    def _gui_controls(self, em: float) -> None:
        """The strip's widgets carry their own IDs, so that the explorable's widgets may use the same labels"""
        assert self.script is not None
        imgui.push_id("narrator")
        if self.waiting is not None:
            imgui.text_colored(ImVec4(1.0, 0.75, 0.3, 1.0), self.waiting.prompt)
            if self.waiting.kind == "challenge" and self.waiting.hint and \
                    time.time() - self.waiting_since > self.waiting.hint_after:
                imgui.text_disabled(self.waiting.hint)
            if imgui.button("Continue" if self.waiting.kind == "pause" else "Skip"):
                self._resume()
            imgui.same_line()
        if imgui.button("Pause" if self.playing else "Play", ImVec2(em * 4, 0)):
            self.playing = not self.playing
            if self.playing and self.t >= self.script.duration:
                self.seek(0.0)
        imgui.same_line()
        if imgui.button("|<", ImVec2(em * 2, 0)):
            self.sentence_offset(0)
        imgui.same_line()
        if imgui.button("<", ImVec2(em * 2, 0)):
            self.sentence_offset(-1)
        imgui.same_line()
        if imgui.button(">", ImVec2(em * 2, 0)):
            self.sentence_offset(1)
        imgui.same_line()
        imgui.set_next_item_width(em * 14)
        imgui.progress_bar(self.t / max(1e-6, self.script.duration), ImVec2(0, 0),
                           f"{self.t:.0f} / {self.script.duration:.0f} s")
        for section in self.script.chapters[self.current_chapter()].sections:
            imgui.same_line()
            if imgui.button(section.title):
                self.open_section = None if self.open_section is section else section
        if self.audio is not None and self.audio_index:
            imgui.same_line()
            if imgui.button("Voice: on" if self.voice_on else "Voice: off"):
                self.voice_on = not self.voice_on
                self._stop_audio()
        imgui.same_line()
        if imgui.button("Full text"):
            self.show_full_text = not self.show_full_text
        for label, which in (("Scenario", "scenario"), ("Program", "program")):
            imgui.same_line()
            if imgui.button(label):
                self.show_source = "" if self.show_source == which else which
        imgui.pop_id()

    def _gui_source(self, em: float) -> None:
        """The scenario as written, or the program, as code"""
        imgui.begin_child("##source", ImVec2(0, em * 24), imgui.ChildFlags_.borders)
        if self.show_source == "scenario":
            text = Path(self.file).read_text(encoding="utf-8") if os.path.isfile(self.file) else ""
            rich_md.render_raw("````markdown\n" + text + "\n````")
        else:
            rich_md.render_file(self.program or self.file, "")
        imgui.end_child()

    def _gui_full_text(self, em: float) -> None:
        assert self.script is not None
        rich_md.register_fenced_block_renderer("cues", lambda _code: None)
        imgui.begin_child("##full_text", ImVec2(0, em * 20), imgui.ChildFlags_.borders)
        rich_md.render(self.script.markdown)
        imgui.end_child()


# =============================================================================
# The build step: the clips
# =============================================================================

def build_audio(script_file: str) -> None:
    """Synthesizes the clips of the sentences that have none yet (edge-tts), and writes the index"""
    import asyncio
    import edge_tts

    lesson = Lesson(script_file)
    lesson.strict = False
    text = _read_script(script_file, lesson.section, resolve=False)   # transclusions are not spoken
    lesson.voice = str(_parse_front_matter(text.splitlines())[0].get("voice", DEFAULT_VOICE))
    script = Parser(lesson, text).parse()
    folder = audio_folder(script_file)
    folder.mkdir(exist_ok=True)
    index = load_audio_index(script_file)
    sentences = [s for c in script.chapters for p in c.paragraphs for s in p.sentences]
    todo = {clip_key(lesson.voice, s.text): s.text for s in sentences if clip_key(lesson.voice, s.text) not in index}
    print(f"{len(sentences)} sentences, {len(todo)} to synthesize with {lesson.voice}")

    async def synthesize(key: str, sentence: str) -> None:
        communicate = edge_tts.Communicate(sentence, lesson.voice, boundary="WordBoundary")
        data: bytearray = bytearray()
        words: list[list[Any]] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                data.extend(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append([round(chunk["offset"] / 1e7, 3), chunk["text"]])
        (folder / f"{key}.mp3").write_bytes(bytes(data))
        last_offset = float(words[-1][0]) if words else 0.0
        duration = round(last_offset + 0.5, 3)      # the last word plus a breath; a decoder gives the exact length
        try:
            import miniaudio  # type: ignore[import-untyped]
            info = miniaudio.get_file_info(str(folder / f"{key}.mp3"))
            duration = round(info.duration, 3)
        except Exception:
            pass
        index[key] = {"file": f"{key}.mp3", "duration": duration, "words": words, "text": sentence}
        print(f"  {duration:5.1f} s  {sentence[:70]}")

    async def run() -> None:
        for key, sentence in todo.items():
            await synthesize(key, sentence)

    asyncio.run(run())
    keys = {clip_key(lesson.voice, s.text) for s in sentences}
    stale = [k for k in index if k not in keys]
    for k in stale:                                 # the clips of sentences that no longer exist
        (folder / index[k]["file"]).unlink(missing_ok=True)
        del index[k]
    (folder / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"index: {len(index)} clips, {len(stale)} removed")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "build":
        build_audio(sys.argv[2])
    else:
        print("usage: python narrator.py build <scenario.md>")
