#include "imgui_bundle/imgui_bundle.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "implot/implot.h"
#include "imgui_md_wrapper.h"

#include <vector>
#include <cmath>

int main(int, char **)
{
    double pi = 3.1415;
    std::vector<double> x, y1, y2;
    for (int i = 0; i < 1000; ++i)
    {
        double x_ = pi * 4. * (double)i / 1000.;
        x.push_back(x_);
        y1.push_back(cos(x_));
        y2.push_back(sin(x_));
    }

    auto gui = [&]() {
        ImGuiMd::Render("# This is the plot of _cosinus_ and *sinus*");
        ImPlot::BeginPlot("Plot");
        ImPlot::PlotLine("y1", x.data(), y1.data(), x.size());
        ImPlot::PlotLine("y2", x.data(), y2.data(), x.size());
        ImPlot::EndPlot();
    };


    ImGuiBundle::Run(
        HelloImGui::SimpleRunnerParams{ .guiFunction=gui, .windowTitle="demo_implot_markdown", .windowSize={640, 400} },
        ImGuiBundle::AddOnsParams{.withImplot = true, .withMarkdown = true}
        );
    return 0;
}