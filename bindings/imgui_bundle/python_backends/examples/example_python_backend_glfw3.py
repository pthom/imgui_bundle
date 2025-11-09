# An example of using Dear ImGui with Glfw using a *full python* backend.
# This mode is inspired from [pyimgui](https://github.com/pyimgui/pyimgui) backends, and is still experimental.
#
# These examples also demonstrate how to use the markdown rendering feature of ImGui Bundle.
#
# See full python backends implementations here:
# https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends


# Workaround issue when using wayland ("Attempt to retrieve context when no valid context", in PyOpenGL)
# (see https://github.com/pthom/imgui_bundle/issues/321)
import os
if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
    os.environ["PYOPENGL_PLATFORM"] = "x11"


import OpenGL.GL as gl  # pip install PyOpenGL
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
# When using a pure python backend, prefer to import glfw before imgui_bundle (so that you end up using the standard glfw, not the one provided by imgui_bundle)
import glfw  # type: ignore
from imgui_bundle import imgui, imgui_ctx
from imgui_bundle import imgui_md
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""


app_state = AppState()


def init_fonts_and_markdown():
    # uncomment to keep using the default hardcoded font, or load your default font here
    # imgui.get_io().fonts.add_font_default()

    # Load markdown fonts
    imgui_md.initialize_markdown()
    font_loader = imgui_md.get_font_loader_function()
    font_loader()


def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)
    init_fonts_and_markdown()

    show_custom_window = True
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        imgui.show_demo_window()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", "Cmd+Q", False, True
                )

                if clicked_quit:
                    sys.exit(0)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        if show_custom_window:
            imgui.set_next_window_size((400, 600))

            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                imgui_md.render_unindented("""
                # Hello, World
                Here is some *markdown* text.
                """)

                imgui.text("Example Text")
                if imgui.button("Hello"):
                    print("World")
                _, app_state.text = imgui.input_text_multiline(
                    "Edit", app_state.text, imgui.ImVec2(200, 200)
                )
                io = imgui.get_io()
                imgui.text(f"""
                Keyboard modifiers:
                    {io.key_ctrl=}
                    {io.key_alt=}
                    {io.key_shift=}
                    {io.key_super=}""")

                if imgui.button("Open popup"):
                    imgui.open_popup("my popup")
                with imgui_ctx.begin_popup_modal("my popup") as popup:
                    if popup.visible:
                        imgui.text("Hello from popup!")
                        if imgui.button("Close popup"):
                            imgui.close_current_popup()

            imgui.end()

        gl.glClearColor(1.0, 1.0, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


if __name__ == "__main__":
    main()
