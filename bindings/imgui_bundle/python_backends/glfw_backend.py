# -*- coding: utf-8 -*-
from __future__ import absolute_import

from imgui_bundle import imgui
import glfw  # pip install glfw

from imgui_bundle.python_backends import compute_fb_scale
from .opengl_backend_programmable import ProgrammablePipelineRenderer

from typing import Dict

GlfwKey = int


class GlfwRenderer(ProgrammablePipelineRenderer):
    key_map: Dict[GlfwKey, imgui.Key]

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

        def get_clipboard_text(_ctx: imgui.internal.Context) -> str:
            s = glfw.get_clipboard_string(self.window)
            return s.decode()

        def set_clipboard_text(_ctx: imgui.internal.Context, text: str) -> None:
            glfw.set_clipboard_string(self.window, text)

        imgui.get_platform_io().platform_get_clipboard_text_fn = get_clipboard_text
        imgui.get_platform_io().platform_set_clipboard_text_fn = set_clipboard_text

        self._map_keys()
        self._gui_time = None

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map

        # Control Keys
        key_map[glfw.KEY_TAB] = imgui.Key.tab
        key_map[glfw.KEY_BACKSPACE] = imgui.Key.backspace
        key_map[glfw.KEY_ENTER] = imgui.Key.enter
        key_map[glfw.KEY_ESCAPE] = imgui.Key.escape
        key_map[glfw.KEY_INSERT] = imgui.Key.insert
        key_map[glfw.KEY_DELETE] = imgui.Key.delete
        key_map[glfw.KEY_SPACE] = imgui.Key.space

        # Function Keys
        key_map[glfw.KEY_F1] = imgui.Key.f1
        key_map[glfw.KEY_F2] = imgui.Key.f2
        key_map[glfw.KEY_F3] = imgui.Key.f3
        key_map[glfw.KEY_F4] = imgui.Key.f4
        key_map[glfw.KEY_F5] = imgui.Key.f5
        key_map[glfw.KEY_F6] = imgui.Key.f6
        key_map[glfw.KEY_F7] = imgui.Key.f7
        key_map[glfw.KEY_F8] = imgui.Key.f8
        key_map[glfw.KEY_F9] = imgui.Key.f9
        key_map[glfw.KEY_F10] = imgui.Key.f10
        key_map[glfw.KEY_F11] = imgui.Key.f11
        key_map[glfw.KEY_F12] = imgui.Key.f12

        # Navigation Keys
        key_map[glfw.KEY_LEFT] = imgui.Key.left_arrow
        key_map[glfw.KEY_RIGHT] = imgui.Key.right_arrow
        key_map[glfw.KEY_UP] = imgui.Key.up_arrow
        key_map[glfw.KEY_DOWN] = imgui.Key.down_arrow
        key_map[glfw.KEY_PAGE_UP] = imgui.Key.page_up
        key_map[glfw.KEY_PAGE_DOWN] = imgui.Key.page_down
        key_map[glfw.KEY_HOME] = imgui.Key.home
        key_map[glfw.KEY_END] = imgui.Key.end

        # Numeric Keys
        key_map[glfw.KEY_0] = imgui.Key._0
        key_map[glfw.KEY_1] = imgui.Key._1
        key_map[glfw.KEY_2] = imgui.Key._2
        key_map[glfw.KEY_3] = imgui.Key._3
        key_map[glfw.KEY_4] = imgui.Key._4
        key_map[glfw.KEY_5] = imgui.Key._5
        key_map[glfw.KEY_6] = imgui.Key._6
        key_map[glfw.KEY_7] = imgui.Key._7
        key_map[glfw.KEY_8] = imgui.Key._8
        key_map[glfw.KEY_9] = imgui.Key._9

        # Keypad Keys
        key_map[glfw.KEY_KP_ENTER] = imgui.Key.keypad_enter
        key_map[glfw.KEY_KP_0] = imgui.Key.keypad0
        key_map[glfw.KEY_KP_1] = imgui.Key.keypad1
        key_map[glfw.KEY_KP_2] = imgui.Key.keypad2
        key_map[glfw.KEY_KP_3] = imgui.Key.keypad3
        key_map[glfw.KEY_KP_4] = imgui.Key.keypad4
        key_map[glfw.KEY_KP_5] = imgui.Key.keypad5
        key_map[glfw.KEY_KP_6] = imgui.Key.keypad6
        key_map[glfw.KEY_KP_7] = imgui.Key.keypad7
        key_map[glfw.KEY_KP_8] = imgui.Key.keypad8
        key_map[glfw.KEY_KP_9] = imgui.Key.keypad9
        key_map[glfw.KEY_KP_DECIMAL] = imgui.Key.keypad_decimal
        key_map[glfw.KEY_KP_DIVIDE] = imgui.Key.keypad_divide
        key_map[glfw.KEY_KP_MULTIPLY] = imgui.Key.keypad_multiply
        key_map[glfw.KEY_KP_SUBTRACT] = imgui.Key.keypad_subtract
        key_map[glfw.KEY_KP_ADD] = imgui.Key.keypad_add
        key_map[glfw.KEY_KP_EQUAL] = imgui.Key.keypad_equal

        # Alphabetic Keys
        key_map[glfw.KEY_A] = imgui.Key.a
        key_map[glfw.KEY_B] = imgui.Key.b
        key_map[glfw.KEY_C] = imgui.Key.c
        key_map[glfw.KEY_D] = imgui.Key.d
        key_map[glfw.KEY_E] = imgui.Key.e
        key_map[glfw.KEY_F] = imgui.Key.f
        key_map[glfw.KEY_G] = imgui.Key.g
        key_map[glfw.KEY_H] = imgui.Key.h
        key_map[glfw.KEY_I] = imgui.Key.i
        key_map[glfw.KEY_J] = imgui.Key.j
        key_map[glfw.KEY_K] = imgui.Key.k
        key_map[glfw.KEY_L] = imgui.Key.l
        key_map[glfw.KEY_M] = imgui.Key.m
        key_map[glfw.KEY_N] = imgui.Key.n
        key_map[glfw.KEY_O] = imgui.Key.o
        key_map[glfw.KEY_P] = imgui.Key.p
        key_map[glfw.KEY_Q] = imgui.Key.q
        key_map[glfw.KEY_R] = imgui.Key.r
        key_map[glfw.KEY_S] = imgui.Key.s
        key_map[glfw.KEY_T] = imgui.Key.t
        key_map[glfw.KEY_U] = imgui.Key.u
        key_map[glfw.KEY_V] = imgui.Key.v
        key_map[glfw.KEY_W] = imgui.Key.w
        key_map[glfw.KEY_X] = imgui.Key.x
        key_map[glfw.KEY_Y] = imgui.Key.y
        key_map[glfw.KEY_Z] = imgui.Key.z

        # Modifier Keys
        key_map[glfw.KEY_LEFT_CONTROL] = imgui.Key.left_ctrl
        key_map[glfw.KEY_RIGHT_CONTROL] = imgui.Key.right_ctrl
        key_map[glfw.KEY_LEFT_SHIFT] = imgui.Key.left_shift
        key_map[glfw.KEY_RIGHT_SHIFT] = imgui.Key.right_shift
        key_map[glfw.KEY_LEFT_ALT] = imgui.Key.left_alt
        key_map[glfw.KEY_RIGHT_ALT] = imgui.Key.right_alt
        key_map[glfw.KEY_LEFT_SUPER] = imgui.Key.left_super
        key_map[glfw.KEY_RIGHT_SUPER] = imgui.Key.right_super

        # Symbol Keys
        key_map[glfw.KEY_APOSTROPHE] = imgui.Key.apostrophe  # '
        key_map[glfw.KEY_COMMA] = imgui.Key.comma  # ,
        key_map[glfw.KEY_MINUS] = imgui.Key.minus  # -
        key_map[glfw.KEY_PERIOD] = imgui.Key.period  # .
        key_map[glfw.KEY_SLASH] = imgui.Key.slash  # /
        key_map[glfw.KEY_SEMICOLON] = imgui.Key.semicolon  # ;
        key_map[glfw.KEY_EQUAL] = imgui.Key.equal  # =
        key_map[glfw.KEY_LEFT_BRACKET] = imgui.Key.left_bracket  # [
        key_map[glfw.KEY_BACKSLASH] = imgui.Key.backslash  # \
        key_map[glfw.KEY_RIGHT_BRACKET] = imgui.Key.right_bracket  # ]
        key_map[glfw.KEY_GRAVE_ACCENT] = imgui.Key.grave_accent  # `

        # Lock Keys
        key_map[glfw.KEY_CAPS_LOCK] = imgui.Key.caps_lock
        key_map[glfw.KEY_SCROLL_LOCK] = imgui.Key.scroll_lock
        key_map[glfw.KEY_NUM_LOCK] = imgui.Key.num_lock

        # Miscellaneous Keys
        key_map[glfw.KEY_PRINT_SCREEN] = imgui.Key.print_screen
        key_map[glfw.KEY_PAUSE] = imgui.Key.pause

        # Application Keys
        key_map[glfw.KEY_MENU] = imgui.Key.menu

    def keyboard_callback(self, window, glfw_key: int, scancode, action, mods):
        # perf: local for faster access
        io = self.io
        if glfw_key not in self.key_map:
            return
        imgui_key = self.key_map[glfw_key]
        down = action != glfw.RELEASE
        io.add_key_event(imgui_key, down)

        # Handle modifiers, since ImGui has an additional mod_ctrl / shift / etc
        if imgui_key == imgui.Key.left_ctrl or imgui_key == imgui.Key.right_ctrl:
            io.add_key_event(imgui.Key.mod_ctrl, down)
        if imgui_key == imgui.Key.left_shift or imgui_key == imgui.Key.right_shift:
            io.add_key_event(imgui.Key.mod_shift, down)
        if imgui_key == imgui.Key.left_alt or imgui_key == imgui.Key.right_alt:
            io.add_key_event(imgui.Key.mod_alt, down)
        if imgui_key == imgui.Key.left_super or imgui_key == imgui.Key.right_super:
            io.add_key_event(imgui.Key.mod_super, down)

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
