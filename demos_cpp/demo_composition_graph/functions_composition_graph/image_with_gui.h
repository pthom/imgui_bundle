#pragma once
#include "functions_composition_graph.h"
#include "immvision/immvision.h"

#include <fplus/fplus.hpp>

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>


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

        ImageWithGui(const Image& image, const std::string& zoomKey = "z", int imageDisplayWidth = 200)
        {
            auto& self = *this;
            self._array = image;
            self._firstFrame = true;
            self._imageParams = ImmVision::ImageParams();
            self._imageParams.ImageDisplaySize = cv::Size(imageDisplayWidth, 0);
            self._imageParams.ZoomKey = zoomKey;
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
    };
    using ImageWithGuiPtr = std::shared_ptr<ImageWithGui>;


    struct ImagesWithGui: public AnyDataWithGui
    {
        std::vector<cv::Mat> _arrays;
        std::vector<ImmVision::ImageParams> _imageParams;
        bool firstFrame;

        ImagesWithGui(const std::vector<cv::Mat>& images,
                      std::string zoomKey = "z",
                      int imageDisplayWidth = 200,
                      bool shareImageParams = false
                      )
        {
            auto& self = *this;
            self._arrays = images;
            self.firstFrame = true;

            auto makeImageParams = [imageDisplayWidth, zoomKey](){
                auto imageParams = ImmVision::ImageParams();
                imageParams.ImageDisplaySize = cv::Size(imageDisplayWidth, 0);
                imageParams.ZoomKey = zoomKey;
                return imageParams;
            };

            if (shareImageParams)
                self._imageParams.push_back(makeImageParams());
            else
            {
                for (size_t i = 0; i < images.size(); ++i)
                    self._imageParams.push_back(makeImageParams());
            }
        }

        void GuiData(std::string_view function_name) override
        {
            auto& self = *this;
            bool refreshImage = self.firstFrame;
            self.firstFrame = false;

            if (_GuiEditSize(&self._imageParams[0].ImageDisplaySize))
                for (auto& params: self._imageParams)
                    params.ImageDisplaySize = self._imageParams[0].ImageDisplaySize;

            for (size_t i = 0; i < self._arrays.size(); ++i)
            {
                auto& image = self._arrays[i];
                ImmVision::ImageParams& imageParams = (i < self._imageParams.size()) ? self._imageParams[0] : self._imageParams[i];
                imageParams.RefreshImage = refreshImage;
                std::string label = std::string(function_name) + " - " + std::to_string(i);
                ImmVision::Image(label, image, &imageParams);
                if (ImGui::SmallButton("inspect"))
                    ImmVision::Inspector_AddImage(image, label);
            }
        }

    };
    using ImagesWithGuiPtr = std::shared_ptr<ImagesWithGui>;


    struct AdjustImage
    {
        float powExponent = 1.f;

        Image Apply(const Image& image)
        {
            auto& self = *this;
            Image r;
            cv::pow(image, self.powExponent, r);
            return r;
        }

        bool GuiParams()
        {
            auto& self = *this;
            ImGui::SetNextItemWidth(100.f);
            bool changed = ImGui::SliderFloat("power", &self.powExponent, 0., 10., "%.1f", ImGuiSliderFlags_Logarithmic);
            return changed;
        }
    };


    // Splits a CV_8UC3 into normalized float channels (i.e. with values between 0 and 1)
    struct SplitChannelsWithGui: public FunctionWithGui
    {
        AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) override
        {
            // assert type(x) == ImageWithGui
            auto asImage = dynamic_cast<ImageWithGui*>(x.get());
            assert(asImage);

            std::vector<Image> channels = SplitChannels(asImage->_array);
            std::vector<Image> channels_normalized;
            for (auto& channel: channels)
            {
                cv::Mat channel_normalized;
                channel.convertTo(channel_normalized, CV_64FC1);
                channel_normalized = channel_normalized / 255.;
                channels_normalized.push_back(channel_normalized);
            }

            auto r = std::make_shared<ImagesWithGui>(channels_normalized);
            return r;
        }

        std::string Name() override
        {
            return "SplitChannels";
        }
    };


    struct AdjustImageWithGui: public FunctionWithGui
    {
        AdjustImage _adjustImage;

        AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) override
        {
            // assert type(x) == ImageWithGui
            auto asImage = dynamic_cast<ImageWithGui*>(x.get());
            assert(asImage);

            auto image_adjusted = _adjustImage.Apply(asImage->_array);

            auto r = std::make_shared<ImageWithGui>(image_adjusted);
            return r;
        }

        std::string Name() override { return "AdjustImage"; }

        bool GuiParams() override { return _adjustImage.GuiParams(); }
    };


    struct AdjustChannelsWithGui: public FunctionWithGui
    {
        std::vector<AdjustImage> _channelAdjustParams;

        void _addParamsOnDemand(size_t nbChannels)
        {
            while(_channelAdjustParams.size() < nbChannels)
                _channelAdjustParams.push_back(AdjustImage());
        }

        AnyDataWithGuiPtr f (const AnyDataWithGuiPtr& x) override
        {
            auto& self = *this;
            // assert type(x) == ImagesWithGui
            auto asImages = dynamic_cast<ImagesWithGui*>(x.get());
            assert(asImages);

            const auto& original_channels = asImages->_arrays;
            _addParamsOnDemand(original_channels.size());

            std::vector<Image> adjustedChannels;
            for (size_t i = 0; i < original_channels.size(); ++i)
            {
                adjustedChannels.push_back(self._channelAdjustParams[i].Apply(original_channels[i]));
            }

            auto r = std::make_shared<ImagesWithGui>(adjustedChannels);
            return r;
        }

        std::string Name() override { return "AdjustChannels"; }

        bool GuiParams() override
        {
            auto& self = *this;
            bool changed = false;
            for (size_t i = 0; i < self._channelAdjustParams.size(); ++i)
            {
                ImGui::PushID(i);
                changed |= self._channelAdjustParams[i].GuiParams();
                ImGui::PopID();
            }
            return changed;
        }
    };


    // Merges normalized float image into a CV_8UC3 image
    struct MergeChannelsWithGui: public FunctionWithGui
    {
        AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) override
        {
            auto &self = *this;
            // assert type(x) == ImagesWithGui
            auto asImages = dynamic_cast<ImagesWithGui *>(x.get());
            assert(asImages);

            cv::Mat image_float;
            cv::merge(asImages->_arrays, image_float);

            image_float = image_float * 255.;

            cv::Mat imageUInt8;
            image_float.convertTo(imageUInt8, CV_MAKE_TYPE(CV_8U, image_float.channels()));

            auto r = std::make_shared<ImageWithGui>(imageUInt8);
            return r;
        }

        std::string Name() override { return "MergeChannels"; }
    };
}