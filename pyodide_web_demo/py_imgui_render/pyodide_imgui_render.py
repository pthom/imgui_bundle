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

    def run(self, runner_params: hello_imgui.RunnerParams):
        """Runs the ImGui application with the provided RunnerParams."""
        print("HelloImGuiRunnerJs.run")

        # Stop any existing renderer before starting a new one
        self.stop()

        try:
            # Initialize the ManualRender with RunnerParams
            hello_imgui.manual_render.setup_from_runner_params(runner_params)
            print("HelloImGuiRunnerJs.run: Renderer initialized successfully.")
        except Exception as e:
            js.console.error(f"Failed to initialize Renderer: {e}")
            return

        # Create a JsAnimationRenderer to handle the rendering loop
        self.js_animation_renderer = JsAnimationRenderer(hello_imgui.manual_render.render)
        self.js_animation_renderer.start()
        print("HelloImGuiRunnerJs.run: Rendering loop started.")


# Instantiate a global runner
_HELLO_IMGUI_RUNNER_JS = HelloImGuiRunnerJs()

# def run(code: str):
#     """Runs the provided Python code in Pyodide."""
#     try:
#         # Execute the user-provided code asynchronously
#         asyncio.ensure_future(js.pyodide.runPythonAsync(code))
#     except Exception as e:
#         js.console.error(f"Error during run: {e}")

# Monkey patch the hello_imgui.run function to use the js version
hello_imgui.run = _HELLO_IMGUI_RUNNER_JS.run
# hello_imgui.stop = _HELLO_IMGUI_RUNNER_JS.stop  # Optionally add a stop method
