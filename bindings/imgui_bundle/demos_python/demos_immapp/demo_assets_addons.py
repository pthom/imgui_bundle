from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, icons_fontawesome
from imgui_bundle.demos_python import demo_utils

from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List
from dataclasses import dataclass, field


def get_doc(which_doc: str) -> str:
    """This function returns the different help strings that are displayed in this demo application
    (implemented later in this file)"""
    ...


@dataclass
class AppState:
    """Your global application state, that will be edited during the execution."""

    # you can edit the ImPlot pie chart values
    plot_data: List[float] = field(default_factory=lambda: [0.15, 0.30, 0.2, 0.05])

    # You can edit a demo markdown string
    markdown_input: str = "*Welcome to the interactive markdown demo!* Try writing some markdown content here."

    # Flags that set whether we show help strings
    show_assets_info: bool = False
    show_markdown_info: bool = False
    show_implot_info: bool = False
    #
    # Note about AppState:
    # Inside ImGui demo code, you will often see static variables, such as in this example
    #     static int value = 10;
    #     bool changed = ImGui::SliderInt("Value", &value, 0, 10);  // edit this variable between 0 and 10
    # In this example, `value` is a static variable whose state is preserved:
    # it merely acts as a global variable, whose scope is limited to this function.
    # Global variables should be avoided, and storing the Application State like this is preferable in production code.


def demo_assets(app_state: AppState):
    """A demo showcasing the assets usage in HelloImGui and ImmApp"""
    imgui_md.render_unindented(get_doc("AssetsIntro"))

    imgui.text("Here are some icons from Font Awesome: ")
    imgui.same_line()
    imgui.set_cursor_pos_x(hello_imgui.em_size(40.0))
    imgui.text(icons_fontawesome.ICON_FA_INFO + " " + icons_fontawesome.ICON_FA_EXCLAMATION_TRIANGLE + " " + icons_fontawesome.ICON_FA_SAVE)

    imgui.text("Here is an image that was loaded from the assets: ")
    imgui.same_line()
    imgui.set_cursor_pos_x(hello_imgui.em_size(40.0))

    # Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    # Below, image_size is equivalent to the size of 5 lines of text
    image_size = hello_imgui.em_to_vec2(3.0, 3.0)
    hello_imgui.image_from_asset("images/world.jpg", image_size)

    # Display help
    _, app_state.show_assets_info = imgui.checkbox("More info", app_state.show_assets_info)
    if app_state.show_assets_info:
        imgui_md.render_unindented(get_doc("AssetsDoc"))


def demo_markdown(app_state: AppState):
    """A demo about the usage of the markdown renderer"""
    markdown_demo = """
        # Demo markdown usage

        *Let's ask GPT4 to give us some fun programming fortunes:*

        1. **Bug Hunt**: In the world of software, the best debugger was, is, and will always be a _good night's sleep_.

        2. **Pythonic Wisdom**:
            > They say if you can't explain something simply, you don't understand it well enough. Well, here's my Python code for simplicity:
            ```python
            def explain(thing):
                return "It's just a " + thing + ". Nothing fancy!"
            ```
    """
    imgui_md.render_unindented(markdown_demo)

    # Interactive demo
    imgui.separator()
    imgui_md.render("*Try it yourself*")
    imgui.same_line(hello_imgui.em_size(30.0))
    if imgui.small_button("Edit the fortune markdown"):
        app_state.markdown_input = immapp.code_utils.unindent_markdown(markdown_demo)
    _, app_state.markdown_input = imgui.input_text_multiline("##Markdown Input", app_state.markdown_input, hello_imgui.em_to_vec2(40.0, 5.0))
    imgui_md.render_unindented(app_state.markdown_input)
    imgui.separator()

    # Display help
    _, app_state.show_markdown_info = imgui.checkbox("More info##Markdown", app_state.show_markdown_info)
    if app_state.show_markdown_info:
        imgui_md.render_unindented(get_doc("MarkdownDoc"))


def demo_plot(app_state: AppState):
    """A demo showcasing the usage of ImPlot"""
    imgui_md.render_unindented(get_doc("PlotIntro"))

    data_labels = ["Frogs", "Hogs", "Dogs", "Logs"]

    imgui.text("Edit Pie Chart values")
    imgui.set_next_item_width(250)
    _, app_state.plot_data = imgui.drag_float4("Pie Data", app_state.plot_data, 0.01, 0, 1)

    # Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    # Below, plot_size is equivalent to the size of 20 lines of text
    plot_size = hello_imgui.em_to_vec2(15.0, 15.0)

    if implot.begin_plot("Pie Chart", plot_size):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.plot_pie_chart(data_labels, np.array(app_state.plot_data), 0.5, 0.5, 0.35, "%.2f", 90)
        implot.end_plot()

    # Display help
    _, app_state.show_implot_info = imgui.checkbox("More info##Implot", app_state.show_implot_info)
    if app_state.show_implot_info:
        imgui_md.render_unindented(get_doc("PlotDoc"))


