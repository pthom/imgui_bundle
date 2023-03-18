# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import webbrowser

from imgui_bundle import imgui, imgui_md, hello_imgui
from imgui_bundle.demos_python.demo_utils.api_demos import show_markdown_file
from imgui_bundle import immapp, ImVec2
from imgui_bundle.demos_python import demo_utils  # this will set the assets folder


class AppState:
    counter = 0
    name = ""


@immapp.static(value=0)
def demo_radio_button():
    static = demo_radio_button
    clicked, static.value = imgui.radio_button("radio a", static.value, 0)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio b", static.value, 1)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio c", static.value, 2)


@immapp.static(text="")
def demo_input_text_upper_case() -> None:
    static = demo_input_text_upper_case
    flags: imgui.InputTextFlags = (
        imgui.InputTextFlags_.chars_uppercase.value | imgui.InputTextFlags_.chars_no_blank.value
    )
    changed, static.text = imgui.input_text("Upper case, no spaces", static.text, flags)


def demo_add_window_size_callback():
    import imgui_bundle

    # always import glfw *after* imgui_bundle!!!
    import glfw  # type: ignore

    # Get the glfw window used by hello imgui
    window = imgui_bundle.glfw_utils.glfw_window_hello_imgui()

    # define a callback
    def my_window_size_callback(window: glfw._GLFWwindow, w: int, h: int):
        from imgui_bundle import hello_imgui

        hello_imgui.log(hello_imgui.LogLevel.info, f"Window size changed to {w}x{h}")

    glfw.set_window_size_callback(window, my_window_size_callback)


@immapp.static(snippet=None)
def show_glfw_callback_advice():
    static = show_glfw_callback_advice
    if static.snippet is None:
        import inspect

        static.snippet = immapp.snippets.SnippetData()
        static.snippet.code = inspect.getsource(demo_add_window_size_callback)

    imgui.text("Code for this demo")
    immapp.snippets.show_code_snippet(static.snippet)

    imgui_md.render_unindented(
        """For more complex applications, you can set various callbacks, using glfw.
    *Click the button below to add a callback*"""
    )

    if imgui.button("Add glfw callback"):
        demo_add_window_size_callback()
        hello_imgui.log(
            hello_imgui.LogLevel.warning,
            "A callback was handed to watch the window size. Change this window size and look at the logs",
        )

    hello_imgui.log_gui()


def show_porting_advices() -> None:
    show_markdown_file("ibd_port_general_advices")
    demo_radio_button()

    imgui.new_line()
    imgui.new_line()
    imgui.new_line()

    show_markdown_file("ibd_port_enums")
    demo_input_text_upper_case()

    imgui.new_line()
    imgui.new_line()
    imgui.new_line()
    show_markdown_file("ibd_port_debug_native")


def gui_front_matter():
    imgui_md.render_unindented(
        """
    # Dear ImGui Bundle
    Easily create ImGui applications in Python and C++. Batteries included!
    """
    )
    btnSize = hello_imgui.em_to_vec2(0.0, 1.5)
    if hello_imgui.image_button_from_asset("images/badge_view_sources.png", btnSize):
        webbrowser.open("https://github.com/pthom/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset("images/badge_view_docs.png", btnSize):
        webbrowser.open("https://pthom.github.io/imgui_bundle")
    imgui.same_line()
    if hello_imgui.image_button_from_asset("images/badge_interactive_manual.png", btnSize):
        webbrowser.open("https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html")


@immapp.static(is_initialized=False)
def demo_gui() -> None:
    static = demo_gui

    if not static.is_initialized:
        static.app_state = AppState()
        static.is_initialized = True

    app_state: AppState = static.app_state

    gui_front_matter()
    imgui_md.render_unindented('(*Note: this documentation is also available as a web page: click on "View Docs"*)')

    if imgui.collapsing_header("Introduction"):
        show_markdown_file("ibd_intro")
    if imgui.collapsing_header("Repository folders structure"):
        show_markdown_file("ibd_folders_structure")
    if imgui.collapsing_header("Build and install instruction"):
        show_markdown_file("ibd_install")

    if imgui.collapsing_header("Dear ImGui - Immediate gui"):

        def immediate_gui_example():
            # Display a text
            imgui.text(f"Counter = {app_state.counter}")
            imgui.same_line()  # by default ImGui starts a new line at each widget

            # The following line displays a button
            if imgui.button("increment counter"):
                # And returns true if it was clicked: you can *immediately* handle the click
                app_state.counter += 1

            # Input a text: in python, input_text returns a tuple(modified, new_value)
            changed, app_state.name = imgui.input_text("Your name?", app_state.name)
            imgui.text(f"Hello {app_state.name}!")

        show_markdown_file("ibd_manual_imgui")
        immediate_gui_example()
        imgui.separator()

    if imgui.collapsing_header("Hello ImGui - Starter pack"):
        show_markdown_file("ibd_manual_himgui")

    if imgui.collapsing_header("ImmApp - Immediate App"):
        show_markdown_file("ibd_manual_immapp")

    if imgui.collapsing_header("Using Dear ImGui Bundle with jupyter notebook"):
        show_markdown_file("ibd_manual_notebook")

    if imgui.collapsing_header("C++ / Python porting advices"):
        show_porting_advices()

    if imgui.collapsing_header("Advanced glfw callbacks"):
        show_glfw_callback_advice()

    if imgui.collapsing_header("Closing words"):
        show_markdown_file("ibd_words_author")

    if imgui.collapsing_header("FAQ"):
        show_markdown_file("ibd_faq")

    demo_utils.animate_logo(
        "images/logo_imgui_bundle_512.png", 1.0, ImVec2(0.5, 3.0), 0.30, "https://github.com/pthom/imgui_bundle"
    )


if __name__ == "__main__":
    from imgui_bundle import immapp

    params = immapp.RunnerParams()
    immapp.run(demo_gui, with_markdown=True, window_size=(1000, 800))  # type: ignore
