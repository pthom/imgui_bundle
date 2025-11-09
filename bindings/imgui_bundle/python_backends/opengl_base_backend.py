from imgui_bundle import imgui
import OpenGL.GL as gl  # pip install PyOpenGL


def _log__update_texture(msg: str):
    pass
    # import logging
    # logging.warning(msg)

class BaseOpenGLRenderer(object):
    def __init__(self):
        if not imgui.get_current_context():
            raise RuntimeError(
                "No valid ImGui context. Use imgui.create_context() first and/or "
                "imgui.set_current_context()."
            )
        self.io = imgui.get_io()
        self.io.delta_time = 1.0 / 60.0

        self._create_device_objects()

        # Honor RendererHasTextures
        # cf https://github.com/ocornut/imgui/commit/ff3f471ab2af25f1cc11c20356711aaa4e6833f8
        imgui.get_io().backend_flags |= imgui.BackendFlags_.renderer_has_textures.value
        max_texture_size = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        imgui.get_platform_io().renderer_texture_max_width = max_texture_size
        imgui.get_platform_io().renderer_texture_max_height = max_texture_size

    def render(self, draw_data):
        raise NotImplementedError

    def _update_textures(self):
        # Honor RendererHasTextures
        # cf https://github.com/ocornut/imgui/commit/ff3f471ab2af25f1cc11c20356711aaa4e6833f8
        for tex in imgui.get_platform_io().textures:
            if tex.status != imgui.ImTextureStatus.ok:
                self._update_texture(tex)

    def _destroy_all_textures(self):
        for tex in imgui.get_platform_io().textures:
            if tex.ref_count == 1:
                tex.status = imgui.ImTextureStatus.want_destroy
                self._update_texture(tex)

    def _update_texture(self, tex: imgui.ImTextureData):
        # Honor RendererHasTextures
        # cf https://github.com/ocornut/imgui/commit/ff3f471ab2af25f1cc11c20356711aaa4e6833f8
        # This method is a port of the C++ function ImGui_ImplOpenGL3_UpdateTexture
        # where we use
        #     pixels = tex.get_pixels_array()
        # to get a numpy array of the pixel data
        # When doing updates, we use a sub-view of the full_pixels array to avoid copying data

        if tex.status == imgui.ImTextureStatus.want_create:
            # Create and upload new texture to graphics system
            _log__update_texture(f"UpdateTexture #{tex.unique_id}: WantCreate {tex.width}x{tex.height}")
            assert tex.tex_id == 0
            assert tex.backend_user_data is None
            assert tex.format == imgui.ImTextureFormat.rgba32

            # Upload texture to graphics system
            # (Bilinear sampling is required by default. Set 'io.Fonts->Flags |= ImFontAtlasFlags_NoBakedLines' or 'style.AntiAliasedLinesUseTex = false' to allow point/nearest sampling)
            last_texture = gl.glGetIntegerv(gl.GL_TEXTURE_BINDING_2D)
            gl_texture_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, gl_texture_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            if hasattr(gl, "GL_UNPACK_ROW_LENGTH"):
                gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH, 0)

            pixels_array = tex.get_pixels_array()
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,
                0,
                gl.GL_RGBA,
                tex.width,
                tex.height,
                0,
                gl.GL_RGBA,
                gl.GL_UNSIGNED_BYTE,
                pixels_array,
            )

            # Store identifiers: store the new GL texture ID back into ImGui's structure
            tex.set_tex_id(gl_texture_id)
            tex.status = imgui.ImTextureStatus.ok

            # Restore state
            gl.glBindTexture(gl.GL_TEXTURE_2D, last_texture)

        elif tex.status == imgui.ImTextureStatus.want_updates:
            _log__update_texture(f"UpdateTexture #{tex.unique_id}: WantUpdate {len(tex.updates)}")
            # Update selected blocks. We only ever write to textures regions that have never been used before!
            # This backend chooses to use tex.Updates[], but you can use tex.UpdateRect to upload a single region.
            last_texture = gl.glGetIntegerv(gl.GL_TEXTURE_BINDING_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex.tex_id)

            # We assume desktop OpenGL where GL_UNPACK_ROW_LENGTH is supported.
            # This allows partial updates without line-by-line copies in Python.
            gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH, tex.width)

            # Get the full 1D array of pixels (shape=(width*height*bpp,))
            full_pixels = tex.get_pixels_array()

            for r in tex.updates:
                # Compute offset into the 1D array for the sub-rectangle's top-left pixel:
                offset = (r.y * tex.width + r.x) * tex.bytes_per_pixel
                # Then get a slice from that offset to the end. We only need the pointer’s start address:
                sub_view = full_pixels[offset:]  # shape is still 1D, but it starts at the correct place

                # glTexSubImage2D will read only r.h rows and r.w columns per row,
                # with the stride controlled by GL_UNPACK_ROW_LENGTH:
                gl.glTexSubImage2D(
                    gl.GL_TEXTURE_2D,
                    0,             # mip level
                    r.x,
                    r.y,
                    r.w,
                    r.h,
                    gl.GL_RGBA,
                    gl.GL_UNSIGNED_BYTE,
                    sub_view
                )

            # Restore the row-length to 0 (the driver default)
            gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH, 0)

            tex.status = imgui.ImTextureStatus.ok
            gl.glBindTexture(gl.GL_TEXTURE_2D, last_texture)  # Restore state

        elif tex.status == imgui.ImTextureStatus.want_destroy:
            _log__update_texture(f"UpdateTexture #{tex.unique_id}: WantDestroy")
            gl_tex_id = tex.tex_id
            gl.glDeleteTextures([gl_tex_id])

            # Clear identifiers and mark as destroyed (so e.g. InvalidateDeviceObjects can be called at runtime)
            ImTextureID_Invalid = 0
            tex.set_tex_id(ImTextureID_Invalid)
            tex.status = imgui.ImTextureStatus.destroyed

    def _create_device_objects(self):
        raise NotImplementedError

    def _invalidate_device_objects(self):
        raise NotImplementedError

    def shutdown(self):
        self._destroy_all_textures()
        imgui.get_io().backend_flags &= ~imgui.BackendFlags_.renderer_has_textures.value
        self._invalidate_device_objects()


