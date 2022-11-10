#include <imgui.h>
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include "imgui_bundle/imgui_bundle.h"

#include <cmath>

std::vector<double> VectorTimesK(const std::vector<double>& values, double k)
{
    std::vector<double> r(values.size(), 0.);
    for (size_t i = 0; i < values.size(); ++i)
        r[i] = k * values[i];
    return r;
}

int main(int , char *[])
{
    std::vector<double> interval, x, y;
    constexpr double pi =  3.1415926535;
    double phase = 0., t0 = ImGuiBundle::ClockSeconds() + 0.2;
    float heart_pulse_rate = 80.;
    for (double t = 0.; t < pi * 2.; t += 0.01)
    {
        interval.push_back(t);
        double x_ = pow(sin(t), 3.) * 16.; x.push_back(x_);
        double y_ = 13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t); y.push_back(y_);
    }

    auto gui = [&]()
    {
        // By setting fpsIdle = 0, we make sure that the animation is smooth
        HelloImGui::GetRunnerParams()->fpsIdle = 0.f;

        double t = ImGuiBundle::ClockSeconds();
        phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.); double k = 0.8 + 0.1 * cos(phase);
        t0 = t;

        ImGui::Text("Bloat free code");
        auto xk = VectorTimesK(x, k);
        auto yk = VectorTimesK(y, k);
        ImPlot::BeginPlot("Heart"); ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size()); ImPlot::EndPlot();

        ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
    };

    ImGuiBundle::Run(
        gui, "Hello!",
        /*windowSizeAuto=*/false , /*windowRestorePreviousGeometry==*/false, /*windowSize=*/{300, 450},
        /*fpsIdle=*/ 25.f, /*withImplot=*/true);
    return 0;
}
