#pragma once
#include <optional>
#include <vector>
#include <string>


namespace VisualProg
{
    using CvColorConversionCode = int;

    enum class ColorType
    {
        BGR = 0,
        RGB,
        HSV,
        HLS,
        Lab,
        Luv,
        XYZ,
    };

    std::vector<ColorType> AllColorTypes();
    std::string ColorTypeName(ColorType colorType);
    std::vector<std::string> ColorTypeChannelNames(ColorType colorType);
    std::string ColorTypeChannelName(ColorType colorType, size_t idxChannel);


    struct ColorConversion
    {
        std::string Name;
        ColorType SrcColor;
        ColorType DstColor;
        CvColorConversionCode ConversionCode;
    };

    // Two inverse color conversions
    struct ColorConversionPair
    {
        std::string Name;
        ColorConversion Conversion;
        ColorConversion InvConversion;
    };


    std::optional<CvColorConversionCode> CvColorConversionCodeBetween(ColorType type1, ColorType type2);
    std::vector<ColorConversionPair> ComputePossibleConversionPairs(ColorType colorType);

}
