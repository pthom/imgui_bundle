#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"


// Split a multi-channel image into a vector of single-channel images
static std::vector<ImmVision::ImageBuffer> SplitChannels(const ImmVision::ImageBuffer& img)
{
    std::vector<ImmVision::ImageBuffer> result;
    for (int c = 0; c < img.channels; c++)
    {
        ImmVision::ImageBuffer ch = ImmVision::ImageBuffer::Zeros(img.width, img.height, 1, img.depth);
        size_t es = img.elemSize();  // bytes per single-channel element
        for (int y = 0; y < img.height; y++)
        {
            const uint8_t* src = static_cast<const uint8_t*>(img.data) + y * img.step;
            uint8_t* dst = static_cast<uint8_t*>(ch.data) + y * ch.step;
            for (int x = 0; x < img.width; x++)
                std::memcpy(dst + x * es, src + (x * img.channels + c) * es, es);
        }
        result.push_back(ch);
    }
    return result;
}


void demo_immvision_link()
{
    static bool inited = false;
    static ImmVision::ImageBuffer image;
    static std::vector<ImmVision::ImageBuffer> channels;
    static ImmVision::ImageParams params_rgb, params_channels;

    if (!inited)
    {
        ImmVision::UseRgbColorOrder();
        image = ImmVision::ImRead(DemosAssetsFolder() + "/images/tennis.jpg");
        channels = SplitChannels(image);

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