def main():
    # This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    #         hello_imgui.set_assets_folder("my_assets")  # (By default, HelloImGui will search inside "assets")
    demo_utils.set_hello_imgui_demo_assets_folder()

    app_state = AppState()  # Initialize our global appState

    # This is our GUI function:
    # it will display the widgets, and it can modify the app_state
    def gui():
        demo_assets(app_state)
        imgui.new_line()
        demo_markdown(app_state)
        imgui.new_line()
        demo_plot(app_state)

    # Then, we start our application:
    runner_params = hello_imgui.SimpleRunnerParams()
    runner_params.window_size = (1000, 1000)
    runner_params.gui_function = gui

    # We need to activate two addons: ImPlot and Markdown
    addons = immapp.AddOnsParams()  # Assuming we have such a class in Python
    addons.with_implot = True
    addons.with_markdown = True

    # And we are ready to go!
    immapp.run(runner_params, addons)


# ///////////////////////////////////////////////////////////////////////////////
# // End of demo code
# ///////////////////////////////////////////////////////////////////////////////


# //
# // Note: the code below only defines the displayed help strings
# //

def get_doc(which_doc: str) -> str:
    """Return the associated documentation string based on the key."""

    docs: Dict[str, str] = {
        "AssetsIntro": """
            # Demos assets
            In order to improve text rendering, HelloImGui will load a default font (DroidSans) as well as "Font Awesome" to be able to display some icons.
        """,

        "AssetsDoc": """
            **About assets**

            HelloImGui and ImmApp applications rely on the presence of an `assets` folder.
            The typical layout of an assets folder looks like this:
            ```
            assets/
                +-- fonts/
                |         +-- DroidSans.ttf             # default fonts used by HelloImGui in order to
                |         +-- fontawesome-webfont.ttf   # improve text rendering.
                +-- images/
                          +-- world.jpg                 # you can add any asset here!
            ```

            You can change the assets folder via:
            ```cpp
            hello_imgui.set_assets_folder("my_assets"); // (By default, HelloImGui will search inside "assets")
            ```

            **Where to find the default assets**

            Look at the [imgui_bundle/bindings/imgui_bundle/assets](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/assets) folder which provides them.
            You can copy it into your execution folder.

            **How was this image displayed**

            This image was found inside the assets folder at `assets/images/world.jpg` and displayed via HelloImGui with the following code:
            ```python
            image_size = hello_imgui.em_to_vec2(5., 5.)
            hello_imgui.image_from_asset("images/world.jpg", imageSize);
            ```

            *Note: prefer to specify sizes using the ["em" unit](https://en.wikipedia.org/wiki/Em_(typography)). Here, `image_size` is equivalent to the size of 5 lines of text.*
        """,

        "MarkdownDoc": """
            This markdown string was rendered by calling:
            ```python
            imgui_md.render(markdown_string);             # render a markdown string
            # or
            imgui_md.render_unindented(markdown_string);  # remove top-most indentation before rendering
            ```

            This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.
            It supports the most common markdown features: emphasis, link, code blocks, etc.

            In order to work, it needs a few files in the assets folder:
            ```
            assets/
            +-- fonts/
            |         +-- DroidSans.ttf
            |         +-- Roboto/
            |         |         +-- LICENSE.txt
            |         |         +-- Roboto-Bold.ttf
            |         |         +-- Roboto-BoldItalic.ttf
            |         |         +-- Roboto-Regular.ttf
            |         |         \\-- Roboto-RegularItalic.ttf
            |         +-- SourceCodePro-Regular.ttf
            |         +-- fontawesome-webfont.ttf
            +-- images/
                +-- markdown_broken_image.png
            ```

            Note: in order to use ImPlot, you need to "activate" this add-on, like this:
            ```python
            addons = immapp.AddOnsParams(with_markdown=True)
            immapp.run(runner_params, addons);
            ```
        """,

        "PlotIntro": """
            # Demo Plot
            By using ImPlot, you can display lots of different plots. See [online demo](https://traineq.org/implot_demo/src/implot_demo.html) which demonstrates lots of plot types (LinePlot, ScatterPlot, Histogram, Error Bars, Heatmaps, etc.)
        """,

        "PlotDoc": """
            Note: in order to use ImPlot, you need to "activate" this add-on, like this:
            ```python
            addons = immapp.AddOnsParams(with_implot=True)
            immapp.run(runnerParams, addons);
            ```
        """
    }

    return docs[which_doc]


if __name__ == "__main__":
    main()
