#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from imgui_bundle import imgui
from imgui_bundle.python_backends.python_backends_disabled.pygame_backend import (
    PygameRenderer,
)
import OpenGL.GL as gl  # type: ignore
import pygame  # type: ignore
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""
    text2: str = "Ahh"


app_state = AppState()


def main():
    pygame.init()
    size = 800, 600

    pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size

    show_custom_window = True

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            impl.process_event(event)
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
                _, app_state.text2 = imgui.input_text("Text2", app_state.text2)

                io = imgui.get_io()
                imgui.text(f"""
                Keyboard modifiers:
                    {io.key_ctrl=}
                    {io.key_alt=}
                    {io.key_shift=}
                    {io.key_super=}""")
            imgui.end()

        # note: cannot use screen.fill((1, 1, 1)) because pygame's screen
        #       does not support fill() on OpenGL sufraces
        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()


if __name__ == "__main__":
    main()
