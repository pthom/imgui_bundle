# -*- coding: utf-8 -*-
from __future__ import absolute_import

import OpenGL.GL as gl  # noqa
from imgui_bundle import imgui
import ctypes
import numpy as np

from .opengl_base_backend import BaseOpenGLRenderer, get_common_gl_state, restore_common_gl_state


class FixedPipelineRenderer(
    BaseOpenGLRenderer
):  # Probably buggy (bad rendering with pygame)
    """Basic OpenGL integration base class."""

    # note: no need to override __init__

    def refresh_font_texture(self):
        # save texture state
        # last_texture = gl.glGetIntegerv(gl.GL_TEXTURE_BINDING_2D)
        # width, height, pixels = self.io.fonts.get_tex_data_as_alpha8()
        texture: np.array = self.io.fonts.get_tex_data_as_rgba32()

        if self._font_texture is not None:
            gl.glDeleteTextures([self._font_texture])

        self._font_texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._font_texture)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_ALPHA, width, height, 0, gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, pixels)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_ALPHA,
            texture.shape[0],
            texture.shape[1],
            0,
            gl.GL_ALPHA,
            gl.GL_UNSIGNED_BYTE,
            texture.data,
        )

        self.io.fonts.tex_id = self._font_texture
        # gl.glBindTexture(gl.GL_TEXTURE_2D, last_texture)
        self.io.fonts.clear_tex_data()

    def _create_device_objects(self):
        pass

    def render(self, draw_data):
        # perf: local for faster access
        io = self.io

        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_framebuffer_scale[0])
        fb_height = int(display_height * io.display_framebuffer_scale[1])

        if fb_width == 0 or fb_height == 0:
            return

        draw_data.scale_clip_rects(io.display_framebuffer_scale)

        # note: we are using fixed pipeline for cocos2d/pyglet
        # todo: consider porting to programmable pipeline
        # backup gl state
        common_gl_state_tuple = get_common_gl_state()

        gl.glPushAttrib(gl.GL_ENABLE_BIT | gl.GL_COLOR_BUFFER_BIT | gl.GL_TRANSFORM_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnable(gl.GL_TEXTURE_2D)

        gl.glViewport(0, 0, int(fb_width), int(fb_height))
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, io.display_size.x, io.display_size.y, 0.0, -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        for commands in draw_data.cmd_lists:

            gl.glVertexPointer(
                2,
                gl.GL_FLOAT,
                imgui.VERTEX_SIZE,
                ctypes.c_void_p(
                    commands.vtx_buffer.data_address() + imgui.VERTEX_BUFFER_POS_OFFSET
                ),
            )
            gl.glTexCoordPointer(
                2,
                gl.GL_FLOAT,
                imgui.VERTEX_SIZE,
                ctypes.c_void_p(
                    commands.vtx_buffer.data_address() + imgui.VERTEX_BUFFER_UV_OFFSET
                ),
            )
            gl.glColorPointer(
                4,
                gl.GL_UNSIGNED_BYTE,
                imgui.VERTEX_SIZE,
                ctypes.c_void_p(
                    commands.vtx_buffer.data_address() + imgui.VERTEX_BUFFER_COL_OFFSET
                ),
            )

            for command in commands.cmd_buffer:
                gl.glBindTexture(gl.GL_TEXTURE_2D, command.texture_id)

                x, y, z, w = command.clip_rect
                gl.glScissor(int(x), int(fb_height - w), int(z - x), int(w - y))

                if imgui.INDEX_SIZE == 2:
                    gltype = gl.GL_UNSIGNED_SHORT
                else:
                    gltype = gl.GL_UNSIGNED_INT

                gl.glDrawElements(
                    gl.GL_TRIANGLES,
                    command.elem_count,
                    gltype,
                    ctypes.c_void_p(command.idx_offset * imgui.INDEX_SIZE),
                )


        restore_common_gl_state(common_gl_state_tuple)

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glPopAttrib()

    def _invalidate_device_objects(self):
        if self._font_texture > -1:
            gl.glDeleteTextures([self._font_texture])
        self.io.fonts.texture_id = 0
        self._font_texture = 0
