#include "lut.h"

//#include <opencv2/imgproc.hpp>
//#include <opencv2/imgcodecs.hpp>


namespace VisualProg
{

    Image LutImage::Apply(const Image &image)
    {
        auto& self = *this;
        Image r;
        cv::pow(image, self.powExponent, r);
        return r;
    }

    bool LutImage::GuiParams(const std::string &channelName)
    {
        auto& self = *this;
        ImGui::Text("%s", channelName.c_str());
        ImGui::SetNextItemWidth(100.f);
        bool changed = ImGui::SliderFloat("power", &self.powExponent, 0., 10., "%.1f", ImGuiSliderFlags_Logarithmic);
        if (ImGui::SmallButton("Reset"))
        {
            self.powExponent = 1.f;
            changed = true;
        }
        return changed;
    }

    LutImageWithGui::LutImageWithGui()
    {
        auto& self = *this;
        self.InputGui = std::make_shared<ImageWithGui>();
        self.OutputGui = std::make_shared<ImageWithGui>();
    }

    std::any LutImageWithGui::f(const std::any &x)
    {
        const auto& asImage = std::any_cast<const cv::Mat&>(x);
        auto image_adjusted = _lutImage.Apply(asImage);
        return image_adjusted;
    }

    LutChannelsWithGui::LutChannelsWithGui()
    {
        auto& self = *this;
        self.InputGui = std::make_shared<ImageChannelsWithGui>();
        self.OutputGui = std::make_shared<ImageChannelsWithGui>();
    }

    std::any LutChannelsWithGui::f(const std::any &x)
    {
        auto& self = *this;
        const auto& asImages =  std::any_cast<const std::vector<cv::Mat>&>(x);

        const auto& original_channels = asImages;
        _addParamsOnDemand(original_channels.size());

        std::vector<Image> adjustedChannels;
        for (size_t i = 0; i < original_channels.size(); ++i)
        {
            adjustedChannels.push_back(self._channelAdjustParams[i].Apply(original_channels[i]));
        }

        return adjustedChannels;
    }

    bool LutChannelsWithGui::GuiParams()
    {
        auto& self = *this;
        bool changed = false;
        for (size_t i = 0; i < self._channelAdjustParams.size(); ++i)
        {
            ImGui::PushID(i);
            auto channel_name = ColorTypeChannelName(self._colorType, i);
            changed |= self._channelAdjustParams[i].GuiParams(channel_name);
            ImGui::PopID();
        }
        return changed;
    }

    Split_Lut_Merge_WithGui::Split_Lut_Merge_WithGui(ColorType colorType)
    {
        auto& self = *this;
        self._possibleConversionPairs = ComputePossibleConversionPairs(colorType);
        self._currentConversion = std::nullopt;
        self._split = std::make_shared<SplitChannelsWithGui>();
        self._split->_guiParamsOptionalFn = [&]() { return self.GuiSelectConversion(); };
        self._lut = std::make_shared<LutChannelsWithGui>();
        self._merge = std::make_shared<MergeChannelsWithGui>();
    }

    bool Split_Lut_Merge_WithGui::GuiSelectConversion()
    {
        auto& self = *this;
        bool changed = false;
        self._showPossibleColorConversions |= ImGui::Checkbox("Show Color ", &self._showPossibleColorConversions);

        if (self._showPossibleColorConversions)
        {
            if (ImGui::RadioButton("None", ! self._currentConversion.has_value()))
            {
                changed = true;
                self._currentConversion = std::nullopt;
            }
            for (const auto& conversionPair: self._possibleConversionPairs)
            {
                bool active = (self._currentConversion->Name == conversionPair.Name);
                if (ImGui::RadioButton(conversionPair.Name.c_str(), active))
                {
                    self._currentConversion = conversionPair;
                    changed = true;
                }
            }
        }

        if (changed)
        {
            if (! self._currentConversion.has_value())
            {
                self._split->_colorConversion = std::nullopt;
                self._merge->_colorConversion = std::nullopt;
            }
            else
            {
                self._split->_colorConversion = self._currentConversion->Conversion;
                self._merge->_colorConversion = self._currentConversion->InvConversion;

                self._lut->_colorType = self._currentConversion->Conversion.DstColor;

                auto lutOutputGui = dynamic_cast<ImageChannelsWithGui*>(self._lut->OutputGui.get());
                auto splitOutputGui = dynamic_cast<ImageChannelsWithGui*>(self._split->OutputGui.get());

                lutOutputGui->_colorType = self._currentConversion->Conversion.DstColor;
                splitOutputGui->_colorType = self._currentConversion->Conversion.DstColor;
            }
        }

        return changed;
    }
}