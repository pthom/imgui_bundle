# An example of using Dear ImGui with Glfw using a *full python* backend.
# This mode is inspired from [pyimgui](https://github.com/pyimgui/pyimgui) backends, and is still experimental.
#
# See full python backends implementations here:
# https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends

from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
import OpenGL.GL as gl  # type: ignore
from imgui_bundle import imgui, imgui_ctx
import glfw  # type: ignore
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""


app_state = AppState()


def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    show_custom_window = True

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

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
            imgui.set_next_window_size((400, 400))
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
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
