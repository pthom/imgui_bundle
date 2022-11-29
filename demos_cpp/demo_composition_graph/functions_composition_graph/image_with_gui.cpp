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

}