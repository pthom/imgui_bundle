import os


def main():
    from imgui_bundle import imgui, ImVec2, imgui_md, hello_imgui, run

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
            runner_params.app_shall_exit = True

    # Instantiate RunnerParams which will contains all the application params and callbacks
    runner_params = hello_imgui.RunnerParams()

    # Set the app windows parameters
    runner_params.app_window_params.window_title = "Hello, globe!"
    runner_params.app_window_params.window_size = ImVec2(180, 210)

    # runner_params.callbacks.show_gui should contain a function with the Gui code
    runner_params.callbacks.show_gui = show_gui

    # Set the assets folder path
    this_dir = os.path.dirname(os.path.abspath(__file__))
    hello_imgui.set_assets_folder(this_dir + "/assets")

    run(runner_params, with_markdown=True)


if __name__ == "__main__":
    main()
