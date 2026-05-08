"""
Render a 3D cube with WebGL from Python, display it inside an ImGui window
via `imgui.image()`. Zero CPU/GPU round-trip on the steady-state path.

**Pyodide only.** This demo uses Python's `js` interop to call the browser's
WebGL2 API directly, and the wheel-side bridge (`imgui_bundle.webgl`) is
compiled in only for Pyodide builds. On desktop, see
`bindings/imgui_bundle/demos_python/demos_immapp/demo_custom_background.py`
for the PyOpenGL equivalent.

## How the WebGL -> ImGui bridge works

ImGui's renderer is C++ compiled to wasm; it identifies textures by
integer IDs (`ImTextureID`). Textures we create from Python via
`gl.createTexture()` come back as JS `WebGLTexture` *objects* — so we
need a bridge that registers the JS texture and returns an integer the
renderer can use.

That bridge is `imgui_bundle.webgl.register_texture`. Usage in a nutshell:

```python
from imgui_bundle import webgl
from js import document
gl = document.getElementById("canvas").getContext("webgl2")

tex = gl.createTexture()
# ... populate the texture (FBO render target, glTexImage2D, etc.) ...
tex_id = webgl.register_texture(tex)

# In the GUI loop:
imgui.image(imgui.ImTextureRef(tex_id), ImVec2(256, 256))

# At shutdown:
webgl.unregister_texture(tex_id)
gl.deleteTexture(tex)
```

Register once at startup; the integer is stable for the lifetime of the
registration. ImGui's renderer samples the same GPU memory we render into
— no copy, no readback per frame.

## What this demo shows

A 3D scene rendered from Python: a colored cube that rotates over time,
with a depth buffer for proper occlusion. Each face has a distinct color
so the 3D-ness is visible at a glance. The cube is drawn into an offscreen
FBO and the resulting texture is shown in an ImGui window.

## Related playground entries

- `webgl_minimal_mandelbrot.py`: the smallest possible WebGL background
  shader, Pyodide-only.
- `webgl_background_shader.py`: a fancier shader (Seascape) with a
  desktop+web compat layer (one source, both targets).
"""
import math

import numpy as np

import imgui_bundle
from imgui_bundle import hello_imgui, imgui, immapp, imgui_md, ImVec2

if not imgui_bundle.has_submodule("webgl"):
    raise RuntimeError(
        "imgui_bundle.webgl is only compiled in Pyodide builds. "
        "On desktop, see the demos_python/demos_immapp/demo_custom_background.py "
        "PyOpenGL equivalent instead."
    )
from imgui_bundle import webgl

from js import document, Float32Array  # type: ignore[import-not-found]


# --- WebGL2 context (shared with hello_imgui's renderer) ------------------

_canvas = document.getElementById("canvas")
gl = _canvas.getContext("webgl2")
if gl is None:
    raise RuntimeError("Could not acquire WebGL2 context on #canvas")


# --- Offscreen FBO: color texture + depth renderbuffer --------------------

TEX_W, TEX_H = 384, 384

_color_tex = gl.createTexture()
gl.bindTexture(gl.TEXTURE_2D, _color_tex)
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, TEX_W, TEX_H, 0,
              gl.RGBA, gl.UNSIGNED_BYTE, None)
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
gl.bindTexture(gl.TEXTURE_2D, None)

# Depth renderbuffer — required for correct occlusion when faces overlap.
_depth_rb = gl.createRenderbuffer()
gl.bindRenderbuffer(gl.RENDERBUFFER, _depth_rb)
gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT16, TEX_W, TEX_H)
gl.bindRenderbuffer(gl.RENDERBUFFER, None)

_fbo = gl.createFramebuffer()
gl.bindFramebuffer(gl.FRAMEBUFFER, _fbo)
gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0,
                        gl.TEXTURE_2D, _color_tex, 0)
gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT,
                           gl.RENDERBUFFER, _depth_rb)
gl.bindFramebuffer(gl.FRAMEBUFFER, None)


# --- Register the texture once with ImGui's renderer ----------------------

TEXTURE_ID = webgl.register_texture(_color_tex)


# --- Cube geometry: 36 vertices, 6 floats each (xyz + rgb) ----------------

def _cube_vertices():
    # Each face: four corners + a single color, triangulated as 0-1-2, 0-2-3.
    faces = [
        ([(-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)], (1.00, 0.30, 0.30)),  # +Z front  red
        ([( 1, -1, -1), (-1, -1, -1), (-1,  1, -1), ( 1,  1, -1)], (0.30, 1.00, 0.30)),  # -Z back   green
        ([( 1, -1,  1), ( 1, -1, -1), ( 1,  1, -1), ( 1,  1,  1)], (0.30, 0.30, 1.00)),  # +X right  blue
        ([(-1, -1, -1), (-1, -1,  1), (-1,  1,  1), (-1,  1, -1)], (1.00, 1.00, 0.30)),  # -X left   yellow
        ([(-1,  1,  1), ( 1,  1,  1), ( 1,  1, -1), (-1,  1, -1)], (1.00, 0.30, 1.00)),  # +Y top    magenta
        ([(-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1)], (0.30, 1.00, 1.00)),  # -Y bottom cyan
    ]
    verts = []
    for corners, (r, g, b) in faces:
        for i in (0, 1, 2, 0, 2, 3):
            x, y, z = corners[i]
            verts.extend([x, y, z, r, g, b])
    return verts


# --- Shaders --------------------------------------------------------------

_VS = """#version 300 es
precision highp float;
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
uniform mat4 uMvp;
out vec3 vColor;
void main() {
    gl_Position = uMvp * vec4(aPos, 1.0);
    vColor = aColor;
}
"""

