from imgui_bundle import hello_imgui, imgui, immapp, ImVec2, ImVec4, imgui_md
from imgui_bundle.demos_python import demo_utils

import OpenGL.GL as GL  # type: ignore

from dataclasses import dataclass
import sys
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
    location: int

    def __init__(self):
        self.location = 0

    def store_location(self, shader_program: int, name: str) -> None:
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

    def store_uniform_locations(self, shader_program: int) -> None:
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

def fail_on_shader_link_error(shader_program: int) -> None:
    is_linked = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    if not is_linked:
        info_log = GL.glGetProgramInfoLog(shader_program)
        print(f"ERROR::SHADER::PROGRAM::LINKING_FAILED\n{info_log}", file=sys.stderr)
        assert is_linked, "Shader program linking failed"


def fail_on_shader_compile_error(shader: int) -> None:
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


def compile_shader(shader_type: int, source: str) -> int:
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    fail_on_shader_compile_error(shader)
    return shader


def create_shader_program(vertex_shader_source: str, fragment_shader_source: str) -> int:
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


def create_full_screen_quad_vao() -> int:
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
# Shader code
#
# ******************************************************************************/

# See https://www.shadertoy.com/view/Ms2SD1 / Many thanks to Alexander Alekseev aka TDM
# This is an old shader, so it uses GLSL 100


VERTEX_SHADER_SOURCE = """#version 100
precision mediump float;
attribute vec3 aPos;
attribute vec2 aTexCoord;

varying vec2 TexCoord;


void main()
{
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
"""

# See https://www.shadertoy.com/view/Ms2SD1 / Many thanks to Alexander Alekseev aka TDM
FRAGMENT_SHADER_SOURCE = """#version 100
precision mediump float;
/*
 * "Seascape" by Alexander Alekseev aka TDM - 2014
 * License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * Contact: tdmaav@gmail.com
 */


varying vec2 TexCoord;
vec4 FragColor;


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

    // Compute uv based on fragCoord
    //    vec2 uv = fragCoord / iResolution.xy;
    //    uv = uv * 2.0 - 1.0;
    //    uv.x *= iResolution.x / iResolution.y;

#ifdef AA
    vec3 color = vec3(0.0);
    // Anti-aliasing loop (optional, can be removed for performance)
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

    // Post-processing (adjust as needed)
    FragColor = vec4(pow(color, vec3(0.65)), 1.0);

    gl_FragColor = FragColor;
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
    shader_program: int # the shader program that is compiled and linked at startup
    full_screen_quad_vao: int # the VAO of a full-screen quad
    uniforms: UniformsList # the uniforms of the shader program

    def __init__(self):
        self.uniforms = UniformsList()
        # self.shader_program and self.full_screen_quad_vao will be initialized later by init_app_resources_3d()

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
        self.shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
        self.full_screen_quad_vao = create_full_screen_quad_vao()
        self.store_uniform_locations()

    def destroy_app_resources_3d(self):
        """Destroy application resources."""
        GL.glDeleteProgram(self.shader_program)
        GL.glDeleteVertexArrays(1, [self.full_screen_quad_vao])


def scaled_display_size():
    """Returns the size of the window in pixels
    for retina displays, io.DisplaySize is the size of the window in points (logical pixels)
    but we need the size in pixels. So we scale io.DisplaySize by io.DisplayFramebufferScale
    ."""
    io = imgui.get_io()
    return ImVec2(io.display_size[0] * io.display_framebuffer_scale[0],
                  io.display_size[1] * io.display_framebuffer_scale[1])


def custom_background(app_state: AppState):
    """Custom background callback: displays the sea shader."""
    display_size = scaled_display_size()
    GL.glViewport(0, 0, int(display_size.x), int(display_size.y))
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    GL.glUseProgram(app_state.shader_program)

    # Set automatic uniforms values
    app_state.uniforms.set_uniform_value("iResolution", display_size)
    app_state.uniforms.set_uniform_value("iTime", imgui.get_time())
    app_state.uniforms.set_uniform_value("iMouse", ImVec2(0.0, 0.0))

    app_state.apply_uniforms()

    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glBindVertexArray(app_state.full_screen_quad_vao)
    GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glBindVertexArray(0)
    GL.glUseProgram(0)


def gui(app_state: AppState):
    """GUI for modifying shader parameters."""
    imgui.set_next_window_pos(hello_imgui.em_to_vec2(0.0, 0.0), imgui.Cond_.appearing)
    imgui.set_next_window_size(hello_imgui.em_to_vec2(31.0, 14.0), imgui.Cond_.appearing)
    imgui.begin("Shader parameters")

    imgui_md.render_unindented("""
        Shader: "Seascape" by Alexander Alekseev aka TDM - 2014 - [Shadertoy](https://www.shadertoy.com/view/Ms2SD1)
    """)
    imgui.separator()

    # Modify the uniforms values
    uniforms = app_state.uniforms

    value = uniforms.get_uniform_value("SEA_HEIGHT")
    _, value = imgui.slider_float("SEA_HEIGHT", value, 0.1, 2.1)
    uniforms.set_uniform_value("SEA_HEIGHT", value)

    value = uniforms.get_uniform_value("SEA_CHOPPY")
    _, value = imgui.slider_float("SEA_CHOPPY", value, 0.1, 10.0)
    uniforms.set_uniform_value("SEA_CHOPPY", value)

    color_vec = uniforms.get_uniform_value("SEA_BASE")
    color_list = [color_vec.x, color_vec.y, color_vec.z]
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


def main():
    # This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    #         hello_imgui.set_assets_folder("my_assets")  # (By default, HelloImGui will search inside "assets")
    demo_utils.set_hello_imgui_demo_assets_folder()

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
    add_ons_params = immapp.AddOnsParams()
    add_ons_params.with_markdown = True
    immapp.run(runner_params, add_ons_params)

    return 0


if __name__ == "__main__":
    sys.exit(main())
