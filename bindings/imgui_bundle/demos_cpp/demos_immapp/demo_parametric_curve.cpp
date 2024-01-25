#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "immapp/immapp.h"
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include <cmath>
#include <vector>
#include <utility>


// Just a parametric curve to demonstrate how to edit its parameters a, b, & c
class Curve
{
public:
    float a = 2.0f;
    float b = 60.0f;
    float c = 2.0f;

    // Return x and y arrays that we will draw
    std::pair<std::vector<float>, std::vector<float>> getXY()
    {
        float t = 0.0f;
        std::vector<float> x, y;
        while (t < 6.28f)
        {
            x.push_back(2 * std::cos(t) + std::sin(a * t) * std::cos(b * t));
            y.push_back(std::sin(c * t) + std::sin(60 * t));
            t += 0.001f;
        }
        return std::make_pair(x, y);
    }
};

Curve curve;


// Our gui function, which will be invoked by the application loop
void gui()
{
    auto [x, y] = curve.getXY();

    // Draw the x/y curve
    ImPlot::BeginPlot("Play with me");
    ImPlot::PlotLine("curve", x.data(), y.data(), x.size());
    ImPlot::EndPlot();

    // Edit the curve parameters: no callback is needed
    ImGuiKnobs::Knob("a", &curve.a, 0.5f, 5.0f);
    ImGui::SameLine();
    ImGuiKnobs::Knob("b", &curve.b, 55.0f, 65.0f);
    ImGui::SameLine();
    ImGuiKnobs::Knob("c", &curve.c, 0.5f, 5.0f);

    //                               // As an illustration of the Immediate Gui paradigm,
    if (ImGui::Button("Random"))     // this draws a button
    {                                // and you handle its action immediately!
        curve.a = (float)rand() / (float)RAND_MAX * (5.0f - 0.5f) + 0.5f;
        curve.b = (float)rand() / (float)RAND_MAX * (65.0f - 55.0f) + 55.0f;
        curve.c = (float)rand() / (float)RAND_MAX * (5.0f - 0.5f) + 0.5f;
    }
}


int main()
{
    // Just set you application params (gui function, etc)
    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = gui;
    // Select your addons
    ImmApp::AddOnsParams addOns;
    addOns.withImplot = true;
    // And run
    ImmApp::Run(params, addOns);
    return 0;
}
#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include <cstdio>
int main(int , char *[]) { printf("This demo requires ImPlot\n"); return 0; }
#endif
