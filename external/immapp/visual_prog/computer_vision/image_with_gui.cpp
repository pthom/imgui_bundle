#include "image_with_gui.h"
#include "immvision/immvision.h"
#include "immapp/utils.h"
#include "ImFileDialog/ImFileDialog.h"

#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

namespace VisualProg
{

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

}