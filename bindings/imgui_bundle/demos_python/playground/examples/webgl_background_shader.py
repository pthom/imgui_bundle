"""
Custom background using a shader, à la Shadertoy — runs on desktop AND in Pyodide
from the same source file.

The shader is the famous "Seascape" by Alexander Alekseev (TDM, 2014). It's
rendered as the application's background through hello_imgui's
`custom_background` callback, with the ImGui parameter panel composited on top.

Why this demo exists
====================

Desktop Python and Pyodide expose OpenGL through different surfaces:
- Desktop: PyOpenGL (`import OpenGL.GL as GL`), targeting GLSL 330.
- Pyodide: WebGL2 via `js`-interop (`canvas.getContext("webgl2")`),
  targeting GLSL ES 3.00.

Naively, that means two separate demos with two shader-source variants. This
file shows how to keep them as one: a small adapter class (`_GLCompat`,
defined below) presents a PyOpenGL-shaped API over WebGL2 in Pyodide, and
the shader uses a per-platform `SHADER_HEADER` that picks the right `#version`
line. Everything below the platform setup block is identical for desktop and webgl (pyodide).

"""
# ruff: noqa: E402  -- platform-conditional imports are intentionally interleaved with logic
import sys

IS_PYODIDE = sys.platform == "emscripten"


# ******************************************************************************
#
# Platform setup: Wayland workaround (desktop) or WebGL2 adapter (Pyodide)
#
# ******************************************************************************/

if not IS_PYODIDE:
    # Workaround for PyOpenGL 3.1.6+ on Wayland: GLFW (used by immapp / hello_imgui)
    # creates X11/XWayland windows, but PyOpenGL defaults to Wayland EGL, causing a
    # context mismatch. Force the X11 backend before importing OpenGL.
    # See https://github.com/pthom/imgui_bundle/issues/321
    import os
    if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
        os.environ["PYOPENGL_PLATFORM"] = "x11"

    import OpenGL.GL as GL  # pip install PyOpenGL

