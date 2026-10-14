"""The ImGui Explorer: a video tour

Every demo of Dear ImGui beside its code. The cursor of the test engine hovers, clicks and scrolls; subtitles tell.
`python imgui_explorer_tour.py cut_demo_code.md` plays a cut; add `--video out.mp4` to record it.
"""
import sys
from pathlib import Path
from typing import Any, Optional

from imgui_bundle import hello_imgui, imgui, immapp, imgui_explorer, rich_md, icons_fontawesome_4 as fa
from imgui_bundle import ImVec2, ImVec4

sys.path.insert(0, str(Path(__file__).parent.parent / "grokking"))   # the player, shared with the grokking lesson
import narrator  # noqa: E402

WINDOW_SIZE = (960, 540)       # in points: 1920 x 1080 pixels on a Retina screen
SCENARIO = "cut_demo_code.md"  # the cut played when none is given
URL = "pthom.github.io/imgui_explorer"
LIBRARIES = ["imgui", "implot", "implot3_d"]   # the toolbar's libraries, as in the online explorer
PHONE_LIBRARY = "imgui"        # the phone shows this library's manual alone: the main one, to end with
PHONE_FONT_SCALE = 0.7         # the app's zoom in the phone, against the desktop's (the explorer shows its code smaller)
PHONE_EM = 0.7                 # the phone's own sizes (its bars), in the desktop's em
PHONE_HEIGHT = 0.92            # the phone's height, in the stage's
PHONE_ASPECT = 402 / 874       # an iPhone's screen (width / height)
PHONE_CENTER_X = 0.68          # the phone's place, in the stage's width; its caption is at the left
PHONE_STATUS_BAR_EM = 1.9      # the phone's status bar, above the app (in the phone's em)
PHONE_HOME_BAR_EM = 1.1        # its home indicator, below the app
CARD_DIM = ImVec4(0.03, 0.04, 0.07, 0.88)   # the veil under a card
WHITE, GRAY, ACCENT = ImVec4(1, 1, 1, 1), ImVec4(0.8, 0.84, 0.9, 1), ImVec4(1.0, 0.75, 0.3, 1.0)
Lines = list[tuple[str, float, ImVec4]]   # a card's lines: text, size (in em), color; the first one in bold
CARDS: dict[str, Lines] = {
    "title": [("Dear ImGui Explorer", 3.0, WHITE), ("Every demo, beside its code", 1.5, GRAY)],
    "end": [("Dear ImGui Explorer", 2.6, WHITE), ("C++ and Python, in your browser", 1.4, GRAY), (URL, 1.5, ACCENT)],
}
PHONE_CAPTION: Lines = [("On a phone too", 2.4, WHITE), ("in the browser, nothing to install", 1.3, GRAY)]


class AppState:
    def __init__(self) -> None:
        self.scene = "desktop"     # "desktop", or "phone": the explorer in a phone, on a background
        self.card = ""             # "title" or "end": a card over the explorer
        self.card_alpha = 0.0      # the card's opacity (animated: it fades)
        self.veil = 0.0            # a black veil over everything: a fade between two scenes


app_state = AppState()
switch_id = [0]                # the phone's "Demo | Code" switch: its id, recorded each frame


# =============================================================================
# The stage
# =============================================================================

def u32(color: ImVec4, alpha: float = 1.0) -> int:
    return imgui.color_convert_float4_to_u32(ImVec4(color.x, color.y, color.z, color.w * alpha))


def draw_lines(lines: Lines, center: ImVec2, alpha: float) -> None:
    """Centered lines of text, over everything"""
    bold = rich_md.get_font(rich_md.MarkdownFontSpec(False, True, 0)).font
    base = imgui.get_style().font_size_base
    sizes = []
    for i, (text, size_em, _) in enumerate(lines):
        imgui.push_font(bold if i == 0 else None, base * size_em)
        sizes.append((imgui.calc_text_size(text), imgui.get_font(), imgui.get_font_size()))
        imgui.pop_font()
    gap = 0.6 * hello_imgui.em_size()
    y = center.y - (sum(s.y for s, _, _ in sizes) + gap * (len(lines) - 1)) / 2
    for (text, _, color), (text_size, font, font_size) in zip(lines, sizes, strict=True):
        imgui.get_foreground_draw_list().add_text(font, font_size, ImVec2(center.x - text_size.x / 2, y),
                                                  u32(color, alpha), text)
        y += text_size.y + gap


