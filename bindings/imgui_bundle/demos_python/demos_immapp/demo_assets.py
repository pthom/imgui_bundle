from imgui_bundle import imgui, imgui_md, hello_imgui, immapp
from imgui_bundle.demos_python import demo_utils


def show_gui():
    # Display Markdown text
    imgui_md.render("Hello, _World_")
    # Display a static image, taken from assets/images/world.png
    # Notes:
    #     * we use EmToVec2 to make sure the Gui render identically on high and low dpi monitors
    #     * we can specify only one dimension, and the image will be scaled proportionally to its size:
    #           in this example, the image height will correspond to 10 text lines
    hello_imgui.image_from_asset("images/world.png", immapp.em_to_vec2(0.0, 10.0))

    # Display a button
    if imgui.button("Bye"):
        # ... and immediately handle its action if it is clicked!
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    # Set the assets folder path
    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())

    immapp.run(
        gui_function=show_gui,
        window_title="Hello, globe!",
        window_size_auto=True,
        with_markdown=True,  # this will initialize markdown and load the required fonts
        # Uncomment the next line to restore the window position and size from previous run
        # , window_restore_previous_geometry=True
    )


if __name__ == "__main__":
    main()
