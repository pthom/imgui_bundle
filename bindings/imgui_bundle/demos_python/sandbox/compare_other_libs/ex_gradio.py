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
