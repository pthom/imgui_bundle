from typing import Callable
from imgui_bundle import hello_imgui
from pyodide.ffi import create_proxy
import js


class JsAnimationRenderer:
    """Make it possible to call a python function to do rendering at each javascript frame."""
    render_fn: Callable[[], None]  # A python function that performs rendering
    stop_requested: bool  # A flag to request the animation loop to stop
    main_loop_proxy: js.Proxy  # A javascript proxy to the main_loop method that is called at each frame

    def __init__(self, render_fn: Callable[[], None]):

        self.render_fn = render_fn
        self.stop_requested = False
        self.main_loop_proxy = create_proxy(self.main_loop)

    def main_loop(self, timestamp):
        if self.stop_requested:
            print("JsAnimationRenderer: Stop requested, destroying main_loop_proxy")
            self.main_loop_proxy.destroy()
            return
        try:
            self.render_fn()
        except Exception as e:
            js.console.error(f"Error during render: {e}")

        js.requestAnimationFrame(self.main_loop_proxy)

    def start(self):
        self.stop_requested = False
        js.requestAnimationFrame(self.main_loop_proxy)

    def request_stop(self):
        print("JsAnimationRenderer: Stop requested")
        self.stop_requested = True


class HelloImGuiRunnerJs:
    # hello_imgui_renderer: Renderer for hello_imgui (holds the imgui and OpenGL context)
    hello_imgui_renderer: hello_imgui.Renderer | None = None
    # js_animation_renderer: Animation loop for rendering (calls hello_imgui_renderer.render at each frame)
    js_animation_renderer: JsAnimationRenderer | None = None

    def __init__(self):
        pass

    def stop(self):
        if self.js_animation_renderer is not None:
            print("Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            # How to wait until the animation loop stops...
            # await asyncio.sleep(0.5) ?
            self.js_animation_renderer = None

        if self.hello_imgui_renderer is not None:
            print("Deleting hello_imgui_renderer")
            del(self.hello_imgui_renderer)  # This should reset the imgui context and the OpenGL context

    def run(self, runner_params: hello_imgui.RunnerParams):
        print("HelloImGuiRunnerJs.run")
        self.stop()
        self.hello_imgui_renderer = hello_imgui.Renderer(runner_params)
        self.js_animation_renderer = JsAnimationRenderer(self.hello_imgui_renderer.render)
        self.js_animation_renderer.start()


# monkey patch the hello_imgui.run function to use the js version
_HELLO_IMGUI_RUNNER_JS = HelloImGuiRunnerJs()
hello_imgui.run = _HELLO_IMGUI_RUNNER_JS.run
