"""narrator: the player of narrated explorables.

A lesson is the `::md Lesson` section of a program (see the format in _plans/narrated_explorables/nex_dsl__format.md):
chapters are `##` headings, the narration is its paragraphs, and `cues` fenced blocks before a paragraph say what
happens on the stage while it is read. The program declares what the cues may touch (parameters, actions), tags the
widgets that show the parameters, and calls `lesson.gui(stage)`: the player lays out the window (the stage, the strip
with the narration and the controls), and `stage` draws the program's figures in the region it gets.

The voice: `python narrator.py build scenario.md` synthesizes one clip per sentence (edge-tts, the voice of the front
matter) into `scenario_audio/` beside the script, with the words' timings (`index.json`); only new sentences are
synthesized. The clips are not in the bundle's repository: `just narrator_audio <lesson>` builds them and copies them
into the website resources, and the browser plays them from the site. With the clips, the audio is the clock: a
sentence lasts what its clip lasts, and a cue anchored to words fires on them. Without them (or with the voice off), the
clock is estimated from the text, or taken from the timings.

The gestures (`click`, `drag`, `press`, `type_keys`, `paste`...): the test engine moves a visible cursor and types, for the
moments where the gesture is the lesson. The program runs with `use_imgui_test_engine`, and names its targets with
`lesson.target(name, resolver)`, or reaches any widget through the built-in target `item` (a test engine reference). The
engine owns the inputs while a gesture plays (Esc aborts it). Without the engine (a browser without JSPI), the gestures
are skipped.

The video (`lesson.video(runner_params, output)`, desktop): the stage fills the window, the sentences show as subtitles,
a click leaves a ripple, and a subtitle stays until its gestures end. With an output file, the frames go to ffmpeg at a
fixed clock (whatever a frame takes to capture), the subtitles to an .srt beside it, and the app quits at the end.
"""
import hashlib
import inspect
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Union

from imgui_bundle import hello_imgui, imgui, rich_md, icons_fontawesome_4 as fa
from imgui_bundle import ImVec2, ImVec4

SECONDS_PER_CHAR = 0.06          # the silent clock: Tangible's estimate of a voice's pace
SENTENCE_GAP = 0.4               # the silence after a sentence
CHAPTER_GAP = 0.8                # the silence before a chapter
HIGHLIGHT_DURATION = 3.0
COMPACT_WIDTH_EM = 40.0          # a window narrower than this (or a landscape one) gets the phone's layout
LANDSCAPE_MAX_HEIGHT_EM = 30.0   # a window shorter than this, and wider than tall: the strip becomes a column
STRIP_MIN_WIDTH_EM = 18.0        # the strip's column, in landscape
SIDE_PANEL_MIN_WIDTH_EM = 60.0   # a stage wider than this shows an open panel beside it; a narrower one, over it
TOUCH_BUTTON_EM = 2.4            # the buttons' height in the phone's layout
PARAGRAPH_ESTIMATE_SCALE = 1.3   # rich_md's paragraphs are taller than imgui's text of the same width
PROMPT_COLOR = ImVec4(1.0, 0.75, 0.3, 1.0)
RESERVED_SECTIONS = ("More", "Code", "References")
IN_BROWSER = sys.platform == "emscripten"
CLIPS_URL = "/resources/explorables"  # the clips on the site (the website resources), by lesson folder
DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
# The video
VIDEO_WIDTH = 1920               # the recorded video's width; its height keeps the window's aspect
VIDEO_WARMUP_FRAMES = 20         # frames before the play: the program lays itself out, its files load
VIDEO_TAIL = 1.5                 # seconds recorded after the lesson's end
VIDEO_MOUSE_SPEED = 1100.0       # the engine's cursor, in points per second (its default, 600, is slow in a video)
VIDEO_ACTION_DELAYS = (0.08, 0.2)  # the engine's pauses between actions, short and standard (default: 0.15, 0.4)
VIDEO_CURSOR_SCALE = 1.6         # the drawn cursor's size
SUBTITLE_EM = 1.6                # the subtitles' size
SUBTITLE_BOTTOM_EM = 1.2         # their distance to the window's bottom
SUBTITLE_MAX_WIDTH = 0.8         # their lines' width, at most, in the window's width
SUBTITLE_FADE = 0.15             # seconds: a subtitle fades in
RIPPLE_DURATION = 0.5            # seconds: the ring a click leaves
RIPPLE_COLOR = ImVec4(1.0, 0.75, 0.3, 1.0)


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


Point = tuple[float, float]     # a point in a target's rectangle, in fractions of its size
At = Optional[Union[str, float]]   # when a cue fires: words of its paragraph, or seconds after its start


@dataclass
class Gesture:
    kind: str                    # click, double_click, right_click, hover, drag, wheel, press, type, paste, menu, wait
    target: str = ""             # a target of the program (click, hover, drag...)
    arg: str = ""                # passed to the target's resolver (a heading, an entry...)
    point: Point = (0.5, 0.5)    # where in the target's rectangle; a drag's start
    end: Point = (0.5, 0.5)      # a drag's end
    text: str = ""               # press: the keys ("ctrl+f"); type, paste: the text; menu: the item's label;
                                 # wait: the seconds
    delta: Point = (0.0, 0.0)    # wheel: the columns and the lines (negative: right, down)
    fast: bool = False           # played at the engine's fast speed: a setup the viewer does not see (under a card)


@dataclass
class Event:
    time: float
    kind: str                    # set, animate, highlight, pause, challenge, call, gesture
    param: str = ""
    value: Any = None
    over: float = 0.0
    prompt: str = ""
    until: str = ""
    hint: str = ""
    hint_after: float = 30.0
    action: str = ""
    args: tuple[Any, ...] = ()
    gesture: Optional[Gesture] = None
    chapter: int = 0
    line: int = 0
    anchor: tuple[Optional["Paragraph"], At] = (None, None)   # the paragraph, and the words or seconds it waits


@dataclass
class Script:
    front_matter: dict[str, Any]
    chapters: list[Chapter]
    events: list[Event]
    markdown: str                # the whole lesson without its front matter, for the full text view
    duration: float


class _CuesBlock:
    def __init__(self, source: str, line: int) -> None:
        self.source, self.line = source, line


def audio_folder(script_file: str) -> Path:
    return Path(script_file).with_name(Path(script_file).stem + "_audio")


