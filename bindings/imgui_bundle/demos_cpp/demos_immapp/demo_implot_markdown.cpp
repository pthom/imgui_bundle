#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <cmath>


int main(int, char**)
{
    // This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    constexpr double pi = 3.1415926535897932384626433;
    std::vector<double> x, y1, y2;
    for (double _x = 0; _x < 4 * pi; _x += 0.01)
    {
        x.push_back(_x);
        y1.push_back(std::cos(_x));
        y2.push_back(std::sin(_x));
    }

    auto gui = [x,y1,y2]()
    {
        ImGuiMd::Render("# This is the plot of _cosinus_ and *sinus*");  // Markdown
        if (ImPlot::BeginPlot("Plot"))
        {
            ImPlot::PlotLine("y1", x.data(), y1.data(), x.size());
            ImPlot::PlotLine("y2", x.data(), y2.data(), x.size());
            ImPlot::EndPlot();
        }
    };

    HelloImGui::SimpleRunnerParams runnerParams { .guiFunction = gui, .windowSize = {600, 400} };
    ImmApp::AddOnsParams addons { .withImplot = true, .withMarkdown = true };
    ImmApp::Run(runnerParams, addons);

    return 0;
}
#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include <cstdio>
int main(int, char**) { std::printf("This demo requires ImPlot.\n"); }
#endif
