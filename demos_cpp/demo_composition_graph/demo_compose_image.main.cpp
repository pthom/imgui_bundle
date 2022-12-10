#include "immapp/visual_prog/computer_vision/image_with_gui.h"
#include "immapp/visual_prog/computer_vision/lut.h"
#include "immapp/immapp.h"

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>


int main(int, char**)
{
    using namespace VisualProg;

    cv::Mat image = cv::imread("assets/images/house.jpg");
    cv::resize(image, image, cv::Size(), 0.5, 0.5);

    auto split_lut_merge_gui = Split_Lut_Merge_WithGui(ColorType::BGR);

//    std::vector<FunctionWithGuiPtr> functions {
//        std::make_shared<SplitChannelsWithGui>(),
//        std::make_shared<LutChannelsWithGui>(),
//        std::make_shared<MergeChannelsWithGui>(),
//    };

    std::vector<FunctionWithGuiPtr> functions {
        split_lut_merge_gui._split, split_lut_merge_gui._lut, split_lut_merge_gui._merge};

    FunctionsCompositionGraph compositionGraph(functions);
    compositionGraph.SetInput(image);

    auto gui = [&](){
        compositionGraph.Draw();
    };

    ImmApp::AddOnsParams addOnsParams;
    ax::NodeEditor::Config nodeEditorConfig;
    nodeEditorConfig.SettingsFile = "demo_compose_image.json";

    addOnsParams.withNodeEditorConfig = nodeEditorConfig;
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = gui;
    params.windowSize = {1600, 1000};
    ImmApp::Run(params, addOnsParams);

    return 0;
}