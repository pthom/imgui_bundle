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


void gui_demo_immvision_link()
{
    constexpr float kNarrowWidthEm = 40.f; // Under this width (in em), two images per row instead of four

    static bool inited = false;
    static std::vector<std::string> names = {"RGB", "Red", "Green", "Blue"};
    static std::vector<ImmVision::ImageBuffer> images;
    // One params per image, all with the same zoom key
    static std::vector<ImmVision::ImageParams> allParams(4);

    if (!inited)
    {
        ImmVision::ImageBuffer image = ImmVision::ImRead(DemosAssetsFolder() + "/images/tennis.jpg");
        images.push_back(image);
        for (const auto& channel : SplitChannels(image))
            images.push_back(channel);

        for (auto& params : allParams)
            params.ZoomKey = "tennis";

        inited = true;
    }

    RichMd::Render(
        "Images whose params share a `ZoomKey` pan and zoom together: drag one to pan, zoom with the mouse wheel.");

    // Four images in a row, or two on a narrow screen (a phone)
    bool narrow = ImGui::GetContentRegionAvail().x < kNarrowWidthEm * ImGui::GetFontSize();
    if (ImGui::BeginTable("images", narrow ? 2 : 4))
    {
        for (size_t i = 0; i < images.size(); ++i)
        {
            ImGui::TableNextColumn();
            // A negative width: the column's width, less one pixel (ImmVision then stores the size it used)
            allParams[i].ImageDisplaySize = {-1, 0};
            ImmVision::Image(names[i], images[i], &allParams[i]);
        }
        ImGui::EndTable();
    }
}