else:
    # Pyodide: acquire the WebGL2 context that hello_imgui is rendering into,
    # and wrap it in a thin PyOpenGL-shaped adapter so the demo body below
    # stays identical to the desktop version.
    from js import document, Float32Array

    class _GLCompat:
        """
        Minimal PyOpenGL-shaped adapter over a WebGL2 context.

        Implements only the subset used by this demo. Two kinds of methods:
          - Trivial renames (e.g. glCreateShader -> createShader) are forwarded
            mechanically via __getattr__.
          - Methods with a semantic difference (gen/delete signatures, numpy
            buffer upload, ctypes byte-offset, 0-vs-None for unbind, *fv vs
            scalar uniforms, bool-vs-int status) are written out explicitly.
        Constants are forwarded too: GL_FOO -> self._gl.FOO.
        """

        def __init__(self):
            canvas = document.getElementById("canvas")
            self._gl = canvas.getContext("webgl2")
            if self._gl is None:
                raise RuntimeError("Could not acquire WebGL2 context on #canvas")

        # A few standard GL enum values that WebGL doesn't expose on the
        # context object (in JS you'd just use true / false).
        _CONSTANT_FALLBACKS = {"FALSE": 0, "TRUE": 1}

        def __getattr__(self, name):
            if name.startswith("GL_"):
                suffix = name[3:]
                if hasattr(self._gl, suffix):
                    return getattr(self._gl, suffix)
                if suffix in self._CONSTANT_FALLBACKS:
                    return self._CONSTANT_FALLBACKS[suffix]
                raise AttributeError(name)
            if name.startswith("gl") and len(name) > 2 and name[2].isupper():
                return getattr(self._gl, name[2].lower() + name[3:])
            raise AttributeError(name)

        # --- VAO / VBO: WebGL has single-object create/delete, no count arg ---
        def glGenVertexArrays(self, n):
            assert n == 1, "compat layer only supports n=1"
            return self._gl.createVertexArray()

        def glDeleteVertexArrays(self, n, vaos):
            for vao in vaos:
                self._gl.deleteVertexArray(vao)

        def glGenBuffers(self, n):
            assert n == 1, "compat layer only supports n=1"
            return self._gl.createBuffer()

        def glGenFramebuffers(self, n):
            assert n == 1, "compat layer only supports n=1"
            return self._gl.createFramebuffer()

        def glDeleteFramebuffers(self, n, fbos):
            for fbo in fbos:
                self._gl.deleteFramebuffer(fbo)

        def glGenTextures(self, n):
            assert n == 1, "compat layer only supports n=1"
            return self._gl.createTexture()

        def glDeleteTextures(self, n, textures):
            for tex in textures:
                self._gl.deleteTexture(tex)

        # --- 0-vs-None: PyOpenGL idiom is bind(target, 0) to unbind ---
        def glBindBuffer(self, target, buffer):
            self._gl.bindBuffer(target, buffer or None)

        def glBindVertexArray(self, vao):
            self._gl.bindVertexArray(vao or None)

        def glUseProgram(self, program):
            self._gl.useProgram(program or None)

        def glBindFramebuffer(self, target, fbo):
            self._gl.bindFramebuffer(target, fbo or None)

        def glBindTexture(self, target, texture):
            self._gl.bindTexture(target, texture or None)

        # --- Buffer upload: numpy float32 array -> Float32Array ---
        def glBufferData(self, target, data, usage):
            if hasattr(data, "tolist"):
                data = data.tolist()
            self._gl.bufferData(target, Float32Array.new(data), usage)

        # --- Vertex attrib offset: ctypes.c_void_p -> int byte offset ---
        def glVertexAttribPointer(self, index, size, type_, normalized, stride, offset):
            if hasattr(offset, "value"):
                offset = offset.value or 0
            self._gl.vertexAttribPointer(index, size, type_, bool(normalized), stride, offset)

        # --- *fv uniforms: WebGL's uniform{2,3,4}f takes scalars ---
        def glUniform2fv(self, loc, count, v):
            assert count == 1
            self._gl.uniform2f(loc, v[0], v[1])

        def glUniform3fv(self, loc, count, v):
            assert count == 1
            self._gl.uniform3f(loc, v[0], v[1], v[2])

        def glUniform4fv(self, loc, count, v):
            assert count == 1
            self._gl.uniform4f(loc, v[0], v[1], v[2], v[3])

        # --- Status queries: WebGL returns bool/None where PyOpenGL returns int/str ---
        def glGetShaderiv(self, shader, pname):
            return self._gl.getShaderParameter(shader, pname)

        def glGetProgramiv(self, program, pname):
            return self._gl.getProgramParameter(program, pname)

        def glGetShaderInfoLog(self, shader):
            return self._gl.getShaderInfoLog(shader) or ""

        def glGetProgramInfoLog(self, program):
            return self._gl.getProgramInfoLog(program) or ""

    GL = _GLCompat()


# Per-platform shader header. Body of the shader source is identical:
# GLSL 330 core and GLSL ES 3.00 share the relevant `in`/`out` syntax and
# function set used here.
if IS_PYODIDE:
    SHADER_HEADER = "#version 300 es\nprecision highp float;\n"
else:
    SHADER_HEADER = "#version 330 core\n"


from imgui_bundle import hello_imgui, imgui, immapp, ImVec2, ImVec4, imgui_md

from dataclasses import dataclass
from typing import Dict, Any
import numpy
import ctypes


# ******************************************************************************
#
# Uniforms Utilities
#
# ******************************************************************************/

@dataclass
class MyVec3:
    """Helper struct to store 3D float uniforms"""
    x: float
    y: float
    z: float


def apply_uniform(location, value):
    """Transmit any uniform type to the shader"""
    if isinstance(value, int):
        GL.glUniform1i(location, value)
    elif isinstance(value, float):
        GL.glUniform1f(location, value)
    elif isinstance(value, MyVec3):
        GL.glUniform3fv(location, 1, (value.x, value.y, value.z))
    elif isinstance(value, ImVec2):
        GL.glUniform2fv(location, 1, (value.x, value.y))
    elif isinstance(value, ImVec4):
        GL.glUniform4fv(location, 1, (value.x, value.y, value.z, value.w))
    else:
        raise TypeError("Unsupported type")


