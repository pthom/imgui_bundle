import dearpygui.dearpygui as dpg  # type: ignore

selected_item = None
items = ["Apple", "Banana", "Cherry"]

dpg.create_context()

def on_selection_changed(sender, app_data):
    global selected_item
    selected_item = app_data
    dpg.set_value("result_label", f"You selected: {selected_item}")

with dpg.window(tag="Primary Window", label="Fruit Picker"):
    dpg.add_text("Choose a fruit:")
    dpg.add_listbox(
        items=items,
        default_value=selected_item,
        callback=on_selection_changed,
        num_items=len(items),
        tag="fruit_list"
    )
    dpg.add_text(f"You selected: {selected_item}", tag="result_label")

dpg.create_viewport(title='Fruit Picker', width=400, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
