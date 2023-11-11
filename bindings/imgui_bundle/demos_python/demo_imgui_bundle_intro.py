# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import webbrowser

from imgui_bundle import imgui, imgui_md, hello_imgui
from imgui_bundle import immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def automation_show_me_code():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(engine, "Automation", "ShowMeCode")

    def test_open_popup_func(ctx):
        ctx.set_ref("Dear ImGui Bundle")
        ctx.item_open("Code for this demo")
        ctx.sleep(2.5)
        ctx.item_close("Code for this demo")

        tab_logger_name = "//**/Logger"
        tab_intro_name = "//**/Dear ImGui Bundle"

        ctx.mouse_move(tab_logger_name)
        ctx.mouse_click(0)
        ctx.set_ref("Logger")
        ctx.item_open("Code for this demo")
        ctx.item_close("Code for this demo")
        ctx.mouse_move(tab_intro_name)
        ctx.mouse_click(0)

    automation.test_func = test_open_popup_func
    return automation


def automation_show_me_immediate_apps():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(
        engine, "Automation", "ShowMeImmediateApps"
    )

    def test_open_popup_func(ctx):
        tab_imm_apps_name = "//**/Immediate Apps"
        tab_intro_name = "//**/Dear ImGui Bundle"

        ctx.mouse_move(tab_imm_apps_name)
        ctx.mouse_click(0)
        ctx.item_click("//**/demo_docking/View code")
        ctx.item_click("//**/demo_assets_addons/View code")
        ctx.item_click("//**/demo_hello_world/View code")
        ctx.mouse_move("//**/demo_hello_world/Run")
        ctx.mouse_move(tab_intro_name)
        ctx.mouse_click(0)

    automation.test_func = test_open_popup_func
    return automation


def automation_show_me_imgui_test_engine():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(
        engine, "Automation", "ShowMeImGuiTestEngine"
    )

    def test_open_popup_func(ctx):
        tab_imm_apps_name = "//**/Immediate Apps"
        tab_intro_name = "//**/Dear ImGui Bundle"

        ctx.mouse_move(tab_imm_apps_name)
        ctx.mouse_click(0)
        ctx.item_click("//**/demo_testengine/View code")
        ctx.sleep(2.5)
        ctx.mouse_move("//**/demo_testengine/Run")
        ctx.mouse_move(tab_intro_name)
        ctx.mouse_click(0)

    automation.test_func = test_open_popup_func
    return automation


@immapp.static(
    automation_show_me_code=None,
    automation_show_me_immediate_apps=None,
    automation_show_me_imgui_test_engine=None,
    was_automation_inited=False,
)
def demo_gui():
    statics = demo_gui
    #
    # Automations
    #
    # Create automations upon first display
    if hello_imgui.get_runner_params().use_imgui_test_engine:
        if not statics.was_automation_inited:
            statics.was_automation_inited = True
            statics.automation_show_me_code = automation_show_me_code()
            statics.automation_show_me_immediate_apps = (
                automation_show_me_immediate_apps()
            )
            statics.automation_show_me_imgui_test_engine = (
                automation_show_me_imgui_test_engine()
            )

        # Set automation speed
        engine_io = imgui.test_engine.get_io(hello_imgui.get_imgui_test_engine())
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.cinematic

        # Optional: show test engine window
        # imgui.test_engine.show_test_engine_windows(hello_imgui.get_imgui_test_engine(), None)

    imgui_md.render_unindented(
        """
        *Dear ImGui Bundle: easily create ImGui applications in Python and C++. Batteries included!*

        Welcome to the interactive manual for *Dear ImGui Bundle*! This manual present lots of examples, together with their code (in C++ and Python).

        Advices:
        * This interactive manual works best when viewed together with "Dear ImGui Bundle docs"
        """
    )
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
    if imgui.button("Open Dear ImGui Bundle docs"):
        webbrowser.open("https://pthom.github.io/imgui_bundle/")

    imgui_md.render_unindented(
        """
        * Browse through demos in the different tabs: at the top of each tab, there is a collapsible header named "Code for this demo". Click on it to show the source code for the current demo.
    """
    )
    if hello_imgui.get_runner_params().use_imgui_test_engine:
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
        if imgui.button("Show me##demo_code_demo"):
            imgui.test_engine.queue_test(
                hello_imgui.get_imgui_test_engine(), statics.automation_show_me_code
            )

    imgui_md.render_unindented(
        """
        * The "Immediate Apps" tab is especially interesting, as it provides sample starter apps from which you can take inspiration. Click on the "View Code" button to view the app's code, and click on "Run" to run them.
        """
    )
    if hello_imgui.get_runner_params().use_imgui_test_engine:
        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
        if imgui.button("Show me##demo_imm_apps"):
            imgui.test_engine.queue_test(
                hello_imgui.get_imgui_test_engine(),
                statics.automation_show_me_immediate_apps,
            )

    if hello_imgui.get_runner_params().use_imgui_test_engine:
        imgui_md.render_unindented(
            """
            * The automations provided by the "Show me" buttons work thanks to [ImGui Test Engine](https://github.com/ocornut/imgui_test_engine), which is integrated into ImGui Bundle and available via Python and C++.
        """
        )

        imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
        if imgui.button("Show me##demo_test_engine"):
            imgui.test_engine.queue_test(
                hello_imgui.get_imgui_test_engine(),
                automation_show_me_imgui_test_engine(),
            )
        imgui_md.render_unindented(
            "&nbsp;&nbsp;&nbsp;*Note: See [Dear ImGui Test Engine License](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt)*"
        )

    imgui_md.render_unindented(
        """
        * The best way to learn about the numerous ImGui widgets usage is to use the online "ImGui Manual" (once inside the manual, you may want to click the "Python" checkbox).
        """
    )
    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
    if imgui.button("Open ImGui Manual"):
        webbrowser.open(
            "https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html"
        )

    # Navigation buttons
    imgui.separator()
    imgui.dummy(hello_imgui.em_to_vec2(1.0, 6.0))  # Skip 6 lines
    btn_size = hello_imgui.em_to_vec2(0.0, 1.5)
    if hello_imgui.image_button_from_asset("images/badge_view_sources.png", btn_size):
        webbrowser.open("https://github.com/pthom/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset("images/badge_view_docs.png", btn_size):
        webbrowser.open("https://pthom.github.io/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset(
        "images/badge_interactive_manual.png", btn_size
    ):
        webbrowser.open(
            "https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html"
        )

    demo_utils.animate_logo(
        "images/logo_imgui_bundle_512.png",
        1.0,
        ImVec2(0.5, 3.0),
        0.30,
        "https://github.com/pthom/imgui_bundle",
    )


if __name__ == "__main__":
    from imgui_bundle import immapp

    params = immapp.RunnerParams()
    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 800))  # type: ignore
