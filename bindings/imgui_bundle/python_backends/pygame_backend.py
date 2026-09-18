from __future__ import absolute_import

from imgui_bundle import imgui

from imgui_bundle.python_backends.opengl_backend_programmable import ProgrammablePipelineRenderer

from typing import Dict

import pygame
import pygame.event
import pygame.scrap
import pygame.time
import time

PygameKey = int


class PygameRenderer(ProgrammablePipelineRenderer):
    key_map: Dict[PygameKey, imgui.Key]
    modifier_map: Dict[PygameKey, imgui.Key]

    def __init__(self):
        super(PygameRenderer, self).__init__()

        self._gui_time = None
        self._map_keys()
        self._init_clipboard()

    def _init_clipboard(self):
        """Connect imgui to the system clipboard, via pygame.scrap (which needs an existing display surface)"""
        try:
            pygame.scrap.init()
        except pygame.error:
            return  # no display surface yet: imgui keeps its own in-app clipboard

        # The accepted text type depends on the platform: macOS only accepts the utf-8 one, pygame's SCRAP_TEXT fails there.
        text_types = ["text/plain;charset=utf-8", pygame.SCRAP_TEXT]
        in_app_clipboard = {"text": ""}  # used when the system clipboard refuses the text

        def get_clipboard_text(_ctx: imgui.internal.Context) -> str:
            for text_type in text_types:
                data = pygame.scrap.get(text_type)
                if data:
                    return data.decode("utf-8", errors="ignore").rstrip("\x00")
            return in_app_clipboard["text"]

        def set_clipboard_text(_ctx: imgui.internal.Context, text: str) -> None:
            in_app_clipboard["text"] = text
            for text_type in text_types:
                try:
                    pygame.scrap.put(text_type, text.encode("utf-8"))
                    return
                except pygame.error:
                    pass

        imgui.get_platform_io().platform_get_clipboard_text_fn = get_clipboard_text
        imgui.get_platform_io().platform_set_clipboard_text_fn = set_clipboard_text

    def _map_keys(self):
        self.key_map = {
            pygame.K_LEFT: imgui.Key.left_arrow,
            pygame.K_RIGHT: imgui.Key.right_arrow,
            pygame.K_UP: imgui.Key.up_arrow,
            pygame.K_DOWN: imgui.Key.down_arrow,
            pygame.K_PAGEUP: imgui.Key.page_up,
            pygame.K_PAGEDOWN: imgui.Key.page_down,
            pygame.K_HOME: imgui.Key.home,
            pygame.K_END: imgui.Key.end,
            pygame.K_INSERT: imgui.Key.insert,
            pygame.K_DELETE: imgui.Key.delete,
            pygame.K_BACKSPACE: imgui.Key.backspace,
            pygame.K_RETURN: imgui.Key.enter,
            pygame.K_ESCAPE: imgui.Key.escape,
            pygame.K_KP_ENTER: imgui.Key.keypad_enter,
            pygame.K_TAB: imgui.Key.tab,

            pygame.K_LCTRL: imgui.Key.left_ctrl,
            pygame.K_RCTRL: imgui.Key.right_ctrl,
            pygame.K_LALT: imgui.Key.left_alt,
            pygame.K_RALT: imgui.Key.right_alt,
            pygame.K_RSHIFT: imgui.Key.right_shift,
            pygame.K_LSHIFT: imgui.Key.left_shift,
            pygame.K_LSUPER: imgui.Key.left_super,
            pygame.K_RSUPER: imgui.Key.right_super,

            # letters used by imgui's shortcuts: select all, copy, paste, cut, redo, undo
            pygame.K_a: imgui.Key.a,
            pygame.K_c: imgui.Key.c,
            pygame.K_v: imgui.Key.v,
            pygame.K_x: imgui.Key.x,
            pygame.K_y: imgui.Key.y,
            pygame.K_z: imgui.Key.z,
        }

        self.modifier_map = {
            pygame.K_LCTRL: imgui.Key.mod_ctrl,
            pygame.K_RCTRL: imgui.Key.mod_ctrl,
            pygame.K_LSHIFT: imgui.Key.mod_shift,
            pygame.K_RSHIFT: imgui.Key.mod_shift,
            pygame.K_LALT: imgui.Key.mod_alt,
            pygame.K_RALT: imgui.Key.mod_alt,
            pygame.K_LSUPER: imgui.Key.mod_super,
            pygame.K_RSUPER: imgui.Key.mod_super,
        }

        self.mouse_map = {
            2: imgui.MouseButton_.middle,
            3: imgui.MouseButton_.right
        }

    def process_event(self, event):
        # perf: local for faster access
        io = self.io

        if event.type == pygame.MOUSEMOTION:
            io.add_mouse_pos_event(event.pos[0], event.pos[1])
            return True

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            down = event.type == pygame.MOUSEBUTTONDOWN
            imgui_button = self.mouse_map.get(event.button, event.button - 1)
            io.add_mouse_button_event(imgui_button, down)
            return True

        if event.type == pygame.MOUSEWHEEL:
            k = 0.5
            io.add_mouse_wheel_event(event.x * k, event.y * k)
            return True

        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            is_down = event.type == pygame.KEYDOWN
            if event.key in self.key_map.keys():
                io.add_key_event(self.key_map[event.key], down=is_down)
            if event.key in self.modifier_map.keys():
                io.add_key_event(self.modifier_map[event.key], down=is_down)

        if event.type == pygame.KEYDOWN:
            # Text input: a key can be both a key event (e.g. C, for Ctrl+C) and a character.
            # Control characters (enter, tab, backspace, escape, delete...) are key events only.
            for char in event.unicode:
                code = ord(char)
                if 32 <= code < 0x10000 and code != 127:
                    io.add_input_character(code)

            return True

        if event.type == pygame.VIDEORESIZE:
            surface = pygame.display.get_surface()
            # note: pygame does not modify existing surface upon resize,
            #       we need to do it ourselves.
            pygame.display.set_mode(
                (event.w, event.h),
                flags=surface.get_flags(),
            )
            # existing font texure is no longer valid, so we need to refresh it
            self._update_textures()

            # notify imgui about new window size
            io.display_size = event.size

            # delete old surface, it is no longer needed
            del surface

            return True

    def process_inputs(self):
        io = imgui.get_io()

        # Note: pygame.time.get_ticks() has a resolution of 1 ms. At high frame rates (no vsync) most frames would get
        # a null delta: imgui's clock would then run faster than the wall clock, and double clicks would be missed.
        current_time = time.perf_counter()

        if self._gui_time:
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1.0 / 60.0
        if io.delta_time <= 0.0:
            io.delta_time = 1e-6
        self._gui_time = current_time
