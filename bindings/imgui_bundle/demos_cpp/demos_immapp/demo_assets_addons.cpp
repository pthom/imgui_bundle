#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "implot/implot.h"
#endif
#include "immapp/code_utils.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <map>


// This function displays the help messages that are displayed in this demo application
void ShowDoc(const std::string& whichDoc);


// Your global application state, that will be edited during the execution
struct AppState
{
    // you can edit the ImPlot pie chart values
    std::vector<float> PlotData = {0.15f, 0.30f, 0.2f, 0.05f};

    // You can edit a demo markdown string
    char MarkdownInput[4000] = "*Welcome to the interactive markdown demo!* Try writing some markdown content here.";

    //
    // Note about AppState:
    // Inside ImGui demo code, you will often see static variables, such as in this example
    // ```cpp
    //     static int value = 10;
    //     bool changed = ImGui::SliderInt("Value", &value, 0, 10);  // edit this variable between 0 and 10
    // ```
    // In this example, `value` is a static variable whose state is preserved:
    // it merely acts as a global variable, whose scope is limited to this function.
    // Global variables should be avoided, and storing the Application State like this is preferable in production code.
    //
};


// A demo showcasing the assets usage in HelloImGui and ImmApp
void DemoAssets(AppState& appState)
{
    ImGuiMd::Render("# Demo Assets");
    ImGui::Text("Here are some icons from Font Awesome: ");
    ImGui::SameLine(); ImGui::SetCursorPosX(HelloImGui::EmSize(40.f));
    ImGui::Text(ICON_FA_INFO " " ICON_FA_EXCLAMATION_TRIANGLE " " ICON_FA_SAVE);


    ImGui::Text("Here is an image that was loaded from the assets: ");
    ImGui::SameLine(); ImGui::SetCursorPosX(HelloImGui::EmSize(40.f));

    // Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    //     Below, imageSize is equivalent to the size of 3 lines of text
    ImVec2 imageSize = HelloImGui::EmToVec2(3.f, 3.f);
    HelloImGui::ImageFromAsset("images/world.png", imageSize);

    ImGuiMd::Render("**Read the [documentation about assets](https://pthom.github.io/imgui_bundle/quickstart.html#quickstart_about_assets)**");

    ShowDoc("AssetsDoc");
}


// A demo about the usage of the markdown renderer
void DemoMarkdown(AppState& appState)
{
    std::string markdownDemo = R"(
        # Demo markdown usage

        Let's ask GPT4 to give us some fun programming fortunes in markdown format:

        1. **Bug Hunt**: In the world of software, the best debugger was, is, and will always be a _good night's sleep_.

        2. **Pythonic Wisdom**:
            > They say if you can't explain something simply, you don't understand it well enough. Well, here's my Python code for simplicity:
            ```python
            def explain(thing):
                return "It's just a " + thing + ". Nothing fancy!"
            ```
        )";
    ImGuiMd::RenderUnindented(markdownDemo);

    // Interactive demo
    ImGui::Separator();
    ImGuiMd::Render("*Try it yourself*");
    ImGui::SameLine(HelloImGui::EmSize(30.f));
    if (ImGui::SmallButton("Edit the fortune markdown"))
        strcpy(appState.MarkdownInput, CodeUtils::UnindentMarkdown(markdownDemo).c_str());
    ImGui::InputTextMultiline("##Markdown Input", appState.MarkdownInput, sizeof(appState.MarkdownInput), HelloImGui::EmToVec2(40.f, 5.f));
    ImGuiMd::RenderUnindented(appState.MarkdownInput);
    ImGui::Separator();

    ShowDoc("MarkdownDoc");
}


#ifdef IMGUI_BUNDLE_WITH_IMPLOT
// A demo showcasing the usage of ImPlot
void DemoPlot(AppState& appState)
{
    ImGuiMd::Render("# Demo ImPlot");

    static const char* data_labels[]    = {"Frogs", "Hogs", "Dogs", "Logs"};

    ImGui::Text("Edit Pie Chart values");
    ImGui::SetNextItemWidth(250);
    ImGui::DragFloat4("Pie Data", appState.PlotData.data(), 0.01f, 0, 1);

    // Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    //     Below, plotSize is equivalent to the size of 1 lines of text
    ImVec2 plotSize = ImmApp::EmToVec2(15.f, 15.f);

    if (ImPlot::BeginPlot("Pie Chart", plotSize))
    {
        ImPlot::SetupAxes("", "", ImPlotAxisFlags_NoDecorations, ImPlotAxisFlags_NoDecorations);
        ImPlot::PlotPieChart(
            data_labels,
            appState.PlotData.data(), appState.PlotData.size(), // data and count
            0.5, 0.5, // pie center position in the plot(x, y). Here, it is centered
            0.35,      // pie radius relative to plotSize
            "%.2f",   // fmt
            90        // angle
            );
            ImPlot::EndPlot();
    }

    ShowDoc("PlotDoc");
}
#else
void DemoPlot(AppState& appState) {}
#endif


// Our main function
int main(int, char**)
{
    // This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    AppState appState;         // Our global appState

    // This is our GUI function:
    //     it will display the widgets
    //     it captures the appState, since it can modify it
    auto gui = [&appState]()
    {
        DemoAssets(appState);
        ImGui::NewLine();
        DemoMarkdown(appState);
        ImGui::NewLine();
        DemoPlot(appState);
    };

    // Then, we start our application:
    //     First, we set some RunnerParams, with simple settings
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.windowSize = {1000, 1000};
    //     Here we set our GUI function
    runnerParams.guiFunction = gui;
    //     Then, we need to activate two addons: ImPlot and Markdown
    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    addons.withMarkdown = true;
    //     And we are ready to go!
    ImmApp::Run(runnerParams, addons);

    return 0;
}

///////////////////////////////////////////////////////////////////////////////
// End of demo code
///////////////////////////////////////////////////////////////////////////////


//
// Note: the code below only displays the help messages
//

std::string GetDoc(const std::string& whichDoc)
{
    static std::map<std::string, std::string> docs =
        {
            {
                "AssetsDoc",
                R"(
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
                )"
            },
            {
                "MarkdownDoc",
                R"(
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
                )"
            },
            {
                "PlotDoc",
                R"(
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
                )"
            },
        };

    return docs.at(whichDoc);
}


void ShowDoc(const std::string& whichDoc)
{
    static std::map<std::string, bool> is_doc_visible;
    if (is_doc_visible.find(whichDoc) == is_doc_visible.end())
        is_doc_visible[whichDoc] = false;

    ImGui::PushID(whichDoc.c_str());
    ImGui::Checkbox("More info", &is_doc_visible[whichDoc]);

    if (is_doc_visible[whichDoc])
    {
        ImGuiMd::RenderUnindented(GetDoc(whichDoc));
        ImGui::Dummy(HelloImGui::EmToVec2(1.f, 6.f));
        ImGui::Separator();
    }
    ImGui::PopID();
}
