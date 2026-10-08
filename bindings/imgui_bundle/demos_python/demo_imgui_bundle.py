# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
"""
Dear ImGui Bundle Explorer: one page with a header, and two states below it.

Welcome: the intro (the carousel of live mini demos) and a button to the demos. Demos: the launcher (the catalog of
demos, with their pictures, descriptions and code). Escape goes back one state (the code view, then Welcome).
"""
import importlib.util
import sys
if importlib.util.find_spec("numpy") is None:
    print(
        "Dear ImGui Bundle Explorer requires numpy!\n"
        "Please install it with:\n"
        "    pip install numpy\n"
        "or\n"
        "    uv pip install numpy",
        file=sys.stderr,
    )
    sys.exit(1)

from typing import Literal, Optional

from imgui_bundle import imgui, hello_imgui, immapp, rich_md, ImVec2, ImVec4, em_size, icons_fontawesome_4 as fa
from imgui_bundle.demos_python import demo_imgui_bundle_intro
from imgui_bundle.demos_python import demo_immapp_launcher
from imgui_bundle.demos_python import demo_utils

WELCOME, DEMOS = "Welcome", "Demos"
CHANGE_DURATION = 0.4  # s: a change of state, through the background
DRIFT = 3.0  # em: the page leaving slides that much (up when going forward), the one arriving comes from as far
WELCOME_LABEL = fa.ICON_FA_HOME + "  Welcome"  # the switch of the header (the intro's automations click it)
DEMOS_LABEL = fa.ICON_FA_TH_LARGE + "  Demos"
# em: below this width, the status bar's content goes to a "..." menu in the header (in the bar, the app's part and
# hello_imgui's idling and FPS, at a fixed place from the right, would overlap)
STATUS_IN_MENU_BELOW = 60.0
_EXPLORER: Optional["Explorer"] = None  # the page, once the app is set up (the intro's automations drive it)


def status_in_menu() -> bool:
    return imgui.get_io().display_size.x < em_size(STATUS_IN_MENU_BELOW)


def is_touch_screen() -> bool:
    return bool(imgui.get_io().config_flags & imgui.ConfigFlags_.is_touch_screen)


def symbol_button(label: str, symbol: Literal["-", "+", "..."], size: ImVec2) -> bool:
    """A button with its symbol drawn at its center (the icon font's minus and ellipsis sit off center)"""
    clicked = imgui.button(label, size)
    mi, ma = imgui.get_item_rect_min(), imgui.get_item_rect_max()
    c = ImVec2((mi.x + ma.x) * 0.5, (mi.y + ma.y) * 0.5)
    em = imgui.get_font_size()
    h, t = em * 0.35, em * 0.09  # the half length and the half thickness of a stroke
    col = imgui.get_color_u32(imgui.Col_.text)
    draw_list = imgui.get_window_draw_list()
    if symbol == "...":
        for i in (-1, 0, 1):
            draw_list.add_circle_filled(ImVec2(c.x + i * em * 0.3, c.y), em * 0.1, col)
        return clicked
    draw_list.add_rect_filled(ImVec2(c.x - h, c.y - t), ImVec2(c.x + h, c.y + t), col)
    if symbol == "+":
        draw_list.add_rect_filled(ImVec2(c.x - t, c.y - h), ImVec2(c.x + t, c.y + h), col)
    return clicked


def zoom_buttons(button_height: float) -> None:
    """The zoom: two buttons, and the pinch on a touch screen. No slider where the finger is: it would move under the
    finger as the scale changes"""
    style = imgui.get_style()
    size = ImVec2(em_size(2), button_height)
    imgui.align_text_to_frame_padding()
    imgui.text("Zoom")
    imgui.same_line()
    if symbol_button("##zoom_out", "-", size):
        style.font_scale_main = min(max(style.font_scale_main / 1.1, 0.5), 5.0)
    imgui.same_line()
    if symbol_button("##zoom_in", "+", size):
        style.font_scale_main = min(max(style.font_scale_main * 1.1, 0.5), 5.0)
    if is_touch_screen():
        imgui.same_line()
        imgui.text("or pinch with two fingers")


def status_menu() -> None:
    """The "..." button of a narrow screen (as tall as the header's chips), and its menu: the status bar's content"""
    from imgui_bundle import __version__, __build_number__
    if symbol_button("##status_menu", "...", ImVec2(em_size(2), imgui.get_font_size())):
        imgui.open_popup("##status_menu_popup")
    if not imgui.begin_popup("##status_menu_popup"):
        return
    imgui.text_disabled("Dear ImGui Bundle Explorer")
    imgui.text_disabled(f"v{__version__} build {__build_number__}")
    zoom_buttons(em_size(1.5))
    fps_idling = hello_imgui.get_runner_params().fps_idling
    _, fps_idling.enable_idling = imgui.checkbox("Enable idling", fps_idling.enable_idling)
    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}{' (Idling)' if fps_idling.is_idling else ''}")
    imgui.end_popup()


