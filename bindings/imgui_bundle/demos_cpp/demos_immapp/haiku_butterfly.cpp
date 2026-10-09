// Lorenz Attractor & Butterfly Effect
// This example demonstrates the Lorenz Attractor and the butterfly effect,
// showing how tiny changes in initial conditions lead to diverging trajectories.

#include "imgui.h"
#include "implot3d/implot3d.h"
#include "immapp/runner.h"
#include "imgui_rich_md/rich_md.h"
#include <algorithm>
#include <vector>

namespace
{

// An (i) at the right of the last widget: a click, or a tap, shows the text (a tooltip would need a mouse)
void InfoButton(const char* text)
{
    ImGui::SameLine();
    ImGui::PushID(text);
    if (ImGui::SmallButton("(i)"))
        ImGui::OpenPopup("info");
    if (ImGui::BeginPopup("info"))
    {
        ImGui::TextUnformatted(text);
        ImGui::EndPopup();
    }
    ImGui::PopID();
}

struct LorenzParams {
    float sigma = 10.0f;
    float rho = 28.0f;
    float beta = 8.0f / 3.0f;
    float dt = 0.01f;
    int max_size = 2000;
} PARAMS;


class AnimatedLorenzTrajectory {
public:
    AnimatedLorenzTrajectory(float x, float y, float z) : xs({x}), ys({y}), zs({z}) {}

    void step() {
        float x = xs.back(), y = ys.back(), z = zs.back();
        float dx = PARAMS.sigma * (y - x);
        float dy = x * (PARAMS.rho - z) - y;
        float dz = x * y - PARAMS.beta * z;
        x += dx * PARAMS.dt;
        y += dy * PARAMS.dt;
        z += dz * PARAMS.dt;

        xs.push_back(x);
        ys.push_back(y);
        zs.push_back(z);

        if (xs.size() > static_cast<size_t>(PARAMS.max_size)) {
            xs.erase(xs.begin());
            ys.erase(ys.begin());
            zs.erase(zs.begin());
        }
    }
    std::vector<float> xs, ys, zs;
};

class CompareLorenzTrajectories
{
public:
    float initial_delta = 0.1f;

    CompareLorenzTrajectories() { init_trajectories(); }

    void init_trajectories() {
        traj1 = std::make_unique<AnimatedLorenzTrajectory>(0.0f, 1.0f, 1.05f);
        traj2 = std::make_unique<AnimatedLorenzTrajectory>(0.0f + initial_delta, 1.0f, 1.05f);
    }

    void gui_params() {
        ImGui::SliderFloat("Sigma", &PARAMS.sigma, 0.0f, 100.0f);
        InfoButton("Controls the rate of divergence between nearby points (chaos level).");

        ImGui::SliderFloat("Rho", &PARAMS.rho, 0.0f, 100.0f);
        InfoButton("Determines the size and shape of the attractor.");

        ImGui::SliderFloat("Beta", &PARAMS.beta, 0.0f, 10.0f);
        InfoButton("A damping parameter affecting vertical movement.");

        ImGui::SliderFloat("dt", &PARAMS.dt, 0.0f, 0.05f);
        InfoButton("Time step size for numerical integration (smaller is smoother).");

        ImGui::SliderFloat("Initial Delta", &initial_delta, 0.0f, 0.2f);
        InfoButton("Initial difference between trajectories to demonstrate divergence.");

        if (ImGui::Button("Reset")) {
            init_trajectories();
        }
    }

    void gui_plot() {
        // A square, as wide as a phone at most
        float side = std::min(HelloImGui::EmSize(40.f), ImGui::GetContentRegionAvail().x);
        if (ImPlot3D::BeginPlot("Lorenz Attractor", ImVec2(side, side))) {
            ImPlot3D::SetupAxes("X", "Y", "Z",
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit);
            ImPlot3D::PlotLine(
                "Trajectory", traj1->xs.data(), traj1->ys.data(), traj1->zs.data(), traj1->xs.size());
            ImPlot3D::PlotLine("Trajectory2", traj2->xs.data(), traj2->ys.data(), traj2->zs.data(), traj2->xs.size());
            ImPlot3D::EndPlot();
            HelloImGui::SetItemIsLive();  // the trajectories move on their own: no idling while they are visible
        }
        bool touch = ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_IsTouchScreen;
        ImGui::TextDisabled(touch ? "Drag with two fingers to rotate." : "Drag with the right button to rotate.");
        traj1->step();
        traj2->step();
    }

    void gui() {
        RichMd::FoldingTextOptions about;
        about.startFolded = true;  // its first paragraph; "More..." shows the rest
        RichMd::RenderFolding("about", R"(
# Lorenz attractor and the butterfly effect
Two trajectories of the [Lorenz system](https://en.wikipedia.org/wiki/Lorenz_system) start almost at the same point,
then drift apart: chaos in action. Drawn in 3D with [ImPlot3D](https://github.com/brenocq/implot3d). Sliders change
the system's parameters and the gap between the two starting points; Reset starts them over.

The term **butterfly effect** in popular media may stem from the real-world implications of the Lorenz attractor,
namely that tiny changes in initial conditions evolve to completely different trajectories.)", about);
        ImGui::SeparatorText("Parameters");
        gui_params();
        ImGui::SeparatorText("Plot");
        gui_plot();
    }

private:
    std::unique_ptr<AnimatedLorenzTrajectory> traj1, traj2;
};

}  // namespace

void gui_haiku_butterfly() {
    static CompareLorenzTrajectories lorenz_comparer;
    lorenz_comparer.gui();
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main() {
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot3d = true;
    addOnsParams.withMarkdown = true;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.appWindowParams.windowGeometry.sizeAuto = true;
    runnerParams.appWindowParams.windowTitle = "Butterfly Effect";
    runnerParams.callbacks.ShowGui = gui_haiku_butterfly;

    ImmApp::Run(runnerParams, addOnsParams);

    return 0;
}
#endif
