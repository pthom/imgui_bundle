# A demo app that demonstrates how to use ImGui Test Engine (https://github.com/ocornut/imgui_test_engine)
#
# It demonstrates how to:
# - enable ImGui Test Engine via RunnerParams.use_imgui_test_engine
# - define a callback where the tests are registered (runner_params.callbacks.register_tests)
# - create tests, and:
#   - automate actions using "named references" (see https://github.com/ocornut/imgui_test_engine/wiki/Named-References)
#   - display an optional custom GUI for a test
#   - manipulate custom variables
#   - check that simulated actions do modify those variables
#
# Important note: ImGui Test Engine falls under the Dear ImGui Test Engine License
#     See: https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt
#     TL;DR: free for individuals, educational, open-source and small businesses uses.
#            Paid for larger businesses. Read license for details.
#            License sales to larger businesses are used to fund and sustain the development of Dear ImGui.


from imgui_bundle import imgui, hello_imgui
from imgui_bundle.imgui.test_engine_checks import CHECK
from typing import List


# Our tests, that will automate the application
test_open_popup: imgui.test_engine.Test
test_capture_screenshot: imgui.test_engine.Test
test_custom_gui = imgui.test_engine.Test


# This function is called at startup and will instantiate the tests
def my_register_tests():
    global test_open_popup, test_capture_screenshot, test_custom_gui
    engine = hello_imgui.get_imgui_test_engine()

    # Demo 1: Open popup
    test_open_popup = imgui.test_engine.register_test(engine, "Demo Tests", "Open Popup")
    def test_open_popup_func(ctx: imgui.test_engine.TestContext):
        # This is the function that will be called by our test
        ctx.set_ref("Dear ImGui Demo")              # From now on, all actions happen in the "Dear ImGui Demo" window
        ctx.item_open("Popups & Modal windows")     # Open the "Popups & Modal windows" tree item
        ctx.item_open("Modals")                     # Open the "Modal" tree item
        ctx.item_click("**/Delete..")               # Click the "Delete.." button ("**" means: search inside children)
        ctx.item_click("//Delete?/Cancel")          # Click the "Cancel" button:
                                                    #    here, "//"  means "ignore previous set_ref" and search
                                                    #    for the cancel button in the root popup window named "Delete?"
        ctx.item_close("Popups & Modal windows")    # Close the "Popups & Modal windows" tree item
    # let the test call our function
    test_open_popup.test_func = test_open_popup_func

    # Demo 2 : Capture Dear ImGui Demo window
    test_capture_screenshot = imgui.test_engine.register_test(engine, "Demo Tests", "Capture Screenshot")
    def test_capture_screenshot_func(ctx: imgui.test_engine.TestContext):
        ctx.set_ref("Dear ImGui Demo")                   # From now on, actions happen in the "Dear ImGui Demo" window
        ctx.item_open("Widgets")                         # Open the "Widgets", then "Basic" tree item
        ctx.item_open_all("Basic")
        ctx.capture_screenshot_window("Dear ImGui Demo") # Capture window and save screenshot
        ctx.item_close("Widgets")
    test_capture_screenshot.test_func = test_capture_screenshot_func

    # Demo 3: a test with a custom GUI and custom variables
    #         which asserts that simulated actions successfully changed the variables values
    test_custom_gui = imgui.test_engine.register_test(engine, "Demo Tests", "Test custom GUI & vars")
    # Our custom variables container
    class TestVar2:
        my_int = 42
    test_var2 = TestVar2()  # our custom variable(s)
    def test_custom_gui_func(ctx: imgui.test_engine.TestContext):
        # Custom GUI for this test: it can edit our custom variable
        imgui.set_next_window_size(hello_imgui.em_to_vec2(40, 8))
        imgui.begin("Custom Gui Test Window", None, imgui.WindowFlags_.no_saved_settings)
        _, test_var2.my_int = imgui.slider_int("Slider", test_var2.my_int, 0, 1000)
        imgui.end()
    def test_with_vars_test_func(ctx: imgui.test_engine.TestContext):
        # Our test, that will perform actions in the custom GUI, and assert that actions do change the custom variables
        # Optional: reset test_var2 to its startup values
        nonlocal test_var2
        test_var2 = TestVar2()
        # Run the test
        ctx.set_ref("Custom Gui Test Window")
        CHECK(test_var2.my_int == 42)
        ctx.item_input_value("Slider", 123)
        CHECK(test_var2.my_int == 123)
    # let the test call our test function, and also call our custom Gui
    test_custom_gui.test_func = test_with_vars_test_func
    test_custom_gui.gui_func = test_custom_gui_func


