from imgui_bundle import imgui, hello_imgui
from imgui_bundle.imgui.test_engine_checks import CHECK

test_open_metric: imgui.test_engine.Test
test_capture_screenshot: imgui.test_engine.Test


def my_register_tests():
    global test_open_metric, test_capture_screenshot
    engine = hello_imgui.get_imgui_test_engine()

    # test with gui and vars
    test_with_vars = imgui.test_engine.register_test(engine, "demo_tests", "test_vars")
    class TestVar2:
        my_int = 42
    test_var2 = TestVar2()
    def test_with_vars_gui_func(ctx: imgui.test_engine.TestContext):
        imgui.set_next_window_size(hello_imgui.em_to_vec2(40, 8))
        imgui.begin("Test Window", None, imgui.WindowFlags_.no_saved_settings)
        _, test_var2.my_int = imgui.slider_int("Slider", test_var2.my_int, 0, 1000)
        imgui.end()
    def test_with_vars_test_func(ctx: imgui.test_engine.TestContext):
        # Optional: reset test_var2 to its startup values
        nonlocal test_var2
        test_var2 = TestVar2()
        # Run the test
        ctx.set_ref("Test Window")
        CHECK(test_var2.my_int == 42)
        ctx.item_input_value("Slider", 123)
        CHECK(test_var2.my_int == 123)
    test_with_vars.test_func = test_with_vars_test_func
    test_with_vars.gui_func = test_with_vars_gui_func

    # Open Metrics
    test_open_metric = imgui.test_engine.register_test(engine, "demo_tests", "open_metrics")
    def tst_func_metrics(ctx: imgui.test_engine.TestContext):
        # This function will be executed in a separate coroutine thread which is launched by C++
        # The coroutine thread never executes in parallel with the main thread.
        # However, since it might be difficult to place a breakpoint in this thread
        ctx.yield_()
        ctx.set_ref("Dear ImGui Demo")
        ctx.menu_check("Tools/Metrics\\/Debugger")
    test_open_metric.test_func = tst_func_metrics

    # Capture entire Dear ImGui Demo window.
    test_capture_screenshot = imgui.test_engine.register_test(engine, "demo_tests", "capture_screenshot")
    def tst_func_capture(ctx: imgui.test_engine.TestContext):
        ctx.set_ref("Dear ImGui Demo")
        ctx.item_open("Widgets")
        ctx.item_open_all("Basic")
        ctx.capture_screenshot_window("Dear ImGui Demo") # not available yet!:  imgui.test_engine. ImGuiCaptureFlags_StitchAll | ImGuiCaptureFlags_HideMouseCursor);
    test_capture_screenshot.test_func = tst_func_capture


def app_gui():
    imgui.show_demo_window()
    imgui.test_engine.show_test_engine_windows(hello_imgui.get_imgui_test_engine(), None)
    if imgui.button("Run open metric automation"):
        imgui.test_engine.queue_test(hello_imgui.get_imgui_test_engine(), test_open_metric)
    if imgui.button("Run capture screenshot automation"):
        imgui.test_engine.queue_test(hello_imgui.get_imgui_test_engine(), test_capture_screenshot)


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.use_imgui_test_engine = True

    runner_params.callbacks.show_gui = app_gui
    runner_params.callbacks.register_tests = my_register_tests

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
