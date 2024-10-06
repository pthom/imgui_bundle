# pyodide_imgui_render.py
from typing import Callable
from imgui_bundle import hello_imgui
from pyodide.ffi import create_proxy
import js
import gc


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
            self.request_stop()
            raise e

        # Schedule the next frame
        js.requestAnimationFrame(self.main_loop_proxy)

    def start(self):
        self.stop_requested = False
        js.requestAnimationFrame(self.main_loop_proxy)

    def request_stop(self):
        print("JsAnimationRenderer: Stop requested")
        self.stop_requested = True


class HelloImGuiRunnerJs:
    """Manages the ManualRender lifecycle and integrates with JsAnimationRenderer."""
    js_animation_renderer: JsAnimationRenderer | None = None

    def __init__(self):
        self.js_animation_renderer = None

    def stop(self):
        """Stops the current rendering loop and tears down the renderer."""
        if self.js_animation_renderer is not None:
            print("Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            self.js_animation_renderer = None

        try:
            hello_imgui.manual_render.tear_down()
            print("HelloImGuiRunnerJs: Renderer torn down successfully.")
        except Exception as e:
            js.console.error(f"Error during Renderer teardown: {e}")
        finally:
            # Force garbage collection to free resources
            gc.collect()

    def run_overloaded(self, *args, **kwargs):
        print("run_overloaded")
        self.stop()

        try:
            if len(args) == 1 and isinstance(args[0], hello_imgui.RunnerParams):
                print("overload with RunnerParams")
                runner_params = args[0]
                hello_imgui.manual_render.setup_from_runner_params(runner_params)
            elif len(args) == 1 and isinstance(args[0], hello_imgui.SimpleRunnerParams):
                print("overload with SimpleRunnerParams")
                simple_runner_params = args[0]
                hello_imgui.manual_render.setup_from_simple_runner_params(simple_runner_params)
            elif len(args) == 1 and callable(args[0]):
                print("overload with callable")
                gui_function = args[0]
                hello_imgui.manual_render.setup_from_gui_function(gui_function, **kwargs)
        except Exception as e:
            js.console.error(f"Failed to initialize Renderer: {e}")
            return

        self.js_animation_renderer = JsAnimationRenderer(hello_imgui.manual_render.render)
        self.js_animation_renderer.start()




# Instantiate a global runner
_HELLO_IMGUI_RUNNER_JS = HelloImGuiRunnerJs()

# Monkey patch the hello_imgui.run function to use the js version
hello_imgui.run = _HELLO_IMGUI_RUNNER_JS.run_overloaded
