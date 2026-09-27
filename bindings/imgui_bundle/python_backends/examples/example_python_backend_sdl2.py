"""
Dear ImGui in an SDL2 window, with a pure Python backend.

Add ImGui to your own [SDL2](https://www.libsdl.org) app: you write the event loop, and a Python backend does the
rest. It uses PySDL2; the backend passes the events to ImGui and draws it with PyOpenGL. Shows the ImGui demo, and a
window with markdown and a formula. Needs `pip install imgui-bundle[sdl2,opengl] pysdl2-dll`.

`pysdl2-dll` brings the SDL2 library itself. See [Pure Python
backends](https://imgui-bundle.pages.dev/doc/python/pure-python-backend/). Unlike `immapp.run()`, there is no Hello
ImGui here: no DPI handling, themes or assets. This backend is adapted from
[pyimgui](https://github.com/pyimgui/pyimgui)'s, and is still experimental. All the backends:
[python_backends](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/python_backends).
"""

# ruff: noqa: F403, F405
from imgui_bundle import imgui, rich_md
from imgui_bundle.python_backends.sdl2_backend import SDL2Renderer
import OpenGL.GL as gl  # pip install PyOpenGL
from sdl2 import *  # type: ignore
import ctypes
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""
    text2: str = "Ahh"


app_state = AppState()


def main():
    window, gl_context = impl_pysdl2_init()
    imgui.create_context()
    impl = SDL2Renderer(window)
    md_options = rich_md.MarkdownOptions()
    md_options.with_latex = True  # LaTeX formulas ($...$ and $$...$$)
    rich_md.create_context(md_options)  # the markdown fonts load at the first render

    show_custom_window = True

    running = True
    event = SDL_Event()
    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            impl.process_event(event)
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
            imgui.set_next_window_size((400, 400))
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                rich_md.render(r"""
                # Hello, World
                Here is some *markdown* text, and a formula: $e^{i\pi} + 1 = 0$

                ![](images/world.png)

                ```python
                print("code blocks too")
                ```
                """)

                imgui.text("Example Text")
                if imgui.button("Hello"):
                    print("World")
                _, app_state.text = imgui.input_text_multiline(
                    "Edit", app_state.text, imgui.ImVec2(200, 200)
                )
                _, app_state.text2 = imgui.input_text("Text2", app_state.text2)

                io = imgui.get_io()
                imgui.text(f"""
                Keyboard modifiers:
                    {io.key_ctrl=}
                    {io.key_alt=}
                    {io.key_shift=}
                    {io.key_super=}""")
            imgui.end()

        gl.glClearColor(1.0, 1.0, 1.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        SDL_GL_SwapWindow(window)

    rich_md.destroy_context()
    impl.shutdown()
    SDL_GL_DeleteContext(gl_context)
    SDL_DestroyWindow(window)
    SDL_Quit()


def impl_pysdl2_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/SDL2 example"

    if SDL_Init(SDL_INIT_EVERYTHING) < 0:
        print(
            "Error: SDL could not initialize! SDL Error: "
            + SDL_GetError().decode("utf-8")
        )
        sys.exit(1)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)
    SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, 8)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_SetHint(SDL_HINT_MAC_CTRL_CLICK_EMULATE_RIGHT_CLICK, b"1")
    SDL_SetHint(SDL_HINT_VIDEO_HIGHDPI_DISABLED, b"1")

    window = SDL_CreateWindow(
        window_name.encode("utf-8"),
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        width,
        height,
        SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE,
    )

    if window is None:
        print(
            "Error: Window could not be created! SDL Error: "
            + SDL_GetError().decode("utf-8")
        )
        sys.exit(1)

    gl_context = SDL_GL_CreateContext(window)
    if gl_context is None:
        print(
            "Error: Cannot create OpenGL Context! SDL Error: "
            + SDL_GetError().decode("utf-8")
        )
        sys.exit(1)

    SDL_GL_MakeCurrent(window, gl_context)
    if SDL_GL_SetSwapInterval(1) < 0:
        print(
            "Warning: Unable to set VSync! SDL Error: " + SDL_GetError().decode("utf-8")
        )
        sys.exit(1)

    return window, gl_context


if __name__ == "__main__":
    main()
