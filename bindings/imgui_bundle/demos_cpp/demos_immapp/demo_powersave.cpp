// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Power save: when nothing happens, Hello ImGui lowers the frame rate to spare the CPU. What changes on its own (a live
// plot, a spinner) then moves by jumps, unless it says that it is live: HelloImGui::SetItemIsLive().
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "imgui.h"
#include "implot/implot.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui_toggle/imgui_toggle_presets.h"
#include "imspinner/imspinner.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <vector>

namespace
{
    const double SIGNAL_SECONDS = 4.;     // the plot shows the last seconds of the signal
    const double SIGNAL_FREQUENCY = 0.6;  // Hz, of the signal's main wave
    const ImVec4 IDLING_COLOR(0.85f, 0.45f, 0.1f, 1.f);      // the status's pill while the app idles
    const ImVec4 FULL_SPEED_COLOR(0.2f, 0.55f, 0.3f, 1.f);   // and at full speed

    // A signal of varying data, sampled once per frame: the gaps between the samples are the frame durations
    std::vector<double> gTimes, gValues;
    bool gLive = false;  // the plot and the spinner say that they are live (HelloImGui::SetItemIsLive)

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

    // An animated on/off switch (imgui_toggle), in the colors of the theme
    bool Switch(const char* label, bool* v)
    {
        ImGuiToggleConfig config = ImGuiTogglePresets::DefaultStyle();
        config.Flags |= ImGuiToggleFlags_Animated;
        config.Size = HelloImGui::EmToVec2(2.2f, 1.2f);
        return ImGui::Toggle(label, v, config);
    }

    // A word on a colored pill
    void Pill(const char* label, ImVec4 color)
    {
        ImVec2 padding(ImGui::GetFontSize() * 0.5f, 0.f);
        ImVec2 size = ImGui::CalcTextSize(label) + padding * 2.f;
        ImVec2 pos = ImGui::GetCursorScreenPos();
        ImDrawList* drawList = ImGui::GetWindowDrawList();
        drawList->AddRectFilled(pos, pos + size, ImGui::GetColorU32(color), size.y * 0.5f);
        drawList->AddText(pos + padding, IM_COL32_WHITE, label);
        ImGui::Dummy(size);
    }

    // The frames of the last second, whether the app idles, and the shortest and longest gaps between frames
    void ShowStatus()
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
        bool idling = HelloImGui::GetRunnerParams()->fpsIdling.isIdling;
        ImGui::Text("%d FPS", nbFrames);
        ImGui::SameLine();
        Pill(idling ? "idling" : "full speed", idling ? IDLING_COLOR : FULL_SPEED_COLOR);
        ImGui::SameLine();
        ImGui::TextDisabled("frames %.0f to %.0f ms apart", shortest, longest);
    }

    // The plot, and the spinner at its right
    void ShowLiveContent()
    {
        float spinnerRadius = ImGui::GetFontSize() * 2.f;
        float plotWidth = ImGui::GetContentRegionAvail().x - spinnerRadius * 2.f - HelloImGui::EmSize(1.5f);
        std::vector<double> ages(gTimes.size());  // the x axis: seconds before now
        for (size_t i = 0; i < gTimes.size(); ++i)
            ages[i] = gTimes[i] - gTimes.back();
        if (ImPlot::BeginPlot("A live signal", ImVec2(plotWidth, HelloImGui::EmSize(10.f))))
        {
            ImPlot::SetupAxesLimits(-SIGNAL_SECONDS, 0., -1.5, 1.5, ImPlotCond_Always);
            ImPlot::PlotLine("signal", ages.data(), gValues.data(), (int)ages.size());
            ImPlot::EndPlot();
        }
        HelloImGui::SetItemIsLive(gLive);  // the plot changes on its own: the app does not idle while it is visible

        ImGui::SameLine();
        ImGui::SetCursorPosY(ImGui::GetCursorPosY() + HelloImGui::EmSize(3.f));
        auto color = ImColor(0.3f, 0.5f, 0.9f, 1.f);
        ImSpinner::SpinnerAngTriple("spinner", spinnerRadius * 0.5f, spinnerRadius * 0.75f, spinnerRadius, 2.5f,
                                    color, color, color);
        HelloImGui::SetItemIsLive(gLive);
    }
}  // namespace

void gui_demo_powersave()
{
    SampleSignal();
    ShowStatus();
    ImGui::Spacing();
    RichMd::Render(R"(
        Hello ImGui tries hard to save the CPU (and the battery) by lowering the frame rate when it is not needed.
        After 3 seconds without user interaction, animations may become choppy: watch the plot and the spinner,
        without moving the mouse or touching the screen.
    )");
    Switch("The plot and the spinner are live", &gLive);
    ImGui::Spacing();
    ShowLiveContent();

    ImGui::Dummy(HelloImGui::EmToVec2(0.f, 0.5f));
    if (ImGui::CollapsingHeader("Keep the full speed while content changes", ImGuiTreeNodeFlags_DefaultOpen))
    {
        RichMd::Render(R"(
            Call `SetItemIsLive()` right after a widget that changes on its own (an animation, a live image, a plot
            of varying data): the app keeps its full speed while the widget is visible.

            ```cpp
            ImPlot::EndPlot();
            HelloImGui::SetItemIsLive();
            ```

            ```python
            implot.end_plot()
            hello_imgui.set_item_is_live()
            ```

            Data that arrives in another thread (a camera, a socket): call `HelloImGui::RequestRefresh()` in C++,
            `hello_imgui.request_refresh()` in Python, when it arrives.
        )");
    }

    ImGui::Dummy(HelloImGui::EmToVec2(0.f, 0.5f));
    if (ImGui::CollapsingHeader("Idling settings"))
    {
        auto& fpsIdling = HelloImGui::GetRunnerParams()->fpsIdling;
        RichMd::Render(R"(
            These settings are global: they act on the whole application. To keep some content moving, prefer
            `SetItemIsLive()` on its widget: the app idles again as soon as the widget leaves the view, or stops
            changing.

            They are in the runner params; while the app runs, `HelloImGui::GetRunnerParams()` gives them
            (`hello_imgui.get_runner_params()` in Python).

            ```cpp
            // Idle frame rate (0: full speed)
            runnerParams.fpsIdling.fpsIdle = 3.f;
            // No idling at all
            runnerParams.fpsIdling.enableIdling = false;
            ```

            ```python
            # Idle frame rate (0: full speed)
            runner_params.fps_idling.fps_idle = 3
            # No idling at all
            runner_params.fps_idling.enable_idling = False
            ```
        )");
        ImGui::SetNextItemWidth(-FLT_MIN);  // the whole width: a slider is easier to drag with a finger
        ImGui::SliderFloat("##fpsIdle", &fpsIdling.fpsIdle, 0.f, 60.f, "fpsIdle: %.0f");
        Switch("Enable idling", &fpsIdling.enableIdling);
    }
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char **)
{
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui_demo_powersave;
    runnerParams.windowTitle = "Power save";
    runnerParams.windowSize = {520, 720};
    runnerParams.fpsIdle = 3.f;
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    addOnsParams.withMarkdown = true;
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