def clip_source(folder: Path, file: str) -> str:
    """The clip's file; in the browser, its URL on the site when the lesson's files do not carry it; else "" (silent)"""
    if (folder / file).is_file():
        return str(folder / file)
    if IN_BROWSER:
        return f"{CLIPS_URL}/{folder.parent.name}/{folder.name}/{file}"
    return ""


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
        duration = max([duration] + [e.time + e.over for e in self.events if e.kind == "animate"])  # the last ones end
        return Script(front_matter, self.chapters, sorted(self.events, key=lambda e: e.time),
                      "\n".join(self.lines[start:]), duration)

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

        def set_value(name: str, value: Any, at: At = None) -> None:
            check_param(name)
            check_value(name, value)
            record("set", param=name, value=value, at=at)

        def animate(name: str, value: Any, over: Optional[float] = None, at: At = None) -> None:
            check_param(name)
            check_value(name, value)
            record("animate", param=name, value=value, over=lesson.default_over if over is None else over, at=at)

        def highlight(name: str, at: At = None) -> None:
            check_param(name)
            record("highlight", param=name, at=at)

        def pause(prompt: str, at: At = None) -> None:
            record("pause", prompt=prompt, at=at)

        def challenge(prompt: str, until: str, hint: str = "", hint_after: float = 30.0,
                      at: At = None) -> None:
            record("challenge", prompt=prompt, until=until, hint=hint, hint_after=hint_after, at=at)

        # The gestures: a target and its argument (a heading, an entry...), a point in its rectangle. The mouse's ones
        # may be `fast`: a setup the viewer does not see (under a card)
        def gesture(kind: str, target: str = "", arg: Any = "", point: Point = (0.5, 0.5), end: Point = (0.5, 0.5),
                    text: str = "", at: At = None, fast: bool = False, delta: Point = (0.0, 0.0)) -> None:
            if target and lesson.strict and target not in lesson.targets:
                raise LessonError(f"line {block.line}: unknown target {target!r} (declared: {list(lesson.targets)})")
            record("gesture", gesture=Gesture(kind, target, str(arg), (float(point[0]), float(point[1])),
                                              (float(end[0]), float(end[1])), text=text, fast=fast,
                                              delta=(float(delta[0]), float(delta[1]))), at=at)

        def click(target: str, arg: Any = "", point: Point = (0.5, 0.5), at: At = None, fast: bool = False) -> None:
            gesture("click", target, arg, point, at=at, fast=fast)

        def double_click(target: str, arg: Any = "", point: Point = (0.5, 0.5), at: At = None,
                         fast: bool = False) -> None:
            gesture("double_click", target, arg, point, at=at, fast=fast)

        def right_click(target: str, arg: Any = "", point: Point = (0.5, 0.5), at: At = None,
                        fast: bool = False) -> None:
            gesture("right_click", target, arg, point, at=at, fast=fast)

        def hover(target: str, arg: Any = "", point: Point = (0.5, 0.5), at: At = None, fast: bool = False) -> None:
            gesture("hover", target, arg, point, at=at, fast=fast)

        def drag(target: str, arg: Any = "", start: Point = (0.0, 0.5), end: Point = (1.0, 0.5),
                 at: At = None, fast: bool = False) -> None:
            gesture("drag", target, arg, start, end, at=at, fast=fast)

        def wheel(target: str, arg: Any = "", lines: float = -5.0, columns: float = 0.0, point: Point = (0.5, 0.5),
                  at: At = None, fast: bool = False) -> None:
            gesture("wheel", target, arg, point, at=at, fast=fast, delta=(columns, lines))

        def wait(seconds: float, at: At = None) -> None:
            gesture("wait", text=str(float(seconds)), at=at)

        def press(keys: str, at: At = None) -> None:
            try:
                key_chord(keys)
            except KeyError as e:
                raise LessonError(f"line {block.line}: unknown key {e} in {keys!r}") from e
            gesture("press", text=keys, at=at)

        def type_keys(text: str, at: At = None) -> None:
            gesture("type", text=text, at=at)

        def paste(text: str, at: At = None) -> None:
            gesture("paste", text=text, at=at)

        def menu(label: str, at: At = None) -> None:
            gesture("menu", text=label, at=at)

        class Lenient(dict[str, Any]):           # the build step knows no actions: an unknown name records nothing
            def __missing__(self, key: str) -> Callable[..., None]:
                return lambda *args, **kw: None

        namespace: dict[str, Any] = (dict if lesson.strict else Lenient)(
            {"set_value": set_value, "animate": animate, "highlight": highlight,
             "pause": pause, "challenge": challenge, "click": click, "double_click": double_click,
             "right_click": right_click, "hover": hover, "drag": drag, "wheel": wheel, "wait": wait, "press": press,
             "type_keys": type_keys, "paste": paste, "menu": menu, **lesson.constants})
        for action_name in lesson.actions:
            def make_call(name: str) -> Callable[..., None]:
                def call(*args: Any, at: At = None) -> None:
                    record("call", action=name, args=args, at=at)
                return call
            namespace[action_name] = make_call(action_name)
        try:
            exec(compile(block.source, f"{lesson.file}:cues at line {block.line}", "exec"), namespace)
        except LessonError:
            raise
        except Exception as e:
            if not lesson.strict:                # the build step needs only the sentences, and knows no constants
                return
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
                        sentence.clip = clip_source(folder, entry["file"])
                        sentence.duration = float(entry["duration"])
                        sentence.words = [(float(o), str(w)) for o, w in entry.get("words", [])]
                    else:
                        sentence.duration = max(0.8, len(sentence.text) * SECONDS_PER_CHAR)
                    t += sentence.duration + SENTENCE_GAP
                paragraph.end = t
            # It lasts until its own animations end, those anchored to its start (a chapter with no paragraph)
            ends = [(float(e.anchor[1]) if isinstance(e.anchor[1], (int, float)) else 0.0) + e.over
                    for e in self.events if e.chapter == i and e.anchor[0] is None and e.kind == "animate"]
            t = max([t] + [chapter.start + end for end in ends])
            chapter.end = t
        for event in self.events:
            target, at = event.anchor
            start = target.start if target is not None else self.chapters[event.chapter].start
            if isinstance(at, (int, float)):           # seconds after the paragraph's start (or the chapter's)
                event.time = start + float(at)
            elif target is None or at is None:
                event.time = start
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