class IUniform:
    """Base uniform class: can be used to store a uniform of any type"""
    location: Any  # int on desktop, WebGLUniformLocation in Pyodide

    def __init__(self):
        self.location = 0

    def store_location(self, shader_program, name: str) -> None:
        self.location = GL.glGetUniformLocation(shader_program, name)

    def apply(self) -> None:
        raise NotImplementedError("This method should be overridden in subclasses.")


class Uniform(IUniform):
    """Concrete uniform class: can be used to store a uniform of a specific type"""
    value: Any

    def __init__(self, initial_value: Any) -> None:
        super().__init__()
        self.value = initial_value

    def apply(self) -> None:  # override
        apply_uniform(self.location, self.value)


class UniformsList:
    """Helper struct to store a list of uniforms"""
    uniforms: Dict[str, IUniform]

    def __init__(self):
        self.uniforms = {}

    def add_uniform(self, name: str, initial_value: Any) -> None:
        self.uniforms[name] = Uniform(initial_value)

    def store_uniform_locations(self, shader_program) -> None:
        """ Query the shader program for the uniform locations
        (should be called once after the shader program is created)
        """
        for name, uniform in self.uniforms.items():
            uniform.store_location(shader_program, name)

    def apply_uniforms(self) -> None:
        """transmits the uniform values to the shader"""
        for uniform in self.uniforms.values():
            uniform.apply()

    def get_uniform_value(self, name: str) -> Any:
        """Gets a uniform value"""
        assert name in self.uniforms, "Uniform not found"
        uniform = self.uniforms[name]
        return uniform.value

    def set_uniform_value(self, name: str, value: Any) -> None:
        """Modifies a uniform value"""
        assert name in self.uniforms, "Uniform not found"
        self.uniforms[name].value = value


# ******************************************************************************
#
# Shader Utilities
#
# *****************************************************************************/

def fail_on_shader_link_error(shader_program) -> None:
    is_linked = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    if not is_linked:
        info_log = GL.glGetProgramInfoLog(shader_program)
        print(f"ERROR::SHADER::PROGRAM::LINKING_FAILED\n{info_log}", file=sys.stderr)
        assert is_linked, "Shader program linking failed"


def fail_on_shader_compile_error(shader) -> None:
    shader_compile_success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not shader_compile_success:
        info_log = GL.glGetShaderInfoLog(shader)
        print(f"ERROR::SHADER::VERTEX::COMPILATION_FAILED\n{info_log}", file=sys.stderr)
        assert shader_compile_success, "Shader compilation failed"


def fail_on_opengl_error() -> None:
    count_opengl_error = 0
    while (err := GL.glGetError()) != GL.GL_NO_ERROR:
        print(f"OpenGL error: {err}", file=sys.stderr)
        count_opengl_error += 1
    assert count_opengl_error == 0, "OpenGL errors occurred"


def compile_shader(shader_type: int, source: str):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    fail_on_shader_compile_error(shader)
    return shader


def create_shader_program(vertex_shader_source: str, fragment_shader_source: str):
    vertex_shader = compile_shader(GL.GL_VERTEX_SHADER, vertex_shader_source)
    fragment_shader = compile_shader(GL.GL_FRAGMENT_SHADER, fragment_shader_source)

    # Create shader program
    shader_program = GL.glCreateProgram()
    GL.glAttachShader(shader_program, vertex_shader)
    GL.glAttachShader(shader_program, fragment_shader)
    GL.glLinkProgram(shader_program)
    fail_on_shader_link_error(shader_program)

    # Delete shader objects once linked
    GL.glDeleteShader(vertex_shader)
    GL.glDeleteShader(fragment_shader)

    # Check for any OpenGL errors
    fail_on_opengl_error()

    return shader_program


