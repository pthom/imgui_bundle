from nicegui import ui

selected_idx = -1
items = ["Apple", "Banana", "Cherry"]

def on_selection_change(e):
    global selected_idx
    selected_idx = items.index(e.value)
    selection_label.text = f"You selected: {e.value}"

ui.label("Choose a fruit:")
dropdown = ui.select(options=items, value=items[0], on_change=on_selection_change)
selection_label = ui.label(f"You selected: {items[0]}")

ui.run(title="Fruit Picker")
