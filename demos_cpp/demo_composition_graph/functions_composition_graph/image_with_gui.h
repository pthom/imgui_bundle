#pragma once
#include "functions_composition_graph.h"
#include "immvision/immvision.h"
#include "ImFileDialog/ImFileDialog.h"
#include <fplus/fplus.hpp>

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>


#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"
inline void SuspendNodeEditorCanvas()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Suspend();
}
inline void ResumeNodeEditorCanvas()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Resume();
}


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

            SuspendNodeEditorCanvas();
            if (ifd::FileDialog::Instance().IsDone("ImageOpenDialog"))
            {
                if (ifd::FileDialog::Instance().HasResult())
                {
                    auto ifd_result = ifd::FileDialog::Instance().GetResult();
                    cv::Mat image = cv::imread(ifd_result.c_str());
                    if (! image.empty())
                        result = image;
                }
                ifd::FileDialog::Instance().Close();
            }
            ResumeNodeEditorCanvas();

            return result;
        }
    };
    using ImageWithGuiPtr = std::shared_ptr<ImageWithGui>;


    struct ImagesWithGui: public AnyDataWithGui
    {
        std::vector<cv::Mat> _arrays;
        ImmVision::ImageParams _imageParams;
        bool firstFrame;

        ImagesWithGui(const std::vector<cv::Mat>& images = {},
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
                auto& image = self._arrays[i];
                self._imageParams.RefreshImage = refreshImage;
                std::string label = std::string(function_name) + " - " + std::to_string(i);
                ImmVision::Image(label, image, &self._imageParams);
                if (ImGui::SmallButton("inspect"))
                    ImmVision::Inspector_AddImage(image, label);
            }
        }

    };
    using ImagesWithGuiPtr = std::shared_ptr<ImagesWithGui>;


    // Splits a CV_8UC3 into normalized float channels (i.e. with values between 0 and 1)
    struct SplitChannelsWithGui: public FunctionWithGui
    {
        std::any f(const std::any& x) override
        {
            const Image& asImage = std::any_cast<const Image&>(x);

            std::vector<Image> channels = SplitChannels(asImage);
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
            return "SplitChannels";
        }

        AnyDataWithGuiPtr InputGui() override { return std::make_shared<ImageWithGui>(); }
        AnyDataWithGuiPtr OutputGui() override { return std::make_shared<ImagesWithGui>(); }
    };


    // Merges normalized float image into a CV_8UC3 image
    struct MergeChannelsWithGui: public FunctionWithGui
    {
        std::any f(const std::any& x) override
        {
            auto &self = *this;
            const auto& asImages = std::any_cast<const std::vector<cv::Mat>&>(x);

            cv::Mat image_float;
            cv::merge(asImages, image_float);

            image_float = image_float * 255.;

            cv::Mat imageUInt8;
            image_float.convertTo(imageUInt8, CV_MAKE_TYPE(CV_8U, image_float.channels()));

            return imageUInt8;
        }

        std::string Name() override { return "MergeChannels"; }

        AnyDataWithGuiPtr InputGui() override { return std::make_shared<ImagesWithGui>(); }
        AnyDataWithGuiPtr OutputGui() override { return std::make_shared<ImageWithGui>(); }
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

        bool GuiParams()
        {
            auto& self = *this;
            ImGui::SetNextItemWidth(100.f);
            bool changed = ImGui::SliderFloat("power", &self.powExponent, 0., 10., "%.1f", ImGuiSliderFlags_Logarithmic);
            return changed;
        }
    };


    struct LutImageWithGui: public FunctionWithGui
    {
        LutImage _lutImage;

        std::any f(const std::any& x) override
        {
            const auto& asImage = std::any_cast<const cv::Mat&>(x);
            auto image_adjusted = _lutImage.Apply(asImage);
            return image_adjusted;
        }

        std::string Name() override { return "LUT"; }

        bool GuiParams() override { return _lutImage.GuiParams(); }

        AnyDataWithGuiPtr InputGui() override { return std::make_shared<ImageWithGui>(); }
        AnyDataWithGuiPtr OutputGui() override { return std::make_shared<ImageWithGui>(); }

    };


    struct LutChannelsWithGui: public FunctionWithGui
    {
        std::vector<LutImage> _channelAdjustParams;

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
                changed |= self._channelAdjustParams[i].GuiParams();
                ImGui::PopID();
            }
            return changed;
        }

        AnyDataWithGuiPtr InputGui() override { return std::make_shared<ImagesWithGui>(); }
        AnyDataWithGuiPtr OutputGui() override { return std::make_shared<ImagesWithGui>(); }
    };
}