from imgui_bundle import imgui
import OpenGL.GL as gl  # noqa


class BaseOpenGLRenderer(object):
    def __init__(self):
        if not imgui.get_current_context():
            raise RuntimeError(
                "No valid ImGui context. Use imgui.create_context() first and/or "
                "imgui.set_current_context()."
            )
        self.io = imgui.get_io()

        self._font_texture = None

        self.io.delta_time = 1.0 / 60.0

        self._create_device_objects()
        self.refresh_font_texture()

    def render(self, draw_data):
        raise NotImplementedError

    def refresh_font_texture(self):
        raise NotImplementedError

    def _create_device_objects(self):
        raise NotImplementedError

    def _invalidate_device_objects(self):
        raise NotImplementedError

    def shutdown(self):
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