# Our application GUI: shows that we can trigger the test manually
def my_gui():
    test_engine = hello_imgui.get_imgui_test_engine()
    if imgui.button('Run "Open popup"'):
        imgui.test_engine.queue_test(test_engine, test_open_popup)
    if imgui.button('Run "Capture Screenshot"'):
        imgui.test_engine.queue_test(test_engine, test_capture_screenshot)
    if imgui.button('Run "Test custom GUI & vars"'):
        imgui.test_engine.queue_test(test_engine, test_custom_gui)

    engine_io = imgui.test_engine.get_io(test_engine)
    imgui.text("Test speed:")
    if imgui.button("Fast"):
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.fast
    imgui.same_line()
    if imgui.button("Normal"):
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.normal
    imgui.same_line()
    if imgui.button("Cinematic"):
        engine_io.config_run_speed = imgui.test_engine.TestRunSpeed.cinematic


# Defined later: helps to define the application layout, display the ImGui Demo, & ImGui Test Engine Window
def apply_application_layout(runner_params: hello_imgui.RunnerParams):
    ...


# Our main  function, where we need to:
#        - instantiate RunnerParams
#        - set `runner_params.use_imgui_test_engine = True`
#        - fill `runner_params.callbacks.register_tests`
def main():
    runner_params = hello_imgui.RunnerParams()
    apply_application_layout(runner_params)

    runner_params.use_imgui_test_engine = True
    runner_params.callbacks.register_tests = my_register_tests

    hello_imgui.run(runner_params)


# ///////////////////////////////////////////////////////////////////////////////
# // End of demo code
# ///////////////////////////////////////////////////////////////////////////////


# //
# // Note: the code below only helps to
# //    - define the application layout
# //    - display the ImGui Demo Window
# //    - display the ImGui Test Engine Window


def create_default_docking_splits() -> List[hello_imgui.DockingSplit]:
    # Define the application layout: splits the window in 3 spaces
    split_main_demo = hello_imgui.DockingSplit()
    split_main_demo.initial_dock = "MainDockSpace"
    split_main_demo.new_dock = "ImGuiDemoSpace"
    split_main_demo.direction = imgui.Dir_.right
    split_main_demo.ratio = 0.5

    split_main_test = hello_imgui.DockingSplit()
    split_main_test.initial_dock = "MainDockSpace"
    split_main_test.new_dock = "TestEngineSpace"
    split_main_test.direction = imgui.Dir_.down
    split_main_test.ratio = 0.7

    return [split_main_demo, split_main_test]


def create_dockable_windows() -> List[hello_imgui.DockableWindow]:
    # Define the app windows: my_gui, ImGui Demo Window, Dear ImGui Test Engine
    my_window = hello_imgui.DockableWindow()
    my_window.label = "Run Demos"
    my_window.dock_space_name = "MainDockSpace"
    my_window.gui_function = my_gui

    dear_imgui_demo_window = hello_imgui.DockableWindow()
    dear_imgui_demo_window.label = "Dear ImGui Demo"
    dear_imgui_demo_window.dock_space_name = "ImGuiDemoSpace"
    dear_imgui_demo_window.gui_function = imgui.show_demo_window

    test_engine_window = hello_imgui.DockableWindow()
    test_engine_window.label = "Dear ImGui Test Engine"
    test_engine_window.dock_space_name = "TestEngineSpace"
    test_engine_window.gui_function = lambda: imgui.test_engine.show_test_engine_windows(hello_imgui.get_imgui_test_engine(), None)

    return [my_window, dear_imgui_demo_window, test_engine_window]


def apply_application_layout(runner_params: hello_imgui.RunnerParams):
    # Define the application layout and windows
    runner_params.app_window_params.window_title = "Demo ImGui Test Engine"
    runner_params.imgui_window_params.default_imgui_window_type = \
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    runner_params.docking_params.docking_splits = create_default_docking_splits()
    runner_params.docking_params.dockable_windows = create_dockable_windows()
    runner_params.docking_params.layout_condition = hello_imgui.DockingLayoutCondition.application_start


if __name__ == "__main__":
    main()


