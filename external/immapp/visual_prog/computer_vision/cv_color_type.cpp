#include "cv_color_type.h"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <map>
#include <fplus/fplus.hpp>

namespace VisualProg
{
    std::vector<ColorType> AllColorTypes()
    {
        return {
            ColorType::BGR,
            ColorType::RGB,
            ColorType::HSV,
            ColorType::HLS,
            ColorType::Lab,
            ColorType::Luv,
            ColorType::XYZ,
        };
    };


    std::string ColorTypeName(ColorType colorType)
    {
        static std::map<ColorType, std::string> table {
            { ColorType::BGR, "BGR" },
            { ColorType::RGB, "RGB" },
            { ColorType::HSV, "HSV" },
            { ColorType::HLS, "HLS" },
            { ColorType::Lab, "Lab" },
            { ColorType::Luv, "Luv" },
            { ColorType::XYZ, "XYZ" },
        };
        return table.at(colorType);
    }


    std::vector<std::string> ColorTypeChannelNames(ColorType colorType)
    {
        std::string name = ColorTypeName(colorType);
        std::vector<std::string> r;
        for (auto c : name)
        {
            r.push_back(std::string("") + c);
        }
        return r;
    }


    std::string ColorTypeChannelName(ColorType colorType, size_t idxChannel)
    {
        auto channelNames = ColorTypeChannelNames(colorType);
        assert(idxChannel >= 0 && idxChannel < channelNames.size());
        return channelNames[idxChannel];
    }


    std::optional<CvColorConversionCode> CvColorConversionCodeBetween(ColorType type1, ColorType type2)
    {
        auto handle_bgr = [=]() -> std::optional<CvColorConversionCode>
        {
            if (type1 == ColorType::BGR)
            {
                static std::map<ColorType, CvColorConversionCode> conversions = {
                    { ColorType::RGB, cv::COLOR_BGR2RGB },
                    { ColorType::HSV, cv::COLOR_BGR2HSV_FULL },
                    { ColorType::HLS, cv::COLOR_BGR2HLS_FULL },
                    { ColorType::Lab, cv::COLOR_BGR2Lab },
                    { ColorType::Luv, cv::COLOR_BGR2Luv },
                    { ColorType::XYZ, cv::COLOR_BGR2XYZ },
                };
                if (fplus::map_contains(conversions, type2))
                    return conversions.at(type2);
            }

            if (type2 == ColorType::BGR)
            {
                static std::map<ColorType, CvColorConversionCode> conversionsInv = {
                    { ColorType::RGB, cv::COLOR_RGB2BGR },
                    { ColorType::HSV, cv::COLOR_HSV2BGR_FULL },
                    { ColorType::HLS, cv::COLOR_HLS2BGR_FULL },
                    { ColorType::Lab, cv::COLOR_Lab2BGR },
                    { ColorType::Luv, cv::COLOR_Luv2BGR },
                    { ColorType::XYZ, cv::COLOR_XYZ2BGR },
                };
                if (fplus::map_contains(conversionsInv, type1))
                    return conversionsInv.at(type1);
            }
            return std::nullopt;
        };

        auto handle_rgb = [=]() -> std::optional<CvColorConversionCode>
        {
            if (type1 == ColorType::RGB)
            {
                static std::map<ColorType, CvColorConversionCode> conversions = {
                    { ColorType::BGR, cv::COLOR_RGB2BGR },
                    { ColorType::HSV, cv::COLOR_RGB2HSV_FULL },
                    { ColorType::HLS, cv::COLOR_RGB2HLS_FULL },
                    { ColorType::Lab, cv::COLOR_RGB2Lab },
                    { ColorType::Luv, cv::COLOR_RGB2Luv },
                    { ColorType::XYZ, cv::COLOR_RGB2XYZ },
                };
                if (fplus::map_contains(conversions, type2))
                    return conversions.at(type2);
            }

            if (type2 == ColorType::RGB)
            {
                static std::map<ColorType, CvColorConversionCode> conversionsInv = {
                    { ColorType::BGR, cv::COLOR_BGR2RGB },
                    { ColorType::HSV, cv::COLOR_HSV2RGB_FULL },
                    { ColorType::HLS, cv::COLOR_HLS2RGB_FULL },
                    { ColorType::Lab, cv::COLOR_Lab2RGB },
                    { ColorType::Luv, cv::COLOR_Luv2RGB },
                    { ColorType::XYZ, cv::COLOR_XYZ2RGB },
                };
                if (fplus::map_contains(conversionsInv, type1))
                    return conversionsInv.at(type1);
            }
            return std::nullopt;
        };

        auto with_bgr = handle_bgr();
        if (with_bgr)
            return with_bgr;

        auto with_rgb = handle_rgb();
        if (with_rgb)
            return with_rgb;

        return std::nullopt;
    }


    std::vector<ColorConversionPair> ComputePossibleConversionPairs(ColorType colorType)
    {
        std::vector<ColorConversionPair> r;
        for (auto otherColorType: AllColorTypes())
        {
            auto conversion_code = CvColorConversionCodeBetween(colorType, otherColorType);
            auto conversion_code_inv = CvColorConversionCodeBetween(otherColorType, colorType);
            if (conversion_code && conversion_code_inv)
            {
                ColorConversion conversionDirect {
                    /* .Name = */ ColorTypeName(colorType) + "=>" + ColorTypeName(otherColorType),
                    /* .SrcColor = */ colorType,
                    /* .DstColor = */ otherColorType,
                    /* .ConversionCode = */ conversion_code.value()
                };
                ColorConversion conversionInv {
                    /* .Name = */ ColorTypeName(otherColorType) + "=>" + ColorTypeName(colorType),
                    /* .SrcColor = */ otherColorType,
                    /* .DstColor = */ colorType,
                    /* .ConversionCode = */ conversion_code_inv.value()
                };

                ColorConversionPair pair {
                    ColorTypeName(colorType) + "=>" + ColorTypeName(otherColorType) + "=>" + ColorTypeName(colorType),
                    conversionDirect,
                    conversionInv };
                r.push_back(pair);
            }
        }
        return r;
    }

}
