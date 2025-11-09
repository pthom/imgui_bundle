from imgui_bundle import immvision, immapp, imgui_md, ImVec2, imgui, hello_imgui
from imgui_bundle.demos_python import demo_utils

immvision.use_rgb_color_order()

@immapp.static(inited=False)
def demo_gui() -> None:
    statics = demo_gui
    if not statics.inited:
        statics.image_display_size = ImVec2(0, immapp.em_size(15))

        assets_dir = demo_utils.demos_assets_folder() + "/images/"

        # Load images as numpy arrays
        statics.bear = demo_utils.imread_demo(assets_dir + "bear_transparent.png", load_alpha=True)
        statics.tennis = demo_utils.imread_demo(assets_dir + "tennis.jpg")

        statics.params = immvision.ImageParams()
        bear_display_size = int(hello_imgui.em_size(15))
        statics.params.image_display_size = (bear_display_size, bear_display_size)
        statics.inited = True

    imgui.begin_group()
    imgui_md.render_unindented("# immvision.image_display()")
    imgui_md.render_unindented("Displays an image (possibly resizable)")
    immvision.image_display_resizable(
        "Tennis", statics.tennis, size=statics.image_display_size
    )
    imgui.end_group()

    imgui.same_line()

    imgui.begin_group()
    imgui_md.render_unindented("# immvision.image()")
    imgui_md.render_unindented("Displays an image, while providing lots of visualization options.")
    immvision.image("Bear", statics.bear, statics.params)
    imgui_md.render_unindented("""
        * Zoom in/out using the mouse wheel.
        * Pixel values are displayed at high zoom levels.
        * Pan the image by dragging it with the left mouse button
        * Open settings via button (bottom right corner of the image)
        """)
    imgui.end_group()


def main():
    demo_utils.set_hello_imgui_demo_assets_folder()
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)


if __name__ == "__main__":
    main()
