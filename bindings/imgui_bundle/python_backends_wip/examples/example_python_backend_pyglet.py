#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from imgui_bundle import imgui
from imgui_bundle.python_backends_wip import pyglet_backend

from pyglet import gl  # type: ignore
import pyglet  # type: ignore
import sys


class AppState:
    text: str = """Hello, World\nLorem ipsum, etc.\netc."""
    text2: str = "Ahh"


app_state = AppState()


def main():
    window = pyglet.window.Window(width=1280, height=720, resizable=True)
    gl.glClearColor(1, 1, 1, 1)
    imgui.create_context()
    impl = pyglet_backend.create_renderer(window)

    global show_custom_window
    show_custom_window = True

    def update(dt):
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

        global show_custom_window
        if show_custom_window:
            imgui.set_next_window_size((400, 400))
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                imgui.text("Example Text")
                if imgui.button("Hello"):
                    print("World")
                _, app_state.text = imgui.input_text_multiline("Edit", app_state.text, imgui.ImVec2(200, 200))
                _, app_state.text2 = imgui.input_text("Text2", app_state.text2)
            imgui.end()

    def draw(dt):
        update(dt)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.clock.schedule_interval(draw, 1 / 120.0)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()
