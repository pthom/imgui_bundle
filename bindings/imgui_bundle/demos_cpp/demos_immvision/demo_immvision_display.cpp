#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"
#include "hello_imgui/hello_imgui.h"
#include <opencv2/imgcodecs.hpp>
#include "imgui.h"

void demo_immvision_display()
{
    static bool inited = false;
    static cv::Mat bear, tennis;
    static ImmVision::ImageParams params;

    static ImVec2 imageDisplaySize(0.f, ImmApp::EmSize(20.f));

    if (!inited)
    {
        ImmVision::UseBgrColorOrder();
        std::string assetsDir = DemosAssetsFolder() + "/images/";
        bear = cv::imread(assetsDir + "bear_transparent.png", cv::IMREAD_UNCHANGED);
        tennis = cv::imread(assetsDir + "tennis.jpg");

        int bearDisplaySize = int(HelloImGui::EmSize(15.f));
        params.ImageDisplaySize = cv::Size(bearDisplaySize, bearDisplaySize);

        inited = true;
    }

    ImGui::BeginGroup();
    ImGuiMd::RenderUnindented("# ImmVision::ImageDisplay()");
    ImGuiMd::RenderUnindented("Displays an image (possibly resizable)");
    ImmVision::ImageDisplayResizable("Tennis", tennis, &imageDisplaySize);
    ImGui::EndGroup();

    ImGui::SameLine();

    ImGui::BeginGroup();
    ImGuiMd::RenderUnindented("# ImmVision::Image()");
    ImGuiMd::RenderUnindented("Displays an image, while providing lots of visualization options.");
    ImmVision::Image("Bear", bear, &params);
    ImGuiMd::RenderUnindented(R"(
        * Zoom in/out using the mouse wheel.
        * Pixel values are displayed at high zoom levels.
        * Pan the image by dragging it with the left mouse button
        * Open settings via button (bottom right corner of the image)
    )");
    ImGui::EndGroup();
}
