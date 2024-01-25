// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include <vector>
#include <cmath>
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


double my_sinc(double x)
{
    constexpr double pi = 3.141592653589793238462643383279502884197;
    if (fabs(x) < 1E-10)
        return 1.;
    return sin(pi * x) / (pi * x);
}


struct MyHeatmapData
{
    static constexpr int N = 400;
    float values[N * N];
    // Note: this C++ demo does less than the python demo, because storing the labels under the form of a vector<const char *> is too tedious
    // std::vector<std::string> x_ticks;
    // std::vector<std::string> y_ticks;
    int n_ticks;

    MyHeatmapData()
    {
        auto& self = *this;

        float x[N];
        for (int i = 0; i < N; ++i)
            x[i] = -4 + (float)i * 0.02f;

        for (int i = 0; i < N; ++i)
        {
            for (int j = 0; j < N; ++j)
            {
                float xx = x[i] * x[j];
                float val = my_sinc(xx);
                self.values[i * N + j] = val;
            }
        }
        self.n_ticks = 5;
    }
};


// Note: this C++ demo does less than the python demo, because storing the labels under the form of a vector<const char *> is too tedious
static void DemoHeatmap()
{
    static MyHeatmapData data;

    const ImPlotAxisFlags axis_flags = ImPlotAxisFlags_Lock | ImPlotAxisFlags_NoGridLines | ImPlotAxisFlags_NoTickMarks;
    const auto cmap = ImPlotColormap_Viridis;
    ImPlot::PushColormap(cmap);
    ImGui::BeginGroup();
    const ImVec2 content_avail = ImGui::GetContentRegionAvail();
    const ImVec2 plot_size(content_avail.x - ImPlot::GetStyle().LegendPadding.x - 5.0f * ImGui::GetFontSize(),
                           content_avail.y);
    ImPlotFlags plot_flags = ImPlotFlags_NoLegend | ImPlotFlags_NoMouseText;
    if (ImPlot::BeginPlot("Sinc Function", plot_size, plot_flags))
    {
        ImPlot::SetupAxes(NULL, NULL, axis_flags, axis_flags);
        ImPlot::SetupAxisTicks(ImAxis_X1, 0.0, 1.0, data.n_ticks);
        ImPlot::SetupAxisTicks(ImAxis_Y1, 0.0, 1.0, data.n_ticks);

        ImPlot::PlotHeatmap("##heatmap", data.values, data.N, data.N, 0., 1., nullptr, ImPlotPoint(0, 1), ImPlotPoint(1, 0), 0);
        ImPlot::EndPlot();
    }
    ImGui::EndGroup();
    ImGui::SameLine();
    ImPlot::ColormapScale("##heatmap_scale", 0., 1., ImVec2(60,-1), "%g", 0, ImPlotColormap_Viridis);
    ImPlot::PopColormap();
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
    if (ImGui::CollapsingHeader("Mixed plot", ImGuiTreeNodeFlags_DefaultOpen))
        DemoMixedPlot();
    if (ImGui::CollapsingHeader("Heatmap"))
        DemoHeatmap();
}

#else // IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
void demo_implot() { ImGui::Text("Dear ImGui Bundle was compiled without support for ImPlot"); }
#endif
