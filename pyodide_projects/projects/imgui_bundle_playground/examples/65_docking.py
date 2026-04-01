"""# Docking Layouts with Hello ImGui

Hello ImGui provides a **docking** system: define named dock spaces, then assign windows to them.
Windows can be dragged, tabbed, and rearranged by the user.

**How it works:**
1. Define **DockingSplits** to divide the screen into named regions
2. Create **DockableWindows** and assign each to a dock space
3. Hello ImGui handles the layout, persistence, and user interaction

```
┌──────────┬────────────────────┐
│ Command  │                    │
│ Space    │  MainDockSpace     │
│          ├────────────────────┤
│          │  BottomSpace       │
└──────────┴────────────────────┘
```

**Links:**
- [Docking documentation](https://pthom.github.io/imgui_bundle/core-libs/hello-imgui-immapp/)
- [Full docking demo in the Explorer](https://traineq.org/imgui_bundle_explorer/)
"""
from imgui_bundle import imgui, immapp, hello_imgui
from typing import List


# ============================================================
# 1. Define the docking splits
#    (how the screen is divided into named dock spaces)
# ============================================================
def create_docking_splits() -> List[hello_imgui.DockingSplit]:
    # We split "MainDockSpace" (provided automatically) into 3 zones:
    #
    #   ┌──────────┬────────────────────┐
    #   │ Command  │                    │
    #   │ Space    │  MainDockSpace     │
    #   │          ├────────────────────┤
    #   │          │  BottomSpace       │
    #   └──────────┴────────────────────┘

    # Split a "CommandSpace" on the left (25% width)
    split_left = hello_imgui.DockingSplit()
    split_left.initial_dock = "MainDockSpace"
    split_left.new_dock = "CommandSpace"
    split_left.direction = imgui.Dir.left
    split_left.ratio = 0.25

    # Split a "BottomSpace" at the bottom of MainDockSpace (40% height)
    split_bottom = hello_imgui.DockingSplit()
    split_bottom.initial_dock = "MainDockSpace"
    split_bottom.new_dock = "BottomSpace"
    split_bottom.direction = imgui.Dir.down
    split_bottom.ratio = 0.4

    return [split_left, split_bottom]


# ============================================================
# 2. Define the dockable windows
#    (each window has a name, a dock space, and a GUI function)
# ============================================================
def create_dockable_windows() -> List[hello_imgui.DockableWindow]:
    windows = []

    # A "Controls" window in the left CommandSpace
    controls = hello_imgui.DockableWindow()
    controls.label = "Controls"
    controls.dock_space_name = "CommandSpace"
    controls.gui_function = gui_controls
    windows.append(controls)

    # A "Main View" window in the center
    main_view = hello_imgui.DockableWindow()
    main_view.label = "Main View"
    main_view.dock_space_name = "MainDockSpace"
    main_view.gui_function = gui_main_view
    windows.append(main_view)

    # A "Log" window at the bottom
    log_win = hello_imgui.DockableWindow()
    log_win.label = "Log"
    log_win.dock_space_name = "BottomSpace"
    log_win.gui_function = gui_log
    windows.append(log_win)

    # A "Properties" window, also at the bottom (tabbed with Log)
    props = hello_imgui.DockableWindow()
    props.label = "Properties"
    props.dock_space_name = "BottomSpace"
    props.gui_function = gui_properties
    windows.append(props)

    return windows


# ============================================================
# 3. GUI functions for each dockable window
# ============================================================
_slider_value = 0.5
_counter = 0
_checkbox = True


def gui_controls():
    global _slider_value, _counter, _checkbox
    imgui.text("Sidebar controls")
    imgui.separator()
    imgui.set_next_item_width(imgui.get_content_region_avail().x)
    _, _slider_value = imgui.slider_float(
        "##slider", _slider_value, 0, 1)
    _, _checkbox = imgui.checkbox("Enable", _checkbox)
    if imgui.button("Increment"):
        _counter += 1
        hello_imgui.log(
            hello_imgui.LogLevel.info,
            f"Counter: {_counter}")
    imgui.text(f"Counter: {_counter}")


def gui_main_view():
    imgui.text("Main content area")
    imgui.separator()
    imgui.text_wrapped(
        "This window is in 'MainDockSpace'. "
        "Try dragging window tabs to rearrange "
        "the layout. The layout is saved and "
        "restored automatically.")
    imgui.spacing()
    imgui.text(f"Slider value: {_slider_value:.2f}")
    imgui.text(f"Checkbox: {_checkbox}")
    # A simple progress bar using the slider value
    imgui.progress_bar(_slider_value)


def gui_log():
    # Use Hello ImGui's built-in log widget
    hello_imgui.log_gui()


def gui_properties():
    imgui.text("Properties panel")
    imgui.separator()
    imgui.text_disabled(
        "This window shares the BottomSpace "
        "with 'Log' (see the tabs).")
    imgui.spacing()
    imgui.bullet_text("Drag tabs to rearrange")
    imgui.bullet_text("Drag title bar to undock")
    imgui.bullet_text("View > Restore layout to reset")


# ============================================================
# 4. Main: wire everything together with RunnerParams
# ============================================================
def main():
    # RunnerParams gives full control over the app
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Docking Layouts"
    params.app_window_params.window_geometry.size = (1000, 700)

    # Enable docking
    params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType
        .provide_full_screen_dock_space)

    # Set up the docking layout
    params.docking_params.docking_splits = (
        create_docking_splits())
    params.docking_params.dockable_windows = (
        create_dockable_windows())

    # Reset layout each time (for playground demos)
    params.docking_params.layout_condition = (
        hello_imgui.DockingLayoutCondition.application_start)

    # Enable the "View" menu (to restore layout)
    params.imgui_window_params.show_menu_bar = True

    immapp.run(params)


if __name__ == "__main__":
    main()
