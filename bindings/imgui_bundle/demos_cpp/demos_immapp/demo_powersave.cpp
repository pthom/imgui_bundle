// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Power save: when nothing happens, Hello ImGui lowers the frame rate to spare the CPU. What changes on its own (a live
// plot, a spinner) then moves by jumps.
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "immapp/immapp.h"
#include "imgui.h"
#include "implot/implot.h"
#include "hello_imgui/hello_imgui.h"
#include "imspinner/imspinner.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <vector>

namespace
{
    const double SIGNAL_SECONDS = 4.;     // the plot shows the last seconds of the signal
    const double SIGNAL_FREQUENCY = 0.6;  // Hz, of the signal's main wave

    // A signal of varying data, sampled once per frame: the gaps between the samples are the frame durations
    std::vector<double> gTimes, gValues;

    void SampleSignal()
    {
        double now = ImmApp::ClockSeconds();
        double phase = 2. * IM_PI * SIGNAL_FREQUENCY * now;
        double y = std::sin(phase) + 0.3 * std::sin(3.7 * phase);  // a main wave, and a faster one
        gTimes.push_back(now);
        gValues.push_back(y);
        size_t nbOld = 0;  // the samples out of the plot, but one (the line enters from its left edge)
        while (nbOld + 1 < gTimes.size() && gTimes[nbOld + 1] < now - SIGNAL_SECONDS)
            ++nbOld;
        gTimes.erase(gTimes.begin(), gTimes.begin() + (std::ptrdiff_t)nbOld);
        gValues.erase(gValues.begin(), gValues.begin() + (std::ptrdiff_t)nbOld);
    }

    // The pace of the last second: the number of frames, and their shortest and longest gaps (ms)
    void ShowPace()
    {
        double now = gTimes.back();
        int nbFrames = 0;
        double shortest = 1e9, longest = 0.;
        for (size_t i = 1; i < gTimes.size(); ++i)
        {
            if (gTimes[i] < now - 1.)
                continue;
            double gap = (gTimes[i] - gTimes[i - 1]) * 1000.;
            shortest = std::min(shortest, gap);
            longest = std::max(longest, gap);
            ++nbFrames;
        }
        ImGui::Text("Last second: %d frames, %.0f to %.0f ms apart", nbFrames, shortest, longest);
    }

    void ShowSignal()
    {
        std::vector<double> ages(gTimes.size());  // the x axis: seconds before now
        for (size_t i = 0; i < gTimes.size(); ++i)
            ages[i] = gTimes[i] - gTimes.back();
        if (ImPlot::BeginPlot("A live signal", ImVec2(-1.f, HelloImGui::EmSize(12.f))))
        {
            ImPlot::SetupAxesLimits(-SIGNAL_SECONDS, 0., -1.5, 1.5, ImPlotCond_Always);
            ImPlot::PlotLine("signal", ages.data(), gValues.data(), (int)ages.size());
            ImPlot::EndPlot();
        }
    }
}  // namespace

void gui_demo_powersave()
{
    SampleSignal();
    auto& fpsIdling = HelloImGui::GetRunnerParams()->fpsIdling;

    ImGui::Text("FPS: %.1f%s", HelloImGui::FrameRate(), fpsIdling.isIdling ? "  (idling)" : "");
    ShowPace();
    ImGui::TextWrapped(
        "In order to reduce the CPU usage, the FPS is reduced automatically when no user interaction is detected. "
        "As a consequence, the plot and the spinner below may move by jumps. Move the mouse or touch the screen, "
        "and they are smooth again.");

    ShowSignal();
    auto color = ImColor(0.3f, 0.5f, 0.9f, 1.f);
    float radius1 = ImGui::GetFontSize();
    ImSpinner::SpinnerAngTriple("spinner_arc_fade", radius1, radius1 * 1.5f, radius1 * 2.f, 2.5f, color, color, color);

    ImGui::TextWrapped("You can adjust HelloImGui::GetRunnerParams()->fpsIdling.fpsIdle if you need smoother "
                       "animations when the app is idle. A value of 0 means that the refresh will be as fast as "
                       "possible.");
    ImGui::TextUnformatted("fpsIdling.fpsIdle");  // the label above the slider: the slider gets the whole width
    ImGui::SetNextItemWidth(-FLT_MIN);
    ImGui::SliderFloat("##fpsIdle", &fpsIdling.fpsIdle, 0.f, 60.f, "%.0f");

    ImGui::TextWrapped("You can also set HelloImGui::GetRunnerParams()->fpsIdling.enableIdling.");
    ImGui::Checkbox("Enable Idling", &fpsIdling.enableIdling);
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char **)
{
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui_demo_powersave;
    runnerParams.windowTitle = "Power save";
    runnerParams.windowSize = {500, 600};
    runnerParams.fpsIdle = 3.f;
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    ImmApp::Run(runnerParams, addOnsParams);
    return 0;
}
#endif

#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include <cstdio>
void gui_demo_powersave() { ImGui::Text("This demo requires ImPlot."); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**) { std::printf("This demo requires ImPlot.\n"); }
#endif
#endif
