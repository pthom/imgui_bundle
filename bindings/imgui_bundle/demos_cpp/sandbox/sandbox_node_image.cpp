#ifdef IMGUI_BUNDLE_WITH_IMMVISION
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "immvision/immvision.h"
#include <opencv2/opencv.hpp>

namespace ed = ax::NodeEditor;


void Gui()
{
    static cv::Mat red, blue, white;
    if (red.empty())
    {
        //red = cv::Mat(300, 300, CV_8UC3, cv::Scalar(0, 0, 255));
        red = cv::imread("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/imgui_bundle/bindings/imgui_bundle/assets/images/world.png");
        blue = cv::Mat(300, 300, CV_8UC3, cv::Scalar(255, 0, 0));
        white = cv::Mat(300, 300, CV_8UC3, cv::Scalar(255, 255, 255));
    }

    static ImmVision::ImageParams redParams;

    ImGui::Text("Hello, world!");

    ed::Begin("My Node Editor");

    ed::BeginNode(ed::NodeId(1));
    ImGui::Text("Hello");
    ImGui::Text("A");
    ImGui::Text("B");
    ImGui::Text("C");
    ImmVision::Image("Red", red, &redParams);
    ed::EndNode();

    ed::BeginNode(ed::NodeId(2));
    ImGui::Text("Hello");
    ImGui::Text("A");
    ImGui::Text("B");
    ImGui::Text("C");
    ImmVision::ImageDisplayResizable("Blue", blue);
    ed::EndNode();

    ed::BeginNode(ed::NodeId(3));
    ImGui::Text("Hello");
    ImGui::Text("A");
    ImGui::Text("B");
    ImGui::Text("C");
    ImmVision::ImageDisplayResizable("White", white);
    ed::EndNode();

    ed::End();
}

int main()
{
    ImmApp::AddOnsParams addonsParams;
    addonsParams.withNodeEditor = true;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;

    ImmApp::Run(runnerParams, addonsParams);

    return 0;
}
#else
int main() { return 0; }
#endif
