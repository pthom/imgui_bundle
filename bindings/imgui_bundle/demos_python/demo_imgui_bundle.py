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

from imgui_bundle import imgui, hello_imgui, immapp, rich_md, ImVec2, ImVec4, em_size, icons_fontawesome_4 as fa
from imgui_bundle.demos_python import demo_imgui_bundle_intro
from imgui_bundle.demos_python import demo_immapp_launcher
from imgui_bundle.demos_python import demo_utils

WELCOME, DEMOS = "Welcome", "Demos"
WELCOME_LABEL = fa.ICON_FA_HOME + "  Welcome"  # the switch of the header (the automations click it)
DEMOS_LABEL = fa.ICON_FA_TH_LARGE + "  Demos"


class Explorer:
    def __init__(self) -> None:
        self.state = WELCOME
        self.launcher = demo_immapp_launcher.Launcher()
        self.nb_demos = sum(len(category.demos) for category in self.launcher.categories)
        self.right_width = 0.0  # of the header's switch, measured on the previous frame

    def gui(self) -> None:
        if imgui.get_frame_count() < 2:  # cf https://github.com/pthom/imgui_bundle/issues/293
            return
        if (self.state == DEMOS and self.launcher.code_view is None and not imgui.is_any_item_active()
                and imgui.is_key_pressed(imgui.Key.escape)):
            self.state = WELCOME
        self.header()
        if self.state == WELCOME:
            self.welcome()
        else:
            self.launcher.gui(with_title=False)

    def header(self) -> None:
        """The title, the sentence of the state, and at the right the switch between the states"""
        top = imgui.get_cursor_pos_y()
        demo_immapp_launcher.big_text("Dear ImGui Bundle", 2.0)
        imgui.same_line()
        imgui.set_cursor_pos_y(top + em_size(0.75))  # the sentence sits on the title's baseline
        if self.state == WELCOME:
            sentence, color = "   Interactive apps in Python and C++, for desktop, web and mobile.", imgui.Col_.text_disabled
        else:
            sentence, color = "   Pick a demo: see it, run it, and read its code.", imgui.Col_.text
        if imgui.calc_text_size(sentence).x + self.right_width + em_size(2) <= imgui.get_content_region_avail().x:
            imgui.text_colored(imgui.get_style_color_vec4(color), sentence)  # only when it does not reach the switch
        imgui.same_line()
        right = imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x - em_size(0.5)
        imgui.set_cursor_pos(ImVec2(right - self.right_width, top + em_size(0.5)))  # centered on the title
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
                self.state = state
            imgui.pop_style_color()
            imgui.same_line()
        imgui.pop_style_var()
        imgui.end_group()
        self.right_width = imgui.get_item_rect_size().x

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
            self.state = DEMOS
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
    explorer = Explorer()
    runner_params.callbacks.show_gui = explorer.gui

    def show_status_bar():
        from imgui_bundle import __version__, __build_number__
        imgui.set_next_item_width(imgui.get_content_region_avail().x / 10)
        _, imgui.get_style().font_scale_main = imgui.slider_float("Font scale", imgui.get_style().font_scale_main, 0.5, 5)
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
    addons.with_node_editor = True
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
