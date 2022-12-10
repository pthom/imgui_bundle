#include "split_merge.h"

#include <opencv2/imgproc.hpp>

namespace VisualProg
{

    std::vector<cv::Mat> SplitChannels(const Image& image)
    {
        assert(image.channels() > 1);
        std::vector<cv::Mat> r;
        cv::split(image, r);
        return r;
    }


    SplitChannelsWithGui::SplitChannelsWithGui()
    {
        auto& self = *this;
        self.InputGui = std::make_shared<ImageWithGui>();
        self.OutputGui = std::make_shared<ImageChannelsWithGui>();
    }

    std::any SplitChannelsWithGui::f(const std::any &x)
    {
        auto& self = *this;
        const Image& asImage = std::any_cast<const Image&>(x);
        cv::Mat imageConverted = asImage;
        if (self._colorConversion)
        {
            imageConverted = cv::Mat();
            cv::cvtColor(asImage, imageConverted, self._colorConversion->ConversionCode);
        }

        std::vector<Image> channels = SplitChannels(imageConverted);
        std::vector<Image> channels_normalized;
        for (auto& channel: channels)
        {
            cv::Mat channel_normalized;
            channel.convertTo(channel_normalized, CV_64FC1);
            channel_normalized = channel_normalized / 255.;
            channels_normalized.push_back(channel_normalized);
        }
        return channels_normalized;
    }

    std::string SplitChannelsWithGui::Name()
    {
        auto& self = *this;
        std::string r = "SplitChannels";
        if (self._colorConversion)
            r += " - " + self._colorConversion->Name;
        return r;
    }

    bool SplitChannelsWithGui::GuiParams()
    {
        auto& self = *this;
        if (self._guiParamsOptionalFn)
            return self._guiParamsOptionalFn();
        else
            return false;
    }

    MergeChannelsWithGui::MergeChannelsWithGui()
    {
        auto& self = *this;
        self.InputGui = std::make_shared<ImageChannelsWithGui>();
        self.OutputGui = std::make_shared<ImageWithGui>();
    }

    std::any MergeChannelsWithGui::f(const std::any &x)
    {
        auto &self = *this;
        const auto& asImages = std::any_cast<const std::vector<cv::Mat>&>(x);

        cv::Mat image_float;
        cv::merge(asImages, image_float);

        image_float = image_float * 255.;

        cv::Mat imageUInt8;
        image_float.convertTo(imageUInt8, CV_MAKE_TYPE(CV_8U, image_float.channels()));

        cv::Mat imageConverted = imageUInt8;
        if (self._colorConversion)
        {
            imageConverted = cv::Mat();
            cv::cvtColor(imageUInt8, imageConverted, self._colorConversion->ConversionCode);
        }

        return imageConverted;
    }

    std::string MergeChannelsWithGui::Name()
    {
        auto& self = *this;
        std::string r = "MergeChannels";
        if (self._colorConversion)
            r += " - " + self._colorConversion->Name;
        return r;
    }

}