def typed(before: str, after: str, k: float) -> str:
    """The text at k (0 to 1) of a typing from `before` to `after`: their common start and end are kept, the middle is
    erased (from its end, as Backspace does), then typed, at a constant pace"""
    n = min(len(before), len(after))
    start = 0
    while start < n and before[start] == after[start]:
        start += 1
    end = 0
    while end < n - start and before[-1 - end] == after[-1 - end]:
        end += 1
    if start == len(before) - end and start > 0 and after[start - 1] == "\n" == after[len(after) - end - 1]:
        start, end = start - 1, end + 1          # a line inserted: its newline first, the text after it keeps its line
    erased, written = before[start:len(before) - end], after[start:len(after) - end]
    keys = int(k * (len(erased) + len(written)))
    tail = after[len(after) - end:]
    if keys <= len(erased):
        return before[:start + len(erased) - keys] + tail
    return after[:start + keys - len(erased)] + tail


# =============================================================================
# The gestures: the test engine's cursor clicks and types
# =============================================================================

_NAMED_KEYS = {"enter": "enter", "escape": "escape", "esc": "escape", "tab": "tab", "space": "space",
               "backspace": "backspace", "delete": "delete", "up": "up_arrow", "down": "down_arrow",
               "left": "left_arrow", "right": "right_arrow", "home": "home", "end": "end",
               "pageup": "page_up", "pagedown": "page_down", "/": "slash"}
_MODIFIERS = {"ctrl": "mod_ctrl", "shift": "mod_shift", "alt": "mod_alt"}


def key_chord(keys: str) -> int:
    """"ctrl+f", "shift+enter", "escape": an ImGui key chord (Ctrl is Cmd on macOS, as ImGui's shortcuts)"""
    chord = 0
    for part in keys.lower().replace(" ", "").split("+"):
        if part in _MODIFIERS:
            chord |= int(getattr(imgui.Key, _MODIFIERS[part]))
        elif part in _NAMED_KEYS:
            chord |= int(getattr(imgui.Key, _NAMED_KEYS[part]))
        elif len(part) == 1 and (part.isalpha() or part.isdigit()):
            chord |= int(getattr(imgui.Key, part if part.isalpha() else f"_{part}"))
        else:
            raise KeyError(part)
    return chord


Rect = tuple[ImVec2, ImVec2]
TargetResolver = Callable[[str, Any], Optional[Rect]]   # (argument, the test context) -> the target's rectangle


def item_target(ref: str, ctx: Any) -> Optional[Rect]:
    """The built-in target `item`: a widget by its test engine reference ("//Dear ImGui Demo/**/Button"), scrolled
    into view first if it is clipped (a scroll moves the engine's cursor to the window)"""
    no_error = imgui.test_engine.TestOpFlags_.no_error
    info = ctx.item_info(ref, no_error)
    if info.id_ == 0:
        return None
    full, clipped = info.rect_full, info.rect_clipped
    if clipped.max.y - clipped.min.y < full.max.y - full.min.y - 1.0:
        ctx.scroll_to_item(ref, imgui.internal.Axis.y, no_error)
        info = ctx.item_info(ref, no_error)
    return (info.rect_full.min, info.rect_full.max) if info.id_ != 0 else None


class _GestureRunner:
    """Plays the gestures with the test engine, one after the other, in a test that ends when none is left (the engine
    owns the inputs while a test runs). A seek replays the chapter's gestures at the engine's fast speed. In a video,
    the test lasts the whole video: the cursor stays drawn, and the real mouse stays out."""

    def __init__(self, lesson: "Lesson") -> None:
        self.lesson = lesson
        self.queue: list[tuple[Gesture, bool]] = []   # (gesture, fast)
        self.playing: Optional[Gesture] = None
        self.test: Any = None
        self.unavailable = False                         # no test engine: the gestures are skipped
        self._aborting = False
        self._clipboard = ""                             # the gestures' clipboard, from a test to the next

    @staticmethod
    def _engine() -> Any:
        try:
            return hello_imgui.get_imgui_test_engine()
        except Exception:
            return None

    def push(self, gesture: Gesture, fast: bool) -> None:
        if self._engine() is None:
            self.unavailable = True
            return
        self.queue.append((gesture, fast))

    def restart(self) -> None:
        """A seek: the gestures waiting are dropped, the one playing is aborted"""
        self.queue.clear()
        engine = self._engine()
        if engine is not None and not imgui.test_engine.is_test_queue_empty(engine):
            self._aborting = True
            imgui.test_engine.abort_current_test(engine)

    def busy(self) -> bool:
        if self.lesson.video_look:                       # its test runs all along: only the gestures count
            return bool(self.queue) or self.playing is not None
        engine = self._engine()
        return bool(self.queue) or (engine is not None and not imgui.test_engine.is_test_queue_empty(engine))

    def _video_running(self) -> bool:
        return self.lesson.video_look and self.lesson.playing_video()

    def tick(self) -> None:
        """Every frame: starts the test when gestures wait and none plays (in a video, when the video starts)"""
        engine = self._engine()
        if self.lesson.video_look and not self.lesson.playing_video():   # the warm-up: the first gestures wait
            return
        if not (self.queue or self._video_running()) or engine is None \
                or not imgui.test_engine.is_test_queue_empty(engine):
            return
        if self.test is None:
            self.test = imgui.test_engine.register_test(engine, "narrator", "gestures")
            self.test.test_func = self._run
            # A gesture leaves the focus where it put it: a menu it opened stays open for the next one
            imgui.test_engine.get_io(engine).config_restore_focus_after_tests = False
        imgui.test_engine.queue_test(engine, self.test)

    def _run(self, ctx: Any) -> None:
        self._aborting = False
        # Each test has a private clipboard, empty at its start: a copy made by a gesture is carried to the next ones
        # (and the learner's own clipboard is left alone)
        if self._clipboard:
            imgui.set_clipboard_text(self._clipboard)
        io = imgui.get_io()
        start = io.mouse_pos                             # the cursor leaves from the learner's mouse, if it is in
        if not imgui.is_mouse_pos_valid(start) or self.lesson.video_look:
            start = imgui.get_main_viewport().get_center()
        ctx.mouse_teleport_to_pos(start)
        engine_io = ctx.engine_io
        while (self.queue or self._video_running()) and not self._aborting and not ctx.is_error():
            if not self.queue:                           # a video: the test waits for the next gestures
                ctx.yield_()
                continue
            gesture, fast = self.queue.pop(0)
            self.playing = gesture
            engine_io.config_run_speed = (imgui.test_engine.TestRunSpeed.fast if fast
                                          else imgui.test_engine.TestRunSpeed.normal)
            self._play(ctx, gesture)
            self.playing = None
            self._clipboard = imgui.get_clipboard_text() or ""
        self.playing = None
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.normal
        if ctx.is_error():
            self.queue.clear()                           # the engine ignores every operation after an error

    def _play(self, ctx: Any, g: Gesture) -> None:
        if g.kind == "wait":
            ctx.sleep(float(g.text))
            return
        if g.kind == "press":
            ctx.key_press(key_chord(g.text))
            return
        if g.kind == "type":
            ctx.key_chars(g.text)
            return
        if g.kind == "paste":
            imgui.set_clipboard_text(g.text)
            ctx.key_press(key_chord("ctrl+v"))
            return
        if g.kind == "menu":
            ctx.item_click("//$FOCUSED/" + g.text)
            self.lesson.ripple()
            return
        resolver = self.lesson.targets.get(g.target)
        rect = resolver(g.arg, ctx) if resolver is not None else None
        if resolver is None or rect is None:
            print(f"narrator: the target {g.target}({g.arg!r}) is not on screen: {g.kind} skipped", file=sys.stderr)
            return

        def point(f: tuple[float, float]) -> ImVec2:
            assert rect is not None
            return ImVec2(rect[0].x + (rect[1].x - rect[0].x) * f[0], rect[0].y + (rect[1].y - rect[0].y) * f[1])

        for _ in range(3):                               # the target may move meanwhile (a scroll still animated)
            goal = point(g.point)
            ctx.mouse_move_to_pos(goal)
            rect = resolver(g.arg, ctx) or rect
            moved = point(g.point) - goal
            if abs(moved.x) + abs(moved.y) < 2:
                break
        if g.kind == "click":
            ctx.mouse_click(0)
        elif g.kind == "double_click":
            ctx.mouse_double_click(0)
        elif g.kind == "right_click":
            ctx.mouse_click(1)
        elif g.kind == "drag":
            ctx.mouse_down(0)
            ctx.mouse_move_to_pos(point(g.end))
            ctx.mouse_up(0)
        elif g.kind == "wheel":
            ctx.mouse_wheel(ImVec2(g.delta[0], g.delta[1]))
        if g.kind in ("click", "double_click", "right_click"):
            self.lesson.ripple()


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

    def failed(self) -> bool:
        return False


