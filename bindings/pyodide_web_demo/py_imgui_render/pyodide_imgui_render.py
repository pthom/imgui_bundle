# pyodide_imgui_render.py
from typing import Callable
from imgui_bundle import hello_imgui, immapp
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
    is_running: bool = False

    def __init__(self):
        self.js_animation_renderer = None

    def stop(self):
        """Stops the current rendering loop and tears down the renderer."""
        if not  self.is_running:
            return
        if self.js_animation_renderer is not None:
            print("HelloImGuiRunnerJs: Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            self.js_animation_renderer = None

        try:
            hello_imgui.manual_render.tear_down()
            print("HelloImGuiRunnerJs: Renderer torn down successfully.")
        except Exception as e:
            js.console.error(f"HelloImGuiRunnerJs: Error during Renderer teardown: {e}")
        finally:
            # Force garbage collection to free resources
            gc.collect()

    def run_overloaded(self, *args, **kwargs):
        print("HelloImGuiRunnerJs: run_overloaded")
        if self.is_running:
            self.stop()
        self.is_running = True

        use_runner_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.RunnerParams)) or "runner_params" in kwargs
        use_simple_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.SimpleRunnerParams)) or "simple_params" in kwargs
        use_gui_function = (len(args) >= 1 and callable(args[0])) or "gui_function" in kwargs

        if use_runner_params:
            print("HelloImGuiRunnerJs: overload with RunnerParams")
            immapp.manual_render.setup_from_runner_params(*args, **kwargs)
        elif use_simple_params:
            print("HelloImGuiRunnerJs: overload with SimpleRunnerParams")
            immapp.manual_render.setup_from_simple_runner_params(*args, **kwargs)
        elif use_gui_function:
            print("HelloImGuiRunnerJs: overload with callable")
            immapp.manual_render.setup_from_gui_function(*args, **kwargs)
        else:
            raise ValueError("HelloImGuiRunnerJs: Invalid arguments")

        self.js_animation_renderer = JsAnimationRenderer(hello_imgui.manual_render.render)
        self.js_animation_renderer.start()


class ImmAppRunnerJs:
    """Manages the ManualRender lifecycle and integrates with JsAnimationRenderer."""
    js_animation_renderer: JsAnimationRenderer | None = None
    is_running: bool = False

    def __init__(self):
        self.js_animation_renderer = None

    def stop(self):
        """Stops the current rendering loop and tears down the renderer."""
        if not  self.is_running:
            return
        if self.js_animation_renderer is not None:
            print("ImmAppRunnerJs: Stopping js_animation_renderer")
            self.js_animation_renderer.request_stop()
            self.js_animation_renderer = None

        try:
            immapp.manual_render.tear_down()
            print("ImmAppRunnerJs: HelloImGuiRunnerJs: Renderer torn down successfully.")
        except Exception as e:
            js.console.error(f"ImmAppRunnerJs: Error during Renderer teardown: {e}")
        finally:
            # Force garbage collection to free resources
            gc.collect()

    def run_overloaded(self, *args, **kwargs):
        print("ImmAppRunnerJs: run_overloaded")
        if self.is_running:
            self.stop()
        self.is_running = True
        print(f"{len(args)=}  args: {args} kwargs: {kwargs}")

        use_runner_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.RunnerParams)) or "runner_params" in kwargs
        use_simple_params = (len(args) >= 1 and isinstance(args[0], hello_imgui.SimpleRunnerParams)) or "simple_params" in kwargs
        use_gui_function = (len(args) >= 1 and callable(args[0])) or "gui_function" in kwargs

        if use_runner_params:
            print("ImmAppRunnerJs: overload with RunnerParams")
            immapp.manual_render.setup_from_runner_params(*args, **kwargs)
        elif use_simple_params:
            print("ImmAppRunnerJs: overload with SimpleRunnerParams")
            immapp.manual_render.setup_from_simple_runner_params(*args, **kwargs)
        elif use_gui_function:
            print("ImmAppRunnerJs: overload with callable")
            immapp.manual_render.setup_from_gui_function(*args, **kwargs)
        else:
            raise ValueError("ImmAppRunnerJs: Invalid arguments")

        self.js_animation_renderer = JsAnimationRenderer(hello_imgui.manual_render.render)
        self.js_animation_renderer.start()




# Instantiate global runners
_HELLO_IMGUI_RUNNER_JS = HelloImGuiRunnerJs()
_IMMAPP_RUNNER_JS = ImmAppRunnerJs()

print("pyodide_imgui_render.py: Version 43.")
# Monkey patch the hello_imgui.run function to use the js version
hello_imgui.run = _HELLO_IMGUI_RUNNER_JS.run_overloaded
# Monkey patch the immapp.run function to use the js version
immapp.run = _IMMAPP_RUNNER_JS.run_overloaded