class Explorer:
    def __init__(self) -> None:
        self.state = WELCOME  # the one wanted
        self.shown = WELCOME  # the one drawn: the previous state, during the first half of a change
        self.change_start: Optional[float] = None  # the time when the state last changed, while the change animates
        self.forward = True  # the change goes from Welcome to Demos (the pages slide up), or back (down)
        self.launcher = demo_immapp_launcher.Launcher()
        self.nb_demos = sum(len(category.demos) for category in self.launcher.categories)
        self.right_width = 0.0  # of the header's switch, measured on the previous frame

    def gui(self) -> None:
        if imgui.get_frame_count() < 2:  # cf https://github.com/pthom/imgui_bundle/issues/293
            return
        if (self.state == DEMOS and self.launcher.depth == 0 and not imgui.is_any_item_active()
                and imgui.is_key_pressed(imgui.Key.escape)):  # else the launcher goes back one level itself
            self.go(WELCOME)
        hello_imgui.get_runner_params().imgui_window_params.show_status_bar = not status_in_menu()
        self.header()
        self.page()

    def go(self, state: str) -> None:
        if state == self.state:
            return
        self.state = state
        self.forward = state == DEMOS
        self.change_start = imgui.get_time()

    def page(self) -> None:
        """The state's content, in a child; during a change, it fades through the background with a drift: the
        page leaving slides away under a veil, then the new one slides into place as the veil lifts"""
        drift, veil = 0.0, 0.0
        if self.change_start is not None:
            t = (imgui.get_time() - self.change_start) / CHANGE_DURATION
            if t >= 1.0:
                self.change_start = None
                self.shown = self.state
            elif t < 0.5:
                u = t / 0.5
                u = u * u  # eased in
                drift, veil = -DRIFT * u, u
            else:
                if self.shown != self.state:
                    self.shown = self.state
                    if self.shown == DEMOS:
                        self.launcher.deal()
                u = (t - 0.5) / 0.5
                u = 1.0 - (1.0 - u) * (1.0 - u)  # eased out
                drift, veil = DRIFT * (1.0 - u), 1.0 - u
            if not self.forward:
                drift = -drift
        drift = em_size(drift)
        top_left = imgui.get_cursor_screen_pos()
        avail = imgui.get_content_region_avail()
        bottom_right = ImVec2(top_left.x + avail.x, top_left.y + avail.y)
        # The page keeps its size while it drifts: a demo shown in place would otherwise see its size change during the
        # transition (a node editor adapts its view to its size, and would lose its fit). A frame without scrollbar
        # holds the page, and clips it.
        frame_flags = imgui.WindowFlags_.no_scrollbar | imgui.WindowFlags_.no_scroll_with_mouse
        imgui.begin_child("page frame", avail, 0, frame_flags)
        imgui.set_cursor_pos(ImVec2(0.0, drift))
        imgui.begin_child("page", avail)
        if self.shown == WELCOME:
            self.welcome()
        else:
            self.launcher.gui(with_title=False)
        imgui.end_child()
        imgui.end_child()
        if veil > 0.0:  # over the child's own draw list, which comes after this window's
            imgui.get_foreground_draw_list().add_rect_filled(top_left, bottom_right, demo_immapp_launcher.curtain(veil))

    def header(self) -> None:
        """The title, the sentence of the state, and at the right the switch between the states (on its own row when
        the title leaves it no room: a phone)"""
        top = imgui.get_cursor_pos_y()
        demo_immapp_launcher.big_text("Dear ImGui Bundle", 2.0)
        title_width = imgui.get_item_rect_size().x
        below_title = imgui.get_cursor_pos_y()
        width = imgui.get_content_region_avail().x
        right = imgui.get_cursor_pos_x() + width - em_size(0.5)
        one_row = title_width + self.right_width + em_size(1.5) <= width
        if one_row:
            if self.state == WELCOME:
                sentence, color = "   Interactive apps in Python and C++, for desktop, web and mobile.", imgui.Col_.text_disabled
            else:
                sentence = "   Pick a demo: see it, run it, and read its code: each demo is a documented quickstart."
                color = imgui.Col_.text
            # Only when it does not reach the switch; same_line only then: pending, it would make the title's row
            # the chips' line
            if title_width + imgui.calc_text_size(sentence).x + self.right_width + em_size(3) <= width:
                imgui.same_line()
                imgui.set_cursor_pos_y(top + em_size(0.75))  # the sentence sits on the title's baseline
                imgui.text_colored(imgui.get_style_color_vec4(color), sentence)
        # The cursor is set, not put on the same line (see above)
        imgui.set_cursor_pos(ImVec2(right - self.right_width, top + em_size(0.5) if one_row else below_title))
        imgui.begin_group()
        # The switch: two chips as the launcher's category chips (wider, and never wrapped: the group's width comes
        # from the previous frame, and a wrapped group would measure too narrow forever), the state's in the accent
        imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(em_size(0.8), 0))
        for state, label in ((WELCOME, WELCOME_LABEL), (DEMOS, DEMOS_LABEL)):
            highlight = demo_immapp_launcher.tween(f"switch {state}", 1.0 if state == self.state else 0.0, 0.25)
            button = imgui.get_style_color_vec4(imgui.Col_.button)
            accent = demo_immapp_launcher.ACCENT
            imgui.push_style_color(imgui.Col_.button,
                                   demo_immapp_launcher.lerp(button, ImVec4(accent.x, accent.y, accent.z, 0.55), highlight))
            if imgui.small_button(label):
                self.go(state)
            imgui.pop_style_color()
            imgui.same_line()
        imgui.pop_style_var()
        if status_in_menu():
            status_menu()
        imgui.end_group()
        self.right_width = imgui.get_item_rect_size().x
        imgui.set_cursor_pos_y(max(imgui.get_cursor_pos_y(), below_title))  # the chips are shorter than the title

    def welcome(self) -> None:
        demo_imgui_bundle_intro.links_row()
        avail = imgui.get_content_region_avail()
        imgui.begin_child("welcome", ImVec2(0, avail.y - em_size(3.5)))
        demo_imgui_bundle_intro.welcome_gui()
        imgui.end_child()
        # The call to action, centered
        label = f"{fa.ICON_FA_TH_LARGE}  Browse the {self.nb_demos} demos"
        imgui.push_font(None, imgui.get_style().font_size_base * 1.3)
        imgui.push_style_var(imgui.StyleVar_.frame_padding, ImVec2(em_size(1.2), em_size(0.4)))
        width = imgui.calc_text_size(label).x + em_size(2.4)
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail.x - width) / 2)
        if imgui.button(label):
            self.go(DEMOS)
        imgui.pop_style_var()
        imgui.pop_font()
        if imgui.is_item_hovered(imgui.HoveredFlags_.delay_normal):
            categories = ", ".join(category.name for category in self.launcher.categories)
            imgui.begin_tooltip()
            imgui.begin_child("tip", ImVec2(em_size(30), 0), imgui.ChildFlags_.auto_resize_y.value)  # wraps the text
            rich_md.render(f"**{self.nb_demos} demos, in {len(self.launcher.categories)} categories:** {categories}.\n\n"
                           "Each one is a documented quickstart: see it, run it, and read its code. Together they are "
                           "the tutorials and the interactive manuals of the bundle.")
            imgui.end_child()
            imgui.end_tooltip()


