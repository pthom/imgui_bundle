#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include "immapp/immapp.h"

#include <cmath>

std::vector<double> VectorTimesK(const std::vector<double>& values, double k)
{
    std::vector<double> r(values.size(), 0.);
    for (size_t i = 0; i < values.size(); ++i)
        r[i] = k * values[i];
    return r;
}

int main(int , char *[]) {
    // Fill x and y whose plot is a heart
    double pi = 3.1415926535;
    std::vector<double>  x, y; {
        for (double t = 0.; t < pi * 2.; t += 0.01) {
            x.push_back(pow(sin(t), 3.) * 16.);
            y.push_back(13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t));
        }
    }
    // Heart pulse rate and time tracking
    double phase = 0., t0 = ImmApp::ClockSeconds() + 0.2;
    float heart_pulse_rate = 80.;

    auto gui = [&]() {
        // Make sure that the animation is smooth
        HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = false;

        double t = ImmApp::ClockSeconds();
        phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.);
        double k = 0.8 + 0.1 * cos(phase);
        t0 = t;

        ImGui::Text("Bloat free code");
        auto xk = VectorTimesK(x, k), yk = VectorTimesK(y, k);
        ImPlot::BeginPlot("Heart", ImmApp::EmToVec2(21, 21));
        ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size());
        ImPlot::EndPlot();

        ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
    };

    ImmApp::Run(
        gui, "Hello!",
        /*windowSizeAuto=*/false , /*windowRestorePreviousGeometry==*/false, /*windowSize=*/{300, 450},
        /*fpsIdle=*/ 25.f, /*withImplot=*/true);
    return 0;
}

#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include <cstdio>
int main(int , char *[]) { printf("This demo requires ImPlot\n"); return 0; }
#endif