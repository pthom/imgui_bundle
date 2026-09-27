"""
Dear ImGui drawn with WebGPU, through wgpu-py.

ImGui drawn with WebGPU, by the ImGui renderer of [wgpu-py](https://github.com/pygfx/wgpu-py), in a
[rendercanvas](https://github.com/pygfx/rendercanvas) window. wgpu-py uses Dear ImGui Bundle for its GUIs. Shows the
ImGui demo, and a window with markdown and a formula. Needs `pip install imgui-bundle[wgpu]`.

The renderer comes with wgpu-py (`wgpu.utils.imgui.ImguiRenderer`), not from this repository. More examples in
[wgpu-py's repository](https://github.com/pygfx/wgpu-py/tree/main/examples): their names start with `imgui_`. See also
[Pure Python backends](https://imgui-bundle.pages.dev/doc/python/pure-python-backend/).
"""

import wgpu  # type: ignore
import sys
from imgui_bundle import imgui, imgui_ctx, rich_md
from rendercanvas.auto import RenderCanvas, loop  #type: ignore
from wgpu.utils.imgui import ImguiRenderer  #type: ignore


# Create a canvas to render to
canvas = RenderCanvas(
    title="imgui", size=(640, 480), max_fps=60, update_mode="continuous"
)

# Create a wgpu device
adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
device = adapter.request_device_sync()

app_state = {"text": "Hello, World\nLorem ipsum, etc.\netc."}
imgui_renderer = ImguiRenderer(device, canvas)

# Markdown: textures are created by wgpu's ImGui backend (Dear ImGui's texture protocol)
md_options = rich_md.MarkdownOptions()
md_options.with_latex = True  # LaTeX formulas ($...$ and $$...$$)
rich_md.create_context(md_options)  # the markdown fonts load at the first render


def update_gui():
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, _ = imgui.menu_item("Quit", "Cmd+Q", False, True)
            if clicked_quit:
                sys.exit(0)

            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.show_demo_window()

    imgui.set_next_window_size((300, 0), imgui.Cond_.appearing)
    imgui.set_next_window_pos((0, 20), imgui.Cond_.appearing)

    imgui.begin("Custom window", None)
    rich_md.render(r"""
    # Hello, World
    Here is some *markdown* text, and a formula: $e^{i\pi} + 1 = 0$

    ![](images/world.png)

    ```python
    print("code blocks too")
    ```
    """)

    imgui.text("Example Text")

    if imgui.button("Hello"):
        print("World")

    _, app_state["text"] = imgui.input_text_multiline(
        "Edit", app_state["text"], imgui.ImVec2(200, 200)
    )
    io = imgui.get_io()
    imgui.text(
        f"""
    Keyboard modifiers:
        {io.key_ctrl=}
        {io.key_alt=}
        {io.key_shift=}
        {io.key_super=}"""
    )

    if imgui.button("Open popup"):
        imgui.open_popup("my popup")
    with imgui_ctx.begin_popup_modal("my popup") as popup:
        if popup.visible:
            imgui.text("Hello from popup!")
            if imgui.button("Close popup"):
                imgui.close_current_popup()

    imgui.end()


# set the GUI update function that gets called to return the draw data
imgui_renderer.set_gui(update_gui)


if __name__ == "__main__":
    canvas.request_draw(imgui_renderer.render)
    loop.run()
    rich_md.destroy_context()