_FS = """#version 300 es
precision highp float;
in vec3 vColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(vColor, 1.0);
}
"""


def _compile(stage, src):
    s = gl.createShader(stage)
    gl.shaderSource(s, src)
    gl.compileShader(s)
    if not gl.getShaderParameter(s, gl.COMPILE_STATUS):
        raise RuntimeError(gl.getShaderInfoLog(s))
    return s


_prog = gl.createProgram()
gl.attachShader(_prog, _compile(gl.VERTEX_SHADER, _VS))
gl.attachShader(_prog, _compile(gl.FRAGMENT_SHADER, _FS))
gl.linkProgram(_prog)
if not gl.getProgramParameter(_prog, gl.LINK_STATUS):
    raise RuntimeError(gl.getProgramInfoLog(_prog))
_uMvp_loc = gl.getUniformLocation(_prog, "uMvp")

# Cube VAO + VBO
_vao = gl.createVertexArray()
gl.bindVertexArray(_vao)
_vbo = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, _vbo)
gl.bufferData(gl.ARRAY_BUFFER, Float32Array.new(_cube_vertices()), gl.STATIC_DRAW)

_STRIDE = 6 * 4  # 6 floats * 4 bytes
gl.vertexAttribPointer(0, 3, gl.FLOAT, False, _STRIDE, 0)        # aPos
gl.enableVertexAttribArray(0)
gl.vertexAttribPointer(1, 3, gl.FLOAT, False, _STRIDE, 3 * 4)    # aColor
gl.enableVertexAttribArray(1)
gl.bindVertexArray(None)


# --- Matrix helpers (numpy, column-major when sent to GL) -----------------

def _perspective(fovy_rad, aspect, near, far):
    f = 1.0 / math.tan(fovy_rad / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def _translate(x, y, z):
    m = np.eye(4, dtype=np.float32)
    m[0, 3] = x
    m[1, 3] = y
    m[2, 3] = z
    return m


def _rotate_y(angle_rad):
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1],
    ], dtype=np.float32)


def _rotate_x(angle_rad):
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1],
    ], dtype=np.float32)


def _mvp_for_time(t):
    aspect = TEX_W / TEX_H
    proj = _perspective(math.radians(45.0), aspect, 0.1, 100.0)
    view = _translate(0.0, 0.0, -5.0)
    model = _rotate_y(t * 0.7) @ _rotate_x(t * 0.4)
    return proj @ view @ model


def render_cube_into_texture():
    gl.bindFramebuffer(gl.FRAMEBUFFER, _fbo)
    gl.viewport(0, 0, TEX_W, TEX_H)
    gl.clearColor(0.10, 0.11, 0.15, 1.0)
    gl.enable(gl.DEPTH_TEST)
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)

    gl.useProgram(_prog)
    mvp = _mvp_for_time(imgui.get_time())
    # GL expects column-major; numpy is row-major, so transpose first.
    gl.uniformMatrix4fv(_uMvp_loc, False, Float32Array.new(mvp.T.flatten().tolist()))

    gl.bindVertexArray(_vao)
    gl.drawArrays(gl.TRIANGLES, 0, 36)

    gl.bindVertexArray(None)
    gl.useProgram(None)
    gl.disable(gl.DEPTH_TEST)
    gl.bindFramebuffer(gl.FRAMEBUFFER, None)


# --- "Show docs" toggle: renders this file's docstring as markdown -------

_show_docs = False


def _docs_window():
    global _show_docs
    if not _show_docs:
        return
    imgui.set_next_window_size(hello_imgui.em_to_vec2(48, 32), imgui.Cond_.first_use_ever)
    expanded, _show_docs = imgui.begin("About this demo", _show_docs)  # type: ignore
    if expanded:
        imgui_md.render_unindented(__doc__ or "")
    imgui.end()


def gui():
    global _show_docs
    render_cube_into_texture()

    imgui.set_next_window_pos(hello_imgui.em_to_vec2(2.0, 2.0), imgui.Cond_.appearing)
    imgui.begin("3D cube via WebGL (Pyodide)")
    imgui.text("Python WebGL renders a depth-tested 3D cube into an FBO;")
    imgui.text("imgui.image() displays the same texture, no readback.")
    imgui.text(f"ImTextureID = {TEXTURE_ID} (constant across frames)")
    imgui.text(f"Texture: {TEX_W} x {TEX_H}")
    _, _show_docs = imgui.checkbox("Show docs", _show_docs)
    imgui.separator()
    imgui.image(imgui.ImTextureRef(TEXTURE_ID), ImVec2(TEX_W, TEX_H))
    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")
    imgui.end()
    _docs_window()


def before_exit():
    # Symmetric cleanup. Browser tab tear-down would handle this for us,
    # but this documents the right pattern: unregister first (so ImGui's
    # renderer stops referencing the slot), then delete the GPU resources.
    webgl.unregister_texture(TEXTURE_ID)
    gl.deleteTexture(_color_tex)
    gl.deleteRenderbuffer(_depth_rb)
    gl.deleteFramebuffer(_fbo)


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.fps_idling.enable_idling = False
    runner_params.app_window_params.window_title = "3D cube via WebGL -> imgui.image (Pyodide)"
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.no_default_window
    )
    runner_params.callbacks.show_gui = gui
    runner_params.callbacks.before_exit = before_exit

    # Markdown for the docs window. (LaTeX not used here, but enabled for
    # consistency with the other webgl playground entries.)
    md_options = imgui_md.MarkdownOptions()
    md_options.with_latex = True
    add_ons_params = immapp.AddOnsParams()
    add_ons_params.with_markdown = True
    add_ons_params.with_markdown_options = md_options

    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
