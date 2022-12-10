#pragma once
#include "immapp/visual_prog/computer_vision/image_with_gui.h"


namespace VisualProg
{
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
}