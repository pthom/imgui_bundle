#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include "immapp/immapp.h"

#include <algorithm>
#include <cmath>

namespace
{

const double LARGEST_SCALE = 0.9 * 1.3;  // of the heart: the pulse scales it up to 0.9, the thickness knob up to 1.3

std::vector<double> VectorTimesK(const std::vector<double>& values, double k)
{
    std::vector<double> r(values.size(), 0.);
    for (size_t i = 0; i < values.size(); ++i)
        r[i] = k * values[i];
    return r;
}

}  // namespace

void gui_haiku_implot_heart() {
    // Fill x and y whose plot is a heart
    const double pi = 3.1415926535;
    static std::vector<double>  x, y;
    if (x.empty()) {
        for (double t = 0.; t < pi * 2.; t += 0.01) {
            x.push_back(pow(sin(t), 3.) * 16.);
            y.push_back(13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t));
        }
    }
    // Heart pulse rate and time tracking
    static double phase = 0., t0 = ImmApp::ClockSeconds() + 0.2;
    static float heart_pulse_rate = 80.;
    static float heart_thickness = 0.15;

    double t = ImmApp::ClockSeconds();
    phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.);
    double k = 0.8 + 0.1 * cos(phase);
    t0 = t;

    ImGui::Text("Bloat free code");

    ImPlot::BeginPlot("Heart", ImmApp::EmToVec2(21, 21));
    // Axes sized for the largest heart (fitted to the first frame's heart, a small one, they would clip the next ones)
    auto [xMin, xMax] = std::minmax_element(x.begin(), x.end());
    auto [yMin, yMax] = std::minmax_element(y.begin(), y.end());
    ImPlot::SetupAxesLimits(*xMin * LARGEST_SCALE, *xMax * LARGEST_SCALE, *yMin * LARGEST_SCALE, *yMax * LARGEST_SCALE);
    for (double k2 = 1 - (double)heart_thickness; k2 <= 1. + (double)heart_thickness; k2 += 0.01)
    {
        auto xk = VectorTimesK(x, k * k2), yk = VectorTimesK(y, k * k2);
        ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size());
    }
    ImPlot::EndPlot();
    HelloImGui::SetItemIsLive();  // the heart beats on its own: the app keeps its full speed while it is visible

    ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
    ImGui::SameLine();
    ImGuiKnobs::Knob("Line Thickness", &heart_thickness, 0.01, 0.3);
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int , char *[]) {
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui_haiku_implot_heart;
    runnerParams.windowTitle = "Hello!";
    runnerParams.windowSize = {380, 470};
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
#endif

#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include <cstdio>
void gui_haiku_implot_heart() { ImGui::Text("This demo requires ImPlot"); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int , char *[]) { printf("This demo requires ImPlot\n"); return 0; }
#endif
#endif