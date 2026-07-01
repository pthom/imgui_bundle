"""TerminalView: a transport-agnostic Dear ImGui terminal widget.

It owns a pyte VT100 screen and knows how to draw it and translate keyboard
input, but it knows *nothing* about where the bytes come from. You push output
bytes in with `feed()`, and you receive keystrokes through the `on_input`
callback. That decoupling is what lets the same widget drive a local shell, an
SSH channel, or a Zenoh subscription (see the TerminalTransport protocol).

Embed it inside any window, or let it manage its own child window. It renders
with the font active at render time (push a monospace font around it):

    view = TerminalView()
    view.on_input = lambda data: my_channel.send(data)
    # ... a background reader calls view.feed(chunk) ...

    def gui():  # each frame
        with imgui_ctx.push_font(mono_font, 0.0):
            view.render_in_child("terminal")

Depends only on pyte + imgui, so it is cross-platform (unlike a local pty).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable, Protocol

try:
    import pyte
except ImportError as e:
    raise ImportError(
        "imgui_terminal needs the 'pyte' package. "
        'Install it with: pip install "imgui-bundle[terminal]"  (or: pip install pyte)'
    ) from e

from imgui_bundle import imgui

IV = imgui.ImVec2
RGB = tuple[int, int, int]

# The 16 ANSI colors, keyed by pyte's color names ("brown" is ANSI yellow).
DEFAULT_ANSI: dict[str, RGB] = {
    "black": (0x00, 0x00, 0x00), "red": (0xC2, 0x36, 0x21),
    "green": (0x25, 0xBC, 0x24), "brown": (0xAD, 0xAD, 0x27),
    "blue": (0x49, 0x2E, 0xE1), "magenta": (0xD3, 0x38, 0xD3),
    "cyan": (0x33, 0xBB, 0xC8), "white": (0xCB, 0xCC, 0xCD),
    "brightblack": (0x81, 0x83, 0x83), "brightred": (0xFC, 0x39, 0x1F),
    "brightgreen": (0x31, 0xE7, 0x22), "brightbrown": (0xEA, 0xEC, 0x23),
    "brightblue": (0x58, 0x33, 0xFF), "brightmagenta": (0xF9, 0x35, 0xF8),
    "brightcyan": (0x14, 0xF0, 0xF0), "brightwhite": (0xE9, 0xEB, 0xEB),
}
_BRIGHTEN = {name: "bright" + name for name in
             ("black", "red", "green", "brown", "blue", "magenta", "cyan", "white")}


@dataclass
class TerminalTheme:
    fg: RGB = (0xCC, 0xCC, 0xCC)
    bg: RGB = (0x1E, 0x1E, 0x1E)
    selection: RGB = (0x33, 0x55, 0x88)
    ansi: dict[str, RGB] = field(default_factory=lambda: dict(DEFAULT_ANSI))


class TerminalTransport(Protocol):
    """Anything that produces/consumes terminal bytes for a TerminalView.

    `start()` takes ownership of the view's callbacks: it overwrites
    `view.on_input` / `view.on_resize` to point at itself, and begins feeding
    output into `view.feed()` (typically from a background thread). To observe
    keystrokes, wrap `view.on_input` AFTER start(). See LocalShellTransport for
    a local-shell implementation; a remote transport (SSH, Zenoh, websocket)
    implements the same two methods.
    """
    def start(self, view: "TerminalView") -> None: ...
    def stop(self) -> None: ...


# keys with no character representation -> the escape sequences a terminal expects
_SPECIAL_KEYS: dict[imgui.Key, bytes] = {
    imgui.Key.enter: b"\r", imgui.Key.keypad_enter: b"\r",
    imgui.Key.backspace: b"\x7f", imgui.Key.escape: b"\x1b",
    imgui.Key.up_arrow: b"\x1b[A", imgui.Key.down_arrow: b"\x1b[B",
    imgui.Key.right_arrow: b"\x1b[C", imgui.Key.left_arrow: b"\x1b[D",
    imgui.Key.home: b"\x1b[H", imgui.Key.end: b"\x1b[F",
    imgui.Key.page_up: b"\x1b[5~", imgui.Key.page_down: b"\x1b[6~",
    imgui.Key.delete: b"\x1b[3~",
    imgui.Key.f1: b"\x1bOP", imgui.Key.f2: b"\x1bOQ",
    imgui.Key.f3: b"\x1bOR", imgui.Key.f4: b"\x1bOS",
    imgui.Key.f5: b"\x1b[15~", imgui.Key.f6: b"\x1b[17~",
    imgui.Key.f7: b"\x1b[18~", imgui.Key.f8: b"\x1b[19~",
    imgui.Key.f9: b"\x1b[20~", imgui.Key.f10: b"\x1b[21~",
    imgui.Key.f11: b"\x1b[23~", imgui.Key.f12: b"\x1b[24~",
}


def _u32(rgb: RGB, alpha: int = 0xFF) -> int:
    r, g, b = rgb
    return (alpha << 24) | (b << 16) | (g << 8) | r


class _VTScreen(pyte.HistoryScreen):
    """pyte HistoryScreen with two fixes needed by real TUIs (tmux, vim):

    - pyte 0.8.2's `report_device_status` lacks `**kwargs`, so a *private* DSR
      query (``CSI ? n``, which tmux sends) raises TypeError. Accept and ignore
      the private flag, matching `report_device_attributes` right above it.
    - `write_process_input` is pyte's reply hook (cursor-position and
      device-attribute answers). By default it is a no-op; route it back to the
      program as input so query-driven apps get their replies.
    """
    reply: Callable[[bytes], None]

    def report_device_status(self, mode: int, **kwargs: bool) -> None:
        super().report_device_status(mode)

    def write_process_input(self, data: str) -> None:
        self.reply(data.encode())


class TerminalView:
    def __init__(self, cols: int = 80, rows: int = 24,
                 theme: TerminalTheme | None = None, history: int = 5000):
        # rendering uses the font active at render() time, which should be
        # monospace (push one around render_in_child / render)
        self.theme = theme or TerminalTheme()
        self.screen = _VTScreen(cols, rows, history=history, ratio=0.5)
        self.screen.reply = self._send  # query replies go back to the program
        self.stream = pyte.ByteStream(self.screen)
        self.lock = threading.Lock()  # screen is read (GUI) + written (transport thread)
        self.on_input: Callable[[bytes], None] = lambda data: None
        self.on_resize: Callable[[int, int], None] = lambda cols, rows: None
        self._snap_bottom = False  # jump back to the live view on next draw
        # selection endpoints as (virtual_line, col) into the `history + live` list;
        # virtual indices are stable across scrolling (only new output shifts them).
        self._sel_anchor: tuple[int, int] | None = None
        self._sel_head: tuple[int, int] | None = None
        self._selecting = False

    @property
    def cols(self) -> int:
        return self.screen.columns

    @property
    def rows(self) -> int:
        return self.screen.lines

    @property
    def title(self) -> str:
        """Window title set by the program (OSC escape), or '' if none."""
        return self.screen.title

    def feed(self, data: bytes) -> None:
        """Push output bytes into the screen. Safe to call from any thread."""
        with self.lock:
            try:
                self.stream.feed(data)
            except Exception:
                pass  # an unsupported escape must not kill the reader thread

    def _send(self, data: bytes) -> None:
        """Bytes the emulator must send back to the program (query replies)."""
        self.on_input(data)

    def render_in_child(self, str_id: str = "terminal",
                        size: imgui.ImVec2 | None = None,
                        child_flags: int = 0, window_flags: int = 0) -> None:
        """Draw the terminal in its own child window (the recommended embedding).

        The child provides what `render()` needs from its host: scrolling (for
        the history scrollbar) and focus (for keyboard input). `size` defaults
        to the remaining content region.
        """
        if imgui.begin_child(str_id, size or IV(0, 0), child_flags, window_flags):
            self.render()
        imgui.end_child()  # always called, like imgui.end()

    def render(self) -> None:
        """Draw the grid and handle input, inside the current window/child.

        Prefer `render_in_child()` unless you manage the host window yourself:
        this method relies on the host window for scrolling (history scrollbar,
        wheel) and focus (keyboard is consumed only while the window is focused).
        The grid fills the host's visible area; size changes are reported via
        `on_resize`.
        """
        cw = imgui.calc_text_size("M").x
        ch = imgui.get_text_line_height()
        # visible area of the host window (content avail already excludes the
        # scrollbar; window height is scroll-independent, unlike content avail y)
        avail_x = imgui.get_content_region_avail().x
        visible_h = imgui.get_window_height() - 2 * imgui.get_style().window_padding.y
        self._maybe_resize(max(20, int(avail_x / cw)), max(4, int(visible_h / ch)))

        if imgui.is_window_focused():
            self._handle_keyboard()

        self._draw(cw, ch)

    # -- input ------------------------------------------------------------
    def _handle_keyboard(self) -> None:
        io = imgui.get_io()

        # Clipboard: Cmd-C/V on macOS, Ctrl-Shift-C/V elsewhere. On macOS Cmd is
        # `key_ctrl` (the Cmd<>Ctrl swap), which is distinct from the terminal's
        # own Ctrl (physical Ctrl -> key_super), so copy never clashes with ^C.
        clip = io.key_ctrl if io.config_mac_osx_behaviors else (io.key_ctrl and io.key_shift)
        if clip:
            if imgui.is_key_pressed(imgui.Key.c):
                self._copy_selection()
                return
            if imgui.is_key_pressed(imgui.Key.v):
                self._paste()
                return

        out: list[bytes] = []
        # macOS: ImGui swaps Cmd<>Ctrl, so physical Ctrl arrives as `key_super`.
        ctrl_down = io.key_super if io.config_mac_osx_behaviors else io.key_ctrl
        if ctrl_down:  # Ctrl-A..Z -> control bytes 0x01..0x1a, Ctrl-Space -> NUL
            for i in range(26):
                if imgui.is_key_pressed(imgui.Key(int(imgui.Key.a) + i)):
                    out.append(bytes([i + 1]))
            if imgui.is_key_pressed(imgui.Key.space):
                out.append(b"\x00")
        elif io.key_alt:  # Alt/Option acts as Meta: ESC-prefixed letter (M-b, M-f...)
            for i in range(26):  # raw letters, ignoring macOS Option composition
                if imgui.is_key_pressed(imgui.Key(int(imgui.Key.a) + i)):
                    out.append(b"\x1b" + bytes([ord("a") + i]))
        else:
            for codepoint in io.input_queue_characters:
                if codepoint >= 0x20 and codepoint != 0x7F:
                    out.append(chr(codepoint).encode("utf-8"))

        if imgui.is_key_pressed(imgui.Key.tab):
            out.append(b"\x1b[Z" if io.key_shift else b"\t")  # Shift-Tab is backtab
        for key, seq in _SPECIAL_KEYS.items():
            if imgui.is_key_pressed(key):
                out.append(seq)

        if out:
            self._snap_bottom = True  # typing snaps back to the live view
            self._sel_anchor = self._sel_head = None  # and clears any selection
            self.on_input(b"".join(out))

    def _paste(self) -> None:
        text = imgui.get_clipboard_text()
        if text:
            self.on_input(text.encode("utf-8"))

    def _copy_selection(self) -> None:
        text = self._selection_text()
        if text:
            imgui.set_clipboard_text(text)

    # -- sizing -----------------------------------------------------------
    def _maybe_resize(self, cols: int, rows: int) -> None:
        if cols == self.cols and rows == self.rows:
            return
        with self.lock:
            self.screen.resize(rows, cols)
        self.on_resize(cols, rows)

    # -- drawing ----------------------------------------------------------
    def _color(self, name: str, default: RGB) -> RGB:
        if name == "default":
            return default
        rgb = self.theme.ansi.get(name)
        if rgb is not None:
            return rgb
        if len(name) == 6:  # pyte hex string for 256-color / truecolor cells
            try:
                return int(name[0:2], 16), int(name[2:4], 16), int(name[4:6], 16)
            except ValueError:
                pass
        return default

    def _colors_of(self, cell: pyte.screens.Char) -> tuple[RGB, RGB]:
        fg_name = _BRIGHTEN[cell.fg] if (cell.bold and cell.fg in _BRIGHTEN) else cell.fg
        fg = self._color(fg_name, self.theme.fg)
        bg = self._color(cell.bg, self.theme.bg)
        return (bg, fg) if cell.reverse else (fg, bg)

    def _draw(self, cw: float, ch: float) -> None:
        dl = imgui.get_window_draw_list()
        rows, cols = self.rows, self.cols

        # background over the window's visible rect (the draw list is clipped to it)
        wp, ws = imgui.get_window_pos(), imgui.get_window_size()
        dl.add_rect_filled(wp, IV(wp.x + ws.x, wp.y + ws.y), _u32(self.theme.bg))

        # `origin` is the top of the FULL virtual content (above the window when
        # scrolled); line i sits at origin.y + i*ch, and only visible lines are drawn.
        origin = imgui.get_cursor_screen_pos()
        scroll_y = imgui.get_scroll_y()
        at_bottom = scroll_y >= imgui.get_scroll_max_y() - 1.0

        with self.lock:
            history = list(self.screen.history.top)
            lines = history + [self.screen.buffer[y] for y in range(rows)]
            n_lines = len(lines)
            self._update_selection(origin, n_lines, cw, ch)
            sel = self._selection_span()

            first = max(0, int(scroll_y / ch))
            for vi in range(first, min(n_lines, first + rows + 1)):
                self._draw_line(dl, origin, vi, lines[vi], cw, ch, cols)
                rng = self._row_sel_range(sel, vi, cols) if sel else None
                if rng is not None:  # translucent highlight over the selected span
                    c0, c1 = rng
                    py = origin.y + vi * ch
                    dl.add_rect_filled(IV(origin.x + c0 * cw, py),
                                       IV(origin.x + c1 * cw, py + ch),
                                       _u32(self.theme.selection, 0x66))

            if at_bottom and sel is None:  # cursor: live view, not selecting
                cur = self.screen.cursor
                if not cur.hidden:
                    px = origin.x + cur.x * cw
                    py = origin.y + (len(history) + cur.y) * ch
                    dl.add_rect_filled(IV(px, py), IV(px + cw, py + ch),
                                       _u32(self.theme.fg, 0x88))

        # declare the full virtual height so the host window scrolls natively
        # (width 0: no horizontal scrollbar; the grid already fits the window)
        imgui.dummy(IV(0.0, n_lines * ch))
        # follow live output unless the user scrolled up; pause while selecting,
        # or it would override the drag-past-the-edge auto-scroll
        if self._snap_bottom or (at_bottom and not self._selecting):
            imgui.set_scroll_y(n_lines * ch)  # clamped to scroll max by imgui
            self._snap_bottom = False

    def _draw_line(self, dl: imgui.ImDrawList, origin: imgui.ImVec2, vi: int,
                   line: dict[int, pyte.screens.Char], cw: float,
                   ch: float, cols: int) -> None:
        x = 0
        while x < cols:  # coalesce consecutive cells sharing fg/bg into one draw
            fg, bg = self._colors_of(line[x])
            start = x
            chars = []
            while x < cols and self._colors_of(line[x]) == (fg, bg):
                chars.append(line[x].data or " ")
                x += 1
            px, py = origin.x + start * cw, origin.y + vi * ch
            if bg != self.theme.bg:
                dl.add_rect_filled(IV(px, py), IV(px + (x - start) * cw, py + ch),
                                   _u32(bg))
            text = "".join(chars)
            if text.strip():
                dl.add_text(IV(px, py), _u32(fg), text)

    # -- selection --------------------------------------------------------
    def _mouse_cell(self, origin: imgui.ImVec2, n_lines: int,
                    cw: float, ch: float) -> tuple[int, int]:
        # origin is the top of the full virtual content, so this maps the mouse
        # straight to a virtual line index (history and live rows alike)
        mp = imgui.get_mouse_pos()
        col = max(0, min(int((mp.x - origin.x) / cw), self.cols))     # cols == line end
        vi = max(0, min(int((mp.y - origin.y) / ch), n_lines - 1))
        return vi, col

    def _update_selection(self, origin: imgui.ImVec2, n_lines: int,
                          cw: float, ch: float) -> None:
        left = imgui.MouseButton_.left
        # exclude the scrollbar strip: clicks there must scroll, not select
        # (cols is computed from the avail width, which excludes the scrollbar)
        on_text = (imgui.is_window_hovered()
                   and imgui.get_mouse_pos().x < origin.x + self.cols * cw)
        if on_text and imgui.is_mouse_clicked(left):
            cell = self._mouse_cell(origin, n_lines, cw, ch)
            if imgui.get_io().key_shift and self._sel_anchor is not None:
                self._sel_head = cell  # shift-click extends the existing selection
            else:
                self._sel_anchor = self._sel_head = cell
            self._selecting = True
        elif self._selecting and imgui.is_mouse_dragging(left):
            # auto-scroll when dragging past the window's top/bottom edge, so a
            # selection can span more than one screenful (no wheel needed)
            my = imgui.get_mouse_pos().y
            wp_y = imgui.get_window_pos().y
            if my < wp_y:
                imgui.set_scroll_y(imgui.get_scroll_y() - ch)
            elif my > wp_y + imgui.get_window_height():
                imgui.set_scroll_y(imgui.get_scroll_y() + ch)
            self._sel_head = self._mouse_cell(origin, n_lines, cw, ch)
        if imgui.is_mouse_released(left):
            self._selecting = False

    def _selection_span(self) -> tuple[int, int, int, int] | None:
        """Normalized selection as (start_line, start_col, end_line, end_col)."""
        a, b = self._sel_anchor, self._sel_head
        if a is None or b is None or a == b:
            return None
        (sl, sc), (el, ec) = (a, b) if a <= b else (b, a)
        return sl, sc, el, ec

    def _row_sel_range(self, sel: tuple[int, int, int, int] | None, vi: int,
                       cols: int) -> tuple[int, int] | None:
        if sel is None:
            return None
        sl, sc, el, ec = sel
        if vi < sl or vi > el:
            return None
        c0 = sc if vi == sl else 0
        c1 = ec if vi == el else cols
        return (c0, c1) if c1 > c0 else None

    def _selection_text(self) -> str:
        sel = self._selection_span()
        if sel is None:
            return ""
        sl, sc, el, ec = sel
        with self.lock:
            lines = (list(self.screen.history.top)
                     + [self.screen.buffer[y] for y in range(self.rows)])
        parts = []
        for vi in range(sl, el + 1):
            if not 0 <= vi < len(lines):
                continue
            line = lines[vi]
            c0 = sc if vi == sl else 0
            c1 = ec if vi == el else self.cols
            parts.append("".join(line[x].data or " " for x in range(c0, c1)).rstrip())
        return "\n".join(parts)
