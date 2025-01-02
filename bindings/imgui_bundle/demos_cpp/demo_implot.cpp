// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include <vector>
#include <cmath>
#include "implot/implot.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"
#include "imgui_internal.h"

#ifdef IMGUI_BUNDLE_WITH_IMPLOT3D
#include "implot3d/implot3d.h"
#endif

// =======================
// Demos for ImPlot (2D)
// =======================

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


// =======================
// Demos for ImPlot3D
// =======================

#ifdef IMGUI_BUNDLE_WITH_IMPLOT3D
void Demo3D_LinePlots() {
    static float xs1[1001], ys1[1001], zs1[1001];
    for (int i = 0; i < 1001; i++) {
        xs1[i] = i * 0.001f;
        ys1[i] = 0.5f + 0.5f * cosf(50 * (xs1[i] + (float)ImGui::GetTime() / 10));
        zs1[i] = 0.5f + 0.5f * sinf(50 * (xs1[i] + (float)ImGui::GetTime() / 10));
    }
    static double xs2[20], ys2[20], zs2[20];
    for (int i = 0; i < 20; i++) {
        xs2[i] = i * 1 / 19.0f;
        ys2[i] = xs2[i] * xs2[i];
        zs2[i] = xs2[i] * ys2[i];
    }
    if (ImPlot3D::BeginPlot("Line Plots")) {
        ImPlot3D::SetupAxes("x", "y", "z");
        ImPlot3D::PlotLine("f(x)", xs1, ys1, zs1, 1001);
        ImPlot3D::SetNextMarkerStyle(ImPlot3DMarker_Circle);
        ImPlot3D::PlotLine("g(x)", xs2, ys2, zs2, 20, ImPlot3DLineFlags_Segments);
        ImPlot3D::EndPlot();
    }
}


void Demo3D_SurfacePlots() {
    constexpr int N = 20;
    static float xs[N * N], ys[N * N], zs[N * N];
    static float t = 0.0f;
    t += ImGui::GetIO().DeltaTime;

    // Define the range for X and Y
    constexpr float min_val = -1.0f;
    constexpr float max_val = 1.0f;
    constexpr float step = (max_val - min_val) / (N - 1);

    // Populate the xs, ys, and zs arrays
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int idx = i * N + j;
            xs[idx] = min_val + j * step;                                             // X values are constant along rows
            ys[idx] = min_val + i * step;                                             // Y values are constant along columns
            zs[idx] = ImSin(2 * t + ImSqrt((xs[idx] * xs[idx] + ys[idx] * ys[idx]))); // z = sin(2t + sqrt(x^2 + y^2))
        }
    }

    // Choose fill color
    ImGui::Text("Fill color");
    static int selected_fill = 1; // Colormap by default
    static ImVec4 solid_color = ImVec4(0.8f, 0.8f, 0.2f, 0.6f);
    const char* colormaps[] = {"Viridis", "Plasma", "Hot", "Cool", "Pink", "Jet",
                               "Twilight", "RdBu", "BrBG", "PiYG", "Spectral", "Greys"};
    static int sel_colormap = 5; // Jet by default
    {
        ImGui::Indent();

        // Choose solid color
        ImGui::RadioButton("Solid", &selected_fill, 0);
        if (selected_fill == 0) {
            ImGui::SameLine();
            ImGui::ColorEdit4("##SurfaceSolidColor", (float*)&solid_color);
        }

        // Choose colormap
        ImGui::RadioButton("Colormap", &selected_fill, 1);
        if (selected_fill == 1) {
            ImGui::SameLine();
            ImGui::Combo("##SurfaceColormap", &sel_colormap, colormaps, IM_ARRAYSIZE(colormaps));
        }
        ImGui::Unindent();
    }

    // Choose range
    static bool custom_range = false;
    static float range_min = -1.0f;
    static float range_max = 1.0f;
    ImGui::Checkbox("Custom range", &custom_range);
    {
        ImGui::Indent();

        if (!custom_range)
            ImGui::BeginDisabled();
        ImGui::SliderFloat("Range min", &range_min, -1.0f, range_max - 0.01f);
        ImGui::SliderFloat("Range max", &range_max, range_min + 0.01f, 1.0f);
        if (!custom_range)
            ImGui::EndDisabled();

        ImGui::Unindent();
    }

    // Begin the plot
    if (selected_fill == 1)
        ImPlot3D::PushColormap(colormaps[sel_colormap]);
    if (ImPlot3D::BeginPlot("Surface Plots", ImVec2(-1, 400), ImPlot3DFlags_NoClip)) {
        // Set styles
        ImPlot3D::SetupAxesLimits(-1, 1, -1, 1, -1.5, 1.5);
        ImPlot3D::PushStyleVar(ImPlot3DStyleVar_FillAlpha, 0.8f);
        if (selected_fill == 0)
            ImPlot3D::SetNextFillStyle(solid_color);
        ImPlot3D::SetNextLineStyle(ImPlot3D::GetColormapColor(1));

        // Plot the surface
        if (custom_range)
            ImPlot3D::PlotSurface("Wave Surface", xs, ys, zs, N, N, (double)range_min, (double)range_max);
        else
            ImPlot3D::PlotSurface("Wave Surface", xs, ys, zs, N, N);

        // End the plot
        ImPlot3D::PopStyleVar();
        ImPlot3D::EndPlot();
    }
    if (selected_fill == 1)
        ImPlot3D::PopColormap();
}
#endif // #ifdef IMGUI_BUNDLE_WITH_IMPLOT3D


// =======================
// Main demo function
// =======================
void demo_implot()
{
    ImGuiMd::RenderUnindented(R"(
        # ImPlot & ImPlot3D
        * [Implot](https://github.com/epezent/implot) provides immediate Mode Plotting for ImGui.
        * [Implot3D](https://github.com/brenocq/implot3d) provides immediate Mode 3D Plotting, with an API inspired from ImPlot.

        You can see lots of demos together with their code [online](https://traineq.org/implot_demo/src/implot_demo.html)
    )");
    if (ImGui::Button("View the full demo"))
    {
        BrowseToUrl("https://traineq.org/implot_demo/src/implot_demo.html");
    }
    ImGui::NewLine();
    if (ImGui::CollapsingHeader("ImPlot: Mixed plot##2"))
        DemoMixedPlot();
    if (ImGui::CollapsingHeader("ImPlot: Heatmap"))
        DemoHeatmap();

#ifdef IMGUI_BUNDLE_WITH_IMPLOT3D
    if (ImGui::CollapsingHeader("ImPlot3D: Line plots##2"))
        Demo3D_LinePlots();
    if (ImGui::CollapsingHeader("ImPlot3D: Surface Plots##2"))
        Demo3D_SurfacePlots();
#endif
}

#else // IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
void demo_implot() { ImGui::Text("Dear ImGui Bundle was compiled without support for ImPlot"); }
#endif
