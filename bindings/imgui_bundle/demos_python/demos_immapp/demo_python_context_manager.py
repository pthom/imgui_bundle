from imgui_bundle import imgui, imgui_ctx, ImVec2, hello_imgui, ImVec4, immapp, imgui_md
import inspect


DOC = """
This demo shows how to use context managers to simplify the use of functions pairs like

    1. `imgui.begin()` and `imgui.end()`
    can be replaced by:  `with imgui_ctx.begin() as window:`

    2. `imgui.begin_child()` and `imgui.end_child()`
    can be replaced by:  `with imgui_ctx.begin_child() as child:`

    3. `imgui.begin_menu_bar()` and `imgui.end_menu_bar()`
    can be replaced by:  `with imgui_ctx.begin_menu_bar() as menu_bar:`

etc.
"""

STANDARD_FONT = None
SOURCE_FONT = None


def demo_begin():
    # Bag for statics variables
    statics = demo_begin
    if not hasattr(statics, "opened_window_shortest"):
        statics.opened_window_shortest = False
    if not hasattr(statics, "opened_window_expandable"):
        statics.opened_window_expandable = False
    if not hasattr(statics, "opened_closable_window"):
        statics.opened_closable_window = False

    # Checkboxes to open windows
    _, statics.opened_window_shortest = imgui.checkbox("Open Window - Shortest", statics.opened_window_shortest)
    _, statics.opened_window_expandable = imgui.checkbox("Open Window - Expandable", statics.opened_window_expandable)
    _, statics.opened_closable_window = imgui.checkbox("Open Closable Window", statics.opened_closable_window)

    imgui.set_next_window_size(ImVec2(200, 200), imgui.Cond_.appearing.value)

    # Shortest use of imgui_ctx.begin()
    if statics.opened_window_shortest:
        with imgui_ctx.begin("Window - Shortest"):
            imgui.text("Hello!")

    # Example where we test if the window is expanded
    if statics.opened_window_expandable:
        with imgui_ctx.begin("Window - Expandable") as window2:
            # The test below will return True if the window is expanded
            # It could also be written:
            #     if window2.expanded:
            # It is optional to test this, since the widgets will not be rendered,
            # if the window is not expanded, but you can exit early if you want.
            if window2:
                imgui.text("Hello!")

    # Example of a closable window
    if statics.opened_closable_window:
        with imgui_ctx.begin("Closable window", statics.opened_closable_window) as window:
            if window:
                imgui.text("Hello!")
            statics.opened_closable_window = window.opened


def demo_begin_child():
    # Example of a child window
    with imgui_ctx.begin_child("Child Window", ImVec2(200, 20)):
        imgui.text("This is a child window!")

    # Example of a child window, where we test if the child is expanded
    with imgui_ctx.begin_child("Child Window Expandable", ImVec2(400, 20)) as child:
        if child:
            imgui.text("This is a child window (where we test if it is expanded)!")


def demo_push_pop():
    # Bag for statics variables
    statics = demo_push_pop
    if not hasattr(statics, "input_text"):
        statics.input_text = "Some text..."

    # Example of push_font
    imgui.separator_text("Push Font")
    with imgui_ctx.push_font(SOURCE_FONT):  # noqa
        imgui.text("This is Source Code Pro!")

    # Example of push_style_color
    imgui.separator_text("Push Style Color")
    with imgui_ctx.push_style_color(imgui.Col_.text.value, ImVec4(1.0, 0.0, 0.0, 1.0)):
        imgui.text("This is red!")

    # Example of push_style_var
    imgui.separator_text("Push Style Var")
    with imgui_ctx.push_style_var(imgui.StyleVar_.alpha.value, 0.5):
        imgui.text("This is half transparent!")

    # Example of push_item_width
    imgui.separator_text("Push Item Width")
    imgui.text("This is a text input field with a width of 100 pixels:")
    with imgui_ctx.push_item_width(100):
        _, statics.input_text = imgui.input_text("Input", statics.input_text)

    # Example of push_id
    imgui.separator_text("Push ID")
    with imgui_ctx.push_id("SubId"):
        imgui.button("A")
        imgui.same_line()
        imgui.text(f"Button ID: {imgui.get_item_id()}")


def demo_tree_node():
    # Note: imgui_ctx.tree_node does not make the code shorter,
    with imgui_ctx.tree_node("Tree Node 1") as node1:
        if node1:
            imgui.text("Inside Node 1")
    # when compared to imgui.tree_node
    if imgui.tree_node("Tree Node2"):
        imgui.text("Inside Node 2")
        imgui.tree_pop()


def demo_begin_group():
    with imgui_ctx.begin_group():
        imgui.button("Group 1 Line 1")
        imgui.button("Group 1 Line 2")
    imgui.same_line()
    with imgui_ctx.begin_group():
        imgui.button("Group 2 Line 1")
        imgui.button("Group 2 Line 2")


def demo_begin_drag_and_drop():
    # Bag for statics variables
    statics = demo_begin_drag_and_drop
    if not hasattr(statics, "received_payload"):
        statics.received_payload = "No payload received"

    imgui.button("Drag me (42)")
    with imgui_ctx.begin_drag_drop_source() as source:
        if source.is_dragging:
            imgui.set_drag_drop_payload_py_id("DRAG_PAYLOAD", 42)
            imgui.text("Dragging!")

    imgui.same_line()
    imgui.button(f"To here: {statics.received_payload}")
    with imgui_ctx.begin_drag_drop_target() as target:
        if target.is_receiving:
            payload = imgui.accept_drag_drop_payload_py_id("DRAG_PAYLOAD")
            if payload is not None:
                statics.received_payload = str(payload.data_id)


