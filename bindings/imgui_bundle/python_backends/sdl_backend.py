# -*- coding: utf-8 -*-
# ruff: noqa: F403, F405
from __future__ import absolute_import

from imgui_bundle import imgui
from sdl2 import *

from .opengl_backend import ProgrammablePipelineRenderer

import ctypes

from typing import Dict

SdlKey = int


class SDL2Renderer(ProgrammablePipelineRenderer):
    """Basic SDL2 integration implementation."""

    key_map: Dict[SdlKey, imgui.Key]
    modifier_map: Dict[SdlKey, imgui.Key]
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

        def get_clipboard_text() -> str:
            return SDL_GetClipboardText()

        def set_clipboard_text(text: str) -> None:
            SDL_SetClipboardText(ctypes.c_char_p(text.encode()))

        imgui.get_io().get_clipboard_text_fn_ = get_clipboard_text
        imgui.get_io().set_clipboard_text_fn_ = set_clipboard_text

        self._map_keys()

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map
        key_map[SDL_SCANCODE_TAB] = imgui.Key.tab
        key_map[SDL_SCANCODE_LEFT] = imgui.Key.left_arrow
        key_map[SDL_SCANCODE_RIGHT] = imgui.Key.right_arrow
        key_map[SDL_SCANCODE_UP] = imgui.Key.up_arrow
        key_map[SDL_SCANCODE_DOWN] = imgui.Key.down_arrow
        key_map[SDL_SCANCODE_PAGEUP] = imgui.Key.page_up
        key_map[SDL_SCANCODE_PAGEDOWN] = imgui.Key.page_down
        key_map[SDL_SCANCODE_HOME] = imgui.Key.home
        key_map[SDL_SCANCODE_END] = imgui.Key.end
        key_map[SDL_SCANCODE_INSERT] = imgui.Key.insert
        key_map[SDL_SCANCODE_DELETE] = imgui.Key.delete
        key_map[SDL_SCANCODE_BACKSPACE] = imgui.Key.backspace
        key_map[SDL_SCANCODE_SPACE] = imgui.Key.space
        key_map[SDL_SCANCODE_RETURN] = imgui.Key.enter
        key_map[SDL_SCANCODE_ESCAPE] = imgui.Key.escape
        key_map[SDL_SCANCODE_KP_ENTER] = imgui.Key.keypad_enter
        key_map[SDL_SCANCODE_A] = imgui.Key.a
        key_map[SDL_SCANCODE_C] = imgui.Key.c
        key_map[SDL_SCANCODE_V] = imgui.Key.v
        key_map[SDL_SCANCODE_X] = imgui.Key.x
        key_map[SDL_SCANCODE_Y] = imgui.Key.y
        key_map[SDL_SCANCODE_Z] = imgui.Key.z

        self.modifier_map = {}
        self.modifier_map[SDL_SCANCODE_LCTRL] = imgui.Key.im_gui_mod_ctrl
        self.modifier_map[SDL_SCANCODE_RCTRL] = imgui.Key.im_gui_mod_ctrl
        self.modifier_map[SDL_SCANCODE_LSHIFT] = imgui.Key.im_gui_mod_shift
        self.modifier_map[SDL_SCANCODE_RSHIFT] = imgui.Key.im_gui_mod_shift
        self.modifier_map[SDL_SCANCODE_LALT] = imgui.Key.im_gui_mod_alt
        self.modifier_map[SDL_SCANCODE_RALT] = imgui.Key.im_gui_mod_alt
        self.modifier_map[SDL_SCANCODE_LGUI] = imgui.Key.im_gui_mod_super
        self.modifier_map[SDL_SCANCODE_RGUI] = imgui.Key.im_gui_mod_super

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

            if sdl_key in self.modifier_map:
                imgui_key = self.modifier_map[sdl_key]
                io.add_key_event(imgui_key, event.type == SDL_KEYDOWN)

            return True

        if event.type == SDL_TEXTINPUT:
            for char in event.text.text.decode("utf-8"):
                io.add_input_character(ord(char))
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


