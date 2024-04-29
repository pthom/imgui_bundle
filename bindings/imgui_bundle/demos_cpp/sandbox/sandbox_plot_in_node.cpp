#include "imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "implot/implot.h"
#include "immapp/runner.h"
#include "immapp/immapp_widgets.h"
#include <cmath>


namespace ed = ax::NodeEditor;


void gui()
{
    static ImVec2 plotSize(200, 200);
    static double xPos = 5.f;

    auto myPlotFunction = []()
    {
        static std::vector<float> x(1000), y(1000);
        for (int i = 0; i < 1000; ++i) {
            x[i] = i * 0.01f;
            y[i] = sin(x[i]);
        }
        ImPlot::PlotLine("My Line", x.data(), y.data(), 1000);
        ImPlot::DragLineX(0, &xPos, ImVec4(1, 1, 0, 1));
    };

    ed::Begin("My Node Editor");
    ed::BeginNode(ed::NodeId(1));
    ImGui::Text("Hello");
    ImGui::Text("World");
    plotSize = ImmApp::ShowResizablePlotInNodeEditor("My Plot", plotSize, myPlotFunction);
    ed::EndNode();
    ed::End();
}

int main(int, char**)
{
    HelloImGui::RunnerParams runner_params;
    runner_params.callbacks.ShowGui = gui;
    ImmApp::AddOnsParams addons_params;
    addons_params.withImplot = true;
    addons_params.withNodeEditor = true;
    ImmApp::Run(runner_params, addons_params);
}