def create_full_screen_quad_vao():
    # Define the vertex data for a full-screen quad
    vertices = [
        # positions   # texCoords
        -1.0, -1.0,  0.0, 0.0, # bottom left  (0)
        1.0, -1.0,  1.0, 0.0, # bottom right (1)
        -1.0,  1.0,  0.0, 1.0, # top left     (2)
        1.0,  1.0,  1.0, 1.0  # top right    (3)
    ]

    # Generate and bind the VAO
    vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vao)

    # Generate and bind the VBO
    vbo = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)

    # Fill the VBO with vertex data
    GL.glBufferData(GL.GL_ARRAY_BUFFER, numpy.array(vertices, dtype='float32'), GL.GL_STATIC_DRAW)

    # Set the vertex attribute pointers
    # Position attribute
    GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, ctypes.c_void_p(0))
    GL.glEnableVertexAttribArray(0)
    # Texture coordinate attribute
    GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
    GL.glEnableVertexAttribArray(1)

    # Unbind the VAO (and VBO)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)

    # Check for any OpenGL errors
    fail_on_opengl_error()

    return vao


# ******************************************************************************
#
# Offscreen render target + upscale-blit (the perf trick)
#
# We render the expensive seascape shader to a low-resolution texture, then
# upscale to the default framebuffer with a trivial blit pass. This decouples
# fragment-shader cost from window size, which is the actual bottleneck on
# Firefox with a large window.
#
# ******************************************************************************/

class OffscreenTarget:
    """Color texture + framebuffer at a fixed resolution."""
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, w, h, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        self.fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
                                  GL.GL_TEXTURE_2D, self.texture, 0)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def destroy(self):
        GL.glDeleteFramebuffers(1, [self.fbo])
        GL.glDeleteTextures(1, [self.texture])


BLIT_VERTEX_SHADER_SOURCE = SHADER_HEADER + """
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;
out vec2 vUv;
void main()
{
    gl_Position = vec4(aPos, 1.0);
    vUv = aTexCoord;
}
"""

BLIT_FRAGMENT_SHADER_SOURCE = SHADER_HEADER + """
in vec2 vUv;
out vec4 FragColor;
uniform sampler2D uTex;
void main()
{
    FragColor = texture(uTex, vUv);
}
"""


# ******************************************************************************
#
# Shader code
#
# ******************************************************************************/

# See https://www.shadertoy.com/view/Ms2SD1 / Many thanks to Alexander Alekseev aka TDM

VERTEX_SHADER_SOURCE = SHADER_HEADER + """
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

void main()
{
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
"""