def demo_begin_tab_bar():
    with imgui_ctx.begin_tab_bar("Tab Bar") as tab_bar:
        if tab_bar:
            with imgui_ctx.begin_tab_item("Tab 1") as tab:
                if tab:
                    imgui.text("This is tab 1!")
            with imgui_ctx.begin_tab_item("Tab 2") as tab:
                if tab:
                    imgui.text("This is tab 2!")


def demo_begin_table():
    table_flags = (imgui.TableFlags_.borders_h.value
                   | imgui.TableFlags_.borders_v.value
                   | imgui.TableFlags_.resizable.value)
    with imgui_ctx.begin_table("Table", 3, table_flags) as table:
        if table:
            imgui.table_setup_column("Column 1")
            imgui.table_setup_column("Column 2")
            imgui.table_setup_column("Column 3")
            imgui.table_headers_row()
            for row in range(5):
                imgui.table_next_row()
                for column in range(3):
                    imgui.table_next_column()
                    imgui.text("Cell {}, {}".format(row, column))


def demo_begin_popup():
    # Example of a standard popup
    imgui.separator_text("Popup with imgui_ctx.begin_popup() and begin_popup_modal()")
    if imgui.button("Open Popup"):
        imgui.open_popup("Popup")
    with imgui_ctx.begin_popup("Popup") as popup:
        if popup.visible:
            imgui.text("This is a popup!")
            if imgui.button("Close Popup"):
                imgui.close_current_popup()

    # Example of a modal popup
    imgui.same_line()
    if imgui.button("Open Modal Popup"):
        imgui.open_popup("Modal Popup")
    with imgui_ctx.begin_popup_modal("Modal Popup") as popup:
        if popup.visible:
            imgui.text("This is a modal popup!")
            if imgui.button("Close Modal Popup"):
                imgui.close_current_popup()


def demo_begin_tooltip():
    imgui.text("Hover me for a tooltip!")
    if imgui.is_item_hovered():
        with imgui_ctx.begin_tooltip():
            imgui.text("This is a tooltip!")


def demo_listbox():
    # Bag for statics variables
    statics = demo_listbox
    if not hasattr(statics, "list_box_items"):
        statics.list_box_items = {"Item 1": True, "Item 2": False, "Item 3": False}

    with imgui_ctx.begin_list_box("List Box", ImVec2(200, 60)) as list_box:
        if list_box:
            for item in statics.list_box_items:
                changed, statics.list_box_items[item] = imgui.selectable(item, statics.list_box_items[item])


def demo_menu_bar():
    # Bag for statics variables
    statics = demo_menu_bar
    if not hasattr(statics, "opened_window_with_menu_bar"):
        statics.opened_window_with_menu_bar = False
    _, statics.opened_window_with_menu_bar = imgui.checkbox(
        "Open Window with menu bar", statics.opened_window_with_menu_bar)

    if statics.opened_window_with_menu_bar:
        with imgui_ctx.begin("Window with menu bar", None, imgui.WindowFlags_.menu_bar.value):
            with imgui_ctx.begin_menu_bar():
                with imgui_ctx.begin_menu("Enabled Menu", True) as menu:
                    if menu.visible:
                        imgui.menu_item_simple("This is a menu item!")
                with imgui_ctx.begin_menu("Disabled Menu", False) as menu:
                    if menu.visible:
                        imgui.menu_item_simple("This is a menu item!")


def demo_main_menu_bar():
    with imgui_ctx.begin_main_menu_bar():
        with imgui_ctx.begin_menu("Enabled Menu", True) as menu:
            if menu.visible:
                imgui.menu_item_simple("This is a menu item!")
        with imgui_ctx.begin_menu("Disabled Menu", False) as menu:
            if menu.visible:
                imgui.menu_item_simple("This is a menu item!")


def gui():
    # Leave some room for the main menu
    imgui.new_line()
    imgui.new_line()

    imgui.button("About this demo")
    if imgui.is_item_hovered():
        with imgui_ctx.begin_tooltip():
            imgui.dummy(immapp.em_to_vec2(50, 1))
            imgui_md.render(DOC)

    demos = {
        "Begin/End": demo_begin,
        "Begin/End Child": demo_begin_child,
        "Begin/End Menu": demo_menu_bar,
        "Begin/End Tooltip": demo_begin_tooltip,
        "Begin/End Popup": demo_begin_popup,
        "Begin/End Table": demo_begin_table,
        "Begin/End Tab Bar": demo_begin_tab_bar,
        "Begin/End Drag and Drop": demo_begin_drag_and_drop,
        "Begin/End Group": demo_begin_group,
        "Tree Node": demo_tree_node,
        "Push/Pop": demo_push_pop,
    }

    for demo_name, demo_fn in demos.items():
        if imgui.tree_node(demo_name):
            demo_fn()
            # Show code of demo_fn
            imgui.separator_text("Source code")
            imgui_md.render("```python\n" + inspect.getsource(demo_fn) + "\n```")

            imgui.tree_pop()

    demo_main_menu_bar()


def main():
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_geometry.size = (800, 900)
    runner_params.app_window_params.window_title = "Demo Python Context Manager"
    runner_params.callbacks.show_gui = gui

    addons = immapp.AddOnsParams()
    addons.with_markdown = True

    def load_font():
        global SOURCE_FONT, STANDARD_FONT
        STANDARD_FONT = hello_imgui.load_font_ttf("fonts/DroidSans.ttf", 14.5)
        SOURCE_FONT = hello_imgui.load_font_ttf("fonts/Inconsolata-Medium.ttf", 16)
    runner_params.callbacks.load_additional_fonts = load_font

    immapp.run(runner_params, addons)


if __name__ == "__main__":
    main()
