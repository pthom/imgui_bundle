# -*- coding: utf-8 -*-
from __future__ import absolute_import
import warnings

from imgui_bundle import imgui

from pyglet.window import key, mouse, Window
import pyglet
import pyglet.clock


from imgui_bundle.python_backends import compute_fb_scale
from imgui_bundle.python_backends.opengl_backend_programmable import ProgrammablePipelineRenderer


class PygletMixin(object):
    _gui_time = None

    MOUSE_CURSORS = {
        imgui.MouseCursor_.arrow.value: Window.CURSOR_DEFAULT,
        imgui.MouseCursor_.text_input.value: Window.CURSOR_TEXT,
        imgui.MouseCursor_.resize_all.value: Window.CURSOR_SIZE,
        imgui.MouseCursor_.resize_ns.value: Window.CURSOR_SIZE_UP_DOWN,
        imgui.MouseCursor_.resize_ew.value: Window.CURSOR_SIZE_LEFT_RIGHT,
        imgui.MouseCursor_.resize_nesw.value: Window.CURSOR_SIZE_DOWN_LEFT,
        imgui.MouseCursor_.resize_nwse.value: Window.CURSOR_SIZE_DOWN_RIGHT,
        imgui.MouseCursor_.hand.value: Window.CURSOR_HAND,
    }

    def __init__(self):
        super(PygletMixin, self).__init__()
        self._cursor = -2
        self._window = None
        # Let Dear imgui know we have mouse cursor support
        self.io = imgui.get_io()
        self.io.backend_flags |= imgui.BackendFlags_.has_mouse_cursors
        self._map_keys()

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map

        # Control Keys
        key_map[key.TAB] = imgui.Key.tab
        key_map[key.BACKSPACE] = imgui.Key.backspace
        key_map[key.RETURN] = imgui.Key.enter
        key_map[key.ESCAPE] = imgui.Key.escape
        key_map[key.INSERT] = imgui.Key.insert
        key_map[key.DELETE] = imgui.Key.delete
        key_map[key.SPACE] = imgui.Key.space

        # Function Keys
        key_map[key.F1] = imgui.Key.f1
        key_map[key.F2] = imgui.Key.f2
        key_map[key.F3] = imgui.Key.f3
        key_map[key.F4] = imgui.Key.f4
        key_map[key.F5] = imgui.Key.f5
        key_map[key.F6] = imgui.Key.f6
        key_map[key.F7] = imgui.Key.f7
        key_map[key.F8] = imgui.Key.f8
        key_map[key.F9] = imgui.Key.f9
        key_map[key.F10] = imgui.Key.f10
        key_map[key.F11] = imgui.Key.f11
        key_map[key.F12] = imgui.Key.f12

        # Navigation Keys
        key_map[key.LEFT] = imgui.Key.left_arrow
        key_map[key.RIGHT] = imgui.Key.right_arrow
        key_map[key.UP] = imgui.Key.up_arrow
        key_map[key.DOWN] = imgui.Key.down_arrow
        key_map[key.PAGEUP] = imgui.Key.page_up
        key_map[key.PAGEDOWN] = imgui.Key.page_down
        key_map[key.HOME] = imgui.Key.home
        key_map[key.END] = imgui.Key.end

        # Numeric Keys
        key_map[key._0] = imgui.Key._0
        key_map[key._1] = imgui.Key._1
        key_map[key._2] = imgui.Key._2
        key_map[key._3] = imgui.Key._3
        key_map[key._4] = imgui.Key._4
        key_map[key._5] = imgui.Key._5
        key_map[key._6] = imgui.Key._6
        key_map[key._7] = imgui.Key._7
        key_map[key._8] = imgui.Key._8
        key_map[key._9] = imgui.Key._9

        # Keypad Keys
        key_map[key.NUM_ENTER] = imgui.Key.keypad_enter
        key_map[key.NUM_0] = imgui.Key.keypad0
        key_map[key.NUM_1] = imgui.Key.keypad1
        key_map[key.NUM_2] = imgui.Key.keypad2
        key_map[key.NUM_3] = imgui.Key.keypad3
        key_map[key.NUM_4] = imgui.Key.keypad4
        key_map[key.NUM_5] = imgui.Key.keypad5
        key_map[key.NUM_6] = imgui.Key.keypad6
        key_map[key.NUM_7] = imgui.Key.keypad7
        key_map[key.NUM_8] = imgui.Key.keypad8
        key_map[key.NUM_9] = imgui.Key.keypad9
        key_map[key.NUM_DECIMAL] = imgui.Key.keypad_decimal
        key_map[key.NUM_DIVIDE] = imgui.Key.keypad_divide
        key_map[key.NUM_MULTIPLY] = imgui.Key.keypad_multiply
        key_map[key.NUM_SUBTRACT] = imgui.Key.keypad_subtract
        key_map[key.NUM_ADD] = imgui.Key.keypad_add

        # Alphabetic Keys
        key_map[key.A] = imgui.Key.a
        key_map[key.B] = imgui.Key.b
        key_map[key.C] = imgui.Key.c
        key_map[key.D] = imgui.Key.d
        key_map[key.E] = imgui.Key.e
        key_map[key.F] = imgui.Key.f
        key_map[key.G] = imgui.Key.g
        key_map[key.H] = imgui.Key.h
        key_map[key.I] = imgui.Key.i
        key_map[key.J] = imgui.Key.j
        key_map[key.K] = imgui.Key.k
        key_map[key.L] = imgui.Key.l
        key_map[key.M] = imgui.Key.m
        key_map[key.N] = imgui.Key.n
        key_map[key.O] = imgui.Key.o
        key_map[key.P] = imgui.Key.p
        key_map[key.Q] = imgui.Key.q
        key_map[key.R] = imgui.Key.r
        key_map[key.S] = imgui.Key.s
        key_map[key.T] = imgui.Key.t
        key_map[key.U] = imgui.Key.u
        key_map[key.V] = imgui.Key.v
        key_map[key.W] = imgui.Key.w
        key_map[key.X] = imgui.Key.x
        key_map[key.Y] = imgui.Key.y
        key_map[key.Z] = imgui.Key.z

        # Modifier Keys
        key_map[key.LCTRL] = imgui.Key.left_ctrl
        key_map[key.RCTRL] = imgui.Key.right_ctrl
        key_map[key.LSHIFT] = imgui.Key.left_shift
        key_map[key.RSHIFT] = imgui.Key.right_shift
        key_map[key.LALT] = imgui.Key.left_alt
        key_map[key.RALT] = imgui.Key.right_alt
        key_map[key.LCOMMAND] = imgui.Key.left_super
        key_map[key.RCOMMAND] = imgui.Key.right_super

        # Symbol Keys
        key_map[key.GRAVE] = imgui.Key.grave_accent  # `
        key_map[key.MINUS] = imgui.Key.minus         # -
        key_map[key.EQUAL] = imgui.Key.equal         # =
        key_map[key.BRACKETLEFT] = imgui.Key.left_bracket  # [
        key_map[key.BRACKETRIGHT] = imgui.Key.right_bracket  # ]
        key_map[key.BACKSLASH] = imgui.Key.backslash  # \
        key_map[key.SEMICOLON] = imgui.Key.semicolon  # ;
        key_map[key.APOSTROPHE] = imgui.Key.apostrophe  # '
        key_map[key.COMMA] = imgui.Key.comma  # ,
        key_map[key.PERIOD] = imgui.Key.period  # .
        key_map[key.SLASH] = imgui.Key.slash  # /

        # Miscellaneous Keys
        key_map[key.PRINT] = imgui.Key.print_screen
        key_map[key.PAUSE] = imgui.Key.pause

        # Lock Keys
        key_map[key.CAPSLOCK] = imgui.Key.caps_lock
        key_map[key.NUMLOCK] = imgui.Key.num_lock
        key_map[key.SCROLLLOCK] = imgui.Key.scroll_lock

    def _set_pixel_ratio(self, window):
        window_size = window.get_size()
        self.io.display_size = window_size
        # It is conceivable that the pyglet version will not be solely
        # determinant of whether we use the fixed or programmable, so do some
        # minor introspection here to check.
        if hasattr(window, "get_viewport_size"):
            viewport_size = window.get_viewport_size()
            self.io.display_framebuffer_scale = compute_fb_scale(
                window_size, viewport_size
            )
        elif hasattr(window, "get_pixel_ratio"):
            self.io.display_framebuffer_scale = (
                window.get_pixel_ratio(),
                window.get_pixel_ratio(),
            )
        else:
            # Default to 1.0 in this unlikely circumstance
            self.io.display_fb_scale = (1.0, 1.0)

    def _attach_callbacks(self, window):
        self._window = window
        window.push_handlers(
            self.on_mouse_motion,
            self.on_key_press,
            self.on_key_release,
            self.on_text,
            self.on_mouse_drag,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_resize,
        )

    def _handle_mouse_cursor(self):
        if self.io.config_flags & imgui.ConfigFlags_.no_mouse_cursor_change.value:
            return

        mouse_cursor = imgui.get_mouse_cursor()
        window = self._window
        if self._cursor != mouse_cursor:
            self._cursor = mouse_cursor
            if mouse_cursor == imgui.MouseCursor_.none:
                window.set_mouse_visible(False)
            else:
                cursor = self.MOUSE_CURSORS.get(mouse_cursor)
                window.set_mouse_cursor(window.get_system_mouse_cursor(cursor))

    def _on_key(self, key_pressed, down):
        if key_pressed in self.key_map:
            imgui_key = self.key_map[key_pressed]
            self.io.add_key_event(imgui_key, down=down)

            # Handle modifiers, since ImGui has an additional mod_ctrl / shift / etc
            if imgui_key == imgui.Key.left_ctrl or imgui_key == imgui.Key.right_ctrl:
                self.io.add_key_event(imgui.Key.mod_ctrl, down)
            if imgui_key == imgui.Key.left_shift or imgui_key == imgui.Key.right_shift:
                self.io.add_key_event(imgui.Key.mod_shift, down)
            if imgui_key == imgui.Key.left_alt or imgui_key == imgui.Key.right_alt:
                self.io.add_key_event(imgui.Key.mod_alt, down)
            if imgui_key == imgui.Key.left_super or imgui_key == imgui.Key.right_super:
                self.io.add_key_event(imgui.Key.mod_super, down)

    def on_key_press(self, key_pressed, mods):
        self._on_key(key_pressed, True)

    def on_key_release(self, key_released, mods):
        self._on_key(key_released, False)

    def on_text(self, text):
        io = imgui.get_io()

        for char in text:
            io.add_input_character(ord(char))

    def on_mouse_motion(self, x, y, dx, dy):
        self.io.add_mouse_pos_event(x, self.io.display_size.y - y)

    def _on_mouse_button(self, pyglet_button, down):
        imgui_button = 0
        if pyglet_button == mouse.LEFT:
            imgui_button = 0
        elif pyglet_button == mouse.RIGHT:
            imgui_button = 1
        elif pyglet_button == mouse.MIDDLE:
            imgui_button = 2
        self.io.add_mouse_button_event(imgui_button, down)
    def on_mouse_press(self, x, y, button, modifiers):
        self._on_mouse_button(button, True)

    def on_mouse_release(self, x, y, button, modifiers):
        self._on_mouse_button(button, False)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self._on_mouse_button(button, True)
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, mods, scroll):
        self.io.add_mouse_wheel_event(0, -scroll)

    def on_resize(self, width, height):
        self.io.display_size = width, height

    def process_inputs(self):
        io = imgui.get_io()

        current_time = pyglet.clock.tick()

        if self._gui_time:
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1.0 / 60.0
        if io.delta_time <= 0.0:
            io.delta_time = 1.0 / 1000.0
        self._gui_time = current_time


class PygletProgrammablePipelineRenderer(PygletMixin, ProgrammablePipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super(PygletProgrammablePipelineRenderer, self).__init__()
        self._set_pixel_ratio(window)
        if attach_callbacks:
            self._attach_callbacks(window)

    def render(self, draw_data):
        super(PygletProgrammablePipelineRenderer, self).render(draw_data)
        self._handle_mouse_cursor()

def create_renderer(window, attach_callbacks=True):
    """
    This is a helper function that wraps the appropriate version of the Pyglet
    renderer class, based on the version of pyglet being used.
    """
    # Determine the context version
    # Pyglet < 2.0 has issues with ProgrammablePipeline even when the context
    # is OpenGL 3, so we need to check the pyglet version rather than looking
    # at window.config.major_version to see if we want to use programmable.
    assert int(pyglet.version.split('.')[0]) >= 2
    return PygletProgrammablePipelineRenderer(window, attach_callbacks)
