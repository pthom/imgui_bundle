"""Sharp or smooth pixels

Show a small image, a heatmap or pixel art, with sharp pixels instead of blurred ones. For a texture made by Dear ImGui,
the renderer decides the sampling: `set_sampler_nearest()` asks it for sharp pixels. A texture made with OpenGL has its
own filter, which the renderer ignores, unless `set_sampler_from_tex()` gives it back.
"""

import numpy as np
from numpy.typing import NDArray

from imgui_bundle import hello_imgui, imgui, immapp, rich_md

try:
    import OpenGL.GL as gl  # optional (pip install PyOpenGL): the part on textures made with OpenGL

    HAS_PYOPENGL = True
except ImportError:
    HAS_PYOPENGL = False

# The heatmap's width and height, in pixels
HEATMAP_PIXELS = 10
# Each image's width and height on screen, in em (1 em = the height of a character)
IMAGE_SIZE_EM = 10.0


# ---------------------------------------------------------------------------------------------------------------------
# Part 1: a texture made by Dear ImGui, from pixels. Its renderer decides the sampling.
# ---------------------------------------------------------------------------------------------------------------------
def make_heatmap() -> NDArray[np.uint8]:
    """A small heatmap, as RGBA pixels: a smooth function of x and y, colored from dark blue to yellow (viridis)"""
    y, x = np.mgrid[0:HEATMAP_PIXELS, 0:HEATMAP_PIXELS] / (HEATMAP_PIXELS - 1)
    values = 0.5 + 0.5 * np.sin(5 * x + 1) * np.cos(4 * y)
    anchors = np.array([[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]], dtype=float)
    stops = np.linspace(0, 1, len(anchors))
    rgb = np.stack([np.interp(values, stops, anchors[:, c]) for c in range(3)], axis=-1)
    alpha = np.full(values.shape + (1,), 255.0)
    return np.concatenate([rgb, alpha], axis=-1).astype(np.uint8)


# The renderer backend (OpenGL, Metal, Vulkan, WebGL...) uploads it at the end of the frame that creates it
heatmap_texture = imgui.ImTextureData()


def heatmap_texture_ref() -> imgui.ImTextureRef:
    # "destroyed": not created yet, or destroyed with the renderer of a previous run
    if heatmap_texture.status == imgui.ImTextureStatus.destroyed:
        heatmap_texture.create(imgui.ImTextureFormat.rgba32, HEATMAP_PIXELS, HEATMAP_PIXELS)
        heatmap_texture.get_pixels_array()[:] = make_heatmap().ravel()
        imgui.internal.register_user_texture(heatmap_texture)
    return heatmap_texture.get_tex_ref()


# ---------------------------------------------------------------------------------------------------------------------
# Part 2: textures made with OpenGL, each with its own filter (glTexParameteri). The renderer ignores it,
# unless set_sampler_from_tex() asks it to use it.
# ---------------------------------------------------------------------------------------------------------------------
# A pixel-art heart: "#" its outline, "x" its red, "o" its highlight, "." transparent
HEART = [
    "...........",
    "..##...##..",
    ".#xx#.#xx#.",
    "#xoxx#xxxx#",
    "#xoxxxxxxx#",
    "#xxxxxxxxx#",
    ".#xxxxxxx#.",
    "..#xxxxx#..",
    "...#xxx#...",
    "....#x#....",
    ".....#.....",
]
HEART_COLORS = {"#": (110, 20, 40, 255), "x": (225, 45, 70, 255), "o": (255, 180, 190, 255), ".": (0, 0, 0, 0)}

opengl_heart_ids: dict[int, int] = {}  # the OpenGL texture of the heart, by its filter


def opengl_heart(gl_filter: int) -> imgui.ImTextureRef:
    """The heart as a texture made with OpenGL, with its own filter: gl.GL_NEAREST or gl.GL_LINEAR"""
    if gl_filter not in opengl_heart_ids:
        heart = np.array([[HEART_COLORS[c] for c in row] for row in HEART], dtype=np.uint8)
        texture_id = int(gl.glGenTextures(1))
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl_filter)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl_filter)
        # Clamp: by default, a linear filter at an edge blends in the opposite edge
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, heart.shape[1], heart.shape[0], 0,
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, heart)
        opengl_heart_ids[gl_filter] = texture_id
    return imgui.ImTextureRef(opengl_heart_ids[gl_filter])


def image_with_caption(tex_ref: imgui.ImTextureRef, caption: str) -> None:
    imgui.begin_group()
    imgui.image(tex_ref, hello_imgui.em_to_vec2(IMAGE_SIZE_EM, IMAGE_SIZE_EM))
    imgui.text(caption)
    imgui.end_group()


def gui() -> None:
    draw_list = imgui.get_window_draw_list()

    rich_md.render("""
        # Sharp or smooth pixels
        Shown large, a small image blurs: Dear ImGui draws images with *linear* sampling.
        For a heatmap or pixel art, each pixel should stay a sharp square: *nearest* sampling.

        ## A texture made by Dear ImGui: the renderer decides
        `set_sampler_nearest()` asks the renderer for nearest sampling, for the images that follow.
        """)
    if draw_list.can_set_sampler_nearest():
        draw_list.set_sampler_nearest()  # the images that follow: nearest sampling
        image_with_caption(heatmap_texture_ref(), "set_sampler_nearest()\nsharp")
        draw_list.set_sampler_linear()  # back to the default, for what follows
        imgui.same_line()
    image_with_caption(heatmap_texture_ref(), "The default\nsmooth")

    imgui.dummy(hello_imgui.em_to_vec2(0, 1))
    rich_md.render("""
        ## A texture made with OpenGL: it decides
        Each texture has its own filter, but the renderer imposes its sampling (since Dear ImGui 1.92.8).
        `set_sampler_from_tex()` gives each texture its own filter back.
        """)
    if not HAS_PYOPENGL:
        imgui.text("Install PyOpenGL to see this part: pip install PyOpenGL")
    elif not draw_list.can_set_sampler_from_tex():
        imgui.text("This renderer cannot use a texture's own filter (OpenGL only).")
    else:
        draw_list.set_sampler_from_tex()  # the images that follow: each texture's own filter
        image_with_caption(opengl_heart(gl.GL_NEAREST), "GL_NEAREST\nfrom_tex: sharp")
        imgui.same_line()
        image_with_caption(opengl_heart(gl.GL_LINEAR), "GL_LINEAR\nfrom_tex: smooth")
        # Back to the renderer's sampling. After set_sampler_from_tex(), set_sampler_linear() would write GL_LINEAR
        # into the textures that follow, which would lose their own filter.
        draw_list.reset_render_state()
        imgui.same_line()
        image_with_caption(opengl_heart(gl.GL_NEAREST), "GL_NEAREST\nthe default: blurred")


def main() -> None:
    immapp.run(gui, window_title="Sharp or smooth pixels", window_size=(540, 740), with_markdown=True)


if __name__ == "__main__":
    main()
