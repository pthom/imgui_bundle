from typing import Callable
from imgui_bundle import hello_imgui
from pyodide.ffi import create_proxy
import js


class JsAnimationRenderer:
    """Setup an animation loop that calls a python function to do rendering at each javascript frame."""
    def __init__(self, render_fn: Callable[[], None]):

        self.render_fn = render_fn
        self.stop_requested = False
        self.main_loop_proxy = create_proxy(self.main_loop)

    def main_loop(self, timestamp):
        if self.stop_requested:
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

    def stop(self):
        self.stop_requested = True

RENDERER = None

def hello_imgui_run_in_js(runner_params: hello_imgui.RunnerParams):
    global RENDERER
    if RENDERER is not None:
        del(RENDERER)
        # await asyncio.sleep(2)
        import time
        time.sleep(0.3)

    print("Entering hello_imgui_run_in_js")
    RENDERER = hello_imgui.Renderer(runner_params)
    print("Renderer created")

    def render():
        RENDERER.render()

    # Animation Loop Setup
    animation_loop = JsAnimationRenderer(render)
    print("Animation loop created")
    print("Starting animation loop")
    animation_loop.start()
    print("Animation loop started")


# monkey patch the hello_imgui.run function to use the js version
hello_imgui.run = hello_imgui_run_in_js
