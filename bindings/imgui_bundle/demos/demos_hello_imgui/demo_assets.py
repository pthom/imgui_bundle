import os


def main():
    from imgui_bundle import imgui, ImVec2, imgui_md, hello_imgui, run, AddOnsParams

    def show_gui():
        """This is the code of the Gui displayed by this app"""

        # Display Markdown text
        imgui_md.render("Hello, _World_")
        # Display a static image, taken from assets/world.jpg,
        # assets are embedded automatically into the app (for *all* platforms)
        hello_imgui.image_from_asset("images/world.jpg")

        # Display a button
        if imgui.button("Bye"):
            # ... and immediately handle its action if it is clicked!
            # here, the flag appShallExit will tell HelloImGui to end the app.
            hello_imgui.get_runner_params().app_shall_exit = True

    # Set the assets folder path
    this_dir = os.path.dirname(os.path.abspath(__file__))
    hello_imgui.set_assets_folder(this_dir + "/assets")

    run(
        gui_function=show_gui,
        window_title="Hello, globe!",
        window_size_auto=True,
        with_markdown=True,
        # Uncomment the next line to restore the window position and size from previous run
        # window_restore_previous_geometry=True
    )


if __name__ == "__main__":
    main()
