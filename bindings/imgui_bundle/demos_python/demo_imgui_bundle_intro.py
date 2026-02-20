# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
import webbrowser

from imgui_bundle import imgui, imgui_md, hello_imgui
from imgui_bundle import immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


def automation_show_me_immediate_apps():
    engine = hello_imgui.get_imgui_test_engine()
    automation = imgui.test_engine.register_test(
        engine, "Automation", "ShowMeImmediateApps"
    )

    def test_func(ctx):
        tab_imm_apps_name = "//**/Demo Apps"
        tab_intro_name = "//**/Intro"

        ctx.mouse_move(tab_imm_apps_name)
        ctx.mouse_click(0)
        ctx.item_click("//**/demo_docking/View code")
        ctx.item_click("//**/demo_assets_addons/View code")
        ctx.item_click("//**/demo_hello_world/View code")
        ctx.mouse_move("//**/demo_hello_world/Run")
        ctx.mouse_move(tab_intro_name)
        ctx.mouse_click(0)

    automation.test_func = test_func
    return automation


@immapp.static(
    automation_show_me_code=None,
    automation_show_me_immediate_apps=None,
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
            statics.automation_show_me_immediate_apps = (
                automation_show_me_immediate_apps()
            )

        # Set automation speed
        engine_io = imgui.test_engine.get_io(hello_imgui.get_imgui_test_engine())
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.cinematic

        # Optional: show test engine window
        # imgui.test_engine.show_test_engine_windows(hello_imgui.get_imgui_test_engine(), None)

    imgui.new_line()
    imgui_md.render_unindented(
        """
        # Dear ImGui Bundle
        *Easily create ImGui applications in Python and C++. Batteries included!*
        """)

    imgui.new_line()
    imgui.new_line()
    imgui.new_line()
    imgui_md.render_unindented(
        """
Welcome to the interactive manual for *Dear ImGui Bundle*! This manual present lots of examples, together with their code (in C++ and Python).

The "Demo Apps" tab is especially interesting, as it provide sample starter apps from which you can take inspiration. Click on the "View Code" button to view the apps code, and click on "Run" to run them.
"""
    )
    if hello_imgui.get_runner_params().use_imgui_test_engine:
        #imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + hello_imgui.em_size(1.0))
        if imgui.button("Show me##demo_imm_apps"):
            imgui.test_engine.queue_test(
                hello_imgui.get_imgui_test_engine(),
                statics.automation_show_me_immediate_apps,
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