# See https://www.shadertoy.com/view/Ms2SD1 / Many thanks to Alexander Alekseev aka TDM
FRAGMENT_SHADER_SOURCE = SHADER_HEADER + """
/*
 * "Seascape" by Alexander Alekseev aka TDM - 2014
 * License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * Contact: tdmaav@gmail.com
 */

in vec2 TexCoord;
out vec4 FragColor;


uniform vec2 iResolution;  // Window resolution
uniform float iTime;      // Shader elapsed time
uniform vec2 iMouse;      // Mouse position


const int NUM_STEPS = 8;
const float PI	 	= 3.141592;
const float EPSILON	= 1e-3;
#define EPSILON_NRM (0.1 / iResolution.x)

// sea
const int ITER_GEOMETRY = 3;
const int ITER_FRAGMENT = 5;

//const float SEA_HEIGHT = 0.6;
//const float SEA_CHOPPY = 4.0;
//const float SEA_SPEED = 0.8;
//const float SEA_FREQ = 0.16;
//const vec3 SEA_WATER_COLOR = vec3(0.8,0.9,0.6)*0.6;
//const vec3 SEA_BASE = vec3(0.0,0.09,0.18);

uniform float SEA_HEIGHT;
uniform float SEA_CHOPPY;
uniform float SEA_SPEED;
uniform float SEA_FREQ;
uniform vec3 SEA_WATER_COLOR;
uniform vec3 SEA_BASE;

#define SEA_TIME (1.0 + iTime * SEA_SPEED)
const mat2 octave_m = mat2(1.6,1.2,-1.2,1.6);

// math
mat3 fromEuler(vec3 ang) {
	vec2 a1 = vec2(sin(ang.x),cos(ang.x));
    vec2 a2 = vec2(sin(ang.y),cos(ang.y));
    vec2 a3 = vec2(sin(ang.z),cos(ang.z));
    mat3 m;
    m[0] = vec3(a1.y*a3.y+a1.x*a2.x*a3.x,a1.y*a2.x*a3.x+a3.y*a1.x,-a2.y*a3.x);
	m[1] = vec3(-a2.y*a1.x,a1.y*a2.y,a2.x);
	m[2] = vec3(a3.y*a1.x*a2.x+a1.y*a3.x,a1.x*a3.x-a1.y*a3.y*a2.x,a2.y*a3.y);
	return m;
}
float hash( vec2 p ) {
	float h = dot(p,vec2(127.1,311.7));
    return fract(sin(h)*43758.5453123);
}
float noise( in vec2 p ) {
    vec2 i = floor( p );
    vec2 f = fract( p );
	vec2 u = f*f*(3.0-2.0*f);
    return -1.0+2.0*mix( mix( hash( i + vec2(0.0,0.0) ),
                     hash( i + vec2(1.0,0.0) ), u.x),
                mix( hash( i + vec2(0.0,1.0) ),
                     hash( i + vec2(1.0,1.0) ), u.x), u.y);
}

// lighting
float diffuse(vec3 n,vec3 l,float p) {
    return pow(dot(n,l) * 0.4 + 0.6,p);
}
float specular(vec3 n,vec3 l,vec3 e,float s) {
    float nrm = (s + 8.0) / (PI * 8.0);
    return pow(max(dot(reflect(e,n),l),0.0),s) * nrm;
}

// sky
vec3 getSkyColor(vec3 e) {
    e.y = (max(e.y,0.0)*0.8+0.2)*0.8;
    return vec3(pow(1.0-e.y,2.0), 1.0-e.y, 0.6+(1.0-e.y)*0.4) * 1.1;
}

// sea
float sea_octave(vec2 uv, float choppy) {
    uv += noise(uv);
    vec2 wv = 1.0-abs(sin(uv));
    vec2 swv = abs(cos(uv));
    wv = mix(wv,swv,wv);
    return pow(1.0-pow(wv.x * wv.y,0.65),choppy);
}

float map(vec3 p) {
    float freq = SEA_FREQ;
    float amp = SEA_HEIGHT;
    float choppy = SEA_CHOPPY;
    vec2 uv = p.xz; uv.x *= 0.75;

    float d, h = 0.0;
    for(int i = 0; i < ITER_GEOMETRY; i++) {
        d = sea_octave((uv+SEA_TIME)*freq,choppy);
        d += sea_octave((uv-SEA_TIME)*freq,choppy);
        h += d * amp;
        uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
    }
    return p.y - h;
}

float map_detailed(vec3 p) {
    float freq = SEA_FREQ;
    float amp = SEA_HEIGHT;
    float choppy = SEA_CHOPPY;
    vec2 uv = p.xz; uv.x *= 0.75;

    float d, h = 0.0;
    for(int i = 0; i < ITER_FRAGMENT; i++) {
        d = sea_octave((uv+SEA_TIME)*freq,choppy);
        d += sea_octave((uv-SEA_TIME)*freq,choppy);
        h += d * amp;
        uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
    }
    return p.y - h;
}

vec3 getSeaColor(vec3 p, vec3 n, vec3 l, vec3 eye, vec3 dist) {
    float fresnel = clamp(1.0 - dot(n,-eye), 0.0, 1.0);
    fresnel = min(pow(fresnel,3.0), 0.5);

    vec3 reflected = getSkyColor(reflect(eye,n));
    vec3 refracted = SEA_BASE + diffuse(n,l,80.0) * SEA_WATER_COLOR * 0.12;

    vec3 color = mix(refracted,reflected,fresnel);

    float atten = max(1.0 - dot(dist,dist) * 0.001, 0.0);
    color += SEA_WATER_COLOR * (p.y - SEA_HEIGHT) * 0.18 * atten;

    color += vec3(specular(n,l,eye,60.0));

    return color;
}

// tracing
vec3 getNormal(vec3 p, float eps) {
    vec3 n;
    n.y = map_detailed(p);
    n.x = map_detailed(vec3(p.x+eps,p.y,p.z)) - n.y;
    n.z = map_detailed(vec3(p.x,p.y,p.z+eps)) - n.y;
    n.y = eps;
    return normalize(n);
}

float heightMapTracing(vec3 ori, vec3 dir, out vec3 p) {
    float tm = 0.0;
    float tx = 1000.0;
    float hx = map(ori + dir * tx);
    if(hx > 0.0) {
        p = ori + dir * tx;
        return tx;
    }
    float hm = map(ori + dir * tm);
    float tmid = 0.0;
    for(int i = 0; i < NUM_STEPS; i++) {
        tmid = mix(tm,tx, hm/(hm-hx));
        p = ori + dir * tmid;
        float hmid = map(p);
        if(hmid < 0.0) {
            tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
    }
    return tmid;
}

vec3 getPixel(in vec2 coord, float time) {
    vec2 uv = coord / iResolution.xy;
    uv = uv * 2.0 - 1.0;
    uv.x *= iResolution.x / iResolution.y;

    // ray
    vec3 ang = vec3(sin(time*3.0)*0.1,sin(time)*0.2+0.3,time);
    vec3 ori = vec3(0.0,3.5,time*5.0);
    vec3 dir = normalize(vec3(uv.xy,-2.0)); dir.z += length(uv) * 0.14;
    dir = normalize(dir) * fromEuler(ang);

    // tracing
    vec3 p;
    heightMapTracing(ori,dir,p);
    vec3 dist = p - ori;
    vec3 n = getNormal(p, dot(dist,dist) * EPSILON_NRM);
    vec3 light = normalize(vec3(0.0,1.0,0.8));

    // color
    return mix(
        getSkyColor(dir),
        getSeaColor(p,n,light,dir,dist),
        pow(smoothstep(0.0,-0.02,dir.y),0.2));
}

// #define AA
void main()
{
    vec2 fragCoord = TexCoord * iResolution;
    float time = iTime * 0.3 + iMouse.x * 0.01;

#ifdef AA
    vec3 color = vec3(0.0);
    for(int i = -1; i <= 1; i++) {
        for(int j = -1; j <= 1; j++) {
            vec2 uv = fragCoord + vec2(i, j) / 3.0;
            color += getPixel(uv, time);
        }
    }
    color /= 9.0;
#else
    vec3 color = getPixel(fragCoord, time);
#endif

    FragColor = vec4(pow(color, vec3(0.65)), 1.0);
}
"""


