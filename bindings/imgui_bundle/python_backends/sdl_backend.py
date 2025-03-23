# -*- coding: utf-8 -*-
# ruff: noqa: F403, F405
from __future__ import absolute_import
from typing import Any

from imgui_bundle import imgui
from sdl2 import *

from .opengl_backend_programmable import ProgrammablePipelineRenderer

import ctypes

from typing import Dict

SdlKey = int


class SDL2Renderer(ProgrammablePipelineRenderer):
    """Basic SDL2 integration implementation."""

    key_map: Dict[SdlKey, imgui.Key]
    MOUSE_WHEEL_OFFSET_SCALE = 0.5

    def __init__(self, window):
        super(SDL2Renderer, self).__init__()
        self.window = window

        self._mouse_wheel = 0.0
        self._gui_time = None

        width_ptr = ctypes.pointer(ctypes.c_int(0))
        height_ptr = ctypes.pointer(ctypes.c_int(0))
        SDL_GetWindowSize(self.window, width_ptr, height_ptr)

        self.io.display_size = width_ptr[0], height_ptr[0]

        def get_clipboard_text(_imgui_context: Any) -> str:
            r: ctypes.c_char_p = SDL_GetClipboardText()
            return r.decode() if r else ""

        def set_clipboard_text(_imgui_context: Any, text: str) -> None:
            SDL_SetClipboardText(ctypes.c_char_p(text.encode()))

        imgui.get_platform_io().platform_get_clipboard_text_fn = get_clipboard_text
        imgui.get_platform_io().platform_set_clipboard_text_fn = set_clipboard_text

        self._map_keys()

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map
        key_map[SDL_SCANCODE_KP_ENTER] = imgui.Key.keypad_enter


    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map

        # Control Keys
        key_map[SDL_SCANCODE_TAB] = imgui.Key.tab
        key_map[SDL_SCANCODE_BACKSPACE] = imgui.Key.backspace
        key_map[SDL_SCANCODE_RETURN] = imgui.Key.enter
        key_map[SDL_SCANCODE_ESCAPE] = imgui.Key.escape
        key_map[SDL_SCANCODE_INSERT] = imgui.Key.insert
        key_map[SDL_SCANCODE_DELETE] = imgui.Key.delete
        key_map[SDL_SCANCODE_SPACE] = imgui.Key.space

        # Function Keys
        key_map[SDL_SCANCODE_F1] = imgui.Key.f1
        key_map[SDL_SCANCODE_F2] = imgui.Key.f2
        key_map[SDL_SCANCODE_F3] = imgui.Key.f3
        key_map[SDL_SCANCODE_F4] = imgui.Key.f4
        key_map[SDL_SCANCODE_F5] = imgui.Key.f5
        key_map[SDL_SCANCODE_F6] = imgui.Key.f6
        key_map[SDL_SCANCODE_F7] = imgui.Key.f7
        key_map[SDL_SCANCODE_F8] = imgui.Key.f8
        key_map[SDL_SCANCODE_F9] = imgui.Key.f9
        key_map[SDL_SCANCODE_F10] = imgui.Key.f10
        key_map[SDL_SCANCODE_F11] = imgui.Key.f11
        key_map[SDL_SCANCODE_F12] = imgui.Key.f12

        # Navigation Keys
        key_map[SDL_SCANCODE_LEFT] = imgui.Key.left_arrow
        key_map[SDL_SCANCODE_RIGHT] = imgui.Key.right_arrow
        key_map[SDL_SCANCODE_UP] = imgui.Key.up_arrow
        key_map[SDL_SCANCODE_DOWN] = imgui.Key.down_arrow
        key_map[SDL_SCANCODE_PAGEUP] = imgui.Key.page_up
        key_map[SDL_SCANCODE_PAGEDOWN] = imgui.Key.page_down
        key_map[SDL_SCANCODE_HOME] = imgui.Key.home
        key_map[SDL_SCANCODE_END] = imgui.Key.end

        # Numeric Keys
        key_map[SDL_SCANCODE_0] = imgui.Key._0
        key_map[SDL_SCANCODE_1] = imgui.Key._1
        key_map[SDL_SCANCODE_2] = imgui.Key._2
        key_map[SDL_SCANCODE_3] = imgui.Key._3
        key_map[SDL_SCANCODE_4] = imgui.Key._4
        key_map[SDL_SCANCODE_5] = imgui.Key._5
        key_map[SDL_SCANCODE_6] = imgui.Key._6
        key_map[SDL_SCANCODE_7] = imgui.Key._7
        key_map[SDL_SCANCODE_8] = imgui.Key._8
        key_map[SDL_SCANCODE_9] = imgui.Key._9

        # Keypad Keys
        key_map[SDL_SCANCODE_KP_ENTER] = imgui.Key.keypad_enter
        key_map[SDL_SCANCODE_KP_0] = imgui.Key.keypad0
        key_map[SDL_SCANCODE_KP_1] = imgui.Key.keypad1
        key_map[SDL_SCANCODE_KP_2] = imgui.Key.keypad2
        key_map[SDL_SCANCODE_KP_3] = imgui.Key.keypad3
        key_map[SDL_SCANCODE_KP_4] = imgui.Key.keypad4
        key_map[SDL_SCANCODE_KP_5] = imgui.Key.keypad5
        key_map[SDL_SCANCODE_KP_6] = imgui.Key.keypad6
        key_map[SDL_SCANCODE_KP_7] = imgui.Key.keypad7
        key_map[SDL_SCANCODE_KP_8] = imgui.Key.keypad8
        key_map[SDL_SCANCODE_KP_9] = imgui.Key.keypad9
        key_map[SDL_SCANCODE_KP_DECIMAL] = imgui.Key.keypad_decimal
        key_map[SDL_SCANCODE_KP_DIVIDE] = imgui.Key.keypad_divide
        key_map[SDL_SCANCODE_KP_MULTIPLY] = imgui.Key.keypad_multiply
        key_map[SDL_SCANCODE_KP_MINUS] = imgui.Key.keypad_subtract
        key_map[SDL_SCANCODE_KP_PLUS] = imgui.Key.keypad_add
        key_map[SDL_SCANCODE_KP_EQUALS] = imgui.Key.keypad_equal

        # Alphabetic Keys
        key_map[SDL_SCANCODE_A] = imgui.Key.a
        key_map[SDL_SCANCODE_B] = imgui.Key.b
        key_map[SDL_SCANCODE_C] = imgui.Key.c
        key_map[SDL_SCANCODE_D] = imgui.Key.d
        key_map[SDL_SCANCODE_E] = imgui.Key.e
        key_map[SDL_SCANCODE_F] = imgui.Key.f
        key_map[SDL_SCANCODE_G] = imgui.Key.g
        key_map[SDL_SCANCODE_H] = imgui.Key.h
        key_map[SDL_SCANCODE_I] = imgui.Key.i
        key_map[SDL_SCANCODE_J] = imgui.Key.j
        key_map[SDL_SCANCODE_K] = imgui.Key.k
        key_map[SDL_SCANCODE_L] = imgui.Key.l
        key_map[SDL_SCANCODE_M] = imgui.Key.m
        key_map[SDL_SCANCODE_N] = imgui.Key.n
        key_map[SDL_SCANCODE_O] = imgui.Key.o
        key_map[SDL_SCANCODE_P] = imgui.Key.p
        key_map[SDL_SCANCODE_Q] = imgui.Key.q
        key_map[SDL_SCANCODE_R] = imgui.Key.r
        key_map[SDL_SCANCODE_S] = imgui.Key.s
        key_map[SDL_SCANCODE_T] = imgui.Key.t
        key_map[SDL_SCANCODE_U] = imgui.Key.u
        key_map[SDL_SCANCODE_V] = imgui.Key.v
        key_map[SDL_SCANCODE_W] = imgui.Key.w
        key_map[SDL_SCANCODE_X] = imgui.Key.x
        key_map[SDL_SCANCODE_Y] = imgui.Key.y
        key_map[SDL_SCANCODE_Z] = imgui.Key.z

        # Modifier Keys
        key_map[SDL_SCANCODE_LCTRL] = imgui.Key.left_ctrl
        key_map[SDL_SCANCODE_RCTRL] = imgui.Key.right_ctrl
        key_map[SDL_SCANCODE_LSHIFT] = imgui.Key.left_shift
        key_map[SDL_SCANCODE_RSHIFT] = imgui.Key.right_shift
        key_map[SDL_SCANCODE_LALT] = imgui.Key.left_alt
        key_map[SDL_SCANCODE_RALT] = imgui.Key.right_alt
        key_map[SDL_SCANCODE_LGUI] = imgui.Key.left_super
        key_map[SDL_SCANCODE_RGUI] = imgui.Key.right_super

        # Media Keys
        key_map[SDL_SCANCODE_AUDIONEXT] = imgui.Key.app_forward
        key_map[SDL_SCANCODE_AUDIOPREV] = imgui.Key.app_back
        # key_map[SDL_SCANCODE_AUDIOSTOP] = imgui.Key.none
        # key_map[SDL_SCANCODE_AUDIOPLAY] = imgui.Key.none
        # key_map[SDL_SCANCODE_AUDIOMUTE] = imgui.Key.none

        # Application Keys
        key_map[SDL_SCANCODE_APPLICATION] = imgui.Key.menu

        # Lock Keys
        key_map[SDL_SCANCODE_CAPSLOCK] = imgui.Key.caps_lock
        key_map[SDL_SCANCODE_SCROLLLOCK] = imgui.Key.scroll_lock
        key_map[SDL_SCANCODE_NUMLOCKCLEAR] = imgui.Key.num_lock

        # Symbol Keys
        key_map[SDL_SCANCODE_GRAVE] = imgui.Key.grave_accent  # `
        key_map[SDL_SCANCODE_MINUS] = imgui.Key.minus         # -
        key_map[SDL_SCANCODE_EQUALS] = imgui.Key.equal       # =
        key_map[SDL_SCANCODE_LEFTBRACKET] = imgui.Key.left_bracket  # [
        key_map[SDL_SCANCODE_RIGHTBRACKET] = imgui.Key.right_bracket  # ]
        key_map[SDL_SCANCODE_BACKSLASH] = imgui.Key.backslash  # \
        key_map[SDL_SCANCODE_SEMICOLON] = imgui.Key.semicolon  # ;
        key_map[SDL_SCANCODE_APOSTROPHE] = imgui.Key.apostrophe  # '
        key_map[SDL_SCANCODE_COMMA] = imgui.Key.comma  # ,
        key_map[SDL_SCANCODE_PERIOD] = imgui.Key.period  # .
        key_map[SDL_SCANCODE_SLASH] = imgui.Key.slash  # /

        # Miscellaneous Keys
        key_map[SDL_SCANCODE_PRINTSCREEN] = imgui.Key.print_screen
        key_map[SDL_SCANCODE_PAUSE] = imgui.Key.pause

    def process_event(self, event):
        io = self.io

        if event.type == SDL_MOUSEMOTION:
            if SDL_GetWindowFlags(self.window) & SDL_WINDOW_MOUSE_FOCUS:
                io.mouse_pos = -1, -1
            io.mouse_pos = event.motion.x, event.motion.y
            return True

        if event.type == SDL_MOUSEWHEEL:
            io.add_mouse_wheel_event(
                event.wheel.x * self.MOUSE_WHEEL_OFFSET_SCALE, event.wheel.y * self.MOUSE_WHEEL_OFFSET_SCALE)
            return True

        if event.type == SDL_MOUSEBUTTONDOWN or event.type == SDL_MOUSEBUTTONUP:
            imgui_button = 0
            if event.button.button == SDL_BUTTON_LEFT:
                imgui_button = 0
            elif event.button.button == SDL_BUTTON_RIGHT:
                imgui_button = 1
            elif event.button.button == SDL_BUTTON_MIDDLE:
                imgui_button = 2

            down = event.type == SDL_MOUSEBUTTONDOWN
            io.add_mouse_button_event(imgui_button, down)
            return True

        if event.type == SDL_KEYUP or event.type == SDL_KEYDOWN:
            sdl_key = event.key.keysym.scancode
            if sdl_key in self.key_map:
                imgui_key = self.key_map[sdl_key]
                down = event.type == SDL_KEYDOWN
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

            return True

        if event.type == SDL_TEXTINPUT:
            for char in event.text.text.decode("utf-8"):
                io.add_input_character(ord(char))
            return True

        if event.type == SDL_CONTROLLERBUTTONDOWN or event.type == SDL_CONTROLLERBUTTONUP:
            button = event.cbutton.button
            is_pressed = event.type == SDL_CONTROLLERBUTTONDOWN

            # Map SDL_CONTROLLER_BUTTON_* to imgui keys
            if button == SDL_CONTROLLER_BUTTON_A:
                imgui.get_io().add_key_event(imgui.Key.gamepad_face_down, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_B:
                imgui.get_io().add_key_event(imgui.Key.gamepad_face_right, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_X:
                imgui.get_io().add_key_event(imgui.Key.gamepad_face_left, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_Y:
                imgui.get_io().add_key_event(imgui.Key.gamepad_face_up, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_DPAD_UP:
                imgui.get_io().add_key_event(imgui.Key.gamepad_dpad_up, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                imgui.get_io().add_key_event(imgui.Key.gamepad_dpad_down, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                imgui.get_io().add_key_event(imgui.Key.gamepad_dpad_left, is_pressed)
            elif button == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                imgui.get_io().add_key_event(imgui.Key.gamepad_dpad_right, is_pressed)
            return True

    def process_inputs(self):
        io = imgui.get_io()

        s_w = ctypes.pointer(ctypes.c_int(0))
        s_h = ctypes.pointer(ctypes.c_int(0))
        SDL_GetWindowSize(self.window, s_w, s_h)
        w = s_w.contents.value
        h = s_h.contents.value

        io.display_size = w, h
        io.display_framebuffer_scale = (1, 1)

        current_time = SDL_GetTicks() / 1000.0

        if self._gui_time:
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1.0 / 60.0
        if io.delta_time <= 0.0:
            io.delta_time = 1.0 / 1000.0
        self._gui_time = current_time