class _WebBackend:
    """The browser: an <audio> element plays the clip from the site (CLIPS_URL), or from a blob URL when the clip came
    with the lesson's files"""

    def __init__(self) -> None:
        import js  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]
        self.js, self.to_js = js, to_js
        self.audio = js.Audio.new()
        self.urls: dict[str, str] = {}
        self.active = False

    def play(self, path: str, offset: float) -> None:
        if path not in self.urls:
            if path.startswith(CLIPS_URL):
                self.urls[path] = path
            else:
                data = Path(path).read_bytes()
                blob = self.js.Blob.new(self.to_js([self.js.Uint8Array.new(data)]), self.to_js({"type": "audio/mpeg"}))
                self.urls[path] = self.js.URL.createObjectURL(blob)
        self.audio.src = self.urls[path]
        self.audio.currentTime = offset
        self._start()
        self.active = True

    def _start(self) -> None:
        # play() returns a future; a clip that cannot play rejects it. Its outcome is read here, so that the
        # playground does not report it as an error: failed() tells the player
        self.audio.play().add_done_callback(lambda future: future.exception())

    def pause(self) -> None:
        self.audio.pause()

    def resume(self) -> None:
        if self.active and not self.audio.ended:
            self._start()

    def stop(self) -> None:
        self.audio.pause()
        self.active = False

    def position(self) -> float:
        return float(self.audio.currentTime)

    def done(self) -> bool:
        return not self.active or bool(self.audio.ended)

    def failed(self) -> bool:
        """The clip could not load (offline, or not deployed): its position would never move"""
        return self.active and bool(getattr(self.audio.error, "code", 0))  # null arrives as jsnull, not None


def make_audio_backend() -> Any:
    """The backend of this platform, or None when no audio can be played"""
    try:
        return _WebBackend() if IN_BROWSER else _MiniaudioBackend()
    except Exception:
        return None


# =============================================================================
# The video: the frames piped to ffmpeg, the subtitles written beside
# =============================================================================

