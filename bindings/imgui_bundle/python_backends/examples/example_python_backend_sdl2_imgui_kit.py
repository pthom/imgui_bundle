"""
imgui_kit in an SDL2 window you own: the touch layer with the fingers, and the wheel session, in pure Python.

The same app as example_python_backend_sdl2.py, plus imgui_kit:
- `imgui_kit.touch.setup()` and `imgui_kit.setup_wheel_session()`, once after the context;
- the fingers of a touch screen, which SDL reports, forwarded to `imgui_kit.touch.add_finger_event()`: two fingers
  pinch (the font, or a widget that claims them), moved together they are a right drag; a touch the system takes over
  ends with no click;
- `imgui_kit.is_animating()`: the app sleeps when nothing happens, and keeps drawing while something of the kit moves.

Needs `pip install imgui-bundle[sdl2,opengl] pysdl2-dll`. On a desktop without a touch screen, the demo's Touch
section has "Simulate a touch source" (the mouse plays one finger); SDL can also turn the mouse into a touch device:
`SDL_MOUSE_TOUCH_EVENTS=1` in the environment.
"""

import ctypes
import sys
from typing import Any

import OpenGL.GL as gl  # pip install PyOpenGL
from imgui_bundle import imgui, imgui_kit
from imgui_bundle.python_backends.sdl2_backend import SDL2Renderer
from sdl2 import (  # type: ignore[import-untyped]
    SDL_Event, SDL_FINGERDOWN, SDL_FINGERMOTION, SDL_FINGERUP, SDL_GetTouchDeviceType, SDL_TOUCH_DEVICE_DIRECT,
    SDL_MOUSE_TOUCHID, SDL_GetWindowSize, SDL_WaitEventTimeout, SDL_PollEvent, SDL_QUIT, SDL_GL_SwapWindow,
    SDL_GL_DeleteContext, SDL_DestroyWindow, SDL_Quit, SDL_Init, SDL_INIT_EVERYTHING, SDL_GetError, SDL_GL_SetAttribute,
    SDL_GL_DOUBLEBUFFER, SDL_GL_DEPTH_SIZE, SDL_GL_STENCIL_SIZE, SDL_GL_CONTEXT_FLAGS,
    SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, SDL_GL_CONTEXT_MAJOR_VERSION, SDL_GL_CONTEXT_MINOR_VERSION,
    SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE, SDL_SetHint, SDL_HINT_VIDEO_HIGHDPI_DISABLED,
    SDL_CreateWindow, SDL_WINDOWPOS_CENTERED, SDL_WINDOW_OPENGL, SDL_WINDOW_RESIZABLE, SDL_GL_CreateContext,
    SDL_GL_MakeCurrent, SDL_GL_SetSwapInterval,
)

IDLE_MS = 100  # the longest wait for an event when nothing happens (an event or an animation ends it)

_FINGER_PHASES = {
    SDL_FINGERDOWN: imgui_kit.TouchPhase_.began,
    SDL_FINGERMOTION: imgui_kit.TouchPhase_.moved,
    SDL_FINGERUP: imgui_kit.TouchPhase_.ended,
}


def forward_finger_event(event: SDL_Event, window: Any) -> None:
    """A finger of a touch screen, to the kit. SDL gives its position as a fraction of the window: in the window's
    coordinates here, as the mouse's. A trackpad is a touch device too (an indirect one): only the screens, and the
    mouse when SDL makes it a touch device (SDL_MOUSE_TOUCH_EVENTS)."""
    if event.type not in _FINGER_PHASES:
        return
    finger = event.tfinger
    direct = SDL_GetTouchDeviceType(finger.touchId) == SDL_TOUCH_DEVICE_DIRECT or finger.touchId == SDL_MOUSE_TOUCHID
    if not direct:
        return
    imgui.get_io().config_flags |= imgui.ConfigFlags_.is_touch_screen  # a screen was touched: thin scroll bars
    w, h = ctypes.c_int(), ctypes.c_int()
    SDL_GetWindowSize(window, ctypes.byref(w), ctypes.byref(h))
    finger_id = int(finger.fingerId) & 0x7FFFFFFF  # SDL's id, folded to an int
    imgui_kit.touch.add_finger_event(finger_id, (finger.x * w.value, finger.y * h.value), _FINGER_PHASES[event.type])


class AppState:
    volume: float = 0.5


app_state = AppState()


def gui() -> None:
    """A window of our own, with the kit's layout helpers; the kit's demo window beside it"""
    imgui.set_next_window_size((420, 300), imgui.Cond_.first_use_ever)
    imgui.begin("A window with imgui_kit")
    imgui.text_wrapped("Scroll with the wheel, swipe with a finger, pinch with two: the font scales (the demo's canvas "
                       "zooms instead). The app sleeps when nothing moves.")
    with imgui_kit.fill_row("volume") as row:  # the slider fills the line, the help marker stays on the right
        _, app_state.volume = imgui.slider_float("##volume", app_state.volume, 0.0, 1.0, "volume %.2f")
        row.tail()
        imgui_kit.help_marker("A fill row: the slider takes the line, minus this marker.")
    for i in range(40):
        imgui.text(f"Line {i + 1}: content to scroll")
    imgui.end()
    imgui_kit.show_demo_window()


def main() -> None:
    window, gl_context = impl_pysdl2_init()
    imgui.create_context()
    imgui_kit.touch.setup()            # the touch layer: swipe, long press, pinch (the fingers: the loop below)
    imgui_kit.setup_wheel_session()    # the wheel stays with the window it scrolls
    impl = SDL2Renderer(window)

    running = True
    event = SDL_Event()
    while running:
        # Sleep until an event, unless something of the kit moves on its own (a fling, a bounce, a slide)
        if not imgui_kit.is_animating():
            SDL_WaitEventTimeout(None, IDLE_MS)
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            impl.process_event(event)
            forward_finger_event(event, window)
        impl.process_inputs()
        imgui.new_frame()
        gui()
        gl.glClearColor(0.45, 0.55, 0.60, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        SDL_GL_SwapWindow(window)

    impl.shutdown()
    SDL_GL_DeleteContext(gl_context)
    SDL_DestroyWindow(window)
    SDL_Quit()


def impl_pysdl2_init():
    width, height = 1000, 720
    window_name = "imgui_kit in a pure Python SDL2 app"
    if SDL_Init(SDL_INIT_EVERYTHING) < 0:
        print("Error: SDL could not initialize! SDL Error: " + SDL_GetError().decode("utf-8"))
        sys.exit(1)
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
    SDL_SetHint(SDL_HINT_VIDEO_HIGHDPI_DISABLED, b"1")
    window = SDL_CreateWindow(window_name.encode("utf-8"), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width,
                              height, SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE)
    if window is None:
        print("Error: Window could not be created! SDL Error: " + SDL_GetError().decode("utf-8"))
        sys.exit(1)
    gl_context = SDL_GL_CreateContext(window)
    if gl_context is None:
        print("Error: Cannot create OpenGL Context! SDL Error: " + SDL_GetError().decode("utf-8"))
        sys.exit(1)
    SDL_GL_MakeCurrent(window, gl_context)
    SDL_GL_SetSwapInterval(1)
    return window, gl_context


if __name__ == "__main__":
    main()
