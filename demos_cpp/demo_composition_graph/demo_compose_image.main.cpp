#include "functions_composition_graph/functions_composition_graph.h"
#include "functions_composition_graph/image_with_gui.h"
#include "imgui_bundle/imgui_bundle.h"

#include <opencv2/highgui.hpp>

int main(int, char**)
{
    using namespace VisualProg;

    cv::Mat image = cv::imread("resources/house.jpg");

    auto x = std::make_shared<ImageWithGui>(image);

    std::vector<FunctionWithGuiPtr> functions {
        std::make_shared<SplitChannelsWithGui>(),
        std::make_shared<AdjustChannelsWithGui>(),
        // std::make_shared<MergeChannelsWithGui>(),
    };

    FunctionsCompositionGraph compositionGraph(functions);
    compositionGraph.SetInput(x);

    auto gui = [&](){
        ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
        compositionGraph.Draw();
    };

    ImGuiBundle::AddOnsParams addOnsParams;
    addOnsParams.withNodeEditor = true;
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = gui;
    params.windowSize = {1200, 600};
    ImGuiBundle::Run(params, addOnsParams);

    return 0;
}