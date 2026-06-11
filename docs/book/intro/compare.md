# How Does It Compare?

Not sure if Dear ImGui Bundle is right for you? Compare the code styles with other popular GUI libraries, when creating the app below:

![Fruit picker app](../images/choose_fruit.jpg)

::::{tab-set}

:::{tab-item} ImGui Bundle
**12 lines** – True immediate mode: UI declaration *is* the event handler

```python
from imgui_bundle import imgui, hello_imgui

selected_idx = 0
items = ["Apple", "Banana", "Cherry"]

def gui():
    global selected_idx
    imgui.text("Choose a fruit:")
    _changed, selected_idx = imgui.list_box("##fruits", selected_idx, items)
    imgui.text(f"You selected: {items[selected_idx]}")

hello_imgui.run(gui, window_title="Fruit Picker", window_size_auto=True)
```

**Strengths**: Simplest code, real-time capable, runs on desktop + web (Pyodide), 20+ integrated libraries, full C++ support

**Best for**: Tools, visualization, games, scientific apps
:::

:::{tab-item} Qt
**31 lines** – Retained mode with class hierarchy and signals/slots

```python
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget

items = ["Apple", "Banana", "Cherry"]

class FruitPicker(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Choose a fruit:")
        self.list_widget = QListWidget()
        self.list_widget.addItems(items)
        self.result_label = QLabel(f"You selected: {items[0]}")
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_selection_changed(self, index):
        self.result_label.setText(f"You selected: {items[index]}")

app = QApplication([])
window = FruitPicker()
window.show()
app.exec()
```

**Qt strengths**: More widgets, Qt Designer, larger ecosystem, rich text, accessibility, native look

**ImGui Bundle strengths**: Simpler code, real-time, lighter weight, scientific viz, easier cross-compilation

**Qt is Best for**: Traditional business apps, enterprise software
:::

:::{tab-item} DearPyGui
**29 lines** – ImGui-based but with retained-mode API and callbacks

```python
import dearpygui.dearpygui as dpg

items = ["Apple", "Banana", "Cherry"]
dpg.create_context()

def on_selection_changed(sender, app_data):
    dpg.set_value("result_label", f"You selected: {app_data}")

with dpg.window(tag="Primary Window", label="Fruit Picker"):
    dpg.add_text("Choose a fruit:")
    dpg.add_listbox(items=items, callback=on_selection_changed, num_items=len(items))
    dpg.add_text("You selected: ", tag="result_label")

dpg.create_viewport(title='Fruit Picker', width=400, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
```

**DearPyGui strengths**: Familiar retained-mode API, large user base, good reputation

**ImGui Bundle strengths**: True immediate mode, more libraries (~20), C++ support, Pyodide web support

**DearPyGui is Best for**: Developers who prefer retained-mode patterns
:::

:::{tab-item} NiceGUI
**15 lines** – Web-based with callbacks

```python
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
```

**NiceGUI strengths**: Web-native, modern UI, easy deployment, familiar web paradigm, reactive

**ImGui Bundle strengths**: Native performance, desktop-native, offline capable, advanced widgets, lower latency

**NiceGUI is Best for**: Web-first apps, internal dashboards, CRUD interfaces
:::

:::{tab-item} Gradio
**18 lines** – Declarative blocks with event wiring

```python
import gradio as gr

items = ["Apple", "Banana", "Cherry"]
selected_item = items[0]

def on_selection_change(choice):
    global selected_item
    selected_item = choice
    return f"You selected: {choice}"

with gr.Blocks() as demo:
    gr.Markdown("# Fruit Picker")
    gr.Markdown("Choose a fruit:")
    dropdown = gr.Dropdown(choices=items, value=items[0], label="Choose a fruit")
    output = gr.Textbox(value=f"You selected: {items[0]}", label="Selection", interactive=False)
    dropdown.change(fn=on_selection_change, inputs=dropdown, outputs=output)

demo.launch()
```

**Gradio strengths**: Web-native, ML-focused, Hugging Face integration, easy sharing, pre-built media components

**ImGui Bundle strengths**: Native performance, desktop-native, stateful apps, professional tools, flexibility

**Gradio is Best for**: ML model demos, Hugging Face Spaces, sharing with non-technical users
:::

::::

:::{note}
These examples are [available here](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/sandbox/compare_other_libs)
:::

