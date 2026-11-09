"""
imgui_kit in a window you own: the touch layer and the wheel session, in a pure Python GLFW app.

The same app as example_python_backend_glfw3.py, plus four lines of imgui_kit:
- `imgui_kit.touch.setup()`: the swipe, the long press, the pinch, through Dear ImGui's context hooks (nothing to call
  per frame);
- `imgui_kit.setup_wheel_session()`: the wheel keeps scrolling the window it started on, even over a plot;
- `imgui_kit.is_animating()`: an app that sleeps when nothing happens keeps drawing while something of the kit moves
  (a fling, a bounce, a switch that slides);
- `imgui_kit.touch.get_config().simulate_touch`: on a desktop, the mouse plays a finger (the demo's checkbox).

GLFW reports no fingers, so a real touch screen gets the swipe and the long press here, not the pinch: a backend that
knows its fingers (SDL) forwards them with `imgui_kit.touch.add_finger_event()`.
`pip install imgui-bundle[glfw,opengl]`.
"""

# Workaround issue when using wayland ("Attempt to retrieve context when no valid context", in PyOpenGL)
# (see https://github.com/pthom/imgui_bundle/issues/321)
import os
if os.getenv("XDG_SESSION_TYPE") == "wayland" and not os.getenv("PYOPENGL_PLATFORM"):
    os.environ["PYOPENGL_PLATFORM"] = "x11"

import sys

import OpenGL.GL as gl  # pip install PyOpenGL
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
# When using a pure python backend, prefer to import glfw before imgui_bundle (so that you end up using the standard
# glfw, not the one provided by imgui_bundle)
import glfw
from imgui_bundle import imgui, imgui_kit

IDLE_SECONDS = 0.1  # the longest sleep between two frames when nothing happens (an event or an animation wakes it)


class AppState:
    volume: float = 0.5


app_state = AppState()


def gui() -> None:
    """A window of our own, with the kit's layout helpers; the kit's demo window beside it"""
    imgui.set_next_window_size((420, 300), imgui.Cond_.first_use_ever)
    imgui.begin("A window with imgui_kit")
    imgui.text_wrapped("Scroll with the wheel, or swipe with a finger (tick \"Simulate a touch source\" in the demo's "
                       "Touch section to swipe with the mouse). The app sleeps when nothing moves.")
    with imgui_kit.fill_row("volume") as row:  # the slider fills the line, the help marker stays on the right
        _, app_state.volume = imgui.slider_float("##volume", app_state.volume, 0.0, 1.0, "volume %.2f")
        row.tail()
        imgui_kit.help_marker("A fill row: the slider takes the line, minus this marker.")
    for i in range(40):
        imgui.text(f"Line {i + 1}: content to scroll")
    imgui.end()
    imgui_kit.show_demo_window()



def main() -> None:
    imgui.create_context()
    imgui_kit.touch.setup()            # the touch layer: swipe, long press, pinch (the fingers come from the backend)
    imgui_kit.setup_wheel_session()    # the wheel stays with the window it scrolls
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    while not glfw.window_should_close(window):
        # Sleep until an event, unless something of the kit moves on its own (a fling, a bounce, a slide)
        if imgui_kit.is_animating():
            glfw.poll_events()
        else:
            glfw.wait_events_timeout(IDLE_SECONDS)
        impl.process_inputs()
        imgui.new_frame()
        gui()
        gl.glClearColor(0.45, 0.55, 0.60, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1000, 720
    window_name = "imgui_kit in a pure Python GLFW app"
    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)
    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)
    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)
    return window


if __name__ == "__main__":
    main()
