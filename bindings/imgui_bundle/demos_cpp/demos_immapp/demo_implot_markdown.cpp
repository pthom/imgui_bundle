#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"
#include "immapp/code_utils.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <map>


// This function returns the different help strings that are displayed in this demo application
std::string GetDoc(const std::string& whichDoc);


// Your global application state, that will be edited during the execution
struct AppState
{
    // you can edit the ImPlot pie chart values
    std::vector<float> PlotData = {0.15f, 0.30f, 0.2f, 0.05f};

    // You can edit a demo markdown string
    char MarkdownInput[4000] = "*Welcome to the interactive markdown demo!* Try writing some markdown content here.";

    // Flags that set whether we show help strings
    bool ShowAssetsInfo = false;
    bool ShowMarkdownInfo = false;
    bool ShowImplotInfo = false;

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
    ImGuiMd::RenderUnindented(GetDoc("AssetsIntro"));
    ImGui::Text("Here are some icons from Font Awesome: ");
    ImGui::SameLine(); ImGui::SetCursorPosX(HelloImGui::EmSize(40.f));
    ImGui::Text(ICON_FA_INFO " " ICON_FA_EXCLAMATION_TRIANGLE " " ICON_FA_SAVE);


    ImGui::Text("Here is an image that was loaded from the assets: ");
    ImGui::SameLine(); ImGui::SetCursorPosX(HelloImGui::EmSize(40.f));

    // Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    //     Below, imageSize is equivalent to the size of 5 lines of text
    ImVec2 imageSize = HelloImGui::EmToVec2(3.f, 3.f);
    HelloImGui::ImageFromAsset("images/world.jpg", imageSize);

    // Display help
    ImGui::Checkbox("More info", &appState.ShowAssetsInfo);
    if (appState.ShowAssetsInfo)
        ImGuiMd::RenderUnindented(GetDoc("AssetsDoc"));
}


// A demo about the usage of the markdown renderer
void DemoMarkdown(AppState& appState)
{
    std::string markdownDemo = R"(
        # Demo markdown usage

        *Let's ask GPT4 to give us some fun programming fortunes:*

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

    // Display help
    ImGui::Checkbox("More info##Markdown", &appState.ShowMarkdownInfo);
    if (appState.ShowMarkdownInfo)
        ImGuiMd::RenderUnindented(GetDoc("MarkdownDoc"));
}


// A demo showcasing the usage of ImPlot
void DemoPlot(AppState& appState)
{
    ImGuiMd::RenderUnindented(GetDoc("PlotIntro"));

    static const char* data_labels[]    = {"Frogs", "Hogs", "Dogs", "Logs"};

    ImGui::Text("Edit Pie Chart values");
    ImGui::SetNextItemWidth(250);
    ImGui::DragFloat4("Pie Data", appState.PlotData.data(), 0.01f, 0, 1);

    // Prefer to specify sizes using the "em" unit: see https://en.wikipedia.org/wiki/Em_(typography)
    //     Below, plotSize is equivalent to the size of 20 lines of text
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

    // Display help
    ImGui::Checkbox("More info##Implot", &appState.ShowImplotInfo);
    if (appState.ShowImplotInfo)
        ImGuiMd::RenderUnindented(GetDoc("PlotDoc"));
}


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
// Note: the code below only defines the displayed help strings
//

std::string GetDoc(const std::string& whichDoc)
{
    static std::map<std::string, std::string> docs =
        {
            {
                "AssetsIntro",
                R"(
                # Demos assets
                In order to improve text rendering, HelloImGui will load a default font (DroidSans) as well as "Font Awesome" to be able to display some icons.
                )"
            },
            {
                "AssetsDoc",
                R"(
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
                HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
                ```


                **Where to find the default assets**

                Look at the [imgui_bundle/bindings/imgui_bundle/assets](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/assets) folder which provides them.
                You can either copy it besides your CMakeLists.txt (it will be deployed into the execution folder automatically), or copy it into your execution folder.


                **How was this image displayed**

                This image was found inside the assets folder at `assets/images/world.jpg` and displayed via HelloImGui with the following code:
                ```cpp
                ImVec2 imageSize = HelloImGui::EmToVec2(5.f, 5.f);
                HelloImGui::ImageFromAsset("images/world.jpg", imageSize);
                ```

                *Note: prefer to specify sizes using the ["em" unit](https://en.wikipedia.org/wiki/Em_(typography)). Here, `imageSize` is equivalent to the size of 5 lines of text.*

                )"
            },
            {
                "MarkdownDoc",
                R"(
                This markdown string was rendered by calling:
                ```cpp
                ImGuiMd::Render(markdown_string);           // render a markdown string
                // or
                ImGuiMd::RenderUnindented(markdown_string);  // remove top-most indentation before rendering
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
                |         |         \-- Roboto-RegularItalic.ttf
                |         +-- SourceCodePro-Regular.ttf
                |         +-- fontawesome-webfont.ttf
                +-- images/
                    +-- markdown_broken_image.png
                ```

                Note: in order to use ImPlot, you need to "activate" this add-on, like this:
                ```cpp
                ImmApp::AddOnsParams addons { .withMarkdown = true };
                ImmApp::Run(runnerParams, addons);
                ```
                )"
            },
            {
                "PlotIntro",
                R"(
                # Demo Plot
                By using ImPlot, you can display lots of different plots. See [online demo](https://traineq.org/implot_demo/src/implot_demo.html) which demonstrates lots of plot types (LinePlot, ScatterPlot, Histogram, Error Bars, Heatmaps, etc.)
                )"
            },
            {
                "PlotDoc",
                R"(
                Note: in order to use ImPlot, you need to "activate" this add-on, like this:
                ```cpp
                ImmApp::AddOnsParams addons { .withImplot = true };
                ImmApp::Run(runnerParams, addons);
                ```
                )"
            },
        };

    return docs.at(whichDoc);
}

