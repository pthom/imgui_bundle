#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <cmath>


void gui_demo_implot_markdown()
{
    static std::vector<double> x, y1, y2;
    if (x.empty())  // the data, computed once
    {
        constexpr double pi = 3.1415926535897932384626433;
        for (double _x = 0; _x < 4 * pi; _x += 0.01)
        {
            x.push_back(_x);
            y1.push_back(std::cos(_x));
            y2.push_back(std::sin(_x));
        }
    }

    RichMd::Render("# This is the plot of _cosinus_ and *sinus*");  // Markdown
    if (ImPlot::BeginPlot("Plot"))
    {
        ImPlot::PlotLine("y1", x.data(), y1.data(), x.size());
        ImPlot::PlotLine("y2", x.data(), y2.data(), x.size());
        ImPlot::EndPlot();
    }
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    // This call is specific to the ImGui Bundle Explorer. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    HelloImGui::SimpleRunnerParams runnerParams { .guiFunction = gui_demo_implot_markdown, .windowSize = {600, 400} };
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
