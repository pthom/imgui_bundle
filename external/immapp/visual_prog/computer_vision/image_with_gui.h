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

    std::vector<cv::Mat> SplitChannels(const Image& image);

    bool _GuiEditSize(cv::Size* size);

    struct ImageWithGui: public AnyDataWithGui
    {
        Image _array;
        ImmVision::ImageParams _imageParams;
        bool _firstFrame;

        ImageWithGui(const Image& image = cv::Mat(), const std::string& zoomKey = "z", int imageDisplayWidth = 200)
        {
            auto& self = *this;
            self._array = image;
            self._firstFrame = true;
            self._imageParams = ImmVision::ImageParams();
            self._imageParams.ImageDisplaySize = cv::Size(imageDisplayWidth, 0);
            self._imageParams.ZoomKey = zoomKey;
        }

        void Set(const std::any& v) override
        {
            auto& self = *this;
            self._array = std::any_cast<const Image&>(v);
            self._firstFrame = true;
        }

        std::any Get() override
        {
            return _array;
        }

        void GuiData(std::string_view function_name) override
        {
            auto& self = *this;
            self._imageParams.RefreshImage = _firstFrame;
            self._firstFrame = false;

            ImGui::SetNextItemWidth(100.f);
            _GuiEditSize(&self._imageParams.ImageDisplaySize);

            ImmVision::Image(std::string(function_name), self._array, &self._imageParams);
            if (ImGui::SmallButton("inspect"))
                ImmVision::Inspector_AddImage(self._array, std::string(function_name));
        }

        std::any GuiSetInput() override
        {
            std::any result;
            if (ImGui::Button("Select image file"))
            {
                ifd::FileDialog::Instance().Open(
                    "ImageOpenDialog",
                    "Choose an image",
                    "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
                    false
                );
            }

            ImmApp::SuspendNodeEditorCanvas();
            if (ifd::FileDialog::Instance().IsDone("ImageOpenDialog"))
            {
                if (ifd::FileDialog::Instance().HasResult())
                {
                    auto ifd_result = ifd::FileDialog::Instance().GetResult();
                    cv::Mat image = cv::imread(ifd_result.string());
                    if (! image.empty())
                        result = image;
                }
                ifd::FileDialog::Instance().Close();
            }
            ImmApp::ResumeNodeEditorCanvas();

            return result;
        }
    };
    using ImageWithGuiPtr = std::shared_ptr<ImageWithGui>;


    struct ImageChannelsWithGui: public AnyDataWithGui
    {
        std::vector<cv::Mat> _arrays;
        ImmVision::ImageParams _imageParams;
        bool firstFrame;
        ColorType _colorType = ColorType::BGR;

        ImageChannelsWithGui(const std::vector<cv::Mat>& images = {},
                             std::string zoomKey = "z",
                             int imageDisplayWidth = 200
                      )
        {
            auto& self = *this;
            self._arrays = images;
            self.firstFrame = true;

            self._imageParams = ImmVision::ImageParams();
            self._imageParams.ImageDisplaySize = {imageDisplayWidth, 0};
            self._imageParams.ZoomKey =zoomKey;
        }

        void Set(const std::any& v) override
        {
            auto& self = *this;
            self._arrays = std::any_cast<const std::vector<cv::Mat>&>(v);
            self.firstFrame = true;
        }

        std::any Get() override
        {
            return _arrays;
        }

        void GuiData(std::string_view function_name) override
        {
            auto& self = *this;
            bool refreshImage = self.firstFrame;
            self.firstFrame = false;

            _GuiEditSize(&self._imageParams.ImageDisplaySize);

            for (size_t i = 0; i < self._arrays.size(); ++i)
            {
                auto channelName = ColorTypeChannelName(self._colorType, i);
                auto& image = self._arrays[i];
                self._imageParams.RefreshImage = refreshImage;
                std::string label = channelName;
                ImmVision::Image(label, image, &self._imageParams);
                if (ImGui::SmallButton("inspect"))
                    ImmVision::Inspector_AddImage(image, label);
            }
        }

    };
    using ImagesWithGuiPtr = std::shared_ptr<ImageChannelsWithGui>;


    // Splits a CV_8UC3 into normalized float channels (i.e. with values between 0 and 1)
    struct SplitChannelsWithGui: public FunctionWithGui
    {
        std::optional<ColorConversion> _colorConversion;
        std::function<bool()> _guiParamsOptionalFn;

        SplitChannelsWithGui()
        {
            auto& self = *this;
            self.InputGui = std::make_shared<ImageWithGui>();
            self.OutputGui = std::make_shared<ImageChannelsWithGui>();
        }

        std::any f(const std::any& x) override
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

        std::string Name() override
        {
            auto& self = *this;
            std::string r = "SplitChannels";
            if (self._colorConversion)
                r += " - " + self._colorConversion->Name;
            return r;
        }

        bool GuiParams() override
        {
            auto& self = *this;
            if (self._guiParamsOptionalFn)
                return self._guiParamsOptionalFn();
            else
                return false;
        }
    };


    // Merges normalized float image into a CV_8UC3 image
    struct MergeChannelsWithGui: public FunctionWithGui
    {
        std::optional<ColorConversion> _colorConversion;

        MergeChannelsWithGui()
        {
            auto& self = *this;
            self.InputGui = std::make_shared<ImageChannelsWithGui>();
            self.OutputGui = std::make_shared<ImageWithGui>();
        }

        std::any f(const std::any& x) override
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

        std::string Name() override
        {
            auto& self = *this;
            std::string r = "MergeChannels";
            if (self._colorConversion)
                r += " - " + self._colorConversion->Name;
            return r;
        }

    };


    struct LutImage
    {
        float powExponent = 1.f;
        Image Apply(const Image& image)
        {
            auto& self = *this;
            Image r;
            cv::pow(image, self.powExponent, r);
            return r;
        }

        bool GuiParams(const std::string& channelName)
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
    };


    struct LutImageWithGui: public FunctionWithGui
    {
        LutImage _lutImage;

        LutImageWithGui()
        {
            auto& self = *this;
            self.InputGui = std::make_shared<ImageWithGui>();
            self.OutputGui = std::make_shared<ImageWithGui>();
        }

        std::any f(const std::any& x) override
        {
            const auto& asImage = std::any_cast<const cv::Mat&>(x);
            auto image_adjusted = _lutImage.Apply(asImage);
            return image_adjusted;
        }

        std::string Name() override { return "LUT"; }

        bool GuiParams() override { return _lutImage.GuiParams("LUT"); }

    };


    struct LutChannelsWithGui: public FunctionWithGui
    {
        ColorType _colorType = ColorType::BGR;
        std::vector<LutImage> _channelAdjustParams;

        LutChannelsWithGui()
        {
            auto& self = *this;
            self.InputGui = std::make_shared<ImageChannelsWithGui>();
            self.OutputGui = std::make_shared<ImageChannelsWithGui>();
        }

        void _addParamsOnDemand(size_t nbChannels)
        {
            while(_channelAdjustParams.size() < nbChannels)
                _channelAdjustParams.push_back(LutImage());
        }

        std::any f (const std::any& x) override
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

        std::string Name() override { return "AdjustChannels"; }

        bool GuiParams() override
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

        Split_Lut_Merge_WithGui(ColorType colorType)
        {
            auto& self = *this;
            self._possibleConversionPairs = ComputePossibleConversionPairs(colorType);
            self._currentConversion = std::nullopt;
            self._split = std::make_shared<SplitChannelsWithGui>();
            self._split->_guiParamsOptionalFn = [&]() { return self.GuiSelectConversion(); };
            self._lut = std::make_shared<LutChannelsWithGui>();
            self._merge = std::make_shared<MergeChannelsWithGui>();
        }

        bool GuiSelectConversion()
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

    };

}