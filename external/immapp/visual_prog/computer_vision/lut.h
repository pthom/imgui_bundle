#pragma once
#include "immapp/visual_prog/computer_vision/image_with_gui.h"
#include "immapp/visual_prog/computer_vision/split_merge.h"


namespace VisualProg
{
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