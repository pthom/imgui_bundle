#include "implot/implot.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"


void DemoMixedPlot()
{
    ImPlot::PushColormap(ImPlotColormap_Deep);
    float plot_height = ImmApp::EmSize() * 30;
    if (ImPlot::BeginPlot("Mixed plot", ImVec2(-1, plot_height)))
    {
        ImPlot::SetupAxes("x-axis", "y-axis");
        ImPlot::SetupAxesLimits(-0.5f, 9.5f, 0.f, 10.f);
        std::vector<float> lin = {8, 8, 9, 7, 8, 8, 8, 9, 7, 8};
        std::vector<float> bar = {1, 2, 5, 3, 4, 1, 2, 5, 3, 4};
        std::vector<float> dot = {7, 6, 6, 7, 8, 5, 6, 5, 8, 7};
        ImPlot::PlotBars("Bars", bar.data(), (int)bar.size(), 0.5f);
        ImPlot::PlotLine("Line", lin.data(), (int)lin.size());
        ImPlot::NextColormapColor(); // skip green
        ImPlot::PlotScatter("Scatter", dot.data(), (int)dot.size());
        ImPlot::EndPlot();
    }
}


void demo_implot()
{
    ImGuiMd::RenderUnindented(R"(
        # ImPlot
        [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        You can see lots of demos together with their code [online](https://traineq.org/implot_demo/src/implot_demo.html)
    )");
    if (ImGui::Button("View the full demo"))
    {
        BrowseToUrl("https://traineq.org/implot_demo/src/implot_demo.html");
    }
    ImGui::NewLine();
    if (ImGui::CollapsingHeader("Mixed plot", ImGuiTreeNodeFlags_DefaultOpen)) {
        DemoMixedPlot();
    }
}
