#pragma once
#include "immapp/visual_prog/functions_composition.h"
#include "immvision/immvision.h"
#include "immapp/utils.h"
#include "ImFileDialog/ImFileDialog.h"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

#include <functional>

#include "cv_color_type.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"


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


    // Splits a CV_8UC3 into normalized float channels (i.e. with values between 0 and 1)
    struct SplitChannelsWithGui: public FunctionWithGui
    {
        std::optional<ColorConversion> _colorConversion;
        std::function<bool()> _guiParamsOptionalFn;

        SplitChannelsWithGui();

        std::any f(const std::any& x) override;
        std::string Name() override;
        bool GuiParams() override;
    };


    // Merges normalized float image into a CV_8UC3 image
    struct MergeChannelsWithGui: public FunctionWithGui
    {
        std::optional<ColorConversion> _colorConversion;

        MergeChannelsWithGui();
        std::any f(const std::any& x) override;
        std::string Name() override;

    };


    struct LutImage
    {
        float powExponent = 1.f;
        Image Apply(const Image& image);
        bool GuiParams(const std::string& channelName);
    };


    struct LutImageWithGui: public FunctionWithGui
    {
        LutImage _lutImage;

        LutImageWithGui();

        std::any f(const std::any& x) override;
        std::string Name() override { return "LUT"; }
        bool GuiParams() override { return _lutImage.GuiParams("LUT"); }

    };


    struct LutChannelsWithGui: public FunctionWithGui
    {
        ColorType _colorType = ColorType::BGR;
        std::vector<LutImage> _channelAdjustParams;

        LutChannelsWithGui();

        void _addParamsOnDemand(size_t nbChannels)
        {
            while(_channelAdjustParams.size() < nbChannels)
                _channelAdjustParams.push_back(LutImage());
        }

        std::any f (const std::any& x) override;
        std::string Name() override { return "AdjustChannels"; }
        bool GuiParams() override;
    };


    class Split_Lut_Merge_WithGui
    {
        std::vector<ColorConversionPair> _possibleConversionPairs;
        std::optional<ColorConversionPair> _currentConversion;
        bool _showPossibleColorConversions = false;

    public:
        std::shared_ptr<SplitChannelsWithGui> _split;
        std::shared_ptr<LutChannelsWithGui> _lut;
        std::shared_ptr<MergeChannelsWithGui> _merge;

        explicit Split_Lut_Merge_WithGui(ColorType colorType);

        bool GuiSelectConversion();

    };

}