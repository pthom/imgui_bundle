# -*- coding: utf-8 -*-
from __future__ import absolute_import

from imgui_bundle import imgui
import glfw  # type: ignore

from imgui_bundle.python_backends import compute_fb_scale
from .opengl_backend import ProgrammablePipelineRenderer

from typing import Dict

GlfwKey = int


class GlfwRenderer(ProgrammablePipelineRenderer):
    key_map: Dict[GlfwKey, imgui.Key]
    modifier_map: Dict[GlfwKey, imgui.Key]

    def __init__(self, window, attach_callbacks: bool = True):
        super(GlfwRenderer, self).__init__()
        self.window = window

        if attach_callbacks:
            glfw.set_key_callback(self.window, self.keyboard_callback)
            glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
            glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
            glfw.set_window_size_callback(self.window, self.resize_callback)
            glfw.set_char_callback(self.window, self.char_callback)
            glfw.set_scroll_callback(self.window, self.scroll_callback)

        self.io.display_size = glfw.get_framebuffer_size(self.window)

        def get_clipboard_text() -> str:
            return glfw.get_clipboard_string(self.window)

        def set_clipboard_text(text: str) -> None:
            glfw.set_clipboard_string(self.window, text)

        imgui.get_io().get_clipboard_text_fn_ = get_clipboard_text
        imgui.get_io().set_clipboard_text_fn_ = set_clipboard_text

        self._map_keys()
        self._gui_time = None

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map
        key_map[glfw.KEY_LEFT] = imgui.Key.left_arrow
        key_map[glfw.KEY_RIGHT] = imgui.Key.right_arrow

        key_map[glfw.KEY_LEFT_CONTROL] = imgui.Key.left_ctrl
        key_map[glfw.KEY_RIGHT_CONTROL] = imgui.Key.right_ctrl
        key_map[glfw.KEY_LEFT_SHIFT] = imgui.Key.left_shift
        key_map[glfw.KEY_RIGHT_SHIFT] = imgui.Key.right_shift
        key_map[glfw.KEY_LEFT_ALT] = imgui.Key.left_alt
        key_map[glfw.KEY_RIGHT_ALT] = imgui.Key.right_alt
        key_map[glfw.KEY_LEFT_SUPER] = imgui.Key.left_super
        key_map[glfw.KEY_RIGHT_SUPER] = imgui.Key.right_super

        key_map[glfw.KEY_TAB] = imgui.Key.tab
        key_map[glfw.KEY_LEFT] = imgui.Key.left_arrow
        key_map[glfw.KEY_RIGHT] = imgui.Key.right_arrow
        key_map[glfw.KEY_UP] = imgui.Key.up_arrow
        key_map[glfw.KEY_DOWN] = imgui.Key.down_arrow
        key_map[glfw.KEY_PAGE_UP] = imgui.Key.page_up
        key_map[glfw.KEY_PAGE_DOWN] = imgui.Key.page_down
        key_map[glfw.KEY_HOME] = imgui.Key.home
        key_map[glfw.KEY_END] = imgui.Key.end
        key_map[glfw.KEY_INSERT] = imgui.Key.insert
        key_map[glfw.KEY_DELETE] = imgui.Key.delete
        key_map[glfw.KEY_BACKSPACE] = imgui.Key.backspace
        key_map[glfw.KEY_SPACE] = imgui.Key.space
        key_map[glfw.KEY_ENTER] = imgui.Key.enter
        key_map[glfw.KEY_ESCAPE] = imgui.Key.escape
        key_map[glfw.KEY_KP_ENTER] = imgui.Key.keypad_enter
        key_map[glfw.KEY_A] = imgui.Key.a
        key_map[glfw.KEY_C] = imgui.Key.c
        key_map[glfw.KEY_V] = imgui.Key.v
        key_map[glfw.KEY_X] = imgui.Key.x
        key_map[glfw.KEY_Y] = imgui.Key.y
        key_map[glfw.KEY_Z] = imgui.Key.z

        self.modifier_map = {}
        self.modifier_map[glfw.KEY_LEFT_CONTROL] = imgui.Key.im_gui_mod_ctrl
        self.modifier_map[glfw.KEY_RIGHT_CONTROL] = imgui.Key.im_gui_mod_ctrl
        self.modifier_map[glfw.KEY_LEFT_SHIFT] = imgui.Key.im_gui_mod_shift
        self.modifier_map[glfw.KEY_RIGHT_SHIFT] = imgui.Key.im_gui_mod_shift
        self.modifier_map[glfw.KEY_LEFT_ALT] = imgui.Key.im_gui_mod_alt
        self.modifier_map[glfw.KEY_RIGHT_ALT] = imgui.Key.im_gui_mod_alt
        self.modifier_map[glfw.KEY_LEFT_SUPER] = imgui.Key.im_gui_mod_super
        self.modifier_map[glfw.KEY_RIGHT_SUPER] = imgui.Key.im_gui_mod_super

    def keyboard_callback(self, window, glfw_key: int, scancode, action, mods):
        # perf: local for faster access
        io = self.io

        if glfw_key not in self.key_map:
            return
        imgui_key = self.key_map[glfw_key]

        down = action != glfw.RELEASE
        io.add_key_event(imgui_key, down)

        if glfw_key in self.modifier_map:
            imgui_key = self.modifier_map[glfw_key]
            io.add_key_event(imgui_key, down)

    def char_callback(self, window, char):
        io = imgui.get_io()

        if 0 < char < 0x10000:
            io.add_input_character(char)

    def resize_callback(self, window, width, height):
        self.io.display_size = width, height

    def mouse_callback(self, *args, **kwargs):
        if glfw.get_window_attrib(self.window, glfw.FOCUSED):
            mouse_pos = glfw.get_cursor_pos(self.window)
            self.io.add_mouse_pos_event(mouse_pos[0], mouse_pos[1])
        else:
            self.io.add_mouse_pos_event(-1, -1)

    def mouse_button_callback(self, window, button, action, mods):
        self.io.add_mouse_button_event(button, action == glfw.PRESS)

    def scroll_callback(self, window, x_offset, y_offset):
        self.io.add_mouse_wheel_event(x_offset, y_offset)

    def process_inputs(self):
        io = imgui.get_io()

        window_size = glfw.get_window_size(self.window)
        fb_size = glfw.get_framebuffer_size(self.window)

        io.display_size = window_size
        io.display_framebuffer_scale = compute_fb_scale(window_size, fb_size)
        io.delta_time = 1.0 / 60

        current_time = glfw.get_time()

        if self._gui_time:
            self.io.delta_time = current_time - self._gui_time
        else:
            self.io.delta_time = 1.0 / 60.0
        if io.delta_time <= 0.0:
            io.delta_time = 1.0 / 1000.0

        self._gui_time = current_time
