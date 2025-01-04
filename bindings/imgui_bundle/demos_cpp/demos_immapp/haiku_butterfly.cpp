// Lorenz Attractor & Butterfly Effect
// This example demonstrates the Lorenz Attractor and the butterfly effect,
// showing how tiny changes in initial conditions lead to diverging trajectories.

#include "imgui.h"
#include "implot3d/implot3d.h"
#include "immapp/runner.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include <vector>

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
        ImGui::SetItemTooltip("Controls the rate of divergence between nearby points (chaos level).");

        ImGui::SliderFloat("Rho", &PARAMS.rho, 0.0f, 100.0f);
        ImGui::SetItemTooltip("Determines the size and shape of the attractor.");

        ImGui::SliderFloat("Beta", &PARAMS.beta, 0.0f, 10.0f);
        ImGui::SetItemTooltip("A damping parameter affecting vertical movement.");

        ImGui::SliderFloat("dt", &PARAMS.dt, 0.0f, 0.05f);
        ImGui::SetItemTooltip("Time step size for numerical integration (smaller is smoother).");

        ImGui::SliderFloat("Initial Delta", &initial_delta, 0.0f, 0.2f);
        ImGui::SetItemTooltip("Initial difference between trajectories to demonstrate divergence.");

        if (ImGui::Button("Reset")) {
            init_trajectories();
        }
    }

    void gui_plot() {
        if (ImPlot3D::BeginPlot("Lorenz Attractor", HelloImGui::EmToVec2(40, 40))) {
            ImPlot3D::SetupAxes("X", "Y", "Z",
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit);
            ImPlot3D::PlotLine(
                "Trajectory", traj1->xs.data(), traj1->ys.data(), traj1->zs.data(), traj1->xs.size());
            ImPlot3D::PlotLine("Trajectory2", traj2->xs.data(), traj2->ys.data(), traj2->zs.data(), traj2->xs.size());
            ImPlot3D::EndPlot();
        }
        traj1->step();
        traj2->step();
    }

    void gui() {
        ImGuiMd::RenderUnindented(R"(
# Lorenz Attractor & Butterfly Effect
This is a simple example of the Lorenz Attractor. It shows two trajectories that diverge
because of a small initial difference, illustrating chaos theory in action.

The term **butterfly effect** in popular media may stem from the real-world implications
of the Lorenz attractor, namely that tiny changes in initial conditions evolve to
completely different trajectories.)");
        ImGui::SeparatorText("Parameters");
        gui_params();
        ImGui::SeparatorText("Plot");
        gui_plot();
    }

private:
    std::unique_ptr<AnimatedLorenzTrajectory> traj1, traj2;
};

int main() {
    CompareLorenzTrajectories lorenz_comparer;
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot3d = true;
    addOnsParams.withMarkdown = true;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.fpsIdling.enableIdling = false;
    runnerParams.appWindowParams.windowGeometry.sizeAuto = true;
    runnerParams.appWindowParams.windowTitle = "Butterfly Effect";
    runnerParams.callbacks.ShowGui = [&]() { lorenz_comparer.gui(); };

    ImmApp::Run(runnerParams, addOnsParams);

    return 0;
}
