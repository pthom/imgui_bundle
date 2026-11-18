"""Sharp or smooth pixels: a small image shown large, with nearest sampling (each pixel a sharp square) and with
linear sampling, Dear ImGui's default (the pixels blend). The draw list's set_sampler_*() methods switch between them."""

import numpy as np
from numpy.typing import NDArray

from imgui_bundle import hello_imgui, imgui, immapp, rich_md

try:
    import OpenGL.GL as gl  # optional (pip install PyOpenGL): the part on a texture made with OpenGL

    HAS_PYOPENGL = True
except ImportError:
    HAS_PYOPENGL = False

# The heatmap's width and height, in pixels
HEATMAP_PIXELS = 10
# Each image's width and height on screen, in em (1 em = the height of a character)
IMAGE_SIZE_EM = 12.0


def make_heatmap() -> NDArray[np.uint8]:
    """A small heatmap, as RGBA pixels: a smooth function of x and y, colored from dark blue to yellow (viridis)"""
    y, x = np.mgrid[0:HEATMAP_PIXELS, 0:HEATMAP_PIXELS] / (HEATMAP_PIXELS - 1)
    values = 0.5 + 0.5 * np.sin(5 * x + 1) * np.cos(4 * y)
    anchors = np.array([[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]], dtype=float)
    stops = np.linspace(0, 1, len(anchors))
    rgb = np.stack([np.interp(values, stops, anchors[:, c]) for c in range(3)], axis=-1)
    alpha = np.full(values.shape + (1,), 255.0)
    return np.concatenate([rgb, alpha], axis=-1).astype(np.uint8)


# The heatmap as a texture made by Dear ImGui: its renderer backend uploads it at the end of the frame that creates it
heatmap_texture = imgui.ImTextureData()


def heatmap_texture_ref() -> imgui.ImTextureRef:
    # "destroyed": not created yet, or destroyed with the renderer of a previous run
    if heatmap_texture.status == imgui.ImTextureStatus.destroyed:
        heatmap_texture.create(imgui.ImTextureFormat.rgba32, HEATMAP_PIXELS, HEATMAP_PIXELS)
        heatmap_texture.get_pixels_array()[:] = make_heatmap().ravel()
        imgui.internal.register_user_texture(heatmap_texture)
    return heatmap_texture.get_tex_ref()


# The same heatmap as a texture made with OpenGL, with its own filter: GL_NEAREST
opengl_texture_id = 0


def opengl_texture_ref() -> imgui.ImTextureRef:
    global opengl_texture_id
    if opengl_texture_id == 0:
        opengl_texture_id = int(gl.glGenTextures(1))
        gl.glBindTexture(gl.GL_TEXTURE_2D, opengl_texture_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, HEATMAP_PIXELS, HEATMAP_PIXELS, 0,
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, make_heatmap())
    return imgui.ImTextureRef(opengl_texture_id)


def image_with_caption(tex_ref: imgui.ImTextureRef, caption: str) -> None:
    imgui.begin_group()
    imgui.image(tex_ref, hello_imgui.em_to_vec2(IMAGE_SIZE_EM, IMAGE_SIZE_EM))
    imgui.text(caption)
    imgui.end_group()


def gui() -> None:
    draw_list = imgui.get_window_draw_list()

    rich_md.render("""
        # Sharp or smooth pixels
        Dear ImGui draws images with *linear* sampling: shown large, a small image blurs, its pixels blend.
        For a heatmap or pixel art, ask the renderer for *nearest* sampling: each pixel stays a sharp square.
        """)
    if draw_list.can_set_sampler_nearest():
        draw_list.set_sampler_nearest()  # the images that follow: nearest sampling
        image_with_caption(heatmap_texture_ref(), "Nearest: sharp")
        draw_list.set_sampler_linear()  # back to the default, for what follows
        imgui.same_line()
    image_with_caption(heatmap_texture_ref(), "Linear, the default")

    imgui.dummy(hello_imgui.em_to_vec2(0, 1))
    rich_md.render("""
        ## A texture of your own, made with OpenGL
        It has its own filter (here `GL_NEAREST`), but the renderer imposes its sampling.
        `set_sampler_from_tex()` asks it to use the texture's own filter.
        """)
    if not HAS_PYOPENGL:
        imgui.text("Install PyOpenGL to see this part: pip install PyOpenGL")
    elif not draw_list.can_set_sampler_from_tex():
        imgui.text("This renderer cannot use a texture's own filter (OpenGL only).")
    else:
        draw_list.set_sampler_from_tex()  # the images that follow: their own filter
        image_with_caption(opengl_texture_ref(), "From the texture: sharp")
        # Back to the default. After set_sampler_from_tex(), set_sampler_linear() would write GL_LINEAR
        # into the texture itself, which would then lose its GL_NEAREST.
        draw_list.reset_render_state()
        imgui.same_line()
        image_with_caption(opengl_texture_ref(), "Linear, the default")


def main() -> None:
    immapp.run(gui, window_title="Sharp or smooth pixels", window_size=(540, 680), with_markdown=True)


if __name__ == "__main__":
    main()
