# -*- coding: utf-8 -*-
from __future__ import absolute_import
import warnings
from distutils.version import LooseVersion

from imgui_bundle import imgui

from pyglet.window import key, mouse, Window
import pyglet
import pyglet.clock


from imgui_bundle.python_backends import compute_fb_scale
from imgui_bundle.python_backends.opengl_backend import (
    FixedPipelineRenderer,
    ProgrammablePipelineRenderer,
)


class PygletMixin(object):
    REVERSE_KEY_MAP = {
        key.TAB: imgui.Key.tab,
        key.LEFT: imgui.Key.left_arrow,
        key.RIGHT: imgui.Key.right_arrow,
        key.UP: imgui.Key.up_arrow,
        key.DOWN: imgui.Key.down_arrow,
        key.PAGEUP: imgui.Key.page_up,
        key.PAGEDOWN: imgui.Key.page_down,
        key.HOME: imgui.Key.home,
        key.END: imgui.Key.end,
        key.INSERT: imgui.Key.insert,
        key.DELETE: imgui.Key.delete,
        key.BACKSPACE: imgui.Key.backspace,
        key.SPACE: imgui.Key.space,
        key.RETURN: imgui.Key.enter,
        key.ESCAPE: imgui.Key.escape,
        key.NUM_ENTER: imgui.Key.keypad_enter,
        key.A: imgui.Key.a,
        key.C: imgui.Key.c,
        key.V: imgui.Key.v,
        key.X: imgui.Key.x,
        key.Y: imgui.Key.y,
        key.Z: imgui.Key.z,
    }
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

    def _on_mods_change(self, mods, key_pressed=0):
        self.io.key_ctrl = mods & key.MOD_CTRL or key_pressed in (key.LCTRL, key.RCTRL)
        self.io.key_super = mods & key.MOD_COMMAND or key_pressed in (
            key.LCOMMAND,
            key.RCOMMAND,
        )
        self.io.key_alt = mods & key.MOD_ALT or key_pressed in (key.LALT, key.RALT)
        self.io.key_shift = mods & key.MOD_SHIFT or key_pressed in (
            key.LSHIFT,
            key.RSHIFT,
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

    def on_mouse_motion(self, x, y, dx, dy):
        self.io.mouse_pos = x, self.io.display_size.y - y

    def on_key_press(self, key_pressed, mods):
        if key_pressed in self.REVERSE_KEY_MAP:
            imgui_key = self.REVERSE_KEY_MAP[key_pressed]
            self.io.add_key_event(imgui_key, down=True)
        self._on_mods_change(mods, key_pressed)

    def on_key_release(self, key_released, mods):
        if key_released in self.REVERSE_KEY_MAP:
            imgui_key = self.REVERSE_KEY_MAP[key_released]
            self.io.add_key_event(imgui_key, down=False)
        self._on_mods_change(mods)

    def on_text(self, text):
        io = imgui.get_io()

        for char in text:
            io.add_input_character(ord(char))

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.io.mouse_pos = x, self.io.display_size.y - y

        if button == mouse.LEFT:
            self.io.mouse_down[0] = 1

        if button == mouse.MIDDLE:
            self.io.mouse_down[1] = 1

        if button == mouse.RIGHT:
            self.io.mouse_down[2] = 1

    def on_mouse_press(self, x, y, button, modifiers):
        self.io.mouse_pos = x, self.io.display_size.y - y

        if button == mouse.LEFT:
            self.io.mouse_down[0] = 1

        if button == mouse.MIDDLE:
            self.io.mouse_down[1] = 1

        if button == mouse.RIGHT:
            self.io.mouse_down[2] = 1

    def on_mouse_release(self, x, y, button, modifiers):
        self.io.mouse_pos = x, self.io.display_size.y - y

        if button == mouse.LEFT:
            self.io.mouse_down[0] = 0

        if button == mouse.MIDDLE:
            self.io.mouse_down[1] = 0

        if button == mouse.RIGHT:
            self.io.mouse_down[2] = 0

    def on_mouse_scroll(self, x, y, mods, scroll):
        self.io.mouse_wheel = scroll

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


class PygletFixedPipelineRenderer(PygletMixin, FixedPipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super(PygletFixedPipelineRenderer, self).__init__()
        self._set_pixel_ratio(window)
        if attach_callbacks:
            self._attach_callbacks(window)

    def render(self, draw_data):
        super(PygletFixedPipelineRenderer, self).render(draw_data)
        self._handle_mouse_cursor()


class PygletProgrammablePipelineRenderer(PygletMixin, ProgrammablePipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super(PygletProgrammablePipelineRenderer, self).__init__()
        self._set_pixel_ratio(window)
        if attach_callbacks:
            self._attach_callbacks(window)

    def render(self, draw_data):
        super(PygletProgrammablePipelineRenderer, self).render(draw_data)
        self._handle_mouse_cursor()


class PygletRenderer(PygletFixedPipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        warnings.warn(
            "PygletRenderer is deprecated; please use either "
            "PygletFixedPipelineRenderer (for OpenGL 2.1, pyglet < 2.0) or "
            "PygletProgrammablePipelineRenderer (for later versions) or "
            "create_renderer(window) to auto-detect.",
            DeprecationWarning,
            stacklevel=2,
        )
        super(PygletRenderer, self).__init__(window, attach_callbacks)


def create_renderer(window, attach_callbacks=True):
    """
    This is a helper function that wraps the appropriate version of the Pyglet
    renderer class, based on the version of pyglet being used.
    """
    # Determine the context version
    # Pyglet < 2.0 has issues with ProgrammablePipeline even when the context
    # is OpenGL 3, so we need to check the pyglet version rather than looking
    # at window.config.major_version to see if we want to use programmable.
    if LooseVersion(pyglet.version) < LooseVersion("2.0"):
        return PygletFixedPipelineRenderer(window, attach_callbacks)
    else:
        return PygletProgrammablePipelineRenderer(window, attach_callbacks)
