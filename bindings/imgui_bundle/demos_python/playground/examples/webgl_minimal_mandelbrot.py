"""
Minimal WebGL fragment shader as the application background.

**Pyodide only.** This demo uses Python's `js` interop to call the browser's
WebGL2 API directly. There is no equivalent on desktop, where you would
use PyOpenGL instead. To write a *single* source file that runs on both
desktop (PyOpenGL) and Pyodide (WebGL2), see the companion example
`webgl_background_shader.py` — it wraps a small adapter class around the
WebGL2 context to expose a PyOpenGL-shaped API, so the rest of the demo
body can be identical for both targets.

## The shader

An animated Mandelbrot zoom near $c_0 = -0.7453 + 0.1127i$, a famous
spiral point in the Seahorse Valley region.

The Mandelbrot set $M$ is the set of complex numbers $c$ for which the
iteration

$$z_{n+1} = z_n^{\\,2} + c, \\quad z_0 = 0$$

stays bounded as $n \\to \\infty$. In practice the orbit either stays
inside the disk $|z| \\le 2$ forever, or escapes to infinity — and the
escape can be detected by the test $|z_n|^2 > 4$. We color each pixel by
the iteration index $n$ at which it first escapes, with points that
survive `MAX_ITER` steps drawn dark (likely inside the set).

## The integration point

`runner_params.callbacks.custom_background`. hello_imgui calls this once
per frame, between clearing the framebuffer and drawing the ImGui UI on
top. Whatever WebGL we issue inside the callback ends up behind the ImGui
windows.

## The hop from Python to WebGL

`getContext("webgl2")` on the canvas hello_imgui already created. The
WebGL spec guarantees that repeated `getContext("webgl2")` calls return
the same context, so we share hello_imgui's GL state and framebuffer.
No copies, no readback.
"""
from imgui_bundle import hello_imgui, imgui, immapp, imgui_md
from js import document, Float32Array  # type: ignore[import-not-found]


# --- WebGL2 context (shared with hello_imgui's renderer) ------------------

_canvas = document.getElementById("canvas")
gl = _canvas.getContext("webgl2")
if gl is None:
    raise RuntimeError("Could not acquire WebGL2 context on #canvas")


# --- Shader sources -------------------------------------------------------
# Vertex shader: a single oversized triangle that covers the entire NDC
# quad, so the fragment shader runs once per pixel of the framebuffer.

VS = """#version 300 es
precision highp float;
layout(location = 0) in vec2 aPos;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

# Fragment shader: animated Mandelbrot. iTime drives an exponential
# zoom that resets every 12 seconds.

FS = """#version 300 es
precision highp float;

out vec4 FragColor;
uniform vec2 iResolution;
uniform float iTime;

const int MAX_ITER = 200;

void main() {
    // Map fragment coord to a centered, square-aspect plane coordinate.
    vec2 uv = (gl_FragCoord.xy / iResolution.xy - 0.5) * 2.0;
    uv.x *= iResolution.x / iResolution.y;

    // Zoom toward a known interesting point (a "spiral" in the Seahorse
    // Valley region). Reset every ~12 seconds to loop the animation.
    float zoom = exp(-mod(iTime * 1.5, 12.0));
    vec2 c = vec2(-0.7453, 0.11294) + uv * zoom;

    // Standard escape-time iteration.
    vec2 z = vec2(0.0);
    int i;
    for (i = 0; i < MAX_ITER; i++) {
        z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
        if (dot(z, z) > 4.0) break;
    }

    if (i == MAX_ITER) {
        // Inside the set: very dark.
        FragColor = vec4(0.05, 0.0, 0.10, 1.0);
    } else {
        // Outside: cosine palette indexed by iteration count.
        float t = float(i) / float(MAX_ITER);
        vec3 col = 0.5 + 0.5 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + t * 4.0));
        FragColor = vec4(col, 1.0);
    }
}
"""


# --- Compile + link -------------------------------------------------------

def _compile(stage, src):
    s = gl.createShader(stage)
    gl.shaderSource(s, src)
    gl.compileShader(s)
    if not gl.getShaderParameter(s, gl.COMPILE_STATUS):
        raise RuntimeError(gl.getShaderInfoLog(s))
    return s


_prog = gl.createProgram()
gl.attachShader(_prog, _compile(gl.VERTEX_SHADER, VS))
gl.attachShader(_prog, _compile(gl.FRAGMENT_SHADER, FS))
gl.linkProgram(_prog)
if not gl.getProgramParameter(_prog, gl.LINK_STATUS):
    raise RuntimeError(gl.getProgramInfoLog(_prog))

_uResolution_loc = gl.getUniformLocation(_prog, "iResolution")
_uTime_loc = gl.getUniformLocation(_prog, "iTime")


# --- Full-screen triangle -------------------------------------------------
# Three vertices spanning a 4x4 box in NDC; the GPU clips to the [-1,+1]
# screen, so the visible result is a full-screen quad.

_vao = gl.createVertexArray()
gl.bindVertexArray(_vao)
_vbo = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, _vbo)
gl.bufferData(gl.ARRAY_BUFFER,
              Float32Array.new([-1.0, -1.0, 3.0, -1.0, -1.0, 3.0]),
              gl.STATIC_DRAW)
gl.vertexAttribPointer(0, 2, gl.FLOAT, False, 0, 0)
gl.enableVertexAttribArray(0)
gl.bindVertexArray(None)


# --- hello_imgui callbacks ------------------------------------------------

def custom_background():
    io = imgui.get_io()
    w = int(io.display_size[0] * io.display_framebuffer_scale[0])
    h = int(io.display_size[1] * io.display_framebuffer_scale[1])

    gl.viewport(0, 0, w, h)
    gl.useProgram(_prog)
    gl.uniform2f(_uResolution_loc, float(w), float(h))
    gl.uniform1f(_uTime_loc, imgui.get_time())
    gl.bindVertexArray(_vao)
    gl.drawArrays(gl.TRIANGLES, 0, 3)
    gl.bindVertexArray(None)
    gl.useProgram(None)


# --- "Show docs" toggle: renders this file's docstring as markdown ------

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
    imgui.set_next_window_pos(hello_imgui.em_to_vec2(2.0, 2.0), imgui.Cond_.appearing)
    imgui.begin("Minimal Mandelbrot")
    imgui.text("Animated Mandelbrot zoom rendered as the app background.")
    imgui.text("Pyodide WebGL2 + hello_imgui custom_background callback.")
    _, _show_docs = imgui.checkbox("Show docs", _show_docs)
    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")
    imgui.end()
    _docs_window()


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.fps_idling.enable_idling = False
    runner_params.app_window_params.window_title = "Minimal Mandelbrot (Pyodide WebGL)"
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.no_default_window
    )
    runner_params.callbacks.custom_background = custom_background
    runner_params.callbacks.show_gui = gui

    # Markdown + LaTeX for the docs window.
    add_ons_params = immapp.AddOnsParams()
    add_ons_params.with_latex = True
    add_ons_params.with_markdown = True

    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