def int_id(id_: int) -> int:
    """An id, as PushID(int) takes it"""
    return id_ if id_ < 2**31 else id_ - 2**32


def record_switch_id() -> None:
    """The id of the "Demo | Code" switch, an invisible button: the toolbar's layout pushes its id as an int"""
    imgui.push_id(int_id(imgui.get_id("tools")))
    switch_id[0] = imgui.get_id("##demo_code_switch")
    imgui.pop_id()


def gui_phone_bars(screen: ImVec2, size: ImVec2, em: float, rounding: float) -> None:
    """The phone's screen (rounded as the bezel's inner edge), its status bar (the time, the battery) and its home
    indicator, around the app; em: the phone's"""
    draw_list = imgui.get_window_draw_list()
    draw_list.add_rect_filled(screen, screen + size, u32(imgui.get_style_color_vec4(imgui.Col_.window_bg)), rounding)
    imgui.push_font(rich_md.get_font(rich_md.MarkdownFontSpec(False, True, 0)).font, 0.0)
    font = imgui.get_font()
    draw_list.add_text(font, 0.95 * em, ImVec2(screen.x + 1.8 * em, screen.y + 0.45 * em), u32(WHITE), "9:41")
    imgui.pop_font()
    battery = ImVec2(screen.x + size.x - 3.2 * em, screen.y + 0.55 * em)
    draw_list.add_rect(battery, battery + ImVec2(1.5 * em, 0.7 * em), u32(WHITE, 0.5), 0.2 * em, thickness=1.0)
    draw_list.add_rect_filled(battery + ImVec2(0.15 * em, 0.15 * em), battery + ImVec2(1.15 * em, 0.55 * em),
                              u32(WHITE), 0.1 * em)
    pill = ImVec2(0.36 * size.x, 0.2 * em)
    pill_pos = ImVec2(screen.x + (size.x - pill.x) / 2, screen.y + size.y - 0.65 * em)
    draw_list.add_rect_filled(pill_pos, pill_pos + pill, u32(WHITE, 0.75), pill.y / 2)


