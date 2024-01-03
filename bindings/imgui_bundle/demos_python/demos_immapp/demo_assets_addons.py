from imgui_bundle import imgui, implot, immapp, hello_imgui, imgui_md, icons_fontawesome
from imgui_bundle.demos_python import demo_utils

import numpy as np
from typing import Dict, List
from dataclasses import dataclass, field


def show_doc(which_doc: str):
    """This function displays the help messages that are displayed in this demo application
    (implemented later in this file)"""
    ...


@dataclass
class AppState:
    """Your global application state, that will be edited during the execution."""

    # you can edit the ImPlot pie chart values
    plot_data: List[float] = field(default_factory=lambda: [0.15, 0.30, 0.2, 0.05])

    # You can edit a demo markdown string
    markdown_input: str = "*Welcome to the interactive markdown demo!* Try writing some markdown content here."

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
    imgui_md.render("# Demo Assets")

    imgui.text("Here are some icons from Font Awesome: ")
    imgui.same_line()
    imgui.set_cursor_pos_x(hello_imgui.em_size(40.0))
    imgui.text(
        icons_fontawesome.ICON_FA_INFO
        + " "
        + icons_fontawesome.ICON_FA_EXCLAMATION_TRIANGLE
        + " "
        + icons_fontawesome.ICON_FA_SAVE
    )

    imgui.text("Here is an image that was loaded from the assets: ")
    imgui.same_line()
    imgui.set_cursor_pos_x(hello_imgui.em_size(40.0))

    # Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    # Below, image_size is equivalent to the size of 3 lines of text
    image_size = hello_imgui.em_to_vec2(3.0, 3.0)
    hello_imgui.image_from_asset("images/world.png", image_size)

    imgui_md.render(
        "**Read the [documentation about assets](https://pthom.github.io/imgui_bundle/quickstart.html#quickstart_about_assets)**"
    )
    show_doc("AssetsDoc")


def demo_markdown(app_state: AppState):
    """A demo about the usage of the markdown renderer"""
    markdown_demo = """
        # Demo markdown usage

        Let's ask GPT4 to give us some fun programming fortunes in markdown format:

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
    _, app_state.markdown_input = imgui.input_text_multiline(
        "##Markdown Input", app_state.markdown_input, hello_imgui.em_to_vec2(40.0, 5.0)
    )
    imgui_md.render_unindented(app_state.markdown_input)
    imgui.separator()

    show_doc("MarkdownDoc")


def demo_plot(app_state: AppState):
    """A demo showcasing the usage of ImPlot"""
    imgui_md.render("# Demo ImPlot")

    data_labels = ["Frogs", "Hogs", "Dogs", "Logs"]

    imgui.text("Edit Pie Chart values")
    imgui.set_next_item_width(250)
    _, app_state.plot_data = imgui.drag_float4(
        "Pie Data", app_state.plot_data, 0.01, 0, 1
    )

    # Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    # Below, plot_size is equivalent to the size of 15 lines of text
    plot_size = hello_imgui.em_to_vec2(15.0, 15.0)

    if implot.begin_plot("Pie Chart", plot_size):
        implot.setup_axes(
            "",
            "",
            implot.AxisFlags_.no_decorations.value,
            implot.AxisFlags_.no_decorations.value,
        )
        implot.plot_pie_chart(
            data_labels, np.array(app_state.plot_data), 0.5, 0.5, 0.35, "%.2f", 90
        )
        implot.end_plot()

    show_doc("PlotDoc")


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
    #     First, we set some RunnerParams, with simple settings
    runner_params = hello_imgui.SimpleRunnerParams()
    runner_params.window_size = (1000, 1000)
    runner_params.gui_function = gui
    #     We need to activate two addons: ImPlot and Markdown
    addons = immapp.AddOnsParams()
    addons.with_implot = True
    addons.with_markdown = True
    #     And we are ready to go!
    immapp.run(runner_params, addons)


# ///////////////////////////////////////////////////////////////////////////////
# // End of demo code
# ///////////////////////////////////////////////////////////////////////////////


# //
# // Note: the code below only displays the help messages
# //


def get_doc(which_doc: str) -> str:
    """Return the associated documentation string based on the key."""

    docs: Dict[str, str] = {
        "AssetsDoc": """
            The icons and image were shown via this code:

            C++
            ```cpp
            ImGui::Text(ICON_FA_INFO " " ICON_FA_EXCLAMATION_TRIANGLE " " ICON_FA_SAVE);
            ImVec2 imageSize = HelloImGui::EmToVec2(3.f, 3.f);
            HelloImGui::ImageFromAsset("images/world.png", imageSize);
            ```

            Python
            ```python
            imgui.text(icons_fontawesome.ICON_FA_INFO + " " + icons_fontawesome.ICON_FA_EXCLAMATION_TRIANGLE + " " + icons_fontawesome.ICON_FA_SAVE)
            image_size = hello_imgui.em_to_vec2(3.0, 3.0)
            hello_imgui.image_from_asset("images/world.png", image_size)
            ```

            *Note: In this code, imageSize is equivalent to the size of 3 lines of text, using the [em unit](https://en.wikipedia.org/wiki/Em_(typography))*
        """,
        "MarkdownDoc": """
            This markdown string was rendered by calling either:

            C++
            ```cpp
            ImGuiMd::Render(markdown_string);            // render a markdown string
            ImGuiMd::RenderUnindented(markdown_string);  // remove top-most indentation before rendering
            ```

            Python
            ```python
            imgui_md.render(markdown_string);            # render a markdown string
            imgui_md.render_unindented(markdown_string); # remove top-most indentation before rendering
            ```

            This markdown renderer is based on [imgui_md](https://github.com/mekhontsev/imgui_md), by Dmitry Mekhontsev.
            It supports the most common markdown features: emphasis, link, code blocks, etc.
        """,
        "PlotDoc": """
            By using ImPlot, you can display lots of different plots. See [online demo](https://traineq.org/implot_demo/src/implot_demo.html) which demonstrates lots of plot types (LinePlot, ScatterPlot, Histogram, Error Bars, Heatmaps, etc.)

            Note: in order to use ImPlot, you need to "activate" this add-on, like this:

            C++
            ```cpp
            ImmApp::AddOnsParams addons { .withImplot = true };
            ImmApp::Run(runnerParams, addons);
            ```

            Python:
            ```python
            addons = immapp.AddOnsParams(with_implot=True)
            immapp.run(runner_params, addons);
            ```
        """,
    }

    return docs[which_doc]


@immapp.static(is_doc_visible={})  # type: ignore # (ignore redef)
def show_doc(which_doc):  # noqa: F811
    # Access the 'static' variable
    is_doc_visible = show_doc.is_doc_visible

    # Check if the doc visibility entry exists, if not, add it
    if which_doc not in is_doc_visible:
        is_doc_visible[which_doc] = False

    imgui.push_id(which_doc)
    _, is_doc_visible[which_doc] = imgui.checkbox(
        "More info", is_doc_visible[which_doc]
    )

    if is_doc_visible[which_doc]:
        # The following are assumed to be valid calls within the context of your specific ImGui wrapper.
        # 'imgui_md' and 'get_doc' should correspond to your actual usage and imports.
        imgui_md.render_unindented(get_doc(which_doc))
        imgui.dummy(
            hello_imgui.em_to_vec2(1.0, 6.0)
        )  # Assumes 'hello_imgui' is available in your environment
        imgui.separator()

    imgui.pop_id()


if __name__ == "__main__":
    main()
