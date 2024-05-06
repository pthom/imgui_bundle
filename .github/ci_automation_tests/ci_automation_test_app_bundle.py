from imgui_bundle import hello_imgui, immapp, imgui

import sys
from typing import Optional


test_open_metrics: Optional[imgui.test_engine.Test] = None
test_capture: Optional[imgui.test_engine.Test] = None
test_exit: Optional[imgui.test_engine.Test] = None


def my_register_tests():
    global test_open_metrics, test_capture, test_exit
    engine = hello_imgui.get_imgui_test_engine()

    engine.io.export_results_filename_set("ci_automation_test_app_bundle.xml")
    engine.io.export_results_format = imgui.test_engine.TestEngineExportFormat.j_unit_xml

    # Open Metrics window
    test_open_metrics = imgui.test_engine.register_test(
        engine, "demo_tests", "open_metrics"
    )

    def test_func_metrics(ctx: imgui.test_engine.TestContext):
        ctx.set_ref("Dear ImGui Demo")
        ctx.menu_check("Tools/Metrics\\/Debugger")

    test_open_metrics.test_func = test_func_metrics

    # Capture entire Dear ImGui Demo window.
    test_capture = imgui.test_engine.register_test(
        engine, "demo_tests", "capture_screenshot"
    )

    def test_func_capture(ctx: imgui.test_engine.TestContext):
        ctx.set_ref("Dear ImGui Demo")
        ctx.item_open("Widgets")  # Open collapsing header
        ctx.item_open_all("Basic")  # Open tree node and all its descendants
        ctx.capture_screenshot_window("Dear ImGui Demo")

    test_capture.test_func = test_func_capture

    # Exit
    test_exit = imgui.test_engine.register_test(engine, "demo_tests", "exit")

    def test_func_exit(ctx: imgui.test_engine.TestContext):
        ctx.item_click("**/Exit")

    test_exit.test_func = test_func_exit


@immapp.static(idx_frame_count=0)
def queue_all_tests():
    static = queue_all_tests
    static.idx_frame_count += 1

    if static.idx_frame_count == 3:
        engine = hello_imgui.get_imgui_test_engine()
        test_io = imgui.test_engine.get_io(engine)
        test_io.config_run_speed = imgui.test_engine.TestRunSpeed.normal

        imgui.test_engine.queue_test(engine, test_open_metrics)
        imgui.test_engine.queue_test(engine, test_capture)
        imgui.test_engine.queue_test(engine, test_exit)


def app_gui():
    imgui.text("Hello")

    if imgui.button("Exit"):
        hello_imgui.get_runner_params().app_shall_exit = True

    imgui.show_demo_window()
    imgui.test_engine.show_test_engine_windows(
        hello_imgui.get_imgui_test_engine(), True
    )

    queue_all_tests()


def main() -> int:
    print("Starting ci_automation_test_app")
    try:
        runner_params = hello_imgui.RunnerParams()
        runner_params.use_imgui_test_engine = True

        runner_params.callbacks.show_gui = app_gui
        runner_params.callbacks.register_tests = my_register_tests
        immapp.run(runner_params)
    except Exception as e:
        print("ERROR: exception in ci_automation_test_app", e)
        return 1

    print("Exiting ci_automation_test_app with success!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