# ******************************************************************************
#
# Our App starts here
#
# ******************************************************************************/


class AppState:
    """
    Our global app state, containing shader program, VAO, and uniforms.
    """
    shader_program: Any # the shader program that is compiled and linked at startup
    full_screen_quad_vao: Any # the VAO of a full-screen quad
    uniforms: UniformsList # the uniforms of the shader program
    blit_program: Any # the program that upscales the offscreen render
    blit_tex_location: Any # uniform location of the blit shader's `uTex`
    offscreen: Any # OffscreenTarget, recreated on resize / scale change
    render_scale: float # 0 < scale <= 1.0; lower = faster, blurrier

    def __init__(self):
        self.uniforms = UniformsList()
        # self.shader_program and self.full_screen_quad_vao will be initialized later by init_app_resources_3d()

        self.offscreen = None
        self.render_scale = 0.5

        # Initialize uniforms with their initial values
        self.uniforms.add_uniform("SEA_HEIGHT", 0.6)
        self.uniforms.add_uniform("SEA_CHOPPY", 4.0)
        self.uniforms.add_uniform("SEA_SPEED", 0.8)
        self.uniforms.add_uniform("SEA_FREQ", 0.16)
        self.uniforms.add_uniform("SEA_WATER_COLOR", MyVec3(0.8 * 0.6, 0.9 * 0.6, 0.6 * 0.6))
        self.uniforms.add_uniform("SEA_BASE", MyVec3(0.0, 0.09, 0.18))
        self.uniforms.add_uniform("iResolution", ImVec2(100.0, 100.0))
        self.uniforms.add_uniform("iTime", 0.0)
        self.uniforms.add_uniform("iMouse", ImVec2(0.0, 0.0))

    def apply_uniforms(self):
        """Transmit new uniforms values to the shader."""
        self.uniforms.apply_uniforms()

    def store_uniform_locations(self):
        """Get uniforms locations in the shader program."""
        self.uniforms.store_uniform_locations(self.shader_program)

    def init_app_resources_3d(self, vertex_shader_source, fragment_shader_source):
        """Initialize application resources."""
        # In Pyodide the WebGL context is shared across the playground's demo
        # switches. When we land here on a re-load, the GL error queue may
        # already contain stale errors caused by the previous demo or by
        # hello_imgui's own lifecycle setup (e.g. a benign readPixels format
        # mismatch). Drain those before doing any of our own GL work, so the
        # subsequent fail_on_opengl_error() checks only observe errors caused
        # by this demo's shader/VAO setup.
        while GL.glGetError() != GL.GL_NO_ERROR:
            pass

        self.shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
        self.full_screen_quad_vao = create_full_screen_quad_vao()
        self.store_uniform_locations()
        self.blit_program = create_shader_program(BLIT_VERTEX_SHADER_SOURCE, BLIT_FRAGMENT_SHADER_SOURCE)
        self.blit_tex_location = GL.glGetUniformLocation(self.blit_program, "uTex")

    def ensure_offscreen(self, full_w: int, full_h: int):
        """Recreate the offscreen target if the viewport or render_scale changed."""
        target_w = max(1, int(full_w * self.render_scale))
        target_h = max(1, int(full_h * self.render_scale))
        if self.offscreen is None or self.offscreen.w != target_w or self.offscreen.h != target_h:
            if self.offscreen is not None:
                self.offscreen.destroy()
            self.offscreen = OffscreenTarget(target_w, target_h)

    def destroy_app_resources_3d(self):
        """Destroy application resources."""
        GL.glDeleteProgram(self.shader_program)
        GL.glDeleteProgram(self.blit_program)
        GL.glDeleteVertexArrays(1, [self.full_screen_quad_vao])
        if self.offscreen is not None:
            self.offscreen.destroy()


