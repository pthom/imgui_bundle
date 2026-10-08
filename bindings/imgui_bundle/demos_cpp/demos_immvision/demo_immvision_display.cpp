#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

#include <algorithm>

namespace
{
    const float TENNIS_WIDTH_EM = 22.5f;  // the first image's width, at most: on a phone, the window's width
    const float SECOND_COLUMN_MIN_EM = 20.f;  // the second column goes beside the first if it fits there, else below
}

void gui_demo_immvision_display()
{
    static bool inited = false;
    static ImmVision::ImageBuffer bear, tennis;
    static ImmVision::ImageParams params;
    static ImVec2 imageDisplaySize;

    if (!inited)
    {
        float width = std::min(HelloImGui::EmSize(TENNIS_WIDTH_EM), ImGui::GetContentRegionAvail().x);
        imageDisplaySize = ImVec2(width, 0.f);  // the height follows the image's aspect ratio
        std::string assetsDir = DemosAssetsFolder() + "/images/";
        bear = ImmVision::ImRead(assetsDir + "bear_transparent.png");
        tennis = ImmVision::ImRead(assetsDir + "tennis.jpg");

        int bearDisplaySize = int(HelloImGui::EmSize(15.f));
        params.ImageDisplaySize = ImmVision::Size(bearDisplaySize, bearDisplaySize);

        inited = true;
    }

    ImGui::BeginGroup();
    RichMd::Render("# ImmVision::ImageDisplay()");
    RichMd::Render("Displays an image (possibly resizable)");
    ImmVision::ImageDisplayResizable("Tennis", tennis, &imageDisplaySize);
    ImGui::EndGroup();

    if (ImGui::GetContentRegionAvail().x - ImGui::GetItemRectSize().x >= HelloImGui::EmSize(SECOND_COLUMN_MIN_EM))
        ImGui::SameLine();

    ImGui::BeginGroup();
    RichMd::Render("# ImmVision::Image()");
    RichMd::Render("Displays an image, while providing lots of visualization options.");
    ImmVision::Image("Bear", bear, &params);
    RichMd::Render(R"(
        * Zoom in/out using the mouse wheel.
        * Pixel values are displayed at high zoom levels.
        * Pan the image by dragging it with the left mouse button
        * Open settings via button (bottom right corner of the image)
    )");
    ImGui::EndGroup();
}