def get_common_gl_state():
    """
    Backups the current OpenGL state
    Returns a tuple of results for glGet / glIsEnabled calls
    NOTE: when adding more backuped state in the future,
    make sure to update function `restore_common_gl_state`
    """
    last_texture = gl.glGetIntegerv(gl.GL_TEXTURE_BINDING_2D)
    last_viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
    last_enable_blend = gl.glIsEnabled(gl.GL_BLEND)
    last_enable_cull_face = gl.glIsEnabled(gl.GL_CULL_FACE)
    last_enable_depth_test = gl.glIsEnabled(gl.GL_DEPTH_TEST)
    last_enable_scissor_test = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
    last_scissor_box = gl.glGetIntegerv(gl.GL_SCISSOR_BOX)
    last_blend_src = gl.glGetIntegerv(gl.GL_BLEND_SRC)
    last_blend_dst = gl.glGetIntegerv(gl.GL_BLEND_DST)
    last_blend_equation_rgb = gl.glGetIntegerv(gl.GL_BLEND_EQUATION_RGB)
    last_blend_equation_alpha = gl.glGetIntegerv(gl.GL_BLEND_EQUATION_ALPHA)
    last_front_and_back_polygon_mode, _ = gl.glGetIntegerv(gl.GL_POLYGON_MODE)
    return (
        last_texture,
        last_viewport,
        last_enable_blend,
        last_enable_cull_face,
        last_enable_depth_test,
        last_enable_scissor_test,
        last_scissor_box,
        last_blend_src,
        last_blend_dst,
        last_blend_equation_rgb,
        last_blend_equation_alpha,
        last_front_and_back_polygon_mode,
    )


def restore_common_gl_state(common_gl_state_tuple):
    """
    Takes a tuple after calling function `get_common_gl_state`,
    to set the given OpenGL state back as it was before rendering the UI
    """
    (
        last_texture,
        last_viewport,
        last_enable_blend,
        last_enable_cull_face,
        last_enable_depth_test,
        last_enable_scissor_test,
        last_scissor_box,
        last_blend_src,
        last_blend_dst,
        last_blend_equation_rgb,
        last_blend_equation_alpha,
        last_front_and_back_polygon_mode,
    ) = common_gl_state_tuple

    gl.glBindTexture(gl.GL_TEXTURE_2D, last_texture)
    gl.glBlendEquationSeparate(last_blend_equation_rgb, last_blend_equation_alpha)
    gl.glBlendFunc(last_blend_src, last_blend_dst)

    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, last_front_and_back_polygon_mode)

    if last_enable_blend:
        gl.glEnable(gl.GL_BLEND)
    else:
        gl.glDisable(gl.GL_BLEND)

    if last_enable_cull_face:
        gl.glEnable(gl.GL_CULL_FACE)
    else:
        gl.glDisable(gl.GL_CULL_FACE)

    if last_enable_depth_test:
        gl.glEnable(gl.GL_DEPTH_TEST)
    else:
        gl.glDisable(gl.GL_DEPTH_TEST)

    if last_enable_scissor_test:
        gl.glEnable(gl.GL_SCISSOR_TEST)
    else:
        gl.glDisable(gl.GL_SCISSOR_TEST)

    gl.glScissor(
        last_scissor_box[0],
        last_scissor_box[1],
        last_scissor_box[2],
        last_scissor_box[3],
    )
    gl.glViewport(
        last_viewport[0], last_viewport[1], last_viewport[2], last_viewport[3]
    )
