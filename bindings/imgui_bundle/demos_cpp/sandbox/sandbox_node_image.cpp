#if defined(IMGUI_BUNDLE_WITH_IMMVISION) && defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "immvision/immvision.h"

namespace ed = ax::NodeEditor;


void Gui()
{
    static ImmVision::ImageBuffer red, blue, white;
    if (red.empty())
    {
        //red = ImmVision::ImageBuffer::Zeros(300, 300, 3, ImmVision::ImageDepth::uint8);
        red = ImmVision::ImRead("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/imgui_bundle/bindings/imgui_bundle/assets/images/world.png");
        blue = ImmVision::ImageBuffer::Zeros(300, 300, 3, ImmVision::ImageDepth::uint8);
        blue.fill(ImmVision::Color4d(0, 0, 255, 255));
        white = ImmVision::ImageBuffer::Zeros(300, 300, 3, ImmVision::ImageDepth::uint8);
        white.fill(ImmVision::Color4d(255, 255, 255, 255));
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
