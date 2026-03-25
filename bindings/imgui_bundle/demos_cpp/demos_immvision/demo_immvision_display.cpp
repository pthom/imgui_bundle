#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

void demo_immvision_display()
{
    static bool inited = false;
    static ImmVision::ImageBuffer bear, tennis;
    static ImmVision::ImageParams params;

    static ImVec2 imageDisplaySize(0.f, ImmApp::EmSize(20.f));

    if (!inited)
    {
        ImmVision::UseRgbColorOrder();
        std::string assetsDir = DemosAssetsFolder() + "/images/";
        bear = ImmVision::ImRead(assetsDir + "bear_transparent.png");
        tennis = ImmVision::ImRead(assetsDir + "tennis.jpg");

        int bearDisplaySize = int(HelloImGui::EmSize(15.f));
        params.ImageDisplaySize = ImmVision::Size(bearDisplaySize, bearDisplaySize);

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
