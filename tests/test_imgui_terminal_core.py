"""Pure-python tests for imgui_bundle.imgui_terminal (no GUI window).

Covers the VT layer (pyte glue) and the selection model, which do not need an
ImGui context.
"""
import pytest

pytest.importorskip("pyte")

from imgui_bundle.imgui_terminal import TerminalView  # noqa: E402


def make_view(cols: int = 20, rows: int = 4) -> TerminalView:
    return TerminalView(cols=cols, rows=rows)  # font optional since it never renders


# -- VT robustness ----------------------------------------------------------

def test_private_dsr_does_not_crash_and_replies() -> None:
    # tmux sends a *private* DSR (CSI ? 6 n); pyte 0.8.2 raises TypeError on it
    # unless _VTScreen works around it. The reply must go back to the program.
    v = make_view()
    replies: list[bytes] = []
    v.on_input = replies.append
    v.feed(b"\x1b[?6n")
    v.feed(b"\x1b[6n")   # normal DSR (cursor position)
    v.feed(b"\x1b[c")    # device attributes
    assert replies == [b"\x1b[1;1R", b"\x1b[1;1R", b"\x1b[?6c"]


def test_bad_escape_does_not_kill_feed() -> None:
    v = make_view()
    v.feed(b"\x1b[999;999;999$~garbage")  # unsupported sequence
    v.feed(b"still alive")
    assert "still alive" in "\n".join(v.screen.display)


def test_title_tracks_osc() -> None:
    v = make_view()
    assert v.title == ""
    v.feed(b"\x1b]0;my window title\x07")
    assert v.title == "my window title"


# -- selection model --------------------------------------------------------

def fill_lines(v: TerminalView, n: int) -> None:
    for i in range(n):
        v.feed(f"line{i:02d}-abcdef\r\n".encode())


def test_selection_partial_line() -> None:
    v = make_view()
    fill_lines(v, 10)
    v._sel_anchor, v._sel_head = (1, 4), (1, 10)
    assert v._selection_text() == "01-abc"


def test_selection_spans_history_to_live() -> None:
    v = make_view()
    fill_lines(v, 10)
    n_hist = len(v.screen.history.top)
    assert n_hist > 0, "test needs lines scrolled off into history"
    v._sel_anchor = (n_hist - 1, 4)   # last history line...
    v._sel_head = (n_hist + 1, 6)     # ...into the live rows
    text = v._selection_text()
    assert text.count("\n") == 2
    assert text.startswith("0")       # tail of lineNN-abcdef from col 4


def test_selection_reversed_drag_normalizes() -> None:
    v = make_view()
    fill_lines(v, 10)
    v._sel_anchor, v._sel_head = (2, 8), (2, 2)
    assert v._selection_text() == "ne02-a"


def test_selection_empty() -> None:
    v = make_view()
    fill_lines(v, 10)
    v._sel_anchor = v._sel_head = (2, 5)
    assert v._selection_text() == ""
