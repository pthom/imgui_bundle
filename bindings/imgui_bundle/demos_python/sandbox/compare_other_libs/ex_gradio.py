import gradio as gr

items = ["Apple", "Banana", "Cherry"]

def on_selection_change(choice):
    return f"You selected: {choice}"

def on_button_click():
    print("Button clicked")
    return "Button clicked"

with gr.Blocks() as demo:
    gr.Markdown("# Fruit Picker")
    gr.Markdown("Choose a fruit:")

    dropdown = gr.Dropdown(choices=items, value=items[0], label="Choose a fruit")
    output = gr.Textbox(value=f"You selected: {items[0]}", label="Selection", interactive=False)

    button = gr.Button("Click Me")
    button_output = gr.Textbox(label="Button Status", interactive=False)

    # Wire up the events
    dropdown.change(fn=on_selection_change, inputs=dropdown, outputs=output)
    button.click(fn=on_button_click, outputs=button_output)

demo.launch()
