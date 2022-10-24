import os.path
from imgui_bundle import static
from imgui_bundle import imgui_color_text_edit as text_edit, imgui_md


def demo_simple():
    from imgui_bundle import imgui, hello_imgui, ImVec2

    def gui():
        imgui.text("Hello, world!")

    hello_imgui.run(gui_fonction=gui, window_size=ImVec2(200, 50), window_title="Hello!")


def demo_params():
    from imgui_bundle import hello_imgui, imgui, ImVec2

    def show_gui():
        """This is the code of the Gui displayed by this app"""
        # Display a simple label
        imgui.text("Hello, ")
        # Display a static image, taken from assets/world.jpg,
        # assets are embedded automatically into the app (for *all* platforms)
        hello_imgui.image_from_asset("world.jpg")

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

    hello_imgui.run(runner_params)


def demo_implot_markdown_simple():
    import numpy as np
    from imgui_bundle import implot, imgui_md
    import imgui_bundle

    x = np.arange(0, np.pi * 4, 0.01)
    y1 = np.cos(x)
    y2 = np.sin(x)

    def gui():
        imgui_md.render("# This is the plot of _cosinus_ and *sinus*")  # Markdown
        implot.begin_plot("Plot")
        implot.plot_line("y1", x, y1)
        implot.plot_line("y2", x, y2)
        implot.end_plot()

    imgui_bundle.run(gui, with_implot=True, with_markdown=True)


@static(was_inited=False)
def demo_hello_imgui():
    static = demo_hello_imgui
    if not static.was_inited:
        static.editor = text_edit.TextEditor()
        static.editor.set_text("")
        static.was_inited = True
    editor = static.editor

    from imgui_bundle import imgui
    from imgui_bundle.demos import demo_hello_imgui_docking
    import inspect

    imgui_md.render(
        """
# HelloImGui
[HelloImGui](https://github.com/pthom/hello_imgui) is a wrapper around ImGui that enables to easily create applications with ImGui.

Features
* Easy setup
* Advanced docking support with easy layout
    """
    )

    def show_one_feature(label, demo_function):
        from multiprocessing import Process

        if imgui.button(label):
            editor.set_text(inspect.getsource(demo_function))
            if demo_function == demo_hello_imgui_docking.main:
                editor.set_text(inspect.getsource(demo_hello_imgui_docking))
            process = Process(target=demo_function)
            process.start()

    imgui.text("Click on any button to launch a demo, and see its code")
    imgui.new_line()

    imgui.text("Hello world demo: how to start an app in as few lines as possible")
    show_one_feature("Hello world", demo_simple)

    imgui.text("How to run more complex application (via RunnerParams) and how to load assets")
    show_one_feature("Assets and Params", demo_params)

    imgui.text(
        "How to build complex applications layouts, with dockable panels, that can even become independent windows"
    )
    show_one_feature("Advanced docking demo", demo_hello_imgui_docking.main)

    imgui.text("How to quickly run an app that uses implot and/or markdown")
    show_one_feature("Implot/Markdown simple", demo_implot_markdown_simple)

    imgui.new_line()
    imgui_md.render(
        """
* Hello ImGui [API Doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md)
* Docking layout [specific documentation](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/hello_imgui_api.md#docking)
    """
    )

    if len(editor.get_text()) > 1:
        imgui.separator()
        imgui.text("Code for this demo")
        editor.render("Code")


if __name__ == "__main__":
    from imgui_bundle import hello_imgui

    hello_imgui.run(demo_hello_imgui)
