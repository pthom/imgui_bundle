#pragma once
#include "immapp/visual_prog/functions_composition.h"
#include "immvision/immvision.h"

#include <opencv2/core.hpp>

#include "cv_color_type.h"


namespace VisualProg
{
    using Image = cv::Mat;

    struct ImageWithGui: public AnyDataWithGui
    {
        Image _array;
        ImmVision::ImageParams _imageParams;
        bool _firstFrame;

        ImageWithGui(const Image& image = cv::Mat(), const std::string& zoomKey = "z", int imageDisplayWidth = 200);

        void Set(const std::any& v) override;
        std::any Get() override;
        void GuiData(std::string_view function_name) override;
        std::any GuiSetInput() override;
    };
    using ImageWithGuiPtr = std::shared_ptr<ImageWithGui>;


    struct ImageChannelsWithGui: public AnyDataWithGui
    {
        std::vector<cv::Mat> _arrays;
        ImmVision::ImageParams _imageParams;
        bool firstFrame;
        ColorType _colorType = ColorType::BGR;

        explicit ImageChannelsWithGui(const std::vector<cv::Mat>& images = {},
                             std::string zoomKey = "z",
                             int imageDisplayWidth = 200
                      );

        void Set(const std::any& v) override;
        std::any Get() override;
        void GuiData(std::string_view function_name) override;

    };
    using ImagesWithGuiPtr = std::shared_ptr<ImageChannelsWithGui>;


}