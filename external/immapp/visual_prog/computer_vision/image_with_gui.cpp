#include "image_with_gui.h"


namespace VisualProg
{

    std::vector<cv::Mat> SplitChannels(const Image& image)
    {
        assert(image.channels() > 1);
        std::vector<cv::Mat> r;
        cv::split(image, r);
        return r;
    }

    bool _GuiEditSize(cv::Size* size)
    {
        auto modifySizeByRatio = [](cv::Size* size, double ratio)
        {
            size->width = (int)((double)size->width * ratio + 0.5);
            size->height = (int)((double)size->height * ratio + 0.5);
        };

        bool changed = false;

        double ratio = 1.05;
        ImGui::PushButtonRepeat(true);
        ImGui::Text("Thubmnail size");
        ImGui::SameLine();
        if (ImGui::SmallButton(" smaller "))
        {
            changed = true;
            modifySizeByRatio(size, 1. / ratio);
        }
        ImGui::SameLine();
        if (ImGui::SmallButton(" bigger "))
        {
            changed = true;
            modifySizeByRatio(size, ratio);
        }
        ImGui::PopButtonRepeat();

        return changed;
    }

    ImageWithGui::ImageWithGui(const Image &image, const std::string &zoomKey, int imageDisplayWidth)
    {
        auto& self = *this;
        self._array = image;
        self._firstFrame = true;
        self._imageParams = ImmVision::ImageParams();
        self._imageParams.ImageDisplaySize = cv::Size(imageDisplayWidth, 0);
        self._imageParams.ZoomKey = zoomKey;
    }

    void ImageWithGui::Set(const std::any &v)
    {
        auto& self = *this;
        self._array = std::any_cast<const Image&>(v);
        self._firstFrame = true;
    }

    std::any ImageWithGui::Get()
    {
        return _array;
    }

    void ImageWithGui::GuiData(std::string_view function_name)
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

    std::any ImageWithGui::GuiSetInput()
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

    ImageChannelsWithGui::ImageChannelsWithGui(const std::vector<cv::Mat> &images, std::string zoomKey,
                                               int imageDisplayWidth)
    {
        auto& self = *this;
        self._arrays = images;
        self.firstFrame = true;

        self._imageParams = ImmVision::ImageParams();
        self._imageParams.ImageDisplaySize = {imageDisplayWidth, 0};
        self._imageParams.ZoomKey =zoomKey;
    }

    void ImageChannelsWithGui::Set(const std::any &v)
    {
        auto& self = *this;
        self._arrays = std::any_cast<const std::vector<cv::Mat>&>(v);
        self.firstFrame = true;
    }

    std::any ImageChannelsWithGui::Get()
    {
        return _arrays;
    }

    void ImageChannelsWithGui::GuiData(std::string_view function_name)
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