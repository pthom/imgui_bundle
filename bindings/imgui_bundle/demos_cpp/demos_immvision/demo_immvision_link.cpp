#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"
#include <opencv2/imgcodecs.hpp>


void demo_immvision_link()
{
    static bool inited = false;
    static cv::Mat image;
    static std::vector<cv::Mat> channels;
    static ImmVision::ImageParams params_rgb, params_channels;

    if (!inited)
    {
        image = cv::imread(DemosAssetsFolder() + "/images/tennis.jpg");
        cv::split(image, channels);

        params_rgb.ImageDisplaySize = {300, 0};
        params_rgb.ZoomKey = "some_common_zoom_key";

        params_channels.ImageDisplaySize = {300, 0};
        params_channels.ZoomKey = "some_common_zoom_key";

        inited = true;
    }

    ImGuiMd::RenderUnindented(R"(If two images params share the same ZoomKey, then the images will pan in sync. Pan and zoom the image with the mouse and the mouse wheel)");
    ImmVision::Image("RGB", image, &params_rgb);
    for (size_t i = 0; i < channels.size(); ++i) {
        ImmVision::Image(std::string("channel") + std::to_string(i), channels[i], &params_channels);
        ImGui::SameLine();
    }
    ImGui::NewLine();
}
