# -*- coding: utf-8 -*-
from __future__ import absolute_import

import OpenGL.GL as gl  # pip install PyOpenGL
from imgui_bundle import imgui
import ctypes

from .opengl_base_backend import BaseOpenGLRenderer, get_common_gl_state, restore_common_gl_state


class ProgrammablePipelineRenderer(BaseOpenGLRenderer):
    """Basic OpenGL integration base class."""

    VERTEX_SHADER_SRC = """
    #version 330

    uniform mat4 ProjMtx;
    in vec2 Position;
    in vec2 UV;
    in vec4 Color;
    out vec2 Frag_UV;
    out vec4 Frag_Color;

    void main() {
        Frag_UV = UV;
        Frag_Color = Color;

        gl_Position = ProjMtx * vec4(Position.xy, 0, 1);
    }
    """

    FRAGMENT_SHADER_SRC = """
    #version 330

    uniform sampler2D Texture;
    in vec2 Frag_UV;
    in vec4 Frag_Color;
    out vec4 Out_Color;

    void main() {
        Out_Color = Frag_Color * texture(Texture, Frag_UV.st);
    }
    """

    def __init__(self):
        self._shader_handle = None
        self._vert_handle = None
        self._fragment_handle = None

        self._attrib_location_tex = None
        self._attrib_proj_mtx = None
        self._attrib_location_position = None
        self._attrib_location_uv = None
        self._attrib_location_color = None

        self._vbo_handle = None
        self._elements_handle = None
        self._vao_handle = None


        super(ProgrammablePipelineRenderer, self).__init__()

    def _create_device_objects(self):
        # save state
        last_texture = gl.glGetIntegerv(gl.GL_TEXTURE_BINDING_2D)
        last_array_buffer = gl.glGetIntegerv(gl.GL_ARRAY_BUFFER_BINDING)

        last_vertex_array = gl.glGetIntegerv(gl.GL_VERTEX_ARRAY_BINDING)

        self._shader_handle = gl.glCreateProgram()
        # note: no need to store shader parts handles after linking
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glShaderSource(vertex_shader, self.VERTEX_SHADER_SRC)
        gl.glShaderSource(fragment_shader, self.FRAGMENT_SHADER_SRC)
        gl.glCompileShader(vertex_shader)
        gl.glCompileShader(fragment_shader)

        gl.glAttachShader(self._shader_handle, vertex_shader)
        gl.glAttachShader(self._shader_handle, fragment_shader)

        gl.glLinkProgram(self._shader_handle)

        # note: after linking shaders can be removed
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        self._attrib_location_tex = gl.glGetUniformLocation(
            self._shader_handle, "Texture"
        )
        self._attrib_proj_mtx = gl.glGetUniformLocation(self._shader_handle, "ProjMtx")
        self._attrib_location_position = gl.glGetAttribLocation(
            self._shader_handle, "Position"
        )
        self._attrib_location_uv = gl.glGetAttribLocation(self._shader_handle, "UV")
        self._attrib_location_color = gl.glGetAttribLocation(
            self._shader_handle, "Color"
        )

        self._vbo_handle = gl.glGenBuffers(1)
        self._elements_handle = gl.glGenBuffers(1)

        self._vao_handle = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self._vao_handle)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo_handle)

        gl.glEnableVertexAttribArray(self._attrib_location_position)
        gl.glEnableVertexAttribArray(self._attrib_location_uv)
        gl.glEnableVertexAttribArray(self._attrib_location_color)

        gl.glVertexAttribPointer(
            self._attrib_location_position,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            imgui.VERTEX_SIZE,
            ctypes.c_void_p(imgui.VERTEX_BUFFER_POS_OFFSET),
        )
        gl.glVertexAttribPointer(
            self._attrib_location_uv,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            imgui.VERTEX_SIZE,
            ctypes.c_void_p(imgui.VERTEX_BUFFER_UV_OFFSET),
        )
        gl.glVertexAttribPointer(
            self._attrib_location_color,
            4,
            gl.GL_UNSIGNED_BYTE,
            gl.GL_TRUE,
            imgui.VERTEX_SIZE,
            ctypes.c_void_p(imgui.VERTEX_BUFFER_COL_OFFSET),
        )

        # restore state
        gl.glBindTexture(gl.GL_TEXTURE_2D, last_texture)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, last_array_buffer)
        gl.glBindVertexArray(last_vertex_array)

    def render(self, draw_data: imgui.ImDrawData):
        # perf: local for faster access
        io = self.io

        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_framebuffer_scale[0])
        fb_height = int(display_height * io.display_framebuffer_scale[1])

        # Honor RendererHasTextures
        self._update_textures()

        if fb_width == 0 or fb_height == 0:
            return

        draw_data.scale_clip_rects(io.display_framebuffer_scale)

        # backup GL state
        # todo: provide cleaner version of this backup-restore code
        common_gl_state_tuple = get_common_gl_state()
        last_program = gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM)
        last_active_texture = gl.glGetIntegerv(gl.GL_ACTIVE_TEXTURE)
        last_array_buffer = gl.glGetIntegerv(gl.GL_ARRAY_BUFFER_BINDING)
        last_element_array_buffer = gl.glGetIntegerv(gl.GL_ELEMENT_ARRAY_BUFFER_BINDING)
        last_vertex_array = gl.glGetIntegerv(gl.GL_VERTEX_ARRAY_BINDING)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendEquation(gl.GL_FUNC_ADD)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        gl.glViewport(0, 0, int(fb_width), int(fb_height))

        ortho_projection = (ctypes.c_float * 16)(  # noqa
            2.0 / display_width,
            0.0,
            0.0,
            0.0,
            0.0,
            2.0 / -display_height,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            -1.0,
            1.0,
            0.0,
            1.0,
        )

        gl.glUseProgram(self._shader_handle)
        gl.glUniform1i(self._attrib_location_tex, 0)
        gl.glUniformMatrix4fv(self._attrib_proj_mtx, 1, gl.GL_FALSE, ortho_projection)
        gl.glBindVertexArray(self._vao_handle)

        for commands in draw_data.cmd_lists:

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo_handle)
            # todo: check this (sizes)
            gl.glBufferData(
                gl.GL_ARRAY_BUFFER,
                commands.vtx_buffer.size() * imgui.VERTEX_SIZE,
                ctypes.c_void_p(commands.vtx_buffer.data_address()),
                gl.GL_STREAM_DRAW,
            )

            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._elements_handle)
            # todo: check this (sizes)
            gl.glBufferData(
                gl.GL_ELEMENT_ARRAY_BUFFER,
                commands.idx_buffer.size() * imgui.INDEX_SIZE,
                ctypes.c_void_p(commands.idx_buffer.data_address()),
                gl.GL_STREAM_DRAW,
            )

            # todo: allow to iterate over _CmdList
            for command in commands.cmd_buffer:
                gl.glBindTexture(gl.GL_TEXTURE_2D, command.tex_ref.get_tex_id())

                # todo: use named tuple
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


        # restore modified GL state
        restore_common_gl_state(common_gl_state_tuple)

        gl.glUseProgram(last_program)
        gl.glActiveTexture(last_active_texture)
        gl.glBindVertexArray(last_vertex_array)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, last_array_buffer)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, last_element_array_buffer)

    def _invalidate_device_objects(self):
        if self._vao_handle > -1:
            gl.glDeleteVertexArrays(1, [self._vao_handle])
        if self._vbo_handle > -1:
            gl.glDeleteBuffers(1, [self._vbo_handle])
        if self._elements_handle > -1:
            gl.glDeleteBuffers(1, [self._elements_handle])
        self._vao_handle = self._vbo_handle = self._elements_handle = 0

        gl.glDeleteProgram(self._shader_handle)
        self._shader_handle = 0
