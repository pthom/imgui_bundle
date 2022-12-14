import os
from imgui_bundle import imgui, ImVec2, imgui_md, hello_imgui, immapp


def show_gui():
    # Display Markdown text
    imgui_md.render("Hello, _World_")
    # Display a static image, taken from assets/images/world.jpg
    hello_imgui.image_from_asset("images/world.jpg")

    # Display a button
    if imgui.button("Bye"):
        # ... and immediately handle its action if it is clicked!
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    # Set the assets folder path
    this_dir = os.path.dirname(os.path.abspath(__file__))
    hello_imgui.set_assets_folder(this_dir + "/../assets")

    immapp.run(
        gui_function=show_gui,
        window_title="Hello, globe!",
        window_size_auto=True,
        with_markdown=True, # this will initialize markdown and load the required fonts
        # Uncomment the next line to restore the window position and size from previous run
        # window_restore_previous_geometry=True
    )


if __name__ == "__main__":
    main()