def make_params() -> tuple[hello_imgui.RunnerParams, immapp.AddOnsParams]:
    print(
        f"For information, demos sources are available in {demo_utils.api_demos.demos_python_folder()}"
    )

    ################################################################################################
    # Part 1: Define the runner params
    ################################################################################################

    # Hello ImGui params (they hold the settings as well as the Gui callbacks)
    runner_params = hello_imgui.RunnerParams()
    # Window size and title
    runner_params.app_window_params.window_title = (
        "Dear ImGui Bundle Explorer"
    )
    runner_params.app_window_params.window_geometry.size = (1400, 950)

    runner_params.imgui_window_params.show_status_bar = True

    runner_params.ini_clear_previous_settings = True

    ################################################################################################
    # Part 2: The explorer's page, in a full screen window
    ################################################################################################
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window
    )
    global _EXPLORER
    explorer = _EXPLORER = Explorer()
    runner_params.callbacks.show_gui = explorer.gui

    def show_status_bar():
        from imgui_bundle import __version__, __build_number__
        if is_touch_screen():
            zoom_buttons(imgui.get_frame_height())
        else:
            imgui.set_next_item_width(imgui.get_content_region_avail().x / 10)
            _, imgui.get_style().font_scale_main = imgui.slider_float(
                "Font scale", imgui.get_style().font_scale_main, 0.5, 5)
        imgui.same_line(spacing=hello_imgui.em_size(4))
        imgui.text_disabled(f"Dear ImGui Bundle Explorer - v{__version__} build {__build_number__}")

    runner_params.callbacks.show_status = show_status_bar

    if "test_engine" in dir(imgui):  # only enable test engine if available (i.e. if imgui bundle was compiled with it)
        runner_params.use_imgui_test_engine = True

    def setup_imgui_config() -> None:
        imgui.get_io().config_flags |= imgui.ConfigFlags_.nav_enable_keyboard.value

    runner_params.callbacks.setup_imgui_config = setup_imgui_config


    ################################################################################################
    # Part 3: Run the app
    ################################################################################################
    addons = immapp.AddOnsParams()
    addons.with_markdown = True
    addons.with_latex = True
    addons.with_implot = True
    addons.with_implot3d = True
    addons.with_im_anim = True

    return runner_params, addons


def main():
    from imgui_bundle import __version__, __build_number__, compilation_time
    print(f"Dear ImGui Bundle Explorer - v{__version__} build {__build_number__}, {compilation_time()}")
    runner_params, addons = make_params()
    immapp.run(runner_params=runner_params, add_ons_params=addons)


if __name__ == "__main__":
    main()
