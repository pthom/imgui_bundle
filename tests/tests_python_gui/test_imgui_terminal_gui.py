"""GUI tests for imgui_bundle.imgui_terminal (opens real windows, driven by the
ImGui Test Engine via immapp.testing).

Covers keyboard -> bytes translation (including the macOS Cmd<>Ctrl swap and
its test-engine caveat) and the native-scroll behaviors (scrollbar, follow
bottom, selection across scrollback).
"""
import pytest

pytest.importorskip("pyte")

from imgui_bundle import imgui, hello_imgui  # noqa: E402
from imgui_bundle.immapp import testing  # noqa: E402
from imgui_bundle.imgui_terminal import TerminalView  # noqa: E402


def physical_ctrl_mod() -> imgui.Key:
    """The modifier to inject to emulate a PHYSICAL Ctrl press.

    On macOS real backends swap Cmd<>Ctrl in AddKeyEvent, but the test engine
    injects modifiers directly (pre-swap): physical Ctrl must be sent as Super.
    """
    if imgui.get_io().config_mac_osx_behaviors:
        return imgui.Key.mod_super
    return imgui.Key.mod_ctrl


def test_keyboard_to_bytes() -> None:
    view = TerminalView(cols=40, rows=8)
    sent: list[bytes] = []
    view.on_input = sent.append

    def gui() -> None:
        imgui.set_next_window_focus()
        view.render_in_child("term")

    results: list[tuple[str, bytes, bytes]] = []

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.set_ref("")
        K = imgui.Key
        ctrl = physical_ctrl_mod()
        cases = [
            ("Ctrl-A", ctrl | K.a, b"\x01"),
            ("Ctrl-C", ctrl | K.c, b"\x03"),
            ("Ctrl-Z", ctrl | K.z, b"\x1a"),
            ("Ctrl-Space", ctrl | K.space, b"\x00"),
            ("Alt-B (Meta)", K.mod_alt | K.b, b"\x1bb"),
            ("Tab", K.tab, b"\t"),
            ("Shift-Tab", K.mod_shift | K.tab, b"\x1b[Z"),
            ("F1", K.f1, b"\x1bOP"),
            ("F10", K.f10, b"\x1b[21~"),
            ("Enter", K.enter, b"\r"),
            ("Up", K.up_arrow, b"\x1b[A"),
            ("Ctrl-Left (word)", ctrl | K.left_arrow, b"\x1b[1;5D"),
            ("Shift-Up", K.mod_shift | K.up_arrow, b"\x1b[1;2A"),
            ("Alt-Right (word)", K.mod_alt | K.right_arrow, b"\x1b[1;3C"),
        ]
        ctx.yield_(3)
        for name, chord, expected in cases:
            sent.clear()
            ctx.key_press(chord)
            ctx.yield_()
            results.append((name, expected, b"".join(sent)))

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params.app_window_params.window_geometry.size = (600, 300)
    testing.run(gui, test_fn, runner_params=params)

    failures = [f"{name}: expected {exp!r}, got {got!r}"
                for name, exp, got in results if exp != got]
    assert not failures, "\n".join(failures)


def test_scrollbar_and_selection() -> None:
    view = TerminalView(cols=40, rows=8)
    for i in range(60):
        view.feed(f"row{i:02d}-XYZ\r\n".encode())

    class Geo:  # child-window geometry captured each frame
        cw = 1.0
        ch = 1.0
        wp = imgui.ImVec2(0, 0)
        scroll = 0.0
        max = 0.0

    geo = Geo()
    forced_scroll: list[float] = []  # test -> gui: emulate a user scroll

    def gui() -> None:
        imgui.set_next_window_focus()
        if imgui.begin_child("term", imgui.ImVec2(0, 0)):
            geo.cw = imgui.calc_text_size("M").x
            geo.ch = imgui.get_text_line_height()
            geo.wp = imgui.get_window_pos()
            view.render()
            if forced_scroll:  # post-render, like real wheel input (which wins)
                imgui.set_scroll_y(forced_scroll.pop())
            geo.scroll = imgui.get_scroll_y()
            geo.max = imgui.get_scroll_max_y()
        imgui.end_child()

    def vis_pos(row: float, col: float) -> imgui.ImVec2:
        return imgui.ImVec2(geo.wp.x + (col + 0.5) * geo.cw,
                            geo.wp.y + (row + 0.5) * geo.ch)

    results: dict[str, bool] = {}

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.set_ref("")
        K = imgui.Key
        ctx.yield_(5)

        results["scrollbar_exists"] = geo.max > 0
        results["follows_bottom"] = abs(geo.scroll - geo.max) < 1.0

        # scrolled up + new output -> position held
        forced_scroll.append(0.0)
        ctx.yield_(3)
        view.feed(b"more-1\r\nmore-2\r\n")
        ctx.yield_(5)
        results["holds_position"] = geo.scroll < geo.max * 0.2

        # typing snaps back to the bottom
        ctx.key_press(K.enter)
        ctx.yield_(5)
        results["typing_snaps"] = abs(geo.scroll - geo.max) < 1.0

        # drag up past the window's top edge -> auto-scroll + multi-line selection
        view._sel_anchor = view._sel_head = None
        ctx.mouse_move_to_pos(vis_pos(4, 2))
        ctx.mouse_down(0)
        s0 = geo.scroll
        ctx.mouse_move_to_pos(imgui.ImVec2(geo.wp.x + 5 * geo.cw, geo.wp.y - 10))
        ctx.yield_(15)
        results["edge_autoscroll_up"] = geo.scroll < s0 - 3 * geo.ch
        ctx.mouse_up(0)
        span = view._selection_span()
        results["drag_sel_multiline"] = span is not None and span[2] - span[0] >= 3

        # shift-click across a scroll keeps the anchor and extends
        view._sel_anchor = view._sel_head = None
        ctx.mouse_move_to_pos(vis_pos(6, 3))
        ctx.mouse_click(0)
        anchor = view._sel_anchor
        forced_scroll.append(0.0)
        ctx.yield_(3)
        ctx.key_down(K.left_shift)
        ctx.mouse_move_to_pos(vis_pos(1, 0))
        ctx.mouse_click(0)
        ctx.key_up(K.left_shift)
        results["shift_anchor_kept"] = view._sel_anchor == anchor
        results["shift_selection_nonempty"] = len(view._selection_text()) > 0

    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params.app_window_params.window_geometry.size = (600, 300)
    testing.run(gui, test_fn, runner_params=params)

    failures = [name for name, ok in results.items() if not ok]
    assert not failures, f"failed checks: {failures} (results: {results})"