def gui_phone() -> None:
    """The explorer in a phone's screen (one pane at a time), on a gradient, its caption at the left"""
    pos, avail = imgui.get_cursor_screen_pos(), imgui.get_content_region_avail()
    top, bottom = ImVec4(0.10, 0.13, 0.22, 1.0), ImVec4(0.30, 0.16, 0.28, 1.0)
    viewport, draw_list = imgui.get_main_viewport(), imgui.get_window_draw_list()
    draw_list.push_clip_rect(viewport.pos, viewport.pos + viewport.size)   # the gradient fills the window, margins too
    draw_list.add_rect_filled_multi_color(viewport.pos, viewport.pos + viewport.size, u32(top), u32(top), u32(bottom),
                                          u32(bottom))
    draw_list.pop_clip_rect()
    height = avail.y * PHONE_HEIGHT
    size = ImVec2(height * PHONE_ASPECT, height)
    screen = ImVec2(pos.x + avail.x * PHONE_CENTER_X - size.x / 2, pos.y + (avail.y - size.y) / 2)
    em = hello_imgui.em_size()
    bezel, rounding = 0.55 * em, 0.16 * size.x   # the bezel's width; its rounding, at the middle of its stroke
    gui_phone_bars(screen, size, PHONE_EM * em, rounding - bezel / 2)
    status, home = PHONE_STATUS_BAR_EM * PHONE_EM * em, PHONE_HOME_BAR_EM * PHONE_EM * em
    imgui.set_cursor_screen_pos(ImVec2(screen.x, screen.y + status))
    # The explorer's own zoom (FontScaleMain), which also scales its code: it pushes the code font at its own size
    style = imgui.get_style()
    desktop_scale = style.font_scale_main
    style.font_scale_main = desktop_scale * PHONE_FONT_SCALE
    imgui.begin_child("##phone", ImVec2(size.x, size.y - status - home), 0,
                      imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse)
    record_switch_id()
    imgui_explorer.show_imgui_explorer_gui_cpp(imgui_explorer.ImGuiExplorerLibrary[PHONE_LIBRARY])
    style.font_scale_main = desktop_scale      # before the child ends: the stage's font size is computed then
    imgui.end_child()
    # The bezel, over the demo's window too: a thick ring whose inner edge rounds the screen's corners
    fg = imgui.get_foreground_draw_list()
    fg.add_rect(screen - ImVec2(bezel / 2, bezel / 2), screen + size + ImVec2(bezel / 2, bezel / 2),
                u32(ImVec4(0.05, 0.05, 0.06, 1.0)), rounding=rounding, thickness=bezel)
    fg.add_rect(screen - ImVec2(bezel, bezel), screen + size + ImVec2(bezel, bezel),
                u32(ImVec4(0.45, 0.47, 0.52, 1.0)), rounding=rounding + bezel / 2, thickness=1.5)
    island = ImVec2(0.3 * size.x, 0.35 * em)
    island_pos = ImVec2(screen.x + (size.x - island.x) / 2, screen.y + 0.35 * em)
    fg.add_rect_filled(island_pos, island_pos + island, u32(ImVec4(0.0, 0.0, 0.0, 1.0)), island.y / 2)
    draw_lines(PHONE_CAPTION, ImVec2((pos.x + screen.x) / 2, pos.y + avail.y / 2), 1.0)   # centered at the left
    # A finger, rather than the arrow
    mouse = imgui.get_io().mouse_pos
    if lesson.playing_video() and screen.x <= mouse.x <= screen.x + size.x and screen.y <= mouse.y <= screen.y + size.y:
        pressed = imgui.is_mouse_down(imgui.MouseButton_.left)
        fg.add_circle_filled(mouse, 0.75 * em, u32(WHITE, 0.55 if pressed else 0.3))
        fg.add_circle(mouse, 0.75 * em, u32(WHITE, 0.8), thickness=1.5)


def gui_card() -> None:
    """A title or end card: centered lines on a veil, over the explorer"""
    lines = CARDS.get(app_state.card)
    if not lines or app_state.card_alpha <= 0.0:
        return
    viewport = imgui.get_main_viewport()
    imgui.get_foreground_draw_list().add_rect_filled(viewport.pos, viewport.pos + viewport.size,
                                                     u32(CARD_DIM, app_state.card_alpha))
    draw_lines(lines, viewport.pos + viewport.size * 0.5, app_state.card_alpha)


def gui_stage() -> None:
    if app_state.scene == "phone":
        gui_phone()
    else:
        imgui_explorer.show_imgui_explorer_gui_cpp()
    gui_card()
    viewport = imgui.get_main_viewport()
    if app_state.veil > 0.0:
        imgui.get_foreground_draw_list().add_rect_filled(viewport.pos, viewport.pos + viewport.size,
                                                         u32(ImVec4(0, 0, 0, 1), app_state.veil))
    if lesson.playing_video():   # the arrow, on the desktop's scene only: not under a card or a veil, not on a phone
        hidden = app_state.scene == "phone" or app_state.card_alpha > 0.5 or app_state.veil > 0.5
        imgui.get_io().mouse_draw_cursor = not hidden


# =============================================================================
# The lesson
# =============================================================================

def _scenario() -> Path:
    names = [a for a in sys.argv[1:] if a.endswith(".md")]
    return Path(__file__).parent / (names[0] if names else SCENARIO)


def _video_output() -> str:
    args = sys.argv[1:]
    return args[args.index("--video") + 1] if "--video" in args and args.index("--video") + 1 < len(args) else ""