class _VideoRecorder:
    """Reads each frame before the swap (OpenGL) and pipes it to ffmpeg; notes the subtitle of each frame"""

    def __init__(self, output: str, fps: int) -> None:
        self.output, self.fps = output, fps
        self.recording = False
        self.frames = 0
        self.size = (0, 0)
        self.process: Optional[subprocess.Popen[bytes]] = None
        self.subtitles: list[list[Any]] = []     # [first frame, last frame, text]

    def note_subtitle(self, text: str) -> None:
        """The subtitle shown in the frame being drawn"""
        if not self.recording or not text:
            return
        if self.subtitles and self.subtitles[-1][2] == text and self.subtitles[-1][1] == self.frames - 1:
            self.subtitles[-1][1] = self.frames
        else:
            self.subtitles.append([self.frames, self.frames, text])

    def capture(self) -> None:
        if not self.recording:
            return
        from OpenGL import GL  # type: ignore[import-untyped]
        io = imgui.get_io()
        w = int(io.display_size.x * io.display_framebuffer_scale.x)
        h = int(io.display_size.y * io.display_framebuffer_scale.y)
        if self.process is None:
            self.size = (w, h)
            self.process = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                 "-r", str(self.fps), "-i", "-", "-vf", f"vflip,scale={VIDEO_WIDTH}:-2:flags=lanczos",
                 "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                 self.output], stdin=subprocess.PIPE)
        if (w, h) != self.size:                  # the window changed its size: the frame would not fit the video
            return
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        data = GL.glReadPixels(0, 0, w, h, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)
        assert self.process.stdin is not None
        self.process.stdin.write(bytes(data))          # bytes, or a numpy array: its buffer
        self.frames += 1

    def finish(self) -> None:
        self.recording = False
        if self.process is not None and self.process.stdin is not None:
            self.process.stdin.close()
            self.process.wait()

        def stamp(frame: int) -> str:
            ms = round(frame * 1000 / self.fps)
            return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

        srt = [f"{i + 1}\n{stamp(first)} --> {stamp(last + 1)}\n{text}\n"
               for i, (first, last, text) in enumerate(self.subtitles)]
        Path(self.output).with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
        print(f"narrator: {self.output}, {self.frames / self.fps:.1f} s, {len(self.subtitles)} subtitles")


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
        self.targets: dict[str, TargetResolver] = {"item": item_target}
        self.gestures = _GestureRunner(self)
        self._replaying = False                    # during a seek: the gestures replayed play fast
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
        self.panel = ""                            # "", "section", "full_text", "scenario" or "program"
        self.open_section: Optional[Section] = None
        self.compact = False                       # the phone's layout (set by gui): large buttons, one figure
        self._measured_width = 0.0                 # the paragraphs' width when _tallest_drawn was measured
        self._tallest_drawn = 0.0                  # the tallest paragraph drawn at that width
        self.strict = True                         # False for the build step: the parameters are not declared there
        self.voice = DEFAULT_VOICE
        self.voice_on = True
        self.audio_index: dict[str, Any] = {}
        self.audio = make_audio_backend()
        self._speaking: Optional[Sentence] = None  # the sentence whose clip plays
        self._mtime = 0.0
        self._last_check = 0.0
        self._loaded = False
        self.video_look = False                    # video(): the stage alone, subtitles, ripples
        self._recorder: Optional[_VideoRecorder] = None
        self._video_frames = 0                     # the frames drawn as a video: the warm-up, then the play
        self._video_end = -1.0                     # imgui's time at the lesson's end (the tail follows)
        self._video_finished = False
        self._ripples: list[tuple[ImVec2, float]] = []   # (where, imgui's time)

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

    def target(self, name: str, resolver: TargetResolver) -> None:
        """A target of the gestures: `resolver(arg, ctx)` gives its rectangle on screen (or None) when a gesture plays;
        ctx is the test engine's context (e.g. to gather the items of a window)"""
        self.targets[name] = resolver

    def video(self, runner_params: Any, output: str = "", fps: int = 30) -> None:
        """Plays the lesson as a video (call it before running the app, which needs the test engine): the stage fills
        the window, the sentences show as subtitles. With `output` (an .mp4, ffmpeg in the PATH), records it at a fixed
        clock, writes the subtitles beside it (.srt), and quits at the end"""
        self.video_look = True
        self.voice_on = False
        if not output:
            return
        recorder = self._recorder = _VideoRecorder(output, fps)
        runner_params.fps_idling.enable_idling = False
        previous = runner_params.callbacks.before_swap

        def before_swap() -> None:
            if previous is not None:              # None when the program set none
                previous()
            recorder.capture()
        runner_params.callbacks.before_swap = before_swap

    def playing_video(self) -> bool:
        """A video plays: its warm-up is over, its tail not"""
        return self.video_look and self._video_frames >= VIDEO_WARMUP_FRAMES and not self._video_finished

    def ripple(self) -> None:
        """A gesture clicked: a ring grows where the mouse is (in a video)"""
        if self.video_look:
            mouse = imgui.get_io().mouse_pos
            self._ripples.append((ImVec2(mouse.x, mouse.y), imgui.get_time()))

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
                if isinstance(value, str):                # a text is typed
                    value = typed(value, str(event.value), k)
                    continue
                k = 0.5 - 0.5 * math.cos(math.pi * k)     # ease in and out
                value = value + (event.value - value) * k
            else:
                value = event.value
        return value

    def _has_keyframe(self, name: str, t: float) -> bool:
        assert self.script is not None
        return any(e.param == name and e.kind in ("set", "animate") and e.time <= t + 1e-6 for e in self.script.events)

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
        self.fired = {id(e) for e in self.script.events if e.kind in ("call", "gesture") and e.time < chapter_start}
        for p in self.params.values():
            p.hold_until = -1.0
        self.gestures.restart()
        self._replaying = True                     # the chapter's actions and gestures before t: replayed, fast
        self._apply()
        self._replaying = False

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
            if p.hold_until < 0 and self._has_keyframe(name, self.t):   # a parameter no cue has set yet is the learner's
                p.set(self.value_at(name, self.t))
        for event in self.script.events:
            if event.time > self.t + 1e-6:
                continue
            if event.kind == "call" and id(event) not in self.fired:
                self.fired.add(id(event))
                self.actions[event.action](*event.args)
            elif event.kind == "gesture" and id(event) not in self.fired and event.gesture is not None:
                self.fired.add(id(event))
                self.gestures.push(event.gesture, fast=self._replaying or event.gesture.fast)
            elif event.kind == "highlight" and self.t - event.time < HIGHLIGHT_DURATION:
                self.params[event.param].highlight_until = event.time + HIGHLIGHT_DURATION

    def update(self) -> None:
        """Advances the clock (call it every frame, or let gui() do it)"""
        if not self._loaded:
            self.load()
        self._reload_if_changed()
        if self.script is None or self.error:
            return
        if self.video_look:
            self._video_course()
        if self.playing:
            self.started = True
        if self.playing and self.waiting is None:
            t_next = self._clock_next()
            if self.video_look and self.gestures.busy():   # a subtitle stays until its gestures end
                t_next = min(t_next, max(self.t, self._next_start() - 1e-4))
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
        self.gestures.tick()
        if (self.playing and self.waiting is None) or self.gestures.busy():
            hello_imgui.request_refresh()  # the lesson's clock runs, or a gesture plays: the frames go on

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
        if self.audio.failed():  # silent: the clock runs on the frames' time
            return self.t + delta
        if self.audio.done():
            return max(self.t, sentence.start + sentence.duration) + delta
        return float(sentence.start + self.audio.position())

    def _stop_audio(self) -> None:
        if self.audio is not None and self._speaking is not None:
            self.audio.stop()
        self._speaking = None

    def _next_start(self) -> float:
        """The start of the next sentence or chapter, or the lesson's end"""
        assert self.script is not None
        chapters = self.script.chapters
        starts = [c.start for c in chapters] + [s.start for c in chapters for p in c.paragraphs for s in p.sentences]
        return min((s for s in starts if s > self.t + 1e-6), default=self.script.duration)

    def _video_course(self) -> None:
        """A video: a warm-up (the program lays itself out), the play, a tail after the end, then the end"""
        self._video_frames += 1
        if self._video_frames == 1:
            engine_io = imgui.test_engine.get_io(hello_imgui.get_imgui_test_engine())
            engine_io.config_watchdog_warning = engine_io.config_watchdog_kill_test = 3600.0   # one test, all along
            engine_io.mouse_speed = VIDEO_MOUSE_SPEED
            engine_io.action_delay_short, engine_io.action_delay_standard = VIDEO_ACTION_DELAYS
            imgui.get_style().mouse_cursor_scale = VIDEO_CURSOR_SCALE
            if self._recorder is not None:                 # the video's clock: a frame lasts 1/fps, however long
                engine_io.config_fixed_delta_time = 1.0 / self._recorder.fps
        if self._video_frames == VIDEO_WARMUP_FRAMES:
            self.playing = True
            if self._recorder is not None:
                self._recorder.recording = True
        ended = self._video_frames > VIDEO_WARMUP_FRAMES and not self.playing and not self.gestures.busy()
        if ended and self._video_end < 0:
            self._video_end = imgui.get_time()
        if self._video_end >= 0 and imgui.get_time() - self._video_end > VIDEO_TAIL and not self._video_finished:
            self._video_finished = True
            if self._recorder is not None:
                self._recorder.finish()
                hello_imgui.get_runner_params().app_shall_exit = True

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
            hello_imgui.request_refresh()  # the highlight pulses on its own

    # ---- the frame -----------------------------------------------------------------------------------------------
    def gui(self, stage: Callable[[], None]) -> None:
        """The whole window: the stage, drawn by `stage` (it sizes its figures from imgui.get_content_region_avail()),
        and the strip below it, or on its right when the window is short and wide (a phone in landscape)"""
        self.update()
        em = hello_imgui.em_size()
        spacing = imgui.get_style().item_spacing
        avail = imgui.get_content_region_avail()
        landscape = avail.y < LANDSCAPE_MAX_HEIGHT_EM * em and avail.x > 1.4 * avail.y
        self.compact = landscape or avail.x < COMPACT_WIDTH_EM * em
        if self.error or self.script is None:
            imgui.push_text_wrap_pos(0.0)
            imgui.text_colored(ImVec4(1.0, 0.4, 0.4, 1.0), f"Lesson error: {self.error}")
            imgui.pop_text_wrap_pos()
            self._gui_stage_child(stage, imgui.get_content_region_avail())
            return
        imgui.push_id("narrator")                  # the player's widgets may share labels with the program's
        if self.video_look:
            self._gui_stage_child(stage, avail)
            self._gui_subtitle()
            self._gui_ripples()
        elif landscape:
            strip_width = max(STRIP_MIN_WIDTH_EM * em, 0.4 * avail.x)
            self._gui_stage(stage, ImVec2(avail.x - strip_width - spacing.x, avail.y))
            imgui.same_line()
            self._gui_strip(ImVec2(strip_width, avail.y))
        else:
            strip_height = min(self._strip_height(avail.x), 0.6 * avail.y)
            self._gui_stage(stage, ImVec2(avail.x, avail.y - strip_height - spacing.y))
            self._gui_strip(ImVec2(avail.x, strip_height))
        imgui.pop_id()

    def _button_height(self) -> float:
        """Large enough for a finger in the phone's layout"""
        return TOUCH_BUTTON_EM * hello_imgui.em_size() if self.compact else imgui.get_frame_height()

    # ---- the stage and the panels --------------------------------------------------------------------------------
    def _gui_stage_child(self, stage: Callable[[], None], size: ImVec2) -> None:
        imgui.push_id("stage")
        imgui.begin_child("##stage", ImVec2(max(1.0, size.x), max(1.0, size.y)))
        stage()
        imgui.end_child()
        imgui.pop_id()

    def _gui_stage(self, stage: Callable[[], None], size: ImVec2) -> None:
        """The stage, and the open panel: beside it on a wide window, over it on a narrow one"""
        if not self.panel:
            self._gui_stage_child(stage, size)
        elif size.x >= SIDE_PANEL_MIN_WIDTH_EM * hello_imgui.em_size():
            panel_width = 0.4 * size.x
            self._gui_stage_child(stage, ImVec2(size.x - panel_width - imgui.get_style().item_spacing.x, size.y))
            imgui.same_line()
            self._gui_panel(ImVec2(panel_width, size.y))
        else:
            self._gui_panel(size)

    def _toggle_panel(self, panel: str, section: Optional[Section] = None) -> None:
        same = self.panel == panel and self.open_section is section
        self.panel, self.open_section = ("", None) if same else (panel, section)

    def _gui_panel(self, size: ImVec2) -> None:
        """A section, the full text, the scenario or the program, with a close button"""
        assert self.script is not None
        h = self._button_height()
        imgui.begin_child("##panel", ImVec2(max(1.0, size.x), max(1.0, size.y)), imgui.ChildFlags_.borders)
        if self.panel == "section" and self.open_section is not None:
            title = self.open_section.title
        else:
            title = {"full_text": "Full text", "scenario": "Scenario", "program": "Program"}.get(self.panel, "")
        imgui.align_text_to_frame_padding()
        imgui.text(title)
        imgui.same_line(imgui.get_window_width() - h - imgui.get_style().window_padding.x)
        if imgui.button(fa.ICON_FA_TIMES + "##close", ImVec2(h, h)):
            self.panel, self.open_section = "", None
        imgui.separator()
        imgui.begin_child("##panel_content")
        if self.panel == "section" and self.open_section is not None:
            rich_md.render(self.open_section.markdown)
        elif self.panel == "full_text":
            rich_md.register_fenced_block_renderer("cues", lambda _code: None)
            rich_md.render(self.script.markdown)
        elif self.panel == "scenario":
            text = Path(self.file).read_text(encoding="utf-8") if os.path.isfile(self.file) else ""
            rich_md.render_raw("````markdown\n" + text + "\n````")
        elif self.panel == "program":
            rich_md.render_file(self.program or self.file, "")
        imgui.end_child()
        imgui.end_child()

    # ---- the video's subtitles and ripples ------------------------------------------------------------------------
    def _gui_subtitle(self) -> None:
        """The sentence being read: centered lines on a dark band, at the bottom of the window, over everything"""
        sentence = self.current_sentence() if self._video_frames >= VIDEO_WARMUP_FRAMES else None
        text = re.sub(r"\*+|`", "", sentence.text) if sentence is not None else ""   # markdown's marks: not shown
        if self._recorder is not None:
            self._recorder.note_subtitle(text)
        if sentence is None or not text:
            return
        em = hello_imgui.em_size()
        viewport = imgui.get_main_viewport()
        imgui.push_font(None, imgui.get_style().font_size_base * SUBTITLE_EM)
        font, size, line_height = imgui.get_font(), imgui.get_font_size(), imgui.get_text_line_height()
        lines: list[str] = []
        for word in text.split():
            if lines and imgui.calc_text_size(lines[-1] + " " + word).x <= SUBTITLE_MAX_WIDTH * viewport.size.x:
                lines[-1] += " " + word
            else:
                lines.append(word)
        widths = [imgui.calc_text_size(line).x for line in lines]
        alpha = min(1.0, (self.t - sentence.start) / SUBTITLE_FADE)
        pad = ImVec2(0.6 * size, 0.25 * size)
        center_x = viewport.pos.x + viewport.size.x / 2
        top = viewport.pos.y + viewport.size.y - SUBTITLE_BOTTOM_EM * em - pad.y - line_height * len(lines)
        draw_list = imgui.get_foreground_draw_list()
        draw_list.add_rect_filled(ImVec2(center_x - max(widths) / 2 - pad.x, top - pad.y),
                                  ImVec2(center_x + max(widths) / 2 + pad.x, top + line_height * len(lines) + pad.y),
                                  imgui.color_convert_float4_to_u32(ImVec4(0.0, 0.0, 0.0, 0.72 * alpha)),
                                  rounding=0.3 * size)
        white = imgui.color_convert_float4_to_u32(ImVec4(1.0, 1.0, 1.0, alpha))
        for i, line in enumerate(lines):
            draw_list.add_text(font, size, ImVec2(center_x - widths[i] / 2, top + i * line_height), white, line)
        imgui.pop_font()

    def _gui_ripples(self) -> None:
        """A ring that grows and fades where a gesture clicked (with the cursor: the program may hide both)"""
        now = imgui.get_time()
        self._ripples = [(p, t0) for p, t0 in self._ripples if now - t0 < RIPPLE_DURATION]
        if not imgui.get_io().mouse_draw_cursor:
            return
        em = hello_imgui.em_size()
        for p, t0 in self._ripples:
            k = (now - t0) / RIPPLE_DURATION
            color = ImVec4(RIPPLE_COLOR.x, RIPPLE_COLOR.y, RIPPLE_COLOR.z, RIPPLE_COLOR.w * (1.0 - k))
            imgui.get_foreground_draw_list().add_circle(p, em * (0.3 + 1.2 * k), imgui.color_convert_float4_to_u32(color),
                                                        thickness=1.0 + 0.2 * em * (1.0 - k))

    # ---- the strip -----------------------------------------------------------------------------------------------
    def _strip_height(self, width: float) -> float:
        """The strip's height at a window's width: the same for every paragraph, so that the stage keeps its size"""
        style = imgui.get_style()
        inner = width - 2 * style.window_padding.x
        h, sp = self._button_height(), style.item_spacing.y
        return (2 * style.window_padding.y + (h + sp) + (self._paragraph_height(inner) + sp)
                + self._prompt_block_height(inner) + self._chips_block_height(inner) + h)

    def _paragraph_height(self, width: float) -> float:
        """The tallest paragraph at this width: estimated with imgui's font, raised by what rich_md really drew"""
        assert self.script is not None
        self._note_drawn(width, 0.0)
        tallest = max((imgui.calc_text_size(_spoken_text(p.text), wrap_width=width).y
                       for c in self.script.chapters for p in c.paragraphs), default=0.0)
        return max(tallest * PARAGRAPH_ESTIMATE_SCALE, self._tallest_drawn)

    def _note_drawn(self, width: float, height: float) -> None:
        if abs(width - self._measured_width) > 0.5:
            self._measured_width, self._tallest_drawn = width, 0.0
        self._tallest_drawn = max(self._tallest_drawn, height)

    def _hint_visible(self) -> bool:
        w = self.waiting
        return (w is not None and w.kind == "challenge" and bool(w.hint)
                and time.time() - self.waiting_since > w.hint_after)

    def _prompt_block_height(self, width: float) -> float:
        """The pause's prompt (wrapped), its hint, and its Continue button"""
        if self.waiting is None:
            return 0.0
        sp = imgui.get_style().item_spacing.y
        height = imgui.calc_text_size(self.waiting.prompt, wrap_width=width).y + sp
        if self._hint_visible():
            height += imgui.calc_text_size(self.waiting.hint, wrap_width=width).y + sp
        return height + self._button_height() + sp

    @staticmethod
    def _chip_labels(chapter: Chapter) -> list[str]:
        icons = {"More": fa.ICON_FA_INFO_CIRCLE, "Code": fa.ICON_FA_CODE, "References": fa.ICON_FA_BOOK}
        return [f"{icons.get(s.kind, '')} {s.title}" for s in chapter.sections]

    def _chip_rows(self, chapter: Chapter, width: float) -> list[list[int]]:
        """The chips of a chapter's sections, in rows that fit the width: the indices of each row"""
        style = imgui.get_style()
        rows: list[list[int]] = []
        x = 0.0
        for i, label in enumerate(self._chip_labels(chapter)):
            w = imgui.calc_text_size(label).x + 2 * style.frame_padding.x
            if rows and x + style.item_spacing.x + w <= width:
                rows[-1].append(i)
                x += style.item_spacing.x + w
            else:
                rows.append([i])
                x = w
        return rows

    def _chips_block_height(self, width: float) -> float:
        """As many rows as the chapter that has the most: the bar stays in place from a chapter to the next"""
        assert self.script is not None
        rows = max((len(self._chip_rows(c, width)) for c in self.script.chapters), default=0)
        return rows * (self._button_height() + imgui.get_style().item_spacing.y)

    def _gui_strip(self, size: ImVec2) -> None:
        """The chapter's line, the paragraph, the pause's prompt, the sections' chips, and the bar at the bottom"""
        assert self.script is not None
        style = imgui.get_style()
        bg = imgui.get_style_color_vec4(imgui.Col_.window_bg)
        imgui.push_style_color(imgui.Col_.child_bg, ImVec4(bg.x + 0.05, bg.y + 0.05, bg.z + 0.06, 1.0))
        imgui.begin_child("##strip", size, imgui.ChildFlags_.always_use_window_padding,
                          imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse)
        imgui.pop_style_color()
        h, sp = self._button_height(), style.item_spacing.y
        top = imgui.get_cursor_pos_y()
        inner = imgui.get_content_region_avail()
        chapter = self.script.chapters[self.current_chapter()]
        self._gui_chapter_line(h)
        paragraph_height = (inner.y - (h + sp) - sp - self._prompt_block_height(inner.x)
                            - self._chips_block_height(inner.x) - h)
        imgui.begin_child("##paragraph", ImVec2(0, max(1.0, paragraph_height)))
        self._gui_paragraph(inner.x)
        imgui.end_child()
        if self.waiting is not None:
            imgui.push_text_wrap_pos(0.0)
            imgui.text_colored(PROMPT_COLOR, self.waiting.prompt)
            if self._hint_visible():
                imgui.text_disabled(self.waiting.hint)
            imgui.pop_text_wrap_pos()
            if imgui.button(("Continue" if self.waiting.kind == "pause" else "Skip") + "###waiting", ImVec2(0, h)):
                self._resume()
        self._gui_chips(chapter, inner.x, h)
        imgui.set_cursor_pos_y(top + inner.y - h)
        self._gui_bar(h)
        imgui.end_child()

    def _gui_chapter_line(self, h: float) -> None:
        """The chapter's title: a tap opens the lesson's menu (the chapters, the full text, the sources)"""
        assert self.script is not None
        chapters = self.script.chapters
        now = self.current_chapter()
        title = chapters[now].title or f"Chapter {now + 1}"
        if imgui.button(f"{fa.ICON_FA_BARS}  {title}   {now + 1}/{len(chapters)}###menu", ImVec2(0, h)):
            imgui.open_popup("##lesson_menu")
        if self.gestures.unavailable:
            imgui.same_line()
            imgui.align_text_to_frame_padding()
            imgui.text_disabled("No test engine here: the gestures are skipped")
        if not imgui.begin_popup("##lesson_menu"):
            return
        imgui.push_style_var(imgui.StyleVar_.selectable_text_align, ImVec2(0.0, 0.5))
        for i, chapter in enumerate(chapters):
            label = f"{i + 1}. {chapter.title or f'Chapter {i + 1}'}"
            if i == now:
                done = (self.t - chapter.start) / max(1e-6, chapter.end - chapter.start)
                label += f"   ({min(100, int(100 * done))}%)"
            if imgui.selectable(f"{label}###chapter{i}", i == now, 0, ImVec2(0, h))[0]:
                self.seek(chapter.start)
        imgui.separator()
        for panel, label in (("full_text", f"{fa.ICON_FA_BOOK}  Full text"),
                             ("scenario", f"{fa.ICON_FA_FILE_ALT}  Scenario"),
                             ("program", f"{fa.ICON_FA_CODE}  Program")):
            if imgui.selectable(label, self.panel == panel, 0, ImVec2(0, h))[0]:
                self._toggle_panel(panel)
        imgui.pop_style_var()
        imgui.end_popup()

    def _gui_paragraph(self, width: float) -> None:
        """The paragraph being read, its spoken sentence in bold"""
        paragraph = self.current_paragraph()
        sentence = self.current_sentence()
        if paragraph is None or sentence is None:
            return
        parts = [f"**{s.text}**" if s is sentence else s.text for s in paragraph.sentences]
        top = imgui.get_cursor_pos_y()
        rich_md.render(" ".join(parts))
        self._note_drawn(width, imgui.get_cursor_pos_y() - top)

    def _gui_chips(self, chapter: Chapter, width: float, h: float) -> None:
        """The chapter's sections (More, Code...): a tap opens or closes one"""
        labels = self._chip_labels(chapter)
        for row in self._chip_rows(chapter, width):
            for n, i in enumerate(row):
                if n > 0:
                    imgui.same_line()
                section = chapter.sections[i]
                selected = self.panel == "section" and self.open_section is section
                if selected:
                    imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
                if imgui.button(f"{labels[i]}##section{i}", ImVec2(0, h)):
                    self._toggle_panel("section", section)
                if selected:
                    imgui.pop_style_color()

    def _gui_bar(self, h: float) -> None:
        """Back one sentence, play or pause, forward one sentence, the progress (a tap seeks), the voice"""
        assert self.script is not None
        button = ImVec2(1.25 * h, h)
        if imgui.button(fa.ICON_FA_STEP_BACKWARD + "##back", button):
            sentence = self.current_sentence()     # back to the start of this sentence, or to the previous one
            self.sentence_offset(0 if sentence is not None and self.t - sentence.start > 1.5 else -1)
        imgui.same_line()
        if imgui.button((fa.ICON_FA_PAUSE if self.playing else fa.ICON_FA_PLAY) + "###play", button):
            self.playing = not self.playing
            if self.playing and self.t >= self.script.duration:
                self.seek(0.0)
        imgui.same_line()
        if imgui.button(fa.ICON_FA_STEP_FORWARD + "##forward", button):
            self.sentence_offset(1)
        imgui.same_line()
        voice = self.audio is not None and bool(self.audio_index)
        voice_width = button.x + imgui.get_style().item_spacing.x if voice else 0.0
        self._gui_progress(ImVec2(max(1.0, imgui.get_content_region_avail().x - voice_width), h))
        if voice:
            imgui.same_line()
            if imgui.button((fa.ICON_FA_VOLUME_UP if self.voice_on else fa.ICON_FA_VOLUME_OFF) + "###voice", button):
                self.voice_on = not self.voice_on
                self._stop_audio()

    def _gui_progress(self, size: ImVec2) -> None:
        """The lesson's progress, a tick at each chapter; a tap or a drag seeks (to the start of a sentence)"""
        assert self.script is not None
        duration = max(1e-6, self.script.duration)
        pos = imgui.get_cursor_screen_pos()
        imgui.invisible_button("##seek", size)
        if imgui.is_item_active():
            target = max(0.0, min(1.0, (imgui.get_io().mouse_pos.x - pos.x) / size.x)) * duration
            starts = [s.start for c in self.script.chapters for p in c.paragraphs for s in p.sentences]
            landing = max((s for s in starts if s <= target + 1e-6), default=0.0)
            sentence = self.current_sentence()
            if sentence is None or abs(sentence.start - landing) > 1e-6:   # seek once per sentence, while dragging
                self.seek(target)
        imgui.set_cursor_screen_pos(pos)
        imgui.progress_bar(self.t / duration, size, f"{self.t:.0f} / {self.script.duration:.0f} s")
        color = imgui.get_color_u32(imgui.Col_.text, 0.45)
        for chapter in self.script.chapters[1:]:
            x = pos.x + size.x * chapter.start / duration
            imgui.get_window_draw_list().add_line(ImVec2(x, pos.y), ImVec2(x, pos.y + size.y), color, 2.0)


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
