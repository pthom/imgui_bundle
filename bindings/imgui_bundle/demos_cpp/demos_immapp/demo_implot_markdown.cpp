// An animated plot and some markdown, in a few lines.
// A cosine wave moves in an ImPlot plot, under a text written in markdown. Both are add-ons, activated in one call:
// `ImmApp::Run(runnerParams, {.withImplot = true, .withMarkdown = true})`. A good start for a small app.
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <cmath>


void gui_demo_implot_markdown()
{
    // Render some markdown text
    RichMd::Render(R"(
        # Render an animated plot with ImPlot
        This example shows how to use `ImPlot` to render an animated plot,
        and how to use `RichMd` to render markdown text (*this text!*).
    )");

    // Render an animated plot:
    // the window's width (-1), and 20 em high (1 em = the height of a character)
    if (ImPlot::BeginPlot("Plot", ImVec2(-1.f, HelloImGui::EmSize(20.f))))
    {
        constexpr double pi = 3.1415926535897932384626433;
        std::vector<double> x, y;
        for (double _x = 0; _x < 4 * pi; _x += 0.01)
        {
            x.push_back(_x);
            y.push_back(std::cos(_x + ImGui::GetTime()));
        }
        ImPlot::PlotLine("y1", x.data(), y.data(), (int)x.size());
        ImPlot::EndPlot();
    }

    if (ImGui::Button("Exit"))
        HelloImGui::GetRunnerParams()->appShallExit = true;
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    // This call is specific to the ImGui Bundle Explorer. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    // Run the app with ImPlot and markdown support
    HelloImGui::SimpleRunnerParams runnerParams { .guiFunction = gui_demo_implot_markdown, .windowSize = {700, 500} };
    ImmApp::AddOnsParams addons { .withImplot = true, .withMarkdown = true };
    ImmApp::Run(runnerParams, addons);

    return 0;
}
#endif
#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include <cstdio>
void gui_demo_implot_markdown() { ImGui::Text("This demo requires ImPlot."); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**) { std::printf("This demo requires ImPlot.\n"); }
#endif
#endif