def scaled_display_size():
    """Returns the size of the window in pixels
    for retina displays, io.DisplaySize is the size of the window in points (logical pixels)
    but we need the size in pixels. So we scale io.DisplaySize by io.DisplayFramebufferScale
    ."""
    io = imgui.get_io()
    return ImVec2(io.display_size[0] * io.display_framebuffer_scale[0],
                  io.display_size[1] * io.display_framebuffer_scale[1])


def custom_background(app_state: AppState):
    """Custom background callback: displays the sea shader.

    Two-pass rendering: the seascape draws into a low-resolution offscreen
    target, then a trivial blit shader upscales it to the default framebuffer.
    """
    full_size = scaled_display_size()
    full_w, full_h = int(full_size.x), int(full_size.y)
    app_state.ensure_offscreen(full_w, full_h)
    low = app_state.offscreen

    # Pass 1: render the seascape into the low-res offscreen target
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, low.fbo)
    GL.glViewport(0, 0, low.w, low.h)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    GL.glUseProgram(app_state.shader_program)

    # Set automatic uniforms values
    app_state.uniforms.set_uniform_value("iResolution", ImVec2(float(low.w), float(low.h)))
    app_state.uniforms.set_uniform_value("iTime", imgui.get_time())
    app_state.uniforms.set_uniform_value("iMouse", ImVec2(0.0, 0.0))

    app_state.apply_uniforms()

    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glBindVertexArray(app_state.full_screen_quad_vao)
    GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

    # Pass 2: upscale-blit into the default framebuffer at full resolution
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
    GL.glViewport(0, 0, full_w, full_h)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glUseProgram(app_state.blit_program)
    GL.glActiveTexture(GL.GL_TEXTURE0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, low.texture)
    GL.glUniform1i(app_state.blit_tex_location, 0)
    GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glBindVertexArray(0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glUseProgram(0)


# --- "Show docs" toggle: renders this file's docstring as markdown -------

_show_docs = False


def _docs_window():
    global _show_docs
    if not _show_docs:
        return
    imgui.set_next_window_size(hello_imgui.em_to_vec2(48, 32), imgui.Cond_.first_use_ever)
    expanded, _show_docs = imgui.begin("About this demo", _show_docs)
    if expanded:
        imgui_md.render_unindented(__doc__ or "")
    imgui.end()


def gui(app_state: AppState):
    """GUI for modifying shader parameters."""
    global _show_docs
    imgui.set_next_window_pos(hello_imgui.em_to_vec2(0.0, 0.0), imgui.Cond_.appearing)
    imgui.set_next_window_size(hello_imgui.em_to_vec2(31.0, 18.0), imgui.Cond_.appearing)
    imgui.begin("Shader parameters")

    imgui_md.render_unindented("""
        Shader: "Seascape" by Alexander Alekseev aka TDM - 2014 - [Shadertoy](https://www.shadertoy.com/view/Ms2SD1)
    """)
    _, _show_docs = imgui.checkbox("Show docs", _show_docs)
    imgui.separator()

    # Render-scale: lower = faster, blurrier. The seascape is ray-marched
    # per pixel, so cost scales with the offscreen resolution.
    _, app_state.render_scale = imgui.slider_float("Render scale", app_state.render_scale, 0.1, 1.0)
    if app_state.offscreen is not None:
        imgui.text(f"Shader resolution: {app_state.offscreen.w} x {app_state.offscreen.h}")

    # Modify the uniforms values
    uniforms = app_state.uniforms

    value = uniforms.get_uniform_value("SEA_HEIGHT")
    _, value = imgui.slider_float("SEA_HEIGHT", value, 0.1, 2.1)
    uniforms.set_uniform_value("SEA_HEIGHT", value)

    value = uniforms.get_uniform_value("SEA_CHOPPY")
    _, value = imgui.slider_float("SEA_CHOPPY", value, 0.1, 10.0)
    uniforms.set_uniform_value("SEA_CHOPPY", value)

    color_vec = uniforms.get_uniform_value("SEA_BASE")
    color_list = ImVec4(color_vec.x, color_vec.y, color_vec.z, 1.0)
    _, color_list = imgui.color_edit3("SEA_BASE", color_list)
    color_vec = MyVec3(color_list[0], color_list[1], color_list[2])
    uniforms.set_uniform_value("SEA_BASE", color_vec)

    value = uniforms.get_uniform_value("SEA_SPEED")
    _, value = imgui.slider_float("SEA_SPEED", value, 0.1, 3.0)
    uniforms.set_uniform_value("SEA_SPEED", value)

    value = uniforms.get_uniform_value("SEA_FREQ")
    _, value = imgui.slider_float("SEA_FREQ", value, 0.01, 0.5)
    uniforms.set_uniform_value("SEA_FREQ", value)

    imgui.text(f"FPS: {hello_imgui.frame_rate():.1f}")

    imgui.end()
    _docs_window()


def main():
    # Our global app state
    app_state = AppState()

    # Hello ImGui parameters
    runner_params = hello_imgui.RunnerParams()

    # Disable idling so that the shader runs at full speed
    runner_params.fps_idling.enable_idling = False
    runner_params.app_window_params.window_geometry.size = (1200, 720)
    runner_params.app_window_params.window_title = "Hello ImGui: custom 3D background - shader by Alexander Alekseev aka TDM - 2014"
    # Do not create a default ImGui window, so that the shader occupies the whole display
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.no_default_window

    # Callbacks
    # post_init is called after the ImGui context is created, and after OpenGL is initialized
    runner_params.callbacks.post_init = lambda: app_state.init_app_resources_3d(VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)
    # before_exit is called before the ImGui context is destroyed, and before OpenGL is deinitialized
    runner_params.callbacks.before_exit = lambda: app_state.destroy_app_resources_3d()
    # show_gui is called every frame, and is used to display the ImGui widgets
    runner_params.callbacks.show_gui = lambda: gui(app_state)
    # custom_background is called every frame, and is used to display the custom background
    runner_params.callbacks.custom_background = lambda: custom_background(app_state)

    # Let's go!
    md_options = imgui_md.MarkdownOptions()
    md_options.with_latex = True
    add_ons_params = immapp.AddOnsParams()
    add_ons_params.with_markdown = True
    add_ons_params.with_markdown_options = md_options
    immapp.run(runner_params, add_ons_params)

    return 0


if __name__ == "__main__":
    main()