lesson = narrator.Lesson(_scenario(), program=__file__)
lesson.param(name="scene", owner=app_state)
lesson.param(name="card", owner=app_state)
lesson.param(name="card_alpha", owner=app_state, range=(0.0, 1.0))
lesson.param(name="veil", owner=app_state, range=(0.0, 1.0))
lesson.constant(name="API", value=fa.ICON_FA_BOOK + " API: ")   # the code's menu item that opens a function's card
lesson.constant(name="API_TAB", value="**/" + fa.ICON_FA_BOOK + " API")   # the code pane's API tab


NO_ERROR = imgui.test_engine.TestOpFlags_.no_error


def _window(part: str) -> Any:
    """The active window whose name contains `part` (child windows' names end with a hash)"""
    return next((w for w in imgui.get_current_context().windows if w.active and part in w.name), None)


def _rect(info: Any) -> Optional[narrator.Rect]:
    return (info.rect_full.min, info.rect_full.max) if info.id_ != 0 else None


def target_code(_: str, ctx: Any) -> Optional[narrator.Rect]:
    """The code, in its editor"""
    window = _window("/##code_")
    return (window.pos, window.pos + window.size) if window is not None else None


def target_button(name: str, ctx: Any) -> Optional[narrator.Rect]:
    """A button of the toolbar: "cpp", "python" (the logos), "switch" ("Demo | Code", on a phone)"""
    if name == "switch":
        return _rect(ctx.item_info(imgui.test_engine.TestRef(switch_id[0]), NO_ERROR))
    return _rect(ctx.item_info(f"**/##logo_{name}", NO_ERROR))


def target_show_in_demo(_: str, ctx: Any) -> Optional[narrator.Rect]:
    """The breadcrumb's button that shows the section in the demo (its labels, as the explorer changed them)"""
    for label in (" Show demo", " Show in the demo", " Demo"):
        rect = _rect(ctx.item_info("**/" + fa.ICON_FA_PLAY + label, NO_ERROR))
        if rect is not None:
            return rect
    return None


def target_crumb(_: str, ctx: Any) -> Optional[narrator.Rect]:
    """The breadcrumb's path (a click opens the outline): the item at the right of "Show in the demo", on its row"""
    window, show = _window("/editor_"), target_show_in_demo("", ctx)
    if window is None or show is None:
        return None
    items = imgui.test_engine.TestItemList()
    ctx.gather_items(items, imgui.test_engine.TestRef(window.id_), -1)
    row = [items.get_by_index(i).rect_full for i in range(items.get_size())]
    row = [r for r in row if abs(r.min.y - show[0].y) < 2 and r.min.x > show[1].x]
    crumb = min(row, key=lambda r: r.min.x, default=None)
    return (crumb.min, crumb.max) if crumb is not None else None


def target_code_word(word: str, ctx: Any) -> Optional[narrator.Rect]:
    """A word of the code on screen (its first occurrence), as the explorer finds it"""
    rect = imgui_explorer.get_imgui_explorer_code_text_rect(word)
    return (rect.min, rect.max) if rect.visible else None


for _name, _resolver in (("code", target_code), ("code_word", target_code_word), ("button", target_button), ("show_in_demo", target_show_in_demo),
                         ("crumb", target_crumb)):
    lesson.target(_name, _resolver)


def gui() -> None:
    lesson.gui(stage=gui_stage)


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "The ImGui Explorer: a video tour"
    params.app_window_params.window_geometry.size = WINDOW_SIZE
    params.app_window_params.resizable = False
    params.ini_disable = True
    params.use_imgui_test_engine = True          # the gestures: the engine's cursor clicks and types
    params.callbacks.show_gui = gui
    imgui_explorer.set_imgui_explorer_libraries([imgui_explorer.ImGuiExplorerLibrary[name] for name in LIBRARIES])
    lesson.video(params, _video_output())
    immapp.run(params, immapp.AddOnsParams(with_markdown=True, with_implot=True, with_implot3d=True))


if __name__ == "__main__":
    main()
